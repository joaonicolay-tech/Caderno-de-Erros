"""V0.5-S2A: auditoria, categorias pessoais, agenda e inclusão manual."""

import uuid
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError

from modules.accounts.models import User, Workspace
from modules.analytics.services import AnalyticsService
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.data_management.services import create_sqlite_backup, restore_sqlite_backup
from modules.errors.models import (
    ErrorCategory,
    ErrorCategoryCode,
    ErrorCategoryKind,
    ErrorCategoryState,
    ErrorClassification,
)
from modules.errors.services import (
    ErrorDiagnosisService,
    PersonalCategoryConflictError,
    PersonalCategoryService,
    seed_standard_error_categories,
)
from modules.operations.integrity import run_integrity_check
from modules.operations.models import AuditEntityType, AuditEvent, AuditEventCode
from modules.questions.models import Question
from modules.questions.services import create_active
from modules.reviews.models import (
    Review,
    ReviewCycle,
    ReviewCycleOriginKind,
    ReviewCycleState,
    ReviewScheduleChange,
    ReviewState,
)
from modules.reviews.policies import ReviewTemporalStatus
from modules.reviews.services import (
    ManualReviewInclusionService,
    ReviewManagementConflictError,
    ReviewScheduleService,
)
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant

CLOCK = FixedClock(Instant(datetime(2026, 9, 20, 15, tzinfo=UTC)))


def _workspace(email: str) -> Workspace:
    user = User.objects.create_user(email=email)
    workspace = Workspace.objects.create(
        owner_user=user,
        name=email,
        timezone_name="America/Sao_Paulo",
    )
    seed_standard_error_categories(workspace)
    return workspace


def _question(workspace: Workspace, suffix: str) -> Question:
    discipline = create_discipline(workspace_id=workspace.id, name=f"Disciplina {suffix}")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name=f"Assunto {suffix}",
    )
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem=f"Questão {suffix}",
        alternatives=["incorreta", "correta"],
        correct_alternative_position=2,
        clock=CLOCK,
    )


def _initial(workspace: Workspace, question: Question, *, correct: bool) -> Attempt:
    revision = question.revisions.get(is_current=True)
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        attempt_type=AttemptType.INITIAL,
        selected_alternative=revision.alternatives.get(position=2 if correct else 1),
        is_correct=correct,
        occurred_at=CLOCK.now().value,
        timezone_name=workspace.timezone_name,
        local_date=date(2026, 9, 20),
        idempotency_key=uuid.uuid4(),
    )


def _finish_activation(question: Question) -> None:
    completed_at = CLOCK.now().value
    Review.objects.filter(question=question, state=ReviewState.PENDING).update(
        state=ReviewState.COMPLETED,
        completed_at=completed_at,
    )
    ReviewCycle.objects.filter(question=question, state=ReviewCycleState.ACTIVE).update(
        state=ReviewCycleState.COMPLETED,
        completed_at=completed_at,
    )


@pytest.mark.django_db
def test_audit_event_is_closed_sanitized_and_append_only() -> None:
    workspace = _workspace("audit@example.test")
    event = AuditEvent.objects.create(
        workspace=workspace,
        event_code=AuditEventCode.MANUAL_REVIEW_INCLUDED,
        entity_type=AuditEntityType.REVIEW_CYCLE,
        entity_id=uuid.uuid4(),
        correlation_id=uuid.uuid4(),
        reason_code="STUDY_PLAN",
    )

    assert not {
        "payload",
        "stem",
        "alternatives",
        "answer",
        "explanation",
        "secret",
    }.intersection(field.name for field in AuditEvent._meta.fields)
    with pytest.raises(ValidationError, match="append-only"):
        event.save()
    with pytest.raises(ValidationError, match="append-only"):
        AuditEvent.objects.filter(pk=event.id).update(reason_code="OTHER")
    with pytest.raises(ValidationError, match="append-only"):
        event.delete()
    with pytest.raises(ValidationError, match="código"):
        AuditEvent.objects.create(
            workspace=workspace,
            event_code=AuditEventCode.MANUAL_REVIEW_INCLUDED,
            entity_type=AuditEntityType.REVIEW_CYCLE,
            entity_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
            reason_code="secret=conteudo da questao",
        )


