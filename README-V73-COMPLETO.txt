VAIGO V73 — PACOTE COMPLETO ESTÁVEL

CONTEÚDO
- Backend Flask/SQLite estável atual
- Ponte Android/mobile OAuth registrada
- Frontend completo (templates + static)
- Mapa com V69 + V70 + V71
- Perfil V72 moderno
- Render config + requirements

IMPORTANTE
1. Este ZIP NÃO inclui wesafe.db para não sobrescrever dados de produção.
   - Se você extrair por cima do clone atual, seu wesafe.db existente fica intacto.
   - Em instalação nova, app.py cria o SQLite automaticamente.
   - Em produção, prefira um disco persistente e WESAFE_DB/RENDER_DISK_PATH.

2. Não altere GOOGLE_REDIRECT_URI para vaigo://...
   O callback Google continua HTTPS:
   https://vaigo.online/login/google/callback

3. O retorno para o APK usa:
   VAIGO_MOBILE_RETURN_URI=vaigo://auth/callback

4. O backend deste pacote foi conferido contra o repositório estável:
   app.py git blob: 01f8715c9eade4296270fcf5ad3cad97cd1cff1a
   mobile_routes.py git blob: f4f2197bdb77be1eb8ec6f9612c47997b4124980
   requirements.txt git blob: 62fdeeb3ec7aeb6c61f7de3768a4b5beb81afc6a
   render.yaml git blob: 7f59f41eba94d9b28c4e204e79932ed81cbfd896
