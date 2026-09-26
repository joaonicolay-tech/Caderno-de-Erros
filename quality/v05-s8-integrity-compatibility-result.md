# V0.5-S8 — evidência de integridade e compatibilidade

**Estado:** `COMPLETE`; PostgreSQL crítico, A8 deep e gate final aprovados.
**Modelo/reasoning solicitado:** GPT-6 Sol / High; metadados de runtime não expostos ao processo para comprovação independente.
**A4:** `tasks/plans/v05-s8-integrity-compatibility-plan.md`, fechado antes da primeira edição funcional.

## Autoridade, baseline e limites

- Branch `main`; `HEAD = origin/main = a1e0d5a0b971de35d0b4f54514eff66feeb6fef2` no início. Working tree inicial: somente `M tasks/current.md` (autorização) e `?? tasks/plans/v05-s8-integrity-compatibility-plan.md` (A4); `git diff --check` exit 0.
- `git rev-list -n 1 v0.4.4` resolveu `46e887e0c4fa4dd6f7e128ab63802223d99c9e29`; a tag anotada não foi tratada como commit.
- `FL-ABR-009 = RESOLVED_FOR_V0.5` conforme adendo humano do A4. OperationReceipt é técnico, distinto de AuditEvent; 30 dias é piso de retenção, não expiry. Nenhum TTL, scheduler ou purge genérico foi criado. Exceção S2D permanece.
- `Migration: NO`; `makemigrations --check --dry-run --settings=config.settings.test` retornou `No changes detected`, exit 0 antes da implementação e na verificação local posterior. Nenhuma migration nova foi criada.
- S9+ não autorizadas; nenhum commit, push, tag ou release foi executado.

## Checker V0.5

- Catálogo passou de 22 para 25 IDs, preservando os 22 anteriores. `SAV-001` diagnostica ownership/Workspace/schema/payload de SavedFilter; `DOM-001` diagnostica sequência e referências de MasteryStateEvent sem recalcular policy histórica; `AUD-002` diagnostica evento S2D sanitizado vencido em 90 dias UTC sem expurgar.
- `OPS-001` aceita receipt existente com idade maior que 30 dias. Não há check de vencimento de receipt.
- O checker continua SQLite `mode=ro`, com snapshot lógico e apenas leituras. Testes com fingerprints de linhas, valores e timestamps de modelos relevantes e bytes de SQLite/sidecars confirmaram ausência de mutação; o teste negativo também confirmou ausência de reparo. Nenhum AuditEvent ou OperationReceipt foi criado pelo checker.
- Fixtures negativas isoladas cobriram owner e referências cross-Workspace de SavedFilter, schema futuro, campo desconhecido, categoria estrangeira, MasteryStateEvent cross-Workspace e sequência com lacuna, e evento S2D vencido. Teste temporal fixou o instante UTC e diferenciou exatamente `created_at + 90 dias` de `+1 microssegundo`.
- V05-INV-001–014 seguem a classificação do A4 entre constraint, guard, transaction, checker, reconciliation e teste histórico. Não foram convertidas artificialmente em 14 checks.

## Upgrade e recuperação SQLite

- `tests/test_v05_s2a_upgrade.py` constrói banco V0.4.4 com `MigrationExecutor.project_state(v044).apps` e fatos legados reais: Workspace/fuso, categorias padrão, Question/Revision/Alternatives, Attempt INITIAL válida/incorreta, classificação, ciclo e Review pendente, além de OperationReceipt legado.
- Antes das migrations, `create_sqlite_backup`/`validate_sqlite_backup` produziram manifesto `CEI-SQLITE-BACKUP` e SHA-256 de 64 caracteres; cópia física em destino isolado foi validada por `integrity_check=ok`, `foreign_key_check=[]`, uma Attempt, um receipt e ausência de tabela SavedFilter. O snapshot pré-upgrade requer software/schema V0.4.4 compatível; o restore S7 atual exige migrations atuais.
- `MigrationExecutor` executou as 10 migrations V0.5 identificadas no A4 (operations.0001–0004, reviews.0003–0005, errors.0003, search.0001, domain.0001) até os leaves atuais. `integrity_check=ok`, `foreign_key_check=[]`, checker 25/zero findings e hash SQLite inalterado pelo checker.
- Reconciliação do dataset: 10 categorias, 1 Attempt, 1 classificação, 1 ciclo, 1 Review e due dates preservados; analytics registrou 1 Attempt/performed/classified e 1 Review futura na data fixa. Campos novos de categoria passaram a `STANDARD`/`ACTIVE`; SavedFilter, AuditEvent, ReviewScheduleChange e MasteryStateEvent permaneceram vazios. Nenhum backfill funcional inventado.
- Receipt legado de mais de 30 dias foi preservado com mesmo ID/created_at e resolvido por `resolve_existing`; backup atual e restore isolado S7 preservaram 1 receipt. CEI export após upgrade validou uma Question e não incluiu receipts.
- Domain S5 leu a Question com clock fixo sem criar evento; Priority S6 retornou `collect_more_evidence` sem ranking persistido; testes próprios S5/S6/S7 e regressões de S2A–S2D passaram no gate.
- O pacote CEI do candidate migrado foi importado em um segundo banco vazio no schema atual e reexportado. O round trip preservou semanticamente Questions, QuestionRevisions e Attempts; a lista de migrations do manifest coincidiu com o grafo atual. O destino foi isolado; receipts não fazem parte do CEI.
- Restore de backup candidato no schema atual retornou checker 25/zero findings e 10 categorias. O probe de reversão presente é restrito a fatos legados representáveis; não constitui promessa de downgrade após fatos V0.5.

