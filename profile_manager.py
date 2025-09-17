from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict

SAVE_DIR = Path("save")
PROFILE_FILE = SAVE_DIR / "profile.json"
CURRENT_VERSION = 1


DEFAULT_PROFILE: Dict[str, Any] = {
    "version": CURRENT_VERSION,
    "scores": {
        "high_score": 0,
        "leaderboard": [],  # list of dicts: {"score": int, "level": int, "timestamp": str}
    },
    "settings": {
        "music_volume": 1.0,
        "sfx_volume": 1.0,
        "screen_shake": 1.0,
    },
}


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
        # Future version handling; currently just reset to defaults
        return json.loads(json.dumps(DEFAULT_PROFILE))

    @property
    def high_score(self) -> int:
        return int(self.data["scores"].get("high_score", 0))

    def set_high_score(self, value: int) -> None:
        self.data.setdefault("scores", {})["high_score"] = max(0, int(value))

    def settings(self) -> Dict[str, Any]:
        return self.data.setdefault("settings", {})

    def leaderboard(self) -> list[Dict[str, Any]]:
        return self.data.setdefault("scores", {}).setdefault("leaderboard", [])

    def submit_score(self, score: int, level: int, bombs_used: int = 0, limit: int = 10) -> None:
        entry = {
            "score": max(0, int(score)),
            "level": max(0, int(level)),
            "bombs_used": max(0, int(bombs_used)),
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        }
        board = self.leaderboard()
        board.append(entry)
        board.sort(key=lambda e: e.get("score", 0), reverse=True)
        del board[limit:]
        if entry["score"] > self.high_score:
            self.set_high_score(entry["score"])
