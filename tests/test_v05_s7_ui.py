"""UI staging, confirmation and backup transport stay outside the active database."""

import hashlib
import io
import json
import shutil
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import cast
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.http import FileResponse
from django.test import Client
from django.urls import reverse

from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.data_management.services import create_sqlite_backup, manifest_path_for
from modules.data_management.ui_services import (
    UIRecoveryError,
    apply_prepared_restore,
    prepare_restore,
    preview_restore,
)
from modules.questions.services import create_active
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace


@pytest.fixture
def live_backup(transactional_db: None, tmp_path: Path) -> Path:
    del transactional_db
    bootstrap_local_workspace(timezone_id="UTC")
    discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Disciplina")
    subject = create_subject(
        workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="Assunto"
    )
    create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Pergunta",
        alternatives=["A", "B"],
        correct_alternative_position=2,
    )
    connection.close()
    backup = tmp_path / "source.sqlite3"
    create_sqlite_backup(backup)
    return backup


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_preview_and_confirm_prepare_preserve_active(live_backup: Path, tmp_path: Path) -> None:
    active = Path(connection.settings_dict["NAME"])
    before = _sha(active)
    manifest = manifest_path_for(live_backup)
    with live_backup.open("rb") as source, manifest.open("rb") as sidecar:
        preview = preview_restore(source, sidecar)
    assert preview.candidate.question_count == 1
    assert _sha(active) == before
    root = tmp_path / "recovery"
    root.mkdir()
    with patch("modules.data_management.ui_services._private_root", return_value=root):
        with live_backup.open("rb") as source, manifest.open("rb") as sidecar:
            ticket = prepare_restore(source, sidecar, expected=preview)
    assert (root / ticket / "candidate.sqlite3").is_file()
    assert (root / f"pre-{ticket}.sqlite3").is_file()
    assert _sha(active) == before


def test_ui_get_read_only_and_downloads_use_distinct_formats(live_backup: Path) -> None:
    active = Path(connection.settings_dict["NAME"])
    before = _sha(active)
    client = Client(enforce_csrf_checks=True)
    url = reverse("data-management:portability")
    response = client.get(url)
    assert response.status_code == 200
    assert b"RESTAU" in response.content.upper()
    assert _sha(active) == before
    csrf = client.cookies["csrftoken"].value
    missing = client.post(url, {"action": "backup"})
    assert missing.status_code == 403
    exported = cast(
        FileResponse, client.post(url, {"action": "export", "csrfmiddlewaretoken": csrf})
    )
    assert exported.status_code == 200
    export_bytes = b"".join(cast(Iterator[bytes], exported.streaming_content))
    exported.close()
    with zipfile.ZipFile(io.BytesIO(export_bytes)) as archive:
        assert "manifest.json" in archive.namelist()
        assert "questions.json" in archive.namelist()
        assert json.loads(archive.read("manifest.json"))["format"] == "CEI-EXPORT"
    backed = cast(FileResponse, client.post(url, {"action": "backup", "csrfmiddlewaretoken": csrf}))
    assert backed.status_code == 200
    backup_bytes = b"".join(cast(Iterator[bytes], backed.streaming_content))
    backed.close()
    with zipfile.ZipFile(io.BytesIO(backup_bytes)) as archive:
        assert set(archive.namelist()) == {"backup.sqlite3", "backup.sqlite3.manifest.json"}
    assert _sha(active) == before


