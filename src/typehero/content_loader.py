"""Parse YAML content (courses, achievements) into domain objects.

Fails fast with a `ContentError` naming the file when data is malformed,
rather than silently skipping content.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from typehero.domain.course import Course
from typehero.domain.lesson import Lesson, LessonType, PassCriteria
from typehero.gamification.achievements import SUPPORTED_OPS, Achievement
from typehero.gamification.context import CONTEXT_METRICS
from typehero.localization import Translator


class ContentError(Exception):
    """Raised when a content file is missing required structure."""


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ContentError(f"Cannot read content file {path}: {exc}") from exc


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContentError(f"Cannot read content file {path}: {exc}") from exc


def _require(data: dict[str, Any], key: str, path: Path) -> Any:
    if not isinstance(data, dict) or key not in data:
        raise ContentError(f"{path}: missing required key {key!r}")
    return data[key]


def _require_list(data: dict[str, Any], key: str, path: Path) -> list[Any]:
    value = _require(data, key, path)
    if not isinstance(value, list):
        raise ContentError(f"{path}: {key!r} must be a list, got {type(value).__name__}")
    return value


def _stage_positive_int(stage: dict[str, Any], key: str, where: str) -> None:
    if key not in stage:
        raise ContentError(f"{where}: stage missing required key {key!r}")
    value = stage[key]
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ContentError(f"{where}: stage {key!r} must be a positive integer, got {value!r}")


def _stage_nonempty_str(stage: dict[str, Any], key: str, where: str) -> None:
    if key not in stage:
        raise ContentError(f"{where}: stage missing required key {key!r}")
    value = stage[key]
    if not isinstance(value, str) or not value:
        raise ContentError(f"{where}: stage {key!r} must be a non-empty string, got {value!r}")


def _validate_stage(stage: object, where: str) -> None:
    """Reject a malformed stage at load time so failure names the file + lesson.

    A `str` stage is a literal and always valid. A generator stage must be a
    `{source: wordlist|corpus, ...}` mapping with the keys that source needs.
    """
    if isinstance(stage, str):
        return
    if not isinstance(stage, dict) or "source" not in stage:
        raise ContentError(
            f"{where}: stage must be a string or a {{source: ...}} mapping, got {stage!r}"
        )
    spec = cast("dict[str, Any]", stage)
    source = spec["source"]
    if source == "wordlist":
        _stage_positive_int(spec, "count", where)
        _stage_nonempty_str(spec, "keys", where)
    elif source == "corpus":
        _stage_nonempty_str(spec, "file", where)
        _stage_positive_int(spec, "length", where)
    else:
        raise ContentError(
            f"{where}: unknown stage source {source!r}; expected 'wordlist' or 'corpus'"
        )


def load_course(path: Path) -> Course:
    """Parse a course YAML file into a `Course`."""
    root = _require(_load_yaml(path), "course", path)
    lessons = [_parse_lesson(raw, path) for raw in _require_list(root, "lessons", path)]
    return Course(
        id=_require(root, "id", path),
        layout=_require(root, "layout", path),
        title=_require(root, "title", path),
        benchmark_text=_require(root, "benchmark_text", path),
        lessons=lessons,
    )


def _parse_lesson(raw: dict[str, Any], path: Path) -> Lesson:
    criteria_raw = _require(raw, "pass", path)
    try:
        criteria = PassCriteria(
            max_error_rate=_require(criteria_raw, "max_error_rate", path),
            min_wpm=criteria_raw.get("min_wpm"),
        )
    except (ValueError, TypeError) as exc:
        raise ContentError(f"{path}: invalid pass criteria: {exc}") from exc
    type_raw = _require(raw, "type", path)
    try:
        lesson_type = LessonType(type_raw)
    except ValueError as exc:
        raise ContentError(
            f"{path}: unknown lesson type {type_raw!r}; "
            f"expected one of {[t.value for t in LessonType]}"
        ) from exc
    lesson_id = _require(raw, "id", path)
    stages = _require_list(raw, "stages", path)
    if not stages:
        raise ContentError(f"{path}: lesson {lesson_id!r} has no stages")
    for stage in stages:
        _validate_stage(stage, f"{path}: lesson {lesson_id!r}")
    try:
        return Lesson(
            id=lesson_id,
            title=_require(raw, "title", path),
            type=lesson_type,
            stages=stages,
            criteria=criteria,
            reward_xp=_require(raw, "reward_xp", path),
        )
    except (ValueError, TypeError) as exc:
        raise ContentError(f"{path}: invalid lesson: {exc}") from exc


def load_achievements(path: Path) -> list[Achievement]:
    """Parse an achievements YAML file into `Achievement` objects."""
    items = _require_list(_load_yaml(path), "achievements", path)
    return [_parse_achievement(raw, path) for raw in items]


def _parse_achievement(raw: dict[str, Any], path: Path) -> Achievement:
    condition = _require(raw, "condition", path)
    op = _require(condition, "op", path)
    if op not in SUPPORTED_OPS:
        raise ContentError(
            f"{path}: unsupported achievement op {op!r}; expected one of {sorted(SUPPORTED_OPS)}"
        )
    metric = _require(condition, "metric", path)
    if metric not in CONTEXT_METRICS:
        raise ContentError(
            f"{path}: unknown achievement metric {metric!r}; "
            f"expected one of {sorted(CONTEXT_METRICS)}"
        )
    value = _require(condition, "value", path)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContentError(
            f"{path}: achievement condition value must be a number, got {type(value).__name__}"
        )
    return Achievement(
        id=_require(raw, "id", path),
        title=_require(raw, "title", path),
        desc=_require(raw, "desc", path),
        metric=metric,
        op=op,
        value=value,
    )


def load_i18n(directory: Path) -> Translator:
    """Parse every ``<locale>.yaml`` in `directory` into a `Translator`.

    Each file is a flat mapping of UI key to string. Raises `ContentError` if
    the directory has no locale files or a file is not a mapping.
    """
    tables: dict[str, dict[str, str]] = {}
    for locale_file in sorted(directory.glob("*.yaml")):
        data = _load_yaml(locale_file)
        if not isinstance(data, dict):
            raise ContentError(f"{locale_file}: expected a mapping of key to string")
        tables[locale_file.stem] = {str(key): str(value) for key, value in data.items()}
    if not tables:
        raise ContentError(f"No i18n locale files found in {directory}")
    return Translator(tables=tables)


def load_wordlist(path: Path) -> list[str]:
    """Parse a newline-separated wordlist, dropping blank lines.

    Raises `ContentError` if the file cannot be read or has no words.
    """
    words = [line.strip() for line in _read_text(path).splitlines() if line.strip()]
    if not words:
        raise ContentError(f"{path}: wordlist is empty")
    return words


def load_corpus(path: Path) -> str:
    """Read a plain-text corpus file, stripped of surrounding whitespace.

    Raises `ContentError` if the file cannot be read or is empty.
    """
    text = _read_text(path).strip()
    if not text:
        raise ContentError(f"{path}: corpus is empty")
    return text
