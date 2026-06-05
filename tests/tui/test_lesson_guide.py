import pytest

from typehero.tui.lesson_guide import select_principle

_PRINCIPLES = [
    {"en": "first", "ru": "первый"},
    {"en": "second", "ru": "второй"},
    {"en": "third", "ru": "третий"},
]


def test_select_principle_is_deterministic_by_index():
    assert select_principle(_PRINCIPLES, 1) == {"en": "second", "ru": "второй"}
    assert select_principle(_PRINCIPLES, 1) == {"en": "second", "ru": "второй"}


def test_select_principle_wraps_modulo_length():
    assert select_principle(_PRINCIPLES, 4) == select_principle(_PRINCIPLES, 1)


def test_select_principle_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        select_principle([], 0)
