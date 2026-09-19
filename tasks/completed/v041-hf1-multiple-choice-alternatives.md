# Task Contract

Status: COMPLETED

## Identification

- Task ID: V0.4.1-HF1
- Product version: V0.4.1
- Stage: post-release hotfix
- Task type: functional hotfix
- Size: M
- Risk: medium
- Target release: v0.4.1

## Goal

Audit and correct the multiple-choice alternative flow so it supports the product's correct number of options with the smallest sustainable change, preserving integrity, creation, editing, answering, correction, validation, history, and compatibility with existing questions.

## Context

Manual post-release testing identified that the question interface permitted only alternatives A-D. The normative sources are RF-011 in `docs/Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md` and RN-012 in `docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md`. `v0.4.0` is immutable; this task may prepare the repository for later human-authorized creation of `v0.4.1`, but must not create or mutate either tag.

## Acceptance Criteria

- The cause and normative rule are evidenced; no arbitrary maximum is assumed.
- Creation and editing preserve order, labels, a single correct alternative, non-empty/duplicate validation and the required minimum.
- Answering and correction render and process every stored alternative, including a correct alternative after D.
- Existing A-D questions, attempts, reviews, analytics, error classifications, history and Workspace isolation remain compatible.
- Focused regressions cover legacy A-D, more than four alternatives, a correct alternative after D, rendering/selection/correction, editing preservation and Workspace isolation.
- The A8 review is APPROVED with no open Blocker or Major finding.

## Expected Scope

- The question alternative flow and directly related focused tests across the audited forms, views/templates, services, validators, answering/correction flow and fixtures.
- A migration only if the audit proved it necessary and compatible.

## Protected Scope

- No change to S1–S8 protected components, BCR-1 thresholds, Architecture v1.0, Skills or `quality.ps1`.
- Do not start V0.5 or implement the review-queue context improvement.
- Do not add correction history belonging to V0.5.

## Constraints

- Do not hardcode a replacement A-D/E/F/fixed numerical limit; use sustainable labels for the evidenced supported range.
- Do not weaken validation merely to allow more fields.
- Preserve `v0.4.0`; do not create `v0.4.1`.
- Do not introduce a migration automatically.

## Verification

- Focused regression evidence: 92 PASS, reused because no functional changes occurred after that run; manual five-alternative/E-correct scenario passed.
- A8 standard review: APPROVED, no Blocker/Major/Minor open.
- `git diff --check`: exit 0 before closure.
- Authoritative gate: GREEN, exit 0; 332 PASS, 88% coverage and `pip-audit` clean after the authorized-network repetition.

## Documentation Impact

- `quality/v041-hf1-result.md` records defect, cause, normative rule, fix, compatibility, tests, manual test, gate, review, tags and target.
- `PROJECT_STATE.md` records the historical V0.4 release and HF1 closure.
- `quality/operational-execution-metrics.jsonl` records the execution and the preceding infrastructure/network incident.

## Done When

- All acceptance criteria, focused evidence, A8 review, diff check and authoritative gate have passed.
- No migration exists; `v0.4.0` is unchanged and `v0.4.1` is absent.
- The task is archived, `tasks/current.md` is `NO_TASK_AUTHORIZED`, the review queue remains outside scope and V0.5 remains unstarted.

## Closure Evidence

- Closed on 2026-09-19.
- Root cause: hardcoded four form fields and a four-alternative edit slice in the web layer, not model/schema storage.
- Normative rule: RF-011/RN-012 require two or more distinct text alternatives and exactly one correct answer; no maximum is defined.
- Implementation supports submitted/stored alternatives beyond D and labels A…Z, AA…; legacy questions remain compatible.
- First gate pass was inconclusive solely due to `pip-audit` network `WinError 10013`; classified `infrastructure/network`, with `gate_first_pass: false`.
- Final gate: GREEN, exit 0; 332 PASS, 88% coverage, all controls including `pip-audit` passed.
- A8 standard review: APPROVED, Blocker 0, Major 0, Minor 0.
- No migration, review-queue change, V0.5 work, commit, push, tag or release.
- `v0.4.0` was read-only verified unchanged; `v0.4.1` remains absent.
