"""The typing prompt widget — captures keystrokes and renders per-char state."""

from __future__ import annotations

import time
from collections.abc import Callable

from rich.text import Text
from textual import events
from textual.message import Message
from textual.widgets import Static

from typehero.engine.keystroke import Keystroke, KeystrokeKind
from typehero.engine.session import CharState, TypingSession

_STYLES = {
    CharState.PENDING: "dim",
    CharState.CORRECT: "green",
    CharState.ERROR: "red underline",
}


class TypingView(Static):
    """Renders a target string and drives a `TypingSession` from live keys."""

    can_focus = True

    class Finished(Message):
        """Posted when the target is fully typed."""

        def __init__(self, keystrokes: list[Keystroke]) -> None:
            super().__init__()
            self.keystrokes = keystrokes

    def __init__(self, target: str, clock: Callable[[], float] = time.monotonic) -> None:
        super().__init__()
        self._clock = clock
        self.session = TypingSession(target=target)
        self._keystrokes: list[Keystroke] = []
        self._finished = False

    def on_mount(self) -> None:
        self.focus()
        self._render_target()

    def on_paste(self, event: events.Paste) -> None:
        """Block paste so WPM cannot be gamed by pasting the target."""
        event.stop()

    def on_key(self, event: events.Key) -> None:
        if self._finished:
            return
        if event.key == "backspace":
            event.stop()
            event.prevent_default()
            self._apply(KeystrokeKind.BACKSPACE, None)
            return
        if event.is_printable and event.character is not None:
            event.stop()
            event.prevent_default()
            self._apply(KeystrokeKind.CHAR, event.character)

    def _apply(self, kind: KeystrokeKind, char: str | None) -> None:
        keystroke = Keystroke(kind=kind, char=char, timestamp=self._clock())
        self._keystrokes.append(keystroke)
        self.session.apply(keystroke)
        self._render_target()
        if self.session.is_complete:
            self._finished = True
            self.post_message(self.Finished(list(self._keystrokes)))

    def _render_target(self) -> None:
        text = Text()
        for index, char in enumerate(self.session.target):
            style = _STYLES[self.session.char_states[index]]
            if index == self.session.cursor:
                style = f"reverse {style}"
            text.append(char, style=style)
        self.update(text)
