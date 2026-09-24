"""Fluxos web de gestão autorizados pela V0.5-S3."""

import json
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast
from zoneinfo import ZoneInfo

import pytest
from django import forms
from django.conf import settings
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.accounts.services import LOCAL_USER_ID
from modules.attempts.context import AnswerContext, contexts
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.data_management.exceptions import RestoreError
from modules.errors.models import ErrorCategory, ErrorCategoryState
from modules.errors.services import PersonalCategoryService
from modules.operations.models import AuditEvent, AuditEventCode
from modules.questions.models import Question, QuestionRevision
from modules.questions.services import create_active, create_draft
from modules.reviews.models import Review, ReviewCycle, ReviewCycleState, ReviewState
from modules.search.models import SavedFilter, SavedFilterContext
from modules.search.saved_filter_services import create_saved_filter
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace


def _workspace() -> Workspace:
    return bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace


def _question(workspace: Workspace, *, suffix: str = "") -> Question:
    unique = suffix or uuid.uuid4().hex[:8]
    discipline = create_discipline(
        workspace_id=workspace.id,
        name=f"Disciplina S3 {unique}",
    )
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name=f"Assunto S3 {unique}",
    )
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        draft_title=f"Questão S3 {unique}",
        stem=f"Enunciado S3 {unique}",
        alternatives=["Alternativa incorreta", "Alternativa correta", "Outra"],
        correct_alternative_position=2,
    )


def _attempt(question: Question, *, correct: bool = False) -> Attempt:
    revision = question.revisions.get(is_current=True)
    now = datetime.now(UTC)
    position = 2 if correct else 1
    return Attempt.objects.create(
        workspace=question.workspace,
        question=question,
        question_revision=revision,
        attempt_type=AttemptType.INITIAL,
        selected_alternative=revision.alternatives.get(position=position),
        is_correct=correct,
        occurred_at=now,
        timezone_name=question.workspace.timezone_name,
        local_date=now.astimezone(ZoneInfo(question.workspace.timezone_name)).date(),
        status=AttemptStatus.VALID,
        idempotency_key=uuid.uuid4(),
    )


def _finish_activation(question: Question) -> None:
    completed_at = datetime.now(UTC)
    Review.objects.filter(question=question, state=ReviewState.PENDING).update(
        state=ReviewState.COMPLETED,
        completed_at=completed_at,
    )
    ReviewCycle.objects.filter(question=question, state=ReviewCycleState.ACTIVE).update(
        state=ReviewCycleState.COMPLETED,
        completed_at=completed_at,
    )


def _post_data(form: forms.Form, values: dict[str, object]) -> dict[str, object]:
    return {
        **values,
        **{
            name: form[name].value()
            for name, field in form.fields.items()
            if field.widget.is_hidden
        },
    }


