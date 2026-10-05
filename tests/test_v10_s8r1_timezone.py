"""Fixed-UTC synthetic regression vectors for approved S8R1 timezone semantics."""

import hashlib
import io
import json
import sqlite3
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from threading import Barrier
from typing import Any, cast
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command
from django.db import OperationalError, connection, connections
from django.db.migrations.executor import MigrationExecutor

from modules.accounts import services as account_services
from modules.accounts.exceptions import WorkspaceAccessDenied, WorkspaceConcurrencyError
from modules.accounts.models import User, Workspace
from modules.accounts.services import change_workspace_timezone
from modules.attempts.context import ContextStore
from modules.attempts.corrections import AttemptCorrectionService
from modules.attempts.models import Attempt, AttemptType
from modules.data_management.portability import (
    ExportValidationError,
    ValidatedExport,
    export_bytes,
    export_workspace,
    import_into_empty,
    validate_export,
)
from modules.data_management.services import create_sqlite_backup, restore_sqlite_backup
from modules.domain.models import MasteryStateEvent
from modules.domain.services import DomainLifecycleService, current_domain
from modules.errors.services import seed_standard_error_categories
from modules.operations import integrity
from modules.operations.integrity import run_integrity_check
from modules.operations.models import AuditEvent
from modules.priority.services import list_subject_priorities
from modules.questions.models import Question
from modules.questions.services import create_active
from modules.reviews.models import Review, ReviewCycle, ReviewScheduleChange, ReviewState
from modules.reviews.policies import ReviewSchedulePolicy, ReviewStage
from modules.reviews.services import (
    CompleteReviewService,
    ManualReviewInclusionService,
    ReviewScheduleService,
)
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import Calendar, FixedClock, Instant, LocalDate, TimeZoneId

ACRE = "Brazil/Acre"
SP = "America/Sao_Paulo"
BOUNDARY = datetime(2026, 10, 5, 4, tzinfo=UTC)
EVALUATION = datetime(2026, 10, 5, 12, tzinfo=UTC)


def _clock(at: datetime) -> FixedClock:
    return FixedClock(Instant(at))


def _workspace() -> tuple[Workspace, uuid.UUID, uuid.UUID]:
    owner = User.objects.create_user(email=f"s8r1-{uuid.uuid4()}@example.test")
    workspace = Workspace.objects.create(
        owner_user=owner, name="Synthetic S8R1", timezone_name=ACRE
    )
    seed_standard_error_categories(workspace)
    discipline = create_discipline(workspace_id=workspace.id, name="Synthetic discipline")
    subject = create_subject(workspace_id=workspace.id, discipline_id=discipline.id, name="Subject")
    return workspace, discipline.id, subject.id


def _question(
    workspace: Workspace, discipline: uuid.UUID, subject: uuid.UUID, at: datetime
) -> Question:
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline,
        subject_id=subject,
        stem="Synthetic question",
        alternatives=["Correct", "Wrong"],
        correct_alternative_position=1,
        clock=_clock(at),
    )


def _switch(workspace: Workspace, at: datetime = EVALUATION) -> None:
    result = change_workspace_timezone(
        actor_user_id=workspace.owner_user_id,
        workspace_id=workspace.id,
        timezone_id=SP,
        expected_lock_version=workspace.lock_version,
        confirmed=True,
        clock=_clock(at),
    )
    assert result.changed
    workspace.refresh_from_db()


def _attempt(
    workspace: Workspace, question: Question, at: datetime, review: Review | None = None
) -> Attempt:
    revision = question.revisions.get(is_current=True)
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        review=review,
        attempt_type=AttemptType.REVIEW if review else AttemptType.INITIAL,
        selected_alternative=revision.alternatives.get(position=1),
        is_correct=True,
        occurred_at=at,
        timezone_name=workspace.timezone_name,
        local_date=at.astimezone(ZoneInfo(workspace.timezone_name)).date(),
        idempotency_key=uuid.uuid4(),
    )


def _completed(workspace: Workspace, question: Question, review: Review, at: datetime) -> Attempt:
    attempt = _attempt(workspace, question, at, review)
    Review.objects.filter(pk=review.id).update(state=ReviewState.COMPLETED, completed_at=at)
    return attempt


@pytest.mark.django_db(transaction=True)
def test_r1_inaugural_boundary_does_not_reinterpret_workspace_timezone() -> None:
    workspace, discipline, subject = _workspace()
    question = _question(workspace, discipline, subject, BOUNDARY)
    due = question.reviews.get().first_due_date
    assert due == date(2026, 10, 5)
    assert run_integrity_check(now=EVALUATION).total_findings == 0
    _switch(workspace)
    after = run_integrity_check(now=EVALUATION)
    assert after.total_findings == 0
    question.reviews.get().refresh_from_db()
    assert question.reviews.get().first_due_date == due


