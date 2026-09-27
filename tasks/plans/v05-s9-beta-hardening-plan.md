# A4 — V0.5-S9: hardening beta, BCR, acessibilidade, segurança/operação local e documentação

- Tarefa relacionada: `V0.5-S9` em `tasks/current.md`.
- Estado deste artefato: `COMPLETED` — investigação e planejamento A4 concluídos; a execução funcional S9 continua dependendo de nova instrução humana explícita.
- Data da auditoria: 2026-09-26.
- Escopo desta sessão: somente atualização autorizada do contrato para a fase A4 e este plano; sem implementação funcional.

## 1. Authority / baseline

- Contrato corrente: `V0.5-S9`, `Status: AUTHORIZED`, `Size: L`, `Risk: high`, classificação inicial de migration `UNLIKELY`, A4 obrigatório, A8 `deep`.
- Fase persistida durante a auditoria: `A4_AUTHORIZED`. O contrato veda implementação funcional, correção de findings, migration, FTS sem gate, atualização de estado como S9 concluída, arquivamento, commit/push/tag/release e S10.
- Baseline verificada após a transição administrativa: branch `main`; `HEAD = origin/main = 4a10cdf8fa44bbaf7240fa19532f6ba29354f246`; antes da auditoria A4, a única alteração era `tasks/current.md`.
- `git diff --check` passou após a alteração do contrato. A validação final deste A4 deve deixar somente `tasks/current.md` e este plano alterados.
- Há drift administrativo em `PROJECT_STATE.md` e `README.md`: ambos ainda registram V0.5-S9 como não autorizada, enquanto `tasks/current.md` autoriza S9. Para o escopo desta tarefa prevalece `tasks/current.md`; o drift foi registrado para a matriz documental futura, sem editar esses arquivos durante o A4.
- A conclusão deste plano fecha apenas a investigação A4. **A conclusão do A4 NÃO autoriza automaticamente a implementação da S9.** O contrato permanece `AUTHORIZED`; qualquer implementação exige nova instrução humana explícita.

## 2. Sources audited

Fontes de autorização e decomposição:

- `AGENTS.md`, `tasks/current.md`, `PROJECT_STATE.md`, `docs/A3_Progressive_Disclosure.md`, `tasks/plans/README.md` e `tasks/plans/v05-release-execution-plan.md`.
- `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md` para lifecycle, Workspace, auditoria, OD06 e fronteiras S7/S8.
- `docs/ADR-012_Parametros_Executaveis_BCR-1_e_CT-125_V0.3.md`, `tasks/plans/v04-release-execution-plan.md`, `tasks/completed/v04-s8-hardening-accessibility-bcr1.md` e `quality/v04-s8-bcr1-result.md` para BCR, método e budgets.
- Fechamentos/evidências: `tasks/completed/v05-s3-management-ui.md`, `quality/v05-s3-management-ui-result.md`; equivalentes S6, S7 e S8; `quality/v05-s5-domain-application-result.md` para medição de Domain.
- Busca, prioridade e Domain: `src/modules/search/{selectors.py,forms.py,saved_filter_views.py,models.py}`, `src/modules/priority/services.py`, `src/modules/domain/{services.py,selectors.py,policy.py}`, `src/modules/accounts/views.py`, `tests/test_question_search.py`, `tests/test_priority_integration.py` e `tests/test_v05_s5_domain.py`.
- UI e operações V0.5: URLs, views, forms, templates e testes em `accounts`, `taxonomy`, `errors`, `search`, `reviews`, `attempts`, `questions` e `data_management`; em especial `tests/test_v05_s3_ui.py`, `tests/test_taxonomy_interface.py`, `tests/test_question_interface.py`, `tests/test_v05_s7_ui.py` e `tests/test_v05_s7_portability.py`.
- Arquivos, restore e logging: `src/modules/data_management/{views.py,ui_services.py,portability.py,services.py}`, `src/modules/operations/{middleware.py,structured_logging.py,integrity.py}`, `tests/test_backup_restore.py`, `tests/test_backup_recovery.py`, `tests/test_operations.py` e `tests/test_windows_operation.py`.
- Operação/documentação: `scripts/start-local.ps1`, `scripts/start-local.cmd`, `docs/V0.4_S7_Operacao_Windows.md`, `docs/V0.5_S7_Portabilidade_e_Restore.md`, `docs/CEI_EXPORT_1_0.md`, `docs/README.md` e `README.md`.
- Evidência de acessibilidade anterior: `quality/v04-s8-accessibility-result.md`.

## 3. Dependency verification

| Dependência | Evidência corrente | Resultado relevante para S9 |
| --- | --- | --- |
| S3 gestão | `tasks/completed/v05-s3-management-ui.md`; `quality/v05-s3-management-ui-result.md` | Concluída; 423 testes no gate final, A8 standard APPROVED. `SavedFilter` tem migration própria já checkpointada. Não reabrir contratos S2A–S2D. |
| S6 Priority | contrato e `quality/v05-s6-priority-heuristic-result.md` | Concluída; 487 testes, A8 deep APPROVED, sem migration. Teste proporcional existente: 4 Subjects/12 Questions/14 queries, com teto de contagem 18; isso não é budget de latência. |
| S7 portabilidade | contrato e `quality/v05-s7-portability-result.md` | Concluída; 498 testes, A8 deep APPROVED, sem migration. CEI, backup e restore são contratos separados; preservar staging, preview, pré-backup e adoção offline. |
| S8 integridade/compatibilidade | contrato e `quality/v05-s8-integrity-compatibility-result.md` | Concluída no checkpoint atual; 502 testes, A8 deep APPROVED, Blocker/Major 0, sem migration. Checker permanece detector read-only; PostgreSQL não deve ser repetido em S9. |

S3/S6/S7/S8 são dependências fechadas, não escopo de redesign nem autorização para alterar semânticas anteriores.

## 4. Current-state inventory

- O mapa de URLs em `src/config/urls.py` confirma `/taxonomy/`, `/categories/`, `/questions/filters/`, `/questions/`, `/reviews/`, `/initial/`, `/prioridades/`, `/dados/` e `/health/`.
- A camada de busca usa `Question.workspace_id`, estado e revisão corrente; texto por `icontains` em `stem`/`explanation`, filtros Workspace-scoped, ordenação estável e paginação de 10 itens. Não há implementação FTS localizada.
- A página `/prioridades/` é a representação consultável de S6 e consome Domain S5 em lote; não há tela independente de política Domain além das explicações dessa recomendação.
- A UI `/dados/` oferece export funcional, backup operacional, preview e preparação de restore. A adoção no banco ativo fica em comando offline separado; não deve ser confundida com importação CEI.
- `src/modules/operations/integrity.py` é baseline S8 read-only. S9 pode caracterizar custo se houver motivo, mas não adicionar checks, repair, retenção, política de receipts, upgrade ou matriz PostgreSQL.
- Não foi encontrado documento geral de guia beta V0.5. README ainda descreve V0.5 como não autorizada; operação Windows e portabilidade V0.5 estão em documentos distintos existentes.

