"""Course: an ordered list of lessons with linear unlocking."""

from __future__ import annotations

from dataclasses import dataclass

from typer.domain.lesson import Lesson


@dataclass(frozen=True)
class Course:
    """An ordered curriculum for one keyboard layout."""

    id: str
    layout: str
    title: dict[str, str]
    benchmark_text: str
    lessons: list[Lesson]


def is_unlocked(course: Course, lesson_id: str, completed_ids: set[str]) -> bool:
    """A lesson is unlocked if it is first, or its predecessor is completed.

    Raises:
        KeyError: if `lesson_id` is not in the course.
    """
    index = _index_of(course, lesson_id)
    if index == 0:
        return True
    return course.lessons[index - 1].id in completed_ids


def _index_of(course: Course, lesson_id: str) -> int:
    for i, lesson in enumerate(course.lessons):
        if lesson.id == lesson_id:
            return i
    raise KeyError(f"Lesson {lesson_id!r} not found in course {course.id!r}")