@pytest.mark.django_db
def test_personal_category_create_normalizes_and_protects_standard_categories() -> None:
    workspace = _workspace("categories@example.test")
    foreign = _workspace("categories-foreign@example.test")
    service = PersonalCategoryService(workspace_id=workspace.id)

    personal = service.create(display_name="  Minha   Categoria  ")
    same_name_elsewhere = PersonalCategoryService(workspace_id=foreign.id).create(
        display_name="minha categoria"
    )

    assert (personal.display_name, personal.name_key) == ("Minha Categoria", "minha categoria")
    assert personal.code.startswith("PERSONAL_")
    assert personal.category_kind == ErrorCategoryKind.PERSONAL
    assert personal.state == ErrorCategoryState.ACTIVE
    assert same_name_elsewhere.workspace_id == foreign.id
    with pytest.raises(PersonalCategoryConflictError, match="Já existe"):
        service.create(display_name="MINHA CATEGORIA")

    standard = workspace.error_categories.get(code=ErrorCategoryCode.ATTENTION)
    with pytest.raises(PersonalCategoryConflictError):
        service.archive(
            category_id=standard.id,
            reason_code="MAINTENANCE",
            expected_lock_version=standard.lock_version,
        )
    with pytest.raises(ValidationError, match="padrão"):
        ErrorCategory.objects.filter(pk=standard.id).update(state=ErrorCategoryState.ARCHIVED)


@pytest.mark.django_db
def test_personal_category_rename_archive_audits_and_blocks_new_use() -> None:
    workspace = _workspace("category-lifecycle@example.test")
    category = PersonalCategoryService(workspace_id=workspace.id).create(display_name="Original")
    stable_code = category.code
    service = PersonalCategoryService(workspace_id=workspace.id)

    renamed = service.rename(
        category_id=category.id,
        display_name="Renomeada",
        reason_code="DISPLAY_CORRECTION",
        expected_lock_version=category.lock_version,
    )
    archived = service.archive(
        category_id=renamed.id,
        reason_code="NO_LONGER_USED",
        expected_lock_version=renamed.lock_version,
    )

    assert archived.code == stable_code
    assert archived.state == ErrorCategoryState.ARCHIVED
    assert list(
        AuditEvent.objects.filter(entity_id=category.id)
        .order_by("created_at")
        .values_list("event_code", flat=True)
    ) == [
        AuditEventCode.PERSONAL_CATEGORY_RENAMED,
        AuditEventCode.PERSONAL_CATEGORY_ARCHIVED,
    ]
    question = _question(workspace, "archived category")
    attempt = _initial(workspace, question, correct=False)
    with pytest.raises(ValidationError, match="pessoal ativa"):
        ErrorClassification.objects.create(
            workspace=workspace,
            attempt=attempt,
            category=archived,
        )


@pytest.mark.django_db
def test_merge_chain_preserves_history_and_projects_one_effective_total() -> None:
    workspace = _workspace("merge@example.test")
    service = PersonalCategoryService(workspace_id=workspace.id)
    category_a = service.create(display_name="A pessoal")
    category_b = service.create(display_name="B pessoal")
    category_c = service.create(display_name="C pessoal")
    classifications: list[ErrorClassification] = []
    for index, category in enumerate((category_a, category_a, category_b), start=1):
        question = _question(workspace, f"merge {index}")
        classifications.append(
            ErrorClassification.objects.create(
                workspace=workspace,
                attempt=_initial(workspace, question, correct=False),
                category=category,
            )
        )

    category_a = service.merge(
        source_id=category_a.id,
        target_id=category_b.id,
        reason_code="DUPLICATE",
        expected_lock_version=category_a.lock_version,
    )
    category_b = service.merge(
        source_id=category_b.id,
        target_id=category_c.id,
        reason_code="CONSOLIDATION",
        expected_lock_version=category_b.lock_version,
    )

    assert [item.category_id for item in classifications] == [
        category_a.id,
        category_a.id,
        category_b.id,
    ]
    breakdown = AnalyticsService(workspace_id=workspace.id).error_categories()
    rows = {row.category_id: row for row in breakdown.rows}
    assert category_a.id not in rows and category_b.id not in rows
    assert rows[category_c.id].errors == 3
    assert breakdown.classified_errors == breakdown.eligible_errors == 3
    assert (
        AnalyticsService(workspace_id=workspace.id)
        .error_category_drilldown(category_id=category_c.id)
        .count()
        == 3
    )


