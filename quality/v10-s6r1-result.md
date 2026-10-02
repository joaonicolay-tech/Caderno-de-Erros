# V1.0-S6R1 — Revalidação após S2R5 / CP-01

Decisão: **S6_REVALIDATED**. Nova prova do estado funcional atual; histórico preservado.

## 1. START_TIME

2026-10-02 13:05:32 -03:00

## 2. END_TIME

2026-10-02 13:59:24 -03:00

## 3. Duração observada

0:53:52

## 4. Modelo

GPT-6.1 Sol High, autorizado pela decisão humana. Identidade efetiva do runtime não exposta para verificação independente.

## 5. Baseline

SHA1:5eb6930aba35a0d1083c92816a83c7c4c2451830; HEAD == origin/main local, verificados novamente. Nenhuma publicação nova.

## 6. Total atual de paths

148 paths;129 na entrada. Acréscimos são evidências quality/v10-s6r1-* e contrato arquivado. tasks/current.md esteve modificado durante execução e retornou aos bytes NO_TASK_AUTHORIZED da entrada. Não houve nova alteração funcional.

## 7. CP-01

RESOLVED / REJECTED_BEFORE_WRITE em target novo. Direct sort_order="17" rejeitado; ZIP novo com checksum válido e o mesmo campo inválido também REJECT. Erros textuais não precisam coincidir. quality/v10-s6r1-cp01-retest.json; FAIL original24INSERTs e teste RED preservados.

## 8. Zero-write CP-01

INSERT/UPDATE/DELETE tentados0/0/0; concluídos0/0/0; total_changes delta0. Contagens e fingerprints semântico/schema/físico iguais; sourceZIP intacto. Rollback não usado como prova de ausência de escrita.

## 9. F01

RESOLVED; N9 incompatível novo REJECTED_BEFORE_WRITE; tentativas/conclusões0/0/0/native0; contagens/fingerprints iguais. Mais11casos permanentes de destino incompatível PASS. quality/v10-s6r1-f01-retest.json.

## 10. F02

RESOLVED; pacote histórico exato rejeitado antes de DML em target novo: ATT-001/ERR-001/REV-001/REV-002. Zero-write e fingerprints iguais; checker pós-transação25/0. quality/v10-s6r1-f02-retest.json.

## 11. F03

RESOLVED; QUE-003 rejeitado antes de DML em target novo; zero-write/native0/fingerprints iguais. quality/v10-s6r1-f03-retest.json.

## 12. F04

RESOLVED; REV-003 rejeitado antes de DML em target novo; zero-write/native0/fingerprints iguais. quality/v10-s6r1-f04-retest.json.

## 13. Matriz estrutural/tipos

Inventário atual21SETS/242fields/14ORMkinds.47testes permanentesPASS;44casos negativos ZIP/direct=88decisões antes de DML:18tipos,5estruturas,21camposid ausentes.2positivos all21não-vazios incluem Decimal finito e mutação do caller; snapshot privado preservado. Coerções históricas bloqueadas; decoder/SETS normativos iguais.

## 14. Matriz semântica

A14/B8/C1/D1/E1 mantida.63testes permanentesPASS:48negativos,14positivos,1exclusão de retenção; regressões question/semantic/destination/portability tambémPASS. DB-001 físico/AUD-002 dependente do relógio/OPS-001 excluído não recebem PASS semântico artificial.

## 15. Import V0.5

VALID_IMPORT_PASS: export produzido pelo runtime histórico real V0.5 → target novo do candidato V1.21conjuntos incluindo vazios/UUID/referências/histórico/revisions/attempts/reviews/policies/derivados iguais; source/expected intactos. Sem falso positivo observado. quality/v10-s6r1-valid-import.json.

## 16. Round-trip

ROUNDTRIP_PASS focado: necessário porque import passa por _validate_manifest/_validated_rows alteradas em S2R5. V0.5→V1reexport→segundo targetV1novo→reexport, todos21sets/UUID/referências/histórico/policies/derivados iguais. Segundo round-trip histórico preservado separadamente; upgrade/recovery completo não repetido. quality/v10-s6r1-roundtrip.json.

## 17. Checker

25checks/0findings na importação válida e no round-trip novos; positivos permanentes também25/0. Catálogo/SQL/helpers normativos preservados.

## 18. SQLite/FK

integrity_check=ok; foreign_key_check vazio nos targets válidos. Provas físicas são distintas das regras semânticas de pacote.

## 19. Migrations

0novas; models/schema inalterados em S6R1.277arquivos funcionais iguais à entrada e ao gate; makemigrations --check --dry-run: No changes detected.

## 20. Formato CEI

