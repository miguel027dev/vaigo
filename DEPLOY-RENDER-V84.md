# Deploy rápido — VAIGO V84

1. Suba este projeto para um repositório GitHub.
2. No Render, escolha **New > Blueprint**.
3. Conecte o repositório.
4. O Render lerá `render.yaml` e criará:
   - `vaigo` (web service)
   - `vaigo-postgres` (PostgreSQL)
5. Informe apenas os secrets solicitados (`MAPBOX_ACCESS_TOKEN`, admin e owner).
6. A variável `DATABASE_URL` será criada automaticamente a partir do PostgreSQL.
7. Após o deploy, adicione `vaigo.online` em **Settings > Custom Domains** do serviço web.

## DATABASE_URL

Você não precisa montar essa URL manualmente no Blueprint.
Depois que o PostgreSQL existir, o Render mostrará a connection string real no painel do banco em **Connect**.
O backend recebe automaticamente essa mesma connection string interna em `DATABASE_URL`.
