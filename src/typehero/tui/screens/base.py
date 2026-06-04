"""Shared base screen with typed access to the running app's state."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from textual.screen import Screen

if TYPE_CHECKING:
    from typehero.tui.app import TypeHeroApp
    from typehero.tui.state import AppState


class AppScreen(Screen):
    """A `Screen` that exposes the app's `AppState` without a per-call cast."""

    @property
    def app_state(self) -> AppState:
        """The running app's shared state."""
        return cast("TypeHeroApp", self.app).state

    def save_profile(self) -> None:
        """Persist the profile, surfacing a write failure as a toast.

        A failed save would otherwise raise out of an event handler and tear
        down the TUI; here the player is told and keeps their session.
        """
        try:
            self.app_state.save()
        except OSError as exc:
            self.notify(f"Could not save your profile: {exc}", severity="error")