@pytest.mark.django_db(transaction=True)
def test_saved_filter_crud_uses_current_query_without_saving_page() -> None:
    workspace = _workspace()
    question = _question(workspace, suffix="filter")
    client = Client()
    list_url = reverse("questions:list")
    empty = client.get(list_url)
    assert "Nenhum filtro salvo" in empty.content.decode("utf-8")

    payload = {
        "query": "S3 filter",
        "status": "ACTIVE",
        "discipline": "",
        "subject": "",
        "subsubject": "",
        "review_status": "",
        "initial_result": "",
        "error_category": "",
    }
    create_url = reverse("search:create-filter")
    response = client.post(
        create_url, {"name": "  Revisão  atual ", "payload": json.dumps(payload)}
    )
    saved_filter = SavedFilter.objects.get(workspace=workspace, owner_user_id=LOCAL_USER_ID)
    assert response.status_code == 302
    assert saved_filter.name == "Revisão atual"
    assert saved_filter.context_code == SavedFilterContext.QUESTIONS_LIST
    assert "page" not in saved_filter.payload

    duplicate = client.post(create_url, {"name": "REVISÃO ATUAL", "payload": json.dumps(payload)})
    assert duplicate.status_code == 400
    assert SavedFilter.objects.filter(owner_user_id=LOCAL_USER_ID).count() == 1

    apply = client.get(reverse("search:apply-filter", args=[saved_filter.id]))
    assert apply.status_code == 302
    assert (
        apply["Location"]
        == f"{list_url}?query=S3+filter&status=ACTIVE&discipline=&subject=&subsubject=&review_status=&initial_result=&error_category="
    )
    assert client.get(apply["Location"]).context["result"].total == 1
    assert question.id in [
        row.question.id for row in client.get(apply["Location"]).context["result"].page.object_list
    ]

    rename_url = reverse("search:rename-filter", args=[saved_filter.id])
    assert client.get(rename_url).status_code == 200
    renamed = client.post(rename_url, {"name": "Questões ativas"})
    assert renamed.status_code == 302
    saved_filter.refresh_from_db()
    assert saved_filter.name == "Questões ativas"

    delete_url = reverse("search:delete-filter", args=[saved_filter.id])
    assert client.get(delete_url).status_code == 200
    assert SavedFilter.objects.filter(pk=saved_filter.id).exists()
    assert client.post(delete_url, {"confirm": "on"}).status_code == 302
    assert not SavedFilter.objects.filter(pk=saved_filter.id).exists()


@pytest.mark.django_db(transaction=True)
def test_saved_filter_rejects_closed_payload_and_scopes_owner_workspace_and_schema() -> None:
    workspace = _workspace()
    foreign_user = User.objects.create_user(email=f"s3-foreign-{uuid.uuid4()}@example.test")
    foreign_workspace = Workspace.objects.create(
        owner_user=foreign_user,
        name="Outro espaço",
        timezone_name="America/Sao_Paulo",
    )
    payload = {"query": "", "status": "ACTIVE"}
    with pytest.raises(ValueError):
        create_saved_filter(
            workspace_id=workspace.id,
            owner_user_id=foreign_user.id,
            name="inválido",
            payload={**payload, "arbitrary": "value"},
        )
    foreign_discipline = create_discipline(
        workspace_id=foreign_workspace.id,
        name="Disciplina externa",
    )
    with pytest.raises(ValueError):
        create_saved_filter(
            workspace_id=workspace.id,
            owner_user_id=LOCAL_USER_ID,
            name="Taxonomia externa",
            payload={"discipline": str(foreign_discipline.id)},
        )
    incompatible = create_saved_filter(
        workspace_id=workspace.id,
        owner_user_id=LOCAL_USER_ID,
        name="Schema futuro",
        payload=payload,
    )
    incompatible.schema_version = 99
    incompatible.save(update_fields=["schema_version"])
    incompatible_context = create_saved_filter(
        workspace_id=workspace.id,
        owner_user_id=LOCAL_USER_ID,
        name="Contexto futuro",
        payload=payload,
    )
    incompatible_context.context_code = "FUTURE_CONTEXT"
    incompatible_context.save(update_fields=["context_code"])
    foreign_row = SavedFilter.objects.create(
        workspace=foreign_workspace,
        owner_user_id=LOCAL_USER_ID,
        name="Fora do workspace",
        name_key="fora do workspace",
        payload=payload,
    )
    client = Client()
    apply = client.get(reverse("search:apply-filter", args=[incompatible.id]))
    assert apply.status_code == 409
    assert "versão" in apply.content.decode("utf-8").lower()
    context_apply = client.get(reverse("search:apply-filter", args=[incompatible_context.id]))
    assert context_apply.status_code == 409
    assert "contexto" in context_apply.content.decode("utf-8").lower()
    assert client.get(reverse("search:apply-filter", args=[foreign_row.id])).status_code == 404
    listing = client.get(reverse("questions:list"))
    html = listing.content.decode("utf-8")
    assert "Precisa de ajuste" in html
    assert "Aplicar indisponível" in html


