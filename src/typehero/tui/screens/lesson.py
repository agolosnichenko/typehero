"""Lesson screen — drives one attempt and applies its rewards."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header

if TYPE_CHECKING:
    from typehero.tui.app import TypeHeroApp

from typehero.domain.lesson import Lesson, lesson_target
from typehero.gamification.rewards import apply_lesson_outcome
from typehero.play import run_lesson
from typehero.tui.widgets.typing_view import TypingView


class LessonScreen(Screen):
    """Hosts the typing widget and routes its result to rewards + results."""

    BINDINGS = [("escape", "app.pop_screen", "Abandon")]

    def __init__(self, course_id: str, lesson: Lesson) -> None:
        super().__init__()
        self._course_id = course_id
        self._lesson = lesson
        self._target = lesson_target(lesson)

    def compose(self) -> ComposeResult:
        yield Header()
        yield TypingView(self._target, clock=cast("TypeHeroApp", self.app).state.clock)
        yield Footer()

    def on_typing_view_finished(self, event: TypingView.Finished) -> None:
        from typehero.tui.screens.results import ResultsScreen

        state = cast("TypeHeroApp", self.app).state
        outcome = run_lesson(self._target, self._lesson, event.keystrokes)
        summary = apply_lesson_outcome(
            state.progress,
            self._lesson,
            outcome,
            achievements=state.achievements,
            today=state.today,
        )
        state.save()
        self.app.switch_screen(ResultsScreen(outcome=outcome, summary=summary))
