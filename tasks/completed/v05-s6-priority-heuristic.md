# Task Contract

Status: COMPLETED

## Identification

- Task ID: `V0.5-S6`
- Product version: `V0.5`
- Stage: `S6`
- Name: `PRI-HEUR-1.0 e recomendação explicável`
- Task type: implementação funcional
- Size: `M`
- Risk: `high`
- Migration: `UNLIKELY`; A4 deve registrar `NO` se o desenho puder permanecer derivado/read-only. Se surgir necessidade comprovada de schema, parar para decisão humana antes de criar migration.
- Modelo/reasoning recomendados: GPT-6 Sol / `Medium`

## Goal

Entregar a recomendação explicável, opcional e determinística `PRI-HEUR-1.0`, priorizando Assuntos elegíveis a partir do Domain/confidence corrente da S5 e dos fatores normativos W/O/R/D. A recomendação é read-only, separada da fila operacional de Reviews e não altera agenda, domínio, mastery ou plano de estudos.

## Context

- Baseline protegido: V0.4.4, V0.5-P0, S1, S2A–S2D, S3, S4 e S5 concluídas. A execução deve confirmar novamente branch, `HEAD`, `origin/main` e `git status`; S5 precisa estar commitada em baseline limpa. Baseline observada no bootstrap: `main`, `HEAD = origin/main = 43f7a38c2e78d31ef10226beb8d99af63271a2d0`, working tree limpa.
- S5 é protected input: reutilizar avaliação/agregação em lote, `M_h`, `C_h`, suficiência/elegibilidade, isolamento por Workspace e data de avaliação. Não duplicar matemática, confidence ou mastery de S4/S5.
- A unidade normativa é Assunto. A4 deve confirmar a granularidade autorizada nos seletores/fontes; não ampliar para Discipline, Subsubject ou Question sem fonte explícita.
- V05-OD03 segue aberto nas fontes consultadas: janela de R, janela/definição de D e desempate não estão definidos. Auditar as fontes canônicas antes de testes normativos ou implementação desses comportamentos. Se continuarem abertas, parar com `BLOCKED_HUMAN_DECISION` e apresentar as opções/impactos separadamente; não escolher defaults.

## Acceptance Criteria

- Implementar somente após A4/checklist completo e resolução humana de V05-OD03 quando as fontes não fecharem as lacunas.
- Preservar exatamente `Prioridade_h = 0.40 × W + 0.30 × O + 0.20 × R + 0.10 × D`, versão `PRI-HEUR-1.0`, usando precisão integral para elegibilidade, empate e ranking; arredondamento é apenas de apresentação.
- `W = 100 - M_h`; `O` é a proporção de Questions ativas atrasadas via `ReviewStatusPolicy` e timezone do Workspace; `R` conta Questions distintas com erro REVIEW recorrente na janela aprovada; `D` mede queda positiva entre desempenhos comparáveis nas janelas/definições aprovadas. Todos limitados ao intervalo 0–100.
- `C_h < 40` resulta em estado explícito equivalente a `COLLECT_MORE_EVIDENCE`, fora do ranking normal; `C_h = 40` tem boundary coberto. Evidência ausente não vira zero silenciosamente.
- Recomendações elegíveis expõem fatores contributivos, explicação e versão. A recomendação pode ser ignorada e não persiste estado nem altera Reviews, queue, Domain, mastery, agenda ou plano.
- Priority não oculta nem modifica Reviews atrasadas na fila operacional, inclusive para confiança insuficiente.
- Todos os fatos pertencem ao mesmo Workspace e usam Questions ativas; archived/deleted, Attempts VOIDED/predecessors substituídos e auditoria sanitizada de exclusão não contribuem. Correções de gabarito são prospectivas.
- Sem snapshot, cache persistente, campo manual, filtro persistente novo ou migration sem necessidade comprovada e autorização; sem N+1 evitável, com batching S5 e medição proporcional.
- UI mínima acessível quando aplicável: recomendação, fatores/score, confiança/evidência, explicação, estados vazio/insuficiente e possibilidade clara de ignorar.
- A8 `deep` aprovado, Blocker 0/Major 0; focused tests, regressões e gate autoritativo GREEN; evidence persistida.

