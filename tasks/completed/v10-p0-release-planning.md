# Task Contract

Status: COMPLETED

## Identification

- Task ID: `V1.0-P0`
- Product version: `V1.0`
- Stage: `P0 — Planejamento executável`
- Phase: `COMPLETED`
- Task type: `planning / architecture / scope audit / execution decomposition`
- Size: `L`
- Risk: `high`
- Migration: `NO`

## Planning Progress

- O plano executável `tasks/plans/v10-release-execution-plan.md` foi aprovado
  humanamente em 2026-09-28 e concluído.
- `V10-D1`, `V10-D2` e `RD-ABR-010` estão resolvidas no nível do planejamento;
  as recomendações A7/A8 e correções menores foram incorporadas.
- O encerramento está registrado em `quality/v10-p0-planning-result.md`.
  Nenhum estágio S1+ foi iniciado ou autorizado.

## Goal

Auditar o estado real pós-V0.5 e produzir, em execução posterior, um plano
executável completo da V1.0, fiel ao Roadmap e aos documentos normativos
aprovados. V1.0 prepara a beta V0.5 para uso pessoal regular por estabilização,
compatibilidade, validação e preparação de release; não adiciona uma nova
camada de funcionalidades.

## Context

- Baseline informada na autorização: branch `main`, `HEAD` e `origin/main`
  `c542b4fb6783f5488bece21542199a88303ee013`; V0.5 `PROMOTION_APPROVED`, S10
  `COMPLETED`, tag anotada publicada `v0.5.0` e reconciliação documental
  pós-release concluída. A execução deve confirmar o estado vivo e reconciliá-lo
  com `PROJECT_STATE.md` e o Roadmap antes de tirar conclusões.
- V1.0 ainda não foi implementada. A auditoria deve comparar documentação
  aprovada com o código, testes e evidências reais, sem presumir presença ou
  ausência de capacidades a partir do Roadmap.
- Aplicar `docs/A3_Progressive_Disclosure.md` e consultar as fontes obrigatórias
  abaixo de forma proporcional, ampliando a inspeção de código/testes apenas
  para sustentar conclusões.

## Acceptance Criteria

- Produzir plano versionado `tasks/plans/v10-release-execution-plan.md` com
  baseline confirmada, escopo oficial, estado real e gaps V0.5→V1.0 apoiados por
  evidência rastreável.
- Decompor o trabalho em estágios `S1...Sn` independentes e ordenados, com
  dependências, tamanho, risco, migrations quando aplicável, testes, critérios
  de aceite, gates, checkpoints, política de findings, A7, A8, recovery/rollback,
  documentação e critérios explícitos de parada para cada estágio.
- Definir critérios de promoção, piloto local real controlado e preparação de
  release V1.0 sem declarar critérios satisfeitos por expectativa.
- Preservar as exclusões de produto e registrar decisões em aberto sem inventar
  requisitos, limiares ou decisões humanas.
- Não autorizar nenhum estágio S1+ como consequência deste P0.

## Required Sources

- `AGENTS.md`, `PROJECT_STATE.md`, `tasks/current.md` e o Roadmap aprovado,
  Etapa 9.
- Plano de Testes, Etapa 10; requisitos funcionais e não funcionais aplicáveis
  à V1; Regras de Negócio; SDD; Modelo de Dados; Fluxos; ADRs aplicáveis.
- Plano e evidências finais da V0.5, incluindo
  `quality/v05-s10-controlled-pilot-result.md` e o contrato S10 arquivado.
- Documentação de upgrade, restore e CEI; código e testes somente para verificar
  o estado real e fundamentar gaps.

## Expected Scope

- Criar `tasks/plans/v10-release-execution-plan.md`.
- Atualizar `PROJECT_STATE.md` e arquivar o contrato em
  `tasks/completed/` somente na conclusão comprovada do P0; retornar
  `tasks/current.md` a `NO_TASK_AUTHORIZED`.
- Alterações de código, testes funcionais, migrations e alterações no Roadmap
  não fazem parte do P0.

## Product Scope and Protected Scope

