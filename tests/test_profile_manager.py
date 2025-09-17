import json
from pathlib import Path

import pytest

from profile_manager import ProfileManager, DEFAULT_PROFILE, CURRENT_VERSION


def test_load_missing_file_uses_defaults(tmp_path: Path):
    manager = ProfileManager(path=tmp_path / "profile.json")
    manager.load()
    assert manager.high_score == 0
    assert manager.data["version"] == CURRENT_VERSION
    assert manager.data["settings"]["music_volume"] == DEFAULT_PROFILE["settings"]["music_volume"]


def test_save_and_reload_profile(tmp_path: Path):
    path = tmp_path / "profile.json"
    manager = ProfileManager(path=path)
    manager.set_high_score(1234)
    manager.save()

    reloaded = ProfileManager(path=path)
    reloaded.load()
    assert reloaded.high_score == 1234


def test_corrupt_file_resets_to_defaults(tmp_path: Path):
    path = tmp_path / "profile.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("not valid json")

    manager = ProfileManager(path=path)
    manager.load()
    assert manager.data == DEFAULT_PROFILE or manager.high_score == 0


def test_save_creates_directory(tmp_path: Path):
    save_dir = tmp_path / "nested"
    path = save_dir / "profile.json"
    manager = ProfileManager(path=path)
    manager.set_high_score(42)
    manager.save()
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["scores"]["high_score"] == 42


def test_submit_score_updates_leaderboard(tmp_path: Path):
    path = tmp_path / "profile.json"
    manager = ProfileManager(path=path)
    manager.submit_score(500, 2, bombs_used=1)
    manager.submit_score(1200, 4, bombs_used=0)
    manager.submit_score(800, 3, bombs_used=2)
    manager.save()

    reloaded = ProfileManager(path=path)
    reloaded.load()
    board = reloaded.leaderboard()
    assert board[0]["score"] == 1200
    assert board[1]["score"] == 800
    assert "timestamp" in board[0]
    assert reloaded.high_score == 1200
