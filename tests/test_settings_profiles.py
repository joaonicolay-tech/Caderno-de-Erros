"""CT-130 local: perfis confinados e recusas reais em subprocesso."""

import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any, cast

import pytest
from django.conf import settings
from django.db import connection

from shared.infrastructure.local_boundary import ROOT, BoundaryError, production_secret

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PROBE = """
import json,os,django
django.setup()
from django.conf import settings
from django.core.checks import run_checks
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    assert cursor.fetchone()==(1,)
from django.test import Client
response=Client().get('/health/', HTTP_HOST='127.0.0.1', REMOTE_ADDR='127.0.0.1')
print(json.dumps({'profile':settings.CEI_PROFILE,'debug':settings.DEBUG,'database_name':str(settings.DATABASES['default']['NAME']),'allowed_hosts':settings.ALLOWED_HOSTS,'secret_matches_environment':settings.SECRET_KEY==os.environ.get('CEI_SECRET_KEY'),'check_errors':[str(x) for x in run_checks()], 'http_status':response.status_code,'response_headers':dict(response.headers)}))
"""


def run_profile_process(
    settings_module: str, environment: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("CEI_") and k not in {"DATABASE_URL", "PYTHONHOME", "PYTHONPATH"}
    }
    env.update(
        PYTHONPATH=str(PROJECT_ROOT / "src"),
        DJANGO_SETTINGS_MODULE=settings_module,
        PYTHONIOENCODING="utf-8",
    )
    if environment:
        env.update(environment)
    return subprocess.run(
        [sys.executable, "-c", PROFILE_PROBE],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def successful_snapshot(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    assert result.returncode == 0, result.stderr
    return cast(dict[str, Any], json.loads(result.stdout.strip().splitlines()[-1]))


def test_development_profile_is_refused_before_database_creation(tmp_path: Path) -> None:
    database = tmp_path / "not-created.sqlite3"
    result = run_profile_process(
        "config.settings.development", {"CEI_DEVELOPMENT_DB": str(database)}
    )
    assert result.returncode != 0 and not database.exists()


def test_test_profile_rejects_inherited_database_overrides(tmp_path: Path) -> None:
    sentinel = tmp_path / "synthetic-sentinel.bin"
    sentinel.write_bytes(b"GENERATED_SYNTHETIC")
    before = hashlib.sha256(sentinel.read_bytes()).hexdigest()
    for key in ["CEI_DEVELOPMENT_DB", "CEI_PRODUCTION_LOCAL_DB"]:
        result = run_profile_process("config.settings.test", {key: str(sentinel)})
        assert result.returncode != 0 and "Override" in result.stderr
    assert hashlib.sha256(sentinel.read_bytes()).hexdigest() == before


def test_test_profile_has_private_disposable_database_and_ignores_secret_env() -> None:
    result = successful_snapshot(
        run_profile_process(
            "config.settings.test",
            {
                "CEI_SECRET_KEY": "synthetic-environment-not-a-secret",  # pragma: allowlist secret -- public invalid test sentinel
            },
        )
    )
    other = successful_snapshot(run_profile_process("config.settings.test"))
    assert result["database_name"] != other["database_name"]
    assert Path(result["database_name"]).is_relative_to(ROOT / "validation")
    assert result["secret_matches_environment"] is False
    assert result["check_errors"] == []


def test_production_local_initializes_without_debug_and_only_local_hosts() -> None:
    snapshot = successful_snapshot(
        run_profile_process(
            "config.settings.production_local",
            {
                "CEI_SECRET_KEY": "ignored-synthetic-value",  # pragma: allowlist secret -- public invalid test sentinel
            },
        )
    )
    assert snapshot["profile"] == "production_local" and snapshot["debug"] is False
    assert Path(snapshot["database_name"]).is_relative_to(ROOT / "validation")
    assert set(snapshot["allowed_hosts"]) <= {"127.0.0.1", "localhost", "[::1]"}
    assert snapshot["secret_matches_environment"] is False
    assert snapshot["check_errors"] == []
    assert snapshot["http_status"] == 200
    assert snapshot["response_headers"]["X-Frame-Options"] == "DENY"
    assert snapshot["response_headers"]["X-Content-Type-Options"] == "nosniff"
    assert snapshot["response_headers"]["Referrer-Policy"] == "same-origin"


def test_production_local_requires_private_file_secret(tmp_path: Path) -> None:
    for name, content in [("missing", None), ("short", "too-short")]:
        path = tmp_path / name
        if content:
            path.write_text(content)
        with pytest.raises(BoundaryError):
            production_secret(path)


def test_production_local_rejects_non_local_host() -> None:
    result = run_profile_process(
        "config.settings.production_local", {"CEI_ALLOWED_HOSTS": "0.0.0.0"}
    )
    assert result.returncode != 0 and "somente hosts locais" in result.stderr


@pytest.mark.django_db
def test_pytest_django_uses_disposable_sqlite_database() -> None:
    assert settings.CEI_PROFILE == "test" and settings.DEBUG is False
    assert settings.DATABASES["default"]["ENGINE"] == "shared.infrastructure.sqlite_backend"
    assert Path(str(settings.DATABASES["default"]["NAME"])).is_relative_to(ROOT / "validation")
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)


def test_pytest_and_mypy_are_bound_to_test_settings(pytestconfig: pytest.Config) -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as file:
        config = tomllib.load(file)
    assert pytestconfig.getini("DJANGO_SETTINGS_MODULE") == "config.settings.test"
    assert (
        config["tool"]["pytest"]["ini_options"]["DJANGO_SETTINGS_MODULE"] == "config.settings.test"
    )
    assert config["tool"]["django-stubs"]["django_settings_module"] == "config.settings.test"
    assert "mypy_django_plugin.main" in config["tool"]["mypy"]["plugins"]
