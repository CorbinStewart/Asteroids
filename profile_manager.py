from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict

SAVE_DIR = Path("save")
PROFILE_FILE = SAVE_DIR / "profile.json"
CURRENT_VERSION = 2


DEFAULT_PROFILE: Dict[str, Any] = {
    "version": CURRENT_VERSION,
    "scores": {
        "high_score": 0,
        "leaderboard": [],  # list of dicts: {"name": str, "score": int, "level": int, ...}
        "milestones": {
            "total_asteroids_destroyed": 0,
            "total_bombs_used": 0,
            "total_pickups_collected": 0,
            "total_time_survived": 0.0,
        },
    },
    "settings": {
        "music_volume": 1.0,
        "music_volume_previous": 1.0,
        "sfx_volume": 1.0,
        "sfx_volume_previous": 1.0,
        "screen_shake": 1.0,
        "player_name": "ACE",
    },
}


def _clamp_float(value: Any, minimum: float, maximum: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return minimum
    return max(minimum, min(maximum, result))


@dataclass
class ProfileManager:
    path: Path = PROFILE_FILE
    data: Dict[str, Any] = field(default_factory=lambda: json.loads(json.dumps(DEFAULT_PROFILE)))

    def load(self) -> None:
        if not self.path.exists():
            self.data = json.loads(json.dumps(DEFAULT_PROFILE))
            return
        try:
            with self.path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (json.JSONDecodeError, OSError):
            self.data = json.loads(json.dumps(DEFAULT_PROFILE))
            return
        version = loaded.get("version")
        if version != CURRENT_VERSION:
            self.data = self._migrate(loaded, version)
        else:
            self.data = loaded
        self._apply_defaults()

    def save(self) -> None:
        self._apply_defaults()
        target_dir = self.path.parent if self.path.parent != Path("") else SAVE_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".tmp")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with temp_path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
        temp_path.replace(self.path)

    def _apply_defaults(self) -> None:
        def merge(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
            for key, value in src.items():
                if isinstance(value, dict):
                    node = dst.setdefault(key, {})
                    if isinstance(node, dict):
                        merge(node, value)
                    else:
                        dst[key] = json.loads(json.dumps(value))
                else:
                    dst.setdefault(key, value)
        merge(self.data, DEFAULT_PROFILE)
        self.data["version"] = CURRENT_VERSION

    def _migrate(self, loaded: Dict[str, Any], version: Any) -> Dict[str, Any]:
        data = json.loads(json.dumps(loaded))
        try:
            current = int(version) if version is not None else 0
        except (TypeError, ValueError):
            current = 0

        if current < 1:
            data = self._migrate_v0_to_v1(data)
            current = 1
        if current < 2:
            data = self._migrate_v1_to_v2(data)
            current = 2
        data["version"] = CURRENT_VERSION
        return data

    @staticmethod
    def _migrate_v0_to_v1(data: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure scores/settings containers exist even if the original file lacked them
        scores = data.setdefault("scores", {})
        scores.setdefault("high_score", 0)
        scores.setdefault("leaderboard", [])
        data.setdefault("settings", {})
        return data

    @staticmethod
    def _migrate_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
        scores = data.setdefault("scores", {})
        scores.setdefault(
            "milestones",
            {
                "total_asteroids_destroyed": 0,
                "total_bombs_used": 0,
                "total_pickups_collected": 0,
                "total_time_survived": 0.0,
            },
        )
        settings = data.setdefault("settings", {})
        settings.setdefault("music_volume", 1.0)
        settings.setdefault("music_volume_previous", 1.0)
        settings.setdefault("sfx_volume", 1.0)
        settings.setdefault("sfx_volume_previous", 1.0)
        settings.setdefault("screen_shake", 1.0)
        settings.setdefault("player_name", "ACE")
        return data

    @property
    def high_score(self) -> int:
        return int(self.data["scores"].get("high_score", 0))

    def set_high_score(self, value: int) -> None:
        self.data.setdefault("scores", {})["high_score"] = max(0, int(value))

    def settings(self) -> Dict[str, Any]:
        return self.data.setdefault("settings", {})

    def update_settings(self, **kwargs: Any) -> None:
        settings = self.settings()
        if "music_volume" in kwargs:
            settings["music_volume"] = _clamp_float(kwargs["music_volume"], 0.0, 1.0)
        if "music_volume_previous" in kwargs:
            settings["music_volume_previous"] = _clamp_float(kwargs["music_volume_previous"], 0.0, 1.0)
        if "sfx_volume" in kwargs:
            settings["sfx_volume"] = _clamp_float(kwargs["sfx_volume"], 0.0, 1.0)
        if "sfx_volume_previous" in kwargs:
            settings["sfx_volume_previous"] = _clamp_float(kwargs["sfx_volume_previous"], 0.0, 1.0)
        if "screen_shake" in kwargs:
            settings["screen_shake"] = _clamp_float(kwargs["screen_shake"], 0.0, 1.0)
        if "player_name" in kwargs:
            name = str(kwargs["player_name"]).strip() or "ACE"
            settings["player_name"] = name[:10].rstrip() or "ACE"

    def leaderboard(self) -> list[Dict[str, Any]]:
        return self.data.setdefault("scores", {}).setdefault("leaderboard", [])

    def submit_score(
        self,
        name: str,
        score: int,
        level: int,
        limit: int = 5,
    ) -> None:
        entry = {
            "name": str(name)[:10] or "ACE",
            "score": max(0, int(score)),
            "level": max(0, int(level)),
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        }
        board = self.leaderboard()
        board.append(entry)
        board.sort(key=lambda e: e.get("score", 0), reverse=True)
        del board[limit:]
        if entry["score"] > self.high_score:
            self.set_high_score(entry["score"])

    def record_milestones(
        self,
        *,
        asteroids_destroyed: int = 0,
        bombs_used: int = 0,
        pickups_collected: int = 0,
        time_survived: float = 0.0,
    ) -> None:
        milestones = self.data.setdefault("scores", {}).setdefault("milestones", {})
        milestones["total_asteroids_destroyed"] = milestones.get("total_asteroids_destroyed", 0) + max(0, asteroids_destroyed)
        milestones["total_bombs_used"] = milestones.get("total_bombs_used", 0) + max(0, bombs_used)
        milestones["total_pickups_collected"] = milestones.get("total_pickups_collected", 0) + max(0, pickups_collected)
        milestones["total_time_survived"] = milestones.get("total_time_survived", 0.0) + max(0.0, time_survived)
