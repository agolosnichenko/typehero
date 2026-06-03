"""Headless runner that drives one typing attempt end to end.

This is the boundary the TUI calls: it owns no terminal logic, only the
engine + domain wiring, so the full loop is unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass

from typer.domain.lesson import Lesson, LessonResult, evaluate
from typer.engine.keystroke import Keystroke
from typer.engine.metrics import SessionMetrics, compute_metrics
from typer.engine.session import TypingSession


@dataclass(frozen=True)
class LessonOutcome:
    """Metrics plus pass/fail for one completed attempt."""

    metrics: SessionMetrics
    result: LessonResult


def run_lesson(target: str, lesson: Lesson, keystrokes: list[Keystroke]) -> LessonOutcome:
    """Replay `keystrokes` against `target` and evaluate against `lesson`."""
    session = TypingSession(target=target)
    for keystroke in keystrokes:
        session.apply(keystroke)
    metrics = compute_metrics(session)
    result = evaluate(lesson.criteria, metrics)
    return LessonOutcome(metrics=metrics, result=result)