@pytest.mark.parametrize(
    "old_at",
    [
        datetime(2026, 9, 6, 4, tzinfo=UTC),
        datetime(2026, 8, 7, 4, tzinfo=UTC),
        datetime(2026, 7, 8, 4, tzinfo=UTC),
        *(EVALUATION - timedelta(days=age) for age in (0, 29, 30, 59, 60, 89, 90)),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_r2_priority_membership_uses_the_historical_civil_date(old_at: datetime) -> None:
    workspace, discipline, subject = _workspace()
    start = datetime(2026, 6, 1, 12, tzinfo=UTC)
    recent = datetime(2026, 10, 4, 12, tzinfo=UTC)
    for _ in range(3):
        question = _question(workspace, discipline, subject, start)
        _attempt(workspace, question, start)
        d1 = question.reviews.get()
        prior = _completed(workspace, question, d1, old_at)
        d7 = Review.objects.create(
            workspace=workspace,
            question=question,
            review_cycle=d1.review_cycle,
            sequence_number=2,
            stage_code="D7",
            first_due_date=prior.local_date + timedelta(days=7),
            current_due_date=prior.local_date + timedelta(days=7),
            scheduled_from_attempt=prior,
            transition_code="ADVANCE_D1_TO_D7",
        )
        recent_attempt = _completed(workspace, question, d7, recent)
        Review.objects.create(
            workspace=workspace,
            question=question,
            review_cycle=d1.review_cycle,
            sequence_number=3,
            stage_code="D14",
            first_due_date=recent_attempt.local_date + timedelta(days=14),
            current_due_date=recent_attempt.local_date + timedelta(days=14),
            scheduled_from_attempt=recent_attempt,
            transition_code="ADVANCE_D7_TO_D14",
        )
    before = list_subject_priorities(workspace_id=workspace.id, clock=_clock(EVALUATION))
    before_result = (*before.ranked, *before.collect_more_evidence)[0].result
    historical_age = (date(2026, 10, 5) - old_at.astimezone(ZoneInfo(ACRE)).date()).days
    assert before_result.recurrence_eligible_count == (3 if historical_age <= 89 else 0)
    assert before_result.comparable_question_count == (3 if 30 <= historical_age <= 59 else 0)
    _switch(workspace)
    after = list_subject_priorities(workspace_id=workspace.id, clock=_clock(EVALUATION))
    after_result = (*after.ranked, *after.collect_more_evidence)[0].result
    assert before.evaluated_on == after.evaluated_on == date(2026, 10, 5)
    assert before_result.recurrence_eligible_count == after_result.recurrence_eligible_count
    assert before_result.comparable_question_count == after_result.comparable_question_count
    assert before_result == after_result


@pytest.mark.django_db(transaction=True)
def test_r3_new_review_replacement_uses_current_context_for_attempt_and_schedule() -> None:
    workspace, discipline, subject = _workspace()
    start = datetime(2026, 9, 20, 12, tzinfo=UTC)
    question = _question(workspace, discipline, subject, start)
    _attempt(workspace, question, start)
    d1 = question.reviews.get()
    prior = _completed(workspace, question, d1, datetime(2026, 9, 21, 12, tzinfo=UTC))
    Review.objects.create(
        workspace=workspace,
        question=question,
        review_cycle=d1.review_cycle,
        sequence_number=2,
        stage_code="D7",
        first_due_date=prior.local_date + timedelta(days=7),
        current_due_date=prior.local_date + timedelta(days=7),
        scheduled_from_attempt=prior,
        transition_code="ADVANCE_D1_TO_D7",
    )
    original = (prior.occurred_at, prior.timezone_name, prior.local_date, prior.is_correct)
    _switch(workspace, BOUNDARY)
    result = AttemptCorrectionService(workspace_id=workspace.id, clock=_clock(BOUNDARY)).replace(
        attempt_id=prior.id,
        expected_tip_id=prior.id,
        selected_alternative_id=prior.selected_alternative_id,
        reason_code="RESULT_CORRECTION",
    )
    assert result.replacement_attempt_id is not None
    replacement = Attempt.objects.get(pk=result.replacement_attempt_id)
    assert replacement.timezone_name == SP
    assert replacement.local_date == date(2026, 10, 5)
    assert result.reconstruction.current_review_id is not None
    new_review = Review.objects.get(pk=result.reconstruction.current_review_id)
    assert new_review.first_due_date == replacement.local_date + timedelta(days=7)
    prior.refresh_from_db()
    assert (prior.occurred_at, prior.timezone_name, prior.local_date, prior.is_correct) == original
    assert prior.status == "VOIDED"
    assert run_integrity_check(now=EVALUATION).total_findings == 0


@pytest.mark.parametrize(
    "at,acre_day,sp_day",
    [
        (datetime(2026, 10, 5, 2, 59, 59, tzinfo=UTC), 4, 4),
        (datetime(2026, 10, 5, 3, tzinfo=UTC), 4, 5),
        (BOUNDARY, 4, 5),
        (datetime(2026, 10, 5, 4, 59, 59, tzinfo=UTC), 4, 5),
        (datetime(2026, 10, 5, 5, tzinfo=UTC), 5, 5),
        (EVALUATION, 5, 5),
    ],
)
@pytest.mark.django_db(transaction=True)
def test_t2_t9_t10_fixed_boundaries_preserve_history_and_new_context(
    at: datetime,
    acre_day: int,
    sp_day: int,
) -> None:
    workspace, discipline, subject = _workspace()
    question = _question(workspace, discipline, subject, at)
    initial = _attempt(workspace, question, at)
    d1 = question.reviews.get()
    prior = _completed(workspace, question, d1, at)
    Review.objects.create(
        workspace=workspace,
        question=question,
        review_cycle=d1.review_cycle,
        sequence_number=2,
        stage_code="D7",
        first_due_date=prior.local_date + timedelta(days=7),
        current_due_date=prior.local_date + timedelta(days=7),
        scheduled_from_attempt=prior,
        transition_code="ADVANCE_D1_TO_D7",
    )
    models = (Attempt, Review, ReviewCycle, AuditEvent, ReviewScheduleChange, Question)
    before = {model: list(model.objects.order_by("pk").values()) for model in models}
    path = Path(connection.settings_dict["NAME"]).resolve()
    all_before = _all_tables_except_workspace(path)
    old_ws: dict[str, Any] = dict(Workspace.objects.values().get(pk=workspace.id))
    assert initial.local_date == date(2026, 10, acre_day)
    _switch(workspace)
    assert before == {model: list(model.objects.order_by("pk").values()) for model in models}
    assert all_before == _all_tables_except_workspace(path)
    new_ws: dict[str, Any] = dict(Workspace.objects.values().get(pk=workspace.id))
    assert {key for key in old_ws if old_ws[key] != new_ws[key]} == {
        "timezone_name",
        "lock_version",
        "updated_at",
    }
    fresh = _question(workspace, discipline, subject, at)
    fresh_attempt = _attempt(workspace, fresh, at)
    assert fresh_attempt.local_date == date(2026, 10, sp_day)
    assert fresh_attempt.timezone_name == SP
    assert fresh.reviews.get().first_due_date == date(2026, 10, sp_day) + timedelta(days=1)
    assert run_integrity_check(now=EVALUATION).total_findings == 0


@pytest.mark.django_db(transaction=True)
def test_t1_empty_workspace_and_rejections_do_not_create_facts() -> None:
    owner = User.objects.create_user(email="s8r1-empty@example.test")
    ws = Workspace.objects.create(owner_user=owner, name="Empty", timezone_name=ACRE)
    for zone, confirmed in ((SP, False), (ACRE, True)):
        result = change_workspace_timezone(
            actor_user_id=owner.id,
            workspace_id=ws.id,
            timezone_id=zone,
            expected_lock_version=ws.lock_version,
            confirmed=confirmed,
            clock=_clock(EVALUATION),
        )
        assert not result.changed
    before = Workspace.objects.values().get(pk=ws.id)
    with pytest.raises(ValueError):
        change_workspace_timezone(
            actor_user_id=owner.id,
            workspace_id=ws.id,
            timezone_id="Invalid/Synthetic",
            expected_lock_version=ws.lock_version,
            confirmed=True,
            clock=_clock(EVALUATION),
        )
    with pytest.raises(WorkspaceAccessDenied):
        change_workspace_timezone(
            actor_user_id=uuid.uuid4(),
            workspace_id=ws.id,
            timezone_id=SP,
            expected_lock_version=ws.lock_version,
            confirmed=True,
            clock=_clock(EVALUATION),
        )
    with pytest.raises(WorkspaceConcurrencyError):
        change_workspace_timezone(
            actor_user_id=owner.id,
            workspace_id=ws.id,
            timezone_id=SP,
            expected_lock_version=ws.lock_version + 1,
            confirmed=True,
            clock=_clock(EVALUATION),
        )
    assert before == Workspace.objects.values().get(pk=ws.id)
    _switch(ws)
    assert not Attempt.objects.exists() and not Review.objects.exists()
    check = run_integrity_check(now=EVALUATION)
    assert (check.checks_executed, check.total_findings, check.total_limited_verifications) == (
        25,
        0,
        0,
    )


@pytest.mark.django_db(transaction=True)
def test_t3_t4_manual_context_is_limited_and_schedule_history_is_preserved() -> None:
    ws, discipline, subject = _workspace()
    q = _question(ws, discipline, subject, BOUNDARY)
    initial = _attempt(ws, q, BOUNDARY)
    d1 = q.reviews.get()
    _completed(ws, q, d1, BOUNDARY)
    ReviewCycle.objects.filter(pk=d1.review_cycle_id).update(
        state="SUPERSEDED", superseded_at=BOUNDARY
    )
    _switch(ws)
    cycle = ManualReviewInclusionService(workspace_id=ws.id, clock=_clock(BOUNDARY)).include(
        question_id=q.id,
        reason_code="STUDY_PLAN",
    )
    assert cycle.origin_attempt_id == initial.id
    review = cycle.reviews.get()
    assert review.first_due_date == date(2026, 10, 6)
    schedule = ReviewScheduleService(workspace_id=ws.id, clock=_clock(BOUNDARY))
    schedule.reschedule(
        review_id=review.id,
        new_due_date=date(2026, 10, 7),
        reason_code="STUDY_PLAN",
        expected_lock_version=review.lock_version,
    )
    history = list(ReviewScheduleChange.objects.values())
    audit = list(AuditEvent.objects.order_by("pk").values())
    change_workspace_timezone(
        actor_user_id=ws.owner_user_id,
        workspace_id=ws.id,
        timezone_id=ACRE,
        expected_lock_version=ws.lock_version,
        confirmed=True,
        clock=_clock(EVALUATION),
    )
    assert history == list(ReviewScheduleChange.objects.values())
    assert audit == list(AuditEvent.objects.order_by("pk").values())
    assert history[0]["timezone_name"] == SP
    check = run_integrity_check(now=EVALUATION)
    assert check.total_findings == 0 and check.total_limited_verifications == 2
    assert {item.reason_code for item in check.limited_verifications} == {
        "TIMEZONE_CONTEXT_UNAVAILABLE"
    }


@pytest.mark.parametrize(
    "stage,correct,offset",
    [
        ("D1", True, 7),
        ("D7", True, 14),
        ("D14", True, 30),
        ("D1", False, 1),
        ("D7", False, 1),
        ("D14", False, 1),
        ("D30", False, 1),
        ("D30", True, None),
    ],
)
def test_t5_schedule_uses_civil_response_date(
    stage: str, correct: bool, offset: int | None
) -> None:
    clock = _clock(BOUNDARY)
    policy = ReviewSchedulePolicy(clock=clock, calendar=Calendar(clock))
    for zone, base in ((ACRE, date(2026, 10, 4)), (SP, date(2026, 10, 5))):
        result = policy.decide(
            current_stage=ReviewStage(stage), is_correct=correct, time_zone_id=TimeZoneId(zone)
        )
        if offset is None:
            assert result.next_due_date is None and result.cycle_state == "COMPLETED"
        else:
            assert result.next_due_date == LocalDate(base + timedelta(days=offset))


@pytest.mark.django_db(transaction=True)
def test_t7_domain_changes_only_with_evaluation_date_not_old_context() -> None:
    ws, discipline, subject = _workspace()
    q = _question(ws, discipline, subject, BOUNDARY - timedelta(days=60))
    prior = _attempt(ws, q, BOUNDARY - timedelta(days=60))
    before = current_domain(workspace_id=ws.id, question_id=q.id, clock=_clock(EVALUATION))
    _switch(ws)
    after = current_domain(workspace_id=ws.id, question_id=q.id, clock=_clock(EVALUATION))
    assert before == after
    prior.refresh_from_db()
    assert prior.local_date == date(2026, 8, 5)
    early = current_domain(workspace_id=ws.id, question_id=q.id, clock=_clock(BOUNDARY))
    assert early.evaluated_on == date(2026, 10, 5)


def _local_workspace() -> tuple[Workspace, uuid.UUID, uuid.UUID]:
    ws = bootstrap_local_workspace(timezone_id=ACRE).workspace
    discipline = create_discipline(workspace_id=ws.id, name="Synthetic local")
    subject = create_subject(workspace_id=ws.id, discipline_id=discipline.id, name="Local subject")
    return ws, discipline.id, subject.id


def _all_tables_except_workspace(path: Path) -> dict[str, list[tuple[Any, ...]]]:
    with closing(sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)) as database:
        result = {}
        names = database.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        for (name,) in names:
            if name == "accounts_workspace":
                continue
            quoted = '"' + name.replace('"', '""') + '"'
            result[name] = sorted(database.execute(f"SELECT * FROM {quoted}").fetchall(), key=str)  # noqa: S608 -- quoted table from SQLite schema
        return result


def _fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("invalid", [False, True])
def test_t8_checker_and_projection_zero_native_dml(
    monkeypatch: pytest.MonkeyPatch,
    invalid: bool,
) -> None:
    ws, discipline, subject = _workspace()
    q = _question(ws, discipline, subject, BOUNDARY)
    attempt = _attempt(ws, q, BOUNDARY)
    _switch(ws)
    if invalid:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE attempts_attempt SET local_date = %s WHERE id = %s",
                ["2026-10-05", attempt.id.hex],
            )
    path = Path(connection.settings_dict["NAME"]).resolve()
    assert path.name == "test.sqlite3" and "development.sqlite3" not in str(path)
    before = _fingerprint(path)
    attempted: list[str] = []
    completed: list[str] = []
    native: list[int] = []
    original_connect = sqlite3.connect

    class RecordingConnection(sqlite3.Connection):
        def execute(self, sql: str, parameters: Any = (), /) -> sqlite3.Cursor:
            verb = sql.lstrip().split()[0].upper()
            if verb in {"INSERT", "UPDATE", "DELETE"}:
                attempted.append(verb)
            result = super().execute(sql, parameters)
            if verb in {"INSERT", "UPDATE", "DELETE"}:
                completed.append(verb)
            return result

        def close(self) -> None:
            native.append(self.total_changes)
            super().close()

    def traced_connect(*args: Any, **kwargs: Any) -> sqlite3.Connection:
        assert "mode=ro" in args[0]
        kwargs["factory"] = RecordingConnection
        return cast(sqlite3.Connection, original_connect(*args, **kwargs))

    monkeypatch.setattr(sqlite3, "connect", traced_connect)
    check = run_integrity_check(now=EVALUATION)
    with closing(traced_connect(f"{path.as_uri()}?mode=ro", uri=True)) as database:
        full_projection = integrity.check_integrity_projection(database, now=EVALUATION)
        assert full_projection == check
        projection = integrity.invariant_python_result(database, ("WS-003", "ATT-002", "REV-004"))
        for _, rule in integrity.invariant_sql_rules(("REV-001", "REV-002", "REV-003", "REV-004")):
            database.execute(rule).fetchall()
    assert ("ATT-002" in projection.violations) == invalid
    assert (check.total_findings > 0) == invalid
    assert check.checks_executed == 25 and check.total_limited_verifications == 1
    assert attempted == completed == [] and native == [0, 0]
    assert _fingerprint(path) == before


