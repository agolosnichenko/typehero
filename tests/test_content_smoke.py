import random
from typing import cast

import pytest

from typehero.content_loader import (
    load_achievements,
    load_corpus,
    load_course,
    load_i18n,
    load_wordlist,
)
from typehero.domain.generators import CourseResources, lesson_target
from typehero.gamification.xp import earned_xp, player_level
from typehero.paths import content_dir
from typehero.tui.keyboard_layout import layout_for


def _resources(course_id: str) -> CourseResources:
    root = content_dir()
    wordlist = tuple(load_wordlist(root / "wordlists" / f"{course_id}.txt"))
    course = load_course(root / "courses" / f"{course_id}.yaml")
    stages = [
        cast("dict[str, object]", stage)
        for lesson in course.lessons
        for stage in lesson.stages
        if isinstance(stage, dict)
    ]
    files = sorted({str(stage["file"]) for stage in stages if stage.get("source") == "corpus"})
    corpora = {name: load_corpus(root / "corpora" / name) for name in files}
    return CourseResources(wordlist=wordlist, corpora=corpora)


def _course_completion_level(course_id: str) -> int:
    course = load_course(content_dir() / "courses" / f"{course_id}.yaml")
    total = 0
    for lesson in course.lessons:
        total += earned_xp(
            base=lesson.reward_xp,
            accuracy=1.0,
            net_wpm=lesson.criteria.min_wpm or 0.0,
            min_wpm=lesson.criteria.min_wpm,
            first_clear=True,
        )
    return player_level(total)


def test_en_course_resolves_every_lesson_target():
    course = load_course(content_dir() / "courses" / "en.yaml")
    assert len(course.lessons) >= 12
    resources = _resources("en")
    rng = random.Random(0)
    for lesson in course.lessons:
        assert lesson_target(lesson, resources=resources, rng=rng)


@pytest.mark.parametrize("course_id", ["en", "ru"])
def test_every_lesson_target_char_is_typable_on_the_layout(course_id):
    course = load_course(content_dir() / "courses" / f"{course_id}.yaml")
    layout = layout_for(course.layout)
    resources = _resources(course_id)
    rng = random.Random(0)
    for lesson in course.lessons:
        target = lesson_target(lesson, resources=resources, rng=rng)
        unmapped = sorted({char for char in target if layout.lookup(char) is None})
        assert not unmapped, f"{lesson.id}: chars not on {course.layout} layout: {unmapped}"


def test_en_course_completion_reaches_target_level():
    assert 6 <= _course_completion_level("en") <= 8


def test_ru_course_resolves_every_lesson_target():
    course = load_course(content_dir() / "courses" / "ru.yaml")
    assert len(course.lessons) >= 10
    resources = _resources("ru")
    rng = random.Random(0)
    for lesson in course.lessons:
        assert lesson_target(lesson, resources=resources, rng=rng)


def test_ru_course_completion_reaches_target_level():
    assert 6 <= _course_completion_level("ru") <= 8


def test_bundled_achievements_and_i18n_load():
    achievements = load_achievements(content_dir() / "achievements.yaml")
    assert any(a.id == "flawless" for a in achievements)
    translator = load_i18n(content_dir() / "i18n")
    assert translator.t("menu.locked", "en") == "locked"


def test_achievement_set_matches_mockup_count():
    achievements = load_achievements(content_dir() / "achievements.yaml")
    assert len(achievements) == 20
    ids = {a.id for a in achievements}
    assert {"flawless", "speed-demon", "week-streak"} <= ids
    # Every achievement is localized in both shipped locales.
    for achievement in achievements:
        assert achievement.title.get("en") and achievement.title.get("ru")
        assert achievement.desc.get("en") and achievement.desc.get("ru")
