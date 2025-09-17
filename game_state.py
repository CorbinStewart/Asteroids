from dataclasses import dataclass, field
from typing import Any

from constants import (
    LIFE_ICON_FLICKER_DURATION,
    PLAYER_START_BOMBS,
    PLAYER_START_LIVES,
    HIGH_SCORE_FLASH_PERIOD,
)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


@dataclass
class GameState:
    lives: int = PLAYER_START_LIVES
    bombs: int = PLAYER_START_BOMBS
    score: int = 0
    high_score: int = 0
    level_index: int = 0
    life_loss_active: bool = False
    life_loss_elapsed: float = 0.0
    life_lost_this_level: bool = False
    bomb_flash_timer: float = 0.0
    bomb_cap: int = 5
    bombs_used: int = 0
    high_score_flash_elapsed: float = 0.0
    high_score_beaten: bool = False
    initial_high_score: int = 0
    leaderboard: list[dict[str, int]] = field(default_factory=list)
    run_time: float = 0.0
    pickups_collected: int = 0
    asteroids_destroyed: int = 0
    music_volume: float = 1.0
    sfx_volume: float = 1.0
    screen_shake_scale: float = 1.0
    player_name: str = "ACE"

    def reset_for_level(self, level_index: int) -> None:
        """Prepare state for the given level."""
        self.level_index = level_index
        self.life_lost_this_level = False
        self.life_loss_active = False
        self.life_loss_elapsed = 0.0
        self.high_score_beaten = False
        self.high_score_flash_elapsed = 0.0
        self.bombs_used = 0
        self.pickups_collected = 0
        self.asteroids_destroyed = 0

    def lose_life(self) -> None:
        if self.lives > 0:
            self.lives -= 1
        self.life_loss_active = True
        self.life_loss_elapsed = 0.0
        self.life_lost_this_level = True

    def add_score(self, amount: int) -> None:
        if amount <= 0:
            return
        self.score += amount
        if self.score > self.high_score:
            self.high_score = self.score

    def can_use_bomb(self) -> bool:
        return self.bombs > 0

    def use_bomb(self) -> bool:
        if not self.can_use_bomb():
            return False
        self.bombs -= 1
        self.bombs_used += 1
        return True

    def add_bombs(self, count: int = 1) -> None:
        if count <= 0:
            return
        self.bombs = min(self.bomb_cap, self.bombs + count)

    def trigger_bomb_flash(self, duration: float) -> None:
        self.bomb_flash_timer = max(self.bomb_flash_timer, duration)

    def start_high_score_flash(self) -> None:
        if not self.high_score_beaten:
            self.high_score_beaten = True
            self.high_score_flash_elapsed = 0.0

    def update(self, dt: float) -> None:
        if self.life_loss_active:
            self.life_loss_elapsed += dt
            if self.life_loss_elapsed >= LIFE_ICON_FLICKER_DURATION:
                self.life_loss_active = False
                self.life_loss_elapsed = 0.0
        if self.bomb_flash_timer > 0:
            self.bomb_flash_timer = max(0.0, self.bomb_flash_timer - dt)
        if self.high_score_beaten:
            self.high_score_flash_elapsed += dt
        self.run_time += dt

    def apply_settings(self, settings: dict[str, Any]) -> None:
        self.music_volume = _clamp(float(settings.get("music_volume", self.music_volume)), 0.0, 1.0)
        self.sfx_volume = _clamp(float(settings.get("sfx_volume", self.sfx_volume)), 0.0, 1.0)
        self.screen_shake_scale = _clamp(float(settings.get("screen_shake", self.screen_shake_scale)), 0.0, 1.0)
        name = str(settings.get("player_name", self.player_name)).strip() or "ACE"
        self.player_name = name[:10].rstrip() or "ACE"
