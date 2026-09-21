# V0.5-S2C — Resultado da correção prospectiva de gabarito

- Data: 2026-09-20.
- Tarefa: `V0.5-S2C`.
- Baseline de execução: `main` em
  `cd878a59a7eb05bbd1150ebb441be212b43cb373`; tag `v0.4.4` documentada em
  `46e887e0c4fa4dd6f7e128ab63802223d99c9e29`.
- Estado inicial da árvore: somente `tasks/current.md`, com a autorização S2C,
  estava modificado.
- Resultado: **APPROVED / GREEN**.

## A4, schema e migration

O plano `tasks/plans/v05-s2c-answer-key-correction-plan.md` foi persistido e
marcado `COMPLETED` antes da primeira edição funcional. Ele auditou Question,
QuestionRevision, alternatives, current, publicação/edição, Attempts,
avaliação, Reviews/Cycles, analytics, classificações, timeline, AuditEvent,
Workspace, concorrência, idempotência, migrations, upgrade, rollback,
recovery e checker.

O schema de `questions` já suportava versão crescente, snapshot imutável,
alternativas próprias, gabarito por FK, current única e Attempt vinculada à
revision histórica. Portanto não houve migration em `questions`, pointer
paralelo nem backfill. A lacuna estrutural comprovada estava em `AuditEvent`:
choices/constraints não admitiam `ANSWER_KEY_CORRECTED`/`QUESTION` e dois IDs
não registravam simultaneamente Question, R1 e R2.

`operations.0003_answer_key_correction_audit` é a única migration S2C. Ela é
aditiva, acrescenta `previous_entity_id` nullable sem default/backfill e amplia
somente os conjuntos fechados de evento/entidade/constraint. Eventos S2A/S2B
permanecem inalterados. Reverse é seguro antes de fatos S2C; após R2/R3 reais,
restore com código compatível é requerido e downgrade não é prometido. O
manifesto `quality/v05-s2c-migrations.json` protege todo o conjunto pós-V0.3.

## Serviço, lifecycle e integridade

`AnswerKeyCorrectionService` é a fronteira transacional Workspace-scoped. Ele
exige Question `ACTIVE`, revisão corrente esperada, posição válida diferente
do gabarito vigente, motivo codificado e correlação. Sob trava da Question,
copia stem, explanation, trap note, notes e todas as alternatives, cria novas
linhas de Alternative para R2/R3, muda apenas a correta, troca current,
incrementa `Question.lock_version` e grava o evento na mesma transação.

R1→R2→R3 foi provado com versões 1/2/3 e exatamente uma current. Revisões e
alternativas antigas rejeitam save/update/delete normais; edição convencional
não pode mascarar mudança de alternativas/gabarito como não crítica depois de
Attempt. A nova correta sempre pertence à nova revision; cinco alternativas
confirmaram quantidade variável e ausência de limite A–D.

Retry equivalente pela mesma correlação retorna a R2 já criada; correlação
divergente e expected revision stale falham sem R3 silenciosa.
`OperationReceipt` e sua retenção não mudaram. Duas correções simultâneas
produziram um sucesso, um conflito, uma nova revision e uma current.
Confirmação de Attempt e correção serializam por lock/CAS de Question; o fato
confirmado mantém a revision efetivamente apresentada.

## Auditoria, sanitização e timeline

`ANSWER_KEY_CORRECTED` persiste somente Workspace, `entity_id=Question`,
`previous_entity_id=R1`, `related_entity_id=R2`, correlação, motivo codificado e
instante. Não existem campos de enunciado, alternatives, resposta, explicação,
payload ou snapshot. Constraint, model validation e `AUD-001` verificam
metadados, ownership, sequência e `CRITICAL_CORRECTION`; AuditEvent continua
append-only.

A timeline read-only mostra “revisão 1 → 2” e Attempts continuam mostrando o
número da revision realmente usada. Não foi construída UI de gestão.

## Atomicidade, Workspace e preservação histórica

Fault injection após criar revision, após copiar alternatives, antes/depois de
trocar current e antes/depois do AuditEvent confirmou rollback de revision,
alternatives, current, lock e audit. Question estrangeira falhou sem mutation.

