# Task Contract

Status: COMPLETED

## Identification

- Task ID: `V0.5-S8`
- Product version: `V0.5`
- Stage: `S8`
- Name: `Integridade, compatibilidade, upgrade V0.4.4 e PostgreSQL crítico`
- Task type: integridade read-only, compatibilidade, upgrade/recovery e validação crítica de banco
- Size: `L`
- Risk: `high`
- Migration: `NO` — decisão final do A4; classificação inicial: `UNLIKELY`.
- A4: plano completo obrigatório antes da primeira edição funcional
- A8: `deep`, aprovação com Blocker 0 e Major 0
- A7 recomendado para a execução: GPT-6 Sol / `High`; não estimar consumo

## Goal

Validar e, quando necessário e fundamentado, evoluir a integridade read-only e a compatibilidade da V0.5, provando upgrade de uma base realmente equivalente à V0.4.4 por migrations reais, integridade/reconciliação, restore isolado e constraints/semânticas críticas em PostgreSQL, sem reescrever fatos históricos nem ampliar o escopo para operação PostgreSQL completa.

## Context

- Baseline do bootstrap: branch `main`; `HEAD = origin/main = a1e0d5a0b971de35d0b4f54514eff66feeb6fef2`; working tree limpa; `git diff --check` inicial sem saída e exit 0.
- V0.5-S2A, S2B, S2C, S2D, S5, S6 e S7 estão concluídas. S7 foi checkpointada no baseline. Evidências principais: `quality/v05-s2d-permanent-deletion-result.md`, `quality/v05-s5-domain-application-result.md`, `quality/v05-s6-priority-heuristic-result.md` e `quality/v05-s7-portability-result.md`, além dos contratos em `tasks/completed/`.
- Dependências oficiais obrigatórias de S8 conforme `tasks/plans/v05-release-execution-plan.md`: S2A–S2D, S5 e S7. S6 está concluída e deve ter compatibilidade auditada; não alterar a matriz oficial de dependências. Considerar S3 onde houver interface ou schema compartilhado relevante.
- Fontes normativas incluem `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md`, plano V0.5, código, migrations, testes e evidências fechadas. Não resolver divergência normativa por suposição.
- S8 é a única tarefa autorizada. S9, S10, V1 e posteriores permanecem não autorizadas.

## Acceptance Criteria

