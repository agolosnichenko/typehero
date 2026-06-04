"""Derived metrics for a typing session.

WPM uses the industry-standard 5-characters-per-word convention so results are
comparable across lessons and with external typing tests. Elapsed time runs
from the first to the last accepted character keystroke (keystrokes typed past
the end of the target are ignored).
"""

from __future__ import annotations

from dataclasses import dataclass

from typehero.engine.session import CharState, TypingSession

_CHARS_PER_WORD = 5


@dataclass(frozen=True)
class SessionMetrics:
    """Immutable snapshot of one session's performance."""

    errors: int
    error_rate: float
    accuracy: float
    net_wpm: float
    raw_wpm: float
    elapsed_seconds: float
    max_combo: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.error_rate <= 1.0:
            raise ValueError(f"error_rate must be in [0, 1], got {self.error_rate}")
        if not 0.0 <= self.accuracy <= 1.0:
            raise ValueError(f"accuracy must be in [0, 1], got {self.accuracy}")
        negatives = {
            "errors": self.errors,
            "net_wpm": self.net_wpm,
            "raw_wpm": self.raw_wpm,
            "elapsed_seconds": self.elapsed_seconds,
            "max_combo": self.max_combo,
        }
        for name, value in negatives.items():
            if value < 0:
                raise ValueError(f"{name} must be non-negative, got {value}")


def compute_metrics(session: TypingSession) -> SessionMetrics:
    """Compute metrics from a (possibly incomplete) session.

    Sessions with fewer than two accepted character keystrokes report an
    elapsed time of 0.0 (and therefore 0 WPM).
    """
    total = session.char_keystroke_count
    errors = session.error_count
    error_rate = errors / total if total else 0.0
    accuracy = 1.0 - error_rate
    correct_chars = sum(1 for st in session.char_states if st is CharState.CORRECT)

    elapsed = (
        session.last_char_ts - session.first_char_ts
        if session.char_keystroke_count >= 2
        and session.first_char_ts is not None
        and session.last_char_ts is not None
        else 0.0
    )
    minutes = elapsed / 60.0
    net_wpm = (correct_chars / _CHARS_PER_WORD) / minutes if minutes > 0 else 0.0
    raw_wpm = (total / _CHARS_PER_WORD) / minutes if minutes > 0 else 0.0

    return SessionMetrics(
        errors=errors,
        error_rate=error_rate,
        accuracy=accuracy,
        net_wpm=net_wpm,
        raw_wpm=raw_wpm,
        elapsed_seconds=elapsed,
        max_combo=session.max_combo,
    )