Snapshots antes/depois sem nova Attempt permaneceram idênticos para:
registered, performed, attempts, correct/errors/rates, discipline, subject,
frequência e drill-down de categoria, Reviews, ReviewCycles e classificação.
Attempt R1 preservou revision, alternativa, `is_correct`, status, void metadata
e replacement. Uma Attempt futura ficou ligada a R2 e foi avaliada pelo
gabarito R2. Feedback/apresentação histórica continuam resolvíveis pela R1.

O cenário S2B `A VOIDED → B VALID` permaneceu byte/semanticamente igual:
mesma cadeia, ponta B, fatos, Reviews/Cycles e contagem de eventos
`ATTEMPT_VOIDED`/`ATTEMPT_REPLACED`; nenhuma replacement ou reconstrução nova
foi criada. S2C não chamou `AttemptCorrectionService`, não reclassificou fatos,
não recalculou analytics antigos e não alterou scheduling, D1/D7/D14/D30,
`REV-FIXA-1.0`, due dates ou completion.

## Checker, upgrade, rollback e recovery

O checker permanece read-only e continua com 22 checks. Não foi criado check
novo: `QUE-002`, `QUE-003` e `ATT-001` já cobriam ownership/current/binding;
somente `AUD-001` foi ampliado. O resultado S2C foi 22 checks e zero findings.

`tests/test_v05_s2c_upgrade.py` executou migrations reais
V0.4.4-equivalent→S2A→S2B→S2C, reverse/forward seguro antes de fatos S2C,
preservou Question/Attempt V0.4.4, categoria pessoal+merge, reagendamento,
AuditEvents S2A, cadeia S2B, classificação e Reviews. Depois criou R2 e uma
Attempt REVIEW futura em R2, fez backup S6 e restore isolado, e reconciliou
current=2, Attempts R1/R2, cadeia VOIDED→VALID, analytics, Reviews, checker,
`PRAGMA integrity_check=ok`, zero violações de foreign key e todos os eventos.
Após fatos S2C, rollback suportado é restore; executar código antigo sobre R2/R3
não é declarado compatível.

## Testes, A8 e gate

- Testes próprios S2C: 14 casos (13 domínio/integração + 1 upgrade/recovery).
- Regressão focada multicamada: **214 passed** em **71,58 s**.
- `makemigrations --check --dry-run`: `No changes detected`.
- Ruff e mypy focados: aprovados; `git diff --check`: aprovado.
- A8 deep: **APPROVED**, Blocker 0, Major 0, Minor 0 aberto.
- Findings resolvidos antes da aprovação: guard passou a detectar o conteúdo
  real em vez de confiar no `change_kind` informado; teste negativo de
  corrupção de current passou a usar injeção deliberada abaixo do guard.

Gate autoritativo:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`

- Tentativa 1: **RED**, exit code 1, no mypy por duas anotações do novo teste;
  falha real da tarefa, corrigida sem mudança semântica.
- Tentativa 2: **GREEN**, exit code 0, duração total **172,9 s**.
- Runtime: Python 3.13.15, Django 5.2.17 e SQLite 3.53.1.
- Banco vazio/migrations, três perfis, formatação de 306 arquivos, Ruff, mypy
  de 150 arquivos, detect-secrets e rastreabilidade: aprovados.
- Pytest: **388 passed** em **133,04 s**; cobertura global **87%** e mínimos de
  domínio de 80% aprovados.
- `pip-audit`: `No known vulnerabilities found`.
- `gate_first_pass: false`; tentativa aceita: 2; incidente externo: não.

## Limites e decisão

Não houve permanent delete, retention cleanup, purge, auditoria de exclusão,
UI S3, domínio, prioridade, export/import, mudança de arquitetura, commit,
push, tag ou release. S2D não foi iniciada nem autorizada.

V0.5-S2C está concluída e elegível para arquivamento. Modelo da execução:
GPT-5; reasoning detalhado, duração total e cotas de 5h/semanal não estavam
observáveis e permanecem `unknown`, sem estimativa.
