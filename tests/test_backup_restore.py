"""CT-132/CT-133 e parcela de corrupção de CT-114 para a fundação V0.1."""

import hashlib
import json
import logging
import os
import sqlite3
import subprocess
import sys
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import pytest
from django.core.management import call_command, get_commands
from django.db import connection

from modules.accounts.models import User, Workspace
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.data_management.exceptions import (
    BackupCreationError,
    BackupValidationError,
    RestoreError,
)
from modules.data_management.services import (
    BACKUP_FORMAT,
    BACKUP_FORMAT_VERSION,
    create_sqlite_backup,
    manifest_path_for,
    restore_sqlite_backup,
    validate_sqlite_backup,
)
from modules.errors.catalog import STANDARD_ERROR_CATEGORIES
from modules.errors.models import ErrorCategory
from modules.operations.structured_logging import StructuredJsonFormatter
from shared.application.bootstrap import bootstrap_local_workspace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXED_CORRELATION_ID = "12345678-1234-4234-8234-123456789abc"
PRIVATE_SENTINEL = "PRIVATE-BACKUP-SENTINEL-42"


@dataclass(frozen=True, slots=True)
class BackupFixture:
    """Artefatos gerados somente dentro do diretório descartável do teste."""

    backup: Path
    manifest: Path


@contextmanager
def captured_logger() -> Iterator[StringIO]:
    logger = logging.getLogger("cei")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(StructuredJsonFormatter())
    previous_level = logger.level
    previous_propagate = logger.propagate
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(handler)
    try:
        yield stream
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate


def parsed_events(stream: StringIO) -> list[dict[str, Any]]:
    return [cast(dict[str, Any], json.loads(line)) for line in stream.getvalue().splitlines()]


def rewrite_manifest(backup: Path, manifest: Path, **changes: object) -> None:
    document = cast(dict[str, object], json.loads(manifest.read_text(encoding="utf-8")))
    document.update(changes)
    manifest.write_text(f"{json.dumps(document, indent=2)}\n", encoding="utf-8")


def reconcile_manifest_after_database_change(backup: Path, manifest: Path) -> None:
    rewrite_manifest(
        backup,
        manifest,
        size_bytes=backup.stat().st_size,
        sha256=hashlib.sha256(backup.read_bytes()).hexdigest(),
    )


@pytest.fixture
def minimal_backup(transactional_db: None, tmp_path: Path) -> BackupFixture:
    del transactional_db
    bootstrap_local_workspace(timezone_id="America/Sao_Paulo", display_name="Estudante")
    connection.close()
    backup_directory = tmp_path / "backups"
    backup_directory.mkdir()
    backup = backup_directory / "foundation.sqlite3"
    create_sqlite_backup(backup)
    return BackupFixture(backup=backup, manifest=manifest_path_for(backup))


def test_ct132_creates_consistent_backup_and_minimal_manifest(
    minimal_backup: BackupFixture,
) -> None:
    document = json.loads(minimal_backup.manifest.read_text(encoding="utf-8"))

    assert minimal_backup.backup.is_file()
    assert set(document) == {"format", "format_version", "created_at", "size_bytes", "sha256"}
    assert document["format"] == BACKUP_FORMAT
    assert document["format_version"] == BACKUP_FORMAT_VERSION
    assert document["size_bytes"] == minimal_backup.backup.stat().st_size
    assert "path" not in minimal_backup.manifest.read_text(encoding="utf-8").lower()


def test_ct132_manifest_sha256_matches_the_artifact(minimal_backup: BackupFixture) -> None:
    result = validate_sqlite_backup(minimal_backup.backup)
    calculated = hashlib.sha256(minimal_backup.backup.read_bytes()).hexdigest()

    assert result.manifest.sha256 == calculated
    assert len(calculated) == 64


def test_sqlite_online_backup_reads_one_committed_point_during_uncommitted_write(
    tmp_path: Path,
) -> None:
    from modules.data_management.services import _sqlite_backup

    source = tmp_path / "source.sqlite3"
    snapshot = tmp_path / "snapshot.sqlite3"
    with closing(sqlite3.connect(source)) as database:
        with database:
            database.execute("PRAGMA journal_mode=WAL")
            database.execute("CREATE TABLE sample (value TEXT NOT NULL)")
            database.execute("INSERT INTO sample VALUES ('committed')")

    writer = sqlite3.connect(source, isolation_level=None)
    try:
        writer.execute("BEGIN IMMEDIATE")
        writer.execute("UPDATE sample SET value = 'not-committed'")
        _sqlite_backup(source, snapshot)
    finally:
        writer.execute("ROLLBACK")
        writer.close()

    with closing(sqlite3.connect(snapshot)) as database:
        assert database.execute("SELECT value FROM sample").fetchone() == ("committed",)


