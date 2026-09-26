# V0.5-S8 — A4 / integridade, compatibilidade e upgrade

**Auditoria:** 2026-09-25
**Estado:** A4 fechado para execução futura; S8 segue AUTHORIZED.
**Execução desta sessão:** auditoria e planejamento documental somente; nenhum código funcional, migration ou teste foi alterado/criado.
**Execução futura recomendada:** GPT-6 Sol / High; A8 deep.

## 1. Autoridade, baseline e fontes

tasks/current.md é a única autoridade de execução: V0.5-S8 é a única tarefa AUTHORIZED, Size L, Risk high, Migration inicial UNLIKELY, A8 deep; S9, S10 e V1+ não estão autorizadas. PROJECT_STATE.md é o checkpoint anterior à autorização S8; sua menção histórica de que S8+ não estava autorizada não prevalece sobre o contrato atual.

| Evidência inicial | Resultado observado |
| --- | --- |
| Branch | main |
| HEAD | a1e0d5a0b971de35d0b4f54514eff66feeb6fef2 |
| origin/main | a1e0d5a0b971de35d0b4f54514eff66feeb6fef2 |
| Working tree antes deste A4 | somente M tasks/current.md, correspondente à autorização S8; sem outros arquivos alterados ou untracked reportados |
| git diff --check inicial | exit 0, sem saída |
| Tag V0.4.4 | git rev-list -n 1 v0.4.4 → 46e887e0c4fa4dd6f7e128ab63802223d99c9e29; foi usado o commit resolvido, não o objeto da tag anotada |

Fontes auditadas: AGENTS.md; docs/A3_Progressive_Disclosure.md; tasks/current.md; PROJECT_STATE.md; tasks/plans/v05-release-execution-plan.md; contrato S1 e evidência S1; planos/evidências S2A, S2B, S2C, S2D, S3, S5, S6 e S7; docs/V0.5_S7_Portabilidade_e_Restore.md; docs/CEI_EXPORT_1_0.md; models, services, checker, comandos e migrations atuais; testes de checker, upgrade, backup/restore, S2A–S2D, S5, S7; manifests de migration S2A–S2D, S3 e S5. Referências executáveis principais aparecem nas seções abaixo.

## 2. Escopo oficial e fronteiras

O plano oficial V0.5 classifica S8 como compatibilidade e qualidade beta. S8 deve evoluir a integridade read-only para fatos V0.5 aprovados, demonstrar upgrade de base equivalente a V0.4.4 pelas migrations reais, recuperar em isolamento, registrar evidência de compatibilidade S5/S6/S7 e executar somente a matriz crítica de PostgreSQL. Dependências oficiais: S2A–S2D, S5 e S7; S6 deve ser auditada sem alterar a matriz de dependências; S3 é relevante por SavedFilter.

Fora da S8: repair ou checker mutável; FTS; BCR amplo; hardening geral; redesign; piloto; release/promoção; hospedagem, deploy, HA, tuning ou observabilidade de PostgreSQL; qualquer trabalho S9+.

## 3. Adendo de decisão humana — FL-ABR-009

**Fonte:** nova decisão humana S8 recebida em 2026-09-25. Ela resolve FL-ABR-009 somente para V0.5. Não atribuir esta política retroativamente ao S1, Roadmap, ADRs, S2D ou documentos anteriores.

FL-ABR-009 = RESOLVED_FOR_V0.5:

- OperationReceipt é recibo técnico de idempotência, separado de AuditEvent, fato funcional, event sourcing e recovery.
- Retenção mínima (retention floor) = 30 dias desde created_at; 30 dias não é prazo máximo nem vencimento.
- Na operação normal, recibos permanecem indefinidamente. V0.5 não tem TTL, expiração automática, scheduler, job, comando genérico de purge por idade, purge em startup/backup/restore/upgrade/request, nem cleanup geral obrigatório por idade.
- Preservar a exceção S2D já aprovada: um recibo relacionado ao agregado só pode sair dentro da exclusão atômica do agregado quando completou pelo menos 30 dias, não há contexto transitório válido dependente e todas as regras de elegibilidade S2D foram satisfeitas. Isto não é purge geral.
- Enquanto o recibo persistir, a identidade (Workspace, operation_kind, idempotency_key) mantém a semântica existente: retry compatível reutiliza resultado e hash divergente conflita; idade acima de 30 dias não executa a mutação novamente.
- Depois da remoção S2D legítima, não há garantia idempotente para o recibo removido; retry passa pelas validações atuais e não recria agregado excluído. Não adicionar tombstone.
- Backup SQLite preserva exatamente os recibos existentes no snapshot. Restore repõe esse estado sem sintetizar ou expurgar recibos; operações ocorridas somente depois do snapshot não ficam protegidas ao retornar ao snapshot.
- OperationReceipt permanece fora de CEI-EXPORT-1.0; import/export não o preserva e não exige round-trip de recibos.
- Upgrade conserva recibos legados presentes e compatíveis; não os expira, apaga ou inventa.
- Não adicionar expires_at, purged_at, TTL, tombstone ou retention_state; a decisão não autoriza migration. Crescimento é consideração operacional futura, sem threshold novo.

Evidência do schema/código atual: OperationReceipt já tem created_at, chave única por workspace/operation_kind/idempotency_key, hash e referência técnica ao resultado; o model fixa MINIMUM_RETENTION_DAYS = 30 e bloqueia exclusão antes do limite. Não existe coluna de expiração. OPS-001 nunca deve considerar idade superior a 30 dias um finding. AuditEvent permanece append-only funcional; a retenção/purge de 90 dias de eventos S2D segue política própria e o comando manual seletivo purge_question_deletion_audit.

## 4. Checker atual e prova read-only

