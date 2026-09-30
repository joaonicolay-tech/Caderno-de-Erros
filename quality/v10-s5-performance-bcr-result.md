# V1.0-S5 — Resultado parcial BCR-1 / BCR-2

**Estado:** `AUTHORIZED / BLOCKED / RETOMÁVEL — GPT-6.1 Sol Medium`
**S5:** não concluída; BCR-2 completo, fechamento bloqueado por gate RED em 30/09/2026.
**Motivo do checkpoint inicial:** o BCR-1 oficial terminou `FAIL` (exit code 1). A coleta foi
interrompida antes de BCR-2, gate, A8 ou qualquer alteração de código.

## Baseline e execução

Retomada em 29/09/2026 sob escalonamento humano autorizado. A execução inicial
abaixo permanece histórica e imutável; `quality/v10-s5-bcr1-diagnostic.json`
registra um `DIAGNOSTIC RUN`, sem substituir a evidência oficial inicial.

- HEAD = `origin/main` = `e3357d26e9c0165617bed221732fabe2db042995`.
- Antes do benchmark, os únicos arquivos modificados eram os contratos
  administrativos autorizados `tasks/current.md` e `PROJECT_STATE.md`.
- Comando: `.venv\Scripts\python.exe .\scripts\run_bcr1.py --result
  .\quality\v10-s5-bcr1-result.json`.
- Resultado preservado integralmente, incluindo as amostras: `quality/v10-s5-bcr1-result.json`.
- O harness executou três bancos SQLite descartáveis, sequenciais e isolados;
  nenhum banco operacional foi usado. As migrações existentes foram aplicadas
  somente nesses bancos temporários; nenhuma migration foi criada.
- Modelo A7 da autorização: `GPT-6 Luna High`. O BCR-1 FAIL aciona a política
  `MODEL_ESCALATION_REQUIRED: GPT-6.1 Sol Medium` antes de qualquer otimização.

## Metodologia e ambiente

- BCR-1 determinístico: 10.000 questões, 100.000 tentativas, 100.000 revisões,
  200 itens por nível taxonômico, dez anos de histórico.
- Seed: `20260909`; fingerprint idêntico nos três runs:
  `bbcf0d7f:86f65f1c:f5685b47:4dadc580:1811fe37:c903e521:e1cd3577:86190d98`.
- Cada operação medida usou 20 warm-ups e 100 amostras; p95 nearest-rank
  conforme ADR-012/CT-107; três runs completos e independentes.
- Windows 11 `10.0.26200`; Python 3.13.15; Django 5.2.17; SQLite 3.53.1;
  CPU AMD64 Family 23 Model 160 Stepping 0, 8 CPUs lógicas; 16 GiB RAM.
- Django development com `CEI_DEVELOPMENT_DB` substituído pelo banco
  descartável. Execução em processo único, gravações sequenciais e sem
  concorrência artificial. Tipo de armazenamento não observado; espaço livre
  observado: 105.576.996.864 bytes.
- Targets autoritativos: telas até 3 s p95 (RNF-001/CT-105); busca/filtros até
  2 s p95 (RNF-002/CT-106); gravações críticas até 2 s p95
  (RNF-003/CT-107); atualização do dashboard até 3 s (RNF-004/CT-108).

## Resultados BCR-1

| Run | save_question | save_attempt | complete_review | dashboard | review_queue | dashboard_update | Resultado |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0,0338 s PASS | 0,0231 s PASS | 0,0713 s PASS | 3,3892 s FAIL | 3,5003 s FAIL | 3,0677 s FAIL | FAIL |
| 2 | 0,0246 s PASS | 0,0177 s PASS | 0,0736 s PASS | 2,6150 s PASS | 2,4071 s PASS | 2,4621 s PASS | PASS |
| 3 | 0,0309 s PASS | 0,0194 s PASS | 0,0752 s PASS | 3,3645 s FAIL | 2,4511 s PASS | 2,7151 s PASS | FAIL |

Os p95 de busca, filtros e listagem/página tardia passaram em todos os runs.
CT-107 passou nos três runs. As excedências de dashboard nos runs 1 e 3 são
reprodutíveis e excedem o limite aprovado de 3 s; CT-105/BCR-1 falha. A fila
de revisão e dashboard_update excederam 3 s somente no run 1; permanecem falhas
por run, sem média entre execuções. Resultado agregado do harness:
`status=FAIL`, `ct107_status=PASS`, `read_status=FAIL`, exit code 1.

## Integridade e rastreabilidade CT-105–112

