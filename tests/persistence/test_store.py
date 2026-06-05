import json
from dataclasses import asdict

from typehero.domain.ids import CourseId
from typehero.domain.progress import BenchmarkKind, BenchmarkSnapshot, Progress
from typehero.persistence.store import load_progress, save_progress


def test_round_trip_preserves_progress(tmp_path):
    path = tmp_path / "profile.json"
    original = Progress(ui_locale="ru", total_xp=350, current_streak=4)
    original.mark_completed("en-01")
    original.add_benchmark(CourseId("en"), BenchmarkSnapshot("2026-06-04", 22.0, 0.95, 2))

    save_progress(path, original)
    loaded = load_progress(path)

    assert loaded.ui_locale == "ru"
    assert loaded.total_xp == 350
    assert loaded.current_streak == 4
    assert loaded.completed_lessons == ["en-01"]
    assert loaded.benchmarks[CourseId("en")][0] == BenchmarkSnapshot("2026-06-04", 22.0, 0.95, 2)


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


def test_corrupt_file_invokes_on_corrupt_with_backup_path(tmp_path):
    path = tmp_path / "profile.json"
    path.write_text("{not valid json", encoding="utf-8")
    seen: list = []

    load_progress(path, on_corrupt=seen.append)

    assert len(seen) == 1
    assert seen[0].name.startswith("profile.json.corrupt-")
    assert seen[0].exists()


def test_on_corrupt_not_called_for_healthy_profile(tmp_path):
    path = tmp_path / "profile.json"
    save_progress(path, Progress(total_xp=10))
    seen: list = []

    load_progress(path, on_corrupt=seen.append)

    assert seen == []


def test_save_is_atomic_no_temp_left_behind(tmp_path):
    path = tmp_path / "profile.json"
    save_progress(path, Progress(total_xp=10))
    leftovers = [p for p in tmp_path.iterdir() if p.name != "profile.json"]
    assert leftovers == []


def test_wrong_typed_benchmarks_is_backed_up_and_reset(tmp_path):
    path = tmp_path / "profile.json"
    data = asdict(Progress(ui_locale="ru", total_xp=42, current_streak=2))
    data["benchmarks"] = []
    path.write_text(json.dumps(data), encoding="utf-8")

    loaded = load_progress(path)

    assert loaded == Progress()
    backups = list(tmp_path.glob("profile.json.corrupt-*"))
    assert len(backups) == 1


def test_valid_profile_missing_optional_key_is_preserved(tmp_path):
    # A profile written by an older version lacks a key added later. It is
    # forward-compatible data, not corruption: defaults fill the gap and the
    # rest of the progress survives instead of being reset.
    path = tmp_path / "profile.json"
    data = asdict(Progress(ui_locale="ru", total_xp=350, current_streak=4))
    del data["current_streak"]
    path.write_text(json.dumps(data), encoding="utf-8")

    loaded = load_progress(path)

    assert loaded.total_xp == 350
    assert loaded.ui_locale == "ru"
    assert loaded.current_streak == 0  # defaulted, not wiped
    assert list(tmp_path.glob("profile.json.corrupt-*")) == []


def test_string_completed_lessons_is_rejected_not_split(tmp_path):
    # list("abc") would silently yield ['a','b','c']; a non-list must be
    # treated as corruption, not coerced.
    path = tmp_path / "profile.json"
    data = asdict(Progress())
    data["completed_lessons"] = "abc"
    path.write_text(json.dumps(data), encoding="utf-8")

    loaded = load_progress(path)

    assert loaded == Progress()
    assert len(list(tmp_path.glob("profile.json.corrupt-*"))) == 1


def test_save_overwrites_existing_profile(tmp_path):
    path = tmp_path / "profile.json"
    save_progress(path, Progress(total_xp=10))
    save_progress(path, Progress(total_xp=99))

    loaded = load_progress(path)
    assert loaded.total_xp == 99
    leftovers = [p for p in tmp_path.iterdir() if p.name != "profile.json"]
    assert leftovers == []


def test_round_trips_kind_and_skipped_baselines(tmp_path):
    path = tmp_path / "profile.json"
    progress = Progress(skipped_baselines=[CourseId("en")])
    progress.add_benchmark(
        CourseId("en"), BenchmarkSnapshot("2026-06-04", 30.0, 0.95, 1, kind=BenchmarkKind.FINAL)
    )
    save_progress(path, progress)
    reloaded = load_progress(path)
    assert reloaded.skipped_baselines == ["en"]
    assert reloaded.benchmarks[CourseId("en")][0].kind is BenchmarkKind.FINAL


def test_loads_legacy_snapshot_without_kind(tmp_path):
    path = tmp_path / "profile.json"
    path.write_text(
        '{"benchmarks": {"en": [{"date": "2026-06-01", "net_wpm": 20.0, '
        '"accuracy": 0.9, "errors": 3}]}}',
        encoding="utf-8",
    )
    reloaded = load_progress(path)
    assert reloaded.benchmarks[CourseId("en")][0].kind == "interim"


def test_round_trip_preserves_active_course_id(tmp_path):
    path = tmp_path / "profile.json"
    save_progress(path, Progress(active_course_id=CourseId("ru")))
    assert load_progress(path).active_course_id == "ru"


def test_old_profile_without_active_course_id_defaults_to_en(tmp_path):
    path = tmp_path / "profile.json"
    path.write_text('{"ui_locale": "ru", "total_xp": 10}', encoding="utf-8")
    assert load_progress(path).active_course_id == "en"