def test_ct114_corrupted_artifact_is_rejected_before_destination_exists(
    minimal_backup: BackupFixture,
    tmp_path: Path,
) -> None:
    with minimal_backup.backup.open("r+b") as artifact:
        artifact.seek(128)
        original = artifact.read(1)
        artifact.seek(128)
        artifact.write(bytes([original[0] ^ 0xFF]))
    destination = tmp_path / "restored.sqlite3"

    with pytest.raises(BackupValidationError, match="checksum"):
        validate_sqlite_backup(minimal_backup.backup)
    with pytest.raises(RestoreError, match="rejeitado"):
        restore_sqlite_backup(minimal_backup.backup, destination)

    assert not destination.exists()


def test_declared_checksum_mismatch_is_rejected(minimal_backup: BackupFixture) -> None:
    rewrite_manifest(minimal_backup.backup, minimal_backup.manifest, sha256="0" * 64)

    with pytest.raises(BackupValidationError, match="checksum"):
        validate_sqlite_backup(minimal_backup.backup)


def test_unknown_manifest_version_is_rejected_without_mutation(
    minimal_backup: BackupFixture,
    tmp_path: Path,
) -> None:
    rewrite_manifest(minimal_backup.backup, minimal_backup.manifest, format_version="99.0")
    destination = tmp_path / "must-not-exist.sqlite3"

    with pytest.raises(RestoreError, match="rejeitado"):
        restore_sqlite_backup(minimal_backup.backup, destination)

    assert not destination.exists()


