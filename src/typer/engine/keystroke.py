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
