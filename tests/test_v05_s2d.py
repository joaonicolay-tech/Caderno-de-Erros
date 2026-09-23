"""Exclusão S2D: preview, transação, auditoria e retenção."""

import sqlite3
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Barrier, Event
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError
from django.db import DatabaseError, close_old_connections, models

from modules.accounts.models import User, Workspace
from modules.analytics.services import AnalyticsService
from modules.attempts.context import AnswerContext, ContextStore
from modules.attempts.corrections import AttemptCorrectionService
from modules.attempts.models import Attempt, AttemptType, OperationKind, OperationReceipt
from modules.data_management.services import create_sqlite_backup, restore_sqlite_backup
from modules.errors.models import ErrorCategory, ErrorClassification, ErrorClassificationRevision
from modules.errors.services import PersonalCategoryService
from modules.operations.integrity import run_integrity_check
from modules.operations.models import AuditEvent, AuditEventCode
from modules.operations.retention import purge_expired_question_deletion_events
from modules.questions.corrections import AnswerKeyCorrectionService
from modules.questions.deletion import (
    PermanentDeletionConflictError,
    PermanentQuestionDeletionService,
)
from modules.questions.models import Alternative, Question, QuestionRevision
from modules.questions.services import create_active, create_draft
from modules.reviews.models import Review, ReviewCycle, ReviewScheduleChange, ReviewState
from modules.reviews.services import ReviewScheduleService
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant


def _workspace() -> Workspace:
    user = User.objects.create_user(email=f"s2d-{uuid.uuid4()}@example.test")
    return Workspace.objects.create(
        owner_user=user,
        name="S2D",
        timezone_name="America/Sao_Paulo",
    )


@pytest.mark.django_db(transaction=True)
def test_simple_draft_preview_delete_and_sanitized_event() -> None:
    workspace = _workspace()
    question = create_draft(
        workspace_id=workspace.id,
        draft_title="temporário",
        stem="texto privado",
        alternatives=["errada", "certa"],
        correct_alternative_position=2,
    )
    another = create_draft(workspace_id=workspace.id, draft_title="preservada")
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    before = service.preview(question_id=question.id)
    assert before.eligible and not before.backup_required
    assert dict(before.impact)["revisions"] == 1
    assert dict(before.impact)["alternatives"] == 2
    assert Question.objects.filter(pk=question.id).exists()

    result = service.delete(
        question_id=question.id,
        expected_fingerprint=before.fingerprint,
        confirmation_token=before.confirmation_token,
        reason_code="USER_REQUEST",
        correlation_id=uuid.uuid4(),
    )
    assert not Question.objects.filter(pk=question.id).exists()
    assert Question.objects.filter(pk=another.id).exists()
    assert not QuestionRevision.objects.filter(question_id=question.id).exists()
    assert not Alternative.objects.filter(question_revision__question_id=question.id).exists()
    assert not Attempt.objects.filter(question_id=question.id).exists()
    event = AuditEvent.objects.get(pk=result.audit_event_id)
    assert event.event_code == AuditEventCode.QUESTION_PERMANENTLY_DELETED
    assert event.workspace_id == workspace.id
    assert event.entity_id is None and event.related_entity_id is None
    assert event.reason_code == "USER_REQUEST"
    assert "texto privado" not in str(event)
    with pytest.raises(PermanentDeletionConflictError):
        service.delete(
            question_id=question.id,
            expected_fingerprint=before.fingerprint,
            confirmation_token=before.confirmation_token,
            reason_code="USER_REQUEST",
            correlation_id=uuid.uuid4(),
        )