@pytest.mark.django_db
def test_diagnosis_correction_after_merge_preserves_source_revision() -> None:
    workspace = _workspace("merge-history@example.test")
    service = PersonalCategoryService(workspace_id=workspace.id)
    source = service.create(display_name="Origem histórica")
    target = service.create(display_name="Alvo atual")
    question = _question(workspace, "merge history")
    classification = ErrorClassification.objects.create(
        workspace=workspace,
        attempt=_initial(workspace, question, correct=False),
        category=source,
    )
    service.merge(
        source_id=source.id,
        target_id=target.id,
        reason_code="CONSOLIDATION",
        expected_lock_version=source.lock_version,
    )

    corrected = ErrorDiagnosisService(workspace_id=workspace.id, clock=CLOCK).correct(
        attempt_id=classification.attempt_id,
        category_id=target.id,
        change_reason="Correção explícita posterior",
        expected_lock_version=classification.lock_version,
    )

    assert corrected.category_id == target.id
    assert list(
        corrected.revisions.order_by("revision_number").values_list("category_id", flat=True)
    ) == [source.id, target.id]


@pytest.mark.django_db
def test_merge_rejects_self_cycle_standard_and_cross_workspace_without_mutation() -> None:
    workspace = _workspace("merge-guards@example.test")
    foreign = _workspace("merge-guards-foreign@example.test")
    service = PersonalCategoryService(workspace_id=workspace.id)
    source = service.create(display_name="Source")
    target = service.create(display_name="Target")
    foreign_target = PersonalCategoryService(workspace_id=foreign.id).create(display_name="Foreign")
    standard = workspace.error_categories.get(code=ErrorCategoryCode.CONCEPTUAL)

    for invalid_target in (source, foreign_target, standard):
        with pytest.raises(PersonalCategoryConflictError):
            service.merge(
                source_id=source.id,
                target_id=invalid_target.id,
                reason_code="INVALID",
                expected_lock_version=source.lock_version,
            )
    source = service.merge(
        source_id=source.id,
        target_id=target.id,
        reason_code="VALID",
        expected_lock_version=source.lock_version,
    )
    with pytest.raises(PersonalCategoryConflictError):
        service.merge(
            source_id=target.id,
            target_id=source.id,
            reason_code="WOULD_CYCLE",
            expected_lock_version=target.lock_version,
        )
    target.refresh_from_db()
    assert target.state == ErrorCategoryState.ACTIVE
    assert (
        AuditEvent.objects.filter(event_code=AuditEventCode.PERSONAL_CATEGORY_MERGED).count() == 1
    )


@pytest.mark.django_db
def test_category_mutation_rolls_back_when_audit_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = _workspace("category-rollback@example.test")
    category = PersonalCategoryService(workspace_id=workspace.id).create(display_name="Rollback")

    def fail_audit(**_kwargs: object) -> None:
        raise RuntimeError("simulated audit failure")

    monkeypatch.setattr("modules.errors.services.record_audit_event", fail_audit)
    with pytest.raises(RuntimeError, match="simulated"):
        PersonalCategoryService(workspace_id=workspace.id).archive(
            category_id=category.id,
            reason_code="NO_LONGER_USED",
            expected_lock_version=category.lock_version,
        )
    category.refresh_from_db()
    assert category.state == ErrorCategoryState.ACTIVE
    assert not AuditEvent.objects.filter(entity_id=category.id).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("new_due_date", [date(2026, 9, 20), date(2026, 10, 1)])
