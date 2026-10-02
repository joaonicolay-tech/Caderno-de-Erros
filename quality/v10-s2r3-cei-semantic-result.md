# V1.0-S2R3 — CEI semantic pre-write validation

**Decisão: S2R3_COMPLETED. S6-F02 RESOLVED.**

## Relatório final — 40 campos

| # | Campo | Resultado |
| --- | --- | --- |
| 1 | START_TIME | 2026-09-30 22:29:35 -03:00 |
| 2 | END_TIME | 2026-09-30 23:05:20 -03:00 |
| 3 | Duração observada | 0:35:45 |
| 4 | Modelo | GPT-6.1 Sol High — autorização humana específica, preservada no contrato |
| 5 | S6-F02 original | Major/P1: pacote estruturalmente aceito; 24 INSERTs commitados; checker posterior encontra quatro violações. Evidência original intacta. |
| 6 | Quatro invariantes | ATT-001 resultado/gabarito/revisão; ERR-001 classificação em tentativa correta; REV-001 origem INITIAL_ERROR correta; REV-002 review D1 ancorado em tentativa correta. |
| 7 | Causa raiz | Preflight estrutural não verifica essas relações semânticas; checker em conexão SQLite separada mode=ro dentro do atomic vê o estado vazio commitado anterior. |
| 8 | Validação ausente | Entre _validate_relations e retorno ValidatedExport; também antes de User.save/INSERT no import direto. O checker possui SQL normativo, mas não enxerga os fatos não commitados nessa conexão. |
| 9 | Solução | Reutilizar as quatro consultas SQL normativas em projeção privada do payload; repetir no import sobre deepcopy usado nos INSERTs, bloqueando mutação posterior do objeto. |
| 10 | Staging/in-memory | Projeção relacional SQLite :memory: com oito conjuntos CEI. Há CREATE/INSERT apenas nessa RAM privada; nenhum arquivo/banco/alias de staging no destino. Destino final permanece sem escrita. |
| 11 | Código alterado | src/modules/data_management/portability.py (preflight e snapshot); src/modules/operations/integrity.py (somente accessor invariant_sql_rules, cinco linhas). Alterações S2R2 anteriores preservadas. |
| 12 | Testes novos | tests/test_cei_semantic_prewrite.py (11 casos); tests/probe_v10_s2r3_semantic.py (regressão opt-in exata). Nenhum teste histórico alterado. |
| 13 | Migrations | 0 novas; nenhum model/schema alterado; makemigrations --check --dry-run PASS. |
| 14 | Formato CEI | CEI-EXPORT-1.0 / format_version 1.0 / produtores V0.5 e V1.0 / policies existentes inalterados. |
| 15 | RED histórica | Probe S2R3 antes do fix: exit 2, ACCEPTED, 24 tentativas/completed INSERTs, total_changes +24, commit sem exceção; checker 25 checks/4 CRITICAL. Pacote exato original, alvo novo NON-CANDIDATE, log e JSON preservados. |
| 16 | Reteste S6-F02 | PASS / REJECTED_BEFORE_WRITE. Mesmo pacote histórico byte a byte; destino novo work/s2r3-final-20260930/target.sqlite3; erro explícito ATT-001, ERR-001, REV-001, REV-002. |
| 17 | INSERT/UPDATE/DELETE | Tentativas 0/0/0; completed 0/0/0 no destino final. |
| 18 | total_changes | Delta 0 na conexão SQLite real do destino. |
| 19 | Contagens | Todos os 29 conjuntos/tabelas físicos antes = depois; django_migrations=34; demais tabelas vazias. Matriz completa no JSON de reteste. |
| 20 | Fingerprints | Semântico, schema e físico antes = depois; hashes exatos na seção de evidência abaixo. |
| 21 | Import válido | VALID_IMPORT_PASS: histórico INITIAL_ERROR e round-trip de todos os 21 conjuntos, checker independente 25/0; casos existentes com correções, revisões, filtros, domínio, auditoria, relações, policies e UUIDs PASS. |
| 22 | Regressão S6-F01 | N9 PASS em target V0.4.4 novo: 0/0/0 tentativas, zero DML completo/row_changes, contagens e fingerprints preservados; probe/CLI histórico intacto. |
| 23 | Quatro invariantes — testes | Cada uma isolada + combinação, via ZIP reader e objeto validado posteriormente alterado: 10 negativos PASS com zero-write; sem criar regras novas. |
| 24 | Testes focados | 43 PASS / 118,54 s / exit 0. Primeiro run: 39 PASS/4 FAIL em 128,49 s por fixture QUESTION_ACTIVATION, corrigida para INITIAL_ERROR legado; log/XML originais preservados. |
| 25 | Gate integral próprio | GREEN / exit 0 observado / 533.11 s; Ruff/mypy/checks/migration/coverage/secrets/pip-audit PASS. Não reutiliza o gate anterior S6. |
| 26 | Total de testes | 543 PASS no gate / 440.29 s; 11 testes novos. |
| 27 | Coverage | 86.6284362% — PASS no gate oficial. |
| 28 | pip-audit | PASS / 0 vulnerabilidades conhecidas / auditoria integral concluída. |
| 29 | A8 deep | APPROVED; revisão do agente executor, sem alegar reviewer independente. Evidência própria em quality/v10-s2r3-a8-deep.json. |
| 30 | Blocker/Major/Minor | 0/0/0 abertos na S2R3; quatro CRITICAL do checker permanecem na evidência RED histórica. |
| 31 | S6-F02 final | RESOLVED pela S2R3; FAIL original preservado. |
| 32 | Artefatos | Relatório, RED, F02, N9, preservação, consultas normativas, focados, gate, A8 deep e verificação final novos v10-s2r3-* em quality/ e outputs/; logs/provas brutos em work/. |
| 33 | PROJECT_STATE | Sincronizado: S2R3 COMPLETED; S6 AUTHORIZED / IN EXECUTION / RESUME AFTER S2R3, ainda não concluída; histórico bloqueado mantido. |
| 34 | tasks/current | S2R3 arquivada em tasks/completed/v10-s2r3-cei-semantic-prewrite.md; tasks/current.md restaura a S6 e preserva seus checkpoints. |
| 35 | S6 retomável | Preparada para execução futura. Repetir somente provas CEI diretamente afetadas, gate integral final próprio e A8 deep final. Nenhuma retomada funcional S6 nesta remediação. |
| 36 | S7–S10 | NOT AUTHORIZED; S1–S5/S2R1/S2R2 permanecem COMPLETED. |
| 37 | git diff --check | PASS / exit 0, reconfirmado após persistência administrativa na verificação final. |
| 38 | git status --short | Working tree explicada por S6/S2R2/S2R3; lista literal e classificação por arquivo em v10-s2r3-final-verification.json. Somente .secrets.baseline permanece staged, idêntica ao estado anterior autorizado. |
| 39 | Git publicação | Nenhum novo git add, commit, push, tag ou release. HEAD == origin/main == SHA1:5eb6930aba35a0d1083c92816a83c7c4c2451830. |
| 40 | Decisão | S2R3_COMPLETED. STOP; S6 restaurada, não executada automaticamente. |

