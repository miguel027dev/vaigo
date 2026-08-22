"""PostgreSQL backend for VAIGO.

Production storage is PostgreSQL only. The app keeps its historical ``db.execute``
call style, while this adapter translates the small amount of SQLite-style
placeholder syntax that remains in call sites.

Connection priority:
1. PGHOST/PGPORT/PGUSER/PGPASSWORD/PGDATABASE (ideal for Render Blueprint wiring)
2. DATABASE_URL (Render/Neon/Supabase/other PostgreSQL providers)

There is intentionally no SQLite fallback, because Render web-service filesystems
are ephemeral and user data must survive redeploys.
"""
from __future__ import annotations

import os
import re
from urllib.parse import quote, urlparse

try:
    import psycopg2
    from psycopg2 import IntegrityError
    from psycopg2.extras import RealDictCursor
except ImportError as exc:  # dependency is installed by requirements.txt
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
_BAD_HOSTS = {"host", "hostname", "host_real", "host_gerado", "hostvaigo"}
_BAD_DATABASES = {"banco", "database", "nome_real_do_banco", "vaigodb_exemplo"}
_BAD_VALUES = {"senha", "senha_real", "password", "usuario", "usuario_real", "user"}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _validate_parts(host: str, user: str, password: str, database: str) -> None:
    host_l = _clean(host).lower()
    user_l = _clean(user).lower()
    password_l = _clean(password).lower()
    database_l = _clean(database).lower()
    if not all((host_l, user_l, password_l, database_l)):
        raise RuntimeError("Configuração PostgreSQL incompleta.")
    if host_l in _BAD_HOSTS or user_l in _BAD_VALUES or password_l in _BAD_VALUES or database_l in _BAD_DATABASES:
        raise RuntimeError(
            "Configuração PostgreSQL contém placeholder. Use as credenciais reais do banco ou o Blueprint do Render."
        )


def _url_from_pg_env() -> str:
    """Build a PostgreSQL URL from standard libpq PG* environment variables."""
    host = _clean(os.environ.get("PGHOST"))
    user = _clean(os.environ.get("PGUSER"))
    password = _clean(os.environ.get("PGPASSWORD"))
    database = _clean(os.environ.get("PGDATABASE"))
    port = _clean(os.environ.get("PGPORT")) or "5432"
    if not any((host, user, password, database)):
        return ""
    _validate_parts(host, user, password, database)
    if not port.isdigit():
        raise RuntimeError("PGPORT precisa ser numérica.")
    return (
        f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}@"
        f"{host}:{port}/{quote(database, safe='')}"
    )


def _valid_database_url(url: str) -> str:
    url = _clean(url)
    if not url:
        return ""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if not url.startswith(("postgresql://", "postgresql+psycopg2://")):
        raise RuntimeError("DATABASE_URL precisa ser uma URL PostgreSQL válida.")

    parsed = urlparse(url)
    host = parsed.hostname or ""
    database = (parsed.path or "").lstrip("/")
    user = parsed.username or ""
    password = parsed.password or ""
    _validate_parts(host, user, password, database)
    return url


def database_url() -> str:
    # Prefer standard PG* vars. The Render Blueprint injects these from the
    # managed database and they also let the app recover from a stale manual
    # DATABASE_URL left on an older Web Service.
    pg_url = _url_from_pg_env()
    if pg_url:
        return pg_url

    url = _valid_database_url(os.environ.get("DATABASE_URL", ""))
    if url:
        return url

    raise RuntimeError(
        "PostgreSQL não configurado. Use o render.yaml como Blueprint (recomendado) "
        "ou defina DATABASE_URL com a URL real do seu PostgreSQL."
    )


def _rewrite_sql(sql: str) -> str:
    """Translate the tiny legacy query dialect still used by application call sites."""
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
        lastrowid = None
        match = _INSERT_TABLE_RE.match(query)
        wants_id = bool(
            match
            and match.group(1).lower() in _INSERT_ID_TABLES
            and " returning " not in query.lower()
        )
        if wants_id:
            query = query.rstrip().rstrip(";") + " RETURNING id"

        cursor = self._connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params if params else None)
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
