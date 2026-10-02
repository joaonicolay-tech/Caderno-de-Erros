"""Opt-in S6 resumption evidence; each phase uses explicitly isolated SQLite paths."""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import sys
import time
import uuid
import zipfile
from contextlib import closing
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def evidence(value: Any) -> Any:
    """Use explicit algorithm-qualified digests in new evidence (not CEI manifests)."""
    if is_dataclass(value) and not isinstance(value, type):
        return evidence(asdict(value))
    if isinstance(value, dict):
        return {str(k): evidence(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [evidence(v) for v in value]
    if isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value):
        return "SHA256:" + value
    return value


def save(path: Path, value: Any) -> None:
    path.write_bytes((json.dumps(evidence(value), indent=2, default=str) + "\n").encode())


def raw_tables(path: Path) -> dict[str, Any]:
    with closing(sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)) as db:
        result = {}
        for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            quoted = '"' + name.replace('"', '""') + '"'
            cursor = db.execute(f"SELECT * FROM {quoted}")  # noqa: S608
            columns = [item[0] for item in cursor.description]
            result[name] = sorted(
                [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()],
                key=lambda row: json.dumps(row, sort_keys=True, default=str),
            )
        return result


def main() -> int:
    if not __debug__:
        raise SystemExit("This opt-in evidence probe requires assertions enabled; do not use -O.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--phase", required=True)
    parser.add_argument("--fixture-db", type=Path)
    args = parser.parse_args()
    root = args.root.absolute()
    assert root.name.startswith("s6-resume-") and root.parent.is_dir()
    assert not any(p.is_symlink() or p.is_junction() for p in (root, *root.parents))
    if args.phase in ("negatives", "recovery"):
        assert not root.exists()
        root.mkdir()
    assert root.is_dir()
    root = root.resolve()
    repo = args.repo.resolve()
    runtime = args.runtime.resolve()
    sys.path.insert(0, str(repo / "tests"))
    sys.path.insert(0, str(runtime / "src"))
    database = root / (
        "negative-source.sqlite3" if args.phase.startswith("negatives") else "chain.sqlite3"
    )
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    os.environ["CEI_DEVELOPMENT_DB"] = str(database)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

    import django
    from django.conf import settings
    from django.core.management import call_command
    from django.db import connection, connections
    from django.db.migrations.executor import MigrationExecutor
    from probe_v10_s6_cei_prewrite import snapshot

    django.setup()

    from modules.accounts.services import LOCAL_WORKSPACE_ID
    from modules.operations.integrity import INVARIANT_CATALOG, run_integrity_check

    def select(path: Path) -> None:
        assert path.parent == root and not path.is_symlink() and not path.is_junction()
        connections.close_all()
        connection.settings_dict["NAME"] = str(path)
        settings.DATABASES["default"]["NAME"] = str(path)
        assert Path(connection.settings_dict["NAME"]).resolve() == path
        assert settings.CEI_PROFILE == "development" and connection.vendor == "sqlite"

    def migrate() -> list[str]:
        executor = MigrationExecutor(connection)
        plan = [
            f"{m.app_label}.{m.name}"
            for m, backwards in executor.migration_plan(executor.loader.graph.leaf_nodes())
            if not backwards
        ]
        executor.migrate(executor.loader.graph.leaf_nodes())
        return plan

    def observe_db(path: Path, *, derived: bool = True) -> dict[str, Any]:
        select(path)
        before = snapshot(path)
        check = run_integrity_check()
        result: dict[str, Any] = {
            "snapshot": before,
            "tables": raw_tables(path),
            "checker": asdict(check),
            "catalog": [asdict(item) for item in INVARIANT_CATALOG],
        }
        assert check.checks_executed == len(INVARIANT_CATALOG) and check.total_findings == 0
        assert before["integrity_check"] == [("ok",)] and before["foreign_key_check"] == []
        if derived:
            from modules.analytics.services import AnalyticsService
            from modules.questions.models import Question
            from modules.reviews.selectors import list_review_queue
            from shared.domain.time import FixedClock, Instant

            clock = FixedClock(Instant(datetime(2026, 9, 20, 15, tzinfo=UTC)))
            analytics = AnalyticsService(workspace_id=LOCAL_WORKSPACE_ID, clock=clock)
            result["derived"] = {
                "activity": asdict(analytics.activity()),
                "errors": asdict(analytics.error_categories()),
                "reviews": asdict(analytics.reviews()),
                "queue": list_review_queue(workspace_id=LOCAL_WORKSPACE_ID, clock=clock),
            }
            if (runtime / "src/modules/domain").exists():
                from modules.domain.services import current_domain
                from modules.priority.services import list_subject_priorities

                result["derived"]["domain"] = [
                    asdict(
                        current_domain(
                            workspace_id=LOCAL_WORKSPACE_ID, question_id=q.id, clock=clock
                        )
                    )
                    for q in Question.objects.order_by("id")
                ]
                result["derived"]["priority"] = asdict(
                    list_subject_priorities(workspace_id=LOCAL_WORKSPACE_ID, clock=clock)
                )
            else:
                result["derived"]["domain"] = "N/A: unavailable in V0.4.4"
                result["derived"]["priority"] = "N/A: unavailable in V0.4.4"
        connections.close_all()
        assert snapshot(path) == before
        result["physical_sha256"] = sha(path.read_bytes())
        result["runtime"] = str(runtime)
        result["versions"] = {
            "python": sys.version,
            "django": django.get_version(),
            "sqlite": sqlite3.sqlite_version,
        }
        return result

    def seed_current(path: Path, label: str) -> None:
        from modules.questions.services import create_active
        from modules.taxonomy.services import create_discipline, create_subject
        from shared.application.bootstrap import bootstrap_local_workspace

        assert not path.exists()
        select(path)
        migrate()
        bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
        discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name=label)
        subject = create_subject(
            workspace_id=LOCAL_WORKSPACE_ID,
            discipline_id=discipline.id,
            name="Independent S6 proof",
        )
        create_active(
            workspace_id=LOCAL_WORKSPACE_ID,
            discipline_id=discipline.id,
            subject_id=subject.id,
            stem=label,
            alternatives=["A", "B"],
            correct_alternative_position=2,
        )

    def smoke(path: Path) -> dict[str, int]:
        from django.test import Client

        select(path)
        client = Client(HTTP_HOST="localhost")
        result = {url: client.get(url).status_code for url in ("/", "/questions/", "/reviews/")}
        assert all(status == 200 for status in result.values())
        connections.close_all()
        return result

    started = time.perf_counter()
    if args.phase.startswith("negatives"):
        from modules.data_management.portability import export_bytes, validate_export
        from modules.questions.services import create_active
        from modules.taxonomy.services import create_discipline, create_subject
        from shared.application.bootstrap import bootstrap_local_workspace

        select(database)
        if args.phase == "negatives":
            migrate()
            bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
            discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="S6 negatives")
            subject = create_subject(
                workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="Pre-write"
            )
            create_active(
                workspace_id=LOCAL_WORKSPACE_ID,
                discipline_id=discipline.id,
                subject_id=subject.id,
                stem="Synthetic S6",
                alternatives=["A", "B"],
                correct_alternative_position=1,
            )
            package = export_bytes(workspace_id=LOCAL_WORKSPACE_ID)
            (root / "negative-valid-v1.zip").write_bytes(package)
        else:
            package = (root / "negative-valid-v1.zip").read_bytes()
        validate_export(io.BytesIO(package))
        source = observe_db(database, derived=False)
        cases = []
        for number in range(1, 9) if args.phase == "negatives" else (5, 8):
            with zipfile.ZipFile(io.BytesIO(package)) as archive:
                entries = {name: archive.read(name) for name in archive.namelist()}
            manifest = json.loads(entries["manifest.json"])
            if number == 1:
                manifest["application_version"] = "UNSUPPORTED"
            elif number == 2:
                manifest["schema_migrations"].pop()
            elif number == 3:
                manifest["policies"]["review"] = "UNSUPPORTED"
            elif number in (4, 8):
                rows = json.loads(entries["questions.json"])
                if number == 4:
                    del rows[0]["question_type"]
                else:
                    if args.phase == "negatives":
                        rows[0]["id"] = "invalid-uuid"
                    else:
                        rows[0]["subject"] = str(uuid.uuid4())
                entries["questions.json"] = json.dumps(rows).encode()
                for item in manifest["files"]:
                    if item["name"] == "questions.json":
                        item["size_bytes"] = len(entries["questions.json"])
                        item["sha256"] = sha(entries["questions.json"])
            elif number == 5:
                original = entries["questions.json"]
                entries["questions.json"] = original.replace(b"ACTIVE", b"DRAFT ", 1)
                # Equal byte length isolates checksum validation from size validation.
                assert len(entries["questions.json"]) == len(original)
                assert entries["questions.json"] != original
            elif number == 6:
                del entries["questions.json"]
            else:
                entries["forbidden.json"] = b"[]"
            entries["manifest.json"] = json.dumps(manifest).encode()
            label = f"N{number}" + ("-extra" if args.phase != "negatives" else "")
            path = root / f"{label}.zip"
            with zipfile.ZipFile(path, "w") as archive:
                for name, content in entries.items():
                    archive.writestr(name, content)
            target = root / f"{label}-target.sqlite3"
            select(target)
            migrate()
            connections.close_all()
            before = snapshot(target)
            physical_before = sha(target.read_bytes())
            attempts = {"INSERT": 0, "UPDATE": 0, "DELETE": 0}
            successful = attempts.copy()
            connection.ensure_connection()
            native = connection.connection
            assert native is not None
            changes_before = native.total_changes

            def count(
                execute: Any,
                sql: str,
                params: Any,
                many: bool,
                context: Any,
                attempted_counts: dict[str, int] = attempts,
                successful_counts: dict[str, int] = successful,
            ) -> Any:
                match = re.match(r"\s*(INSERT|UPDATE|DELETE)\b", sql, re.I)
                if match:
                    attempted_counts[match[1].upper()] += 1
                output = execute(sql, params, many, context)
                if match:
                    successful_counts[match[1].upper()] += 1
                return output

            error = None
            with connection.execute_wrapper(count):
                try:
                    call_command("import_cei", package=str(path), stdout=io.StringIO())
                except Exception as caught:
                    error = {"type": type(caught).__name__, "message": str(caught)}
                    if caught.__cause__ is not None:
                        error["cause"] = str(caught.__cause__)
            changes = native.total_changes - changes_before
            connections.close_all()
            after = snapshot(target)
            physical_after = sha(target.read_bytes())
            passed = error is not None and sum(attempts.values()) == 0 and changes == 0
            passed = passed and before == after and physical_before == physical_after
            case = {
                "case": label,
                "status": "REJECTED_BEFORE_WRITE" if passed else "FAIL",
                "attempts": attempts.copy(),
                "successful": successful.copy(),
                "total_changes_delta": changes,
                "before": before,
                "after": after,
                "physical_before": physical_before,
                "physical_after": physical_after,
                "error": error,
                "target": str(target),
                "package": str(path),
            }
            cases.append(case)
            save(
                root / f"{args.phase}.json",
                {
                    "cases": cases,
                    "source": source,
                    "duration_seconds": time.perf_counter() - started,
                },
            )
            print(json.dumps({"case": case["case"], "status": case["status"], "error": error}))
            if not passed:
                return 2
        assert observe_db(database, derived=False) == source
    elif args.phase == "seed":
        assert not database.exists()
        module = ast.parse((repo / "tests/test_v05_s2a_upgrade.py").read_text(encoding="utf-8"))
        fixture = next(
            node.value.value
            for node in ast.walk(module)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "probe" for target in node.targets
            )
            and isinstance(node.value, ast.Constant)
        )
        assert isinstance(fixture, str)
        prefix = fixture.split("pre_result =", 1)[0]
        namespace: dict[str, Any] = {}
        exec(compile(prefix, "approved-V044-fixture", "exec"), namespace)  # noqa: S102 -- trusted approved repository fixture
        apps = namespace["apps"]
        source = apps.get_model("questions", "Source").objects.create(
            workspace=namespace["workspace"],
            name="Synthetic book",
            name_key="synthetic book",
            source_type="BOOK",
        )
        apps.get_model("questions", "QuestionOrigin").objects.create(
            workspace=namespace["workspace"],
            question=namespace["question"],
            source=source,
            reference_text="Synthetic historical origin",
        )
        connections.close_all()
        save(
            root / "seed.json",
            {
                "fixture": "test_v05_s2a_upgrade.py prefix, historical registries",
                "snapshot": snapshot(database),
                "physical_sha256": sha(database.read_bytes()),
            },
        )
    elif args.phase in ("v044", "v05", "v1"):
        from modules.data_management.services import (
            create_sqlite_backup,
            restore_sqlite_backup,
            validate_sqlite_backup,
        )

        select(database)
        applied = migrate() if args.phase != "v044" else []
        result = observe_db(database)
        result["migration_plan"] = applied
        if args.phase == "v044":
            backup = root / "v044-pre-upgrade.sqlite3"
            create_sqlite_backup(backup)
            validate_sqlite_backup(backup)
            restored = root / "v044-pre-restored.sqlite3"
            restore_sqlite_backup(backup, restored)
            assert snapshot(restored) == snapshot(database)
            result["prebackup"] = str(backup)
            result["pre_restore"] = observe_db(restored)
        if args.phase == "v05":
            from modules.data_management.portability import export_bytes, validate_export

            select(database)
            package = export_bytes(workspace_id=LOCAL_WORKSPACE_ID)
            validated = validate_export(io.BytesIO(package))
            assert validated.manifest["application_version"] == "V0.5"
            (root / "real-v05-export.zip").write_bytes(package)
            result["manifest"] = validated.manifest
            connections.close_all()
            shutil.copyfile(database, root / "v05-checkpoint.sqlite3")
        save(root / f"{args.phase}.json", result)
    elif args.phase == "positive":
        from modules.data_management.portability import (
            export_bytes,
            import_into_empty,
            validate_export,
        )

        package_path = root / "real-v05-export.zip"
        data = package_path.read_bytes()
        # Independent stdlib reader verifies membership, sizes, digests and counts.
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            assert manifest["format"] == "CEI-EXPORT" and manifest["format_version"] == "1.0"
            assert manifest["application_version"] == "V0.5"
            assert set(archive.namelist()) == {
                "manifest.json",
                *(f["name"] for f in manifest["files"]),
            }
            for entry in manifest["files"]:
                content = archive.read(entry["name"])
                assert len(content) == entry["size_bytes"] and sha(content) == entry["sha256"]
                if entry["name"].endswith(".json"):
                    assert len(json.loads(content)) == entry["count"]
        validated = validate_export(io.BytesIO(data))
        source = observe_db(database)
        imported = root / "cei-v05-to-v1.sqlite3"
        select(imported)
        migrate()
        counts = import_into_empty(package=validated)
        after = observe_db(imported)
        select(imported)
        replay = export_bytes(workspace_id=LOCAL_WORKSPACE_ID)
        (root / "v1-reexport.zip").write_bytes(replay)
        replayed = validate_export(io.BytesIO(replay))
        assert validated.rows == replayed.rows
        assert manifest["policies"] == replayed.manifest["policies"]
        assert manifest["schema_migrations"] == replayed.manifest["schema_migrations"]
        assert evidence(source["derived"]) == evidence(after["derived"])
        # Repeat an actual V1-produced package into another fresh compatible destination.
        roundtrip = root / "cei-v1-to-v1.sqlite3"
        select(roundtrip)
        migrate()
        second_counts = import_into_empty(package=replayed)
        second = observe_db(roundtrip)
        select(roundtrip)
        second_export = export_bytes(workspace_id=LOCAL_WORKSPACE_ID)
        (root / "v1-second-export.zip").write_bytes(second_export)
        second_package = validate_export(io.BytesIO(second_export))
        assert replayed.rows == second_package.rows
        assert counts == second_counts
        assert evidence(after["derived"]) == evidence(second["derived"])
        assert observe_db(database) == source
        save(
            root / "positive.json",
            {
                "status": "PASS",
                "source": source,
                "v05_manifest": manifest,
                "v1_manifest": replayed.manifest,
                "imported": after,
                "roundtrip": second,
                "counts": counts,
                "all_21_record_sets_equal": True,
                "functional_projection_sha256": sha(
                    json.dumps(evidence(validated.rows), sort_keys=True, default=str).encode()
                ),
                "technical_exclusion": "OperationReceipt (1 at source / 0 in CEI destinations) and regenerated local user credential are excluded by CEI-EXPORT-1.0; no historical study fact is excluded.",
                "smoke": smoke(imported),
                "seconds": time.perf_counter() - started,
            },
        )
    elif args.phase == "clean":
        clean = root / "clean-v1.sqlite3"
        seed_current(clean, "Clean V1 install")
        result = observe_db(clean)
        result["status"] = "CLEAN_INSTALL_PASS"
        result["smoke"] = smoke(clean)
        assert len(result["snapshot"]["migrations"]) == 34
        assert result["snapshot"]["counts"]["errors_error_category"] == 10
        assert all(
            row["category_kind"] == "STANDARD"
            and row["state"] == "ACTIVE"
            and row["lock_version"] == 1
            for row in result["tables"]["errors_error_category"]
        )
        save(root / "clean.json", result)
    elif args.phase == "recovery":
        from unittest.mock import patch

        from modules.accounts.models import Workspace
        from modules.data_management import ui_services
        from modules.data_management.exceptions import BackupValidationError, RestoreError
        from modules.data_management.services import (
            create_sqlite_backup,
            manifest_path_for,
            restore_sqlite_backup,
            validate_sqlite_backup,
        )

        source_path = root / "backup-independent-source.sqlite3"
        assert args.fixture_db is not None
        fixture_db = args.fixture_db.resolve()
        assert fixture_db.parent.parent == root.parent
        assert (
            fixture_db.parent.name.startswith("s6-resume-") and fixture_db.name == "chain.sqlite3"
        )
        fixture_before = snapshot(fixture_db)
        fixture_hash = sha(fixture_db.read_bytes())
        shutil.copyfile(fixture_db, source_path)
        source = observe_db(source_path)
        select(source_path)
        backup = root / "independent-valid-backup.sqlite3"
        backup_at = datetime.now(UTC)
        created = create_sqlite_backup(backup)
        validation = validate_sqlite_backup(backup)
        valid_hash = sha(backup.read_bytes())
        sidecar_hash = sha(manifest_path_for(backup).read_bytes())
        # Corrupt only a new backup copy; preserve valid pair and source.
        corrupt = root / "corrupt-backup.sqlite3"
        corrupt_bytes = bytearray(backup.read_bytes())
        corrupt_bytes[128] ^= 1
        corrupt.write_bytes(corrupt_bytes)
        shutil.copyfile(manifest_path_for(backup), manifest_path_for(corrupt))
        corrupt_error = None
        try:
            validate_sqlite_backup(corrupt)
        except BackupValidationError as caught:
            corrupt_error = str(caught)
        assert corrupt_error is not None
        refused = root / "corrupt-must-not-create.sqlite3"
        try:
            restore_sqlite_backup(corrupt, refused)
        except (BackupValidationError, RestoreError):
            pass
        else:
            raise AssertionError("Corrupt restore unexpectedly succeeded")
        assert not refused.exists()
        restored_path = root / "independent-restored.sqlite3"
        restored_result = restore_sqlite_backup(backup, restored_path)
        restored = observe_db(restored_path)
        for key in ("snapshot", "tables", "derived"):
            assert evidence(source[key]) == evidence(restored[key])
        occupied_hash = sha(restored_path.read_bytes())
        try:
            restore_sqlite_backup(backup, restored_path)
        except RestoreError:
            pass
        else:
            raise AssertionError("Occupied restore unexpectedly succeeded")
        assert sha(restored_path.read_bytes()) == occupied_hash
        active = root / "synthetic-offline-active.sqlite3"
        restore_sqlite_backup(backup, active)
        select(active)
        Workspace.objects.filter(pk=LOCAL_WORKSPACE_ID).update(
            name="Post-backup synthetic incident"
        )
        connections.close_all()
        failure_at = datetime.now(UTC)
        altered = observe_db(active)
        save(
            root / "recovery-before-adoption.json",
            {
                "source": source,
                "altered_active": altered,
                "backup_at": backup_at,
                "failure_at": failure_at,
                "backup": created,
                "validation": validation,
                "restore": restored,
                "corrupt_error": corrupt_error,
            },
        )
        assert altered["snapshot"]["semantic_sha256"] != source["snapshot"]["semantic_sha256"]

        def prepare() -> str:
            select(active)
            with (
                backup.open("rb") as data_stream,
                manifest_path_for(backup).open("rb") as manifest_stream,
            ):
                preview = ui_services.preview_restore(data_stream, manifest_stream)
            with (
                backup.open("rb") as data_stream,
                manifest_path_for(backup).open("rb") as manifest_stream,
            ):
                ticket = ui_services.prepare_restore(data_stream, manifest_stream, expected=preview)
            connections.close_all()
            assert not any(
                Path(str(active) + suffix).exists() for suffix in ("-wal", "-shm", "-journal")
            )
            return ticket

        ticket_return = prepare()
        rollback_error = None
        # Exercise the real automatic return branch using an injected post-adoption failure.
        with patch.object(
            ui_services,
            "_check_restored_integrity",
            side_effect=RuntimeError("S6 synthetic post-adoption fault"),
        ):
            try:
                ui_services.apply_prepared_restore(ticket_return)
            except ui_services.UIRecoveryError as caught:
                rollback_error = str(caught)
        assert rollback_error is not None and "estado anterior restaurado" in rollback_error
        returned = observe_db(active)
        for key in ("snapshot", "tables", "derived"):
            assert evidence(altered[key]) == evidence(returned[key])
        prebackup = root / "cei-recovery" / f"pre-{ticket_return}.sqlite3"
        assert returned["physical_sha256"] == sha(prebackup.read_bytes())
        header_differences = [
            (i, x, y)
            for i, (x, y) in enumerate(
                zip(source_path.read_bytes(), backup.read_bytes(), strict=True)
            )
            if x != y
        ]
        assert all(
            i in {*range(24, 28), *range(40, 44), *range(92, 96)} for i, x, y in header_differences
        )
        ticket_success = prepare()
        adoption = ui_services.apply_prepared_restore(ticket_success)
        assert adoption["status"] == "RESTORED"
        final = observe_db(active)
        for key in ("snapshot", "tables", "derived"):
            assert evidence(source[key]) == evidence(final[key])
        smoke_result = smoke(active)
        returned_at = datetime.now(UTC)
        rpo = (failure_at - backup_at).total_seconds()
        rto = (returned_at - failure_at).total_seconds()
        assert 0 <= rpo <= 24 * 3600 and 0 <= rto <= 4 * 3600
        assert sha(backup.read_bytes()) == valid_hash
        assert sha(manifest_path_for(backup).read_bytes()) == sidecar_hash
        assert observe_db(source_path) == source
        assert (
            snapshot(fixture_db) == fixture_before and sha(fixture_db.read_bytes()) == fixture_hash
        )
        save(
            root / "recovery.json",
            {
                "status": "RECOVERY_PASS",
                "source": source,
                "backup": {
                    "created": created,
                    "validation": validation,
                    "path": str(backup),
                    "sha256": valid_hash,
                    "sidecar_sha256": sidecar_hash,
                },
                "corrupt_rejected": corrupt_error,
                "corrupt_restore_destination_absent": True,
                "occupied_restore_unchanged": True,
                "restore": restored,
                "restore_reconciliation": restored_result,
                "altered_active": altered,
                "automatic_return": returned,
                "return_error": rollback_error,
                "fault": "Harness-injected post-adoption failure, no product finding",
                "sqlite_snapshot_header_differences": header_differences,
                "physical_equivalence": "Adopted/returned file matches chosen validated backup exactly; source SQLite technical header counters can differ from backup without semantic loss.",
                "recovered": final,
                "adoption": adoption,
                "smoke": smoke_result,
                "tickets_preserved": [ticket_return, ticket_success],
                "backup_at": backup_at,
                "failure_at": failure_at,
                "returned_at": returned_at,
                "rpo_seconds": rpo,
                "rto_seconds": rto,
                "loss": "Only the explicit post-backup synthetic Workspace name mutation; all chosen recovery-point facts restored.",
                "thresholds": {
                    "rpo_hours": 24,
                    "rto_hours": 4,
                    "scope": "Only this isolated exercise, no production SLA inference",
                },
                "seconds": time.perf_counter() - started,
            },
        )
    else:
        raise ValueError(args.phase)
    print(
        json.dumps(
            {"phase": args.phase, "status": "PASS", "seconds": time.perf_counter() - started}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
