"""Ensaio S6 sintético descartável; nunca usa o banco configurado pelo operador."""

import argparse
import hashlib
import json
import os
import platform
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="cei-s6-drill-") as directory:
        root = Path(directory)
        active, backup, restored = (
            root / name for name in ("active.sqlite3", "backup.sqlite3", "restored.sqlite3")
        )
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
        os.environ["CEI_DEVELOPMENT_DB"] = str(active)
        sys.path.insert(0, str(ROOT / "src"))
        import django

        django.setup()
        from django.core.management import call_command
        from django.db import connections

        from modules.accounts.services import LOCAL_WORKSPACE_ID
        from modules.attempts.models import Attempt, OperationReceipt
        from modules.errors.models import (
            ErrorCategory,
            ErrorClassification,
            ErrorClassificationRevision,
        )
        from modules.questions.services import create_active
        from modules.taxonomy.services import create_discipline, create_subject
        from shared.application.bootstrap import bootstrap_local_workspace
        from shared.domain.time import FixedClock, Instant

        call_command("migrate", verbosity=0, interactive=False)
        bootstrap_local_workspace(timezone_id="UTC")
        discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Sintética S6")
        subject = create_subject(
            workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="S6"
        )
        instant = datetime(2026, 9, 10, 15, tzinfo=UTC)
        for index in range(2):
            question = create_active(
                workspace_id=LOCAL_WORKSPACE_ID,
                discipline_id=discipline.id,
                subject_id=subject.id,
                stem=f"Sintética {index}",
                alternatives=["A", "B"],
                correct_alternative_position=2,
                clock=FixedClock(Instant(instant)),
            )
            revision = question.revisions.get(is_current=True)
            attempt = Attempt.objects.create(
                workspace_id=LOCAL_WORKSPACE_ID,
                question=question,
                question_revision=revision,
                selected_alternative=revision.alternatives.get(position=1),
                attempt_type="INITIAL",
                is_correct=False,
                occurred_at=instant,
                timezone_name="UTC",
                local_date=instant.date(),
                idempotency_key=uuid4(),
            )
            if index == 0:
                category = ErrorCategory.objects.get(
                    workspace_id=LOCAL_WORKSPACE_ID, code="CONCEPTUAL"
                )
                classification = ErrorClassification.objects.create(
                    workspace_id=LOCAL_WORKSPACE_ID,
                    attempt=attempt,
                    category=category,
                )
                ErrorClassificationRevision.objects.create(
                    workspace_id=LOCAL_WORKSPACE_ID,
                    error_classification=classification,
                    revision_number=1,
                    category=category,
                )
                OperationReceipt.objects.create(
                    workspace_id=LOCAL_WORKSPACE_ID,
                    operation_kind="INITIAL_ERROR",
                    idempotency_key=attempt.idempotency_key,
                    request_hash=hashlib.sha256(b"synthetic-s6").hexdigest(),
                    result_entity_type="ATTEMPT",
                    result_entity_id=attempt.id,
                )
        connections.close_all()
        active_before = sha256(active)
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        steps: list[dict[str, object]] = []

        def command(name: str, *arguments: str, database: Path = active) -> None:
            environment["CEI_DEVELOPMENT_DB"] = str(database)
            started = time.perf_counter()
            completed = subprocess.run(  # noqa: S603 - executable and commands fixed by this drill
                [sys.executable, str(ROOT / "manage.py"), name, *arguments],
                cwd=ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            steps.append(
                {
                    "command": name,
                    "database": "restored" if database == restored else "synthetic_active",
                    "exit_code": completed.returncode,
                    "duration_seconds": round(time.perf_counter() - started, 6),
                }
            )
            if completed.returncode:
                raise RuntimeError(f"Ensaio interrompido: {name}, exit {completed.returncode}")

        command("check_integrity")
        command("backup_sqlite", "--output", str(backup))
        manifest = backup.with_name(f"{backup.name}.manifest.json")
        backup_before, manifest_before = sha256(backup), sha256(manifest)
        command("validate_backup", "--backup", str(backup))
        recovery_started = time.perf_counter()
        command("restore_backup", "--backup", str(backup), "--destination", str(restored))
        command("check_integrity", database=restored)
        # ORM opening in a separate application process, without bootstrap/migrate.
        command(
            "shell",
            "-c",
            "from modules.attempts.models import Attempt; assert Attempt.objects.count() == 2",
            database=restored,
        )
        with closing(sqlite3.connect(f"{restored.as_uri()}?mode=ro", uri=True)) as database:
            physical = database.execute("PRAGMA integrity_check").fetchall()
            foreign_keys = database.execute("PRAGMA foreign_key_check").fetchall()
            tables = (
                "questions_question",
                "attempts_attempt",
                "errors_errorclassification",
                "errors_errorclassificationrevision",
                "reviews_reviewcycle",
                "reviews_review",
                "attempts_operationreceipt",
                "django_migrations",
            )
            counts = {
                table: database.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]  # noqa: S608 - fixed table tuple
                for table in tables
            }
        duration = time.perf_counter() - recovery_started
        if physical != [("ok",)] or foreign_keys:
            raise RuntimeError("Falha física no restore sintético.")
        if sha256(active) != active_before or sha256(manifest) != manifest_before:
            raise RuntimeError("O ensaio alterou um arquivo protegido.")
        if not sha256(backup) == backup_before == sha256(restored):
            raise RuntimeError("Falha de reconciliação por SHA-256.")
        if list(counts.values()) != [2, 2, 1, 1, 2, 2, 1, 24]:
            raise RuntimeError("As contagens não reconciliam com o estado sintético esperado.")
        report = {
            "task_id": "V0.4-S6",
            "observed_at": datetime.now(UTC).isoformat(),
            "environment": {
                "os": platform.system(),
                "python": platform.python_version(),
                "sqlite": sqlite3.sqlite_version,
                "django": django.get_version(),
            },
            "dataset": "synthetic, 2 active questions, 2 initial errors, 1 S1 residue",
            "steps": steps,
            "size_bytes": backup.stat().st_size,
            "recovery_duration_seconds": round(duration, 6),
            "rto_sla": False,
            "physical_integrity": "ok",
            "foreign_key_findings": 0,
            "s5_exit_code": 0,
            "counts": counts,
            "reconciliation_method": "exact SHA-256 equality before/after validation",
            "reconciled": True,
            "backup_unchanged": True,
            "manifest_unchanged": True,
            "active_unchanged": True,
            "application_opened": True,
            "result": "PASS",
            "human_validation": "not performed",
            "limitations": "Local synthetic drill, not BCR-1, pilot, production RTO or SLA.",
        }
        options.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
