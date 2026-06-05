import json
import time
from datetime import date
from pathlib import Path

from textual.widgets import RadioButton, RadioSet

from typehero.paths import content_dir
from typehero.tui.app import TypeHeroApp, build_app
from typehero.tui.screens.menu import MenuScreen
from typehero.tui.screens.settings import LanguageChoice, SettingsScreen


def _app(tmp_path: Path) -> TypeHeroApp:
    return build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )


async def test_settings_view_marks_current_axes(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        app.state.progress.ui_locale = "en"
        app.state.progress.active_course_id = "ru"
        screen = SettingsScreen()
        app.push_screen(screen)
        await pilot.pause()
        view = screen.settings_view()

        assert LanguageChoice("ru", "Русский", True) in view.typing
        assert LanguageChoice("en", "English", False) in view.typing
        ui_current = {c.code: c.current for c in view.ui}
        assert ui_current == {"en": True, "ru": False}


async def test_selecting_typing_language_persists_and_updates_menu(tmp_path):
    app = _app(tmp_path)
    profile = tmp_path / "profile.json"
    async with app.run_test() as pilot:
        screen = SettingsScreen()
        app.push_screen(screen)
        await pilot.pause()

        typing = screen.query_one("#typing-language", RadioSet)
        typing.query(RadioButton)[1].value = True  # "ru" (sorted: en, ru)
        await pilot.pause()

        assert app.state.progress.active_course_id == "ru"
        assert json.loads(profile.read_text())["active_course_id"] == "ru"

        await pilot.press("escape")  # pop back to the menu
        await pilot.pause()
        menu = app.screen
        assert isinstance(menu, MenuScreen)
        assert menu.lesson_rows()[0].lesson.id.startswith("ru-")
