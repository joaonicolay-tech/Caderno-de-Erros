"""CT-073/074/076-082 e complementares da fundação de aprendizagem V0.3/E1."""

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import uuid
from contextlib import closing
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError, connection, transaction
from django.db.migrations.loader import MigrationLoader

from modules.accounts.models import User, Workspace
from modules.attempts.exceptions import IdempotencyConflictError
from modules.attempts.models import (
    Attempt,
    AttemptStatus,
    AttemptType,
    OperationKind,
    OperationReceipt,
    ResultEntityType,
)
from modules.attempts.persistence import (
    SQLITE_BUSY_TIMEOUT_SECONDS,
    SQLITE_MAX_RETRIES,
    SQLITE_RETRY_DELAY_SECONDS,
    run_sqlite_critical_write,
)
from modules.data_management.services import create_sqlite_backup, restore_sqlite_backup
from modules.errors.models import (
    ErrorCategory,
    ErrorCategoryCode,
    ErrorClassification,
    ErrorClassificationRevision,
)
from modules.questions.fixture import load_v02_fixture
from modules.questions.models import Question, QuestionStatus
from modules.questions.services import create_active
from modules.reviews.models import (
    Review,
    ReviewCycle,
    ReviewCycleState,
    ReviewStageCode,
    ReviewState,
)
from modules.reviews.policies import (
    CycleState,
    ReviewSchedulePolicy,
    ReviewStage,
    ReviewStatusPolicy,
    ReviewStructuralState,
    ReviewTemporalStatus,
)
from modules.taxonomy.services import create_discipline, create_subject
from shared.domain.time import Calendar, FixedClock, Instant, LocalDate, TimeZoneId

PROJECT_ROOT = Path(__file__).resolve().parents[1]
V02_MIGRATION_PATHS = (
    "src/modules/accounts/migrations/0001_initial.py",
    "src/modules/errors/migrations/0001_initial.py",
    "src/modules/taxonomy/migrations/0001_initial.py",
    "src/modules/questions/migrations/0001_origin_catalog.py",
    "src/modules/questions/migrations/0002_question_catalog.py",
)


def _workspace(*, email: str) -> Workspace:
    user = User.objects.create_user(email=email)
    return Workspace.objects.create(
        owner_user=user,
        name=f"Espaço {email}",
        timezone_name="America/Sao_Paulo",
    )


def _active_question(*, workspace: Workspace, suffix: str = "") -> Question:
    discipline = create_discipline(workspace_id=workspace.id, name=f"Matemática{suffix}")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name=f"Álgebra{suffix}",
    )
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem=f"Quanto é 2 + 2?{suffix}",
        alternatives=["3", "4"],
        correct_alternative_position=2,
    )


def _attempt(
    *,
    workspace: Workspace,
    question: Question,
    correct: bool = False,
    attempt_type: str = AttemptType.INITIAL,
    review: Review | None = None,
    status: str = AttemptStatus.VALID,
) -> Attempt:
    revision = question.revisions.get(is_current=True)
    selected = revision.alternatives.get(position=2 if correct else 1)
    voided = status == AttemptStatus.VOIDED
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        review=review,
        attempt_type=attempt_type,
        selected_alternative=selected,
        is_correct=correct,
        occurred_at=datetime(2026, 9, 8, 12, 0, tzinfo=UTC),
        timezone_name="America/Sao_Paulo",
        local_date=date(2026, 9, 8),
        status=status,
        voided_at=datetime(2026, 9, 8, 12, 1, tzinfo=UTC) if voided else None,
        void_reason="Registro histórico anulado" if voided else None,
        idempotency_key=uuid.uuid4(),
    )


def _cycle_and_review(
    *, workspace: Workspace, question: Question, origin_attempt: Attempt
) -> tuple[ReviewCycle, Review]:
    existing = ReviewCycle.objects.filter(
        workspace=workspace,
        question=question,
        state=ReviewCycleState.ACTIVE,
    ).first()
    if existing is not None:
        return existing, existing.reviews.get(state=ReviewState.PENDING)
    cycle = ReviewCycle.objects.create(
        workspace=workspace,
        question=question,
        origin_attempt=origin_attempt,
        origin_question_revision=origin_attempt.question_revision,
        started_at=origin_attempt.occurred_at,
    )
    review = Review.objects.create(
        workspace=workspace,
        review_cycle=cycle,
        question=question,
        sequence_number=1,
        stage_code=ReviewStageCode.D1,
        first_due_date=date(2026, 9, 9),
        current_due_date=date(2026, 9, 9),
        scheduled_from_attempt=origin_attempt,
        transition_code="INITIAL_ERROR_TO_D1",
    )
    return cycle, review


