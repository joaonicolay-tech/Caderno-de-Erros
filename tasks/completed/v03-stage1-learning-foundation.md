# V0.3 — Etapa 1 — Fundação de Aprendizagem: Schema, Constraints e Políticas Puras

## Situação

Concluída e arquivada em 8 de setembro de 2026, com gate autoritativo GREEN,
exit code 0.

## Escopo entregue

- seis entidades autorizadas: `Attempt`, `OperationReceipt`,
  `ErrorClassification`, `ErrorClassificationRevision`, `ReviewCycle` e
  `Review`;
- quatro migrations ordenadas, sem ciclo e sem alteração das migrations
  protegidas V0.1/V0.2;
- FKs `PROTECT`, `CHECK`s, índices, unicidades parciais, isolamento por
  Workspace e guardas de integridade intertabelas;
- fatos de tentativa imutáveis, histórico de classificação append-only e
  recibos minimizados/idempotentes com retenção mínima;
- `ReviewSchedulePolicy` e `ReviewStatusPolicy` puras, determinísticas e com
  `Clock`/`Calendar` injetáveis;
- timeout/retry SQLite congelados e prova de contenção sem estado parcial;
- `CT-073`, `CT-074`, `CT-076`–`CT-082`, instalação limpa, upgrade desde
  `v0.2.0`, backup e restauração aprovados.

## Evidência

Consultar `quality/v03-stage1-learning-foundation-result.md`.

## Resultado

- 209 testes aprovados;
- 86% de cobertura global e mínimos de 80% por módulo crítico aprovados;
- nenhum P0/P1 aplicável aberto;
- nenhuma migration V0.1/V0.2 alterada;
- nenhuma interface, fluxo ou capacidade da Etapa 2+ implementada;
- nenhum commit, push, tag ou release executado.

## Próximo estado

Não há tarefa autorizada. A Etapa 2 não foi preparada nem iniciada e exige
autorização formal futura em nova `tasks/current.md` e novo chat.
