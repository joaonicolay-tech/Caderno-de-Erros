# Plano A4: V0.5-S2C — Correção prospectiva de gabarito

- ID da tarefa relacionada: `V0.5-S2C`
- Status: `COMPLETED`
- Objetivo: fixar, antes da primeira edição funcional, a menor implementação
  auditável de correção de gabarito por nova `QuestionRevision`, sem
  reinterpretar fatos históricos nem ampliar `tasks/current.md`.
- Baseline observado: `main` em
  `cd878a59a7eb05bbd1150ebb441be212b43cb373`; tag `v0.4.4` documentada em
  `46e887e0c4fa4dd6f7e128ab63802223d99c9e29`; somente a autorização em
  `tasks/current.md` estava modificada ao iniciar.
- Premissas: preservar integralmente S2A/S2B, Workspace, `registered`,
  `performed`, analytics, classificações, Reviews, `REV-FIXA-1.0`,
  D1/D7/D14/D30, checker read-only e recovery S6.

## Auditoria fechada antes da implementação

1. **Question, revision e alternatives.** `Question` mantém identidade,
   estado e `lock_version`; `QuestionRevision` já contém versão crescente,
   flag `is_current`, snapshot de enunciado/explicação/notas, gabarito,
   `CRITICAL_CORRECTION` e motivo. As constraints garantem versão única por
   Question e no máximo uma corrente. `Alternative` pertence a uma única
   revisão, com posição/texto únicos. O serviço existente cria nova revisão,
   copia alternativas e troca a corrente em transação. Não será criado um
   segundo sistema de versionamento.
2. **Imutabilidade e publicação existentes.** `save()` já recusa alteração de
   `QuestionRevision` e `Alternative`, mas `QuerySet.update/delete` ainda é um
   bypass de aplicação. S2C fechará somente esse bypass e manterá helpers
   internos explícitos para finalizar o gabarito e trocar `is_current` durante
   a criação. Edição convencional com histórico não poderá contornar o serviço
   auditado para alterar alternativas/gabarito.
3. **Attempts e avaliação.** `Attempt` persiste `question_revision_id`,
   `selected_alternative_id` e `is_correct`; o model valida o resultado contra
   o gabarito da revisão vinculada. INITIAL e REVIEW apresentam a current,
   carregam seu ID no contexto e confirmam sob CAS de `Question.lock_version`.
   Feedback histórico consulta a revisão persistida. A mesma trava/CAS
   serializa confirmação de Attempt e troca de revisão sem reavaliar o passado.
4. **S2B, Reviews, classificação e analytics.** Correção S2B exige a mesma
   revision na cadeia e permanece independente. Analytics, frequência,
   drill-down e classificações leem Attempts `VALID` persistidas, não o
   gabarito corrente. Reviews/Cycles guardam suas âncoras e não precisam de
   rebuild ou scheduling. S2C não chamará `AttemptCorrectionService` nem
   escreverá nesses agregados.
5. **Timeline.** Attempts já exibem o número da revisão. A projeção será
   ampliada somente para o evento `ANSWER_KEY_CORRECTED`, mostrando a transição
   anterior→nova; não será criada UI de gestão.
6. **Checker.** `QUE-002`, `QUE-003` e `ATT-001` já verificam ownership,
   revisão corrente completa, sequência e Attempt→revision/alternative/result.
   Não é necessário novo check. `AUD-001` será apenas estendido para validar os
   metadados S2C e continuará read-only.

## Migration gate e decisão

- **`questions`: zero migration.** O schema atual já suporta R1→R2→R3,
  alternativas próprias, exatamente uma correta, corrente única e vínculo
  histórico de Attempt. Não haverá campo, pointer paralelo ou backfill.
- **Lacuna estrutural comprovada em `operations`: uma migration aditiva é
  necessária.** O check fechado de `AuditEvent` não admite
  `ANSWER_KEY_CORRECTED` nem entidade `QUESTION`; além disso, `entity_id` e
  `related_entity_id` não conseguem registrar simultaneamente Question,
  revisão anterior e revisão nova. A migration acrescentará
  `previous_entity_id` nullable e ampliará choices/constraints. Eventos S2A/S2B
  antigos permanecem byte/semanticamente iguais; não há default nem backfill.
