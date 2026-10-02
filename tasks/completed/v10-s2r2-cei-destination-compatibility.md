# Task Contract — V1.0-S2R2

Status: COMPLETED
Phase: S2R2_COMPLETED

## Identification

- Task ID: V1.0-S2R2
- Product version: V1.0
- Stage: S2R2 — CEI pre-write destination compatibility remediation
- Type: integrity / compatibility / regression
- Size: M
- Risk: high
- Migration expectation: NO
- Authorized execution model: GPT-6.1 Sol High
- Review A8: deep
- START_TIME: 2026-09-30 20:04:05 -03:00

## Goal

Resolve S6-F01 through the smallest compatible pre-write destination validation in the existing CEI import path. An incompatible destination must reject before the first INSERT, UPDATE or DELETE attempt; compatible empty imports must continue working.

## Context

- Human authorization of 2026-09-30 exclusively authorizes S2R2. S1–S5 and S2R1 are COMPLETED; S6 remains AUTHORIZED / BLOCKED / PAUSED / RETOMÁVEL. Its contract is preserved byte-for-byte in tasks/paused/v10-s6-upgrade-recovery.md.
- Baseline HEAD = origin/main = 5eb6930aba35a0d1083c92816a83c7c4c2451830. Existing authorized changes: S6 administrative files PROJECT_STATE.md/tasks/current.md/A4, S6 harness tests/probe_v10_s6_cei_prewrite.py and S6 evidence quality/v10-s6-cei-result.json/quality/v10-s6-upgrade-recovery-result.md.
- S6-F01 Major was reproduced with eight successful INSERTs into a V0.4.4-schema target (24 migrations) for a valid V1 CEI package (34 migrations), followed by missing category_kind and rollback. Preserve the original FAIL, first non-candidate attempt and valid reproduction without edits.
- Read the S6 A4, V1 frozen compatibility contract, docs/CEI_EXPORT_1_0.md and the existing import/validation, migration, schema and tests.

## Acceptance Criteria

- Applied migrations and required real tables/columns/schema are validated before any data write attempt, without migration/repair/fallback in import.
- Automated regression reconstructs the historical incompatible destination, instruments attempted INSERT/UPDATE/DELETE and proves rejection with the correct compatibility error, zero attempts and unchanged row counts/fingerprints.
- Fresh N9 target retest is PASS / REJECTED_BEFORE_WRITE with zero INSERT/UPDATE/DELETE, no partial effect, counts/fingerprints preserved.
- Valid empty CEI import, round-trip and related package validation regressions remain PASS.
- New migrations zero; gate scripts/quality.ps1 exit 0 observed; A8 deep APPROVED; Blocker 0 / Major 0.

## Expected Scope

- Minimal destination guard and transaction placement in src/modules/data_management/portability.py.
- Focused automated regressions for this finding and actual schema damage, plus tests of valid import and transaction isolation.
- A distinct fresh N9 retest using the unchanged S6 probe, without modifying or reusing historical evidence/targets.
- Remediation evidence in quality/v10-s2r2-cei-destination-result.md and quality/v10-s2r2-n9-retest.json; task/state synchronization, paused S6 contract and completed S2R2 contract when eligible.

## Protected Scope

- A4 S6, S6 probe and original FAIL evidence remain byte-for-byte unchanged.
- CEI-EXPORT-1.0, format_version 1.0, producer policy, schema/migrations, package semantics, Workspace isolation and histories.
- No merge, conversion, coercion, automatic adaptation or partial import.
- No original/active user database operations; all data-changing tests use new synthetic/disposable targets.
- S7–S10 NOT AUTHORIZED. Do not execute pending S6 proofs as substitutes for S6.
- No git add, commit, push, tag or release.

## A4 — Remediation sequence and safety

1. Confirm baseline/diff classification; preserve S6 files and copy its contract before replacing tasks/current.md.
2. Locate import_into_empty, _schema_migrations, applied-migration reads, transaction boundary and first User/record INSERT.
3. Add an automated red regression using MigrationExecutor V0.4.4 and an execution wrapper recording attempts before execute, plus native SQLite changes and full before/after fingerprints.
4. Validate destination applied migration parity and concrete table/column metadata by reads; move destination emptiness validation into the same transaction as the guard and writes, addressing the relevant local TOCTOU interval. No schema writes occur in the guard.
5. Add cases with current migration metadata but damaged real schema; demonstrate correct pre-write rejection. Existing compatible import remains the positive control.
6. Run focused tests and fresh N9 retest, preserve before/after evidence separately; then run the full project gate and deep review.
7. Unexpected migration/architecture/format change requires HUMAN_DECISION_REQUIRED. Unexplained regression or gate failure prevents completion.

## Verification

- tests/test_cei_destination_compatibility.py and tests/test_v05_s7_portability.py.
- Unmodified tests/probe_v10_s6_cei_prewrite.py with a fresh isolated root, separate quality/v10-s2r2-n9-retest.json.
- Full powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1, observed exit 0; deep A8 review of order, transaction, TOCTOU, schema/migrations, valid/invalid imports and side effects.
- Finish with preserved-file hash comparison, git diff --check and git status --short.

## Documentation Impact / Done When

After all acceptance checks: mark S6-F01 RESOLVED in the remediation record, preserve original FAIL unchanged, archive S2R2 at tasks/completed/v10-s2r2-cei-destination-compatibility.md and restore S6 as AUTHORIZED / IN EXECUTION / RESUME AFTER S2R2. End this execution; S6 remaining proofs and its final gate/A8 run only on resumption. S7–S10 remain NOT AUTHORIZED.

## Human authorization addenda — 2026-09-30

- The official gate passed 532 tests/domain coverage but failed secrets on exact public Git SHAs and generated evidence fingerprints in the protected S6 files. Originals must not be changed.
- Automatic approval review rejected a persistent .secrets.baseline update without explicit authorization. The human then expressly authorized the reviewed proposal: 59 exact false-positive entries for public Git IDs/generated SHA-256 evidence digests, preserving all plugins, filters and prior entries. Proposal/evidence is saved in this execution's outputs/secrets-baseline-proposta.diff and outputs/s2r2-hashes-revisados.json.
- The official detect-secrets-hook refused the unstaged changed baseline. The human separately authorized the narrow exception git add -- .secrets.baseline only. Verify the cached list contains only that file. No other staging, commit, push, tag or release is authorized.
- These two explicit human addenda extend this contract only for this required gate control. Do not add broader exclusions or alter protected S6 evidence. S6 remains paused until S2R2 acceptance and formal restoration.

## Closure — 2026-09-30 20:57:39 -03:00

S2R2_COMPLETED; S6-F01 RESOLVED. Final N9 zero INSERT/UPDATE/DELETE attempts; 32 focused tests PASS; full official gate exit 0 observed, 532 tests PASS, 86.5747% coverage, pip-audit clean; A8 deep APPROVED, Blocker/Major/Minor 0/0/0, migrations 0. Evidence quality/v10-s2r2-cei-destination-result.md and quality/v10-s2r2-n9-retest.json. Protected S6 originals preserved byte-for-byte. S6 restored AUTHORIZED / IN EXECUTION / RESUME AFTER S2R2; no remaining S6 proofs executed. S7–S10 NOT AUTHORIZED; human separately authorized the exact 59-entry .secrets.baseline false-positive update and staging only of that file, required by the official hook. No other staging/commit/push/tag/release. START_TIME 2026-09-30 20:04:05 -03:00; END_TIME 2026-09-30 20:57:39 -03:00; duration 0:53:34.