| CT | Evidência observada | Resultado nesta execução |
| --- | --- | --- |
| CT-105 | Dashboard e fila medidos; dashboard excedeu 3 s nos runs 1 e 3; fila excedeu 3 s no run 1. | FAIL |
| CT-106 | Busca, filtros e combinação passaram em cada run; isolamento entre Workspaces preservado pelo caso do harness. | PASS |
| CT-107 | As três gravações reais passaram em cada run; p95 por operação abaixo de 2 s. | PASS |
| CT-108 | Dashboard após gravação: run 1 p95 3,0677 s; runs 2 e 3 abaixo de 3 s. | FAIL |
| CT-109 | BCR-2 e verificação direta de integridade não foram executados após o gatilho de parada BCR-1. | NOT RUN — bloqueado pelo escalonamento |
| CT-110 | Tentativa, fila e paginação medidas; paginação observou 8.000/8.000 IDs únicos em 2.403 queries. | PASS |
| CT-111 | Contenção concorrente não foi introduzida; ADR-012 mantém concorrência nos CTs próprios. Execução parada antes de teste focado. | NOT RUN |
| CT-112 | Três runs com seed, fingerprint e contagens idênticos; variação de latência preservada no JSON. | PASS |

O harness reconciliou contagens do dashboard e da fila, manteve isolamento de
Workspace, e a paginação percorreu 8.000 registros ativos sem omissão ou
duplicação. Um checker completo durante BCR-2 não foi executado, pois BCR-2 não
foi iniciado.

## Parada da primeira execução e condição de retomada

- Nenhum código ou teste foi alterado. Nenhuma migration nova foi criada.
- BCR-2 (dataset 2×), testes S5 adicionais, quality gate e A8 standard não
  foram executados; portanto, não há decisão final de desempenho V1.
- Não foi feita otimização nem alteração de threshold. Os limites acima vêm
  somente de RNF-001–004 e CT-105–108.
- Retomar somente após atender o escalonamento para `GPT-6.1 Sol Medium` e
  reavaliar o finding com a evidência bruta preservada. S6–S10 permanecem
  `NOT AUTHORIZED`.

## Profiling da retomada — antes de alterar código
Modelo escalado: `GPT-6.1 Sol Medium`. Dataset BCR-1 integral; DIAGNOSTIC RUN
em banco temporário isolado. Fixture e migrations existentes fora das medições.
Perfis com cProfile são instrumentados e não são percentis oficiais.
- `dashboard`: diagnóstico sem cProfile 4.4412–6.0203 s; 15 queries. Perfil: 5.5829 s, execute SQL 2.4922 s (fetch não incluído).
- `review_queue`: diagnóstico sem cProfile 3.4879–4.9843 s; 4 queries. Perfil: 9.4009 s, execute SQL 0.0346 s (fetch não incluído).
- `performance_pair`: diagnóstico sem cProfile 1.8864–2.7359 s; 4 queries. Perfil: 3.0372 s, execute SQL 0.0366 s (fetch não incluído).
- `error_categories`: diagnóstico sem cProfile 1.5628–5.0506 s; 2 queries. Perfil: 1.9412 s, execute SQL 1.9315 s (fetch não incluído).
- `queue_selector`: diagnóstico sem cProfile 3.4808–4.8768 s; 3 queries. Perfil: 7.9583 s, execute SQL 0.0157 s (fetch não incluído).

Causas comprovadas e correções propostas, registradas antes da mudança:

1. Fila: `list_review_queue` materializa 8.000 revisões, relações e revisões
   atuais antes de paginar; perfil `from_db` 48.001 chamadas e conversão de
   176.002 UUIDs. Custo é carregamento/conversão/prefetch, não N+1 (3 queries
   no selector). Contar/grupar no SQL e carregar apenas as páginas preserva
   filtros, ordem, seções, totais, dados e paginação independente.
2. Dashboard: `performance_pair` agrega por questão e cria 10.000 objetos
   Question para somar por taxonomia. Perfil: 10.400 chamadas `from_db`,
   fetchmany 1,547 s e conversões 0,555 s. Agrupar diretamente pelos mesmos
   IDs de disciplina/assunto evita essa passagem redundante, preservando
   valores, questões sem taxonomia, categorias vazias e isolamento.
3. Dashboard: `error_categories` usa LEFT JOINs e OR para classificados e
   não classificados no histórico inteiro; execute da consulta agrupada
   consumiu 1,931 s. Separar contagem de não classificados da agregação de
   classificados evita joins de categorias no subconjunto sem classificação,
   preservando exclusão de classificações estrangeiras e projeção de merges.
   A validação posterior medirá se essa mudança reduz o custo.

Variação ambiental: CPU do processo, wall, GC, consultas e primeira leitura
estão no JSON. Os runs oficiais têm queries constantes (dashboard 15, fila 4),
mas medianas e caudas variam; cache quente não eliminou os FAILs. Os dados
originais não contêm CPU/processos/I/O por amostra: não há prova para atribuir
os runs 1/3 a processo específico ou ignorá-los. No diagnóstico há trabalho
real de CPU/conversão e SQL. Fixture/bootstrap/limpeza são externos à região
cronometrada; requests são novos, sem cache de resultados introduzido.
Nenhuma estabilização artificial ou alteração de protocolo será usada para PASS.

Finding S5-F01: **Major**, fluxo obrigatório com falha reproduzível de
CT-105/CT-108. Não é Blocker pelos critérios do plano: não há evidência de
perda/corrupção, cross-Workspace ou vulnerabilidade crítica. Reteste pendente.