## 5. V0.5 surface matrix

| Superfície / rota | View, form, template e serviço | Mutabilidade e estados observáveis | Testes existentes / acessibilidade / gap S9 |
| --- | --- | --- | --- |
| Taxonomia `/taxonomy/…` usada pela gestão | `taxonomy/views.py`, `taxonomy/forms.py`; `taxonomy/{index,children,item_form,archive_confirm}.html`; serviços de taxonomia | Create/edit/archive; lista vazia, erro de validação, cancelamento e conflito de versão são estados aplicáveis. | `tests/test_taxonomy_interface.py`, inclusive empty, stale, cancel, CSRF e teste semântico/teclado/responsivo. Prova browser S9 ainda necessária para fluxos centrais e reflow/zoom. |
| Categorias pessoais `/categories/…` | `errors/views.py`, `errors/management_forms.py`; `errors/category_{list,form,confirm,merge}.html`; `PersonalCategoryService` | Create/rename/archive/merge; vazio, erro, stale/cross-Workspace, bloqueio de categoria padrão e retorno recuperável. | `tests/test_v05_s3_ui.py`, `tests/test_error_categories.py`. Testes cobrem serviço, stale e escopo; não equivalem a observação de teclado/foco em browser. |
| SavedFilters `/questions/filters/…` + listagem `/questions/` | `search/saved_filter_views.py`, `saved_filter_forms.py`, `search/selectors.py`; templates `questions/list.html` e `search/saved_filter_*.html` | Criar/aplicar/renomear/excluir; lista vazia, payload/context/schema incompatível, filtro obsoleto, erro e cancelamento. Aplicar é leitura; demais ações são POST. | `tests/test_v05_s3_ui.py` cobre CRUD, payload fechado, isolamento e contagem; `tests/test_question_search.py` cobre busca, filtros, paginação, empty e semântica/teclado/responsivo. Falta browser nas rotas de gestão do filtro. |
| Review management `/reviews/…` | `reviews/views.py`, `management_forms.py`; `reviews/{queue,reschedule,manual_inclusion,timeline}.html`; services S2A | Fila/timeline read-only; reschedule e inclusão manual mutáveis. Estados vazios, validação, stale conflict, cancelamento e sucesso são aplicáveis. | `tests/test_v05_s3_ui.py`, `tests/test_review_completion.py`; markup usa forms/labels/mensagens nativas. Confirmar foco e recovery visual/manual nos fluxos escolhidos. |
| Correção de Attempt `/initial/corrections/<uuid>/…` | `attempts/views.py`, `correction_forms.py`; `attempts/correction_preview.html`, `correction_void.html`, `correction_replace.html`; `AttemptCorrectionService` S2B | Preview read-only; void/replace mutáveis e confirmados. Erro, ponta stale, cancelamento, conflito e resultado recuperável importam. | `tests/test_v05_s3_ui.py`, `tests/test_v05_s2b.py`, `tests/test_question_interface.py`. Nenhuma mudança de história/policy autorizada por hardening. |
| Correção de gabarito e exclusão `/questions/<uuid>/{correct-answer-key,permanent-delete}/` | `questions/views.py`, forms de gestão; `answer_key_correction.html`, `permanent_delete_preview.html`; services S2C/S2D | Correção prospectiva; exclusão por preview/confirm/fingerprint/backup. Estados blocked, erro, stale, confirmação, cleanup/recovery e sucesso. | `tests/test_v05_s3_ui.py`, `tests/test_v05_s2c.py`, `tests/test_v05_s2d.py`, `tests/test_question_interface.py`. Browser deve cobrir aviso, confirmação, erros e retorno; nenhum teste manual destrutivo em banco real. |
| Priority + explicação Domain `/prioridades/` | `accounts.views.priority`, `accounts.priority.html`; `list_subject_priorities` S6 e serviços/policy Domain S5 | Read-only; resultados ranqueados, coleta de mais evidência e vazio. Evidência indisponível permanece distinta de zero. | `tests/test_priority_integration.py`, `tests/test_priority_policy.py`, `tests/test_v05_s5_domain.py`. HTML estruturado e texto explicativo presentes; falta evidência browser da nova tela e zoom/reflow observado. |
| Export, backup e restore `/dados/` | `data_management.views.portability`, `data_management/ui_services.py`; `data_management/portability.html`; serviços CEI e SQLite S7 | GET/preview read-only; export/download; confirmação prepara ticket e pré-backup para adoção offline. Estados erro, preview inválido, confirmação, cancelamento, preparado e recovery. | `tests/test_v05_s7_ui.py`, `tests/test_v05_s7_portability.py`, `tests/test_backup_restore.py`, `tests/test_backup_recovery.py`. Automatizados cobrem formatos, validação e reject-before-mutation; manual deve observar labels, teclado, reflow e estados sem aplicar restore no banco ativo. |
| Health e operação local `/health/`, launcher | `operations.health`, `LocalCorrelationMiddleware`; `scripts/start-local.ps1`, `scripts/start-local.cmd` | Health read-only saudável/indisponível; launcher inicia em loopback, trata porta ocupada e encerra no terminal. | `tests/test_operations.py`, `tests/test_windows_operation.py`; testes de launcher são predominantemente estáticos. Ensaio Windows S9 em DB descartável precisa confirmar start/health/shutdown/porta e paths. |

`S8 checker` não é uma nova superfície de produto S9; mantê-lo fora de mudanças funcionais e revalidá-lo somente se um finding concreto tocar esse contrato.

## 6. BCR-1 audit

### Parâmetros e budgets

- Definição de gravação: `docs/ADR-012_Parametros_Executaveis_BCR-1_e_CT-125_V0.3.md`; banco SQLite descartável, serviço real sem mock, 20 warm-ups excluídos, 100 amostras, 3 execuções independentes, p95 nearest-rank em `ceil(0.95 × N)`. `CT-107` exige cada gravação em cada execução `≤ 2 s`.
- Harness corrente: `src/shared/application/bcr1.py`, `bcr1_reads.py`, `scripts/run_bcr1.py`, `tests/test_bcr1.py`. O script mantém fixture determinística e bancos separados por execução; escreve JSON no destino informado por `--result` e limpa o diretório descartável.
- A extensão de leitura V0.4 usa 20 warm-ups/100 amostras; budgets vigentes documentados pelo plano S8 V0.4 e usados no resultado aprovado: tela `≤ 3 s`; busca/filtros `≤ 2 s`. Leitura sem budget formal permanece `OBSERVED`, nunca recebe PASS/FAIL inferido.

