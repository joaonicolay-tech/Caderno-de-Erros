# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: `V0.5-S2D`
- Product version: `V0.5`
- Stage: Exclusão permanente por agregado e retenção sanitizada
- Task type: implementação funcional destrutiva, integridade, auditoria e recovery
- Size: `L`
- Risk: `high`
- Migration: `EXPECTED`, sujeita à confirmação pela auditoria de schema do plano A4
- A4: obrigatório antes da implementação
- Recommended execution model: GPT-5.6 Sol, reasoning High
- A8 review: deep

## Goal

Implementar com segurança a exclusão permanente autorizada do agregado de
`Question`, com elegibilidade e impacto explícitos, confirmação transacional,
remoção sem órfãos, reconciliação das projeções e auditoria
`QUESTION_PERMANENTLY_DELETED` estritamente sanitizada, retida por 90 dias
corridos e expurgável pelo mecanismo exigido pelo contrato normativo.

## Context

- Baseline: `v0.4.4`, V0.5-P0, V0.5-S1, V0.5-S2A, V0.5-S2B e V0.5-S2C
  concluídos; `AuditEvent` append-only, checker read-only com 22 checks e S6
  backup/recovery isolado estão disponíveis.
- As autoridades normativas são
  `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md` e
  `tasks/plans/v05-release-execution-plan.md`.
- `ARCHIVED`, `VOIDED` e `PERMANENT DELETE` são operações distintas.
  Arquivamento é o padrão para Question com histórico; Attempt não é removida
  isoladamente.
- S3 e todas as etapas posteriores permanecem `NOT AUTHORIZED`. S2D é a única
  tarefa atualmente autorizada.

## Acceptance Criteria

- Antes de código funcional, existe plano A4 específico e coerente que audita
  o agregado Question e seu grafo real: Question, QuestionRevision,
  Alternative, Attempt e cadeias S2B, ErrorClassification e revisões, Review,
  ReviewCycle, ReviewScheduleChange, ciclos manuais/superseded, tags/origens/
  associações, AuditEvent, projeções e tabelas auxiliares. O plano classifica
  cada relação como parte removível, histórico externo bloqueante, projeção
  reconstruível, auditoria sanitizável ou referência bloqueante; define ordem
  de remoção, comportamento de FKs, migrations, retenção/expurgo, backup,
  recovery, analytics, Workspace, atomicidade, concorrência, checker, testes e
  gate, sem inferir a ordem apenas pelo nome de FKs.
- O A4 reconcilia as fontes quanto à elegibilidade exata, backup prévio,
  tratamento de Question com histórico e mecanismo de expurgo. Se persistir
  uma lacuna que altere perda permanente de dados, a implementação para e pede
  decisão humana, sem escolher regra silenciosamente.
- Um serviço Workspace-scoped de preview, sem mutação, retorna de forma
  determinística elegibilidade, bloqueios, razões, impacto, dependências,
  necessidade de backup e confirmação requerida. DRAFT sem Attempt, ciclo ou
  dependência usa somente o caminho simples normativamente permitido;
  Question com histórico permanece arquivada por padrão e só é apagada quando
  cumprir todos os requisitos explícitos.
- Quando aplicável, backup pré-exclusão só libera a operação depois de criado,
  validado, restaurado em destino isolado, reconciliado e aprovado pelo checker
  S5; arquivo existente não é prova suficiente. Não antecipar exportação S7,
  nem reescrever backups válidos anteriores.
- A confirmação revalida elegibilidade, Workspace e concorrência. A remoção é
  all-or-nothing por agregado, com ordem explícita e compreendida: não resta
  Question apagada com Attempt, Review, classification, Alternative, cadeia de
  replacement ou referência órfã; CASCADE só pode ser mantido onde já for
  justificado e testado, nunca como substituto da análise.
- O delete trata todas as revisões e alternatives, Attempts vinculadas a
  revisões distintas, cadeias `VOIDED → VALID`, classificações e revisões,
  Reviews/ciclos ativos, completos, manuais e superseded, mudanças de agenda e
  pendências. Não apaga categorias padrão ou pessoais compartilhadas; anomalia
  cross-Workspace bloqueia e vira finding de integridade, sem apagar ambos.
- Delete, reconciliação e `QUESTION_PERMANENTLY_DELETED` confirmam juntos. O
  evento preserva apenas tipo, instante, identificador técnico do próprio
  evento, correlação técnica, tipo da entidade e motivo codificado, pelo prazo
  de 90 dias corridos; não retém Question ID quando vedado, stem, alternatives,
  answers, explanation, texto de classificação, payload, snapshot ou dado que
  reconstrua conteúdo. Logs técnicos e novos snapshots também não podem copiar
  esse conteúdo.
- Após 90 dias, o registro sanitizado deve ser obrigatoriamente e
  definitivamente expurgado pelo mecanismo autorizado. O A4 determina, por
  fonte, se S2D deve
  implementar o cleanup agora ou somente a estrutura/seleção para manutenção
  posterior; se não houver decisão suficiente, para e pede decisão humana, sem
  inventar scheduler.
- Após confirmação, o agregado não participa de `registered`, `performed`,
  attempts, acertos/erros/taxas, categorias, drill-down, disciplina ou assunto;
  cycles/Reviews são removidos juntos e nenhuma pendência permanece. Não deixar
  cache ou projeção órfã, nem tentar manter timeline funcional do conteúdo.
- Fault injection durante análise final, em cada ponto relevante da remoção,
  antes/depois da reconciliação e antes/depois do AuditEvent prova rollback
  integral. Concorrência protege Attempt, Review/reagendamento, correções S2B,
  correções S2C e dois deletes simultâneos. Retry idêntico não cria dois
  eventos; requisição para agregado inexistente com correlação diferente não é
  sucesso automático.