def test_reschedule_today_or_future_preserves_schedule_facts(new_due_date: date) -> None:
    workspace = _workspace(f"reschedule-{new_due_date.isoformat()}@example.test")
    question = _question(workspace, new_due_date.isoformat())
    review = question.reviews.get(state=ReviewState.PENDING)
    original = (
        review.first_due_date,
        review.stage_code,
        review.policy_code,
        Attempt.objects.count(),
        AnalyticsService(workspace_id=workspace.id, clock=CLOCK).activity(),
    )

    changed = ReviewScheduleService(workspace_id=workspace.id, clock=CLOCK).reschedule(
        review_id=review.id,
        new_due_date=new_due_date,
        reason_code="STUDY_PLAN",
        expected_lock_version=review.lock_version,
    )

    assert (changed.first_due_date, changed.stage_code, changed.policy_code) == original[:3]
    assert changed.current_due_date == new_due_date
    assert Attempt.objects.count() == original[3]
    assert AnalyticsService(workspace_id=workspace.id, clock=CLOCK).activity() == original[4]
    history = ReviewScheduleChange.objects.get(review=review)
    audit = AuditEvent.objects.get(
        event_code=AuditEventCode.REVIEW_RESCHEDULED,
        entity_id=review.id,
    )
    assert history.correlation_id == audit.correlation_id
    assert history.previous_due_date == review.current_due_date
    assert history.new_due_date == new_due_date
    changed.first_due_date = date(2026, 12, 31)
    with pytest.raises(ValidationError, match="first_due_date"):
        changed.save()
    with pytest.raises(ValidationError, match="append-only"):
        history.save()
    with pytest.raises(ValidationError, match="append-only"):
        ReviewScheduleChange.objects.filter(pk=history.id).update(reason_code="OTHER")
    with pytest.raises(ValidationError, match="append-only"):
        history.delete()
    status = (
        ReviewTemporalStatus.DUE
        if new_due_date == date(2026, 9, 20)
        else ReviewTemporalStatus.FUTURE
    )
    assert (
        AnalyticsService(workspace_id=workspace.id, clock=CLOCK)
        .review_drilldown(status=status)
        .get()
        .id
        == review.id
    )


@pytest.mark.django_db
def test_reschedule_rejects_invalid_context_and_stale_version_atomically() -> None:
    workspace = _workspace("reschedule-guards@example.test")
    foreign = _workspace("reschedule-guards-foreign@example.test")
    review = _question(workspace, "reschedule guards").reviews.get()
    service = ReviewScheduleService(workspace_id=workspace.id, clock=CLOCK)

    with pytest.raises(ValidationError, match="hoje ou futura"):
        service.reschedule(
            review_id=review.id,
            new_due_date=date(2026, 9, 19),
            reason_code="STUDY_PLAN",
            expected_lock_version=review.lock_version,
        )
    with pytest.raises(ValidationError, match="obrigatório"):
        service.reschedule(
            review_id=review.id,
            new_due_date=date(2026, 9, 25),
            reason_code="",
            expected_lock_version=review.lock_version,
        )
    with pytest.raises(ReviewManagementConflictError):
        ReviewScheduleService(workspace_id=foreign.id, clock=CLOCK).reschedule(
            review_id=review.id,
            new_due_date=date(2026, 9, 25),
            reason_code="STUDY_PLAN",
            expected_lock_version=review.lock_version,
        )
    changed = service.reschedule(
        review_id=review.id,
        new_due_date=date(2026, 9, 25),
        reason_code="STUDY_PLAN",
        expected_lock_version=review.lock_version,
    )
    with pytest.raises(ReviewManagementConflictError):
        service.reschedule(
            review_id=review.id,
            new_due_date=date(2026, 9, 26),
            reason_code="STUDY_PLAN",
            expected_lock_version=review.lock_version,
        )
    assert changed.current_due_date == date(2026, 9, 25)
    assert (
        ReviewScheduleChange.objects.count()
        == AuditEvent.objects.filter(event_code=AuditEventCode.REVIEW_RESCHEDULED).count()
        == 1
    )


