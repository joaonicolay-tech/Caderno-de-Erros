# Resultado integrado — V0.3 Etapa 5

## Decisão formal histórica pré-ADR-013

**V0.3 — NÃO PROMOVIDA.**

O gate técnico E5 terminou GREEN, com exit code 0, mas promoção exige toda a
matriz GREEN. Há um bloqueador P0 de carga (`CT-107`) e uma evidência manual
P1 vinculante ausente (`CT-125`). Nenhum deles foi convertido em PASS por
inferência.

## Adendo BCR-1/CT-107 - 9 de setembro de 2026

`CT-107` recebeu **PASS** por execucao real do executor reproduzivel
`scripts/run_bcr1.py`. O artefato completo, com cada uma das 100 amostras por
operacao e por execucao, esta em `quality/v03-bcr1-result.json`.

- Ambiente: Windows 11 10.0.26200, Python 3.13.15, Django 5.2.17 e SQLite
  3.53.1; CPU AMD64 Family 23 Model 160, 8 nucleos logicos; RAM 16 GiB;
  armazenamento em `C:\\src\\Projeto`, 86.75 GiB livres (tipo indisponivel).
- Perfil Django `development`, com SQLite dedicado por execucao; modo
  sequencial, sem concorrencia artificial. Migrations, bootstrap e dataset
  ficaram fora da medicao, e cada banco foi removido apos capturar o resultado.
- Dataset sintetico deterministico, seed `20260909`: 10.000 questoes, 100.000
  tentativas, 100.000 Reviews, 200 disciplinas/assuntos/subassuntos ativos por
  nivel e datas de 2016-09-09 a 2026-09-06; sem dados pessoais.
- Operacoes reais: `create_active`, `AttemptService.confirm` e
  `CompleteReviewService.complete_review`; 20 warm-ups excluidos, 100 amostras
  medidas e tres execucoes independentes por operacao. p95 nearest-rank:
  amostras ordenadas na posicao `ceil(0.95 x N)`; limite 2.000000 s.

| Execucao | Questao p95/max (s) | Tentativa p95/max (s) | Revisao p95/max (s) | Decisao |
|---|---:|---:|---:|---|
| 1 | 0.021407 / 0.025436 | 0.035050 / 0.066249 | 0.052480 / 0.107080 | PASS |
| 2 | 0.019754 / 0.023697 | 0.019637 / 0.056831 | 0.078263 / 0.167723 | PASS |
| 3 | 0.019682 / 0.035362 | 0.031583 / 0.142784 | 0.040550 / 0.086532 | PASS |

Todas as nove combinacoes ficaram em ou abaixo de 2 s: **CT-107/BCR-1: PASS**.
`CT-125` nao foi executado, preenchido ou inferido; permanece BLOCKED - P1,
aguardando execucao humana. V0.3 nao foi promovida e E5 continua aberta.

## Adendo de validação UX - 10 de setembro de 2026

Foi informado que uma sessão humana real de `CT-125` ocorreu com 10
participantes e que 9 demonstraram compreensão do próximo passo. O recorte
quantitativo informado atende ao limiar de 90%, mas os registros individuais
reais P01--P10, o ambiente e os achados ainda não foram incorporados a este
repositório. Portanto, este documento **não declara CT-125 PASS** e o caso
permanece PENDENTE/BLOCKED até que a evidência individual prevista no protocolo
seja preservada, sem inferir ou inventar respostas humanas.

Os achados de UX reportados nesta execução foram tratados antes de nova
avaliação: pós-revisão sem UUID técnico e com retorno à fila; tentativa inicial
já registrada com navegação útil em vez de código técnico; pré-requisitos do
cadastro explicitados; e identificação contextual de Explicação, Pegadinha e
Observações após o feedback autorizado. A correção não altera regras de
aprendizagem, migrations ou a decisão de promoção.

## Ambiente e comandos

- Windows, Python 3.13.15, Django 5.2.17 e SQLite 3.53.1;
- dados exclusivamente sintéticos e bancos de teste/backup descartáveis;
- regressão focada: `uv run --locked pytest tests/test_initial_attempt.py tests/test_review_completion.py tests/test_stage4_learning.py tests/test_learning_foundation.py tests/test_backup_restore.py tests/test_stage5_promotion.py -q` — 85 passed;
- gate autoritativo: `powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\quality.ps1` — exit code 0;
- suite integral: 269 passed; cobertura global 86%; Ruff, mypy, checks Django,
  `makemigrations --check --dry-run`, banco vazio, segredos, `pip-audit`,
  rastreabilidade e `git diff --check` GREEN.

## Matriz de promoção histórica pré-ADR-013

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
## Fechamento final pós-ADR-013 — 10 de setembro de 2026

### Decisão

**V0.3 está formalmente PROMOVIDA.** A decisão considera o candidato final
ADR-013, não a matriz histórica deste documento. Nenhum P0/P1 aplicável
permanece aberto.

### CT-107 e CT-125

- `CT-107` / BCR-1: **PASS** por execução real registrada em
  `quality/v03-bcr1-result.json`: três execuções independentes, 20 warm-ups,
  100 amostras por operação, p95 nearest-rank e todas as nove medições em até
  2 s.
- `CT-125`: **PASS — 9/10 (90%)**. Os dez registros individuais históricos
  estão preservados em `quality/v03-ct125-manual-protocol.md`.
- P07–P09: compreensão parcial dos termos, registrada como achado sem
  inventar observações adicionais.
- P10: **FAIL real**; não classificou a causa, não explicou o próximo passo,
  não compreendeu o feedback e precisou de ajuda crítica.
- Não houve nova sessão humana pós-ADR-013. ADR-014 aceita de modo limitado a
  evidência histórica porque ADR-013 não mudou o objeto humano de CT-125; a
  validação manual funcional posterior pelo responsável pelo produto não é
  apresentada como amostra de participantes.

### Regressão, migrations e gate final

- Candidato ADR-013: 280 testes aprovados, 87% de cobertura global e testes
  focais de ativação/regressão aprovados, conforme
  `quality/v03-adr013-activation-review-result.md`.
- Migrations: `reviews.0002_activation_review_cycle` foi validada pelo gate;
  não cria ciclos retroativos para questões `ACTIVE` históricas. As migrations
  E1 e os manifestos E1–E4 permanecem protegidos.
- Gate final desta promoção: `powershell -NoProfile -ExecutionPolicy Bypass
  -File .\scripts\quality.ps1` — **GREEN, exit code 0**.
- `git diff --check`: aprovado.

### Integridade e não ações

Nenhuma funcionalidade, migration, política D1/D7/D14/D30 ou reativação foi
implementada neste fechamento. Nenhuma evidência histórica foi apagada. Não
houve commit, tag, push ou release. V0.4 não foi iniciada.