### Classificação

| Classe | Evidência/valor | Interpretação em S9 |
| --- | --- | --- |
| `APPROVED_BUDGET` | Gravações CT-107 `≤ 2 s`; tela BCR `≤ 3 s`; busca/filtros BCR `≤ 2 s` | Aplicar sem alteração às operações correspondentes; fontes: ADR-012 e plano S8 V0.4, confirmadas pela evidência BCR S8. |
| `MEASUREMENT_ONLY` | `analytics_summary`, `question_detail`, `learning_timeline` ficaram explicitamente `OBSERVED`; S5 mediu Domain em fixture de 40 Questions/5 Attempts por Question com `FixedClock` — uma Question 21,41 ms/8 queries; lote 112,06 ms/8; Subject 71,05 ms/11; Discipline 43,63 ms/11 — sem threshold; S6 tem teto de queries em cenário pequeno | Registrar os dados como medição/contagem, não como contrato temporal. |
| `HISTORICAL_REFERENCE` | `quality/v04-s8-bcr1-result.md` e JSON: seed `20260909`; 10.000 Questions, 100.000 Attempts, 100.000 Reviews, 200 entidades por nível taxonômico; Windows 11/Python 3.13.15/Django 5.2.17/SQLite 3.53.1; valores e contagens por operação | Evidência histórica útil para contexto e regressão, não prova automática do estado S9 atual. Comparar somente mesma operação/fixture/método. |
| `NO_APPROVED_THRESHOLD` | Domain em escala, Priority, SavedFilter gestão, CEI export/validation/import, backup, restore preview, checker | S9 pode coletar medidas reproduzíveis onde justificado, mas sem PASS/FAIL temporal ou SLA novo. |

`quality/v05-s6-priority-heuristic-result.md` registra 4 Subjects/12 Questions/14 queries e teto de teste 18; não é budget de tempo nem volume geral. A medição S5 de uma consulta e a fixture de 40 Questions não são comparáveis com a fixture BCR de 10.000 Questions.

### Leituras BCR-1 históricas por operação

| Operação S8 | Queries/amostra | p95 mínimo–máximo | Classificação preservada |
| --- | ---: | ---: | --- |
| Dashboard | 15 | 1,7501–1,8390 s | `APPROVED_BUDGET` 3 s; histórico PASS |
| Resumo analytics S2 | 14 | 1,5554–1,7992 s | `MEASUREMENT_ONLY` / OBSERVED |
| Fila de revisões | 3 | 0,9040–1,0279 s | `APPROVED_BUDGET` 3 s; histórico PASS |
| Listagem | 8 | 0,0852–0,1102 s | `APPROVED_BUDGET` 3 s; histórico PASS |
| Busca | 8 | 0,1275–0,1426 s | `APPROVED_BUDGET` 2 s; histórico PASS |
| Filtros | 9 | 0,0770–0,1008 s | `APPROVED_BUDGET` 2 s; histórico PASS |
| Busca + filtros | 9 | 0,0663–0,0792 s | `APPROVED_BUDGET` 2 s; histórico PASS |
| Página posterior | 8 | 0,3607–0,4097 s | `APPROVED_BUDGET` 3 s; histórico PASS |
| Detalhe | 6 | 0,0104–0,0143 s | `MEASUREMENT_ONLY` / OBSERVED |
| Timeline | 7 | 0,0143–0,0170 s | `MEASUREMENT_ONLY` / OBSERVED |
| Dashboard após gravação | 15 | 1,6190–1,7904 s | `APPROVED_BUDGET` 3 s; histórico PASS |

Fonte: `quality/v04-s8-bcr1-result.md`; estes números não são resultados S9. A travessia histórica de 8.000 Questions percorreu 800 páginas sem omissão/duplicação, 2.403 queries e 78,828/79,605/82,286 s nas três execuções, com fingerprint de ordenação estável. Esses tempos de travessia são referência histórica, sem budget normativo adicional.

### Benchmark existente executado nesta auditoria

- Comando: `& .\.venv\Scripts\python.exe scripts\run_bcr1.py --result $a4ResultPath`, onde `$a4ResultPath` foi um nome único em `%TEMP%` (`v05-s9-bcr1-<guid>.json`). Nenhum benchmark ou teste foi criado.
- Fixture pretendida pelo executor existente: seed `20260909`; 10.000 Questions, 100.000 Attempts, 100.000 Reviews e 200 itens por nível taxonômico; SQLite descartável, 3 runs completos.
- Ambiente observado no processo: Windows 11 `10.0.26200`; Python 3.13.15; Django 5.2.17; SQLite 3.53.1; CPU `AMD64 Family 23 Model 160 Stepping 0, AuthenticAMD`, 8 cores lógicos, 16 GiB RAM. Tipo de storage não observado pelo harness.
- Resultado: tentativa **interrompida/inconclusiva** antes de produzir resultado de um run ou qualquer p95. O primeiro banco chegou a 210.395.136 bytes e a execução passou de 18 minutos; não constitui `FAIL` de produto nem resultado BCR. Exit 1 decorreu da interrupção manual. A base descartável restante foi removida de `%TEMP%`; não há amostra S9 atual desta tentativa.
- Variabilidade: sem amostras concluídas, não quantificável. Não inferir busca lenta a partir do tempo de preparação/execução da fixture.
- Evidência completa disponível para a decisão atual: resultado S8 abaixo, obtido pelo mesmo harness e metodologia.

## 7. BCR measurement matrix

Usar o BCR sintético de seed `20260909`, isolado e sem dados pessoais. Setup, migrações e fixture ficam fora do trecho cronometrado. Registrar Windows, Python, Django, SQLite, CPU, RAM, storage disponível reportado, perfil, seed, composição e cada execução. `perf_counter_ns`/captura de queries já usados pelo harness são preferidos. Sem threshold, reportar os tempos brutos e queries por execução; não criar status PASS/FAIL, SLA ou estatística nova.

