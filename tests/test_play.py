from typer.domain.lesson import Lesson, PassCriteria
from typer.engine.keystroke import Keystroke, KeystrokeKind
from typer.play import run_lesson


def _chars(text: str) -> list[Keystroke]:
    return [
        Keystroke(kind=KeystrokeKind.CHAR, char=c, timestamp=float(i)) for i, c in enumerate(text)
    ]


def _lesson(min_wpm: float | None) -> Lesson:
    return Lesson(
        id="en-01",
        title={"en": "Home row"},
        type="keys",
        stages=["fj"],
        criteria=PassCriteria(max_error_rate=0.1, min_wpm=min_wpm),
        reward_xp=50,
    )


def test_run_lesson_returns_metrics_and_result():
    outcome = run_lesson(target="fj", lesson=_lesson(min_wpm=None), keystrokes=_chars("fj"))
    assert outcome.metrics.errors == 0
    assert outcome.result.passed


def test_run_lesson_flags_failure_on_errors():
    outcome = run_lesson(target="fj", lesson=_lesson(min_wpm=None), keystrokes=_chars("xj"))
    assert outcome.metrics.errors == 1
    assert not outcome.result.passed  # 1/2 = 50% error rate > 10%


def test_run_lesson_speed_gate_fails_when_too_slow():
    # Two chars one second apart => very low WPM, below a 25 wpm gate.
    slow = [
        Keystroke(kind=KeystrokeKind.CHAR, char="f", timestamp=0.0),
        Keystroke(kind=KeystrokeKind.CHAR, char="j", timestamp=60.0),
    ]
    outcome = run_lesson(target="fj", lesson=_lesson(min_wpm=25.0), keystrokes=slow)
    assert outcome.metrics.errors == 0
    assert not outcome.result.passed
    assert not outcome.result.met_speed
