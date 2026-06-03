"""Derived metrics for a typing session.

WPM uses the industry-standard 5-characters-per-word convention so results are
comparable across lessons and with external typing tests. Elapsed time runs
from the first to the last character keystroke.
"""

from __future__ import annotations

from dataclasses import dataclass

from typer.engine.keystroke import KeystrokeKind
from typer.engine.session import CharState, TypingSession

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


def compute_metrics(session: TypingSession) -> SessionMetrics:
    """Compute metrics from a (possibly incomplete) session."""
    char_keys = [k for k in session.keystrokes if k.kind is KeystrokeKind.CHAR]
    total = session.char_keystroke_count
    errors = session.error_count
    error_rate = errors / total if total else 0.0
    accuracy = 1.0 - error_rate
    correct_chars = sum(1 for st in session.char_states if st is CharState.CORRECT)

    elapsed = char_keys[-1].timestamp - char_keys[0].timestamp if len(char_keys) >= 2 else 0.0
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
