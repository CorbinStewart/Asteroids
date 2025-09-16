from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from constants import LEVEL_MESSAGE_DURATION, LEVEL_DEFINITIONS
from asteroidfield import AsteroidField
from game_state import GameState
from score_manager import ScoreManager


@dataclass
class LevelTransition:
    next_level: int
    timer: float = 0.0
    phase: str = "top"
    header: str = field(default_factory=lambda: random.choice(
        ["Good Work!", "Nice Shooting!", "Level Complete!"]
    ))


class LevelManager:
    def __init__(
        self,
        state: GameState,
        asteroid_field: AsteroidField,
        score_manager: ScoreManager,
    ) -> None:
        self.state = state
        self.asteroid_field = asteroid_field
        self.score_manager = score_manager
        self.transition: Optional[LevelTransition] = None
        self.total_levels = len(LEVEL_DEFINITIONS)

    def configure_level(self, index: int) -> None:
        self.state.reset_for_level(index)
        config = LEVEL_DEFINITIONS[index]
        self.asteroid_field.configure_level(
            config["spawn_total"],
            config["max_active"],
            config["speed_multiplier"],
        )

    def start_transition(self, next_level: int) -> None:
        self.transition = LevelTransition(next_level=next_level)

    def update(self, dt: float) -> None:
        if not self.transition:
            return
        self.transition.timer += dt
        if self.transition.phase == "top":
            if self.transition.timer >= LEVEL_MESSAGE_DURATION:
                self.transition.phase = "bottom"
                self.transition.timer = 0.0
        elif self.transition.phase == "bottom":
            if self.transition.timer >= LEVEL_MESSAGE_DURATION:
                self.configure_level(self.transition.next_level)
                self.transition = None

    def should_start_transition(self) -> bool:
        if self.transition is not None:
            return False
        return self.asteroid_field.level_complete()

    def levels_remaining(self) -> bool:
        return self.state.level_index + 1 < self.total_levels

    def apply_level_completion(self) -> None:
        self.score_manager.apply_level_bonus()
