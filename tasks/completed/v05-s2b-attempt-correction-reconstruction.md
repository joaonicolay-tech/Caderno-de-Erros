# Task Contract

Status: COMPLETED

## Identification

- Task ID: `V0.5-S2B`
- Product version: `V0.5`
- Stage: Correção estrutural de Attempt: anulação, substituição, reconstrução e reconciliação
- Task type: implementação funcional de lifecycle e integridade
- Size: `L`
- Risk: `high`
- Migration: `EXPECTED`, sujeita à confirmação pelo plano A4 e à auditoria do schema
- A4: obrigatório antes da implementação
- Recommended execution model: GPT-5.6 Sol, reasoning High
- A8 review: deep

## Goal

Implementar o lifecycle seguro de correção estrutural de `Attempt`: anulação,
substituição por novo fato imutável, cadeia acíclica e ponta efetiva, reconstrução
dos derivados e reconciliação de analytics, `ReviewCycle`/`Review`, classificação,
auditoria e recovery compatíveis com `v0.4.4` e S2A.

## Context

- Baseline: `v0.4.4`, V0.5-P0, V0.5-S1 e V0.5-S2A concluídos.
- S2A fornece auditoria funcional append-only, guards de Workspace/integridade,
  checker read-only com 20 checks e recovery isolado; sua funcionalidade deve ser
  preservada.
- A autoridade normativa é `docs/V0.5_S1_Contratos_Normativos_e_Invariantes.md`;
  o plano de release é `tasks/plans/v05-release-execution-plan.md`.
- Nenhuma funcionalidade S2B, S2C ou S2D foi previamente autorizada. S2B é a única
  tarefa atualmente autorizada.

## Acceptance Criteria

- Antes da implementação, existe plano A4 específico e coerente que audita o estado
  real de `Attempt`, schema/migrations, guards, serviços e relações com revisão,
  `Review` e `ErrorClassification`; mapeia grafo de substituição, ponta efetiva,
  reconstrução, Workspace, concorrência, idempotência, upgrade, rollback, recovery,
  checker, testes e gate.
- A anulação explícita exige `Attempt` `VALID`, Workspace correto, motivo obrigatório,
  impacto calculável e revalidação de concorrência; preserva o fato, registra
  instante/motivo, gera `ATTEMPT_VOIDED` sanitizado e reconstrói os derivados
  atomicamente.
- A anulação sem substituição somente ocorre quando o evento não deveria existir;
  o fato permanece visível na timeline e não permanece efetivo em analytics,
  classificação ou scheduling.
- Uma substituição anula a ponta efetiva, cria nova `Attempt` imutável com contexto
  compatível e referência à anulada, reconstrói derivados e gera auditoria
  correlacionada `ATTEMPT_REPLACED`, tudo ou nada.
- A cadeia é acíclica, sem autorreferência, descendência, sucessores paralelos ou
  mais de uma ponta `VALID`; cada anulada possui no máximo uma substituta direta e
  a resolução da Attempt efetiva é centralizada, determinística e sem N+1.
- Referências de substituição e contexto validam Workspace, Question,
  QuestionRevision, Alternative, Review e tipo `INITIAL`/`REVIEW`; referências
  estrangeiras falham sem mutação.
- Reconstrução distingue fatos históricos imutáveis de projeções atuais e reconcilia
  `ReviewCycle`/`Review`, `ErrorClassification`, analytics, drill-down e timeline a
  partir dos fatos efetivos e da policy/version aplicável, sem alterar D1/D7/D14/D30,
  `REV-FIXA-1.0` ou a policy de timezone.
- Attempt `VOIDED` não conta na projeção corrente; quando houver substituição,
  somente a ponta válida conta em `registered`, `performed`, acertos, erros, taxas,
  frequência de categoria e drill-down, sem dupla contagem ou classificação
  inventada.
- `AuditEvent` preserva somente metadados permitidos e sanitizados, com Workspace,
  instante e correlação; não retém enunciado, resposta completa, explicação,
  conteúdo de estudo nem payload da Attempt.
- Falhas simuladas após void, criação da substituta, reconstrução ou auditoria
  restauram o estado anterior; concorrência proporcional bloqueia double void,
  double replacement, ponta obsoleta e reconstrução concorrente. `OperationReceipt`
  só é reutilizado se semanticamente apropriado e sua expiração não muda.
- A necessidade de migration é confirmada após a auditoria. Se necessária, ela é
  aditiva e mínima, com finalidade, defaults, nullability, backfill,
  reversibilidade e risco de upgrade documentados; não criar migration artificial.
- Upgrade cobre `v0.4.4-equivalent → S2A → S2B` (ou fixture equivalente que percorra
  migrations reais) e preserva fatos S2A relevantes; rollback é classificado e não
  presume reverse seguro após fatos reais de correção.
- Backup/restore isolado cobre cenário S2B real e, após restore, reconcilia checker,
  analytics, cadeia, Attempt efetiva e Reviews. O checker permanece read-only e só
  recebe checks mínimos necessários para lifecycle, cardinalidade, ciclos, Workspace,
  ponta efetiva e consistência derivada.