@pytest.mark.django_db(transaction=True)
def test_saved_filter_compatibility_queries_do_not_grow_per_saved_filter() -> None:
    workspace = _workspace()
    payload = {"query": "", "status": "ACTIVE"}
    create_saved_filter(
        workspace_id=workspace.id,
        owner_user_id=LOCAL_USER_ID,
        name="Filtro 0",
        payload=payload,
    )
    client = Client()
    with CaptureQueriesContext(connection) as one_filter:
        response = client.get(reverse("questions:list"))
    for index in range(1, 9):
        create_saved_filter(
            workspace_id=workspace.id,
            owner_user_id=LOCAL_USER_ID,
            name=f"Filtro {index}",
            payload=payload,
        )
    with CaptureQueriesContext(connection) as many_filters:
        response = client.get(reverse("questions:list"))
    assert response.status_code == 200
    assert len(many_filters) <= len(one_filter) + 1


@pytest.mark.django_db(transaction=True)
def test_category_ui_calls_personal_lifecycle_and_blocks_standard_category_mutation() -> None:
    workspace = _workspace()
    client = Client()
    empty = client.get(reverse("categories:list")).content.decode("utf-8")
    assert "Nenhuma categoria pessoal foi criada" in empty
    create_url = reverse("categories:create")
    created = client.post(create_url, {"display_name": "Minha categoria"})
    category = ErrorCategory.objects.get(workspace=workspace, display_name="Minha categoria")
    assert created.status_code == 302
    assert client.get(reverse("categories:list")).status_code == 200

    rename_url = reverse("categories:rename", args=[category.id])
    rename_form = client.get(rename_url).context["form"]
    renamed = client.post(
        rename_url,
        _post_data(
            rename_form,
            {"display_name": "Categoria revisada", "reason_code": "CATEGORY_MAINTENANCE"},
        ),
    )
    assert renamed.status_code == 302
    category.refresh_from_db()
    assert category.display_name == "Categoria revisada"

    target = PersonalCategoryService(workspace_id=workspace.id).create(
        display_name="Categoria destino"
    )
    merge_url = reverse("categories:merge", args=[category.id])
    merge_form = client.get(merge_url).context["form"]
    merged = client.post(
        merge_url,
        _post_data(
            merge_form,
            {"target": str(target.id), "reason_code": "CATEGORY_MAINTENANCE", "confirm": "on"},
        ),
    )
    assert merged.status_code == 302
    category.refresh_from_db()
    assert category.state == ErrorCategoryState.MERGED
    assert category.merged_into_id == target.id

    archived = PersonalCategoryService(workspace_id=workspace.id).create(
        display_name="Categoria para arquivar"
    )
    archive_url = reverse("categories:archive", args=[archived.id])
    archive_form = client.get(archive_url).context["form"]
    assert (
        client.post(
            archive_url,
            _post_data(archive_form, {"reason_code": "CATEGORY_MAINTENANCE", "confirm": "on"}),
        ).status_code
        == 302
    )
    archived.refresh_from_db()
    assert archived.state == ErrorCategoryState.ARCHIVED

    standard = ErrorCategory.objects.filter(workspace=workspace, category_kind="STANDARD").first()
    assert standard is not None
    assert client.get(reverse("categories:rename", args=[standard.id])).status_code == 404


@pytest.mark.django_db(transaction=True)
def test_category_stale_lock_and_workspace_scope_are_explicit() -> None:
    workspace = _workspace()
    category = PersonalCategoryService(workspace_id=workspace.id).create(display_name="Concorrente")
    client = Client()
    route = reverse("categories:rename", args=[category.id])
    form = client.get(route).context["form"]
    ErrorCategory.objects.filter(pk=category.id).update(lock_version=category.lock_version + 1)
    response = client.post(
        route,
        _post_data(form, {"display_name": "Nome novo", "reason_code": "CATEGORY_MAINTENANCE"}),
    )
    assert response.status_code == 409
    assert ErrorCategory.objects.get(pk=category.id).display_name == "Concorrente"

    foreign_user = User.objects.create_user(email=f"category-foreign-{uuid.uuid4()}@example.test")
    foreign_workspace = Workspace.objects.create(
        owner_user=foreign_user,
        name="Outro",
        timezone_name="America/Sao_Paulo",
    )
    foreign_category = PersonalCategoryService(workspace_id=foreign_workspace.id).create(
        display_name="Alheia"
    )
    assert client.get(reverse("categories:rename", args=[foreign_category.id])).status_code == 404


