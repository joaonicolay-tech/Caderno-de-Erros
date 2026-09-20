"""Upgrade V0.4.4→S2A→S2B, reverse seguro pré-fatos e recovery real S2B."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v044_s2a_s2b_upgrade_and_replacement_recovery(tmp_path: Path) -> None:
    database_path = tmp_path / "s2b-upgrade.sqlite3"
    candidate_backup = tmp_path / "s2b-candidate.sqlite3"
    restored_path = tmp_path / "s2b-restored.sqlite3"
    probe = r"""
import json
import os
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
from modules.attempts.services import AttemptCorrectionService
from modules.data_management.services import create_sqlite_backup, restore_sqlite_backup
from modules.errors.catalog import STANDARD_ERROR_CATEGORIES, normalize_name_key
from modules.operations.integrity import run_integrity_check
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
s2a_apps = executor.loader.project_state(s2a).apps
S2ACategory = s2a_apps.get_model("errors", "ErrorCategory")
Audit = s2a_apps.get_model("operations", "AuditEvent")
S2AReview = s2a_apps.get_model("reviews", "Review")
ScheduleChange = s2a_apps.get_model("reviews", "ReviewScheduleChange")
source = S2ACategory.objects.create(
    workspace_id=LOCAL_WORKSPACE_ID,
    code="PERSONAL_SOURCE",
    display_name="Origem",
    name_key="origem",
    description="",
    category_kind="PERSONAL",
    state="ACTIVE",
    lock_version=1,
)
target = S2ACategory.objects.create(
    workspace_id=LOCAL_WORKSPACE_ID,
    code="PERSONAL_TARGET",
    display_name="Alvo",
    name_key="alvo",
    description="",
    category_kind="PERSONAL",
    state="ACTIVE",
    lock_version=1,
)
S2ACategory.objects.filter(pk=source.id).update(state="MERGED", merged_into_id=target.id)
merge_correlation = uuid.uuid4()
Audit.objects.create(
    workspace_id=LOCAL_WORKSPACE_ID,
    event_code="PERSONAL_CATEGORY_MERGED",
    entity_type="ERROR_CATEGORY",
    entity_id=source.id,
    related_entity_id=target.id,
    correlation_id=merge_correlation,
    reason_code="CONSOLIDATION",
)
schedule_correlation = uuid.uuid4()
S2AReview.objects.filter(pk=review.id).update(current_due_date=date(2026, 9, 22))
ScheduleChange.objects.create(
    workspace_id=LOCAL_WORKSPACE_ID,
    review_id=review.id,
    previous_due_date=date(2026, 9, 21),
    new_due_date=date(2026, 9, 22),
    timezone_name="America/Sao_Paulo",
    reason_code="PLAN_CHANGE",
    correlation_id=schedule_correlation,
)
Audit.objects.create(
    workspace_id=LOCAL_WORKSPACE_ID,
    event_code="REVIEW_RESCHEDULED",
    entity_type="REVIEW",
    entity_id=review.id,
    correlation_id=schedule_correlation,
    reason_code="PLAN_CHANGE",
    previous_date=date(2026, 9, 21),
    new_date=date(2026, 9, 22),
    timezone_name="America/Sao_Paulo",
)

executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
executor = MigrationExecutor(connection)
executor.migrate(s2a)
rollback_safe = {
    "categories": S2ACategory.objects.count(),
    "audit": Audit.objects.count(),
    "schedule_changes": ScheduleChange.objects.count(),
}
executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())

clock = FixedClock(Instant(datetime(2026, 9, 20, 18, tzinfo=UTC)))
result = AttemptCorrectionService(workspace_id=LOCAL_WORKSPACE_ID, clock=clock).replace(
    attempt_id=original.id,
    expected_tip_id=original.id,
    selected_alternative_id=correct.id,
    reason_code="UPGRADE_CORRECTION",
)
replacement = Attempt.objects.get(pk=result.replacement_attempt_id)
original_now = Attempt.objects.get(pk=original.id)
activity = AnalyticsService(workspace_id=LOCAL_WORKSPACE_ID, clock=clock).activity()
integrity = run_integrity_check()
candidate = create_sqlite_backup(Path(os.environ["CEI_CANDIDATE_BACKUP"]))
restore = restore_sqlite_backup(
    Path(os.environ["CEI_CANDIDATE_BACKUP"]),
    Path(os.environ["CEI_RESTORED_PATH"]),
)
with connection.cursor() as cursor:
    physical = cursor.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_keys = cursor.execute("PRAGMA foreign_key_check").fetchall()

print(json.dumps({
    "rollback_safe": rollback_safe,
    "statuses": [original_now.status, replacement.status],
    "replacement_link": str(replacement.replaces_attempt_id) == str(original.id),
    "classification_preserved": original_now.error_classification.attempt_id == original.id,
    "personal_merge_preserved": S2ACategory.objects.get(pk=source.id).merged_into_id == target.id,
    "schedule_change_preserved": ScheduleChange.objects.filter(pk__isnull=False).count(),
    "audit_codes": sorted(Audit.objects.values_list("event_code", flat=True)),
    "activity": [activity.performed_questions, activity.attempts, activity.correct_answers],
    "checker": [integrity.checks_executed, integrity.total_findings],
    "physical": physical,
    "foreign_keys": foreign_keys,
    "backup_size": candidate.manifest.size_bytes,
    "restore": [restore.integrity.checks_executed, restore.integrity.total_findings],
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

    assert evidence["rollback_safe"] == {
        "categories": 12,
        "audit": 2,
        "schedule_changes": 1,
    }
    assert evidence["statuses"] == ["VOIDED", "VALID"]
    assert evidence["replacement_link"]
    assert evidence["classification_preserved"]
    assert evidence["personal_merge_preserved"]
    assert evidence["schedule_change_preserved"] == 1
    assert {"ATTEMPT_VOIDED", "ATTEMPT_REPLACED"}.issubset(evidence["audit_codes"])
    assert evidence["activity"] == [1, 1, 1]
    assert evidence["checker"] == [22, 0]
    assert (evidence["physical"], evidence["foreign_keys"]) == ("ok", [])
    assert evidence["backup_size"] > 0
    assert evidence["restore"] == [22, 0]
