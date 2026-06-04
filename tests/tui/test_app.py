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
