"""Lesson definition and pass/fail evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from typer.engine.metrics import SessionMetrics


@dataclass(frozen=True)
class PassCriteria:
    """Thresholds a session must meet to clear a lesson.

    `max_error_rate` is a fraction of error keystrokes and is always required.
    `min_wpm` is optional (`None` on early lessons where speed is not gated).
    """

    max_error_rate: float
    min_wpm: float | None = None


@dataclass(frozen=True)
class LessonResult:
    """Outcome of evaluating one session against a lesson's criteria."""

    passed: bool
    met_accuracy: bool
    met_speed: bool


@dataclass(frozen=True)
class Lesson:
    """A single ordered exercise in a course."""

    id: str
    title: dict[str, str]
    type: str
    stages: list[object]
    criteria: PassCriteria
    reward_xp: int


def evaluate(criteria: PassCriteria, metrics: SessionMetrics) -> LessonResult:
    """A lesson is cleared only when BOTH accuracy and speed criteria hold."""
    met_accuracy = metrics.error_rate <= criteria.max_error_rate
    met_speed = criteria.min_wpm is None or metrics.net_wpm >= criteria.min_wpm
    return LessonResult(
        passed=met_accuracy and met_speed,
        met_accuracy=met_accuracy,
        met_speed=met_speed,
    )