@pytest.mark.django_db(transaction=True)
def test_review_manual_inclusion_reschedule_stale_and_csrf() -> None:
    workspace = _workspace()
    empty_queue = Client().get(reverse("reviews:queue")).content.decode("utf-8")
    assert empty_queue.count("Nenhuma") >= 3
    question = _question(workspace, suffix="review")
    initial = _attempt(question, correct=True)
    _finish_activation(question)
    assert (
        initial.workspace_id,
        initial.question_id,
        initial.attempt_type,
        initial.status,
        initial.is_correct,
    ) == (workspace.id, question.id, AttemptType.INITIAL, AttemptStatus.VALID, True)
    assert Attempt.objects.filter(
        workspace_id=workspace.id,
        question=question,
        attempt_type=AttemptType.INITIAL,
        status=AttemptStatus.VALID,
        is_correct=True,
    ).exists()
    client = Client()
    inclusion_url = reverse("reviews:manual-inclusion", args=[question.id])
    inclusion = client.get(inclusion_url)
    assert "nenhuma Attempt será criada ou alterada" in inclusion.content.decode("utf-8")
    response = client.post(
        inclusion_url,
        {"reason_code": "MANUAL_REVIEW_REQUESTED", "confirm": "on"},
    )
    assert response.status_code == 302, response.context["form"].errors
    assert ReviewCycle.objects.filter(question=question, state="ACTIVE").count() == 1
    assert Attempt.objects.filter(pk=initial.id).count() == 1
    review = Review.objects.get(question=question, state="PENDING")

    reschedule_url = reverse("reviews:reschedule", args=[review.id])
    form = client.get(reschedule_url).context["form"]
    target_date = review.current_due_date + timedelta(days=2)
    response = client.post(
        reschedule_url,
        _post_data(
            form,
            {"new_due_date": target_date.isoformat(), "reason_code": "SCHEDULE_ADJUSTMENT"},
        ),
    )
    assert response.status_code == 302
    review.refresh_from_db()
    assert review.current_due_date == target_date

    form = client.get(reschedule_url).context["form"]
    old_version = form["expected_lock_version"].value()
    Review.objects.filter(pk=review.id).update(lock_version=review.lock_version + 1)
    stale = client.post(
        reschedule_url,
        {
            "expected_lock_version": old_version,
            "new_due_date": (target_date + timedelta(days=1)).isoformat(),
            "reason_code": "PERSONAL_COMMITMENT",
        },
    )
    assert stale.status_code == 409

    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.get(inclusion_url)
    denied = csrf_client.post(inclusion_url, {"confirm": "on"})
    assert denied.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_attempt_void_and_replacement_keep_history_and_reject_stale_tip() -> None:
    workspace = _workspace()
    client = Client()
    void_question = _question(workspace, suffix="void")
    voided_candidate = _attempt(void_question)
    preview_url = reverse("attempts:correction-preview", args=[voided_candidate.id])
    preview = client.get(preview_url)
    assert preview.status_code == 200
    assert "Ciclos ativos afetados" in preview.content.decode("utf-8")
    void_url = reverse("attempts:void", args=[voided_candidate.id])
    void_form = client.get(void_url).context["form"]
    void_response = client.post(
        void_url,
        _post_data(void_form, {"reason_code": "DUPLICATE_EVENT", "confirm": "on"}),
    )
    assert void_response.status_code == 302
    voided_candidate.refresh_from_db()
    assert voided_candidate.status == AttemptStatus.VOIDED
    assert Attempt.objects.filter(pk=voided_candidate.id).exists()
    void_timeline = client.get(reverse("reviews:timeline", args=[void_question.id]))
    assert "Corrigir Attempt" not in void_timeline.content.decode("utf-8")

    replace_question = _question(workspace, suffix="replace")
    old_attempt = _attempt(replace_question)
    replace_url = reverse("attempts:replace", args=[old_attempt.id])
    replace_form = client.get(replace_url).context["form"]
    new_alternative = replace_question.revisions.get(is_current=True).alternatives.get(position=3)
    data = _post_data(
        replace_form,
        {
            "selected_alternative": str(new_alternative.id),
            "perceived_ease": "MEDIUM",
            "reason_code": "ANSWER_RECORDED_INCORRECTLY",
            "confirm": "on",
        },
    )
    replaced = client.post(replace_url, data)
    assert replaced.status_code == 302
    old_attempt.refresh_from_db()
    replacement = Attempt.objects.get(replaces_attempt=old_attempt)
    assert old_attempt.status == AttemptStatus.VOIDED
    assert replacement.status == AttemptStatus.VALID
    assert replacement.selected_alternative_id == new_alternative.id
    replacement_timeline = client.get(reverse("reviews:timeline", args=[replace_question.id]))
    timeline_html = replacement_timeline.content.decode("utf-8")
    assert timeline_html.count("Corrigir Attempt") == 1
    assert reverse("attempts:correction-preview", args=[replacement.id]) in timeline_html
    assert reverse("attempts:correction-preview", args=[old_attempt.id]) not in timeline_html

    stale_form = replace_form
    stale_data = _post_data(
        stale_form,
        {
            "selected_alternative": str(new_alternative.id),
            "reason_code": "ANSWER_RECORDED_INCORRECTLY",
            "confirm": "on",
        },
    )
    stale_data.update(data)
    stale_data["correlation_id"] = str(uuid.uuid4())
    stale_data["idempotency_key"] = str(uuid.uuid4())
    stale = client.post(replace_url, stale_data)
    assert stale.status_code == 409
    assert Attempt.objects.filter(question=replace_question).count() == 2


