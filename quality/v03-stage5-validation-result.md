# Resultado integrado — V0.3 Etapa 5

## Decisão formal

**V0.3 — NÃO PROMOVIDA.**

O gate técnico E5 terminou GREEN, com exit code 0, mas promoção exige toda a
matriz GREEN. Há um bloqueador P0 de carga (`CT-107`) e uma evidência manual
P1 vinculante ausente (`CT-125`). Nenhum deles foi convertido em PASS por
inferência.

## Ambiente e comandos

- Windows, Python 3.13.15, Django 5.2.17 e SQLite 3.53.1;
- dados exclusivamente sintéticos e bancos de teste/backup descartáveis;
- regressão focada: `uv run --locked pytest tests/test_initial_attempt.py tests/test_review_completion.py tests/test_stage4_learning.py tests/test_learning_foundation.py tests/test_backup_restore.py tests/test_stage5_promotion.py -q` — 85 passed;
- gate autoritativo: `powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\quality.ps1` — exit code 0;
- suite integral: 269 passed; cobertura global 86%; Ruff, mypy, checks Django,
  `makemigrations --check --dry-run`, banco vazio, segredos, `pip-audit`,
  rastreabilidade e `git diff --check` GREEN.

## Matriz de promoção

| CT / critério | Evidência | Status |
|---|---|---|
| `CT-013`–`018`, `021`, `022`, `093`, `100`, `101` | `tests/test_initial_attempt.py` | PASS automático |
| `CT-023`–`029`, `037`–`040`, `042` | `tests/test_review_completion.py` | PASS automático |
| `CT-019`, `030`–`036`, `041` | `tests/test_stage4_learning.py` | PASS automático |
| `CT-073`, `074`, `076`–`080` | `tests/test_learning_foundation.py` | PASS automático |
| `CT-081` | gate: migration em banco vazio; `test_ct081_migration_graph_and_final_schema_are_frozen_without_cycle` | PASS |
| `CT-082` | upgrade isolado `v0.2.0` para V0.3, preservação V0.2 e criação de `Attempt` V0.3 pós-upgrade | PASS |
| Backup/restauração V0.3 | `test_v03_backup_restore_reconciles_learning_relations` e `tests/test_backup_restore.py` | PASS |
| `CT-111` | contenção real SQLite, retry único e sem estado parcial | PASS |
| `CT-123` | `test_e5_integrated_synthetic_flow_completes_cycle_and_resets_review_error` | PASS |
| Fluxo E2E | erro inicial, diagnóstico, D1→D7→D14→D30, conclusão, fila/timeline, erro em D7 e novo D1, acerto inicial sem ciclo | PASS |
| `CT-107` / `BCR-1` | `CT-107` e `RNF-003` fixam as três gravações, o dataset BCR-1 e o teto p95 de 2 s, mas as fontes autoritativas não definem número de amostras, método de cálculo do p95, warm-up, isolamento ou regra de repetição. Sem esses parâmetros não é permitido escolher um executor/dataset nem medir por convenção. | **BLOCKED — P0** |
| `CT-125` manual | sem evidência fornecida de participantes humanos para compreensão do pós-resposta; as verificações automatizadas de interface não a substituem. O roteiro não preenchido está em `quality/v03-ct125-manual-protocol.md`. | **BLOCKED — P1** |

## Integridade e não ações

- Nenhuma migration foi criada ou alterada; o upgrade preservou os dados V0.2
  e a cópia restaurada foi reconciliada;
- o manifesto E5 é exclusivo do gate atual; testes conferem os blobs históricos
  dos manifestos E1, E2, E3 e E4;
- `PROJECT_STATE.md` e `tasks/current.md` não foram atualizados/arquivados,
  pois a promoção não foi aprovada;
- não houve commit, push, tag, release, preparação ou início de V0.4.

## Bloqueador de especificação do `CT-107`

O Plano de Testes e `RNF-003` definem `BCR-1` (10.000 questões, 100.000
tentativas, 100.000 revisões, 200 níveis ativos e dez anos), as operações salvar
questão/tentativa/revisão e o limite p95 de 2 s. Eles também exigem ambiente,
semente e percentis registrados. Contudo, não fixam o volume de execuções,
algoritmo/convenção do p95, warm-up, estado entre amostras, isolamento ou
quantidade/regra de repetições. Esses parâmetros são necessários para que uma
medida seja reproduzível e auditável; escolher um valor localmente contrariaria
a autorização atual. Não houve benchmark, executor/dataset novo, números reais
ou PASS para `CT-107` nesta reavaliação.

## Correção necessária antes de nova avaliação

Uma decisão formal deve primeiro fixar os parâmetros ausentes de `CT-107`.
Então uma nova autorização poderá implementar/executar o gerador e relatório
determinístico de carga `BCR-1`; somente uma medição real poderá decidir
PASS/FAIL. A evidência manual vinculante de `CT-125` também precisa ser
registrada usando o roteiro. Enquanto isso, o repositório não está pronto para
commit final, tag local `v0.3.0` ou push de tag.

## Adendo documental posterior

Em 9 de setembro de 2026, ADR-012 formalizou os parâmetros reprodutíveis do
`BCR-1`/`CT-107` e a amostra manual de `CT-125`. Este adendo não altera o
resultado histórico desta execução: não houve benchmark, sessão humana, PASS
ou promoção. Os dois casos seguem como os únicos bloqueadores da V0.3, agora
executáveis sem ambiguidade.
