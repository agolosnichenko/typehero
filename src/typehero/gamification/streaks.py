"""Calendar-day streak tracking. `today` is injected for determinism."""

from __future__ import annotations

from datetime import date
from typing import NamedTuple


class StreakResult(NamedTuple):
    streak: int
    last_active_iso: str


def update_streak(
    current_streak: int,
    last_active: str | None,
    today: date,
) -> StreakResult:
    """Return the updated `(streak, last_active_iso)` for activity on `today`.

    Same day: unchanged. Next day: +1. Any larger gap: reset to 1.
    """
    today_iso = today.isoformat()
    if last_active is None:
        return StreakResult(1, today_iso)
    delta = (today - date.fromisoformat(last_active)).days
    if delta == 0:
        return StreakResult(current_streak, last_active)
    if delta == 1:
        return StreakResult(current_streak + 1, today_iso)
    return StreakResult(1, today_iso)
