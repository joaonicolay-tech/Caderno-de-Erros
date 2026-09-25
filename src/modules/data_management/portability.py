"""CEI-EXPORT-1.0: functional ZIP/JSON portability for an empty compatible install."""

import hashlib
import io
import json
import re
import stat
import tempfile
import uuid
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any, BinaryIO, cast

from django.apps import apps
from django.db import connections, transaction
from django.db.migrations.loader import MigrationLoader
from django.db.models import Model

from modules.accounts.models import User, Workspace
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.domain.policy import POLICY_VERSION as DOMAIN_POLICY
from modules.operations.integrity import run_integrity_check
from modules.priority.policy import POLICY_VERSION as PRIORITY_POLICY
from modules.reviews.models import ReviewCycle
from modules.search.saved_filter_services import (
    QUESTIONS_LIST_FIELDS,
    QUESTIONS_LIST_SCHEMA_VERSION,
)

FORMAT = "CEI-EXPORT"
VERSION = "1.0"
APPLICATION_VERSION = "V0.5"
_SHA = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class RecordSet:
    name: str
    model: str
    fields: tuple[str, ...]


def _set(name: str, model: str, fields: str) -> RecordSet:
    return RecordSet(name, model, tuple(fields.split()))


# This closed list is the functional format, not an automatic ORM dump.
SETS = (
    _set(
        "workspace",
        "accounts.Workspace",
        "id name timezone_name locale lock_version created_at updated_at",
    ),
    _set(
        "disciplines",
        "taxonomy.Discipline",
        "id workspace name name_key status sort_order archived_at lock_version created_at updated_at",
    ),
    _set(
        "subjects",
        "taxonomy.Subject",
        "id workspace discipline name name_key status sort_order archived_at lock_version created_at updated_at",
    ),
    _set(
        "subsubjects",
        "taxonomy.Subsubject",
        "id workspace subject name name_key status sort_order archived_at lock_version created_at updated_at",
    ),
    _set(
        "boards",
        "questions.Board",
        "id workspace name name_key status archived_at lock_version created_at updated_at website_url",
    ),
    _set(
        "exams",
        "questions.Exam",
        "id workspace board name name_key status archived_at lock_version created_at updated_at year",
    ),
    _set(
        "sources",
        "questions.Source",
        "id workspace name name_key status archived_at lock_version created_at updated_at source_type locator_url notes",
    ),
    _set(
        "questions",
        "questions.Question",
        "id workspace discipline subject subsubject question_type status difficulty draft_title activated_at archived_at lock_version created_at updated_at",
    ),
    _set(
        "question_revisions",
        "questions.QuestionRevision",
        "id workspace question version_number is_current stem explanation trap_note notes correct_alternative change_kind change_reason created_at",
    ),
    _set(
        "alternatives",
        "questions.Alternative",
        "id workspace question_revision position label text text_key created_at",
    ),
    _set(
        "question_origins",
        "questions.QuestionOrigin",
        "id workspace question source exam board reference_year reference_text lock_version created_at updated_at",
    ),
    _set(
        "attempts",
        "attempts.Attempt",
        "id workspace question question_revision review attempt_type selected_alternative is_correct perceived_ease occurred_at timezone_name local_date status replaces_attempt voided_at void_reason idempotency_key created_at",
    ),
    _set(
        "error_categories",
        "errors.ErrorCategory",
        "id workspace code display_name name_key description category_kind state merged_into lock_version created_at updated_at",
    ),
    _set(
        "error_classifications",
        "errors.ErrorClassification",
        "id workspace attempt category other_description lock_version created_at updated_at",
    ),
    _set(
        "error_classification_revisions",
        "errors.ErrorClassificationRevision",
        "id workspace error_classification revision_number category other_description change_reason created_at",
    ),
    _set(
        "review_cycles",
        "reviews.ReviewCycle",
        "id workspace question origin_attempt origin_question_revision origin_kind manual_purpose policy_code state started_at completed_at suspended_at superseded_at suspension_reason lock_version created_at updated_at",
    ),
    _set(
        "reviews",
        "reviews.Review",
        "id workspace review_cycle question sequence_number stage_code state first_due_date current_due_date scheduled_from_attempt transition_code policy_code completed_at suspended_at lock_version created_at updated_at",
    ),
    _set(
        "review_schedule_changes",
        "reviews.ReviewScheduleChange",
        "id workspace review previous_due_date new_due_date timezone_name reason_code correlation_id created_at",
    ),
    _set(
        "saved_filters",
        "search.SavedFilter",
        "id workspace name name_key context_code schema_version payload created_at updated_at",
    ),
    _set(
        "mastery_events",
        "domain.MasteryStateEvent",
        "id workspace question sequence event_type formula_code evaluated_on domain_index confidence trigger_attempt manual_cycle reason_code occurred_at",
    ),
    _set(
        "audit_events",
        "operations.AuditEvent",
        "id workspace event_code entity_type entity_id previous_entity_id related_entity_id correlation_id reason_code previous_date new_date timezone_name created_at",
    ),
)