## PostgreSQL real — matriz crítica A4 §11

- Após o usuário configurar `pgpass.conf` fora do repositório, a conexão `psql -w` confirmou servidor PostgreSQL **18.6** em `127.0.0.1:5432`. Nenhuma senha foi solicitada, lida, impressa ou copiada. `postgres` foi usado somente como banco administrativo para provisionamento; nenhuma prova destrutiva rodou nele.
- Banco descartável dedicado `cei_s8_test_20260925_a61e`, owner/role `cei_s8_role_20260925_a61e` com `NOLOGIN`. O probe opt-in `tests/probe_v05_s8_postgres.py` exige esses prefixos, verifica `current_database`, `current_user`, owner e ausência de superuser no papel efetivo antes de migrar. Conexões Django/psycopg usam `SET ROLE` via options, autenticadas por pgpass. Dados sintéticos somente.
- O target foi confirmado por nome exato, owner, `datistemplate=false` e zero sessões antes de cada `DROP DATABASE` usado para reiniciar a prova. O banco `postgres` não foi alvo de DROP nem de mutação de teste. Migrations reais chegaram a **34** registros; backend `postgresql`, **429** constraints observadas.
- Resultado final do probe: **PASS, exit 0**. FK inválida, UNIQUE de Attempt INITIAL, Review pendente, categoria pessoal e receipt rejeitaram duplicatas; CHECK de Attempt, ciclo, categoria, auditoria e mastery e NOT NULL rejeitaram estados inválidos. Casos válidos foram persistidos antes dos negativos. JSONField materializou `jsonb`; validador S3 rejeitou chave desconhecida e referências de outro Workspace. FK simples aceitou relação cross-Workspace em transação revertida, enquanto o service a recusou. Rollbacks de reschedule/audit e void S2B com falha injetada preservaram fatos; duas conexões comprovaram `FOR UPDATE` com timeout e liberação. Priority/Review Queue demonstraram ordenação estável de duas linhas com data fixa. Receipt com mais de 30 dias resolveu retry de mesmo hash e recusou hash divergente.
- Após a prova, o alvo foi novamente confirmado pelo nome exato, owner, ausência de sessões e `datistemplate=false`; `DROP DATABASE` removeu apenas o banco S8. O papel `NOLOGIN` também foi confirmado pelo nome, sem superuser e sem ownership de outro database antes de `DROP ROLE`. Ambos os comandos terminaram com exit 0; nenhum dado pessoal ou banco não dedicado foi apagado.
- PostgreSQL foi usado só para a matriz crítica. O checker físico permanece deliberadamente SQLite read-only conforme A4 §11. A falha inicial do probe por exceção de guard esperada diferente, e a tentativa de CEI export com Workspace sintético fora do ID local, foram correções do harness; a prova CEI foi feita no upgrade SQLite, dentro da matriz prevista. Nenhuma dessas tentativas foi relatada como PASS PostgreSQL.

## Verificações observadas e A8

