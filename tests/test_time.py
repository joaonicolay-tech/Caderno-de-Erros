"""Objetos temporais e relógio controlável exigidos por CT-135."""

from datetime import UTC, date, datetime, timedelta

import pytest

from shared.domain.time import Calendar, FixedClock, Instant, LocalDate, TimeZoneId


def test_instant_requires_timezone_and_normalizes_to_utc() -> None:
    with pytest.raises(ValueError, match="datetime com fuso"):
        Instant(datetime(2026, 9, 2, 12, 0))

    instant = Instant(datetime.fromisoformat("2026-09-02T09:00:00-03:00"))
    assert instant.value == datetime(2026, 9, 2, 12, 0, tzinfo=UTC)


def test_timezone_id_accepts_iana_and_rejects_unknown_identifier() -> None:
    assert TimeZoneId(" America/Sao_Paulo ").value == "America/Sao_Paulo"

    with pytest.raises(ValueError, match="Fuso IANA desconhecido"):
        TimeZoneId("GMT-03-sem-historico")


def test_calendar_produces_distinct_local_dates_for_same_instant() -> None:
    instant = Instant(datetime(2026, 1, 1, 2, 30, tzinfo=UTC))
    clock = FixedClock(instant)
    calendar = Calendar(clock)

    assert calendar.today(TimeZoneId("America/Sao_Paulo")) == LocalDate(date(2025, 12, 31))
    assert calendar.today(TimeZoneId("Asia/Tokyo")) == LocalDate(date(2026, 1, 1))
    assert clock.now() == instant


def test_fixed_clock_can_advance_without_changing_system_clock() -> None:
    initial = Instant(datetime(2026, 9, 2, 23, 30, tzinfo=UTC))
    clock = FixedClock(initial)
    calendar = Calendar(clock)

    assert calendar.today(TimeZoneId("UTC")) == LocalDate(date(2026, 9, 2))
    clock.advance(timedelta(hours=1))
    assert calendar.today(TimeZoneId("UTC")) == LocalDate(date(2026, 9, 3))
    assert Calendar.add_days(LocalDate(date(2026, 9, 3)), 7) == LocalDate(date(2026, 9, 10))