## Expected Scope

- Fechar checklist A4 em `tasks/plans/` antes da primeira edição funcional, incluindo mapa de facts/código/testes, granularidade, ausência de dados (RN-097–100), migration, OD03, arquitetura, fronteiras e matriz de testes.
- Mudanças mínimas nos módulos de domínio/prioridade, selectors/services, rotas/views/templates e testes diretamente necessários, conforme auditoria A4.
- Evidência final em `quality/v05-s6-priority-heuristic-result.md` (ou nome equivalente consistente com o repositório).
- Atualizar `PROJECT_STATE.md` e arquivar esta tarefa somente depois de todos os critérios Done When comprovados.

## Protected Scope

- Não alterar fórmulas, fatos ou serviços protegidos S4/S5; não recalcular Domain em algoritmo paralelo.
- Não alterar semântica de Review Queue/`ReviewStatusPolicy` ou `REV-FIXA-1.0`.
- Não reinterpretar histórico S2B/S2C/S2D nem alterar fatos imutáveis; não modificar `MasteryStateEvent`/estados de mastery.
- Não antecipar S7 ou etapas posteriores; não criar exportação, backup/restore UI, hardening S8/S9 ou piloto S10.

## Constraints

- A4/checklist obrigatório; A8 `deep` obrigatório. Migration inicial `UNLIKELY`.
- Não inventar janelas, limiar/quantidade mínima, método estatístico, comparação de desempenho ou desempate para R/D. Antes de implementação/testes normativos, auditar RN-ABR-003, V05-OD03, PT-ABR-008, RN-081–084, RN-097–100 e fontes canônicas relacionadas. Se insuficientes, acionar Human Decision Gate e parar a parte bloqueada.
- Auditar significado de erro REVIEW recorrente; contar Questions distintas e Attempts efetivas, nunca INITIAL, quantidade de tentativas da mesma Question, categoria como peso ou Reviews planejadas.
- Error category pode apoiar explicação somente com fonte/fato sustentado; PRI tem apenas W/O/R/D.
- Revalidar baseline Git limpa e dependência S5 antes da execução funcional.
- Durante S6: não fazer commit, push, tag ou release. Não autorizar/iniciar S7+.

## Verification

- Antes de implementar: completar A4 e resolver OD03 ou registrar Human Decision Gate bloqueante.
- Executar matriz focada de W/O/R/D após definições aprovadas, precisão/fórmula independente, RN-081 boundary, explicabilidade, não mutação, Workspace, S2B/S2C/S2D, fila separada, UI/acessibilidade e performance/query count quando aplicável.
- Executar regressões aplicáveis e `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`; registrar cada tentativa, exit code, retries e `gate_first_pass` na evidence. Se A8 alterar código após GREEN, repetir gate.
- Executar A8 deep e registrar decisão, findings e status.

## Documentation Impact

Criar plano A4 e evidence de S6; atualizar `PROJECT_STATE.md` e mover o contrato para `tasks/completed/` somente no encerramento comprovado. Não alterar regras normativas; decisões humanas necessárias devem ser registradas nas fontes/evidence apropriadas antes dos testes correspondentes.

## Done When

- A4 completo; V05-OD03 fechado por fontes aprovadas ou decisões humanas documentadas; migration decision comprovada.
- PRI-HEUR-1.0 implementada com fórmula/pesos/precisão aprovados, W/O/R/D corretos, elegibilidade/ausência de dados explícitas, explicações, determinismo aprovado e isolamento Workspace.
- S5 reutilizada; Review Queue preservada; não mutação e compatibilidade S2B/S2C/S2D demonstradas; UI acessível quando aplicável; performance/query count medida; sem snapshot/migration indevidos.
- Focused tests e regressões GREEN; A8 deep `APPROVED`, Blocker 0/Major 0; gate final GREEN; evidence concluída.
- Atualizar estado e arquivar S6, retornando `tasks/current.md` a `NO_TASK_AUTHORIZED`; S7+ permanecem não autorizadas.