## Registros e conhecimento normativo

A alteração original é somente `Attempt.is_correct=False → True`, mantendo
a alternativa selecionada diferente do gabarito da revisão histórica.
Checksums/tamanhos foram atualizados, mas não a verdade dos relacionamentos.

| Invariante | Registro histórico afetado | Causa específica |
| --- | --- | --- |
| ATT-001 | Attempt `f35fea72-af48-4b56-ada9-673710188f77` | `is_correct=True` contradiz alternativa/gabarito da revisão usada |
| ERR-001 | ErrorClassification `44b6d5bb-305a-43e5-8c5e-2d84edf4df5e` | ATTENTION classifica a tentativa agora marcada correta |
| REV-001 | ReviewCycle `a8c3f429-9723-4d6d-8499-d031fddebe40` | INITIAL_ERROR referencia tentativa agora correta |
| REV-002 | Review `362c67cf-e2a4-4b50-966a-a46ca322f2ca` | D1/INITIAL_ERROR_TO_D1 tem âncora agora correta |

Question comum: `5f336ede-44f3-4ffe-8502-60f997f3302f`.
Os IDs são apresentados em UUID canônico; equivalem ao hexadecimal sem hífens
do diagnóstico SQLite original, que não foi alterado.

O validator anterior conferia ZIP/manifesto/formatos/tipos/UUIDs/refs;
`_validate_relations` demonstrava existência, não coerência composta.
O conhecimento adicional já existia nas quatro consultas `_SQL_RULES`.
A conexão independente do checker `mode=ro` só vê dados commitados:
por isso sua chamada no `atomic` importador não demonstrava a integridade
das linhas recém-inseridas. Mantida intacta, essa chamada não é apresentada
como prova semântica dos dados não commitados. A barreira para os quatro
findings é agora o preflight privado sobre os mesmos fatos.