## Correção e validação focada

Alterações locais: `modules/reviews/selectors.py` pagina as seções no SQL antes
 de hidratar os objetos; `modules/analytics/services.py` agrega por taxonomia e
separa classificados/não classificados com UNION ALL, mantendo duas consultas.
Sem cache, schema, índice, migration ou regra nova. Dois testes de regressão
comprovam paginação independente/limites e ausência de hidratação por questão.
Primeira rodada focada: 78 PASS/1 FAIL por orçamento de duas queries da análise
 de erros. Corrigida com UNION ALL, sem relaxar o teste; reteste: **79 passed em
33,82 s**. mypy dos quatro arquivos: PASS. Reteste oficial BCR-1 será gravado em
`quality/v10-s5-bcr1-final-result.json`; o resultado inicial não será sobrescrito.

Harness BCR-2 separado: `scripts/run_bcr2.py` reutiliza `execute_run`, os mesmos
serviços e protocolo 20/100/3; duplica questões/tentativas/revisões/taxonomia no
mesmo intervalo de dez anos. Não redefine o SLA: latências BCR-1 são comparações,
aceite BCR-2 depende de completude, contagens e checker integral. Executar apenas
após BCR-1 final válido. Contagens posteriores incluem as escritas/fixtures reais
 do harness (4N+1 questões, 3N tentativas, 5N+1 revisões locais; N=120).

## BCR-1 oficial após correção — PASS
Comando: `.venv\Scripts\python.exe scripts/run_bcr1.py --result quality/v10-s5-bcr1-final-result.json`; exit code **0**. O harness oficial não foi modificado.
| Run | save_question | save_attempt | complete_review | dashboard | fila | dashboard_update |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.0592239 s PASS | 0.0200825 s PASS | 0.0798429 s PASS | 2.2934019 s PASS | 0.0443488 s PASS | 1.8167493 s PASS |
| 2 | 0.0224416 s PASS | 0.0183155 s PASS | 0.0491591 s PASS | 1.6880568 s PASS | 0.0635432 s PASS | 2.2265964 s PASS |
| 3 | 0.0347464 s PASS | 0.0336811 s PASS | 0.0605473 s PASS | 2.1056085 s PASS | 0.0542713 s PASS | 1.7868170 s PASS |

Todos os targets vinculantes passaram em cada run; nenhum FAIL foi removido ou combinado por média. Método, seed, dataset, fingerprint e versões do ambiente permanecem os mesmos da execução inicial. Hash SHA-256 do arquivo inicial novamente conferido, sem alteração.

## CT-110 complementar e BCR-2 em execução

`quality/v10-s5-ct110-diagnostic.json`: DIAGNOSTIC RUN no BCR-1 completo,
2 tentativas reais confirmadas, 16 queries em cada uma; histórico consultado
por question/workspace e LIMIT 1, sem hidratar o histórico integral. Peaks
instrumentados: 219.051 e 155.741 bytes; tempos cProfile/tracemalloc 0,0822 e
0,0741 s (não são amostras oficiais CT-107). Banco dedicado descartado depois.
Fila e paginação já possuem os perfis/queries do JSON BCR-1 e testes de páginas.
Os testes comparam crescimento do trabalho por subconjunto, mantendo os totais
funcionais e sem fixar uma capacidade nova. Reteste dos três arquivos: 26 PASS
em 9,90 s; teste de contagens locais/checker após todas as operações: 1 PASS em
5,54 s. mypy dos testes e harness BCR-2: PASS.

Variação/caches: os cold_seconds do harness representam a primeira leitura de
cada target, após preparação/reconciliação; não houve flush de cache do sistema
operacional. Templates/URLs usam o comportamento padrão do Django. Queries por
request continuam registradas, sem cache analítico novo. Não há telemetria de
I/O físico ou CPU de terceiros na primeira execução; nenhum processo específico
foi tratado como causa comprovada ou encerrado para obter PASS.

BCR-2 foi autorizado após o BCR-1 final válido. Comando:
`.venv\Scripts\python.exe scripts/run_bcr2.py --result quality/v10-s5-bcr2-result.json`.
Dados: 20.000 questões / 200.000 tentativas / 200.000 revisões / 400 itens em cada
nível taxonômico, seed 20260909, mesmo intervalo de dez anos. Cada run verifica
contagens reais locais e checker integral; latências comparadas com BCR-1 são
observações, sem SLA adicional. Gate e A8 final permanecem pendentes.

## Checkpoint BCR-2 run 1

Run 1 concluído: PASS para RNF-005/CT-109. Contagens pós-operações locais:
20.481 questões, 200.360 tentativas, 200.601 revisões, 400 itens por nível
taxonômico; valores esperados e reais idênticos. Protocolo completo 20/100;
checker integral: 25 checks, 26 queries, zero findings. Paginação percorreu
16.000/16.000 IDs únicos, sem omissão/duplicação. Dashboard p95 4,1373038 s e
dashboard_update 4,337212 s excedem a referência BCR-1 de 3 s; excedência
comunicada como degradação observada em 2×, sem SLA BCR-2 inventado. Runs 2/3,
gate e A8 ainda pendentes.

