"""Live typing stats — current net WPM and a running error count.

A dumb view following the `LessonGuide`/`FingerMap` pattern: it holds two
already-computed values and renders them. The pure `render_text` method builds
the Rich text so it can be asserted without a terminal. `LessonScreen` feeds it
fresh values on every keystroke via `update_stats`.
"""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

_SPEED_MARKER = "⚡ "
_ERROR_MARKER = "✗ "


class LiveStats(Static):
    """Renders live net WPM and error count, refreshed per keystroke."""

    DEFAULT_CSS = """
    LiveStats {
        width: auto;
        height: auto;
        padding: 0 2;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._net_wpm = 0.0
        self._errors = 0

    def on_mount(self) -> None:
        self.update(self.render_text())

    def update_stats(self, net_wpm: float, errors: int) -> None:
        """Store fresh metrics and re-render."""
        self._net_wpm = net_wpm
        self._errors = errors
        if self.is_mounted:
            self.update(self.render_text())

    def render_text(self) -> Text:
        """Build the stats line: speed segment then error-count segment."""
        text = Text()
        text.append(_SPEED_MARKER, style="bold yellow")
        text.append(f"{round(self._net_wpm)} WPM", style="bold")
        text.append("   ")
        error_style = "bold red" if self._errors else "dim"
        text.append(_ERROR_MARKER, style=error_style)
        text.append(str(self._errors), style=error_style)
        return text