@pytest.mark.django_db(transaction=True)
def test_answer_key_correction_is_prospective_and_stale_revision_is_rejected() -> None:
    workspace = _workspace()
    question = _question(workspace, suffix="answer-key")
    historical_attempt = _attempt(question, correct=True)
    original = question.revisions.get(is_current=True)
    client = Client()
    route = reverse("questions:answer-key-correction", args=[question.id])
    page = client.get(route)
    assert "tentativas futuras" in page.content.decode("utf-8")
    form = page.context["form"]
    response = client.post(
        route,
        _post_data(
            form,
            {
                "correct_alternative_position": "1",
                "reason_code": "ANSWER_KEY_PUBLISHED_INCORRECT",
                "confirm": "on",
            },
        ),
    )
    assert response.status_code == 302
    original.refresh_from_db()
    historical_attempt.refresh_from_db()
    current = question.revisions.get(is_current=True)
    assert current.version_number == 2
    assert not original.is_current
    assert historical_attempt.question_revision_id == original.id

    stale_form = client.get(route).context["form"]
    stale_revision_id = stale_form["expected_revision_id"].value()
    from modules.questions.corrections import AnswerKeyCorrectionService

    AnswerKeyCorrectionService(workspace_id=workspace.id).correct(
        question_id=question.id,
        expected_revision_id=uuid.UUID(str(stale_revision_id)),
        correct_alternative_position=3,
        reason_code="CORRECT_OPTION_MISIDENTIFIED",
    )
    stale = client.post(
        route,
        _post_data(
            stale_form,
            {
                "correct_alternative_position": "1",
                "reason_code": "ANSWER_KEY_PUBLISHED_INCORRECT",
                "confirm": "on",
            },
        ),
    )
    assert stale.status_code == 409
    assert QuestionRevision.objects.filter(question=question).count() == 3
    assert historical_attempt.question_revision_id == original.id


