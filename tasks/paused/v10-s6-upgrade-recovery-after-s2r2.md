# Task Contract

Status: AUTHORIZED
Phase: BLOCKED
Checkpoint: A8 NEW FINDING S6-F02

## Identification

- Task ID: V1.0-S6
- Product version: V1.0
- Stage: S6 — Cadeia de upgrade e recuperação
- Task type: compatibility / upgrade / backup / restore / recovery / CEI evidence
- Size: L
- Risk: high
- Migration expectation: NO
- Potential data impact: HIGH
- A7 planned execution model: GPT-6 Sol High
- Effective authorized execution model: GPT-6.1 Sol High
- Model decision: human-authorized execution-model override for V1.0-S6 (2026-09-30); only this stage, without changing the global plan
- A8 review: deep


## Resume checkpoint — S2R2 completed (2026-09-30 20:57:39 -03:00)

- Current state: AUTHORIZED / IN EXECUTION / RESUME AFTER S2R2. The historical BLOCKED checkpoint below is preserved as history.
- S6-F01 RESOLVED by V1.0-S2R2. See quality/v10-s2r2-cei-destination-result.md and quality/v10-s2r2-n9-retest.json: N9 fresh target PASS / REJECTED_BEFORE_WRITE, zero INSERT/UPDATE/DELETE attempts, counts and fingerprints unchanged; full S2R2 gate exit 0 observed, 532 tests PASS, 86.5747% coverage, A8 deep APPROVED, Blocker/Major/Minor 0/0/0, migrations 0.
- Original N9 FAIL, first non-candidate preparation, valid eight-INSERT reproduction, probe and A4 remain intact; blocked contract remains byte-for-byte in tasks/paused/v10-s6-upgrade-recovery.md. Do not repeat already valid evidence without need or retroactively rewrite the FAIL as PASS.
- Pending S6 proofs remain pending: N1–N8 and independent upgrade chain, clean install, backup/restore/recovery, V0.5 CEI positive/round-trip and final integral S6 gate/A8 deep. S2R2 ends upon restoring this contract; no pending S6 proof was started in the remediation.
- S1–S5, S2R1 and S2R2 COMPLETED; S7–S10 NOT AUTHORIZED. S6 retains its human-authorized GPT-6.1 Sol High override. Git add/commit/push/tag/release remain unauthorized.
- Existing cached state at resumption: only .secrets.baseline is staged, by the separate explicit human S2R2 exception required by detect-secrets-hook; the 59 reviewed entries preserve all detectors/filters. No other staging, commit, push, tag or release was performed.

## Historical execution checkpoint — 2026-09-30

- S6 was AUTHORIZED / IN EXECUTION with the human-authorized GPT-6.1 Sol High override before any functional probe.
- Final decision for this execution: BLOCKED. Finding S6-F01 (Major): a valid V1 CEI package imported into a fresh empty V0.4.4-schema target executed eight successful INSERT statements before OperationalError on errors_error_category.category_kind. SQLite total_changes increased by eight; transaction rollback restored the logical and physical fingerprints. This is not REJECTED_BEFORE_WRITE.
- Evidence: quality/v10-s6-cei-result.json and quality/v10-s6-upgrade-recovery-result.md; reproducible opt-in probe tests/probe_v10_s6_cei_prewrite.py.
- Mandatory stop applied under section 13 of the functional authorization. No remaining functional proofs, application fix, gate or A8 were executed after this finding. S6 is not complete; do not archive this contract or return it to NO_TASK_AUTHORIZED.
- Probe targets are preserved as NON-CANDIDATE in the execution workspace; no original/active user database was touched. The first attempt failed during harness preparation before import and is preserved separately; it is not a product finding.
- S1–S5 and S2R1 remain COMPLETED; S7–S10 remain NOT AUTHORIZED. New migrations zero; no git add, commit, push, tag or release.

## Goal

Provar de forma reproduzível a cadeia de uma V0.4.4 representativa para V0.5 e candidato V1, além de instalação limpa, backup, restore, recovery e CEI em provas independentes. Estado final pretendido: upgrade/recuperação V1 comprovados.

## Context

