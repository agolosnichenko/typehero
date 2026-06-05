"""Lesson screen — drives one attempt and applies its rewards."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Center
from textual.widgets import Footer, Header

from typehero.domain.benchmark import has_final, is_final_lesson
from typehero.domain.course import index_of
from typehero.domain.generators import lesson_target
from typehero.domain.ids import CourseId
from typehero.domain.lesson import Lesson
from typehero.gamification.rewards import apply_lesson_outcome
from typehero.localization import pick_locale
from typehero.play import run_lesson
from typehero.tui.keyboard_layout import layout_for
from typehero.tui.lesson_guide import select_principle
from typehero.tui.screens.base import AppScreen
from typehero.tui.widgets.finger_map import FingerMap
from typehero.tui.widgets.lesson_guide import LessonGuide
from typehero.tui.widgets.live_stats import LiveStats
from typehero.tui.widgets.typing_view import TypingView

if TYPE_CHECKING:
    from typehero.tui.state import AppState


class LessonScreen(AppScreen):
    """Hosts the typing widget and routes its result to rewards + results."""

    DEFAULT_CSS = """
    LessonScreen {
        align: center middle;
    }
    """

    BINDINGS = [("escape", "app.pop_screen", "Abandon")]

    def __init__(self, course_id: CourseId, lesson: Lesson) -> None:
        super().__init__()
        self._course_id = course_id
        self._lesson = lesson
        self._target = ""
        self._aborted = False

    def compose(self) -> ComposeResult:
        state = self.app_state
        try:
            layout = layout_for(state.courses[self._course_id].layout)
            self._target = lesson_target(
                self._lesson, resources=state.resources[self._course_id], rng=state.rng
            )
            tip, principle = self._resolve_guide(state)
        except (ValueError, KeyError) as exc:
            self.notify(f"This lesson can't start: {exc}", severity="error")
            self._aborted = True
            yield Header()
            yield Footer()
            return
        yield Header()
        if tip is not None or principle is not None:
            with Center():
                yield LessonGuide(tip=tip, principle=principle or "")
        with Center():
            yield LiveStats()
        with Center():
            yield TypingView(self._target, clock=state.clock)
        with Center():
            yield FingerMap(layout)
        yield Footer()

    def _resolve_guide(self, state: AppState) -> tuple[str | None, str | None]:
        """Resolve the localized tip and principle for this lesson.

        Runs inside `compose`'s guarded setup so a malformed tip or an
        unresolvable principle aborts the lesson cleanly instead of crashing
        the screen with an uncaught error.
        """
        locale = state.progress.ui_locale
        index = index_of(state.courses[self._course_id], self._lesson.id)
        tip = pick_locale(self._lesson.tip, locale) if self._lesson.tip else None
        principle = (
            pick_locale(select_principle(state.principles, index), locale)
            if state.principles
            else None
        )
        return tip, principle

    def on_mount(self) -> None:
        # Pop a lesson that could not be built only once it is fully mounted;
        # popping from compose deadlocks the still-settling screen stack.
        if self._aborted:
            self.app.pop_screen()

    def on_typing_view_cursor_moved(self, event: TypingView.CursorMoved) -> None:
        self.query_one(FingerMap).highlight(event.char)

    def on_typing_view_progress(self, event: TypingView.Progress) -> None:
        self.query_one(LiveStats).update_stats(event.net_wpm, event.errors)

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
        course = state.courses[self._course_id]
        due_final = (
            outcome.result.passed
            and is_final_lesson(course, self._lesson.id)
            and not has_final(state.progress, self._course_id)
        )
        self.app.switch_screen(
            ResultsScreen(
                outcome=outcome,
                summary=summary,
                final_course_id=self._course_id if due_final else None,
            )
        )
