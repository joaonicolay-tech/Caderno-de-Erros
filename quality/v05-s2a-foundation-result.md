# V0.5-S2A — Evidência da fundação auditável e gestão não destrutiva

## Estado da evidência

- Task: `V0.5-S2A`.
- Baseline de execução: `main` em
  `8617d73965ef6da365e2d10788fe413e8ae7b197`; tag `v0.4.4` em
  `46e887e0c4fa4dd6f7e128ab63802223d99c9e29`.
- Estado inicial da árvore: somente `tasks/current.md`, com a autorização
  fornecida, estava modificado.
- Implementação, regressão focada e A8 deep: concluídas.
- Gate autoritativo: **GREEN** na segunda execução, exit code 0.
- Encerramento documental: concluído após o gate verde.

## Plano A4 e escopo

O plano `tasks/plans/v05-s2a-auditable-foundation-plan.md` foi persistido e
marcado `COMPLETED` antes da primeira edição funcional. Ele fixou schema,
migrations, serviços, projeção analytics, upgrade, rollback, recovery, riscos,
testes e verificação. O plano não ampliou `tasks/current.md`.

Não foram criados UI geral, VOID/substituição/rebuild de Attempt (S2B),
correção de gabarito (S2C), delete/retention/expurgo (S2D), filtros salvos,
domínio, prioridade, export/import, event sourcing ou infraestrutura
distribuída. O plano de release já registrava S2C como `UNLIKELY/UNKNOWN`, em
conformidade com S1; nenhuma correção documental foi necessária.

## Schema final e migrations

### `operations.0001_initial`

- Cria `AuditEvent` Workspace-scoped e append-only.
- Campos fechados: evento, entidade/IDs técnicos, correlação, motivo codificado,
  datas técnicas opcionais do reagendamento, timezone e instante de criação.
- Não há JSON, payload, snapshot, enunciado, alternativa, resposta, explicação
  ou conteúdo de estudo.
- Compatibilidade: aditiva, sem backfill e sem mudança de linha V0.4.4.
- Rollback: safely reversible enquanto não existirem eventos S2A; após uso,
  `restore recommended`, pois reverse apagaria auditoria funcional.

### `errors.0003_errorcategory_category_kind_and_more`

- Reutiliza `ErrorCategory` e suas FKs históricas; acrescenta kind
  `STANDARD/PERSONAL`, state `ACTIVE/ARCHIVED/MERGED`, `merged_into` e
  `lock_version`.
- Categorias V0.4.4 recebem defaults semanticamente verdadeiros
  `STANDARD/ACTIVE`; não há categoria pessoal, evento ou reclassificação
  inventada.
- Constraints: código/kind, lifecycle, código e nome normalizado único pessoal
  por Workspace, versão positiva e self-merge proibido.
- Classificações e revisões históricas não são reescritas por archive/merge.
- Rollback: safely reversible antes de fatos pessoais; após uso,
  `restore recommended`, pois reverse perderia lifecycle/merge.

### `reviews.0003_reviewschedulechange_and_more`

- Acrescenta origem `MANUAL` ao `ReviewCycle` e cria
  `ReviewScheduleChange` append-only.
- Dados V0.4.4 mantêm origem, `first_due_date`, `current_due_date`, estágio,
  policy e Attempts; não há backfill.
- A unicidade parcial vigente de ciclo ativo por Question e Review pendente por
  ciclo continua sendo a barreira de duplicação.
- Rollback: safely reversible sem fatos S2A; após reagendamento/ciclo manual,
  `restore recommended`.

As três migrations são aditivas e independentes por app. O risco operacional é
classificado `high`; não se recomenda downgrade destrutivo sobre a única cópia.

## Auditoria funcional

Eventos implementados estritamente para S2A:

- `REVIEW_RESCHEDULED`;
- `MANUAL_REVIEW_INCLUDED`;
- `PERSONAL_CATEGORY_RENAMED`;
- `PERSONAL_CATEGORY_ARCHIVED`;
- `PERSONAL_CATEGORY_MERGED`.