- S1–S5 e S2R1 concluídas. Baseline de autorização: HEAD e origin/main em 5eb6930aba35a0d1083c92816a83c7c4c2451830, árvore inicial limpa.
- Plano oficial: tasks/plans/v10-release-execution-plan.md, seção S6. A4 obrigatório: tasks/plans/v10-s6-upgrade-recovery-plan.md, fechado antes de qualquer operação de risco.
- Contratos: docs/V1.0_S1_Contratos_e_Compatibilidade.md, docs/CEI_EXPORT_1_0.md, docs/V0.4_S6_Backup_e_Recuperacao.md e docs/V0.5_S7_Portabilidade_e_Restore.md.
- Fontes executáveis: MigrationExecutor em tests/test_v05_s2a_upgrade.py e provas relacionadas; services de backup/restore, portability.py, ui_services.py e integrity.py.
- Nenhum PASS S6 pode depender somente de evidência V0.5 antiga.

## Acceptance Criteria

- Cadeia V0.4.4 → V0.5 → V1 exercitada em cópias com migrations reais, backup pré, IDs, contagens, histórico, policies, derivados, fingerprints, SQLite integrity_check, foreign_key_check e checker reconciliados sem diferença inexplicada.
- Instalação limpa V1 comprovada independentemente, com migrations, schema, defaults, checks físicos/funcionais e smoke mínimo.
- Backup válido e corrompido, restore isolado, recovery offline em cópia, retorno e reconciliação comprovados; pré-backup preservado.
- Export CEI V0.5 válido → import V1 válido e round-trip aplicável; CEI-EXPORT-1.0 / format_version 1.0 mantidos, application_version identifica produtor. Só produtores V0.5/V1.0 estritamente compatíveis são aceitos.
- Pacotes/ambientes negativos cobrem produtor, migration, policy, schema, checksum, arquivo ausente/extra, UUID/referência e destino incompatível, com rejeição antes de escrita quando aplicável e fingerprint do destino.
- CT-113–120 e CT-122 mapeados a prova V1 nova; gate integral exit 0 observado; A8 deep aprovado sem Blocker/Major nem P0/P1 aplicável aberto.

## Expected Scope

- Fixtures e testes/harness sintéticos de upgrade, instalação, backup, restore, recovery, CEI e checker estritamente necessários à prova.
- Correção local de defeito concreto de compatibilidade S6 somente após reprodução e dentro dos contratos vigentes, sem migration nova automática.
- Evidências brutas e relatório consolidado S6 em quality/, este contrato e A4; atualização de PROJECT_STATE.md e arquivamento do contrato somente no fechamento futuro.
- Dados de execução exclusivamente fixtures, cópias e targets isolados.

## Protected Scope

- Banco original, banco ativo e dados reais; jamais restore, overwrite, importação ou recovery nesses alvos.
- Fatos históricos e contratos CEI/policies congelados; nenhuma conversão silenciosa, coerção, importação parcial, merge, remapeamento ou adaptação automática de schema.
- S7, S8, S9 e S10: NOT AUTHORIZED. Sem downgrade automático, tag ou release.
- Migration expectation NO. Necessidade real de migration exige parada HUMAN_DECISION_REQUIRED com análise de dados, reversibilidade, compatibilidade, risco e alternativas.

## Constraints

- A4 permanece fechado e aprovado antes de qualquer operação de risco, mesmo em cópia descartável. Execução funcional S6 explicitamente autorizada em 2026-09-30; todos os alvos de dados devem ser comprovadamente sintéticos e isolados.
- Validar integralmente CEI e compatibilidade efetiva do destino antes de escrita. Distinguir rejeição pré-escrita de rollback transacional.
- Parar em diferença inexplicada, perda semântica, ID/contagem divergente, backup/restore inválido, checker/SQLite/FK finding, CEI incompatível sem decisão, escrita prematura, migration inesperada ou risco de tocar original/ativo.
- Verificar modelo/esforço A7 antes da execução funcional. Se não corresponder ao plano autorizado, parar e reportar.
- Git add, commit, push, tag e release não são autorizados nesta execução funcional.

## Verification

- A4 define matriz, fingerprints, recovery e testes focados. Na execução funcional futura: testes de upgrade S6 e regressões relacionadas, backup/restore, CEI e checker.
- Ao final funcional: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1; observar exit 0, além de git diff --check e A8 deep.
- Nesta execução funcional: registrar provas, testes focados, comandos, contagens e tempos; executar gate integral somente após todas as provas. Finding de rejeição apenas após escrita exige parada e relatório.

## Documentation Impact

Execução funcional: contrato/estado/A4 e evidências necessárias da S6. Na conclusão funcional: quality/v10-s6-upgrade-recovery-result.md e tasks/completed/v10-s6-upgrade-recovery.md, com estado reconciliado.

