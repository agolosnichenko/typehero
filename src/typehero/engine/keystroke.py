"""Keystroke value types — the engine's only input."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KeystrokeKind(Enum):
    """Kind of a single keypress the engine understands."""

    CHAR = "char"
    BACKSPACE = "backspace"


@dataclass(frozen=True)
class Keystroke:
    """A single keypress with an injected timestamp (seconds).

    `char` is the typed character for `CHAR` keystrokes and `None` for
    `BACKSPACE`. `timestamp` is supplied by the caller so the engine stays
    deterministic and testable.
    """

    kind: KeystrokeKind
    char: str | None
    timestamp: float

    def __post_init__(self) -> None:
        if self.kind is KeystrokeKind.CHAR and self.char is None:
            raise ValueError("CHAR keystroke must have a non-None char")
        if self.kind is KeystrokeKind.BACKSPACE and self.char is not None:
            raise ValueError("BACKSPACE keystroke must have char=None")
