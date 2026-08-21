# VAIGO — Navegação adaptativa


## VAIGO V50 — novo branding

Esta build muda a marca pública para **VAIGO** e aplica um design system claro: Indigo `#5B5CE2`, branco, fundo `#F6F7FB` e menta `#2CC7A0`. Splash, autenticação, onboarding, perfil, HUD e rota ativa seguem a mesma linguagem visual.

Visitantes podem calcular **10 novos trajetos sem login**. Recalcular, trocar o modo da mesma viagem ou atualizar a rota pelo GPS não consome outro crédito.

O roteamento e a busca continuam **Mapbox-only**, com geocodificação global e suporte a endereços/códigos postais europeus.

> Identificadores internos antigos (`SPARK_*`, algumas classes e chaves de storage) foram mantidos de propósito para não quebrar deploys, sessões e preferências já salvas.

## Novidades X3

- busca de rua/endereço/CEP/CEP + número com validação forte de número e CEP;
- uso de ponto navegável e entrada de edifício quando fornecidos pelo geocoder;
- novo marcador de chegada;
- layout mobile mais compacto, com safe areas revisadas;
- Safety Engine V3 baseado em exposição do corredor, hotspots, zonas e incerteza dos dados;
- score conservador separado do risco observado.

Aplicação Flask + SQLite, mobile-first, com Mapbox, navegação em terceira pessoa, cálculo de rotas, trânsito, micro-rotas, contexto de segurança, alertas comunitários e compartilhamento de trajeto.

## O que mudou nesta build

### Navegação em terceira pessoa

A câmera foi refeita para trabalhar como acompanhamento real de rota: o usuário fica visualmente mais baixo na tela e a câmera mira um ponto adiante da geometria. O bearing vem da própria linha da rota, há look-ahead variável por velocidade e a câmera antecipa curvas fechadas ajustando horizonte e zoom.

Também existe **Prévia 3D**, que anima a câmera sobre a rota calculada sem usar o GPS. Ela serve para conferir rapidamente o comportamento visual antes de sair.

### VAIGO Intelligence + Safety Engine

Cada alternativa recebe um `spark_score` explicável. O motor combina, dentro das alternativas daquela viagem:

- segurança estimada;
- ETA relativo;
- trânsito no modo carro;
- tamanho do desvio;
- confiança dos dados disponíveis;
- incidentes e fechamentos;
- micro-rota, quando aplicável.

O motor retorna `score_breakdown`, `decision_reasons` e `decision_confidence`. A confiança de dados não é confundida com segurança: ausência de relatos não vira uma garantia artificial.

Quando o usuário está autenticado, escolhas recentes da própria conta podem ajustar suavemente os pesos. O dispositivo também mantém preferências locais conforme a pessoa usa Segura, Mais rápida ou Equilibrada.

### HUD e orientação

- próxima manobra com glyph próprio;
- lane guidance quando as faixas chegam no dado de roteamento;
- voz em estágios de aproximação;
- risco/contexto relevante à frente da rota;
- velocidade média, ETA, distância restante e progresso;
- Road Awareness para sinalização mapeada;
- monitoramento de trânsito e sugestão de nova rota sem troca automática;
- recálculo quando o aparelho permanece fora da rota.

### Safety Toolkit

Durante a navegação há um painel de segurança com:

- **Ao vivo:** cria link temporário de acompanhamento;
- **Pontos de apoio:** procura polícia, bombeiros, hospital, clínica, farmácia, posto e conveniência mapeados próximos;
- **Compartilhar SOS:** compartilha posição/link com alguém de confiança;
- **Estou bem:** check-in com localização;
- **Safety Pulse:** heatmap opcional dos alertas recentes carregados no mapa.

O botão SOS não liga nem aciona automaticamente serviços públicos. Pontos de apoio são apenas locais mapeados e não são classificados pelo sistema como garantidamente seguros.

## Compartilhamento ao vivo

O link ao vivo é criado somente por usuário autenticado, usa token aleatório e expira em 6 horas. O criador envia posição/progresso durante a navegação e o token é encerrado quando o trajeto termina. A página pública não mostra nome ou e-mail da conta.

## Rotas e segurança

Perfis:

- carro (`driving-traffic`);
- moto sobre o grafo motorizado do Mapbox, com ajustes próprios de cálculo.

Modos:

- **Segura**;
- **Mais rápida**;
- **Equilibrada**.