@pytest.mark.django_db(transaction=True)
def test_t8_cli_reports_limitation_separately() -> None:
    ws, discipline, subject = _workspace()
    _question(ws, discipline, subject, BOUNDARY)
    _switch(ws)
    output = io.StringIO()
    call_command("check_integrity", stdout=output)
    assert "Limited verifications: 1" in output.getvalue()
    assert "TIMEZONE_CONTEXT_UNAVAILABLE" in output.getvalue()


@pytest.mark.django_db(transaction=True)
def test_t11_initial_replacement_preserves_old_facts_and_captures_new_zone() -> None:
    ws, discipline, subject = _workspace()
    q = _question(ws, discipline, subject, BOUNDARY)
    initial = _attempt(ws, q, BOUNDARY)
    old = (
        initial.occurred_at,
        initial.timezone_name,
        initial.local_date,
        initial.is_correct,
        initial.question_id,
        initial.question_revision_id,
        initial.selected_alternative_id,
    )
    _switch(ws)
    result = AttemptCorrectionService(workspace_id=ws.id, clock=_clock(BOUNDARY)).replace(
        attempt_id=initial.id,
        expected_tip_id=initial.id,
        selected_alternative_id=initial.selected_alternative_id,
        reason_code="RESULT_CORRECTION",
    )
    assert result.replacement_attempt_id is not None
    replacement = Attempt.objects.get(pk=result.replacement_attempt_id)
    initial.refresh_from_db()
    assert old == (
        initial.occurred_at,
        initial.timezone_name,
        initial.local_date,
        initial.is_correct,
        initial.question_id,
        initial.question_revision_id,
        initial.selected_alternative_id,
    )
    assert initial.status == "VOIDED"
    assert replacement.timezone_name == SP and replacement.local_date == date(2026, 10, 5)
    assert run_integrity_check(now=EVALUATION).total_findings == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "producer,policy",
    [
        ("V0.5", "PRI-HEUR-1.0"),
        ("V1.0", "PRI-HEUR-1.0"),
        ("V1.0", "PRI-HEUR-1.1"),
    ],
)
def test_t12_compatible_packages_import_without_remapping(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    django_db_blocker: Any,
    producer: str,
    policy: str,
) -> None:
    ws, discipline, subject = _local_workspace()
    q = _question(ws, discipline, subject, BOUNDARY)
    _attempt(ws, q, BOUNDARY)
    _switch(ws)
    raw = export_bytes(workspace_id=ws.id)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    manifest = json.loads(entries["manifest.json"])
    assert (
        manifest["format_version"] == "1.0" and manifest["policies"]["priority"] == "PRI-HEUR-1.1"
    )
    manifest["application_version"] = producer
    manifest["policies"]["priority"] = policy
    entries["manifest.json"] = json.dumps(manifest).encode()
    rewritten = io.BytesIO()
    with zipfile.ZipFile(rewritten, "w") as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    package = validate_export(io.BytesIO(rewritten.getvalue()))
    assert len(package.limited_verifications) == 1
    alias = f"s8r1_{uuid.uuid4().hex}"
    connections.databases[alias] = {
        **connections["default"].settings_dict,
        "NAME": str(tmp_path / "synthetic-import.sqlite3"),
    }
    with django_db_blocker.unblock():
        try:
            database = connections[alias]
            executor = MigrationExecutor(database)
            executor.migrate(executor.loader.graph.leaf_nodes())
            import_into_empty(package=package, database_alias=alias)
            reports = [
                record
                for record in caplog.records
                if getattr(record, "operation", None) == "cei.import.integrity"
            ]
            assert (
                reports and cast(Any, reports[-1]).technical_context["limited_verifications"] == 1
            )
            check = run_integrity_check(using=alias, now=EVALUATION)
            assert check.total_findings == 0 and check.total_limited_verifications == 1
            replay = io.BytesIO()
            export_workspace(workspace_id=ws.id, destination=replay, database_alias=alias)
            revalidated = validate_export(io.BytesIO(replay.getvalue()))
            assert package.rows == revalidated.rows
            assert (
                package.manifest["schema_migrations"] == revalidated.manifest["schema_migrations"]
            )
            assert revalidated.manifest["policies"]["priority"] == "PRI-HEUR-1.1"
        finally:
            connections[alias].close()
            del connections[alias]
            del connections.databases[alias]


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "producer,policy",
    [
        ("V1.0", "PRI-HEUR-9.9"),
        ("V0.5", "PRI-HEUR-1.1"),
    ],
)
def test_t12_unknown_policy_is_rejected_before_destination_dml(producer: str, policy: str) -> None:
    ws, discipline, subject = _local_workspace()
    _question(ws, discipline, subject, BOUNDARY)
    package = validate_export(io.BytesIO(export_bytes(workspace_id=ws.id)))
    manifest = deepcopy(package.manifest)
    manifest["application_version"] = producer
    manifest["policies"]["priority"] = policy
    invalid = ValidatedExport(manifest=manifest, rows=package.rows)
    path = Path(connection.settings_dict["NAME"])
    before = _fingerprint(path)
    attempted: list[str] = []
    completed: list[str] = []
    assert connection.connection is not None
    native_before = connection.connection.total_changes

    def capture(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
        verb = sql.lstrip().split()[0].upper()
        if verb in {"INSERT", "UPDATE", "DELETE"}:
            attempted.append(verb)
        result = execute(sql, params, many, context)
        if verb in {"INSERT", "UPDATE", "DELETE"}:
            completed.append(verb)
        return result

    with connection.execute_wrapper(capture), pytest.raises(ExportValidationError):
        import_into_empty(package=invalid)
    assert attempted == completed == []
    assert connection.connection.total_changes - native_before == 0
    assert _fingerprint(path) == before


@pytest.mark.django_db(transaction=True)
def test_t12_synthetic_restore_uses_shared_limited_semantics(tmp_path: Path) -> None:
    ws, discipline, subject = _local_workspace()
    q = _question(ws, discipline, subject, BOUNDARY)
    _attempt(ws, q, BOUNDARY)
    _switch(ws)
    backup = tmp_path / "synthetic-backup.sqlite3"
    create_sqlite_backup(backup, now=lambda: EVALUATION)
    restored = restore_sqlite_backup(backup, tmp_path / "synthetic-restored.sqlite3")
    assert restored.integrity.checks_executed == 25
    assert restored.integrity.total_findings == 0
    assert restored.integrity.total_limited_verifications == 1


@pytest.mark.django_db(transaction=True)
def test_t13_concurrent_timezone_changes_have_one_cas_winner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ws, _, _ = _workspace()
    barrier = Barrier(2)
    original_get = account_services.get_workspace_for_owner

    def synchronized_get(**kwargs: Any) -> Workspace:
        found = original_get(**kwargs)
        barrier.wait(timeout=10)
        return found

    monkeypatch.setattr(account_services, "get_workspace_for_owner", synchronized_get)

    def update(zone: str) -> str:
        try:
            change_workspace_timezone(
                actor_user_id=ws.owner_user_id,
                workspace_id=ws.id,
                timezone_id=zone,
                expected_lock_version=ws.lock_version,
                confirmed=True,
                clock=_clock(EVALUATION),
            )
            return "CHANGED"
        except WorkspaceConcurrencyError:
            return "STALE"
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(update, zone) for zone in (SP, "UTC")]
        assert sorted(future.result(timeout=15) for future in futures) == ["CHANGED", "STALE"]
    ws.refresh_from_db()
    assert ws.lock_version == 2


