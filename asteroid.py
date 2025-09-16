from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from circleshape import CircleShape
from constants import (
    ASTEROID_MIN_RADIUS,
    ASTEROID_SCORE_LARGE,
    ASTEROID_SCORE_MEDIUM,
    ASTEROID_SCORE_SMALL,
)

if TYPE_CHECKING:
    from pygame import Surface

class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: float) -> None:
        super().__init__(x, y, radius)
        self.radius = radius
    
    # Drawing asteroid sprite
    def draw(self, screen: Surface) -> None:
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    # Adding asteroid movement
    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.wrap_position()

    def score_value(self) -> int:
        if self.radius > ASTEROID_MIN_RADIUS * 2:
            return ASTEROID_SCORE_LARGE
        if self.radius > ASTEROID_MIN_RADIUS:
            return ASTEROID_SCORE_MEDIUM
        return ASTEROID_SCORE_SMALL

    # Asteroid spliting logic
    def split(self) -> None:
        old_radius = self.radius
        self.kill()
        if old_radius <= ASTEROID_MIN_RADIUS:
            return
        random_angle = random.uniform(20, 50)
        v1 = self.velocity.rotate(random_angle)
        v2 = self.velocity.rotate(-random_angle)
        
        new_radius = old_radius - ASTEROID_MIN_RADIUS
        
        asteroid_1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid_2 = Asteroid(self.position.x, self.position.y, new_radius)
        
        asteroid_1.velocity = v1 * 1.2
        asteroid_2.velocity = v2 * 1.2
