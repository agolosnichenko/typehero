from typehero.domain.progress import Progress
from typehero.engine.metrics import SessionMetrics
from typehero.gamification.context import CONTEXT_METRICS, build_context


def _metrics() -> SessionMetrics:
    return SessionMetrics(
        errors=2,
        error_rate=0.1,
        accuracy=0.9,
        net_wpm=40.0,
        raw_wpm=44.0,
        elapsed_seconds=30.0,
        max_combo=15,
    )


def test_build_context_merges_metrics_and_progress():
    progress = Progress(total_xp=500, current_streak=7)
    progress.mark_completed("en-01")
    ctx = build_context(_metrics(), progress)
    assert ctx["errors"] == 2.0
    assert ctx["net_wpm"] == 40.0
    assert ctx["max_combo"] == 15.0
    assert ctx["streak"] == 7.0
    assert ctx["total_xp"] == 500.0
    assert ctx["lessons_completed"] == 1.0


def test_context_values_are_all_numeric():
    ctx = build_context(_metrics(), Progress())
    assert all(isinstance(v, float) for v in ctx.values())


def test_context_metrics_constant_matches_built_keys():
    # The achievement loader validates metric names against CONTEXT_METRICS;
    # it must stay exactly in sync with the keys build_context produces.
    assert set(build_context(_metrics(), Progress())) == CONTEXT_METRICS
