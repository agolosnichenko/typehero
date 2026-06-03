import logging

from typer.localization import Translator, pick_locale


def test_pick_locale_returns_requested():
    field = {"ru": "Привет", "en": "Hello"}
    assert pick_locale(field, "ru") == "Привет"


def test_pick_locale_falls_back_to_english(caplog):
    field = {"en": "Hello"}
    with caplog.at_level(logging.WARNING):
        assert pick_locale(field, "ru") == "Hello"
    assert "ru" in caplog.text


def test_pick_locale_falls_back_to_any_when_no_english():
    field = {"de": "Hallo"}
    assert pick_locale(field, "ru") == "Hallo"


def test_translator_resolves_key():
    t = Translator(tables={"en": {"menu.start": "Start"}, "ru": {"menu.start": "Старт"}})
    assert t.t("menu.start", "ru") == "Старт"


def test_translator_missing_key_falls_back_to_english():
    t = Translator(tables={"en": {"menu.start": "Start"}, "ru": {}})
    assert t.t("menu.start", "ru") == "Start"


def test_translator_missing_everywhere_returns_key():
    t = Translator(tables={"en": {}})
    assert t.t("menu.unknown", "ru") == "menu.unknown"
