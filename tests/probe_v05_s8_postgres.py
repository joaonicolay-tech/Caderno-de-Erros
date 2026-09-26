"""Prova S8 opt-in em um PostgreSQL local descartável, sem credenciais no código."""

from __future__ import annotations

import json
import os
import re
import sys
import uuid
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

import django
import psycopg
from django.conf import settings
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

DATABASE = os.environ.get("CEI_S8_PG_DATABASE", "")
ROLE = os.environ.get("CEI_S8_PG_ROLE", "")
if not re.fullmatch(r"cei_s8_test_[a-z0-9_]+", DATABASE) or not re.fullmatch(
    r"cei_s8_role_[a-z0-9_]+", ROLE
):
    raise SystemExit("S8 exige database/role de teste dedicados e identificados.")

settings.DATABASES["default"] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": DATABASE,
    "USER": "postgres",
    "HOST": "127.0.0.1",
    "PORT": "5432",
    "OPTIONS": {"options": f"-c role={ROLE}"},
}
django.setup()

from modules.accounts.models import User, Workspace  # noqa: E402
from modules.attempts.corrections import AttemptCorrectionService  # noqa: E402
from modules.attempts.exceptions import IdempotencyConflictError  # noqa: E402
from modules.attempts.models import Attempt, OperationReceipt  # noqa: E402
from modules.domain.models import MasteryStateEvent  # noqa: E402
from modules.domain.services import current_domain  # noqa: E402
from modules.errors.models import ErrorCategory  # noqa: E402
from modules.errors.services import seed_standard_error_categories  # noqa: E402
from modules.operations.models import AuditEvent  # noqa: E402
from modules.priority.services import list_subject_priorities  # noqa: E402
from modules.questions.models import Question  # noqa: E402
from modules.questions.services import create_active  # noqa: E402
from modules.reviews.models import ReviewScheduleChange  # noqa: E402
from modules.reviews.selectors import list_review_queue  # noqa: E402
from modules.reviews.services import ReviewScheduleService  # noqa: E402
from modules.search.saved_filter_services import (  # noqa: E402
    SavedFilterError,
    create_saved_filter,
    validate_questions_list_payload,
)
from modules.taxonomy.exceptions import TaxonomyNotFoundError  # noqa: E402
from modules.taxonomy.models import Subject  # noqa: E402
from modules.taxonomy.services import create_discipline, create_subject  # noqa: E402
from shared.domain.time import FixedClock, Instant  # noqa: E402

CLOCK = FixedClock(Instant(datetime(2026, 9, 24, 15, tzinfo=UTC)))


def assert_database() -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_user, session_user, "
            "pg_get_userbyid(d.datdba), r.rolsuper, current_setting('server_version') "
            "FROM pg_database d JOIN pg_roles r ON r.rolname = current_user "
            "WHERE d.datname = current_database()"
        )
        observed = cursor.fetchone()
    assert observed is not None
    assert observed[:5] == (DATABASE, ROLE, "postgres", ROLE, False), observed
    assert connection.vendor == "postgresql"


def rejected_by_db(operation: Callable[[], object]) -> None:
    try:
        with transaction.atomic():
            operation()
    except IntegrityError:
        return
    raise AssertionError("A constraint PostgreSQL não rejeitou a alteração inválida.")


