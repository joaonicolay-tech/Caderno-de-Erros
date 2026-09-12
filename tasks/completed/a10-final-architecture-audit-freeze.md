# Task Contract

Status: COMPLETED

## Identification

- Task ID: A10
- Product version: Post-V0.3 operational architecture
- Stage: Final audit, consolidation, and freeze of Project Development Architecture v1.0
- Task type: operational architecture / final audit / consolidation
- Size: L
- Risk: medium

## Goal

Audit A1-A9 as one operational architecture, using the real A9 pilot as primary
evidence; correct proven issues, consolidate sources of truth, and decide
whether to freeze the resulting, simplified architecture as Project
Development Architecture v1.0.

## Context

- A1 baseline, A2 task-contract policy, A3 progressive disclosure, A4 task
  plans, A5 Codex configuration, A6 Skills, A7 model/reasoning/metrics policy,
  A8 code-review policy, and the completed A9 pilot were the audit subjects.
- The A7 bootstrap/authorization defect, Windows sandbox/ACL infrastructure
  incident, and metric classifications required explicit review.
- Real repository evidence and A9 took precedence over theoretical additions.

## Acceptance Criteria and scope

The authorized work required classification of A1–A9, correction of proven
conflicts/redundancy and the bootstrap defect, concise Architecture v1.0
documentation, validation of A6–A9, a deferred backlog, metrics, review, gate
and formal closure. It allowed only operational documentation, policies,
records and minimal supported corrections.

Protected throughout: Django functionality, business rules, migrations,
schema, functional tests, V0.3 baseline and tag, V0.4 roadmap, historical ADRs,
domain decisions, user data and personal Codex configuration. No Project
Starter, V0.4 work, feature, MCP, CI/CD, dashboard, Skill, `.codex/config.toml`,
commit, push, tag or release was authorized.

### Acceptance Criteria

- Each relevant A1-A9 component has a recorded KEEP, SIMPLIFY, FIX, REMOVE, or
  DEFER decision supported by repository or pilot evidence.
- Proven conflicts, redundancy, and the A7 bootstrap/authorization defect are
  resolved or explicitly deferred with rationale.
- A concise Project Development Architecture v1.0 definition consolidates
  objective, principles, sources of truth, authorization and execution
  workflows, disclosure, tasks/plans, Skills, gate, review, metrics,
  model/reasoning policy, completion, and evolution criteria.
- The four essential Skills, A7 policy, A8 policy, operational boundaries, and
  official post-A10 workflow are validated against the A9 pilot.
- Deferred v1.0 improvements and Project Starter extraction criteria are
  recorded without creating a Project Starter or beginning V0.4.

### Expected Scope

- Audit and, only when supported by evidence, simplify or correct the
  operational architecture and documentation from A1-A9.
- Review `AGENTS.md`, `tasks/`, A2/A3, A5, the four Skills, A7/A8 and A9.
- Create or update the minimal final Architecture v1.0 documentation,
  operational task records and A7 execution metrics needed to close A10.
- Archive A10 after all acceptance criteria and required verification pass.

### Constraints and Verification

- Prefer simplification; do not add a layer, Skill, MCP, CI/CD or Codex
  configuration without concrete evidence.
- Do not create Project Starter, start V0.4, alter product/migrations, create
  parallel architecture or perform Git/release actions.
- Keep the Windows ACL event classified as infrastructure and use `unknown`
  for unavailable quotas.
