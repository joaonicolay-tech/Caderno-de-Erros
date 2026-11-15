"""Run the source-distribution gate in an explicitly prepared synthetic instance."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

CODE = Path(__file__).absolute().parents[1]


def main() -> None:
    sys.path.insert(0, str(CODE))
    from scripts.source_release import digest, payload

    def source_identity() -> str:
        return digest(
            json.dumps({p: digest(raw) for p, raw in payload().items()}, sort_keys=True).encode()
        )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uv", default="uv")
    args = parser.parse_args()
    marker = json.loads((CODE / ".local-r1.json").read_text(encoding="utf-8"))
    if (
        CODE.name != "candidate"
        or marker.get("source_distribution") != "PUBLIC_SOURCE_SYNTHETIC_ONLY"
        or marker.get("user_enabled") is not False
        or marker.get("root") != str(CODE.parent)
    ):
        raise RuntimeError(
            "Prepare a new synthetic source instance; real installation is prohibited"
        )
    root = CODE.parent
    initial_identity = source_identity()
    run = root / "validation" / ("gate-" + uuid.uuid4().hex)
    run.mkdir()
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("CEI_")
        and k not in {"DATABASE_URL", "PYTHONPATH", "PYTHONHOME", "DJANGO_SETTINGS_MODULE"}
    }
    env.update(
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONIOENCODING="utf-8",
        DJANGO_SETTINGS_MODULE="config.settings.test",
        TEMP=str(root / "validation/tmp"),
        TMP=str(root / "validation/tmp"),
        UV_LINK_MODE="copy",
        RUFF_CACHE_DIR=str(root / "validation/cache/ruff"),
        MYPY_CACHE_DIR=str(root / "validation/cache/mypy"),
        COVERAGE_FILE=str(run / ".coverage"),
    )
    python = str(CODE / ".venv/Scripts/python.exe")
    phases: dict[str, int] = {}

    def step(label: str, command: list[str]) -> None:
        print("==> " + label, flush=True)
        with (run / (label + ".log")).open("xb") as log:
            result = subprocess.run(  # noqa: S603 -- fixed phase arguments and explicit uv executable; no shell
                command, cwd=CODE, env=env, stdout=log, stderr=subprocess.STDOUT, check=False
            )
        phases[label] = result.returncode
        if result.returncode:
            print((run / (label + ".log")).read_text(encoding="utf-8", errors="replace")[-10000:])
            raise RuntimeError("Source gate failed: " + label)

    result = {
        "scope": "PUBLIC_SOURCE_SYNTHETIC_ONLY",
        "result": "FAIL",
        "phases": phases,
        "real_use_qualified": False,
        "source_identity": initial_identity,
    }
    try:
        step("sync", [args.uv, "sync", "--locked"])
        step("lock", [args.uv, "lock", "--check", "--offline"])
        step(
            "runtime",
            [
                python,
                "-c",
                "import sys,django,sqlite3; assert sys.version_info[:3]==(3,13,15); assert django.get_version()=='5.2.17'; assert sqlite3.sqlite_version=='3.53.1'; print(sys.version, django.get_version(), sqlite3.sqlite_version)",
            ],
        )
        step("lint", [python, "-m", "ruff", "check", "src", "tests", "scripts"])
        step("format", [python, "-m", "ruff", "format", "--check", "src", "tests", "scripts"])
        step("typing", [python, "-m", "mypy"])
        step("checks", [python, "manage.py", "check"])
        step("models", [python, "manage.py", "makemigrations", "--check", "--dry-run"])
        step(
            "empty-migrate",
            [
                python,
                "manage.py",
                "migrate",
                "--noinput",
                "--settings=config.settings.production_local",
            ],
        )
        step(
            "production-checks",
            [python, "manage.py", "check", "--settings=config.settings.production_local"],
        )
        step("public-source", [python, "-m", "scripts.check_source"])
        step(
            "tests",
            [
                python,
                "-m",
                "pytest",
                "tests",
                "--basetemp",
                str(run / "pytest"),
                "--junitxml",
                str(run / "tests.xml"),
                "--cov=src",
                "--cov-branch",
                "--cov-report=json:" + str(run / "coverage.json"),
                "--cov-report=term:skip-covered",
                "-q",
                "--tb=short",
            ],
        )
        step(
            "dependency-audit",
            [
                python,
                "-m",
                "pip_audit",
                "--local",
                "--strict",
                "--progress-spinner",
                "off",
                "--format",
                "json",
                "--output",
                str(run / "dependency-audit.json"),
            ],
        )
        step(
            "source-build",
            [python, "scripts/source_release.py", "build", "--output", str(run / "source.zip")],
        )
        if source_identity() != initial_identity:
            raise RuntimeError("Public source changed during gate execution")
        result["result"] = "PASS_PUBLIC_SOURCE_GATE"
    finally:
        (run / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
