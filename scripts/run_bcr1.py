"""BCR canônico local: três execuções seriais; bancos e falhas preservados."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

CODE = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(CODE / "src"))
from shared.infrastructure.local_boundary import (  # noqa: E402
    ROOT,
    admit,
    configure_process,
    sqlite_path,
)


def _environment(database_path: Path) -> dict[str, Any]:
    import django

    storage = shutil.disk_usage(database_path.parent)
    return {
        "operating_system": platform.platform(),
        "python": platform.python_version(),
        "django": django.get_version(),
        "sqlite": sqlite3.sqlite_version,
        "cpu": {"model": platform.processor(), "logical_cores": os.cpu_count()},
        "storage": {"slot": "validation", "free_bytes": storage.free},
        "django_profile": "test; database explicitly admitted under validation before connection",
        "execution_mode": "single worker, serial operations; no artificial concurrency",
    }


def _worker(args: argparse.Namespace, multiplier: int) -> int:
    if args.database is None or args.run_number not in {1, 2, 3}:
        raise ValueError("Worker exige banco novo e run 1, 2 ou 3.")
    database = sqlite_path(args.database)
    output = admit(args.result, slots=frozenset({"validation"}), require_existing=False)
    if database.exists() or output.exists():
        raise ValueError("Worker não sobrescreve banco ou resultado existente.")
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
    import django

    django.setup()
    from django.core.management import call_command
    from django.db import connection, connections

    from modules.accounts.services import LOCAL_WORKSPACE_ID
    from modules.attempts.models import Attempt
    from modules.operations.integrity import run_integrity_check
    from modules.questions.models import Question
    from modules.reviews.models import Review
    from modules.taxonomy.models import Discipline, Subject, Subsubject
    from shared.application.bcr1 import DEFAULT_DATASET, execute_run

    connection.settings_dict["NAME"] = str(database)
    dataset = replace(
        DEFAULT_DATASET,
        question_count=DEFAULT_DATASET.question_count * multiplier,
        attempt_count=DEFAULT_DATASET.attempt_count * multiplier,
        review_count=DEFAULT_DATASET.review_count * multiplier,
        taxonomy_per_level=DEFAULT_DATASET.taxonomy_per_level * multiplier,
    )
    try:
        call_command("migrate", interactive=False, verbosity=0)
        run = execute_run(run_number=args.run_number, dataset=dataset)
        actual = {
            "questions": Question.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
            "attempts": Attempt.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
            "reviews": Review.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
            "disciplines": Discipline.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
            "subjects": Subject.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
            "subsubjects": Subsubject.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
        }
        operations = 20 + 100
        expected = {
            "questions": dataset.question_count + 4 * operations + 1,
            "attempts": dataset.attempt_count + 3 * operations,
            "reviews": dataset.review_count + 5 * operations + 1,
            "disciplines": dataset.taxonomy_per_level,
            "subjects": dataset.taxonomy_per_level,
            "subsubjects": dataset.taxonomy_per_level,
        }
        integrity = run_integrity_check()
        reads = run.read_benchmark or {}
        complete = (
            len(run.operations) == 3
            and all(op.warmups_excluded == 20 and op.sample_count == 100 for op in run.operations)
            and len(reads.get("operations", [])) == 11
            and all(
                op["warmups_excluded"] == 20 and op["sample_count"] == 100
                for op in reads.get("operations", [])
            )
        )
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA integrity_check")
            sqlite_integrity = cursor.fetchall()
            cursor.execute("PRAGMA foreign_key_check")
            foreign_keys = cursor.fetchall()
        timing_ok = run.status == "PASS" and reads.get("status") == "PASS"
        passed = (
            complete
            and actual == expected
            and integrity.total_findings == 0
            and sqlite_integrity == [("ok",)]
            and not foreign_keys
            and reads.get("pagination", {}).get("status") == "PASS"
            and reads.get("reconciliation", {}).get("workspace_isolation") is True
            and (timing_ok if multiplier == 1 else True)
        )
        payload = {
            "environment": _environment(database),
            "dataset": asdict(dataset),
            "run": run.as_dict(),
            "integrity": asdict(integrity),
            "sqlite_integrity": sqlite_integrity,
            "foreign_keys": foreign_keys,
            "counts": {"expected": expected, "actual": actual},
            "protocol_complete": complete,
            "timing_within_bcr1_limits": timing_ok,
            "new_bcr2_latency_sla": None,
            "status": "PASS" if passed else "FAIL",
        }
    except Exception as error:
        payload = {
            "run_number": args.run_number,
            "status": "FAIL",
            "error": {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            },
        }
    finally:
        connections.close_all()
    with output.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, default=str)
    return 0 if payload["status"] == "PASS" else 1


def main(multiplier: int = 1) -> int:
    parser = argparse.ArgumentParser(description=f"BCR-{multiplier}: protocolo integral Local r1")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--run-number", type=int)
    parser.add_argument("--database", type=Path)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    configure_process()
    if args.worker:
        return _worker(args, multiplier)
    result_path = admit(args.result, slots=frozenset({"evidence"}), require_existing=False)
    if result_path.exists():
        raise ValueError("Resultado existente será preservado.")
    target = admit(
        Path(tempfile.mkdtemp(prefix=f"bcr{multiplier}-", dir=admit(ROOT / "validation")))
    )
    entries: list[dict[str, Any]] = []
    for number in range(1, 4):
        artifact = target / f"run-{number}.json"
        command = [
            sys.executable,
            str(CODE / f"scripts/run_bcr{multiplier}.py"),
            "--worker",
            "--run-number",
            str(number),
            "--database",
            str(target / f"run-{number}.sqlite3"),
            "--result",
            str(artifact),
        ]
        completed = subprocess.run(command, check=False)  # noqa: S603 -- worker próprio
        entry = (
            json.loads(artifact.read_text(encoding="utf-8"))
            if artifact.exists()
            else {"status": "FAIL", "reason": "worker produced no result"}
        )
        entry["worker_exit_code"] = completed.returncode
        entries.append(entry)
    passed = all(entry["status"] == "PASS" and entry["worker_exit_code"] == 0 for entry in entries)
    result = {
        "benchmark": f"BCR-{multiplier}",
        "method": {
            "warmups_per_operation": 20,
            "measured_samples_per_operation": 100,
            "repetitions": 3,
            "p95": "nearest-rank: ceil(0.95 * N)",
            "write_query_limit_seconds": 2.0 if multiplier == 1 else None,
            "screen_limit_seconds": 3.0 if multiplier == 1 else None,
        },
        "dataset_multiplier": multiplier,
        "runs": entries,
        "status": "PASS" if passed else "FAIL",
        "database_policy": "Three owned synthetic validation databases and all worker results preserved; no cleanup.",
        "validation_directory": str(target.relative_to(ROOT)),
    }
    with result_path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    print(
        json.dumps(
            {
                "benchmark": result["benchmark"],
                "status": result["status"],
                "result": str(result_path),
            }
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
