"""Results screen — metrics and rewards for one attempt."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Static

from typehero.domain.ids import CourseId
from typehero.domain.lesson import LessonOutcome
from typehero.domain.progress import BenchmarkKind
from typehero.gamification.rewards import RewardSummary
from typehero.localization import Translator
from typehero.tui.screens.base import AppScreen


class ResultsScreen(AppScreen):
    """Renders the outcome of a lesson attempt; Enter/Esc returns to the menu."""

    BINDINGS = [("enter,escape", "to_menu", "Continue")]

    def __init__(
        self,
        outcome: LessonOutcome,
        summary: RewardSummary,
        final_course_id: CourseId | None = None,
    ) -> None:
        super().__init__()
        self._outcome = outcome
        self._summary = summary
        self._final_course_id = final_course_id

    def summary_lines(self, translator: Translator, locale: str) -> list[str]:
        """Pure view-model: the lines shown to the player, localized to `locale`.

        The translator is injected rather than read from the app so the lines
        stay unit-testable without a running TUI."""
        metrics = self._outcome.metrics
        summary = self._summary

        def t(key: str) -> str:
            return translator.t(key, locale)

        headline = t("results.passed") if summary.passed else t("results.failed")
        level = f"{summary.level}"
        if summary.leveled_up:
            level = f"{level} ({t('results.level_up')})"
        lines = [
            headline,
            f"{t('results.wpm')}: {metrics.net_wpm:.0f}",
            f"{t('results.accuracy')}: {metrics.accuracy * 100:.0f}%",
            f"{t('results.errors')}: {metrics.errors}",
            f"{t('results.xp_earned')}: {summary.earned_xp}",
            f"{t('results.level')}: {level}",
            f"{t('results.streak')}: {summary.streak}",
        ]
        for unlocked in summary.newly_unlocked:
            lines.append(f"{t('results.unlocked')}: {unlocked}")
        return lines

    def compose(self) -> ComposeResult:
        translator = self.app_state.translator
        locale = self.app_state.progress.ui_locale
        yield Header()
        yield Static("\n".join(self.summary_lines(translator, locale)))
        yield Footer()

    def action_to_menu(self) -> None:
        if self._final_course_id is not None:
            from typehero.tui.screens.benchmark import BenchmarkScreen

            self.app.switch_screen(
                BenchmarkScreen(course_id=self._final_course_id, kind=BenchmarkKind.FINAL)
            )
            return
        self.app.pop_screen()