@pytest.mark.parametrize(
    "at,zone,expected",
    [
        (datetime(2026, 12, 31, 23, tzinfo=UTC), SP, date(2027, 1, 1)),
        (datetime(2024, 2, 28, 12, tzinfo=UTC), SP, date(2024, 2, 29)),
        (datetime(2024, 2, 29, 12, tzinfo=UTC), SP, date(2024, 3, 1)),
        (datetime(2010, 1, 1, 3, tzinfo=UTC), ACRE, date(2010, 1, 1)),
        (datetime(2010, 1, 1, 3, tzinfo=UTC), SP, date(2010, 1, 2)),
        (datetime(2026, 3, 8, 6, 59, tzinfo=UTC), "America/New_York", date(2026, 3, 9)),
        (datetime(2026, 3, 8, 7, tzinfo=UTC), "America/New_York", date(2026, 3, 9)),
    ],
)
def test_t14_year_leap_and_historical_iana_civil_arithmetic(
    at: datetime, zone: str, expected: date
) -> None:
    calendar = Calendar(_clock(at))
    assert Calendar.add_days(calendar.today(TimeZoneId(zone)), 1).value == expected
    if zone == ACRE:
        assert calendar.today(TimeZoneId(zone)) == calendar.today(TimeZoneId("America/Rio_Branco"))


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("mutation", ["sequence", "stage", "transition", "unverifiable_date"])
def test_t8_inaugural_structure_remains_exact_and_missing_date_context_is_explicit(
    mutation: str,
) -> None:
    ws, discipline, subject = _workspace()
    q = _question(ws, discipline, subject, BOUNDARY)
    review = q.reviews.get()
    _switch(ws)
    mutations: dict[str, dict[str, Any]] = {
        "sequence": {"sequence_number": 2},
        "stage": {"stage_code": "D7"},
        "transition": {"transition_code": "MANUAL_INCLUSION_D1"},
        "unverifiable_date": {
            "first_due_date": date(2026, 10, 7),
            "current_due_date": date(2026, 10, 7),
        },
    }
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA ignore_check_constraints = ON")
        try:
            Review.objects.filter(pk=review.id).update(**mutations[mutation])
        finally:
            cursor.execute("PRAGMA ignore_check_constraints = OFF")
    checked = run_integrity_check(now=EVALUATION)
    assert (checked.total_findings > 0) == (mutation != "unverifiable_date")
    # Equal stored columns cannot tell a historical bad inaugural date from a valid one.
    if mutation == "unverifiable_date":
        assert checked.total_limited_verifications == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "offset,stage,transition",
    [
        (1, "D1", "RESET_TO_D1_AFTER_ERROR"),
        (7, "D7", "ADVANCE_D1_TO_D7"),
        (14, "D14", "ADVANCE_D7_TO_D14"),
        (30, "D30", "ADVANCE_D14_TO_D30"),
    ],
)
def test_t8_all_anchored_offsets_reject_one_day_corruption(
    offset: int, stage: str, transition: str
) -> None:
    ws, discipline, subject = _workspace()
    q = _question(ws, discipline, subject, BOUNDARY)
    initial = _attempt(ws, q, BOUNDARY)
    inaugural = q.reviews.get()
    # An ATTEMPT_CORRECTION projection has a trustworthy replacement anchor.
    Review.objects.filter(pk=inaugural.id).update(state="CANCELLED")
    ReviewCycle.objects.filter(pk=inaugural.review_cycle_id).update(
        state="SUPERSEDED", superseded_at=BOUNDARY
    )
    cycle = ReviewCycle.objects.create(
        workspace=ws,
        question=q,
        origin_attempt=initial,
        origin_question_revision=initial.question_revision,
        origin_kind="ATTEMPT_CORRECTION",
        started_at=BOUNDARY,
    )
    due = initial.local_date + timedelta(days=offset)
    r = Review.objects.create(
        workspace=ws,
        question=q,
        review_cycle=cycle,
        sequence_number=1,
        stage_code=stage,
        first_due_date=due,
        current_due_date=due,
        scheduled_from_attempt=initial,
        transition_code=transition,
    )
    _switch(ws)
    assert run_integrity_check(now=EVALUATION).total_findings == 0
    Review.objects.filter(pk=r.id).update(first_due_date=due + timedelta(days=1))
    assert "REV-004" in {
        finding.invariant_id for finding in run_integrity_check(now=EVALUATION).findings
    }


