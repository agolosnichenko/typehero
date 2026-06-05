"""Progress screen — speed/accuracy sparklines plus a benchmark history table."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Label, Sparkline, Static

from typehero.tui.screens.base import AppScreen

if TYPE_CHECKING:
    from typehero.domain.progress import BenchmarkSnapshot


class ProgressScreen(AppScreen):
    """Sparklines (only with ≥2 snapshots) over a benchmark history table."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    DEFAULT_CSS = """
    ProgressScreen .metric-row {
        height: 1;
    }
    ProgressScreen .metric-label {
        width: 16;
    }
    ProgressScreen Sparkline {
        width: 1fr;
    }
    ProgressScreen #history {
        padding-top: 1;
    }
    """

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

    def history_rows(self) -> list[str]:
        """Aligned table lines (header then one per snapshot), oldest first."""
        snaps = self._snapshots()
        if not snaps:
            return []
        rows = [f"{'date':<10}  {'WPM':>4}  {'acc':>4}  {'err':>3}  kind"]
        rows.extend(
            f"{snap.date:<10}  {snap.net_wpm:>4.0f}  "
            f"{snap.accuracy * 100:>3.0f}%  {snap.errors:>3}  {snap.kind}"
            for snap in snaps
        )
        return rows

    def compose(self) -> ComposeResult:
        yield Header()
        snaps = self._snapshots()
        if not snaps:
            yield Label("No benchmarks yet — run a benchmark to start tracking progress.")
            yield Footer()
            return
        with Vertical():
            if len(snaps) >= 2:
                with Horizontal(classes="metric-row"):
                    yield Label("Speed (WPM)", classes="metric-label")
                    yield Sparkline(self.speed_series(), summary_function=max)
                with Horizontal(classes="metric-row"):
                    yield Label("Accuracy (%)", classes="metric-label")
                    yield Sparkline(self.accuracy_series(), summary_function=max)
            yield Static("\n".join(self.history_rows()), id="history")
        yield Footer()
