from typer.domain.progress import BenchmarkSnapshot, Progress
from typer.persistence.store import load_progress, save_progress


def test_round_trip_preserves_progress(tmp_path):
    path = tmp_path / "profile.json"
    original = Progress(ui_locale="ru", total_xp=350, current_streak=4)
    original.mark_completed("en-01")
    original.add_benchmark("en", BenchmarkSnapshot("2026-06-04", 22.0, 0.95, 2))

    save_progress(path, original)
    loaded = load_progress(path)

    assert loaded.ui_locale == "ru"
    assert loaded.total_xp == 350
    assert loaded.current_streak == 4
    assert loaded.completed_lessons == ["en-01"]
    assert loaded.benchmarks["en"][0] == BenchmarkSnapshot("2026-06-04", 22.0, 0.95, 2)


def test_missing_file_returns_default_progress(tmp_path):
    loaded = load_progress(tmp_path / "nope.json")
    assert loaded == Progress()


def test_corrupt_file_is_backed_up_and_reset(tmp_path):
    path = tmp_path / "profile.json"
    path.write_text("{not valid json", encoding="utf-8")

    loaded = load_progress(path)

    assert loaded == Progress()
    backups = list(tmp_path.glob("profile.json.corrupt-*"))
    assert len(backups) == 1


def test_save_is_atomic_no_temp_left_behind(tmp_path):
    path = tmp_path / "profile.json"
    save_progress(path, Progress(total_xp=10))
    leftovers = [p for p in tmp_path.iterdir() if p.name != "profile.json"]
    assert leftovers == []
