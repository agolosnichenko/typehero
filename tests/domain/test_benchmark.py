from typehero.domain.benchmark import snapshot_from_metrics
from typehero.domain.progress import BenchmarkSnapshot
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