def sql(statement: str, parameters: list[Any]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(statement, parameters)


def workspace(name: str) -> Workspace:
    user = User.objects.create_user(email=f"pg-s8-{name}@example.test")
    result = Workspace.objects.create(owner_user=user, name=f"S8 {name}", timezone_name="UTC")
    seed_standard_error_categories(result)
    return result


def question(owner: Workspace, name: str) -> Question:
    discipline = create_discipline(workspace_id=owner.id, name=f"PG Discipline {name}")
    subject = create_subject(
        workspace_id=owner.id, discipline_id=discipline.id, name=f"PG Subject {name}"
    )
    return create_active(
        workspace_id=owner.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem=f"Synthetic S8 {name}",
        alternatives=["Wrong", "Correct"],
        correct_alternative_position=2,
        clock=CLOCK,
    )


def check_row_lock(question_id: uuid.UUID) -> None:
    options = f"-c role={ROLE}"
    with (
        psycopg.connect(
            host="127.0.0.1", port=5432, user="postgres", dbname=DATABASE, options=options
        ) as first,
        psycopg.connect(
            host="127.0.0.1", port=5432, user="postgres", dbname=DATABASE, options=options
        ) as second,
    ):
        first.execute("SELECT id FROM questions_question WHERE id = %s FOR UPDATE", (question_id,))
        second.execute("SET LOCAL lock_timeout = '200ms'")
        try:
            second.execute(
                "SELECT id FROM questions_question WHERE id = %s FOR UPDATE", (question_id,)
            )
        except psycopg.errors.LockNotAvailable:
            second.rollback()
        else:
            raise AssertionError("FOR UPDATE não bloqueou a segunda conexão.")
        first.commit()
        row = second.execute(
            "SELECT id FROM questions_question WHERE id = %s FOR UPDATE", (question_id,)
        ).fetchone()
        assert row is not None


def main() -> None:
    assert_database()
    executor = MigrationExecutor(connection)
    executor.migrate(executor.loader.graph.leaf_nodes())
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM django_migrations")
        migration_count = cursor.fetchone()[0]
    assert migration_count == 34
    assert User.objects.count() == 0
    first = workspace("first")
    item = question(first, "first")
    second = workspace("second")
    foreign = question(second, "second")
    revision = item.revisions.get(is_current=True)
    review = item.reviews.get()
    attempt = Attempt.objects.create(
        workspace=first,
        question=item,
        question_revision=revision,
        attempt_type="INITIAL",
        selected_alternative=revision.alternatives.get(position=1),
        is_correct=False,
        occurred_at=datetime(2026, 9, 24, 15, tzinfo=UTC),
        timezone_name="UTC",
        local_date=date(2026, 9, 24),
        idempotency_key=uuid.uuid4(),
    )
    receipt = OperationReceipt.objects.create(
        workspace=first,
        operation_kind="INITIAL_ERROR",
        idempotency_key=attempt.idempotency_key,
        request_hash="a" * 64,
        result_entity_type="ATTEMPT",
        result_entity_id=attempt.id,
    )
    sql(
        "UPDATE attempts_operationreceipt SET created_at = %s WHERE id = %s",
        [datetime(2026, 8, 1, 15, tzinfo=UTC), receipt.id],
    )
    receipt.refresh_from_db()
    assert receipt.minimum_retention_until < CLOCK.now().value
    assert (
        OperationReceipt.objects.resolve_existing(
            workspace_id=first.id,
            operation_kind="INITIAL_ERROR",
            idempotency_key=attempt.idempotency_key,
            request_hash="a" * 64,
        ).id
        == receipt.id
    )
    try:
        OperationReceipt.objects.resolve_existing(
            workspace_id=first.id,
            operation_kind="INITIAL_ERROR",
            idempotency_key=attempt.idempotency_key,
            request_hash="b" * 64,
        )
    except IdempotencyConflictError:
        pass
    else:
        raise AssertionError("Hash divergente não gerou conflito idempotente.")

    rejected_by_db(
        lambda: sql(
            "UPDATE questions_question SET discipline_id = %s WHERE id = %s",
            [uuid.uuid4(), item.id],
        )
    )
    rejected_by_db(
        lambda: sql("UPDATE attempts_attempt SET status = 'VOIDED' WHERE id = %s", [attempt.id])
    )
    rejected_by_db(
        lambda: Attempt.objects.bulk_create(
            [
                Attempt(
                    workspace=first,
                    question=item,
                    question_revision=revision,
                    attempt_type="INITIAL",
                    selected_alternative=revision.alternatives.get(position=1),
                    is_correct=False,
                    occurred_at=CLOCK.now().value,
                    timezone_name="UTC",
                    local_date=date(2026, 9, 24),
                    idempotency_key=uuid.uuid4(),
                )
            ]
        )
    )
    rejected_by_db(
        lambda: sql("UPDATE questions_question SET workspace_id = NULL WHERE id = %s", [item.id])
    )
    standard = ErrorCategory.objects.get(workspace=first, code="ATTENTION")
    rejected_by_db(
        lambda: sql(
            "UPDATE errors_error_category SET state = 'ARCHIVED' WHERE id = %s", [standard.id]
        )
    )
    personal_a, personal_b = ErrorCategory.objects.bulk_create(
        [
            ErrorCategory(
                workspace=first,
                code=f"PERSONAL_{uuid.uuid4().hex.upper()}",
                display_name=name,
                name_key=name.casefold(),
                category_kind="PERSONAL",
                state="ACTIVE",
            )
            for name in ("Alpha", "Beta")
        ]
    )
    rejected_by_db(
        lambda: sql(
            "UPDATE errors_error_category SET name_key = %s WHERE id = %s",
            [personal_a.name_key, personal_b.id],
        )
    )
    rejected_by_db(
        lambda: OperationReceipt.objects.create(
            workspace=first,
            operation_kind="INITIAL_ERROR",
            idempotency_key=attempt.idempotency_key,
            request_hash="a" * 64,
            result_entity_type="ATTEMPT",
            result_entity_id=attempt.id,
        )
    )
    rejected_by_db(
        lambda: sql(
            "INSERT INTO reviews_review (id, workspace_id, review_cycle_id, question_id, "
            "sequence_number, stage_code, state, first_due_date, current_due_date, "
            "scheduled_from_attempt_id, transition_code, policy_code, lock_version, "
            "created_at, updated_at) "
            "SELECT %s, workspace_id, review_cycle_id, question_id, 2, 'D7', 'PENDING', "
            "first_due_date, current_due_date, %s, 'ADVANCE_D1_TO_D7', policy_code, 1, "
            "created_at, updated_at FROM reviews_review WHERE id = %s",
            [uuid.uuid4(), attempt.id, review.id],
        )
    )
    rejected_by_db(
        lambda: sql(
            "UPDATE reviews_reviewcycle SET origin_kind = 'MANUAL' WHERE id = %s",
            [review.review_cycle_id],
        )
    )
    rejected_by_db(
        lambda: sql(
            "INSERT INTO operations_auditevent "
            "(id, workspace_id, event_code, entity_type, entity_id, correlation_id, "
            "reason_code, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            [
                uuid.uuid4(),
                first.id,
                "QUESTION_PERMANENTLY_DELETED",
                "QUESTION",
                item.id,
                uuid.uuid4(),
                "USER_REQUEST",
                CLOCK.now().value,
            ],
        )
    )
    assert item.subject_id is not None and item.discipline_id is not None
    assert foreign.discipline_id is not None
    with transaction.atomic():
        sql(
            "UPDATE taxonomy_subject SET discipline_id = %s WHERE id = %s",
            [foreign.discipline_id, item.subject_id],
        )
        transaction.set_rollback(True)
    assert Subject.objects.get(pk=item.subject_id).discipline_id == item.discipline_id
    try:
        create_subject(workspace_id=first.id, discipline_id=foreign.discipline_id, name="Foreign")
    except TaxonomyNotFoundError:
        pass
    else:
        raise AssertionError("Guard de taxonomia aceitou disciplina estrangeira.")

    valid_filter = create_saved_filter(
        workspace_id=first.id,
        owner_user_id=first.owner_user_id,
        name="PG Filter",
        payload={"status": "ACTIVE", "discipline": str(item.discipline_id)},
    )
    assert isinstance(valid_filter.payload, dict)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name = 'search_savedfilter' AND column_name = 'payload'"
        )
        assert cursor.fetchone() == ("jsonb",)
    for payload in (
        {"future_field": "unknown"},
        {"discipline": str(foreign.discipline_id)},
        {"error_category": str(second.error_categories.get(code="ATTENTION").id)},
    ):
        try:
            validate_questions_list_payload(payload, workspace_id=first.id)
        except SavedFilterError:
            pass
        else:
            raise AssertionError("Validator aceitou payload inválido no PostgreSQL.")

    event = MasteryStateEvent.objects.create(
        workspace=first,
        question=item,
        sequence=1,
        event_type="DOMINATED",
        formula_code="DOM-HEUR-1.0",
        evaluated_on=date(2026, 9, 24),
        occurred_at=CLOCK.now().value,
    )
    rejected_by_db(
        lambda: sql(
            "UPDATE domain_masterystateevent SET event_type = 'MANUAL_REOPENED' WHERE id = %s",
            [event.id],
        )
    )
    assert (
        current_domain(workspace_id=first.id, question_id=item.id, clock=CLOCK).result.question_id
        == item.id
    )
    priorities = list_subject_priorities(workspace_id=first.id, clock=CLOCK)
    assert not priorities.ranked and len(priorities.collect_more_evidence) == 1
    queue = list_review_queue(workspace_id=first.id, clock=CLOCK)
    assert queue.overdue.total == 0 and queue.due.total == 0 and queue.future.total == 1
    other = question(first, "ordering")
    assert other.subject_id is not None
    ordered_priorities = list_subject_priorities(workspace_id=first.id, clock=CLOCK)
    subject_ids = tuple(row.subject.id for row in ordered_priorities.collect_more_evidence)
    assert subject_ids == tuple(sorted((item.subject_id, other.subject_id)))
    assert subject_ids == tuple(
        row.subject.id
        for row in list_subject_priorities(workspace_id=first.id, clock=CLOCK).collect_more_evidence
    )
    ordered_queue = list_review_queue(workspace_id=first.id, clock=CLOCK)
    assert ordered_queue.future.total == 2
    queue_keys = tuple(
        (row.current_due_date, row.created_at, row.id) for row in ordered_queue.future.entries
    )
    assert queue_keys == tuple(sorted(queue_keys))
    assert queue_keys == tuple(
        (row.current_due_date, row.created_at, row.id)
        for row in list_review_queue(workspace_id=first.id, clock=CLOCK).future.entries
    )

    original_due = review.current_due_date
    original_version = review.lock_version
    schedule_count = ReviewScheduleChange.objects.count()
    audit_count = AuditEvent.objects.count()
    with patch("modules.reviews.services.record_audit_event", side_effect=RuntimeError("S8 fault")):
        try:
            ReviewScheduleService(workspace_id=first.id, clock=CLOCK).reschedule(
                review_id=review.id,
                new_due_date=date(2026, 9, 26),
                reason_code="STUDY_PLAN",
                expected_lock_version=original_version,
            )
        except RuntimeError:
            pass
        else:
            raise AssertionError("Falha injetada não abortou transação.")
    review.refresh_from_db()
    assert (review.current_due_date, review.lock_version) == (original_due, original_version)
    assert ReviewScheduleChange.objects.count() == schedule_count
    assert AuditEvent.objects.count() == audit_count

    def fail_after_void(phase: str) -> None:
        if phase == "after_void":
            raise RuntimeError("S8 fault")

    try:
        AttemptCorrectionService(workspace_id=first.id, clock=CLOCK).void(
            attempt_id=attempt.id,
            expected_tip_id=attempt.id,
            reason_code="S8_FAULT_PROBE",
            fault_hook=fail_after_void,
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("Falha de correção S2B não abortou transação.")
    attempt.refresh_from_db()
    assert attempt.status == "VALID"
    assert AuditEvent.objects.count() == audit_count

    check_row_lock(item.id)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(*) FROM pg_constraint WHERE connamespace = 'public'::regnamespace"
        )
        constraint_count = cursor.fetchone()[0]
    assert constraint_count > 0
    print(
        json.dumps(
            {
                "status": "PASS",
                "server_version": "18.6",
                "backend": connection.vendor,
                "database": DATABASE,
                "effective_role": ROLE,
                "migration_count": migration_count,
                "constraint_count": constraint_count,
                "checks": [
                    "FK",
                    "partial_unique_review",
                    "partial_unique_initial_attempt",
                    "partial_unique_category",
                    "unique_receipt",
                    "CHECK_attempt",
                    "CHECK_category",
                    "CHECK_review_cycle",
                    "CHECK_audit",
                    "CHECK_mastery",
                    "nullability",
                    "cross_workspace_guard",
                    "JSONB_and_validator",
                    "transaction_rollback",
                    "S2B_void_rollback",
                    "row_lock",
                    "ordering",
                    "receipt_after_30_days",
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