- Review the final diff under A8, run `git diff --check`, and require GREEN from
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quality.ps1`.

### Done When

- A1-A9, conflicts, redundancy, boundaries and bootstrap flow are resolved or
  explicitly deferred with evidence.
- Architecture v1.0, evolution criteria, official workflow and minimal backlog
  exist; A6-A9 evidence is incorporated.
- No Project Starter or V0.4 work is created or started.
- Diff check and gate pass, metrics are recorded, no P0/P1 remains, A10 is
  archived and `tasks/current.md` returns to `NO_TASK_AUTHORIZED`.

## Audit result

| Component | Decision | Result |
| --- | --- | --- |
| A1 baseline | SIMPLIFY | Retained as historical snapshot, no longer a current guide. |
| A2 task contract | FIX | Administrative bootstrap is now explicit, stops before execution and persists only the real executable contract. |
| A3 disclosure | KEEP | A9 proved proportional reading and stop/escalation rules sufficient. |
| A4 tasks/plans | KEEP | Plans remain optional; A10 needed none because its contract already decomposed the work. |
| A5 Codex config | KEEP | No evidence justified config or rules. |
| A6 start-task | KEEP | Correct authority/preflight boundary. |
| A6 implement-current-task | KEEP | Correct minimal implementation boundary. |
| A6 run-quality-gate | KEEP | Correct authoritative measurement boundary. |
| A6 finish-task | KEEP | Correct evidence/closure boundary. |
| A7 models/metrics | FIX | Kept lightweight policy; corrected contradictory A8 fields and strengthened consistency/provenance. |
| A8 code review | KEEP | A9 and A10 showed proportional value distinct from the gate. |
| A9 real pilot | KEEP | Primary operational evidence; completed without workaround or scope expansion. |

The only material process conflict was the A7 bootstrap path: a transient
"do not implement in this session" restriction and an incompatible Done When
had entered the durable contract. A2 now defines
`NO_TASK_AUTHORIZED → explicit administrative authorization → executable
AUTHORIZED contract → later execution session`. Skills remain execution
boundaries and never create authorization.

The second conflict was factual: the A8 JSONL line contained reasoning,
duration and quota values while its note and archived task said they were
unavailable. Those fields now read `unknown`, with correction provenance.

Residual overlap among AGENTS, A2/A3 and Skills is intentional and small:
rules, detailed policy and invocable phase have distinct responsibilities.
Accumulated chronological detail was removed from current `PROJECT_STATE.md`;
the evidence remains in ADRs, quality artifacts and completed tasks.

The Windows `.agents` owner/ACL failure, `SetNamedSecurityInfoW` error 5 and
`setup refresh had errors` remain an infrastructure incident already recorded
in metrics. No permanent architectural layer or troubleshooting mechanism was
created.

## Architecture v1.0 and freeze

`docs/PROJECT_DEVELOPMENT_ARCHITECTURE_V1.md` is the concise primary view. It
defines purpose, principles, component roles, sources of truth, authorization,
disclosure, lifecycle, optional plans, four Skills, implementation, tests,
review, gate, metrics, model/reasoning, finish, Git and evolution.

Official flow:

`authorization → start-task → minimal implementation → focused tests →
proportional review → gate → finish-task/state/archive/metrics → explicitly
authorized Git checkpoint`.

Mandatory, proportional and optional parts, and documentary/complex-task rules,
are stated in the primary document. A9 demonstrated the full low-risk path;
A10 demonstrated the architectural L/medium path with deep review.

All freeze criteria were satisfied: no relevant operational conflict remains;
A9 validated the flow; bootstrap has a durable solution; A6 boundaries are
clear; A8 and gate are complementary; A7 is sustainable; workflow and sources
are understandable; and no unjustified bureaucracy remains. Therefore Project
Development Architecture v1.0 is **APPROVED/FROZEN** as the operational
baseline. Freeze is evolutive, not absolute.

## DEFER and Project Starter assessment

- DEFER external standardization of duration, reasoning and quota capture until
  more comparable evidence or reliable environment support exists.
- DEFER Project Starter extraction until Architecture v1.0 is exercised in
  V0.4, including at least one more complex functional task.

Reusable candidates: A2, A3, A4 separation, A6 phase boundaries, A7/A8
principles and a single-gate interface. Caderno-specific: functional docs/ADRs,
state/roadmap, concrete gate/manifests, thresholds, tests and V0.3 evidence.
Parameterization would be required for names/versions, gate command, model/risk
taxonomy, document layout and evidence fields. No Starter was created.

## Review, verification and metrics

A8 depth: deep, because A10 is L/medium and changes the operational
architecture. Result: **APPROVED**, with no Blocker, Major or Minor finding.
Review covered Goal/Done When, expected/protected scope, source conflicts,
duplication, operational regression, references, metrics consistency and final
documentation.

- Focused validation: 11 JSONL records parsed; A8 corrected fields matched
  preserved evidence; Architecture references existed; protected-scope diff was
  empty.
- `git diff --check`: passed before the gate and after closure.
- Authoritative gate: GREEN on first pass, exit code 0, 119.9 s; final-tree
  confirmation also GREEN, exit code 0, 100.6 s.
- Tests: 280 passed in 75.80 s on the first pass and in 70.55 s on final
  confirmation; 87% global coverage in both.
- Other gate checks: lock/runtime, three settings profiles, unexpected and
  empty-database migrations, formatting, Ruff, mypy, domain coverage,
  detect-secrets and `pip-audit` passed.
- Applicable open P0/P1: none.

A10 metrics: model `gpt-5` from system-provided identity; reasoning,
started-at, task duration and 5h/weekly quota unavailable and therefore
`unknown`; one execution attempt; gate first pass true; no model escalation,
functional rework or infrastructure incident; low operational rework because
one atomic closure patch was rejected without applying content and split into
valid incremental patches; seven final changed files.

## Final state and non-actions

`PROJECT_STATE.md` now records the current baseline without duplicating the
chronological archive. `tasks/current.md` returned to
`NO_TASK_AUTHORIZED`. No functional behavior, migration, schema, business rule,
functional test, gate or V0.3 baseline changed. V0.4 was not started; Project
Starter was not created; no commit, push, tag or release occurred.

Immediate recommendation: use Architecture v1.0 in further real work under a
new explicit authorization before considering extraction or new automation.