@pytest.mark.django_db(transaction=True)
def test_stale_preview_and_fault_leave_draft_unchanged() -> None:
    workspace = _workspace()
    question = create_draft(workspace_id=workspace.id, draft_title="rascunho")
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    preview = service.preview(question_id=question.id)
    Question.objects.filter(pk=question.id).update(lock_version=models.F("lock_version") + 1)
    with pytest.raises(PermanentDeletionConflictError):
        service.delete(
            question_id=question.id,
            expected_fingerprint=preview.fingerprint,
            confirmation_token=preview.confirmation_token,
            reason_code="USER_REQUEST",
            correlation_id=uuid.uuid4(),
        )
    current = service.preview(question_id=question.id)

    def fail(point: str) -> None:
        if point == "after_audit":
            raise RuntimeError("fault")

    with pytest.raises(RuntimeError, match="fault"):
        service.delete(
            question_id=question.id,
            expected_fingerprint=current.fingerprint,
            confirmation_token=current.confirmation_token,
            reason_code="USER_REQUEST",
            correlation_id=uuid.uuid4(),
            fault_hook=fail,
        )
    assert Question.objects.filter(pk=question.id).exists()
    assert not AuditEvent.objects.filter(
        event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED
    ).exists()


@pytest.mark.django_db(transaction=True)
def test_content_change_without_version_bump_invalidates_preview() -> None:
    workspace = _workspace()
    question = create_draft(
        workspace_id=workspace.id,
        draft_title="rascunho",
        stem="conteudo original",
    )
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    preview = service.preview(question_id=question.id)
    Question.objects.filter(pk=question.id).update(draft_title="titulo alterado")

    with pytest.raises(PermanentDeletionConflictError, match="Preview obsoleto"):
        service.delete(
            question_id=question.id,
            expected_fingerprint=preview.fingerprint,
            confirmation_token=preview.confirmation_token,
            reason_code="USER_REQUEST",
            correlation_id=uuid.uuid4(),
        )
    assert Question.objects.filter(pk=question.id).exists()


@pytest.mark.django_db(transaction=True)
def test_audit_metadata_cannot_retain_aggregate_identifier() -> None:
    workspace = _workspace()
    question = create_draft(workspace_id=workspace.id, draft_title="rascunho")
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    preview = service.preview(question_id=question.id)

    for correlation_id, reason_code in (
        (question.id, "USER_REQUEST"),
        (uuid.uuid4(), f"Q_{question.id.hex.upper()}"),
    ):
        with pytest.raises(PermanentDeletionConflictError, match="ID do agregado"):
            service.delete(
                question_id=question.id,
                expected_fingerprint=preview.fingerprint,
                confirmation_token=preview.confirmation_token,
                reason_code=reason_code,
                correlation_id=correlation_id,
            )
    assert Question.objects.filter(pk=question.id).exists()
    assert not AuditEvent.objects.filter(
        event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED
    ).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "point",
    [
        "after_lock",
        "after_first_dependency",
        "middle_delete",
        "before_reconciliation",
        "after_reconciliation",
        "before_audit",
        "after_audit",
    ],
)
def test_fault_injection_rolls_back_entire_draft_aggregate(point: str) -> None:
    workspace = _workspace()
    question = create_draft(
        workspace_id=workspace.id,
        draft_title="falha",
        stem="conteúdo",
        alternatives=["A", "B"],
        correct_alternative_position=2,
    )
    revision = question.revisions.get()
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    preview = service.preview(question_id=question.id)

    def fail(reached: str) -> None:
        if reached == point:
            raise RuntimeError("injected")

    with pytest.raises(RuntimeError, match="injected"):
        service.delete(
            question_id=question.id,
            expected_fingerprint=preview.fingerprint,
            confirmation_token=preview.confirmation_token,
            reason_code="USER_REQUEST",
            correlation_id=uuid.uuid4(),
            fault_hook=fail,
        )
    assert service.preview(question_id=question.id) == preview
    assert QuestionRevision.objects.filter(pk=revision.id).exists()
    assert Alternative.objects.filter(question_revision_id=revision.id).count() == 2
    assert not AuditEvent.objects.filter(
        event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED
    ).exists()