CEI-EXPORT-1.0; format_version1.0; SETS21; allowlistV0.5/V1.0; policies REV-FIXA-1.0/DOM-HEUR-1.0/PRI-HEUR-1.0 mantidas. Sem conversion/merge/remapping/repair/silentcoercion. Exclusões contratuais de credencial local/OperationReceipt preservadas.

## 21. Temporary evidence policy

docs/operations/temporary-test-evidence.md coerente com PRES-01. Manifesto quality/v10-s6r1-artifact-policy.json registrado antes dos testes: targets/provas essenciais e logs/XML/receipts/gate reports DESIGNATED_FOR_RETENTION; scratchpytest DISPOSABLE / NOT_REQUIRED_FOR_FINAL_EVIDENCE. Basetemp novo explícito, cópias+hashes verificados, nenhum cleanup solicitado.

## 22. PRIV-01

RESOLVED mantido.33relatórios sanitizados byte-equal; novas evidências canônicas sem usuário local/home/Documents-Codex/AppData pessoal. Prefixos reais somente em brutos fora do Git; hook oficialPASS.

## 23. PRES-01

HUMAN_EXEMPTED para exatamente11targets sintéticos temporários ausentes, registro individual mantido. Bytes originais continuam indisponíveis; nenhuma reconstrução ou falsa byte-preservation. FAIL/BLOCKED/gateinterrompido históricos preservados.162brutos originais remanescentes e cópias iguais;389artefatos da cadeiaS6 histórica iguais/copiados; brutos adicionais protegidos.

## 24. Testes focados

179PASS em780.2s, sem warnings; comandos/log/XML e propriedades completas em quality/v10-s6r1-focused.json. Módulos: structure47,destination20,question26,matrix63,semantic11,portability12. Provas essenciais CP/F01-F04/import/roundtrip executadas separadamente em targets novos.

## 25. Gate

GREEN/exit0; novo gate integral próprio S6R1: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1. Duração1612.8137872s; pytest1488.84s. Ruff/mypy/Djangoprofiles/migrations/coverage-domains/secrets/pip-auditPASS. Gate históricoS6/S2R5 não reutilizado. quality/v10-s6r1-gate.json.

## 26. Total de testes

679PASS no gate próprio;179PASS na suíte focada, além das7provas essenciais isoladas. Sem skips/falhas na suíte focada; gate completo sem warningpytest reportado.

## 27. Coverage

87.15073695632516%global; controles de domínio oficiaisPASS. Snapshot próprio de cobertura preservado com hash/cópia.

## 28. Pip-audit

0vulnerabilidades conhecidas/0dependências ignoradas;53dependências no relatório do gate próprio. JSON original preservado.

## 29. A8 deep

APPROVED, depois do gate integral próprio; revisão pelo executor conforme docs/review/code-review.md, sem alegação de independência. S6/S2R2-S2R5/CP/F01-F04/paridade/semântica/tipos/zero-write/import/roundtrip/matriz/migrations/formato/temporarypolicy/PRES/PRIV/gate revisados. quality/v10-s6r1-a8-deep.json.

## 30. Novos findings

0defeitos funcionais materiais reproduzidos. Erro local inicial no preparo do ZIP CP01 ocorreu antes de migrations/import; diretório diagnóstico NON-CANDIDATE retido e target novo run2 usado. Comparação local de metadados corrigiu encodingUTF8/lista de paths autorizados. Hook suplementar sinalizou chave descritiva do novo relatório de gate; renomeada para official_hook, rascunho/diagnóstico preservados, mesmo hookPASS; baseline/detectores/filtros e código inalterados.

## 31. Blocker/Major/Minor

0/0/0abertos nesta revalidação. Findings históricos resolvidos prospectivamente ou exatamente11human-exempted preservam sua cronologia.

## 32. S6_REVALIDATED?

SIM; todos os critérios essenciais observados, gateGREEN/exit0 e A8deepAPPROVED.

## 33. PROJECT_STATE

S6_REVALIDATED_AFTER_S2R5. HistóricoS6COMPLETED/S2R5COMPLETED/CPRESOLVED mantido; heading atual informa novo gate/A8 e checkpoint aguardando só auditoriaGit. Texto histórico anterior preservado como sufixo byte-equal.

## 34. tasks/current

NO_TASK_AUTHORIZED; S6R1 arquivada em tasks/completed/v10-s6r1-revalidation-after-s2r5.md como COMPLETED.

## 35. Checkpoint status

CHECKPOINT_BLOCKED / READY_FOR_AUDIT; somente aguardando auditoria Git separadamente autorizada. A auditoria completa do checkpoint não foi executada nesta tarefa.

