"""XP rewards and player-level curve.

Bonuses reward quality (accuracy, speed) and first clears, steering players
toward progressing through the course rather than grinding easy lessons.
"""

from __future__ import annotations

_ACCURACY_FLOOR = 0.9
_ACCURACY_MAX_BONUS = 0.5
_SPEED_CAP_RATIO = 0.5
_SPEED_MAX_BONUS = 0.3
_FIRST_CLEAR_MULTIPLIER = 2.0
_LEVEL_BASE = 100
_LEVEL_EXPONENT = 1.5


def accuracy_bonus(accuracy: float) -> float:
    """1.0 at/below 90% accuracy, scaling linearly to 1.5 at 100%."""
    if accuracy >= 1.0:
        return 1.0 + _ACCURACY_MAX_BONUS
    if accuracy <= _ACCURACY_FLOOR:
        return 1.0
    span = (accuracy - _ACCURACY_FLOOR) / (1.0 - _ACCURACY_FLOOR)
    return round(1.0 + span * _ACCURACY_MAX_BONUS, 10)


def speed_bonus(net_wpm: float, min_wpm: float | None) -> float:
    """1.0 until `min_wpm` is met, scaling to 1.3 at 50% over the requirement."""
    if not min_wpm or net_wpm < min_wpm:
        return 1.0
    over = (net_wpm - min_wpm) / min_wpm
    span = min(over, _SPEED_CAP_RATIO) / _SPEED_CAP_RATIO
    return 1.0 + span * _SPEED_MAX_BONUS


def earned_xp(
    base: int,
    accuracy: float,
    net_wpm: float,
    min_wpm: float | None,
    first_clear: bool,
) -> int:
    """Total XP for a session, rounded to the nearest integer."""
    multiplier = accuracy_bonus(accuracy) * speed_bonus(net_wpm, min_wpm)
    if first_clear:
        multiplier *= _FIRST_CLEAR_MULTIPLIER
    return round(base * multiplier)


def player_level(total_xp: int, base: int = _LEVEL_BASE) -> int:
    """Player level from cumulative XP using a `base * level^1.5` curve."""
    level = 1
    spent = 0
    while True:
        needed = int(base * level**_LEVEL_EXPONENT)
        if total_xp < spent + needed:
            return level
        spent += needed
        level += 1
