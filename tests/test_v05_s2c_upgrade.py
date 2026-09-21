"""Upgrade V0.4.4→S2A→S2B→S2C e recovery isolado com fatos S2C."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v044_s2a_s2b_s2c_upgrade_and_answer_key_recovery(tmp_path: Path) -> None:
    database_path = tmp_path / "s2c-upgrade.sqlite3"
    candidate_backup = tmp_path / "s2c-candidate.sqlite3"
    restored_path = tmp_path / "s2c-restored.sqlite3"
    probe = r"""
import json
import os
import sqlite3
import uuid
from datetime import UTC, date, datetime
from pathlib import Path

import django
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

django.setup()

from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.analytics.services import AnalyticsService
from modules.attempts.models import Attempt
from modules.attempts.services import AttemptCorrectionService, AttemptService
from modules.data_management.services import create_sqlite_backup, restore_sqlite_backup
from modules.errors.catalog import STANDARD_ERROR_CATEGORIES, normalize_name_key
from modules.errors.services import PersonalCategoryService
from modules.operations.integrity import run_integrity_check
from modules.operations.models import AuditEvent
from modules.questions.corrections import AnswerKeyCorrectionService
from modules.questions.models import QuestionRevision
from modules.questions.services import create_active
from modules.reviews.services import CompleteReviewService, ReviewScheduleService
from modules.taxonomy.services import create_discipline, create_subject
from shared.domain.time import FixedClock, Instant

v044 = [
    ("auth", "0012_alter_user_first_name_max_length"),
    ("attempts", "0002_review_receipt_constraints"),
    ("errors", "0002_learning_classification"),
    ("questions", "0002_question_catalog"),
    ("reviews", "0002_activation_review_cycle"),
    ("taxonomy", "0001_initial"),
]
s2a = [
    ("auth", "0012_alter_user_first_name_max_length"),
    ("attempts", "0002_review_receipt_constraints"),
    ("errors", "0003_errorcategory_category_kind_and_more"),
    ("operations", "0001_initial"),
    ("questions", "0002_question_catalog"),
    ("reviews", "0003_reviewschedulechange_and_more"),
    ("taxonomy", "0001_initial"),
]
s2b = [
    ("auth", "0012_alter_user_first_name_max_length"),
    ("attempts", "0002_review_receipt_constraints"),
    ("errors", "0003_errorcategory_category_kind_and_more"),
    ("operations", "0002_attempt_audit_events"),
    ("questions", "0002_question_catalog"),
    ("reviews", "0004_attempt_correction_projection"),
    ("taxonomy", "0001_initial"),
]
s2c = [*s2b[:3], ("operations", "0003_answer_key_correction_audit"), *s2b[4:]]

executor = MigrationExecutor(connection)
executor.migrate(v044)
apps = executor.loader.project_state(v044).apps
User = apps.get_model("accounts", "User")
Workspace = apps.get_model("accounts", "Workspace")
Category = apps.get_model("errors", "ErrorCategory")
Discipline = apps.get_model("taxonomy", "Discipline")
Subject = apps.get_model("taxonomy", "Subject")
Question = apps.get_model("questions", "Question")
Revision = apps.get_model("questions", "QuestionRevision")
Alternative = apps.get_model("questions", "Alternative")
HistoricalAttempt = apps.get_model("attempts", "Attempt")
Classification = apps.get_model("errors", "ErrorClassification")
Cycle = apps.get_model("reviews", "ReviewCycle")
Review = apps.get_model("reviews", "Review")

user = User.objects.create(
    id=LOCAL_USER_ID,
    password="!",
    email="local@example.test",
    display_name="Usuário local",
    status="ACTIVE",
)
workspace = Workspace.objects.create(
    id=LOCAL_WORKSPACE_ID,
    owner_user=user,
    name="Meu espaço",
    timezone_name="America/Sao_Paulo",
    locale="pt-BR",
    lock_version=1,
)
categories = {}
for definition in STANDARD_ERROR_CATEGORIES:
    categories[definition.code] = Category.objects.create(
        workspace=workspace,
        code=definition.code,
        display_name=definition.display_name,
        name_key=normalize_name_key(definition.display_name),
        description=definition.description,
    )
