"""Headless runner that drives one typing attempt end to end.

This is the boundary the TUI calls: it owns no terminal logic, only the
engine + domain wiring, so the full loop is unit-testable.
"""

from __future__ import annotations

from typehero.domain.lesson import Lesson, LessonOutcome, evaluate
from typehero.engine.keystroke import Keystroke
from typehero.engine.metrics import compute_metrics
from typehero.engine.session import TypingSession


def run_lesson(target: str, lesson: Lesson, keystrokes: list[Keystroke]) -> LessonOutcome:
    """Replay `keystrokes` against `target` and evaluate against `lesson`."""
    session = TypingSession(target=target)
    for keystroke in keystrokes:
        session.apply(keystroke)
    metrics = compute_metrics(session)
    result = evaluate(lesson.criteria, metrics)
    return LessonOutcome(metrics=metrics, result=result)
