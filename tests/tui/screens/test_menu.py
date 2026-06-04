import time
from datetime import date

from typehero.paths import content_dir
from typehero.tui.app import build_app
from typehero.tui.screens.achievements import AchievementsScreen
from typehero.tui.screens.benchmark import BenchmarkScreen
from typehero.tui.screens.menu import MenuRow
from typehero.tui.screens.progress import ProgressScreen


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
    app = _app(tmp_path, completed=["en-01-home-row"])
    async with app.run_test():
        rows = app.screen.lesson_rows()
        assert rows[0].completed is True
        assert rows[1].unlocked is True


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
