import random

from typehero.content_loader import load_achievements, load_course, load_i18n
from typehero.domain.generators import CourseResources, lesson_target
from typehero.paths import content_dir


def test_bundled_en_course_loads_and_resolves_targets():
    course = load_course(content_dir() / "courses" / "en.yaml")
    assert len(course.lessons) >= 2
    resources = CourseResources(wordlist=[], corpora={})
    rng = random.Random(0)
    for lesson in course.lessons:
        assert lesson_target(lesson, resources=resources, rng=rng)


def test_bundled_ru_course_loads():
    course = load_course(content_dir() / "courses" / "ru.yaml")
    assert course.id == "ru"


def test_bundled_achievements_and_i18n_load():
    achievements = load_achievements(content_dir() / "achievements.yaml")
    assert any(a.id == "flawless" for a in achievements)
    translator = load_i18n(content_dir() / "i18n")
    assert translator.t("menu.locked", "en") == "locked"
