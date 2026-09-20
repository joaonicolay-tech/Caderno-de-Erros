# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: V0.5-S1
- Product version: V0.5 -- Beta das capacidades V1
- Stage: Fechamento normativo e contratos de invariantes/dados
- Task type: normativa e documental, sem implementação funcional
- Size: M
- Risk: high
- Migration: UNLIKELY; proibida nesta etapa
- Recommended execution model: GPT-5.6 Terra
- Recommended reasoning: High
- A4: checklist, conforme o plano V0.5
- A8: deep

## Goal

Transformar as decisões normativas necessárias para iniciar com segurança a
implementação da V0.5 em contratos explícitos, rastreáveis e testáveis,
desbloqueando o desenho seguro de S2 sem inventar regras críticas durante
migrations ou implementação.

## Context

- Baseline: release `v0.4.4`, V0.5-P0 concluído, sem implementação funcional
  V0.5 iniciada.
- Planejamento autoritativo: `tasks/plans/v05-release-execution-plan.md`.
- Consultar proporcionalmente as fontes normativas necessárias: Roadmap §§8 e
  11; RF-027, 033, 035/036, 057--062, 066, 069--072 e auditoria; RN-027,
  055, 068--084 e regras de correção/exportação; RNF aplicáveis; Modelo de
  Dados, Fluxos, Plano de Testes, ADRs 007/012--014, Architecture v1.0,
  contratos/evidências V0.4 e código/testes diretamente relacionados.
- Preservar as semânticas V0.4 congeladas, especialmente isolamento de
  Workspace, histórico imutável, registered/performed, INITIAL/REVIEW,
  overdue/due/future, D1/D7/D14/D30, `REV-FIXA-1.0`, classificação residual e
  denominadores analytics.

## Acceptance Criteria

- Auditar `V05-OD01`; resolver a política de anulação, exclusão, reconstrução
  e retenção somente quando a fonte a fechar. Se decisão humana bloqueante
  permanecer, registrar pergunta, opções, consequências e recomendação, e não
  encerrar S1 como concluída.
- Auditar `V05-OD02` e resolver somente FL-ABR-001--004 e 009--010 necessários
  aos contratos fundamentais e a S2; registrar matéria exclusivamente de
  exportação como `DEFERRED_TO_S7`.
- Registrar `V05-OD03` como `DEFERRED_TO_S6`, `V05-OD04` como
  `DEFERRED_TO_S5`, `V05-OD05` como `DEFERRED_TO_S7` e `V05-OD06` como
  `DEFERRED_TO_S9`, salvo pré-condição fundamental comprovada.
- Persistir um artefato recuperável por IA com metadata, fontes, decisões e
  `DECISION_STATUS`; contratos de lifecycle, auditoria funcional, invariantes,
  analytics, reviews, Workspace, compatibilidade V0.4.4, constraints de
  migration e itens não resolvidos.
- Definir, sem implementar, contratos para reagendamento, inclusão manual,
  Attempt anulado e substituto, correção de gabarito, exclusão permanente,
  categorias pessoais e auditoria funcional. Distinguir auditoria funcional de
  logs técnicos e não desenhar event sourcing sem requisito.
- Produzir catálogo de invariantes futuros com ID, descrição, entidades,
  estado válido, violação, camada preventiva, necessidade futura no checker S5
  e teste esperado; não alterar o checker nesta etapa.
- Definir para cada operação futura S2 o efeito em fatos válidos, métricas,
  drill-down/reconciliação, ReviewCycle, Review, due date e completion, sem
  reimplementar scheduling ou alterar `AnalyticsService`.
- Especificar constraints para migrations futuras sem fechar schema físico cedo:
  campos candidatos, nullable/default/backfill somente se normativamente
  sustentados, constraints, reversibilidade classificada, backup pré-upgrade e
  fixture de upgrade V0.4.4.
- Reavaliar prospectivamente tamanho, risco, migrations prováveis e
  independência de S2. Preservar S2 como L se honesto; se for XL, decompor o
  plano de modo rastreável antes de qualquer autorização de implementação.
  Reavaliar também a recomendação de modelo para S4 e S10, sem executá-las.
- Concluir A8 deep como `APPROVED`, sem Blocker ou Major, após verificar risco
  destrutivo sem fonte, inferência de decisão humana, reescrita de histórico,
  inconsistência analytics/reviews, retenção, Workspace, decisão precoce de
  schema, tamanho S2 e decisão futura antecipada.

## Expected Scope

- Um artefato documental de contratos S1 em `docs/` ou `tasks/plans/`.
- `tasks/plans/v05-release-execution-plan.md`, somente para registrar decisões
  S1 e eventual decomposição obrigatória de S2.
- `PROJECT_STATE.md`, `quality/operational-execution-metrics.jsonl`,
  `tasks/completed/` e `tasks/current.md` somente no encerramento documental
  legítimo de S1.

## Protected Scope

- Código funcional, models, schema, migrations, backfill, banco e dados
  operacionais.
- Implementação ou autorização de S2 e de qualquer etapa posterior.
- Semânticas V0.4 protegidas, algoritmo de scheduling, `AnalyticsService`,
  checker S5 read-only, backup/restore S6, tags, commits, push e release.

## Constraints

- S1 não implementa funcionalidades, não cria migration, não altera schema e
  não antecipa S2.
- Não inferir silenciosamente regra destrutiva nem substituir decisão humana por
  preferência técnica; pendência bloqueante impede o encerramento da etapa.
- Toda mutação futura prevista deve manter isolamento de Workspace, validação,
  transação, confirmação quando destrutiva, auditabilidade, failure-safe e
  nenhuma mutação parcial.
- Não prometer downgrade automático; backups V0.4.4 são restaurados pelo
  software compatível que os produziu.

## Verification

- Executar `git diff --check` obrigatoriamente.
- Executar testes ou gate somente se a política proporcional os tornar
  necessários por alteração em artefato executável; não alterar código para
  produzir gate verde.
- Realizar A8 deep conforme os critérios de aceite.

## Documentation Impact

Criar o contrato normativo S1 e atualizar apenas os documentos de plano/estado,
métricas e arquivamento que forem exigidos pelo encerramento efetivo da etapa.

## Done When

- Fontes normativas aplicáveis auditadas; OD01 resolvida ou sem decisão humana
  bloqueante; partes de OD02 necessárias a S2 resolvidas; OD03--OD06
  explicitamente deferidas.
- Contratos de lifecycle, auditoria, invariantes, analytics, reviews,
  Workspace, compatibilidade V0.4.4 e constraints de migration persistidos.
- S2 reavaliada e decomposta se efetivamente XL; nenhuma migration, schema ou
  funcionalidade V0.5 criada.
- A8 deep `APPROVED` sem Blocker/Major, `git diff --check` aprovado, métricas
  A7 registradas e estado documental atualizado.
- S1 arquivada por `finish-task`, `tasks/current.md` retornada a
  `NO_TASK_AUTHORIZED`, e S2 permanece não autorizada.
