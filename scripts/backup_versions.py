"""Seleção não destrutiva de sete versões diárias e quatro semanais próprias."""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Version:
    name: str
    created_at: datetime


def select_versions(versions: list[Version], *, now: datetime) -> dict[str, list[str]]:
    """Relógio explícito; seleção não apaga nem altera nenhum arquivo."""
    if now.tzinfo is None or any(v.created_at.tzinfo is None for v in versions):
        raise ValueError("Versões e relógio exigem fuso explícito.")
    if len({v.name for v in versions}) != len(versions):
        raise ValueError("Identidades de versão duplicadas.")
    ordered = sorted(
        (v for v in versions if v.created_at <= now), key=lambda v: v.created_at, reverse=True
    )
    daily: list[str] = []
    for days in range(7):
        target = (now - timedelta(days=days)).date()
        match = next(
            (v for v in ordered if v.created_at.astimezone(now.tzinfo).date() == target), None
        )
        if match is not None:
            daily.append(match.name)
    weekly: list[str] = []
    for weeks in range(1, 5):
        target_week = (now - timedelta(weeks=weeks)).isocalendar()[:2]
        match = next(
            (
                v
                for v in ordered
                if v.created_at.astimezone(now.tzinfo).isocalendar()[:2] == target_week
            ),
            None,
        )
        if match is not None:
            weekly.append(match.name)
    return {"daily": daily, "weekly": weekly, "preserved": [v.name for v in ordered]}
