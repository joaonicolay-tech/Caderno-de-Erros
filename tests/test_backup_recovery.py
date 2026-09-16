"""S6: recuperação real, isolamento e falhas impeditivas."""

import hashlib
import json
import shutil
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection, connections

from modules.accounts.models import Workspace
from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.attempts.models import Attempt
from modules.data_management import services
from modules.data_management.exceptions import BackupCreationError, RestoreError
from modules.operations.integrity import run_integrity_check
from modules.questions.services import create_active
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh_manifest(backup: Path) -> None:
    path = services.manifest_path_for(backup)
    document = json.loads(path.read_text(encoding="utf-8"))
    document.update(sha256=digest(backup), size_bytes=backup.stat().st_size)
    path.write_text(json.dumps(document), encoding="utf-8")


@pytest.fixture
def recovery_backup(transactional_db: None, tmp_path: Path) -> Path:
    del transactional_db
    bootstrap_local_workspace(timezone_id="UTC")
    discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Sintética")
    subject = create_subject(
        workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="Assunto"
    )
    instant = datetime(2026, 9, 10, 15, tzinfo=UTC)
    question = create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Sintética",
        alternatives=["A", "B"],
        correct_alternative_position=2,
        clock=FixedClock(Instant(instant)),
    )
    revision = question.revisions.get(is_current=True)
    # Resíduo S1 legítimo: erro VALID sem classificação.
    Attempt.objects.create(
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
    connection.close()
    backup = tmp_path / "s6.sqlite3"
    services.create_sqlite_backup(backup)
    return backup


def test_recovery_accepts_s1_residue_and_preserves_all_files(recovery_backup: Path) -> None:
    active = Path(connection.settings_dict["NAME"])
    manifest = services.manifest_path_for(recovery_backup)
    before = {path: digest(path) for path in (active, recovery_backup, manifest)}
    aliases = set(connections.databases)
    for index in range(2):
        restored = recovery_backup.with_name(f"restored-{index}.sqlite3")
        result = services.restore_sqlite_backup(recovery_backup, restored)
        assert result.integrity.total_findings == 0
        assert result.integrity.checks_executed == 17
        assert result.reconciliation.attempt_count == 1
        assert result.reconciliation.classification_count == 0
        assert result.reconciliation.review_count == 1
        assert digest(restored) == before[recovery_backup]
    assert {path: digest(path) for path in before} == before
    assert set(connections.databases) == aliases


def test_checker_rejects_bad_restore_while_active_is_healthy(recovery_backup: Path) -> None:
    with closing(sqlite3.connect(recovery_backup)) as database, database:
        database.execute("UPDATE attempts_attempt SET local_date = '2000-01-01'")
    refresh_manifest(recovery_backup)
    assert not run_integrity_check().has_blocking_findings
    before = digest(recovery_backup)
    active = Path(connection.settings_dict["NAME"])
    active_before = digest(active)
    destination = recovery_backup.with_name("bad.sqlite3")
    with pytest.raises(CommandError) as caught:
        call_command("restore_backup", backup=str(recovery_backup), destination=str(destination))
    assert caught.value.returncode == 2
    assert not destination.exists()
    assert digest(recovery_backup) == before
    assert digest(active) == active_before
    assert not list(destination.parent.glob(".cei-*"))


def test_checker_accepts_good_restore_while_active_has_finding(recovery_backup: Path) -> None:
    Workspace.objects.update(timezone_name="Invalid/Zone")
    connection.close()
    assert run_integrity_check().has_blocking_findings
    active = Path(connection.settings_dict["NAME"])
    before = digest(active)
    result = services.restore_sqlite_backup(
        recovery_backup, recovery_backup.with_name("good.sqlite3")
    )
    assert not result.integrity.has_blocking_findings
    assert digest(active) == before


def test_s5_operational_failure_is_exit_three_and_cleans_alias(recovery_backup: Path) -> None:
    # A missing column is a real SQLite failure only when S5 reaches its SQL.
    with closing(sqlite3.connect(recovery_backup)) as database, database:
        database.execute("ALTER TABLE attempts_attempt RENAME COLUMN local_date TO absent_date")
    refresh_manifest(recovery_backup)
    aliases = set(connections.databases)
    before = digest(recovery_backup)
    destination = recovery_backup.with_name("inconclusive.sqlite3")
    with pytest.raises(CommandError) as caught:
        call_command("restore_backup", backup=str(recovery_backup), destination=str(destination))
    assert caught.value.returncode == 3
    assert digest(recovery_backup) == before
    assert set(connections.databases) == aliases
    assert not destination.exists()


def test_wrong_copy_is_rejected_by_reconciliation(recovery_backup: Path, tmp_path: Path) -> None:
    wrong = tmp_path / "other.sqlite3"
    shutil.copyfile(recovery_backup, wrong)
    with closing(sqlite3.connect(wrong)) as database, database:
        database.execute("UPDATE accounts_workspace SET name = 'Outro estado'")
    original_copy = shutil.copyfile

    def copy_wrong(source: Path, destination: Path) -> None:
        del source
        original_copy(wrong, destination)

    with patch("modules.data_management.services.shutil.copyfile", side_effect=copy_wrong):
        with pytest.raises(RestoreError, match="diverge"):
            services.restore_sqlite_backup(recovery_backup, tmp_path / "wrong-restore.sqlite3")
    assert not (tmp_path / "wrong-restore.sqlite3").exists()


def test_invalid_sqlite_with_matching_manifest_is_rejected(recovery_backup: Path) -> None:
    recovery_backup.write_bytes(b"not a SQLite database")
    refresh_manifest(recovery_backup)
    before = digest(recovery_backup)
    active = Path(connection.settings_dict["NAME"])
    active_before = digest(active)
    destination = recovery_backup.with_name("corrupt.sqlite3")
    with pytest.raises(RestoreError, match="rejeitado"):
        services.restore_sqlite_backup(recovery_backup, destination)
    assert not destination.exists()
    assert digest(recovery_backup) == before
    assert digest(active) == active_before


@pytest.mark.parametrize("error", [PermissionError("private"), OSError(28, "private")])
def test_filesystem_failure_is_safe(recovery_backup: Path, error: OSError) -> None:
    before = digest(recovery_backup)
    destination = recovery_backup.with_name("no-space.sqlite3")
    with patch("modules.data_management.services.shutil.copyfile", side_effect=error):
        with pytest.raises(RestoreError) as caught:
            services.restore_sqlite_backup(recovery_backup, destination)
    assert "private" not in str(caught.value)
    assert digest(recovery_backup) == before
    assert not destination.exists()
    assert not list(destination.parent.glob(".cei-*"))


def test_locked_database_aborts_snapshot(tmp_path: Path) -> None:
    source = tmp_path / "locked.sqlite3"
    target = tmp_path / "backup.sqlite3"
    with closing(sqlite3.connect(source)) as writer:
        writer.execute("CREATE TABLE sample (value INTEGER)")
        writer.commit()
        writer.execute("BEGIN EXCLUSIVE")
        with patch.object(services, "_BACKUP_TIMEOUT_SECONDS", 0.05):
            with pytest.raises(BackupCreationError, match="tempo seguro"):
                services._sqlite_backup(source, target)
        writer.rollback()


def test_existing_backup_and_manifest_are_unchanged(recovery_backup: Path) -> None:
    manifest = services.manifest_path_for(recovery_backup)
    before = (digest(recovery_backup), digest(manifest))
    with pytest.raises(BackupCreationError):
        services.create_sqlite_backup(recovery_backup)
    assert (digest(recovery_backup), digest(manifest)) == before


@pytest.mark.parametrize("suffix", ["-wal", "-shm", "-journal"])
def test_artifact_in_use_is_refused_without_touching_sidecars(
    recovery_backup: Path, suffix: str
) -> None:
    sidecar = Path(f"{recovery_backup}{suffix}")
    sidecar.write_bytes(b"private-sentinel")
    before = digest(recovery_backup)
    with pytest.raises(RestoreError, match="rejeitado"):
        services.restore_sqlite_backup(
            recovery_backup, recovery_backup.with_name("refused.sqlite3")
        )
    assert sidecar.read_bytes() == b"private-sentinel"
    assert digest(recovery_backup) == before


def test_sidecar_destination_cannot_be_overwritten(recovery_backup: Path) -> None:
    output = recovery_backup.with_name("new.sqlite3")
    manifest = services.manifest_path_for(output)
    manifest.write_bytes(b"preserve")
    with pytest.raises(BackupCreationError):
        services.create_sqlite_backup(output)
    assert manifest.read_bytes() == b"preserve"
    assert not output.exists()


def test_link_destination_is_refused_before_resolving(tmp_path: Path) -> None:
    destination = tmp_path / "link.sqlite3"
    with patch.object(Path, "is_symlink", return_value=True):
        with pytest.raises(ValueError, match="links"):
            services._resolved_output(destination)
    assert not destination.exists()


def test_failed_publication_preserves_existing_file(recovery_backup: Path) -> None:
    destination = recovery_backup.with_name("race.sqlite3")
    publish = services._publish_new_file

    def competing_publish(temporary: Path, target: Path) -> None:
        target.write_bytes(b"competing-owner")
        publish(temporary, target)

    with patch.object(services, "_publish_new_file", side_effect=competing_publish):
        with pytest.raises(RestoreError):
            services.restore_sqlite_backup(recovery_backup, destination)
    assert destination.read_bytes() == b"competing-owner"
    assert not list(destination.parent.glob(".cei-*"))


def test_missing_file_and_invalid_destination_are_recoverable(tmp_path: Path) -> None:
    with pytest.raises(CommandError, match="Preserve o backup"):
        call_command(
            "restore_backup",
            backup=str(tmp_path / "missing.sqlite3"),
            destination=str(tmp_path / "missing-directory" / "restore.sqlite3"),
        )
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("finding", [False, True])
def test_wal_snapshot_recovers_committed_state_without_leftovers(
    recovery_backup: Path, finding: bool
) -> None:
    active = Path(connection.settings_dict["NAME"])
    output = recovery_backup.with_name("wal-backup.sqlite3")
    restored = recovery_backup.with_name("wal-restored.sqlite3")
    with closing(sqlite3.connect(active, isolation_level=None)) as writer:
        writer.execute("PRAGMA journal_mode=WAL")
        if finding:
            writer.execute("UPDATE attempts_attempt SET local_date = '2000-01-01'")
        writer.execute("BEGIN IMMEDIATE")
        writer.execute("UPDATE accounts_workspace SET name = 'uncommitted'")
        try:
            services.create_sqlite_backup(output)
            if finding:
                with pytest.raises(RestoreError, match="exit 2"):
                    services.restore_sqlite_backup(output, restored)
            else:
                services.restore_sqlite_backup(output, restored)
        finally:
            writer.execute("ROLLBACK")
    if not finding:
        with closing(sqlite3.connect(restored)) as database:
            assert database.execute("SELECT name FROM accounts_workspace").fetchone() != (
                "uncommitted",
            )
    else:
        assert not restored.exists()
    assert not list(output.parent.glob(".cei-*"))


def test_restore_refuses_orphan_sidecars_at_destination(recovery_backup: Path) -> None:
    destination = recovery_backup.with_name("orphan.sqlite3")
    sidecar = Path(f"{destination}-wal")
    sidecar.write_bytes(b"other-owner")
    with pytest.raises(RestoreError):
        services.restore_sqlite_backup(recovery_backup, destination)
    assert sidecar.read_bytes() == b"other-owner"
    assert not destination.exists()
