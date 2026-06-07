import time
from datetime import date

from typehero.paths import content_dir, profile_path
from typehero.tui.app import TypeHeroApp, build_app
from typehero.tui.screens.menu import MenuScreen


async def test_app_starts_on_the_menu(tmp_path):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    async with app.run_test():
        assert isinstance(app.screen, MenuScreen)


def test_build_app_defaults_use_real_paths(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    app = build_app()
    assert isinstance(app, TypeHeroApp)
    assert app.state.profile_file == profile_path()


async def test_system_commands_localized_to_ui_locale(tmp_path):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    app.state.progress.ui_locale = "ru"
    async with app.run_test():
        titles = [command.title for command in app.get_system_commands(app.screen)]
        assert "Тема" in titles
        assert "Выход" in titles
        assert "Theme" not in titles


async def test_command_palette_placeholder_localized(tmp_path):
    from textual.widgets import Input

    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    app.state.progress.ui_locale = "ru"
    async with app.run_test() as pilot:
        app.action_command_palette()
        await pilot.pause()
        placeholders = [field.placeholder for field in app.screen.query(Input)]
        assert "Поиск команд…" in placeholders
