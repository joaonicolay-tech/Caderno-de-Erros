"""Opt-in S6 proof: incompatible CEI target must reject before any row write."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

V044 = [
    ("auth", "0012_alter_user_first_name_max_length"),
    ("attempts", "0002_review_receipt_constraints"),
    ("errors", "0002_learning_classification"),
    ("questions", "0002_question_catalog"),
    ("reviews", "0002_activation_review_cycle"),
    ("taxonomy", "0001_initial"),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(path: Path) -> dict[str, Any]:
    """Read every table in a read-only connection; emit hashes, never payloads."""
    with closing(sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)) as database:
        database.execute("BEGIN")
        schema = database.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master ORDER BY type, name"
        ).fetchall()
        tables: dict[str, Any] = {}
        for (name,) in database.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall():
            quoted = '"' + name.replace('"', '""') + '"'
            cursor = database.execute(f"SELECT * FROM {quoted}")  # noqa: S608
            rows = sorted(cursor.fetchall(), key=lambda row: json.dumps(row, default=str))
            tables[name] = {
                "columns": [column[0] for column in cursor.description],
                "rows": rows,
            }
        migrations = database.execute(
            "SELECT app || '.' || name FROM django_migrations ORDER BY app, name"
        ).fetchall()
        physical = database.execute("PRAGMA integrity_check").fetchall()
        foreign_keys = database.execute("PRAGMA foreign_key_check").fetchall()
        database.rollback()
    semantic = json.dumps(tables, sort_keys=True, default=str).encode("utf-8")
    return {
        "semantic_sha256": digest(semantic),
        "schema_sha256": digest(json.dumps(schema).encode("utf-8")),
        "counts": {name: len(item["rows"]) for name, item in tables.items()},
        "migrations": [name for (name,) in migrations],
        "integrity_check": physical,
        "foreign_key_check": foreign_keys,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.absolute()
    if (
        not root.name.startswith("s6-cei-prewrite-")
        or root.exists()
        or not root.parent.is_dir()
        or any(parent.is_symlink() or parent.is_junction() for parent in root.parents)
    ):
        raise SystemExit("S6 requires a new isolated s6-cei-prewrite-* directory.")
    root.mkdir()
    root = root.resolve()
    source = root / "source-v1.sqlite3"
    target = root / "target-v044-empty-N9.sqlite3"
    package_path = root / "valid-v1-export.zip"
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "src"))
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    os.environ["CEI_DEVELOPMENT_DB"] = str(source)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

    import django
    from django.conf import settings
    from django.core.management import call_command
    from django.core.management.base import CommandError
    from django.db import DatabaseError, connection
    from django.db.migrations.executor import MigrationExecutor

    django.setup()

    from modules.accounts.services import LOCAL_WORKSPACE_ID
    from modules.data_management.portability import export_workspace, validate_export
    from modules.operations.integrity import INVARIANT_CATALOG, run_integrity_check
    from modules.questions.services import create_active
    from modules.taxonomy.services import create_discipline, create_subject
    from shared.application.bootstrap import bootstrap_local_workspace
    from shared.application.version import PRODUCT_VERSION

    def guard(expected: Path) -> None:
        observed = Path(connection.settings_dict["NAME"]).resolve()
        assert expected in {source, target}
        assert observed == expected and expected.parent == root
        assert not expected.is_symlink() and not expected.is_junction()
        assert settings.CEI_PROFILE == "development"
        assert connection.vendor == "sqlite" and PRODUCT_VERSION == "V1.0"

    started = time.perf_counter()
    guard(source)
    assert not source.exists()
    assert len(INVARIANT_CATALOG) == 25
    executor = MigrationExecutor(connection)
    executor.migrate(executor.loader.graph.leaf_nodes())
    bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="S6 synthetic")
    subject = create_subject(
        workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="CEI pre-write"
    )
    create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="S6 synthetic CEI pre-write fixture",
        alternatives=["Incorrect", "Correct"],
        correct_alternative_position=2,
    )
    checker = run_integrity_check()
    assert checker.checks_executed == 25 and checker.total_findings == 0
    source_snapshot = snapshot(source)
    with package_path.open("wb") as destination:
        manifest = export_workspace(workspace_id=LOCAL_WORKSPACE_ID, destination=destination)
    with package_path.open("rb") as stream:
        validate_export(stream)
    connection.close()
    source_hash = digest(source.read_bytes())
    assert source_snapshot == snapshot(source)

    connection.settings_dict["NAME"] = str(target)
    settings.DATABASES["default"]["NAME"] = str(target)
    guard(target)
    assert not target.exists()
    executor = MigrationExecutor(connection)
    executor.migrate(V044)
    before = snapshot(target)
    assert before["counts"]["accounts_workspace"] == 0
    assert before["migrations"] != manifest["schema_migrations"]
    assert before["integrity_check"] == [("ok",)] and before["foreign_key_check"] == []
    connection.close()
    physical_before = digest(target.read_bytes())
    connection.ensure_connection()
    native = connection.connection
    assert native is not None
    changes_before = native.total_changes
    successful_dml: list[dict[str, str]] = []
    failure: dict[str, str] | None = None

    def observe(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
        result = execute(sql, params, many, context)
        match = re.match(r'\s*(INSERT INTO|UPDATE|DELETE FROM)\s+("[^"]+"|\w+)', sql, re.IGNORECASE)
        if match:
            successful_dml.append({"operation": match[1].upper(), "table": match[2].strip('"')})
        return result

    attempted = time.perf_counter()
    guard(target)
    try:
        with connection.execute_wrapper(observe):
            call_command("import_cei", package=str(package_path), stdout=io.StringIO())
    except (CommandError, DatabaseError) as error:
        failure = {"type": type(error).__name__, "message": str(error)}
        if error.__cause__ is not None:
            failure["cause_type"] = type(error.__cause__).__name__
            failure["cause_message"] = str(error.__cause__)
    changes = native.total_changes - changes_before
    after = snapshot(target)
    connection.close()
    physical_after = digest(target.read_bytes())
    source_unchanged = source_hash == digest(source.read_bytes()) and source_snapshot == snapshot(
        source
    )
    package_sha256 = digest(package_path.read_bytes())
    rejected_before_write = (
        failure is not None and not successful_dml and changes == 0 and before == after
    )
    status = "REJECTED_BEFORE_WRITE" if rejected_before_write else "FAILED_REJECT_BEFORE_WRITE"
    report = {
        "task_id": "V1.0-S6",
        "execution_model": "GPT-6.1 Sol High",
        "model_decision": "human-authorized execution-model override for V1.0-S6",
        "baseline": "5eb6930aba35a0d1083c92816a83c7c4c2451830",
        "generated_at": datetime.now(UTC).isoformat(),
        "case": "N9 destination with physically incompatible V0.4.4 migrations/schema",
        "status": status,
        "expected": "REJECTED_BEFORE_WRITE",
        "isolation": {
            "fresh_root": True,
            "effective_profile": settings.CEI_PROFILE,
            "effective_target": target.name,
            "source": source.name,
            "original_or_active_database_touched": False,
            "artifacts_preserved": True,
        },
        "source": {
            "snapshot": source_snapshot,
            "checker": {
                "checks": checker.checks_executed,
                "findings": checker.total_findings,
            },
            "sha256": source_hash,
            "unchanged": source_unchanged,
        },
        "package": {
            "sha256": package_sha256,
            "independent_validation_before_import": "validate_export passed",
            "application_version": manifest["application_version"],
            "format": manifest["format"],
            "format_version": manifest["format_version"],
            "policies": manifest["policies"],
            "schema_migrations": manifest["schema_migrations"],
            "counts": {entry["name"]: entry["count"] for entry in manifest["files"]},
        },
        "destination_before": before,
        "destination_after": after,
        "physical_sha256_before": physical_before,
        "physical_sha256_after": physical_after,
        "successful_dml": successful_dml,
        "successful_dml_counts": dict(Counter(item["table"] for item in successful_dml)),
        "sqlite_total_changes_delta": changes,
        "exception": failure,
        "logical_rollback_verified": before == after,
        "import_duration_seconds": time.perf_counter() - attempted,
        "duration_seconds": time.perf_counter() - started,
        "target_classification": "NON-CANDIDATE"
        if not rejected_before_write
        else "NEGATIVE_TEST_TARGET",
        "stop_rule": "Stop functional S6 immediately on write before complete compatibility validation.",
    }
    (root / "result.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": status,
                "successful_dml": len(successful_dml),
                "row_changes": changes,
                "logical_rollback_verified": before == after,
                "source_unchanged": source_unchanged,
                "exception": failure,
            },
            ensure_ascii=False,
        )
    )
    return 0 if rejected_before_write else 1


if __name__ == "__main__":
    raise SystemExit(main())
