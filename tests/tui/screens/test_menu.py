import time
from datetime import date

from textual.widgets import ListView

from typehero.paths import content_dir
from typehero.tui.app import build_app
from typehero.tui.screens.achievements import AchievementsScreen
from typehero.tui.screens.baseline_prompt import BaselinePrompt
from typehero.tui.screens.benchmark import BenchmarkScreen
from typehero.tui.screens.lesson import LessonScreen
from typehero.tui.screens.menu import MenuRow
from typehero.tui.screens.progress import ProgressScreen
from typehero.tui.screens.settings import SettingsScreen


def _app(tmp_path, completed=None):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    if completed:
        app.state.progress.completed_lessons.extend(completed)
    return app


async def test_menu_rows_reflect_lock_state(tmp_path):
    app = _app(tmp_path)
    async with app.run_test():
        rows = app.screen.lesson_rows()
        assert isinstance(rows[0], MenuRow)
        assert rows[0].unlocked is True  # first lesson always unlocked
        assert rows[1].unlocked is False  # locked until en-01 done


async def test_completing_first_unlocks_second(tmp_path):
    app = _app(tmp_path, completed=["en-01-home-fj"])
    async with app.run_test():
        rows = app.screen.lesson_rows()
        assert rows[0].completed is True
        assert rows[1].unlocked is True


async def test_resuming_menu_refreshes_lock_state(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        lessons = app.screen.query_one("#lessons", ListView)
        assert lessons.children[1].disabled is True  # second locked on first render

        app.state.progress.mark_completed("en-01-home-fj")
        await pilot.press("p")  # push ProgressScreen
        await pilot.pause()
        await pilot.press("escape")  # pop back → ScreenResume on the menu
        await pilot.pause()

        lessons = app.screen.query_one("#lessons", ListView)
        assert lessons.children[1].disabled is False  # now unlocked after resume


async def test_menu_bindings_open_each_screen(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("b")
        assert isinstance(app.screen, BenchmarkScreen)
        await pilot.press("escape")
        await pilot.press("p")
        assert isinstance(app.screen, ProgressScreen)
        await pilot.press("escape")
        await pilot.press("a")
        assert isinstance(app.screen, AchievementsScreen)


async def test_selecting_first_lesson_prompts_for_baseline(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("enter")  # select the highlighted first lesson
        await pilot.pause()
        assert isinstance(app.screen, BaselinePrompt)


async def test_baseline_prompt_yes_opens_benchmark(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        assert isinstance(app.screen, BenchmarkScreen)


async def test_menu_s_opens_settings(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("s")
        assert isinstance(app.screen, SettingsScreen)


async def test_baseline_prompt_skip_records_and_opens_lesson(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("s")
        await pilot.pause()
        assert isinstance(app.screen, LessonScreen)
        assert app.state.progress.skipped_baselines == ["en"]
