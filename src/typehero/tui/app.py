"""The Textual application shell: owns AppState and screen navigation."""

from __future__ import annotations

import random
import sys
import time
from collections.abc import Callable, Iterable
from datetime import date
from pathlib import Path

from textual.app import App, SystemCommand
from textual.command import CommandPalette
from textual.screen import Screen

from typehero.content_loader import ContentError
from typehero.paths import content_dir, profile_path
from typehero.tui.screens.menu import MenuScreen
from typehero.tui.state import AppState, load_app_state

_SYSTEM_COMMAND_KEYS: dict[str, tuple[str, str]] = {
    "Change the current theme": ("palette.theme", "palette.theme.help"),
    "Quit the application as soon as possible": ("palette.quit", "palette.quit.help"),
    "Show help for the focused widget and a summary of available keys": (
        "palette.keys",
        "palette.keys_show.help",
    ),
    "Hide the keys and widget help panel": ("palette.keys", "palette.keys_hide.help"),
    "Maximize the focused widget": ("palette.maximize", "palette.maximize.help"),
    "Minimize the widget and restore to normal size": ("palette.minimize", "palette.minimize.help"),
    "Save an SVG 'screenshot' of the current screen": (
        "palette.screenshot",
        "palette.screenshot.help",
    ),
}
"""Maps a built-in system command's English help text (unique per command) to the
i18n keys for its translated title and help, so the command palette localizes
without re-implementing Textual's stateful callbacks. The "Keys" command appears
in two mutually-exclusive states (show vs hide help panel), so both share the
`palette.keys` title but differ in help. The keys are verbatim copies of
Textual's strings; `tests/tui/test_app.py` guards them against drift on upgrade."""


class TypeHeroApp(App):
    """Root app. Holds the loaded `AppState` and starts on the menu."""

    TITLE = "typehero"

    def __init__(self, state: AppState) -> None:
        super().__init__()
        self.state = state

    def on_mount(self) -> None:
        self.push_screen(MenuScreen())
        for notice in self.state.startup_notices:
            self.notify(notice, severity="warning")

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Yield Textual's built-in palette commands with localized title/help.

        Each command's callback is preserved; only its display strings are swapped
        for the active UI locale. Unmapped commands pass through unchanged."""
        translator = self.state.translator
        locale = self.state.progress.ui_locale
        for command in super().get_system_commands(screen):
            keys = _SYSTEM_COMMAND_KEYS.get(command.help)
            if keys is None:
                yield command
                continue
            title_key, help_key = keys
            yield command._replace(
                title=translator.t(title_key, locale),
                help=translator.t(help_key, locale),
            )

    def action_command_palette(self) -> None:
        """Open the command palette with a localized search placeholder.

        Mirrors `App.action_command_palette` as of Textual 8.x; only the
        placeholder differs. Textual exposes no cleaner injection point for it,
        so the guard (`use_command_palette`, `CommandPalette.is_open`) and the
        `--command-palette` id must track the upstream method on a version bump."""
        if self.use_command_palette and not CommandPalette.is_open(self):
            placeholder = self.state.translator.t("palette.search", self.state.progress.ui_locale)
            self.push_screen(CommandPalette(placeholder=placeholder, id="--command-palette"))


def build_app(
    content_root: Path | None = None,
    profile_file: Path | None = None,
    today: date | None = None,
    clock: Callable[[], float] = time.monotonic,
    rng: random.Random | None = None,
) -> TypeHeroApp:
    """Construct a `TypeHeroApp`, defaulting to real content/profile/date."""
    state = load_app_state(
        content_root=content_root if content_root is not None else content_dir(),
        profile_file=profile_file if profile_file is not None else profile_path(),
        today=today if today is not None else date.today(),
        clock=clock,
        rng=rng if rng is not None else random.Random(),
    )
    return TypeHeroApp(state)


def main() -> None:
    """Console entry point (`typehero` / `python -m typehero`).

    Content/profile loading happens before the screen is taken over, so a
    malformed YAML file or missing content directory surfaces as a clean
    stderr message and a non-zero exit instead of a raw traceback.
    """
    try:
        app = build_app()
    except (ContentError, OSError) as exc:
        print(f"typehero: cannot start: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    app.run()
