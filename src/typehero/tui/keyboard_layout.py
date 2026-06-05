"""Keyboard layouts and the char->key index that drives the finger map.

Pure presentation data: which finger presses which key, and which key
produces a given character. Lives in `tui` because it describes the physical
keyboard, not domain logic. Mirrors `TypingSession`'s NFC normalization so a
looked-up character matches the normalized target.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from enum import Enum


class Hand(Enum):
    """Which hand a finger belongs to."""

    LEFT = "left"
    RIGHT = "right"


class Finger(Enum):
    """A typing finger with its display color and hand.

    The thumb has no hand: it presses only the space bar.
    """

    L_PINKY = ("#e06c75", Hand.LEFT)
    L_RING = ("#d19a66", Hand.LEFT)
    L_MIDDLE = ("#e5c07b", Hand.LEFT)
    L_INDEX = ("#98c379", Hand.LEFT)
    R_INDEX = ("#56b6c2", Hand.RIGHT)
    R_MIDDLE = ("#61afef", Hand.RIGHT)
    R_RING = ("#c678dd", Hand.RIGHT)
    R_PINKY = ("#be5046", Hand.RIGHT)
    THUMB = ("#5c6370", None)

    def __init__(self, color: str, hand: Hand | None) -> None:
        self.color = color
        self.hand = hand


@dataclass(frozen=True)
class Key:
    """One physical key: its base character, shifted character, and finger."""

    base: str
    shifted: str | None
    finger: Finger


@dataclass(frozen=True)
class KeyRef:
    """Where a character lives on the layout and whether it needs Shift."""

    row: int
    col: int
    finger: Finger
    needs_shift: bool


@dataclass(frozen=True)
class KeyboardLayout:
    """A physical layout: rows of keys plus a derived char->KeyRef index.

    The last row holds the single space key.
    """

    name: str
    rows: tuple[tuple[Key, ...], ...]
    chars: dict[str, KeyRef] = field(default_factory=dict, init=False, compare=False, hash=False)

    def __post_init__(self) -> None:
        index: dict[str, KeyRef] = {}
        for row_index, row in enumerate(self.rows):
            for col_index, key in enumerate(row):
                index[key.base] = KeyRef(row_index, col_index, key.finger, needs_shift=False)
                if key.shifted is not None:
                    index[key.shifted] = KeyRef(row_index, col_index, key.finger, needs_shift=True)
        object.__setattr__(self, "chars", index)

    def lookup(self, char: str | None) -> KeyRef | None:
        """Find the key for `char`, or None if it is not on this layout.

        An uppercase letter resolves to its lowercase key with `needs_shift`.
        """
        if char is None:
            return None
        normalized = unicodedata.normalize("NFC", char)
        direct = self.chars.get(normalized)
        if direct is not None:
            return direct
        lowered = normalized.lower()
        if lowered == normalized:
            return None
        ref = self.chars.get(lowered)
        if ref is None:
            return None
        return KeyRef(ref.row, ref.col, ref.finger, needs_shift=True)


@dataclass(frozen=True)
class Highlight:
    """What the finger map should highlight for the current character."""

    key: KeyRef | None
    shift_hand: Hand | None


def highlight_for(layout: KeyboardLayout, char: str | None) -> Highlight:
    """Compute the key and opposite-hand Shift to highlight for `char`."""
    ref = layout.lookup(char)
    if ref is None:
        return Highlight(key=None, shift_hand=None)
    shift_hand: Hand | None = None
    if ref.needs_shift and ref.finger.hand is not None:
        shift_hand = Hand.RIGHT if ref.finger.hand is Hand.LEFT else Hand.LEFT
    return Highlight(key=ref, shift_hand=shift_hand)


def _row(spec: list[tuple[str, str | None, Finger]]) -> tuple[Key, ...]:
    return tuple(Key(base, shifted, finger) for base, shifted, finger in spec)


_SPACE_ROW = (Key(" ", None, Finger.THUMB),)

QWERTY = KeyboardLayout(
    name="qwerty",
    rows=(
        _row(
            [
                ("q", None, Finger.L_PINKY),
                ("w", None, Finger.L_RING),
                ("e", None, Finger.L_MIDDLE),
                ("r", None, Finger.L_INDEX),
                ("t", None, Finger.L_INDEX),
                ("y", None, Finger.R_INDEX),
                ("u", None, Finger.R_INDEX),
                ("i", None, Finger.R_MIDDLE),
                ("o", None, Finger.R_RING),
                ("p", None, Finger.R_PINKY),
            ]
        ),
        _row(
            [
                ("a", None, Finger.L_PINKY),
                ("s", None, Finger.L_RING),
                ("d", None, Finger.L_MIDDLE),
                ("f", None, Finger.L_INDEX),
                ("g", None, Finger.L_INDEX),
                ("h", None, Finger.R_INDEX),
                ("j", None, Finger.R_INDEX),
                ("k", None, Finger.R_MIDDLE),
                ("l", None, Finger.R_RING),
            ]
        ),
        _row(
            [
                ("z", None, Finger.L_PINKY),
                ("x", None, Finger.L_RING),
                ("c", None, Finger.L_MIDDLE),
                ("v", None, Finger.L_INDEX),
                ("b", None, Finger.L_INDEX),
                ("n", None, Finger.R_INDEX),
                ("m", None, Finger.R_INDEX),
                (",", None, Finger.R_MIDDLE),
                (".", None, Finger.R_RING),
            ]
        ),
        _SPACE_ROW,
    ),
)

JCUKEN = KeyboardLayout(
    name="jcuken",
    rows=(
        _row(
            [
                ("ё", None, Finger.L_PINKY),
                ("й", None, Finger.L_PINKY),
                ("ц", None, Finger.L_RING),
                ("у", None, Finger.L_MIDDLE),
                ("к", None, Finger.L_INDEX),
                ("е", None, Finger.L_INDEX),
                ("н", None, Finger.R_INDEX),
                ("г", None, Finger.R_INDEX),
                ("ш", None, Finger.R_MIDDLE),
                ("щ", None, Finger.R_RING),
                ("з", None, Finger.R_PINKY),
                ("х", None, Finger.R_PINKY),
                ("ъ", None, Finger.R_PINKY),
            ]
        ),
        _row(
            [
                ("ф", None, Finger.L_PINKY),
                ("ы", None, Finger.L_RING),
                ("в", None, Finger.L_MIDDLE),
                ("а", None, Finger.L_INDEX),
                ("п", None, Finger.L_INDEX),
                ("р", None, Finger.R_INDEX),
                ("о", None, Finger.R_INDEX),
                ("л", None, Finger.R_MIDDLE),
                ("д", None, Finger.R_RING),
                ("ж", None, Finger.R_PINKY),
                ("э", None, Finger.R_PINKY),
            ]
        ),
        _row(
            [
                ("я", None, Finger.L_PINKY),
                ("ч", None, Finger.L_RING),
                ("с", None, Finger.L_MIDDLE),
                ("м", None, Finger.L_INDEX),
                ("и", None, Finger.L_INDEX),
                ("т", None, Finger.R_INDEX),
                ("ь", None, Finger.R_INDEX),
                ("б", None, Finger.R_MIDDLE),
                ("ю", None, Finger.R_RING),
                (".", ",", Finger.R_PINKY),
            ]
        ),
        _SPACE_ROW,
    ),
)

_LAYOUTS = {QWERTY.name: QWERTY, JCUKEN.name: JCUKEN}


def layout_for(course_layout: str) -> KeyboardLayout:
    """Return the layout for a course's `layout` value.

    Raises:
        ValueError: if `course_layout` is not a known layout.
    """
    try:
        return _LAYOUTS[course_layout]
    except KeyError:
        raise ValueError(f"unknown keyboard layout {course_layout!r}") from None