| Item | Estado confirmado |
| --- | --- |
| Implementação | src/modules/operations/integrity.py, run_integrity_check() e INVARIANT_CATALOG |
| Entry point | python manage.py check_integrity [--limit 1..1000] [--correlation-id UUID]; comando em src/modules/operations/management/commands/check_integrity.py |
| Catálogo atual | 22 invariantes: 17 do checker V0.4, mais cinco checks incrementais V0.5 (CAT-001, REV-005, AUD-001 em S2A/S2D; ATT-003 e REV-006 em S2B) |
| IDs existentes | DB-001/002; WS-001/002/003; QUE-001/002/003; ATT-001/002/003; REV-001/002/003/004/005/006; ERR-001/002; OPS-001; CAT-001; AUD-001 |
| Leitura | O executor abre o arquivo SQLite por URI mode=ro, inicia snapshot lógico com BEGIN, executa PRAGMAs e SELECTs, faz rollback() e fecha a conexão. O checker lê SQL bruto para manter o diagnóstico em lote; não chama services mutáveis nem faz save, create, delete, repair, reconstrução ou purge. |
| Saída | Saudável exit 0; findings bloqueantes exit 2; falha operacional/inconclusiva exit 3. Limite só reduz findings exibidos, não o total. Eventos INTEGRITY_CHECK_* são logging operacional sanitizado; não são AuditEvent nem escrita funcional no banco. |
| Evidência existente | tests/test_integrity_checker.py verifica 22 IDs únicos, banco saudável, snapshot antes/depois igual, fixtures negativas e códigos de saída. quality/v04-s5-integrity-result.md registra execução em SQLite descartável com hash SHA-256 inalterado. S2A/S2B/S2D chamam o mesmo checker em upgrades isolados. |

Conclusão read-only: o código atual e os testes observados mostram caminho de leitura apenas para o banco. O comando também emite logging técnico; o requisito de ausência de side effects refere-se a linhas/timestamps/contagens/arquivos/agenda/Domain/Priority/AuditEvent/OperationReceipt, e deve ser provado novamente com fingerprint abrangente em S8. Não inferir que logs de operação sejam AuditEvent.

### Gaps atuais do catálogo

O catálogo executável cobre bem fatos históricos V0.4 e parte do lifecycle V0.5, mas não contém checks próprios para SavedFilter (S3) ou MasteryStateEvent (S5). AUD-001 verifica coerência/sanitização estrutural de eventos, mas não a retenção vencida de QUESTION_PERMANENTLY_DELETED; S1/S2D exigem purge obrigatório a partir de created_at + 90 dias UTC, que deve permanecer manual e separado do checker. OPS-001 descreve compatibilidade do recibo de forma mais ampla que o SELECT atual, que verifica sobretudo existência do alvo e Workspace; revisão S8 deve alinhar a prova ao contrato sem mudar ID/semântica silenciosamente. A idade do recibo continua estado válido.

Recomendações a decidir tecnicamente dentro do escopo, sem migration:

1. Preservar os 22 IDs e significados existentes; explicitar em documentação e testes qualquer ampliação de cobertura.
2. Fechar cobertura de V05-INV-013 com um check read-only de payload/ownership/Workspace/schema usando as mesmas regras fechadas do validador S3; possível ID aditivo SAV-001.
3. Avaliar check aditivo DOM-001 para referências e escopo de MasteryStateEvent (Workspace, Question, Attempt/ciclo, forma), sem recalcular estado Domain nem reinterpretar formula_code histórico.
4. Avaliar check aditivo AUD-002 para evento S2D sanitizado ainda presente no limite/pós-limite de retenção obrigatória, sem expurgar. Testar limite exato com relógio fixado; o checker só reporta.
5. Revisar o SQL de OPS-001 frente ao model, à chave/hash e aos tipos de operação; cobrir casos de referência/hash/key inválidos permitidos por SQL no banco descartável. Não verificar expiry por idade nem criar regra de retenção além deste adendo.

Todo ID novo é aditivo, estável e documentado em catálogo/testes. Não duplicar validações de escrita de service como proteção de checker se a regra é inobservável após escrita; distinguir prevenção de diagnóstico.

## 5. Matriz normativa V05-INV-001–014

