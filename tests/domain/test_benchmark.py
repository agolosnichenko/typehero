import pytest

from typehero.domain.benchmark import snapshot_from_metrics
from typehero.domain.progress import BenchmarkSnapshot, Progress
from typehero.engine.metrics import SessionMetrics


def _metrics() -> SessionMetrics:
    return SessionMetrics(
        errors=2,
        error_rate=0.05,
        accuracy=0.95,
        net_wpm=42.0,
        raw_wpm=44.0,
        elapsed_seconds=60.0,
        max_combo=30,
    )


def test_snapshot_from_metrics_picks_the_benchmark_subset():
    snap = snapshot_from_metrics("2026-06-04", _metrics())
    assert snap == BenchmarkSnapshot(date="2026-06-04", net_wpm=42.0, accuracy=0.95, errors=2)


def test_snapshot_from_metrics_sets_kind():
    snap = snapshot_from_metrics("2026-06-04", _metrics(), kind="baseline")
    assert snap.kind == "baseline"


def test_snapshot_kind_defaults_to_interim():
    assert snapshot_from_metrics("2026-06-04", _metrics()).kind == "interim"


def test_benchmark_snapshot_rejects_unknown_kind():
    with pytest.raises(ValueError, match="kind"):
        BenchmarkSnapshot(date="2026-06-04", net_wpm=10.0, accuracy=0.9, errors=0, kind="bogus")


def test_progress_defaults_skipped_baselines_empty():
    assert Progress().skipped_baselines == []
