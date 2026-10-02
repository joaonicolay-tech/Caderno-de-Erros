"""S2R3: exact preserved CEI package versus a fresh isolated destination."""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.absolute()
    if not __debug__ or not root.name.startswith("s2r3-") or root.exists():
        raise SystemExit("Requires assertions and a fresh isolated s2r3-* root")
    if not root.parent.is_dir() or any(
        p.is_symlink() or p.is_junction() for p in (root, *root.parents)
    ):
        raise SystemExit("Requires a direct isolated root")
    package = args.package.resolve(strict=True)
    repo = args.repo.resolve(strict=True)
    root.mkdir()
    target = root / "target.sqlite3"
    package_hash = hashlib.sha256(package.read_bytes()).hexdigest()
    sys.path.insert(0, str(repo / "src"))
    sys.path.insert(0, str(repo / "tests"))
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    os.environ["CEI_DEVELOPMENT_DB"] = str(target)
    import django
    from django.db import connection, connections
    from django.db.migrations.executor import MigrationExecutor
    from probe_v10_s6_cei_prewrite import snapshot
    from probe_v10_s6_resume import evidence

    django.setup()
    from modules.data_management.portability import import_into_empty, validate_export
    from modules.operations.integrity import run_integrity_check

    assert Path(connection.settings_dict["NAME"]).resolve() == target
    executor = MigrationExecutor(connection)
    executor.migrate(executor.loader.graph.leaf_nodes())
    connections.close_all()
    before = snapshot(target)
    physical_before = hashlib.sha256(target.read_bytes()).hexdigest()
    connection.ensure_connection()
    native = connection.connection
    assert native is not None
    initial_changes = native.total_changes
    attempted = dict.fromkeys(("INSERT", "UPDATE", "DELETE"), 0)
    completed = attempted.copy()

    def count(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
        match = re.match(r"\s*(INSERT|UPDATE|DELETE)\b", sql, re.I)
        if match:
            attempted[match[1].upper()] += 1
        result = execute(sql, params, many, context)
        if match:
            completed[match[1].upper()] += 1
        return result

    validation = "REJECTED"
    exception = None
    started = time.perf_counter()
    with connection.execute_wrapper(count):
        try:
            validated = validate_export(io.BytesIO(package.read_bytes()))
            validation = "ACCEPTED"
            import_into_empty(package=validated)
        except Exception as caught:
            exception = {"type": type(caught).__name__, "message": str(caught)}
    delta = native.total_changes - initial_changes
    # Independent file checker AFTER the import transaction completes.
    checker = run_integrity_check()
    connections.close_all()
    after = snapshot(target)
    physical_after = hashlib.sha256(target.read_bytes()).hexdigest()
    passed = (
        exception is not None
        and not sum(attempted.values())
        and delta == 0
        and before == after
        and physical_before == physical_after
    )
    result = {
        "case": "S6-F02-exact-preserved-package",
        "status": "REJECTED_BEFORE_WRITE" if passed else "RED_HISTORICAL_EVIDENCE",
        "observed_at": datetime.now(UTC).isoformat(),
        "validation": validation,
        "attempted": attempted,
        "completed": completed,
        "total_changes_delta": delta,
        "before": before,
        "after": after,
        "physical_before": physical_before,
        "physical_after": physical_after,
        "exception": exception,
        "post_transaction_checker": {
            "checks": checker.checks_executed,
            "findings": [
                {
                    "code": f.invariant_id,
                    "severity": f.severity,
                    "entity": f.entity_type,
                }
                for f in checker.findings
            ],
        },
        "package": str(package),
        "package_sha256": package_hash,
        "package_unchanged": package_hash == hashlib.sha256(package.read_bytes()).hexdigest(),
        "target": str(target),
        "duration_seconds": time.perf_counter() - started,
        "rollback_is_not_prewrite": True,
    }
    (root / "result.json").write_bytes((json.dumps(evidence(result), indent=2) + "\n").encode())
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "status",
                    "validation",
                    "attempted",
                    "completed",
                    "total_changes_delta",
                    "exception",
                    "post_transaction_checker",
                    "package_unchanged",
                )
            }
        )
    )
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
