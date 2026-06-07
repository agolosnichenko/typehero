"""Main menu — lists the active course's lessons with lock/completion state."""

from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from typehero import __version__
from typehero.domain.benchmark import needs_baseline
from typehero.domain.course import Course, is_unlocked
from typehero.domain.lesson import Lesson
from typehero.domain.progress import BenchmarkKind
from typehero.localization import pick_locale
from typehero.tui.banner import BANNER
from typehero.tui.screens.base import AppScreen


@dataclass(frozen=True)
class MenuRow:
    """A lesson as shown in the menu."""

    lesson: Lesson
    unlocked: bool
    completed: bool


class MenuScreen(AppScreen):
    """A LazyVim-style dashboard: an ASCII wordmark and a progress tagline above
    the active course's lessons. Opens the selected unlocked lesson."""

    BINDINGS = [
        ("b", "benchmark", "Benchmark"),
        ("p", "progress", "Progress"),
        ("a", "achievements", "Achievements"),
        ("s", "settings", "Settings"),
        ("q", "app.quit", "Quit"),
    ]

    DEFAULT_CSS = """
    MenuScreen #banner {
        width: 100%;
        text-align: center;
        color: $primary;
        text-style: bold;
        padding-top: 1;
    }
    MenuScreen #tagline {
        width: 100%;
        text-align: center;
        color: $text-muted;
        padding-bottom: 1;
    }
    MenuScreen #lessons {
        height: 1fr;
        background: transparent;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(BANNER, id="banner")
        yield Static(self.dashboard_tagline(), id="tagline")
        yield ListView(*self._list_items(), id="lessons")
        yield Footer()

    def dashboard_tagline(self) -> str:
        """Pure view-model for the muted status line under the banner."""
        rows = self.lesson_rows()
        cleared = sum(1 for row in rows if row.completed)
        locale = self.app_state.progress.ui_locale
        template = self.app_state.translator.t("menu.tagline", locale)
        return template.format(version=__version__, cleared=cleared, total=len(rows))

    def on_screen_resume(self) -> None:
        """Rebuild the list whenever this screen is resumed, so a lesson cleared
        or a typing language switched while it was hidden is reflected: a freshly
        cleared lesson shows as completed and unlocks its successor."""
        lessons = self.query_one("#lessons", ListView)
        index = lessons.index
        lessons.clear()
        lessons.extend(self._list_items())
        lessons.index = index
        self.query_one("#tagline", Static).update(self.dashboard_tagline())
        self.refresh_bindings()

    @property
    def _course(self) -> Course:
        state = self.app_state
        return state.courses[state.active_course_id]

    def lesson_rows(self) -> list[MenuRow]:
        """Pure view-model: each lesson with its unlock and completion flags."""
        course = self._course
        completed = set(self.app_state.progress.completed_lessons)
        rows: list[MenuRow] = []
        for lesson in course.lessons:
            rows.append(
                MenuRow(
                    lesson=lesson,
                    unlocked=is_unlocked(course, lesson.id, completed),
                    completed=lesson.id in completed,
                )
            )
        return rows

    def _list_items(self) -> list[ListItem]:
        locale = self.app_state.progress.ui_locale
        translator = self.app_state.translator
        items: list[ListItem] = []
        for row in self.lesson_rows():
            title = pick_locale(row.lesson.title, locale)
            if row.completed:
                suffix = translator.t("menu.completed", locale)
            elif not row.unlocked:
                suffix = translator.t("menu.locked", locale)
            else:
                suffix = ""
            label = f"{title}  ({suffix})" if suffix else title
            item = ListItem(Label(label))
            item.disabled = not row.unlocked
            items.append(item)
        return items

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index
        if index is None:
            return
        row = self.lesson_rows()[index]
        if not row.unlocked:
            return
        course = self._course
        if row.lesson.id == course.lessons[0].id and needs_baseline(
            self.app_state.progress, course.id
        ):
            from typehero.tui.screens.baseline_prompt import BaselinePrompt

            locale = self.app_state.progress.ui_locale
            translator = self.app_state.translator
            message = translator.t("benchmark.baseline_prompt", locale)
            self.app.push_screen(
                BaselinePrompt(
                    message,
                    yes_label=translator.t("baseline.yes", locale),
                    skip_label=translator.t("baseline.skip", locale),
                ),
                lambda take: self._after_baseline_choice(bool(take), row.lesson),
            )
            return
        self._open_lesson(row.lesson)

    def _after_baseline_choice(self, take: bool, lesson: Lesson) -> None:
        from typehero.tui.screens.benchmark import BenchmarkScreen

        if take:
            self.app.push_screen(
                BenchmarkScreen(course_id=self._course.id, kind=BenchmarkKind.BASELINE)
            )
        else:
            self.app_state.progress.mark_baseline_skipped(self._course.id)
            self.save_profile()
            self._open_lesson(lesson)

    def _open_lesson(self, lesson: Lesson) -> None:
        from typehero.tui.screens.lesson import LessonScreen

        self.app.push_screen(LessonScreen(course_id=self._course.id, lesson=lesson))

    def action_benchmark(self) -> None:
        from typehero.tui.screens.benchmark import BenchmarkScreen

        self.app.push_screen(BenchmarkScreen(course_id=self._course.id))

    def action_progress(self) -> None:
        from typehero.tui.screens.progress import ProgressScreen

        self.app.push_screen(ProgressScreen(course_id=self._course.id))

    def action_achievements(self) -> None:
        from typehero.tui.screens.achievements import AchievementsScreen

        self.app.push_screen(AchievementsScreen())

    def action_settings(self) -> None:
        """Open the settings screen."""
        from typehero.tui.screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())
