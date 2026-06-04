import pytest

from typehero.domain.lesson import Lesson, PassCriteria, evaluate
from typehero.engine.metrics import SessionMetrics


def _metrics(error_rate: float, net_wpm: float) -> SessionMetrics:
    return SessionMetrics(
        errors=0,
        error_rate=error_rate,
        accuracy=1 - error_rate,
        net_wpm=net_wpm,
        raw_wpm=net_wpm,
        elapsed_seconds=60.0,
        max_combo=0,
    )


def test_passes_when_both_criteria_met():
    crit = PassCriteria(max_error_rate=0.05, min_wpm=25.0)
    result = evaluate(crit, _metrics(error_rate=0.04, net_wpm=30.0))
    assert result.passed
    assert result.met_accuracy
    assert result.met_speed


def test_fails_when_too_many_errors():
    crit = PassCriteria(max_error_rate=0.05, min_wpm=25.0)
    result = evaluate(crit, _metrics(error_rate=0.06, net_wpm=30.0))
    assert not result.passed
    assert not result.met_accuracy
    assert result.met_speed


def test_fails_when_too_slow():
    crit = PassCriteria(max_error_rate=0.05, min_wpm=25.0)
    result = evaluate(crit, _metrics(error_rate=0.0, net_wpm=20.0))
    assert not result.passed
    assert result.met_accuracy
    assert not result.met_speed


def test_speed_optional_when_min_wpm_none():
    crit = PassCriteria(max_error_rate=0.08, min_wpm=None)
    result = evaluate(crit, _metrics(error_rate=0.07, net_wpm=1.0))
    assert result.passed
    assert result.met_speed


def test_boundary_error_rate_exactly_at_threshold_passes():
    crit = PassCriteria(max_error_rate=0.05, min_wpm=None)
    result = evaluate(crit, _metrics(error_rate=0.05, net_wpm=99.0))
    assert result.met_accuracy


@pytest.mark.parametrize("bad_rate", [-0.1, 1.5])
def test_pass_criteria_rejects_out_of_range_error_rate(bad_rate):
    with pytest.raises(ValueError, match="max_error_rate"):
        PassCriteria(max_error_rate=bad_rate)


def test_pass_criteria_rejects_negative_min_wpm():
    with pytest.raises(ValueError, match="min_wpm"):
        PassCriteria(max_error_rate=0.05, min_wpm=-1.0)


def test_lesson_holds_criteria_and_reward():
    lesson = Lesson(
        id="en-01",
        title={"en": "Home row"},
        type="keys",
        stages=["fff jjj"],
        criteria=PassCriteria(max_error_rate=0.08, min_wpm=None),
        reward_xp=50,
    )
    assert lesson.criteria.max_error_rate == 0.08
    assert lesson.reward_xp == 50
