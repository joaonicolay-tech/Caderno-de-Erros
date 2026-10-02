"""Destination preflight must reject before the first attempted DML statement."""

import hashlib
import io
import json
import re
import sqlite3
import uuid
import zipfile
from collections.abc import Callable
from contextlib import closing
from pathlib import Path
from typing import Any

import pytest
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from probe_v10_s6_cei_prewrite import V044, snapshot

from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.data_management.portability import (
    ExportValidationError,
    export_bytes,
    import_into_empty,
    validate_export,
)
from modules.questions.services import create_active
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace


@pytest.fixture
def valid_package(transactional_db: None) -> bytes:
    del transactional_db
    bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="S2R2")
    subject = create_subject(
        workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="Preflight"
    )
    create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Destino compatÃ­vel",
        alternatives=["A", "B"],
        correct_alternative_position=1,
    )
    return export_bytes(workspace_id=LOCAL_WORKSPACE_ID)


@pytest.mark.parametrize(
    "damage",
    [
        "historical",
        "missing_migration",
        "extra_migration",
        "table",
        "column",
        "type",
        "null",
        "fk",
        "check",
        "unique",
        "trigger",
    ],
)
def test_incompatible_destination_rejects_before_write_attempt(
    valid_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    record_property: Callable[[str, object], None],
    damage: str,
) -> None:
    alias = "s2r2_" + uuid.uuid4().hex
    path = tmp_path / "destination.sqlite3"
    connections.databases[alias] = {**connections["default"].settings_dict, "NAME": str(path)}
    try:
        with django_db_blocker.unblock():
            connection = connections[alias]
            executor = MigrationExecutor(connection)
            executor.migrate(V044 if damage == "historical" else executor.loader.graph.leaf_nodes())
            with connection.cursor() as cursor:
                if damage == "missing_migration":
                    # Use an applied migration selected from the live graph, not a guessed name.
                    cursor.execute(
                        "DELETE FROM django_migrations WHERE id=(SELECT MAX(id) FROM django_migrations)"
                    )
                elif damage == "extra_migration":
                    cursor.execute(
                        "INSERT INTO django_migrations(app,name,applied) VALUES ('unknown','0001_extra',CURRENT_TIMESTAMP)"
                    )
                elif damage == "table":
                    cursor.execute("DROP TABLE errors_error_category")
                elif damage == "column":
                    cursor.execute(
                        "ALTER TABLE errors_error_category RENAME COLUMN category_kind TO broken_kind"
                    )
                elif damage == "unique":
                    cursor.execute(
                        "CREATE UNIQUE INDEX unexpected_unique ON errors_error_category(display_name)"
                    )
                elif damage == "trigger":
                    cursor.execute(
                        "CREATE TRIGGER unexpected_trigger AFTER INSERT ON accounts_user BEGIN SELECT 1; END"
                    )
                elif damage in {"type", "null", "fk", "check"}:
                    # Rebuild only this empty synthetic table, preserving migration metadata.
                    cursor.execute(
                        "SELECT sql FROM sqlite_master WHERE name='errors_error_category'"
                    )
                    original_ddl = cursor.fetchone()[0]
                    ddl = original_ddl
                    if damage == "type":
                        ddl = ddl.replace('"category_kind" varchar(16)', '"category_kind" integer')
                    elif damage == "null":
                        ddl = ddl.replace(
                            '"category_kind" varchar(16) NOT NULL',
                            '"category_kind" varchar(16) NULL',
                        )
                    elif damage == "check":
                        ddl = ddl.replace("'STANDARD', 'PERSONAL'", "'PERSONAL'")
                    else:
                        ddl = ddl.replace(
                            'REFERENCES "accounts_workspace" ("id")',
                            'REFERENCES "accounts_user" ("id")',
                        )
                    assert ddl != original_ddl
                    cursor.execute("DROP TABLE errors_error_category")
                    cursor.execute(ddl)
            connection.close()
            before = snapshot(path)
            physical_before = hashlib.sha256(path.read_bytes()).hexdigest()
            attempts = {"INSERT": 0, "UPDATE": 0, "DELETE": 0}
            connection.ensure_connection()
            raw = connection.connection
            assert raw is not None
            changes_before = raw.total_changes

            def observe(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
                matched = re.match(r"\s*(INSERT|UPDATE|DELETE)\b", sql, re.IGNORECASE)
                if matched:
                    attempts[matched.group(1).upper()] += 1
                return execute(sql, params, many, context)

            error = None
            with connection.execute_wrapper(observe):
                try:
                    import_into_empty(
                        package=validate_export(io.BytesIO(valid_package)), database_alias=alias
                    )
                except (
                    Exception
                ) as caught:  # Capture the original failure before asserting evidence.
                    error = caught
            changes = raw.total_changes - changes_before
            connection.close()
            after = snapshot(path)
            physical_after = hashlib.sha256(path.read_bytes()).hexdigest()
            evidence = {
                "damage": damage,
                "target": str(path),
                "attempts": attempts,
                "total_changes_delta": changes,
                "before": before,
                "after": after,
                "physical_before": physical_before,
                "physical_after": physical_after,
                "error": str(error),
                "error_type": type(error).__name__,
            }
            record_property("prewrite_evidence", json.dumps(evidence, sort_keys=True))
            assert isinstance(error, ExportValidationError), evidence
            assert "destino incompat" in str(error).lower(), evidence
            assert attempts == {"INSERT": 0, "UPDATE": 0, "DELETE": 0}, evidence
            assert changes == 0, evidence
            assert before == after, evidence
            assert physical_before == physical_after, evidence
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]