@pytest.mark.django_db(transaction=True)
def test_wrong_workspace_cross_reference_and_live_context_block_preview() -> None:
    owner = _workspace()
    foreign = _workspace()
    question = create_draft(workspace_id=owner.id, draft_title="isolada")
    assert (
        not PermanentQuestionDeletionService(workspace_id=foreign.id)
        .preview(question_id=question.id)
        .eligible
    )
    store = ContextStore()
    now = datetime(2026, 9, 23, 12, tzinfo=UTC)
    store.put(
        AnswerContext(
            actor_id=owner.owner_user_id,
            session="session",
            workspace_id=owner.id,
            workspace_version=1,
            question_id=question.id,
            revision_id=uuid.uuid4(),
            lock_version=question.lock_version,
            alternative_id=uuid.uuid4(),
            is_correct=False,
            evaluated_at=now,
            timezone_name=owner.timezone_name,
        )
    )
    active = PermanentQuestionDeletionService(
        workspace_id=owner.id,
        clock=FixedClock(Instant(now)),
        context_store=store,
    )
    assert "TRANSIENT_CONTEXT" in active.preview(question_id=question.id).blockers
    expired = PermanentQuestionDeletionService(
        workspace_id=owner.id,
        clock=FixedClock(Instant(now + timedelta(minutes=15))),
        context_store=store,
    )
    assert expired.preview(question_id=question.id).eligible

    revision = create_draft(
        workspace_id=owner.id, draft_title="com revisão", stem="texto"
    ).revisions.get()
    models.QuerySet.update(QuestionRevision.objects.filter(pk=revision.id), workspace_id=foreign.id)
    assert (
        "CROSS_WORKSPACE_REFERENCE"
        in PermanentQuestionDeletionService(workspace_id=owner.id)
        .preview(question_id=revision.question_id)
        .blockers
    )


@pytest.mark.django_db(transaction=True)
def test_two_concurrent_deletes_have_one_winner_and_one_final_event() -> None:
    workspace = _workspace()
    question = create_draft(workspace_id=workspace.id, draft_title="concorrente")
    preview = PermanentQuestionDeletionService(workspace_id=workspace.id).preview(
        question_id=question.id
    )
    barrier = Barrier(2)

    def contender() -> bool:
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            PermanentQuestionDeletionService(workspace_id=workspace.id).delete(
                question_id=question.id,
                expected_fingerprint=preview.fingerprint,
                confirmation_token=preview.confirmation_token,
                reason_code="USER_REQUEST",
                correlation_id=uuid.uuid4(),
            )
            return True
        except PermanentDeletionConflictError:
            return False
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: contender(), range(2)))
    assert sorted(outcomes) == [False, True]
    assert (
        AuditEvent.objects.filter(event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED).count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("mutation", ["attempt", "s2b", "s2c", "review"])
def test_delete_serializes_concurrent_writers(mutation: str, tmp_path: Path) -> None:
    workspace = bootstrap_local_workspace(timezone_id="UTC").workspace
    discipline = create_discipline(workspace_id=workspace.id, name="Concorrência")
    subject = create_subject(
        workspace_id=workspace.id, discipline_id=discipline.id, name="Concorrência"
    )
    question = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Interleaving",
        alternatives=["A", "B"],
        correct_alternative_position=2,
    )
    revision = question.revisions.get(is_current=True)
    alternative = revision.alternatives.get(position=2)
    now = datetime.now(UTC)
    initial = Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        attempt_type=AttemptType.INITIAL,
        selected_alternative=alternative,
        is_correct=True,
        occurred_at=now,
        timezone_name="UTC",
        local_date=now.date(),
        idempotency_key=uuid.uuid4(),
    )
    pending = Review.objects.filter(question_id=question.id, state=ReviewState.PENDING).first()
    assert pending is not None
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    preview = service.preview(question_id=question.id)
    started = Event()
    began = Event()

    def writer() -> bool:
        close_old_connections()
        try:
            if not started.wait(timeout=15):
                return False
            began.set()
            if mutation == "attempt":
                Attempt.objects.create(
                    workspace=workspace,
                    question=question,
                    question_revision=revision,
                    attempt_type=AttemptType.REVIEW,
                    review=pending,
                    selected_alternative=alternative,
                    is_correct=True,
                    occurred_at=now,
                    timezone_name="UTC",
                    local_date=now.date(),
                    idempotency_key=uuid.uuid4(),
                )
            elif mutation == "s2b":
                AttemptCorrectionService(workspace_id=workspace.id).replace(
                    attempt_id=initial.id,
                    expected_tip_id=initial.id,
                    selected_alternative_id=alternative.id,
                    reason_code="RACE_FIX",
                )
            elif mutation == "s2c":
                AnswerKeyCorrectionService(workspace_id=workspace.id).correct(
                    question_id=question.id,
                    expected_revision_id=revision.id,
                    correct_alternative_position=1,
                    reason_code="RACE_KEY_FIX",
                )
            else:
                ReviewScheduleService(workspace_id=workspace.id).reschedule(
                    review_id=pending.id,
                    new_due_date=now.date() + timedelta(days=10),
                    reason_code="RACE_RESCHEDULE",
                    expected_lock_version=pending.lock_version,
                )
            return True
        except (DatabaseError, ValidationError, RuntimeError, ValueError):
            return False
        finally:
            close_old_connections()

    def release_writer(point: str) -> None:
        if point == "after_lock":
            started.set()
            assert began.wait(timeout=10)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(writer)
        service.delete(
            question_id=question.id,
            expected_fingerprint=preview.fingerprint,
            confirmation_token=preview.confirmation_token,
            reason_code="USER_REQUEST",
            correlation_id=uuid.uuid4(),
            backup_path=tmp_path / "pre.sqlite3",
            isolated_restore_path=tmp_path / "isolated.sqlite3",
            fault_hook=release_writer,
        )
        assert not future.result(timeout=15)
    assert not Question.objects.filter(pk=question.id).exists()
    assert not Attempt.objects.filter(question_id=question.id).exists()
    assert not run_integrity_check().has_blocking_findings


