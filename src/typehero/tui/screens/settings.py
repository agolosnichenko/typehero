"""Settings screen — switch UI language and typing language."""

from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.widgets import Footer, Header, Label, RadioButton, RadioSet

from typehero.tui.screens.base import AppScreen


@dataclass(frozen=True)
class LanguageChoice:
    """One selectable language on one axis."""

    code: str
    label: str
    current: bool


@dataclass(frozen=True)
class SettingsView:
    """The two language axes shown on the settings screen."""

    ui: list[LanguageChoice]
    typing: list[LanguageChoice]


class SettingsScreen(AppScreen):
    """Switch the interface language and the typing-language course."""

    BINDINGS = [("escape", "app.pop_screen", "Back")]

    _ui_codes: list[str]
    _typing_codes: list[str]

    def settings_view(self) -> SettingsView:
        """Pure view-model: both axes with localized labels and the current flag."""
        state = self.app_state
        locale = state.progress.ui_locale
        ui = [
            LanguageChoice(
                code=code,
                label=state.translator.t(f"language.{code}", locale),
                current=code == locale,
            )
            for code in sorted(state.translator.tables)
        ]
        typing = [
            LanguageChoice(
                code=code,
                label=state.translator.t(f"language.{code}", locale),
                current=code == state.progress.active_course_id,
            )
            for code in sorted(state.courses)
        ]
        return SettingsView(ui=ui, typing=typing)

    def compose(self) -> ComposeResult:
        view = self.settings_view()
        self._ui_codes = [choice.code for choice in view.ui]
        self._typing_codes = [choice.code for choice in view.typing]
        locale = self.app_state.progress.ui_locale
        translator = self.app_state.translator
        yield Header()
        yield Label(translator.t("settings.ui_language", locale))
        yield RadioSet(
            *(RadioButton(choice.label, value=choice.current) for choice in view.ui),
            id="ui-language",
        )
        yield Label(translator.t("settings.typing_language", locale))
        yield RadioSet(
            *(RadioButton(choice.label, value=choice.current) for choice in view.typing),
            id="typing-language",
        )
        yield Footer()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Apply a language choice, persist it, and confirm with a toast."""
        progress = self.app_state.progress
        if event.radio_set.id == "ui-language":
            choice = self._ui_codes[event.index]
            if choice == progress.ui_locale:
                return
            progress.ui_locale = choice
        elif event.radio_set.id == "typing-language":
            choice = self._typing_codes[event.index]
            if choice == progress.active_course_id:
                return
            progress.active_course_id = choice
        else:
            return
        self.save_profile()
        self.notify(self.app_state.translator.t("settings.saved", progress.ui_locale))