| Operação | Por que medir / fixture | Método e repetição | Budget aprovado | Prova necessária na execução S9 |
| --- | --- | --- | --- | --- |
| Dashboard, fila, listagem, busca, filtros, busca+filtros e página tardia | Cobertos no read harness e exercitam superfícies core; busca governa gate FTS. Fixture oficial 10k/100k. | Executar BCR existente integralmente; 20 warm-ups/100 amostras/3 bancos, p95 nearest-rank; guardar queries e reconciliação. | Tela 3 s; busca/filtros 2 s, nas operações correspondentes. | Nova medição atual; causa-raiz antes de qualquer correção se falhar. |
| SavedFilter aplicado à listagem | Reusa busca/listagem; teste existente prova queries constantes conforme quantidade de filtros. Não medir CRUD individual por padrão. | Reusar operação de busca/filtro com payload permitido; incluir query count/compatibilidade no teste S3. Só adicionar tempo se houver finding ou diferença material no plano de query. | Budget de busca/filtro 2 s; sem budget separado de SavedFilter. | Reconfirmar teste `test_saved_filter_compatibility_queries_do_not_grow_per_saved_filter`; medir no BCR apenas se o filtro introduzir caminho diferente. |
| Gestão/categorias pessoais | CRUD curto, sem evidência de lote/caminho de alto custo. | Não adicionar benchmark temporal de rotina; manter testes de serviço/contagem e medir apenas se profiling/finding concreto indicar. | `NONE_APPROVED`. | Nenhuma medição S9 pré-determinada. |
| Domain em lote/hierarquia | Nova leitura derivada sobre muitos fatos; a medição S5 foi em fixture pequena e sem threshold. | Reusar fixture BCR; `FixedClock` com instante explícito registrado; setup fora do tempo; 3 execuções raw de uma chamada representativa de lote e uma hierarquia; registrar tempo, rows e queries sem p95/limite novo. | `NONE_APPROVED`. | Sim; incluir no relatório como medida, não gate temporal. |
| Priority `/prioridades/` | Consome Domain, Attempts e Reviews em lote; único caminho S6 user-facing. | Mesma fixture e `FixedClock`; 3 requests independentes após setup; registrar tempos brutos, queries e quantidade de Subjects/Questions; sem concorrência artificial. | `NONE_APPROVED`; teto S6 de 18 queries não é threshold universal para outra escala. | Sim; medir e comparar apenas execuções equivalentes. |
| CEI export + validação/importação | Itera e valida múltiplos conjuntos; S8 round-trip foi semântico e não é medição de volume. | Fixture BCR; export e validate separados; importar somente em DB descartável vazio. 3 execuções isoladas; registrar duração, bytes, contagens, queries quando capturáveis e resultado semântico; sem p95 inventado. | `NONE_APPROVED`. | Sim para export/validation em escala; import somente como operação de contexto se a fixture compatível for preparada. |
| Backup, validação e preview de restore | Operações de arquivo/SQLite com staging, checksum e reconciliação sobre dados grandes. | Base descartável do BCR; medir separadamente create, validate e preview/restore isolado; repetir 3 vezes com artefatos próprios de cada run; nunca adotar no banco ativo. Registrar duração, bytes e contagens. | `NONE_APPROVED`. | Sim; não confundir tamanho/tempo observado com SLA. |
| Checker S8 | Read-only mas pode percorrer invariantes sobre o mesmo dataset. | Uma caracterização separada por DB BCR quando a fixture estiver pronta; registrar exit, checks/findings, duração e fingerprint before/after. Não executar matriz PostgreSQL. | `NONE_APPROVED`. | Sim apenas para custo/fingerprint; nenhum finding abre autorização de repair. |

Se o custo de executar repetição adequada dessas operações tornar a evidência desproporcional, classificar a lacuna como `BLOCKED_EVIDENCE` ou propor escopo/decisão humana; não substituir execução real por mock nem promover medida pequena a representativa.

## 8. Search / FTS decision gate

- Busca executável: `src/modules/search/selectors.py::list_questions`; filtro de Workspace/estado e revisão corrente, substring case-insensitive em enunciado/explicação, filtros por taxonomia, estado de revisão, resultado inicial/categoria, `.distinct()`, ordenação `-updated_at, id` e paginação estável de 10.
- Cobertura atual: `tests/test_question_search.py` (isolamento, filtro, empty, paginação/recuperação, escaping, link de detalhe, markup) e BCR `question_search`, `question_filters`, `question_search_filters`.
- BCR oficial S8 mediu busca em 10k Questions: p95 `0,1275–0,1426 s`; filtros `0,0770–0,1008 s`; busca+filtros `0,0663–0,0792 s`; 8/9 queries por amostra; 20 warm-ups, 100 amostras, 3 runs. Cada operação ficou abaixo do budget existente de 2 s. São resultados históricos, não PASS da execução S9.
- A tentativa atual de BCR foi interrompida durante o primeiro run, sem amostra e sem resultado; ela não altera a evidência S8 e não é falha de latência da busca.
- Decisão A4: **`FTS_NOT_JUSTIFIED`**. Existe caminho simples correto, budget aplicável e evidência BCR válida abaixo do budget; não há falha medida objetiva que exija FTS. Não adicionar FTS, índice especializado, ranking/fuzzy search ou migration.
- S9 deve repetir o BCR de busca atual. Só uma falha objetiva contra o budget aplicável, confirmada e atribuível à busca no escopo S9, permite reclassificar como `FTS_CANDIDATE_BY_MEASURED_FAILURE`; investigar primeiro query/ORM, N+1, índice já permitido, redundância e paginação. Falha de outro endpoint ou tentativa incompleta não abre esse gate.

## 9. V05-R08 — regressão de performance/acessibilidade

| Risco | Superfície/operação | Proteção/evidência atual | Gap | Prova S9 / aprovação |
| --- | --- | --- | --- | --- |
| Performance | Dashboard/listagem/busca/filtros | BCR S8 em fixture de escala, budgets de telas e busca existentes; regressões de queries. | Não é evidência executada no checkpoint S9; novas rotas Priority/portabilidade não estão no BCR. | BCR atual passa nos budgets existentes; novas rotas têm medições raw reprodutíveis sem threshold novo; causa de qualquer falha deve ser identificada. |
| Performance | Domain/Priority batch | S5 mediu fixture pequena sem latência normativa; S6 tem teste de queries em 4 Subjects/12 Questions. | Escala realística 10k/100k não caracterizada. | Clock/seed fixos, execuções raw, queries e cardinalidade registradas; nenhum budget temporal atribuído. |
| Performance | Export, import validation, backup, restore preview, checker | Testes e round-trip/recovery cobrem correção e integridade; medição de grande volume ausente. | Tempo/tamanho sob escala BCR desconhecidos. | Medir funções separadas em cópias descartáveis; validar conteúdo/contagens/fingerprint; `NONE_APPROVED` sem PASS/FAIL de tempo. |
| Acessibilidade | S3 gestão, correções e estados de conflito | Testes de view/template e revisão de markup; baseline S8 inspecionou browser de superfícies V0.4. | Não há prova manual observada para as páginas V0.5 em 200% nativo/360 px. | Roteiro manual das páginas centrais, keyboard/focus e estados, aprovado somente com observação registrável; automatizado/estático rotulados separadamente. |
| Acessibilidade | Priority/Domain explicado | Mensagens em texto e teste de empty/insuficiência; política preserva missing ≠ 0. | Nova tela ainda sem evidência browser. | Inspecionar estado ranqueado e `Coletar mais evidências`, semântica, ordem, foco, zoom e viewport; conferir explicações sem depender de cor. |
| Acessibilidade | `/dados/` restore/export | Templates com labels, feedback textual, confirmação explícita e controles nativos; testes automatizados S7. | Evidência browser de seleção/preview/erro/recovery e zoom não localizada. | Observar o workflow em DB descartável, sem adoção no banco ativo; foco e recuperação compreensíveis em cada passo. |