@pytest.mark.django_db(transaction=True)
def test_t13_replacement_context_survives_interleaved_workspace_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ws, discipline, subject = _workspace()
    # Distinct fixed instants make the replacement the last Domain evidence.
    # Equal timestamps would choose INITIAL/replacement by random UUID tie-break.
    activation = BOUNDARY - timedelta(days=1)
    q = _question(ws, discipline, subject, activation)
    _attempt(ws, q, activation)
    prior = _completed(ws, q, q.reviews.get(), BOUNDARY - timedelta(seconds=1))
    _switch(ws)

    def interleave(point: str) -> None:
        if point == "after_replacement":
            # Controlled interleaving exercises the gap without adding global locks.
            change_workspace_timezone(
                actor_user_id=ws.owner_user_id,
                workspace_id=ws.id,
                timezone_id=ACRE,
                expected_lock_version=ws.lock_version,
                confirmed=True,
                clock=_clock(BOUNDARY),
            )

    from modules.reviews.reconstruction import AttemptDerivedStateRebuilder

    rebuild = AttemptDerivedStateRebuilder.rebuild
    observed: list[date] = []

    def inspect_schedule(
        self: AttemptDerivedStateRebuilder, *, voided: Attempt, replacement: Attempt | None
    ) -> Any:
        result = rebuild(self, voided=voided, replacement=replacement)
        assert replacement is not None and replacement.timezone_name == SP
        assert result.current_review_id is not None
        observed.append(Review.objects.get(pk=result.current_review_id).first_due_date)
        return result

    monkeypatch.setattr(AttemptDerivedStateRebuilder, "rebuild", inspect_schedule)
    # Reverse civil boundary makes the new evidence future-dated for Domain.
    # Existing policy rejects explicitly and the whole operation rolls back.
    with pytest.raises(ValueError, match="anteceder"):
        AttemptCorrectionService(workspace_id=ws.id, clock=_clock(BOUNDARY)).replace(
            attempt_id=prior.id,
            expected_tip_id=prior.id,
            selected_alternative_id=prior.selected_alternative_id,
            reason_code="RESULT_CORRECTION",
            fault_hook=interleave,
        )
    assert observed == [date(2026, 10, 12)]
    ws.refresh_from_db()
    prior.refresh_from_db()
    assert ws.timezone_name == SP and prior.status == "VALID"
    assert Attempt.objects.filter(replaces_attempt=prior).count() == 0


