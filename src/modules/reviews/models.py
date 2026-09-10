"""Schema fundacional de ciclos e revisões da V0.3."""

import uuid
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from modules.accounts.models import Workspace
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.questions.models import Question, QuestionRevision


class ReviewCycleOriginKind(models.TextChoices):
    """Origem automática disponível no recorte V0.3."""

    INITIAL_ERROR = "INITIAL_ERROR", "Erro inicial"
    QUESTION_ACTIVATION = "QUESTION_ACTIVATION", "Ativacao da questao"


class ReviewCycleState(models.TextChoices):
    """Estados estruturais persistidos do ciclo."""

    ACTIVE = "ACTIVE", "Ativo"
    COMPLETED = "COMPLETED", "Concluído"
    SUSPENDED = "SUSPENDED", "Suspenso"


class ReviewState(models.TextChoices):
    """Estados estruturais persistidos da revisão."""

    PENDING = "PENDING", "Pendente"
    COMPLETED = "COMPLETED", "Concluída"
    SUSPENDED = "SUSPENDED", "Suspensa"
    CANCELLED = "CANCELLED", "Cancelada"


class ReviewStageCode(models.TextChoices):
    """Etapas fixas da política REV-FIXA-1.0."""

    D1 = "D1", "D1"
    D7 = "D7", "D7"
    D14 = "D14", "D14"
    D30 = "D30", "D30"


