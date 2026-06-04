import time
from datetime import date

import pytest

from typehero.content_loader import ContentError
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
    assert state.translator.t("menu.locked", "en") == "locked"
    assert state.progress.total_xp == 0  # fresh profile


def test_load_app_state_raises_when_no_courses(tmp_path):
    (tmp_path / "courses").mkdir()
    (tmp_path / "i18n").mkdir()
    (tmp_path / "i18n" / "en.yaml").write_text('menu.locked: "locked"\n', encoding="utf-8")
    (tmp_path / "achievements.yaml").write_text("achievements: []\n", encoding="utf-8")
    with pytest.raises(ContentError) as exc:
        load_app_state(
            content_root=tmp_path,
            profile_file=tmp_path / "profile.json",
            today=date(2026, 6, 4),
            clock=time.monotonic,
        )
    assert "No course files found" in str(exc.value)


def test_corrupt_profile_records_startup_notice(tmp_path):
    profile = tmp_path / "profile.json"
    profile.write_text("{not valid json", encoding="utf-8")
    state = load_app_state(
        content_root=content_dir(),
        profile_file=profile,
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    assert len(state.startup_notices) == 1
    assert "reset" in state.startup_notices[0]
    assert state.progress.total_xp == 0  # fell back to a fresh profile


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
