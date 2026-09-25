"""UI orchestration for physical backups; active adoption is a separate offline command."""

import hashlib
import json
import os
import shutil
import tempfile
import uuid
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import BinaryIO

from django.db import connections

from .exceptions import BackupCreationError, BackupValidationError, RestoreError
from .services import (
    ReconciliationResult,
    _check_restored_integrity,
    _database_path,
    _sha256,
    _validate_sqlite_file,
    create_sqlite_backup,
    manifest_path_for,
    restore_sqlite_backup,
    validate_sqlite_backup,
)

BACKUP_MEMBER = "backup.sqlite3"
MANIFEST_MEMBER = "backup.sqlite3.manifest.json"


class UIRecoveryError(ValueError):
    """Safe user-facing failure before or during controlled restore."""


@dataclass(frozen=True)
class RestorePreview:
    upload_sha256: str
    manifest_sha256: str
    active_fingerprint: str
    candidate: ReconciliationResult


def _private_root() -> Path:
    active = _database_path("default")
    root = active.parent / "cei-recovery"
    root.mkdir(mode=0o700, exist_ok=True)
    if root.is_symlink() or root.is_junction():
        raise UIRecoveryError("Diretório de recuperação inseguro.")
    return root


def _stream_copy(source: BinaryIO, target: Path) -> None:
    with target.open("xb") as output:
        shutil.copyfileobj(source, output, length=1024 * 1024)
        output.flush()
        os.fsync(output.fileno())


def _fingerprint_active() -> str:
    active = _database_path("default")
    digest = hashlib.sha256()
    for suffix in ("", "-wal", "-shm", "-journal"):
        part = Path(f"{active}{suffix}")
        digest.update(suffix.encode())
        if part.exists():
            digest.update(str(part.stat().st_size).encode())
            digest.update(_sha256(part).encode())
        else:
            digest.update(b"absent")
    return digest.hexdigest()


def _stage_upload(
    backup_file: BinaryIO, manifest_file: BinaryIO, folder: Path
) -> tuple[Path, Path]:
    backup = folder / BACKUP_MEMBER
    manifest = folder / MANIFEST_MEMBER
    _stream_copy(backup_file, backup)
    _stream_copy(manifest_file, manifest)
    return backup, manifest


def create_backup_download(destination: BinaryIO) -> dict[str, object]:
    """Return existing SQLite/sidecar format in a two-member transport ZIP."""
    try:
        with tempfile.TemporaryDirectory(prefix="cei-backup-") as directory:
            backup = Path(directory) / BACKUP_MEMBER
            result = create_sqlite_backup(backup)
            # The transfer ZIP does not redefine the backup's SQLite+sidecar contract.
            with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED) as archive:
                archive.write(backup, BACKUP_MEMBER)
                archive.write(manifest_path_for(backup), MANIFEST_MEMBER)
            return asdict(result.manifest)
    except (OSError, BackupCreationError) as error:
        raise UIRecoveryError("Não foi possível criar o backup validado.") from error


def preview_restore(backup_file: BinaryIO, manifest_file: BinaryIO) -> RestorePreview:
    """Stage and validate uploaded pair, then report its isolated reconciliation."""
    try:
        with tempfile.TemporaryDirectory(prefix="cei-preview-") as directory:
            folder = Path(directory)
            backup, manifest = _stage_upload(backup_file, manifest_file, folder)
            validate_sqlite_backup(backup, manifest_path=manifest)
            result = restore_sqlite_backup(
                backup, folder / "candidate.sqlite3", manifest_path=manifest
            )
            return RestorePreview(
                upload_sha256=_sha256(backup),
                manifest_sha256=_sha256(manifest),
                active_fingerprint=_fingerprint_active(),
                candidate=result.reconciliation,
            )
    except (OSError, BackupValidationError, RestoreError, BackupCreationError) as error:
        raise UIRecoveryError(
            "Backup inválido ou incompatível; o destino não foi alterado."
        ) from error


def prepare_restore(
    backup_file: BinaryIO, manifest_file: BinaryIO, *, expected: RestorePreview
) -> str:
    """Revalidate input/active state and prepare durable candidate plus pre-backup."""
    root = _private_root()
    ticket = uuid.uuid4().hex
    pending = root / ticket
    prebackup = root / f"pre-{ticket}.sqlite3"
    try:
        with tempfile.TemporaryDirectory(prefix="cei-confirm-") as directory:
            folder = Path(directory)
            backup, manifest = _stage_upload(backup_file, manifest_file, folder)
            validate_sqlite_backup(backup, manifest_path=manifest)
            if (
                _sha256(backup) != expected.upload_sha256
                or _sha256(manifest) != expected.manifest_sha256
            ):
                raise UIRecoveryError("Arquivo diferente do preview; valide novamente.")
            if _fingerprint_active() != expected.active_fingerprint:
                raise UIRecoveryError("O estado atual mudou; valide novamente.")
            pending.mkdir(mode=0o700)
            candidate = pending / "candidate.sqlite3"
            result = restore_sqlite_backup(backup, candidate, manifest_path=manifest)
            shutil.copyfile(manifest, manifest_path_for(candidate))
            create_sqlite_backup(prebackup)
            validate_sqlite_backup(prebackup)
            restore_sqlite_backup(prebackup, folder / "pre-verified.sqlite3")
            current_fingerprint = _fingerprint_active()
            if current_fingerprint != expected.active_fingerprint:
                raise UIRecoveryError(
                    "O estado atual mudou durante o pré-backup; valide novamente."
                )
            document = {
                "ticket": ticket,
                "active_path": str(_database_path("default")),
                "active_fingerprint": current_fingerprint,
                "candidate_sha256": _sha256(candidate),
                "prebackup_sha256": _sha256(prebackup),
                "candidate_counts": asdict(result.reconciliation),
            }
            (pending / "ticket.json").write_text(json.dumps(document), encoding="utf-8")
            return ticket
    except (OSError, BackupValidationError, RestoreError, BackupCreationError) as error:
        raise UIRecoveryError(
            "Não foi possível preparar o restore; o destino não foi alterado."
        ) from error
    finally:
        if not (pending / "ticket.json").exists():
            shutil.rmtree(pending, ignore_errors=True)
            prebackup.unlink(missing_ok=True)
            manifest_path_for(prebackup).unlink(missing_ok=True)


