# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: `V1.0-S1`
- Product version: `V1.0`
- Stage: `S1 — Contratos V1 e decisões de compatibilidade`
- Task type: `contracts / compatibility / documentary stabilization`
- Size: `M`
- Risk: `high`
- Migration: `NO`

## Goal

Congelar os contratos funcionais e de compatibilidade necessários para a V1.0,
incorporando as decisões aprovadas no P0 e determinando versões, fronteiras,
compatibilidade e suporte antes da estabilização funcional da S2.

## Context

- O plano `tasks/plans/v10-release-execution-plan.md` está `COMPLETED / APPROVED`
  e é a autoridade de planejamento para esta etapa.
- P0 resolveu V10-D1 (compatibilidade CEI) e V10-D2 (plataforma, distribuição e
  suporte), além de `RD-ABR-010`. Não reabrir essas decisões.
- A execução deve confirmar o estado real por fontes e evidências proporcionais,
  sem reescrever fatos históricos. Aplicar `docs/A3_Progressive_Disclosure.md`.

## Acceptance Criteria

- Auditar os quatro contratos `REV-FIXA-1.0`, `DOM-HEUR-1.0`, `PRI-HEUR-1.0` e
  `CEI-EXPORT-1.0`, registrando versões, fronteiras e compatibilidade V0.5/V1.
- Consolidar a matriz Windows 11 x64 e browsers conforme V10-D2.
- Identificar findings beta ainda aplicáveis e rastrear CTs, RFs, RNs e RNFs
  pertinentes.
- Manter V10-D1 e V10-D2 sem alterações e sem reescrever histórico.
- Produzir documentação e evidência S1 coerentes com o plano, sem mudança de
  regra, schema ou formato, migration ou feature nova.
- Registrar decisão final `CONTRACTS_FROZEN_FOR_V1` somente após execução e
  revisão formal; não presumir nem antecipar esse estado.

## Expected Scope

- Auditar as fontes normativas e evidências necessárias, incluindo plano V1.0,
  Roadmap §9, Etapa 10 aplicável, requisitos relacionados, contratos e
  documentação V0.5, `docs/CEI_EXPORT_1_0.md`, policies e evidências S7/S8/S9/S10.
- Consultar código e testes somente para confirmar o estado real.
- Criar/atualizar os artefatos documentais de contratos, compatibilidade e
  matriz CT/RF/RN/RNF necessários, registrar evidência S1, atualizar
  `PROJECT_STATE.md` ao concluir e arquivar esta tarefa somente após satisfazer
  os critérios de encerramento.
- Executar revisão documental e validações proporcionais. Não executar suíte
  nova se a etapa permanecer somente documental.

## Protected Scope

- Regras funcionais de revisão; fórmulas Domain e Priority; `CEI-EXPORT-1.0`;
  schema e migrations; dados e fatos históricos.
- S2 e qualquer etapa posterior; findings funcionais, redesign, CSS/JS por
  estética, launcher, instalador, tag e release.

## Constraints

- Preservar V10-D1: `CEI-EXPORT-1.0`, `format_version = 1.0`; produtores V0.5 e
  V1.0 aceitos somente quando compatíveis; validação estrita antes da escrita;
  sem conversão silenciosa, merge ou adaptação automática de schema.
- Preservar V10-D2: Windows 11 x64, uso local individual; Chrome, Edge e Brave
  estáveis vigentes; Firefox estável vigente e imediatamente anterior; Safari
  N/A para a plataforma suportada; GitHub Release estável `v1.0.0` somente após
  promoção e autorização próprias. Launcher/instalador/redesign permanecem
  Pós-V1.
- Se a auditoria identificar necessidade de mudar regra, schema ou formato, ou
  revelar conflito/decisão material nova, parar e registrar
  `HUMAN_DECISION_REQUIRED`.
- A7 recomendado para execução futura: `GPT-6 Luna High`. A8: `standard`.
- Nenhuma tag, release, commit ou push está incluído na S1 por este contrato.

## Verification

- Revisar os quatro contratos, rastreabilidade, matriz de suporte e findings
  aplicáveis; confirmar que V10-D1/V10-D2 foram preservadas.
- Executar validações documentais proporcionais e `git diff --check`.
- Executar verificações específicas registradas pelo plano; sem suíte nova se
  somente documental.
- Gate de produto conforme aplicabilidade definida pela arquitetura e pela
  etapa; registrar evidência observada, sem declarar PASS por expectativa.

## Documentation Impact

Produzir/atualizar os artefatos contratuais e a matriz de compatibilidade e
suporte necessários; registrar resultado S1 em `quality/`, atualizar
`PROJECT_STATE.md` e arquivar o contrato ao concluir. Não editar decisões
congeladas nem o Roadmap.

## Done When

- Os quatro contratos, versões, fronteiras e compatibilidade estiverem
  documentados; matriz de browser/plataforma consolidada; findings e requisitos
  aplicáveis rastreados; e validações/evidências proporcionais registradas.
- Não houver mudança de regra, schema, formato, migration ou feature nova.
- A decisão de congelamento tiver sido formalmente revisada antes de registrar
  `CONTRACTS_FROZEN_FOR_V1`; tarefa concluída arquivada e próximo estado
  registrado sem autorizar automaticamente etapa posterior.

## Closure Record

- Estado: `COMPLETED`; decisão documental: `CONTRACTS_FROZEN_FOR_V1`.
- Evidência: `quality/v10-s1-contracts-compatibility-result.md`.
- Gate: GREEN, exit 0; 505 testes, 86% de cobertura; 2 ResourceWarning registrados.
- `PROJECT_STATE.md` atualizado. Próxima ação possível: V1.0-S2 sob autorização própria.
- Nenhuma regra, schema, formato, migration, feature ou etapa S2+ foi alterada/iniciada.
- Sem commit, push, tag ou release.
