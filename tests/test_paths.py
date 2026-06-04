from pathlib import Path

from typehero.paths import content_dir, profile_path


def test_content_dir_env_override(monkeypatch):
    monkeypatch.setenv("TYPEHERO_CONTENT_DIR", "/tmp/typehero-content")
    assert content_dir() == Path("/tmp/typehero-content")


def test_content_dir_defaults_to_repo_content(monkeypatch):
    monkeypatch.delenv("TYPEHERO_CONTENT_DIR", raising=False)
    assert content_dir().name == "content"


def test_profile_path_uses_xdg_config_home(monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/cfg")
    assert profile_path() == Path("/tmp/cfg/typehero/profile.json")


def test_profile_path_defaults_to_home_config(monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    assert profile_path() == Path.home() / ".config" / "typehero" / "profile.json"
