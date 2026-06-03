import pytest

from typer.gamification.achievements import Achievement, check, newly_unlocked


def _ach(ach_id: str, metric: str, op: str, value: float) -> Achievement:
    return Achievement(
        id=ach_id,
        title={"en": ach_id},
        desc={"en": ach_id},
        metric=metric,
        op=op,
        value=value,
    )


def test_check_equality_condition():
    flawless = _ach("flawless", "errors", "==", 0)
    assert check(flawless, {"errors": 0})
    assert not check(flawless, {"errors": 1})


def test_check_gte_condition():
    speed = _ach("speed", "net_wpm", ">=", 80)
    assert check(speed, {"net_wpm": 80})
    assert check(speed, {"net_wpm": 95})
    assert not check(speed, {"net_wpm": 79})


def test_missing_metric_is_not_unlocked():
    speed = _ach("speed", "net_wpm", ">=", 80)
    assert not check(speed, {"errors": 0})


def test_check_raises_on_unknown_operator():
    bad = _ach("bad", "errors", "!=", 0)
    with pytest.raises(KeyError):
        check(bad, {"errors": 1})


def test_newly_unlocked_excludes_already_owned():
    flawless = _ach("flawless", "errors", "==", 0)
    speed = _ach("speed", "net_wpm", ">=", 80)
    achievements = [flawless, speed]
    context = {"errors": 0, "net_wpm": 90}
    result = newly_unlocked(achievements, context, already_unlocked={"flawless"})
    assert result == ["speed"]
