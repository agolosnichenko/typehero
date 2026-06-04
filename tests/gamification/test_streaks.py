from datetime import date

from typehero.gamification.streaks import update_streak


def test_first_ever_activity_starts_streak_at_one():
    streak, last = update_streak(current_streak=0, last_active=None, today=date(2026, 6, 4))
    assert streak == 1
    assert last == "2026-06-04"


def test_same_day_does_not_change_streak():
    streak, last = update_streak(current_streak=3, last_active="2026-06-04", today=date(2026, 6, 4))
    assert streak == 3
    assert last == "2026-06-04"


def test_consecutive_day_increments_streak():
    streak, last = update_streak(current_streak=3, last_active="2026-06-04", today=date(2026, 6, 5))
    assert streak == 4
    assert last == "2026-06-05"


def test_gap_resets_streak_to_one():
    streak, last = update_streak(current_streak=9, last_active="2026-06-04", today=date(2026, 6, 7))
    assert streak == 1
    assert last == "2026-06-07"


def test_backwards_date_resets_streak_to_one():
    # A future-dated last_active (clock rolled back / edited profile) yields a
    # negative delta and must reset rather than silently extend the streak.
    streak, last = update_streak(current_streak=5, last_active="2026-06-07", today=date(2026, 6, 4))
    assert streak == 1
    assert last == "2026-06-04"
