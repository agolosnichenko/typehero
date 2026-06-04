import pytest

from typehero.domain.lesson import Lesson, LessonType, PassCriteria, lesson_target, stage_text


def _lesson(stages: list[object]) -> Lesson:
    return Lesson(
        id="en-01",
        title={"en": "Home row"},
        type=LessonType.KEYS,
        stages=stages,
        criteria=PassCriteria(max_error_rate=0.1, min_wpm=None),
        reward_xp=10,
    )


def test_stage_text_returns_string_stage():
    assert stage_text("fff jjj") == "fff jjj"


def test_stage_text_rejects_generator_stage():
    with pytest.raises(ValueError, match="generator"):
        stage_text({"source": "wordlist", "count": 40})


def test_lesson_target_joins_stages_with_space():
    assert lesson_target(_lesson(["fff jjj", "fj fj"])) == "fff jjj fj fj"
