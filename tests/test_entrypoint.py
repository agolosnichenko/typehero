import importlib


def test_main_is_importable():
    module = importlib.import_module("typehero.__main__")
    assert callable(module.main)
