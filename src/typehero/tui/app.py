"""The Textual application shell: owns AppState and screen navigation."""

from __future__ import annotations

import random
import sys
import time
from collections.abc import Callable
from datetime import date
from pathlib import Path

from textual.app import App

from typehero.content_loader import ContentError
from typehero.paths import content_dir, profile_path
from typehero.tui.screens.menu import MenuScreen
from typehero.tui.state import AppState, load_app_state


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
