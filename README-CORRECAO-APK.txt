VAIGO — CORREÇÃO DO LOGIN DO APK / ERRO 404
================================================

CAUSA CONFIRMADA
----------------
O APK atual abre:
  /mobile/entry

e usa:
  /mobile/auth/google/start
  /mobile/auth/exchange

O backend atual do site não possui essas rotas. Por isso o APK abre em 404.

O QUE ESTE PATCH FAZ
--------------------
1. Adiciona /mobile/entry.
2. Reaproveita o login Google web já existente (/login/google).
3. Depois do login no navegador, volta para:
     vaigo://auth/callback
4. Usa PKCE (state + verifier/challenge) para validar que o retorno pertence
   ao APK que iniciou o login.
5. Entrega ao WebView o mesmo remember-token persistente usado pelo site.
6. Não muda o fluxo de login normal do navegador.
7. Mantém o Start Command atual do Render: gunicorn app:app

COMO APLICAR
------------
Extraia/copiei estes arquivos para a RAIZ do repositório do site:
  mobile_routes.py
  apply_mobile_fix.py

Depois, dentro do repositório:

  python3 apply_mobile_fix.py
  python3 -m py_compile app.py mobile_routes.py

Confira:

  git diff -- app.py mobile_routes.py

Depois:

  git add -- app.py mobile_routes.py
  git commit -m "Fix Android mobile login bridge"
  git push origin main

O Render deverá fazer deploy automaticamente.

VARIÁVEL NO RENDER
------------------
Opcional, porque já existe um valor padrão correto:

  VAIGO_MOBILE_RETURN_URI=vaigo://auth/callback

Se quiser deixar explícito, adicione essa variável no Render.
NÃO altere GOOGLE_REDIRECT_URI para vaigo://...
O callback OAuth do Google continua sendo o callback HTTPS normal do site,
por exemplo:
  https://vaigo.online/login/google/callback

COMO TESTAR DEPOIS DO DEPLOY
----------------------------
Abra no navegador:

  https://vaigo.online/mobile/health

Deve responder algo parecido com:
  {"ok":true,"mobile_bridge":true,"google_configured":true,"entry":"/mobile/entry"}

Depois teste:
  https://vaigo.online/mobile/entry

Sem login, deve redirecionar para /login em vez de retornar 404.

IMPORTANTE
----------
O APK Android que você já compilou está compatível com essas rotas:
  - VAIGO_BASE_URL=https://vaigo.online
  - MOBILE_RETURN_URI=vaigo://auth/callback

Não precisa recompilar o APK apenas por causa do 404, desde que ele seja a
versão que contém o fluxo /mobile/auth/* e o deep link vaigo://auth/callback.
