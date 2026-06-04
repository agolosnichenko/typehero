"""Results screen — metrics and rewards for one attempt."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from typehero.domain.lesson import LessonOutcome
from typehero.domain.progress import BenchmarkKind
from typehero.gamification.rewards import RewardSummary


class ResultsScreen(Screen):
    """Renders the outcome of a lesson attempt; Enter/Esc returns to the menu."""

    BINDINGS = [("enter,escape", "to_menu", "Continue")]

    def __init__(
        self,
        outcome: LessonOutcome,
        summary: RewardSummary,
        final_course_id: str | None = None,
    ) -> None:
        super().__init__()
        self._outcome = outcome
        self._summary = summary
        self._final_course_id = final_course_id

    def summary_lines(self) -> list[str]:
        """Pure view-model: the lines shown to the player."""
        metrics = self._outcome.metrics
        summary = self._summary
        headline = "Lesson passed!" if summary.passed else "Not yet — try again"
        lines = [
            headline,
            f"WPM: {metrics.net_wpm:.0f}",
            f"Accuracy: {metrics.accuracy * 100:.0f}%",
            f"Errors: {metrics.errors}",
            f"XP earned: {summary.earned_xp}",
            f"Level: {summary.level}{' (up!)' if summary.leveled_up else ''}",
            f"Streak: {summary.streak}",
        ]
        for unlocked in summary.newly_unlocked:
            lines.append(f"Unlocked: {unlocked}")
        return lines

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("\n".join(self.summary_lines()))
        yield Footer()

    def action_to_menu(self) -> None:
        if self._final_course_id is not None:
            from typehero.tui.screens.benchmark import BenchmarkScreen

            self.app.switch_screen(
                BenchmarkScreen(course_id=self._final_course_id, kind=BenchmarkKind.FINAL)
            )
            return
        self.app.pop_screen()
