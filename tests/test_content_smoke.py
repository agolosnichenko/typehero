import random
from typing import cast

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


def _resources(course_id: str) -> CourseResources:
    root = content_dir()
    wordlist = load_wordlist(root / "wordlists" / f"{course_id}.txt")
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


def test_en_course_completion_reaches_target_level():
    assert 6 <= _course_completion_level("en") <= 8


def test_bundled_achievements_and_i18n_load():
    achievements = load_achievements(content_dir() / "achievements.yaml")
    assert any(a.id == "flawless" for a in achievements)
    translator = load_i18n(content_dir() / "i18n")
    assert translator.t("menu.locked", "en") == "locked"
