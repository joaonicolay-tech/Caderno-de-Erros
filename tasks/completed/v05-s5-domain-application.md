# Task Contract

Status: COMPLETED

## Identification

- Task ID: `V0.5-S5`
- Product version: `V0.5`
- Stage: Aplicação de Domain, reabertura, agregações e explicação consultável
- Task type: implementação funcional transversal de domínio, lifecycle, consultas e agregações
- Size: `L`
- Risk: `high`
- Migration: `UNKNOWN` até auditoria A4
- A4: obrigatório e deve ser concluído antes da primeira edição funcional
- A8 review: `deep`
- Modelo recomendado para execução: GPT-6 Sol, reasoning High

## Goal

Aplicar `DOM-HEUR-1.0` de S4 aos fatos efetivos reais, entregando avaliação
corrente por Question, mastery e reabertura conforme RN-079/RN-080, agregações
hierárquicas, confidence/suficiência e explicações consultáveis, com
recalculabilidade determinística, isolamento por Workspace e preservação do
histórico S2A–S2D.

## Context

- Baseline concluído e protegido: V0.4.4, V0.5-P0, S1, S2A, S2B, S2C, S2D,
  S3 e S4. Dependências obrigatórias S2A–S2D e S4 estão satisfeitas.
- S4 é a autoridade matemática aprovada: policy pura versionada
  `DOM-HEUR-1.0`, adapter read-only, `Aq`, `Pq`, `Fq`, `Eq`, `M_q`, `C_q`,
  recovery cap, maturity/sufficiency, RN-078, RN-079, agregação matemática e
  explicações estruturadas. Consumir a policy; não a redesenhar nem duplicar
  fórmulas, thresholds, critérios ou matemática.
- Fontes obrigatórias: `tasks/plans/v05-release-execution-plan.md`,
  `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md`,
  `tasks/plans/v05-s4-domain-heuristic-plan.md`,
  `quality/v05-s4-domain-heuristic-result.md`, contratos concluídos S2A–S2D e
  S3 quando necessário à integração. Consultar código, migrations e testes
  diretamente relacionados; `PROJECT_STATE.md` para baseline/encerramento.
- Revisões históricas, Attempts, analytics e Reviews não podem ser
  reinterpretados. S2B define ponta VALID efetiva; S2C é prospectiva; S2D
  remove definitivamente o agregado e fatos derivados. Dados excluídos e
  auditoria sanitizada não são evidência corrente.
- S3 existe, mas não autoriza por si só expansão de UI. S5/S6 e posteriores
  permanecem fora deste contrato, exceto S5 explicitamente autorizada aqui.

## Acceptance Criteria

- Criar e concluir plano A4 S5 antes de qualquer edição funcional. Auditar
  policy/selectors S4; Question/QuestionRevision, Attempts e replacement
  chains, ReviewCycle/Review e ciclos MANUAL, taxonomy/archive/Workspace,
  analytics, transações, locks/CAS/idempotência, OperationReceipt/auditoria,
  checker, migrations/schema, consultas/performance e fluxos FL-018/FL-019 e
  CT-044/casos Domain. A4 fecha arquitetura e decisão de migration YES/NO com
  evidência; não criar migration de cache.
- Avaliação corrente por Question deriva somente de Question ativa e fatos
  efetivos válidos, revisão histórica vinculada e Reviews/ciclo válidos,
  consumindo S4. Archived fica fora das avaliações e agregações atuais; deleted
  não reaparece. DOMINATED só ocorre automaticamente se a decisão RN-079 de S4
  for verdadeira; ciclo COMPLETED não equivale a DOMINATED e o usuário não pode
  forçar esse estado.
- Implementar reabertura automática somente por gatilhos explicitamente
  normatizados em RN-080/fluxo autorizado. Considerar os gatilhos aplicáveis
  documentados (erro válido, anulação que remova evidência essencial,
  arquivamento e confidence abaixo do requisito), sem acrescentar gatilhos
  intuitivos. Avaliação on-demand deve detectar envelhecimento de confidence;
  não criar scheduler sem necessidade normativa.
