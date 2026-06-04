import pytest
from hypothesis import given
from hypothesis import strategies as st

from typehero.gamification.xp import (
    accuracy_bonus,
    earned_xp,
    player_level,
    speed_bonus,
    streak_bonus,
)


def test_accuracy_bonus_ranges():
    assert accuracy_bonus(0.80) == 1.0  # at or below 0.9 floor
    assert accuracy_bonus(0.90) == 1.0
    assert accuracy_bonus(1.00) == 1.5  # perfect
    assert accuracy_bonus(0.95) == 1.25  # halfway


def test_speed_bonus_requires_meeting_min():
    assert speed_bonus(net_wpm=20.0, min_wpm=25.0) == 1.0  # below min
    assert speed_bonus(net_wpm=25.0, min_wpm=25.0) == 1.0  # exactly min
    assert speed_bonus(net_wpm=37.5, min_wpm=25.0) == 1.3  # 50% over caps at 1.3
    assert speed_bonus(net_wpm=50.0, min_wpm=25.0) == 1.3  # beyond cap stays 1.3


def test_speed_bonus_neutral_when_no_min():
    assert speed_bonus(net_wpm=99.0, min_wpm=None) == 1.0


def test_earned_xp_first_clear_doubles():
    base = 100
    repeat = earned_xp(base=base, accuracy=0.9, net_wpm=10.0, min_wpm=None, first_clear=False)
    first = earned_xp(base=base, accuracy=0.9, net_wpm=10.0, min_wpm=None, first_clear=True)
    assert repeat == 100
    assert first == 200


def test_player_level_increases_with_xp():
    assert player_level(0) == 1
    assert player_level(79) == 1
    assert player_level(80) == 2  # first threshold base*1^1.5 = 80
    assert player_level(80 + 226) == 3  # + base*2^1.5 = int(80*2.828) = 226


def test_player_level_honors_non_default_base():
    # With base=50 the first threshold is 50*1^1.5 = 50, not 100.
    assert player_level(49, base=50) == 1
    assert player_level(50, base=50) == 2


def test_player_level_rejects_non_positive_base():
    with pytest.raises(ValueError, match="base"):
        player_level(100, base=0)


@given(st.integers(min_value=0, max_value=1_000_000))
def test_player_level_is_monotonic_in_xp(xp: int):
    assert player_level(xp) <= player_level(xp + 1)


def test_streak_bonus_ranges():
    assert streak_bonus(0) == 1.0
    assert streak_bonus(1) == 1.0
    assert streak_bonus(2) == 1.02
    assert streak_bonus(10) == 1.18
    assert streak_bonus(50) == 1.18  # capped at 10 days


def test_earned_xp_applies_streak_multiplier():
    base = 100
    no_streak = earned_xp(base=base, accuracy=0.9, net_wpm=10.0, min_wpm=None, first_clear=False)
    with_streak = earned_xp(
        base=base, accuracy=0.9, net_wpm=10.0, min_wpm=None, first_clear=False, streak=10
    )
    assert no_streak == 100
    assert with_streak == 118
