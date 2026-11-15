# Task Contract

Status: AUTHORIZED

## Identification

- Task ID: v10-local-r1-public-source-preparation
- Product version: V1.0 Local r1 / 1.0.0
- Stage: Local Git integration and public source release preparation
- Task type: implementation, integration, documentation and verification
- Size: L
- Risk: high

## Goal

Prepare local commits on an isolated branch based on the audited public reference,
integrating the necessary v014 source and a reproducible source distribution.
The owner's current request explicitly permits implementation, proportionate
tests and local commits. Push, tags and GitHub Release publication are prohibited
pending a later decision.

## Context

Use the completed pre-publication inventory (155 items) and candidate comparison
(307 files). Preserve the original main checkout, its six unpublished commits,
private history and approved v014 candidate/ZIP. The historical S8 contract at
the public base is superseded only in this isolated checkout; its original bytes
remain in the audited base commit. No historical S8 operation is authorized.
References: AGENTS.md, docs/A2_Contrato_de_Tarefa_Atual.md,
docs/A3_Progressive_Disclosure.md, ADR-002, ADR-008, and the Local r1 audit.

## Acceptance Criteria

- Necessary product, tests and locked dependencies from v014 are integrated.
- Public source build and synthetic verification need no private evidence.
- Documentation declares Chrome-only scope, no universal installer and no
  transfer of private installation approval to new hosts.
- Public content and all outgoing ancestry are inspected for private payloads.
- Applicable gates pass; final commit SHA and limitations are reported.

## Expected Scope

Product/configuration/test/script deltas for source reproducibility; public
allowlists/manifests; release/installation/operation documentation; additive
normative reconciliation, state and a concise sanitized quality record.
Archive this contract and restore current.md to NO_TASK_AUTHORIZED on completion.

## Protected Scope

Original main/index/pending files; six unpublished commits; v014 and its ZIP and
evidence; historical originals, D2, personal databases, backups, secrets, ACL/owner
policy and consumed STOPs. No migration changes or real-data operations.

## Constraints

No push, tag or Release. No visual redesign or advanced launcher. No private
markers/approval records copied. No historical gate enumerating protected
storage. New synthetic files stay under this task's workspace. Security,
containment or identity failure stops the affected operation; ordinary code or
harness failures may be fixed while preserving their results.

## Verification

Positive-list source build, hash/ZIP verification, lint/format, typing, applicable
regression and synthetic integration tests, secret/path scan of outgoing commits
and ancestor review. Reuse unchanged evidence with its original scope; do not
repeat historical recovery or human CT-126. The task's source gate supersedes
the historical quality.ps1 for this isolated source-distribution scope only.

For an ordinary source-harness defect, preserve the complete failing run and
reuse its passing cases only after proving unchanged product/dependency bytes
and unchanged other test ASTs. Retest the corrected case and affected packaging
checks, then complete remaining gate phases in a new composition record. Never
rename the original failed run PASS or change the migration/catalog oracle.

## Documentation Impact

README, Local r1 notes/operation/source-distribution guide, normative addenda,
state and sanitized verification/provenance summary.

## Done When

Local commits and final source artifact are reviewable, checks agree with the
proposed SHA, private history is preserved and no public mutation occurred.
