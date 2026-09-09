# V0.3 — Etapa 4 — Fila Derivada, Linha do Tempo, Diagnóstico Auditável e Suspensão por Arquivamento

## Autorização e objetivo

Esta é a tarefa formal de **IMPLEMENTAÇÃO** da E4. Ela autoriza exclusivamente a implementação funcional da E4, formalmente liberada depois da E3 GREEN e ainda não iniciada. O nome confirma o recorte de ADR-011 §9: fila/timeline, diagnóstico e arquivamento com suspensão; não inclui dashboard, métricas, analytics, domínio ou prioridade. E5 continua não autorizada.

O objetivo é consolidar a leitura e manutenção operacional dos fatos existentes: fila derivada, timeline histórica, correção auditável de diagnóstico e arquivamento que suspende o ciclo ativo atomicamente.

## Fontes e limites obrigatórios

- Consultar `AGENTS.md`, `PROJECT_STATE.md`, ADR-011 §§2–4 e 8–9, e somente os recortes E4 de requisitos, regras, fluxos, SDD, modelo, roadmap e Plano de Testes.
- Código, migrations e testes E1–E3 prevalecem: `AttemptService`, `CompleteReviewService`, `ReviewSchedulePolicy`, `ReviewStatusPolicy`, `Clock`, `Calendar`, `OperationReceipt` e `QuestionCommandService.archive`.
- Preservar Workspace, Attempt imutável, diagnóstico append-only, `REV-FIXA-1.0`, transações curtas, lock/version e SQLite de ADR-011.

## Fila derivada e status temporal

Implementar leitura derivada de `Review`, `ReviewCycle` e `Question`, sem persistir fila, contadores ou `SavedFilter`.

- Elegível: `Review.state=PENDING`, `ReviewCycle.state=ACTIVE` e `Question.status=ACTIVE`, todos do Workspace atual. `COMPLETED`, `SUSPENDED`, `CANCELLED`, ciclos concluídos/suspensos e arquivadas não são pendências executáveis.
- `ReviewStatusPolicy` é a única dona da classificação. Para `PENDING`, compara `current_due_date` com `Calendar.today` no fuso IANA do Workspace: menor é `OVERDUE`/atrasada; igual é `DUE`/hoje; maior é `FUTURE`/futura. Estado estrutural não pendente prevalece e retorna `COMPLETED`, `SUSPENDED` ou `CANCELLED`; suspensa pode ser exibida como indisponível, nunca na fila.
- `Clock` dá o instante; `Calendar` a data civil no fuso explícito. Status temporal e data de consulta são derivados, não gravados por job e não substituem estado persistido.
- Expor seções atrasadas, hoje e futuras. Ordenar cada uma por `current_due_date`, `created_at`, `id`, crescentes. O `id` é desempate obrigatório. Paginar separadamente por cursor ou página numerada com esta mesma ordem estável; documentar e testar a opção escolhida.

## Selectors e timeline

Criar somente `list_review_queue(...)`, `get_review_pending_detail(...)` e `get_learning_timeline(...)`, sempre Workspace-scoped. Selectors consultam e combinam; policies decidem temporalidade; nenhum selector grava ou replica a comparação temporal.

A timeline usa fatos existentes em ordem determinística por instante, precedência de tipo documentada em empate e `id` como desempate: Attempts `INITIAL`/`REVIEW`, classificações/revisões, Reviews concluídas/suspensas, criação/progressões D1/D7/D14/D30, erros/reinícios, timestamps, timezone/data civil e `QuestionRevision` apresentada. Ela permanece consultável após arquivamento ou ciclo concluído/suspenso. Não calcular percentuais, score, domínio, confiança, prioridade, recomendação, gráficos ou analytics.

## Correção auditável de diagnóstico

Criar comando/service exclusivo para corrigir `ErrorClassification` de Attempt incorreta válida do Workspace do usuário autenticado (proprietário no modelo atual; sem RBAC novo). Aceitar categoria canônica do Workspace, descrição normalizada e obrigatória para `OTHER`, razão opcional normalizada, `lock_version` e chave idempotente quando aplicável.

Na mesma transação: bloquear/validar classificação, Workspace, Attempt, categoria e versão; preservar valor anterior em `ErrorClassificationRevision`; gravar nova revisão sequencial; atualizar somente a projeção corrente e incrementar o lock. Revisões guardam número, categoria, `OTHER`, razão e instante e são append-only. A projeção `ErrorClassification` é a corrente, consistente com a maior revisão após commit. Definir/testar semeadura da revisão 1 para classificações E2 sem histórico, sem lacuna ou duplicação concorrente.

Não alterar alternativa/resposta, resultado, Attempt, QuestionRevision apresentada, `occurred_at`, `local_date`, calendário, Review ou ciclo; não há correção estrutural/anulação de Attempt.

## Arquivamento e suspensão

Estender minimamente `QuestionCommandService.archive`/`archive_question`, sem reescrever o agregado. Na mesma transação, após Workspace e `lock_version`, bloquear Question ativa e eventual `ReviewCycle.ACTIVE`. Se existir, marcar ciclo `SUSPENDED` com instante/motivo canônico de arquivamento e sua única `Review.PENDING` como `SUSPENDED`, preservando sequência, datas e fatos.

