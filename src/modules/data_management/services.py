"""Snapshot SQLite, manifesto, validação e restauração isolada da V0.1."""

import hashlib
import json
import logging
import os
import re
import sqlite3
import tempfile
from collections.abc import Callable, Mapping
from contextlib import closing
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

from django.db import connections
from django.db.migrations.loader import MigrationLoader

from modules.accounts.models import UserStatus, WorkspaceLocale
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.errors.catalog import STANDARD_ERROR_CATEGORIES
from modules.operations.correlation import correlation_scope
from modules.operations.events import EventCode, EventOutcome
from modules.operations.structured_logging import emit_event
from shared.domain.time import TimeZoneId

from .exceptions import BackupCreationError, BackupValidationError, RestoreError

BACKUP_FORMAT = "CEI-SQLITE-BACKUP"
BACKUP_FORMAT_VERSION = "1.0"
MANIFEST_SUFFIX = ".manifest.json"
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_BUFFER_SIZE = 1024 * 1024


@dataclass(frozen=True, slots=True)
class BackupManifest:
    """Metadados técnicos mínimos, sem caminhos ou conteúdo privado."""

    format: str
    format_version: str
    created_at: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class BackupValidationResult:
    """Evidência de que manifesto, checksum e SQLite são íntegros."""

    manifest: BackupManifest


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    """Contagens comprovadas no banco restaurado da fundação."""

    migration_count: int
    user_count: int
    workspace_count: int
    category_count: int


@dataclass(frozen=True, slots=True)
class RestoreResult:
    """Resultado publicado somente após a reconciliação integral."""

    manifest: BackupManifest
    reconciliation: ReconciliationResult


def manifest_path_for(backup_path: Path | str) -> Path:
    """Derive o sidecar sem armazenar o caminho dentro do manifesto."""
    backup = Path(backup_path)
    return backup.with_name(f"{backup.name}{MANIFEST_SUFFIX}")


def _database_path(database_alias: str, *, require_existing: bool = True) -> Path:
    configuration = connections[database_alias].settings_dict
    if configuration.get("ENGINE") != "django.db.backends.sqlite3":
        raise BackupCreationError("O mecanismo da V0.1 aceita somente SQLite.")
    configured_name = configuration.get("NAME")
    if not isinstance(configured_name, (str, Path)) or str(configured_name) == ":memory:":
        raise BackupCreationError("O banco SQLite precisa ser um arquivo local.")
    database_path = Path(configured_name).resolve()
    if require_existing and not database_path.is_file():
        raise BackupCreationError("O banco SQLite não está disponível para backup.")
    return database_path


