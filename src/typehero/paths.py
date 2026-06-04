"""Filesystem locations for content and the local profile.

Both are environment-overridable so tests and packagers can redirect them
without touching code.
"""

from __future__ import annotations

import os
from importlib.resources import files
from pathlib import Path

_APP_NAME = "typehero"


def content_dir() -> Path:
    """Directory holding courses/achievements/i18n YAML.

    Honours ``TYPEHERO_CONTENT_DIR``; otherwise the ``content/`` data bundled
    inside the installed package.
    """
    override = os.environ.get("TYPEHERO_CONTENT_DIR")
    if override:
        return Path(override)
    resource = files(_APP_NAME) / "content"
    if not isinstance(resource, Path):
        raise RuntimeError(f"Bundled content is not a real directory: {resource!r}")
    return resource


def profile_path() -> Path:
    """Path to the single local profile JSON, honouring ``XDG_CONFIG_HOME``."""
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / _APP_NAME / "profile.json"
