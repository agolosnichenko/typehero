import pytest

from typehero.content_loader import (
    ContentError,
    load_achievements,
    load_corpus,
    load_course,
    load_i18n,
    load_principles,
    load_wordlist,
)
from typehero.localization import Translator

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
        - { source: wordlist, count: 40, keys: "asdfjkl" }
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


_COURSE_WITH_TIP = """
course:
  id: en
  layout: qwerty
  title: { en: "Touch typing" }
  benchmark_text: "fj"
  lessons:
    - id: en-01
      title: { en: "Home row" }
      type: keys
      stages: ["fff jjj"]
      pass: { max_error_rate: 0.08, min_wpm: null }
      reward_xp: 50
      tip: { en: "f and j are home keys", ru: "f и j — опорные" }
    - id: en-02
      title: { en: "More" }
      type: keys
      stages: ["ddd kkk"]
      pass: { max_error_rate: 0.08, min_wpm: null }
      reward_xp: 50
"""


def test_load_course_parses_optional_tip(tmp_path):
    path = _write(tmp_path, "en.yaml", _COURSE_WITH_TIP)
    course = load_course(path)
    assert course.lessons[0].tip == {"en": "f and j are home keys", "ru": "f и j — опорные"}
    assert course.lessons[1].tip is None


def test_load_principles_parses_bilingual_entries(tmp_path):
    path = _write(
        tmp_path,
        "principles.yaml",
        'principles:\n'
        '  - { en: "Stay on home row", ru: "Держись домашнего ряда" }\n'
        '  - { en: "Accuracy first", ru: "Сначала точность" }\n',
    )
    principles = load_principles(path)
    assert principles[0] == {"en": "Stay on home row", "ru": "Держись домашнего ряда"}
    assert len(principles) == 2


def test_load_principles_rejects_missing_key(tmp_path):
    path = _write(tmp_path, "principles.yaml", "rules: []\n")
    with pytest.raises(ContentError, match="principles"):
        load_principles(path)


def test_load_principles_rejects_empty_list(tmp_path):
    path = _write(tmp_path, "principles.yaml", "principles: []\n")
    with pytest.raises(ContentError, match="principles.yaml"):
        load_principles(path)


def test_load_principles_rejects_non_mapping_entry(tmp_path):
    path = _write(tmp_path, "principles.yaml", 'principles:\n  - "just a string"\n')
    with pytest.raises(ContentError, match="principles.yaml"):
        load_principles(path)


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


def test_empty_stages_raises_content_error(tmp_path):
    bad_yaml = """
course:
  id: en
  layout: qwerty
  title:
    en: "T"
  benchmark_text: "x"
  lessons:
    - id: en-01
      title:
        en: "Home row"
      type: keys
      stages: []
      pass:
        max_error_rate: 0.1
      reward_xp: 50
"""
    path = _write(tmp_path, "empty_stages.yaml", bad_yaml)
    with pytest.raises(ContentError) as exc:
        load_course(path)
    assert "en-01" in str(exc.value)
    assert "no stages" in str(exc.value)


def test_unknown_achievement_metric_raises_content_error(tmp_path):
    bad_yaml = """
achievements:
  - id: typo
    title:
      en: "Typo"
    desc:
      en: "Misspelled metric"
    condition: { metric: net_wmp, op: ">=", value: 80 }
"""
    path = _write(tmp_path, "bad_metric.yaml", bad_yaml)
    with pytest.raises(ContentError) as exc:
        load_achievements(path)
    assert "net_wmp" in str(exc.value)
    assert "bad_metric.yaml" in str(exc.value)


def test_out_of_range_max_error_rate_raises_content_error(tmp_path):
    bad_yaml = """
course:
  id: en
  layout: qwerty
  title:
    en: "T"
  benchmark_text: "x"
  lessons:
    - id: en-01
      title:
        en: "Home row"
      type: keys
      stages:
        - "fff"
      pass:
        max_error_rate: 5
      reward_xp: 50
"""
    path = _write(tmp_path, "bad_rate.yaml", bad_yaml)
    with pytest.raises(ContentError) as exc:
        load_course(path)
    assert "bad_rate.yaml" in str(exc.value)
    assert "max_error_rate" in str(exc.value)


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


_EN_I18N = 'menu.start: "Start"\nmenu.quit: "Quit"\n'
_RU_I18N = 'menu.start: "Старт"\nmenu.quit: "Выход"\n'


def test_load_i18n_builds_translator(tmp_path):
    (tmp_path / "en.yaml").write_text(_EN_I18N, encoding="utf-8")
    (tmp_path / "ru.yaml").write_text(_RU_I18N, encoding="utf-8")
    translator = load_i18n(tmp_path)
    assert isinstance(translator, Translator)
    assert translator.t("menu.start", "ru") == "Старт"
    assert translator.t("menu.start", "en") == "Start"


