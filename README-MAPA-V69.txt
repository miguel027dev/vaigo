VAIGO V69 — MAP ONLY
====================

Este ZIP altera SOMENTE:
- templates/index.html
- static/vaigo-map-v69.css

NÃO contém:
- app.py
- requirements.txt
- banco de dados
- mobile_routes.py
- configurações do Render
- autenticação/login

Objetivo:
- corrigir margens e elementos encostando nas bordas;
- impedir texto sobre texto ou texto cortando ícones;
- bottom sheet/card inferior com gesto e animação mais fluidos;
- melhorar 340px, 390px, 430px e tablets;
- preservar o backend estável.

Para aplicar no repositório:
  unzip -o VAIGO-V69-MAPA-ONLY.zip -d ~/vaigo
  cd ~/vaigo
  git add templates/index.html static/vaigo-map-v69.css
  git commit -m "VAIGO V69 map mobile polish"
  git push origin main
