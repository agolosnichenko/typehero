import dataclasses

import pytest

from typer.engine.keystroke import Keystroke, KeystrokeKind


def test_char_keystroke_holds_char_and_timestamp():
    ks = Keystroke(kind=KeystrokeKind.CHAR, char="a", timestamp=1.5)
    assert ks.kind is KeystrokeKind.CHAR
    assert ks.char == "a"
    assert ks.timestamp == 1.5


def test_backspace_keystroke_has_no_char():
    ks = Keystroke(kind=KeystrokeKind.BACKSPACE, char=None, timestamp=2.0)
    assert ks.kind is KeystrokeKind.BACKSPACE
    assert ks.char is None


def test_keystroke_is_frozen():
    ks = Keystroke(kind=KeystrokeKind.CHAR, char="x", timestamp=0.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ks.char = "y"  # type: ignore[misc]


def test_char_keystroke_requires_char():
    with pytest.raises(ValueError):
        Keystroke(kind=KeystrokeKind.CHAR, char=None, timestamp=0.0)


def test_backspace_keystroke_rejects_char():
    with pytest.raises(ValueError):
        Keystroke(kind=KeystrokeKind.BACKSPACE, char="x", timestamp=0.0)
