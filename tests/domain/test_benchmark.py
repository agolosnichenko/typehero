import pytest

from typehero.domain.benchmark import (
    has_final,
    is_final_lesson,
    needs_baseline,
    snapshot_from_metrics,
)
from typehero.domain.course import Course
from typehero.domain.lesson import Lesson, LessonType, PassCriteria
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


def _course() -> Course:
    def lesson(lid: str) -> Lesson:
        return Lesson(
            id=lid,
            title={"en": lid},
            type=LessonType.KEYS,
            stages=["fj"],
            criteria=PassCriteria(max_error_rate=0.1, min_wpm=None),
            reward_xp=10,
        )

    return Course(
        id="en",
        layout="q",
        title={"en": "E"},
        benchmark_text="fj",
        lessons=[lesson("a"), lesson("b")],
    )


def test_needs_baseline_true_for_fresh_course():
    assert needs_baseline(Progress(), "en") is True


def test_needs_baseline_false_after_snapshot():
    p = Progress()
    p.add_benchmark("en", BenchmarkSnapshot("2026-06-04", 20.0, 0.9, 1, kind="baseline"))
    assert needs_baseline(p, "en") is False


def test_needs_baseline_false_when_skipped():
    assert needs_baseline(Progress(skipped_baselines=["en"]), "en") is False


def test_is_final_lesson():
    course = _course()
    assert is_final_lesson(course, "b") is True
    assert is_final_lesson(course, "a") is False


def test_has_final():
    p = Progress()
    assert has_final(p, "en") is False
    p.add_benchmark("en", BenchmarkSnapshot("2026-06-04", 20.0, 0.9, 1, kind="final"))
    assert has_final(p, "en") is True
