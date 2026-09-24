"""S5 schema upgrade preserves legacy MANUAL inclusion without inventing mastery."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_legacy_manual_cycle_is_classified_and_no_mastery_is_backfilled() -> None:
    probe = r"""
import json
import uuid
from datetime import UTC, datetime

import django
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

django.setup()

from modules.attempts.models import Attempt
from modules.domain.models import MasteryStateEvent
from modules.questions.services import create_active
from modules.reviews.models import ReviewCycle, ReviewCycleOriginKind, ReviewCycleState
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace

executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
workspace = bootstrap_local_workspace(timezone_id="UTC").workspace
discipline = create_discipline(workspace_id=workspace.id, name="Legacy")
subject = create_subject(workspace_id=workspace.id, discipline_id=discipline.id, name="Legacy")
question = create_active(
    workspace_id=workspace.id, discipline_id=discipline.id, subject_id=subject.id,
    stem="Legacy manual", alternatives=["Wrong", "Correct"], correct_alternative_position=2,
)
revision = question.revisions.get(is_current=True)
now = datetime.now(UTC)
initial = Attempt.objects.create(
    workspace=workspace, question=question, question_revision=revision,
    attempt_type="INITIAL", selected_alternative=revision.alternatives.get(position=2),
    is_correct=True, occurred_at=now, timezone_name="UTC", local_date=now.date(),
    idempotency_key=uuid.uuid4(),
)
manual = ReviewCycle.objects.create(
    workspace=workspace, question=question, origin_attempt=initial,
    origin_question_revision=revision, origin_kind=ReviewCycleOriginKind.MANUAL,
    manual_purpose="INCLUSION", state=ReviewCycleState.COMPLETED,
    started_at=now, completed_at=now,
)
MigrationExecutor(connection).migrate([("reviews", "0004_attempt_correction_projection")])
with connection.cursor() as cursor:
    before_column = any(row[1] == "manual_purpose" for row in cursor.execute("PRAGMA table_info(reviews_reviewcycle)"))
    before_cycle = cursor.execute("SELECT origin_kind FROM reviews_reviewcycle WHERE id = %s", [manual.id.hex]).fetchone()[0]
MigrationExecutor(connection).migrate([("domain", "0001_initial")])
restored = ReviewCycle.objects.get(pk=manual.id)
with connection.cursor() as cursor:
    physical = cursor.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_keys = cursor.execute("PRAGMA foreign_key_check").fetchall()
no_mastery_backfill = not MasteryStateEvent.objects.exists()
event = MasteryStateEvent.objects.create(
    workspace=workspace, question=question, sequence=1, event_type="DOMINATED",
    formula_code="DOM-HEUR-1.0", evaluated_on=now.date(), occurred_at=now,
)
try:
    MigrationExecutor(connection).migrate([("reviews", "0004_attempt_correction_projection")])
except RuntimeError as error:
    reverse_rejected = "Mastery history exists" in str(error)
else:
    reverse_rejected = False
print(json.dumps({
    "old_column_absent": not before_column,
    "old_cycle_manual": before_cycle == "MANUAL",
    "purpose": restored.manual_purpose,
    "origin_attempt_preserved": restored.origin_attempt_id == initial.id,
    "no_mastery_backfill": no_mastery_backfill,
    "reverse_rejected": reverse_rejected and MasteryStateEvent.objects.filter(pk=event.id).exists(),
    "physical": physical,
    "foreign_keys": foreign_keys,
}))
connection.close()
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
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
    assert evidence == {
        "old_column_absent": True,
        "old_cycle_manual": True,
        "purpose": "INCLUSION",
        "origin_attempt_preserved": True,
        "no_mastery_backfill": True,
        "reverse_rejected": True,
        "physical": "ok",
        "foreign_keys": [],
    }
