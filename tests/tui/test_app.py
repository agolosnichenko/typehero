import time
from datetime import date
from types import SimpleNamespace

from textual.app import App, SystemCommand

from typehero.paths import content_dir, profile_path
from typehero.tui.app import _SYSTEM_COMMAND_KEYS, TypeHeroApp, build_app
from typehero.tui.screens.menu import MenuScreen


def _app(tmp_path, *, ui_locale="en"):
    app = build_app(
        content_root=content_dir(),
        profile_file=tmp_path / "profile.json",
        today=date(2026, 6, 4),
        clock=time.monotonic,
    )
    app.state.progress.ui_locale = ui_locale
    return app


def _fake_screen(*, help_panel, maximized, allow_maximize):
    """A stand-in screen that drives every conditional branch of Textual's
    `App.get_system_commands` without a live, focused, maximized screen."""
    return SimpleNamespace(
        query=lambda _selector: [object()] if help_panel else [],
        maximized=maximized,
        focused=SimpleNamespace(allow_maximize=allow_maximize),
        action_minimize=lambda: None,
        action_maximize=lambda: None,
    )


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


async def test_system_commands_default_locale_in_english(tmp_path):
    app = _app(tmp_path)  # default ui_locale == "en"
    async with app.run_test():
        titles = [command.title for command in app.get_system_commands(app.screen)]
        assert "Theme" in titles  # en.yaml value, not the raw key
        assert "Quit" in titles


async def test_system_command_keys_match_textual_strings(tmp_path):
    """Drift guard: the map keys are verbatim copies of Textual's English help
    strings. A Textual upgrade that rewords one would otherwise pass through
    untranslated with no other test failing. The union over both help-panel and
    both maximize states covers all seven (Keys show/hide and Minimize/Maximize
    are mutually exclusive per screen state)."""
    app = _app(tmp_path)
    async with app.run_test():
        help_strings: set[str] = set()
        for help_panel in (False, True):
            for maximized, allow_maximize in ((object(), False), (None, True)):
                screen = _fake_screen(
                    help_panel=help_panel, maximized=maximized, allow_maximize=allow_maximize
                )
                help_strings.update(c.help for c in App.get_system_commands(app, screen))
    assert help_strings == set(_SYSTEM_COMMAND_KEYS), (
        "Textual's system-command help strings drifted from _SYSTEM_COMMAND_KEYS; "
        "re-verify the mapping against the installed Textual version."
    )


async def test_keys_command_localized_in_show_and_hide_states(tmp_path):
    """Both Keys states share the `palette.keys` title but carry distinct help,
    so the show/hide pair the design exists to handle is exercised end to end."""
    app = _app(tmp_path, ui_locale="ru")
    async with app.run_test():
        show = app.get_system_commands(
            _fake_screen(help_panel=False, maximized=None, allow_maximize=True)
        )
        hide = app.get_system_commands(
            _fake_screen(help_panel=True, maximized=None, allow_maximize=True)
        )
        show_help = {c.title: c.help for c in show}
        hide_help = {c.title: c.help for c in hide}
    assert "Клавиши" in show_help and "Клавиши" in hide_help  # shared localized title
    assert show_help["Клавиши"].startswith("Показать")  # keys_show.help (ru)
    assert hide_help["Клавиши"].startswith("Скрыть")  # keys_hide.help (ru)


async def test_unmapped_system_command_passes_through_unchanged(tmp_path, monkeypatch):
    """An unmapped command (e.g. one a future Textual adds) must survive the
    localizing loop untouched, not be dropped or crash on the None unpack."""
    extra = SystemCommand("Bell", "Ring the bell", lambda: None)
    base = App.get_system_commands

    def with_extra(self, screen):
        yield from base(self, screen)
        yield extra

    monkeypatch.setattr(App, "get_system_commands", with_extra)
    app = _app(tmp_path, ui_locale="ru")
    async with app.run_test():
        commands = list(app.get_system_commands(app.screen))
    assert extra in commands  # yielded verbatim despite the ru locale
