import pytest

from typehero.domain.course import Course, is_unlocked
from typehero.domain.lesson import Lesson, LessonType, PassCriteria


def _lesson(lesson_id: str) -> Lesson:
    return Lesson(
        id=lesson_id,
        title={"en": lesson_id},
        type=LessonType.KEYS,
        stages=["x"],
        criteria=PassCriteria(max_error_rate=0.1, min_wpm=None),
        reward_xp=10,
    )


def _course() -> Course:
    return Course(
        id="en",
        layout="qwerty",
        title={"en": "English"},
        benchmark_text="the quick brown fox",
        lessons=[_lesson("l1"), _lesson("l2"), _lesson("l3")],
    )


def test_first_lesson_always_unlocked():
    assert is_unlocked(_course(), "l1", completed_ids=set())


def test_second_lesson_locked_until_first_completed():
    course = _course()
    assert not is_unlocked(course, "l2", completed_ids=set())
    assert is_unlocked(course, "l2", completed_ids={"l1"})


def test_unknown_lesson_id_raises():
    with pytest.raises(KeyError):
        is_unlocked(_course(), "nope", completed_ids=set())


def test_duplicate_lesson_ids_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        Course(
            id="en",
            layout="qwerty",
            title={"en": "English"},
            benchmark_text="x",
            lessons=[_lesson("l1"), _lesson("l1")],
        )