O nível 0–5 considera alertas recentes, gravidade, recência, confirmações, distância ao corredor da rota, zonas de atenção cadastradas e contexto temporal quando aplicável. O sistema não usa tipo de comunidade ou nome de bairro como proxy de criminalidade.

> O nível de segurança é uma estimativa e não garante ausência de risco. Sinalização, trânsito, limites de velocidade e pontos de apoio também dependem da cobertura cartográfica disponível; a sinalização real da via sempre prevalece.

## Rodar localmente

```bash
pip install -r requirements.txt
python app.py
```

Abra `http://127.0.0.1:5000`.

## Render

Build:

```bash
pip install -r requirements.txt
```

Start:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
```

Enquanto usar SQLite, mantenha uma única instância de escrita. Para escalar horizontalmente, prefira migrar o banco para PostgreSQL.

### Variáveis principais

- `WESAFE_SECRET_KEY`
- `WESAFE_ADMIN_EMAIL`
- `WESAFE_ADMIN_PASSWORD`
- `MAPBOX_ACCESS_TOKEN`
- `MAPBOX_STYLE` (opcional)
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `OVERPASS_URL` (opcional)

## Arquivos principais

- `app.py` — backend, banco, APIs, inteligência de rota, live sharing e dados contextuais.
- `templates/index.html` — mapa, câmera, HUD, Safety Toolkit e navegação.
- `templates/live_trip.html` — acompanhamento público temporário.
- `wesafe.db` — banco SQLite de demonstração; novas tabelas são criadas automaticamente.
- `CHANGELOG-X3.md` — lista detalhada das alterações desta build.
- `SAFETY-ENGINE-X3.md` — arquitetura do motor de segurança.
- `TESTS-X3.md` — validações executadas nesta build.
- `CHANGELOG-X2.md` / `TESTS-X2.md` — histórico da versão anterior.

## Testes desta entrega

Consulte `TESTS-X2.md`. Foram executadas verificações de sintaxe Python/JavaScript, parse de templates, integridade de IDs de UI, schema SQLite e testes isolados do motor geométrico/de score.

## X17 — mapa ambiental automático

Configure no ambiente do Render:

```env
MAPBOX_STYLE_DAY=mapbox://styles/mapbox/standard
MAPBOX_STYLE_AFTERNOON=mapbox://styles/miguwl0287/cmixney1h001501s111340npb
MAPBOX_STYLE_NIGHT=mapbox://styles/miguwl0287/cmiwm8kse007v01s023vnadqb
MAPBOX_STYLE_RAIN=mapbox://styles/miguwl0287/cmszu604f001x01rw8gcyh06b
```

No modo **Mapa adaptativo**, chuva tem prioridade. Sem chuva: dia = Standard, 12h–17h59 = tarde, 18h–05h59 = noite. O endpoint `/api/weather-now` usa o Open-Meteo existente e cache do backend; nenhuma nova API key é necessária.


## X18 — Traffic Intelligence

- `mapbox://mapbox.mapbox-traffic-v1` is rendered directly as a vector traffic overlay; moderate/heavy/severe traffic follows the actual road geometry.
- `driving-traffic` route annotations (`congestion_numeric`) paint the selected route segment-by-segment, so congested pieces turn orange/red above the normal route.
- Street-level corridor summaries use existing Directions steps, avoiding reverse-geocoding calls just to name traffic.
- Traffic Radar surfaces the next relevant slowdown up to roughly 1.8 km ahead.
- Normal reroute suggestions require about 2 minutes of savings; severe congestion/closure can lower that threshold while safety constraints remain active outside Fast mode.
- Live driving provider responses are only deduplicated for a few seconds; map tiles, geocoding, weather, signs and other non-critical context retain longer caches.


## Mapbox global + Europa (V48)
O Mapbox é o provedor ativo de busca/geocodificação e rotas. Endereços não ficam mais presos ao Brasil: consultas europeias podem usar rua, número, cidade, país e formatos locais de código postal. Quando o país é informado explicitamente, a busca não usa o GPS atual como viés, evitando que um endereço europeu seja puxado para resultados brasileiros. CEP brasileiro continua com enriquecimento ViaCEP/BrasilAPI, mas a navegação e a validação final usam Mapbox. Carro e moto usam o grafo motorizado do Mapbox; o VAIGO expande as alternativas com microrrotas por quarteirões/corredores próximos.
