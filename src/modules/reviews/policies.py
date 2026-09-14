"""Políticas puras e determinísticas da revisão fixa V0.3."""

from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar, Protocol

from shared.domain.time import Clock, Instant, LocalDate, TimeZoneId


class CalendarPort(Protocol):
    """Operações civis necessárias pelas policies, injetáveis em testes."""

    def today(self, time_zone_id: TimeZoneId) -> LocalDate:
        """Retorne hoje no fuso explícito."""
        ...

    def add_days(self, local_date: LocalDate, days: int) -> LocalDate:
        """Some dias civis sem consultar relógio global."""
        ...


class ReviewStage(StrEnum):
    """Etapas fixas aprovadas em REV-FIXA-1.0."""

    D1 = "D1"
    D7 = "D7"
    D14 = "D14"
    D30 = "D30"


class CycleState(StrEnum):
    """Estados estruturais usados na decisão de agendamento."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class ReviewStructuralState(StrEnum):
    """Estados persistidos que prevalecem sobre a situação temporal."""

    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"


class ReviewTemporalStatus(StrEnum):
    """Situação derivada, nunca persistida nem atualizada por job diário."""

    FUTURE = "FUTURE"
    DUE = "DUE"
    OVERDUE = "OVERDUE"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class ReviewScheduleDecision:
    """Saída sem efeito colateral da política fixa."""

    policy_code: str
    evaluated_at: Instant
    cycle_state: CycleState
    next_stage: ReviewStage | None
    next_due_date: LocalDate | None
    transition_code: str


class ReviewSchedulePolicy:
    """Calcule D1/D7/D14/D30 a partir da data civil real da resposta."""

    POLICY_CODE = "REV-FIXA-1.0"
    _CORRECT_TRANSITIONS: ClassVar[dict[ReviewStage, tuple[ReviewStage, int, str]]] = {
        ReviewStage.D1: (ReviewStage.D7, 7, "ADVANCE_D1_TO_D7"),
        ReviewStage.D7: (ReviewStage.D14, 14, "ADVANCE_D7_TO_D14"),
        ReviewStage.D14: (ReviewStage.D30, 30, "ADVANCE_D14_TO_D30"),
    }

    def __init__(self, *, clock: Clock, calendar: CalendarPort) -> None:
        self._clock = clock
        self._calendar = calendar

    def decide(
        self,
        *,
        current_stage: ReviewStage,
        is_correct: bool,
        time_zone_id: TimeZoneId,
        policy_code: str = POLICY_CODE,
    ) -> ReviewScheduleDecision:
        if policy_code != self.POLICY_CODE:
            raise ValueError("Versão de política de revisão não suportada.")
        evaluated_at = self._clock.now()
        today = self._calendar.today(time_zone_id)
        if not is_correct:
            return ReviewScheduleDecision(
                policy_code=policy_code,
                evaluated_at=evaluated_at,
                cycle_state=CycleState.ACTIVE,
                next_stage=ReviewStage.D1,
                next_due_date=self._calendar.add_days(today, 1),
                transition_code="RESET_TO_D1_AFTER_ERROR",
            )
        if current_stage == ReviewStage.D30:
            return ReviewScheduleDecision(
                policy_code=policy_code,
                evaluated_at=evaluated_at,
                cycle_state=CycleState.COMPLETED,
                next_stage=None,
                next_due_date=None,
                transition_code="COMPLETE_AFTER_D30_SUCCESS",
            )
        next_stage, days, transition_code = self._CORRECT_TRANSITIONS[current_stage]
        return ReviewScheduleDecision(
            policy_code=policy_code,
            evaluated_at=evaluated_at,
            cycle_state=CycleState.ACTIVE,
            next_stage=next_stage,
            next_due_date=self._calendar.add_days(today, days),
            transition_code=transition_code,
        )


class ReviewStatusPolicy:
    """Derive futura/devida/atrasada respeitando primeiro o estado estrutural."""

    def __init__(self, *, clock: Clock, calendar: CalendarPort) -> None:
        self._clock = clock
        self._calendar = calendar

    def evaluate(
        self,
        *,
        structural_state: ReviewStructuralState,
        current_due_date: LocalDate,
        time_zone_id: TimeZoneId,
    ) -> ReviewTemporalStatus:
        if structural_state != ReviewStructuralState.PENDING:
            return ReviewTemporalStatus(structural_state.value)
        today = self.reference_date(time_zone_id)
        if current_due_date.value > today.value:
            return ReviewTemporalStatus.FUTURE
        if current_due_date.value == today.value:
            return ReviewTemporalStatus.DUE
        return ReviewTemporalStatus.OVERDUE

    def reference_date(self, time_zone_id: TimeZoneId) -> LocalDate:
        """Capture a data civil usada por todas as leituras de situação."""
        return self._calendar.today(time_zone_id)