Sem ciclo ativo, arquivamento continua válido e não cria fatos. Replay não pode duplicar suspensão; reenvio pós-arquivamento retorna conflito/estado atualizado coerente. Falha antes de commit reverte Question, ciclo e Review. Não deletar Question/ciclo/Review/Attempt, nem reativar nesta etapa.

A pendência sai da fila, a timeline segue legível e `CompleteReviewService.complete_review(...)` deve rejeitar Review suspensa, ciclo inativo ou questão arquivada antes de criar Attempt/recibo/contexto.

## Entrega autorizada, interface, transações e migrações

Interface mínima: três seções da fila, abertura de Review elegível, timeline, correção de diagnóstico e indicação histórica de arquivamento/suspensão. Usar views finas, services/selectors, autorização Workspace, POST+CSRF, escaping, PRG e padrões acessíveis (semântica, teclado, foco, labels, erros e vazio). Sem dashboard, gráficos ou métricas.

Esta implementação autoriza criar e alterar exclusivamente o código funcional E4 necessário: selectors, services, views, forms, templates mínimos, extensão mínima do arquivamento e testes E4. Não autoriza antecipar nenhuma capacidade fora deste recorte.

Fila/detalhe/timeline são leitura e não escrevem cache/status/recibo. Correção de diagnóstico é uma transação de lock, snapshots, projeção e recibo quando aplicável; mesma chave/hash reproduz resultado, payload divergente conflita e falha reverte tudo. Arquivamento+suspensão é uma transação Question/ciclo/Review, mantendo constraints, locks, `busy_timeout` e a única retentativa SQLite de ADR-011. `AttemptService` continua exclusivo para inicial e `CompleteReviewService` para conclusão.

Expectativa: **nenhuma migration**. O schema já tem `ErrorClassificationRevision` (Workspace, número, categoria, `OTHER`, razão e instante) e estados/timestamps/constraints/índices de suspensão. Confirmar com `makemigrations --check --dry-run`. Se regra aprovada não couber corretamente, registrar lacuna/necessidade como bloqueador de revisão antes de criar migration.

## Rastreabilidade, CTs e aceite

Mapear apenas `RF-019` (arquivamento), `RF-031`, `RF-036`–`RF-040`; `RN-032`, `RN-040`–`RN-044`, `RN-048`, `RN-049`, `RN-055`, `RN-087`; RNFs de acessibilidade, CSRF/escaping, Workspace, integridade, imutabilidade, tempo, idempotência, rollback e SQLite; `FL-006`, `FL-008`, `FL-009`, `FL-013`. ADR-011 §8 prevalece: `CT-019` e `CT-041` são E4.

Cobrir no mínimo `CT-019`, `CT-030`–`CT-036`, `CT-041`, `CT-125` e regressões de Workspace, CSRF/escaping, idempotência e rollback: filas/status/ordem/fuso, concluída/suspensa fora, timeline/versões/D1-D30/reinício, `OTHER`/razão/append-only/concorrência, preservação de Attempt, arquivamento com/sem ciclo e bloqueio pós-arquivamento.

Aceite: filas derivadas corretas; timezone/data civil corretos; concluídas e suspensas fora da fila; timeline preserva fatos; correção cria história imutável; arquivamento suspende atomicamente e preserva histórico; Workspace isolado; mutações atômicas/idempotentes quando aplicável; sem E5+; gate GREEN e nenhum P0/P1 aplicável.

## Riscos e contenções

- Concorrência, replay e falha parcial podem duplicar ou divergir fatos: preservar locks, constraints, transações curtas, `busy_timeout`, a única retentativa SQLite e idempotência aplicável de ADR-011.
- Correção de diagnóstico pode violar a auditoria: manter `Attempt` imutável, revisões append-only, semeadura determinística da revisão 1 e projeção corrente consistente após commit.
- Arquivamento pode deixar pendência executável: suspender atomicamente ciclo ativo e sua única Review pendente, sem apagar histórico e sem reativação.
- O schema pode não comportar uma regra aprovada: tratar como bloqueador e reportar antes de criar migration.
- O gate pode perder rastreabilidade histórica: criar somente o manifesto E4 e preservar imutáveis os manifestos E1–E3.

## Manifesto, gate e encerramento da implementação

Criar `quality/v03-stage4-gate.json`, exclusivo E4, com CTs/evidências, cobertura E4 e hashes de migrations históricas. Testar proteção contra alteração/reuso de `v03-stage1-gate.json`, `v03-stage2-gate.json` e `v03-stage3-gate.json`: são históricos e imutáveis. Na E4, apontar `scripts/quality.ps1` exclusivamente ao manifesto E4; jamais sobrescrever/reaproveitar os anteriores. Executar testes específicos, `git diff --check` e o gate autoritativo.

Quando todos os critérios estiverem GREEN, registrar a evidência final, atualizar `PROJECT_STATE.md` e arquivar esta tarefa conforme o padrão do repositório. Commit, push, tag e release continuam fora desta tarefa.

## Fora de escopo e limites permanentes

Fora: dashboard, métricas, analytics, domínio, confiança, prioridade, recomendações, revisão adaptativa, reagendamento, reativação, `SavedFilter`, exportação, correção/anulação estrutural de Attempt, E5 e V0.4+.

Não alterar migrations históricas, nem criar migration nova. Se a implementação demonstrar bloqueador real de schema, parar e reportar a lacuna antes de criar qualquer migration. Não iniciar E5, nem fazer commit, push, tag ou release.