- Testes focados: `tests/test_integrity_checker.py` → 15 passed; upgrade S2A integrado → 1 passed; conjunto inicial de checker e upgrades S2A/S2B/S2C/S2D/S5 → 18 passed antes das últimas extensões locais.
- Ruff e mypy focados passaram; `git diff --check` sem saída, exit 0 na inspeção posterior.
- Gate tentativa 1, antes da adição do driver: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1` → **GREEN, exit 0**, duração reportada 321,4 s; 502 passed, 86% coverage, duas `ResourceWarning` SQLite. Essa working tree era anterior ao driver.
- Gate tentativa 2, após adição do driver: **RED, exit 1** na etapa de testes; 501 passed, 1 failed, 86% coverage em 235,70 s. `test_simultaneous_manual_reopen_has_one_event_cycle_and_d1` recebeu `sqlite3.OperationalError: database is locked` na concorrência de S5. O mesmo teste isolado passou em seguida (`1 passed`, exit 0, 4,60 s). Sem alteração de código/política de retry, a falha foi classificada provisoriamente como contenção intermitente SQLite. As etapas anteriores da tentativa 2 (lock, migrações, Ruff, mypy) passaram; detect-secrets/pip-audit não foram alcançados.
- Gate tentativa 3, mesma working tree funcional e dependências da tentativa 2: **GREEN, exit 0**, duração reportada 287,9 s; 502 passed em 242,51 s, 86% coverage e duas `ResourceWarning` SQLite no teste S2D. Lock, migrações, formatação, Ruff, mypy, cobertura de domínio, detect-secrets e pip-audit (`No known vulnerabilities found`) passaram. A tentativa 2 RED permanece registrada.
- Gate tentativa 4, após o probe PostgreSQL inicial: **RED, exit 1** na formatação do probe; corrigida antes da etapa de testes.
- Gate tentativa 5, com probe formatado: **GREEN, exit 0**, 502 passed, 86% coverage, duas `ResourceWarning` SQLite, pip-audit sem vulnerabilidades conhecidas; duração reportada 307,3 s.
- Gate tentativa 6, após round trip CEI do candidate: **GREEN, exit 0**, 502 passed, 86% coverage, duas `ResourceWarning` SQLite, pip-audit sem vulnerabilidades conhecidas; duração reportada 287,9 s.
- Gate tentativa 7, após a última ampliação do probe PostgreSQL: **GREEN, exit 0**, duração reportada **335,9 s**; **502 passed** em 286,93 s, 86% coverage e duas `ResourceWarning` SQLite preexistentes nos testes S2D. Lock, três perfis, banco vazio/migrations, formatação, Ruff, mypy, cobertura de domínio, detect-secrets e pip-audit (`No known vulnerabilities found`) passaram. `gate_first_pass=false` para S8, por causa das tentativas 2 e 4 RED; não foi reescrito como true após o GREEN.
- `git diff --check` observado sem saída, exit 0 depois do gate. Nenhuma migration nova, segredo, backup, `pgpass.conf` ou fixture pessoal apareceu no diff/status.

## A8 deep — APPROVED

- **Blocker 0; Major 0; P0/P1 aplicável aberto 0.** Revisão do diff e das fontes A4/contrato: somente checker/catalog V0.5, testes e harness de upgrade/PostgreSQL, dependência dev do driver, documentação e evidence. Nenhuma ação S9+, migration, repair, scheduler, purge de receipt, commit, push, tag ou release.
- Os 22 IDs do checker anteriores permaneceram estáveis e os três novos estão documentados; SQL e tratamento temporal apenas leem o snapshot SQLite. Testes cobrem fingerprints de modelos, timestamps e bytes do arquivo, casos sadios/negativos e limite exato de 90 dias sem expurgo. `OPS-001` não transforma o piso de 30 dias em expiração de receipts.
- Upgrade partiu de ProjectState V0.4.4 pelas migrations reais, com backup pré validado, facts legados preservados, checks físicos/FK, projections de data fixa, restore isolado atual, Domain/Priority derivados e round trip CEI em destino vazio. Backup V0.4.4 requer software compatível; restore de snapshot pré-delete é recuperação deliberada, não ressurreição por migration. Rollback testado apenas no subconjunto legado representável; nenhum downgrade de fatos V0.5 foi prometido.
- PostgreSQL 18.6 foi servidor real descartável, não fake backend. Constraints, guards, transações, locks, ordenação e receipt foram comprovados no probe segregado; seus alvos foram verificados antes do cleanup. A matriz crítica não equivale a operação PostgreSQL completa. A correção do teste de ordenação e o round trip do candidate surgiram na revisão e foram concluídos antes deste APPROVED.
- Ressalvas observadas sem Blocker/Major: duas `ResourceWarning` SQLite preexistentes no gate; uma tentativa RED anterior por contenção SQLite intermitente S5 e outra por formatação do probe, ambas preservadas acima. O gate final atual é GREEN; não há finding aberto que impeça S8.