def test_load_i18n_empty_directory_raises(tmp_path):
    with pytest.raises(ContentError):
        load_i18n(tmp_path)


def test_unreadable_yaml_raises_content_error(tmp_path):
    path = _write(tmp_path, "broken.yaml", "course: [unterminated\n")
    with pytest.raises(ContentError) as exc:
        load_course(path)
    assert "broken.yaml" in str(exc.value)


def test_non_list_lessons_raises_content_error(tmp_path):
    path = _write(tmp_path, "str_lessons.yaml", "course:\n  id: en\n  lessons: oops\n")
    with pytest.raises(ContentError) as exc:
        load_course(path)
    assert "lessons" in str(exc.value)
    assert "must be a list" in str(exc.value)


def test_non_numeric_achievement_value_raises_content_error(tmp_path):
    bad_yaml = """
achievements:
  - id: typo
    title:
      en: "Typo"
    desc:
      en: "String value"
    condition: { metric: errors, op: "==", value: "zero" }
"""
    path = _write(tmp_path, "bad_value.yaml", bad_yaml)
    with pytest.raises(ContentError) as exc:
        load_achievements(path)
    assert "bad_value.yaml" in str(exc.value)
    assert "value must be a number" in str(exc.value)


def test_unknown_lesson_type_raises_content_error(tmp_path):
    bad_yaml = _COURSE_YAML.replace("type: keys", "type: hieroglyphs", 1)
    path = _write(tmp_path, "bad_type.yaml", bad_yaml)
    with pytest.raises(ContentError) as exc:
        load_course(path)
    assert "bad_type.yaml" in str(exc.value)
    assert "hieroglyphs" in str(exc.value)


def test_non_mapping_locale_file_raises_content_error(tmp_path):
    (tmp_path / "en.yaml").write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ContentError) as exc:
        load_i18n(tmp_path)
    assert "en.yaml" in str(exc.value)


def test_load_wordlist_reads_nonblank_lines(tmp_path):
    path = tmp_path / "en.txt"
    path.write_text("ask\n\nall\n  dad  \n", encoding="utf-8")
    assert load_wordlist(path) == ["ask", "all", "dad"]


def test_load_wordlist_empty_raises(tmp_path):
    path = tmp_path / "en.txt"
    path.write_text("\n  \n", encoding="utf-8")
    with pytest.raises(ContentError, match="empty"):
        load_wordlist(path)


def test_load_corpus_reads_text(tmp_path):
    path = tmp_path / "p.txt"
    path.write_text("Alpha beta. Gamma delta.\n", encoding="utf-8")
    assert load_corpus(path) == "Alpha beta. Gamma delta."


def test_load_corpus_missing_file_raises(tmp_path):
    with pytest.raises(ContentError, match="Cannot read"):
        load_corpus(tmp_path / "nope.txt")


def _course_with_stage(stage_yaml: str) -> str:
    return _COURSE_YAML.replace('- "fff jjj"', stage_yaml, 1)


def test_stage_with_unknown_source_raises_at_load(tmp_path):
    path = _write(tmp_path, "bad.yaml", _course_with_stage("- { source: synth, count: 5 }"))
    with pytest.raises(ContentError) as exc:
        load_course(path)
    assert "en-01" in str(exc.value)
    assert "unknown stage source" in str(exc.value)


def test_wordlist_stage_missing_keys_raises_at_load(tmp_path):
    path = _write(tmp_path, "bad.yaml", _course_with_stage("- { source: wordlist, count: 5 }"))
    with pytest.raises(ContentError, match="missing required key 'keys'"):
        load_course(path)


def test_wordlist_stage_non_positive_count_raises_at_load(tmp_path):
    stage = "- { source: wordlist, count: 0, keys: asdf }"
    path = _write(tmp_path, "bad.yaml", _course_with_stage(stage))
    with pytest.raises(ContentError, match="'count' must be a positive integer"):
        load_course(path)


def test_corpus_stage_non_int_length_raises_at_load(tmp_path):
    stage = "- { source: corpus, file: p.txt, length: 1.5 }"
    path = _write(tmp_path, "bad.yaml", _course_with_stage(stage))
    with pytest.raises(ContentError, match="'length' must be a positive integer"):
        load_course(path)


def test_non_mapping_stage_raises_at_load(tmp_path):
    path = _write(tmp_path, "bad.yaml", _course_with_stage("- 42"))
    with pytest.raises(ContentError, match="stage must be a string or"):
        load_course(path)
