"""Pure selection of a touch-typing principle for a lesson.

Kept out of the widget so the choice is deterministic and testable without a
terminal, mirroring the `highlight_for` / `FingerMap` split.
"""

from __future__ import annotations


def select_principle(principles: list[dict[str, str]], lesson_index: int) -> dict[str, str]:
    """Pick a principle deterministically by lesson index, wrapping modulo length.

    The same lesson index always yields the same principle. Raises `ValueError`
    when `principles` is empty.
    """
    if not principles:
        raise ValueError("cannot select a principle from an empty list")
    return principles[lesson_index % len(principles)]