- Implementar reabertura manual com validação transacional: Question ativa e
  DOMINATED no Workspace correto, sem ciclo ativo incompatível, motivo
  obrigatório; preservar domínio anterior, registrar reabertura, criar ciclo
  `MANUAL` e D1 para hoje+1. A ação manual é a âncora temporal; não recalcular
  D1 de Attempt histórica usada como contexto. Reutilizar serviços S2A quando
  semanticamente compatíveis, mantendo distinta a semântica de inclusão
  manual. Repetição, concorrência e corrida com erro, void/replacement,
  confidence e archive não podem produzir eventos/ciclos/D1 duplicados ou
  sucesso parcial; usar lock/CAS/idempotência coerentes com a arquitetura.
- Agregar com peso igual por Question, sem favorecer quem tem mais Attempts,
  deduplicando IDs e respeitando a matemática S4, para subsubject quando
  existente, subject e discipline; preservar confidence hierárquica, C_h,
  suficiência e comportamento para C_q ausente conforme S4. Sem N+1 em lotes.
- Explicações consultáveis expõem versão da policy, fatores, códigos/IDs de
  evidência permitidos, exclusões, maturity, confidence e critérios de mastery,
  sem texto contraditório nem conteúdo proibido.
- Mesmo conjunto de fatos e data de avaliação explícita produzem resultado
  determinístico. Workspace é isolado em serviços/consultas/transições.
- Preservar histórico de DOMINATED/AUTO_REOPENED/MANUAL_REOPENED se a
  representação exigida for confirmada no contrato/schema; eventos anteriores
  nunca são reescritos. Reavaliações sem mudança não duplicam transições.
- Auditar e medir on-demand para uma Question, lote, subject e discipline em
  volume representativo; registrar query count e tempo observado sem inventar
  threshold. Criar snapshots apenas se benchmark demonstrar necessidade e,
  antes de persistência/snapshot ou decisão semântica de recálculo/versão,
  resolver V05-OD04 / RN-ABR-004 pelo `BLOCKED_HUMAN_DECISION`, com lacuna,
  evidências, alternativas, impacto, benchmark aplicável e recomendação técnica
  separada. Não decidir semanticamente pelo usuário.
- Qualquer mutação nova é atômica; fault injection prova rollback proporcional
  entre evento, ciclo, D1 e projeções. Migration, se A4 comprovar necessidade
  autorizada, documenta entidade/campos/constraints/indexes/defaults/backfill,
  reversibilidade, impacto e recovery; snapshot/materialização aguarda OD04.
  Provar upgrade sobre baseline V0.5 atual, preservando S2A–S2D, S3 e S4;
  nunca reescrever migration histórica.
- Cobrir testes focados de: estados Domain (NO_DATA, INITIAL/provisional,
  INITIAL+REVIEW/established, mastery falso/verdadeiro, confidence stale,
  archive, replacement, revisão histórica, ciclos completed/superseded e
  delete); mastery idempotente e Workspace; cada gatilho autorizado de
  auto-reopen e histórico; manual reopen e pré-condições, D1/âncora,
  duplicação/concorrência/rollback; reconciliação S2B, prospectividade S2C,
  ausência pós-delete S2D; agregações/pesos/dedup/hierarquia/C_h/suficiência;
  explicabilidade e determinismo; desempenho representativo e query counts.
- Executar regressões relacionadas a S2A–S2D, S4, Attempts, Reviews, ciclos
  manuais, taxonomy, analytics, timeline, checker e backup/recovery se houver
  migration. Checker permanece read-only. Não implementar Priority nem
  antecipar S6.
- A8 deep `APPROVED`, Blocker 0 e Major 0; gate autoritativo GREEN com exit 0;
  evidência registra tentativas, resultados, benchmark, migration/snapshot/
  OD04, A4/A8, recovery e escopo excluído. Métricas A7 não observáveis ficam
  `unknown`, nunca estimadas.

## Expected Scope

- Plano A4 S5 e, após sua conclusão, mudanças mínimas em `src/modules/domain/`
  e integrações de serviço/selector necessárias a avaliação, lifecycle,
  agregações e explicações.
- Testes focados e regressões diretamente relacionadas; probes de upgrade/
  recovery apenas se migration ou mutação histórica os exigir.