Performance e acessibilidade são eixos distintos: uma medição rápida não aprova UX; inspeção estática não aprova renderização/responsividade.

## 10. Accessibility inventory

Classificações usadas: `AUTOMATED`, `STATIC_REVIEW`, `MANUAL_BROWSER_REQUIRED`. Teste de template/DOM é evidência automatizada; leitura de markup/CSS é estática; somente observação real em browser prova viewport, zoom nativo, foco visível e overflow.

| Grupo | Semântica/labels/feedback observáveis no código/testes | Evidência existente | Gap e prova S9 |
| --- | --- | --- | --- |
| Base + search/questions | `base.html` fornece `skip-link`, `main` único focável e nav nomeada; lista usa fieldset/legend, labels, erros em texto, botões para submit e links para navegação. | `AUTOMATED`: `test_question_search.py`/`test_question_interface.py` têm prova semântica/keyboard/responsive; `STATIC_REVIEW`: HTML/CSS consultados. | `MANUAL_BROWSER_REQUIRED` para filtro salvo, erros/empty, keyboard, 200% e 360 px. |
| Taxonomy + categories | Headings, links/botões, labels, help/errors e confirmação; operação sem dependência obrigatória de JavaScript. | `AUTOMATED`: testes de interface de taxonomy/S3 para empty, erros, cancel, stale, CSRF, escaping e markup; `STATIC_REVIEW` dos templates. | `MANUAL_BROWSER_REQUIRED` para ordem/foco, erro → correção → sucesso/cancel e reflow/zoom em páginas selecionadas. |
| Reviews + Attempt/question corrections | Forms nativos, texto explicativo, feedback de erro/conflito; confirmação por POST e cancel por link/botão conforme fluxo. | `AUTOMATED`: testes S3 UI cobrem conflitos, confirmação, CSRF e recovery; `STATIC_REVIEW` dos templates. | `MANUAL_BROWSER_REQUIRED` para estado de confirmação, retorno após erro, foco e ausência de ação destrutiva acidental. |
| Priority/Domain | Seções nomeadas por heading, listas e motivos textuais; estado empty/collect-more é texto explícito. | `AUTOMATED`: integração de ranking, insuficiência, vazio e ausência de mutação; `STATIC_REVIEW`: `accounts/priority.html`. | `MANUAL_BROWSER_REQUIRED` em estado com ranking e estado de evidência insuficiente. |
| Portability/restore | Labels de arquivo/frase/checkbox, headings por seção, status/alert textual, controles HTML nativos. | `AUTOMATED`: S7 UI/protocol tests; `STATIC_REVIEW`: template `data_management/portability.html`. | `MANUAL_BROWSER_REQUIRED` para upload, preview, invalidação, confirmação/cancelamento e 200%/360 px em cópia descartável. |

Revisar associações de erro/instrução (`aria-describedby`/`role=alert`), headings/landmarks, foco visível, botões vs links, disabled/readonly, confirmações destrutivas, status sem cor como única informação e recovery. Usar `aria-*` somente onde o HTML semântico não basta; não adicionar atributos por checklist sem finding.

## 11. Manual / browser evidence — 200% e 360 px

Estado atual: `MANUAL_BROWSER_EVIDENCE_REQUIRED`. Evidência S8 anterior observou somente telas V0.4 em Chromium/Brave; 360×800 CSS px foi testado e 768 px foi usado como reflow equivalente a 200%, mas o zoom nativo não foi acionado. Isso não comprova páginas V0.5 nem 200% nativo.

Roteiro reproduzível futuro:

| Página/estado | Viewport/zoom | Ação | Resultado esperado | Evidência necessária |
| --- | --- | --- | --- | --- |
| `/taxonomy/` e formulário com erro + vazio/cancel | 360 CSS px e 200% nativo, em sessões separadas | Tab/Shift+Tab por links, submit inválido, corrigir, cancelar e retornar | Sem overflow do documento/controles cortados; headings/labels/erros legíveis; foco visível e ordem coerente. | Browser/versão, tamanho CSS, zoom observado, percurso, achados; screenshot legível antes/depois se um defeito for encontrado. |
| `/categories/` lista/merge ou erro stale | 360 CSS px e 200% nativo | Percorrer ações; abrir form; validar/erro; cancelar; confirmação textual | Ações identificáveis por texto, erro associado, confirmação compreensível, retorno sem perder contexto. | Registro de estado/ação, foco e clipping; captura visual quando necessária para revisar finding. |
| `/questions/` filtro vazio e filtro salvo aplicado/incompatível | 360 CSS px e 200% nativo | Buscar termo sem resultado, salvar/aplicar filtro e navegar de volta | Formulário e estado vazio/incompatível utilizáveis sem scroll horizontal da página; conteúdo da tabela pode usar wrapper já previsto. | Valores de viewport/zoom, roteiro e resultado observado; não usar screenshot de CSS como prova de zoom. |
| `/prioridades/` ranking e coleta de evidência | 360 CSS px e 200% nativo | Navegar links de Subject/fila e ler score, fatores e motivos | Ordem de leitura clara, explicações completas e sem dependência de cor; links atingíveis e visíveis. | Browser/zoom/viewport, screenshot dos dois estados ou anotação equivalente verificável. |
| `/dados/` com preview válido/erro e cancelamento | 360 CSS px e 200% nativo, DB sintético descartável | Selecionar arquivos, ler preview, provocar erro de validação com fixture inválida, cancelar | Labels, confirmação, impacto, erro e recovery claros; nenhum arquivo/controle fica fora da tela; não aplicar ao banco ativo. | Identificação da fixture sintética, estado/ação, browser/zoom/viewport; captura sem path pessoal/dado real. |

