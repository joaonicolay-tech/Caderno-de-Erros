# V0.5-S9 — evidência intermediária de hardening beta

Estado final: **CONCLUÍDA** após A8 deep APPROVED e gate final GREEN. As seções intermediárias abaixo preservam os estados e tentativas anteriores.

## Autoridade e baseline

- Contrato `tasks/current.md`: `AUTHORIZED`, `IMPLEMENTATION_AUTHORIZED`, `Size L`, `Risk high`, `A8 deep`; migration `NO` como decisão final do A4, após classificação inicial `UNLIKELY`. S10 não autorizada.
- A4 fechado em `tasks/plans/v05-s9-beta-hardening-plan.md`. Preflight: branch `main`; `HEAD = origin/main = 4a10cdf8fa44bbaf7240fa19532f6ba29354f246`; antes da implementação havia somente `M tasks/current.md` e `?? tasks/plans/v05-s9-beta-hardening-plan.md`; `git diff --check` exit 0.
- Baseline focado antes da alteração funcional: 134 testes aprovados em 61,90 s, exit 0. Arquivos: `test_v05_s3_ui.py`, `test_taxonomy_interface.py`, `test_question_search.py`, `test_question_interface.py`, `test_priority_integration.py`, `test_v05_s7_ui.py`, `test_v05_s7_portability.py`, `test_backup_restore.py`, `test_backup_recovery.py`, `test_operations.py`, `test_windows_operation.py`, `test_bcr1.py`.

## BCR e decisões de desempenho

- Comando: `.venv/Scripts/python.exe scripts/run_bcr1.py --result quality/v05-s9-bcr1-result.json`, iniciado em 2026-09-26 19:58:58 UTC. Harness existente, seed `20260909`, SQLite descartável, 20 warm-ups, 100 samples e 3 runs independentes; sem overwrite de artefatos históricos. Ambiente observado: Windows 11 `10.0.26200`, Python 3.13.15, Django 5.2.17, SQLite 3.53.1, CPU AMD64 Family 23 Model 160 Stepping 0, 8 cores lógicos, 103.378.006.016 bytes livres em `%TEMP%` após a execução; tipo de storage não observado.
- Budgets existentes aplicáveis: gravações CT-107 ≤ 2 s; telas BCR aplicáveis ≤ 3 s; busca/filtros ≤ 2 s. Operações V0.5 Domain, Priority, CEI, backup/restore e checker são `NONE_APPROVED` para latência; apenas duração, queries, cardinalidade e bytes podem ser reportados.
- **BLOCKED_EVIDENCE:** esta segunda tentativa foi interrompida de forma controlada após cerca de 19 minutos no primeiro run. O SQLite descartável chegou a 210.395.136 bytes; o worker consumia CPU, mas não havia JSON de run, amostra publicada ou progresso verificável após o setup. O comando terminou exit 1 pela interrupção, sem criar `quality/v05-s9-bcr1-result.json`. O banco temporário específico desta tentativa foi removido após constatar encerramento dos processos. A tentativa A4 anterior também ultrapassou 18 minutos sem resultado; a repetição demonstra custo de coleta desproporcional neste ambiente. Nenhuma das tentativas constitui FAIL de produto ou fornece p95 parcial.
- FTS: `FTS_NOT_JUSTIFIED` segundo o A4 e BCR histórico S8; decisão S9 final depende da medição atual. Nenhum FTS, índice, policy ou migration implementado.
- As medições V0.5 sem threshold (Domain em lote/hierarquia, Priority, CEI export/validation, backup/preview e checker SQLite) exigiam a fixture BCR preparada. Como o primeiro run não concluiu nem publicou um banco/resultados aproveitáveis e o harness limpa seu banco descartável, não há cardinalidade/queries/tempos comparáveis para reportar. Nenhum SLA ou PASS/FAIL temporal foi atribuído a essas operações.

## Findings reproduzidos antes das edições

| ID | Superfície e evidência | Severidade / causa provável | Menor correção e teste | Contrato protegido |
| --- | --- | --- | --- | --- |
| S9-F01 | `/questions/` vazio exibia `Total: 0 questãoes encontradas.` em Brave; o teste novo falhou antes da correção. | Minor, flexão literal incorreta no template. | Renderizar singular/plural completos em `questions/list.html`; `test_question_search.py::test_ct085_list_view_has_visible_filters_hierarchical_validation_and_empty_state` passou após a mudança. | Busca, paginação e SavedFilter sem mudança semântica. |
| S9-F02 | README dizia que V0.5 não estava autorizada, enquanto o contrato S9 está autorizado e S1–S8 estão concluídas. A4 já registrava o drift. | Minor documental; resumo obsoleto. | Atualizado estado beta e links para fontes S7/contrato. | Sem declarar promoção, release ou S10. |
| S9-F03 | Guia Windows V0.4 não apontava o fluxo V0.5 `/dados/` e encerrava com S9 sem autorização. A4 já registrava a lacuna. | Minor documental; guia anterior à S7 V0.5. | Incluído link ao procedimento S7 e distinção de adoção offline. | CEI, backup e restore preservados. |