class ExportValidationError(ValueError):
    """Untrusted functional package is invalid or incompatible."""


def _schema_migrations() -> list[str]:
    return sorted(f"{app}.{name}" for app, name in MigrationLoader(None).disk_migrations)


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    ).encode("utf-8")


def _encode(value: object) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat(timespec="microseconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (dict, list)):
        return value
    raise TypeError("Campo funcional sem codificação explícita.")


def _row(model: Model, spec: RecordSet) -> dict[str, object]:
    result: dict[str, object] = {}
    for name in spec.fields:
        field = cast(Any, model._meta.get_field(name))
        attribute = field.attname if field.is_relation else name
        result[name] = _encode(getattr(model, attribute))
    return result


def _model(spec: RecordSet) -> type[Model]:
    return apps.get_model(spec.model)


def _write_entry(archive: zipfile.ZipFile, name: str, chunks: Iterator[bytes]) -> dict[str, object]:
    digest = hashlib.sha256()
    size = 0
    with archive.open(name, "w", force_zip64=True) as output:
        for chunk in chunks:
            output.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    return {"name": name, "size_bytes": size, "sha256": digest.hexdigest()}


def _record_chunks(
    spec: RecordSet, workspace_id: uuid.UUID, database_alias: str
) -> Iterator[bytes]:
    model = _model(spec)
    records = (
        model._base_manager.using(database_alias).filter(pk=workspace_id)
        if spec.name == "workspace"
        else model._base_manager.using(database_alias).filter(workspace_id=workspace_id)
    )
    yield b"["
    first = True
    for record in records.order_by("pk").iterator(chunk_size=200):
        if not first:
            yield b","
        yield _json_bytes(_row(record, spec)).rstrip(b"\n")
        first = False
    yield b"]\n"


def export_workspace(
    *, workspace_id: uuid.UUID, destination: BinaryIO, database_alias: str = "default"
) -> dict[str, object]:
    """Write a deterministic functional package without changing the database."""
    workspace = (
        Workspace.objects.using(database_alias)
        .filter(pk=workspace_id, owner_user_id=LOCAL_USER_ID)
        .first()
    )
    if workspace is None or workspace_id != LOCAL_WORKSPACE_ID:
        raise ExportValidationError("Workspace não autorizado para exportação.")
    files: list[dict[str, object]] = []
    with (
        transaction.atomic(using=database_alias),
        zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive,
    ):
        for spec in SETS:
            name = f"{spec.name}.json"
            entry = _write_entry(archive, name, _record_chunks(spec, workspace_id, database_alias))
            manager = _model(spec)._base_manager.using(database_alias)
            entry["count"] = (
                manager.filter(pk=workspace_id).count()
                if spec.name == "workspace"
                else manager.filter(workspace_id=workspace_id).count()
            )
            files.append(entry)
        readme = (
            "CEI-EXPORT-1.0: dados funcionais em JSON UTF-8.\n"
            "Schema: docs/CEI_EXPORT_1_0.md. Importação S7 requer destino vazio compatível; "
            "merge não é suportado. SQLite não integra este pacote.\n"
        ).encode()
        entry = _write_entry(archive, "README.txt", iter((readme,)))
        entry["count"] = 0
        files.append(entry)
        manifest: dict[str, object] = {
            "format": FORMAT,
            "format_version": VERSION,
            "generated_at": datetime.now(UTC).isoformat(timespec="microseconds"),
            "application_version": APPLICATION_VERSION,
            "schema_migrations": _schema_migrations(),
            "workspace_id": str(workspace_id),
            "workspace_timezone": workspace.timezone_name,
            "policies": {
                "review": ReviewCycle.POLICY_CODE,
                "domain": DOMAIN_POLICY,
                "priority": PRIORITY_POLICY,
            },
            "files": files,
        }
        archive.writestr("manifest.json", _json_bytes(manifest))
    return manifest


def _unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ExportValidationError("JSON contém campo duplicado.")
        result[key] = value
    return result


def _parse_json(data: bytes) -> Any:
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_keys)
    except (UnicodeError, ValueError) as error:
        raise ExportValidationError("JSON UTF-8 inválido.") from error


