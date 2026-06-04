"""Benchmark snapshot construction from session metrics.

A benchmark records only the comparable before/after subset of a session; it
gives no XP and cannot be failed (see the TUI benchmark flow).
"""

from __future__ import annotations

from typehero.domain.progress import BenchmarkSnapshot
from typehero.engine.metrics import SessionMetrics


def snapshot_from_metrics(snapshot_date: str, metrics: SessionMetrics) -> BenchmarkSnapshot:
    """Build a `BenchmarkSnapshot` (date + net WPM + accuracy + errors) from metrics."""
    return BenchmarkSnapshot(
        date=snapshot_date,
        net_wpm=metrics.net_wpm,
        accuracy=metrics.accuracy,
        errors=metrics.errors,
    )
