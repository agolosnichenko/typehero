"""Persistent player progress."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class BenchmarkKind(StrEnum):
    """Where a benchmark snapshot sits in a course's lifecycle.

    `baseline` is taken once before the first lesson, `final` once after the
    last, and `interim` is any on-demand measurement in between. The closed set
    is pinned so a typo at a call site is a type error, not a runtime surprise.
    """

    BASELINE = "baseline"
    INTERIM = "interim"
    FINAL = "final"


@dataclass(frozen=True)
class BenchmarkSnapshot:
    """One before/after benchmark measurement."""

    date: str
    net_wpm: float
    accuracy: float
    errors: int
    kind: BenchmarkKind = BenchmarkKind.INTERIM

    def __post_init__(self) -> None:
        date.fromisoformat(self.date)  # raises ValueError on a non-ISO date
        if self.net_wpm < 0:
            raise ValueError(f"net_wpm must be non-negative, got {self.net_wpm}")
        if not 0.0 <= self.accuracy <= 1.0:
            raise ValueError(f"accuracy must be in [0, 1], got {self.accuracy}")
        if self.errors < 0:
            raise ValueError(f"errors must be non-negative, got {self.errors}")
        try:
            object.__setattr__(self, "kind", BenchmarkKind(self.kind))
        except ValueError as exc:
            raise ValueError(f"kind must be baseline/interim/final, got {self.kind!r}") from exc


@dataclass
class Progress:
    """All saved state for the single local profile."""

    ui_locale: str = "en"
    active_course_id: str = "en"
    total_xp: int = 0
    completed_lessons: list[str] = field(default_factory=list)
    last_active_date: str | None = None
    current_streak: int = 0
    unlocked_achievements: list[str] = field(default_factory=list)
    benchmarks: dict[str, list[BenchmarkSnapshot]] = field(default_factory=dict)
    skipped_baselines: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.active_course_id:
            raise ValueError("active_course_id must be a non-empty string")
        if self.total_xp < 0:
            raise ValueError(f"total_xp must be non-negative, got {self.total_xp}")
        if self.current_streak < 0:
            raise ValueError(f"current_streak must be non-negative, got {self.current_streak}")
        if self.last_active_date is not None:
            date.fromisoformat(self.last_active_date)  # raises ValueError on a non-ISO date

    def mark_completed(self, lesson_id: str) -> None:
        """Record a lesson as cleared (idempotent)."""
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)

    def mark_baseline_skipped(self, course_id: str) -> None:
        """Record a course's baseline benchmark as declined (idempotent)."""
        if course_id not in self.skipped_baselines:
            self.skipped_baselines.append(course_id)

    def add_benchmark(self, course_id: str, snapshot: BenchmarkSnapshot) -> None:
        """Append a benchmark snapshot for a course."""
        self.benchmarks.setdefault(course_id, []).append(snapshot)
