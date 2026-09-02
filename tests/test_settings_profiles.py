"""Testes técnicos dos perfis e do isolamento exigido por CT-130."""

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import TypedDict, cast

import pytest
from django.conf import settings
from django.db import connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProfileSnapshot(TypedDict):
    profile: str
    debug: bool
    database_name: str
    database_test_name: str
    allowed_hosts: list[str]
    secret_matches_environment: bool
    check_errors: list[str]


PROFILE_PROBE = """
import json
import os

import django
from django.conf import settings
from django.core.checks import run_checks
from django.db import connection

django.setup()
with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    cursor.fetchone()

test_config = settings.DATABASES["default"].get("TEST", {})
print(json.dumps({
    "profile": settings.CEI_PROFILE,
    "debug": settings.DEBUG,
    "database_name": str(settings.DATABASES["default"]["NAME"]),
    "database_test_name": str(test_config.get("NAME", "")),
    "allowed_hosts": list(settings.ALLOWED_HOSTS),
    "secret_matches_environment": settings.SECRET_KEY == os.environ.get("CEI_SECRET_KEY"),
    "check_errors": [str(error) for error in run_checks()],
}))
"""


def run_profile_process(
    settings_module: str,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Inicialize um perfil em processo limpo e devolva sua evidência."""
    process_environment = os.environ.copy()
    process_environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    process_environment["DJANGO_SETTINGS_MODULE"] = settings_module
    process_environment.pop("CEI_SECRET_KEY", None)
    process_environment.pop("CEI_ALLOWED_HOSTS", None)
    process_environment.pop("CEI_DEVELOPMENT_DB", None)
    process_environment.pop("CEI_PRODUCTION_LOCAL_DB", None)
    if environment:
        process_environment.update(environment)

    return subprocess.run(
        [sys.executable, "-c", PROFILE_PROBE],
        cwd=PROJECT_ROOT,
        env=process_environment,
        capture_output=True,
        text=True,
        check=False,
    )


def successful_snapshot(result: subprocess.CompletedProcess[str]) -> ProfileSnapshot:
    """Exija sucesso do processo e converta sua última linha JSON."""
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    return cast(ProfileSnapshot, payload)


def synthetic_secret() -> str:
    """Produza valor de teste que não representa credencial real."""
    return hashlib.sha256(b"production-local-test-only").hexdigest()


def test_development_profile_initializes_with_local_database(tmp_path: Path) -> None:
    database_path = tmp_path / "development.sqlite3"
    snapshot = successful_snapshot(
        run_profile_process(
            "config.settings.development",
            {"CEI_DEVELOPMENT_DB": str(database_path)},
        )
    )

    assert snapshot["profile"] == "development"
    assert snapshot["debug"] is True
    assert Path(snapshot["database_name"]) == database_path
    assert set(snapshot["allowed_hosts"]) <= {"127.0.0.1", "localhost", "[::1]"}
    assert snapshot["check_errors"] == []


def test_test_profile_ignores_real_database_and_secret_environment(tmp_path: Path) -> None:
    sentinel_database = tmp_path / "real-local.sqlite3"
    sentinel_connection = sqlite3.connect(sentinel_database)
    try:
        sentinel_connection.execute("CREATE TABLE sentinel (value TEXT NOT NULL)")
        sentinel_connection.execute("INSERT INTO sentinel VALUES ('preservado')")
        sentinel_connection.commit()
    finally:
        sentinel_connection.close()
    original_bytes = sentinel_database.read_bytes()

    snapshot = successful_snapshot(
        run_profile_process(
            "config.settings.test",
            {
                "CEI_DEVELOPMENT_DB": str(sentinel_database),
                "CEI_PRODUCTION_LOCAL_DB": str(sentinel_database),
                "CEI_SECRET_KEY": synthetic_secret(),
            },
        )
    )

    test_database = Path(snapshot["database_name"])
    assert test_database != sentinel_database
    assert test_database.is_relative_to(Path(tempfile.gettempdir()).resolve())
    assert snapshot["database_test_name"] == snapshot["database_name"]
    assert snapshot["secret_matches_environment"] is False
    assert sentinel_database.read_bytes() == original_bytes
    assert snapshot["check_errors"] == []

    shutil.rmtree(test_database.parent, ignore_errors=True)


def test_production_local_initializes_without_debug_and_only_local_hosts(tmp_path: Path) -> None:
    database_path = tmp_path / "production-local.sqlite3"
    snapshot = successful_snapshot(
        run_profile_process(
            "config.settings.production_local",
            {
                "CEI_SECRET_KEY": synthetic_secret(),
                "CEI_PRODUCTION_LOCAL_DB": str(database_path),
            },
        )
    )

    assert snapshot["profile"] == "production_local"
    assert snapshot["debug"] is False
    assert Path(snapshot["database_name"]) == database_path
    assert set(snapshot["allowed_hosts"]) <= {"127.0.0.1", "localhost", "[::1]"}
    assert snapshot["secret_matches_environment"] is True
    assert snapshot["check_errors"] == []


def test_production_local_requires_external_secret() -> None:
    result = run_profile_process("config.settings.production_local")

    assert result.returncode != 0
    assert "CEI_SECRET_KEY é obrigatória" in result.stderr


def test_production_local_rejects_non_local_host(tmp_path: Path) -> None:
    result = run_profile_process(
        "config.settings.production_local",
        {
            "CEI_SECRET_KEY": synthetic_secret(),
            "CEI_ALLOWED_HOSTS": "0.0.0.0",
            "CEI_PRODUCTION_LOCAL_DB": str(tmp_path / "must-not-open.sqlite3"),
        },
    )

    assert result.returncode != 0
    assert "aceita somente hosts locais" in result.stderr
    assert not (tmp_path / "must-not-open.sqlite3").exists()


@pytest.mark.django_db
def test_pytest_django_uses_disposable_sqlite_database() -> None:
    assert settings.CEI_PROFILE == "test"
    assert settings.DEBUG is False
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"
    configured_name = settings.DATABASES["default"]["NAME"]
    assert isinstance(configured_name, (str, Path))
    assert Path(configured_name).is_relative_to(Path(tempfile.gettempdir()).resolve())

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)


def test_pytest_and_mypy_are_bound_to_test_settings(pytestconfig: pytest.Config) -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        configuration = tomllib.load(pyproject_file)

    pytest_configuration = configuration["tool"]["pytest"]["ini_options"]
    mypy_configuration = configuration["tool"]["mypy"]
    stubs_configuration = configuration["tool"]["django-stubs"]

    assert pytestconfig.getini("DJANGO_SETTINGS_MODULE") == "config.settings.test"
    assert pytest_configuration["DJANGO_SETTINGS_MODULE"] == "config.settings.test"
    assert "mypy_django_plugin.main" in mypy_configuration["plugins"]
    assert stubs_configuration["django_settings_module"] == "config.settings.test"
