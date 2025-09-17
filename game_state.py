from dataclasses import dataclass, field

from constants import (
    LIFE_ICON_FLICKER_DURATION,
    PLAYER_START_BOMBS,
    PLAYER_START_LIVES,
)


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
    high_score_flash_timer: float = 0.0
    leaderboard: list[dict[str, int]] = field(default_factory=list)

    def reset_for_level(self, level_index: int) -> None:
        """Prepare state for the given level."""
        self.level_index = level_index
        self.life_lost_this_level = False
        self.life_loss_active = False
        self.life_loss_elapsed = 0.0

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

    def trigger_high_score_flash(self, duration: float) -> None:
        self.high_score_flash_timer = max(self.high_score_flash_timer, duration)

    def update(self, dt: float) -> None:
        if self.life_loss_active:
            self.life_loss_elapsed += dt
            if self.life_loss_elapsed >= LIFE_ICON_FLICKER_DURATION:
                self.life_loss_active = False
                self.life_loss_elapsed = 0.0
        if self.bomb_flash_timer > 0:
            self.bomb_flash_timer = max(0.0, self.bomb_flash_timer - dt)
        if self.high_score_flash_timer > 0:
            self.high_score_flash_timer = max(0.0, self.high_score_flash_timer - dt)
