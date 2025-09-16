from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from asteroid import Asteroid
from constants import (
    ASTEROID_KINDS,
    ASTEROID_MAX_RADIUS,
    ASTEROID_MIN_RADIUS,
    ASTEROID_SPAWN_RATE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

if TYPE_CHECKING:
    from pygame.math import Vector2
    from pygame.sprite import Group


class AsteroidField(pygame.sprite.Sprite):
    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self, asteroids_group: Group) -> None:
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer: float = 0.0
        self.asteroids_group = asteroids_group
        self.spawn_limit: int = 0
        self.max_active: int = 0
        self.spawned_this_level: int = 0
        self.speed_multiplier: float = 1.0

    def spawn(self, radius: float, position: pygame.Vector2, velocity: pygame.Vector2) -> None:
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity
        self.spawned_this_level += 1

    def configure_level(self, spawn_limit: int, max_active: int, speed_multiplier: float) -> None:
        self.spawn_limit = max(0, spawn_limit)
        self.max_active = max(1, max_active)
        self.spawned_this_level = 0
        self.spawn_timer = 0.0
        self.speed_multiplier = max(0.1, speed_multiplier)

    def level_complete(self) -> bool:
        if self.spawn_limit == 0:
            return False
        return (
            self.spawned_this_level >= self.spawn_limit
            and len(self.asteroids_group) == 0
        )

    def update(self, dt: float) -> None:
        if self.spawn_limit == 0:
            return
        self.spawn_timer += dt
        if self.spawned_this_level >= self.spawn_limit:
            return
        if len(self.asteroids_group) >= self.max_active:
            return
        if self.spawn_timer > ASTEROID_SPAWN_RATE:
            self.spawn_timer = 0

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            speed = random.randint(40, 100) * self.speed_multiplier
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            kind = random.randint(1, ASTEROID_KINDS)
            self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity)
