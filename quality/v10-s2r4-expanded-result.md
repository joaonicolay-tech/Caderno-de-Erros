# V1.0-S2R4 — ampliação controlada do preflight semântico CEI

**Decisão: S2R4_COMPLETED. S6-F03 e S6-F04 RESOLVED; S6 autorizada para retomada.**

## Relatório final — 42 campos

| # | Campo | Resultado observado |
| --- | --- | --- |
| 1 | START_TIME | 2026-10-01 12:22:46 -03:00 |
| 2 | END_TIME | 2026-10-01 13:48:34 -03:00 |
| 3 | Duração observada | 1:25:48 |
| 4 | Modelo | GPT-6.1 Sol High, conforme autorização humana específica. |
| 5 | Matriz dos 25 checks | Completa e persistida antes da ampliação funcional. Os 15 campos por check, dados, dependências e justificativas estão em v10-s2r4-expanded-matrix.json/md. |
| 6 | Quantidade A | 14: WS-003, QUE-001, QUE-002, ATT-002, ATT-003, REV-003, REV-004, ERR-002, CAT-001, REV-005, REV-006, AUD-001, SAV-001 e DOM-001. |
| 7 | Quantidade B | 8: DB-002, WS-001, WS-002, QUE-003, ATT-001, ERR-001, REV-001 e REV-002. |
| 8 | Quantidade C | 1: DB-001. |
| 9 | Quantidade D | 1: AUD-002. |
| 10 | Quantidade E | 1: OPS-001. |
| 11 | Justificativa de cada não-prewrite | DB-001: integridade física do arquivo SQLite não é representada pelo CEI; a projeção RAM não certifica páginas/índices do destino. AUD-002: retenção de 90 dias depende do now do checker; generated_at não fornece um relógio normativo de retenção. OPS-001: OperationReceipt é excluído do CEI e nenhum receipt é importado. Esses checks não foram declarados validados pelo preflight. |
| 12 | Arquitetura | Pacote CEI → projeção privada SQLite :memory: dos 21 conjuntos → decisão semântica completa A/B → somente então DML no destino. Owners projetados são o mesmo LOCAL_USER_ID que o importador já atribui, contexto local explícito. Helpers usam o resolvedor IANA/tzdata instalado, sem relógio variável. Destino real não é staging. |
| 13 | Regras compartilhadas | 19 SQLs normativos completos fornecidos por invariant_sql_rules. Hash/AST das regras e catálogo preservados. DB-002 continua protegido pela validação estrutural de referências; isso não declara todas as constraints físicas do SQLite cobertas. |
| 14 | Helpers reutilizados | _append_workspace_timezone_findings, _append_attempt_time_findings e _append_inaugural_schedule_findings, por adaptador pequeno invariant_python_violations. Nenhum algoritmo foi copiado; funções anteriores do checker são AST-iguais. |
| 15 | F01 | PASS: N9 incompatível rejeitado em target novo, antes de qualquer tentativa ou execução de DML. |
| 16 | F02 | PASS: ZIP histórico exato das quatro invariantes rejeitado com códigos explícitos e zero DML. |
| 17 | F03 | PASS: ZIP histórico exato QUE-003 rejeitado antes da escrita. Correção e evidências anteriores preservadas. |
| 18 | F04 | PASS: ZIP histórico exato ARCHIVED/ACTIVE/PENDING rejeitado por REV-003, antes da escrita. FAIL original com 24 INSERTs commitados permanece intacto. |
| 19 | Zero-write | F01–F04, os 48 novos negativos e os 24 probes adversariais: INSERT/UPDATE/DELETE attempted e completed = 0/0/0; total_changes delta = 0; counts e fingerprints semântico/schema/físico iguais. Rollback não foi usado como prova de rejeição pré-write. |
| 20 | Novos commit findings reproduzidos | 0 na busca sobre todas as 14 regras A e 10 bordas. Candidatos de inspeção não foram chamados de findings. Erro inicial de fixture ocorreu antes de pacote/import, foi preservado e corrigido somente no fixture. |
| 21 | Import válido | VALID_IMPORT_PASS para o export V0.5 histórico real: 21 conjuntos, UUIDs, relações, histórico, revisões, attempts, reviews, policies e derivados iguais à fonte; SQLite ok, FK vazio e checker 25/0. Os 14 positivos correspondentes adicionais também importam todos os conjuntos não vazios, preservam dados no reexport e passam checker 25/0. |
| 22 | Testes focados | 132 PASS em 687.810 s. Incluem todas as A, positivos/bordas, semântica anterior, QUE-003, destination compatibility e portability. Novos 63 testes passaram em 361,23 s. Execução inicial com 1 erro de fixture em 6,43 s permanece em log/XML separado. |
| 23 | Migrations | 0 novas. Model/schema inalterados. makemigrations --check --dry-run PASS. |
| 24 | Formato CEI | CEI-EXPORT-1.0, format_version 1.0, producer allowlist V0.5/V1.0, policies e SETS inalterados. Sem merge, conversion, remapping, repair ou silent coercion. |
| 25 | Gate | GREEN próprio desta ampliação; exit 0 observado; 1308.287 s. Lock, sync, runtime, Django checks, migration check, Ruff, mypy, coverage, secrets e pip-audit PASS. |
| 26 | Total testes | 632 PASS no gate integral; pytest em 1218.33 s. |
| 27 | Coverage | 86.7866230462% global; cobertura de domínio PASS. Relatório da execução preservado. |
| 28 | pip-audit | PASS próprio, 0 vulnerabilidades conhecidas e 0 dependências omitidas. Relatório preservado. |
| 29 | A8 deep | APPROVED. Revisão da matriz A–E, justificativas, F01–F04, zero-write, regras compartilhadas, projeção, helpers, limites CEI, imports válidos, falso positivo/negativo, migrations, formato e gate. Busca explícita de outro commit finding A com 24 ZIPs e probe separado. Revisão feita pelo executor; não se alega reviewer independente. |
| 30 | Blocker/Major/Minor | 0/0/0 abertos nesta ampliação. |
| 31 | S6-F03 | RESOLVED prospectivamente após aceite integral S2R4. FIX_VERIFIED e RED anteriores conservados como fatos históricos. |
| 32 | S6-F04 | RESOLVED prospectivamente após aceite integral S2R4. RED original com 24 INSERTs/REV-003 preservado. |
| 33 | Artefatos | quality/v10-s2r4-expanded-*; tests/test_cei_semantic_matrix.py; tasks/completed/v10-s2r4-cei-semantic-prewrite.md. ZIPs, targets, logs, XML, coverage e audit brutos retidos no workspace/work, sem remoção ou reutilização de targets históricos. |
| 34 | PROJECT_STATE | Novo checkpoint S2R4_COMPLETED / F03 e F04 RESOLVED / S6 retomável. Checkpoints anteriores mantidos como história. |
| 35 | tasks/current | V1.0-S6: AUTHORIZED / IN EXECUTION / RESUME AFTER S2R4. S2R4 arquivada. |
| 36 | S6 retomável | Sim; ainda não concluída. Próxima execução repete somente CEI afetado + gate integral FINAL S6 + A8 deep FINAL S6. Upgrade, clean install, backup, restore, recovery, RPO/RTO e round-trip preservados, sem repetição automática. Nenhuma execução funcional S6 nesta ampliação. |
| 37 | S7–S10 | NOT AUTHORIZED. |
| 38 | .secrets.baseline | Bytes, detectores, filtros e index anteriores iguais. Somente baseline permanece staged pela autorização anterior dos 59 registros; nenhum registro ou staging adicional. |
| 39 | git diff --check | PASS, exit 0 observado. Advertência CRLF antiga da métrica não é falha. Evidência final em JSON. |
| 40 | git status --short | Os 63 caminhos iniciais e os novos caminhos S2R4 foram classificados explicitamente. Lista literal no JSON final. HEAD e origin/main preservados em SHA1:5eb6930aba35a0d1083c92816a83c7c4c2451830. |
| 41 | Git/publicação | Nenhum novo staging, commit, push, tag ou release. |
| 42 | Decisão | S2R4_COMPLETED. S2R4 arquivada e S6 restaurada como autorizada para retomada. STOP após relatório. |

