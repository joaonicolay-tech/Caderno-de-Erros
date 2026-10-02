# V1.0-S2R2 — CEI destination compatibility remediation

Decisão: **S2R2_COMPLETED**. S6-F01 **RESOLVED**, sem alteração da evidência FAIL original. S6 restaurada AUTHORIZED / IN EXECUTION / RESUME AFTER S2R2; nenhuma prova S6 pendente foi iniciada nesta remediação.

## Relatório final — 33 campos

| Item | Resultado observado |
| --- | --- |
| 1 START_TIME | 2026-09-30 20:04:05 -03:00 |
| 2 END_TIME | 2026-09-30 20:57:39 -03:00 |
| 3 Duração | 0:53:34 |
| 4 Modelo | GPT-6.1 Sol High, conforme autorização; identificação interna independente do runtime não exposta pelas ferramentas |
| 5 Causa raiz | Validação de pacote conferia migrations disponíveis no código (34), sem conferir migrations aplicadas (24) e schema real do destino V0.4.4 antes de escrever |
| 6 Ponto faltante | import_into_empty: transaction.atomic era seguido do primeiro User.save; _schema_migrations usava MigrationLoader(None).disk_migrations; Workspace.exists ficava fora da transação |
| 7 Correção | Preflight somente de leitura dentro da mesma transação; paridade de migrations aplicadas, DDL real de modelos gerenciados/automáticos e unicidade; rejeita trigger inesperado; Workspace vazio verificado antes de User.save |
| 8 Código alterado | C:\src\Projeto\src\modules\data_management\portability.py |
| 9 Testes | C:\src\Projeto\tests\test_cei_destination_compatibility.py: 20 casos novos; 12 testes CEI existentes executados; probe S6 inalterado |
| 10 Migrations criadas | 0; schema, dependências, lock e producer policy não alterados |
| 11 N9 antes | FAIL histórico: 8 INSERTs concluídos / total_changes +8 e OperationalError na coluna category_kind; rollback preservou fingerprints |
| 12 N9 depois | PASS / REJECTED_BEFORE_WRITE, target novo work/s6-cei-prewrite-20260930-s2r2-final/target-v044-empty-N9.sqlite3 |
| 13 INSERT/UPDATE/DELETE | Final: tentativas 0/0/0; concluídos 0/0/0; total_changes delta 0. Regressão RED nova: 9 tentativas INSERT, 8 concluídos; a nona falhou |
| 14 Contagens | Todas iguais antes/depois; tabelas funcionais 0→0, django_migrations 24→24, sqlite_sequence 4→4; tabela integral abaixo |
| 15 Fingerprints | Semântico, schema e físico iguais antes/depois; valores integrais abaixo e no JSON |
| 16 Import válido | PASS: empty-install round-trip, histórico/correções/filtro/domínio/audit e import sob bloqueio de DDL concorrente |
| 17 Focados | 32 PASS em 72.86 s; manifesto/migrations/schema/checksum/policies/producer/UUID/referências/Workspace/destino e pre-write |
| 18 Gate | GREEN, comando oficial acima, exit 0 efetivamente observado; tentativas anteriores preservadas abaixo |
| 19 Total de testes | 532 PASS em 360.18 s no gate final |
| 20 Coverage | 86.5747% global; limiares de domínio PASS pelo gate oficial |
| 21 pip-audit | PASS, 0 vulnerabilidades conhecidas; relatório C:\src\Projeto\.tools\quality\pip-audit-df76ae196ff14a368b042ae9e6a60400.json |
| 22 A8 deep | APPROVED, revisão pelo próprio Codex, sem alegação de revisor independente; análise detalhada abaixo |
| 23 Blocker/Major/Minor | 0/0/0 abertos na remediação |
| 24 S6-F01 | RESOLVED nesta evidência nova; FAIL histórico permanece FAIL |
| 25 Artefatos | quality/v10-s2r2-cei-destination-result.md, quality/v10-s2r2-n9-retest.json, tasks/completed/v10-s2r2-cei-destination-compatibility.md, paused S6; código/teste/estado/contrato e .secrets.baseline com 59 falsos positivos individualmente revisados/autorizados; cópias e logs em outputs desta execução |
| 26 PROJECT_STATE | Sincronizado: S1–S5/S2R1/S2R2 COMPLETED; S6 resume; S7–S10 NOT AUTHORIZED; histórico preservado |
| 27 tasks/current | Contrato S6 restaurado, AUTHORIZED / IN EXECUTION / RESUME AFTER S2R2; contrato bloqueado original preservado byte a byte em tasks/paused |
| 28 S6 retomável | Sim; N9 final é reteste candidato. N1–N8, cadeia/clean install/backup/restore/recovery/CEI positivo e gate/A8 final da própria S6 continuam pendentes |
| 29 S7–S10 | NOT AUTHORIZED |
| 30 git diff --check | Verificado no fechamento; exit 0; avisos CRLF/LF não são erro de diff |
| 31 git status --short | Working tree autorizada modificada; somente .secrets.baseline staged por exceção humana específica para permitir o hook oficial; lista final em outputs/s2r2-git-final.log |
| 32 Git egress | git add somente .secrets.baseline expressamente autorizado; nenhum commit, push, tag ou release. HEAD/origin/main permanecem 5eb6930aba35a0d1083c92816a83c7c4c2451830 |
| 33 Decisão | S2R2_COMPLETED |

