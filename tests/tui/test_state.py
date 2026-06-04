import time
from datetime import date

from typehero.paths import content_dir
from typehero.tui.state import AppState, load_app_state


def test_load_app_state_reads_courses_achievements_and_profile(tmp_path):
    state = load_app_state(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    assert isinstance(state, AppState)
    assert set(state.courses) == {"en", "ru"}
    assert any(a.id == "flawless" for a in state.achievements)
    assert state.translator.t("menu.start", "en") == "Start lesson"
    assert state.progress.total_xp == 0  # fresh profile


def test_save_progress_round_trips_through_state(tmp_path):
    profile = tmp_path / "profile.json"
    state = load_app_state(
        content_root=content_dir(),
        profile_file=profile,
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    state.progress.total_xp = 123
    state.save()
    reloaded = load_app_state(
        content_root=content_dir(),
        profile_file=profile,
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    assert reloaded.progress.total_xp == 123
