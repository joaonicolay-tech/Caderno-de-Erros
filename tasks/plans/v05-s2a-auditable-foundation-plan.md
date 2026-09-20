# Plano A4: V0.5-S2A — Fundação auditável e gestão não destrutiva

- ID da tarefa relacionada: `V0.5-S2A`
- Status: `COMPLETED`
- Objetivo: fixar a menor decomposição executável antes da implementação da
  fundação auditável, sem ampliar o contrato em `tasks/current.md`.
- Baseline observado: `main` em
  `8617d73965ef6da365e2d10788fe413e8ae7b197`; tag `v0.4.4` no commit
  `46e887e0c4fa4dd6f7e128ab63802223d99c9e29`; somente o contrato corrente
  fornecido estava modificado ao iniciar.
- Premissas: preservar facts V0.4.4, `Workspace`, `REV-FIXA-1.0`,
  D1/D7/D14/D30, `ReviewStatusPolicy`, analytics, checker read-only e S6.

## Decomposição fechada antes da implementação

1. **Schema e migrations aditivas.**
   - `operations`: criar `AuditEvent` com colunas fechadas de metadados
     técnicos, sem JSON/payload/conteúdo, proteção append-only, correlação,
     Workspace e catálogo limitado aos eventos S2A.
   - `errors`: evoluir `ErrorCategory` para distinguir `STANDARD` e `PERSONAL`,
     acrescentar lifecycle `ACTIVE`/`ARCHIVED`/`MERGED` e alvo de merge; manter
     os IDs/FKs históricos e aplicar unicidade normalizada pessoal por
     Workspace. Não migrar nem reescrever classificações.
   - `reviews`: acrescentar origem `MANUAL` a `ReviewCycle` e criar
     `ReviewScheduleChange` append-only; preservar `Review.first_due_date` e a
     unicidade parcial já existente de ciclo/Review pendentes.
   - Gerar somente as migrations desses três grupos, sem backfill funcional.
     Defaults `STANDARD`/`ACTIVE` classificam fielmente categorias V0.4.4;
     ausência de AuditEvent, mudança de agenda, merge e ciclo manual continua
     válida para dados antigos.

2. **Serviços transacionais e guards.**
   - Centralizar registro funcional mínimo em `operations`, separado de logs
     técnicos e de `OperationReceipt`.
   - Criar serviço de categoria pessoal para create, rename, archive e merge,
     com código estável, motivo codificado, optimistic guard, Workspace e
     ciclo/target canônico validados antes da escrita.
   - Criar serviço de reagendamento que aceite somente Review pendente de
     ciclo/Question ativos, data civil válida no fuso do Workspace e motivo
     codificado; alterar somente `current_due_date`/lock e inserir histórico e
     auditoria no mesmo commit.
   - Criar serviço de inclusão manual que reutilize a INITIAL correta `VALID`,
     exija Question ativa e ausência de ciclo ativo, e crie apenas ciclo
     `MANUAL`, D1 e auditoria no mesmo commit.
   - Usar transações curtas, constraints existentes, locks/versões e o retry
     SQLite já existente; nenhum command-processing novo.

3. **Classificação, selectors e analytics.**
   - Aceitar em novos diagnósticos apenas categoria padrão ou pessoal
     `ACTIVE` do mesmo Workspace.
   - Resolver explicitamente cadeias de merge para alvo pessoal ativo, com
     conjunto visitado e limite derivado do número de categorias, nunca por
     recursão silenciosa.
   - Projetar frequência corrente no alvo canônico e preservar a FK/revisões
     históricas na origem; drill-down usa o mesmo mapa para evitar dupla
     contagem e N+1.

4. **Testes focados e upgrade.**
   - Cobrir modelos/serviços de auditoria, sanitização negativa, append-only,
     Workspace e rollback transacional.
   - Cobrir create/rename/archive/merge, duplicidade normalizada, padrão
     protegido, cadeia, self/cycle/cross-Workspace, concorrência proporcional
     e analytics reconciliado.
   - Cobrir reagendamento hoje/futuro, rejeições, preservação de
     `first_due_date`/stage/policy/facts, fila, analytics, auditoria, conflito e
     falha atômica.
   - Cobrir inclusão elegível, D1 `MANUAL`, rejeições, ausência de nova
     Attempt/performed, Workspace, conflito/duplicidade e falha atômica.
   - Executar teste de migration partindo das folhas equivalentes a V0.4.4,
     confirmar preservação/defaults/constraints e retornar às folhas atuais.
   - Exercitar backup pré-upgrade e restore em arquivo isolado, checks físicos,
     FKs, reconciliação e S5 aplicável; nunca usar a única cópia operacional.

