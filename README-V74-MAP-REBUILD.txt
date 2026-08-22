VAIGO V74 — REBUILD COMPLETO DA INTERFACE DO MAPA

O que mudou
- Interface visual do mapa reconstruída com uma nova camada V74.
- White como visual claro e Black opcional pelo botão no topo e pelo menu.
- Mesma identidade VAIGO: roxo #5B5CE2, superfícies limpas e tipografia simples.
- Mobile: bottom sheet com arraste, busca clara e controles grandes.
- Tablet/Desktop: o planner vira painel lateral para deixar o mapa sempre visível.
- Busca, confirmação de destino, escolha Carro/Moto/A pé, rota, estacionamento e navegação foram reestilizados.
- Resultados de busca usam contraste correto nos dois temas.
- Cards, margens, espaçamentos, textos e botões foram padronizados.
- Modo navegação ganhou HUD superior e resumo inferior mais simples.
- Feedback de rota ficou discreto.
- Aviso visual de recalculando continua oculto; a lógica de voz existente continua responsável pela informação ao usuário.
- Drawers de conta, preferências e segurança agora seguem o mesmo sistema visual.

Arquivos novos
- static/vaigo-map-v74.css
- static/vaigo-map-v74-ui.js

Arquivo atualizado
- templates/index.html

IMPORTANTE
- app.py não foi alterado.
- mobile_routes.py não foi alterado.
- render.yaml e requirements.txt não foram alterados.
- O banco wesafe.db não está incluído para não sobrescrever dados existentes no deploy.

Deploy recomendado
Extraia o ZIP dentro do repositório VAIGO e envie todos os arquivos para o GitHub/Render.