## Done When

Todas as provas independentes e negativas V1 forem reproduzíveis, sem perda semântica ou mutação prematura; checker, SQLite/FK, fingerprints e recovery forem reconciliados; gate integral for GREEN com exit 0 observado; A8 deep aprovado; contrato arquivado e PROJECT_STATE.md atualizado. S7–S10 permanecem sem autorização até decisão humana própria.

## Human resumption authorization — 2026-09-30

- START_TIME resumed execution: 2026-09-30 21:31:07 -03:00. Human explicitly resumes functional S6 under GPT-6.1 Sol High, preserving A4 and historical S6/S2R2 files and targets.
- Incorporate N9 FAIL → S2R2 → final PASS without re-executing N9 merely formally. Do not modify the importer/preflight or reopen S2R2 without a new proved finding.
- Execute pending N1–N8, actual historical runtimes/migrations V0.4.4 → V0.5 → V1, independent clean install, backup/corruption/restore/offline recovery, real V0.5 CEI production and V1 round-trip, full reconciliation/checker and focused tests. Then own full S6 gate and A8 deep.
- Preserve old quality/v10-s6-cei-result.json and quality/v10-s6-upgrade-recovery-result.md byte-for-byte. New proof harness tests/probe_v10_s6_resume.py and new evidence quality/v10-s6-resume-cei-result.json, quality/v10-s6-resume-upgrade-result.json, quality/v10-s6-resume-recovery-result.json and quality/v10-s6-resume-result.md provide this execution's records.
- Stop on premature writing, unexplained differences, invalid backup/restore/recovery, checker/SQLite/FK findings. Migration/structural CEI change requires HUMAN_DECISION_REQUIRED. Preserve staged .secrets.baseline exception; no additional unnecessary staging; no commit/push/tag/release.
- Only after all acceptance criteria, archive S6 and set tasks/current.md NO_TASK_AUTHORIZED. S7–S10 remain NOT AUTHORIZED.

## Resumption stopped by final A8 — S6-F02

- Decision: BLOCKED. START_TIME 2026-09-30 21:31:07 -03:00; END_TIME 2026-09-30 22:16:47 -03:00; observed duration 0:45:40; human-authorized GPT-6.1 Sol High.
- Planned N1–N8 and supplementary checksum/reference cases PASS / REJECTED_BEFORE_WRITE. Historical chain, clean install, independent backup/corruption/restore/offline recovery, real V0.5 CEI positive and 21-set round-trip PASS. All evidence and targets preserved.
- Own integral S6 gate before A8 GREEN, observed exit 0, 532 tests PASS / 86.5746664% coverage / 491.4 s, pip-audit 0. This technical gate does not authorize closure after a new material A8 finding.
- A8 deep CHANGES_REQUESTED / NOT APPROVED. S6-F02 Major/P1 OPEN: checksum-valid CEI package with Attempt.is_correct=True while selected alternative differs from historical revision answer key is accepted and committed: INSERT attempts/completed 24/24, UPDATE/DELETE 0/0, total_changes +24, no rejection/rollback. Post-commit read-only checker 25 checks / 4 findings (ATT-001, ERR-001, REV-001, REV-002).
- Cause: package validator omits this semantic relational coherence; importer calls file-based read-only checker from inside atomic transaction, through another SQLite connection that sees the previous committed empty target. No product fix made. New migration/structural CEI change not demonstrated necessary.
- Mandatory stop immediately after reproduction; further diagnosis read-only and evidence/state recording only. Target work/s6-resume-20260930-a8-invariant preserved NON-CANDIDATE, never reused. No full gate or further functional proof after finding.
- New evidence quality/v10-s6-resume-a8-invariant-result.json and tests/probe_v10_s6_a8_invariant.py; consolidated quality/v10-s6-resume-result.md and previous three new JSONs. Original A4/FAIL/probe/S2R2 files and code/tests unchanged; S6-F01 remains RESOLVED.
- Blocker/Major/Minor = 0/1/0 open. S6 is NOT COMPLETED and NOT archived; current remains AUTHORIZED / BLOCKED, not NO_TASK_AUTHORIZED. Separate material remediation requires its own authorization under the authoritative policy. S1–S5/S2R1/S2R2 COMPLETED; S7–S10 NOT AUTHORIZED.
- Only .secrets.baseline remains staged under the earlier human exception; zero new entries or staging. No commit, push, tag or release; HEAD/origin/main remain original authorized SHA.
