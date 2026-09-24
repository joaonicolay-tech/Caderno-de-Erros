"""Immutable recognition history; Attempts and Reviews remain the evidence."""

import uuid
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from modules.accounts.models import Workspace
from modules.attempts.models import Attempt, AttemptStatus
from modules.operations.validators import normalize_reason_code
from modules.questions.models import Question
from modules.reviews.models import ManualCyclePurpose, ReviewCycle, ReviewCycleOriginKind


class MasteryEventType(models.TextChoices):
    DOMINATED = "DOMINATED", "Dominada"
    AUTO_REOPENED = "AUTO_REOPENED", "Reaberta automaticamente"
    MANUAL_REOPENED = "MANUAL_REOPENED", "Reaberta manualmente"


class MasteryStateEventQuerySet(models.QuerySet["MasteryStateEvent"]):
    def update(self, **kwargs: Any) -> int:
        raise ValidationError("MasteryStateEvent é append-only.")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("MasteryStateEvent é append-only.")


class MasteryStateEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="mastery_events")
    sequence = models.PositiveIntegerField()
    event_type = models.CharField(max_length=24, choices=MasteryEventType.choices)
    formula_code = models.CharField(max_length=64)
    evaluated_on = models.DateField()
    domain_index = models.DecimalField(max_digits=36, decimal_places=28, null=True, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    trigger_attempt = models.ForeignKey(Attempt, on_delete=models.PROTECT, null=True, blank=True)
    manual_cycle = models.ForeignKey(ReviewCycle, on_delete=models.PROTECT, null=True, blank=True)
    reason_code = models.CharField(max_length=64, null=True, blank=True)  # noqa: DJ001
    occurred_at = models.DateTimeField()

    objects = MasteryStateEventQuerySet.as_manager()

    class Meta:
        db_table = "domain_masterystateevent"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["workspace", "question", "-sequence"], name="mastery_ws_q_seq_idx")
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                condition=Q(event_type__in=MasteryEventType.values), name="mastery_event_type_valid"
            ),
            models.UniqueConstraint(fields=["question", "sequence"], name="mastery_q_sequence_uq"),
            models.CheckConstraint(condition=Q(sequence__gte=1), name="mastery_sequence_positive"),
            models.CheckConstraint(condition=~Q(formula_code=""), name="mastery_formula_not_empty"),
            models.CheckConstraint(
                condition=Q(reason_code__isnull=True) | ~Q(reason_code=""),
                name="mastery_reason_not_empty",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        event_type=MasteryEventType.MANUAL_REOPENED,
                        reason_code__isnull=False,
                        manual_cycle__isnull=False,
                    )
                    | (
                        ~Q(event_type=MasteryEventType.MANUAL_REOPENED)
                        & Q(manual_cycle__isnull=True)
                    )
                ),
                name="mastery_manual_metadata_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.event_type}:{self.question_id}:{self.sequence}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("MasteryStateEvent é append-only.")
        self.reason_code = normalize_reason_code(
            self.reason_code, required=self.event_type == MasteryEventType.MANUAL_REOPENED
        )
        question = Question.objects.filter(
            pk=self.question_id, workspace_id=self.workspace_id
        ).first()
        if question is None:
            raise ValidationError("Question não pertence ao Workspace do evento.")
        if (
            self.trigger_attempt_id is not None
            and not Attempt.objects.filter(
                pk=self.trigger_attempt_id,
                workspace_id=self.workspace_id,
                question_id=self.question_id,
                status=AttemptStatus.VALID,
            ).exists()
        ):
            raise ValidationError("Attempt gatilho deve ser válida e da mesma Question.")
        if (
            self.manual_cycle_id is not None
            and not ReviewCycle.objects.filter(
                pk=self.manual_cycle_id,
                workspace_id=self.workspace_id,
                question_id=self.question_id,
                origin_kind=ReviewCycleOriginKind.MANUAL,
                manual_purpose=ManualCyclePurpose.MASTERY_REOPEN,
            ).exists()
        ):
            raise ValidationError("Ciclo de reabertura não pertence à Question.")
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("MasteryStateEvent é append-only.")