## 36. S7–S10

NOT AUTHORIZED; nenhuma etapa futura antecipada.

## 37. git diff --check

exit0 na verificação final.

## 38. git status --short

148paths; listagem literal completa abaixo e no JSON de verificação final. Working tree acumulada permanece não publicada.

## 39. Staging

Nenhum novo staging. .secrets.baseline continua único arquivo staged herdado, bytes de trabalho/blob do index iguais à entrada; detectores/filtros não alterados.

## 40. Commit/push/tag/release

Nenhum commit/push/tag/release/branch/checkpoint nesta execução; HEAD e origin/main local continuam na baseline.

## 41. Decisão

S6_REVALIDATED. CHECKPOINT_BLOCKED / READY_FOR_AUDIT. STOP.

## Listagem Git observada

```text
M  .secrets.baseline
 M PROJECT_STATE.md
 M quality/operational-execution-metrics.jsonl
 M src/modules/data_management/portability.py
 M src/modules/operations/integrity.py
?? docs/operations/temporary-test-evidence.md
?? quality/v10-s2r2-cei-destination-result.md
?? quality/v10-s2r2-n9-retest.json
?? quality/v10-s2r3-a8-deep.json
?? quality/v10-s2r3-cei-semantic-result.md
?? quality/v10-s2r3-f02-retest.json
?? quality/v10-s2r3-final-verification.json
?? quality/v10-s2r3-focused.json
?? quality/v10-s2r3-gate.json
?? quality/v10-s2r3-n9-retest.json
?? quality/v10-s2r3-normative-rules.json
?? quality/v10-s2r3-preservation.json
?? quality/v10-s2r3-red-historical.json
?? quality/v10-s2r4-a8-deep.json
?? quality/v10-s2r4-audit-f04-result.json
?? quality/v10-s2r4-cei-que003-result.md
?? quality/v10-s2r4-expanded-a8-deep.json
?? quality/v10-s2r4-expanded-adversarial.json
?? quality/v10-s2r4-expanded-f02-retest.json
?? quality/v10-s2r4-expanded-f03-retest.json
?? quality/v10-s2r4-expanded-f04-retest.json
?? quality/v10-s2r4-expanded-final-verification.json
?? quality/v10-s2r4-expanded-focused.json
?? quality/v10-s2r4-expanded-gate.json
?? quality/v10-s2r4-expanded-matrix.json
?? quality/v10-s2r4-expanded-matrix.md
?? quality/v10-s2r4-expanded-n9-retest.json
?? quality/v10-s2r4-expanded-preservation.json
?? quality/v10-s2r4-expanded-result.md
?? quality/v10-s2r4-expanded-source-review.json
?? quality/v10-s2r4-expanded-valid-import.json
?? quality/v10-s2r4-f02-retest.json
?? quality/v10-s2r4-f03-retest.json
?? quality/v10-s2r4-final-verification.json
?? quality/v10-s2r4-focused.json
?? quality/v10-s2r4-gate.json
?? quality/v10-s2r4-invariant-audit.json
?? quality/v10-s2r4-n9-retest.json
?? quality/v10-s2r4-normative-rule.json
?? quality/v10-s2r4-preservation.json
?? quality/v10-s2r4-red-historical.json
?? quality/v10-s2r4-valid-import.json
?? quality/v10-s2r5-a8-deep.json
?? quality/v10-s2r5-cp01-red-historical.json
?? quality/v10-s2r5-cp01-retest.json
?? quality/v10-s2r5-f01-retest.json
?? quality/v10-s2r5-f02-retest.json
?? quality/v10-s2r5-f03-retest.json
?? quality/v10-s2r5-f04-retest.json
?? quality/v10-s2r5-final-verification.json
?? quality/v10-s2r5-focused.json
?? quality/v10-s2r5-gate.json
?? quality/v10-s2r5-preservation.json
?? quality/v10-s2r5-result.md
?? quality/v10-s2r5-resume-a8-deep.json
?? quality/v10-s2r5-resume-artifact-policy.json
?? quality/v10-s2r5-resume-cp01-retest.json
?? quality/v10-s2r5-resume-destination-reproducibility.json
?? quality/v10-s2r5-resume-essential-retention.json
?? quality/v10-s2r5-resume-f01-retest.json
?? quality/v10-s2r5-resume-f02-retest.json
?? quality/v10-s2r5-resume-f03-retest.json
?? quality/v10-s2r5-resume-f04-retest.json
?? quality/v10-s2r5-resume-final-verification.json
?? quality/v10-s2r5-resume-focused.json
?? quality/v10-s2r5-resume-gate.json
?? quality/v10-s2r5-resume-historical-log-map.json
?? quality/v10-s2r5-resume-pres01-exception.json
?? quality/v10-s2r5-resume-preservation.json
?? quality/v10-s2r5-resume-result.md
?? quality/v10-s2r5-resume-valid-retest.json
?? quality/v10-s2r5-type-matrix.json
?? quality/v10-s2r5-valid-import.json
?? quality/v10-s6-after-s2r4-a8-deep.json
?? quality/v10-s6-after-s2r4-f02-retest.json
?? quality/v10-s6-after-s2r4-f03-retest.json
?? quality/v10-s6-after-s2r4-f04-retest.json
?? quality/v10-s6-after-s2r4-final-verification.json
?? quality/v10-s6-after-s2r4-focused.json
?? quality/v10-s6-after-s2r4-gate.json
?? quality/v10-s6-after-s2r4-matrix-revalidation.json
?? quality/v10-s6-after-s2r4-n9-retest.json
?? quality/v10-s6-after-s2r4-preservation.json
?? quality/v10-s6-after-s2r4-result.md
?? quality/v10-s6-after-s2r4-retained-chain-review.json
?? quality/v10-s6-after-s2r4-valid-import.json
?? quality/v10-s6-cei-result.json
?? quality/v10-s6-final-a8-deep.json
?? quality/v10-s6-final-a8-f03-result.json
?? quality/v10-s6-final-f01-n9-retest.json
?? quality/v10-s6-final-f02-retest.json
?? quality/v10-s6-final-focused.json
?? quality/v10-s6-final-impact-retained.json
?? quality/v10-s6-final-preservation.json
?? quality/v10-s6-final-result.md
?? quality/v10-s6-final-valid-import.json
?? quality/v10-s6-final-verification.json
?? quality/v10-s6-resume-a8-invariant-result.json
?? quality/v10-s6-resume-cei-result.json
?? quality/v10-s6-resume-recovery-result.json
?? quality/v10-s6-resume-result.md
?? quality/v10-s6-resume-upgrade-result.json
?? quality/v10-s6-upgrade-recovery-result.md
?? quality/v10-s6r1-a8-deep.json
?? quality/v10-s6r1-artifact-policy.json
?? quality/v10-s6r1-cp01-retest.json
?? quality/v10-s6r1-essential-retention.json
?? quality/v10-s6r1-f01-retest.json
?? quality/v10-s6r1-f02-retest.json
?? quality/v10-s6r1-f03-retest.json
?? quality/v10-s6r1-f04-retest.json
?? quality/v10-s6r1-final-verification.json
?? quality/v10-s6r1-focused.json
?? quality/v10-s6r1-gate.json
?? quality/v10-s6r1-impact-review.json
?? quality/v10-s6r1-preservation.json
?? quality/v10-s6r1-prior-extra-retention.json
?? quality/v10-s6r1-result.md
?? quality/v10-s6r1-retained-chain.json
?? quality/v10-s6r1-roundtrip.json
?? quality/v10-s6r1-valid-import.json
?? tasks/completed/v10-s2r2-cei-destination-compatibility.md
?? tasks/completed/v10-s2r3-cei-semantic-prewrite.md
?? tasks/completed/v10-s2r4-cei-semantic-prewrite.md
?? tasks/completed/v10-s2r5-cei-direct-input.md
?? tasks/completed/v10-s6-upgrade-recovery.md
?? tasks/completed/v10-s6r1-revalidation-after-s2r5.md
?? tasks/paused/v10-s2r4-cei-que003-before-expansion.md
?? tasks/paused/v10-s6-upgrade-recovery-after-s2r2.md
?? tasks/paused/v10-s6-upgrade-recovery-after-s2r3.md
?? tasks/paused/v10-s6-upgrade-recovery-after-s2r4.md
?? tasks/paused/v10-s6-upgrade-recovery.md
?? tasks/plans/v10-s6-upgrade-recovery-plan.md
?? tests/probe_v10_s2r3_semantic.py
?? tests/probe_v10_s6_a8_invariant.py
?? tests/probe_v10_s6_cei_prewrite.py
?? tests/probe_v10_s6_final_cei.py
?? tests/probe_v10_s6_resume.py
?? tests/test_cei_destination_compatibility.py
?? tests/test_cei_direct_structure.py
?? tests/test_cei_question_invariant.py
?? tests/test_cei_semantic_matrix.py
?? tests/test_cei_semantic_prewrite.py
```

Verificação final: quality/v10-s6r1-final-verification.json. Logs/XML/targets/ZIPs/cobertura/audit e manifestos locais permanecem fora do Git em work/s6r1-*.