@pytest.mark.django_db(transaction=True)
def test_permanent_delete_ui_blocks_live_context_then_requires_s6_backup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = _workspace()
    client = Client()
    question = _question(workspace, suffix="delete-blocked")
    revision = question.revisions.get(is_current=True)
    context_token = contexts.put(
        AnswerContext(
            actor_id=LOCAL_USER_ID,
            session="s3-delete-blocker",
            workspace_id=workspace.id,
            workspace_version=1,
            question_id=question.id,
            revision_id=revision.id,
            lock_version=question.lock_version,
            alternative_id=revision.alternatives.get(position=1).id,
            is_correct=False,
            evaluated_at=datetime.now(UTC),
            timezone_name=workspace.timezone_name,
        )
    )
    try:
        blocked_url = reverse("questions:permanent-delete-preview", args=[question.id])
        blocked = client.get(blocked_url)
        assert blocked.status_code == 200
        assert "Exclusão bloqueada" in blocked.content.decode("utf-8")
        assert "TRANSIENT_CONTEXT" not in blocked.content.decode("utf-8")
        assert "Excluir definitivamente" not in blocked.content.decode("utf-8")
        preview = blocked.context["preview"]
        forged = client.post(
            blocked_url,
            {
                "expected_fingerprint": preview.fingerprint,
                "confirmation_token": preview.confirmation_token,
                "correlation_id": str(uuid.uuid4()),
                "confirmation_text": preview.confirmation_token,
                "confirm": "on",
                "backup_acknowledgement": "on",
            },
        )
        assert forged.status_code == 409
        assert Question.objects.filter(pk=question.id).exists()
    finally:
        contexts.discard(context_token)

    historical_question = _question(workspace, suffix="delete-history")
    original_attempt = _attempt(historical_question)
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path)
    backup_directory = tmp_path / "backups"
    backup_directory.mkdir()
    delete_url = reverse("questions:permanent-delete-preview", args=[historical_question.id])
    page = client.get(delete_url)
    assert page.context["preview"].eligible
    assert page.context["preview"].backup_required
    assert "backup" in page.content.decode("utf-8").lower()
    form = page.context["form"]
    data = _post_data(
        form,
        {
            "confirmation_text": page.context["preview"].confirmation_token,
            "confirm": "on",
        },
    )
    missing_ack = client.post(delete_url, data)
    assert missing_ack.status_code == 400
    assert Question.objects.filter(pk=historical_question.id).exists()

    data["backup_acknowledgement"] = "on"
    deleted = client.post(delete_url, data)
    assert deleted.status_code == 302
    assert not Question.objects.filter(pk=historical_question.id).exists()
    assert Attempt.objects.filter(pk=original_attempt.id).count() == 0
    assert len(list(backup_directory.glob("pre-delete-*.sqlite3"))) == 1
    assert not list(backup_directory.glob(".s3-delete-restore-*"))
    events = AuditEvent.objects.filter(event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED)
    assert events.count() == 1
    replay = client.post(delete_url, data)
    assert replay.status_code == 404
    assert events.count() == 1


