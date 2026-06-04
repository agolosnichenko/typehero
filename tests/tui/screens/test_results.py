from typehero.domain.lesson import LessonResult
from typehero.engine.metrics import SessionMetrics
from typehero.gamification.rewards import RewardSummary
from typehero.play import LessonOutcome
from typehero.tui.screens.results import ResultsScreen


def _outcome() -> LessonOutcome:
    metrics = SessionMetrics(
        errors=0,
        error_rate=0.0,
        accuracy=1.0,
        net_wpm=42.0,
        raw_wpm=42.0,
        elapsed_seconds=60.0,
        max_combo=12,
    )
    return LessonOutcome(metrics=metrics, result=LessonResult(True, True, True))


def _summary() -> RewardSummary:
    return RewardSummary(
        passed=True,
        earned_xp=200,
        total_xp=200,
        level=2,
        leveled_up=True,
        streak=1,
        newly_unlocked=["flawless"],
    )


def test_summary_lines_include_xp_and_unlocks():
    screen = ResultsScreen(outcome=_outcome(), summary=_summary())
    lines = screen.summary_lines()
    joined = "\n".join(lines)
    assert "42" in joined  # WPM
    assert "200" in joined  # XP
    assert "flawless" in joined  # newly unlocked achievement