@pytest.mark.django_db
def test_reschedule_requires_pending_review_active_question_and_cycle() -> None:
    workspace = _workspace("reschedule-eligibility@example.test")
    service = ReviewScheduleService(workspace_id=workspace.id, clock=CLOCK)

    completed_review = _question(workspace, "completed review").reviews.get()
    Review.objects.filter(pk=completed_review.id).update(
        state=ReviewState.COMPLETED,
        completed_at=CLOCK.now().value,
    )
    with pytest.raises(ReviewManagementConflictError):
        service.reschedule(
            review_id=completed_review.id,
            new_due_date=date(2026, 9, 25),
            reason_code="STUDY_PLAN",
            expected_lock_version=completed_review.lock_version,
        )

    inactive_question_review = _question(workspace, "inactive question").reviews.get()
    Question.objects.filter(pk=inactive_question_review.question_id).update(
        status="ARCHIVED",
        archived_at=CLOCK.now().value,
    )
    with pytest.raises(ReviewManagementConflictError):
        service.reschedule(
            review_id=inactive_question_review.id,
            new_due_date=date(2026, 9, 25),
            reason_code="STUDY_PLAN",
            expected_lock_version=inactive_question_review.lock_version,
        )

    inactive_cycle_review = _question(workspace, "inactive cycle").reviews.get()
    ReviewCycle.objects.filter(pk=inactive_cycle_review.review_cycle_id).update(
        state=ReviewCycleState.COMPLETED,
        completed_at=CLOCK.now().value,
    )
    with pytest.raises(ReviewManagementConflictError):
        service.reschedule(
            review_id=inactive_cycle_review.id,
            new_due_date=date(2026, 9, 25),
            reason_code="STUDY_PLAN",
            expected_lock_version=inactive_cycle_review.lock_version,
        )


@pytest.mark.django_db
def test_reschedule_rolls_back_operational_date_when_audit_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _workspace("reschedule-rollback@example.test")
    review = _question(workspace, "reschedule rollback").reviews.get()
    original_due = review.current_due_date

    def fail_audit(**_kwargs: object) -> None:
        raise RuntimeError("simulated audit failure")

    monkeypatch.setattr("modules.reviews.services.record_audit_event", fail_audit)
    with pytest.raises(RuntimeError, match="simulated"):
        ReviewScheduleService(workspace_id=workspace.id, clock=CLOCK).reschedule(
            review_id=review.id,
            new_due_date=date(2026, 9, 25),
            reason_code="STUDY_PLAN",
            expected_lock_version=review.lock_version,
        )
    review.refresh_from_db()
    assert review.current_due_date == original_due
    assert not ReviewScheduleChange.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_manual_inclusion_creates_only_cycle_d1_and_audit() -> None:
    workspace = _workspace("manual@example.test")
    question = _question(workspace, "manual")
    initial = _initial(workspace, question, correct=True)
    _finish_activation(question)
    before_attempts = Attempt.objects.count()
    before_performed = AnalyticsService(workspace_id=workspace.id).activity().performed_questions

    cycle = ManualReviewInclusionService(workspace_id=workspace.id, clock=CLOCK).include(
        question_id=question.id
    )

    review = cycle.reviews.get()
    assert cycle.origin_kind == ReviewCycleOriginKind.MANUAL
    assert cycle.origin_attempt_id == initial.id
    assert (review.stage_code, review.first_due_date, review.current_due_date) == (
        "D1",
        date(2026, 9, 21),
        date(2026, 9, 21),
    )
    assert review.scheduled_from_attempt_id == initial.id
    assert Attempt.objects.count() == before_attempts
    assert (
        AnalyticsService(workspace_id=workspace.id).activity().performed_questions
        == before_performed
    )
    assert AuditEvent.objects.filter(
        event_code=AuditEventCode.MANUAL_REVIEW_INCLUDED,
        entity_id=cycle.id,
        related_entity_id=question.id,
    ).exists()
    assert AuditEvent.objects.get(entity_id=cycle.id).reason_code is None
    integrity = run_integrity_check()
    assert not [
        finding
        for finding in integrity.findings
        if finding.invariant_id in {"REV-001", "REV-002", "REV-004", "AUD-001"}
        and finding.technical_id in {str(cycle.id), str(review.id)}
    ]
    with pytest.raises(ReviewManagementConflictError):
        ManualReviewInclusionService(workspace_id=workspace.id, clock=CLOCK).include(
            question_id=question.id
        )


