"""The lesson guide widget — a per-lesson tip plus a touch-typing principle.

A dumb view: it holds two already-resolved strings and renders them. The pure
`render_text` method builds the Rich text so it can be asserted without a
terminal, mirroring the `FingerMap` pattern.
"""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

_TIP_MARKER = "💡 "
_PRINCIPLE_MARKER = "▸ "


class LessonGuide(Static):
    """Renders an optional lesson tip above a single touch-typing principle."""

    DEFAULT_CSS = """
    LessonGuide {
        width: auto;
        height: auto;
        padding: 0 2;
    }
    """

    def __init__(self, *, tip: str | None, principle: str) -> None:
        super().__init__()
        self._tip = tip
        self._principle = principle

    def on_mount(self) -> None:
        self.update(self.render_text())

    def render_text(self) -> Text:
        """Build the guide text: tip line (if any) then the principle line."""
        text = Text()
        if self._tip:
            text.append(_TIP_MARKER, style="bold yellow")
            text.append(self._tip, style="italic")
            text.append("\n")
        text.append(_PRINCIPLE_MARKER, style="bold cyan")
        text.append(self._principle, style="dim")
        return text
