"""Persistent player progress."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BenchmarkSnapshot:
    """One before/after benchmark measurement."""

    date: str
    net_wpm: float
    accuracy: float
    errors: int


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

    def mark_completed(self, lesson_id: str) -> None:
        """Record a lesson as cleared (idempotent)."""
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)

    def add_benchmark(self, course_id: str, snapshot: BenchmarkSnapshot) -> None:
        """Append a benchmark snapshot for a course."""
        self.benchmarks.setdefault(course_id, []).append(snapshot)
