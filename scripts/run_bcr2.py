"""BCR-2: reuse o protocolo BCR-1 em três SQLite descartáveis com carga 2x."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import traceback
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any


def _worker(args: argparse.Namespace) -> int:
    if args.database is None or args.run_number is None:
        raise SystemExit("Worker exige --database e --run-number.")
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "src"))
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    os.environ["CEI_DEVELOPMENT_DB"] = str(args.database.resolve())
    import django

    django.setup()
    from django.core.management import call_command
    from django.db import connections

    from modules.accounts.services import LOCAL_WORKSPACE_ID
    from modules.attempts.models import Attempt
    from modules.operations.integrity import run_integrity_check
    from modules.questions.models import Question
    from modules.reviews.models import Review
    from modules.taxonomy.models import Discipline, Subject, Subsubject
    from scripts.run_bcr1 import _environment
    from shared.application.bcr1 import DEFAULT_DATASET, execute_run

    dataset = replace(
        DEFAULT_DATASET,
        question_count=DEFAULT_DATASET.question_count * 2,
        attempt_count=DEFAULT_DATASET.attempt_count * 2,
        review_count=DEFAULT_DATASET.review_count * 2,
        taxonomy_per_level=DEFAULT_DATASET.taxonomy_per_level * 2,
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
        operations = run.operations[0].warmups_excluded + run.operations[0].sample_count
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
        passed = (
            complete
            and actual == expected
            and integrity.total_findings == 0
            and reads.get("pagination", {}).get("status") == "PASS"
            and reads.get("reconciliation", {}).get("workspace_isolation") is True
        )
        payload = {
            "environment": _environment(args.database),
            "run": run.as_dict(),
            "integrity": asdict(integrity),
            "counts": {
                "expected": expected,
                "actual": actual,
                "status": "PASS" if actual == expected else "FAIL",
            },
            "protocol_complete": complete,
            "baseline_target_comparison_only": "BCR-1 timing statuses are observations; RNF-005 sets no new BCR-2 latency SLA.",
            "status": "PASS" if passed else "FAIL",
        }
        args.result.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return 0 if passed else 1
    except Exception as error:
        args.result.write_text(
            json.dumps(
                {
                    "run_number": args.run_number,
                    "status": "FAIL",
                    "error": {
                        "type": type(error).__name__,
                        "message": str(error),
                        "traceback": traceback.format_exc(),
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return 1
    finally:
        connections.close_all()


def main() -> int:
    parser = argparse.ArgumentParser(description="BCR-2 / CT-109 sem novo SLA")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--run-number", type=int)
    parser.add_argument("--database", type=Path)
    parser.add_argument("--result", type=Path, default=Path("quality/v10-s5-bcr2-result.json"))
    args = parser.parse_args()
    if args.worker:
        return _worker(args)
    entries = []
    with tempfile.TemporaryDirectory(prefix="cei-bcr2-") as folder:
        target = Path(folder)
        for number in range(1, 4):
            artifact = target / f"run-{number}.json"
            database = target / f"run-{number}.sqlite3"
            command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                "--run-number",
                str(number),
                "--database",
                str(database),
                "--result",
                str(artifact),
            ]
            completed = subprocess.run(command, check=False)  # noqa: S603
            entry = (
                json.loads(artifact.read_text(encoding="utf-8"))
                if artifact.exists()
                else {"status": "FAIL", "reason": "worker produced no result"}
            )
            entry["worker_exit_code"] = completed.returncode
            entries.append(entry)
            database.unlink(missing_ok=True)
        passed = all(
            entry["status"] == "PASS" and entry["worker_exit_code"] == 0 for entry in entries
        )
        result: dict[str, Any] = {
            "benchmark": "BCR-2",
            "ct": "CT-109 / RNF-005",
            "method": {
                "warmups_per_operation": 20,
                "measured_samples_per_operation": 100,
                "repetitions": 3,
                "p95": "nearest-rank: ceil(0.95 * N)",
                "new_latency_threshold": None,
            },
            "dataset_multiplier": {
                "questions": 2,
                "attempts": 2,
                "reviews": 2,
                "taxonomy_per_level": 2,
            },
            "history_window": "same ten-year interval; record density doubled",
            "runs": entries,
            "status": "PASS" if passed else "FAIL",
            "database": "three isolated disposable SQLite databases removed after evidence capture",
        }
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(
            json.dumps(
                {"benchmark": "BCR-2", "status": result["status"], "result": str(args.result)}
            )
        )
        return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