@pytest.mark.django_db(transaction=True)
def test_purge_exact_utc_boundary_and_idempotency() -> None:
    workspace = _workspace()
    question = create_draft(workspace_id=workspace.id, draft_title="prazo")
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    preview = service.preview(question_id=question.id)
    result = service.delete(
        question_id=question.id,
        expected_fingerprint=preview.fingerprint,
        confirmation_token=preview.confirmation_token,
        reason_code="USER_REQUEST",
        correlation_id=uuid.uuid4(),
    )
    created = datetime(2026, 1, 1, 12, tzinfo=UTC)
    models.QuerySet.update(AuditEvent.objects.filter(pk=result.audit_event_id), created_at=created)
    unrelated = AuditEvent.objects.create(
        workspace=workspace,
        event_code=AuditEventCode.MANUAL_REVIEW_INCLUDED,
        entity_type="REVIEW_CYCLE",
        entity_id=uuid.uuid4(),
        correlation_id=uuid.uuid4(),
    )
    models.QuerySet.update(AuditEvent.objects.filter(pk=unrelated.id), created_at=created)
    boundary = created + timedelta(days=90)
    assert purge_expired_question_deletion_events(now=boundary - timedelta(microseconds=1)) == 0
    assert purge_expired_question_deletion_events(now=boundary) == 1
    assert purge_expired_question_deletion_events(now=boundary) == 0
    assert AuditEvent.objects.filter(pk=unrelated.id).exists()