5. **Verificação e encerramento.**
   - Rodar suites focadas e regressão de learning, Reviews, analytics,
     classificações, fila, dashboard, checker e recovery.
   - Executar `makemigrations --check --dry-run`, `git diff --check` e o gate
     autoritativo; registrar comandos, totais, cobertura e `pip-audit`.
   - Fazer A8 deep de migrations, constraints, upgrade/rollback, Workspace,
     atomicidade/concorrência, leakage, append-only, categorias/merge/ciclos,
     analytics, agenda, inclusão e vazamento S2B/C/D; corrigir Blocker/Major.
   - Persistir evidence S2A, métricas A7 (`unknown` quando não observáveis),
     atualizar somente fatos concluídos em `PROJECT_STATE.md`, arquivar o
     contrato e restaurar `tasks/current.md` a `NO_TASK_AUTHORIZED` via
     `finish-task`.

## Arquivos prováveis

- Modelos/migrations: `src/modules/operations/models.py`,
  `src/modules/operations/migrations/`, `src/modules/errors/models.py`,
  `src/modules/errors/migrations/`, `src/modules/reviews/models.py` e
  `src/modules/reviews/migrations/`.
- Serviços/selectors/analytics: `src/modules/operations/services.py`,
  `src/modules/errors/services.py`, `src/modules/errors/selectors.py`,
  `src/modules/reviews/services.py`, `src/modules/analytics/services.py` e,
  somente se necessário, selectors diretamente relacionados.
- Testes/evidência: novos testes focados S2A, regressões existentes, artefato
  `quality/v05-s2a-*.md`, métricas A7, `PROJECT_STATE.md`, plano e contrato.

## Migrations, upgrade, rollback e recovery

- As migrations devem ser independentes por app e ordenar dependências apenas
  quando uma FK exigir; cada uma documentará finalidade, compatibilidade,
  default/nullability, ausência de backfill funcional, constraints e risco.
- Mudanças puramente aditivas são tecnicamente reversíveis enquanto não houver
  fatos S2A. Após uso funcional, downgrade perde auditoria/histórico de agenda
  e lifecycle pessoal: `restore recommended`, nunca reversão destrutiva sobre
  a única cópia.
- A prova de upgrade usa artefato descartável equivalente às migrations
  V0.4.4, backup S6 anterior, candidate migrado, `foreign_key_check`, dados e
  métricas reconciliados, checker read-only e restore isolado validado.
- Checker S5 não ganha repair. Se os testes e constraints S2A forem suficientes
  sem falsa declaração de saúde, a consolidação do catálogo fica como handoff
  explícito para S8.

## Riscos e controles

- **História reescrita/dupla contagem:** manter FKs de classificação e agregar
  por mapa canônico único.
- **Cross-Workspace/ciclo de merge:** guards antes da escrita, constraint local
  e transação integral.
- **Mutation sem audit ou audit órfão:** criar ambos na mesma transação e testar
  falha intermediária.
- **Concorrência local SQLite:** constraints parciais, `lock_version`,
  `select_for_update` quando portátil e retry crítico existente.
- **Leakage:** schema sem payload livre; razões são códigos limitados; testes
  negativos para stem, alternativas, respostas, explicações e secrets.
- **Escopo:** nenhum serviço, migration ou evento funcional de S2B, S2C ou S2D;
  nenhum delete/expurgo/UI geral. A classificação de migration de S2C já está
  coerente como `UNLIKELY/UNKNOWN`, logo não requer edição documental.

## Condição de saída

Este desenho A4 está fechado antes de qualquer edição funcional. A execução só
segue dentro do contrato `V0.5-S2A`; sua conclusão dependerá das evidências,
A8 deep e gate, não do status deste plano.
