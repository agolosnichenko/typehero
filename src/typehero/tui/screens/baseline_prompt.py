"""Modal asking whether to take a baseline benchmark before the first lesson."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class BaselinePrompt(ModalScreen[bool]):
    """Yes/Skip dialog; dismisses with `True` (take) or `False` (skip)."""

    BINDINGS = [("y", "take", "Yes"), ("s", "skip", "Skip")]

    def __init__(self, message: str, yes_label: str = "Yes", skip_label: str = "Skip") -> None:
        super().__init__()
        self._message = message
        self._yes_label = yes_label
        self._skip_label = skip_label

    def compose(self) -> ComposeResult:
        with Vertical(id="baseline-dialog"):
            yield Static(self._message)
            yield Button(self._yes_label, id="take", variant="primary")
            yield Button(self._skip_label, id="skip")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "take")

    def action_take(self) -> None:
        self.dismiss(True)

    def action_skip(self) -> None:
        self.dismiss(False)