## Evidências principais

- [Matriz completa](v10-s2r4-expanded-matrix.md), [campos e dependências](v10-s2r4-expanded-matrix.json).
- [F01/N9](v10-s2r4-expanded-n9-retest.json), [F02](v10-s2r4-expanded-f02-retest.json), [F03](v10-s2r4-expanded-f03-retest.json), [F04](v10-s2r4-expanded-f04-retest.json).
- [Import V0.5 válido](v10-s2r4-expanded-valid-import.json), [testes focados](v10-s2r4-expanded-focused.json).
- [Auditoria adversarial](v10-s2r4-expanded-adversarial.json), [fontes compartilhadas](v10-s2r4-expanded-source-review.json), [A8 deep](v10-s2r4-expanded-a8-deep.json).
- [Gate integral próprio](v10-s2r4-expanded-gate.json), [preservação](v10-s2r4-expanded-preservation.json), [verificação final](v10-s2r4-expanded-final-verification.json).

## Preservação e limites

Os 61 arquivos protegidos e 154 artefatos históricos passaram pela conferência de hash. Gates e FAILs anteriores conservam seus resultados. A resolução pertence a este novo checkpoint.

A implementação seleciona as regras normativas inteiras; o catálogo e os algoritmos anteriores permanecem iguais. Diagnóstico físico, retenção relativa ao relógio e receipts excluídos permanecem fora da decisão semântica do pacote. A auditoria adversarial executada é finita e não constitui prova sobre todos os inputs possíveis.

S6 ainda exige suas provas CEI afetadas e gate/A8 finais próprios. A autorização restaurada não declara S6 concluída.

## Verificação documental após o gate

A primeira varredura da documentação de fechamento retornou exit 1 por Secret Keyword em um campo JSON que continha somente o resultado PASS. O rótulo desse campo foi ajustado, mantendo o resultado. A baseline, os detectores e os filtros permaneceram iguais. O mesmo hook oficial sobre todos os arquivos retornou exit 0 no reteste. O log e o JSON originais foram preservados em work/s2r4-expanded-final-secrets.log/json; o reteste está em work/s2r4-expanded-final-secrets-rerun.log/json. O gate integral próprio já havia retornado exit 0; nenhuma lógica de produto ou teste mudou depois dele.