def cancel_prepared_restore(ticket: str) -> None:
    """Discard an unapplied ticket and its pre-backup on explicit cancellation."""
    try:
        ticket_id = uuid.UUID(ticket).hex
    except ValueError as error:
        raise UIRecoveryError("Identificador de restore inválido.") from error
    root = _private_root()
    pending = root / ticket_id
    if pending.is_symlink() or not (pending / "ticket.json").is_file():
        raise UIRecoveryError("Ticket de restore inexistente ou inseguro.")
    if (pending / "result.json").exists():
        raise UIRecoveryError("Restore já aplicado; pré-backup preservado.")
    prebackup = root / f"pre-{ticket_id}.sqlite3"
    try:
        shutil.rmtree(pending)
        prebackup.unlink(missing_ok=True)
        manifest_path_for(prebackup).unlink(missing_ok=True)
    except OSError as error:
        raise UIRecoveryError("Não foi possível limpar o restore pendente.") from error


def apply_prepared_restore(ticket: str) -> dict[str, object]:
    """Offline-only active adoption, with a validated pre-backup available for return."""
    try:
        ticket_id = uuid.UUID(ticket).hex
    except ValueError as error:
        raise UIRecoveryError("Identificador de restore inválido.") from error
    root = _private_root()
    pending = root / ticket_id
    if pending.is_symlink():
        raise UIRecoveryError("Ticket de restore inseguro.")
    if (pending / "result.json").exists():
        raise UIRecoveryError("Este restore já foi aplicado.")
    document = json.loads((pending / "ticket.json").read_text(encoding="utf-8"))
    if document["ticket"] != ticket_id:
        raise UIRecoveryError("Ticket de restore inconsistente.")
    active = _database_path("default")
    if (
        str(active) != document["active_path"]
        or _fingerprint_active() != document["active_fingerprint"]
    ):
        raise UIRecoveryError("Banco ativo mudou após a confirmação; restore recusado.")
    if any(Path(f"{active}{suffix}").exists() for suffix in ("-wal", "-shm", "-journal")):
        raise UIRecoveryError(
            "Encerre a aplicação e remova sidecars somente por procedimento seguro."
        )
    candidate = pending / "candidate.sqlite3"
    prebackup = root / f"pre-{ticket_id}.sqlite3"
    if (
        _sha256(candidate) != document["candidate_sha256"]
        or _sha256(prebackup) != document["prebackup_sha256"]
    ):
        raise UIRecoveryError("Artefato de recuperação alterado; restore recusado.")
    validate_sqlite_backup(candidate)
    validate_sqlite_backup(prebackup)
    # Recheck application compatibility and S5 in a fresh isolated copy.
    with tempfile.TemporaryDirectory(prefix="cei-adopt-") as directory:
        folder = Path(directory)
        restore_sqlite_backup(candidate, folder / "candidate-verified.sqlite3")
        restore_sqlite_backup(prebackup, folder / "return-verified.sqlite3")
        if _fingerprint_active() != document["active_fingerprint"]:
            raise UIRecoveryError("Banco ativo mudou durante a validação final.")
        descriptor, temp_name = tempfile.mkstemp(
            prefix=".cei-adopt-", suffix=".sqlite3", dir=active.parent
        )
        os.close(descriptor)
        temporary = Path(temp_name)
        try:
            shutil.copyfile(candidate, temporary)
            if _sha256(temporary) != document["candidate_sha256"]:
                raise UIRecoveryError("Cópia candidata divergente.")
            with temporary.open("r+b") as stream:
                os.fsync(stream.fileno())
            connections.close_all()
            os.replace(temporary, active)
            try:
                _validate_sqlite_file(active)
                _check_restored_integrity(active)
                report: dict[str, object] = {
                    "status": "RESTORED",
                    "ticket": ticket_id,
                    "counts": document["candidate_counts"],
                    "candidate_sha256": document["candidate_sha256"],
                    "active_sha256": _sha256(active),
                    "prebackup_sha256": document["prebackup_sha256"],
                }
                (pending / "result.json").write_text(json.dumps(report), encoding="utf-8")
            except Exception as error:
                return_copy = folder / "return.sqlite3"
                try:
                    shutil.copyfile(prebackup, return_copy)
                    if _sha256(return_copy) != document["prebackup_sha256"]:
                        raise UIRecoveryError("Pré-backup mudou durante o retorno.")
                    os.replace(return_copy, active)
                except (OSError, UIRecoveryError) as return_error:
                    raise UIRecoveryError(
                        "Retorno automático falhou; preserve o pré-backup para recuperação."
                    ) from return_error
                raise UIRecoveryError(
                    "Verificação final falhou; estado anterior restaurado."
                ) from error
            # Cleanup is best effort after a durable success report.
            try:
                candidate.unlink(missing_ok=True)
                manifest_path_for(candidate).unlink(missing_ok=True)
            except OSError:
                pass
            return report
        finally:
            temporary.unlink(missing_ok=True)
