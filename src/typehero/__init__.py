"""Typer — console touch-typing trainer."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("typehero")
except PackageNotFoundError:  # running from an uninstalled source tree
    __version__ = "0+unknown"

__all__ = ["__version__"]