def _valid_instant(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        instant = datetime.fromisoformat(value)
    except ValueError:
        return False
    return instant.tzinfo is not None and instant.utcoffset() == UTC.utcoffset(instant)


def _decoded(value: object, field: Any) -> object:
    if value is None:
        if not field.null:
            raise ExportValidationError("Campo obrigatório ausente.")
        return None
    kind = field.get_internal_type()
    try:
        if field.is_relation or kind == "UUIDField":
            if not isinstance(value, str):
                raise ValueError
            return uuid.UUID(value)
        if kind == "DateTimeField":
            if not _valid_instant(value):
                raise ValueError
            return datetime.fromisoformat(str(value))
        if kind == "DateField":
            if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError
            return date.fromisoformat(value)
        if kind == "DecimalField":
            if not isinstance(value, str):
                raise ValueError
            decimal = Decimal(value)
            if not decimal.is_finite():
                raise ValueError
            return decimal
        if kind == "BooleanField":
            if not isinstance(value, bool):
                raise ValueError
            return value
        if kind in {
            "IntegerField",
            "PositiveIntegerField",
            "PositiveSmallIntegerField",
            "SmallIntegerField",
        }:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError
            return value
        if kind == "JSONField":
            if not isinstance(value, (dict, list)):
                raise ValueError
            return value
        if kind in {"CharField", "TextField"}:
            if not isinstance(value, str):
                raise ValueError
            if field.max_length is not None and len(value) > field.max_length:
                raise ValueError
            if field.choices and value not in {choice for choice, _ in field.flatchoices}:
                raise ValueError
            return value
    except (ValueError, ArithmeticError) as error:
        raise ExportValidationError("Campo funcional possui tipo ou valor inválido.") from error
    raise ExportValidationError("Campo funcional desconhecido.")


@dataclass(frozen=True)
class ValidatedExport:
    manifest: dict[str, Any]
    rows: dict[str, list[dict[str, object]]]


def validate_export(source: BinaryIO) -> ValidatedExport:
    """Validate container, integrity, schema and graph without mutating storage."""
    try:
        with zipfile.ZipFile(source) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            expected = {"manifest.json", "README.txt", *(f"{item.name}.json" for item in SETS)}
            if (
                len(names) != len(expected)
                or set(names) != expected
                or len(set(names)) != len(names)
            ):
                raise ExportValidationError("Pacote contém arquivos ausentes ou inesperados.")
            for info in infos:
                mode = (info.external_attr >> 16) & 0xFFFF
                if (
                    info.filename not in expected
                    or "/" in info.filename
                    or "\\" in info.filename
                    or ":" in info.filename
                    or info.is_dir()
                    or stat.S_ISLNK(mode)
                    or info.flag_bits & 1
                    or info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}
                ):
                    raise ExportValidationError("Entrada ZIP insegura.")
            manifest = _parse_json(archive.read("manifest.json"))
            required = {
                "format",
                "format_version",
                "generated_at",
                "application_version",
                "schema_migrations",
                "workspace_id",
                "workspace_timezone",
                "policies",
                "files",
            }
            if not isinstance(manifest, dict) or set(manifest) != required:
                raise ExportValidationError("Manifesto inválido.")
            if manifest["format"] != FORMAT or manifest["format_version"] != VERSION:
                raise ExportValidationError("Versão ou formato CEI incompatível.")
            if (
                not _valid_instant(manifest["generated_at"])
                or manifest["application_version"] != APPLICATION_VERSION
                or manifest["schema_migrations"] != _schema_migrations()
                or not isinstance(manifest["workspace_timezone"], str)
                or manifest["policies"]
                != {
                    "review": ReviewCycle.POLICY_CODE,
                    "domain": DOMAIN_POLICY,
                    "priority": PRIORITY_POLICY,
                }
            ):
                raise ExportValidationError("Schema ou metadata incompatível.")
            try:
                workspace_id = uuid.UUID(manifest["workspace_id"])
            except (TypeError, ValueError, AttributeError) as error:
                raise ExportValidationError("Workspace inválido.") from error
            files = manifest["files"]
            if not isinstance(files, list) or len(files) != len(expected) - 1:
                raise ExportValidationError("Lista do manifesto incompleta.")
            entries: dict[str, dict[str, Any]] = {}
            for item in files:
                if not isinstance(item, dict) or set(item) != {
                    "name",
                    "size_bytes",
                    "sha256",
                    "count",
                }:
                    raise ExportValidationError("Entrada do manifesto inválida.")
                name = item["name"]
                if (
                    not isinstance(name, str)
                    or name in entries
                    or name not in expected - {"manifest.json"}
                ):
                    raise ExportValidationError("Entrada do manifesto inesperada.")
                if (
                    isinstance(item["size_bytes"], bool)
                    or not isinstance(item["size_bytes"], int)
                    or item["size_bytes"] < 0
                    or isinstance(item["count"], bool)
                    or not isinstance(item["count"], int)
                    or item["count"] < 0
                    or not isinstance(item["sha256"], str)
                    or _SHA.fullmatch(item["sha256"]) is None
                ):
                    raise ExportValidationError("Tamanho, contagem ou SHA-256 inválido.")
                entries[name] = item
            if set(entries) != expected - {"manifest.json"}:
                raise ExportValidationError("Arquivos do manifesto não coincidem com ZIP.")
            rows: dict[str, list[dict[str, object]]] = {}
            for name, item in entries.items():
                if archive.getinfo(name).file_size != item["size_bytes"]:
                    raise ExportValidationError("INVALID_EXPORT_INTEGRITY")
                with tempfile.TemporaryFile(mode="w+b") as staged:
                    digest = hashlib.sha256()
                    size = 0
                    with archive.open(name) as source_file:
                        while chunk := source_file.read(1024 * 1024):
                            staged.write(chunk)
                            digest.update(chunk)
                            size += len(chunk)
                    if size != item["size_bytes"] or digest.hexdigest() != item["sha256"]:
                        raise ExportValidationError("INVALID_EXPORT_INTEGRITY")
                    staged.seek(0)
                    if name == "README.txt":
                        if item["count"] != 0 or not staged.read().decode("utf-8").startswith(
                            "CEI-EXPORT-1.0:"
                        ):
                            raise ExportValidationError("README inválido.")
                        continue
                    try:
                        with io.TextIOWrapper(staged, encoding="utf-8") as text_file:
                            parsed = json.load(text_file, object_pairs_hook=_unique_keys)
                    except ValueError as error:
                        raise ExportValidationError("JSON UTF-8 inválido.") from error
                if not isinstance(parsed, list) or len(parsed) != item["count"]:
                    raise ExportValidationError("Contagem funcional divergente.")
                spec = next(spec for spec in SETS if name == f"{spec.name}.json")
                model = _model(spec)
                typed: list[dict[str, object]] = []
                for row in parsed:
                    if not isinstance(row, dict) or set(row) != set(spec.fields):
                        raise ExportValidationError("Campos funcionais incompletos ou inesperados.")
                    decoded = {
                        key: _decoded(row[key], model._meta.get_field(key)) for key in spec.fields
                    }
                    if spec.name != "workspace" and decoded["workspace"] != workspace_id:
                        raise ExportValidationError("Referência cross-Workspace.")
                    typed.append(decoded)
                rows[spec.name] = typed
            if (
                len(rows["workspace"]) != 1
                or rows["workspace"][0]["id"] != workspace_id
                or rows["workspace"][0]["timezone_name"] != manifest["workspace_timezone"]
            ):
                raise ExportValidationError("Identidade do Workspace não coincide.")
            _validate_relations(rows)
            return ValidatedExport(manifest, rows)
    except (zipfile.BadZipFile, EOFError, OSError, UnicodeError) as error:
        raise ExportValidationError("Pacote CEI inválido.") from error


