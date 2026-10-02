# V1.0-S6 — retomada final após S2R3

**Decisão: BLOCKED. S6-F03 Major/P1 OPEN.**

F01 e F02 continuam RESOLVED com novos retestes zero-write PASS. O novo caso adversarial QUE-003 não foi rejeitado antes de escrita: 24 INSERTs commitados, total_changes +24 e finding posterior. Não é possível fechar S6.

## Relatório final — 50 campos

| # | Campo | Resultado observado |
| --- | --- | --- |
| 1 | START_TIME | 2026-10-01 10:31:03 -03:00 |
| 2 | END_TIME | 2026-10-01 11:00:52 -03:00 |
| 3 | Duração observada | 0:29:49 |
| 4 | Modelo | GPT-6.1 Sol High, autorização humana específica da retomada final S6 |
| 5 | Baseline | HEAD = origin/main = SHA1:5eb6930aba35a0d1083c92816a83c7c4c2451830, verificados nesta execução |
| 6 | S6-F01 histórico | FAIL preservado: oito INSERTs antes de OperationalError; rollback preservou estado mas não comprovou pré-write. Cadeia FAIL → S2R2 → PASS mantida. |
| 7 | S6-F01 final | RESOLVED; nova execução essencial N9 PASS nesta retomada. |
| 8 | S6-F02 histórico | FAIL preservado: pacote aceito e 24 INSERTs commitados; checker pós-commit quatro findings ATT-001/ERR-001/REV-001/REV-002. Cadeia FAIL → S2R3 → PASS mantida. |
| 9 | S6-F02 final | RESOLVED para o pacote original/quatro invariantes: reteste exato PASS. Novo QUE-003 é S6-F03 separado e não reescreve F02. |
| 10 | Zero-write S6-F01 | N9 novo: INSERT/UPDATE/DELETE attempts 0/0/0, completed 0, total_changes/row_changes 0; contagens e fingerprints preservados. |
| 11 | Zero-write S6-F02 | Mesmo ZIP original: attempts/completed 0/0/0, total_changes 0, full counts e fingerprints semântico/schema/físico iguais; erro contém quatro códigos. |
| 12 | Import CEI válido | VALID_IMPORT_PASS: pacote V0.5 real original em destino V1 novo; 21 conjuntos, IDs, contagens, relações, histórico, policies, derivados, SQLite/FK/checker reconciliados. |
| 13 | Testes semânticos | Dez negativos quatro invariantes isoladas/combinação × reader/objeto alterado PASS zero-write. Nova regressão adicional QUE-003 RED, com 24 INSERTs commitados. |
| 14 | N1–N8 | Preservados/aceitos por hashes; não reexecutados formalmente. Regressões automatizadas relacionadas executadas na suíte focada. |
| 15 | Análise de impacto | Seis funções estruturais AST iguais ao HEAD publicado, removendo apenas a chamada nova de semântica ao comparar validate_export. Negativos N1–N8 rejeitam antes dela. Upgrade/clean/backup/restore/recovery sem impacto de código; import válido/F01/F02 diretamente afetados reexecutados. |
| 16 | V0.4.4→V0.5→V1 | PASS anterior preservado: runtimes históricos reais, 24→34 migrations com dez aditivas; V0.5→V1 plano vazio, campos legados/UUIDs/fatos reconciliados. Não reexecutado por formalidade. |
| 17 | Clean install | CLEAN_INSTALL_PASS anterior preservado: 34 migrations, dez categorias STANDARD/ACTIVE, defaults e smoke HTTP 200. |
| 18 | Backup | PASS independente anterior preservado; par válido intacto; cópia corrompida rejeitada. |
| 19 | Restore | ISOLATED_RESTORE_PASS anterior preservado; fatos/derivados iguais; target ocupado intacto e backup corrompido sem novo destino. |
| 20 | Recovery | RECOVERY_PASS anterior preservado: adoção offline real, falha pós-adoção injetada/retorno automático e ticket final reconciliados; pré-backups preservados. |
| 21 | RPO/RTO | 0,378565 s / 1,707174 s registrados no exercício anterior, abaixo de 24 h/4 h somente no ambiente sintético; não medidos novamente nem tratados como SLA real. |
| 22 | CEI positivo | V0.5→V1 PASS nesta retomada; pacote produzido pelo runtime v0.5.0 histórico, não por troca de rótulo de V1. |
| 23 | Round-trip | Segundo import V1→V1 anterior preservado. Nesta retomada, somente import afetado V0.5→V1 e reexport/validate para igualdade funcional dos 21 conjuntos; sem repetir segundo target. |
| 24 | IDs | PASS nos 21 conjuntos funcionais novos; mesmos UUIDs canônicos/relações; legado/backup/recovery preservados. F03 mantém IDs, mas quebra condição de revisão corrente. |
| 25 | Contagens | PASS por conjunto no import válido, iguais à prova anterior; full counts iguais nos negativos F01/F02. F03 muda contagens por 24 INSERTs commitados. |
| 26 | Fingerprints | F01/F02 iguais antes/depois; válido tem mesmo functional_projection_sha256 histórico, leitura/checker/derivados sem mutação. F03 altera semântico/físico, demonstrando commit; hashes exatos no JSON. |
| 27 | Histórico | Import válido preserva revisão/gabarito usado, Attempt VALID, ATTENTION, origem, ciclo INITIAL_ERROR, D1 PENDING/due 2026-09-21. Receipt excluído somente do CEI conforme contrato; backup/cadeia o preservam. |
| 28 | Policies | REV-FIXA-1.0, DOM-HEUR-1.0, PRI-HEUR-1.0 iguais; produtores e formato não alterados. |
| 29 | Derivados | Analytics, fila, Domain e Priority do import novo iguais à fonte histórica preservada sob relógio fixo 2026-09-20 15:00 UTC; demais provas preservadas. |
| 30 | SQLite integrity | ok nos targets válidos e no target F03; falha nova é semântica, mesmo com integridade física ok. |
| 31 | FK | foreign_key_check vazio nos targets válidos e F03; existência de referências não demonstra revisão corrente. |
| 32 | Checker | Import válido 25 checks/0 findings. Novo target F03: 25 checks/1 finding QUE-003 ERROR em Question. Zero findings geral não satisfeito. |
| 33 | Migrations | 0 novas; nenhum model/schema alterado; código de produto anterior hash-equal. Gate final migration check NÃO EXECUTADO devido à parada. |
| 34 | Formato CEI | CEI-EXPORT-1.0 / format_version 1.0 / allowlist V0.5/V1.0 inalterados. Sem merge/conversão/remapeamento/adaptação/repair. |
| 35 | Testes focados | 43 PASS, 135,05 s, exit 0; três módulos CEI. Novo probe válido Ruff/mypy PASS. Regressão adversarial QUE-003 adicional exit 2 (RED preservado). |
| 36 | Gate final próprio S6 | NOT_EXECUTED: parada obrigatória por novo finding semântico material antes do gate, conforme Constraints do contrato e A4 §7. Gates anteriores não substituem o final. |
| 37 | Total de testes | Gate final: não disponível/não executado. Suíte focada própria: 43 PASS; três probes finais afetados PASS; um adversarial QUE-003 RED. |
| 38 | Coverage | Não aferida por gate final nesta retomada; 86,6284362% anterior pertence à S2R3 e não é PASS final S6. |
| 39 | pip-audit | Gate final não executado; auditoria anterior S2R3 limpa é histórica, não auditoria final própria S6. |
| 40 | A8 deep final | CHANGES_REQUIRED / NOT APPROVED: novo S6-F03 Major/P1 demonstrado; revisão pelo agente executor, sem alegar reviewer independente. |
| 41 | Blocker/Major/Minor | 0/1/0 abertos: S6-F03. F01/F02 RESOLVED, evidências FAIL mantidas. |
| 42 | Artefatos finais | Novos quality/v10-s6-final-{f01-n9-retest,f02-retest,valid-import,a8-f03-result,a8-deep,impact-retained,preservation,focused,verification}.json e v10-s6-final-result.md; probe tests/probe_v10_s6_final_cei.py; logs/targets/ZIPs em work/ preservados. |
| 43 | .secrets.baseline | Bytes/detectores/filtros e staging anterior preservados; somente ela staged pela autorização humana anterior; zero registros/staging novos. |
| 44 | git diff --check | PASS / exit 0 antes e após registro da parada; aviso de normalização CRLF preexistente em métricas não é falha. |
| 45 | git status --short | Somente cadeia autorizada S6/S2R2/S2R3 e novos arquivos S6 final; lista literal/classificação por arquivo na verificação final. Nenhum caminho alheio. |
| 46 | PROJECT_STATE | S6 AUTHORIZED / BLOCKED / S6-F03 Major OPEN; F01/F02 RESOLVED; S1–S5/S2R1/S2R2/S2R3 COMPLETED; histórico preservado. |
| 47 | tasks/current | AUTHORIZED / BLOCKED / FINAL A8 NEW FINDING S6-F03; não arquivada, não retornada a NO_TASK_AUTHORIZED. |
| 48 | S7–S10 | NOT AUTHORIZED; nenhuma etapa futura iniciada. |
| 49 | Git/publicação | Nenhum git add, commit, push, tag ou release; HEAD/origin/main intactos; sem checkpoint. |
| 50 | Decisão | BLOCKED. S6_COMPLETED não declarado. Parada aplicada após S6-F03; somente diagnóstico read-only e registro documental/verificações de metadados depois, sem fix ou gate integral. |

