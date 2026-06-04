"""Lesson screen — drives one attempt and applies its rewards."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Footer, Header

from typehero.domain.lesson import Lesson, lesson_target
from typehero.gamification.rewards import apply_lesson_outcome
from typehero.play import run_lesson
from typehero.tui.screens.base import AppScreen
from typehero.tui.widgets.typing_view import TypingView


class LessonScreen(AppScreen):
    """Hosts the typing widget and routes its result to rewards + results."""

    BINDINGS = [("escape", "app.pop_screen", "Abandon")]

    def __init__(self, course_id: str, lesson: Lesson) -> None:
        super().__init__()
        self._course_id = course_id
        self._lesson = lesson
        self._target = lesson_target(lesson)

    def compose(self) -> ComposeResult:
        yield Header()
        yield TypingView(self._target, clock=self.app_state.clock)
        yield Footer()

    def on_typing_view_finished(self, event: TypingView.Finished) -> None:
        from typehero.tui.screens.results import ResultsScreen

        state = self.app_state
        outcome = run_lesson(self._target, self._lesson, event.keystrokes)
        summary = apply_lesson_outcome(
            state.progress,
            self._lesson,
            outcome,
            achievements=state.achievements,
            today=state.today,
        )
        self.save_profile()
        self.app.switch_screen(ResultsScreen(outcome=outcome, summary=summary))