- Antes de qualquer alteração funcional, criar e fechar `tasks/plans/v05-s8-integrity-compatibility-plan.md` (A4), com auditoria de invariantes S1 `V05-INV-001` em diante, checker/catálogo atual, S2A–S2D, S3 quando aplicável, S5/S6/S7, todas as migrations V0.5 relevantes, fixture V0.4.4, backup/restore, `OperationReceipt`/`FL-ABR-009`, SQLite, PostgreSQL crítico, gate/ambiente de execução e documentação.
- O A4 mapeará cada invariante a regra, fato/modelo, cobertura existente, dependências de etapa e mecanismo apropriado (checker, guard/service ou constraint). Ampliar o checker somente para fatos/modelos V0.5 aprovados; não duplicar regra sem justificativa nem renumerar/redefinir checks existentes silenciosamente.
- O checker permanece estritamente read-only: diagnostica e reporta; não repara, limpa, expurga, corrige dados, reescreve histórico ou reconstrói fatos. Testar ausência de side effects em linhas, timestamps, estados, contagens, arquivos, scheduling, Domain, Priority, `AuditEvent` e `OperationReceipt`.
- Provar upgrade de uma fixture/cópia realmente equivalente ao schema e estado V0.4.4 através das migrations reais até o V0.5 candidato. Não substituir por banco criado diretamente no schema atual nem adicionar fatos fictícios para satisfazer funcionalidades posteriores. Começar por cópia protegida com backup anterior validado; preservar o backup e demonstrar restore isolado.
- No upgrade, verificar checks físicos/FKs, invariantes, reconciliação de fatos/projeções e checker; fixar `evaluation_date` onde derivados dependerem da data. Cobrir export S7 após upgrade quando proporcional e compatibilidade documentada de `CEI-EXPORT-1.0`, backup, restore/import, manifest, migrations e schema version.
- Preservar contratos V0.4.4 de Workspace/timezone, Questions/QuestionRevision/Alternatives, Attempts, ReviewCycles/Reviews, classificações, analytics, dashboard, queue e histórico. Attempts legados permanecem válidos segundo o contrato de migration, sem inventar void/replacement ou alterar resultados históricos. Não alterar agenda histórica de Reviews/Cycles nem inventar classificações pessoais. Exclusões permanentes S2D não podem voltar após upgrade/restore; checker somente as detecta.
- Validar S2B (VALID/VOIDED, replacement, efetividade, cadeia acíclica, Workspace e reconstrução) e S2C (revisão usada, correção prospectiva, preservação de Attempts/Reviews históricos). Validar S2D (órfãos, auditoria sanitizada/retida, não reconstrução de conteúdo apagado e não ressurreição de fatos excluídos).
- Após upgrade, demonstrar Domain S5 read-only sobre fatos válidos, sem snapshot inventado, respeitando Workspace, confiança/suficiência e sem reescrita; demonstrar Priority S6 derivada/determinística, sem persistência e sem substituir Review Queue, inclusive insuficiência de evidência; validar compatibilidade com portabilidade/restore S7.
- Auditar referências cross-Workspace e criar fixtures deliberadamente inválidas em bancos/cópias isolados para provar detecção, sem corromper banco real e sem reparo automático.
- Testar somente constraints e semânticas críticas SQLite/PostgreSQL que o A4 fundamentar (por exemplo unique/partial unique, CHECK, FK, transação, enum/text, JSON, nullability, ordering normativo e locks semanticamente necessários). Não transformar a etapa em hospedagem, deploy, HA, tuning ou observabilidade PostgreSQL.
- Auditar migrations S2A–S2D, S3 quando aplicável, S5 e demais relevantes: propósito, defaults, nullability, backfill, preservação factual, reversibilidade, classificação de rollback e risco. Não presumir downgrade seguro. Documentar que backup antigo exige software compatível que o produziu; distinguir rollback de migration, restore de backup e import CEI.
- Auditar `OperationReceipt` e definição exata de `FL-ABR-009` nas fontes: papel, idempotência, retenção/expiração, relação com auditoria funcional e compatibilidade após upgrade/restore. Preservar `AuditEvent` como auditoria funcional append-only e `OperationReceipt` como mecanismo técnico de idempotência; um não substitui o outro. Se regra normativa essencial estiver aberta, parar a parte dependente com `BLOCKED_HUMAN_DECISION`, sem inventar retenção.
- A8 `deep` aprovado com Blocker 0/Major 0; testes focados, regressões aplicáveis e gate autoritativo GREEN com exit 0 observado; registrar evidências de migration/compatibilidade/restore em `quality/v05-s8-integrity-compatibility-result.md`.

## Expected Scope

- A4 e evidence S8 em `tasks/plans/` e `quality/`.
- Mudanças mínimas, se justificadas pelo A4, em checker read-only/catalog, guards/constraints críticos, harness/fixtures de upgrade e testes, recovery/reconciliação e documentação estritamente necessários à integridade/compatibilidade S8.
- Atualização de `PROJECT_STATE.md` e arquivamento do contrato somente no encerramento comprovado da execução S8.

## Protected Scope

- Nenhum auto-fix ou outro side effect no checker; não converter checker em repair.
- Sem alteração retroativa de Attempts, analytics, Reviews/scheduling, classificações, Domain/Mastery ou fatos históricos; correções futuras devem seguir contratos/versionamento já aprovados.
- Sem migration até a auditoria de schema e decisão justificada no A4; não presumir rollback nem prometer downgrade automático.
- Sem segundo mecanismo de restore; reutilizar infraestrutura S7. Não confundir restore, rollback e import CEI.
- Sem PostgreSQL de produção completo, tuning geral, HA, deploy ou observabilidade de produção.
- Não antecipar S9: sem FTS, hardening geral, redesign, auditoria WCAG abrangente, performance geral ou thresholds BCR novos.
- Não autorizar/iniciar S9, S10 ou V1. Sem commit, push, tag ou release sem autorização explícita posterior.

## Constraints

