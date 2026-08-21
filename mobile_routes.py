from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
from urllib.parse import urlencode

from flask import jsonify, redirect, request, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


_STATE_RE = re.compile(r"^[A-Za-z0-9_-]{20,200}$")
_CHALLENGE_RE = re.compile(r"^[A-Za-z0-9_-]{40,100}$")
_VERIFIER_RE = re.compile(r"^[A-Za-z0-9._~-]{20,200}$")


def _b64url_sha256(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def register_mobile_routes(app, core: dict) -> None:
    """Registra a ponte de autenticação entre o site VAIGO e o APK Android.

    O fluxo usa o OAuth Google já existente no app.py. O APK gera state/verifier,
    envia apenas state + challenge ao servidor, abre o Google no navegador e,
    depois do callback web, o servidor devolve um código curto para o deep link
    vaigo://auth/callback. O APK troca esse código usando o verifier original.
    """

    google_ready = core["google_ready"]
    current_user = core["current_user"]
    onboarding_needed = core["onboarding_needed"]
    issue_persistent_login = core["issue_persistent_login"]
    get_db = core["get_db"]
    rate_limit = core["rate_limit"]
    remember_cookie_name = core["REMEMBER_COOKIE_NAME"]
    remember_login_days = int(core["REMEMBER_LOGIN_DAYS"])

    allowed_return_uri = os.environ.get(
        "VAIGO_MOBILE_RETURN_URI", "vaigo://auth/callback"
    ).strip() or "vaigo://auth/callback"

    start_serializer = URLSafeTimedSerializer(
        app.config["SECRET_KEY"], salt="vaigo-mobile-start-v1"
    )
    code_serializer = URLSafeTimedSerializer(
        app.config["SECRET_KEY"], salt="vaigo-mobile-code-v1"
    )

    @app.get("/mobile/entry")
    def mobile_entry():
        """Entrada estável do APK: login se anônimo, app normal se autenticado."""
        user = current_user()
        if not user or not user["is_active"]:
            return redirect(url_for("login"))
        if onboarding_needed(user):
            return redirect(url_for("onboarding", next=url_for("index")))
        return redirect(url_for("index"))

    @app.get("/mobile/auth/google/start")
    def mobile_auth_google_start():
        """Abre o OAuth web existente e preserva o state/challenge do APK."""
        if not google_ready():
            return jsonify({
                "ok": False,
                "error": "google_not_configured",
                "message": "Login com Google não configurado no servidor.",
            }), 503

        if not rate_limit("mobile-google-start", 20, 60):
            return jsonify({"ok": False, "error": "rate_limited"}), 429

        state = (request.args.get("state") or "").strip()
        challenge = (request.args.get("challenge") or "").strip()
        return_uri = (request.args.get("return_uri") or "").strip()

        if (
            not _STATE_RE.fullmatch(state)
            or not _CHALLENGE_RE.fullmatch(challenge)
            or return_uri != allowed_return_uri
        ):
            return jsonify({"ok": False, "error": "invalid_mobile_auth_request"}), 400

        ticket = start_serializer.dumps({
            "state": state,
            "challenge": challenge,
            "return_uri": return_uri,
            "nonce": secrets.token_urlsafe(16),
        })

        finish_path = url_for("mobile_auth_google_finish", ticket=ticket)
        return redirect(url_for("google_login", next=finish_path))

    @app.get("/mobile/auth/google/finish")
    def mobile_auth_google_finish():
        """Chamado pelo callback web depois que o Google autenticou o usuário."""
        user = current_user()
        if not user or not user["is_active"]:
            return redirect(url_for("login"))

        ticket = (request.args.get("ticket") or "").strip()
        try:
            payload = start_serializer.loads(ticket, max_age=15 * 60)
        except SignatureExpired:
            return redirect(url_for("login"))
        except BadSignature:
            return jsonify({"ok": False, "error": "invalid_mobile_ticket"}), 400

        state = str(payload.get("state") or "")
        challenge = str(payload.get("challenge") or "")
        return_uri = str(payload.get("return_uri") or "")

        if (
            not _STATE_RE.fullmatch(state)
            or not _CHALLENGE_RE.fullmatch(challenge)
            or return_uri != allowed_return_uri
        ):
            return jsonify({"ok": False, "error": "invalid_mobile_ticket"}), 400

        code = code_serializer.dumps({
            "uid": int(user["id"]),
            "state": state,
            "challenge": challenge,
            "nonce": secrets.token_urlsafe(24),
        })

        callback_url = f"{return_uri}?{urlencode({'code': code, 'state': state})}"
        response = redirect(callback_url)
        response.headers["Cache-Control"] = "no-store, max-age=0"
        return response

    @app.post("/mobile/auth/exchange")
    def mobile_auth_exchange():
        """Troca código + verifier PKCE por um remember-token do site."""
        if not rate_limit("mobile-auth-exchange", 30, 60):
            return jsonify({"ok": False, "error": "rate_limited"}), 429

        data = request.get_json(silent=True) or {}
        code = str(data.get("code") or "").strip()
        state = str(data.get("state") or "").strip()
        verifier = str(data.get("verifier") or "").strip()

        if (
            not code
            or not _STATE_RE.fullmatch(state)
            or not _VERIFIER_RE.fullmatch(verifier)
        ):
            return jsonify({"ok": False, "error": "invalid_exchange_request"}), 400

        try:
            payload = code_serializer.loads(code, max_age=5 * 60)
        except SignatureExpired:
            return jsonify({"ok": False, "error": "mobile_code_expired"}), 400
        except BadSignature:
            return jsonify({"ok": False, "error": "invalid_mobile_code"}), 400

        expected_state = str(payload.get("state") or "")
        challenge = str(payload.get("challenge") or "")
        uid = payload.get("uid")

        if not hmac.compare_digest(state, expected_state):
            return jsonify({"ok": False, "error": "state_mismatch"}), 400

        calculated_challenge = _b64url_sha256(verifier)
        if not challenge or not hmac.compare_digest(calculated_challenge, challenge):
            return jsonify({"ok": False, "error": "pkce_mismatch"}), 400

        try:
            uid = int(uid)
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "invalid_user"}), 400

        user = get_db().execute(
            "SELECT id,is_active FROM users WHERE id=? LIMIT 1", (uid,)
        ).fetchone()
        if not user or not user["is_active"]:
            return jsonify({"ok": False, "error": "user_unavailable"}), 403

        remember_token = issue_persistent_login(uid)
        max_age = remember_login_days * 24 * 60 * 60

        response = jsonify({
            "ok": True,
            "cookie_name": remember_cookie_name,
            "remember_token": remember_token,
            "max_age": max_age,
            "entry": "/mobile/entry",
        })
        response.headers["Cache-Control"] = "no-store, max-age=0"
        return response

    @app.get("/mobile/health")
    def mobile_health():
        return jsonify({
            "ok": True,
            "mobile_bridge": True,
            "google_configured": bool(google_ready()),
            "entry": "/mobile/entry",
        })