def test_valid_import_keeps_preflight_and_writes_in_one_schema_snapshot(
    valid_package: bytes, tmp_path: Path, django_db_blocker: Any
) -> None:
    alias = "s2r2_" + uuid.uuid4().hex
    path = tmp_path / "compatible.sqlite3"
    connections.databases[alias] = {**connections["default"].settings_dict, "NAME": str(path)}
    try:
        with django_db_blocker.unblock():
            connection = connections[alias]
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
            first_write = False
            locked_schema_change = False
            preflight_reads = 0

            def observe(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
                nonlocal first_write, locked_schema_change, preflight_reads
                if sql.startswith("SELECT") and not first_write:
                    assert connection.in_atomic_block
                    preflight_reads += 1
                if re.match(r"\s*(INSERT|UPDATE|DELETE)\b", sql, re.IGNORECASE) and not first_write:
                    first_write = True
                    assert connection.in_atomic_block
                    assert preflight_reads > 0
                    with closing(sqlite3.connect(path, timeout=0.05)) as competitor:
                        try:
                            competitor.execute(
                                "ALTER TABLE errors_error_category "
                                "RENAME COLUMN category_kind TO concurrently_changed"
                            )
                            competitor.commit()
                        except sqlite3.OperationalError as error:
                            assert "locked" in str(error).lower()
                            locked_schema_change = True
                        finally:
                            competitor.rollback()
                return execute(sql, params, many, context)

            with connection.execute_wrapper(observe):
                result = import_into_empty(
                    package=validate_export(io.BytesIO(valid_package)), database_alias=alias
                )
            assert first_write and locked_schema_change
            assert result["questions"] == 1
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA foreign_key_check")
                assert cursor.fetchall() == []
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]


def test_occupied_workspace_is_rejected_without_write_attempt(valid_package: bytes) -> None:
    attempts = []

    def observe(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
        if re.match(r"\s*(INSERT|UPDATE|DELETE)\b", sql, re.IGNORECASE):
            attempts.append(sql)
        return execute(sql, params, many, context)

    with connections["default"].execute_wrapper(observe):
        with pytest.raises(ExportValidationError, match="merge é proibido"):
            import_into_empty(package=validate_export(io.BytesIO(valid_package)))
    assert attempts == []


@pytest.mark.parametrize(
    ("damage", "reason"),
    [
        ("manifest", "Manifesto"),
        ("migrations", "metadata incompatível"),
        ("policies", "metadata incompatível"),
        ("uuid", "tipo ou valor inválido"),
        ("reference", "Referência funcional ausente"),
        ("duplicate", "UUID duplicado"),
        ("workspace", "cross-Workspace"),
    ],
)
def test_invalid_package_never_reaches_destination_write(
    valid_package: bytes, damage: str, reason: str
) -> None:
    with zipfile.ZipFile(io.BytesIO(valid_package)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    manifest = json.loads(entries["manifest.json"])
    if damage == "manifest":
        del manifest["workspace_timezone"]
    elif damage == "migrations":
        manifest["schema_migrations"].pop()
    elif damage == "policies":
        manifest["policies"]["review"] = "unsupported"
    else:
        questions = json.loads(entries["questions.json"])
        if damage == "uuid":
            questions[0]["id"] = "invalid"
        elif damage == "reference":
            questions[0]["subject"] = str(uuid.uuid4())
        elif damage == "duplicate":
            questions.append(questions[0].copy())
        else:
            questions[0]["workspace"] = str(uuid.uuid4())
        entries["questions.json"] = json.dumps(questions).encode("utf-8")
        for entry in manifest["files"]:
            if entry["name"] == "questions.json":
                entry["count"] = len(questions)
                entry["size_bytes"] = len(entries["questions.json"])
                entry["sha256"] = hashlib.sha256(entries["questions.json"]).hexdigest()
    entries["manifest.json"] = json.dumps(manifest).encode("utf-8")
    changed = io.BytesIO()
    with zipfile.ZipFile(changed, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    attempts = []

    def observe(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
        if re.match(r"\s*(INSERT|UPDATE|DELETE)\b", sql, re.IGNORECASE):
            attempts.append(sql)
        return execute(sql, params, many, context)

    changed.seek(0)
    with connections["default"].execute_wrapper(observe):
        with pytest.raises(ExportValidationError, match=reason):
            import_into_empty(package=validate_export(changed))
    assert attempts == []
