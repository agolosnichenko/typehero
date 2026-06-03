from typer.gamification.xp import (
    accuracy_bonus,
    earned_xp,
    player_level,
    speed_bonus,
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
    repeat = earned_xp(base, accuracy=0.9, net_wpm=10.0, min_wpm=None, first_clear=False)
    first = earned_xp(base, accuracy=0.9, net_wpm=10.0, min_wpm=None, first_clear=True)
    assert repeat == 100
    assert first == 200


def test_player_level_increases_with_xp():
    assert player_level(0) == 1
    assert player_level(99) == 1
    assert player_level(100) == 2  # first threshold base*1^1.5 = 100
    assert player_level(100 + 282) == 3  # + base*2^1.5 ≈ 282
