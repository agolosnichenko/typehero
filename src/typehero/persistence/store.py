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
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import Any

from typehero.domain.progress import BenchmarkSnapshot, Progress

_logger = logging.getLogger(__name__)


def save_progress(path: Path, progress: Progress) -> None:
    """Atomically write `progress` to `path` as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(json.dumps(asdict(progress), ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)
    except OSError as exc:
        _logger.error("Failed to save profile to %s: %s", path, exc)
        tmp.unlink(missing_ok=True)
        raise


def load_progress(path: Path, on_corrupt: Callable[[Path], None] | None = None) -> Progress:
    """Load progress from `path`, returning a default on missing/corrupt files.

    Missing optional keys are filled from `Progress` defaults (forward
    compatibility with older saves); only structurally invalid data is treated
    as corruption and backed up. `on_corrupt`, if given, is called with the
    backup-triggering `path` so a caller (e.g. the TUI) can surface the reset.
    """
    if not path.exists():
        return Progress()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return _from_dict(data)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        _logger.warning("Corrupt profile at %s (%s); backing up and resetting", path, exc)
        backup = _backup_corrupt(path)
        if on_corrupt is not None:
            on_corrupt(backup)
        return Progress()


def _require_list(data: dict, key: str) -> list:
    value = data.get(key, [])
    if not isinstance(value, list):
        raise TypeError(f"{key} must be a list, got {type(value).__name__}")
    return value


def _from_dict(data: Any) -> Progress:
    if not isinstance(data, dict):
        raise TypeError(f"profile must be a mapping, got {type(data).__name__}")
    raw_benchmarks = data.get("benchmarks", {})
    if not isinstance(raw_benchmarks, dict):
        raise TypeError(f"benchmarks must be a mapping, got {type(raw_benchmarks).__name__}")
    benchmarks = {
        course_id: [BenchmarkSnapshot(**snap) for snap in snaps]
        for course_id, snaps in raw_benchmarks.items()
    }
    defaults = Progress()
    return Progress(
        ui_locale=data.get("ui_locale", defaults.ui_locale),
        total_xp=data.get("total_xp", defaults.total_xp),
        completed_lessons=_require_list(data, "completed_lessons"),
        last_active_date=data.get("last_active_date", defaults.last_active_date),
        current_streak=data.get("current_streak", defaults.current_streak),
        unlocked_achievements=_require_list(data, "unlocked_achievements"),
        benchmarks=benchmarks,
        skipped_baselines=_require_list(data, "skipped_baselines"),
    )


def _backup_corrupt(path: Path) -> Path:
    backup = path.with_name(f"{path.name}.corrupt-{int(time.time() * 1_000_000)}")
    path.replace(backup)
    return backup