- V1.0 cobre estabilização, compatibilidade, testes, segurança, desempenho,
  acessibilidade, usabilidade, documentação, validação de atualização e
  recuperação, piloto final e preparação de release.
- O plano deverá tratar, dentro desse escopo, findings de piloto/beta por
  severidade; congelamento de `CEI-EXPORT-1.0`, `REV-FIXA-1.0`, `DOM-HEUR-1.0` e
  `PRI-HEUR-1.0`; testes funcionais e regressão; banco, segurança, desempenho,
  acessibilidade e usabilidade; upgrade `V0.4 → V0.5 → V1.0`; backup,
  rollback/recovery documentado e restauração periódica; mensagens de erro e
  recuperação; otimização somente de gargalos medidos; remoção de feature flags
  temporárias quando aplicável; dívida bloqueante; documentação de instalação,
  uso, atualização, backup, restauração e troubleshooting; changelog, release
  notes e piloto local real controlado.
- Permanecem fora: IA assistiva, revisão adaptativa, API pública, integrações
  externas, multiusuário, hospedagem pública, PWA, OCR, anexos, gamificação,
  redesign visual completo, nova identidade visual, novo design system,
  launcher/executável de um clique e instalador simplificado. Esses itens foram
  adiados para Pós-V1.
- Não criar V0.6, V0.7, V0.8 ou V0.9. A sequência aprovada é
  `V0.1 → V0.2 → V0.3 → V0.4 → V0.5 → V1.0 → Pós-V1`.

## Constraints

- Planejamento somente. Nenhuma implementação funcional V1.0, estágio S1+,
  bugfix, migration ou teste novo é autorizado por este P0.
- Não editar o Roadmap nem adicionar funcionalidades fora do escopo oficial.
- Não inferir PASS, gaps, threshold, decisão humana ou capacidade sem evidência
  direta. Registrar divergências materiais e decisões pendentes explicitamente.
- Commit, push, tag e release não estão autorizados.

## Verification

- Na execução do P0, verificar baseline e working tree antes de planejar;
  reconciliar drift material antes de depender dele.
- Fazer revisão proporcional do plano quanto à fidelidade ao Roadmap,
  rastreabilidade de evidências, limites de escopo, decomposição, dependências,
  riscos, gates e critérios de parada.
- Executar `git diff --check` e verificações documentais aplicáveis. Gate de
  qualidade só se exigido pela arquitetura aplicável ao fechamento documental;
  nunca apresentar auditoria inconclusiva como PASS.

## Documentation Impact

- Criar `tasks/plans/v10-release-execution-plan.md` durante a execução do P0.
- Na conclusão comprovada, atualizar `PROJECT_STATE.md`, arquivar o contrato e
  restaurar `tasks/current.md` para `NO_TASK_AUTHORIZED`.
- Não editar o Roadmap neste P0.

## Done When

- O plano executável cobre baseline, auditoria de escopo e gaps, estágios,
  dependências, migrations, testes, aceitação, gates, checkpoints, findings,
  promoção, piloto, release, A7/A8, recovery/rollback, documentação e parada,
  com evidência rastreável e decisões em aberto explicitadas.
- O P0 está documentado e arquivado, `PROJECT_STATE.md` reflete a conclusão do
  planejamento sem afirmar implementação V1.0, e `tasks/current.md` retorna a
  `NO_TASK_AUTHORIZED`.
- Nenhum estágio S1+, implementação V1.0, commit, push, tag ou release foi
  executado ou autorizado por este P0.

## Closure Record

- Decisão humana final do plano: `APPROVED`; o plano está `COMPLETED` e aprovado
  como autoridade de planejamento para os estágios futuros, sem autorizar S1.
- Evidência de encerramento: `quality/v10-p0-planning-result.md`.
- Gate autoritativo: GREEN, exit code 0; 505 testes existentes passaram, 86%
  de cobertura, dois `ResourceWarning` observados. Demais checks estão
  registrados na evidência.
- Sem implementação funcional V1.0, migration ou novo teste funcional; sem
  piloto, promoção V1, tag/release V1, commit ou push.
- Próxima ação permitida somente após autorização independente: `V1.0-S1`.
