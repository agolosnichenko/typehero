"""Builds the metric context dict that achievement conditions are checked against."""

from __future__ import annotations

from typehero.domain.progress import Progress
from typehero.engine.metrics import SessionMetrics

CONTEXT_METRICS: frozenset[str] = frozenset(
    {
        "errors",
        "error_rate",
        "accuracy",
        "net_wpm",
        "raw_wpm",
        "elapsed_seconds",
        "max_combo",
        "streak",
        "total_xp",
        "lessons_completed",
    }
)


def build_context(metrics: SessionMetrics, progress: Progress) -> dict[str, float]:
    """Merge session metrics and player progress into one flat metric map.

    Achievement conditions reference these keys by name; keeping the set
    explicit (and validated at load time against `CONTEXT_METRICS`) prevents a
    typo'd or forgotten key from silently never unlocking an achievement.
    """
    return {
        "errors": float(metrics.errors),
        "error_rate": metrics.error_rate,
        "accuracy": metrics.accuracy,
        "net_wpm": metrics.net_wpm,
        "raw_wpm": metrics.raw_wpm,
        "elapsed_seconds": metrics.elapsed_seconds,
        "max_combo": float(metrics.max_combo),
        "streak": float(progress.current_streak),
        "total_xp": float(progress.total_xp),
        "lessons_completed": float(len(progress.completed_lessons)),
    }
