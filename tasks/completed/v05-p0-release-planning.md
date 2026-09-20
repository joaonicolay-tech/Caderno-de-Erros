# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: `V0.5-P0`
- Product version: `V0.5`
- Stage: `P0 — Planejamento oficial e executável da release`
- Task type: release planning / scope audit / execution decomposition
- Size: `L`
- Risk: `high`
- Recommended execution model: `GPT-5.6 Sol`
- Recommended reasoning: `High`
- Required review: A8 `profundo`
- Required plan: this task produces `tasks/plans/v05-release-execution-plan.md`; no
  separate A4 plan is required before this planning work.

## Goal

Produce a durable, official, and executable V0.5 release plan, grounded in the
authoritative Roadmap and applicable project sources. The plan must establish
the real V0.5 scope, audit existing implementation, separate V0.5 from V1.0
and Post-V1, and decompose only V0.5 into independently authorizable stages.

## Context

- The V0.4.4 baseline must be verified before planning conclusions are made;
  V0.5 implementation has not started.
- `tasks/current.md` authorizes only this P0. `PROJECT_STATE.md` records state
  and is not authorization.
- Follow `docs/A3_Progressive_Disclosure.md`; this is planning and release
  delimitation, so read the official Roadmap, applicable requirements/rules,
  relevant ADRs, `PROJECT_STATE.md`, prior release plans/evidence, and only the
  code/tests necessary to audit existing capabilities.
- Preserve approved V0.4 semantics and the frozen operational architecture
  unless an authoritative V0.5 requirement explicitly requires otherwise.

## Preconditions

- Confirm the V0.4.4 baseline and reconcile any material drift among Git,
  `PROJECT_STATE.md`, and the official Roadmap before relying on it. Do not
  silently resolve a material inconsistency.

## Acceptance Criteria

- Identify V0.5 scope from authoritative sources, rather than this contract
  alone, and explicitly list V1.0/Post-V1 and other excluded work.
- Produce a scope-audit matrix for every official V0.5 item with source rule,
  description, status (`NOT_STARTED`, `PARTIAL`,
  `EXISTING_BUT_NEEDS_HARDENING`, `COMPLETE`, or `OUT_OF_SCOPE`), code and test
  evidence, dependencies, risk, complexity, gaps, and candidate stage.
- Audit reusable V0.4 interfaces for Questions, Attempts, Reviews,
  ErrorClassification, Analytics, Workspace, S5, S6, S7, consultation/detail/
  history, dashboard, filters, integrity, and operational documentation.
- Determine the normative meanings and effects of V0.5 domain and priority;
  do not infer discipline, category, Workspace, automatic scoring, or review/
  analytics effects absent a source.
- Determine the actual V0.5 scope for advanced management, advanced integrity,
  portability, and operation; distinguish backup, restore, functional export,
  and operational portability.
- Map likely schema impact by stage as `migration expected`, `migration
  unlikely`, or `unknown pending design`, including compatibility, defaults,
  backfill, reversibility, prior backups, checker, and test effects.
- Preserve frozen semantics for analytics, scheduling, performed versus
  registered, ErrorClassification, history, and filters unless an official
  V0.5 rule explicitly changes them.
- Create an acyclic dependency graph distinguishing mandatory and convenient
  dependencies and parallelizable stages.
- Decompose V0.5 into small, ordered, independently authorizable stages. For
  every stage specify ID, name, goal, scope, exclusions, dependencies, size,
  risk, migration expectation, A4 requirement, A8 review level, recommended
  A7 model/reasoning, and principal completion criteria.
- Apply A4 policy proportionally: XS/S normally no plan, M checklist when
  sufficient, L plan required, and XL decomposed before execution. Apply A7
  proportionally, without selecting an expensive model by size alone, and A8
  proportionally with stronger review for data/integrity/portability risk.
- Define a V0.5 promotion gate based only on applicable scope, including as
  justified tests, migrations, quality controls, S5/S6, compatibility,
  portability, documentation, pilot, performance/BCR, and open severity
  conditions. Do not invent thresholds or blindly copy V0.4.
- Include `REUSED_FROM_V0.4`, `OPEN_DECISIONS`, a proportionate risk register,
  documentation impacts, pilot assessment, and rollback/recovery plan when
  V0.5 changes make them applicable.