def _resolved_output(path: Path | str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.parent.is_dir():
        raise ValueError("O diretório de destino precisa existir.")
    if resolved.exists():
        raise FileExistsError("O destino já existe e não será substituído.")
    return resolved


def _temporary_file(directory: Path, suffix: str) -> Path:
    descriptor, raw_path = tempfile.mkstemp(prefix=".cei-", suffix=suffix, dir=directory)
    os.close(descriptor)
    return Path(raw_path)


def _remove_created_file(path: Path | None) -> bool:
    if path is None:
        return True
    try:
        path.unlink(missing_ok=True)
    except OSError:
        return False
    return True


def _publish_new_file(temporary_path: Path, destination: Path) -> None:
    """Publique sem a semântica de sobrescrita de ``os.replace``."""
    if os.name == "nt":
        os.rename(temporary_path, destination)
        return
    os.link(temporary_path, destination)
    temporary_path.unlink()


def _readonly_connection(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True, timeout=5.0)


def _sqlite_backup(source: Path, destination: Path) -> None:
    with (
        closing(_readonly_connection(source)) as source_connection,
        closing(sqlite3.connect(destination, timeout=5.0)) as destination_connection,
    ):
        with destination_connection:
            source_connection.backup(destination_connection)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        while chunk := artifact.read(_BUFFER_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _flush_file(path: Path) -> None:
    with path.open("r+b") as artifact:
        os.fsync(artifact.fileno())


def _validate_sqlite_file(path: Path) -> None:
    try:
        with closing(_readonly_connection(path)) as database:
            integrity_rows = database.execute("PRAGMA integrity_check").fetchall()
            foreign_key_rows = database.execute("PRAGMA foreign_key_check").fetchall()
    except sqlite3.Error as error:
        raise BackupValidationError("O artefato não é um banco SQLite íntegro.") from error
    if integrity_rows != [("ok",)] or foreign_key_rows:
        raise BackupValidationError("A verificação interna do SQLite encontrou inconsistências.")


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    document: dict[str, object] = {}
    for key, value in pairs:
        if key in document:
            raise ValueError("Campo duplicado no manifesto.")
        document[key] = value
    return document


def _parse_manifest(path: Path) -> BackupManifest:
    try:
        raw_document = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        raise BackupValidationError("O manifesto não é um JSON válido.") from error
    if not isinstance(raw_document, dict):
        raise BackupValidationError("O manifesto precisa ser um objeto JSON.")
    document = cast(dict[str, object], raw_document)
    required_fields = {"format", "format_version", "created_at", "size_bytes", "sha256"}
    if set(document) != required_fields:
        raise BackupValidationError("O manifesto não possui exatamente os campos esperados.")

    format_name = document["format"]
    format_version = document["format_version"]
    created_at = document["created_at"]
    size_bytes = document["size_bytes"]
    checksum = document["sha256"]
    if format_name != BACKUP_FORMAT or format_version != BACKUP_FORMAT_VERSION:
        raise BackupValidationError("O formato ou a versão do backup não é compatível.")
    if not isinstance(created_at, str):
        raise BackupValidationError("O instante de criação do manifesto é inválido.")
    try:
        parsed_created_at = datetime.fromisoformat(created_at)
    except ValueError as error:
        raise BackupValidationError("O instante de criação do manifesto é inválido.") from error
    if parsed_created_at.utcoffset() != UTC.utcoffset(parsed_created_at):
        raise BackupValidationError("O instante de criação precisa estar em UTC.")
    if not isinstance(size_bytes, int) or isinstance(size_bytes, bool) or size_bytes <= 0:
        raise BackupValidationError("O tamanho declarado no manifesto é inválido.")
    if not isinstance(checksum, str) or _SHA256_PATTERN.fullmatch(checksum) is None:
        raise BackupValidationError("O checksum declarado no manifesto é inválido.")
    return BackupManifest(
        format=format_name,
        format_version=format_version,
        created_at=created_at,
        size_bytes=size_bytes,
        sha256=checksum,
    )


def _validate_backup_files(backup: Path, manifest_file: Path) -> BackupManifest:
    if not backup.is_file() or not manifest_file.is_file():
        raise BackupValidationError("O backup e seu manifesto precisam existir como arquivos.")
    manifest = _parse_manifest(manifest_file)
    if backup.stat().st_size != manifest.size_bytes:
        raise BackupValidationError("O tamanho do backup não corresponde ao manifesto.")
    if _sha256(backup) != manifest.sha256:
        raise BackupValidationError("O checksum SHA-256 do backup é inválido.")
    _validate_sqlite_file(backup)
    return manifest


def _event_failure(
    event_code: EventCode,
    *,
    operation: str,
    error_code: str,
    error: Exception,
    temporary_cleanup_succeeded: bool = True,
) -> None:
    emit_event(
        event_code,
        operation=operation,
        outcome=EventOutcome.FAILED,
        level=logging.ERROR,
        context={
            "error_code": error_code,
            "error_type": type(error).__name__,
            "temporary_cleanup_succeeded": temporary_cleanup_succeeded,
        },
    )


def create_sqlite_backup(
    output_path: Path | str,
    *,
    database_alias: str = "default",
    correlation_id: str | None = None,
    now: Callable[[], datetime] | None = None,
) -> BackupValidationResult:
    """Crie e valide um snapshot consistente sem substituir artefatos existentes."""
    temporary_backup: Path | None = None
    temporary_manifest: Path | None = None
    published_backup: Path | None = None
    published_manifest: Path | None = None
    with correlation_scope(correlation_id):
        emit_event(
            EventCode.BACKUP_STARTED,
            operation="backup.create",
            outcome=EventOutcome.STARTED,
        )
        try:
            source = _database_path(database_alias)
            output = _resolved_output(output_path)
            manifest_file = manifest_path_for(output).resolve()
            if output == source or manifest_file == source:
                raise BackupCreationError("O backup não pode substituir o banco principal.")
            if manifest_file.exists():
                raise BackupCreationError("O manifesto de destino já existe.")

            temporary_backup = _temporary_file(output.parent, ".sqlite3.tmp")
            temporary_manifest = _temporary_file(output.parent, ".manifest.tmp")
            _sqlite_backup(source, temporary_backup)
            _validate_sqlite_file(temporary_backup)
            _flush_file(temporary_backup)

            instant = (now or (lambda: datetime.now(UTC)))()
            if instant.tzinfo is None:
                raise BackupCreationError("O relógio do backup precisa fornecer instante com fuso.")
            manifest = BackupManifest(
                format=BACKUP_FORMAT,
                format_version=BACKUP_FORMAT_VERSION,
                created_at=instant.astimezone(UTC).isoformat(timespec="milliseconds"),
                size_bytes=temporary_backup.stat().st_size,
                sha256=_sha256(temporary_backup),
            )
            temporary_manifest.write_text(
                f"{json.dumps(asdict(manifest), ensure_ascii=False, indent=2)}\n",
                encoding="utf-8",
            )
            _flush_file(temporary_manifest)

            _publish_new_file(temporary_backup, output)
            temporary_backup = None
            published_backup = output
            _publish_new_file(temporary_manifest, manifest_file)
            temporary_manifest = None
            published_manifest = manifest_file
            validated_manifest = _validate_backup_files(output, manifest_file)
        except Exception as error:
            cleanup_succeeded = all(
                (
                    _remove_created_file(temporary_backup),
                    _remove_created_file(temporary_manifest),
                    _remove_created_file(published_manifest),
                    _remove_created_file(published_backup),
                )
            )
            _event_failure(
                EventCode.BACKUP_FAILED,
                operation="backup.create",
                error_code="BACKUP_CREATION_FAILED",
                error=error,
                temporary_cleanup_succeeded=cleanup_succeeded,
            )
            if isinstance(error, BackupCreationError):
                raise
            if isinstance(error, (BackupValidationError, FileExistsError, ValueError, OSError)):
                raise BackupCreationError("Não foi possível criar e validar o backup.") from error
            raise BackupCreationError("Não foi possível criar e validar o backup.") from error

        emit_event(
            EventCode.BACKUP_SUCCEEDED,
            operation="backup.create",
            outcome=EventOutcome.SUCCEEDED,
            context={"size_bytes": validated_manifest.size_bytes},
        )
        return BackupValidationResult(validated_manifest)


def validate_sqlite_backup(
    backup_path: Path | str,
    *,
    manifest_path: Path | str | None = None,
    correlation_id: str | None = None,
) -> BackupValidationResult:
    """Valide formato, tamanho, SHA-256 e integridade interna do SQLite."""
    with correlation_scope(correlation_id):
        emit_event(
            EventCode.BACKUP_VALIDATION_STARTED,
            operation="backup.validate",
            outcome=EventOutcome.STARTED,
        )
        try:
            backup = Path(backup_path).expanduser().resolve()
            manifest_file = (
                Path(manifest_path).expanduser().resolve()
                if manifest_path is not None
                else manifest_path_for(backup).resolve()
            )
            manifest = _validate_backup_files(backup, manifest_file)
        except Exception as error:
            _event_failure(
                EventCode.BACKUP_VALIDATION_FAILED,
                operation="backup.validate",
                error_code="BACKUP_VALIDATION_FAILED",
                error=error,
            )
            if isinstance(error, BackupValidationError):
                raise
            raise BackupValidationError("Não foi possível validar o backup.") from error

        emit_event(
            EventCode.BACKUP_VALIDATION_SUCCEEDED,
            operation="backup.validate",
            outcome=EventOutcome.SUCCEEDED,
            context={"size_bytes": manifest.size_bytes},
        )
        return BackupValidationResult(manifest)


def _fetch_one(database: sqlite3.Connection, query: str) -> tuple[Any, ...]:
    row = database.execute(query).fetchone()
    if row is None:
        raise RestoreError("O estado mínimo esperado não foi encontrado.")
    return cast(tuple[Any, ...], row)


def _uuid(value: object, *, invalid_message: str) -> UUID:
    try:
        return UUID(str(value))
    except (TypeError, ValueError, AttributeError) as error:
        raise RestoreError(invalid_message) from error


def _expected_migrations() -> set[tuple[str, str]]:
    loader = MigrationLoader(None, ignore_no_migrations=True)
    return set(loader.disk_migrations)


def _reconcile_minimal_foundation(path: Path) -> ReconciliationResult:
    """Confira a fundação sem executar bootstrap ou recriar registros ausentes."""
    try:
        with closing(_readonly_connection(path)) as database:
            _validate_sqlite_file(path)
            applied_migrations = {
                cast(tuple[str, str], row)
                for row in database.execute("SELECT app, name FROM django_migrations")
            }
            expected_migrations = _expected_migrations()
            if applied_migrations != expected_migrations:
                raise RestoreError("As migrações do backup não correspondem à versão atual.")

            user_count = cast(int, _fetch_one(database, "SELECT COUNT(*) FROM accounts_user")[0])
            user = _fetch_one(database, "SELECT id, status FROM accounts_user")
            workspace_count = cast(
                int, _fetch_one(database, "SELECT COUNT(*) FROM accounts_workspace")[0]
            )
            workspace = _fetch_one(
                database,
                "SELECT id, owner_user_id, locale, timezone_name FROM accounts_workspace",
            )
            category_rows = database.execute(
                "SELECT code, display_name, description, workspace_id FROM errors_error_category"
            ).fetchall()
    except RestoreError:
        raise
    except (sqlite3.Error, ValueError, TypeError) as error:
        raise RestoreError("O banco restaurado não possui a fundação V0.1 válida.") from error

    if (
        user_count != 1
        or _uuid(
            user[0],
            invalid_message="A identidade local restaurada não corresponde ao estado mínimo.",
        )
        != LOCAL_USER_ID
    ):
        raise RestoreError("A identidade local restaurada não corresponde ao estado mínimo.")
    if user[1] != UserStatus.ACTIVE:
        raise RestoreError("A identidade local restaurada não está ativa.")
    if workspace_count != 1:
        raise RestoreError("O backup precisa conter exatamente um Workspace local.")
    if (
        _uuid(workspace[0], invalid_message="O identificador do Workspace é inválido.")
        != LOCAL_WORKSPACE_ID
        or _uuid(workspace[1], invalid_message="O proprietário do Workspace é inválido.")
        != LOCAL_USER_ID
    ):
        raise RestoreError("O Workspace restaurado não pertence à identidade local esperada.")
    if workspace[2] != WorkspaceLocale.PT_BR:
        raise RestoreError("O locale restaurado não corresponde à fundação V0.1.")
    try:
        TimeZoneId(cast(str, workspace[3]))
    except (TypeError, ValueError) as error:
        raise RestoreError("O fuso restaurado não é um identificador IANA válido.") from error

    expected_categories: Mapping[str, tuple[str, str]] = {
        definition.code: (definition.display_name, definition.description)
        for definition in STANDARD_ERROR_CATEGORIES
    }
    restored_categories: dict[str, tuple[str, str]] = {}
    for code, display_name, description, workspace_id in category_rows:
        if (
            _uuid(workspace_id, invalid_message="A categoria possui Workspace inválido.")
            != LOCAL_WORKSPACE_ID
            or code in restored_categories
        ):
            raise RestoreError("As categorias restauradas violam o isolamento do Workspace.")
        restored_categories[cast(str, code)] = (
            cast(str, display_name),
            cast(str, description),
        )
    if restored_categories != expected_categories:
        raise RestoreError("As dez categorias padrão restauradas não correspondem ao catálogo.")

    return ReconciliationResult(
        migration_count=len(applied_migrations),
        user_count=user_count,
        workspace_count=workspace_count,
        category_count=len(category_rows),
    )


def restore_sqlite_backup(
    backup_path: Path | str,
    destination_path: Path | str,
    *,
    manifest_path: Path | str | None = None,
    database_alias: str = "default",
    correlation_id: str | None = None,
) -> RestoreResult:
    """Restaure somente em destino novo e publique após reconciliação da V0.1."""
    temporary_destination: Path | None = None
    published_destination: Path | None = None
    with correlation_scope(correlation_id):
        emit_event(
            EventCode.RESTORE_STARTED,
            operation="backup.restore",
            outcome=EventOutcome.STARTED,
        )
        try:
            active_database = _database_path(database_alias, require_existing=False)
            backup = Path(backup_path).expanduser().resolve()
            manifest_file = (
                Path(manifest_path).expanduser().resolve()
                if manifest_path is not None
                else manifest_path_for(backup).resolve()
            )
            destination = _resolved_output(destination_path)
            if destination in {active_database, backup, manifest_file}:
                raise RestoreError("O destino isolado não pode substituir um arquivo existente.")

            manifest = _validate_backup_files(backup, manifest_file)
            temporary_destination = _temporary_file(destination.parent, ".restore.sqlite3.tmp")
            _sqlite_backup(backup, temporary_destination)
            reconciliation = _reconcile_minimal_foundation(temporary_destination)
            _flush_file(temporary_destination)
            _publish_new_file(temporary_destination, destination)
            temporary_destination = None
            published_destination = destination
            _validate_sqlite_file(destination)
        except Exception as error:
            cleanup_succeeded = all(
                (
                    _remove_created_file(temporary_destination),
                    _remove_created_file(published_destination),
                )
            )
            _event_failure(
                EventCode.RESTORE_FAILED,
                operation="backup.restore",
                error_code="RESTORE_VALIDATION_FAILED",
                error=error,
                temporary_cleanup_succeeded=cleanup_succeeded,
            )
            if isinstance(error, RestoreError):
                raise
            if isinstance(error, BackupValidationError):
                raise RestoreError("O backup foi rejeitado antes da restauração.") from error
            if isinstance(error, (BackupCreationError, FileExistsError, ValueError, OSError)):
                raise RestoreError("Não foi possível concluir a restauração isolada.") from error
            raise RestoreError("Não foi possível concluir a restauração isolada.") from error

        emit_event(
            EventCode.RESTORE_VALIDATED,
            operation="backup.restore",
            outcome=EventOutcome.SUCCEEDED,
            context={
                "category_count": reconciliation.category_count,
                "migration_count": reconciliation.migration_count,
            },
        )
        return RestoreResult(manifest=manifest, reconciliation=reconciliation)