| ID | Regra; fato/modelo; fonte | Estado/proteção principal atual | Checker atual? | Prova futura S8 |
| --- | --- | --- | --- | --- |
| 001 | Referências novas no mesmo Workspace; modelos com workspace_id e relações; S1 | service guard + FK simples; constraints compostas não são uniformes/portáveis | Parcial: WS/QUE/ATT/REV/CAT/AUD cobrem relações concretas | Fixtures cross-Workspace válidas no nível FK para Question/revision/Attempt/category/cycle/event/filter; findings e isolamento. |
| 002 | Uma Review pendente por ciclo; ReviewScheduleChange/AuditEvent explicam última data; S1/S2A | unique parcial + transaction/service | Parcial: REV-003/004/005 | duplicidade onde o schema permite, evento órfão, cronologia e due date; não aceitar transação parcialmente aplicada. |
| 003 | first_due_date imutável; nova data hoje/futura no fuso Workspace; Review/reagendamento; S1/S2A | service guard + validação temporal + transação | REV-005 compara histórico/data operacional, mas não reexecuta condição temporal original em todos os casos | casos de escrita temporal com FixedClock; checker compara fatos registrados sem inventar data operacional. |
| 004 | Inclusão MANUAL requer INITIAL correta VALID e sem ciclo ativo; ReviewCycle/Review/Attempt; S1/S2A | partial unique + service guard + transaction | REV-001 cobre origem/contexto; não é cobertura completa do caso de uso | serviço idempotente, conflito/segundo ciclo, analytics inalterada; negative fixture só onde DB permite. |
| 005 | VOIDED tem instante/motivo; VALID não tem metadados de anulação; fato permanece; Attempt; S1/S2B | DB checks + guard/model + serviço transacional | ATT-003 | estado e campos coerentes; mudança de lifecycle falha atomicamente; VOIDED continua histórico e não conta como efetivo. |
| 006 | Substituta direta de VOIDED no mesmo contexto; cadeia acíclica/sem bifurcação; Attempt; S1/S2B | unique parcial + guards + transaction | ATT-003 e REV-006 | ciclo, self-link, branch, cross-Workspace e contexto discordante em DB isolado; não duplicar fatos efetivos. |
| 007 | Derivados usam somente fatos efetivos válidos e policy identificada; Attempt/reconstrução; S1/S2B | services de reconstrução transacional + selectors | ATT-003/REV-006 cobrem cadeia/projeção Review; analytics são queries, não snapshot persistido | comparar projections/analytics por serviços com estado VOIDED e replacement; checker não reconstrói. |
| 008 | Revisões publicadas e Attempts históricos não são reescritos por correção prospectiva; QuestionRevision/Attempt/Review; S1/S2C | append-only guards + AnswerKeyCorrectionService transacional | ATT-001/AUD-001 validam vínculos/evento, não provam ausência de edição histórica sem checksum anterior | serviço cria revisão nova e preserva conteúdo/referências/resultados/agendas anteriores; não alegar detecção retrospectiva impossível. |
| 009 | Exclusão elegível apenas por agregado, atômica, sem órfãos; dependências Question; S1/S2D | PermanentQuestionDeletionService, guard/locks/CAS/transaction e FKs PROTECT | DB-002 + checks concretos; não pode provar atomicidade passada depois do commit | fault injection/contagens/FK pre/post e backup/recovery isolados; checker read-only não apaga nem reconstrói. |
| 010 | Evento final sanitizado, sem conteúdo recuperável, purge obrigatório no prazo S2D de 90 dias UTC; AuditEvent; S1/S2D | shape por DB constraints + service; purge manual seletivo e idempotente | AUD-001 cobre metadados, não vencimento | payload proibido, Workspace/correlação, limite created_at + 90d, evento vencido somente finding/check manual; checker jamais executa purge. |
| 011 | Categoria pessoal única por Workspace; padrão imutável; ErrorCategory; S1/S2A | partial UNIQUE + service guard | CAT-001 | duplicidade, categoria padrão, ownership e no-op/atomicidade em DBs isolados. |
| 012 | MERGED pessoal aponta para pessoal ACTIVE local; origem/histórico mantidos; ErrorCategory/revisões; S1/S2A | CHECK local + service guard + transaction | CAT-001 | target padrão/arquivado/foreign, ciclo e projeção histórica; não unir categorias padrão. |
| 013 | SavedFilter usa context/schema/campos/valores/IDs permitidos do Workspace; SavedFilter/payload JSON; S1/S3 | validador de payload fechado, forms e guards; DB só garante constraints locais | Não | validade do schema, context_code, schema_version, tipos, IDs inexistentes/foreign/arquivados; comparar validator e check compatível sem ler payload em logs. |
| 014 | AuditEvent correlacionado, append-only, sem conteúdo/segredo; AuditEvent; S1/S2A–D | schema/códigos fechados + manager/model guard + transaction | AUD-001 parcial/forte para vínculos e shape permitido | tentativa de update/delete via APIs, metadados proibidos/órfãos, IDs removidos; não afirmar prova pós-hoc de imutabilidade sem baseline. |

OperationReceipt é técnico e regulado pelo novo adendo FL-ABR-009, não vira AuditEvent nem ganha invariant de expiry. S3 e S5 requerem atenção específica mesmo sem novos códigos V05-INV.

## 6. Auditoria por etapa e compatibilidade

### S2A — agenda, inclusão manual, auditoria e idempotência

ReviewScheduleChange registra Workspace, Review, datas anterior/nova, timezone, motivo, correlação e instante; o service reagenda transacionalmente apenas Review pendente/ciclo ativo e escreve AuditEvent. Inclusão MANUAL cria ciclo e D1 sem novo Attempt/performed. AuditEvent é funcional, append-only e sanitizado; recibo é técnico e distinto. Checker incremental S2A: CAT-001, REV-005, AUD-001 (catálogo 20 checks ao fechar S2A). Testes futuros devem provar data operacional/histórico e falhas atômicas; ausência opcional de recibo não é inválida.

### S2B — Attempts e reconstrução

O schema V0.4.4 já contém os campos de lifecycle Attempt.status, replaces_attempt, voided_at e void_reason; migration attempts.0002 já oferece unicidades parciais relevantes. Legacy V0.4.4 permanece VALID, replacement nulo, sem VOIDED inventado. Services impedem estado/contexto inválido e resolvem cadeia iterativamente; constraints não provam aciclicidade ou Workspace composto. ATT-003 e REV-006 ampliaram o checker a 22. Testar ciclo, branch, cross-Workspace, VOIDED e ponta efetiva em banco descartável; revisar projeções via serviço de reconciliação, não via checker.

### S2C — correção prospectiva

Usa QuestionRevision/versionamento existente e adiciona apenas campos/regras de auditoria em operations.0003; não requer migration de Question nem backfill. Correção cria revisão nova e troca current atomicamente; Attempts continuam ligados à revisão histórica que viram e Reviews/scheduling não são reescritas. Testes comparem IDs, conteúdo, correct_alternative, Attempts, classificações, analytics e agenda antes/depois; checker valida vínculo/evento, não pode demonstrar que texto antigo nunca mudou sem digest histórico.

### S2D — exclusão permanente por agregado

Service preview/fingerprint/CAS/revalidação, backup/restore isolado obrigatório para agregado histórico, exclusão transacional explícita de dependências e evento final sanitizado sem ID/conteúdo reconstruível. Evento final é expurgado por manutenção manual a created_at + 90 × 24h UTC; checker read-only nunca expurga. OperationReceipt só é removido na exceção agregada após retention floor e sem contexto transitório. Prova fechada em quality/v05-s2d-permanent-deletion-result.md inclui upgrade V0.4.4-equivalent, recovery de backup pré-delete, FKs/checker e limite exato de 30/90 dias.

**Fronteira de recovery:** upgrade não deve preencher Question apagada; restore de snapshot pós-delete preserva o agregado ausente e a auditoria sanitizada que existir naquele snapshot. S2D/S7 aprovam explicitamente recuperar usando backup compatível pré-delete; esse restore deliberado retorna ao estado anterior e pode trazer o agregado de volta. Não tratar essa recuperação selecionada como ressurreição automática por migration, AuditEvent, receipt ou CEI. Não há tombstone para sobrepor o snapshot. Essa distinção deve estar visível no teste e em A8.

### S3 — SavedFilter