Não marcar PASS antes da observação. Não executar leitor de tela como se uma árvore de acessibilidade fosse equivalente; se tecnologia assistiva for usada, relatar nome/versão e percurso efetivamente testado.

## 12. Keyboard / focus matrix

| Interação | Percurso S9 | Aprovação observável |
| --- | --- | --- |
| Navegação global e skip link | `Tab` desde carregamento; `Enter` no skip link; seguir `Tab` e `Shift+Tab` | Skip link aparece quando focado e move para `#conteudo-principal`; foco visível, ordem segue leitura, sem trap. |
| Forms de busca/gestão/Priority links | `Tab`/`Shift+Tab`, `Enter` em links, `Space` apenas em checkbox/botão conforme semântica | Cada ação é operável sem mouse; ordem lógica; seleção/checked é anunciada visualmente e por estado nativo. |
| Erro e retorno | Enviar form inválido; observar erro; corrigir e submeter | Erro é texto associado e localizável; foco não some nem fica em ação removida; submissão recuperável sem repetir campos sem necessidade. |
| Confirmação de categoria/Attempt/Question | Navegar preview, confirmação, cancelamento e retorno | Nenhuma ação destrutiva ocorre em GET; ação e alvo são lidos antes de confirmar; cancelamento é controlável e volta a estado seguro. |
| Restore | Navegar upload → preview → confirmar/cancelar/preparado | `Enter`/`Space` funcionam conforme controle nativo; checkbox e frase são identificáveis; cancelamento preserva banco; foco/feedback compreensíveis após cada POST. |
| Priority | Ler ranked e `Coletar mais evidências`; abrir Subject e fila | Score, fatores, motivos e escolha permanecem disponíveis sem atalho de teclado não documentado. |

Não inventar atalhos. Registrar o caminho real do foco em transições após submit/navegação e qualquer quebra como finding concreto.

## 13. Security / local threat matrix

O modelo avaliado é a aplicação local loopback com dados de estudo privados; não é SaaS, serviço público, cloud ou multi-tenant remoto além dos guardas Workspace internos.

| Fronteira | Proteção atual observada | Cobertura e prova S9 |
| --- | --- | --- |
| Input, IDs e Workspace | Views escopam por Workspace/owner; forms e SavedFilter aceitam payload fechado; IDs estrangeiros falham sem conteúdo; middleware recusa cliente non-loopback. | Reexecutar focused tests de payload/IDs, isolamento e HTTP; validar GET sem mutação e erro recuperável. Não relaxar guardas nem inferir permissão de UI. |
| ZIP/CEI | `portability.py` aceita nomes/conjuntos fechados, manifesto/versão/checksums/campos conhecidos; rejeita path/entry extra/relacionamentos incompatíveis antes da transação. Import só em DB SQLite compatível sem Workspace e preserva IDs. | `test_v05_s7_portability.py`; manter reject-before-mutation e round-trip sem alteração de CEI-EXPORT-1.0. |
| Backup/restore/staging | `ui_services.py` usa dirs temporários, root `cei-recovery` próximo do DB, modo restrito para root/ticket, UUID de ticket, fingerprints do active DB e SHA-256; preview/candidate/pre-backup são revalidados; adoção é offline; cleanup só remove artefatos do ticket próprio. | `test_v05_s7_ui.py`, `test_backup_restore.py`, `test_backup_recovery.py`; usar arquivos sintéticos, verificar before/after fingerprints e paths com espaços; nenhum restore sobre DB real. |
| Logs/secrets | `structured_logging.py` remove chaves sensíveis e padrões de credencial, valores da `SECRET_KEY`, corpo/payload/paths; formatter não serializa traceback; correlation ID técnico. | `tests/test_operations.py`; acrescentar somente caso se finding concreto surgir. Evidências/logs S9 não devem incluir segredo, path privado ou conteúdo de usuário. |
| Operações destrutivas | GET/preview não muda fatos; confirmação POST explícita, pre-backup e revalidação são existentes em S2D/S7. | Testes existentes preservam hash/fingerprint e backup; review manual só em banco descartável; não redesenhar fronteira de delete/restore. |

Não há finding de segurança confirmado no A4 que justifique correção imediata ou mudança de serviço/schema. Se a execução descobrir exposição, mistura de dados, traversal, path não confiável ou segredo em log, interromper o fluxo dependente, registrar before/after e classificar severity antes de editar.

## 14. Windows / local operation matrix

| Item | Estado atual | Prova S9 planejada |
| --- | --- | --- |
| Launcher PowerShell | Resolve raiz via `$PSScriptRoot`, exige `.venv`/Python 3.13.15, seleciona profiles, limita listener a loopback, falha orientando se porta ocupada, usa `--noreload`; não migra/bootstrap nem abre browser. | Executar `tests/test_windows_operation.py`; iniciar manualmente com DB development descartável, validar `GET /health/`, encerrar com `Ctrl+C` e provar liberação de porta. |
| Wrapper Explorer | `start-local.cmd` chama PowerShell com Bypass só para o processo e deriva diretório pelo script. | Prova estática existente; abrir pelo wrapper somente se o ambiente permitir sem janela/processo órfão, registrar processo/encerramento. |
| CWD/path com espaços | Script usa `Join-Path -LiteralPath` e paths entre aspas no wrapper; S7 reporta execução de diretório externo. | Rodar launcher de CWD externo; se validação de raiz com espaços for necessária, usar junction/cópia descartável de nome com espaço e DB sob temp; nunca escrever em `var` real. |
| Loopback/porta/shutdown | `127.0.0.1`; porta padrão 8000, override explícito; porta ocupada falha sem matar processo ou escolher porta aleatória. | Health 200 em loopback, cliente não-loopback 403 via teste, porta ocupada com processo de teste próprio e liberação após stop. |
| Backup/export/restore | Coberto pelo guia S7 e operações em `/dados/`; adoção offline separada. | Validar download/preview/cancelamento em DB temporário, erros recuperáveis, instruções e cleanup; nenhum restore no banco ativo. |

Reutilizar `docs/V0.4_S7_Operacao_Windows.md`, `docs/V0.5_S7_Portabilidade_e_Restore.md`, `scripts/start-local.ps1` e `.cmd`. Não criar serviço, instalador, segundo launcher ou mecanismo de restore.

## 15. S7 portability contract

S9 preserva `CEI-EXPORT-1.0` (ZIP/JSON UTF-8, manifest, SHA-256, schema migrations estritas, sem merge/remapeamento) e o contrato separado `CEI-SQLITE-BACKUP`/restore. Importação funcional só ocorre em DB SQLite compatível e vazio. Restore da UI valida e reconcilia em cópia isolada, cria ticket/pre-backup e requer adoção offline com app parada. GET, preview, cancelamento e entradas inválidas não alteram DB ativo.

