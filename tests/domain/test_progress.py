from typer.domain.progress import BenchmarkSnapshot, Progress


def test_default_progress_is_empty():
    p = Progress()
    assert p.ui_locale == "en"
    assert p.total_xp == 0
    assert p.completed_lessons == []
    assert p.current_streak == 0
    assert p.last_active_date is None
    assert p.unlocked_achievements == []
    assert p.benchmarks == {}


def test_mark_completed_is_idempotent():
    p = Progress()
    p.mark_completed("l1")
    p.mark_completed("l1")
    assert p.completed_lessons == ["l1"]


def test_add_benchmark_appends_per_course():
    p = Progress()
    snap = BenchmarkSnapshot(date="2026-06-04", net_wpm=20.0, accuracy=0.9, errors=3)
    p.add_benchmark("en", snap)
    assert p.benchmarks["en"] == [snap]