## Acessibilidade e browser

- `AUTOMATED`: baseline focado acima; testes da busca, taxonomia, S3 UI, Priority e S7 UI cobrem estados e markup. Teste específico novo reproduziu S9-F01 (1 falha intencional antes; 1 passed em 6,49 s depois).
- `STATIC_REVIEW`: `base.html` tem skip link, `main` focável e navegação nomeada; templates centrais examinados têm headings, labels, feedback textual e controles nativos. ZIP/restore permanece descrito em texto, sem informação dependente só de cor. Revisão estática não prova reflow ou foco visual.
- `MANUAL_BROWSER_OBSERVED`: Brave (versão não obtida), aplicação sintética descartável em `127.0.0.1:8765`, viewport explícito de 360 × 800 CSS px, DPR observado 1. Em `/taxonomy/`, `/categories/`, `/questions/`, `/prioridades/` e `/dados/`, `documentElement.scrollWidth = 345` com `innerWidth = 360`; capturas exibiram conteúdo legível nas áreas examinadas, sem overflow horizontal do documento. O override de viewport foi restaurado.
- Teclado: em `/taxonomy/`, Tab mostrou foco visível no skip link; Enter levou a `#conteudo-principal`. Em `/questions/`, Tab percorreu skip link → marca; Shift+Tab retornou ao skip link. Formulário de disciplina inválido exibiu erro e focou `Nome`; após correção, criou disciplina sintética. Categoria vazia acionou validação nativa no campo; Cancelar voltou à lista sem criação. Busca vazia, filtro salvo e aplicação foram observados em browser.
- Priority: com um Subject sintético sem Questions, a página mostrou explicitamente `Coletar mais evidências` e motivos de insuficiência; estado ranqueado não foi preparado/observado nesta sessão.
- `/dados/`: formulário, labels, botões e orientação de preparação offline observados em browser. Um backup sintético foi criado para preview, mas a ferramenta de browser recusou selecionar o arquivo; preview válido/erro/cancelamento não foram observados.
- **Evidência obrigatória pendente:** zoom **nativo** de 200% não foi alcançado/observado; atalhos enviados à aba não alteraram a escala observada. Não tratar viewport de 360 px como substituto do zoom. Também faltam estado ranqueado e workflow visual completo de restore. A versão exata do Brave não foi obtida; acesso à página interna de versão foi recusado pela política do navegador e não deve ser contornado.

## Segurança local e Windows

- Baseline automatizado passou para isolamento Workspace, payload fechado de SavedFilter, ZIP/manifest/checksum, staging, rejeição antes de mutação, backup/restore e sanitização de logs nos testes focados. Revisão estática confirmou entradas ZIP em allowlist sem separadores/path traversal, checksums SHA-256, staging temporário e sanitização de chaves/valores sensíveis em logs. Não houve alteração de serviços S7/S8.
- Ensaio Windows em SQLite sintético sob `.tools/s9-manual`: migration/bootstrap exit 0; launcher `scripts/start-local.ps1` iniciado por PowerShell com `-ExecutionPolicy Bypass` a partir de CWD externo, porta explícita 8765 e host `127.0.0.1`; `/health/` retornou HTTP 200, `healthy`, DB `ok` e `X-Correlation-ID`. Segundo início na porta ocupada retornou exit 1 com orientação, sem trocar porta. Após Ctrl+C, porta 8765 foi verificada livre. O diretório sintético foi removido após checagem do alvo. Não houve restore no banco ativo.
- Limites ainda pendentes: path com espaços em execução real do launcher, se necessário; preview browser de restore; revisão final de logs/diff com detect-secrets no gate.

## Validação e conclusão pendentes

