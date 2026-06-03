"""Declarative achievement engine.

Each achievement is a `metric op value` condition checked against a context
dict built from session metrics and player progress.
"""

from __future__ import annotations

import operator
from collections.abc import Callable, Mapping
from dataclasses import dataclass

_OPS: dict[str, Callable[[float, float], bool]] = {
    "==": operator.eq,
    ">=": operator.ge,
    ">": operator.gt,
    "<=": operator.le,
    "<": operator.lt,
}


@dataclass(frozen=True)
class Achievement:
    """A single unlockable badge defined by a numeric condition."""

    id: str
    title: dict[str, str]
    desc: dict[str, str]
    metric: str
    op: str
    value: float


def check(achievement: Achievement, context: Mapping[str, float]) -> bool:
    """True if the achievement's condition holds for `context`.

    Raises:
        KeyError: if the achievement uses an unsupported operator.
    """
    if achievement.metric not in context:
        return False
    compare = _OPS[achievement.op]
    return compare(context[achievement.metric], achievement.value)


def newly_unlocked(
    achievements: list[Achievement],
    context: Mapping[str, float],
    already_unlocked: set[str],
) -> list[str]:
    """IDs of achievements whose condition now holds and weren't owned before."""
    return [a.id for a in achievements if a.id not in already_unlocked and check(a, context)]
