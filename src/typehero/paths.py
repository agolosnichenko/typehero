"""Filesystem locations for content and the local profile.

Both are environment-overridable so tests and packagers can redirect them
without touching code.
"""

from __future__ import annotations

import os
from pathlib import Path

_APP_NAME = "typehero"


def content_dir() -> Path:
    """Directory holding courses/achievements/i18n YAML.

    Honours ``TYPEHERO_CONTENT_DIR``; otherwise the repo-root ``content/``.
    """
    override = os.environ.get("TYPEHERO_CONTENT_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "content"


def profile_path() -> Path:
    """Path to the single local profile JSON, honouring ``XDG_CONFIG_HOME``."""
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / _APP_NAME / "profile.json"
