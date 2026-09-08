"""Schema fundacional de tentativas e recibos idempotentes da V0.3."""

import re
import uuid
from datetime import datetime, timedelta
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from modules.accounts.models import Workspace
from modules.accounts.validators import validate_iana_timezone
from modules.questions.models import Alternative, Question, QuestionRevision
from shared.domain.time import Clock, TimeZoneId

from .exceptions import IdempotencyConflictError

_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


class AttemptType(models.TextChoices):
    """Origens fechadas de uma tentativa finalizada na V0.3."""

    INITIAL = "INITIAL", "Inicial"
    REVIEW = "REVIEW", "Revisão"


class AttemptStatus(models.TextChoices):
    """Estados históricos previstos; anulação funcional permanece posterior."""

    VALID = "VALID", "Válida"
    VOIDED = "VOIDED", "Anulada"


class PerceivedEase(models.TextChoices):
    """Percepção opcional registrada sem influenciar a política fixa."""

    EASY = "EASY", "Fácil"
    MEDIUM = "MEDIUM", "Média"
    HARD = "HARD", "Difícil"


class AttemptQuerySet(models.QuerySet["Attempt"]):
    """Impeça mutação ou exclusão silenciosa de fatos finalizados."""

    def update(self, **kwargs: Any) -> int:
        raise ValidationError("Attempt é imutável; correção estrutural não pertence à V0.3.")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("Attempt não pode ser excluída isoladamente.")


