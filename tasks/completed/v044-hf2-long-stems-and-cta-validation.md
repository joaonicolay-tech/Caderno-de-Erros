# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: V0.4.4-HF2
- Product version: v0.4.4 candidate (tag not yet created)
- Stage: post-release UI hotfix and focused validation
- Task type: corrective UI hotfix + controlled end-to-end validation
- Size: S
- Risk: low/medium

## Goal

Correct the real visual-clamp failure for long question stems in the Review
Queue and validate the actionable-review CTA end to end with isolated,
synthetic scenarios, without changing review scheduling or policy.

## Context

- `v0.4.3` is a historical release tag and must remain immutable. This work
  prepares a later `v0.4.4` candidate; it does not create, move, delete, or
  overwrite either tag.
- A user smoke test found that a Queue item with an approximately 1,500-character
  stem displayed practically all of its text, contrary to UX2's intended
  compact two-line visual clamp. The complete value must remain available in
  the appropriate review/detail flow.
- Clarification: the Queue summary is capped at approximately 500 characters.
  This is a presentation-only maximum; shorter stems remain intact and a
  truncated summary signals continuation without changing the stored stem.
- UX2 established that actionable reviews are `OVERDUE` and `DUE`, while
  `FUTURE` reviews are excluded; the CTA follows the Queue's existing order:
  `current_due_date`, `created_at`, `id`.
- Required sources: `tasks/completed/v043-ux2-review-queue.md`,
  `quality/v043-ux2-review-queue-result.md`, the Queue template/styles,
  directly related views/selectors/tests, and the normative temporal-policy
  source if its current behavior needs confirmation.

## Acceptance Criteria

- Before changing code, reproduce when technically possible the Queue behavior
  with a synthetic approximately 1,500-character stem; record the observed
  failure and its root cause after auditing the rendered text element, applied
  CSS classes/selectors, loaded stylesheet, specificity, desktop and narrow
  widths, existing UX2 tests, and prior UX2 evidence.
- The Queue presents a compact, approximately two-line visual clamp with
  ellipsis/controlled height for that long stem; short stems remain normal,
  metadata remains visible, and no horizontal overflow, overlap, or navigation
  break occurs on desktop and approximately 360 px.
- The stored stem is neither truncated nor replaced; its full text remains
  available in the appropriate review/detail flow and is not made accessible
  only through title, hover, or tooltip.
- A controlled, isolated synthetic validation confirms that the CTA can start
  an overdue review and a review due today, selects the item defined by the
  existing ordering, and never selects a future review.
- A scenario with no overdue or due reviews and only future reviews confirms
  the existing coherent no-action behavior and does not start a future review.
- Regression coverage preserves the dashboard drill-down, Workspace isolation,
  and the existing no-N+1 guarantee; no migration is created.

## Expected Scope

- Directly related Review Queue template, stylesheet, view/selector integration,
  focused tests, and proportional HF2 evidence/review/state records required
  at task closure.
- Isolated fixtures, temporary database data, or other disposable controlled
  test setup needed to validate the CTA and the long-stem scenario, with
  cleanup recorded.

## Protected Scope

- `ReviewStatusPolicy`, D1/D7/D14/D30 rules, date rules, and scheduling.
- `AnalyticsService`, S1 semantics, Attempts, backup/recovery, integrity
  checker, architecture, Skills, and `scripts/quality.ps1`.
- Queue structure introduced by V0.4.2/V0.4.3 and dashboard design, except for
  the minimal clamp correction and regression fixes directly proven necessary.
- Workspace boundaries, existing query strategy/no-N+1 behavior, schema, and
  migrations.

## Constraints

- Identify the clamp failure's cause before correcting it; do not accept merely
  the presence of a CSS class as proof of rendered behavior.
- Preserve the existing CTA semantics and ordering; do not redefine priorities
  between overdue and due reviews or alter scheduling.
- Do not change permanent real-user review dates for validation. Prefer
  fixtures, isolated databases, synthetic data, or disposable environments;
  document cleanup if development data is used.
- Validate browser rendering with the long synthetic stem on desktop and near
  360 px. Validate 200% zoom when real observation is possible; otherwise
  record that limitation without claiming a visual pass.
- Do not redesign the Queue, start V0.5, create a migration, commit, push,
  create a release, or create/alter tags. `v0.4.3` remains immutable and
  `v0.4.4` must still not exist at task closure.

## Verification

- Focused automated tests cover short and long stems, full-stem availability,
  CTA overdue, CTA due today, future exclusion, policy ordering, only-future
  no-action behavior, dashboard drill-down, Workspace, and query count.
- Controlled browser validation records the pre-fix reproduction, post-fix
  long-stem rendering, full content in review/detail, CTA overdue/due behavior,
  future exclusion, only-future behavior, responsive widths, and zoom result
  or limitation.
- Standard A8 review must be `APPROVED` with no Blocker or Major.
- Run `git diff --check` and
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`;
  the final gate must be GREEN. Classify a `pip-audit` network failure under
  the applicable infrastructure/retry policy; do not modify the gate script.

## Documentation Impact

- At closure, record proportional HF2 evidence: reproduction, root cause,
  correction, controlled CTA scenarios and cleanup, manual results,
  accessibility/responsiveness/zoom evidence or limitations, review, and gate.
- Update `PROJECT_STATE.md` at closure to state: `v0.4.3` remains historical,
  HF2 completed, a `v0.4.4` candidate is prepared but its tag is not created,
  and V0.5 remains `NOT AUTHORIZED`.
- Record HF2 separately from bootstrap in A7 metrics, without estimating
  duration or quotas.

## Done When

- The approximately 1,500-character Queue failure has a recorded pre-fix
  reproduction, identified root cause, and verified rendered correction.
- Full content remains available outside the visual clamp; short text,
  metadata, responsive layout, accessibility, and existing navigation are
  preserved.
- Controlled overdue, due-today, only-future, ordering, and future-exclusion
  CTA scenarios are verified and temporary data is cleaned up.
- Scheduling, Workspace isolation, no-N+1 behavior, protected scope, schema,
  and migrations remain unchanged.
- Focused tests, manual evidence, standard A8 review, `git diff --check`, and
  the complete quality gate are green; any real zoom limitation is documented.
- Closure evidence and required state/metric records exist; the task is
  archived and `tasks/current.md` returns to `NO_TASK_AUTHORIZED` only after
  real completion. No `v0.4.4` tag, commit, push, release, or V0.5 work occurs.

## Encerramento observado

- A clarificação de 500 caracteres, a reprodução de ~1.500, a causa raiz, a
  correção, CTA, cleanup, A8 e gate estão em `quality/v044-hf2-result.md`.
- Não houve migration, alteração de policy/scheduling/analytics, tag, commit,
  push, release ou V0.5.