@pytest.mark.django_db(transaction=True)
def test_t3_t5_mastery_reopen_boundary_after_complete_service_journey() -> None:
    ws, discipline, subject = _workspace()
    start = datetime(2026, 8, 1, 12, tzinfo=UTC)
    q = _question(ws, discipline, subject, start)
    _attempt(ws, q, start)
    for at in (
        datetime(2026, 8, 2, 12, tzinfo=UTC),
        datetime(2026, 8, 9, 12, tzinfo=UTC),
        datetime(2026, 8, 23, 12, tzinfo=UTC),
        datetime(2026, 9, 22, 12, tzinfo=UTC),
    ):
        review = Review.objects.get(question=q, state="PENDING")
        service = CompleteReviewService(
            actor_id=ws.owner_user_id,
            workspace_id=ws.id,
            session="s8r1-journey",
            store=ContextStore(),
            clock=_clock(at),
        )
        shown = service.presentation(review.id)
        correct_id = q.revisions.get(is_current=True).correct_alternative_id
        assert correct_id is not None
        token = service.evaluate(
            review_id=review.id,
            revision_id=shown["revision_id"],
            lock_version=shown["lock_version"],
            review_lock_version=shown["review_lock_version"],
            alternative_id=correct_id,
        )
        service.complete_review(token=token, key=uuid.uuid4())
        assert run_integrity_check(now=EVALUATION).total_findings == 0
    DomainLifecycleService(workspace_id=ws.id, clock=_clock(BOUNDARY)).manual_reopen(
        question_id=q.id,
        reason_code="REVISIT_TOPIC",
    )
    reopen = ReviewCycle.objects.get(question=q, manual_purpose="MASTERY_REOPEN")
    assert reopen.reviews.get().first_due_date == date(2026, 10, 5)
    history = list(MasteryStateEvent.objects.order_by("pk").values())
    _switch(ws)
    assert list(MasteryStateEvent.objects.order_by("pk").values()) == history
    checked = run_integrity_check(now=EVALUATION)
    assert checked.total_findings == 0 and checked.total_limited_verifications == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("operation", ["creation", "replacement", "reschedule"])