- Testes cobrem lifecycle/cadeias, contextos inválidos, analytics, INITIAL e REVIEW,
  histórico, atomicidade, concorrência, migrations, preservação S2A e recovery;
  regressão focada cobre Attempt, fluxos inicial/review/fila, analytics,
  classificação, S2A, checker e backup/recovery.
- A8 deep é `APPROVED`, sem Blocker/Major, cobrindo schema/migrations, preservação
  histórica, grafo, ponta efetiva, reconciliação, atomicidade, concorrência,
  Workspace, vazamento de auditoria, recovery, regressões S2A e ausência de escopo
  S2C/S2D. O gate final é GREEN, com first pass registrado corretamente, e a
  evidência persistente registra baseline, A4, implementação, testes, A8 e gate.

## Expected Scope

- Domínio, serviços, selectors/policies, migrations aditivas se confirmadas, testes,
  checker read-only, recovery/evidência e documentação estritamente necessários para
  o lifecycle e a reconstrução S2B.
- `PROJECT_STATE.md`, métricas e arquivamento da tarefa somente no encerramento
  comprovado de S2B.

## Protected Scope

- S2C: correção prospectiva de gabarito por nova `QuestionRevision`; não usar
  replacement como atalho para reinterpretar histórico.
- S2D: exclusão permanente, retention e purge; `VOIDED` preserva histórico e não é
  delete.
- UI geral de gestão (S3), domínio (S4/S5), prioridade (S6), export/import (S7),
  event sourcing, infraestrutura distribuída e qualquer mudança de D1/D7/D14/D30,
  `REV-FIXA-1.0` ou timezone policy.
- Categorias pessoais, merge, reagendamento, inclusão manual, `AuditEvent`, os 20
  checks S2A e recovery S6, exceto integração mínima comprovadamente necessária.

## Constraints

- Não apagar, sobrescrever ou ocultar Attempt histórica para simular correção.
- Não espalhar lógica divergente de Attempt efetiva em analytics, Reviews,
  classificações ou templates; não implementar recursão sem proteção contra ciclos e
  profundidade.
- Não inventar classificação automática, não introduzir UI geral e não otimizar
  prematuramente com infraestrutura complexa.
- Migrations, se houver, não podem usar reverse como premissa de recuperação depois
  de existirem correções reais; recomendar/exigir restore quando aplicável.

## Verification

- Executar os testes focados do plano A4, incluindo lifecycle, grafo, reconstrução,
  analytics, Reviews, Workspace, atomicidade, concorrência, upgrade e recovery.
- Executar `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`
  e exigir resultado GREEN observável.
- Executar A8 deep e registrar evidência persistente; executar as verificações S5/S6
  aplicáveis em cópias isoladas, sem repair no checker.

## Documentation Impact

- Plano A4 específico, evidence persistente S2B, classificação de migration/rollback
  e atualização factual de `PROJECT_STATE.md` no encerramento. Atualizar somente a
  documentação exigida pelo comportamento comprovadamente entregue.

## Done When

- O plano A4 foi concluído; o schema mínimo e migrations necessárias foram auditados
  e aplicados; void, replacement, cadeia acíclica, sucessor único, ponta efetiva e
  preservação histórica funcionam.
- Reconstrução, analytics, Reviews e classificações/projeções reconciliam; auditoria
  sanitizada, atomicidade, concorrência, Workspace, upgrade, rollback/recovery e
  checker read-only estão comprovados.
- S2C/S2D permanecem fora; regressão focada, A8 deep e gate final estão GREEN;
  evidence existe; S2B é arquivada e `tasks/current.md` retorna a
  `NO_TASK_AUTHORIZED` no encerramento da etapa.

## Closure Evidence

- Plano A4 fechado antes da implementação:
  `tasks/plans/v05-s2b-attempt-correction-plan.md`.
- Resultado integrado: `quality/v05-s2b-attempt-correction-result.md`.
- Proteção aditiva das migrations:
  `quality/v05-s2b-migrations.json`, sem alterar os manifestos históricos.
- Baseline focado: 118 testes aprovados; regressão focada multicamada: 206
  aprovados; testes próprios cobrem lifecycle, reconstrução, concorrência,
  upgrade e recovery.
- Upgrade real V0.4.4-equivalente → S2A → S2B, reverse anterior a fatos S2B,
  backup/restore isolado, analytics, cadeia e checker foram reconciliados.
- A8 deep: APPROVED, Blocker 0, Major 0, Minor 0 aberto.
- Gate de 2026-09-20: primeira execução GREEN, exit 0; 374 testes aprovados em
  156,28 s; cobertura global 87%; duração total 208,3 s; `pip-audit` sem
  vulnerabilidades conhecidas.

## Non-actions

Não houve correção prospectiva de gabarito/nova revisão S2C,
delete/retention/purge S2D, UI geral, event sourcing, infraestrutura
distribuída, commit, push, tag, release ou autorização/início de V0.5-S2C ou
S2D.
