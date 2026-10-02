"""A8 S6: measure rejection of inconsistent Attempt.is_correct before DML."""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def main() -> int:
    if not __debug__:
        raise SystemExit("Assertions required; do not use -O")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.absolute()
    if (
        not root.name.startswith("s6-resume-")
        or not root.parent.is_dir()
        or root.exists()
        or any(p.is_symlink() or p.is_junction() for p in (root, *root.parents))
    ):
        raise SystemExit("Requires fresh direct isolated audit root")
    root.mkdir()
    target = root / "invariant-target.sqlite3"
    source = args.source.resolve()
    if source.parent.parent != root.parent or not source.parent.name.startswith("s6-resume-"):
        raise SystemExit("Source must be a preserved synthetic S6 sibling root")
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo / "tests"))
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    os.environ["CEI_DEVELOPMENT_DB"] = str(target)
    import django
    from django.core.management import call_command
    from django.db import connection, connections
    from django.db.migrations.executor import MigrationExecutor
    from probe_v10_s6_cei_prewrite import snapshot
    from probe_v10_s6_resume import evidence

    django.setup()
    from modules.data_management.portability import validate_export

    with zipfile.ZipFile(source) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    manifest = json.loads(entries["manifest.json"])
    attempts_rows = json.loads(entries["attempts.json"])
    revisions = json.loads(entries["question_revisions.json"])
    assert len(attempts_rows) == 1 and attempts_rows[0]["is_correct"] is False
    assert attempts_rows[0]["selected_alternative"] != revisions[0]["correct_alternative"]
    attempts_rows[0]["is_correct"] = True
    entries["attempts.json"] = json.dumps(attempts_rows).encode()
    for entry in manifest["files"]:
        if entry["name"] == "attempts.json":
            entry["size_bytes"] = len(entries["attempts.json"])
            entry["sha256"] = hashlib.sha256(entries["attempts.json"]).hexdigest()
    entries["manifest.json"] = json.dumps(manifest).encode()
    package = root / "valid-checksum-inconsistent-attempt.zip"
    with zipfile.ZipFile(package, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    validated = validate_export(io.BytesIO(package.read_bytes()))
    assert validated.rows["attempts"][0]["is_correct"] is True
    assert Path(connection.settings_dict["NAME"]).resolve() == target
    executor = MigrationExecutor(connection)
    executor.migrate(executor.loader.graph.leaf_nodes())
    connections.close_all()
    before = snapshot(target)
    physical_before = hashlib.sha256(target.read_bytes()).hexdigest()
    attempted = {"INSERT": 0, "UPDATE": 0, "DELETE": 0}
    completed = attempted.copy()
    statements = []
    connection.ensure_connection()
    native = connection.connection
    assert native is not None
    previous_changes = native.total_changes

    def count(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
        match = re.match(r"\s*(INSERT|UPDATE|DELETE)\b", sql, re.I)
        if match:
            attempted[match[1].upper()] += 1
            statements.append(sql.split(" VALUES", 1)[0])
        result = execute(sql, params, many, context)
        if match:
            completed[match[1].upper()] += 1
        return result

    exception = None
    started = time.perf_counter()
    with connection.execute_wrapper(count):
        try:
            call_command("import_cei", package=str(package), stdout=io.StringIO())
        except Exception as caught:
            exception = {
                "type": type(caught).__name__,
                "message": str(caught),
                "cause_type": type(caught.__cause__).__name__,
                "cause": str(caught.__cause__),
            }
    changes = native.total_changes - previous_changes
    connections.close_all()
    after = snapshot(target)
    physical_after = hashlib.sha256(target.read_bytes()).hexdigest()
    passed = (
        exception is not None
        and not sum(attempted.values())
        and changes == 0
        and before == after
        and physical_before == physical_after
    )
    result = {
        "case": "A8-INV-ATT-001",
        "status": "REJECTED_BEFORE_WRITE" if passed else "FAILED_REJECT_BEFORE_WRITE",
        "generated_at": datetime.now(UTC).isoformat(),
        "package_validation": "validate_export accepted before import",
        "mutation": "Only Attempt.is_correct false -> true while selected alternative remains different from revision correct alternative; manifest member checksum/size updated; producer/format/migrations/policies/UUIDs/references unchanged",
        "attempted": attempted,
        "completed": completed,
        "total_changes_delta": changes,
        "before": before,
        "after": after,
        "physical_before": physical_before,
        "physical_after": physical_after,
        "exception": exception,
        "statements_without_payload": statements,
        "source": str(source),
        "source_sha256": source_hash,
        "source_unchanged": source_hash == hashlib.sha256(source.read_bytes()).hexdigest(),
        "package": str(package),
        "target": str(target),
        "duration_seconds": time.perf_counter() - started,
        "rollback_is_not_prewrite_rejection": True,
    }
    (root / "result.json").write_bytes((json.dumps(evidence(result), indent=2) + "\n").encode())
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "case",
                    "status",
                    "attempted",
                    "completed",
                    "total_changes_delta",
                    "exception",
                    "source_unchanged",
                )
            }
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