`AuditEvent` é distinto de log técnico e de `OperationReceipt`. Model e
QuerySet bloqueiam update/delete pela API normal. Razões são códigos limitados,
sem texto livre; o schema não possui campo arbitrário. Testes negativos cobrem
campo/payload funcional ausente, motivo com conteúdo livre recusado e tentativas
de save/update/delete.

Cada mutação auditada cria mutation, histórico específico e AuditEvent dentro
da mesma transação. Falha simulada na auditoria reverte archive, data
operacional, histórico de agenda, ciclo e D1.

## Categorias pessoais e analytics

- Create normaliza nome, garante unicidade pessoal por Workspace, gera código
  UUID estável e inicia `ACTIVE`.
- Rename preserva código/Workspace, usa optimistic version e audita.
- Archive preserva linha e classificações; impede novo uso e audita.
- Merge aceita somente pessoal `ACTIVE` para pessoal `ACTIVE` do mesmo
  Workspace, bloqueia self/cross-Workspace/standard/ciclo, preserva a FK da
  classificação e audita origem/alvo.
- A projeção resolve cadeias em lote com conjunto visitado. O cenário A→B→C
  soma os fatos de A/B uma única vez em C; drill-down usa o mesmo mapa.
- A consulta de categorias permanece em duas queries no teste de regressão,
  sem N+1 previsível.
- Correção explícita posterior ao merge pode criar r1 na origem histórica e r2
  no alvo ativo; o merge em si nunca reescreve revisões.
- Categorias padrão permanecem `STANDARD/ACTIVE`, código/lifecycle protegidos e
  continuam sem delete isolado.

## Reagendamento

- Aceita somente Review `PENDING`, Question `ACTIVE`, ReviewCycle `ACTIVE`,
  mesmo Workspace, data hoje/futura no timezone do Workspace, motivo codificado
  obrigatório e `lock_version` vigente.
- Atualiza somente `current_due_date`, `updated_at` e lock; preserva
  `first_due_date`, estágio, `REV-FIXA-1.0`, ciclo, Attempt e uma única
  pendência.
- `ReviewScheduleChange` guarda data anterior/nova, timezone, instante,
  correlação e motivo; AuditEvent usa a mesma correlação.
- Fila passa a derivar o estado da data atual; activity/performed/acertos/erros
  permanecem idênticos. Passado, motivo vazio, Review concluída, Question/ciclo
  inativos, Workspace externo e versão concorrente são rejeitados sem mudança.

## Inclusão manual

- Exige Question `ACTIVE`, INITIAL correta `VALID`, mesmo Workspace e ausência
  de ciclo ativo.
- Cria somente novo ReviewCycle `MANUAL` e sua D1 `REV-FIXA-1.0` para hoje+1
  civil, ancorada na INITIAL existente, mais AuditEvent correlacionado.
- Motivo é opcional. Não cria/altera/reclassifica Attempt, não recria INITIAL e
  não aumenta `performed`.
- INITIAL incorreta/VOIDED, Question arquivada, Workspace externo e repetição
  com ciclo ativo são rejeitados. Constraint parcial e transação protegem a
  dupla inclusão local.

## Checker e recovery

- O checker permanece read-only e sem repair.
- O catálogo passou de 17 para 20 checks com a extensão mínima necessária:
  `CAT-001` (lifecycle/cadeia/Workspace), `REV-005`
  (mudança↔Review↔AuditEvent/data atual) e `AUD-001`
  (evento/entidade/Workspace/metadados).
- `REV-001/002/004` foram ampliadas apenas para a origem `MANUAL`; D1 manual é
  validada pelo início civil do ciclo, sem alterar D1/D7/D14/D30.
- S6 continua usando snapshot SQLite, manifesto, SHA-256, restore isolado,
  reconciliação e S5. A reconciliação agora aceita categorias pessoais válidas
  e resolve cadeias até alvo `ACTIVE`, preservando a verificação exata das dez
  categorias padrão.