@pytest.mark.django_db(transaction=True)
def test_ct073_foreign_keys_and_local_checks_reject_invalid_learning_rows() -> None:
    workspace = _workspace(email="ct073@example.test")
    question = _active_question(workspace=workspace)
    revision = question.revisions.get(is_current=True)
    alternative = revision.alternatives.get(position=1)
    unknown_id = uuid.uuid4()

    with pytest.raises(IntegrityError):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO attempts_attempt "
                "(id, workspace_id, question_id, question_revision_id, selected_alternative_id, "
                "attempt_type, is_correct, occurred_at, timezone_name, local_date, status, "
                "idempotency_key, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    str(uuid.uuid4()),
                    str(workspace.id),
                    str(unknown_id),
                    str(revision.id),
                    str(alternative.id),
                    AttemptType.INITIAL,
                    False,
                    "2026-09-08T12:00:00+00:00",
                    "America/Sao_Paulo",
                    "2026-09-08",
                    AttemptStatus.VALID,
                    str(uuid.uuid4()),
                    "2026-09-08T12:00:00+00:00",
                ],
            )

    attempt = _attempt(workspace=workspace, question=question)
    invalid_updates = (
        ("attempts_attempt", "attempt_type", "INVALID", attempt.id),
        ("attempts_attempt", "status", "INVALID", attempt.id),
        ("attempts_attempt", "perceived_ease", "INVALID", attempt.id),
    )
    for table, field, value, identifier in invalid_updates:
        with pytest.raises(IntegrityError):
            with transaction.atomic(), connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {table} SET {field} = %s WHERE id = %s",  # noqa: S608
                    [value, identifier.hex],
                )

    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_key_check")
        assert cursor.fetchall() == []


@pytest.mark.django_db
def test_ct074_model_guards_reject_cross_workspace_learning_links() -> None:
    workspace_a = _workspace(email="ct074-a@example.test")
    workspace_b = _workspace(email="ct074-b@example.test")
    question_a = _active_question(workspace=workspace_a, suffix=" A")
    question_b = _active_question(workspace=workspace_b, suffix=" B")
    revision_b = question_b.revisions.get(is_current=True)
    alternative_b = revision_b.alternatives.get(position=1)

    with pytest.raises(ValidationError, match="Workspace"):
        Attempt.objects.create(
            workspace=workspace_a,
            question=question_a,
            question_revision=revision_b,
            attempt_type=AttemptType.INITIAL,
            selected_alternative=alternative_b,
            is_correct=False,
            occurred_at=datetime(2026, 9, 8, 12, 0, tzinfo=UTC),
            timezone_name="America/Sao_Paulo",
            local_date=date(2026, 9, 8),
            idempotency_key=uuid.uuid4(),
        )

    attempt_a = _attempt(workspace=workspace_a, question=question_a)
    category_b = ErrorCategory.objects.create(
        workspace=workspace_b,
        code=ErrorCategoryCode.CONCEPTUAL,
        display_name="Conceitual",
        description="Categoria B",
    )
    with pytest.raises(ValidationError, match="categoria"):
        ErrorClassification.objects.create(
            workspace=workspace_a,
            attempt=attempt_a,
            category=category_b,
        )

    assert Attempt.objects.filter(workspace=workspace_b).count() == 0
    assert ErrorClassification.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_ct076_only_one_valid_initial_attempt_exists_per_question() -> None:
    workspace = _workspace(email="ct076@example.test")
    question = _active_question(workspace=workspace)
    _attempt(workspace=workspace, question=question)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            _attempt(workspace=workspace, question=question)

    assert Attempt.objects.filter(question=question, status=AttemptStatus.VALID).count() == 1


