"""Modal asking whether to take a baseline benchmark before the first lesson."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class BaselinePrompt(ModalScreen[bool]):
    """Yes/Skip dialog; dismisses with `True` (take) or `False` (skip)."""

    BINDINGS = [("y", "take", "Yes"), ("s", "skip", "Skip")]

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="baseline-dialog"):
            yield Static(self._message)
            yield Button("Yes", id="take", variant="primary")
            yield Button("Skip", id="skip")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "take")

    def action_take(self) -> None:
        self.dismiss(True)

    def action_skip(self) -> None:
        self.dismiss(False)
