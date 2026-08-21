from pathlib import Path
import sys

APP = Path("app.py")
MOBILE = Path("mobile_routes.py")

if not APP.exists():
    raise SystemExit("ERRO: app.py não encontrado. Rode este script na raiz do repositório VAIGO.")
if not MOBILE.exists():
    raise SystemExit("ERRO: mobile_routes.py não encontrado na raiz do repositório.")

text = APP.read_text(encoding="utf-8")

marker = "# VAIGO_ANDROID_MOBILE_BRIDGE_V1"
block = f"""
{marker}
from mobile_routes import register_mobile_routes as _register_vaigo_mobile_routes
_register_vaigo_mobile_routes(app, globals())
# /VAIGO_ANDROID_MOBILE_BRIDGE_V1

"""

if marker in text:
    print("OK: app.py já possui a ponte mobile. Nada alterado.")
    raise SystemExit(0)

needle = "\nstart_keepalive_worker()\n"
if needle in text:
    text = text.replace(needle, "\n" + block + "start_keepalive_worker()\n", 1)
else:
    main_needle = '\nif __name__ == "__main__":\n'
    if main_needle not in text:
        raise SystemExit("ERRO: não encontrei ponto seguro para inserir a ponte mobile no app.py.")
    text = text.replace(main_needle, "\n" + block + main_needle, 1)

backup = APP.with_suffix(".py.before-mobile-fix")
if not backup.exists():
    backup.write_text(APP.read_text(encoding="utf-8"), encoding="utf-8")

APP.write_text(text, encoding="utf-8")
print("OK: app.py corrigido.")
print(f"Backup: {backup}")
print("Rotas adicionadas:")
print("  /mobile/entry")
print("  /mobile/auth/google/start")
print("  /mobile/auth/google/finish")
print("  /mobile/auth/exchange")
print("  /mobile/health")
