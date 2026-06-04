"""Lesson definition and pass/fail evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from typehero.engine.metrics import SessionMetrics


class LessonType(StrEnum):
    """The kind of exercise a lesson presents.

    Drives nothing yet, but pins the closed set so the content loader rejects
    typos instead of carrying an arbitrary string through the domain.
    """

    KEYS = "keys"
    COMBOS = "combos"
    WORDS = "words"
    TEXT = "text"


@dataclass(frozen=True)
class PassCriteria:
    """Thresholds a session must meet to clear a lesson.

    `max_error_rate` is a fraction of error keystrokes and is always required.
    `min_wpm` is optional (`None` on early lessons where speed is not gated).
    """

    max_error_rate: float
    min_wpm: float | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.max_error_rate <= 1.0:
            raise ValueError(f"max_error_rate must be in [0, 1], got {self.max_error_rate}")
        if self.min_wpm is not None and self.min_wpm <= 0:
            raise ValueError(f"min_wpm must be positive when set, got {self.min_wpm}")


@dataclass(frozen=True)
class LessonResult:
    """Outcome of evaluating one session against a lesson's criteria."""

    met_accuracy: bool
    met_speed: bool

    @property
    def passed(self) -> bool:
        """A lesson is cleared only when BOTH accuracy and speed criteria hold."""
        return self.met_accuracy and self.met_speed


@dataclass(frozen=True)
class LessonOutcome:
    """Metrics plus pass/fail for one completed attempt."""

    metrics: SessionMetrics
    result: LessonResult


@dataclass(frozen=True)
class Lesson:
    """A single ordered exercise in a course.

    `stages` holds raw stage payloads passed through from YAML; their structure
    is consumed by the TUI and deliberately not modeled here yet.
    """

    id: str
    title: dict[str, str]
    type: LessonType
    stages: list[object]
    criteria: PassCriteria
    reward_xp: int

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("lesson id must be non-empty")
        if self.reward_xp < 0:
            raise ValueError(f"reward_xp must be non-negative, got {self.reward_xp}")


def evaluate(criteria: PassCriteria, metrics: SessionMetrics) -> LessonResult:
    """Evaluate a session's metrics against a lesson's pass criteria."""
    met_accuracy = metrics.error_rate <= criteria.max_error_rate
    met_speed = criteria.min_wpm is None or metrics.net_wpm >= criteria.min_wpm
    return LessonResult(met_accuracy=met_accuracy, met_speed=met_speed)


def stage_text(stage: object) -> str:
    """Return the typed text of a stage.

    Only explicit string stages are supported here. Generator stages
    (`wordlist`/`corpus` dicts) are not yet supported and raise.

    Raises:
        ValueError: if the stage is a generator spec rather than a string.
    """
    if isinstance(stage, str):
        return stage
    raise ValueError(f"generator stage not supported yet: {stage!r}")


def lesson_target(lesson: Lesson) -> str:
    """The full text the player types for a lesson: its stages joined by spaces."""
    return " ".join(stage_text(stage) for stage in lesson.stages)