- Correção S9-F01: 1 teste específico passou após a reprodução RED. Após o diff, `tests/test_question_search.py` e `tests/test_v05_s3_ui.py` passaram: 23 testes, exit 0, 19,28 s. Regressões restantes são cobertas pelo gate completo, ainda pendente.
- A8 deep (revisão intermediária do contrato, A4, diff, V05-R08, budgets, FTS, UI, segurança local, Windows, S3/S6/S7/S8, migration, documentação e cleanup): **BLOCKED_EVIDENCE**, não `APPROVED`. Blockers de evidência: BCR oficial atual sem resultado e browser obrigatório incompleto (zoom nativo 200%, Priority ranqueada, preview/erro/cancelamento de restore); nenhum Major de código identificado no diff revisado. A8 deve ser repetido após obter essas provas.
- Gate attempt 1: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1` terminou **GREEN**, exit 0, em 340,7 s; `gate_first_pass = true`. Lock/sync, três perfis, migrations protegidas e banco vazio, formatação (384 arquivos), Ruff, mypy (193 fontes), cobertura mínima de domínio, detect-secrets e pip-audit passaram; 502 testes passaram em 279,64 s com 86% de cobertura global. Houve 2 `ResourceWarning` de conexões SQLite não fechadas no teste S2D; não derrubaram o gate e não foram classificados como finding S9 sem reprodução causal. Nenhuma tentativa RED de quality gate. Este resultado valida a working tree automatizada, mas **não** satisfaz sozinho o Done When da S9 enquanto A8 e evidências obrigatórias permanecem bloqueados.
- `PROJECT_STATE.md` permanece histórico S8; contrato não arquivado; `tasks/current.md` segue `AUTHORIZED`. Nenhum commit, push, tag, release, piloto, promoção ou S10.

### Roteiro humano ainda necessário para fechar a evidência visual

Em uma instalação SQLite sintética descartável, registrar Brave/Chromium e versão, viewport CSS e zoom **nativo** confirmado em 200% para `/taxonomy/`, `/categories/`, `/questions/`, `/prioridades/` e `/dados/`. Percorrer Tab, Shift+Tab, Enter e Space em controles apropriados; registrar foco visível e ordem. Exercitar vazio/erro/correção/cancelamento, filtro salvo incompatível, Priority com ranking e coleta, e restore com preview válido, arquivo inválido e cancelamento, sem adoção no banco ativo. Para cada estado, registrar página, ação, resultado, clipping/overflow e identificação da fixture sintética. A captura de 360 px sem zoom não substitui essa prova.

## Continuação de 2026-09-26 — preparação para coleta humana

- Preflight: as mudanças Git presentes continuam restritas à S9 (`README.md`, guia Windows, template/teste de busca, contrato, A4 e esta evidence); `git diff --check` exit 0. Nenhuma alteração anterior foi descartada.
- Diagnóstico read-only do BCR: `run_bcr1.py` executa três workers sequenciais e escreve o JSON final somente após os três encerrarem. Cada worker migra um SQLite temporário, prepara 10.000 Questions, 100.000 Attempts e 100.000 Reviews, mede leituras, paginação, três escritas e atualização de dashboard; só então grava `run-N.json`. O método usa 20 warm-ups e 100 amostras por operação; preparação, chamadas frias, warm-ups e paginação não são p95. Não há progresso granular emitido durante o run. No BCR histórico S8, somente a soma das amostras medidas de leitura ocupou aproximadamente 626 s, 591 s e 1.000 s nos três runs, sem contar setup e warm-ups. Nas tentativas S9 anteriores o worker consumiu CPU e o SQLite temporário cresceu até 210.395.136 bytes, sem JSON completo. Isso é compatível com trabalho caro; não constitui indício concreto de hang nem FAIL do produto.
- Decisão operacional: **BCR_HUMAN_TERMINAL_REQUIRED** por duração e confiabilidade da sessão. Não houve terceira execução longa nem alteração do harness, fixture ou estatística. O comando oficial para PowerShell em `C:\src\Projeto` é `& .\.venv\Scripts\python.exe .\scripts\run_bcr1.py --result .\quality\v05-s9-bcr1-human-20260926.json`; o caminho novo foi verificado ausente nesta continuação. Antes de rodar, confirmar que continua ausente; não sobrescrever se existir. Aguardar o processo concluir mesmo com longo silêncio. O sucesso exige exit 0 e `status: PASS` no JSON; exit 1/`FAIL` exige análise do resultado, e ausência de JSON não fornece p95. O BCR cria bancos descartáveis em `%TEMP%\cei-bcr1-*`, remove cada um ao fim do worker e remove o diretório ao concluir.
- Fixture browser isolada criada em `C:\src\Projeto\.tools\s9-evidence\data.sqlite3` com dados exclusivamente sintéticos. Há um Subject ranqueado com score, fatores, motivos e link, mais um Subject em “Coletar mais evidências”. Backup válido: `.tools\s9-evidence\valid-backup.sqlite3` e `.tools\s9-evidence\valid-backup.sqlite3.manifest.json`; arquivo inválido: `.tools\s9-evidence\invalid-backup.sqlite3` (usar com o mesmo manifesto). Os arquivos e auxiliares `seed.py`/`verify.py` são ignorados pelo Git e permanecem para coleta manual.
- Verificação automatizada pontual contra essa base: migration/bootstrap e seed exit 0; GET `/prioridades/` HTTP 200 exibiu os dois estados; POST de preview válido HTTP 200 exibiu impacto e contagens; POST de cancelamento HTTP 200 exibiu feedback; POST com SQLite inválido HTTP 200 exibiu erro recuperável. SHA-256 do SQLite ativo antes/depois dessas chamadas foi idêntico. O serviço validou o backup e a cópia isolada com 25 checks de integridade e 0 findings. Nenhum restore foi preparado ou aplicado. Isso não substitui observação visual/teclado humana.
- Para iniciar a fixture, em PowerShell no projeto: `$env:CEI_DEVELOPMENT_DB = (Resolve-Path '.tools\s9-evidence\data.sqlite3').Path`; depois `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-local.ps1 -Profile development -Port 8765`. URL: `http://127.0.0.1:8765/`. Encerrar com Ctrl+C. Este processo usa apenas a base descartável apontada; não usar dados pessoais. Na tela `/dados/`, executar somente preview e Cancelar, nunca confirmar/preparar/adotar restore.
- Evidência humana pendente: versão do navegador; zoom nativo 200% e viewport 360 × 800 CSS px nas cinco rotas; teclado/foco; Priority ranqueada/coleta; preview válido, cancelamento e erro inválido. A8 deep permanece `BLOCKED_EVIDENCE`; o gate GREEN anterior foi mantido, sem repetição. `tasks/current.md` permanece `AUTHORIZED`; S9 não foi arquivada, `PROJECT_STATE.md` não foi atualizado, e S10 continua não autorizada. Nenhum commit/push/tag/release.

