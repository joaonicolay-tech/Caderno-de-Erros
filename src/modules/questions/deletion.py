"""Exclusão permanente excepcional, por agregado e com auditoria minimizada."""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

from django.db import OperationalError, connection, transaction
from django.db.models import F, Q

from modules.analytics.services import AnalyticsService
from modules.attempts.context import ContextStore, contexts
from modules.attempts.models import Attempt, OperationReceipt
from modules.attempts.persistence import is_sqlite_busy, run_sqlite_critical_write
from modules.data_management.services import (
    create_sqlite_backup,
    restore_sqlite_backup,
    validate_sqlite_backup,
)
from modules.errors.models import ErrorCategory, ErrorClassification, ErrorClassificationRevision
from modules.operations.models import AuditEntityType, AuditEvent, AuditEventCode
from modules.operations.services import record_audit_event
from modules.operations.validators import normalize_reason_code
from modules.reviews.models import Review, ReviewCycle, ReviewScheduleChange
from modules.taxonomy.models import Discipline, Subject, Subsubject
from shared.domain.time import Clock, SystemClock

from .models import (
    Alternative,
    Board,
    Exam,
    Question,
    QuestionOrigin,
    QuestionRevision,
    QuestionStatus,
    Source,
)

FaultHook = Callable[[str], None]


class PermanentDeletionConflictError(RuntimeError):
    """O estado, a confirmação ou a prova de recovery não autoriza o delete."""


@dataclass(frozen=True, slots=True)
class PermanentDeletionPreview:
    question_id: uuid.UUID
    eligible: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    impact: tuple[tuple[str, int], ...]
    fingerprint: str
    backup_required: bool
    confirmation_token: str


@dataclass(frozen=True, slots=True)
class PermanentDeletionResult:
    audit_event_id: uuid.UUID
    correlation_id: uuid.UUID
    impact: tuple[tuple[str, int], ...]
    backup_path: Path | None


_TABLES = (
    ("schedule_changes", "reviews_reviewschedulechange"),
    ("classification_revisions", "errors_errorclassificationrevision"),
    ("classifications", "errors_errorclassification"),
    ("cycles", "reviews_reviewcycle"),
    ("reviews", "reviews_review"),
    ("attempts", "attempts_attempt"),
    ("origins", "questions_questionorigin"),
    ("alternatives", "questions_alternative"),
    ("revisions", "questions_questionrevision"),
    ("questions", "questions_question"),
)


def _hex(value: uuid.UUID) -> str:
    return value.hex


def _ids(rows: list[dict[str, Any]]) -> set[uuid.UUID]:
    return {row["id"] for row in rows}


def _rows(queryset: Any, *fields: str) -> list[dict[str, Any]]:
    # O fingerprint inclui tambem conteudo e timestamps, mesmo quando a
    # elegibilidade precisa somente das colunas explicitadas pelo chamador.
    return list(queryset.order_by("pk").values())