- O evento S2C usará `entity_id=Question`, `previous_entity_id=R1` e
  `related_entity_id=R2`, além de Workspace, correlação, motivo codificado e
  instante. Não haverá conteúdo, alternativa textual, resposta, explicação,
  JSON ou snapshot.
- Compatibilidade: aditiva para upgrade S2A→S2B→S2C. Reverse é tecnicamente
  seguro antes de fatos S2C; depois de eventos/correções reais perde trilha
  obrigatória e o recovery suportado é restore com versão compatível. Não se
  promete downgrade de código sobre R2/R3.

## Decomposição executável

1. **Serviço transacional explícito.** Criar `AnswerKeyCorrectionService`
   Workspace-scoped. Entrada: Question, revisão corrente esperada, posição do
   novo gabarito, motivo codificado e correlação. O serviço trava a Question,
   revalida current/estado, copia sem alteração todo conteúdo e alternativas,
   muda somente o gabarito, publica nova revisão, incrementa o lock e registra
   auditoria na mesma transação durável.
2. **Exactly-one-correct e identidade.** A posição deve apontar para uma das
   pelo menos duas alternativas distintas da revisão esperada e deve realmente
   alterar o gabarito. A alternativa correta da nova revisão será uma nova
   linha pertencente a ela; nenhum ID de Alternative anterior será reutilizado.
3. **Concorrência e idempotência.** `select_for_update`, expected revision,
   current única, versão crescente e `Question.lock_version` protegem correção
   dupla, edição/publicação concorrente e confirmação de Attempt. Retry com a
   mesma correlação e entrada resolve o evento/revisão já confirmados; uso
   divergente da correlação falha. `OperationReceipt` e sua retenção não mudam.
4. **Atomicidade/fault injection.** Expor hooks de teste após criar revision,
   após copiar alternatives, antes/depois de trocar current e antes/depois do
   AuditEvent. Qualquer falha deve restaurar revisão, alternativas, current,
   lock e auditoria.
5. **Projeções e guards.** Estender timeline e `AUD-001`; preservar analytics,
   Reviews, classificação e cadeias S2B sem escrita. Bloquear apenas o bypass
   convencional de mudança crítica após histórico, mantendo edições permitidas
   fora desse caso.
6. **Testes focados.** Cobrir R1→R2→R3, current única, stale/double correction,
   retry e correlação conflitante, alternativas variáveis, Workspace,
   imutabilidade, fault injection, Attempt R1 preservada/explicável, Attempt R2
   futura, cadeia VOIDED→VALID, snapshots de analytics/classificação/Reviews e
   timeline/auditoria sanitizada.
7. **Upgrade e recovery.** Estender o ensaio real V0.4.4-equivalent→S2A→S2B
   até S2C, preservando AuditEvent/categoria/merge/reagendamento/ciclo MANUAL e
   cadeia S2B. Após R1→R2 e Attempt R2, criar backup S6, restaurar isoladamente
   e reconciliar integridade física/FKs, current, Attempts R1/R2, cadeia,
   analytics, Reviews e checker.
8. **Fechamento.** Executar regressão focada, migration checks, A8 deep,
   `git diff --check` e gate autoritativo. Persistir evidence e métricas A7;
   atualizar estado/arquivar somente após GREEN e então usar `finish-task`.

## Riscos e controles

- **Reinterpretação histórica:** nenhuma escrita em Attempt, classificação,
  Review ou analytics; testes com snapshots e cadeia S2B.
- **Branch/dupla current:** trava da Question, expected revision, unique
  parcial, versão única e CAS do lock.
- **Attempt concorrente:** ambos os fluxos escrevem/validam
  `Question.lock_version`; o vencedor define a revisão apresentada e o outro
  revalida/falha sem fato ambíguo.
- **Cross-Workspace:** Question, revisões, alternativas e evento são
  recarregados sob o Workspace antes da mutation.
- **Leakage:** motivo fechado e IDs UUID; nenhum campo de conteúdo no evento.
- **Escopo:** sem S2D, permanent delete, purge, retenção, UI S3, domínio,
  prioridade, export/import, mudança de scheduling ou arquitetura.

## Condição de saída

O desenho A4 e a decisão de migration estão fechados antes da primeira edição
funcional. A execução segue somente dentro de `V0.5-S2C`; conclusão depende de
upgrade/recovery, testes focados, A8 deep `APPROVED`, gate GREEN, evidence e
`finish-task`.