discipline = Discipline.objects.create(workspace=workspace, name="Matemática", name_key="matemática")
subject = Subject.objects.create(
    workspace=workspace,
    discipline=discipline,
    name="Álgebra",
    name_key="álgebra",
)
question = Question.objects.create(
    workspace=workspace,
    discipline=discipline,
    subject=subject,
    question_type="OBJECTIVE_SINGLE",
    status="ACTIVE",
    activated_at=datetime(2026, 9, 20, 15, tzinfo=UTC),
    lock_version=1,
)
revision = Revision.objects.create(
    workspace=workspace,
    question=question,
    version_number=1,
    is_current=True,
    stem="Fato V0.4.4 preservado",
    change_kind="INITIAL",
)
wrong = Alternative.objects.create(
    workspace=workspace,
    question_revision=revision,
    position=1,
    text="Errada",
    text_key="errada",
)
correct = Alternative.objects.create(
    workspace=workspace,
    question_revision=revision,
    position=2,
    text="Correta",
    text_key="correta",
)
Revision.objects.filter(pk=revision.id).update(correct_alternative=correct)
original = HistoricalAttempt.objects.create(
    workspace=workspace,
    question=question,
    question_revision=revision,
    attempt_type="INITIAL",
    selected_alternative=wrong,
    is_correct=False,
    occurred_at=datetime(2026, 9, 20, 15, tzinfo=UTC),
    timezone_name="America/Sao_Paulo",
    local_date=date(2026, 9, 20),
    status="VALID",
    idempotency_key=uuid.UUID("33333333-3333-4333-8333-333333333333"),
)
Classification.objects.create(
    workspace=workspace,
    attempt=original,
    category=categories["ATTENTION"],
    lock_version=1,
)
cycle = Cycle.objects.create(
    workspace=workspace,
    question=question,
    origin_attempt=original,
    origin_question_revision=revision,
    origin_kind="INITIAL_ERROR",
    policy_code="REV-FIXA-1.0",
    state="ACTIVE",
    started_at=datetime(2026, 9, 20, 15, tzinfo=UTC),
    lock_version=1,
)
review = Review.objects.create(
    workspace=workspace,
    review_cycle=cycle,
    question=question,
    sequence_number=1,
    stage_code="D1",
    state="PENDING",
    first_due_date=date(2026, 9, 21),
    current_due_date=date(2026, 9, 21),
    scheduled_from_attempt=original,
    transition_code="INITIAL_ERROR_TO_D1",
    policy_code="REV-FIXA-1.0",
    lock_version=1,
)

executor = MigrationExecutor(connection)
executor.migrate(s2a)
executor = MigrationExecutor(connection)
executor.migrate(s2b)
executor = MigrationExecutor(connection)
executor.migrate(s2c)

# Reverse/forward seguro antes de fatos S2C.
executor = MigrationExecutor(connection)
executor.migrate(s2b)
pre_fact_counts = {
    "questions": executor.loader.project_state(s2b).apps.get_model("questions", "Question").objects.count(),
    "attempts": executor.loader.project_state(s2b).apps.get_model("attempts", "Attempt").objects.count(),
}
executor = MigrationExecutor(connection)
executor.migrate(s2c)

clock = FixedClock(Instant(datetime(2026, 9, 20, 18, tzinfo=UTC)))
personal = PersonalCategoryService(workspace_id=LOCAL_WORKSPACE_ID)
source = personal.create(display_name="Origem rica")
target = personal.create(display_name="Alvo rico")
personal.merge(
    source_id=source.id,
    target_id=target.id,
    reason_code="RECOVERY_MERGE",
    expected_lock_version=source.lock_version,
)
ReviewScheduleService(workspace_id=LOCAL_WORKSPACE_ID, clock=clock).reschedule(
    review_id=review.id,
    new_due_date=date(2026, 9, 22),
    reason_code="RECOVERY_RESCHEDULE",
    expected_lock_version=1,
)
s2b_result = AttemptCorrectionService(workspace_id=LOCAL_WORKSPACE_ID, clock=clock).replace(
    attempt_id=original.id,
    expected_tip_id=original.id,
    selected_alternative_id=correct.id,
    reason_code="RECOVERY_REPLACEMENT",
)
replacement = Attempt.objects.get(pk=s2b_result.replacement_attempt_id)
historical_before = list(
    Attempt.objects.filter(question_id=question.id).order_by("created_at").values(
        "id", "question_revision_id", "selected_alternative_id", "is_correct", "status",
        "voided_at", "void_reason", "replaces_attempt_id"
    )
)
s2c_result = AnswerKeyCorrectionService(
    workspace_id=LOCAL_WORKSPACE_ID,
    clock=clock,
).correct(
    question_id=question.id,
    expected_revision_id=revision.id,
    correct_alternative_position=1,
    reason_code="RECOVERY_KEY_FIX",
)

# Uma segunda Question prova Attempt futura pela current R2 no fluxo normal de REVIEW.
discipline_now = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Física")
subject_now = create_subject(
    workspace_id=LOCAL_WORKSPACE_ID,
    discipline_id=discipline_now.id,
    name="Mecânica",
)
activation_clock = FixedClock(Instant(datetime(2026, 9, 19, 15, tzinfo=UTC)))
future_question = create_active(
    workspace_id=LOCAL_WORKSPACE_ID,
    discipline_id=discipline_now.id,
    subject_id=subject_now.id,
    stem="Questão futura",
    alternatives=["Nova correta", "Antiga correta"],
    correct_alternative_position=2,
    clock=activation_clock,
)
future_r1 = future_question.revisions.get(is_current=True)
initial = Attempt.objects.create(
    workspace_id=LOCAL_WORKSPACE_ID,
    question=future_question,
    question_revision=future_r1,
    attempt_type="INITIAL",
    selected_alternative=future_r1.alternatives.get(position=2),
    is_correct=True,
    occurred_at=activation_clock.now().value,
    timezone_name="America/Sao_Paulo",
    local_date=date(2026, 9, 19),
    idempotency_key=uuid.uuid4(),
)
future_correction = AnswerKeyCorrectionService(
    workspace_id=LOCAL_WORKSPACE_ID,
    clock=clock,
).correct(
    question_id=future_question.id,
    expected_revision_id=future_r1.id,
    correct_alternative_position=1,
    reason_code="FUTURE_KEY_FIX",
)
pending = future_question.reviews.get(state="PENDING")
attempt_service = AttemptService(
    actor_id=LOCAL_USER_ID,
    workspace_id=LOCAL_WORKSPACE_ID,
    session="s2c-upgrade",
    clock=clock,
)
review_service = CompleteReviewService(attempt_service)
presentation = review_service.presentation(pending.id)
future_r2 = QuestionRevision.objects.get(pk=future_correction.new_revision_id)
token = review_service.evaluate(
    review_id=pending.id,
    revision_id=presentation["revision_id"],
    lock_version=presentation["lock_version"],
    review_lock_version=presentation["review_lock_version"],
    alternative_id=future_r2.alternatives.get(position=1).id,
)
receipt = review_service.complete_review(token=token, key=uuid.uuid4())
future_attempt = Attempt.objects.get(pk=receipt.result_entity_id)

