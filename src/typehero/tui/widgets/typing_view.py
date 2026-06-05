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

    DEFAULT_CSS = """
    TypingView {
        width: 1fr;
        max-width: 64;
        height: auto;
        padding: 1 2;
    }
    """

    can_focus = True

    class Finished(Message):
        """Posted when the target is fully typed.

        Carries both the raw `keystrokes` (for the headless `run_lesson`
        boundary) and the already-applied `session`, so consumers that only
        need metrics don't replay the keystrokes into a second session.
        """

        def __init__(self, keystrokes: list[Keystroke], session: TypingSession) -> None:
            super().__init__()
            self.keystrokes = keystrokes
            self.session = session

    class CursorMoved(Message):
        """Posted whenever the cursor moves, carrying the next char to type.

        `char` is the character now under the cursor, or None when the target
        is fully typed. Consumers (e.g. the finger map) use it to highlight the
        next key.
        """

        def __init__(self, char: str | None) -> None:
            super().__init__()
            self.char = char

    def __init__(self, target: str, clock: Callable[[], float] = time.monotonic) -> None:
        super().__init__()
        self._clock = clock
        self.session = TypingSession(target=target)
        self._finished = False

    @property
    def current_char(self) -> str | None:
        """The character under the cursor, or None when complete."""
        if self.session.is_complete:
            return None
        return self.session.target[self.session.cursor]

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
        self.session.apply(keystroke)
        self._render_target()
        self.post_message(self.CursorMoved(self.current_char))
        if self.session.is_complete:
            self._finished = True
            self.post_message(self.Finished(list(self.session.keystrokes), self.session))

    def _render_target(self) -> None:
        text = Text()
        for index, char in enumerate(self.session.target):
            style = _STYLES[self.session.char_states[index]]
            if index == self.session.cursor:
                style = f"reverse {style}"
            text.append(char, style=style)
        self.update(text)
