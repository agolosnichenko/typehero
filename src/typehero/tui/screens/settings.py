"""Settings screen — switch UI language and typing language."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Label, RadioButton, RadioSet

from typehero.domain.ids import CourseId
from typehero.tui.screens.base import AppScreen

_logger = logging.getLogger(__name__)

_UI_LANGUAGE_ID = "ui-language"
_TYPING_LANGUAGE_ID = "typing-language"


@dataclass(frozen=True)
class LanguageChoice:
    """One selectable language on one axis."""

    code: str
    label: str


@dataclass(frozen=True)
class LanguageAxis:
    """The options on one language axis and the currently selected code."""

    choices: list[LanguageChoice]
    selected: str


@dataclass(frozen=True)
class SettingsView:
    """The two language axes shown on the settings screen."""

    ui: LanguageAxis
    typing: LanguageAxis


class SettingsScreen(AppScreen):
    """Switch the interface language and the typing-language course."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    _ui_codes: list[str]
    _typing_codes: list[str]

    def settings_view(self) -> SettingsView:
        """Pure view-model: both axes with localized labels and the selected code."""
        state = self.app_state
        ui = [
            LanguageChoice(code=code, label=self.t(f"language.{code}"))
            for code in sorted(state.translator.tables)
        ]
        typing = [
            LanguageChoice(code=code, label=self.t(f"language.{code}"))
            for code in sorted(state.courses)
        ]
        return SettingsView(
            ui=LanguageAxis(choices=ui, selected=state.progress.ui_locale),
            typing=LanguageAxis(choices=typing, selected=state.progress.active_course_id),
        )

    def _radio_set(self, axis: LanguageAxis, axis_id: str) -> RadioSet:
        return RadioSet(
            *(
                RadioButton(choice.label, value=choice.code == axis.selected)
                for choice in axis.choices
            ),
            id=axis_id,
        )

    def compose(self) -> ComposeResult:
        view = self.settings_view()
        self._ui_codes = [choice.code for choice in view.ui.choices]
        self._typing_codes = [choice.code for choice in view.typing.choices]
        yield Header()
        yield Label(self.t("settings.title"))
        yield Label(self.t("settings.ui_language"))
        yield self._radio_set(view.ui, _UI_LANGUAGE_ID)
        yield Label(self.t("settings.typing_language"))
        yield self._radio_set(view.typing, _TYPING_LANGUAGE_ID)
        yield Footer()

    async def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Apply a language choice, persist it, confirm with a toast, and re-localize.

        A choice that does not move, an out-of-range index, or a failed save all
        leave the profile untouched and stay silent; a UI-language switch also
        recomposes so the screen's own labels render in the new language.
        """
        progress = self.app_state.progress
        is_ui = event.radio_set.id == _UI_LANGUAGE_ID
        if is_ui:
            codes, current = self._ui_codes, progress.ui_locale
        elif event.radio_set.id == _TYPING_LANGUAGE_ID:
            codes, current = self._typing_codes, progress.active_course_id
        else:
            _logger.warning("Unhandled RadioSet id %r in settings", event.radio_set.id)
            return
        if not 0 <= event.index < len(codes) or codes[event.index] == current:
            return
        choice = codes[event.index]
        if is_ui:
            progress.ui_locale = choice
        else:
            progress.active_course_id = CourseId(choice)
        if not self.save_profile():
            if is_ui:
                progress.ui_locale = current
            else:
                progress.active_course_id = CourseId(current)
            return
        self.notify(self.t("settings.saved"))
        if is_ui:
            await self.recompose()