## Ambiente BCR-2 — espera moderna fora da medição

No run 2, os eventos System/Microsoft-Windows-Kernel-Power 506/507 registram
espera moderna por Idle Timeout às 23:02:41 de 29/09/2026 e saída por teclado
às 23:25:44 (-03:00). O segundo bootstrap após preparação do dataset ocorreu
às 02:26:28 UTC: o intervalo ficou na fixture, antes das leituras cronometradas.
A observação não explica retroativamente o FAIL BCR-1 inicial nem altera seus
resultados. Para evitar suspensão durante amostras seguintes, foi ativado
um guard temporário SetThreadExecutionState(SYSTEM_REQUIRED), ligado somente
ao processo pai BCR-2, com liberação automática ao término. Não há alteração
permanente do plano de energia, prioridade, caches, thresholds ou processos
externos. Os eventos finais serão conferidos para detectar suspensão durante
a região medida; amostras não serão descartadas ou selecionadas.

## Pausa controlada — 2026-09-30

Estado: **AUTHORIZED / PAUSED / RETOMÁVEL**. Nenhuma nova execução até retomada
humana. Modelo escalado `GPT-6.1 Sol Medium`; migration expectation `NO`;
S6–S10 `NOT AUTHORIZED`. Código, testes, profiling e resultados anteriores
preservados; BCR-1 inicial FAIL intacto e final oficial PASS nos três runs.

**Divergência factual:** o pedido afirma conclusão da BCR-2 Run 2, mas o processo
continuava em dashboard_update e não havia `run-2.json` nem resultado agregado
`quality/v10-s5-bcr2-result.json`. A pausa interrompeu esses processos; não é
possível declarar essa run completa/PASS. Run 3 não começou. O banco sintético
interrompido foi copiado para `.tools/quality/v10-s5-paused/run-2-interrupted.sqlite3`
(somente preservação; não comprova percentis/completude/integridade final).
A Run 1 foi copiada byte a byte do resultado temporário para
`quality/v10-s5-bcr2-run-1-result.json`, com método completo, contagens exatas e
checker 25/0. Nenhum resultado bruto produzido foi sobrescrito.

| CT | Evidência atual preservada | Estado na pausa |
| --- | --- | --- |
| CT-105 | BCR-1 final, todos os targets aplicáveis nos três runs | PASS; FAIL inicial preservado |
| CT-106 | Busca/filtros/isolamento BCR-1 final nos três runs | PASS |
| CT-107 | Gravações reais BCR-1 inicial e final nos três runs | PASS |
| CT-108 | Dashboard após gravação BCR-1 final nos três runs | PASS; FAIL inicial preservado |
| CT-109 | BCR-2 run 1 completa, contagens/checker 25/0; run 2 interrompida, run 3 não iniciada | INCOMPLETE, sem aceite agregado |
| CT-110 | Profiling tentativa/fila/paginação e testes de trabalho limitado | PASS |
| CT-111 | Testes focados de contenção SQLite real, retry e ausência de confirmação falsa | PASS |
| CT-112 | BCR-1 três runs com manifestos idênticos; BCR-2 repetição ainda incompleta | PASS BCR-1 / PENDING BCR-2 |

Pendente após retomada humana: localizar eventual JSON completo externo da Run 2
ou repetir integralmente a Run 2 em banco novo, executar Run 3, consolidar as três
runs e a degradação, depois gate autoritativo e A8 standard final. Não reutilizar
uma run interrompida como completa. Nenhum gate/A8/arquivamento/Git checkpoint
foi feito na pausa. Guard temporário de energia liberado; nenhum plano de energia
permanente alterado. Não se considera duas runs suficientes para um contrato de três.

## Retomada após pausa — 2026-09-30

Preflight: HEAD = origin/main = baseline e3357d26e9c0165617bed221732fabe2db042995;
working tree contém somente S5; diff --check PASS; nenhum processo Python órfão.
BCR-1 final e BCR-2 Run 1 preservados, com hashes conferidos. Banco interrompido
pertence ao target sintético documentado da Run 2, sem banco operacional.

Decisão metodológica: **não retomável com certeza**. `execute_run` mantém
resultados em memória e `run_bcr2._worker` só grava o JSON após operações e
checker. Não há journal durável de samples; não é possível provar ausência de
perda/duplicação de amostras, p95 válido ou equivalência contínua. Preservar como
**INTERRUPTED / NON-CANDIDATE EVIDENCE** em
`quality/v10-s5-bcr2-run-2-interrupted.json`, com banco parcial retido em `.tools`.
O incidente é operacional/humano, sem classificação automática como defeito.

