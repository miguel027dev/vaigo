# VAIGO — PostgreSQL

Esta versão usa PostgreSQL exclusivamente.

## Render
Cadastre no painel Environment:

- `DATABASE_URL` = URL PostgreSQL completa
- `DATABASE_CONNECT_TIMEOUT` = `10` (opcional)

Não use mais `WESAFE_DB` nem arquivo `wesafe.db`.

O backend cria tabelas e índices faltantes com `CREATE ... IF NOT EXISTS` e executa apenas migrações aditivas de colunas. Os dados existentes no PostgreSQL não são apagados.

## Dependência
`requirements.txt` inclui `psycopg2-binary`.
