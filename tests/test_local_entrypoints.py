"""Entradas recusadas e segredos sintéticos, sem abrir banco externo."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from shared.infrastructure import local_boundary as boundary


@pytest.mark.parametrize("content", [None, "curta"])
def test_missing_or_short_secret_is_native_failure(tmp_path: Path, content: str | None) -> None:
    key = tmp_path / "synthetic-secret.txt"
    if content is not None:
        key.write_text(content)
    with pytest.raises(boundary.BoundaryError):
        boundary.production_secret(key)


@pytest.mark.parametrize(
    "arguments,extra,expected",
    [
        (["check", "--settings=config.settings.development"], {}, "Perfil"),
        (["runserver", "0.0.0.0:8000"], {}, "127.0.0.1"),
        (["check"], {"CEI_PRODUCTION_LOCAL_DB": r"Z:\synthetic-refused\db.sqlite3"}, "Override"),
        (["check", "--pythonpath=Z:\\synthetic-refused"], {}, "módulos"),
    ],
)
def test_direct_cli_rejection(arguments: list[str], extra: dict[str, str], expected: str) -> None:
    environment = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("CEI_")
        and k not in {"DATABASE_URL", "PYTHONPATH", "PYTHONHOME", "DJANGO_SETTINGS_MODULE"}
    }
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings.production_local"
    environment["PYTHONIOENCODING"] = "utf-8"
    environment.update(extra)
    result = subprocess.run(
        [sys.executable, str(boundary.CODE / "manage.py"), *arguments],
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode != 0
    assert expected in result.stderr


def test_nonlocal_host_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    from config.settings.base import local_allowed_hosts

    monkeypatch.setenv("CEI_ALLOWED_HOSTS", "synthetic-remote.invalid")
    from django.core.exceptions import ImproperlyConfigured

    with pytest.raises(ImproperlyConfigured, match="somente hosts locais"):
        local_allowed_hosts()


def test_invalid_marker_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    original = Path.read_text

    def read(path: Path, *args: Any, **kwargs: Any) -> str:
        return (
            '{"route":"INVALID"}'
            if path == boundary.CODE / ".local-r1.json"
            else original(path, *args, **kwargs)
        )

    monkeypatch.setattr(Path, "read_text", read)
    with pytest.raises(boundary.BoundaryError, match="Marcador"):
        boundary.configure_process()