def test_t13_actual_timezone_race_has_coherent_committed_operations(operation: str) -> None:
    ws, discipline, subject = _workspace()
    q = _question(ws, discipline, subject, BOUNDARY)
    initial = _attempt(ws, q, BOUNDARY)
    barrier = Barrier(2)

    def change() -> str:
        try:
            barrier.wait(timeout=10)
            _switch(ws)
            return "CHANGED"
        except OperationalError:
            return "BUSY"
        finally:
            connections.close_all()

    def mutate() -> str:
        try:
            barrier.wait(timeout=10)
            if operation == "creation":
                fresh = _question(ws, discipline, subject, BOUNDARY)
                assert fresh.reviews.get().first_due_date in (date(2026, 10, 5), date(2026, 10, 6))
            elif operation == "reschedule":
                review = q.reviews.get()
                ReviewScheduleService(workspace_id=ws.id, clock=_clock(BOUNDARY)).reschedule(
                    review_id=review.id,
                    new_due_date=date(2026, 10, 8),
                    reason_code="STUDY_PLAN",
                    expected_lock_version=review.lock_version,
                )
                change_row = ReviewScheduleChange.objects.get(review=review)
                audit = AuditEvent.objects.get(entity_id=review.id, event_code="REVIEW_RESCHEDULED")
                assert (change_row.timezone_name, change_row.new_due_date) == (
                    audit.timezone_name,
                    audit.new_date,
                )
            else:
                result = AttemptCorrectionService(
                    workspace_id=ws.id, clock=_clock(EVALUATION)
                ).replace(
                    attempt_id=initial.id,
                    expected_tip_id=initial.id,
                    selected_alternative_id=initial.selected_alternative_id,
                    reason_code="RESULT_CORRECTION",
                )
                assert result.replacement_attempt_id is not None
                replacement = Attempt.objects.get(pk=result.replacement_attempt_id)
                assert replacement.timezone_name in (ACRE, SP)
                assert (
                    replacement.local_date
                    == EVALUATION.astimezone(ZoneInfo(replacement.timezone_name)).date()
                )
            return "COMMITTED"
        except OperationalError:
            return "BUSY"
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        changing, mutating = pool.submit(change), pool.submit(mutate)
        outcomes = (changing.result(timeout=20), mutating.result(timeout=20))
    assert outcomes != ("BUSY", "BUSY")
    assert run_integrity_check(now=EVALUATION).total_findings == 0


@pytest.mark.django_db(transaction=True)
def test_t6_t7_reverse_boundary_rejects_future_evidence_explicitly() -> None:
    ws, discipline, subject = _workspace()
    _switch(ws)
    q = _question(ws, discipline, subject, BOUNDARY)
    _attempt(ws, q, BOUNDARY)
    assert current_domain(
        workspace_id=ws.id, question_id=q.id, clock=_clock(BOUNDARY)
    ).evaluated_on == date(2026, 10, 5)
    change_workspace_timezone(
        actor_user_id=ws.owner_user_id,
        workspace_id=ws.id,
        timezone_id=ACRE,
        expected_lock_version=ws.lock_version,
        confirmed=True,
        clock=_clock(BOUNDARY),
    )
    with pytest.raises(ValueError, match="anteceder"):
        list_subject_priorities(workspace_id=ws.id, clock=_clock(BOUNDARY))
    assert Attempt.objects.get(question=q).local_date == date(2026, 10, 5)