class ReviewCycle(models.Model):
    """Ciclo automático iniciado por uma tentativa inicial incorreta."""

    POLICY_CODE = "REV-FIXA-1.0"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="review_cycles",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name="review_cycles",
    )
    origin_attempt = models.OneToOneField(
        Attempt,
        on_delete=models.PROTECT,
        related_name="originated_review_cycle",
        null=True,
        blank=True,
    )
    origin_question_revision = models.ForeignKey(
        QuestionRevision,
        on_delete=models.PROTECT,
        related_name="originated_review_cycles",
    )
    origin_kind = models.CharField(
        max_length=24,
        choices=ReviewCycleOriginKind.choices,
        default=ReviewCycleOriginKind.INITIAL_ERROR,
    )
    policy_code = models.CharField(max_length=64, default=POLICY_CODE)
    state = models.CharField(
        max_length=16,
        choices=ReviewCycleState.choices,
        default=ReviewCycleState.ACTIVE,
    )
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspension_reason = models.CharField(max_length=1000, null=True, blank=True)  # noqa: DJ001
    lock_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews_reviewcycle"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "question", "state"],
                name="cycle_ws_q_state_idx",
            )
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["question"],
                condition=Q(state=ReviewCycleState.ACTIVE),
                name="cycle_active_question_uq",
            ),
            models.CheckConstraint(
                condition=Q(origin_kind__in=ReviewCycleOriginKind.values),
                name="cycle_origin_kind_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        origin_kind=ReviewCycleOriginKind.INITIAL_ERROR,
                        origin_attempt__isnull=False,
                    )
                    | Q(
                        origin_kind=ReviewCycleOriginKind.QUESTION_ACTIVATION,
                        origin_attempt__isnull=True,
                    )
                ),
                name="cycle_origin_attempt_valid",
            ),
            models.CheckConstraint(
                condition=Q(policy_code="REV-FIXA-1.0"),
                name="cycle_policy_valid",
            ),
            models.CheckConstraint(
                condition=Q(state__in=ReviewCycleState.values),
                name="cycle_state_valid",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="cycle_lock_positive",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        state=ReviewCycleState.ACTIVE,
                        completed_at__isnull=True,
                        suspended_at__isnull=True,
                        suspension_reason__isnull=True,
                    )
                    | Q(
                        state=ReviewCycleState.COMPLETED,
                        completed_at__isnull=False,
                        suspended_at__isnull=True,
                        suspension_reason__isnull=True,
                    )
                    | Q(
                        state=ReviewCycleState.SUSPENDED,
                        completed_at__isnull=True,
                        suspended_at__isnull=False,
                        suspension_reason__isnull=False,
                    )
                ),
                name="cycle_state_dates_valid",
            ),
            models.CheckConstraint(
                condition=Q(suspension_reason__isnull=True) | ~Q(suspension_reason=""),
                name="cycle_suspend_reason_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"Ciclo {self.question_id} ({self.state})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self._validate_references()
        super().save(*args, **kwargs)

    def _validate_references(self) -> None:
        question = Question.objects.filter(pk=self.question_id).only("workspace_id").first()
        attempt = None
        if self.origin_attempt_id is not None:
            attempt = (
                Attempt.objects.filter(pk=self.origin_attempt_id)
                .only(
                    "workspace_id",
                    "question_id",
                    "question_revision_id",
                    "attempt_type",
                    "is_correct",
                    "status",
                )
                .first()
            )
        revision = (
            QuestionRevision.objects.filter(pk=self.origin_question_revision_id)
            .only("workspace_id", "question_id")
            .first()
        )
        if question is not None and question.workspace_id != self.workspace_id:
            raise ValidationError("O ciclo deve pertencer ao Workspace da questão.")
        if revision is None or (
            revision.workspace_id != self.workspace_id or revision.question_id != self.question_id
        ):
            raise ValidationError("Origin revision must belong to the cycle.")
        if self.origin_kind == ReviewCycleOriginKind.QUESTION_ACTIVATION:
            if self.origin_attempt_id is not None:
                raise ValidationError("Activation cycle cannot have an origin attempt.")
            return
        if (
            self.origin_kind != ReviewCycleOriginKind.INITIAL_ERROR
            or attempt is None
            or (
                attempt.workspace_id != self.workspace_id
                or attempt.question_id != self.question_id
                or attempt.question_revision_id != self.origin_question_revision_id
                or attempt.attempt_type != AttemptType.INITIAL
                or attempt.is_correct
                or attempt.status != AttemptStatus.VALID
            )
        ):
            raise ValidationError(
                "O ciclo automático exige tentativa inicial incorreta válida do mesmo contexto."
            )


class Review(models.Model):
    """Pendência ou fato histórico de uma etapa D1/D7/D14/D30."""

    POLICY_CODE = "REV-FIXA-1.0"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="reviews",
    )
    review_cycle = models.ForeignKey(
        ReviewCycle,
        on_delete=models.PROTECT,
        related_name="reviews",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name="reviews",
    )
    sequence_number = models.PositiveIntegerField()
    stage_code = models.CharField(max_length=8, choices=ReviewStageCode.choices)
    state = models.CharField(
        max_length=16,
        choices=ReviewState.choices,
        default=ReviewState.PENDING,
    )
    first_due_date = models.DateField()
    current_due_date = models.DateField()
    scheduled_from_attempt = models.ForeignKey(
        Attempt,
        on_delete=models.PROTECT,
        related_name="scheduled_reviews",
        null=True,
        blank=True,
    )
    transition_code = models.CharField(max_length=64)
    policy_code = models.CharField(max_length=64, default=POLICY_CODE)
    completed_at = models.DateTimeField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    lock_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews_review"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "state", "current_due_date", "created_at"],
                name="review_ws_state_due_idx",
            ),
            models.Index(
                fields=["workspace", "question", "state"],
                name="review_ws_q_state_idx",
            ),
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["review_cycle", "sequence_number"],
                name="review_cycle_sequence_uq",
            ),
            models.UniqueConstraint(
                fields=["review_cycle"],
                condition=Q(state=ReviewState.PENDING),
                name="review_cycle_pending_uq",
            ),
            models.CheckConstraint(
                condition=Q(sequence_number__gte=1),
                name="review_sequence_positive",
            ),
            models.CheckConstraint(
                condition=Q(stage_code__in=ReviewStageCode.values),
                name="review_stage_valid",
            ),
            models.CheckConstraint(
                condition=Q(state__in=ReviewState.values),
                name="review_state_valid",
            ),
            models.CheckConstraint(
                condition=Q(policy_code="REV-FIXA-1.0"),
                name="review_policy_valid",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="review_lock_positive",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        state=ReviewState.PENDING,
                        completed_at__isnull=True,
                        suspended_at__isnull=True,
                    )
                    | Q(
                        state=ReviewState.COMPLETED,
                        completed_at__isnull=False,
                        suspended_at__isnull=True,
                    )
                    | Q(
                        state=ReviewState.SUSPENDED,
                        completed_at__isnull=True,
                        suspended_at__isnull=False,
                    )
                    | Q(
                        state=ReviewState.CANCELLED,
                        completed_at__isnull=True,
                        suspended_at__isnull=True,
                    )
                ),
                name="review_state_dates_valid",
            ),
            models.CheckConstraint(
                condition=~Q(transition_code=""),
                name="review_transition_not_empty",
            ),
            models.CheckConstraint(
                condition=Q(scheduled_from_attempt__isnull=False)
                | Q(
                    sequence_number=1,
                    stage_code=ReviewStageCode.D1,
                    transition_code="QUESTION_ACTIVATION_D1",
                ),
                name="review_activation_anchor_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.review_cycle_id} #{self.sequence_number} {self.stage_code}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self._validate_references()
        if (
            self.state == ReviewState.PENDING
            and type(self)
            .objects.filter(
                review_cycle_id=self.review_cycle_id,
                state=ReviewState.PENDING,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("O ciclo já possui uma Review pendente.")
        super().save(*args, **kwargs)

    def _validate_references(self) -> None:
        cycle = (
            ReviewCycle.objects.filter(pk=self.review_cycle_id)
            .only("workspace_id", "question_id", "origin_kind")
            .first()
        )
        question = Question.objects.filter(pk=self.question_id).only("workspace_id").first()
        anchor = None
        if self.scheduled_from_attempt_id is not None:
            anchor = (
                Attempt.objects.filter(pk=self.scheduled_from_attempt_id)
                .only("workspace_id", "question_id", "status")
                .first()
            )
        if cycle is not None and (
            cycle.workspace_id != self.workspace_id or cycle.question_id != self.question_id
        ):
            raise ValidationError(
                "A Review deve pertencer ao ciclo, questão e Workspace informados."
            )
        if question is not None and question.workspace_id != self.workspace_id:
            raise ValidationError("A Review deve pertencer ao Workspace da questão.")
        if anchor is None:
            if (
                cycle is None
                or cycle.origin_kind != ReviewCycleOriginKind.QUESTION_ACTIVATION
                or self.sequence_number != 1
                or self.stage_code != ReviewStageCode.D1
                or self.transition_code != "QUESTION_ACTIVATION_D1"
            ):
                raise ValidationError("Only the activation D1 may omit its origin attempt.")
            return
        if anchor is not None and (
            anchor.workspace_id != self.workspace_id
            or anchor.question_id != self.question_id
            or anchor.status != AttemptStatus.VALID
        ):
            raise ValidationError("A âncora da Review deve ser válida e do mesmo contexto.")
