from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from utils import wrap_position as wrap_position_helper

if TYPE_CHECKING:
    from pygame import Surface

# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, radius: float) -> None:
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(self.containers)  # type: ignore[arg-type]
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen: Surface) -> None:
        # sub-classes must override
        pygame.draw.polygon(screen, "white", self.triangle(), 2)

    def update(self, dt: float) -> None:
        # sub-classes must override
        pass

    # Adding collision check to sprites
    def collision_check(self, other: "CircleShape") -> bool:
        distance = self.position.distance_to(other.position)
        return distance <= self.radius + other.radius

    def wrap_position(self) -> None:
        wrap_position_helper(self.position, self.radius)