## Investigação read-only do BCR oficial manual — 2026-09-26

O usuário informou que `quality/v05-s9-bcr1-human-20260926.json` foi produzido após execução completa, com exit 1. O JSON preservado registra `status: FAIL`, `ct107_status: PASS`, `read_status: FAIL`; os três runs estão presentes. Não houve repetição nesta investigação. Valores abaixo em segundos; queries `—` indicam que o harness não registra contagem para as três escritas. `OBSERVED` significa ausência de budget formal, não PASS temporal.

| Run | Operação | Mediana | p95 | Máximo | Queries/amostra | Budget | Status |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | save_question | 0,0211 | 0,0327 | 0,0492 | — | 2 s | PASS |
| 1 | save_attempt | 0,0172 | 0,0335 | 0,0492 | — | 2 s | PASS |
| 1 | complete_review | 0,0426 | 0,0712 | 0,1667 | — | 2 s | PASS |
| 1 | dashboard | 2,0074 | 2,4285 | 2,5693 | 15 | 3 s | PASS |
| 1 | analytics_summary | 2,1927 | 2,7561 | 3,0207 | 14 | — | OBSERVED |
| 1 | review_queue | 1,9179 | 2,2691 | 2,4609 | 4 | 3 s | PASS |
| 1 | question_list | 0,0763 | 0,0976 | 0,3788 | 9 | 3 s | PASS |
| 1 | question_search | 0,0900 | 0,1194 | 0,1339 | 9 | 2 s | PASS |
| 1 | question_filters | 0,0714 | 0,0868 | 0,1325 | 10 | 2 s | PASS |
| 1 | question_search_filters | 0,0606 | 0,1071 | 0,1395 | 10 | 2 s | PASS |
| 1 | question_late_page | 0,3339 | 0,4345 | 0,5543 | 9 | 3 s | PASS |
| 1 | question_detail | 0,0075 | 0,0095 | 0,0132 | 6 | — | OBSERVED |
| 1 | learning_timeline | 0,0127 | 0,0150 | 0,0193 | 10 | — | OBSERVED |
| 1 | dashboard_update | 2,2018 | 2,5955 | 2,8177 | 15 | 3 s | PASS |
| 2 | save_question | 0,0209 | 0,0276 | 0,1118 | — | 2 s | PASS |
| 2 | save_attempt | 0,0172 | 0,0246 | 0,0306 | — | 2 s | PASS |
| 2 | complete_review | 0,0442 | 0,0724 | 0,1183 | — | 2 s | PASS |
| 2 | dashboard | 2,0089 | 2,4559 | 2,5695 | 15 | 3 s | PASS |
| 2 | analytics_summary | 2,0005 | 2,4887 | 2,7603 | 14 | — | OBSERVED |
| 2 | review_queue | 1,9843 | 2,3715 | 2,7346 | 4 | 3 s | PASS |
| 2 | question_list | 0,0843 | 0,1392 | 0,3851 | 9 | 3 s | PASS |
| 2 | question_search | 0,1023 | 0,1302 | 0,1819 | 9 | 2 s | PASS |
| 2 | question_filters | 0,0759 | 0,0910 | 0,1406 | 10 | 2 s | PASS |
| 2 | question_search_filters | 0,0636 | 0,0778 | 0,1120 | 10 | 2 s | PASS |
| 2 | question_late_page | 0,3320 | 0,4430 | 0,4948 | 9 | 3 s | PASS |
| 2 | question_detail | 0,0077 | 0,0111 | 0,0570 | 6 | — | OBSERVED |
| 2 | learning_timeline | 0,0131 | 0,0152 | 0,0220 | 10 | — | OBSERVED |
| 2 | dashboard_update | 2,2832 | 2,6538 | 2,9056 | 15 | 3 s | PASS |
| 3 | save_question | 0,0242 | 0,0392 | 0,0953 | — | 2 s | PASS |
| 3 | save_attempt | 0,0189 | 0,0289 | 0,1037 | — | 2 s | PASS |
| 3 | complete_review | 0,0422 | 0,0722 | 0,1237 | — | 2 s | PASS |
| 3 | dashboard | 2,4407 | 3,3304 | 4,2996 | 15 | 3 s | FAIL |
| 3 | analytics_summary | 2,3060 | 2,7927 | 2,9135 | 14 | — | OBSERVED |
| 3 | review_queue | 2,0786 | 3,4611 | 43,7913 | 4 | 3 s | FAIL |
| 3 | question_list | 0,0846 | 0,1288 | 0,4415 | 9 | 3 s | PASS |
| 3 | question_search | 0,1189 | 0,1936 | 0,2231 | 9 | 2 s | PASS |
| 3 | question_filters | 0,0748 | 0,1415 | 0,1849 | 10 | 2 s | PASS |
| 3 | question_search_filters | 0,0649 | 0,1014 | 0,1085 | 10 | 2 s | PASS |
| 3 | question_late_page | 0,3095 | 0,4005 | 0,4696 | 9 | 3 s | PASS |
| 3 | question_detail | 0,0105 | 0,0161 | 0,0384 | 6 | — | OBSERVED |
| 3 | learning_timeline | 0,0133 | 0,0221 | 0,0449 | 10 | — | OBSERVED |
| 3 | dashboard_update | 2,1731 | 2,6070 | 2,7855 | 15 | 3 s | PASS |