- Create `tasks/plans/v05-release-execution-plan.md` as a recoverable planning
  artifact useful to future execution, audit, selective recovery, and release
  promotion.
- Complete A8 deep review with result `APPROVED` and no Blocker/Major in the
  plan; archive P0, update project state, and return this file to
  `NO_TASK_AUTHORIZED` without authorizing a functional V0.5 stage.

## Expected Scope

- Planning documentation, scoped source/code/test audit, evidence needed to
  support the plan, A8 review, task archival, and applicable project-state
  update.
- No functional V0.5 code, migration, backfill, feature, or operational data
  change is within scope.

## Protected Scope

- Do not change the official Roadmap, approved requirements/rules, ADRs,
  frozen V0.4 semantics, `scripts/quality.ps1`, historical V0.4.x tags, or
  V0.4.x release state during P0.
- Do not implement, authorize, or start V0.5-S1 or any later functional stage.
- Do not import V1.0/Post-V1 work, authentication, API, external integration,
  AI, OCR, attachments, notifications, or gamification unless authoritative
  sources classify an item as V0.5.

## Constraints

- Planning must be evidence-led and proportionate; record actual gaps and
  unresolved questions rather than inventing requirements, metrics, thresholds,
  decisions, or PASS evidence.
- The S5 checker remains read-only; do not turn it into a repair tool without a
  separate explicit requirement.
- Do not create migrations during P0. Record proven defects outside the plan
  separately; do not repair them unless separately authorized.
- Commit, push, tag, release, and any V0.4.x patch require separate explicit
  authorization.

## Verification

- Perform only proportional read-only checks necessary to establish documented
  facts; use code/tests to substantiate the implementation audit.
- Review the plan deeply for Roadmap fidelity, exclusion boundaries,
  decomposition, dependencies, schema impact, risks, promotion gate, and A4/
  A7/A8 compliance.
- Run `git diff --check`.
- Run the authoritative quality gate if required by the applicable architecture
  for documentary closure; do not treat an inconclusive external audit as PASS.

## Documentation Impact

- Create `tasks/plans/v05-release-execution-plan.md` only during execution.
- At proven closure, record the planning state in `PROJECT_STATE.md`, archive
  this contract under `tasks/completed/`, and restore `tasks/current.md` to
  `NO_TASK_AUTHORIZED`. Do not prepare an authorized functional successor.

## Done When

- The V0.4.4 baseline is verified; official V0.5 scope, exclusions, existing
  implementation, gaps, dependencies, risks, likely migrations, open decisions,
  and promotion criteria are evidenced in the persistent plan.
- The plan contains the required audit matrix, dependency graph, executable
  stage decomposition, `REUSED_FROM_V0.4`, `OPEN_DECISIONS`, risk register,
  promotion gate, pilot assessment, and applicable recovery/rollback guidance.
- Every candidate stage has proportionate size, risk, migration, A4, A7, A8,
  dependency, scope, exclusion, and completion guidance.
- The plan's A8 deep review is `APPROVED` with no Blocker/Major.
- P0 is archived, project state is updated to show planning complete and V0.5
  implementation not started, and this file is `NO_TASK_AUTHORIZED`.
- No functional V0.5 work, migration, V0.4.x patch, commit, push, tag, or
  release has been performed or authorized as a consequence of P0.

## Closure Evidence

- Baseline: `main`, `HEAD` and `origin/main` at
  `46e887e0c4fa4dd6f7e128ab63802223d99c9e29`; annotated `v0.4.4` object
  `1938283f8a473054f443fc2733aaf462b861f713` peels to that commit.
- A8 deep plan review: `APPROVED`, Blocker 0, Major 0, Minor 0; see
  `tasks/plans/v05-release-execution-plan.md` §10.
- Final authoritative gate: exit 0 on 2026-09-20; 338 passed, 88% coverage,
  clean migrations/format/Ruff/mypy/detect-secrets/pip-audit. The initial
  sandbox pass was inconclusive only at pip-audit (`WinError 10013`); the
  authorized-network repeat was GREEN in 127.6 s.
- `git diff --check`: PASS before closure; no functional code, migration,
  backfill, operational-data change, commit, push, tag, release, or V0.5-S1
  authorization.
