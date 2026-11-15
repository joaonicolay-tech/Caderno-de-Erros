"""S8: negativos lexicais e nativos somente com sentinelas próprias."""

import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from django.core.management.base import CommandError
from pytest_django.fixtures import Settings

from shared.infrastructure import local_boundary as boundary


@pytest.mark.parametrize(
    "path",
    [
        r"Z:\synthetic-refused\sentinel.sqlite3",
        r"\\synthetic-host\share\sentinel",
        "relative.sqlite3",
        str(boundary.ROOT / "validation" / ".." / "candidate" / "x"),
        str(boundary.ROOT / "validation" / "x:stream"),
        str(boundary.ROOT / "validation" / "NUL"),
        str(boundary.ROOT / "validation" / "x."),
        str(boundary.ROOT / "user" / "not-enabled.sqlite3"),
    ],
)
def test_refused_path_does_not_reach_native_or_stat(
    path: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        calls.append(True)
        raise AssertionError("Alvo recusado não pode ser consultado")

    monkeypatch.setattr(boundary, "_native", forbidden)
    monkeypatch.setattr(Path, "stat", forbidden)
    with pytest.raises(boundary.BoundaryError):
        boundary.admit(path)
    assert calls == []


def test_native_regular_file_identity(tmp_path: Path) -> None:
    path = tmp_path / "owned.txt"
    path.write_text("GENERATED_SYNTHETIC")
    assert boundary.admit(path) == path
    assert boundary._native(path, require_existing=True)["links"] == 1


def test_native_hardlink_is_refused(tmp_path: Path) -> None:
    source = tmp_path / "owned.txt"
    alias = tmp_path / "owned-alias.txt"
    source.write_text("GENERATED_SYNTHETIC")
    os.link(source, alias)
    with pytest.raises(boundary.BoundaryError, match="hardlink"):
        boundary.admit(alias)


def test_native_junction_is_refused_without_following(tmp_path: Path) -> None:
    target = tmp_path / "owned-target"
    target.mkdir()
    junction = tmp_path / "owned-junction"
    result = subprocess.run(
        [r"C:\Windows\System32\cmd.exe", "/c", "mklink", "/J", str(junction), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    with pytest.raises(boundary.BoundaryError, match="junction"):
        boundary.admit(junction / "not-opened.sqlite3", require_existing=False)


def test_database_override_is_refused_before_connect(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CEI_PRODUCTION_LOCAL_DB", r"Z:\synthetic-refused\db.sqlite3")
    with pytest.raises(boundary.BoundaryError, match="Override"):
        boundary.configure_process()


def test_import_entrypoint_is_disabled_before_open(monkeypatch: pytest.MonkeyPatch) -> None:
    from modules.data_management.management.commands.import_cei import Command

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Importação desabilitada não pode abrir arquivo")

    monkeypatch.setattr(Path, "open", forbidden)
    with pytest.raises(CommandError, match="desabilitada"):
        Command().handle(package=r"Z:\synthetic-refused\export.zip")


@pytest.mark.parametrize("profile", ["config.settings.development", "synthetic.untrusted"])
def test_profile_override_is_refused(profile: str) -> None:
    with pytest.raises(boundary.BoundaryError, match="Perfil"):
        boundary.entry_settings(["manage.py", "check", "--settings=" + profile])


def test_non_loopback_bind_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "config.settings.production_local")
    with pytest.raises(boundary.BoundaryError, match=r"127\.0\.0\.1"):
        boundary.entry_settings(["manage.py", "runserver", "0.0.0.0:8000"])


@pytest.mark.django_db
@pytest.mark.parametrize(
    "command,options",
    [
        ("backup_sqlite", {"output": "EXTERNAL"}),
        ("validate_backup", {"backup": "EXTERNAL"}),
        ("restore_backup", {"backup": "EXTERNAL", "destination": "OWN_DESTINATION"}),
        ("apply_prepared_restore", {"ticket": "EXTERNAL"}),
        ("validate_backup", {"backup": "OWN_DATABASE", "manifest": "EXTERNAL"}),
    ],
)
def test_direct_recovery_commands_never_inspect_refused_target(
    command: str,
    options: dict[str, str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
) -> None:
    import sqlite3

    from django.core.management import call_command

    refused = r"Z:\synthetic-refused\sentinel.sqlite3"
    calls = []

    def spy(original: Callable[..., Any]) -> Callable[..., Any]:
        def checked(path: Any, *args: Any, **kwargs: Any) -> Any:
            if "synthetic-refused" in str(path):
                calls.append(str(path))
                raise AssertionError("Alvo externo recusado foi consultado")
            return original(path, *args, **kwargs)

        return checked

    monkeypatch.setattr(Path, "stat", spy(Path.stat))
    monkeypatch.setattr(Path, "open", spy(Path.open))
    monkeypatch.setattr(Path, "resolve", spy(Path.resolve))
    monkeypatch.setattr(sqlite3, "connect", spy(sqlite3.connect))
    monkeypatch.setattr(sqlite3.dbapi2, "connect", spy(sqlite3.dbapi2.connect))
    values = {
        "EXTERNAL": refused,
        "OWN_DATABASE": settings.DATABASES["default"]["NAME"],
        "OWN_DESTINATION": str(tmp_path / "not-created.sqlite3"),
    }
    with pytest.raises(CommandError):
        call_command(command, **{key: values[value] for key, value in options.items()})
    assert calls == []
    assert not (tmp_path / "not-created.sqlite3").exists()