- Aplicar progressive disclosure: antes da execução, ler `AGENTS.md`, este contrato e `docs/A3_Progressive_Disclosure.md`; consultar código, testes e fontes proporcionais ao risco. Confirmar baseline e dependências por evidência atual.
- A4 obrigatório antes da primeira edição funcional. O plano deve auditar fixture/cópia V0.4.4, backup validado pré-upgrade, migrations reais, recuperação isolada, reconciliação, side effects do checker, invariantes S1/S2A–S2D/S5/S6/S7, catálogo, referências cross-Workspace, constraints PostgreSQL críticas e fontes exatas de `FL-ABR-009`.
- Para invariantes novos, identificar cobertura existente, dependência (S2A–S2D, S3, S5, S7), pertinência ao checker versus guard/constraint e relação invariante → regra → fato/model → teste. Preservar/versionar catálogo explicitamente.
- Se surgir lacuna normativa real, parar antes da implementação dependente e reportar `BLOCKED_HUMAN_DECISION` com pergunta, fonte, estado atual, opções, impactos em dados/migration/upgrade/restore/PostgreSQL e recomendação técnica separada.
- Não inventar janela, threshold, métrica, tie-break, retenção, semântica de recálculo ou expectativa de igualdade. Manter desconhecido como desconhecido; fixar relógio/data somente quando o contrato de teste exigir determinismo.
- Incluir fixtures negativas isoladas e provar que diagnósticos não mutam os dados. Probes de schema e recovery devem percorrer migrations reais e código compatível; recuperação pós-fatos deve usar restore isolado conforme S7.

## Verification

- Confirmar branch/HEAD/remoto/estado inicial, dependências e evidências fechadas; `git diff --check` inicial.
- Executar testes focados de checker/read-only/fixtures negativas, upgrade V0.4.4 por migrations reais, checks físicos/FKs, reconciliação, restore/recovery isolado, S2B/S2C/S2D, S5/S6/S7, isolamento Workspace e constraints críticas PostgreSQL justificadas no A4.
- Executar regressões aplicáveis e o gate autoritativo: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`. Registrar comando, tentativas e exit codes. Não declarar GREEN sem exit 0 observado.
- Fechar A8 deep e `git diff --check`; produzir evidence final e atualizar estado/arquivar tarefa apenas após todos os critérios atendidos.

## Documentation Impact

Registrar A4, decisão de migration/rollback, decisões humanas necessárias como adendos sem atribuí-las retroativamente às fontes, classificação de compatibilidade/upgrade/restore/PostgreSQL e evidence final. Atualizar documentação de checker/invariantes e fronteira de downgrade somente se o comportamento/contrato resultar alterado ou esclarecido pela execução.

## Done When

- A4 foi fechado antes de mudança funcional; lacunas normativas relevantes foram resolvidas por fonte/decisão humana ou permaneceram explicitamente bloqueadas sem implementação dependente.
- Checker read-only e catálogo de invariantes estão comprovados; upgrade real de fixture V0.4.4, migrations, reconciliação e restore/recovery isolado estão documentados com evidências verificáveis.
- Compatibilidade S2A–S2D/S5/S6/S7 e constraints críticas PostgreSQL fundamentadas estão verificadas sem alteração histórica indevida ou expansão para S9.
- A8 deep `APPROVED` sem Blocker/Major, testes/regressões aplicáveis aprovados e gate final GREEN com exit 0 observado; evidência persistida.
- `PROJECT_STATE.md` atualizado, contrato arquivado em `tasks/completed/` e `tasks/current.md` retorna a `NO_TASK_AUTHORIZED`; nenhuma etapa posterior iniciada ou autorizada.

## Closure evidence

- S8 concluída em 2026-09-25. A4 fechado antes da primeira edição funcional em `tasks/plans/v05-s8-integrity-compatibility-plan.md`; Migration: NO. A decisão humana FL-ABR-009 permanece como adendo V0.5, sem expiry geral de OperationReceipt.
- Checker read-only 25/zero findings no candidate migrado; backup V0.4.4 pré-upgrade, migrations reais, reconciliação, restore isolado e round trip CEI comprovados. Matriz crítica PostgreSQL 18.6 PASS em banco dedicado e descartável, removido após a prova.
- A8 deep APPROVED, Blocker 0, Major 0, P0/P1 aberto 0. Gate final GREEN na sétima tentativa, exit 0, 502 passed, 86% coverage, pip-audit sem vulnerabilidades conhecidas; `gate_first_pass=false`. Evidence completa: `quality/v05-s8-integrity-compatibility-result.md`.
- `PROJECT_STATE.md` atualizado e `tasks/current.md` retornado a `NO_TASK_AUTHORIZED`; S9+ não iniciadas nem autorizadas. Sem commit, push, tag ou release.
