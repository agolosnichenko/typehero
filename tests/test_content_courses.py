import pytest

from typehero.content_loader import load_course
from typehero.paths import content_dir


@pytest.mark.parametrize("course_file", ["ru.yaml", "en.yaml"])
def test_every_lesson_has_a_bilingual_tip(course_file):
    course = load_course(content_dir() / "courses" / course_file)
    for lesson in course.lessons:
        assert lesson.tip is not None, f"{lesson.id} has no tip"
        assert lesson.tip.get("en"), f"{lesson.id} missing en tip"
        assert lesson.tip.get("ru"), f"{lesson.id} missing ru tip"
