from typehero.domain.ids import CourseId
from typehero.domain.lesson import LessonOutcome, LessonResult
from typehero.engine.metrics import SessionMetrics
from typehero.gamification.rewards import RewardSummary
from typehero.tui.screens.results import ResultsScreen


def _outcome(*, met_accuracy: bool = True, met_speed: bool = True) -> LessonOutcome:
    metrics = SessionMetrics(
        errors=0,
        error_rate=0.0,
        accuracy=1.0,
        net_wpm=42.0,
        raw_wpm=42.0,
        elapsed_seconds=60.0,
        max_combo=12,
    )
    result = LessonResult(met_accuracy=met_accuracy, met_speed=met_speed)
    return LessonOutcome(metrics=metrics, result=result)


def _summary(
    *,
    passed: bool = True,
    earned_xp: int = 200,
    leveled_up: bool = True,
    newly_unlocked: tuple[str, ...] = ("flawless",),
) -> RewardSummary:
    return RewardSummary(
        passed=passed,
        earned_xp=earned_xp,
        total_xp=200,
        level=2,
        leveled_up=leveled_up,
        streak=1,
        newly_unlocked=newly_unlocked,
    )


def test_summary_lines_include_xp_and_unlocks():
    screen = ResultsScreen(outcome=_outcome(), summary=_summary())
    lines = screen.summary_lines()
    assert "Lesson passed!" in lines
    assert "WPM: 42" in lines
    assert "XP earned: 200" in lines
    assert "Level: 2 (up!)" in lines
    assert "Unlocked: flawless" in lines


def test_summary_lines_failed_attempt():
    screen = ResultsScreen(
        outcome=_outcome(met_speed=False),
        summary=_summary(passed=False, earned_xp=0, leveled_up=False, newly_unlocked=()),
    )
    lines = screen.summary_lines()
    assert "Not yet — try again" in lines
    assert "XP earned: 0" in lines


def test_summary_lines_no_level_up_or_unlocks():
    screen = ResultsScreen(
        outcome=_outcome(),
        summary=_summary(leveled_up=False, newly_unlocked=()),
    )
    lines = screen.summary_lines()
    assert "Level: 2" in lines
    assert "Level: 2 (up!)" not in lines
    assert not any(line.startswith("Unlocked:") for line in lines)


def test_results_without_final_pops_to_previous():
    screen = ResultsScreen(outcome=_outcome(), summary=_summary())
    assert screen._final_course_id is None


def test_results_carries_final_course_id():
    screen = ResultsScreen(outcome=_outcome(), summary=_summary(), final_course_id=CourseId("en"))
    assert screen._final_course_id == "en"