class Attempt(models.Model):
    """Fato imutável de resposta inicial ou de revisão."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="attempts",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name="attempts",
    )
    question_revision = models.ForeignKey(
        QuestionRevision,
        on_delete=models.PROTECT,
        related_name="attempts",
    )
    review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.PROTECT,
        related_name="attempts",
        null=True,
        blank=True,
    )
    attempt_type = models.CharField(max_length=16, choices=AttemptType.choices)
    selected_alternative = models.ForeignKey(
        Alternative,
        on_delete=models.PROTECT,
        related_name="selected_in_attempts",
    )
    is_correct = models.BooleanField()
    perceived_ease = models.CharField(  # noqa: DJ001
        max_length=16,
        choices=PerceivedEase.choices,
        null=True,
        blank=True,
    )
    occurred_at = models.DateTimeField()
    timezone_name = models.CharField(max_length=64, validators=[validate_iana_timezone])
    local_date = models.DateField()
    status = models.CharField(
        max_length=16,
        choices=AttemptStatus.choices,
        default=AttemptStatus.VALID,
    )
    replaces_attempt = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,
        related_name="replacement_attempt",
        null=True,
        blank=True,
    )
    voided_at = models.DateTimeField(null=True, blank=True)
    void_reason = models.CharField(max_length=1000, null=True, blank=True)  # noqa: DJ001
    idempotency_key = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AttemptQuerySet.as_manager()

    class Meta:
        db_table = "attempts_attempt"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "question", "occurred_at"],
                name="attempt_ws_q_time_idx",
            ),
            models.Index(
                fields=["workspace", "status", "is_correct", "local_date"],
                name="attempt_ws_st_res_date_idx",
            ),
            models.Index(
                fields=["workspace", "attempt_type", "local_date"],
                name="attempt_ws_type_date_idx",
            ),
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["question"],
                condition=Q(attempt_type=AttemptType.INITIAL, status=AttemptStatus.VALID),
                name="attempt_initial_valid_uq",
            ),
            models.UniqueConstraint(
                fields=["review"],
                condition=Q(status=AttemptStatus.VALID, review__isnull=False),
                name="attempt_review_valid_uq",
            ),
            models.UniqueConstraint(
                fields=["workspace", "idempotency_key"],
                name="attempt_ws_idempotency_uq",
            ),
            models.CheckConstraint(
                condition=Q(attempt_type__in=AttemptType.values),
                name="attempt_type_valid",
            ),
            models.CheckConstraint(
                condition=Q(status__in=AttemptStatus.values),
                name="attempt_status_valid",
            ),
            models.CheckConstraint(
                condition=Q(perceived_ease__isnull=True)
                | Q(perceived_ease__in=PerceivedEase.values),
                name="attempt_ease_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(attempt_type=AttemptType.INITIAL, review__isnull=True)
                    | Q(attempt_type=AttemptType.REVIEW, review__isnull=False)
                ),
                name="attempt_type_review_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=AttemptStatus.VALID, voided_at__isnull=True, void_reason__isnull=True)
                    | Q(
                        status=AttemptStatus.VOIDED,
                        voided_at__isnull=False,
                        void_reason__isnull=False,
                    )
                ),
                name="attempt_void_state_valid",
            ),
            models.CheckConstraint(
                condition=Q(void_reason__isnull=True) | ~Q(void_reason=""),
                name="attempt_void_reason_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.attempt_type} {self.question_id} @ {self.occurred_at.isoformat()}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("Attempt é imutável; correção estrutural não pertence à V0.3.")
        self._validate_references()
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("Attempt não pode ser excluída isoladamente.")

    def _validate_references(self) -> None:
        validate_iana_timezone(self.timezone_name)
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValidationError({"occurred_at": "O instante da tentativa deve possuir fuso."})
        expected_local_date = self.occurred_at.astimezone(
            TimeZoneId(self.timezone_name).zone
        ).date()
        if self.local_date != expected_local_date:
            raise ValidationError(
                {"local_date": "A data civil deve corresponder ao instante e fuso da tentativa."}
            )
        question = Question.objects.filter(pk=self.question_id).only("workspace_id").first()
        revision = (
            QuestionRevision.objects.filter(pk=self.question_revision_id)
            .only("workspace_id", "question_id", "correct_alternative_id")
            .first()
        )
        alternative = (
            Alternative.objects.filter(pk=self.selected_alternative_id)
            .only("workspace_id", "question_revision_id")
            .first()
        )
        if question is not None and question.workspace_id != self.workspace_id:
            raise ValidationError("A tentativa deve pertencer ao Workspace da questão.")
        if revision is not None and (
            revision.workspace_id != self.workspace_id or revision.question_id != self.question_id
        ):
            raise ValidationError(
                "A QuestionRevision apresentada deve pertencer à questão e ao Workspace."
            )
        if alternative is not None and (
            alternative.workspace_id != self.workspace_id
            or alternative.question_revision_id != self.question_revision_id
        ):
            raise ValidationError(
                "A alternativa selecionada deve pertencer à QuestionRevision apresentada."
            )
        if revision is not None and alternative is not None:
            expected_result = revision.correct_alternative_id == alternative.id
            if self.is_correct != expected_result:
                raise ValidationError("O resultado deve corresponder ao gabarito da revisão.")
        if self.review_id:
            from modules.reviews.models import Review

            review = (
                Review.objects.filter(pk=self.review_id).only("workspace_id", "question_id").first()
            )
            if review is not None and (
                review.workspace_id != self.workspace_id or review.question_id != self.question_id
            ):
                raise ValidationError(
                    "A Review deve pertencer à questão e ao Workspace da tentativa."
                )
        if self.replaces_attempt_id:
            replaced = (
                type(self)
                .objects.filter(pk=self.replaces_attempt_id)
                .only("workspace_id", "question_id", "status")
                .first()
            )
            if replaced is not None and (
                replaced.workspace_id != self.workspace_id
                or replaced.question_id != self.question_id
                or replaced.status != AttemptStatus.VOIDED
            ):
                raise ValidationError(
                    "A tentativa substituída deve ser anulada e do mesmo contexto."
                )


class OperationKind(models.TextChoices):
    """Operações críticas previstas para os recibos V0.3."""

    INITIAL_CORRECT = "INITIAL_CORRECT", "Inicial correta"
    INITIAL_ERROR = "INITIAL_ERROR", "Erro inicial"
    REVIEW_COMPLETION = "REVIEW_COMPLETION", "Conclusão de revisão"


class ResultEntityType(models.TextChoices):
    """Tipos mínimos de resultado sem conteúdo de estudo."""

    ATTEMPT = "ATTEMPT", "Tentativa"


class OperationReceiptQuerySet(models.QuerySet["OperationReceipt"]):
    """Consulta idempotente sempre isolada pelo Workspace."""

    def resolve_existing(
        self,
        *,
        workspace_id: uuid.UUID,
        operation_kind: str,
        idempotency_key: uuid.UUID,
        request_hash: str,
    ) -> "OperationReceipt":
        receipt = self.get(
            workspace_id=workspace_id,
            operation_kind=operation_kind,
            idempotency_key=idempotency_key,
        )
        if receipt.request_hash != request_hash:
            raise IdempotencyConflictError(
                "A chave idempotente já foi usada com uma solicitação diferente."
            )
        return receipt

    def update(self, **kwargs: Any) -> int:
        raise ValidationError("OperationReceipt é imutável.")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("Use a remoção explícita com retenção validada.")


class OperationReceipt(models.Model):
    """Prova técnica minimizada de uma operação crítica concluída."""

    MINIMUM_RETENTION_DAYS = 30

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="operation_receipts",
    )
    operation_kind = models.CharField(max_length=32, choices=OperationKind.choices)
    idempotency_key = models.UUIDField()
    request_hash = models.CharField(max_length=64)
    result_entity_type = models.CharField(max_length=32, choices=ResultEntityType.choices)
    result_entity_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = OperationReceiptQuerySet.as_manager()

    class Meta:
        db_table = "attempts_operationreceipt"
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["workspace", "operation_kind", "idempotency_key"],
                name="receipt_ws_kind_key_uq",
            ),
            models.CheckConstraint(
                condition=Q(operation_kind__in=OperationKind.values),
                name="receipt_kind_valid",
            ),
            models.CheckConstraint(
                condition=Q(result_entity_type__in=ResultEntityType.values),
                name="receipt_result_type_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.operation_kind}:{self.idempotency_key}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("OperationReceipt é imutável.")
        if not _SHA256_PATTERN.fullmatch(self.request_hash):
            raise ValidationError({"request_hash": "O hash deve ser um SHA-256 hexadecimal."})
        if self.result_entity_type == ResultEntityType.ATTEMPT:
            result = Attempt.objects.filter(pk=self.result_entity_id).only("workspace_id").first()
            if result is None:
                raise ValidationError("O resultado do recibo deve existir antes da confirmação.")
            if result.workspace_id != self.workspace_id:
                raise ValidationError("O resultado do recibo deve pertencer ao mesmo Workspace.")
        super().save(*args, **kwargs)

    @property
    def minimum_retention_until(self) -> datetime:
        """Calcule o limite mínimo sem persistir payload ou estado derivado."""
        return self.created_at + timedelta(days=self.MINIMUM_RETENTION_DAYS)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("Use a remoção explícita com retenção validada.")

    def delete_if_retention_elapsed(
        self,
        *,
        clock: Clock,
    ) -> tuple[int, dict[str, int]]:
        """Permita expurgo somente após o mínimo congelado de 30 dias."""
        if clock.now().value < self.minimum_retention_until:
            raise ValidationError("OperationReceipt ainda está no período mínimo de retenção.")
        return super().delete()
