"""Typing session state — applies keystrokes to a target string."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from enum import Enum

from typer.engine.keystroke import Keystroke, KeystrokeKind


class CharState(Enum):
    """Per-character display/correctness state."""

    PENDING = "pending"
    CORRECT = "correct"
    ERROR = "error"


@dataclass
class TypingSession:
    """Mutable state of one typing attempt.

    Counts every error keystroke (including ones later fixed with backspace)
    so accuracy cannot be gamed by corrections. `char_keystroke_count` excludes
    keystrokes typed past the end of the target.
    """

    target: str
    cursor: int = 0
    char_states: list[CharState] = field(default_factory=list)
    keystrokes: list[Keystroke] = field(default_factory=list)
    error_count: int = 0
    char_keystroke_count: int = 0
    max_combo: int = 0
    _combo: int = field(default=0, init=False, repr=False)
    first_char_ts: float | None = field(default=None, init=False)
    last_char_ts: float | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.target = unicodedata.normalize("NFC", self.target)
        if not self.char_states:
            self.char_states = [CharState.PENDING] * len(self.target)

    @property
    def is_complete(self) -> bool:
        return self.cursor >= len(self.target)

    def apply(self, ks: Keystroke) -> None:
        """Apply one keystroke, mutating session state."""
        self.keystrokes.append(ks)
        if ks.kind is KeystrokeKind.BACKSPACE:
            self._apply_backspace()
            return
        if self.is_complete:
            return
        self.char_keystroke_count += 1
        if self.first_char_ts is None:
            self.first_char_ts = ks.timestamp
        self.last_char_ts = ks.timestamp
        expected = self.target[self.cursor]
        if ks.char == expected:
            self.char_states[self.cursor] = CharState.CORRECT
            self._combo += 1
            self.max_combo = max(self.max_combo, self._combo)
        else:
            self.char_states[self.cursor] = CharState.ERROR
            self.error_count += 1
            self._combo = 0
        self.cursor += 1

    def _apply_backspace(self) -> None:
        if self.cursor > 0:
            self.cursor -= 1
            self.char_states[self.cursor] = CharState.PENDING
