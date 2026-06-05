"""The finger map widget — a colored keyboard with the current key lit up.

A dumb view: it holds a `KeyboardLayout` and the last computed `Highlight`,
and redraws on `highlight(char)`. All highlight logic lives in the pure
`highlight_for` function so it can be tested without a terminal.
"""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from typehero.tui.keyboard_layout import (
    Finger,
    Hand,
    Highlight,
    KeyboardLayout,
    highlight_for,
)

_LEFT_LEGEND = (Finger.L_PINKY, Finger.L_RING, Finger.L_MIDDLE, Finger.L_INDEX)
_RIGHT_LEGEND = (Finger.R_INDEX, Finger.R_MIDDLE, Finger.R_RING, Finger.R_PINKY)


class FingerMap(Static):
    """Renders a layout, coloring each key by finger and lighting the target."""

    DEFAULT_CSS = """
    FingerMap {
        width: auto;
        height: auto;
        padding: 1 2;
    }
    """

    def __init__(self, layout: KeyboardLayout) -> None:
        super().__init__()
        self._layout = layout
        self._highlight = Highlight(key=None, shift_hand=None)

    @property
    def highlight_state(self) -> Highlight:
        """The currently highlighted key and Shift hand (for tests/consumers)."""
        return self._highlight

    def on_mount(self) -> None:
        self.update(self._build())

    def highlight(self, char: str | None) -> None:
        """Light up the key (and opposite-hand Shift) for `char`."""
        self._highlight = highlight_for(self._layout, char)
        self.update(self._build())

    def _build(self) -> Text:
        text = Text()
        self._append_keys(text)
        self._append_space(text)
        self._append_shift(text)
        self._append_legend(text)
        return text

    def _append_keys(self, text: Text) -> None:
        hl = self._highlight
        letter_rows = self._layout.rows[:-1]
        for row_index, row in enumerate(letter_rows):
            text.append(" " * row_index)
            for col_index, key in enumerate(row):
                style = key.finger.color
                if hl.key is not None and hl.key.row == row_index and hl.key.col == col_index:
                    style = f"bold reverse {style}"
                text.append(key.base, style=style)
                text.append(" ")
            text.append("\n")

    def _append_space(self, text: Text) -> None:
        hl = self._highlight
        style = Finger.THUMB.color
        if hl.key is not None and hl.key.finger is Finger.THUMB:
            style = f"bold reverse {style}"
        text.append("      [ ", style="dim")
        text.append("space", style=style)
        text.append(" ]\n", style="dim")

    def _append_shift(self, text: Text) -> None:
        left = self._shift_style(Hand.LEFT, Finger.L_PINKY)
        right = self._shift_style(Hand.RIGHT, Finger.R_PINKY)
        text.append("Shift", style=left)
        text.append("              ")
        text.append("Shift", style=right)
        text.append("\n")

    def _shift_style(self, hand: Hand, finger: Finger) -> str:
        if self._highlight.shift_hand is hand:
            return f"bold reverse {finger.color}"
        return "dim"

    def _append_legend(self, text: Text) -> None:
        text.append("\n")
        text.append("L ", style="dim")
        for finger in _LEFT_LEGEND:
            text.append("█", style=finger.color)
        text.append("   R ", style="dim")
        for finger in _RIGHT_LEGEND:
            text.append("█", style=finger.color)
