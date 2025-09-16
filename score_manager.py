from __future__ import annotations

from dataclasses import dataclass

from constants import LEVEL_CLEAR_BONUS
from game_state import GameState


@dataclass
class ScoreManager:
    state: GameState

    def add_points(self, amount: int) -> None:
        if amount <= 0:
            return
        self.state.score += amount
        if self.state.score > self.state.high_score:
            self.state.high_score = self.state.score

    def add_asteroid_points(self, asteroid) -> None:
        self.add_points(asteroid.score_value())

    def apply_level_bonus(self) -> int:
        level_number = self.state.level_index + 1
        bonus = LEVEL_CLEAR_BONUS * level_number
        if self.state.life_lost_this_level:
            bonus //= 2
        self.add_points(bonus)
        return bonus

    def save_high_score(self) -> None:
        """Placeholder for future persistence."""

    def load_high_score(self) -> None:
        """Placeholder for future persistence."""