@pytest.mark.django_db(transaction=True)
def test_permanent_delete_ui_rejects_stale_fingerprint_and_foreign_workspace() -> None:
    workspace = _workspace()
    client = Client()
    draft = create_draft(workspace_id=workspace.id, draft_title="Concurrent preview")
    delete_url = reverse("questions:permanent-delete-preview", args=[draft.id])
    page = client.get(delete_url)
    preview = page.context["preview"]
    data = _post_data(
        page.context["form"],
        {
            "confirmation_text": preview.confirmation_token,
            "confirm": "on",
        },
    )
    Question.objects.filter(pk=draft.id).update(draft_title="Changed after preview")
    stale = client.post(delete_url, data)
    assert stale.status_code == 409
    assert Question.objects.filter(pk=draft.id).exists()
    assert not AuditEvent.objects.filter(
        event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED
    ).exists()

    foreign_user = User.objects.create_user(email=f"delete-foreign-{uuid.uuid4()}@example.test")
    foreign_workspace = Workspace.objects.create(
        owner_user=foreign_user,
        name="Foreign workspace",
        timezone_name="America/Sao_Paulo",
    )
    foreign_draft = create_draft(workspace_id=foreign_workspace.id, draft_title="Foreign draft")
    assert (
        client.get(
            reverse("questions:permanent-delete-preview", args=[foreign_draft.id])
        ).status_code
        == 404
    )


@pytest.mark.django_db(transaction=True)
def test_permanent_delete_ui_keeps_aggregate_when_isolated_restore_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = _workspace()
    question = _question(workspace, suffix="restore-failure")
    _attempt(question)
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path)
    backup_directory = tmp_path / "backups"
    backup_directory.mkdir()

    def fail_restore(*_args: object, **_kwargs: object) -> None:
        raise RestoreError("simulated isolated restore failure")

    monkeypatch.setattr("modules.questions.deletion.restore_sqlite_backup", fail_restore)
    client = Client()
    delete_url = reverse("questions:permanent-delete-preview", args=[question.id])
    page = client.get(delete_url)
    preview = page.context["preview"]
    data = _post_data(
        page.context["form"],
        {
            "confirmation_text": preview.confirmation_token,
            "backup_acknowledgement": "on",
            "confirm": "on",
        },
    )

    failed = client.post(delete_url, data)
    assert failed.status_code == 400
    assert failed.context["backup_failure"]
    assert "falhou" in failed.content.decode("utf-8").lower()
    assert Question.objects.filter(pk=question.id).exists()
    assert not AuditEvent.objects.filter(
        event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED
    ).exists()
    assert len(list(backup_directory.glob("pre-delete-*.sqlite3"))) == 1
    assert not list(backup_directory.glob(".s3-delete-restore-*"))


@pytest.mark.django_db(transaction=True)
def test_permanent_delete_ui_reports_committed_delete_when_restore_cleanup_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tempfile import TemporaryDirectory as RealTemporaryDirectory

    workspace = _workspace()
    question = _question(workspace, suffix="cleanup-failure")
    _attempt(question)
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path)
    backup_directory = tmp_path / "backups"
    backup_directory.mkdir()

    class CleanupFailure:
        def __init__(self, **kwargs: Any) -> None:
            self.delegate = RealTemporaryDirectory(**kwargs)

        def __enter__(self) -> str:
            return cast(str, self.delegate.__enter__())

        def __exit__(self, *_args: object) -> None:
            self.delegate.cleanup()
            raise OSError("simulated restore cleanup failure")

    monkeypatch.setattr("modules.questions.views.TemporaryDirectory", CleanupFailure)
    client = Client()
    delete_url = reverse("questions:permanent-delete-preview", args=[question.id])
    page = client.get(delete_url)
    preview = page.context["preview"]
    data = _post_data(
        page.context["form"],
        {
            "confirmation_text": preview.confirmation_token,
            "backup_acknowledgement": "on",
            "confirm": "on",
        },
    )

    completed = client.post(delete_url, data)
    assert completed.status_code == 302
    assert "result=deleted-cleanup-warning" in completed["Location"]
    assert not Question.objects.filter(pk=question.id).exists()
    assert AuditEvent.objects.filter(
        event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED
    ).exists()
    assert len(list(backup_directory.glob("pre-delete-*.sqlite3"))) == 1
    assert not list(backup_directory.glob(".s3-delete-restore-*"))
    feedback = client.get(reverse("questions:list") + "?result=deleted-cleanup-warning")
    assert "A questão foi excluída" in feedback.content.decode("utf-8")