**Todas e somente as operações `FAIL`:** `dashboard` e `review_queue`, ambas no run 3. As três escritas passaram nos três runs; `question_search`, `question_filters` e `question_search_filters` passaram nos três runs sob 2 s. `FTS_NOT_JUSTIFIED` permanece, sem abertura de implementação FTS. Paginação passou nos três runs: 8.000/8.000 IDs únicos, 800 páginas e 2.403 queries em cada um.

### Distribuição temporal do run 3

- `dashboard` teve 9/100 amostras acima de 3 s: nº 13=3,5415; 14=4,2996; 15=3,4288; 59=3,5729; 60=3,3101; 61=3,0438; 62=3,6406; 63=3,2884; 64=3,3304. Clusters consecutivos 13–15 e 59–64. Runs 1/2: mediana 2,0074/2,0089; p95 2,4285/2,4559; máximo 2,5693/2,5695; zero amostras acima de 3 s. Todas as amostras dos três runs fizeram 15 queries.
- `review_queue` teve 6/100 acima de 3 s: nº 51=4,5516; 52=43,7913; 53=7,2358; 54=3,4611; 80=10,0371; 81=3,8864. Clusters 51–54 e 80–81. Runs 1/2: mediana 1,9179/1,9843; p95 2,2691/2,3715; máximo 2,4609/2,7346; zero amostras acima de 3 s. Todas as amostras dos três runs fizeram 4 queries. O valor 43,7913 s permanece integral no resultado; p95 oficial é 3,4611 s, sem descarte ou recálculo.
- As amostras posteriores de `dashboard` e `review_queue` voltaram abaixo de 3 s; `question_list`, busca, filtros, página posterior e `dashboard_update` subsequentes passaram. Os índices indicam agrupamentos dentro de cada operação, mas o JSON não traz timestamp externo, uso de CPU/disco, temperatura, frequência ou processo concorrente para vincular os picos a uma causa ambiental.

### Comparação histórica e atribuição