def test_ct133_restores_and_reconciles_minimal_foundation(
    minimal_backup: BackupFixture,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "recovery" / "restored.sqlite3"
    destination.parent.mkdir()

    result = restore_sqlite_backup(minimal_backup.backup, destination)

    assert destination.is_file()
    assert result.reconciliation.user_count == 1
    assert result.reconciliation.workspace_count == 1
    assert result.reconciliation.category_count == 10
    with closing(sqlite3.connect(destination)) as database:
        user = database.execute("SELECT id FROM accounts_user").fetchone()
        workspace = database.execute(
            "SELECT id, owner_user_id, locale, timezone_name FROM accounts_workspace"
        ).fetchone()
        categories = database.execute(
            "SELECT code FROM errors_error_category ORDER BY code"
        ).fetchall()
        assert database.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        assert database.execute("PRAGMA foreign_key_check").fetchall() == []

    assert user == (LOCAL_USER_ID.hex,)
    assert workspace == (
        LOCAL_WORKSPACE_ID.hex,
        LOCAL_USER_ID.hex,
        "pt-BR",
        "America/Sao_Paulo",
    )
    assert [row[0] for row in categories] == sorted(
        definition.code for definition in STANDARD_ERROR_CATEGORIES
    )


def test_restored_database_allows_application_initialization(
    minimal_backup: BackupFixture,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "restored-for-startup.sqlite3"
    restore_sqlite_backup(minimal_backup.backup, destination)
    probe = (
        "import django; django.setup(); "
        "from modules.accounts.models import User, Workspace; "
        "from modules.errors.models import ErrorCategory; "
        "assert (User.objects.count(), Workspace.objects.count(), "
        "ErrorCategory.objects.count()) == (1, 1, 10)"
    )
    environment = os.environ.copy()
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings.development"
    environment["CEI_DEVELOPMENT_DB"] = str(destination)
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")

    completed = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr


def test_restore_does_not_duplicate_or_change_live_identity(
    minimal_backup: BackupFixture,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "isolated.sqlite3"
    before = (User.objects.count(), Workspace.objects.count(), ErrorCategory.objects.count())

    restore_sqlite_backup(minimal_backup.backup, destination)

    assert (
        User.objects.count(),
        Workspace.objects.count(),
        ErrorCategory.objects.count(),
    ) == before
    assert User.objects.get().id == LOCAL_USER_ID
    assert Workspace.objects.get().id == LOCAL_WORKSPACE_ID


def test_restore_remains_available_when_configured_active_database_is_missing(
    minimal_backup: BackupFixture,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "recovery-after-loss.sqlite3"
    missing_active_database = tmp_path / "lost-active.sqlite3"

    with patch(
        "modules.data_management.services._database_path",
        return_value=missing_active_database,
    ):
        result = restore_sqlite_backup(minimal_backup.backup, destination)

    assert destination.is_file()
    assert result.reconciliation.category_count == 10


def test_existing_destination_is_never_replaced(
    minimal_backup: BackupFixture, tmp_path: Path
) -> None:
    destination = tmp_path / "existing.sqlite3"
    sentinel = b"existing-database-sentinel"
    destination.write_bytes(sentinel)

    with pytest.raises(RestoreError):
        restore_sqlite_backup(minimal_backup.backup, destination)

    assert destination.read_bytes() == sentinel


def test_missing_category_is_not_silently_recreated(
    minimal_backup: BackupFixture,
    tmp_path: Path,
) -> None:
    with closing(sqlite3.connect(minimal_backup.backup)) as database:
        with database:
            database.execute("DELETE FROM errors_error_category WHERE code = 'OTHER'")
    reconcile_manifest_after_database_change(minimal_backup.backup, minimal_backup.manifest)
    destination = tmp_path / "invalid-foundation.sqlite3"

    with pytest.raises(RestoreError, match="dez categorias"):
        restore_sqlite_backup(minimal_backup.backup, destination)

    assert not destination.exists()


def test_missing_migration_is_rejected_before_publication(
    minimal_backup: BackupFixture,
    tmp_path: Path,
) -> None:
    with closing(sqlite3.connect(minimal_backup.backup)) as database:
        with database:
            database.execute(
                "DELETE FROM django_migrations WHERE app = 'errors' AND name = '0001_initial'"
            )
    reconcile_manifest_after_database_change(minimal_backup.backup, minimal_backup.manifest)
    destination = tmp_path / "wrong-schema.sqlite3"

    with pytest.raises(RestoreError, match="migrações"):
        restore_sqlite_backup(minimal_backup.backup, destination)

    assert not destination.exists()


def test_backup_failure_cleans_temporary_files_and_does_not_publish(
    transactional_db: None,
    tmp_path: Path,
) -> None:
    del transactional_db
    bootstrap_local_workspace(timezone_id="UTC")
    connection.close()
    output = tmp_path / "failed.sqlite3"

    with patch(
        "modules.data_management.services._sqlite_backup",
        side_effect=OSError(PRIVATE_SENTINEL),
    ):
        with pytest.raises(BackupCreationError):
            create_sqlite_backup(output)

    assert not output.exists()
    assert not manifest_path_for(output).exists()
    assert list(tmp_path.glob(".cei-*")) == []


def test_backup_and_restore_success_logs_share_correlation(
    transactional_db: None,
    tmp_path: Path,
) -> None:
    del transactional_db
    bootstrap_local_workspace(timezone_id="UTC")
    connection.close()
    backup = tmp_path / "backup.sqlite3"
    destination = tmp_path / "restored.sqlite3"

    with captured_logger() as stream:
        create_sqlite_backup(backup, correlation_id=FIXED_CORRELATION_ID)
        restore_sqlite_backup(backup, destination, correlation_id=FIXED_CORRELATION_ID)

    events = parsed_events(stream)
    assert [event["event_code"] for event in events] == [
        "BACKUP_STARTED",
        "BACKUP_SUCCEEDED",
        "RESTORE_STARTED",
        "INTEGRITY_CHECK_STARTED",
        "INTEGRITY_CHECK_SUCCEEDED",
        "RESTORE_VALIDATED",
    ]
    assert {event["correlation_id"] for event in events} == {FIXED_CORRELATION_ID}
    assert all("path" not in json.dumps(event["context"]).lower() for event in events)


def test_invalid_backup_failure_log_is_correlated_and_sanitized(tmp_path: Path) -> None:
    backup = tmp_path / PRIVATE_SENTINEL / "invalid.sqlite3"
    destination = tmp_path / "destination.sqlite3"

    with captured_logger() as stream:
        with pytest.raises(RestoreError):
            restore_sqlite_backup(
                backup,
                destination,
                correlation_id=FIXED_CORRELATION_ID,
            )

    raw_log = stream.getvalue()
    events = parsed_events(stream)
    assert [event["event_code"] for event in events] == ["RESTORE_STARTED", "RESTORE_FAILED"]
    assert {event["correlation_id"] for event in events} == {FIXED_CORRELATION_ID}
    assert PRIVATE_SENTINEL not in raw_log
    assert "Traceback" not in raw_log


def test_management_commands_are_available_and_validate_backup(
    minimal_backup: BackupFixture,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    commands = get_commands()
    assert commands["backup_sqlite"] == "modules.data_management"
    assert commands["validate_backup"] == "modules.data_management"
    assert commands["restore_backup"] == "modules.data_management"

    command_backup = tmp_path / "command-backup.sqlite3"
    command_restore = tmp_path / "command-restored.sqlite3"
    call_command("backup_sqlite", output=str(command_backup))
    call_command("validate_backup", backup=str(command_backup))
    call_command(
        "restore_backup",
        backup=str(command_backup),
        destination=str(command_restore),
    )

    output = capsys.readouterr().out
    assert "Backup criado e validado" in output
    assert "Backup válido" in output
    assert "Restauração isolada validada" in output
    assert command_restore.is_file()