- Evidência `quality/v05-s5-domain-application-result.md` (ou nome consistente),
  atualização de `PROJECT_STATE.md` e arquivamento em `tasks/completed/` somente
  após critérios e gate comprovados.
- Migration é condicional ao A4; snapshots são condicionais ao benchmark e à
  resolução humana de OD04.

## Protected Scope

- Fórmulas/regras de S4, RN-068–RN-079, policy `DOM-HEUR-1.0` e decisões já
  aprovadas; não alterar silenciosamente policy ou limiares. Se necessário,
  parar e registrar a lacuna/decisão aplicável.
- Fatos históricos, tentativas, resultados, analytics, classificações,
  revisões, Reviews/ciclos preservados; não reinterpretar história nem
  reconstruir fatos removidos por S2D.
- Checker read-only; nenhum repair automático. Nenhuma funcionalidade Priority,
  scheduler intuitivo, UI/dashboard ampliado, S6+, commit, push, tag ou release
  é autorizado por este contrato.
- Nenhuma migration artificial, cache persistente, snapshot ou materialização
  de Domain sem evidência e decisão humana requeridas.

## Constraints

- `tasks/current.md` é a autoridade única. Concluir A4 antes da primeira edição
  funcional; decidir migration a partir da auditoria real do schema.
- S4 é autoridade matemática; S5 integra fatos, lifecycle e consultas.
- `DOMINATED` apenas via RN-079. Separar ciclo concluído de domínio; manter
  Workspace e histórico íntegros.
- Se V05-OD04 exigir escolha semântica entre on-demand, snapshot, histórico
  materializado ou recálculo sob nova versão, parar o trabalho dependente e
  usar `BLOCKED_HUMAN_DECISION` conforme evidência exigida acima.
- Backups/recovery seguem política aprovada; recovery de mudança durável é
  restore isolado compatível, não downgrade presumido.

## Verification

- Testes focados e regressões especificados nos Acceptance Criteria, incluindo
  failure injection, Workspace, determinismo e query/performance.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`;
  registrar cada tentativa, exit code e gate_first_pass conforme observado.
- A8 deep e evidência persistida; `PROJECT_STATE.md` e arquivo concluído
  atualizados após comprovação. Não declarar GREEN sem exit code 0 observado.

## Documentation Impact

Concluir o A4 em `tasks/plans/`; registrar resultado completo em `quality/`;
atualizar `PROJECT_STATE.md` e arquivar este contrato em
`tasks/completed/` após conclusão comprovada. Só alterar requisitos/decisões
normativas se uma lacuna for identificada e tratada por decisão autorizada.

## Done When

- A4 COMPLETED; migration YES/NO comprovada; OD04 resolvida se necessária;
  S4 consumida sem duplicação ou alteração normativa indevida.
- Avaliação corrente, mastery/reabertura automática e manual, agregações,
  confidence/suficiência, explicações, determinismo, Workspace, concorrência,
  atomicidade e compatibilidade S2A–S2D atendem aos critérios e testes.
- Benchmark, performance, upgrade/recovery quando aplicáveis, regressões e A8
  deep estão aprovados; gate completo GREEN; evidência e estado atualizados;
  S5 arquivada e `tasks/current.md` retorna a `NO_TASK_AUTHORIZED`.
- S6 e etapas posteriores continuam não autorizadas e não são iniciadas nesta
  tarefa.

## Closure Evidence

- A4 `COMPLETED`: `tasks/plans/v05-s5-domain-application-plan.md`; OD04 e as quatro decisões humanas registradas.
- Migration `YES` para `MasteryStateEvent` e `ReviewCycle.manual_purpose`; sem snapshot, backfill fictício ou alteração de limiares S4.
- A8 deep `APPROVED`, Blocker 0, Major 0, Minor 0 abertos; benchmark, upgrade/reverse/recovery, testes e ressalvas em `quality/v05-s5-domain-application-result.md`.
- Gate autoritativo final `GREEN`, exit code 0, 473 passed, 87% de cobertura; `git diff --check` exit 0.
- `PROJECT_STATE.md` atualizado; `tasks/current.md` retorna a `NO_TASK_AUTHORIZED`. S6+ não autorizada. Nenhum commit, push, tag ou release.
