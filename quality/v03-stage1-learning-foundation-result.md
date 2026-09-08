# V0.3 — Etapa 1 — Resultado da Fundação de Aprendizagem

| Campo | Resultado |
|---|---|
| Data | 8 de setembro de 2026 |
| Decisão | **GREEN — Etapa 1 concluída** |
| Baseline protegida | `v0.2.0` (`a756b6d`) |
| Gate autoritativo | GREEN — exit code 0, 62,4 s |
| Testes | 209 aprovados |
| Coverage global | 86% |
| Cobertura crítica | Todos os módulos de domínio/regra listados no manifesto acima de 80% |
| P0/P1 aberto | Nenhum |

## Entrega

Foram materializadas somente as seis entidades autorizadas:

- `attempts`: `Attempt` e `OperationReceipt`;
- `errors`: `ErrorClassification` e `ErrorClassificationRevision`, preservando
  `ErrorCategory`;
- `reviews`: `ReviewCycle` e `Review`.

Não foram criados `AttemptService`, `CompleteReviewService`, view, form,
template, contexto transitório, fila, timeline, analytics, snapshot,
`AuditEvent`, `ReviewScheduleChange`, `SavedFilter` ou entidade adiada.

## Migrations e baseline

Ordem final comprovada em banco vazio:

1. `attempts/0001_learning_foundation`, dependente de `accounts/0001_initial`
   e `questions/0002_question_catalog`;
2. `errors/0002_learning_classification`, dependente de
   `errors/0001_initial` e `attempts/0001_learning_foundation`, com
   `run_before` explícito para congelar a ordem antes de `reviews/0001`;
3. `reviews/0001_learning_foundation`, dependente de
   `accounts/0001_initial`, `questions/0002_question_catalog` e
   `attempts/0001_learning_foundation`;
4. `attempts/0002_review_receipt_constraints`, dependente de
   `reviews/0001_learning_foundation` e
   `errors/0002_learning_classification`.

A FK `Attempt.review` existe somente na quarta migration. O grafo não possui
dependência circular. `makemigrations --check --dry-run` informou `No changes
detected`. A comparação direta com a tag `v0.2.0` e o manifesto de hashes
confirmaram que as cinco migrations V0.1/V0.2 permanecem byte a byte intactas.

## Constraints, índices e validações

- FKs novas usam `PROTECT` e rejeitam órfãos.
- `CHECK`s cobrem enums/estados, coerência local de tipo, datas de estado,
  motivos, política fixa, sequências e `lock_version` positivo.
- Unicidades cobrem tentativa inicial válida por questão, tentativa válida por
  `Review`, ciclo `ACTIVE` por questão, `Review` `PENDING` por ciclo,
  classificação por tentativa, revisão/número, âncora automática do ciclo,
  idempotência da tentativa no Workspace e recibo por
  `(workspace, operation_kind, idempotency_key)`.
- Índices cobrem histórico de tentativa, resultado/data, tipo/data,
  classificação, ciclos, fila estrutural de revisões e consulta por questão.
- Validações de modelo impedem vínculos cruzados de Workspace, versão ou
  alternativa incompatível, resultado divergente do gabarito, classificação
  de acerto, categoria `OTHER` sem descrição e recibo apontando para resultado
  incompatível.
- `Attempt`, `OperationReceipt` e `ErrorClassificationRevision` possuem
  caminhos de mutação bloqueados; a revisão de classificação é append-only.
- O recibo possui somente metadados técnicos mínimos, retenção mínima de 30
  dias e expurgo explícito dependente de `Clock`.

As invariantes intertabelas não foram simuladas com `CHECK` SQLite. Elas são
validadas nos caminhos de modelo desta fundação e permanecem contratuais para
os services das etapas próprias.

## Policies e contenção

`ReviewSchedulePolicy` e `ReviewStatusPolicy` são Python puro, sem ORM, escrita
ou transação. Ambas recebem `Clock` e `Calendar` injetáveis. Os testes cobrem:

- erro em qualquer estágio → D1 em data real + 1 dia;
- acertos D1/D7/D14 → D7/D14/D30 em +7/+14/+30 dias;
- acerto D30 → ciclo concluído sem nova pendência;
- estados futura, devida e atrasada por data civil/fuso, com prevalência dos
  estados estruturais.

O perfil SQLite mantém timeout de 5 s. A política de escrita crítica repetiu
somente erro `SQLITE_BUSY`/`locked`, exatamente uma vez após 150 ms, mantendo a
mesma chave. Um teste com lock SQLite real confirmou duas tentativas totais,
falha recuperável após contenção persistente e zero estado parcial; outros
erros não são repetidos.

## CTs e provas operacionais

| Caso | Resultado e evidência |
|---|---|
| `CT-073` | PASS — FKs/`PROTECT`, órfãos e `CHECK`s locais |
| `CT-074` | PASS — validações rejeitam vínculos cruzados; zero vazamento |
| `CT-076` | PASS — segunda inicial válida rejeitada |
| `CT-077` | PASS — segunda tentativa válida da mesma revisão rejeitada |
| `CT-078` | PASS — segundo ciclo ativo rejeitado; histórico concluído preservado |
| `CT-079` | PASS — segunda pendência rejeitada pelo guard e pelo índice único |
| `CT-080` | PASS — mesma chave/hash recupera recibo; hash divergente conflita |
| `CT-081` | PASS — todas as migrations aplicadas em SQLite vazio e aplicação inicia |
| `CT-082` | PASS — cópia representativa V0.2 preservou contagens, FKs, datas, revisão, alternativas e gabarito após upgrade |

O backup físico pré-upgrade foi restaurado em novo destino isolado. O banco
restaurado retornou ao plano V0.2, sem qualquer migration V0.3 aplicada, com
`PRAGMA integrity_check = ok`, `foreign_key_check` vazio e os dados
representativos preservados. A restauração corrente também reconciliou as seis
entidades V0.3 e suas relações.

## Gate e decisão

Comando executado:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

Resultado: exit code 0. O gate aprovou lock/runtime, perfis Django,
rastreabilidade, hashes, migration limpa, formatação, lint, mypy, 209 testes,
cobertura, secrets e auditoria de dependências (`No known vulnerabilities
found`).

Etapa 1 encerrada sem commit, push, tag ou release. A Etapa 2 não foi
preparada nem iniciada.
