# V0.4-S5 — Resultado de integridade operacional

- Resultado: **GREEN**.
- Checker: 17 invariantes; conexão SQLite `mode=ro`; 18 consultas constantes
  por execução; nenhuma capacidade de repair.
- Testes específicos: 10 aprovados em 3,93 s.
- Regressões relacionadas: 153 aprovadas em 36,48 s; cobertura focada 90%
  (checker 88%, comando 95%).
- Teste manual seguro: exit 0, saída `HEALTHY`, hash SHA-256 do SQLite
  descartável inalterado antes/depois.
- Review A8 profundo: `APPROVED`, sem Blocker ou Major aberto.
- `git diff --check`: aprovado.
- Gate autoritativo: exit 0; 302 testes aprovados em 62,55 s; 87% de cobertura
  global; migrations, formatação, Ruff, mypy, detect-secrets, cobertura de
  domínio e pip-audit aprovados; duração total 91,5 s.
- Incidente: a primeira execução do gate ficou inconclusiva no pip-audit por
  `WinError 10013` do sandbox. A repetição autorizada fora do sandbox concluiu a
  auditoria sem vulnerabilidades conhecidas. Não houve falha funcional.
- Escopo preservado: nenhuma migration/schema, repair, alteração de S1-S4,
  execução de S6-S9, commit, push, tag ou release.
