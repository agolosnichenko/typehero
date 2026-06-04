"""Progress screen — speed/accuracy sparklines over benchmark history."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Sparkline


class ProgressScreen(Screen):
    """Two sparklines (speed, accuracy) built from the course's snapshots."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, course_id: str) -> None:
        super().__init__()
        self._course_id = course_id

    def _snapshots(self) -> list:
        return self.app.state.progress.benchmarks.get(self._course_id, [])

    def speed_series(self) -> list[float]:
        """Net WPM per benchmark snapshot, oldest first."""
        return [snap.net_wpm for snap in self._snapshots()]

    def accuracy_series(self) -> list[float]:
        """Accuracy percent per benchmark snapshot, oldest first."""
        return [snap.accuracy * 100 for snap in self._snapshots()]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Label("Speed (WPM)")
            yield Sparkline(self.speed_series() or [0], summary_function=max)
            yield Label("Accuracy (%)")
            yield Sparkline(self.accuracy_series() or [0], summary_function=max)
        yield Footer()