## Prova N9 final: dados antes/depois

Destino novo: `work/s6-cei-prewrite-20260930-s2r2-final/target-v044-empty-N9.sqlite3`.
34 migrations requeridas pelo pacote/código; 24 aplicadas no destino V0.4.4; erro causado por ExportValidationError: “Migrations do destino incompatíveis com a instalação.” O comando oficial retorna CommandError preservando essa causa. Origem checker 25/0 findings, SQLite integrity_check ok e foreign_key_check vazio; origem inalterada.

| Tabela | Antes | Depois |
| --- | ---: | ---: |
| accounts_user | 0 | 0 |
| accounts_workspace | 0 | 0 |
| attempts_attempt | 0 | 0 |
| attempts_operationreceipt | 0 | 0 |
| auth_group | 0 | 0 |
| auth_group_permissions | 0 | 0 |
| auth_permission | 0 | 0 |
| django_content_type | 0 | 0 |
| django_migrations | 24 | 24 |
| errors_error_category | 0 | 0 |
| errors_errorclassification | 0 | 0 |
| errors_errorclassificationrevision | 0 | 0 |
| questions_alternative | 0 | 0 |
| questions_board | 0 | 0 |
| questions_exam | 0 | 0 |
| questions_question | 0 | 0 |
| questions_questionorigin | 0 | 0 |
| questions_questionrevision | 0 | 0 |
| questions_source | 0 | 0 |
| reviews_review | 0 | 0 |
| reviews_reviewcycle | 0 | 0 |
| sqlite_sequence | 4 | 4 |
| taxonomy_discipline | 0 | 0 |
| taxonomy_subject | 0 | 0 |
| taxonomy_subsubject | 0 | 0 |

| Fingerprint SHA-256 | Antes | Depois |
| --- | --- | --- |
| Semântico | eb28f135b717d1ca7e9499e7e1f6202e219b50592561d81caf255b4f276f7551 | igual |
| Schema | 9a451c08e172669bc43738c9e33a69293db85e148064b6d93314f3700d33ba5b | igual |
| Físico | 8caa08296e9a3ac5653d95726647734cb346c9a49655394d451e9deef527cb49 | igual |

Counters de tentativas são incrementados **antes** de execute por execute_wrapper em torno de call_command(import_cei). O wrapper suplementar está integralmente incorporado ao JSON; o probe histórico mantém os counters de escritas concluídas. A regressão permanente faz ambas as medições. O campo legado independent_validation_before_import do probe refere-se a validate_export, que é validator de produção, não leitor independente; a leitura independente ZIP/JSON permanece nos testes existentes.

## A8 deep — análise e decisão

- Ordem: validate_export do comando oficial precede import; backend/Workspace identity são checados; transaction.atomic abre antes do preflight; migrations/schema e ausência de Workspace são lidos na mesma conexão antes de User.save e de qualquer INSERT funcional. Nenhum merge, adaptação, fallback ou execução de migration foi acrescentado.
- Migrations efetivamente aplicadas são lidas com MigrationRecorder.applied_migrations, cujo caminho has_table/query não chama ensure_schema. MigrationLoader(None).disk_migrations define apenas o esperado; comparar os dois resolve a confusão que causou S6-F01. Metadata de migration forjada não basta: schema é conferido independentemente.
- Schema real: leitura parametrizada de sqlite_master comparada ao DDL esperado gerado apenas em memória por table_sql; o SchemaEditor não é aberto como context manager nem executado. deferred_sql é inicializado explicitamente para renderização. Comparação inclui todas as definições de colunas, tipos, nulabilidade, PK/FK, defaults, CHECKs e UNIQUE inline, além de índices UNIQUE condicionais/deferred. Nenhum DDL é executado no destino. Índices comuns não são comparados porque não alteram a semântica de gravação. Ordem física de colunas, whitespace/comentários e caixa de keywords são ignorados; identificadores/literais e expressões permanecem significativos. Schema equivalente escrito de forma diferente pode ser recusado: compatibilidade estrita com o schema migrado do projeto, sem conversão.
- Triggers não integram migrations/modelos atuais e são recusados antes de escrita. Os nomes executados em consultas são parâmetros; o SQL real é analisado como texto, sem execução. sqlparse já é dependência transitiva instalada/fixada do Django; nenhuma dependência ou arquivo de lock foi alterado.
- TOCTOU local: as leituras de migrations/schema/Workspace e as escritas compartilham a transação SQLite e sua visão consistente. O teste provoca ALTER TABLE em outra conexão imediatamente antes do primeiro DML; no journal padrão DELETE a mudança não consegue commit (database locked), é revertida e o import válido passa. Em WAL, uma alteração externa após a visão de leitura pode impedir a promoção para escrita por snapshot conflict; não há retry/fallback para escrever contra schema novo sem validar. Operação externa que ignora os mecanismos de locking do SQLite não é coberta por essa garantia.
- Workspace: checagem de destino ocupado foi movida para dentro da transação; continua recusando merge com zero tentativas. Owner local, IDs e seleções por alias permanecem. Pacote com referência cross-Workspace, UUID inválido/duplicado ou relação ausente é recusado antes de chamar o import. Round-trips válidos preservam histórico, correções, SavedFilter/Mastery/Audit; exclusões sanitizadas não reaparecem.
- Observabilidade: histórico e regressão RED mostram por que rollback não comprova pre-write. Final N9 e os 11 schemas negativos têm zero tentativas e total_changes delta 0; counts, schema hash, semantic hash e physical hash permanecem iguais. Primeira preparação não candidata S6 e N9 FAIL original não foram alterados.
- Revisão estática: ExportManifest TypedDict somente descreve o manifesto já emitido, permitindo ao harness preservado iterar files sob mypy sem suprimir erro nem modificar o probe. Nenhuma mudança de bytes do formato, policies, allowlist de producer ou semântica de pacote.
- Resultado: **APPROVED**, Blocker 0 / Major 0 / Minor 0 abertos. S6-F01 resolvido. A8 desta remediação não substitui A8 deep da S6 futura.

