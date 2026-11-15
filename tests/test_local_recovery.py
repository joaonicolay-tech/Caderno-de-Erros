"""S9: falhas de staging, rollback, drift e versões de backups sintéticos próprios."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from collections.abc import Iterator
from contextlib import closing
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import BinaryIO

import pytest
from django.db import connection, connections

from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.data_management import ui_services as ui
from modules.data_management.services import (
    create_sqlite_backup,
    manifest_path_for,
    restore_sqlite_backup,
)
from modules.operations.integrity import run_integrity_check
from modules.taxonomy.services import create_discipline
from scripts.backup_versions import Version, select_versions
from shared.infrastructure import local_boundary as boundary
from tests.local_fixture import create_fixture
from tests.local_snapshot import snapshot


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def recovery(
    transactional_db: None, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[tuple[Path, Path, Path]]:
    del transactional_db
    # Earlier WAL tests may leave their shared test database in WAL mode.
    # Recover only a dedicated closed copy, never that live shared database.
    previous_name = connection.settings_dict["NAME"]
    empty_backup = tmp_path / "initial-empty.sqlite3"
    create_sqlite_backup(empty_backup)
    active = boundary.sqlite_path(tmp_path / "active.sqlite3")
    with empty_backup.open("rb") as source, active.open("xb") as target:
        shutil.copyfileobj(source, target)
    with closing(sqlite3.connect(active, timeout=5.0)) as database:
        assert database.execute("PRAGMA journal_mode=DELETE").fetchone() == ("delete",)
    assert not any(Path(f"{active}{suffix}").exists() for suffix in ("-wal", "-shm", "-journal"))
    connections.close_all()
    connection.settings_dict["NAME"] = str(active)
    try:
        create_fixture(
            start=datetime(2026, 11, 5, 15, tzinfo=UTC), expected_d1="2026-11-06", secondary=False
        )
        connection.close()
        root = tmp_path / "recovery"
        root.mkdir()
        monkeypatch.setattr(ui, "_private_root", lambda: root)
        backup = tmp_path / "final.sqlite3"
        create_sqlite_backup(backup)
        yield active, backup, root
    finally:
        connections.close_all()
        connection.settings_dict["NAME"] = previous_name


def prepare(backup: Path) -> str:
    with backup.open("rb") as source, manifest_path_for(backup).open("rb") as manifest:
        preview = ui.preview_restore(source, manifest)
    with backup.open("rb") as source, manifest_path_for(backup).open("rb") as manifest:
        return ui.prepare_restore(source, manifest, expected=preview)


def test_staging_permission_error_preserves_active(
    recovery: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    active, backup, _ = recovery
    before = sha(active)
    with backup.open("rb") as source, manifest_path_for(backup).open("rb") as manifest:
        preview = ui.preview_restore(source, manifest)

    def denied(source: BinaryIO, target: Path) -> None:
        del source, target
        raise PermissionError("injected synthetic staging denial")

    monkeypatch.setattr(ui, "_stream_copy", denied)
    with backup.open("rb") as source, manifest_path_for(backup).open("rb") as manifest:
        with pytest.raises(ui.UIRecoveryError, match="destino não foi alterado"):
            ui.prepare_restore(source, manifest, expected=preview)
    assert sha(active) == before


def test_active_drift_after_preview_rejects_confirmation(recovery: tuple[Path, Path, Path]) -> None:
    active, backup, _ = recovery
    with backup.open("rb") as source, manifest_path_for(backup).open("rb") as manifest:
        preview = ui.preview_restore(source, manifest)
    create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Fato sintético posterior ao preview")
    connection.close()
    before = sha(active)
    with backup.open("rb") as source, manifest_path_for(backup).open("rb") as manifest:
        with pytest.raises(ui.UIRecoveryError, match="estado atual mudou"):
            ui.prepare_restore(source, manifest, expected=preview)
    assert sha(active) == before


def test_staging_copy_failure_preserves_return_pair(
    recovery: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    active, backup, root = recovery
    ticket = prepare(backup)
    before = sha(active)
    prebackup = root / f"pre-{ticket}.sqlite3"
    prebackup_before = sha(prebackup)
    expected_state = snapshot(active)
    original = shutil.copyfile

    def interrupted(
        source: str | Path, destination: str | Path, *, follow_symlinks: bool = True
    ) -> str | Path:
        if Path(destination).name.startswith(".cei-adopt-"):
            raise OSError("injected interrupted staging write")
        return original(source, destination, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(shutil, "copyfile", interrupted)
    with pytest.raises(OSError, match="interrupted staging"):
        ui.apply_prepared_restore(ticket)
    assert sha(active) == before
    assert sha(prebackup) == prebackup_before
    assert snapshot(prebackup) == expected_state
    assert not (root / ticket / "result.json").exists()


def test_apply_refuses_sidecar_and_preserves_preimage(recovery: tuple[Path, Path, Path]) -> None:
    active, backup, root = recovery
    ticket = prepare(backup)
    before = sha(active)
    sidecar = Path(f"{active}-journal")
    sidecar.write_bytes(b"GENERATED_SYNTHETIC_ORPHAN")
    try:
        with pytest.raises(ui.UIRecoveryError):
            ui.apply_prepared_restore(ticket)
        assert sha(active) == before
        assert (root / f"pre-{ticket}.sqlite3").is_file()
    finally:
        sidecar.unlink()


def test_post_swap_checker_finding_restores_complete_prebackup(
    recovery: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    active, backup, root = recovery
    checked = run_integrity_check()
    assert checked.total_findings == 0
    connection.close()
    ticket = prepare(backup)
    before = snapshot(active)
    prebackup = root / f"pre-{ticket}.sqlite3"
    prebackup_hash = sha(prebackup)
    monkeypatch.setattr(
        ui, "_check_restored_integrity", lambda path: replace(checked, total_findings=1)
    )
    with pytest.raises(ui.UIRecoveryError, match="estado anterior restaurado"):
        ui.apply_prepared_restore(ticket)
    assert snapshot(active) == before
    assert sha(prebackup) == prebackup_hash
    assert not (root / ticket / "result.json").exists()


def test_native_hardlinked_ticket_candidate_is_refused_before_apply(
    recovery: tuple[Path, Path, Path], tmp_path: Path
) -> None:
    active, backup, root = recovery
    ticket = prepare(backup)
    before = sha(active)
    alias = tmp_path / "own-synthetic-alias.sqlite3"
    os.link(root / ticket / "candidate.sqlite3", alias)
    try:
        with pytest.raises(boundary.BoundaryError, match="hardlink"):
            ui.apply_prepared_restore(ticket)
        assert sha(active) == before
        assert not (root / ticket / "result.json").exists()
    finally:
        alias.unlink()


def test_daily_weekly_selection_and_earlier_real_restore(
    recovery: tuple[Path, Path, Path], tmp_path: Path
) -> None:
    active, _, _ = recovery
    now = datetime(2026, 12, 7, 15, tzinfo=UTC)
    offsets = [*range(7), 7, 14, 21, 28]
    versions: list[Version] = []
    before = snapshot(active)
    for index, offset in enumerate(offsets):
        instant = now - timedelta(days=offset)
        name = f"version-{index:02}.sqlite3"

        def injected_clock(value: datetime = instant) -> datetime:
            return value

        create_sqlite_backup(tmp_path / name, now=injected_clock)
        versions.append(Version(name, instant))
    selected = select_versions(versions, now=now)
    assert selected["daily"] == [f"version-{i:02}.sqlite3" for i in range(7)]
    assert selected["weekly"] == [f"version-{i:02}.sqlite3" for i in (1, 8, 9, 10)]
    # Monday's previous week includes the six recent daily copies; keep both designations.
    restored = tmp_path / "earlier-restored.sqlite3"
    result = restore_sqlite_backup(tmp_path / selected["weekly"][-1], restored)
    assert result.integrity.total_findings == 0
    assert result.integrity.total_limited_verifications == 4
    assert snapshot(restored) == before
    assert snapshot(active) == before
    assert len(selected["preserved"]) == 11


@pytest.mark.parametrize(
    "value",
    [
        r"C:\outside-synthetic.sqlite3",
        "../outside.sqlite3",
        "validation/../outside.sqlite3",
        "validation//bad.sqlite3",
        "validation/data.txt",
    ],
)
def test_marker_database_slot_rejects_before_target_io(
    value: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(boundary, "marker", lambda: {"database_slot": value})

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("Rejected marker path reached native admission")

    monkeypatch.setattr(boundary, "admit", forbidden)
    with pytest.raises(boundary.BoundaryError):
        boundary.database_path(test=False)


@pytest.mark.parametrize(
    "field",
    [
        "ticket",
        "active_path",
        "active_fingerprint",
        "candidate_sha256",
        "prebackup_sha256",
        "candidate_counts",
        "authorization",
        "unexpected_field",
    ],
)
def test_signed_ticket_metadata_tamper_is_rejected_before_mutation(
    recovery: tuple[Path, Path, Path], monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    active, backup, root = recovery
    ticket = prepare(backup)
    before = sha(active)
    path = root / ticket / "ticket.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document[field] = {"question_count": 999} if field == "candidate_counts" else "SYNTHETIC_TAMPER"
    path.write_text(json.dumps(document), encoding="utf-8")

    def forbidden_active(*args: object, **kwargs: object) -> Path:
        raise AssertionError("Tampered ticket reached active database lookup")

    monkeypatch.setattr(ui, "_database_path", forbidden_active)
    with pytest.raises(ui.UIRecoveryError, match="Ticket"):
        ui.apply_prepared_restore(ticket)
    assert sha(active) == before
    assert not (root / ticket / "result.json").exists()


def test_ticket_from_different_instance_secret_is_rejected(
    recovery: tuple[Path, Path, Path],
) -> None:
    import secrets

    from django.test import override_settings

    active, backup, _ = recovery
    ticket = prepare(backup)
    before = sha(active)
    with override_settings(SECRET_KEY=secrets.token_urlsafe(64), SECRET_KEY_FALLBACKS=[]):
        with pytest.raises(ui.UIRecoveryError, match="Ticket adulterado"):
            ui.apply_prepared_restore(ticket)
    assert sha(active) == before
