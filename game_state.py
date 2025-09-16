from dataclasses import dataclass

from constants import (
    LEVEL_CLEAR_BONUS,
    LIFE_ICON_FLICKER_DURATION,
    PLAYER_START_LIVES,
)


@dataclass
class GameState:
    lives: int = PLAYER_START_LIVES
    bombs: int = 0
    score: int = 0
    high_score: int = 0
    level_index: int = 0
    life_loss_active: bool = False
    life_loss_elapsed: float = 0.0
    life_lost_this_level: bool = False

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

    def apply_level_bonus(self, level_number: int) -> int:
        bonus = LEVEL_CLEAR_BONUS * level_number
        if self.life_lost_this_level:
            bonus //= 2
        self.add_score(bonus)
        return bonus

    def update(self, dt: float) -> None:
        if self.life_loss_active:
            self.life_loss_elapsed += dt
            if self.life_loss_elapsed >= LIFE_ICON_FLICKER_DURATION:
                self.life_loss_active = False
                self.life_loss_elapsed = 0.0
