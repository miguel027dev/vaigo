# Spark X3 — Render Hotfix (18/08/2026)

## Corrigido: HTTP 500 na home

A build X3 chamava `mapbox_ready()` em `/`, compartilhamento e live trip, mas a função havia sido removida durante a refatoração do geocoder. Isso causava:

`NameError: name 'mapbox_ready' is not defined`

O helper foi restaurado e agora valida o token sem expô-lo.

## Corrigido: Google OAuth retornando HTTP 400

O callback recebia `state` + `code`, mas abortava com 400 antes da troca de token quando a sessão Flask não retornava ao callback. Esse caso é especialmente relevante porque o Spark suporta iframe e usa cookie de sessão `Partitioned`.

A correção mantém três camadas de validação:

1. state da sessão Flask, quando disponível;
2. cookie OAuth separado, assinado por HMAC, `Secure`, `HttpOnly`, `SameSite=Lax`, expiração de 12 minutos;
3. registro de state de uso único no SQLite, com expiração e fingerprint hash do cliente como fallback para navegadores/WebViews que descartem o cookie no redirecionamento.

O state persistido é consumido no callback e não pode ser reutilizado.

O `redirect_uri` utilizado no início da autorização também fica associado à transação e é reutilizado na troca do código, evitando divergência caso a sessão seja perdida.

## Health check

`/healthz` agora verifica:

- acesso ao SQLite;
- compilação/carregamento do template `index.html`;
- helper de configuração do Mapbox;
- helper de configuração do Google.

Nenhuma chamada externa é feita no health check.

## Render / Google

Para o domínio mostrado nos logs, mantenha no Render:

`GOOGLE_REDIRECT_URI=https://wesafe-c7kg.onrender.com/login/google/callback`

E a MESMA URI deve estar cadastrada como URI de redirecionamento autorizada no cliente OAuth do Google.

## Validações locais

- `python -m py_compile app.py`: OK
- schema SQLite incluindo `oauth_states`: OK
- `mapbox_ready()` presente e com todos os call sites resolvidos: OK
- JavaScript inline de `index.html`: Node syntax OK
- JavaScript inline de `map.html`: Node syntax OK
- JavaScript inline de `live_trip.html`: Node syntax OK
- JavaScript inline de `shared_route.html`: Node syntax OK

O ambiente de build não possui Flask/Werkzeug e não possui acesso à internet para instalá-los, então não foi possível iniciar um servidor Flask real dentro do container. A validação final HTTP deve ser feita após o deploy no Render.