- O BCR V0.4-S8 (`quality/v04-s8-bcr1-result.md` e JSON bruto) e o atual compartilham seed `20260909`, fingerprint do dataset `bbcf0d7f:...:e1cd3577:86190d98`, 10.000 Questions, 100.000 Attempts, 100.000 Reviews, 200 itens por nível, datas sintéticas, 20 warm-ups, 100 amostras, 3 runs, p95 nearest-rank e os mesmos budgets. Ambos registram Windows 11 build 26200, Python 3.13.15, Django 5.2.17, SQLite 3.53.1, 8 CPUs lógicas e 16 GiB RAM; o tipo de storage não foi registrado. O espaço livre em `%TEMP%` difere. A especificação de hardware coincide, mas carga/energia/atividade do sistema não foram capturadas; tempos distintos não bastam para atribuição de regressão.
- p95 histórico → atual: `dashboard` 1,7501–1,8390 → 2,4285–3,3304 s (15→15 queries); `review_queue` 0,9040–1,0279 → 2,2691–3,4611 s (3→4); `question_list` 0,0852–0,1102 → 0,0976–0,1392 (8→9); busca 0,1275–0,1426 → 0,1194–0,1936 (8→9); filtros 0,0770–0,1008 → 0,0868–0,1415 (9→10); busca+filtros 0,0663–0,0792 → 0,0778–0,1071 (9→10); página posterior 0,3607–0,4097 → 0,4005–0,4430 (8→9); `dashboard_update` 1,6190–1,7904 → 2,5955–2,6538 (15→15). Detalhe 6→6 e analytics 14→14; timeline 7→10. As contagens atuais são constantes por operação em todos os runs; a comparação histórica cruza versões do produto, não códigos idênticos.
- `PRODUCT_EVIDENCE`: o FAIL medido de duas telas no run 3 é real; os p95 atuais de dashboard/fila estão acima dos históricos também nos runs PASS. Há mudanças implementadas desde V0.4-S8: a fila atual usa prefetch de revisão corrente (uma query adicional coerente com 3→4); a listagem atual consulta SavedFilters (uma query adicional coerente com 8→9). Isso mostra mudança estável de trabalho entre versões, mas não explica deterministamente o pico de 43,7913 s, os clusters apenas no run 3 ou a volta a PASS das operações posteriores. Nenhum arquivo do harness ou das rotas medidas tem diff não commitado nesta investigação.
- `ENVIRONMENTAL_EVIDENCE`: nenhum dado direto de processo concorrente, scan, energia, thermal throttling ou contenção de disco foi coletado durante o run. Os clusters e a recuperação posterior são compatíveis com perturbação transitória, mas não provam sua origem.
- `UNKNOWN`: causa imediata dos picos, contribuição relativa da carga normal do host versus mudanças do produto e reprodutibilidade do FAIL em uma execução independente. Não há evidência para retirar o outlier ou reclassificar o FAIL.

**Classificação: `BCR_TRANSIENT_SUSPECTED_REPRODUCTION_REQUIRED`.** O FAIL original fica preservado. Planejada **uma** repetição oficial controlada, não executada nesta sessão, com o mesmo `scripts/run_bcr1.py`, fixture, seed, 20 warm-ups, 100 amostras, 3 runs, budgets e novo JSON `quality/v05-s9-bcr1-repeat-20260926.json` (verificado ausente). Antes de iniciar: máquina ligada à energia e em plano normal/estável; sem outro benchmark, teste manual no browser ou processo de desenvolvimento desnecessário; evitar atualização/scan pesado conhecido durante a coleta. Preservar antivírus e segurança normais, sem construir ambiente artificial. Registrar condições observadas e o resultado inteiro, inclusive eventual FAIL. Repetição não autoriza mudança de policy, query, threshold ou harness.

S9 continua `BLOCKED_EVIDENCE`; A8 final, fechamento, arquivamento, commit/push/tag/release e S10 não ocorreram. Nenhum código foi corrigido nesta investigação. O gate GREEN anterior não foi repetido.

## Evidências recebidas para o fechamento — 2026-09-26

- O primeiro BCR oficial, `quality/v05-s9-bcr1-human-20260926.json`, permanece preservado integralmente: `FAIL` global, CT-107 `PASS`, leitura `FAIL`; somente `dashboard` e `review_queue` falharam, ambas no run 3. A investigação acima classificou `BCR_TRANSIENT_SUSPECTED_REPRODUCTION_REQUIRED`; causa imediata não foi confirmada.
- O usuário informou exit 0 da repetição controlada `quality/v05-s9-bcr1-reproduction-20260926.json`. Inspeção direta do JSON confirma `status: PASS`, `ct107_status: PASS`, `read_status: PASS`; os três runs de escrita e leitura, busca/filtros e paginação passaram. Método, seed, contagens e fingerprint da fixture são iguais aos do primeiro BCR. p95 do `dashboard`: 2,2845/2,3461/2,3093 s; de `review_queue`: 2,1439/2,1024/2,2125 s, todos sob o budget de 3 s. Busca, filtros e busca+filtros passaram nos três runs sob 2 s. O FAIL anterior não se reproduziu. Classificação do episódio: **`TRANSIENT_NOT_REPRODUCED`**, sem regressão de produto confirmada por esses dois resultados e sem atribuir causa ambiental como fato. `FTS_NOT_JUSTIFIED` permanece; nenhum FTS foi implementado.
- `MANUAL_USER_OBSERVED`: o usuário informou PASS em todos os cenários que testou, em Brave/Chromium sobre a base sintética descartável `.tools/s9-evidence`: zoom **nativo 200%**, viewport **360 × 800 CSS px**, rotas `/taxonomy/`, `/categories/`, `/questions/`, `/prioridades/` e `/dados/`, navegação por teclado/foco, Priority ranqueada e “Coletar mais evidências”, preview de backup válido, cancelamento e arquivo inválido com erro recuperável. Nenhum problema foi relatado nesses cenários; nenhum restore foi aplicado ao banco ativo. Versão do navegador, screenshots, medidas individuais de layout e detalhes específicos de foco por página não foram informados. Esta declaração humana não é evidência automatizada nem inspeção visual feita pelo agente.