### Ordem observada

`ZIP/metadata/tipos/refs → quatro regras em RAM → ValidatedExport`.
No import direto: `deepcopy dos fatos → atomic → destino/emptiness/refs →
quatro regras em RAM → User.save/INSERTs`. Os INSERTs usam exatamente o
snapshot validado. Nenhum dado inválido é excluído ou reparado.

Esta extensão cobre as quatro invariantes identificadas de S6-F02; não
declara executar todo o catálogo de 25 checks no pacote. O checker completo
e todas as regras normativas continuam inalterados. A projeção privada
consulta a mesma SQL, evitando implementar regras concorrentes em Python.
São oito tabelas derivadas da lista CEI fechada/model metadata em RAM,
sem instalar schema, alias, migration, usuário ou candidato no destino.
Não houve alteração material de arquitetura/pipeline ou contrato CEI.

## Fingerprints do reteste exato

- Pacote incoerente preservado: `SHA256:848f3a2c19ea4e90f37c6ad2b8f30ed79e91a7b4321b94cbe307eaf6e4ddbd1f`.
- Semântico antes/depois: `SHA256:94f92c9f335503c57f8c057099de9f1f1ca80267f05729b3696fc7ebb505c2f9`.
- Schema antes/depois: `SHA256:5faccaf07aa61ecec85bab63142b5c7acb92778129250b983a396efa84095c5e`.
- Físico antes/depois: `SHA256:cff30c8c36b6079e434a6e7beee7090a1c2181e8918abdfb4a41f0a49846d837`.

## A8 deep própria

