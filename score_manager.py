from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from constants import LEVEL_CLEAR_BONUS
from game_state import GameState


class AsteroidScoring(Protocol):
    def score_value(self) -> int:
        ...


@dataclass
class ScoreManager:
    state: GameState
    profile: "ProfileManager" | None = None

    def add_points(self, amount: int) -> None:
        if amount <= 0:
            return
        self.state.score += amount
        previous_high = self.state.high_score
        if self.state.score > self.state.high_score:
            self.state.high_score = self.state.score
            if (
                self.state.initial_high_score > 0
                and previous_high >= self.state.initial_high_score
                and not self.state.high_score_beaten
            ):
                self.state.start_high_score_flash()
            if self.profile is not None:
                self.profile.set_high_score(self.state.high_score)

    def add_asteroid_points(self, asteroid: "AsteroidScoring") -> None:
        self.add_points(asteroid.score_value())

    def add_bombs(self, count: int = 1) -> None:
        if count <= 0:
            return
        self.state.add_bombs(count)

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
