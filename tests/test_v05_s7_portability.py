"""CEI-EXPORT-1.0 independent reader, integrity and empty-install round-trip."""

import hashlib
import io
import json
import uuid
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from django.db import connections
from django.db.migrations.executor import MigrationExecutor

from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.attempts.corrections import AttemptCorrectionService
from modules.attempts.models import Attempt
from modules.data_management.portability import (
    ExportValidationError,
    export_bytes,
    export_workspace,
    import_into_empty,
    validate_export,
)
from modules.domain.models import MasteryStateEvent
from modules.questions.corrections import AnswerKeyCorrectionService
from modules.questions.deletion import PermanentQuestionDeletionService
from modules.questions.services import create_active, create_draft
from modules.search.models import SavedFilter
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace


@pytest.fixture
def package(transactional_db: None) -> bytes:
    del transactional_db
    bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Língua portuguesa")
    subject = create_subject(
        workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="Acentuação"
    )
    create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Qual é a opção correta? çã 日本語",
        alternatives=["Errada", "Correta"],
        correct_alternative_position=2,
    )
    return export_bytes(workspace_id=LOCAL_WORKSPACE_ID)


def _independent_reader(data: bytes) -> dict[str, object]:
    """Use stdlib ZIP/JSON only; no ORM or exporter validation helpers."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        assert manifest["format"] == "CEI-EXPORT"
        assert manifest["format_version"] == "1.0"
        for entry in manifest["files"]:
            payload = archive.read(entry["name"])
            assert len(payload) == entry["size_bytes"]
            assert hashlib.sha256(payload).hexdigest() == entry["sha256"]
            if entry["name"].endswith(".json"):
                assert len(json.loads(payload.decode("utf-8"))) == entry["count"]
        return {
            "manifest": manifest,
            "questions": json.loads(archive.read("questions.json").decode("utf-8")),
            "revisions": json.loads(archive.read("question_revisions.json").decode("utf-8")),
        }


def test_ct118_reader_is_independent_and_unicode(package: bytes) -> None:
    result = _independent_reader(package)
    questions = result["questions"]
    revisions = result["revisions"]
    assert isinstance(questions, list) and isinstance(revisions, list)
    assert len(questions) == len(revisions) == 1
    assert revisions[0]["stem"] == "Qual é a opção correta? çã 日本語"
    assert revisions[0]["question"] == questions[0]["id"]
    assert b"SECRET_KEY" not in package
    assert b"password" not in package


def test_ct120_future_version_rejected_without_mutation(package: bytes) -> None:
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    manifest = json.loads(entries["manifest.json"])
    manifest["format_version"] = "9.0"
    entries["manifest.json"] = json.dumps(manifest).encode()
    changed = io.BytesIO()
    with zipfile.ZipFile(changed, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    with pytest.raises(ExportValidationError, match="incompatível"):
        validate_export(io.BytesIO(changed.getvalue()))


def test_invalid_checksum_and_traversal_rejected(package: bytes) -> None:
    with zipfile.ZipFile(io.BytesIO(package)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    entries["questions.json"] += b" "
    changed = io.BytesIO()
    with zipfile.ZipFile(changed, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    with pytest.raises(ExportValidationError, match="INVALID_EXPORT_INTEGRITY"):
        validate_export(io.BytesIO(changed.getvalue()))
    changed = io.BytesIO()
    with zipfile.ZipFile(changed, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
        archive.writestr("../escape", b"x")
    with pytest.raises(ExportValidationError, match="inesperados"):
        validate_export(io.BytesIO(changed.getvalue()))


def test_saved_filter_payload_is_validated_before_import(package: bytes) -> None:
    del package
    SavedFilter.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID,
        owner_user_id=LOCAL_USER_ID,
        name="Filtro",
        name_key="filtro",
        context_code="QUESTIONS_LIST",
        schema_version=1,
        payload={"query": "texto"},
    )
    with zipfile.ZipFile(io.BytesIO(export_bytes(workspace_id=LOCAL_WORKSPACE_ID))) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    filters = json.loads(entries["saved_filters.json"])
    filters[0]["payload"] = ["estrutura indevida"]
    payload = json.dumps(filters, ensure_ascii=False).encode("utf-8")
    entries["saved_filters.json"] = payload
    manifest = json.loads(entries["manifest.json"])
    for item in manifest["files"]:
        if item["name"] == "saved_filters.json":
            item["size_bytes"] = len(payload)
            item["sha256"] = hashlib.sha256(payload).hexdigest()
    entries["manifest.json"] = json.dumps(manifest).encode("utf-8")
    changed = io.BytesIO()
    with zipfile.ZipFile(changed, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    with pytest.raises(ExportValidationError, match="Payload de filtro salvo"):
        validate_export(io.BytesIO(changed.getvalue()))


def test_ct119_round_trip_to_empty_compatible_database(
    package: bytes, tmp_path: Path, django_db_blocker: Any
) -> None:
    validated = validate_export(io.BytesIO(package))
    alias = f"cei_import_{uuid.uuid4().hex}"
    connections.databases[alias] = {
        **connections["default"].settings_dict,
        "NAME": str(tmp_path / "empty.sqlite3"),
    }
    with django_db_blocker.unblock():
        try:
            database = connections[alias]
            executor = MigrationExecutor(database)
            executor.migrate(executor.loader.graph.leaf_nodes())
            counts = import_into_empty(package=validated, database_alias=alias)
            assert counts["questions"] == 1
            assert counts["question_revisions"] == 1
            replay = io.BytesIO()
            export_workspace(
                workspace_id=LOCAL_WORKSPACE_ID, destination=replay, database_alias=alias
            )
            first = _independent_reader(package)
            second = _independent_reader(replay.getvalue())
            assert first["questions"] == second["questions"]
            assert first["revisions"] == second["revisions"]
            with pytest.raises(ExportValidationError, match="merge"):
                import_into_empty(package=validated, database_alias=alias)
        finally:
            connections[alias].close()
            del connections[alias]
            del connections.databases[alias]


def test_s2b_s2c_history_and_saved_filter_survive_round_trip(
    transactional_db: None, tmp_path: Path, django_db_blocker: Any
) -> None:
    del transactional_db
    local = bootstrap_local_workspace(timezone_id="UTC")
    discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Histórico")
    subject = create_subject(
        workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="Correções"
    )
    question = create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Versão original",
        alternatives=["Primeira", "Segunda"],
        correct_alternative_position=2,
    )
    revision = question.revisions.get(is_current=True)
    wrong = revision.alternatives.get(position=1)
    right = revision.alternatives.get(position=2)
    instant = datetime.now(UTC)
    first = Attempt.objects.create(
        workspace=local.workspace,
        question=question,
        question_revision=revision,
        attempt_type="INITIAL",
        selected_alternative=wrong,
        is_correct=False,
        occurred_at=instant,
        timezone_name="UTC",
        local_date=instant.date(),
        idempotency_key=uuid.uuid4(),
    )
    replacement = AttemptCorrectionService(workspace_id=LOCAL_WORKSPACE_ID).replace(
        attempt_id=first.id,
        expected_tip_id=first.id,
        selected_alternative_id=right.id,
        reason_code="SOURCE_EVENT_INVALID",
    )
    AnswerKeyCorrectionService(workspace_id=LOCAL_WORKSPACE_ID).correct(
        question_id=question.id,
        expected_revision_id=revision.id,
        correct_alternative_position=1,
        reason_code="OFFICIAL_KEY_FIX",
    )
    MasteryStateEvent.objects.create(
        workspace=local.workspace,
        question=question,
        sequence=1,
        event_type="DOMINATED",
        formula_code="DOM-HEUR-1.0",
        evaluated_on=instant.date(),
        occurred_at=instant,
    )
    SavedFilter.objects.create(
        workspace=local.workspace,
        owner_user=local.user,
        name="Meu filtro",
        name_key="meu filtro",
        context_code="QUESTIONS_LIST",
        schema_version=1,
        payload={"query": "Versão"},
    )
    raw = export_bytes(workspace_id=LOCAL_WORKSPACE_ID)
    package = validate_export(io.BytesIO(raw))
    assert len(package.rows["attempts"]) == 2
    assert {row["status"] for row in package.rows["attempts"]} == {"VALID", "VOIDED"}
    assert len(package.rows["question_revisions"]) == 2
    assert len(package.rows["saved_filters"]) == 1
    assert len(package.rows["mastery_events"]) == 1
    assert any(row["event_code"] == "ANSWER_KEY_CORRECTED" for row in package.rows["audit_events"])
    alias = f"cei_history_{uuid.uuid4().hex}"
    connections.databases[alias] = {
        **connections["default"].settings_dict,
        "NAME": str(tmp_path / "history.sqlite3"),
    }
    with django_db_blocker.unblock():
        try:
            database = connections[alias]
            executor = MigrationExecutor(database)
            executor.migrate(executor.loader.graph.leaf_nodes())
            import_into_empty(package=package, database_alias=alias)
            replay = io.BytesIO()
            export_workspace(
                workspace_id=LOCAL_WORKSPACE_ID, destination=replay, database_alias=alias
            )
            revalidated = validate_export(io.BytesIO(replay.getvalue()))
            for name in (
                "attempts",
                "question_revisions",
                "audit_events",
                "saved_filters",
                "mastery_events",
            ):
                assert package.rows[name] == revalidated.rows[name]
            assert replacement.replacement_attempt_id in {
                row["id"] for row in revalidated.rows["attempts"]
            }
        finally:
            connections[alias].close()
            del connections[alias]
            del connections.databases[alias]


def test_s2d_deleted_question_does_not_reappear_from_sanitized_audit(
    transactional_db: None,
) -> None:
    del transactional_db
    bootstrap_local_workspace(timezone_id="UTC")
    question = create_draft(
        workspace_id=LOCAL_WORKSPACE_ID,
        draft_title="Remover",
        stem="Conteúdo eliminado",
    )
    removed_id = question.id
    service = PermanentQuestionDeletionService(workspace_id=LOCAL_WORKSPACE_ID)
    preview = service.preview(question_id=removed_id)
    service.delete(
        question_id=removed_id,
        expected_fingerprint=preview.fingerprint,
        confirmation_token=preview.confirmation_token,
        reason_code="USER_REQUEST",
        correlation_id=uuid.uuid4(),
    )
    artifact = export_bytes(workspace_id=LOCAL_WORKSPACE_ID)
    parsed = validate_export(io.BytesIO(artifact))
    assert parsed.rows["questions"] == []
    assert parsed.rows["question_revisions"] == []
    assert parsed.rows["alternatives"] == []
    assert any(
        row["event_code"] == "QUESTION_PERMANENTLY_DELETED" and row["entity_id"] is None
        for row in parsed.rows["audit_events"]
    )
    with zipfile.ZipFile(io.BytesIO(artifact)) as archive:
        functional_bytes = b"".join(archive.read(name) for name in archive.namelist())
    assert str(removed_id).encode() not in functional_bytes
    assert "Conteúdo eliminado".encode() not in functional_bytes
