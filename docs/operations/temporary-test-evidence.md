# Temporary test evidence

Before each audited test/probe run, classify its temporary artifacts in the run evidence manifest. A temporary SQLite target used solely as test scratch may be `DISPOSABLE / NOT_REQUIRED_FOR_FINAL_EVIDENCE`; this does not make it an original database, canonical backup or versionable deliverable.

Artifacts needed for later audit must instead be explicitly designated for retention and copied, with hashes, to a preserved evidence area before any cleanup. Preserve canonical results, necessary logs, historical RED cases and every artifact explicitly designated for retention. Record source paths logically in publishable evidence; private absolute prefixes remain local.

Use a fresh explicit `--basetemp` for audited focused pytest runs. Refuse reuse of an existing evidence root: pytest may clear an explicitly supplied base directory on reuse, and its default numbered roots have retention cleanup. Copy designated targets and verify their hashes after execution, before any permitted cleanup. Keep raw SQLite/ZIP files outside Git candidates; retain only necessary canonical reports in the repository.

The official quality gate remains unchanged and already selects a fresh unique basetemp. Its pytest scratch databases are disposable when the run manifest says so; preserve the gate log, exit/timing receipt, coverage/audit reports and test results. No permanent retention requirement applies to every SQLite created by pytest.

An absent artifact must be recorded as absent, with historical hash/result/reference and provenance if available. A new target provides fresh reproducibility and cannot be labeled byte-identical to an unavailable historical target. Any human exception must identify the exact files and must not weaken preservation for canonical evidence, active/user databases or real backups.

V1.0-S2R5 PRES-01: only11 historical synthetic numbered-root destination targets are `TEMP_ARTIFACT_MISSING / HUMAN_EXEMPTED` under the explicit2026-10-02 decision and individual registry quality/v10-s2r5-resume-pres01-exception.json. The original blocked findings/results remain historical facts.
