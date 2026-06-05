from typehero.content_loader import load_principles
from typehero.paths import content_dir


def test_bundled_principles_load_and_are_bilingual():
    principles = load_principles(content_dir() / "principles.yaml")
    assert len(principles) >= 6
    for entry in principles:
        assert entry.get("en")
        assert entry.get("ru")