class PermanentQuestionDeletionService:
    """Preview sem escrita; confirmação revalida e remove em um único commit."""

    def __init__(
        self,
        *,
        workspace_id: uuid.UUID,
        clock: Clock | None = None,
        context_store: ContextStore | None = None,
    ) -> None:
        self.workspace_id = workspace_id
        self.clock = clock or SystemClock()
        self.context_store = context_store or contexts

    def preview(self, *, question_id: uuid.UUID) -> PermanentDeletionPreview:
        preview, _ = self._inspect(question_id)
        return preview

    def delete(
        self,
        *,
        question_id: uuid.UUID,
        expected_fingerprint: str,
        confirmation_token: str,
        reason_code: str,
        correlation_id: uuid.UUID,
        backup_path: Path | str | None = None,
        isolated_restore_path: Path | str | None = None,
        fault_hook: FaultHook | None = None,
    ) -> PermanentDeletionResult:
        reason = normalize_reason_code(reason_code, required=True)
        if reason is None:
            raise PermanentDeletionConflictError("Motivo codificado obrigatório.")
        initial, initial_graph = self._inspect(question_id)
        self._require_confirmation(initial, expected_fingerprint, confirmation_token)
        self._require_sanitized_metadata(initial_graph, correlation_id, reason)
        if AuditEvent.objects.filter(
            workspace_id=self.workspace_id,
            event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED,
            correlation_id=correlation_id,
        ).exists():
            raise PermanentDeletionConflictError("Correlação já utilizada para exclusão.")

        protected_backup: Path | None = None
        if initial.backup_required:
            if backup_path is None or isolated_restore_path is None:
                raise PermanentDeletionConflictError("Backup e restore isolado são obrigatórios.")
            protected_backup = Path(backup_path).expanduser().resolve()
            create_sqlite_backup(protected_backup, correlation_id=str(correlation_id))
            validate_sqlite_backup(protected_backup, correlation_id=str(correlation_id))
            restored = restore_sqlite_backup(
                protected_backup,
                isolated_restore_path,
                correlation_id=str(correlation_id),
            )
            if restored.integrity.has_blocking_findings:
                raise PermanentDeletionConflictError(
                    "S5 do restore isolado encontrou inconsistência."
                )

        def write() -> PermanentDeletionResult:
            with transaction.atomic(durable=True):
                preview, graph = self._inspect(question_id)
                self._require_confirmation(preview, expected_fingerprint, confirmation_token)
                self._require_sanitized_metadata(graph, correlation_id, reason)
                locked = (
                    Question.objects.select_for_update()
                    .filter(pk=question_id, workspace_id=self.workspace_id)
                    .only("lock_version")
                    .first()
                )
                if (
                    locked is None
                    or Question.objects.filter(
                        pk=question_id,
                        workspace_id=self.workspace_id,
                        lock_version=locked.lock_version,
                    ).update(lock_version=F("lock_version") + 1)
                    != 1
                ):
                    raise PermanentDeletionConflictError("A Question mudou durante a confirmação.")
                self._fault(fault_hook, "after_lock")
                with connection.cursor() as cursor:
                    self._remove_rows(cursor, "operations_auditevent", graph["audit_events"])
                    self._remove_rows(cursor, "attempts_operationreceipt", graph["receipts"])
                    self._fault(fault_hook, "after_first_dependency")
                    for key, table in _TABLES:
                        self._remove_rows(cursor, table, graph[key])
                        if key == "cycles":
                            self._fault(fault_hook, "middle_delete")
                    self._fault(fault_hook, "before_reconciliation")
                    self._reconcile(graph)
                    cursor.execute("PRAGMA foreign_key_check")
                    if cursor.fetchone() is not None:
                        raise PermanentDeletionConflictError("A exclusão deixaria FK órfã.")
                    self._fault(fault_hook, "after_reconciliation")
                    self._fault(fault_hook, "before_audit")
                    event = record_audit_event(
                        workspace_id=self.workspace_id,
                        event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED,
                        entity_type=AuditEntityType.QUESTION,
                        entity_id=None,
                        correlation_id=correlation_id,
                        reason_code=reason,
                    )
                    self._fault(fault_hook, "after_audit")
                return PermanentDeletionResult(
                    audit_event_id=event.id,
                    correlation_id=correlation_id,
                    impact=preview.impact,
                    backup_path=protected_backup,
                )

        try:
            return run_sqlite_critical_write(write)
        except OperationalError as error:
            if is_sqlite_busy(error):
                raise PermanentDeletionConflictError(
                    "Outra operação concorreu com a exclusão; recarregue o preview."
                ) from error
            raise

    @staticmethod
    def _fault(hook: FaultHook | None, point: str) -> None:
        if hook is not None:
            hook(point)

    @staticmethod
    def _require_confirmation(
        preview: PermanentDeletionPreview, fingerprint: str, token: str
    ) -> None:
        if not preview.eligible or preview.fingerprint != fingerprint:
            raise PermanentDeletionConflictError("Preview obsoleto ou exclusão bloqueada.")
        if token != preview.confirmation_token:
            raise PermanentDeletionConflictError("Confirmação explícita ausente.")

    @staticmethod
    def _require_sanitized_metadata(
        graph: dict[str, list[dict[str, Any]]], correlation_id: uuid.UUID, reason: str
    ) -> None:
        aggregate_ids = {row["id"] for rows in graph.values() for row in rows}
        if correlation_id in aggregate_ids or any(
            item.hex.upper() in reason for item in aggregate_ids
        ):
            raise PermanentDeletionConflictError("Metadados de auditoria contêm ID do agregado.")

    def _inspect(
        self, question_id: uuid.UUID
    ) -> tuple[PermanentDeletionPreview, dict[str, list[dict[str, Any]]]]:
        graph: dict[str, list[dict[str, Any]]] = {}
        graph["questions"] = _rows(
            Question.objects.filter(pk=question_id, workspace_id=self.workspace_id),
            "id",
            "workspace_id",
            "status",
            "lock_version",
            "discipline_id",
            "subject_id",
            "subsubject_id",
        )
        if not graph["questions"]:
            return (
                PermanentDeletionPreview(
                    question_id, False, ("QUESTION_NOT_FOUND",), (), (), "", True, ""
                ),
                graph,
            )
        graph["revisions"] = _rows(
            QuestionRevision.objects.filter(question_id=question_id),
            "id",
            "workspace_id",
            "question_id",
            "version_number",
            "is_current",
            "correct_alternative_id",
        )
        revision_ids = _ids(graph["revisions"])
        graph["alternatives"] = _rows(
            Alternative.objects.filter(question_revision_id__in=revision_ids),
            "id",
            "workspace_id",
            "question_revision_id",
            "position",
        )
        alternative_ids = _ids(graph["alternatives"])
        graph["attempts"] = _rows(
            Attempt.objects.filter(question_id=question_id),
            "id",
            "workspace_id",
            "question_id",
            "question_revision_id",
            "selected_alternative_id",
            "review_id",
            "replaces_attempt_id",
            "status",
            "attempt_type",
            "is_correct",
        )
        attempt_ids = _ids(graph["attempts"])
        graph["classifications"] = _rows(
            ErrorClassification.objects.filter(attempt_id__in=attempt_ids),
            "id",
            "workspace_id",
            "attempt_id",
            "category_id",
            "lock_version",
        )
        classification_ids = _ids(graph["classifications"])
        graph["classification_revisions"] = _rows(
            ErrorClassificationRevision.objects.filter(
                error_classification_id__in=classification_ids
            ),
            "id",
            "workspace_id",
            "error_classification_id",
            "category_id",
        )
        graph["cycles"] = _rows(
            ReviewCycle.objects.filter(question_id=question_id),
            "id",
            "workspace_id",
            "question_id",
            "origin_attempt_id",
            "origin_question_revision_id",
            "state",
            "lock_version",
        )
        cycle_ids = _ids(graph["cycles"])
        graph["reviews"] = _rows(
            Review.objects.filter(question_id=question_id),
            "id",
            "workspace_id",
            "question_id",
            "review_cycle_id",
            "scheduled_from_attempt_id",
            "state",
            "lock_version",
            "current_due_date",
        )
        review_ids = _ids(graph["reviews"])
        graph["schedule_changes"] = _rows(
            ReviewScheduleChange.objects.filter(review_id__in=review_ids),
            "id",
            "workspace_id",
            "review_id",
        )
        graph["origins"] = _rows(
            QuestionOrigin.objects.filter(question_id=question_id),
            "id",
            "workspace_id",
            "question_id",
            "source_id",
            "exam_id",
            "board_id",
        )
        aggregate_ids = (
            {question_id}
            | revision_ids
            | alternative_ids
            | attempt_ids
            | classification_ids
            | _ids(graph["classification_revisions"])
            | cycle_ids
            | review_ids
            | _ids(graph["schedule_changes"])
            | _ids(graph["origins"])
        )
        graph["audit_events"] = _rows(
            AuditEvent.objects.filter(
                Q(entity_id__in=aggregate_ids)
                | Q(previous_entity_id__in=aggregate_ids)
                | Q(related_entity_id__in=aggregate_ids)
            ),
            "id",
            "workspace_id",
            "event_code",
            "entity_id",
            "previous_entity_id",
            "related_entity_id",
        )
        graph["receipts"] = _rows(
            OperationReceipt.objects.filter(result_entity_id__in=attempt_ids),
            "id",
            "workspace_id",
            "result_entity_id",
            "created_at",
        )

        blockers: list[str] = []
        if any(row["workspace_id"] != self.workspace_id for rows in graph.values() for row in rows):
            blockers.append("CROSS_WORKSPACE_REFERENCE")
        if any(
            row["correct_alternative_id"] is not None
            and row["correct_alternative_id"] not in alternative_ids
            for row in graph["revisions"]
        ):
            blockers.append("REVISION_EXTERNAL_REFERENCE")
        shared_references: list[tuple[Any, uuid.UUID | None]] = [
            (Discipline, graph["questions"][0]["discipline_id"]),
            (Subject, graph["questions"][0]["subject_id"]),
            (Subsubject, graph["questions"][0]["subsubject_id"]),
            *((ErrorCategory, row["category_id"]) for row in graph["classifications"]),
            *((ErrorCategory, row["category_id"]) for row in graph["classification_revisions"]),
            *((Source, row["source_id"]) for row in graph["origins"]),
            *((Exam, row["exam_id"]) for row in graph["origins"]),
            *((Board, row["board_id"]) for row in graph["origins"]),
        ]
        if any(
            item_id is not None
            and not model.objects.filter(pk=item_id, workspace_id=self.workspace_id).exists()
            for model, item_id in shared_references
        ):
            blockers.append("SHARED_CROSS_WORKSPACE_REFERENCE")
        if any(
            row["question_revision_id"] not in revision_ids
            or row["selected_alternative_id"] not in alternative_ids
            or (row["review_id"] is not None and row["review_id"] not in review_ids)
            or (
                row["replaces_attempt_id"] is not None
                and row["replaces_attempt_id"] not in attempt_ids
            )
            for row in graph["attempts"]
        ):
            blockers.append("ATTEMPT_EXTERNAL_REFERENCE")
        if any(
            row["origin_question_revision_id"] not in revision_ids
            or (
                row["origin_attempt_id"] is not None and row["origin_attempt_id"] not in attempt_ids
            )
            for row in graph["cycles"]
        ):
            blockers.append("CYCLE_EXTERNAL_REFERENCE")
        if any(
            row["review_cycle_id"] not in cycle_ids
            or (
                row["scheduled_from_attempt_id"] is not None
                and row["scheduled_from_attempt_id"] not in attempt_ids
            )
            for row in graph["reviews"]
        ):
            blockers.append("REVIEW_EXTERNAL_REFERENCE")
        if (
            Attempt.objects.filter(
                Q(question_revision_id__in=revision_ids)
                | Q(selected_alternative_id__in=alternative_ids)
                | Q(replaces_attempt_id__in=attempt_ids)
                | Q(review_id__in=review_ids)
            )
            .exclude(question_id=question_id)
            .exists()
            or ReviewCycle.objects.filter(
                Q(origin_attempt_id__in=attempt_ids)
                | Q(origin_question_revision_id__in=revision_ids)
            )
            .exclude(question_id=question_id)
            .exists()
            or Review.objects.filter(
                Q(review_cycle_id__in=cycle_ids) | Q(scheduled_from_attempt_id__in=attempt_ids)
            )
            .exclude(question_id=question_id)
            .exists()
        ):
            blockers.append("EXTERNAL_DEPENDENCY")
        now = self.clock.now().value
        if any(now < row["created_at"] + timedelta(days=30) for row in graph["receipts"]):
            blockers.append("RECEIPT_RETENTION")
        if self.context_store.has_live_question_context(
            workspace_id=self.workspace_id, question_id=question_id, now=now
        ):
            blockers.append("TRANSIENT_CONTEXT")

        simple = graph["questions"][0]["status"] == QuestionStatus.DRAFT and not any(
            graph[key]
            for key in (
                "attempts",
                "classifications",
                "classification_revisions",
                "cycles",
                "reviews",
                "schedule_changes",
                "origins",
                "audit_events",
                "receipts",
            )
        )
        analytics = AnalyticsService(workspace_id=self.workspace_id)
        impact = (
            *((key, len(rows)) for key, rows in graph.items()),
            (
                "registered_questions",
                analytics.registered_questions().filter(pk=question_id).count(),
            ),
            ("performed_questions", analytics.performed_questions().filter(pk=question_id).count()),
            ("valid_attempts", analytics.attempts().filter(question_id=question_id).count()),
            (
                "correct_answers",
                analytics.attempts(is_correct=True).filter(question_id=question_id).count(),
            ),
            (
                "incorrect_answers",
                analytics.attempts(is_correct=False).filter(question_id=question_id).count(),
            ),
        )
        technical_graph = {
            key: sorted(
                ({field: str(value) for field, value in row.items()} for row in rows),
                key=lambda row: row["id"],
            )
            for key, rows in graph.items()
        }
        fingerprint = hashlib.sha256(
            json.dumps(technical_graph, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return (
            PermanentDeletionPreview(
                question_id=question_id,
                eligible=not blockers,
                blockers=tuple(blockers),
                warnings=("ARCHIVE_IS_DEFAULT",) if not simple else (),
                impact=impact,
                fingerprint=fingerprint,
                backup_required=not simple,
                confirmation_token=(
                    "PERMANENT_DELETE_WITH_HISTORY" if not simple else "CONFIRM_DELETE_DRAFT"
                ),
            ),
            graph,
        )

    def _remove_rows(self, cursor: Any, table: str, rows: list[dict[str, Any]]) -> None:
        ids = sorted(_ids(rows))
        for offset in range(0, len(ids), 400):
            batch = ids[offset : offset + 400]
            placeholders = ",".join(["%s"] * len(batch))
            cursor.execute(
                f"DELETE FROM {table} WHERE workspace_id = %s AND id IN ({placeholders})",  # noqa: S608
                [_hex(self.workspace_id), *(_hex(item) for item in batch)],
            )
            if cursor.rowcount != len(batch):
                raise PermanentDeletionConflictError("O agregado mudou durante a exclusão.")

    def _reconcile(self, graph: dict[str, list[dict[str, Any]]]) -> None:
        for key, model in (
            ("questions", Question),
            ("revisions", QuestionRevision),
            ("alternatives", Alternative),
            ("attempts", Attempt),
            ("classifications", ErrorClassification),
            ("classification_revisions", ErrorClassificationRevision),
            ("cycles", ReviewCycle),
            ("reviews", Review),
            ("schedule_changes", ReviewScheduleChange),
            ("origins", QuestionOrigin),
            ("audit_events", AuditEvent),
            ("receipts", OperationReceipt),
        ):
            if model.objects.filter(pk__in=_ids(graph[key])).exists():
                raise PermanentDeletionConflictError(
                    "A reconciliação encontrou resíduo do agregado."
                )
