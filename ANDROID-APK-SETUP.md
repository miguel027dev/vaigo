# Backend para VAIGO Android

Variáveis adicionais no Render:

```text
MOBILE_AUTH_RETURN_URI=vaigo://auth/callback
MOBILE_AUTH_TTL_SECONDS=300
```

Mantenha as variáveis existentes, principalmente:

```text
DATABASE_URL=...
SECRET_KEY=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://SEU-DOMINIO/login/google/callback
MAPBOX_ACCESS_TOKEN=...
```

O callback do Google permanece HTTPS. `vaigo://auth/callback` só é usado depois que o backend concluiu o OAuth.
