"""Main menu — lists the active course's lessons with lock/completion state."""

from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from typehero.domain.course import Course, is_unlocked
from typehero.domain.lesson import Lesson
from typehero.localization import pick_locale


@dataclass(frozen=True)
class MenuRow:
    """A lesson as shown in the menu."""

    lesson: Lesson
    unlocked: bool
    completed: bool


class MenuScreen(Screen):
    """Lists lessons; opens the selected unlocked lesson."""

    BINDINGS = [("q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(*self._list_items(), id="lessons")
        yield Footer()

    @property
    def _course(self) -> Course:
        state = self.app.state
        return state.courses["en"]

    def lesson_rows(self) -> list[MenuRow]:
        """Pure view-model: each lesson with its unlock and completion flags."""
        course = self._course
        completed = set(self.app.state.progress.completed_lessons)
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
        locale = self.app.state.progress.ui_locale
        translator = self.app.state.translator
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
        from typehero.tui.screens.lesson import LessonScreen

        index = event.list_view.index
        if index is None:
            return
        row = self.lesson_rows()[index]
        if row.unlocked:
            self.app.push_screen(LessonScreen(course_id=self._course.id, lesson=row.lesson))