### Medições V0.5 sem budget temporal

O A4 exigia caracterizar operações V0.5 ausentes do BCR-1 oficial. A coleta suplementar foi executada em um **único SQLite descartável** preparado por `prepare_dataset(DEFAULT_DATASET)`, com o mesmo seed, composição e fingerprint dos BCRs oficiais; não é uma quarta execução BCR-1 nem altera seu método/status. O resultado bruto reproduzível está em `quality/v05-s9-v05-operations-measurement.json`: três chamadas sequenciais por operação após setup, relógio fixo `2026-09-09T15:00:00+00:00` para Domain, sem warm-ups/p95 inventados. Queries foram capturadas em Domain/Priority e pelo checker; para operações de arquivo permanecem não capturadas. `NONE_APPROVED` significa **sem decisão PASS/FAIL de latência**, mesmo quando a duração é alta.

| Operação | Durações brutas (s) | Queries | Cardinalidade/bytes e resultado semântico |
| --- | --- | --- | --- |
| Domain lote | 0,444 / 0,377 / 0,505 | 8 por chamada | 200 Questions avaliadas |
| Domain hierarquia | 0,202 / 0,210 / 0,178 | 11 por chamada | Discipline com 40 Questions consideradas; 10 exclusões |
| `/prioridades/` | 15,835 / 16,190 / 15,786 | 15 por request | HTTP 200; 200 Subjects e 8.000 Questions ativas |
| CEI export | 28,443 / 30,637 / 27,488 | não capturadas | três ZIPs de 32.240.295 bytes; 22 entradas manifestadas |
| CEI validate | 15,616 / 17,417 / 15,371 | não capturadas | 10.000 Questions validadas por pacote; 21 conjuntos |
| Backup create | 32,688 / 35,630 / 35,102 | não capturadas | três SQLite de 210.386.944 bytes, com manifesto validado |
| Backup validate | 16,896 / 15,490 / 15,717 | não capturadas | três pares válidos de 210.386.944 bytes |
| Restore preview isolado | 93,336 / 99,663 / 96,352 | não capturadas | 10.000 Questions reconciliadas por cópia; 25 checks, 0 findings em cada; hash do banco ativo igual antes/depois |
| Checker S8 read-only | 28,771 | 26 | 25 checks, 0 findings; hash do banco igual antes/depois |

A exportação e a validação foram medidas separadamente; a importação em destino vazio era apenas contextual/condicional no A4 e não foi executada como benchmark. O preview não preparou nem adotou restore. A duração da página Priority é uma observação de risco para uma etapa futura, sem budget normativo aplicável e sem autorização para tuning especulativo. Os arquivos de fixture e pacotes desta coleta foram descartados após conferir os resultados; o JSON de medidas permanece.

### Segurança, Windows e cleanup final

- Auditoria do diff e dos artefatos: apenas contrato/plano/evidence S9, os dois JSONs BCR, medição V0.5, README, guia Windows e correção textual/teste de `/questions/` estão no escopo. Não foram encontrados valores de secret, dados pessoais, caminhos privados ou artefatos inesperados; as ocorrências de `CEI_SECRET_KEY` no README/guia são comandos para gerar chave, não valores persistidos. `git diff --check` passou antes da revisão. Nenhum módulo Domain/Priority, CEI, checker, migration ou harness foi alterado.
- Ensaio complementar Windows: launcher existente iniciado de um CWD com espaços (`.tools/s9 path check`) com `CEI_DEVELOPMENT_DB` apontando ao SQLite sintético; iniciou em `127.0.0.1:8766`, `/health/` retornou HTTP 200, application/database `ok` e correlation ID. O Ctrl+C enviado pelo terminal automatizado não alcançou o subprocesso aninhado; o PID Python identificado pelo horário e caminho deste ensaio foi parado explicitamente e a porta 8766 ficou livre. O ensaio anterior já havia observado encerramento normal por Ctrl+C. Não houve uso de banco real.
- Cleanup: após verificar caminhos absolutos contidos em `C:\src\Projeto\.tools`, foram removidos somente `.tools/s9-evidence` (6 arquivos sintéticos), `.tools/s9-scale` (11 arquivos de fixture/medição) e `.tools/s9 path check` (vazio). Os dois JSONs BCR e `quality/v05-s9-v05-operations-measurement.json` ficaram preservados; nenhuma evidence permanente foi removida.

### A8 deep final — revisão do diff e da evidence antes do gate final

**Resultado: APPROVED; Blocker 0, Major 0, Minor 1.** Revisão de `tasks/current.md`, A4, diff real, testes/evidências, limpeza, migration `NO`, contratos S3/S6/S7/S8 e limites S10/V1. O único finding funcional S9-F01 tinha reprodução RED, correção textual mínima e teste GREEN; README e guia Windows corrigem gaps documentais observados. Nenhum serviço, policy, migration, checker, formato CEI, harness, threshold, dependência ou fluxo de restore foi modificado. `git diff --check` aprovado.

