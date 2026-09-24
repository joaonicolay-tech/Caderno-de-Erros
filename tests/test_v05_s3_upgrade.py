"""Upgrade e downgrade isolados da preference SavedFilter V0.5-S3."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_s2d_data_survives_saved_filter_migration_and_empty_rollback() -> None:
    probe = r"""
import json
import django
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

django.setup()

from modules.accounts.services import LOCAL_USER_ID
from modules.questions.models import Question, QuestionRevision
from modules.questions.services import create_active
from modules.search.models import SavedFilter
from modules.search.saved_filter_services import create_saved_filter
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace

s2d = [
    ("auth", "0012_alter_user_first_name_max_length"),
    ("attempts", "0002_review_receipt_constraints"),
    ("errors", "0003_errorcategory_category_kind_and_more"),
    ("operations", "0004_remove_auditevent_audit_event_code_valid_and_more"),
    ("questions", "0002_question_catalog"),
    ("reviews", "0004_attempt_correction_projection"),
    ("taxonomy", "0001_initial"),
]
MigrationExecutor(connection).migrate(s2d)
MigrationExecutor(connection).migrate([*s2d, ("domain", "0001_initial")])
workspace = bootstrap_local_workspace(timezone_id="UTC").workspace
discipline = create_discipline(workspace_id=workspace.id, name="Migration S3")
subject = create_subject(workspace_id=workspace.id, discipline_id=discipline.id, name="Upgrade")
question = create_active(
    workspace_id=workspace.id,
    discipline_id=discipline.id,
    subject_id=subject.id,
    stem="Fato anterior preservado",
    alternatives=["N\u00e3o", "Sim"],
    correct_alternative_position=2,
)
before = question.revisions.filter(is_current=True).values_list("stem", flat=True).get()
executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
new_table_present = "search_savedfilter" in connection.introspection.table_names()
created = create_saved_filter(
    workspace_id=workspace.id,
    owner_user_id=LOCAL_USER_ID,
    name="Migra\u00e7\u00e3o",
    payload={"status": "ACTIVE"},
)
schema_version = SavedFilter.objects.get(pk=created.id).schema_version
executor = MigrationExecutor(connection)
executor.migrate([("search", None)])
tables_after_rollback = connection.introspection.table_names()
preserved = QuestionRevision.objects.filter(
    question_id=question.id, is_current=True
).values_list("stem", flat=True).get()
print(json.dumps({
    "new_table_present": new_table_present,
    "schema_version": schema_version,
    "question_preserved": before == preserved,
    "old_schema_absent": "search_savedfilter" not in tables_after_rollback,
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
        "new_table_present": True,
        "schema_version": 1,
        "question_preserved": True,
        "old_schema_absent": True,
    }