def _validate_relations(rows: dict[str, list[dict[str, object]]]) -> None:
    ids = {spec.model: {row["id"] for row in rows[spec.name]} for spec in SETS}
    for row in rows["saved_filters"]:
        payload = row["payload"]
        if (
            row["schema_version"] != QUESTIONS_LIST_SCHEMA_VERSION
            or not isinstance(payload, dict)
            or set(payload) - QUESTIONS_LIST_FIELDS
            or any(not isinstance(value, str) for value in payload.values())
        ):
            raise ExportValidationError("Payload de filtro salvo incompatível.")
        for name in ("discipline", "subject", "subsubject", "error_category"):
            value = payload.get(name, "")
            if not value or (name == "error_category" and value == "unclassified"):
                continue
            try:
                uuid.UUID(value)
            except ValueError as error:
                raise ExportValidationError("Referência de filtro salvo inválida.") from error
    for spec in SETS:
        model = _model(spec)
        if len(ids[spec.model]) != len(rows[spec.name]):
            raise ExportValidationError("UUID duplicado no conjunto funcional.")
        for row in rows[spec.name]:
            for name in spec.fields:
                field = cast(Any, model._meta.get_field(name))
                if not field.is_relation or row[name] is None:
                    continue
                related_model = field.related_model
                if related_model is None:
                    raise ExportValidationError("Relação funcional desconhecida.")
                target = related_model._meta.label
                if target == "accounts.User":
                    continue
                if row[name] not in ids.get(target, set()):
                    raise ExportValidationError("Referência funcional ausente.")


