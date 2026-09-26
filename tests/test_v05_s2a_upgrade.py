"""Prova isolada de upgrade V0.4.4-equivalente, rollback seguro e recovery S6."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_v044_equivalent_upgrade_backup_restore_and_safe_empty_rollback(tmp_path: Path) -> None:
    database_path = tmp_path / "v044-upgrade.sqlite3"
    pre_upgrade_backup = tmp_path / "v044-pre-upgrade.sqlite3"
    candidate_backup = tmp_path / "s2a-candidate.sqlite3"
    restored_path = tmp_path / "s2a-restored.sqlite3"
    probe = r"""
import hashlib
import io
import json
import os
import sqlite3
import uuid
from datetime import UTC, date, datetime
from pathlib import Path

import django
from django.db import connection, connections
from django.db.migrations.executor import MigrationExecutor

django.setup()

from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.analytics.services import AnalyticsService
from modules.analytics.read_models import ErrorCategoryBreakdown
from modules.data_management.services import (
    create_sqlite_backup,
    restore_sqlite_backup,
    validate_sqlite_backup,
)
from modules.data_management.portability import (
    export_bytes,
    export_workspace,
    import_into_empty,
    validate_export,
)
from modules.domain.services import current_domain
from modules.errors.catalog import STANDARD_ERROR_CATEGORIES, normalize_name_key
from modules.operations.integrity import run_integrity_check
from modules.priority.services import list_subject_priorities
from shared.domain.time import FixedClock, Instant

v044 = [
    ("auth", "0012_alter_user_first_name_max_length"),
    ("attempts", "0002_review_receipt_constraints"),
    ("errors", "0002_learning_classification"),
    ("questions", "0002_question_catalog"),
    ("reviews", "0002_activation_review_cycle"),
    ("taxonomy", "0001_initial"),
]
executor = MigrationExecutor(connection)
executor.migrate(v044)
with connection.cursor() as cursor:
    old_migrations = set(cursor.execute(
        "SELECT app || '.' || name FROM django_migrations"
    ).fetchall())
apps = executor.loader.project_state(v044).apps
User = apps.get_model("accounts", "User")
Workspace = apps.get_model("accounts", "Workspace")
Category = apps.get_model("errors", "ErrorCategory")
Discipline = apps.get_model("taxonomy", "Discipline")
Subject = apps.get_model("taxonomy", "Subject")
Question = apps.get_model("questions", "Question")
Revision = apps.get_model("questions", "QuestionRevision")
Alternative = apps.get_model("questions", "Alternative")
Attempt = apps.get_model("attempts", "Attempt")
Classification = apps.get_model("errors", "ErrorClassification")
Cycle = apps.get_model("reviews", "ReviewCycle")
Review = apps.get_model("reviews", "Review")
Receipt = apps.get_model("attempts", "OperationReceipt")

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
discipline = Discipline.objects.create(
    workspace=workspace,
    name="Matemática",
    name_key="matemática",
)
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
    stem="Fato representativo V0.4.4",
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
attempt = Attempt.objects.create(
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
    attempt=attempt,
    category=categories["ATTENTION"],
    lock_version=1,
)
cycle = Cycle.objects.create(
    workspace=workspace,
    question=question,
    origin_attempt=attempt,
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
    scheduled_from_attempt=attempt,
    transition_code="INITIAL_ERROR_TO_D1",
    policy_code="REV-FIXA-1.0",
    lock_version=1,
)
receipt = Receipt.objects.create(
    workspace=workspace,
    operation_kind="INITIAL_ERROR",
    idempotency_key=attempt.idempotency_key,
    request_hash="a" * 64,
    result_entity_type="ATTEMPT",
    result_entity_id=attempt.id,
)
Receipt.objects.filter(pk=receipt.id).update(
    created_at=datetime(2026, 8, 1, 15, tzinfo=UTC)
)
before = {
    "categories": Category.objects.count(),
    "attempts": Attempt.objects.count(),
    "classifications": Classification.objects.count(),
    "cycles": Cycle.objects.count(),
    "reviews": Review.objects.count(),
    "receipts": Receipt.objects.count(),
    "review_due": review.current_due_date.isoformat(),
}
pre_result = create_sqlite_backup(Path(os.environ["CEI_PRE_UPGRADE_BACKUP"]))
validate_sqlite_backup(Path(os.environ["CEI_PRE_UPGRADE_BACKUP"]))
with sqlite3.connect(os.environ["CEI_PRE_UPGRADE_BACKUP"]) as source:
    with sqlite3.connect(os.environ["CEI_PRE_RESTORED_PATH"]) as recovered:
        source.backup(recovered)
with sqlite3.connect(os.environ["CEI_PRE_RESTORED_PATH"]) as recovered:
    pre_restore = {
        "physical": recovered.execute("PRAGMA integrity_check").fetchone()[0],
        "foreign_keys": recovered.execute("PRAGMA foreign_key_check").fetchall(),
        "attempts": recovered.execute("SELECT COUNT(*) FROM attempts_attempt").fetchone()[0],
        "receipts": recovered.execute("SELECT COUNT(*) FROM attempts_operationreceipt").fetchone()[0],
        "new_tables_absent": "search_savedfilter" not in {
            row[0] for row in recovered.execute("SELECT name FROM sqlite_master WHERE type='table'")
        },
    }

executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
with connection.cursor() as cursor:
    new_migrations = set(cursor.execute(
        "SELECT app || '.' || name FROM django_migrations"
    ).fetchall())
added_migrations = sorted(name for (name,) in new_migrations - old_migrations)
final_apps = executor.loader.project_state().apps
FinalCategory = final_apps.get_model("errors", "ErrorCategory")
FinalAttempt = final_apps.get_model("attempts", "Attempt")
FinalClassification = final_apps.get_model("errors", "ErrorClassification")
FinalCycle = final_apps.get_model("reviews", "ReviewCycle")
FinalReview = final_apps.get_model("reviews", "Review")
Audit = final_apps.get_model("operations", "AuditEvent")
ScheduleChange = final_apps.get_model("reviews", "ReviewScheduleChange")
FinalReceipt = final_apps.get_model("attempts", "OperationReceipt")
SavedFilter = final_apps.get_model("search", "SavedFilter")
MasteryEvent = final_apps.get_model("domain", "MasteryStateEvent")
upgraded_category = FinalCategory.objects.get(pk=categories["ATTENTION"].id)
upgraded_review = FinalReview.objects.get(pk=review.id)
clock = FixedClock(Instant(datetime(2026, 9, 20, 15, tzinfo=UTC)))
analytics = AnalyticsService(workspace_id=LOCAL_WORKSPACE_ID, clock=clock)
activity = analytics.activity()
errors: ErrorCategoryBreakdown = analytics.error_categories()
reviews = analytics.reviews()
domain = current_domain(workspace_id=LOCAL_WORKSPACE_ID, question_id=question.id, clock=clock)
priority = list_subject_priorities(workspace_id=LOCAL_WORKSPACE_ID, clock=clock)
package = validate_export(io.BytesIO(export_bytes(workspace_id=LOCAL_WORKSPACE_ID)))
assert len(package.manifest["schema_migrations"]) == len(new_migrations)
alias = "s8_cei_import"
connections.databases[alias] = {
    **connections["default"].settings_dict,
    "NAME": os.environ["CEI_EXPORT_IMPORT_PATH"],
}
try:
    import_executor = MigrationExecutor(connections[alias])
    import_executor.migrate(import_executor.loader.graph.leaf_nodes())
    imported_counts = import_into_empty(package=package, database_alias=alias)
    replay = io.BytesIO()
    export_workspace(workspace_id=LOCAL_WORKSPACE_ID, destination=replay, database_alias=alias)
    replayed = validate_export(io.BytesIO(replay.getvalue()))
    cei_round_trip = (
        imported_counts["questions"] == 1
        and all(
            package.rows[name] == replayed.rows[name]
            for name in ("questions", "question_revisions", "attempts")
        )
    )
finally:
    connections[alias].close()
    del connections[alias]
    del connections.databases[alias]
from modules.attempts.models import OperationReceipt
retry = OperationReceipt.objects.resolve_existing(
    workspace_id=LOCAL_WORKSPACE_ID,
    operation_kind="INITIAL_ERROR",
    idempotency_key=attempt.idempotency_key,
    request_hash="a" * 64,
)
with connection.cursor() as cursor:
    foreign_keys = cursor.execute("PRAGMA foreign_key_check").fetchall()
    physical = cursor.execute("PRAGMA integrity_check").fetchone()[0]
connection.close()
database_file = Path(connection.settings_dict["NAME"])
hash_before_s5 = hashlib.sha256(database_file.read_bytes()).hexdigest()
integrity = run_integrity_check()
hash_after_s5 = hashlib.sha256(database_file.read_bytes()).hexdigest()
after = {
    "categories": FinalCategory.objects.count(),
    "attempts": FinalAttempt.objects.count(),
    "classifications": FinalClassification.objects.count(),
    "cycles": FinalCycle.objects.count(),
    "reviews": FinalReview.objects.count(),
    "audit": Audit.objects.count(),
    "schedule_changes": ScheduleChange.objects.count(),
    "saved_filters": SavedFilter.objects.count(),
    "mastery_events": MasteryEvent.objects.count(),
    "receipts": FinalReceipt.objects.count(),
    "receipt_id_preserved": str(retry.id) == str(receipt.id),
    "receipt_created_at_preserved": retry.created_at.date().isoformat() == "2026-08-01",
    "domain_question": str(domain.result.question_id) == str(question.id),
    "domain_events_unchanged": MasteryEvent.objects.count() == 0,
    "priority_insufficient": len(priority.ranked) == 0 and len(priority.collect_more_evidence) == 1,
    "cei_questions": len(package.rows["questions"]),
    "cei_excludes_receipts": "operation_receipts" not in package.rows,
    "cei_round_trip": cei_round_trip,
    "added_migrations": added_migrations,
    "category_kind": upgraded_category.category_kind,
    "category_state": upgraded_category.state,
    "review_due": upgraded_review.current_due_date.isoformat(),
    "first_due": upgraded_review.first_due_date.isoformat(),
    "activity_attempts": activity.attempts,
    "performed": activity.performed_questions,
    "classified": errors.classified_errors,
    "future_reviews": reviews.future,
    "foreign_keys": foreign_keys,
    "physical": physical,
    "s5_checks": integrity.checks_executed,
    "s5_findings": integrity.total_findings,
    "s5_read_only": hash_before_s5 == hash_after_s5,
}

