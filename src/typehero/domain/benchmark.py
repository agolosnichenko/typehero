"""Benchmark snapshot construction from session metrics.

A benchmark records only the comparable before/after subset of a session; it
gives no XP and cannot be failed (see the TUI benchmark flow).
"""

from __future__ import annotations

from typehero.domain.course import Course
from typehero.domain.progress import BenchmarkSnapshot, Progress
from typehero.engine.metrics import SessionMetrics


def snapshot_from_metrics(
    snapshot_date: str, metrics: SessionMetrics, kind: str = "interim"
) -> BenchmarkSnapshot:
    """Build a `BenchmarkSnapshot` (date + net WPM + accuracy + errors + kind)."""
    return BenchmarkSnapshot(
        date=snapshot_date,
        net_wpm=metrics.net_wpm,
        accuracy=metrics.accuracy,
        errors=metrics.errors,
        kind=kind,
    )


def needs_baseline(progress: Progress, course_id: str) -> bool:
    """True when no snapshot exists for the course and it was not skipped."""
    has_snapshot = bool(progress.benchmarks.get(course_id))
    return not has_snapshot and course_id not in progress.skipped_baselines


def is_final_lesson(course: Course, lesson_id: str) -> bool:
    """True if `lesson_id` is the last lesson in the course."""
    return bool(course.lessons) and course.lessons[-1].id == lesson_id


def has_final(progress: Progress, course_id: str) -> bool:
    """True if a `final` snapshot has already been recorded for the course."""
    return any(snap.kind == "final" for snap in progress.benchmarks.get(course_id, []))