## S6-F03 — reprodução e impacto

**[Major/P1] portability.py:642 e :792 — preflight semântico parcial permite
commit de Question ACTIVE sem revisão corrente.** A regra existente QUE-003
(`integrity.py:654`) exige exatamente uma revisão corrente em ACTIVE/ARCHIVED.
A unicidade física limita quantidade máxima, mas não exige existência.

- Origem: ZIP real V0.5 preservado `work/s6-resume-20260930-run1/real-v05-export.zip`.
- Mutação única: `QuestionRevision.is_current=True → False`, com Question ainda ACTIVE.
- Checksum/tamanho desse membro recalculados; produtor, formato, migrations,
  policies, UUIDs, referências, Attempt e todas as outras linhas mantidos.
- Question: `5f336ede-44f3-4ffe-8502-60f997f3302f`; revisão: `35f771bb-ad9b-4973-b8f1-5c4d4af21673`.
- `validate_export` aceitou; `import_into_empty` retornou sem exceção/rollback.
- Tentativas/completed INSERT/UPDATE/DELETE: **24/0/0**; `total_changes` **+24**.
- Commit confirmado por checker independente após transação: **25 checks /
  1 finding QUE-003 ERROR**; contagens/fingerprints semântico/físico mudaram.
- SQLite integrity `ok` e FK sem findings não tornam o estado funcional válido.
- Impacto normativo: uma Question utilizável não tem revisão corrente, tornando
  apresentação e semântica da tentativa não determinísticas.