Executar worker existente para Run 2 completa em target novo e resultado
`quality/v10-s5-bcr2-run-2-final-result.json`; validar antes de iniciar worker
Run 3, também em target novo. Não mudar harness, produto, BCR-1 ou protocolo.
Banco original temporário interrompido será descartado somente após confirmar
hash idêntico à cópia preservada. Guard temporário contra suspensão durante as
novas runs, sem alterar permanentemente energia/prioridade/cache. S5 ativa;
S6–S10 não autorizadas, migration NO. Gate/A8 aguardam três runs BCR-2 válidas.

## BCR-2 Run 2 refeita — COMPLETE / PASS

Resultado distinto `quality/v10-s5-bcr2-run-2-final-result.json`, exit 0.
Contagens locais exatas 20.481/200.360/200.601 e 400 por nível taxonômico;
checker 25 checks/26 queries/zero findings; paginação 16.000 IDs únicos.
Manifesto idêntico à Run 1; 14 operações com 20 warm-ups/100 samples e p95
nearest-rank conferido diretamente contra as amostras. Dashboard 4,1370357 s,
dashboard_update 3,9851496 s: excedências da referência BCR-1 comunicadas, sem
novo SLA. Hashes de todo código/JSON anterior intactos. Run 3 em execução.

## BCR-2 consolidado — PASS / três runs válidas

Run 1 original preservada + Run 2 integral refeita + Run 3 isolada. Workers
retomados exit 0; 14 operações por run, 20/100, samples 1–100 e nearest-rank
conferidos contra amostras. JSON completo: `quality/v10-s5-bcr2-result.json`.

| Run | save_question | save_attempt | complete_review | dashboard | fila | dashboard_update |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.0347233 s | 0.0424390 s | 0.0628949 s | 4.1373038 s | 0.1348849 s | 4.3372120 s |
| 2 | 0.0363275 s | 0.0389938 s | 0.0601297 s | 4.1370357 s | 0.1168073 s | 3.9851496 s |
| 3 | 0.0392415 s | 0.0299250 s | 0.0474521 s | 3.9953826 s | 0.1295217 s | 4.2628848 s |

Prova 2×: questões 10.000→20.000; tentativas/revisões 100.000→200.000;
taxonomia por nível 200→400. Mesma seed 20260909 e período 2016-09-09–2026-09-06;
fingerprint BCR-2 igual nas três runs. Ambiente igual ao BCR-1 final: Windows 11
10.0.26200, Python 3.13.15, Django 5.2.17, SQLite 3.53.1, 8 CPUs lógicas/16 GiB;
processo único/escritas sequenciais. Tipo físico de armazenamento não observado.

Contagens locais finais nas três runs: 20.481 questões, 200.360 tentativas,
200.601 revisões, 400 disciplinas/assuntos/subassuntos. Cada checker: 25 checks,
26 queries, zero findings. Paginação de 16.000 IDs únicos, reconciliação e
isolamento PASS. Corrupção, duplicação indevida e falha silenciosa: nenhuma
observada; todas as operações esperadas concluídas e confirmações persistidas.

### Degradação observada — p95 BCR-1 final → BCR-2

Diferenças individuais, sem média; aumentos/reduções são observações, sem limite
aceitável ou inferência de capacidade nova. Todas as amostras preservadas.