- BCR V05-R08: FAIL inicial preservado e diagnosticado; reprodução oficial completa PASS, sem causa ambiental afirmada; buscas/filtros PASS e `FTS_NOT_JUSTIFIED`. Domain, Priority, CEI, backup/preview e checker receberam as medidas brutas sem SLA novo, inclusive a duração observada de Priority. Ausência de regressão de produto confirmada por evidência disponível.
- Acessibilidade: testes automatizados, revisão estática, browser anteriormente observado e relato humano `MANUAL_USER_OBSERVED` estão rotulados separadamente. O usuário informou PASS para zoom nativo 200%, 360 × 800, teclado/foco, Priority ranqueada/coleta e restore preview/cancel/erro. **Minor 1 — precisão da evidence manual:** versão exata do navegador e detalhes por página não foram informados; não foram inventados nem convertidos em observação direta do agente. Não há defeito de acessibilidade relatado nesses cenários.
- Segurança/operação: testes focados existentes cobrem Workspace, entradas/ZIP/manifest/staging, restore sem mutação em preview, logs e checker read-only; ensaio local em DB sintético cobriu loopback, health, porta ocupada/stop e CWD com espaços. Scan do diff/evidence não encontrou valor de secret, dado pessoal ou path privado indevido. Artefatos sintéticos foram removidos depois de verificação de alvo; JSONs permanentes permanecem.
- Regressões: baseline focado 134 testes, teste específico RED→GREEN e 23 testes focados pós-diff já registrados acima; gate anterior GREEN com 502 testes/86% e exit 0. O novo gate final ainda será executado após esta revisão, conforme instrução de fechamento. Qualquer RED relevante invalida este APPROVED até correção/revisão.

Nenhum P0/P1 aplicável aberto foi identificado. O A8 não declara promoção V0.5, piloto, release ou S10.

### Gate final — tentativa 2, ambiente restrito

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1` terminou **RED, exit 1** após aproximadamente 6 minutos. Lock/sync, runtime, rastreabilidade, três perfis, migrações, formatação, Ruff, mypy, 502 testes em 285,41 s, 86% de cobertura, cobertura de domínio e detect-secrets passaram. Os testes emitiram 2 `ResourceWarning` de conexões SQLite no S2D, já observados na tentativa 1. A etapa `pip-audit` não concluiu: acesso ao cache de usuário negado e conexão HTTPS a `pypi.org` bloqueada pelo ambiente (`WinError 10013`). Classificação: **falha ambiental da auditoria de dependências, não falha comprovada do produto**. O gate anterior GREEN permanece no histórico, mas esta tentativa RED não satisfaz o gate final. O A8 permanece válido para o diff revisado, condicionado a novo gate GREEN; nenhuma conclusão/arquivamento ocorreu nesta tentativa.

### Gate final — tentativa 3 e conclusão

O mesmo comando autoritativo foi repetido com acesso de rede permitido, sem mudar o script ou seus controles. Resultado **GREEN, exit 0**, duração observada **363,2 s**. Passaram lock/sync, runtime, rastreabilidade, checks dos três perfis, migrations protegidas e banco vazio, formatação (384 arquivos), Ruff, mypy (193 fontes), 502 testes em 284,65 s com 86% de cobertura, cobertura mínima de domínio, detect-secrets e `pip-audit` (`No known vulnerabilities found`). Houve os mesmos 2 `ResourceWarning` de conexões SQLite no teste S2D; não derrubaram o gate e não houve finding causal S9. Histórico: tentativa 1 GREEN, tentativa 2 RED ambiental, tentativa 3 GREEN; `gate_first_pass=true` permanece como fato da primeira tentativa da fase de implementação, sem apagar a tentativa RED posterior.

**Done When S9 verificado:** Migration `NO`; BCR original FAIL e reprodução PASS preservados; `TRANSIENT_NOT_REPRODUCED` sem causa ambiental afirmada; CT-107 e leituras PASS na reprodução; busca/filtros PASS, `FTS_NOT_JUSTIFIED`; operações V0.5 medidas sem threshold novo; evidence manual `MANUAL_USER_OBSERVED` PASS informado para 200% nativo, 360 × 800, Priority e restore preview/cancel/erro em base sintética; segurança local e operação Windows verificadas; S9-F01 corrigido/testado; A8 deep **APPROVED**, Blocker 0/Major 0/Minor 1; gate final GREEN. Sem P0/P1 aplicável aberto. `PROJECT_STATE.md` foi atualizado, o contrato foi arquivado como `COMPLETED` e `tasks/current.md` voltou a `NO_TASK_AUTHORIZED`. V0.5 não foi promovida, nenhum piloto/release/commit/push/tag ocorreu e S10 permanece `NOT AUTHORIZED`.
