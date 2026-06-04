"""Main menu — lesson list and navigation (expanded in a later task)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header


class MenuScreen(Screen):
    """Placeholder menu; lesson list is added in Task 12."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