@pytest.mark.django_db(transaction=True)
def test_historical_question_requires_retention_and_real_s6_restore(tmp_path: Path) -> None:
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    discipline = create_discipline(workspace_id=workspace.id, name="Disciplina")
    subject = create_subject(workspace_id=workspace.id, discipline_id=discipline.id, name="Assunto")
    question = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Conteúdo a recuperar",
        alternatives=["não", "sim"],
        correct_alternative_position=2,
    )
    revision = question.revisions.get(is_current=True)
    now = datetime.now(UTC)
    key = uuid.uuid4()
    attempt = Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        attempt_type=AttemptType.INITIAL,
        selected_alternative=revision.alternatives.get(position=2),
        is_correct=True,
        occurred_at=now,
        timezone_name=workspace.timezone_name,
        local_date=now.astimezone(ZoneInfo(workspace.timezone_name)).date(),
        idempotency_key=key,
    )
    receipt = OperationReceipt.objects.create(
        workspace=workspace,
        operation_kind=OperationKind.INITIAL_CORRECT,
        idempotency_key=key,
        request_hash="a" * 64,
        result_entity_type="ATTEMPT",
        result_entity_id=attempt.id,
    )
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    blocked = service.preview(question_id=question.id)
    assert "RECEIPT_RETENTION" in blocked.blockers
    boundary = PermanentQuestionDeletionService(
        workspace_id=workspace.id, clock=FixedClock(Instant(now))
    )
    models.QuerySet.update(
        OperationReceipt.objects.filter(pk=receipt.id),
        created_at=now - timedelta(days=30) + timedelta(microseconds=1),
    )
    assert "RECEIPT_RETENTION" in boundary.preview(question_id=question.id).blockers
    models.QuerySet.update(
        OperationReceipt.objects.filter(pk=receipt.id), created_at=now - timedelta(days=30)
    )
    assert "RECEIPT_RETENTION" not in boundary.preview(question_id=question.id).blockers
    models.QuerySet.update(
        OperationReceipt.objects.filter(pk=receipt.id),
        created_at=now - timedelta(days=31),
    )
    first = AttemptCorrectionService(workspace_id=workspace.id).replace(
        attempt_id=attempt.id,
        expected_tip_id=attempt.id,
        selected_alternative_id=revision.alternatives.get(position=1).id,
        reason_code="ENTRY_FIX",
    )
    assert first.replacement_attempt_id is not None
    second = AttemptCorrectionService(workspace_id=workspace.id).replace(
        attempt_id=first.replacement_attempt_id,
        expected_tip_id=first.replacement_attempt_id,
        selected_alternative_id=revision.alternatives.get(position=2).id,
        reason_code="SECOND_FIX",
    )
    assert second.replacement_attempt_id is not None
    corrected = AnswerKeyCorrectionService(workspace_id=workspace.id).correct(
        question_id=question.id,
        expected_revision_id=revision.id,
        correct_alternative_position=1,
        reason_code="KEY_FIX",
    )
    AnswerKeyCorrectionService(workspace_id=workspace.id).correct(
        question_id=question.id,
        expected_revision_id=corrected.new_revision_id,
        correct_alternative_position=2,
        reason_code="KEY_FIX_AGAIN",
    )
    pending = Review.objects.filter(question_id=question.id, state=ReviewState.PENDING).first()
    assert pending is not None
    ReviewScheduleService(workspace_id=workspace.id).reschedule(
        review_id=pending.id,
        new_due_date=now.astimezone(ZoneInfo(workspace.timezone_name)).date() + timedelta(days=10),
        reason_code="USER_RESCHEDULE",
        expected_lock_version=pending.lock_version,
    )
    preview = service.preview(question_id=question.id)
    assert preview.eligible and preview.backup_required
    assert dict(preview.impact)["revisions"] == 3
    assert dict(preview.impact)["attempts"] == 3
    assert dict(preview.impact)["audit_events"] >= 6
    assert dict(preview.impact)["cycles"] >= 1
    assert dict(preview.impact)["schedule_changes"] == 1
    assert AnalyticsService(workspace_id=workspace.id).registered_questions().count() == 1
    assert AnalyticsService(workspace_id=workspace.id).performed_questions().count() == 1
    backup = tmp_path / "pre-delete.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    result = service.delete(
        question_id=question.id,
        expected_fingerprint=preview.fingerprint,
        confirmation_token=preview.confirmation_token,
        reason_code="USER_REQUEST",
        correlation_id=uuid.uuid4(),
        backup_path=backup,
        isolated_restore_path=restored,
    )
    assert result.backup_path == backup
    assert backup.exists() and restored.exists()
    assert not Question.objects.filter(pk=question.id).exists()
    assert not OperationReceipt.objects.filter(pk=receipt.id).exists()
    assert not AuditEvent.objects.filter(entity_id__in={question.id, attempt.id}).exists()
    assert not ReviewCycle.objects.filter(question_id=question.id).exists()
    assert not Review.objects.filter(question_id=question.id).exists()
    assert not ReviewScheduleChange.objects.filter(review__question_id=question.id).exists()
    assert AnalyticsService(workspace_id=workspace.id).registered_questions().count() == 0
    assert AnalyticsService(workspace_id=workspace.id).performed_questions().count() == 0
    assert Question.objects.filter(pk=question.id).count() == 0
    with sqlite3.connect(restored) as database:
        assert database.execute(
            "SELECT count(*) FROM questions_question WHERE id = ?", (question.id.hex,)
        ).fetchone() == (1,)
    assert not run_integrity_check().has_blocking_findings
    post = tmp_path / "post-delete.sqlite3"
    post_restored = tmp_path / "post-restored.sqlite3"
    create_sqlite_backup(post)
    assert not restore_sqlite_backup(post, post_restored).integrity.has_blocking_findings
    with sqlite3.connect(post_restored) as database:
        assert database.execute(
            "SELECT count(*) FROM questions_question WHERE id = ?", (question.id.hex,)
        ).fetchone() == (0,)