def import_into_empty(
    *, package: ValidatedExport, database_alias: str = "default"
) -> dict[str, int]:
    """Import only after independent validation, atomically into an empty install."""
    if database_alias == "default" and package.rows["workspace"][0]["id"] != LOCAL_WORKSPACE_ID:
        raise ExportValidationError("Workspace incompatível com a instalação local.")
    if Workspace.objects.using(database_alias).exists():
        raise ExportValidationError("Destino já contém Workspace; merge é proibido.")
    connection = connections[database_alias]
    if connection.vendor != "sqlite":
        raise ExportValidationError("Importação S7 requer SQLite compatível.")
    with transaction.atomic(using=database_alias):
        if not User.objects.using(database_alias).filter(pk=LOCAL_USER_ID).exists():
            user = User(id=LOCAL_USER_ID, status="ACTIVE")
            user.set_unusable_password()
            user.save(using=database_alias)
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA defer_foreign_keys = ON")
            for spec in SETS:
                model = _model(spec)
                fields = [cast(Any, model._meta.get_field(name)) for name in spec.fields]
                field_names = [cast(str, field.column) for field in fields]
                if spec.name in {"workspace", "saved_filters"}:
                    field_names.append("owner_user_id")
                quoted_table = connection.ops.quote_name(model._meta.db_table)
                columns = ", ".join(connection.ops.quote_name(name) for name in field_names)
                placeholders = ", ".join("%s" for _ in field_names)
                # Identifiers come only from the closed in-code SETS and model metadata.
                sql = f"INSERT INTO {quoted_table} ({columns}) VALUES ({placeholders})"  # noqa: S608
                for row in package.rows[spec.name]:
                    values = [
                        field.get_db_prep_save(row[field.name], connection) for field in fields
                    ]
                    if spec.name in {"workspace", "saved_filters"}:
                        values.append(LOCAL_USER_ID.hex)
                    cursor.execute(sql, values)
            cursor.execute("PRAGMA foreign_key_check")
            if cursor.fetchone() is not None:
                raise ExportValidationError("Relações importadas não reconciliam.")
        integrity = run_integrity_check(using=database_alias)
        if integrity.has_blocking_findings:
            raise ExportValidationError("Fatos importados violam invariantes funcionais.")
    return {spec.name: len(package.rows[spec.name]) for spec in SETS}


def export_bytes(*, workspace_id: uuid.UUID) -> bytes:
    """Small artifact helper for focused tests; UI uses a temporary file."""
    buffer = io.BytesIO()
    export_workspace(workspace_id=workspace_id, destination=buffer)
    return buffer.getvalue()
