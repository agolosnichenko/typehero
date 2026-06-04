"""Apply one lesson outcome to player progress.

Pure logic with the calendar date injected: update the streak (any finished
attempt counts), award XP and mark completion on a pass, then check
achievements against the refreshed progress. Returns a summary for the UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from typehero.domain.lesson import Lesson, LessonOutcome
from typehero.domain.progress import Progress
from typehero.gamification.achievements import Achievement, newly_unlocked
from typehero.gamification.context import build_context
from typehero.gamification.streaks import update_streak
from typehero.gamification.xp import earned_xp, player_level


@dataclass(frozen=True)
class RewardSummary:
    """What the player earned for one attempt — rendered on the results screen."""

    passed: bool
    earned_xp: int
    total_xp: int
    level: int
    leveled_up: bool
    streak: int
    newly_unlocked: list[str]


def apply_lesson_outcome(
    progress: Progress,
    lesson: Lesson,
    outcome: LessonOutcome,
    achievements: list[Achievement],
    today: date,
) -> RewardSummary:
    """Mutate `progress` for one attempt and return a `RewardSummary`."""
    previous_level = player_level(progress.total_xp)
    is_first_clear = lesson.id not in progress.completed_lessons

    streak, last_active = update_streak(progress.current_streak, progress.last_active_date, today)
    progress.current_streak = streak
    progress.last_active_date = last_active

    earned = 0
    if outcome.result.passed:
        earned = earned_xp(
            lesson.reward_xp,
            accuracy=outcome.metrics.accuracy,
            net_wpm=outcome.metrics.net_wpm,
            min_wpm=lesson.criteria.min_wpm,
            first_clear=is_first_clear,
            streak=streak,
        )
        progress.total_xp += earned
        progress.mark_completed(lesson.id)

    context = build_context(outcome.metrics, progress)
    unlocked = newly_unlocked(achievements, context, set(progress.unlocked_achievements))
    progress.unlocked_achievements.extend(unlocked)

    level = player_level(progress.total_xp)
    return RewardSummary(
        passed=outcome.result.passed,
        earned_xp=earned,
        total_xp=progress.total_xp,
        level=level,
        leveled_up=level > previous_level,
        streak=streak,
        newly_unlocked=unlocked,
    )