- Migration, se comprovadamente necessária para auditoria/retenção/expurgo, é
  mínima, aditiva quando possível, sem conteúdo ou backfill artificial, e
  classificada quanto a upgrade/rollback. O checker permanece exclusivamente
  read-only e recebe apenas checks necessários para auditoria sanitizada,
  retenção/expurgo e referências ao agregado inexistente.
- Upgrade e recovery provam `V0.4.4-equivalent → S2A → S2B → S2C → S2D`, com
  fatos S2A, cadeia S2B e revisões S2C, backup/restore isolado, reconciliação,
  `integrity_check`, `foreign_key_check` e checker S5. Após fatos S2D, rollback
  suportado é recovery por backup compatível, não reverse destrutivo presumido.
- Testes cobrem preview/eligible/blocked, impacto, confirmação, agregado,
  ordem/FKs, ausência de órfãos, auditoria e conteúdo proibido, retenção/expurgo,
  analytics, Reviews, categorias, Workspace, atomicidade, fault injection,
  concorrência, idempotência, migration, upgrade, backup/recovery e regressões
  S2A/S2B/S2C.
- A8 deep é `APPROVED`, sem Blocker/Major, e revisa destruição, sanitização,
  retenção, purge, grafo, FKs, migrações, Workspace, atomicidade, concorrência,
  idempotência, analytics, recovery, checker e ausência de escopo S3+. O gate
  final é GREEN observável e a evidência persistente registra baseline, A4,
  schema/migration, lifecycle, audit, retention/purge, recovery, checker,
  testes, A8 e gate.

## Expected Scope

- Plano A4, domínio/serviços/selectors necessários, migrations somente se
  justificadas, testes, checker read-only, backup/recovery, evidências e
  documentação estritamente necessários à exclusão permanente S2D.
- `PROJECT_STATE.md`, métricas e arquivamento somente no encerramento
  comprovado de S2D.

## Protected Scope

- Arquivamento, VOID/replacement S2B, correção prospectiva de gabarito S2C,
  categorias pessoais/merge, scheduling, D1/D7/D14/D30, `REV-FIXA-1.0`, policy
  de timezone e funcionalidades concluídas S2A--S2C, exceto integração mínima
  comprovadamente indispensável a S2D.
- UI geral de gestão (S3), filtros salvos, domínio (S4/S5), prioridade (S6),
  export/import e UI de backup/restore (S7), event sourcing e infraestrutura
  distribuída.

## Constraints

- Não usar permanent delete quando archive ou void forem a operação correta;
  não apagar entidades fora do agregado autorizado e não reparar inconsistências
  apagando dados cross-Workspace.
- Não preservar conteúdo funcional excluído em AuditEvent, logs, payloads,
  snapshots ou trilhas alternativas; backup não é auditoria de delete.
- Não introduzir scheduler, exportação, UI geral ou política não decidida; não
  duplicar lógica temporal ou de review e não tornar o checker mutável.
- Migrations e rollback não podem prometer recuperação por reverse após fatos
  reais; aplicar restore isolado quando exigido.

## Verification

- Executar os testes focados definidos pelo A4, incluindo preview, agregados,
  FKs, audit/retenção/purge, analytics, Reviews, Workspace, atomicidade,
  concorrência, idempotência, upgrade e recovery.
- Executar `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`
  e exigir GREEN observável, registrando corretamente tentativa, falha real ou
  incidente externo.
- Executar A8 deep e S5/S6 aplicáveis somente em cópias isoladas; manter o
  checker exclusivamente read-only.

## Documentation Impact

- Plano A4 específico, evidência persistente S2D, decisão de migration/rollback,
  retenção/purge, métricas A7 sem estimar dados indisponíveis e atualização
  factual de `PROJECT_STATE.md` somente no encerramento comprovado.

## Done When

- O plano A4 decide por evidência o grafo, schema/migration, elegibilidade,
  backup, sanitização e mecanismo de expurgo; a exclusão transacional por
  agregado, preview, confirmação, ausência de órfãos, reconciliação e auditoria
  sanitizada de 90 dias funcionam.
- Retenção/expurgo, Workspace, atomicidade, concorrência, idempotência,
  analytics, Reviews, S2B/S2C, upgrade e backup/recovery estão comprovados, com
  checker read-only.
- Regressão focada, A8 deep e gate final estão GREEN; evidência existe; S2D é
  arquivada e `tasks/current.md` retorna a `NO_TASK_AUTHORIZED` no encerramento.
  S3 e etapas posteriores permanecem não autorizadas.

## Closure Evidence

- Plano A4 `tasks/plans/v05-s2d-permanent-deletion-plan.md`: `COMPLETED`.
- Decisões humanas: `quality/v05-s2d-human-decision-gate.md`; evento final
  preserva somente `workspace_id` técnico, jamais ID da Question.
- Implementação: preview, elegibilidade, backup S6/restore S5 para histórico,
  delete transacional, exceções controladas de AuditEvent/OperationReceipt,
  checker read-only e expurgo manual no limite UTC de 90 dias.
- Migration: somente `operations.0004`; manifesto suplementar
  `quality/v05-s2d-migrations.json`; recovery pós-fatos por backup compatível.
- Testes: 20 casos S2D, upgrade/recovery isolado e gate com 409 passed;
  cobertura global 87%, `git diff --check` aprovado.
- A8 deep: `APPROVED`, Blocker 0, Major 0, Minor 0 abertos.
- Gate autoritativo: GREEN, exit code 0, 226,8 s; evidência detalhada em
  `quality/v05-s2d-permanent-deletion-result.md`.
- Não ações: sem exclusão em banco de produção, commit, push, tag, release ou
  início de S3 e etapas posteriores.
