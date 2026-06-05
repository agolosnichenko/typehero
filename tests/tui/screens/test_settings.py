import json
import time
from datetime import date
from pathlib import Path

from textual.widgets import Label, RadioButton, RadioSet

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

        assert LanguageChoice("ru", "Русский") in view.typing.choices
        assert LanguageChoice("en", "English") in view.typing.choices
        assert view.typing.selected == "ru"
        assert view.ui.selected == "en"
        assert {c.code for c in view.ui.choices} == {"en", "ru"}


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


async def test_selecting_ui_language_persists(tmp_path):
    app = _app(tmp_path)
    profile = tmp_path / "profile.json"
    async with app.run_test() as pilot:
        screen = SettingsScreen()
        app.push_screen(screen)
        await pilot.pause()

        ui = screen.query_one("#ui-language", RadioSet)
        ui.query(RadioButton)[1].value = True  # "ru" (sorted: en, ru)
        await pilot.pause()

        assert app.state.progress.ui_locale == "ru"
        assert json.loads(profile.read_text())["ui_locale"] == "ru"


async def test_real_change_shows_saved_toast_in_new_locale(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        screen = SettingsScreen()
        app.push_screen(screen)
        await pilot.pause()

        ui = screen.query_one("#ui-language", RadioSet)
        ui.query(RadioButton)[1].value = True  # "ru"
        await pilot.pause()

        messages = [n.message for n in app._notifications]
        assert "Сохранено" in messages  # localized to the just-chosen UI language


async def test_ui_language_switch_relocalizes_screen(tmp_path):
    app = _app(tmp_path)
    async with app.run_test() as pilot:
        screen = SettingsScreen()
        app.push_screen(screen)
        await pilot.pause()
        assert "Settings" in [str(label.render()) for label in screen.query(Label)]

        ui = screen.query_one("#ui-language", RadioSet)
        ui.query(RadioButton)[1].value = True  # "ru"
        await pilot.pause()

        labels = [str(label.render()) for label in screen.query(Label)]
        assert "Настройки" in labels  # the screen re-rendered in Russian
        assert "Settings" not in labels


async def test_save_failure_rolls_back_and_skips_confirmation(tmp_path, monkeypatch):
    app = _app(tmp_path)
    profile = tmp_path / "profile.json"
    async with app.run_test() as pilot:
        screen = SettingsScreen()
        app.push_screen(screen)
        await pilot.pause()

        def _fail() -> None:
            raise OSError("disk full")

        monkeypatch.setattr(app.state, "save", _fail)

        ui = screen.query_one("#ui-language", RadioSet)
        ui.query(RadioButton)[1].value = True  # attempt "ru"
        await pilot.pause()

        assert app.state.progress.ui_locale == "en"  # rolled back in memory
        assert not profile.exists()  # nothing written
        messages = [n.message for n in app._notifications]
        assert "Сохранено" not in messages and "Saved" not in messages
