# V0.5-S4 — DOM-HEUR-1.0

## Escopo e decisões aprovadas

- Tarefa executada: `V0.5-S4`, autorizada em `tasks/current.md`.
- A4: `tasks/plans/v05-s4-domain-heuristic-plan.md`, concluído. Schema auditado; migration **NO**.
- Decisões humanas de 2026-09-24 registradas no A4: RN-077 (`40`) não se aplica a `C_q`; suficiência estrutural exige INITIAL válida e REVIEW válida posterior; `Eq` usa somente erros REVIEW do ciclo efetivo mais recente (inclui completed, exclui superseded); erro REVIEW reinicia `C_q` em base 20, avançada pela próxima etapa tentada.
- RN-077 permaneceu inalterada. Nenhum novo limiar de confidence ou suficiência foi criado.

## Implementação

- `src/modules/domain/policy.py`: API pura, tipada e versionada `DOM-HEUR-1.0`; `Aq/Pq/Fq/Eq`, `M_q` e teto pós-erro; bandas RN-078; `C_q` com fórmula e atualidade vigentes; estados `NO_DATA`, `INSUFFICIENT`/`PROVISIONAL` e `SUFFICIENT`/`ESTABLISHED`; `DOMINATED` calculado independentemente somente por RN-079. Os limites de `M_q` usam frações exatas para comparações não arredondadas e não dependem do contexto Decimal externo.
- `src/modules/domain/selectors.py`: adaptador read-only, Workspace-scoped, restrito a Question ativa, reutiliza selectors de Attempts e Reviews, seleciona o ciclo efetivo vigente e registra fatos excluídos. Número de consultas é constante por avaliação de uma Question.
- Agregação hierárquica matemática pura RN-074/075 opera em IDs distintos de Question, sem consulta/agregação operacional ou integração S5.
- Não houve persistência, migration, campo, snapshot, UI, dashboard, Priority ou reopening operacional.

## Testes e revisão

- `tests/test_domain_policy.py` e `tests/test_domain_evidence.py`: **32 passed** após a revisão final; fórmula, limites, separação de confidence/suficiência, ciclo selecionado, completed/superseded, `C_q` após erro, RN-079, explicações e agregação, inclusive ausência de `C_q` hierárquico.
- Regressão selecionada S2B/S2C/S2D/Attempts/Reviews/analytics/classificações/taxonomia: **191 passed** antes do ajuste final da agregação; os testes focados e a suíte completa foram repetidos depois do ajuste.
- A8 deep: **APPROVED**, Blocker 0, Major 0, Minor 0 abertos. Revisão cobriu fidelidade normativa, fatos/replacements, revisão histórica, ausência de difficulty e de sinais não autorizados, suficiência, thresholds, determinismo, evidências explicativas, agregação, isolamento/consultas, migration e limites S4.
- `git diff --check`: exit 0.

## Gate autoritativo

Comando: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

- Tentativa 1: **GREEN**, exit code **0**, 454 passed. A8 subsequente identificou que `C_h` poderia omitir silenciosamente uma Question sem `C_q`; agregação corrigida para deixar cobertura indisponível quando incompleta.
- Tentativa 2, final: **GREEN**, exit code **0**, **455 passed** em 178.44 s; cobertura total **87%**. Nenhuma tentativa de gate RED.
- Perfis, migração de banco vazio, `makemigrations --check --dry-run` (No changes detected), formatação, Ruff, mypy (174 arquivos), cobertura de domínio, detect-secrets e pip-audit aprovados. Pip-audit: `No known vulnerabilities found`.
- Duração total observada no gate final: **217.8 s**. Permaneceram dois `ResourceWarning` de conexão SQLite em `tests/test_v05_s2d.py`; sem falhas.
- Duração da sessão de trabalho e deltas de quotas A7: `unknown`; não estimados. Registro A7 em `quality/operational-execution-metrics.jsonl`.

## Encerramento

S4 concluída. `PROJECT_STATE.md` atualizado; contrato arquivado em `tasks/completed/v05-s4-domain-heuristic.md`; `tasks/current.md` retorna a `NO_TASK_AUTHORIZED`. Nenhuma etapa posterior foi antecipada ou iniciada. Sem commit, push, tag ou release.
