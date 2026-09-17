# V0.4-S8 — Resultado BCR-1 e leituras V0.4

- Data: 17 de setembro de 2026.
- Resultado oficial: **PASS** em três execuções independentes.
- Evidência bruta: `quality/v04-s8-bcr1-result.json`.
- Baseline de gravações: `quality/v04-s8-bcr1-baseline.json`.

## Parâmetros preservados

- Seed: `20260909`.
- Por execução: 10.000 questões, 100.000 attempts, 100.000 reviews e 200 itens
  por nível taxonômico.
- Histórico sintético: 2016-09-09 a 2026-09-06.
- Três bancos SQLite dedicados e removidos depois da captura.
- Por operação: 20 warm-ups excluídos e 100 amostras medidas.
- p95: nearest-rank, posição `ceil(0,95 * N)`.
- Threshold oficial de CT-107: 2 s por gravação.
- Thresholds vigentes: 3 s para tela e 2 s para busca/filtro. Leituras sem
  threshold formal ficaram `OBSERVED`, nunca receberam PASS arbitrário.
- Ambiente: Windows 11, Python 3.13.15, Django 5.2.17, SQLite 3.53.1, 8 CPUs
  lógicas e 16 GiB de RAM; execução single-process e sequencial.

O fingerprint do dataset foi idêntico nas três execuções. Os SHA-256 são
gravados em grupos separados por `:` para permanecerem completos e reversíveis
sem disparar falso positivo de segredo hexadecimal.

## Gravações oficiais

| Execução | `save_question` p95 | `save_attempt` p95 | `complete_review` p95 |
| --- | ---: | ---: | ---: |
| baseline 1 / final 1 | 0,0247 / 0,0403 s | 0,0254 / 0,0236 s | 0,0316 / 0,0334 s |
| baseline 2 / final 2 | 0,0242 / 0,1119 s | 0,0288 / 0,0839 s | 0,0272 / 0,0708 s |
| baseline 3 / final 3 | 0,0245 / 0,0427 s | 0,0180 / 0,0219 s | 0,0290 / 0,0401 s |

Todas ficaram abaixo de 2 s; CT-107 terminou `PASS` nas três execuções.

## Leituras V0.4

Faixa de p95 observada nas três execuções:

| Leitura | Queries por amostra | p95 mínimo–máximo | Decisão |
| --- | ---: | ---: | --- |
| dashboard | 15 | 1,7501–1,8390 s | PASS, limite 3 s |
| resumo analytics S2 | 14 | 1,5554–1,7992 s | OBSERVED |
| fila de revisões | 3 | 0,9040–1,0279 s | PASS, limite 3 s |
| listagem | 8 | 0,0852–0,1102 s | PASS, limite 3 s |
| busca | 8 | 0,1275–0,1426 s | PASS, limite 2 s |
| filtros | 9 | 0,0770–0,1008 s | PASS, limite 2 s |
| busca + filtros | 9 | 0,0663–0,0792 s | PASS, limite 2 s |
| página posterior | 8 | 0,3607–0,4097 s | PASS, limite 3 s |
| detalhe | 6 | 0,0104–0,0143 s | OBSERVED |
| timeline | 7 | 0,0143–0,0170 s | OBSERVED |
| dashboard após gravação | 15 | 1,6190–1,7904 s | PASS, limite 3 s |

As contagens de queries permaneceram constantes por operação, sem crescimento
por linha. A paginação percorreu 800 páginas e 8.000 questões ativas em cada
execução: 8.000 IDs observados, 8.000 únicos, zero duplicação/omissão, 2.403
queries constantes no percurso e fingerprint de ordering idêntico. Tempos do
percurso completo: 78,828 s, 79,605 s e 82,286 s.

Uma amostra suplementar no candidato final, depois do review, executou uma
leitura fria, 5 warm-ups e 20 amostras: dashboard p50 1,315 s, p95 1,529 s,
15 queries e `PASS` sob o limite de 3 s. Ela não substitui nem reclassifica o
BCR-1 oficial acima.

## Findings e correções

- **S8-F001 Major, resolvido:** dashboard inicial de 9,6338 s excedia 3 s por
  agregações reversas repetidas. A correção mínima combinou os dois níveis de
  desempenho em uma passagem e removeu trabalho redundante, preservando os
  read models e a semântica S1/S2. Diagnóstico imediato após a correção: 1,263
  s e 15 queries; BCR final confirmado acima.
- **S8-F002 Major, resolvido:** o gerador BCR produzia 108.026 findings S5 por
  data civil UTC e cadeia de reviews artificial incompatível com a política.
  O dataset passou a usar `America/Sao_Paulo` e uma cadeia D1/reset válida. O
  teste reduzido exige zero findings; o candidato completo terminou S5 exit 0.
- Incidentes de harness separados de defeito de produto: host padrão do client,
  expectativa inicial de filtro e uma asserção de encoding foram corrigidos
  antes da evidência final.

Não houve alteração de threshold, descarte de amostra, cache, schema ou
migration para obter o resultado.