- **root_cause:** Reader omitted relational truth; importer file checker uses separate mode=ro SQLite connection and sees committed empty target, not pending INSERTs. RED exact package reproduced 24 committed INSERTs plus four checker findings before fix.
- **invariants:** ATT-001/ERR-001/REV-001/REV-002 SQL unchanged, exposed through one accessor, reused verbatim. All existing checker function/class ASTs and all SQL compared against HEAD unchanged.
- **ordering:** Reader relations then RAM semantics before ValidatedExport; direct import snapshots rows then checks destination/emptiness/relations/semantics before User.save or record INSERT. Mutable nested rows cannot bypass semantic checks.
- **isolation:** Eight CEI tables in dedicated sqlite3 :memory: connection only; no destination alias, physical staging, migrations, users or active DB. RAM CREATE/INSERT is distinct from final destination DML, which is measured before execution.
- **transactions:** Private projection queries see their own rows on same connection; projection closed on success/error. Final destination atomic/schema validation retained. Rollback not accepted as pre-write evidence; total_changes and attempted counters verify zero writes.
- **scope_limit:** Small four-invariant preflight extension; not a copy or execution of the full 25-check catalog on the package. Existing wider structural/destination validation and checker unchanged. No new semantic rules or significant pipeline/architecture change.
- **invalid_package:** Same preserved V0.5 producer incoherent ZIP rejects with all four codes on fresh target; source ZIP unchanged, all complete counts and semantic/schema/physical fingerprints equal.
- **negative_tests:** Ten focused cases: isolated four + combination via reader and direct mutated ValidatedExport. Each asserts attempted/completed DML zero, total_changes zero, full counts and fingerprints equal, exact rejection codes. Fixture corrected for legacy INITIAL_ERROR without weakening assertions.
- **valid_import:** New legacy initial-error history import: 21-set equality, checker 25 checks/0 findings. Existing current activation and S2B/S2C corrections/revisions/filter/domain/audit/UUID/policy round-trips PASS in focused and integral suite.
- **N9:** Essential fresh N9 through unchanged CLI probe; zero attempted INSERT/UPDATE/DELETE, no completed writes/total_changes, full fingerprints/counts preserved; schema/migration error before target DML.
- **no_repair:** No row skipped, coerced, repaired, merged or remapped; UUID.hex only mirrors SQLite UUID storage for comparison; final inserts use unchanged field DB serializers.
- **format_migrations:** No model/schema/policy/producer/CEI format or migration changes; gate migration check PASS.
- **security:** Identifiers from closed SETS/model metadata, values bound as SQL parameters. Errors contain invariant codes, no study contents. No new dependency or secrets/baseline changes.
- **gate:** Own full gate exit 0; 543 PASS; coverage 86.6284362%; audit zero; all official gates PASS.
- **chronology:** Protected 17 files/95 historical artifacts hash-equal, two immutable S6 blocked contracts retained; old RED never rewritten. Restore S6 authorization only after S2R3 completion, no automatic S6 execution/S7-S10.

## Artefatos e reprodução

- `quality/v10-s2r3-red-historical.json`: novo RED automatizado antes do fix; source ZIP original preservado.
- `quality/v10-s2r3-f02-retest.json`: zero tentativas/completed, total_changes, todas as contagens e fingerprints.
- `quality/v10-s2r3-n9-retest.json`: nova execução essencial S6-F01/N9; task_id original do probe retido e execution_task S2R3 explícito.
- `quality/v10-s2r3-focused.json`: 43 casos e dez propriedades zero-write; JUnit/log completos em outputs/work.
- `quality/v10-s2r3-gate.json`: gate integral próprio observado; log completo em outputs/work.
- `quality/v10-s2r3-a8-deep.json`: revisão profunda própria.
- `quality/v10-s2r3-preservation.json`: 17 arquivos/95 artefatos históricos verificados por hashes e nova pausa S6 idêntica.
- `quality/v10-s2r3-normative-rules.json`: todas as SQL e ASTs anteriores do checker intactas.
- `quality/v10-s2r3-final-verification.json`: diff/status/HEAD/cached/baseline, histórico e classificação finais.
- `tests/test_cei_semantic_prewrite.py`: 11 casos novos; sem dependência de paths locais de evidências antigas.
- `tests/probe_v10_s2r3_semantic.py`: `--repo`, `--root` novo `s2r3-*` e `--package` preservado obrigatórios; execução sintética isolada, assertions ativas. Exit 2 no RED histórico, exit 0 no reteste.

Os targets RED original e RED S2R3 são NON-CANDIDATE e nunca reutilizados.
Os arquivos/logs anteriores S6/S2R2 não foram reescritos. Os hashes de evidências
novas têm prefixo de algoritmo, sem alterar hashes dos manifests CEI.
A baseline e seus detectores/filtros/staging autorizados permanecem idênticos.

## Estado restaurado e parada

S6-F01 e S6-F02 RESOLVED. S6 continua não concluída/não arquivada.
Seu próximo contrato AUTHORIZED permite uma execução futura delimitada de
provas CEI afetadas, gate final integral e A8 deep própria. N1–N8, upgrade,
clean install, backup, restore, recovery e round-trip já válidos não são
repetidos automaticamente. S7–S10 permanecem sem autorização.

S2R3 termina aqui; nenhuma execução futura ou publicação Git foi iniciada.