Revalidar testes S7 existentes se alterações tocarem UI, validação, paths, staging, cleanup ou documentação. Hardening S9 não altera formato, checksums, versionamento, política de incompatibilidade, pré-backup, reject-before-mutation nem adoção offline sem finding concreto e revisão humana se ampliar contrato.

## 16. S8 integrity baseline

S8 está fechado e confirmado no commit baseline. S9 **não precisa** adicionar invariantes, criar repair, alterar checker/catálogo, mudar `OperationReceipt`, repetir a matriz PostgreSQL, reabrir upgrade/recovery ou criar migration. Pode caracterizar somente duração/fingerprint do checker em SQLite descartável como operação de desempenho sem threshold. Qualquer finding que exija schema, nova regra de integridade, mutação ou nova evidência de backend é stop condition, não implementação autorizada por este plano.

## 17. Documentation matrix

| Documento | Estado observado | Gap e ação futura possível |
| --- | --- | --- |
| `README.md` | Guia de instalação/execução aponta a documentação V0.4 e declara V0.5 não autorizada. | Atualizar sumário/estado beta e apontar a operação/portabilidade V0.5 correta após evidência S9; deixar claro que hardening não equivale a promoção/release. |
| `docs/V0.4_S7_Operacao_Windows.md` | Documenta launcher, perfis, loopback, backup CLI, troubleshooting e limites locais. | Conferir fluxo de `/dados/`, paths com espaços e links. Acrescentar apenas passo/limitação que esteja realmente ausente; não duplicar procedimentos S7. |
| `docs/V0.5_S7_Portabilidade_e_Restore.md` | Documenta export, backup UI, restore staging/pre-backup/adoção offline e import CEI em DB vazio. | Baseline normativa/operacional já correta; alterar somente se execução encontrar discrepância observável. |
| `docs/CEI_EXPORT_1_0.md` | Contrato canônico do formato e validação. | Protegido; não atualizar para resolver simples gap de manual. |
| `docs/README.md` | Índice existente de fontes e documentos V0.5. | Atualizar índice apenas se S9 adicionar/alterar documento vivo. Não criar guia beta separado sem necessidade provada. |
| `PROJECT_STATE.md` | Histórico ainda diz S9+ não autorizadas. | Não editar no A4. Na conclusão futura da S9, atualizar o estado real conforme contrato, sem declarar promoção ou iniciar S10. |
| `quality/v05-s9-beta-hardening-result.md` | Ainda não existe. | Criar na futura execução/encerramento S9 com evidência efetivamente observada; não é evidência a produzir nesta sessão A4. |

Não reescrever Roadmap, contratos S1–S8 ou documentação correta apenas para uniformizar estilo.

## 18. Migration decision

**Migration: NO.** O escopo comprovado é medição com fixture descartável, revisão de templates/CSS/views/forms somente se defeito concreto, testes/harness e documentação. Nada exige novo campo, constraint, entidade, backfill ou alteração de formato. `SavedFilter` já tem a migration S3; isso não é motivo para migration S9. Se um finding futuro parecer exigir schema, parar e obter decisão humana; não criar migration por antecipação.

## 19. Expected implementation changes (future S9 only)

| Classe | Arquivos/condição |
| --- | --- |
| Prováveis | `README.md` para remover estado documental V0.5 obsoleto e indicar documentação beta; `quality/v05-s9-beta-hardening-result.md` para evidência final. Atualização da seção real de operação em `docs/V0.4_S7_Operacao_Windows.md` somente se a auditoria final confirmar lacuna concreta. |
| Condicionais | `src/shared/application/bcr1_reads.py`/`scripts/run_bcr1.py` e `tests/test_bcr1.py` caso seja preciso adicionar ao harness existente medições determinísticas de Domain/Priority/export/backup/restore/checker; novos raw outputs em `quality/` somente se necessários e sem sobrescrever evidência anterior. Templates específicos e `src/static/css/app.css` com seus testes somente para findings concretos de acessibilidade/segurança/UX. Views/forms/services apenas se finding reproduzível não puder ser corrigido no template/documentação. |
| Protegidos | Migrations/schema sem decisão nova; `src/modules/domain/policy.py`, `src/modules/priority/policy.py`, contracts `DOM-HEUR-1.0`, `PRI-HEUR-1.0`, `CEI-EXPORT-1.0`; semânticas S2/S3/S5/S6/S7; checker S8, `OperationReceipt`, logs/auditoria histórica; dependências e lock; `PROJECT_STATE.md` durante A4. |

Nenhuma lista acima autoriza trabalho nesta sessão além de `tasks/current.md` e deste plano. Nenhum finding deve ser corrigido durante o A4.

## 20. Test plan for future S9

| Dimensão | Provas focadas planejadas |
| --- | --- |
| BCR | Executar `scripts/run_bcr1.py` com saída nova e fixture isolada; conferir fingerprint/reconciliação, writes, telas, busca/filtros e paginação. Adições de medição devem testar clock, seed, operação, serializer e query count sem tocar DB real. |
| UI/forms/HTML | `tests/test_v05_s3_ui.py`, `test_taxonomy_interface.py`, `test_question_search.py`, `test_question_interface.py`, `test_priority_integration.py`, `test_v05_s7_ui.py`; cobrir labels/erro/estado vazio/disabled/read-only/feedback/conflito e rendered HTML nas rotas tocadas. |
| Segurança | `test_v05_s3_ui.py`, `test_v05_s7_portability.py`, `test_v05_s7_ui.py`, `test_backup_restore.py`, `test_backup_recovery.py`, `test_operations.py`; inputs, Workspace, ZIP/extra/path, uploads, staging, checksum, logs/secrets, no side effect/fingerprint antes-depois. |
| Windows | `test_windows_operation.py`; ensaio manual autorizado futuro do launcher, loopback, CWD/path com espaços, start/stop, porta, health e DB temporário. |
| Navegador | Manual/browser: teclado e foco, 200% zoom nativo, 360px, empty/error/recovery, Priority explanatory states, restore preview/cancel. Evidência deve identificar browser/version, viewport, zoom, estado e resultado. |
| Testes finais | Regressões relacionadas, A8 deep, gate completo. Não reduzir cobertura nem alterar expectativa para ocultar defeito. |

Não executar esses testes funcionais/gate no A4. Nesta sessão só houve a tentativa documentada do benchmark existente, interrompida sem amostra.

## 21. Regression plan

