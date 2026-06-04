from datetime import date

from typehero.domain.lesson import Lesson, LessonOutcome, LessonResult, LessonType, PassCriteria
from typehero.domain.progress import Progress
from typehero.engine.metrics import SessionMetrics
from typehero.gamification.achievements import Achievement
from typehero.gamification.rewards import apply_lesson_outcome


def _lesson() -> Lesson:
    return Lesson(
        id="en-01",
        title={"en": "Home row"},
        type=LessonType.KEYS,
        stages=["fj"],
        criteria=PassCriteria(max_error_rate=0.1, min_wpm=None),
        reward_xp=100,
    )


def _outcome(passed: bool, *, errors: int = 0, net_wpm: float = 30.0) -> LessonOutcome:
    # accuracy 0.9 -> accuracy_bonus == 1.0, so XP assertions below isolate the
    # first-clear and streak factors from the quality bonus.
    metrics = SessionMetrics(
        errors=errors,
        error_rate=0.0 if passed else 0.5,
        accuracy=0.9 if passed else 0.5,
        net_wpm=net_wpm,
        raw_wpm=net_wpm,
        elapsed_seconds=60.0,
        max_combo=10,
    )
    result = LessonResult(met_accuracy=passed, met_speed=True)
    return LessonOutcome(metrics=metrics, result=result)


def _flawless() -> Achievement:
    return Achievement(
        id="flawless",
        title={"en": "Flawless"},
        desc={"en": "Zero typos"},
        metric="errors",
        op="==",
        value=0,
    )


def test_pass_awards_xp_marks_completion_and_starts_streak():
    progress = Progress()
    summary = apply_lesson_outcome(
        progress, _lesson(), _outcome(passed=True), achievements=[], today=date(2026, 6, 4)
    )
    assert summary.passed
    assert summary.earned_xp == 200  # first clear doubles 100
    assert progress.total_xp == 200
    assert progress.completed_lessons == ["en-01"]
    assert progress.current_streak == 1
    assert progress.last_active_date == "2026-06-04"


def test_fail_gives_no_xp_or_completion_but_still_counts_for_streak():
    progress = Progress()
    summary = apply_lesson_outcome(
        progress,
        _lesson(),
        _outcome(passed=False, errors=3),
        achievements=[],
        today=date(2026, 6, 4),
    )
    assert not summary.passed
    assert summary.earned_xp == 0
    assert progress.total_xp == 0
    assert progress.completed_lessons == []
    assert progress.current_streak == 1


def test_repeat_clear_does_not_double_and_unlocks_achievement():
    progress = Progress(completed_lessons=["en-01"])
    summary = apply_lesson_outcome(
        progress,
        _lesson(),
        _outcome(passed=True),
        achievements=[_flawless()],
        today=date(2026, 6, 4),
    )
    assert summary.earned_xp == 100  # no first-clear bonus
    assert summary.newly_unlocked == ("flawless",)
    assert progress.unlocked_achievements == ["flawless"]


def test_level_up_is_reported():
    progress = Progress(total_xp=50)
    summary = apply_lesson_outcome(
        progress, _lesson(), _outcome(passed=True), achievements=[], today=date(2026, 6, 4)
    )
    # 50 + 200 = 250 XP crosses the level-2 threshold (100).
    assert summary.leveled_up
    assert summary.level >= 2
