"""Progress screen — speed/accuracy sparklines over benchmark history."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Label, Sparkline

from typehero.tui.screens.base import AppScreen

if TYPE_CHECKING:
    from typehero.domain.progress import BenchmarkSnapshot


class ProgressScreen(AppScreen):
    """Two sparklines (speed, accuracy) built from the course's snapshots."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, course_id: str) -> None:
        super().__init__()
        self._course_id = course_id

    def _snapshots(self) -> list[BenchmarkSnapshot]:
        return self.app_state.progress.benchmarks.get(self._course_id, [])

    def speed_series(self) -> list[float]:
        """Net WPM per benchmark snapshot, oldest first."""
        return [snap.net_wpm for snap in self._snapshots()]

    def accuracy_series(self) -> list[float]:
        """Accuracy percent per benchmark snapshot, oldest first."""
        return [snap.accuracy * 100 for snap in self._snapshots()]

    def compose(self) -> ComposeResult:
        yield Header()
        speed = self.speed_series()
        if not speed:
            yield Label("No benchmarks yet — run a benchmark to start tracking progress.")
        else:
            with Horizontal():
                yield Label("Speed (WPM)")
                yield Sparkline(speed, summary_function=max)
                yield Label("Accuracy (%)")
                yield Sparkline(self.accuracy_series(), summary_function=max)
        yield Footer()