- S3: SavedFilter CRUD/compatibility/query count, categorias, reviews, Attempt correction, answer-key correction, permanent delete, Workspace, stale/conflito e serviços oficiais.
- S5/S6: Domain read-only, relógio/fuso, confidence/missing evidence, Priority ranking/explanations/empty, sem mutação de queue/mastery.
- S7: CEI round-trip/rejections, backup validation, preview, pre-backup, cancel/cleanup, adoption offline, sem mudança no DB ativo em preview/erro.
- S8: checker read-only/fingerprint somente se arquivo/serviço correspondente for afetado; sem repetir PostgreSQL.
- Busca, question list/detail, dashboard/fila/timeline somente conforme rota/selector tocado. Não executar suíte irrelevante por padrão antes do gate exigido.
- Tratar qualquer falha em história imutável, cross-Workspace, compatibility ou dados como bloqueadora, não como regressão aceitável de UX.

## 22. A8 deep

A8 futuro deve revisar diff real, contrato e este A4; decisão FTS; V05-R08; budgets/medições; cada superfície/estado; prova automated/static/manual separada; keyboard/focus/200%/360px; security inputs/Workspace/ZIP/paths/staging/logs/secrets; Windows; contratos S3/S6/S7/S8; migration; documentação; testes/regressões; cleanup/rollback; gate attempts e evidência; e ausência de leakage S10/V1.

Critério: **APPROVED**, Blocker 0 e Major 0. Qualquer discrepância entre o plano e os findings exige atualizar o plano/evidência antes da aprovação; o A8 não pode converter limitação/manual evidence faltante em PASS.

## 23. Quality gate

Após mudanças futuras e todas as correções/A8 aplicáveis, executar exatamente:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Registrar cada tentativa RED/GREEN, exit code, etapa/motivo, correção, quantidade de testes, coverage e duração observada. `gate_first_pass` reflete a primeira tentativa verdadeira; não reclassificar falha intermitente como inexistente. A4 não executou o gate, não executou suíte de testes e não declara S9 GREEN.

## 24. Rollback / recovery

Sem migration prevista e sem alteração de dado persistente. Correções futuras restritas a template/CSS/docs/harness são reversíveis por patch e teste. Qualquer ensaio usa DB/arquivos sintéticos próprios em pasta temporária, registra fingerprints e limpa apenas seus próprios artefatos após comprovar o alvo. Não inventar fluxo de recuperação complexo. Para operações existentes, preservar o contrato S7; não restaurar sobre banco aberto/real nem alterar pré-backup.

## 25. Stop conditions

Parar a ação dependente e classificar corretamente se houver:

- baseline/dependência S3/S6/S7/S8 diferente do checkpoint;
- decisão normativa necessária ou threshold inexistente que seria preciso inventar (`BLOCKED_HUMAN_DECISION`);
- falha medida de busca não reproduzida contra budget existente, ou desejo de FTS sem falha (`FTS_NOT_JUSTIFIED`; não implementar);
- finding que exige migration, mudança de policy Domain/Priority, CEI, checker mutável, semântica histórica ou redesign (`BLOCKED_HUMAN_DECISION`);
- impossibilidade de browser/Windows suportado para obter evidência obrigatória (`BLOCKED_ENVIRONMENT` ou `BLOCKED_EVIDENCE`), sem alegar PASS;
- risco de dado privado/segredo, path traversal, arquivo fora do staging esperado, mistura parcial ou necessidade de restore destrutivo;
- necessidade de PostgreSQL de produção, deploy, promoção, piloto, tag/release, V1 ou S10;
- benchmark amplo desproporcional/inconclusivo: preservar a medição limitada, não a converter em FAIL nem inventar equivalência.

## 26. Execution order for a newly authorized S9 implementation

1. Obter instrução humana explícita para sair da fase A4; confirmar `tasks/current.md`, baseline e status limpo conforme novo contrato.
2. Executar testes focados atuais e BCR; registrar orçamento aplicável e condições de ambiente antes de interpretar.
3. Medir operações selecionadas da matriz, construir inventário de findings com evidência/classificação, reproduzir o defeito e priorizar query/ORM/N+1/paginação antes de solução arquitetural.
4. Corrigir somente findings S9 reproduzíveis com menor mudança compatível; nenhum FTS sem todas as condições do gate.
5. Verificar acessibilidade estática/automatizada e obter evidência browser manual nas telas/estados/zoom/viewports definidos.
6. Revalidar segurança local/arquivos/logs e executar ensaio Windows em DB descartável; preservar integralmente S7/S8.
7. Atualizar apenas documentação que tenha gap provado; preparar evidence S9.
8. Executar testes focados e regressões S3/S5/S6/S7/S8 aplicáveis; corrigir e repetir provas afetadas.
9. Executar A8 deep; resolver Blocker/Major e atualizar evidência antes de gate final.
10. Rodar gate completo; registrar todas as tentativas e resultado final GREEN. Só então atualizar estado/evidence e arquivar conforme contrato humano de encerramento. Parar antes de S10.

## 27. Done When mapping

| Done When S9 | Condição para execução posterior | Estado ao fechar este A4 |
| --- | --- | --- |
| Evidência BCR medida | BCR atualizado e operações selecionadas registradas sem inventar threshold; tentativa interrompida atual é explicitamente inconclusiva. | Parcial; S8 histórica disponível; nova evidência necessária. |
| FTS sob gate | Busca S8 abaixo de 2 s e decisão A4 `FTS_NOT_JUSTIFIED`; reexecutar BCR S9. | Decisão atual sustentada; FTS não autorizada. |
| UX/acessibilidade central | Automated/static/manual classificados e browser observado para telas novas, foco, 200% nativo, 360 px e estados. | Inventário e procedimento definidos; evidência manual V0.5 ainda pendente. |
| Segurança local e operação Windows | Inputs/arquivos/logs verificados e start/health/shutdown/paths comprovados em ambiente descartável. | Contratos/provas existentes auditados; repetição S9 futura pendente. |
| Documentação beta completa | Resolver gaps README/Windows observados e manter CEI/S7 correto; evidence final persistida. | Gaps documentados; nenhum guia/evidence S9 criado durante A4. |
| Migration decidida | Decisão fundamentada após inventário. | `Migration: NO`. |
| A8 deep e gate final GREEN | A8 APPROVED com Blocker 0/Major 0; gate observável exit 0 e evidence. | Não executados/não declarados em A4. |
| Limite de etapa | Atualizar estado/arquivar somente após encerramento comprovado. | S9 permanece `AUTHORIZED`; S10 e posteriores `NOT AUTHORIZED`; implementação requer nova instrução humana explícita. |
