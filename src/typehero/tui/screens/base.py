"""Shared base screen with typed access to the running app's state."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, cast

from textual.binding import ActiveBinding
from textual.screen import Screen

if TYPE_CHECKING:
    from typehero.tui.app import TypeHeroApp
    from typehero.tui.state import AppState

_FOOTER_I18N: dict[str, str] = {
    "Benchmark": "footer.benchmark",
    "Progress": "footer.progress",
    "Achievements": "footer.achievements",
    "Settings": "footer.settings",
    "Quit": "footer.quit",
    "Back": "footer.back",
    "Continue": "footer.continue",
    "Abandon": "footer.abandon",
    "Yes": "footer.yes",
    "Skip": "footer.skip",
    "palette": "footer.palette",
}
"""Maps a binding's English description (its `BINDINGS` text and en.yaml value)
to the i18n key used to translate the footer label for the current UI locale."""


class AppScreen(Screen):
    """A `Screen` that exposes the app's `AppState` without a per-call cast."""

    @property
    def app_state(self) -> AppState:
        """The running app's shared state."""
        return cast("TypeHeroApp", self.app).state

    @property
    def active_bindings(self) -> dict[str, ActiveBinding]:
        """Footer bindings with descriptions translated to the current UI locale.

        `BINDINGS` descriptions are static class literals fixed at import time, so
        the footer would otherwise always render English. The `Footer` reads this
        property on every (re)compose, so translating here keeps the labels in
        sync with the active locale without mutating the static bindings. Unmapped
        descriptions pass through unchanged."""
        bindings = super().active_bindings
        translator = self.app_state.translator
        locale = self.app_state.progress.ui_locale
        translated: dict[str, ActiveBinding] = {}
        for key, active in bindings.items():
            i18n_key = _FOOTER_I18N.get(active.binding.description)
            if i18n_key is None:
                translated[key] = active
                continue
            binding = replace(active.binding, description=translator.t(i18n_key, locale))
            translated[key] = active._replace(binding=binding)
        return translated

    def save_profile(self) -> bool:
        """Persist the profile, surfacing a write failure as a toast.

        A failed save would otherwise raise out of an event handler and tear
        down the TUI; here the player is told and keeps their session. Returns
        whether the save succeeded, so callers can avoid reporting success or
        can roll back an in-memory change that did not reach disk.
        """
        try:
            self.app_state.save()
        except OSError as exc:
            self.notify(f"Could not save your profile: {exc}", severity="error")
            return False
        return True
