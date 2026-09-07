"""CT-141: fixture V0.2 explícita, segura e reproduzível."""

from dataclasses import asdict
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import override_settings

from modules.data_management.exceptions import RestoreError
from modules.data_management.services import create_sqlite_backup, restore_sqlite_backup
from modules.questions.fixture import FIXTURE_SEED, FixtureSafetyError, load_v02_fixture
from modules.questions.models import Question, QuestionRevision, QuestionStatus


@pytest.mark.django_db(transaction=True)
def test_ct141_fixture_is_deterministic_idempotent_and_covers_catalog_states() -> None:
    first = load_v02_fixture()
    second = load_v02_fixture(seed=FIXTURE_SEED)

    assert first == second
    assert asdict(first) == {
        "discipline_count": 1,
        "subject_count": 1,
        "subsubject_count": 1,
        "board_count": 1,
        "exam_count": 1,
        "source_count": 1,
        "question_count": 3,
        "revision_count": 3,
        "alternative_count": 12,
        "origin_count": 1,
    }
    assert set(Question.objects.values_list("status", flat=True)) == {
        QuestionStatus.DRAFT,
        QuestionStatus.ACTIVE,
        QuestionStatus.ARCHIVED,
    }
    active = Question.objects.get(status=QuestionStatus.ACTIVE)
    assert active.origin.source is not None
    assert active.origin.exam is not None
    assert list(active.revisions.values_list("version_number", flat=True)) == [1, 2]
    assert QuestionRevision.objects.get(question=active, is_current=True).version_number == 2


@pytest.mark.django_db(transaction=True)
def test_ct141_fixture_command_is_explicit_and_rejects_non_disposable_profiles() -> None:
    call_command("load_v02_fixture", seed=FIXTURE_SEED)

    with override_settings(CEI_PROFILE="development"):
        with pytest.raises(FixtureSafetyError, match="perfil de teste"):
            load_v02_fixture()
        with pytest.raises(CommandError, match="perfil de teste"):
            call_command("load_v02_fixture")

    with pytest.raises(FixtureSafetyError, match="semente documentada"):
        load_v02_fixture(seed="other-seed")


@pytest.mark.django_db(transaction=True)
def test_ct143_backup_restore_reconciles_v02_catalog_and_rejects_corruption(tmp_path: Path) -> None:
    load_v02_fixture()
    backup = tmp_path / "catalog.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    corrupt_destination = tmp_path / "must-not-exist.sqlite3"
    connection.close()

    create_sqlite_backup(backup)
    result = restore_sqlite_backup(backup, restored)

    assert result.reconciliation.discipline_count == 1
    assert result.reconciliation.question_count == 3
    assert result.reconciliation.revision_count == 3
    assert result.reconciliation.alternative_count == 12
    assert result.reconciliation.origin_count == 1
    with backup.open("r+b") as artifact:
        artifact.seek(128)
        original = artifact.read(1)
        artifact.seek(128)
        artifact.write(bytes([original[0] ^ 0xFF]))
    with pytest.raises(RestoreError, match="rejeitado"):
        restore_sqlite_backup(backup, corrupt_destination)
    assert not corrupt_destination.exists()
