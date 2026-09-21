# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: `V0.5-S2C`
- Product version: `V0.5`
- Stage: Correção prospectiva e auditável de gabarito por nova `QuestionRevision`
- Task type: implementação funcional de versionamento, integridade e auditoria
- Size: `L`
- Risk: `high`
- Migration: `UNLIKELY/UNKNOWN`, sujeita à auditoria de schema do plano A4
- A4: obrigatório antes da implementação
- Recommended execution model: GPT-5.6 Sol, reasoning Medium; escalar para High somente se A4 demonstrar complexidade adicional real
- A8 review: deep

## Goal

Implementar a correção prospectiva e auditável de gabarito por nova
`QuestionRevision` imutável, sem reinterpretar fatos históricos: a nova revisão
torna-se corrente para futuras Attempts, enquanto Attempts, resultados,
classificações, analytics e Reviews históricos permanecem vinculados aos fatos e
às revisões originalmente aplicáveis.

## Context

- Baseline: `v0.4.4`, V0.5-P0, V0.5-S1, V0.5-S2A e V0.5-S2B concluídos.
- S2A fornece `AuditEvent` funcional append-only, isolamento por Workspace,
  recovery isolado e checker read-only; S2B fornece lifecycle estável de
  correção de Attempt, cadeia efetiva e checker com 22 checks. Ambos devem ser
  preservados.
- As autoridades normativas são
  `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md` e
  `tasks/plans/v05-release-execution-plan.md`.
- S2D continua `NOT AUTHORIZED`; S2C é a única tarefa atualmente autorizada.

## Acceptance Criteria

- Antes da implementação, existe plano A4 específico que audita `Question`,
  `QuestionRevision`, alternativas, ponteiro de revisão corrente, criação e
  edição existentes, vínculo/elegibilidade de Attempt, avaliação de resposta,
  Reviews, analytics, timeline, `AuditEvent`, Workspace, concorrência,
  migrations, recovery e checker; ele decide por evidência a necessidade real
  de migration.
- A correção cria nova `QuestionRevision` imutável, preservando todos os campos
  não autorizados para alteração e mudando somente o gabarito permitido. A
  revisão anterior continua consultável, inalterada e vinculada às Attempts
  históricas; correções posteriores produzem R3, R4 etc., nunca edição da
  revisão publicada.
- A nova revisão tem exatamente um gabarito válido conforme as regras existentes
  do tipo de questão, preservando mínimo de alternativas, unicidade da correta,
  alternativas variáveis e constraints vigentes; a referência de revisão corrente
  é atualizada atomicamente, sem duas revisões correntes incompatíveis.
- A operação exige motivo estruturado/codificado, registra
  `ANSWER_KEY_CORRECTED` sanitizado e append-only com Workspace, Question, IDs
  técnicos das revisões, correlação, motivo e instante; não armazena enunciado,
  alternativas textuais, resposta, explicação ou payload de revisão.
- Nova revisão, atualização de corrente e auditoria confirmam juntas. Fault
  injection na criação, na mudança de corrente ou na auditoria prova rollback
  integral, sem revisão órfã, ponteiro parcial, mudança sem auditoria ou
  auditoria sem mudança.
- Attempts históricas preservam `revision_id`, alternativa selecionada,
  correctness, resultado, classificação, status, campos de void e cadeia de
  replacement. A correção de gabarito não aciona `ATTEMPT_VOIDED`,
  `ATTEMPT_REPLACED`, reconstrução S2B, reclassificação ou alteração retroativa.
- Attempts futuras usam a revisão corrente e são avaliadas pelo gabarito da
  revisão a que realmente se vinculam. Consulta/timeline de Attempt histórica
  continua explicando alternativas, gabarito, resposta e resultado da revisão
  histórica, sem substituição silenciosa pela corrente.
- Sem nova Attempt, analytics históricos permanecem numericamente idênticos;
  Reviews, `ReviewCycle`, due dates, etapas, completion, D1/D7/D14/D30,
  `REV-FIXA-1.0` e scheduling histórico não são recriados, reagendados ou
  modificados. Futuras Attempts de REVIEW seguem o modelo canônico de conteúdo
  corrente sem mudar a policy de agenda.
- Cross-Workspace falha sem mutação. Concorrência protege correções simultâneas,
  ponteiro corrente obsoleto, edição convencional concorrente e criação de
  Attempt durante a troca de revisão, com comportamento transacional e
  determinístico. Retry semanticamente equivalente não cria revisões novas
  duplicadas e não altera a expiração de `OperationReceipt`.
- A necessidade de migration é documentada após a auditoria: zero migration é o
  resultado correto se o versionamento atual bastar; qualquer migration real é
  mínima, justificada e classificada quanto a upgrade/rollback. Não há backfill
  ou migration artificial.
- Upgrade prova `V0.4.4-equivalent → S2A → S2B → S2C candidate`, preservando
  fatos relevantes S2A/S2B. Backup/restore isolado após uma correção e uma
  Attempt futura reconcilia checker, Attempt histórica, revisão corrente,
  analytics e Reviews. Rollback não presume que código anterior suporte dados
  de revisões novas; se não houver migration, essa limitação é documentada.
- O checker permanece read-only; recebe apenas checks mínimos comprovadamente
  necessários para revisão corrente, ownership, vínculo de Attempt e consistência
  do versionamento, sem repair.
