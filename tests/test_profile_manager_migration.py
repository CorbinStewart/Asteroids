from pathlib import Path
import json

from profile_manager import ProfileManager, CURRENT_VERSION


def test_migrate_version0(tmp_path: Path):
    path = tmp_path / "profile.json"
    legacy = {
        "scores": {"high_score": 500},
        "settings": {"player_name": "Vector"},
    }
    path.write_text(json.dumps(legacy))

    manager = ProfileManager(path=path)
    manager.load()

    assert manager.data["version"] == CURRENT_VERSION
    assert manager.high_score == 500
    assert manager.settings()["player_name"].startswith("Vector")
    assert "milestones" in manager.data["scores"]


def test_migrate_version1_without_milestones(tmp_path: Path):
    path = tmp_path / "profile.json"
    legacy = {
        "version": 1,
        "scores": {"high_score": 1234, "leaderboard": []},
        "settings": {"music_volume": 0.5},
    }
    path.write_text(json.dumps(legacy))

    manager = ProfileManager(path=path)
    manager.load()

    assert manager.data["version"] == CURRENT_VERSION
    milestones = manager.data["scores"]["milestones"]
    assert milestones["total_bombs_used"] == 0
    assert manager.settings()["music_volume"] == 0.5
