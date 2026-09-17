"""CLI isolada para executar BCR-1 em três bancos SQLite descartáveis."""

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
from pathlib import Path
from typing import Any


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Executor reproduzível BCR-1 / CT-107")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--run-number", type=int)
    parser.add_argument("--database", type=Path)
    parser.add_argument("--result", type=Path, default=Path("quality/v03-bcr1-result.json"))
    return parser


def _environment(database_path: Path) -> dict[str, Any]:
    import django

    storage = shutil.disk_usage(database_path.parent)
    cpu_name = platform.processor() or None
    memory_bytes: int | None = None
    try:
        import ctypes

        status = ctypes.c_ulonglong()
        if ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(status)):
            memory_bytes = int(status.value) * 1024
    except (AttributeError, OSError):
        pass
    return {
        "operating_system": platform.platform(),
        "python": platform.python_version(),
        "django": django.get_version(),
        "sqlite": sqlite3.sqlite_version,
        "cpu": {"model": cpu_name, "logical_cores": os.cpu_count()},
        "ram_bytes": memory_bytes,
        "storage": {
            "path": "temporary benchmark directory",
            "type": "unavailable",
            "free_bytes": storage.free,
        },
        "django_profile": "development (CEI_DEVELOPMENT_DB overridden for BCR-1)",
        "execution_mode": "single process, sequential writes, no artificial concurrency",
    }


def _worker(args: argparse.Namespace) -> int:
    if args.database is None or args.run_number is None:
        raise SystemExit("--worker exige --database e --run-number")
    database = args.database.resolve()
    database.parent.mkdir(parents=True, exist_ok=True)
    source_root = Path(__file__).resolve().parents[1] / "src"
    sys.path.insert(0, str(source_root))
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    os.environ["CEI_DEVELOPMENT_DB"] = str(database)
    import django

    django.setup()

    from django.core.management import call_command

    from shared.application.bcr1 import execute_run

    try:
        call_command("migrate", interactive=False, verbosity=0)
        run = execute_run(run_number=args.run_number)
        args.result.write_text(
            json.dumps({"environment": _environment(database), "run": run.as_dict()}, indent=2),
            encoding="utf-8",
        )
        return 0
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
        from django.db import connections

        connections.close_all()
        if database.exists():
            database.unlink()


def _parent(args: argparse.Namespace) -> int:
    temporary = Path(tempfile.mkdtemp(prefix="cei-bcr1-"))
    worker_results: list[dict[str, Any]] = []
    try:
        for run_number in range(1, 4):
            run_result = temporary / f"run-{run_number}.json"
            database = temporary / f"run-{run_number}.sqlite3"
            command = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                "--run-number",
                str(run_number),
                "--database",
                str(database),
                "--result",
                str(run_result),
            ]
            subprocess.run(command, check=False)  # noqa: S603
            if not run_result.exists():
                worker_results.append(
                    {"run_number": run_number, "status": "FAIL", "reason": "worker failed"}
                )
                continue
            worker_results.append(json.loads(run_result.read_text(encoding="utf-8")))
        write_statuses = [entry.get("run", entry).get("status") for entry in worker_results]
        read_statuses = [
            entry.get("run", entry).get("read_benchmark", {}).get("status")
            for entry in worker_results
        ]
        result = {
            "benchmark": "BCR-1",
            "ct": "CT-105/CT-106/CT-107/CT-108/CT-110/CT-112",
            "method": {
                "warmups_per_operation": 20,
                "measured_samples_per_operation": 100,
                "repetitions": 3,
                "p95": "nearest-rank: sorted samples at position ceil(0.95 * N)",
                "limit_seconds": 2.0,
                "read_warmups_per_operation": 20,
                "read_measured_samples_per_operation": 100,
                "screen_limit_seconds": 3.0,
                "query_limit_seconds": 2.0,
            },
            "runs": worker_results,
            "ct107_status": ("PASS" if write_statuses == ["PASS", "PASS", "PASS"] else "FAIL"),
            "read_status": ("PASS" if read_statuses == ["PASS", "PASS", "PASS"] else "FAIL"),
            "status": (
                "PASS"
                if write_statuses == ["PASS", "PASS", "PASS"]
                and read_statuses == ["PASS", "PASS", "PASS"]
                else "FAIL"
            ),
            "database": "one dedicated SQLite database per run; each removed after result capture",
        }
        args.result.parent.mkdir(parents=True, exist_ok=True)
        args.result.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(
            json.dumps({"ct": result["ct"], "status": result["status"], "result": str(args.result)})
        )
        return 0 if result["status"] == "PASS" else 1
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


def main() -> int:
    args = _parser().parse_args()
    return _worker(args) if args.worker else _parent(args)


if __name__ == "__main__":
    raise SystemExit(main())
