"""Atomic JSON persistence for the single local profile.

Writes go through a temp file + `os.replace` so an interrupted save never
leaves a half-written profile. A corrupt profile is backed up (not deleted)
and replaced with a fresh one, so progress is never silently lost.
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict
from pathlib import Path

from typer.domain.progress import BenchmarkSnapshot, Progress

_logger = logging.getLogger(__name__)


def save_progress(path: Path, progress: Progress) -> None:
    """Atomically write `progress` to `path` as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(asdict(progress), ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_progress(path: Path) -> Progress:
    """Load progress from `path`, returning a default on missing/corrupt files."""
    if not path.exists():
        return Progress()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return _from_dict(data)
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        _logger.warning("Corrupt profile at %s (%s); backing up and resetting", path, exc)
        _backup_corrupt(path)
        return Progress()


def _from_dict(data: dict) -> Progress:
    benchmarks = {
        course_id: [BenchmarkSnapshot(**snap) for snap in snaps]
        for course_id, snaps in data.get("benchmarks", {}).items()
    }
    return Progress(
        ui_locale=data["ui_locale"],
        total_xp=data["total_xp"],
        completed_lessons=list(data["completed_lessons"]),
        last_active_date=data["last_active_date"],
        current_streak=data["current_streak"],
        unlocked_achievements=list(data["unlocked_achievements"]),
        benchmarks=benchmarks,
    )


def _backup_corrupt(path: Path) -> None:
    backup = path.with_name(f"{path.name}.corrupt-{int(time.time())}")
    path.replace(backup)