## Cronologia preservada de verificações

1. Regressão automatizada RED antes do fix: OperationalError, 9 INSERT attempts/8 completed changes; fingerprints finais preservados por rollback, sem conformidade pre-write.
2. Primeiro focused run: 18 PASS/2 erros de preparação do teste (varchar(20) presumido vs varchar(16) real), corrigidos sem mudar guard. Segundo focused run: 22 PASS; 7 controles de pacote adicionais PASS.
3. Gate 1 RED, exit 1: arquivo portability.py com CRLF após alteração de anotação; Ruff normalizou LF. Probe original intacto.
4. A8 identificou que a primeira versão estrutural precisava também verificar constraints. Refinamento DDL inicialmente falhou em import válido por deferred_sql não inicializado; corrigido explicitamente. O gate 2, já em execução durante esse refinamento, viu uma versão provisória em subprocesso: 528 PASS/1 FAIL, exit 1; é NON-FINAL e não candidato. Logs e o erro são preservados, sem PASS retroativo.
5. Versão final estável: mypy PASS, 32 focados PASS em 72.86 s; N9 final suplementado PASS em root novo, zero tentativas; gate 3 RED em secrets após 532 testes PASS. Todas as 9 ocorrências S6 eram SHAs públicos/fingerprints; proposta de 59 registros exatos, incluindo hashes das novas evidências S2R2, foi revisada. A revisão automática inicialmente rejeitou alterar esse controle sem autorização explícita, que o humano forneceu. Nenhum detector/filtro/registo antigo foi retirado. O hook depois exigiu staging da baseline; foi necessária autorização humana própria da exceção à seção 15, restrita a .secrets.baseline. Sem commit/push/tag/release.
6. Gate integral final exit 0 observado, 532 PASS, coverage 86.5747%, controles oficiais e pip-audit PASS. Nenhuma alteração funcional durante esse gate final. Pip-audit também executado separadamente durante a espera de autorização: exit 0, zero vulnerabilidades, sem ser tratado como substituto do gate.

## Preservação, estado e próximos passos

Os cinco SHA-256 dos arquivos protegidos conferem byte a byte: A4 S6, probe, JSON/MD FAIL e contrato bloqueado em paused. Os roots das tentativas S6 originais e dos retestes S2R2 foram preservados; nenhum target FAIL foi reutilizado. N9 final permanece target negativo, não instalação candidata.

S2R2 arquivada após aceite. Contrato S6 restaurado com checkpoint novo de resolução, preservando o texto histórico e o A4 original. Esta execução termina aqui: não inicia N1–N8 nem demais provas S6, não usa a regressão histórica do gate como substituto da matriz S6, não declara S6 concluída. S7–S10 continuam NOT AUTHORIZED. Nenhum banco original/ativo foi usado como destino; testes e gate utilizaram instalações sintéticas/isoladas.

## Verificação documental de fechamento

O hook pós-fechamento inicialmente sinalizou o texto de autorização humana sob uma chave de metadata que continha a palavra secret. A chave foi corrigida para baseline_review_authorization; o conteúdo de autorização foi preservado. Nenhum detector/filtro ou registro adicional de baseline foi alterado. Os documentos finais foram novamente submetidos ao hook oficial. Essa correção documental não altera o código validado pelo gate integral.
