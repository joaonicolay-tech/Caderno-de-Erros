"""Semântica temporal explícita, independente de HTTP e persistência."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True, slots=True)
class Instant:
    """Instante absoluto normalizado para UTC."""

    value: datetime

    def __post_init__(self) -> None:
        if self.value.tzinfo is None or self.value.utcoffset() is None:
            raise ValueError("Instant exige datetime com fuso.")
        object.__setattr__(self, "value", self.value.astimezone(UTC))


@dataclass(frozen=True, slots=True)
class LocalDate:
    """Data civil sem horário ou fuso embutido."""

    value: date


@dataclass(frozen=True, slots=True)
class TimeZoneId:
    """Identificador IANA validado pela base de fusos disponível."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise ValueError("TimeZoneId exige um identificador IANA não vazio.")
        normalized = self.value.strip()
        try:
            zone = ZoneInfo(normalized)
        except ZoneInfoNotFoundError as error:
            raise ValueError(f"Fuso IANA desconhecido: {normalized}.") from error
        object.__setattr__(self, "value", zone.key)

    @property
    def zone(self) -> ZoneInfo:
        return ZoneInfo(self.value)


class Clock(Protocol):
    """Fonte substituível de instantes."""

    def now(self) -> Instant:
        """Retorne o instante corrente da fonte."""
        ...


class SystemClock:
    """Adaptador do relógio real usado fora dos testes."""

    def now(self) -> Instant:
        return Instant(datetime.now(UTC))


class FixedClock:
    """Relógio controlável para testes determinísticos."""

    def __init__(self, instant: Instant) -> None:
        self._instant = instant

    def now(self) -> Instant:
        return self._instant

    def set(self, instant: Instant) -> None:
        self._instant = instant

    def advance(self, delta: timedelta) -> None:
        self._instant = Instant(self._instant.value + delta)


class Calendar:
    """Operações de data civil derivadas de uma fonte explícita de tempo."""

    def __init__(self, clock: Clock) -> None:
        self._clock = clock

    def today(self, time_zone_id: TimeZoneId) -> LocalDate:
        local_datetime = self._clock.now().value.astimezone(time_zone_id.zone)
        return LocalDate(local_datetime.date())

    @staticmethod
    def add_days(local_date: LocalDate, days: int) -> LocalDate:
        return LocalDate(local_date.value + timedelta(days=days))
