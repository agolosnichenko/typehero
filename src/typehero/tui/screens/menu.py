"""Main menu — lists the active course's lessons with lock/completion state."""

from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Label, ListItem, ListView

from typehero.domain.benchmark import needs_baseline
from typehero.domain.course import Course, is_unlocked
from typehero.domain.lesson import Lesson
from typehero.localization import pick_locale
from typehero.tui.screens.base import AppScreen


@dataclass(frozen=True)
class MenuRow:
    """A lesson as shown in the menu."""

    lesson: Lesson
    unlocked: bool
    completed: bool


class MenuScreen(AppScreen):
    """Lists lessons; opens the selected unlocked lesson."""

    BINDINGS = [
        ("b", "benchmark", "Benchmark"),
        ("p", "progress", "Progress"),
        ("a", "achievements", "Achievements"),
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(*self._list_items(), id="lessons")
        yield Footer()

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
            message = self.app_state.translator.t("benchmark.baseline_prompt", locale)
            self.app.push_screen(
                BaselinePrompt(message),
                lambda take: self._after_baseline_choice(bool(take), row.lesson),
            )
            return
        self._open_lesson(row.lesson)

    def _after_baseline_choice(self, take: bool, lesson: Lesson) -> None:
        from typehero.tui.screens.benchmark import BenchmarkScreen

        if take:
            self.app.push_screen(BenchmarkScreen(course_id=self._course.id, kind="baseline"))
        else:
            self.app_state.progress.skipped_baselines.append(self._course.id)
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
