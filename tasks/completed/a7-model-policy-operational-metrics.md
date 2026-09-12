# A7 — Política de modelos, reasoning e métricas operacionais

Status final: concluída e arquivada em 12 de setembro de 2026.

## Contrato executado

- Task ID: A7
- Product version: V0.3
- Stage: Stage 9
- Task type: operational architecture / model policy / telemetry
- Size: M
- Risk: low

O objetivo autorizado foi formalizar uma política inicial e calibrável para
modelo, reasoning e escalonamento baseada em dificuldade, risco e benchmarks
reais, e estabelecer métricas operacionais leves, versionáveis e honestas.
O escopo cobriu somente política, reasoning, escalonamento, persistência leve
de métricas, integração proporcional e documentação. Permaneceram protegidos
código Django, migrations, regras de negócio, baseline V0.3, V0.4, A8+,
configuração pessoal, `.codex/config.toml`, novas Skills e o gate.

## Resultado

`docs/A7_Politica_de_Modelos_Reasoning_Escalonamento_e_Metricas.md` é a fonte
durável da política. Ela separa modelo de reasoning, aplica o princípio do
modelo menos dispendioso plausivelmente suficiente, determina escalonamento
por evidência e explicita que tamanho não escolhe modelo sozinho. Os seis
casos conceituais exigidos estão incluídos sem executar tarefas reais.

`quality/operational-execution-metrics.jsonl` é o registro canônico JSONL
append-friendly. Inclui os benchmarks A1–A6 com proveniência, mantém A4 como
desconhecido onde faltam dados e separa incidentes de infraestrutura e de
contrato/processo de falhas de modelo. Não há quota, duração ou precisão
inventadas; quotas informadas manualmente são identificadas como tal.

Não foi necessário alterar as quatro Skills: elas já referenciam fontes de
verdade e o fluxo de encerramento sem duplicar política ou criar telemetria
complexa. `docs/README.md` passou a indexar a nova fonte.

## Incidentes classificados

- O incidente ACL/sandbox anterior à A7 é `infrastructure`, não falha de
  modelo, A7 ou retrabalho funcional.
- O bootstrap administrativo contraditório é `scope_contract`, não falha de
  modelo.
- A primeira tentativa local do gate ficou inconclusiva somente no `pip-audit`
  por `WinError 10013`; a repetição em rede autorizada foi GREEN. Isso é
  infraestrutura, não retrabalho funcional.

## Verificação e encerramento

- Validação JSONL: 8 registros iniciais válidos antes do fechamento; o registro
  final A7 foi acrescentado após o gate com fatos conhecidos.
- `git diff --check`: aprovado antes do gate e após o fechamento.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`:
  GREEN, exit code 0, 280 testes aprovados, 87% de cobertura, migrations,
  Ruff, mypy, detect-secrets e `pip-audit` aprovados; duração 87,3 s na
  execução elegível.

## Escopo preservado e próximo estado

Nenhuma funcionalidade Django, teste funcional, migration, gate, configuração
pessoal, commit, push, tag ou release foi alterado/criado. A8 e V0.4 não foram
iniciadas. A escolha de modelo/reasoning desta execução foi registrada como
instrução fornecida pelo usuário; duração e quota da A7 permanecem
`unknown`. `tasks/current.md` retorna ao estado sem tarefa autorizada.
