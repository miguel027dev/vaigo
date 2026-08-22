# VAIGO + PostgreSQL persistente no Render

## Caminho recomendado: Blueprint

1. Suba este projeto para o GitHub.
2. No Render: **New > Blueprint**.
3. Selecione o repositório e o `render.yaml` da raiz.
4. O Render cria dois recursos separados:
   - `vaigo` (web service)
   - `vaigo-postgres` (PostgreSQL)
5. O Render injeta automaticamente `DATABASE_URL`, `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD` e `PGDATABASE`.
6. Preencha apenas os secrets solicitados na criação do Blueprint.

O código usa `CREATE TABLE IF NOT EXISTS` e migrações aditivas. Fazer deploy de uma nova versão do web service não recria nem apaga o PostgreSQL.

## Se você continuar usando um Web Service criado manualmente

Crie/conecte um PostgreSQL persistente e configure **uma** destas opções:

- `DATABASE_URL` = URL PostgreSQL real; ou
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`.

Não use `host`, `hostname`, `HOST_GERADO`, `SENHA` ou outros placeholders.

## Observação sobre o plano gratuito do Render

O Blueprint usa `plan: free` para não gerar cobrança automaticamente. O banco gratuito do Render é temporário; para armazenamento de usuários de produção por prazo longo, faça upgrade do `vaigo-postgres` para um plano persistente pago antes da expiração do plano gratuito.