search.0001 é tabela nova, sem backfill: UUID, Workspace, owner, nome/name_key, contexto QUESTIONS_LIST, schema_version=1, JSONField(default=dict), timestamps; uniqueness do owner/context/name_key e checks locais de nome/version. O serviço valida payload com conjunto fechado de campos, tipos string, form corrente e IDs de Workspace; categoria deve estar ACTIVE. FKs CASCADE apagam filtro junto ao owner/Workspace. Não existe checker dedicado hoje. A4 recomenda diagnosticar payload incompatível/ownership em leitura; a UI pode marcar filtro stale, não reinterpretar payload antigo. V0.4.4 upgrade deixa tabela vazia; nenhum filtro default é criado.

### S5 — Domain e MasteryStateEvent

DOM-HEUR-1.0 continua on-demand/derivado. Persistem apenas eventos de transição append-only com formula_code, evaluated_on, sequência, índices/confiança e referências opcionais. domain.0001 cria a tabela sem backfill; reversão é recusada com histórico. Não criar snapshots. Guard/constraints verificam forma e contexto básico; checker atual não tem catálogo Domain. Planejar DOM-001 para referências/Workspace/shape, preservando fórmula registrada e sem recalcular score de histórico sob policy corrente. Consulta/reconciliação S5 pode gravar apenas transições aprovadas pelo lifecycle; não chamar S5 a partir do checker/side-effect test.

### S6 — Priority

PRI-HEUR-1.0 é cálculo on-demand por Subject, derivado de Domain e Reviews/Attempts efetivos, com COLLECT_MORE_EVIDENCE quando dados são insuficientes e desempate técnico aprovado por UUID. Não tem model, snapshot, migration, scheduler ou persistência Priority; não substitui a Review Queue. Serviço atual usa ordenação explícita e workspace filters. Ele chama current_domains; esse adapter pode reconciliar transições S5 conforme regra aprovada, mas não grava estado Priority. Teste com FixedClock/evaluation_date, ids determinísticos, insuficiência e fingerprint; preparar estado Domain estável ou contabilizar transições S5 legítimas separadamente.

### S7 — export, backup, restore e CEI

CEI-EXPORT-1.0 é ZIP/JSON funcional em destino vazio compatível, com schema/policies/schema_migrations estritos e reexportação semântica. O manifest é produzido por MigrationLoader(None).disk_migrations, portanto já enumera migrations presentes no checkout; validators rejeitam schema migration diferente. Sem migration S8, não se altera CEI 1.0. Export inclui fatos funcionais/históricos aprovados, inclusive MasteryStateEvent e AuditEvent sanitizado; exclui OperationReceipt, logs, credenciais e derivados correntes de Domain/Priority. Round-trip não compara recibos.

Backup SQLite é snapshot físico separado e inclui receipts presentes. create_sqlite_backup usa API de backup do SQLite, valida arquivo físico e hash/manifest sem alterar origem; validate_sqlite_backup confere formato, tamanho, hash e checks físicos. Restore atual trabalha em novo destino isolado, confere conjunto exato de migrations contra loader do código corrente, valida/reconcilia fundação e roda checker. Staging/UI S7 aplica preview, confirmação, pré-backup e adoção offline; não há rotação automática.

Consequência para recovery de V0.4.4: backup físico pré-upgrade é validável por hash/formato/integridade, mas o restore executável pelo código atual exige conjunto de migrations exatamente igual ao atual. Portanto recuperação de backup antigo exige software compatível que o produziu (ou worktree isolada do commit V0.4.4); não anunciar que o restore S7 atual aceita um schema antigo. Restore atual do candidato upgraded usa software atual em caminho isolado.

## 7. Inventário de migrations desde V0.4.4

Tag V0.4.4 contém o conjunto de migrations alvo usado no probe existente (auth.0012, attempts.0002, errors.0002, questions.0002, reviews.0002, taxonomy.0001, com dependências como accounts.0001). Comparação Git mostra **10 migrations V0.5 adicionadas**, sem edição das migrations antigas; não há migration nova em attempts, questions ou taxonomy. Ordem abaixo é por grafo de dependência/app, não um timestamp global.

| App / migration | Dependência principal; mudança efetiva | Defaults, nullability, backfill | Reverse, risco e fatos |
| --- | --- | --- | --- |
| operations.0001_initial | accounts.0001; cria AuditEvent, FKs/indexes, códigos e checks iniciais | campos opcionais de metadata nullable; sem linhas/backfill | Reverse remove tabela; após auditorias S2A perde fatos, usar restore compatível. |
| reviews.0003_reviewschedulechange_and_more | contas/attempts/questions/reviews.0002; cria ReviewScheduleChange, amplia origin_kind e constraints | origin_kind default INITIAL_ERROR; sem alteração factual de due/Review, sem backfill | Reverse perde registros de reagendamento e recusa valores/origens não representáveis. Risco de agenda/histórico. |
| errors.0003_errorcategory_category_kind_and_more | accounts.0001, errors.0002; categoria pessoal/lifecycle/merge/lock, code até 64 e descrição até 500, unique parcial e checks | colunas category_kind=STANDARD, state=ACTIVE, lock_version=1; merged_into=NULL; aplicação de default aos registros existentes; sem RunPython | Reverse remove capacidade e dados pessoal/merge/versão; só antes desses fatos. Categorias padrão V0.4 permanecem padrão/ativas. |
| operations.0002_attempt_audit_events | operations.0001; adiciona codes/entities de void/replacement e constraint de metadata | sem campo/backfill novo | Reverse perde compatibilidade com auditoria S2B. |
| reviews.0004_attempt_correction_projection | reviews.0003; superseded_at nullable, origin ATTEMPT_CORRECTION, estado SUPERSEDED e constraints atualizadas | novo timestamp null; campos existentes mantidos; sem backfill declarado | Reverse não representa ciclos reconstruídos/superseded e fatos associados; recovery após fatos. |
| operations.0003_answer_key_correction_audit | operations.0002; previous_entity_id nullable, adiciona ANSWER_KEY_CORRECTED e checks de metadados | campo novo null; sem backfill | Reverse não representa eventos de correção; não seguro após S2C. Nenhuma migration de revisão/Attempt. |
| operations.0004_remove_auditevent_audit_event_code_valid_and_more | operations.0003 + accounts.0001; entity_id nullable, QUESTION_PERMANENTLY_DELETED, shape e unicidade parcial por correlação | nullabilidade amplia; sem backfill | Reverse incompatível com evento final S2D; depois de fatos usar restore, não rollback automático. |
| reviews.0005_reviewcycle_manual_purpose_and_more | reviews.0004 + contas/attempts/questions; manual_purpose e check coerente com origin | nullable; RunPython marca ciclos MANUAL já existentes como INCLUSION; nesta sequência, a base V0.4.4 não tinha origem MANUAL, portanto não inventar linha antiga | reverse recusa MASTERY_REOPEN, limpa INCLUSION; essa classificação aprovada é o único backfill de ciclo. Não reescreve agenda/timestamps. |
| search.0001_initial | accounts.0001 + AUTH_USER_MODEL; cria SavedFilter | context_code=QUESTIONS_LIST, schema_version=1, payload dict, timestamps; nenhuma linha/backfill | Reverse descarta filtros; base V0.4.4 permanece vazia. Risco de perda de preferências, não fato de aprendizagem. |
| domain.0001_initial | accounts, attempts.0002, questions.0002, reviews.0005; cria ledger MasteryStateEvent, constraints/indexes | event table começa vazia; sem backfill de mastery; campos domain/confidence/reason/trigger/manual_cycle opcionais conforme schema | RunPython impede reverse com event rows; snapshots/upgrade reverso após fatos não são recovery. Event ledger append-only. |