| Run | Operação | BCR-1 | BCR-2 | Diferença |
| --- | --- | ---: | ---: | ---: |
| 1 | save_question | 0.0592239 s | 0.0347233 s | -41.37% |
| 1 | save_attempt | 0.0200825 s | 0.0424390 s | +111.32% |
| 1 | complete_review | 0.0798429 s | 0.0628949 s | -21.23% |
| 1 | dashboard | 2.2934019 s | 4.1373038 s | +80.40% |
| 1 | analytics_summary | 2.0160466 s | 4.2964625 s | +113.11% |
| 1 | review_queue | 0.0443488 s | 0.1348849 s | +204.15% |
| 1 | question_list | 0.1384035 s | 0.2468898 s | +78.38% |
| 1 | question_search | 0.1235541 s | 0.2851756 s | +130.81% |
| 1 | question_filters | 0.1260565 s | 0.1872999 s | +48.58% |
| 1 | question_search_filters | 0.1051729 s | 0.1757606 s | +67.12% |
| 1 | question_late_page | 0.3935448 s | 0.9891767 s | +151.35% |
| 1 | question_detail | 0.0157516 s | 0.0146793 s | -6.81% |
| 1 | learning_timeline | 0.0144736 s | 0.0176545 s | +21.98% |
| 1 | dashboard_update | 1.8167493 s | 4.3372120 s | +138.73% |
| 2 | save_question | 0.0224416 s | 0.0363275 s | +61.88% |
| 2 | save_attempt | 0.0183155 s | 0.0389938 s | +112.90% |
| 2 | complete_review | 0.0491591 s | 0.0601297 s | +22.32% |
| 2 | dashboard | 1.6880568 s | 4.1370357 s | +145.08% |
| 2 | analytics_summary | 2.1110832 s | 4.2989215 s | +103.64% |
| 2 | review_queue | 0.0635432 s | 0.1168073 s | +83.82% |
| 2 | question_list | 0.1272294 s | 0.1903227 s | +49.59% |
| 2 | question_search | 0.1881372 s | 0.2274119 s | +20.88% |
| 2 | question_filters | 0.1554973 s | 0.2381397 s | +53.15% |
| 2 | question_search_filters | 0.0866038 s | 0.1514669 s | +74.90% |
| 2 | question_late_page | 0.4459506 s | 0.9879374 s | +121.54% |
| 2 | question_detail | 0.0156961 s | 0.0099511 s | -36.60% |
| 2 | learning_timeline | 0.0271962 s | 0.0192082 s | -29.37% |
| 2 | dashboard_update | 2.2265964 s | 3.9851496 s | +78.98% |
| 3 | save_question | 0.0347464 s | 0.0392415 s | +12.94% |
| 3 | save_attempt | 0.0336811 s | 0.0299250 s | -11.15% |
| 3 | complete_review | 0.0605473 s | 0.0474521 s | -21.63% |
| 3 | dashboard | 2.1056085 s | 3.9953826 s | +89.75% |
| 3 | analytics_summary | 2.3146545 s | 4.0615920 s | +75.47% |
| 3 | review_queue | 0.0542713 s | 0.1295217 s | +138.66% |
| 3 | question_list | 0.1205167 s | 0.1959926 s | +62.63% |
| 3 | question_search | 0.1493199 s | 0.2193327 s | +46.89% |
| 3 | question_filters | 0.1005290 s | 0.1860471 s | +85.07% |
| 3 | question_search_filters | 0.1299463 s | 0.1583469 s | +21.86% |
| 3 | question_late_page | 0.4748860 s | 0.9489052 s | +99.82% |
| 3 | question_detail | 0.0112284 s | 0.0109337 s | -2.62% |
| 3 | learning_timeline | 0.0166494 s | 0.0207282 s | +24.50% |
| 3 | dashboard_update | 1.7868170 s | 4.2628848 s | +138.57% |

Dashboard e dashboard_update excedem a referência BCR-1 de 3 s em 2×.
Excedências comunicadas conforme RNF-005; BCR-1 final PASS em 1×, BCR-2 aprovado
por completude/integridade. Nenhum SLA ou threshold adicional foi criado.

### BCR-1 inicial → final (gargalos corrigidos)

| Run | Operação | Inicial | Final | Diferença |
| --- | --- | ---: | ---: | ---: |
| 1 | dashboard | 3.3892182 s | 2.2934019 s | -32.33% |
| 1 | review_queue | 3.5003203 s | 0.0443488 s | -98.73% |
| 1 | dashboard_update | 3.0677007 s | 1.8167493 s | -40.78% |
| 2 | dashboard | 2.6150400 s | 1.6880568 s | -35.45% |
| 2 | review_queue | 2.4070578 s | 0.0635432 s | -97.36% |
| 2 | dashboard_update | 2.4621058 s | 2.2265964 s | -9.57% |
| 3 | dashboard | 3.3644675 s | 2.1056085 s | -37.42% |
| 3 | review_queue | 2.4510921 s | 0.0542713 s | -97.79% |
| 3 | dashboard_update | 2.7151031 s | 1.7868170 s | -34.19% |

### CT-105–112 consolidada

| CT | Evidência direta | Resultado |
| --- | --- | --- |
| CT-105 | Telas BCR-1 final, todos os targets nos três runs | PASS |
| CT-106 | Busca/filtros/isolamento BCR-1 final nos três runs | PASS |
| CT-107 | Três gravações persistidas, três runs iniciais e finais | PASS |
| CT-108 | Dashboard pós-gravação/reconciliação BCR-1 final | PASS |
| CT-109 | JSON BCR-2 completo, três runs 2×, contagens/checker 25/0 | PASS |
| CT-110 | Profiles tentativa/fila/paginação, queries e testes de trabalho limitado | PASS |
| CT-111 | test_actual_sqlite_contention_has_no_partial_state_or_false_success e retry/erros nos 79 testes focados | PASS |
| CT-112 | Seed/manifestos/contagens iguais, três runs por dataset e variação bruta preservada | PASS |

Gate/A8 pendentes. Nenhuma mudança de produto/harness/teste nesta retomada;
nenhuma migration. Interrupção é incidente operacional, não defeito do produto.

## Gate — primeira tentativa (preservada)

Exit 1 na auditoria pip-audit: cache fora do workspace negado e conexão PyPI
WinError 10013 no sandbox. Falha ambiental de acesso; auditoria inconclusiva,
não se declara ausência de vulnerabilidades nem GREEN. Antes disso: 512 testes
PASS em 244,90 s, cobertura exibida 86%, domínio ≥80% PASS; runtime, migrations
inesperadas/DB vazio, format/lint/mypy e detect-secrets PASS. Log integral
`.tools/quality/v10-s5-gate-attempt-1.log`. Reexecutar o mesmo gate com acesso
necessário, sem alterar controles. S5 ativa; A8/fechamento aguardam gate GREEN.

