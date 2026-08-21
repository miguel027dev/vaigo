# Spark Live Road X4

O X4 adiciona uma camada dinâmica de contexto à navegação sem exigir novas chaves de API além do Mapbox que o projeto já utiliza para mapa/roteamento.

## Fontes adicionadas

### Open-Meteo
- Sem chave no endpoint padrão usado pelo projeto.
- Condições atuais: chuva/precipitação, visibilidade, vento, rajadas, temperatura e código meteorológico.
- O Spark converte essas variáveis em um **contexto meteorológico de condução**. Não é uma medição de pista nem garantia de condição da rua.

### OpenStreetMap + Overpass
- Consulta atributos mapeados próximos ao corredor: obra, barreira, pavimento ruim, superfície não pavimentada, trecho sem iluminação, ford/risco de água, hazard e redutores.
- Esses itens aparecem no mapa como **dados mapeados**. Eles não são apresentados como ocorrências instantâneas.
- Obras/barreiras/trechos com água de severidade alta podem ser usados pelo servidor como candidatos para procurar um pequeno desvio alternativo.

### Spark Community
- Continua usando alertas recentes do próprio Spark.
- A interface distingue relato comunitário de informação mapeada.

### Spark Live Flow
- Fluxo colaborativo anônimo criado pelo próprio app.
- Durante navegação de carro, o dispositivo envia no máximo uma amostra aproximadamente a cada 30 segundos.
- A coordenada é quantizada para uma célula aproximada (~centenas de metros); a coordenada GPS exata não é salva nessa tabela.
- Não há `user_id` na tabela de fluxo.
- O identificador da fonte é efêmero e derivado da sessão.
- Uma célula só é publicada no mapa/algoritmo quando existem **pelo menos 3 fontes distintas** recentes.
- Amostras usadas na leitura têm janela de 20 minutos e são removidas após 45 minutos.

## Trânsito

O trânsito de rota continua usando o provedor `driving-traffic` já configurado no projeto. O X4 adiciona:

1. segmentos coloridos sobre a rota;
2. agregação Spark Live Flow quando houver cobertura suficiente;
3. rechecagem periódica durante navegação;
4. micro-rota somente quando há ganho útil e a trava de segurança é preservada;
5. tentativa de contorno de obra/barreira/risco de água **mapeado**, com aviso de que o dado pode estar desatualizado.

## O que não é coletado

O Spark X4 **não consulta, armazena ou divulga localização de blitz/fiscalização policial**. O motor Live Road é voltado a trânsito, estado/contexto viário, clima, incidentes comunitários e navegação segura.

## UI mobile

Durante a navegação existe o bloco compacto **Spark Live Road** com:

- Tempo;
- Via;
- Fluxo;
- evento relevante mais próximo no corredor.

O mapa também recebe:

- halo colorido de trânsito por segmento;
- células agregadas do Spark Live Flow;
- pontos de contexto viário com diferenciação visual;
- popup explicando a origem/frescor do dado.

## Falhas externas

Open-Meteo e Overpass são tratados como enriquecimento. Se um deles estiver indisponível, rota, mapa e navegação continuam funcionando. O frontend mostra informação degradada em vez de quebrar a viagem.
