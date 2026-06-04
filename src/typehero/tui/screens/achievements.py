"""Achievements screen — every badge with its locked/unlocked state."""

from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Label, ListItem, ListView

from typehero.localization import pick_locale
from typehero.tui.screens.base import AppScreen


@dataclass(frozen=True)
class AchievementRow:
    """An achievement as shown to the player."""

    id: str
    title: str
    desc: str
    unlocked: bool


class AchievementsScreen(AppScreen):
    """Lists achievements with localized text and unlock state."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def achievement_rows(self) -> list[AchievementRow]:
        """Pure view-model: each achievement with localized text + unlock flag."""
        state = self.app_state
        locale = state.progress.ui_locale
        unlocked = set(state.progress.unlocked_achievements)
        rows: list[AchievementRow] = []
        for achievement in state.achievements:
            rows.append(
                AchievementRow(
                    id=achievement.id,
                    title=pick_locale(achievement.title, locale),
                    desc=pick_locale(achievement.desc, locale),
                    unlocked=achievement.id in unlocked,
                )
            )
        return rows

    def compose(self) -> ComposeResult:
        yield Header()
        items = []
        for row in self.achievement_rows():
            mark = "✓" if row.unlocked else "🔒"
            items.append(ListItem(Label(f"{mark} {row.title} — {row.desc}")))
        yield ListView(*items)
        yield Footer()