@pytest.mark.django_db(transaction=True)
def test_ct077_only_one_valid_attempt_exists_per_review() -> None:
    workspace = _workspace(email="ct077@example.test")
    question = _active_question(workspace=workspace)
    initial = _attempt(workspace=workspace, question=question)
    _, review = _cycle_and_review(
        workspace=workspace,
        question=question,
        origin_attempt=initial,
    )
    _attempt(
        workspace=workspace,
        question=question,
        correct=True,
        attempt_type=AttemptType.REVIEW,
        review=review,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            _attempt(
                workspace=workspace,
                question=question,
                correct=False,
                attempt_type=AttemptType.REVIEW,
                review=review,
            )

    assert Attempt.objects.filter(review=review, status=AttemptStatus.VALID).count() == 1


@pytest.mark.django_db(transaction=True)
def test_ct078_only_one_active_cycle_exists_and_completed_history_is_preserved() -> None:
    workspace = _workspace(email="ct078@example.test")
    question = _active_question(workspace=workspace)
    initial = _attempt(workspace=workspace, question=question)
    cycle, _ = _cycle_and_review(
        workspace=workspace,
        question=question,
        origin_attempt=initial,
    )
    voided_origin = _attempt(
        workspace=workspace,
        question=question,
        status=AttemptStatus.VOIDED,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ReviewCycle.objects.bulk_create(
                [
                    ReviewCycle(
                        workspace=workspace,
                        question=question,
                        origin_attempt=voided_origin,
                        origin_question_revision=voided_origin.question_revision,
                        started_at=initial.occurred_at,
                    )
                ]
            )

    cycle.state = ReviewCycleState.COMPLETED
    cycle.completed_at = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)
    cycle.save()
    assert (
        ReviewCycle.objects.filter(question=question, state=ReviewCycleState.COMPLETED).count() == 1
    )


@pytest.mark.django_db(transaction=True)
def test_ct079_pending_review_is_rejected_by_guard_and_database_constraint() -> None:
    workspace = _workspace(email="ct079@example.test")
    question = _active_question(workspace=workspace)
    initial = _attempt(workspace=workspace, question=question)
    cycle, _ = _cycle_and_review(
        workspace=workspace,
        question=question,
        origin_attempt=initial,
    )
    duplicate = Review(
        workspace=workspace,
        review_cycle=cycle,
        question=question,
        sequence_number=2,
        stage_code=ReviewStageCode.D7,
        first_due_date=date(2026, 9, 15),
        current_due_date=date(2026, 9, 15),
        scheduled_from_attempt=initial,
        transition_code="TEST_SECOND_PENDING",
    )

    with pytest.raises(ValidationError, match="pendente"):
        duplicate.save()
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Review.objects.bulk_create([duplicate])

    assert Review.objects.filter(review_cycle=cycle, state=ReviewState.PENDING).count() == 1


@pytest.mark.django_db(transaction=True)
def test_ct080_receipt_recovers_equal_hash_and_rejects_collision() -> None:
    workspace = _workspace(email="ct080@example.test")
    question = _active_question(workspace=workspace)
    attempt = _attempt(workspace=workspace, question=question, correct=True)
    key = uuid.uuid4()
    request_hash = hashlib.sha256(b"canonical-minimal-request").hexdigest()
    receipt = OperationReceipt.objects.create(
        workspace=workspace,
        operation_kind=OperationKind.INITIAL_CORRECT,
        idempotency_key=key,
        request_hash=request_hash,
        result_entity_type=ResultEntityType.ATTEMPT,
        result_entity_id=attempt.id,
    )

    recovered = OperationReceipt.objects.resolve_existing(
        workspace_id=workspace.id,
        operation_kind=OperationKind.INITIAL_CORRECT,
        idempotency_key=key,
        request_hash=request_hash,
    )
    assert recovered.id == receipt.id
    assert recovered.minimum_retention_until == recovered.created_at + timedelta(days=30)
    retention_clock = FixedClock(Instant(receipt.created_at + timedelta(days=29)))
    with pytest.raises(ValidationError, match="retenção"):
        receipt.delete_if_retention_elapsed(clock=retention_clock)
    with pytest.raises(IdempotencyConflictError):
        OperationReceipt.objects.resolve_existing(
            workspace_id=workspace.id,
            operation_kind=OperationKind.INITIAL_CORRECT,
            idempotency_key=key,
            request_hash=hashlib.sha256(b"different-request").hexdigest(),
        )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            OperationReceipt.objects.create(
                workspace=workspace,
                operation_kind=OperationKind.INITIAL_CORRECT,
                idempotency_key=key,
                request_hash=request_hash,
                result_entity_type=ResultEntityType.ATTEMPT,
                result_entity_id=attempt.id,
            )
    retention_clock.set(Instant(receipt.created_at + timedelta(days=30)))
    assert receipt.delete_if_retention_elapsed(clock=retention_clock)[0] == 1


@pytest.mark.django_db
def test_classification_is_error_only_other_is_described_and_revision_is_append_only() -> None:
    workspace = _workspace(email="classification@example.test")
    incorrect_question = _active_question(workspace=workspace, suffix=" Incorreta")
    correct_question = _active_question(workspace=workspace, suffix=" Correta")
    incorrect = _attempt(workspace=workspace, question=incorrect_question)
    correct = _attempt(workspace=workspace, question=correct_question, correct=True)
    category = ErrorCategory.objects.create(
        workspace=workspace,
        code=ErrorCategoryCode.CONCEPTUAL,
        display_name="Conceitual",
        description="Categoria conceitual",
    )
    other = ErrorCategory.objects.create(
        workspace=workspace,
        code=ErrorCategoryCode.OTHER,
        display_name="Outra",
        description="Outra categoria",
    )

    with pytest.raises(ValidationError, match="incorreta"):
        ErrorClassification.objects.create(
            workspace=workspace,
            attempt=correct,
            category=category,
        )
    with pytest.raises(ValidationError, match="exige descrição"):
        ErrorClassification.objects.create(
            workspace=workspace,
            attempt=incorrect,
            category=other,
            other_description="   ",
        )

    classification = ErrorClassification.objects.create(
        workspace=workspace,
        attempt=incorrect,
        category=category,
    )
    revision = ErrorClassificationRevision.objects.create(
        workspace=workspace,
        error_classification=classification,
        revision_number=1,
        category=category,
    )
    revision.change_reason = "Tentativa de sobrescrita"
    with pytest.raises(ValidationError, match="append-only"):
        revision.save()
    with pytest.raises(ValidationError, match="append-only"):
        ErrorClassificationRevision.objects.filter(pk=revision.id).update(revision_number=2)


@pytest.mark.django_db
def test_attempt_is_immutable_and_validates_revision_alternative_and_result() -> None:
    workspace = _workspace(email="immutable@example.test")
    question_a = _active_question(workspace=workspace, suffix=" A")
    question_b = _active_question(workspace=workspace, suffix=" B")
    attempt = _attempt(workspace=workspace, question=question_a)
    attempt.is_correct = True
    with pytest.raises(ValidationError, match="imutável"):
        attempt.save()
    with pytest.raises(ValidationError, match="imutável"):
        Attempt.objects.filter(pk=attempt.id).update(is_correct=True)

    revision_a = question_a.revisions.get(is_current=True)
    alternative_b = question_b.revisions.get(is_current=True).alternatives.get(position=1)
    with pytest.raises(ValidationError, match="alternativa"):
        Attempt.objects.create(
            workspace=workspace,
            question=question_a,
            question_revision=revision_a,
            attempt_type=AttemptType.REVIEW,
            selected_alternative=alternative_b,
            is_correct=False,
            occurred_at=datetime(2026, 9, 8, 12, 0, tzinfo=UTC),
            timezone_name="America/Sao_Paulo",
            local_date=date(2026, 9, 8),
            idempotency_key=uuid.uuid4(),
        )


def test_review_policies_are_pure_deterministic_and_timezone_aware() -> None:
    clock = FixedClock(Instant(datetime(2026, 9, 9, 2, 30, tzinfo=UTC)))
    calendar = Calendar(clock)
    schedule = ReviewSchedulePolicy(clock=clock, calendar=calendar)
    sao_paulo = TimeZoneId("America/Sao_Paulo")

    transitions = {
        ReviewStage.D1: (ReviewStage.D7, date(2026, 9, 15)),
        ReviewStage.D7: (ReviewStage.D14, date(2026, 9, 22)),
        ReviewStage.D14: (ReviewStage.D30, date(2026, 10, 8)),
    }
    for stage, expected in transitions.items():
        decision = schedule.decide(
            current_stage=stage,
            is_correct=True,
            time_zone_id=sao_paulo,
        )
        assert (decision.next_stage, decision.next_due_date.value) == expected  # type: ignore[union-attr]
        assert decision.cycle_state == CycleState.ACTIVE

    reset = schedule.decide(
        current_stage=ReviewStage.D30,
        is_correct=False,
        time_zone_id=sao_paulo,
    )
    assert reset.next_stage == ReviewStage.D1
    assert reset.next_due_date == LocalDate(date(2026, 9, 9))
    completed = schedule.decide(
        current_stage=ReviewStage.D30,
        is_correct=True,
        time_zone_id=sao_paulo,
    )
    assert completed.cycle_state == CycleState.COMPLETED
    assert completed.next_stage is None and completed.next_due_date is None

    status = ReviewStatusPolicy(clock=clock, calendar=calendar)
    assert (
        status.evaluate(
            structural_state=ReviewStructuralState.PENDING,
            current_due_date=LocalDate(date(2026, 9, 7)),
            time_zone_id=sao_paulo,
        )
        == ReviewTemporalStatus.OVERDUE
    )
    assert (
        status.evaluate(
            structural_state=ReviewStructuralState.PENDING,
            current_due_date=LocalDate(date(2026, 9, 8)),
            time_zone_id=sao_paulo,
        )
        == ReviewTemporalStatus.DUE
    )
    assert (
        status.evaluate(
            structural_state=ReviewStructuralState.PENDING,
            current_due_date=LocalDate(date(2026, 9, 9)),
            time_zone_id=sao_paulo,
        )
        == ReviewTemporalStatus.FUTURE
    )
    assert (
        status.evaluate(
            structural_state=ReviewStructuralState.COMPLETED,
            current_due_date=LocalDate(date(2020, 1, 1)),
            time_zone_id=sao_paulo,
        )
        == ReviewTemporalStatus.COMPLETED
    )


def test_sqlite_contention_policy_has_one_retry_and_preserves_failure() -> None:
    operation = Mock(side_effect=[OperationalError("database is locked"), "ok"])
    sleeper = Mock()
    assert run_sqlite_critical_write(operation, sleep=sleeper) == "ok"
    assert operation.call_count == SQLITE_MAX_RETRIES + 1
    sleeper.assert_called_once_with(SQLITE_RETRY_DELAY_SECONDS)
    assert SQLITE_BUSY_TIMEOUT_SECONDS == 5.0

    exhausted = Mock(side_effect=OperationalError("database is locked"))
    with pytest.raises(OperationalError, match="locked"):
        run_sqlite_critical_write(exhausted, sleep=lambda _: None)
    assert exhausted.call_count == 2

    unrelated = Mock(side_effect=OperationalError("disk I/O error"))
    with pytest.raises(OperationalError, match="I/O"):
        run_sqlite_critical_write(unrelated, sleep=lambda _: None)
    assert unrelated.call_count == 1


def test_actual_sqlite_contention_has_no_partial_state_or_false_success(tmp_path: Path) -> None:
    database_path = tmp_path / "contention.sqlite3"
    key = "same-idempotency-key"
    observed_keys: list[str] = []
    holder = sqlite3.connect(database_path, timeout=0)
    holder.execute("CREATE TABLE effects (idempotency_key TEXT UNIQUE)")
    holder.commit()
    holder.execute("BEGIN EXCLUSIVE")

    def write_effect() -> str:
        observed_keys.append(key)
        try:
            with closing(sqlite3.connect(database_path, timeout=0)) as contender:
                with contender:
                    contender.execute(
                        "INSERT INTO effects (idempotency_key) VALUES (?)",
                        [key],
                    )
        except sqlite3.OperationalError as error:
            raise OperationalError(str(error)) from error
        return "success"

    try:
        with pytest.raises(OperationalError, match="locked"):
            run_sqlite_critical_write(write_effect, sleep=lambda _: None)
    finally:
        holder.rollback()
        holder.close()

    assert observed_keys == [key, key]
    with closing(sqlite3.connect(database_path)) as verifier:
        assert verifier.execute("SELECT COUNT(*) FROM effects").fetchone() == (0,)


@pytest.mark.django_db
def test_operation_receipt_payload_is_minimized() -> None:
    field_names = {field.name for field in OperationReceipt._meta.fields}
    assert field_names == {
        "id",
        "workspace",
        "operation_kind",
        "idempotency_key",
        "request_hash",
        "result_entity_type",
        "result_entity_id",
        "created_at",
    }
    forbidden = {"stem", "alternative", "answer", "explanation", "session", "token", "ip"}
    assert forbidden.isdisjoint(field_names)
    with pytest.raises(ValidationError, match="SHA-256"):
        workspace = _workspace(email="receipt-minimal@example.test")
        OperationReceipt.objects.create(
            workspace=workspace,
            operation_kind=OperationKind.INITIAL_CORRECT,
            idempotency_key=uuid.uuid4(),
            request_hash="invalid",
            result_entity_type=ResultEntityType.ATTEMPT,
            result_entity_id=uuid.uuid4(),
        )


@pytest.mark.django_db(transaction=True)
def test_v03_backup_restore_reconciles_learning_relations(tmp_path: Path) -> None:
    load_v02_fixture()
    workspace = Workspace.objects.get()
    question = Question.objects.get(status=QuestionStatus.ACTIVE)
    attempt = _attempt(workspace=workspace, question=question)
    category = ErrorCategory.objects.get(
        workspace=workspace,
        code=ErrorCategoryCode.CONCEPTUAL,
    )
    classification = ErrorClassification.objects.create(
        workspace=workspace,
        attempt=attempt,
        category=category,
    )
    ErrorClassificationRevision.objects.create(
        workspace=workspace,
        error_classification=classification,
        revision_number=1,
        category=category,
    )
    _cycle_and_review(workspace=workspace, question=question, origin_attempt=attempt)
    OperationReceipt.objects.create(
        workspace=workspace,
        operation_kind=OperationKind.INITIAL_ERROR,
        idempotency_key=uuid.uuid4(),
        request_hash=hashlib.sha256(b"initial-error").hexdigest(),
        result_entity_type=ResultEntityType.ATTEMPT,
        result_entity_id=attempt.id,
    )
    backup = tmp_path / "v03.sqlite3"
    restored = tmp_path / "v03-restored.sqlite3"
    connection.close()

    create_sqlite_backup(backup)
    result = restore_sqlite_backup(backup, restored)

    assert result.reconciliation.attempt_count == 1
    assert result.reconciliation.classification_count == 1
    assert result.reconciliation.classification_revision_count == 1
    assert result.reconciliation.review_cycle_count == 1
    assert result.reconciliation.review_count == 1
    assert result.reconciliation.operation_receipt_count == 1


@pytest.mark.django_db
def test_ct081_migration_graph_and_final_schema_are_frozen_without_cycle() -> None:
    loader = MigrationLoader(connection)
    attempts_1 = loader.get_migration("attempts", "0001_learning_foundation")
    errors_2 = loader.get_migration("errors", "0002_learning_classification")
    reviews_1 = loader.get_migration("reviews", "0001_learning_foundation")
    reviews_2 = loader.get_migration("reviews", "0002_activation_review_cycle")
    attempts_2 = loader.get_migration("attempts", "0002_review_receipt_constraints")

    assert attempts_1.dependencies == [
        ("accounts", "0001_initial"),
        ("questions", "0002_question_catalog"),
    ]
    assert ("attempts", "0001_learning_foundation") in errors_2.dependencies
    assert ("errors", "0001_initial") in errors_2.dependencies
    assert errors_2.run_before == [("reviews", "0001_learning_foundation")]
    assert {
        ("accounts", "0001_initial"),
        ("questions", "0002_question_catalog"),
        ("attempts", "0001_learning_foundation"),
    }.issubset(set(reviews_1.dependencies))
    assert ("reviews", "0001_learning_foundation") in attempts_2.dependencies
    assert ("reviews", "0001_learning_foundation") in reviews_2.dependencies
    assert ("attempts", "0002_review_receipt_constraints") in reviews_2.dependencies
    assert not any(
        getattr(operation, "name", None) == "review" for operation in attempts_1.operations
    )
    assert any(getattr(operation, "name", None) == "review" for operation in attempts_2.operations)
    assert any(
        getattr(operation, "name", None) == "origin_question_revision"
        for operation in reviews_2.operations
    )
    assert {
        "attempts_attempt",
        "attempts_operationreceipt",
        "errors_errorclassification",
        "errors_errorclassificationrevision",
        "reviews_reviewcycle",
        "reviews_review",
    }.issubset(connection.introspection.table_names())


def test_ct082_upgrade_v020_and_backup_restore_preserve_representative_data(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "upgrade.sqlite3"
    backup_path = tmp_path / "v02-backup.sqlite3"
    restored_path = tmp_path / "v02-restored.sqlite3"
    probe = r"""
import json
import os
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, UTC
from pathlib import Path
import django
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

django.setup()
v02 = [("auth", "0012_alter_user_first_name_max_length"), ("errors", "0001_initial"), ("questions", "0002_question_catalog"), ("taxonomy", "0001_initial")]
executor = MigrationExecutor(connection)
executor.migrate(v02)
apps = executor.loader.project_state(v02).apps
User = apps.get_model("accounts", "User")
Workspace = apps.get_model("accounts", "Workspace")
Category = apps.get_model("errors", "ErrorCategory")
Discipline = apps.get_model("taxonomy", "Discipline")
Subject = apps.get_model("taxonomy", "Subject")
Subsubject = apps.get_model("taxonomy", "Subsubject")
Board = apps.get_model("questions", "Board")
Exam = apps.get_model("questions", "Exam")
Source = apps.get_model("questions", "Source")
Question = apps.get_model("questions", "Question")
Revision = apps.get_model("questions", "QuestionRevision")
Alternative = apps.get_model("questions", "Alternative")
Origin = apps.get_model("questions", "QuestionOrigin")
user = User.objects.create(id=uuid.UUID("11111111-1111-4111-8111-111111111111"), password="!", display_name="Representativo", status="ACTIVE")
workspace = Workspace.objects.create(id=uuid.UUID("22222222-2222-4222-8222-222222222222"), owner_user=user, name="Espaço V0.2", timezone_name="America/Sao_Paulo", locale="pt-BR", lock_version=1)
Category.objects.create(workspace=workspace, code="CONCEPTUAL", display_name="Conceitual", name_key="conceitual", description="Histórico")
discipline = Discipline.objects.create(workspace=workspace, name="Matemática", name_key="matemática")
subject = Subject.objects.create(workspace=workspace, discipline=discipline, name="Álgebra", name_key="álgebra")
subsubject = Subsubject.objects.create(workspace=workspace, subject=subject, name="Equações", name_key="equações")
board = Board.objects.create(workspace=workspace, name="Banca", name_key="banca")
exam = Exam.objects.create(workspace=workspace, board=board, name="Prova", name_key="prova", year=2026)
source_ref = Source.objects.create(workspace=workspace, name="Livro", name_key="livro", source_type="BOOK")
question = Question.objects.create(workspace=workspace, discipline=discipline, subject=subject, subsubject=subsubject, question_type="OBJECTIVE_SINGLE", status="ACTIVE", activated_at=datetime(2026, 9, 7, 12, tzinfo=UTC), lock_version=1)
revision_1 = Revision.objects.create(workspace=workspace, question=question, version_number=1, is_current=False, stem="2+2?", change_kind="INITIAL")
Alternative.objects.create(workspace=workspace, question_revision=revision_1, position=1, text="3", text_key="3")
correct_1 = Alternative.objects.create(workspace=workspace, question_revision=revision_1, position=2, text="4", text_key="4")
Revision.objects.filter(pk=revision_1.pk).update(correct_alternative=correct_1)
revision_2 = Revision.objects.create(workspace=workspace, question=question, version_number=2, is_current=True, stem="Quanto é 2 + 2?", explanation="Quatro", change_kind="ENRICHMENT")
wrong_2 = Alternative.objects.create(workspace=workspace, question_revision=revision_2, position=1, text="3", text_key="3")
correct_2 = Alternative.objects.create(workspace=workspace, question_revision=revision_2, position=2, text="4", text_key="4")
Revision.objects.filter(pk=revision_2.pk).update(correct_alternative=correct_2)
origin = Origin.objects.create(workspace=workspace, question=question, source=source_ref, exam=exam, reference_text="Página 10", lock_version=1)
before = {"users": User.objects.count(), "workspaces": Workspace.objects.count(), "categories": Category.objects.count(), "disciplines": Discipline.objects.count(), "subjects": Subject.objects.count(), "subsubjects": Subsubject.objects.count(), "boards": Board.objects.count(), "exams": Exam.objects.count(), "sources": Source.objects.count(), "questions": Question.objects.count(), "revisions": Revision.objects.count(), "alternatives": Alternative.objects.count(), "origins": Origin.objects.count(), "activated_at": question.activated_at.isoformat(), "current_version": revision_2.version_number, "historical_stem": revision_1.stem, "correct": str(correct_2.id), "wrong": str(wrong_2.id), "origin_source": str(source_ref.id), "origin_exam": str(exam.id), "origin_reference": origin.reference_text}
source = Path(connection.settings_dict["NAME"])
connection.close()
with closing(sqlite3.connect(source)) as src, closing(sqlite3.connect(Path(os.environ["CEI_V03_BACKUP_PATH"]))) as dst:
    with dst:
        src.backup(dst)
executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
final_apps = executor.loader.project_state().apps
FinalRevision = final_apps.get_model("questions", "QuestionRevision")
FinalOrigin = final_apps.get_model("questions", "QuestionOrigin")
current_revision = FinalRevision.objects.get(version_number=2)
historical_revision = FinalRevision.objects.get(version_number=1)
current_origin = FinalOrigin.objects.get()
FinalAttempt = final_apps.get_model("attempts", "Attempt")
FinalCycle = final_apps.get_model("reviews", "ReviewCycle")
FinalAttempt.objects.create(workspace_id=workspace.id, question_id=question.id, question_revision_id=current_revision.id, attempt_type="INITIAL", selected_alternative_id=current_revision.correct_alternative_id, is_correct=True, occurred_at=datetime(2026, 9, 8, 12, tzinfo=UTC), timezone_name="America/Sao_Paulo", local_date=datetime(2026, 9, 8, 12, tzinfo=UTC).astimezone().date(), idempotency_key=uuid.UUID("33333333-3333-4333-8333-333333333333"))
after = {"users": final_apps.get_model("accounts", "User").objects.count(), "workspaces": final_apps.get_model("accounts", "Workspace").objects.count(), "categories": final_apps.get_model("errors", "ErrorCategory").objects.count(), "disciplines": final_apps.get_model("taxonomy", "Discipline").objects.count(), "subjects": final_apps.get_model("taxonomy", "Subject").objects.count(), "subsubjects": final_apps.get_model("taxonomy", "Subsubject").objects.count(), "boards": final_apps.get_model("questions", "Board").objects.count(), "exams": final_apps.get_model("questions", "Exam").objects.count(), "sources": final_apps.get_model("questions", "Source").objects.count(), "questions": final_apps.get_model("questions", "Question").objects.count(), "revisions": FinalRevision.objects.count(), "alternatives": final_apps.get_model("questions", "Alternative").objects.count(), "origins": FinalOrigin.objects.count(), "activated_at": final_apps.get_model("questions", "Question").objects.get().activated_at.isoformat(), "current_version": current_revision.version_number, "historical_stem": historical_revision.stem, "correct": str(current_revision.correct_alternative_id), "wrong": str(wrong_2.id), "origin_source": str(current_origin.source_id), "origin_exam": str(current_origin.exam_id), "origin_reference": current_origin.reference_text, "v03_attempts": FinalAttempt.objects.count(), "v03_cycles": FinalCycle.objects.count()}
connection.close()
with closing(sqlite3.connect(Path(os.environ["CEI_V03_BACKUP_PATH"]))) as src, closing(sqlite3.connect(Path(os.environ["CEI_V03_RESTORED_PATH"]))) as dst:
    with dst:
        src.backup(dst)
with closing(sqlite3.connect(Path(os.environ["CEI_V03_RESTORED_PATH"]))) as restored:
    restored.execute("PRAGMA foreign_keys=ON")
    restored_migrations = set(restored.execute("SELECT app, name FROM django_migrations"))
    rollback = {"integrity": restored.execute("PRAGMA integrity_check").fetchone()[0], "foreign_keys": restored.execute("PRAGMA foreign_key_check").fetchall(), "questions": restored.execute("SELECT COUNT(*) FROM questions_question").fetchone()[0], "v03_migrations": sorted([f"{app}.{name}" for app, name in restored_migrations if app in {"attempts", "reviews"} or (app == "errors" and name == "0002_learning_classification")])}
print(json.dumps({"before": before, "after": after, "rollback": rollback}))
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
    environment["CEI_TEST_DATABASE_PATH"] = str(database_path)
    environment["CEI_V03_BACKUP_PATH"] = str(backup_path)
    environment["CEI_V03_RESTORED_PATH"] = str(restored_path)
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    evidence = json.loads(result.stdout.strip().splitlines()[-1])
    assert {
        key: value
        for key, value in evidence["after"].items()
        if key not in {"v03_attempts", "v03_cycles"}
    } == evidence["before"]
    assert evidence["after"]["v03_attempts"] == 1
    assert evidence["after"]["v03_cycles"] == 0
    assert evidence["rollback"] == {
        "integrity": "ok",
        "foreign_keys": [],
        "questions": 1,
        "v03_migrations": [],
    }


def test_v01_v02_migrations_match_protected_v020_tag() -> None:
    git_executable = shutil.which("git")
    assert git_executable is not None
    result = subprocess.run(
        [git_executable, "diff", "--exit-code", "v0.2.0", "--", *V02_MIGRATION_PATHS],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
