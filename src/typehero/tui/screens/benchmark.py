"""Benchmark screen — records a comparable snapshot, no XP, no fail, no streak."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from typehero.domain.benchmark import snapshot_from_metrics
from typehero.engine.metrics import compute_metrics
from typehero.engine.session import TypingSession
from typehero.tui.widgets.typing_view import TypingView


class BenchmarkScreen(Screen):
    """Types the course benchmark text and saves one snapshot."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, course_id: str) -> None:
        super().__init__()
        self._course_id = course_id

    def compose(self) -> ComposeResult:
        state = self.app.state
        course = state.courses[self._course_id]
        locale = state.progress.ui_locale
        yield Header()
        yield Static(state.translator.t("benchmark.intro", locale))
        yield TypingView(course.benchmark_text, clock=state.clock)
        yield Footer()

    def on_typing_view_finished(self, event: TypingView.Finished) -> None:
        state = self.app.state
        course = state.courses[self._course_id]
        session = TypingSession(target=course.benchmark_text)
        for keystroke in event.keystrokes:
            session.apply(keystroke)
        metrics = compute_metrics(session)
        snapshot = snapshot_from_metrics(state.today.isoformat(), metrics)
        state.progress.add_benchmark(self._course_id, snapshot)
        state.save()
        self.app.pop_screen()
