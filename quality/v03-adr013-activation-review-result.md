# V0.3 — Correção ADR-013: resultado de implementação

Data: 10 de setembro de 2026

## Resultado

Implementada a criação atômica do ciclo de revisão e da D1 na transição efetiva
de uma questão para `ACTIVE`, conforme ADR-013. Não há `Attempt` artificial.

- Migration: `reviews.0002_activation_review_cycle`.
- `ReviewCycle` aceita a origem `QUESTION_ACTIVATION`, sem `origin_attempt`, e
  preserva `origin_question_revision`; `Review.scheduled_from_attempt` é nulo
  apenas na D1 inaugural de ativação.
- `create_active`, `complete_draft` e `save_revision(..., activate=True)`
  usam `QuestionActivationReviewService` na mesma transação lógica.
- INITIAL correta e incorreta preservam o ciclo/D1 existente; somente erro de
  Review reinicia D1. Arquivamento, fila e timeline seguem operando com a
  âncora nula de ativação.
- Os literais de pós-acerto foram corrigidos para UTF-8 e agora informam que a
  questão faz parte do ciclo de revisão.

## Evidência automatizada

- Testes focais: 94 aprovados.
- Regressão total: 280 aprovados.
- Cobertura global: 87%.
- `git diff --check`: aprovado.
- Gate autoritativo: GREEN, exit code 0, 89,9 s; checks, migration em banco
  vazio, Ruff, mypy, cobertura, detect-secrets e pip-audit aprovados.

## Limites preservados

Nenhum ciclo foi criado retroativamente para questões ACTIVE históricas. Não
houve reativação, capacidade V0.4, promoção, commit, push, tag ou release.

CT-125 preserva a evidência humana histórica de 9/10 e continua PENDENTE de
reteste no candidato corrigido; V0.3 permanece não promovida.
