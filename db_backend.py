"""PostgreSQL compatibility layer for VAIGO.

The application historically calls ``db.execute(sql, params)`` using SQLite-style
``?`` placeholders.  This small adapter keeps that call-site API while the real
storage engine is PostgreSQL.  No SQLite fallback is provided: production and
local development must set DATABASE_URL.
"""
from __future__ import annotations

import os
import re
from urllib.parse import quote_plus, urlparse

try:
    import psycopg2
    from psycopg2 import IntegrityError
    from psycopg2.extras import RealDictCursor
except ImportError as exc:  # pragma: no cover - dependency is installed by requirements.txt
    psycopg2 = None
    RealDictCursor = None

    class IntegrityError(Exception):
        pass

    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


_INSERT_ID_TABLES = {"users", "reports"}
_QMARK_RE = re.compile(r"\?")
_LIMIT_MINUS_ONE_RE = re.compile(r"\bLIMIT\s+-1\s+OFFSET\s+(\d+)\b", re.IGNORECASE)
_INSERT_TABLE_RE = re.compile(r"^\s*INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)\b", re.IGNORECASE)


def _valid_database_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"): ]
    if not url.startswith(("postgresql://", "postgresql+psycopg2://")):
        raise RuntimeError("DATABASE_URL precisa ser uma URL PostgreSQL válida.")

    parsed = urlparse(url)
    host = (parsed.hostname or "").strip().lower()
    database = (parsed.path or "").lstrip("/").strip().lower()
    user = (parsed.username or "").strip().lower()
    password = (parsed.password or "").strip().lower()
    bad_hosts = {"host", "hostname", "host_real", "host_gerado", "hostvaigo"}
    bad_db = {"banco", "database", "nome_real_do_banco", "vaigodb_exemplo"}
    bad_values = {"senha", "senha_real", "password", "usuario", "usuario_real", "user"}
    if not host or host in bad_hosts or database in bad_db or user in bad_values or password in bad_values:
        raise RuntimeError(
            "DATABASE_URL contém placeholder. No Render, apague valores como HOST_GERADO/hostname/host "
            "e use a Internal Database URL real do PostgreSQL ou sincronize o render.yaml via Blueprint."
        )
    return url


def database_url() -> str:
    # 1) URL completa (Render/Neon/Supabase/etc.)
    url = _valid_database_url(os.environ.get("DATABASE_URL", ""))
    if url:
        return url

    # 2) Fallback padrão libpq: permite configurar os campos separados, sem montar URL manualmente.
    host = os.environ.get("PGHOST", "").strip()
    user = os.environ.get("PGUSER", "").strip()
    password = os.environ.get("PGPASSWORD", "").strip()
    database = os.environ.get("PGDATABASE", "").strip()
    port = os.environ.get("PGPORT", "5432").strip() or "5432"
    if all((host, user, password, database)):
        candidate = (
            f"postgresql://{quote_plus(user)}:{quote_plus(password)}@"
            f"{host}:{port}/{quote_plus(database)}"
        )
        return _valid_database_url(candidate)

    raise RuntimeError(
        "PostgreSQL não configurado. Defina DATABASE_URL com a Internal Database URL real do Render "
        "ou configure PGHOST, PGPORT, PGUSER, PGPASSWORD e PGDATABASE."
    )


def _rewrite_sql(sql: str) -> str:
    """Translate the tiny SQLite query dialect still used by application call sites."""
    rewritten = _LIMIT_MINUS_ONE_RE.sub(r"OFFSET \1", str(sql))
    rewritten = _QMARK_RE.sub("%s", rewritten)
    return rewritten


class CursorProxy:
    def __init__(self, cursor, lastrowid=None):
        self._cursor = cursor
        self.lastrowid = lastrowid

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor)

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def close(self):
        self._cursor.close()


class PostgresDB:
    def __init__(self, connection):
        self._connection = connection

    def execute(self, sql, params=()):
        query = _rewrite_sql(sql)
        params = tuple(params or ())

        # The legacy code reads cursor.lastrowid after inserting users/reports.
        # PostgreSQL exposes this through RETURNING instead.
        lastrowid = None
        match = _INSERT_TABLE_RE.match(query)
        wants_id = bool(match and match.group(1).lower() in _INSERT_ID_TABLES and " returning " not in query.lower())
        if wants_id:
            query = query.rstrip().rstrip(";") + " RETURNING id"

        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if wants_id:
            row = cursor.fetchone()
            if row:
                lastrowid = row.get("id")
        return CursorProxy(cursor, lastrowid=lastrowid)

    def executemany(self, sql, seq_of_params):
        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        cursor.executemany(_rewrite_sql(sql), seq_of_params)
        return CursorProxy(cursor)

    def executescript(self, script):
        # psycopg2 can execute a semicolon-separated DDL script in one call.
        cursor = self._connection.cursor()
        cursor.execute(script)
        cursor.close()

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


def connect_db() -> PostgresDB:
    if psycopg2 is None:
        raise RuntimeError(
            "psycopg2 não está instalado. Execute pip install -r requirements.txt antes de iniciar o VAIGO."
        ) from _IMPORT_ERROR
    connection = psycopg2.connect(
        database_url(),
        connect_timeout=max(3, min(30, int(os.environ.get("DATABASE_CONNECT_TIMEOUT", "10") or 10))),
        application_name="vaigo",
    )
    connection.autocommit = False
    return PostgresDB(connection)


def table_columns(db: PostgresDB, table_name: str) -> set[str]:
    rows = db.execute(
        """SELECT column_name
           FROM information_schema.columns
           WHERE table_schema = current_schema() AND table_name = ?""",
        (table_name,),
    ).fetchall()
    return {str(row["column_name"]) for row in rows}