def test_offline_adoption_and_tamper_rejection_use_isolated_active_copy(
    live_backup: Path, tmp_path: Path
) -> None:
    original = Path(connection.settings_dict["NAME"])
    # Add a later fact to the current installation; the uploaded backup is older.
    discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Outra disciplina")
    subject = create_subject(
        workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="Outro assunto"
    )
    create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Nova pergunta",
        alternatives=["A", "B"],
        correct_alternative_position=2,
    )
    connection.close()
    active_copy = tmp_path / "active-copy.sqlite3"
    create_sqlite_backup(active_copy)
    root = tmp_path / "recovery"
    root.mkdir()
    manifest = manifest_path_for(live_backup)
    with (
        patch("modules.data_management.ui_services._private_root", return_value=root),
        patch("modules.data_management.ui_services._database_path", return_value=active_copy),
    ):
        with live_backup.open("rb") as source, manifest.open("rb") as sidecar:
            preview = preview_restore(source, sidecar)
        with live_backup.open("rb") as source, manifest.open("rb") as sidecar:
            ticket = prepare_restore(source, sidecar, expected=preview)
        before = _sha(active_copy)
        candidate = root / ticket / "candidate.sqlite3"
        candidate.write_bytes(candidate.read_bytes() + b"tamper")
        with pytest.raises(UIRecoveryError, match="alterado"):
            apply_prepared_restore(ticket)
        assert _sha(active_copy) == before
        shutil.copyfile(live_backup, candidate)
        with patch(
            "modules.data_management.ui_services._check_restored_integrity",
            side_effect=RuntimeError("injected post-swap failure"),
        ):
            with pytest.raises(UIRecoveryError, match="estado anterior restaurado"):
                apply_prepared_restore(ticket)
        assert _sha(active_copy) == _sha(root / f"pre-{ticket}.sqlite3")
        with live_backup.open("rb") as source, manifest.open("rb") as sidecar:
            second_preview = preview_restore(source, sidecar)
        with live_backup.open("rb") as source, manifest.open("rb") as sidecar:
            ticket = prepare_restore(source, sidecar, expected=second_preview)
        result = apply_prepared_restore(ticket)
        assert result["status"] == "RESTORED"
        assert _sha(active_copy) == _sha(live_backup)
        assert (root / f"pre-{ticket}.sqlite3").is_file()
        assert (root / ticket / "result.json").is_file()
        assert not (root / ticket / "candidate.sqlite3").exists()
    assert original.is_file()


def test_ui_confirmation_requires_preview_phrase_and_reuploaded_pair(
    live_backup: Path, tmp_path: Path
) -> None:
    active = Path(connection.settings_dict["NAME"])
    before = _sha(active)
    client = Client(enforce_csrf_checks=True)
    url = reverse("data-management:portability")
    client.get(url)
    csrf = client.cookies["csrftoken"].value
    manifest = manifest_path_for(live_backup)

    def upload() -> dict[str, object]:
        return {
            "backup": SimpleUploadedFile("../unsafe.sqlite3", live_backup.read_bytes()),
            "manifest": SimpleUploadedFile("C:\\unsafe.json", manifest.read_bytes()),
            "csrfmiddlewaretoken": csrf,
        }

    cancelled = client.post(url, {"action": "cancel", "csrfmiddlewaretoken": csrf})
    assert cancelled.status_code == 200
    assert b"cancelada" in cancelled.content
    invalid = client.post(url, {"action": "confirm", **upload()})
    assert b"RESTAU" in invalid.content.upper()
    assert _sha(active) == before
    preview = client.post(url, {"action": "preview", **upload()})
    assert preview.status_code == 200
    assert b"Contagens atuais e do backup" in preview.content
    token = preview.context["token"]
    root = tmp_path / "recovery"
    root.mkdir()
    with patch("modules.data_management.ui_services._private_root", return_value=root):
        confirmed = client.post(
            url,
            {
                "action": "confirm",
                "token": token,
                "confirmed": "on",
                "confirmation": "RESTAURAR",
                **upload(),
            },
        )
    assert confirmed.status_code == 200
    assert b"Restore preparado" in confirmed.content
    assert len(list(root.glob("*/ticket.json"))) == 1
    assert _sha(active) == before
    ticket = confirmed.context["ticket"]
    with patch("modules.data_management.ui_services._private_root", return_value=root):
        discarded = client.post(
            url,
            {"action": "cancel_prepared", "ticket": ticket, "csrfmiddlewaretoken": csrf},
        )
    assert b"pendente descartado" in discarded.content
    assert not (root / ticket).exists()
    assert not (root / f"pre-{ticket}.sqlite3").exists()
    assert _sha(active) == before
