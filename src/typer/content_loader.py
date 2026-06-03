"""Parse YAML content (courses, achievements) into domain objects.

Fails fast with a `ContentError` naming the file when data is malformed,
rather than silently skipping content.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from typer.domain.course import Course
from typer.domain.lesson import Lesson, PassCriteria
from typer.gamification.achievements import Achievement


class ContentError(Exception):
    """Raised when a content file is missing required structure."""


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ContentError(f"Cannot read content file {path}: {exc}") from exc


def _require(data: dict[str, Any], key: str, path: Path) -> Any:
    if not isinstance(data, dict) or key not in data:
        raise ContentError(f"{path}: missing required key {key!r}")
    return data[key]


def load_course(path: Path) -> Course:
    """Parse a course YAML file into a `Course`."""
    root = _require(_load_yaml(path), "course", path)
    lessons = [_parse_lesson(raw, path) for raw in _require(root, "lessons", path)]
    return Course(
        id=_require(root, "id", path),
        layout=_require(root, "layout", path),
        title=_require(root, "title", path),
        benchmark_text=_require(root, "benchmark_text", path),
        lessons=lessons,
    )


def _parse_lesson(raw: dict[str, Any], path: Path) -> Lesson:
    criteria_raw = _require(raw, "pass", path)
    return Lesson(
        id=_require(raw, "id", path),
        title=_require(raw, "title", path),
        type=_require(raw, "type", path),
        stages=_require(raw, "stages", path),
        criteria=PassCriteria(
            max_error_rate=_require(criteria_raw, "max_error_rate", path),
            min_wpm=criteria_raw.get("min_wpm"),
        ),
        reward_xp=_require(raw, "reward_xp", path),
    )


def load_achievements(path: Path) -> list[Achievement]:
    """Parse an achievements YAML file into `Achievement` objects."""
    items = _require(_load_yaml(path), "achievements", path)
    return [_parse_achievement(raw, path) for raw in items]


def _parse_achievement(raw: dict[str, Any], path: Path) -> Achievement:
    condition = _require(raw, "condition", path)
    return Achievement(
        id=_require(raw, "id", path),
        title=_require(raw, "title", path),
        desc=_require(raw, "desc", path),
        metric=_require(condition, "metric", path),
        op=_require(condition, "op", path),
        value=_require(condition, "value", path),
    )
