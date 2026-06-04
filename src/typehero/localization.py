"""Localization for content fields and UI strings.

Two axes, intentionally separate: typing language is a course property;
interface language is a profile setting. Missing translations fall back to
English with a logged warning rather than crashing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

_FALLBACK = "en"
_logger = logging.getLogger(__name__)


def pick_locale(field: dict[str, str], locale: str, fallback: str = _FALLBACK) -> str:
    """Resolve a localized content field, falling back to English then any value."""
    if locale in field:
        return field[locale]
    _logger.warning("Missing %r translation; falling back to %r", locale, fallback)
    if fallback in field:
        return field[fallback]
    values = list(field.values())
    if not values:
        raise ValueError(f"Empty localized field; cannot resolve locale {locale!r}")
    return values[0]


@dataclass(frozen=True)
class Translator:
    """Resolves UI string keys per locale with English fallback."""

    tables: dict[str, dict[str, str]]

    def t(self, key: str, locale: str) -> str:
        """Translate `key` for `locale`; fall back to English, then the key itself."""
        table = self.tables.get(locale, {})
        if key in table:
            return table[key]
        english = self.tables.get(_FALLBACK, {})
        if key in english:
            _logger.warning("Missing %r UI string for %r; using English", key, locale)
            return english[key]
        _logger.warning("Missing UI string %r for %r and English fallback; using key", key, locale)
        return key