O preflight S2R3 consulta somente ATT-001/ERR-001/REV-001/REV-002. Essas regras
continuam corretas e o pacote F02 original é rejeitado; elas não verificam
cardinalidade de revisão corrente. A chamada do checker de arquivo dentro de
`atomic` continua usando outra conexão SQLite `mode=ro`, que vê o destino
vazio anteriormente commitado. Por isso não detecta QUE-003 nas novas linhas
antes de confirmar a importação.

O target novo `work/s2r3-s6-final-a8-que003-20261001/target.sqlite3` está
preservado **NON-CANDIDATE**, nunca reutilizado. Pacote mutado, proveniência,
resultado bruto e log também estão preservados. O probe de medição S2R3 foi
reutilizado sem alteração; seu rótulo bruto F02 foi retido como
`harness_case_as_emitted` na entrega, e o caso novo é identificado como F03.
Não se reinterpreta o reteste original F02 nem se sobrescreve qualquer FAIL.

## A8 deep — evidência e decisão

- **A4_isolation:** Original approved A4 preserved; only fresh synthetic targets/new roots. No original/active/user DB. Bad QUE-003 target NON-CANDIDATE preserved, not reused.
- **N1_N8:** Direct historical negatives hash-equal, accepted; six structural validator ASTs match published HEAD after removing only the added semantic call. All N1–N8 reject before that call; automated related regressions PASS.
- **F01_S2R2:** Historical eight INSERTs + rollback retained; S2R2 completed evidence retained; new final N9 zero attempts/changes and unchanged counts/fingerprints.
- **F02_S2R3:** Historical 24 committed INSERTs/four CRITICAL findings retained; S2R3 completed evidence/code/tests retained; exact package rejects with ATT-001/ERR-001/REV-001/REV-002, zero final destination writes.
- **structural_semantic_order:** Destination preflight and four-rule preflight still precede DML. Additional existing QUE-003 invariant is absent, demonstrated by new checksum-valid package accepted and 24 INSERTs committed.
- **root_cause:** The four-invariant projection does not validate current revision cardinality. File-based independent mode=ro checker called inside atomic sees old committed empty target, cannot see new rows, so commit is allowed; post-commit sees QUE-003.
- **upgrade_clean:** Historical real V0.4.4 24 migrations/17 checks; ten real additive migrations to V0.5 34/25 checks; V1 migration plan empty/equal facts. Clean install defaults/smoke verified in retained JSON. Not re-executed formally.
- **backup_restore_recovery:** Independent backup/corrupt rejection/isolated restore/offline adoption/automatic return/final recovery snapshots and hashes retained; RPO 0.378565 s/RTO 1.707174 s only isolated exercise, no real SLA extrapolation.
- **CEI_roundtrip:** Actual historical V0.5 producer package verified independently and imported anew; all 21 sets/IDs/counts/relationships/history/policies and functional hash equal; derived analytics/queue/domain/priority equal retained source. Previous second V1 import roundtrip preserved without formal re-execution.
- **SQLite_FK_checker:** Valid targets integrity_check ok/FK empty/checker 25/0; new F03 target physical integrity/FK still PASS but semantic checker 25/1 QUE-003 ERROR. Physical correctness is insufficient for semantic acceptability.
- **migrations_format:** Product code/schema/models/migrations/CEI policies/producers untouched during final resumption; no merge/conversion/remapping/repair/new dependency.
- **tests:** 43 focused PASS / 135.05 s, including ten four-invariant negatives and valid history/corrections. New QUE-003 adversarial automated regression separately RED, showing focused GREEN is insufficient.
- **gate:** Final own integral S6 gate NOT_EXECUTED: mandatory stop on material semantic/integrity finding under tasks/current Constraints and A4 section 7. Previous GREEN S6/S2R2/S2R3 gates not substituted.
- **scope:** Only authorized S6 proof harness/evidence/contracts/state/metrics. No product fix or S7–S10, no staging/publication. S6 remains AUTHORIZED/BLOCKED, not archived and not NO_TASK_AUTHORIZED.