candidate_result = create_sqlite_backup(Path(os.environ["CEI_CANDIDATE_BACKUP"]))
restore = restore_sqlite_backup(
    Path(os.environ["CEI_CANDIDATE_BACKUP"]),
    Path(os.environ["CEI_RESTORED_PATH"]),
)

executor = MigrationExecutor(connection)
rollback_targets = [*v044, ("operations", None)]
executor.migrate(rollback_targets)
old_apps = executor.loader.project_state(v044).apps
rollback = {
    "categories": old_apps.get_model("errors", "ErrorCategory").objects.count(),
    "attempts": old_apps.get_model("attempts", "Attempt").objects.count(),
    "classifications": old_apps.get_model("errors", "ErrorClassification").objects.count(),
    "cycles": old_apps.get_model("reviews", "ReviewCycle").objects.count(),
    "reviews": old_apps.get_model("reviews", "Review").objects.count(),
    "new_tables_absent": not {
        "operations_auditevent",
        "reviews_reviewschedulechange",
    }.intersection(connection.introspection.table_names()),
}
print(json.dumps({
    "before": before,
    "after": after,
    "pre_backup_size": pre_result.manifest.size_bytes,
    "pre_backup_hash": pre_result.manifest.sha256,
    "pre_restore": pre_restore,
    "candidate_backup_size": candidate_result.manifest.size_bytes,
    "restore_checks": restore.integrity.checks_executed,
    "restore_findings": restore.integrity.total_findings,
    "restore_categories": restore.reconciliation.category_count,
    "restore_receipts": restore.reconciliation.operation_receipt_count,
    "rollback": rollback,
}))
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
    environment["CEI_TEST_DATABASE_PATH"] = str(database_path)
    environment["CEI_PRE_UPGRADE_BACKUP"] = str(pre_upgrade_backup)
    environment["CEI_PRE_RESTORED_PATH"] = str(tmp_path / "v044-pre-restored.sqlite3")
    environment["CEI_EXPORT_IMPORT_PATH"] = str(tmp_path / "s8-cei-import.sqlite3")
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

    assert evidence["before"] == {
        "categories": 10,
        "attempts": 1,
        "classifications": 1,
        "cycles": 1,
        "reviews": 1,
        "receipts": 1,
        "review_due": "2026-09-21",
    }
    assert evidence["after"] == {
        "categories": 10,
        "attempts": 1,
        "classifications": 1,
        "cycles": 1,
        "reviews": 1,
        "audit": 0,
        "schedule_changes": 0,
        "saved_filters": 0,
        "mastery_events": 0,
        "receipts": 1,
        "receipt_id_preserved": True,
        "receipt_created_at_preserved": True,
        "domain_question": True,
        "domain_events_unchanged": True,
        "priority_insufficient": True,
        "cei_questions": 1,
        "cei_excludes_receipts": True,
        "cei_round_trip": True,
        "added_migrations": [
            "domain.0001_initial",
            "errors.0003_errorcategory_category_kind_and_more",
            "operations.0001_initial",
            "operations.0002_attempt_audit_events",
            "operations.0003_answer_key_correction_audit",
            "operations.0004_remove_auditevent_audit_event_code_valid_and_more",
            "reviews.0003_reviewschedulechange_and_more",
            "reviews.0004_attempt_correction_projection",
            "reviews.0005_reviewcycle_manual_purpose_and_more",
            "search.0001_initial",
        ],
        "category_kind": "STANDARD",
        "category_state": "ACTIVE",
        "review_due": "2026-09-21",
        "first_due": "2026-09-21",
        "activity_attempts": 1,
        "performed": 1,
        "classified": 1,
        "future_reviews": 1,
        "foreign_keys": [],
        "physical": "ok",
        "s5_checks": 25,
        "s5_findings": 0,
        "s5_read_only": True,
    }
    assert evidence["pre_backup_size"] > 0
    assert len(evidence["pre_backup_hash"]) == 64
    assert evidence["pre_restore"] == {
        "physical": "ok",
        "foreign_keys": [],
        "attempts": 1,
        "receipts": 1,
        "new_tables_absent": True,
    }
    assert evidence["candidate_backup_size"] > 0
    assert (evidence["restore_checks"], evidence["restore_findings"]) == (25, 0)
    assert evidence["restore_categories"] == 10
    assert evidence["restore_receipts"] == 1
    assert evidence["rollback"] == {
        "categories": 10,
        "attempts": 1,
        "classifications": 1,
        "cycles": 1,
        "reviews": 1,
        "new_tables_absent": True,
    }
