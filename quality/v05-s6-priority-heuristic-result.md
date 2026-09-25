# V0.5-S6 — PRI-HEUR-1.0 e recomendação explicável

## Baseline, A4 e decisões

- `main`; `HEAD = origin/main = 43f7a38c2e78d31ef10226beb8d99af63271a2d0` no início. A única alteração preexistente era `tasks/current.md` com autorização S6; S5 está no commit baseline. `git diff --check` inicial exit 0.
- Modelo da execução indicado no contrato: GPT-6 Sol / Medium. Variante e nível efetivos não foram confirmados por telemetria nesta sessão; duração total e quotas: `unknown`.
- A4 concluído em `tasks/plans/v05-s6-priority-heuristic-plan.md` antes da primeira edição funcional. Auditoria das fontes RN-081–084, RN-097–100, RN-ABR-003, RF-062, FL-017, PT-ABR-008, OD03, código/migrations S5, taxonomy, Questions, Attempts, Reviews, analytics, Workspace, UI e testes. Granularidade: Subject. Migration: **NO**, `makemigrations --check --dry-run` observou `No changes detected`.
- `V05-OD03`, `PT-ABR-008` e parte operacional de `RN-ABR-003` fechados pelas decisões humanas novas de 2026-09-24 registradas no A4. Não foram atribuídas aos textos normativos originais. Nenhuma outra decisão normativa foi inventada.

## Implementação e fidelidade

- `src/modules/priority/policy.py`: núcleo puro tipado, `PRI-HEUR-1.0`, frações exatas para cálculo/ordem e peso 40/30/20/10. W usa `100 - M_h` de S5; O usa proporção de Questions ativas distintas em atraso; R e D usam fatos por Question distinta. Score só existe quando os quatro fatores e `C_h >= 40` estão disponíveis. `C_h < 40`, confidence ausente, domínio ausente ou R/D insuficientes produzem `COLLECT_MORE_EVIDENCE` com reason codes; zero observado permanece distinto de indisponível. Empate exato: `subject_id ASC`, depois de score integral DESC. Arredondamento só na apresentação.
- `src/modules/priority/services.py`: seleciona Subjects e Questions ativas do Workspace, consome `current_domains`/`aggregate_hierarchy` S5 em lote, `valid_attempts` efetivas, `eligible_reviews`/`ReviewStatusPolicy` e data civil do Workspace. `occurred_at` é convertido para o fuso atual do Workspace antes de classificar as janelas. R: 90 dias inclusivos, ≥2 REVIEWs por Question elegível, ≥2 erros para recorrência e ≥3 Questions elegíveis. D: janelas recentes/baseline de 30 dias não sobrepostas, média de taxas por Question com peso igual e ≥3 comparáveis. Nenhum fato histórico é reinterpretado após correção de gabarito.
- UI mínima em `/prioridades/`, com link no painel: ranking, score, W/O/R/D, confiança/evidência, explicação, coleta de evidência e estado vazio. Link de Subject e fila operacional permanecem escolhas do usuário. GET não persiste score, snapshot, plano, Review, ReviewCycle, MasteryStateEvent ou mutação de scheduling. A Review Queue existente continua independente.
- Sem novo schema, migration, cache persistente, snapshot, campo em Subject, scheduler ou mudança das policies Domain/Mastery/Review.

## Testes e performance

- Vetores puros independentes: fórmula, W 0/intermediário/100, confiança 39.99/40, falta de W/C/R/D, zero observado, Question distinta, média D com peso igual, melhora D=0, explicações, comparação não arredondada e desempate por UUID.
- Integração: S5, UI, read-only, Workspace estranho, fila overdue para assunto insuficiente, estado vazio, janelas inclusivas, S2B void, S2C gabarito prospectivo e archive S2D. Regressões S4/S5/analytics incluídas.
- Testes focados e regressões selecionadas antes do primeiro gate: **65 passed**. Após ajuste da navegação: **14 passed** focados. Benchmark proporcional da lista: **4 Subjects / 12 Questions / 14 queries**, via `CaptureQueriesContext`, com limite de 18 no teste; resultado sem crescimento por Subject via chamadas unitárias S5.

## A8 deep

- Revisão da autorização, A4/OD03, fatores W/O/R/D, fronteiras de data local, precisão e desempate, ausência de evidência, explicações, isolamento Workspace, S5 batching, S2B/S2C/S2D, leitura sem escrita, Review Queue separada, UI/teclado/foco/labels, schema e exclusões S7+.
- Finding Major de regressão no primeiro gate: teste de navegação com conjunto exato de links não contemplava a nova rota; expectativa atualizada para a capacidade S6 e teste repetido. Nenhum requisito protegido precisou mudar.
- **APPROVED após correção**; Blocker 0, Major 0, Minor 0 abertos. A medição adicional de 4 Subjects foi acrescentada após o segundo gate e exige gate final repetido.

## Gate autoritativo

Comando: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.

1. Tentativa 1 **RED**, exit 1: 485 passed, 1 failed em `tests/test_interface.py` pela nova rota `/prioridades/` ausente do conjunto esperado. Migrações, formatação, Ruff e mypy haviam passado. Correção: incluir a rota no teste de navegação.
2. Tentativa 2 **GREEN**, exit 0: 486 passed, 87% de cobertura; banco vazio e `makemigrations --check`, formatação, Ruff, mypy (184 arquivos), cobertura mínima, detect-secrets e `pip-audit` aprovados. `pip-audit`: `No known vulnerabilities found`. Duração observada: 265,5 s. Dois `ResourceWarning` de SQLite em teste S3 existente, sem falha.
3. Tentativa final após benchmark adicional: **GREEN**, exit 0, **487 passed** em 213,29 s, **87%** de cobertura global; perfis, migrações em banco vazio, `makemigrations --check --dry-run`, formatação, Ruff, mypy (184 arquivos), cobertura mínima, detect-secrets e pip-audit aprovados. `No known vulnerabilities found`. Duração observada do gate: **257 s**. Dois `ResourceWarning` de conexões SQLite em teste S3 existente, sem falha.

`gate_first_pass=false`. A8 deep `APPROVED`, Blocker 0/Major 0, gate final GREEN; sem P0/P1 aplicável aberto. `PROJECT_STATE.md` atualizado e S6 arquivada após esta evidência. Sem commit, push, tag, release ou início de S7+.
