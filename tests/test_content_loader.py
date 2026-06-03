import pytest

from typer.content_loader import ContentError, load_achievements, load_course

_COURSE_YAML = """
course:
  id: en
  layout: qwerty
  title:
    en: "Touch typing"
  benchmark_text: "the quick brown fox"
  lessons:
    - id: en-01
      title:
        en: "Home row"
      type: keys
      stages:
        - "fff jjj"
      pass:
        max_error_rate: 0.08
        min_wpm: null
      reward_xp: 50
    - id: en-02
      title:
        en: "Words"
      type: words
      stages:
        - { source: wordlist, count: 40 }
      pass:
        max_error_rate: 0.05
        min_wpm: 25
      reward_xp: 120
"""

_ACH_YAML = """
achievements:
  - id: flawless
    title:
      en: "Flawless"
    desc:
      en: "Zero typos"
    condition: { metric: errors, op: "==", value: 0 }
"""


def _write(tmp_path, name: str, text: str):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_load_course_parses_lessons(tmp_path):
    path = _write(tmp_path, "en.yaml", _COURSE_YAML)
    course = load_course(path)
    assert course.id == "en"
    assert course.benchmark_text == "the quick brown fox"
    assert [lesson.id for lesson in course.lessons] == ["en-01", "en-02"]
    assert course.lessons[0].criteria.max_error_rate == 0.08
    assert course.lessons[0].criteria.min_wpm is None
    assert course.lessons[1].criteria.min_wpm == 25


def test_load_achievements_parses_condition(tmp_path):
    path = _write(tmp_path, "achievements.yaml", _ACH_YAML)
    achievements = load_achievements(path)
    assert achievements[0].id == "flawless"
    assert achievements[0].metric == "errors"
    assert achievements[0].op == "=="
    assert achievements[0].value == 0


def test_malformed_course_raises_content_error(tmp_path):
    path = _write(tmp_path, "bad.yaml", "course:\n  id: en\n")  # missing lessons
    with pytest.raises(ContentError) as exc:
        load_course(path)
    assert "bad.yaml" in str(exc.value)
    assert "lessons" in str(exc.value)


def test_null_lessons_raises_content_error(tmp_path):
    path = _write(tmp_path, "null_lessons.yaml", "course:\n  id: en\n  lessons:\n")
    with pytest.raises(ContentError) as exc:
        load_course(path)
    assert "lessons" in str(exc.value)


def test_unknown_achievement_op_raises_content_error(tmp_path):
    bad_yaml = """
achievements:
  - id: flawless
    title:
      en: "Flawless"
    desc:
      en: "Zero typos"
    condition: { metric: errors, op: "=>", value: 0 }
"""
    path = _write(tmp_path, "bad_achievements.yaml", bad_yaml)
    with pytest.raises(ContentError) as exc:
        load_achievements(path)
    assert "=>" in str(exc.value)
