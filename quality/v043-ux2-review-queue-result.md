# V0.4.3-UX2 — evidência de encerramento

## Decisões e escopo

- Os indicadores Atrasadas, Devidas hoje e Futuras passam a abrir a Fila existente
  com `section=OVERDUE|DUE|FUTURE`. Mesmo o zero é link semântico e leva ao
  empty state específico; Concluídas hoje permanece sem destino, pois não é
  uma pendência.
- A fonte do conjunto acionável é a `ReviewStatusPolicy` já consumida pela
  Fila: `OVERDUE` e `DUE`; `FUTURE` é excluída. O CTA abre a primeira revisão
  na ordenação já aplicada pela Fila (`current_due_date`, `created_at`, `id`).
- O texto do enunciado usa clamp visual de duas linhas. O valor integral fica
  no DOM e na revisão; disciplina/assunto ausentes continuam omitidos.

## Evidências

- Testes focados: 29 aprovados em `test_dashboard.py`, `test_interface.py` e
  `test_stage4_learning.py`, incluindo drill-down, zero, CTA, futura excluída,
  Workspace e query count constante.
- Manual local: dashboard com 0 atrasadas, 0 devidas e 7 futuras; links com
  nomes acessíveis, drill-down de Futuras, aviso sem CTA quando só há futuras,
  e fila legível a 360 px. Zoom 200% não foi observado e não é alegado.
- Review A8 padrão: **APPROVED**, sem Blocker ou Major. A revisão confirmou
  sem alteração de policy/scheduling/analytics/schema, sem N+1 novo, sem links
  aninhados e com foco/teclado nativos dos links.
- `git diff --check`: aprovado. Gate autoritativo: **GREEN**, exit code 0,
  337 testes aprovados em 85,28 s, 88% de cobertura; migrations, formatador,
  Ruff, mypy, detect-secrets e pip-audit aprovados. A primeira execução ficou
  inconclusiva somente por `pip-audit` com WinError 10013 de rede/sandbox.

Não houve migration, alteração de schema, tag, commit, push, release ou início
de V0.5.