Essas migrations são auditáveis por git diff --name-only v0.4.4..HEAD -- src/*/migrations/*.py, conteúdo dos dez arquivos e manifests suplementares quality/v05-s2a-migrations.json a v05-s5-migrations.json/manifests de etapa. Classificação global: aditivas/constraints, mas reverse após fatos não é downgrade seguro. A única data migration de V0.4.4 potencialmente pertinente é a classificação de ciclos MANUAL; tal origem ainda não existia em V0.4.4 e não pode virar backfill inventado. Nenhuma migration muda Attempt histórico, datas/regras de Review, revisão usada, classificação, analytics, ou cria receipts.

## 8. Base V0.4.4 e fixture reproduzível

Não foi encontrada fixture SQLite versionada nem backup binário oficial. A fonte confiável existente é MigrationExecutor usando migrations reais e project_state(v044).apps nos testes tests/test_v05_s2a_upgrade.py e tests/test_v05_s2d_upgrade.py; tests/test_v05_s5_upgrade.py prova especificamente sem backfill de mastery e a classificação normativa de ciclo MANUAL. A baseline V0.4.4 real foi verificada pelo commit da tag acima; o diff de migrations confirma que os arquivos antigos não foram alterados.

Fixture futura: reutilizar essa fronteira/harness em banco temporário/descartável; mover executor às migrations V0.4.4; construir fatos com models históricos daquela ProjectState (não models atuais e não SQL manual de um schema parecido); guardar uma fixture sintética pequena determinística, sem pessoa real. Dataset representativo dentro do que existia em V0.4.4: User/Workspace/timezone; Discipline/Subject (e Subsubject quando suportado); Questions em estados compatíveis, QuestionRevision/Alternatives; Attempts INITIAL e REVIEW válidas e classificações; ReviewCycles/Reviews com states/due dates variados; receipts legados válidos se a fixture exercitar idempotência. Não incluir ReviewScheduleChange, AuditEvent, categoria pessoal/merge, SavedFilter, MasteryStateEvent, VOIDED ou ATTEMPT_CORRECTION antes das migrations que os tornam válidos.

O teste existente S2A já cobre um Workspace, categorias padrão, hierarquia, questão/revisão/alternativas, Attempt incorreta, classificação, ciclo/Review pendente, backup antes, migração para leaves, comparação de métricas/due date, checks SQLite/FKs, 20 checks e restore de candidato. O S2D acrescenta correção/merge/cadeia e exclusão/recovery; S5 valida manual cycle e ausência de mastery backfill. Esses probes são base útil, mas o teste final S8 deve medir resultado até o grafo completo atual (incluindo S3/S5) e preencher gaps S8/CEI/PostgreSQL; não duplicar a suite anterior sem necessidade.

## 9. Upgrade, reconciliação e testes futuros

### Pipeline obrigatório

1. Criar a base V0.4.4 equivalente no diretório/DB descartável e registrar versão, migration targets e impressão sem segredos.
2. Capturar baseline semântica de linhas/fatos e analytics com evaluation_date fixa.
3. Criar backup pré-upgrade pela infraestrutura SQLite (create_sqlite_backup), preservar artefato e validar manifesto/hash/tamanho/integridade/FKs. Restaurar/validar esse backup somente com software compatível V0.4.4; não usar restore current-code que exige migration set atual.
4. Fazer cópia de trabalho protegida; migrar pelo grafo real até MigrationExecutor.loader.graph.leaf_nodes() do candidate S8.
5. Rodar PRAGMA integrity_check e foreign_key_check; executar checker read-only e fixtures negativas apenas em outras cópias isoladas.
6. Comparar fatos e projeções legados pré/pós; diferenciar colunas novas defaultadas, tabelas vazias legítimas e efeitos derivados S5 que só ocorrem quando política/serviço explicitamente os produz.
7. Verificar Domain S5 com data/clock controlados e policy DOM-HEUR-1.0, registrando apenas transições permitidas; Priority S6 com PRI-HEUR-1.0, insuficiência e desempate atuais, sem persistência Priority nem alteração da fila.
8. Fazer backup do candidate upgraded, validar e restaurar em destino novo pela S7 atual; conferir migration set, checker, hashes/reconciliação e estado do recibo conforme snapshot.
9. Exportar o candidate no CEI-EXPORT-1.0; validar/importar em destino vazio compatível e comparar semanticamente fatos incluídos; receipts são deliberadamente omitidos.
10. Testar estado S2D removido sob upgrade e restore de snapshot pós-delete. Teste separado de recuperação pré-delete usa explicitamente o backup anterior e software compatível; reportar como recuperação de snapshot, não como migration que ressuscita fato.
11. Rodar matriz crítica PostgreSQL com ambiente real descartável, conforme seção 11. Sem esse ambiente, não declarar o critério PostgreSQL GREEN.
12. Preservar backup e artefatos isolados; fechar A8 deep, testes/regressões e gate somente na futura sessão autorizada de execução.

### Reconciliation pré/pós

Devem permanecer iguais semanticamente: Workspace id/owner/locale/timezone; hierarquia e status; Questions, revisões publicadas, is_current, alternativas/gabarito; Attempts e relações a revisão/alternativa/Review, resultado, instante/fuso/data local/status/idempotency key; classificações/revisões; ciclos/Reviews, first_due_date, current_due_date, sequência/stage/state/origin/policy/timestamps; receipts que já existiam; analytics registered, performed, attempts, correct/incorrect/classified/unclassified e totais due/overdue/future para a mesma data/fuso.

Mudanças novas previstas sem alterar história: categorias antigas ganham STANDARD, ACTIVE, version 1, merged_into=NULL; campos de origin/purpose/timestamp adicionais recebem defaults/nullability definidos nas migrations; SavedFilter/AuditEvent/ReviewScheduleChange/MasteryStateEvent começam vazios se não havia fatos correspondentes. ReviewCycle.manual_purpose só classifica como INCLUSION ciclos MANUAL que já fossem possíveis numa base da migração que os conheça; não inventar ciclos V0.4.4. Analytics continuam projeções por query; não comparar cache ausente. Fatos derivados Domain/Priority só existem conforme S5/S6 após consulta/ação, sem backfill no upgrade.

Attempts V0.4.4: status legado VALID, replaces_attempt=NULL, nenhum VOIDED ou replacement inventado. Revisões e agenda histórica não se movem. Categoria pessoal/merge/revision/classification não é criada por migration cosmética. SavedFilter permanece ausente. OperationReceipt antigo se preserva semanticamente; idade >30 dias é válida e não o expira.

### Testes por área

- **Checker/read-only:** fingerprint determinístico antes/depois de todos os fatos/tabelas e contagens: accounts/Workspace; taxonomy; origins/catalog; Questions/revisions/alternatives; Attempts; classifications e revisões; cycles/Reviews/schedule changes; categories; SavedFilters; MasteryStateEvents; AuditEvents; OperationReceipts; django_migrations. Rodar service e management command em banco saudável e em DB isolado com findings. Conferir também hash do SQLite e existência/conteúdo de -wal, -shm, journal e artefatos de teste; nenhuma agenda, timestamp, Domain/Priority, AuditEvent ou receipt deve mudar. Logging de saída é observabilidade técnica, sem texto funcional/segredo.
- **Failure fixtures:** inserir por SQL somente inconsistências que schema/service podem não impedir (relações cross-Workspace com FKs válidas, origem composta discordante, ciclo/branch quando constraints não barram, receipt com alvo incompatível, SavedFilter com JSON válido mas schema/ID/owner inválidos, MasteryEvent com Workspace/trigger/cycle incompatível, AuditEvent com metadata proibida). Usar DB temp/cópia; respeitar CHECK/unique ativos, e não contornar schema quando o teste deveria demonstrar prevenção pelo DB. Provar finding exato e fingerprint inalterado. Casos inválidos impossíveis devido CHECK/unique são testes de constraint/service, não do checker.
- **S2A/S2B/S2C/S2D:** retry idempotente/hash conflitante; reschedule/manual inclusion atômicos; Attempts status/void/replacement/cadeia; edição de gabarito prospectiva; merge/categoria; exclusão e fault injection; retention AuditEvent 90d; receipt 30d floor sem expiry geral.
- **Upgrade/migration/reconciliation:** V0.4.4 target histórico, migrations reais todas, defaults/nulls e data migration, ids/fatos/projeções; backup antes, candidato depois, recovery isolada; reverse probes só antes de fatos ou em schema sem risco, nunca prometer rollback com dados novos.
- **S5/S6:** leituras e transições Domain separadas; no event backfill; preserve formula_code; event/ref Workspace; date fixada; prioridade determinística e COLLECT_MORE_EVIDENCE; prova de nenhuma tabela/campo Priority e Review Queue inalterada. Não reabrir fórmulas S4/S6.
- **S7/CEI:** schema_migrations no manifest igual ao loader do candidate; export → validator/reader independente → import em banco funcional vazio → reexport/semantic compare. Validar ausência esperada de receipts no CEI e presença em backup físico.
- **Recovery:** hash/original do backup preservado; restore para path novo; checks físico/FK/checker; restore pós-delete segue apagado; pré-delete backup só recupera por fluxo deliberado S2D com código compatível.
- **PostgreSQL:** seção 11; nenhum fake backend ou inferência de portabilidade substitui servidor real.

## 10. Backup, restore, downgrade e riscos

Reusar apenas modules.data_management.services.create_sqlite_backup, validate_sqlite_backup, restore_sqlite_backup e, no fluxo S7, o staging/offline apply existente. Não criar segundo mecanismo de restore. Manter uma cópia pré-upgrade imutável e uma cópia candidata; confirmar manifests, SHA-256, tamanho e checks físicos. Restore sempre para destino que não existe. Backup V0.4.4 requer software compatível com schema/migration daquele snapshot; backup candidato usa software candidate. A decisão de recibos explicita que restauração reinstaura receipts exatamente como estavam no snapshot, sem gerar memória de operações posteriores.

Distinções obrigatórias:

- **Reversing migrations:** executa operações reversas no schema/dados; pode perder fatos ou falhar por guards (Domain events e ciclos MASTERY_REOPEN); não é downgrade geral.
- **Restoring old backup:** retorna o banco inteiro ao snapshot, inclusive ao estado anterior a operações posteriores; recovery isolado e software compatível são obrigatórios. Um backup pré-delete é a recuperação S2D aprovada.
- **Application downgrade:** executar versão antiga de código contra schema de sua versão; requer banco/backup compatível, não é garantido só por migrations reversíveis.
- **CEI import:** transfere somente fatos funcionais para instalação vazia compatível; não restaura arquivo/schema/receipts e não é rollback.

Riscos a tratar no A8/testes:

1. Corrupção/perda de dados por migration, reverse ou cópia inadequada.
2. Backfill semântico indevido de attempts, revisão, categoria, classificação, ciclos ou mastery.
3. Reinterpretação histórica de resultados/agenda por policy corrente.
4. Relações cross-Workspace com FKs individualmente válidas.
5. Checker mutável ou false negative, incluindo gaps SAV/Domain/Audit age/OPS-001.
6. Checker incompatível com JSON/NULL ou com SQL alterado entre engines.
7. Restore incompatível por version/migration ou confundido com import/rollback.
8. CEI incompatível por lista estrita de migrations/fields; receipts foram excluídos por decisão S7.
9. OperationReceipt envelhecido tratado incorretamente como expirado, ou retry tentando ressuscitar agregado S2D; evitar ambos.
10. Divergência SQLite/PostgreSQL em constraints parciais/CHECK, locks, transação e ordenação.
11. Domain/Priority executados em harness sem separar transições MasteryStateEvent legítimas.
12. Fixture histórica que só parece V0.4.4; ancorar em tag/graph e models históricos.

## 11. PostgreSQL — inventário, disponibilidade e matriz crítica

Config de development, test e production_local em src/config/settings/*.py chama helper sqlite_database; pyproject.toml/uv.lock declaram Django e ferramentas, sem driver PostgreSQL localizado; não há backend PostgreSQL, DATABASE_URL/PG config, testes/caminho CI PG, comando psql, serviço PostgreSQL, Docker/Podman ou variáveis de ambiente PG visíveis nesta sessão. Não foi instalado/baixado/alterado ambiente. **Disponibilidade real: NOT_AVAILABLE.** A busca não imprimiu valores de ambiente/secrets.

**Adendo de execução — availability changed after A4 audit (2026-09-25).** O diagnóstico original acima descreve a sessão de planejamento, não o ambiente atual. Nesta execução, `C:\Program Files\PostgreSQL\18\bin\psql.exe --version` retornou `psql (PostgreSQL) 18.6` e a porta local `127.0.0.1:5432` respondeu. Assim, o servidor está **AVAILABLE / VERIFIED_TCP**; a versão do *servidor* ainda depende de `SELECT version()` autenticado. `psql -w` retornou `fe_sendauth: no password supplied` (exit 2), não há `PGPASSWORD` ou pgpass disponível ao processo e o Python local não contém `psycopg`/`psycopg2`. A matriz crítica continua pendente de autenticação segura e driver; nenhum PASS PostgreSQL foi inferido desses probes. Usar somente database descartável criado/identificado para S8, sem senha em Git/evidence.

**Atualização posterior nesta execução:** a necessidade do driver foi comprovada e `uv add --dev 'psycopg[binary]==3.3.6'` adicionou `psycopg`/`psycopg-binary` ao perfil de desenvolvimento e lock; import local confirmou versão 3.3.6. O bloqueio restante para conexão autenticada é `BLOCKED_POSTGRES_CREDENTIALS`. Não foi criado database PostgreSQL nem executado teste destrutivo nele. O gate final deverá ser repetido após esta alteração de dependência.

O plano oficial exige constraints críticas em PostgreSQL. A futura etapa S8 pode avançar SQLite/checker/recovery, mas não pode fechar a evidência S8/GREEN nem afirmar suporte à matriz PG até que um banco de teste descartável autorizado e driver/configuração executável sejam disponibilizados. Não instalar nem ativar automaticamente. O teste deve registrar versões/backend sem credenciais.

| Regra | SQLite atual | PostgreSQL — risco relevante | Prova exigida |
| --- | --- | --- | --- |
| FK direta | habilitada/verificada por foreign_key_check; FK simples | Ambas garantem target; nenhuma FK simples garante Workspace combinado | invalid target rejeitado pelo banco e referência cross-Workspace válida isoladamente barrada por service/checker. |
| UNIQUE/partial UNIQUE | usada por Attempt inicial/Review, category pessoal, receipt e outros | ambas suportam índices/constraints parciais relevantes; diferenças de criação/NULL devem ser observadas | duplicata idempotency, uma INITIAL válida, Review pendente e category name; conflito íntegro/atômico. |
| CHECK/enums em texto | choices Django não bastam; migrations criam checks | ambas avaliam CHECK, mas testar explicitamente combinações anuláveis e operadores emitidos pelo ORM | ciclo Review, Attempt VOIDED, audit shape, mastery event, category lifecycle; NULL boundary. |
| Nullability | columns Django explícitas; check constraint pode coexistir com null | validação do DB e comportamento de CHECK/NULL | distinguir NULL válido de string vazia/valor inválido em events, metadata, saved filter e schedules. |
| JSONField | JSON em SQLite/JSON1 e validador S3 em Python | jsonb e operadores do backend podem divergir | payload fechado segue mesmo validator; desconhecido/foreign/archived rejeitado; não depender de JSON-path específico do engine. |
| Transaction | atomicidade/rollback; SQLite single writer e helpers críticos SQLite-specific | níveis/locks concorrentes diferentes | falha entre gravações não deixa metade de reschedule/audit, correction, deletion/reconstruction. |
| select_for_update | SQLite não oferece lock de linha equivalente | PostgreSQL efetivamente bloqueia linha | duas correções/voids/deletes concorrentes no mesmo aggregate; CAS/version e idempotência preservados. |
| Ordering | resultados precisam .order_by explícito | planner/índice podem mudar ordem natural | Review sequence e Priority UUID tie-break idênticos com data fixa; nunca depender de ordem implícita. |
| Isolamento Workspace | guards e SQL do checker detectam muitas relações compostas | FKs válidas cross-tenant também são aceitas; guard continua indispensável | relações foreign com PKs reais, leitura/escrita bloqueada e nenhuma fuga por adapter/import. |
| OperationReceipt | unique por Workspace/kind/key; idade não expira | unique/transaction em concorrência devem manter retry | mesmo hash retorna resultado, hash divergente conflita, receipt de >30d continua válido; não criar purge. |

PostgreSQL não exige testar checker SQLite PRAGMA como se portável. Caso a execução registre que run_integrity_check é deliberadamente SQLite-only, testar nele as invariantes do candidate e cobrir no PostgreSQL constraints/services na matriz reduzida; qualquer ampliação multi-engine exige escopo/decisão própria.

## 12. Schema drift e comandos desta auditoria

Executado diagnóstico permitido, com Python local .venv\Scripts\python.exe e profile descartável de teste:

~~~powershell
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run --settings=config.settings.test
~~~

Resultado: No changes detected, exit 0. Nenhum migration foi gerado. Também foram executados comandos Git read-only (branch, rev-parse, status, diff --check, rev-list), buscas/leituras de fontes, inventário do grafo de migrations, settings/dependencies, comandos e serviços PostgreSQL. Não foram executados testes funcionais, A8 ou quality gate nesta auditoria.

## 13. Plano ordenado para GPT-6 Sol / High

| Etapa | Objetivo e arquivos prováveis | Prova/teste | Risco e rollback | Done When |
| --- | --- | --- | --- | --- |
| 1. Harness histórico | tests/test_v05_s8_upgrade.py/fixture helper e possivelmente script de probe isolado; targets V0.4.4 da tag | MigrationExecutor + historical app registry; dados V0.4.4 determinísticos; migration traceability unchanged | drift de target/fixture; descartar somente DB temporário; restaurar backup compatível | Schema/state V0.4.4 reproduzíveis, hashes e migrações antigas conferidos. |
| 2. Backup e upgrade | reutilizar data_management.services; migrations existentes | backup pré validado; upgrade a current leaves; SQLite/FK; baseline semantic compare; candidate restore isolado | perda/backfill; manter original imutável e candidate descartável; rollback por backup/software compatível | upgrade conserva fatos e recovery isolado reproduz snapshot correto. |
| 3. Fechar checker/catálogo | operations/integrity.py, comando, tests/test_integrity_checker.py, docs/evidence checker | fingerprints completos, fixtures cross-Workspace e estruturas negativas; catálogo ID único; CLI 0/2/3; sanitizer | falso positivo/negativo e vazamento; somente adicionar IDs e manter saída read-only, reverter candidato/código antes de liberar | V05-INV aplicado com mecanismo/teste explícito; nada muta; gaps SAV/DOM/AUD/OPS resolvidos ou justificados. |
| 4. Compatibilidade por camada | testes S2A–D, S3, S5, S6 | preserved legacy facts, SavedFilter empty/valid, Domain event semantics, Priority deterministic/insufficient, timezone/date fixos | reinterpretar história/transição Domain; usar fixtures isoladas e separar leitura de lifecycle write | S2A–S7 semantic facts concordam; nenhum snapshot/Priority/Review novo indevido. |
| 5. Portabilidade/recovery | test_v05_s7_portability.py, data_management, docs S7 | candidate export→validate→empty import→semantic compare; receipt ausente CEI/retida no backup; restore pós-delete e recovery pré-delete separados | snapshot/engine incompatível; nunca publicar sobre ativo, usar destinos novos e software compatível | restore/version boundary e CEI-1.0 comprovados com relatório sanitizado. |
| 6. PostgreSQL crítico | testes de integração segregados e settings de teste/driver somente se autorizados e necessários | executar matriz §11 em PostgreSQL descartável real; preservar logs de versão/resultado sem secrets | ausência/compartilhamento de DB ou driver errado; parar essa prova até ambiente autorizado, sem instalação automática | todas as provas críticas rodam em servidor real; nenhum PASS inferido de SQLite. |
| 7. Revisão/fechamento S8 | testes focados/regressões, quality/v05-s8-integrity-compatibility-result.md, quality/ e depois estado formal | A8 deep APPROVED Blocker 0/Major 0; gate completo exit 0 observado; git diff --check | gate inconclusivo não fecha S8; corrigir somente findings autorizados e repetir evidência | Só então, conforme tarefa, atualizar estado/arquivar; não iniciar S9+. |

## 14. Checklist A8 deep e riscos de escopo

- Autoridade/baseline/ausência de S9 leakage.
- Checker 22 IDs preservados; novos IDs documentados; ausência de escrita, repair, scheduler e purge.
- V05-INV-001–014 mapeados para fato/model, guard/transaction/constraint/checker e teste sem duplicação cega.
- Upgrade V0.4.4 por migrations reais com backup pré válido; facts/defaults/legacy/analytics e migration reversibility verificados.
- S2B chains e S2C prospective revision/historical link; S2D sanitized audit/90d/no content recovery, com exceção explicitada de pre-delete backup recovery.
- OperationReceipt = floor 30d, normal indefinite, no generic expiration; retry, backup/restore, upgrade e CEI semantics aderentes ao novo adendo.
- S3 SavedFilter ownership, payload/schema and no legacy rows; S5 no mastery backfill/snapshot; S6 policy unchanged/derived/no queue mutation.
- S7 CEI migration list and semantic round-trip; physical backup separated from functional export.
- PostgreSQL tested only on real authorized disposable server; if unavailable, blocker remains and no false GREEN.
- Teste de fingerprint e fixtures negativas não tocam DB real; logs e artifacts não têm segredo/dados pessoais reais.
- Gate final somente na sessão futura; exit code 0 real; A8 Blocker 0/Major 0; git diff --check.

## Migration assessment

**Migration: NO para o escopo S8 planejado neste A4.** As evidências concretas mostram que a evolução proposta é read-only catalog/check/test harness e compatibility proof; S3 SavedFilter e S5 MasteryStateEvent já têm schema e constraints próprios; OperationReceipt já tem created_at, unicidade e floor de 30 dias; a decisão humana proíbe expiry/purge geral e explicitamente não autoriza expires_at, tombstone ou outra persistência. O upgrade V0.4.4 usa migrations existentes, não uma migration artificial de S8. makemigrations --check --dry-run resultou No changes detected.

Esta decisão não antecipa qualquer mudança de schema. Se Sol High encontrar uma invariável crítica cuja prevenção exija nova persistência/constraint irredutível, parar antes de migration e solicitar autorização/addendum humano; não reinterpretar Migration: NO como permissão. PostgreSQL indisponível é bloqueio operacional da prova PG, não razão para criar migration.
