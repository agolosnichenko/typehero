"""Benchmark screen — records a comparable snapshot, no XP, no fail, no streak."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Static

from typehero.domain.benchmark import snapshot_from_metrics
from typehero.domain.ids import CourseId
from typehero.domain.progress import BenchmarkKind
from typehero.engine.metrics import compute_metrics
from typehero.tui.screens.base import AppScreen
from typehero.tui.widgets.typing_view import TypingView


class BenchmarkScreen(AppScreen):
    """Types the course benchmark text and saves one snapshot."""

    DEFAULT_CSS = """
    BenchmarkScreen {
        align: center middle;
    }
    BenchmarkScreen .intro {
        width: 1fr;
        max-width: 64;
        text-align: center;
        padding-bottom: 1;
    }
    """

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, course_id: CourseId, kind: BenchmarkKind = BenchmarkKind.INTERIM) -> None:
        super().__init__()
        self._course_id = course_id
        self._kind = kind

    def compose(self) -> ComposeResult:
        state = self.app_state
        course = state.courses[self._course_id]
        locale = state.progress.ui_locale
        yield Header()
        yield Static(state.translator.t("benchmark.intro", locale), classes="intro")
        yield TypingView(course.benchmark_text, clock=state.clock)
        yield Footer()

    def on_typing_view_finished(self, event: TypingView.Finished) -> None:
        state = self.app_state
        metrics = compute_metrics(event.session)
        snapshot = snapshot_from_metrics(state.today.isoformat(), metrics, self._kind)
        state.progress.add_benchmark(self._course_id, snapshot)
        self.save_profile()
        self.app.pop_screen()