- Testes cobrem R1 preservada/R2 corrente/R3 posterior, motivo/auditoria
  sanitizada, histórico e futuro de Attempts, snapshot de analytics, ausência de
  mutação de Reviews, preservação de cadeia S2B, atomicidade, concorrência,
  Workspace, upgrade, recovery e regressão focada de revisions, alternatives,
  Attempts, S2B, Reviews, analytics, classifications, timeline e checker.
- A8 deep é `APPROVED`, sem Blocker/Major, e revisa versionamento, imutabilidade,
  ponteiro corrente, histórico, vínculo de Attempt, analytics, Reviews,
  auditoria, atomicidade, concorrência, Workspace, upgrade/recovery, regressões
  S2A/S2B e ausência de vazamento S2D. O gate final é GREEN observável e a
  evidência persistente registra baseline, A4, schema/migration, lifecycle,
  histórico, auditoria, recovery, checker, testes, A8 e gate.

## Expected Scope

- Domínio, serviços, selectors/policies, migrations aditivas somente se
  confirmadas, testes, checker read-only, recovery/evidência e documentação
  estritamente necessários para a correção prospectiva de gabarito S2C.
- `PROJECT_STATE.md`, métricas e arquivamento da tarefa somente no encerramento
  comprovado de S2C.

## Protected Scope

- S2B: void/replacement, cadeia efetiva, reconstrução de Attempts e seus fatos
  históricos; não usar esses fluxos para reinterpretar gabarito passado.
- S2D: exclusão permanente, retention e purge permanecem `NOT AUTHORIZED`.
- UI geral de gestão (S3), domínio (S4/S5), prioridade (S6), export/import (S7),
  event sourcing, infraestrutura distribuída e alterações de D1/D7/D14/D30,
  `REV-FIXA-1.0` ou policy de timezone.
- Funcionalidades concluídas de S2A, incluindo categorias pessoais, merge,
  reagendamento, inclusão manual, auditoria append-only, checker e recovery,
  exceto integração mínima comprovadamente indispensável para S2C.

## Constraints

- Correção de gabarito não corrige o passado: não sobrescrever, excluir, ocultar,
  anular, substituir ou recalcular fatos históricos para simular correção.
- Não alterar arbitrariamente enunciado, explicação, taxonomia ou outros dados
  fora do gabarito autorizado; não introduzir texto livre sensível em auditoria.
- Não duplicar lógica temporal/de revisão em templates ou serviços divergentes;
  não ampliar o contrato com UI, domínio, prioridade, export/import ou S2D.
- Migrations, se houver, não podem tratar reverse como recuperação suportada após
  fatos reais; usar restore isolado quando aplicável.

## Verification

- Executar testes focados definidos pelo A4, incluindo revision lifecycle,
  histórico/futuro de Attempts, analytics, Reviews, cadeia S2B, auditoria,
  atomicidade, concorrência, Workspace, upgrade, rollback e recovery.
- Executar `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`
  e exigir resultado GREEN observável, registrando first pass, retry, falha real
  ou incidente externo corretamente.
- Executar A8 deep, checks S5/S6 aplicáveis em cópias isoladas e manter o checker
  exclusivamente read-only.

## Documentation Impact

- Plano A4 específico, evidence persistente S2C, decisão de migration/rollback,
  métricas A7 sem estimar dados indisponíveis e atualização factual de
  `PROJECT_STATE.md` somente no encerramento comprovado.

## Done When

- O plano A4 decide por evidência o schema/migration; nova revisão imutável,
  revisão anterior preservada, ponteiro corrente atômico, motivo e auditoria
  sanitizada funcionam.
- Histórico de Attempts, analytics e Reviews/scheduling permanecem inalterados;
  futuras Attempts usam a revisão nova; S2B, Workspace, atomicidade,
  concorrência, upgrade, rollback/recovery e checker read-only estão provados.
- Regressão focada, A8 deep e gate final estão GREEN; evidence existe; S2C é
  arquivada e `tasks/current.md` retorna a `NO_TASK_AUTHORIZED` no encerramento
  da etapa. S2D permanece não autorizada.

## Closure Evidence

- Plano A4: `tasks/plans/v05-s2c-answer-key-correction-plan.md`, `COMPLETED`
  antes da primeira edição funcional.
- Implementação: correção transacional R1→R2→R3, alternativas próprias,
  current única, motivo codificado e `ANSWER_KEY_CORRECTED` sanitizado.
- Migration: somente `operations.0003_answer_key_correction_audit`, aditiva,
  sem backfill; manifesto `quality/v05-s2c-migrations.json`.
- Preservação: Attempts históricos, cadeia S2B, analytics, classificações,
  Reviews/scheduling e Workspaces reconciliados; S2D ausente.
- Testes: 14 S2C; regressão focada 214 passed; upgrade/recovery isolado GREEN.
- A8 deep: `APPROVED`, Blocker 0, Major 0, Minor 0 aberto.
- Gate autoritativo: tentativa 1 RED no mypy de testes; tentativa 2 GREEN,
  exit 0, 388 passed em 133,04 s, 87% coverage, total 172,9 s e pip-audit sem
  vulnerabilidades conhecidas.
- Evidência: `quality/v05-s2c-answer-key-correction-result.md`.
- Não ações: sem S2D, delete/retention/purge, UI S3, commit, push, tag ou release.
