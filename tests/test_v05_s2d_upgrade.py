"""Upgrade isolado V0.4.4-equivalente até S2D com fatos S2A/S2B/S2C."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_s2d_upgrade_preserves_prior_facts_then_deletes_with_recovery(tmp_path: Path) -> None:
    probe = r"""
import json
import os
import sqlite3
import uuid
from datetime import UTC, datetime

import django
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

django.setup()

from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.attempts.corrections import AttemptCorrectionService
from modules.attempts.models import Attempt
from modules.errors.services import PersonalCategoryService
from modules.operations.integrity import run_integrity_check
from modules.operations.models import AuditEvent
from modules.questions.corrections import AnswerKeyCorrectionService
from modules.questions.deletion import PermanentQuestionDeletionService
from modules.questions.models import Question, QuestionRevision
from modules.questions.services import create_active
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace

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
    *s2a[:3],
    ("operations", "0002_attempt_audit_events"),
    s2a[4],
    ("reviews", "0004_attempt_correction_projection"),
    s2a[6],
]
s2c = [*s2b[:3], ("operations", "0003_answer_key_correction_audit"), *s2b[4:]]
s2d = [*s2b[:3], (
    "operations", "0004_remove_auditevent_audit_event_code_valid_and_more"
), *s2b[4:]]
for stage in (v044, s2a, s2b, s2c, s2d):
    MigrationExecutor(connection).migrate(stage)
# Current service models require the current S5 schema before they are called.
MigrationExecutor(connection).migrate(MigrationExecutor(connection).loader.graph.leaf_nodes())

workspace = bootstrap_local_workspace(timezone_id="UTC").workspace
discipline = create_discipline(workspace_id=workspace.id, name="Upgrade")
subject = create_subject(
    workspace_id=workspace.id, discipline_id=discipline.id, name="Upgrade"
)
category_service = PersonalCategoryService(workspace_id=workspace.id)
source = category_service.create(display_name="Origem")
target = category_service.create(display_name="Destino")
category_service.merge(
    source_id=source.id,
    target_id=target.id,
    reason_code="MERGE_REASON",
    expected_lock_version=source.lock_version,
)
question = create_active(
    workspace_id=workspace.id,
    discipline_id=discipline.id,
    subject_id=subject.id,
    stem="Fato S2C",
    alternatives=["errada", "certa"],
    correct_alternative_position=2,
)
revision = question.revisions.get(is_current=True)
now = datetime.now(UTC)
initial = Attempt.objects.create(
    workspace=workspace,
    question=question,
    question_revision=revision,
    attempt_type="INITIAL",
    selected_alternative=revision.alternatives.get(position=2),
    is_correct=True,
    occurred_at=now,
    timezone_name="UTC",
    local_date=now.date(),
    idempotency_key=uuid.uuid4(),
)
replacement = AttemptCorrectionService(workspace_id=workspace.id).replace(
    attempt_id=initial.id,
    expected_tip_id=initial.id,
    selected_alternative_id=revision.alternatives.get(position=1).id,
    reason_code="ENTRY_FIX",
)
AnswerKeyCorrectionService(workspace_id=workspace.id).correct(
    question_id=question.id,
    expected_revision_id=revision.id,
    correct_alternative_position=1,
    reason_code="KEY_FIX",
)
before = {
    "attempts": Attempt.objects.filter(question_id=question.id).count(),
    "revisions": QuestionRevision.objects.filter(question_id=question.id).count(),
    "audit": sorted(AuditEvent.objects.values_list("event_code", flat=True)),
}
checker_before = run_integrity_check()
after = {
    "attempts": Attempt.objects.filter(question_id=question.id).count(),
    "revisions": QuestionRevision.objects.filter(question_id=question.id).count(),
    "audit": sorted(AuditEvent.objects.values_list("event_code", flat=True)),
}
# Validate isolated restore and deletion against the current compatible schema.
service = PermanentQuestionDeletionService(workspace_id=LOCAL_WORKSPACE_ID)
preview = service.preview(question_id=question.id)
result = service.delete(
    question_id=question.id,
    expected_fingerprint=preview.fingerprint,
    confirmation_token=preview.confirmation_token,
    reason_code="USER_REQUEST",
    correlation_id=uuid.uuid4(),
    backup_path=os.environ["CEI_PRE_BACKUP"],
    isolated_restore_path=os.environ["CEI_PRE_RESTORE"],
)
checker_after = run_integrity_check()
with connection.cursor() as cursor:
    physical = cursor.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_keys = cursor.execute("PRAGMA foreign_key_check").fetchall()
with sqlite3.connect(os.environ["CEI_PRE_RESTORE"]) as restored:
    recovered = restored.execute(
        "SELECT count(*) FROM questions_question WHERE id = ?", (question.id.hex,)
    ).fetchone()[0]
print(json.dumps({
    "preserved": before == after,
    "before": before,
    "checker_before": checker_before.total_findings,
    "eligible": preview.eligible,
    "deleted": not Question.objects.filter(pk=question.id).exists(),
    "old_events_removed": not AuditEvent.objects.filter(entity_id__in=[
        question.id, initial.id, replacement.replacement_attempt_id
    ]).exists(),
    "shared_event_kept": AuditEvent.objects.filter(
        event_code="PERSONAL_CATEGORY_MERGED"
    ).exists(),
    "final_event": AuditEvent.objects.get(pk=result.audit_event_id).entity_id is None,
    "checker_after": checker_after.total_findings,
    "physical": physical,
    "foreign_keys": foreign_keys,
    "recovered": recovered,
}))
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
    environment["CEI_PRE_BACKUP"] = str(tmp_path / "pre.sqlite3")
    environment["CEI_PRE_RESTORE"] = str(tmp_path / "restored.sqlite3")
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
    assert evidence["preserved"]
    assert evidence["before"]["attempts"] == 2
    assert evidence["before"]["revisions"] == 2
    assert {"PERSONAL_CATEGORY_MERGED", "ATTEMPT_REPLACED", "ANSWER_KEY_CORRECTED"}.issubset(
        evidence["before"]["audit"]
    )
    assert evidence["checker_before"] == 0
    assert evidence["eligible"] and evidence["deleted"]
    assert evidence["old_events_removed"] and evidence["shared_event_kept"]
    assert evidence["final_event"] and evidence["checker_after"] == 0
    assert evidence["physical"] == "ok" and evidence["foreign_keys"] == []
    assert evidence["recovered"] == 1
