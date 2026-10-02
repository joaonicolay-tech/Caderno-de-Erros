# Task Contract

Status: COMPLETED
Phase: COMPLETED
Checkpoint: S2R3_COMPLETED

## Identification

- Task ID: V1.0-S2R3
- Product version: V1.0
- Task type: CEI semantic pre-write validation remediation
- Size: L
- Risk: high; potential data impact HIGH
- Migration expectation: NO
- Effective human-authorized model: GPT-6.1 Sol High
- A8 review: deep
- START_TIME: 2026-09-30 22:29:35 -03:00 (observed Get-Date)

## Goal

Resolve S6-F02: reject the same semantically inconsistent CEI package before the first attempted INSERT/UPDATE/DELETE in the final destination. Preserve valid imports and S6-F01/N9 pre-write protection.

## Context and authoritative scope

Human authorization V1.0-S2R3 dated 2026-09-30 authorizes only this remediation. Published HEAD/origin/main remain 5eb6930aba35a0d1083c92816a83c7c4c2451830. Current working changes are authorized S6/S2R2 evidence/code, contracts/state, operational S6 metrics and previously authorized staged .secrets.baseline.

S1–S5/S2R1/S2R2 COMPLETED. S6 remains BLOCKED/PAUSED/RETOMABLE for S6-F02; its latest blocked contract is preserved byte for byte at tasks/paused/v10-s6-upgrade-recovery-after-s2r2.md, in addition to the immutable original F01 pause. S7–S10 NOT AUTHORIZED.

## Acceptance Criteria

- Root cause and the four checker invariants/affected records identified before fix; original 24 committed INSERTs and four findings preserved as RED HISTORICAL EVIDENCE; automated regression runs RED before product changes.
- Same incompatible package fresh-target retest REJECTED_BEFORE_WRITE: attempted/completed DML 0/0/0, SQLite total_changes delta 0, complete counts and logical/schema/physical fingerprints unchanged; invariant codes explicit.
- Focused negatives for ATT-001/ERR-001/REV-001/REV-002 and combination; representative valid history/corrections/revisions/filters/domain/audit/relationships/policies/UUID imports remain PASS; S6-F01 essential fresh N9 retest zero DML.
- Small extension reuses existing normative rules without weakening checker. Prefer package in-memory validation; any relational staging must be wholly isolated from final destination. No partial import, rollback substitute, merge, coercion, repair, schema adaptation or dropped facts.
- No new migrations/schema/producer policy/CEI format changes; CEI-EXPORT-1.0 and format_version 1.0 unchanged.
- Own integral S2R3 quality.ps1 exit 0 observed; focused tests PASS; A8 deep APPROVED; Blocker/Major 0. Only then S2R3_COMPLETED and S6-F02 RESOLVED.

## Expected Scope

Inspect portability.py, integrity.py and relevant models/tests. Add smallest semantic preflight and required focused regression/probe/evidence; new quality/v10-s2r3-* evidence, tests/test_cei_semantic_prewrite.py or necessary opt-in probe, current/state/closure and scoped operational metrics. Expose/reuse normative query logic only if needed; no change to checker findings/rules.

## Protected Scope and Stop Rules

- Preserve all prior S6/S2R2 evidence, A4, probes, targets, negative/positive proofs, logs, valid packages and the inconsistent original package byte for byte. Fix files may change as explicitly scoped, never reinterpret past FAIL as PASS.
- Only synthetic isolated final destinations; no real/original/active user databases. No S6 functional resumption inside S2R3 and no future stages.
- Material architecture, significant import pipeline change, new format/contract or migration required: stop HUMAN_DECISION_REQUIRED before implementation. Do not infer staging/repair authority on real destination.
- Preserve .secrets.baseline and its authorized staged state; no additional staging, commit, push, tag or release.

## Verification and Closure

Run automated RED before fix; fresh exact-package and N9 retests; semantic negatives and valid regressions with counts/attempt counters and fingerprints; then powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1 and own A8 deep. Observe actual values, timings, git diff --check/status; record 40 requested fields.

Only after completion archive S2R3 at tasks/completed/v10-s2r3-cei-semantic-prewrite.md and restore preserved S6 as AUTHORIZED / IN EXECUTION / RESUME AFTER S2R3, with its historical checkpoints intact. Existing S6 proofs remain valid unless directly affected; future S6 needs its own affected-CEI retests, full final gate and A8. Stop this task after report; do not automatically resume S6.

## Closure — 2026-09-30 23:05:20 -03:00

S2R3_COMPLETED; duration 0:35:45; S6-F02 RESOLVED. Own gate exit 0: 543 PASS / 86.6284362% coverage / audit 0; 43 focused PASS. A8 deep APPROVED, Blocker/Major/Minor 0/0/0. Exact preserved package rejects with four explicit codes before 0/0/0 attempted/completed DML, total_changes 0, all counts and fingerprints equal. N9 regression PASS. No migrations, format changes, baseline changes/additional staging or Git publication. Evidence quality/v10-s2r3-cei-semantic-result.md and companion JSONs. S6 restored for future affected CEI proofs and its own final gate/A8, not resumed here; S7–S10 NOT AUTHORIZED.
