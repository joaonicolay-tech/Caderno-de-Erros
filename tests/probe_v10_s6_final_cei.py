"""Final S6 affected valid CEI proof; no upgrade/recovery or second import."""

import argparse
import hashlib
import io
import json
import os
import sys
import time
import zipfile
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--source-package", required=True, type=Path)
    parser.add_argument("--expected", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.absolute()
    if not __debug__ or not root.name.startswith("s6-final-") or root.exists():
        raise SystemExit("Requires assertions and a fresh isolated s6-final-* root")
    if not root.parent.is_dir() or any(
        p.is_symlink() or p.is_junction() for p in (root, *root.parents)
    ):
        raise SystemExit("Requires a direct isolated root")
    source = args.source_package.resolve(strict=True)
    expected_path = args.expected.resolve(strict=True)
    if source.parent != expected_path.parent or source.parent.parent != root.parent:
        raise SystemExit(
            "Requires preserved historical package/evidence in a sibling synthetic root"
        )
    if not source.parent.name.startswith("s6-resume-"):
        raise SystemExit("Requires preserved S6 synthetic source")
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    expected_sha = hashlib.sha256(expected_path.read_bytes()).hexdigest()
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert expected["status"] == "PASS"
    root.mkdir()
    target = root / "valid-v05-to-v1.sqlite3"
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "src"))
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    os.environ["CEI_DEVELOPMENT_DB"] = str(target)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    import django
    from django.conf import settings
    from django.db import connection, connections
    from django.db.migrations.executor import MigrationExecutor
    from probe_v10_s6_cei_prewrite import snapshot
    from probe_v10_s6_resume import evidence, save

    django.setup()
    from modules.accounts.services import LOCAL_WORKSPACE_ID
    from modules.analytics.services import AnalyticsService
    from modules.data_management.portability import export_bytes, import_into_empty, validate_export
    from modules.domain.services import current_domain
    from modules.operations.integrity import run_integrity_check
    from modules.priority.services import list_subject_priorities
    from modules.questions.models import Question
    from modules.reviews.selectors import list_review_queue
    from shared.domain.time import FixedClock, Instant

    assert settings.CEI_PROFILE == "development"
    assert Path(connection.settings_dict["NAME"]).resolve() == target
    assert connection.vendor == "sqlite" and not target.exists()
    started = time.perf_counter()
    data = source.read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["application_version"] == "V0.5"
        assert manifest["format"] == "CEI-EXPORT" and manifest["format_version"] == "1.0"
        assert set(archive.namelist()) == {"manifest.json", *(f["name"] for f in manifest["files"])}
        for entry in manifest["files"]:
            member = archive.read(entry["name"])
            assert hashlib.sha256(member).hexdigest() == entry["sha256"]
            assert len(member) == entry["size_bytes"]
            if entry["name"].endswith(".json"):
                assert len(json.loads(member)) == entry["count"]
    validated = validate_export(io.BytesIO(data))
    executor = MigrationExecutor(connection)
    executor.migrate(executor.loader.graph.leaf_nodes())
    connections.close_all()
    before = snapshot(target)
    counts = import_into_empty(package=validated)
    checker = run_integrity_check()
    assert checker.checks_executed == 25 and checker.total_findings == 0
    connections.close_all()
    imported = snapshot(target)
    assert imported["integrity_check"] == [("ok",)] and imported["foreign_key_check"] == []
    physical_before_reads = hashlib.sha256(target.read_bytes()).hexdigest()
    clock = FixedClock(Instant(datetime(2026, 9, 20, 15, tzinfo=UTC)))
    analytics = AnalyticsService(workspace_id=LOCAL_WORKSPACE_ID, clock=clock)
    derived = {
        "activity": asdict(analytics.activity()),
        "errors": asdict(analytics.error_categories()),
        "reviews": asdict(analytics.reviews()),
        "queue": list_review_queue(workspace_id=LOCAL_WORKSPACE_ID, clock=clock),
        "domain": [
            asdict(current_domain(workspace_id=LOCAL_WORKSPACE_ID, question_id=q.id, clock=clock))
            for q in Question.objects.order_by("id")
        ],
        "priority": asdict(list_subject_priorities(workspace_id=LOCAL_WORKSPACE_ID, clock=clock)),
    }
    normalized_derived = json.loads(json.dumps(evidence(derived), default=str))
    assert normalized_derived == expected["source"]["derived"]
    reexport = export_bytes(workspace_id=LOCAL_WORKSPACE_ID)
    (root / "v1-reexport.zip").write_bytes(reexport)
    replayed = validate_export(io.BytesIO(reexport))
    assert validated.rows == replayed.rows
    assert counts == expected["counts"]
    assert (
        manifest["policies"]
        == replayed.manifest["policies"]
        == expected["v05_manifest"]["policies"]
    )
    assert manifest["schema_migrations"] == replayed.manifest["schema_migrations"]
    projection_sha = hashlib.sha256(
        json.dumps(evidence(validated.rows), sort_keys=True, default=str).encode()
    ).hexdigest()
    assert "SHA256:" + projection_sha == expected["functional_projection_sha256"]
    connections.close_all()
    assert snapshot(target) == imported
    assert hashlib.sha256(target.read_bytes()).hexdigest() == physical_before_reads
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_sha
    assert hashlib.sha256(expected_path.read_bytes()).hexdigest() == expected_sha
    result = {
        "task_id": "V1.0-S6",
        "status": "VALID_IMPORT_PASS",
        "execution": "final resumption after S2R3",
        "observed_at": datetime.now(UTC).isoformat(),
        "duration_seconds": time.perf_counter() - started,
        "source": str(source),
        "source_sha256": source_sha,
        "source_unchanged": True,
        "expected_evidence": str(expected_path),
        "expected_sha256": expected_sha,
        "target": str(target),
        "isolation": "fresh synthetic target only; source ZIP/evidence read-only",
        "before": before,
        "imported": imported,
        "physical_after": physical_before_reads,
        "functional_projection_sha256": projection_sha,
        "all_21_record_sets_equal": True,
        "ids": {name: [str(row["id"]) for row in rows] for name, rows in validated.rows.items()},
        "counts": counts,
        "policies": manifest["policies"],
        "format": manifest["format"],
        "format_version": manifest["format_version"],
        "producer": manifest["application_version"],
        "checker": {"checks": checker.checks_executed, "findings": checker.total_findings},
        "derived": normalized_derived,
        "derived_equal_preserved_source": True,
        "historical_relationships_equal": True,
        "read_checks_did_not_mutate_target": True,
        "technical_exclusions": expected["technical_exclusion"],
        "second_V1_import_not_repeated": "Unaffected prior second round-trip remains preserved; single affected V0.5 import/reexport performed",
    }
    save(root / "result.json", result)
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "status",
                    "counts",
                    "all_21_record_sets_equal",
                    "checker",
                    "derived_equal_preserved_source",
                    "source_unchanged",
                    "duration_seconds",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
