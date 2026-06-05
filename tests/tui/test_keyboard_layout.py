import pytest

from typehero.tui.keyboard_layout import (
    JCUKEN,
    QWERTY,
    Finger,
    Hand,
    Highlight,
    highlight_for,
    layout_for,
)

RU_ALPHABET = "абвгдежзийклмнопрстуфхцчшщъыьэюяё"
EN_ALPHABET = "abcdefghijklmnopqrstuvwxyz"


def test_layout_for_maps_course_layout_strings():
    assert layout_for("qwerty") is QWERTY
    assert layout_for("jcuken") is JCUKEN


def test_layout_for_unknown_raises_with_value():
    with pytest.raises(ValueError, match="dvorak"):
        layout_for("dvorak")


def test_qwerty_covers_its_alphabet_and_punctuation():
    for char in EN_ALPHABET + ".,":
        assert QWERTY.lookup(char) is not None, char
    assert QWERTY.lookup(" ") is not None


def test_jcuken_covers_its_alphabet_and_punctuation():
    for char in RU_ALPHABET + ".,":
        assert JCUKEN.lookup(char) is not None, char
    assert JCUKEN.lookup(" ") is not None


def test_lowercase_letter_needs_no_shift():
    ref = QWERTY.lookup("d")
    assert ref is not None
    assert ref.needs_shift is False
    assert ref.finger is Finger.L_MIDDLE


def test_uppercase_letter_is_same_key_with_shift():
    lower = JCUKEN.lookup("д")
    upper = JCUKEN.lookup("Д")
    assert lower is not None and upper is not None
    assert (upper.row, upper.col, upper.finger) == (lower.row, lower.col, lower.finger)
    assert lower.needs_shift is False
    assert upper.needs_shift is True


def test_jcuken_comma_is_shifted_period():
    period = JCUKEN.lookup(".")
    comma = JCUKEN.lookup(",")
    assert period is not None and comma is not None
    assert (comma.row, comma.col, comma.finger) == (period.row, period.col, period.finger)
    assert comma.needs_shift is True
    assert period.finger is Finger.R_PINKY


def test_jcuken_yo_is_left_pinky():
    ref = JCUKEN.lookup("ё")
    assert ref is not None
    assert ref.finger is Finger.L_PINKY


def test_char_off_the_map_returns_none():
    assert QWERTY.lookup("1") is None
    assert QWERTY.lookup(None) is None


def test_highlight_for_left_hand_char_uses_right_shift():
    # "Д" is right hand on ЙЦУКЕН, so Shift is pressed by the left hand.
    hl = highlight_for(JCUKEN, "Д")
    assert isinstance(hl, Highlight)
    assert hl.key is not None and hl.key.finger is Finger.R_RING
    assert hl.shift_hand is Hand.LEFT


def test_highlight_for_no_shift_when_lowercase():
    hl = highlight_for(JCUKEN, "д")
    assert hl.shift_hand is None
    assert hl.key is not None


def test_highlight_for_off_map_char_is_empty():
    hl = highlight_for(QWERTY, "1")
    assert hl.key is None and hl.shift_hand is None