## Gate final — RED / exit 1

Segunda execução integral do comando autoritativo, com acesso de rede/cache
permitido: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.
512 testes PASS em 222,71 s; cobertura total 86,4013% (exibida 86%), domínio
≥80% por módulo PASS. Lock/sync/runtime, perfis, migrations inesperadas
(`No changes detected`), banco vazio, formato (406 arquivos), lint, mypy
(195 arquivos) e detect-secrets PASS. Nenhuma regressão funcional conhecida.
Nenhum warning de pytest foi emitido na segunda execução.

Pip-audit final FAIL: três vulnerabilidades conhecidas em **urllib3 2.7.0**.
Resultado bruto copiado sem alteração para `quality/v10-s5-pip-audit-result.json`.
Log integral `.tools/quality/v10-s5-gate-attempt-2.log`; primeira tentativa
ambiental também preservada. Gate não imprimiu duração final porque lançou erro;
intervalo observado de escrita do log: 299.61 s (não é duração oficial).

| Advisory | Evidência / correção indicada pelo mantenedor |
| --- | --- |
| [CVE-2026-97687 / GHSA-8988-9cw3-xx77](https://github.com/urllib3/urllib3/security/advisories/GHSA-8988-9cw3-xx77) | Separação TLS proxy/alvo; fix 2.8.0 |
| [CVE-2026-97688 / GHSA-gh4c-6fx4-qh6g](https://github.com/urllib3/urllib3/security/advisories/GHSA-gh4c-6fx4-qh6g) | Loop em streaming Deflate/chunked; fix 2.8.0 |
| [CVE-2026-97689 / GHSA-vxq7-64xx-v4gw](https://github.com/urllib3/urllib3/security/advisories/GHSA-vxq7-64xx-v4gw) | Buffer sem limite na linha de tamanho de chunk; fix 2.8.0 |

`uv.lock`/`pyproject.toml` não foram alterados pela S5. urllib3 vem de requests,
via pip-audit/detect-secrets no grupo dev. Busca dirigida em src/scripts não
identificou uso direto de requests/urllib3; não se declara exploração do produto
nem se inventa causa para resultados históricos de auditoria. O gate vigente
bloqueia o fechamento independentemente dessa distinção. Atualizar dependências
não é otimização BCR-2 nem está coberto pela retomada; nenhuma alteração de
lock/dependência ou controle de segurança foi feita.

## A8 standard final — CHANGES REQUIRED

Revisão conforme `docs/review/code-review.md`, começando pelo contrato/diff.

| Item revisto | Conclusão |
| --- | --- |
| Autorização/modelo/escopo | S5 AUTHORIZED; GPT-6.1 Sol Medium por FAIL medido; S6–S10 não autorizadas |
| BCR-1 inicial e profiling | FAIL/hashes preservados; DIAGNOSTIC RUN separado; gargalos ORM/SQL comprovados antes das correções |
| Correção/testes | Paginação SQL, agregação taxonômica e UNION ALL localizados; filtros, ordem, datas civis, totais e isolamento preservados; 79 focados e 512 globais PASS |
| BCR-1 final | Três runs PASS, dataset/seed/20/100/nearest-rank/thresholds preservados; não reexecutado nesta retomada |
| Run 1 BCR-2 | Artefato completo original/hashes preservados; contagens/checker 25/0 |
| Run 2 interrompida | Não candidata; samples somente em memória, continuação válida não demonstrável; banco parcial preservado |
| Run 2 final / Run 3 | Workers existentes, bancos novos, protocolo integral, exit 0; contagens/checker 25/0 em cada |
| Dataset/degradação | 2× provado, mesmo período/seed/ambiente; 42 comparações p95 individuais incluem aumentos/reduções; excedências da referência comunicadas, nenhum SLA novo |
| Integridade/CT-105–112 | Evidência direta, checker completo e reconciliação; todos os CT PASS; nenhuma corrupção/duplicação/falha silenciosa observada |
| Migrations/mudanças funcionais | Zero migration; nenhuma mudança de código/harness/teste nesta retomada; sem schema/cache/FTS/feature/regra nova |
| Gate | RED exit 1 por auditoria concluída com vulnerabilidades; fechamento não aprovado |

### Findings finais

- **S5-F01 — Major histórico resolvido:** BCR-1 inicial FAIL por gargalos reais;
  correção medida, reteste oficial três runs PASS e regressão global PASS.
  FAIL inicial continua no histórico, sem reclassificação retroativa.
- **S5-F02 — Major aberto:** `uv.lock` (urllib3 2.7.0) / gate pip-audit:
  três advisories confirmados; auditoria mandatória FAIL impede o aceite S5.
  Dependência preexistente de tooling/dev; não causada pela correção S5.
  Requer tratamento autorizado de dependências e novo gate integral.
  Não classificado automaticamente como Blocker de produto: não há prova de
  exploração do runtime, perda/corrupção ou vulnerabilidade crítica causada
  pela mudança. Não dispensar a auditoria nem aceitar exceção implícita.
- Pausa/interrupção humana e erro de rede/cache da primeira tentativa são
  incidentes operacionais, não defeitos de produto.
- Findings abertos: **Blocker 0 / Major 1 / Minor 0**.

## Decisão e estado retomável

**BLOCKED**. BCR-1 final PASS e BCR-2 três runs válidas PASS preservados;
CT-105–112 consolidados. Gate RED e A8 CHANGES REQUIRED impedem S5_COMPLETED.
`tasks/current.md` permanece AUTHORIZED, sem arquivar nem NO_TASK_AUTHORIZED;
`PROJECT_STATE.md` coerente: S1–S4 concluídas, S5 bloqueada/retomável.
Migration expectation NO; S6–S10 NOT AUTHORIZED. Dependências/lock/gate não
alterados. Sem commit, push, tag, release ou início de outra etapa.

Após tratamento humano autorizado da pendência de dependências, reexecutar o
gate integral e repetir A8; os benchmarks só precisam de nova execução se houver
mudança relevante de candidato/ambiente ou finding concreto. Não há autorização
implícita para esse tratamento nesta execução.

Verificação ambiental final: System/Kernel-Power 506/507 consultados desde
13:09 de 30/09/2026 (-03:00), sem evento de espera moderna retornado durante
as novas Runs 2/3. Guards temporários liberados ao término. Targets completos
descartados após validar JSON/contagens/checker; cópia parcial não candidata
continua preservada. Hashes anteriores (JSON/código/testes/harness) novamente
conferidos sem diferenças. HEAD/origin/main permanecem no baseline; working
tree preservada para revisão humana, exclusivamente S5.

## V1.0-S2R1 — Remediação do finding S5-F02 — 2026-09-30

- A autorização humana específica para S2R1 foi executada sem ampliar o escopo
funcional da S5. `urllib3` era transitiva via `requests 2.34.2`, trazida por
`pip-audit`, `detect-secrets` e `cachecontrol` no grupo dev.
- Lock mínimo: só a entrada urllib3 mudou de 2.7.0 para 2.8.0; demais pacotes,
`pyproject.toml`, código, testes e migrations ficaram inalterados por S2R1.
- Auditoria anterior preservada em `quality/v10-s5-pip-audit-result.json` com os
três advisories. A auditoria posterior em
`quality/v10-s2r1-pip-audit-result.json` lista zero vulnerabilidades; o gate
confirmou `No known vulnerabilities found`.
- Gate integral: GREEN, exit 0; 512 testes PASS em 238,07 s; cobertura
86,4013267%; duração total 317,6 s; migrations sem mudanças; controles restantes
PASS. A8 standard de S2R1 APPROVED, Blocker 0 / Major 0 / Minor 0.
- S5-F02 está resolvido. A falha inicial do BCR-1 e todos os resultados
posteriores, BCRs, CT-105–112 e artefatos raw permanecem preservados; não houve
benchmark adicional, pois a dependência de tooling não participa dos imports
Python do produto/harness.
- S5 permanece autorizada e aguarda fechamento formal separado; não declarar
`S5_COMPLETED` aqui. S6–S10 NOT AUTHORIZED; migration NO. Sem commit, push, tag
ou release.

Evidência detalhada da remediação: `quality/v10-s2r1-dependency-remediation-result.md`.
## V1.0-S5 — Fechamento formal e A8 final — 2026-09-30

- Decisão final: `S5_COMPLETED`.
- A8 standard final: `APPROVED`. A revisão cobriu autorização e limites de
  escopo, BCR-1 inicial FAIL e resultado final PASS nos três runs, profiling e
  estabilização, protocolo e artefatos brutos, BCR-2 em dataset 2× com três
  runs válidos PASS, CT-105–112, degradação medida e registrada sem SLA novo,
  integridade, regressão, migrations e gate final.
- BCR-2 Run 2 interrompida permanece preservada e excluída como
  `NON-CANDIDATE`; sua repetição completa PASS e Runs 1 e 3 PASS compõem os
  três runs válidos. Evidência anterior e JSONs não foram alterados.
- Integridade: PASS; corrupção, duplicação indevida e silent failure: nenhum.
  S5-F02: `RESOLVED` por S2R1. urllib3 2.8.0; auditoria pós-fix limpa.
- Gate final elegível: GREEN, exit 0; 512 testes PASS; coverage 86.4013%;
  migrations sem alterações; controles estáticos, segredos e pip-audit PASS.
  Nenhuma alteração funcional/dependência relevante ocorreu após o gate;
  portanto ele foi reutilizado sem nova execução.
- Findings finais: Blocker 0 / Major 0 / Minor 0. Migration expectation `NO`.
- `PROJECT_STATE.md` reconciliado; contrato arquivado em
  `tasks/completed/v10-s5-performance-bcr.md`; `tasks/current.md` voltou a
  `NO_TASK_AUTHORIZED`. S6–S10 permanecem `NOT AUTHORIZED`.
- Não houve benchmark, teste ou gate adicional; sem commit, push, tag ou release.