integrity = run_integrity_check()
activity = AnalyticsService(workspace_id=LOCAL_WORKSPACE_ID, clock=clock).activity()
candidate = create_sqlite_backup(Path(os.environ["CEI_CANDIDATE_BACKUP"]))
restore = restore_sqlite_backup(
    Path(os.environ["CEI_CANDIDATE_BACKUP"]),
    Path(os.environ["CEI_RESTORED_PATH"]),
)
with connection.cursor() as cursor:
    physical = cursor.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_keys = cursor.execute("PRAGMA foreign_key_check").fetchall()
with sqlite3.connect(os.environ["CEI_RESTORED_PATH"]) as restored:
    restored_current = restored.execute(
        "SELECT version_number FROM questions_questionrevision WHERE question_id = ? AND is_current = 1",
        (question.id.hex,),
    ).fetchone()[0]
    restored_chain = restored.execute(
        "SELECT status, replaces_attempt_id FROM attempts_attempt WHERE question_id = ? ORDER BY created_at",
        (question.id.hex,),
    ).fetchall()
    restored_audit = {
        row[0] for row in restored.execute("SELECT event_code FROM operations_auditevent")
    }

historical_after = list(
    Attempt.objects.filter(question_id=question.id).order_by("created_at").values(
        "id", "question_revision_id", "selected_alternative_id", "is_correct", "status",
        "voided_at", "void_reason", "replaces_attempt_id"
    )
)
print(json.dumps({
    "pre_fact_counts": pre_fact_counts,
    "historical_preserved": historical_before == historical_after,
    "s2b_statuses": [Attempt.objects.get(pk=original.id).status, replacement.status],
    "s2c_versions": [
        QuestionRevision.objects.get(pk=s2c_result.previous_revision_id).version_number,
        QuestionRevision.objects.get(pk=s2c_result.new_revision_id).version_number,
    ],
    "future_binding": [
        str(initial.question_revision_id) == str(future_r1.id),
        str(future_attempt.question_revision_id) == str(future_r2.id),
        future_attempt.is_correct,
    ],
    "audit_codes": sorted(AuditEvent.objects.values_list("event_code", flat=True)),
    "activity": [activity.performed_questions, activity.attempts, activity.correct_answers],
    "checker": [integrity.checks_executed, integrity.total_findings],
    "physical": physical,
    "foreign_keys": foreign_keys,
    "backup_size": candidate.manifest.size_bytes,
    "restore": [restore.integrity.checks_executed, restore.integrity.total_findings],
    "restored_current": restored_current,
    "restored_chain": restored_chain,
    "restored_audit": sorted(restored_audit),
}))
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
    environment["CEI_TEST_DATABASE_PATH"] = str(database_path)
    environment["CEI_CANDIDATE_BACKUP"] = str(candidate_backup)
    environment["CEI_RESTORED_PATH"] = str(restored_path)
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    evidence = json.loads(result.stdout.splitlines()[-1])

    assert evidence["pre_fact_counts"] == {"questions": 1, "attempts": 1}
    assert evidence["historical_preserved"]
    assert evidence["s2b_statuses"] == ["VOIDED", "VALID"]
    assert evidence["s2c_versions"] == [1, 2]
    assert evidence["future_binding"] == [True, True, True]
    assert {
        "PERSONAL_CATEGORY_MERGED",
        "REVIEW_RESCHEDULED",
        "ATTEMPT_VOIDED",
        "ATTEMPT_REPLACED",
        "ANSWER_KEY_CORRECTED",
    }.issubset(evidence["audit_codes"])
    assert evidence["checker"] == [22, 0]
    assert (evidence["physical"], evidence["foreign_keys"]) == ("ok", [])
    assert evidence["backup_size"] > 0
    assert evidence["restore"] == [22, 0]
    assert evidence["restored_current"] == 2
    assert [row[0] for row in evidence["restored_chain"]] == ["VOIDED", "VALID"]
    assert "ANSWER_KEY_CORRECTED" in evidence["restored_audit"]