@pytest.mark.django_db(transaction=True)
def test_shared_personal_categories_taxonomy_and_other_question_survive(tmp_path: Path) -> None:
    workspace = bootstrap_local_workspace(timezone_id="UTC").workspace
    discipline = create_discipline(workspace_id=workspace.id, name="Compartilhada")
    subject = create_subject(
        workspace_id=workspace.id, discipline_id=discipline.id, name="Compartilhado"
    )
    categories = PersonalCategoryService(workspace_id=workspace.id)
    source = categories.create(display_name="Origem pessoal")
    target = categories.create(display_name="Destino pessoal")
    created: list[Question] = []
    now = datetime.now(UTC)
    for index in range(2):
        question = create_active(
            workspace_id=workspace.id,
            discipline_id=discipline.id,
            subject_id=subject.id,
            stem=f"Questão {index}",
            alternatives=["erro", "acerto"],
            correct_alternative_position=2,
        )
        revision = question.revisions.get(is_current=True)
        attempt = Attempt.objects.create(
            workspace=workspace,
            question=question,
            question_revision=revision,
            attempt_type=AttemptType.INITIAL,
            selected_alternative=revision.alternatives.get(position=1),
            is_correct=False,
            occurred_at=now,
            timezone_name="UTC",
            local_date=now.date(),
            idempotency_key=uuid.uuid4(),
        )
        classification = ErrorClassification.objects.create(
            workspace=workspace, attempt=attempt, category=source
        )
        ErrorClassificationRevision.objects.create(
            workspace=workspace,
            error_classification=classification,
            revision_number=1,
            category=source,
        )
        created.append(question)
    categories.merge(
        source_id=source.id,
        target_id=target.id,
        reason_code="CATEGORY_MERGE",
        expected_lock_version=source.lock_version,
    )
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    preview = service.preview(question_id=created[0].id)
    assert preview.eligible and preview.backup_required
    assert dict(preview.impact)["classification_revisions"] == 1
    service.delete(
        question_id=created[0].id,
        expected_fingerprint=preview.fingerprint,
        confirmation_token=preview.confirmation_token,
        reason_code="USER_REQUEST",
        correlation_id=uuid.uuid4(),
        backup_path=tmp_path / "shared-pre.sqlite3",
        isolated_restore_path=tmp_path / "shared-restore.sqlite3",
    )
    assert Question.objects.filter(pk=created[1].id).exists()
    assert ErrorCategory.objects.filter(pk__in=[source.id, target.id]).count() == 2
    assert ErrorClassification.objects.filter(attempt__question_id=created[1].id).exists()
    assert AuditEvent.objects.filter(event_code=AuditEventCode.PERSONAL_CATEGORY_MERGED).exists()
    assert not run_integrity_check().has_blocking_findings