## Upgrade V0.4.4-equivalente, rollback e recovery

`tests/test_v05_s2a_upgrade.py` executa em arquivo SQLite descartável:

1. migra até folhas equivalentes a V0.4.4;
2. cria Workspace local, dez categorias padrão, Question/revisão/alternativas,
   INITIAL incorreta, classificação, ciclo e D1;
3. cria e valida backup S6 pré-upgrade;
4. migra até as folhas S2A;
5. comprova `integrity_check=ok`, `foreign_key_check=[]`, dados e datas
   preservados, defaults `STANDARD/ACTIVE`, zero backfill S2A, analytics
   reconciliado e S5 read-only com 20 checks/zero findings;
6. cria backup candidate e restaura/reconcilia em arquivo isolado;
7. reverte as migrations S2A ainda sem fatos S2A e comprova que dados V0.4.4
   permanecem.

Prova adicional S6 cria A→B→C e um reagendamento reais, faz backup/restore
isolado, reconcilia 13 categorias e obtém S5 com 20 checks/zero findings.
Backup pré-upgrade deve ser restaurado com o executável V0.4.4 correspondente;
após fatos S2A, rollback recomendado é restore, não reverse destrutivo.

## Testes e verificações antes do gate

- Regressão focada final: **170 passed** em **48,45 s**.
- Escopo: S2A, migration/upgrade, learning foundation, initial Attempt,
  completion/Reviews, consulta/fila, analytics, categorias/classificações,
  dashboard, checker e backup/recovery.
- Ruff format: 158 arquivos conformes.
- Ruff check: aprovado.
- mypy: 110 arquivos, sem issues.
- Django system check: aprovado.
- `makemigrations --check --dry-run`: `No changes detected`.
- `git diff --check`: aprovado.

## A8 deep

Resultado: **APPROVED — Blocker 0, Major 0, Minor 0 aberto**.

Revisão cobriu contrato/Protected Scope, migrations/defaults/nullability,
upgrade/rollback, Workspace, atomicidade, concorrência local, leakage,
append-only, categorias padrão/pessoais, merge/cadeias/ciclos, analytics,
reagendamento, inclusão manual, checker/recovery e vazamento S2B/C/D.

Defeitos encontrados e resolvidos antes da aprovação:

- regressão inicial de uma query extra na projeção de categorias;
- recovery S6 inicialmente restrito às dez categorias padrão;
- revisão histórica de diagnóstico inicialmente bloqueada após merge;
- regra do checker inicialmente ancorava D1 manual na data antiga da INITIAL.

Não há finding Blocker/Major/Minor aberto.

## Gate autoritativo final

- Comando: `powershell -NoProfile -ExecutionPolicy Bypass -File
  .\scripts\quality.ps1`.
- Primeira execução: **RED**, exit code 1, interrompida no controle de
  rastreabilidade porque as três migrations S2A ainda não constavam do
  conjunto protegido.
- Correção mínima: preservado o manifesto histórico V0.3 byte a byte; criado
  `quality/v05-s2a-migrations.json` e suporte explícito a manifesto adicional
  no verificador/gate, com teste de regressão próprio (`20 passed`).
- Segunda execução: **GREEN**, exit code 0, em **157,6 s**.
- Resultado: **356 passed** em **113,51 s**, cobertura global **87%**;
  cobertura dos módulos de domínio conforme o mínimo de 80% por módulo.
- Banco vazio: todas as migrations, inclusive as três S2A, aplicadas com
  sucesso; `makemigrations --check --dry-run`: `No changes detected`.
- Checks development/test/production_local, Ruff format, Ruff lint, mypy (142
  arquivos), detect-secrets e rastreabilidade: aprovados.
- `pip-audit`: `No known vulnerabilities found`; não houve incidente de rede.
- Gate first pass: `false`; tentativa aceita: 2.

## Decisão de encerramento

V0.5-S2A está concluída e elegível para arquivamento. Não houve commit, push,
tag ou release. V0.5-S2B, S2C e S2D não foram iniciadas nem autorizadas.
