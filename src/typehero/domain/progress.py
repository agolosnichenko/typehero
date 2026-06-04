"""Persistent player progress."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class BenchmarkSnapshot:
    """One before/after benchmark measurement."""

    date: str
    net_wpm: float
    accuracy: float
    errors: int
    kind: str = "interim"

    def __post_init__(self) -> None:
        date.fromisoformat(self.date)  # raises ValueError on a non-ISO date
        if self.net_wpm < 0:
            raise ValueError(f"net_wpm must be non-negative, got {self.net_wpm}")
        if not 0.0 <= self.accuracy <= 1.0:
            raise ValueError(f"accuracy must be in [0, 1], got {self.accuracy}")
        if self.errors < 0:
            raise ValueError(f"errors must be non-negative, got {self.errors}")
        if self.kind not in {"baseline", "interim", "final"}:
            raise ValueError(f"kind must be baseline/interim/final, got {self.kind!r}")


@dataclass
class Progress:
    """All saved state for the single local profile."""

    ui_locale: str = "en"
    total_xp: int = 0
    completed_lessons: list[str] = field(default_factory=list)
    last_active_date: str | None = None
    current_streak: int = 0
    unlocked_achievements: list[str] = field(default_factory=list)
    benchmarks: dict[str, list[BenchmarkSnapshot]] = field(default_factory=dict)
    skipped_baselines: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
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

    def add_benchmark(self, course_id: str, snapshot: BenchmarkSnapshot) -> None:
        """Append a benchmark snapshot for a course."""
        self.benchmarks.setdefault(course_id, []).append(snapshot)