@pytest.mark.django_db
def test_manual_inclusion_rejects_wrong_voided_and_cross_workspace() -> None:
    workspace = _workspace("manual-guards@example.test")
    foreign = _workspace("manual-guards-foreign@example.test")
    wrong_question = _question(workspace, "manual wrong")
    _initial(workspace, wrong_question, correct=False)
    _finish_activation(wrong_question)
    with pytest.raises(ReviewManagementConflictError):
        ManualReviewInclusionService(workspace_id=workspace.id, clock=CLOCK).include(
            question_id=wrong_question.id
        )

    voided_question = _question(workspace, "manual voided")
    voided = _initial(workspace, voided_question, correct=True)
    _finish_activation(voided_question)
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE attempts_attempt SET status = %s, voided_at = %s, void_reason = %s WHERE id = %s",
            [AttemptStatus.VOIDED, CLOCK.now().value, "fixture", voided.id.hex],
        )
    with pytest.raises(ReviewManagementConflictError):
        ManualReviewInclusionService(workspace_id=workspace.id, clock=CLOCK).include(
            question_id=voided_question.id
        )
    with pytest.raises(ReviewManagementConflictError):
        ManualReviewInclusionService(workspace_id=foreign.id, clock=CLOCK).include(
            question_id=voided_question.id
        )

    archived_question = _question(workspace, "manual archived")
    _initial(workspace, archived_question, correct=True)
    _finish_activation(archived_question)
    Question.objects.filter(pk=archived_question.id).update(
        status="ARCHIVED",
        archived_at=CLOCK.now().value,
    )
    with pytest.raises(ReviewManagementConflictError):
        ManualReviewInclusionService(workspace_id=workspace.id, clock=CLOCK).include(
            question_id=archived_question.id
        )
    assert not ReviewCycle.objects.filter(origin_kind=ReviewCycleOriginKind.MANUAL).exists()


@pytest.mark.django_db
def test_manual_inclusion_rolls_back_cycle_and_d1_when_audit_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _workspace("manual-rollback@example.test")
    question = _question(workspace, "manual rollback")
    _initial(workspace, question, correct=True)
    _finish_activation(question)
    cycles_before = ReviewCycle.objects.count()
    reviews_before = Review.objects.count()

    def fail_audit(**_kwargs: object) -> None:
        raise RuntimeError("simulated audit failure")

    monkeypatch.setattr("modules.reviews.services.record_audit_event", fail_audit)
    with pytest.raises(RuntimeError, match="simulated"):
        ManualReviewInclusionService(workspace_id=workspace.id, clock=CLOCK).include(
            question_id=question.id
        )
    assert ReviewCycle.objects.count() == cycles_before
    assert Review.objects.count() == reviews_before
    assert not ReviewCycle.objects.filter(origin_kind=ReviewCycleOriginKind.MANUAL).exists()


@pytest.mark.django_db(transaction=True)
def test_s6_backup_restore_accepts_personal_chain_and_reschedule(tmp_path: Path) -> None:
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    service = PersonalCategoryService(workspace_id=workspace.id)
    category_a = service.create(display_name="Recovery A")
    category_b = service.create(display_name="Recovery B")
    category_c = service.create(display_name="Recovery C")
    service.merge(
        source_id=category_a.id,
        target_id=category_b.id,
        reason_code="CONSOLIDATION",
        expected_lock_version=category_a.lock_version,
    )
    service.merge(
        source_id=category_b.id,
        target_id=category_c.id,
        reason_code="CONSOLIDATION",
        expected_lock_version=category_b.lock_version,
    )
    review = _question(workspace, "recovery reschedule").reviews.get()
    ReviewScheduleService(workspace_id=workspace.id, clock=CLOCK).reschedule(
        review_id=review.id,
        new_due_date=date(2026, 9, 25),
        reason_code="STUDY_PLAN",
        expected_lock_version=review.lock_version,
    )
    backup = tmp_path / "s2a.sqlite3"
    restored = tmp_path / "s2a-restored.sqlite3"

    create_sqlite_backup(backup)
    result = restore_sqlite_backup(backup, restored)

    assert result.reconciliation.category_count == 13
    assert result.integrity.checks_executed == 20
    assert result.integrity.total_findings == 0
