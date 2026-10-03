# Current Task Contract

Status: AUTHORIZED
Task ID: V1.0-S7R1
Phase: IN EXECUTION
Parent: V1.0-S7 — BLOCKED / PAUSED / RETOMÁVEL by S7-F01
A7 authorized model: GPT-6 Luna Medium
A8: standard
Migration expectation: NO

## Scope

Remediate only S7-F01 by exposing the existing `PRODUCT_VERSION` (`V1.0`) through a common template context and base HTML template, with focused tests. Investigate the base template, global context mechanisms, version source and existing template/layout tests before editing. No independent hardcode, redesign, route, feature, database/schema/model/migration/dependency/lock change, CEI/package/product version change, or unrelated file change.

## Required evidence

Prove that UI output equals the canonical `PRODUCT_VERSION`, appears on a shared page, remains semantic/accessibility-friendly and discreet, and does not interfere with layout. Check representative structure at 360px, desktop width and 1920px using available proportional test/inspection evidence without reopening all S4 browser validation. Keep product `V1.0`, package `1.0.0` and CEI `CEI-EXPORT-1.0` / `format_version=1.0` distinct.

Run focused version/base-template/layout tests, `makemigrations --check --dry-run` (expect no changes), the full `scripts/quality.ps1` gate because functional UI code changes, and an independent A8 standard review. Preserve logs and evidence without personal paths/secrets. Do not run full CT-127, S7 documentation proofs, or later stages.

## Stop rules

Stop on material normative conflict (`HUMAN_DECISION_REQUIRED`, recommend GPT-6 Luna High), unexpected model/schema/migration/dependency or broader product issue, failed gate, privacy concern, or a scope-expanding implementation requirement. Do not silently alter S1 or the product version.

## Completion

Complete S7R1 only when S7-F01 is `FIX_VERIFIED`, focused tests and migration check pass, the integral gate exits 0, A8 standard is APPROVED with no Blocker/Major, and privacy/scope checks pass. Then record S7R1 completion and restore parent S7 to `AUTHORIZED / IN EXECUTION / RESUME AFTER S7R1`; do not continue remaining S7 in this turn. S8–S10 remain `NOT AUTHORIZED`. No git add, commit, push, tag or release.

---

## Completion outcome

S7R1_COMPLETED. S7-F01 FIX_VERIFIED and RESOLVED. The shared UI renders the canonical PRODUCT_VERSION in the base footer through shared.application.context_processors.product_identity; focused tests, migration check and full quality gate passed. A8 standard APPROVED with 0 Blocker / 0 Major / 0 Minor. Full execution evidence: quality/v10-s7r1-ui-product-version-result.md. Parent S7 is resumable and remains AUTHORIZED / IN EXECUTION after this subtask. No S7 remainder, CT-127, documentation proofs or future stage was run.