## Parada e próximos limites

O finding material acionou a parada de `tasks/current.md` (Constraints) e A4,
seção 7, antes do gate integral final. Não executar esse gate após a parada
evita tratar GREEN técnico como aprovação de um candidato com violação
semântica demonstrada. Não houve correção de produto neste turno.

Direção segura para autorização própria de remediação: inventariar invariantes
demonstráveis no CEI e reutilizar regras normativas pré-write, incluindo
QUE-003, preservando imports históricos válidos e proteções F01/F02.
Não foi demonstrada necessidade de migration, formato novo ou mudança
material de arquitetura. Nenhuma dessas mudanças foi aplicada.

Os 36 arquivos protegidos e 104 artefatos históricos foram conferidos por
hashes; produto, A4, testes S2R2/S2R3, contratos congelados e provas anteriores
continuam idênticos. N1–N8, upgrade, clean install, backup, restore, recovery,
RPO/RTO e segundo round-trip permanecem evidência válida, sem repetição formal.

Novas provas finais F01/F02 e import válido PASS estão nos JSONs próprios.
Os 43 focados passaram em 135,05 s; JUnit legacy evitou warnings de propriedades.
Esse PASS não cobre QUE-003: a regressão adversarial separada é RED e prevalece
para o fechamento. Não há gate/coverage/pip-audit final próprios aprovados.

S6 permanece AUTHORIZED / BLOCKED / RETOMÁVEL, sem arquivamento.
S7–S10 continuam NOT AUTHORIZED. Sem staging/publicação Git. **STOP.**
