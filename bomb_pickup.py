from __future__ import annotations

import math
import random
from typing import Iterable

import pygame

from constants import (
    BOMB_PICKUP_BASE_CHANCE,
    BOMB_PICKUP_BOB_HEIGHT,
    BOMB_PICKUP_BOB_SPEED,
    BOMB_PICKUP_FLICKER_TIME,
    BOMB_PICKUP_LIFETIME,
    BOMB_PICKUP_LEVEL_BONUS,
    BOMB_PICKUP_MAX_CHANCE,
)
from hud_icons import BombIcon


class BombPickup(pygame.sprite.Sprite):
    def __init__(self, position: pygame.Vector2) -> None:
        super().__init__()
        self.base_position = pygame.Vector2(position)
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = 12
        self.timer = BOMB_PICKUP_LIFETIME
        self.spawn_time = 0.0
        self.visible = True
        self.icon = BombIcon(int(self.radius * 2.6), line_width=3)
        self.image = self._create_surface()
        self.rect = self.image.get_rect(center=self.position)

    def _create_surface(self) -> pygame.Surface:
        return self.icon.create_surface((255, 255, 255), (40, 40, 80))

    def update(self, dt: float) -> None:
        self.spawn_time += dt
        self.timer -= dt
        bob_offset = math.sin(self.spawn_time * BOMB_PICKUP_BOB_SPEED) * BOMB_PICKUP_BOB_HEIGHT
        self.position.y = self.base_position.y + bob_offset
        flicker_phase = self.timer <= BOMB_PICKUP_FLICKER_TIME
        letter_on = True
        if flicker_phase:
            letter_on = int(self.spawn_time * 10) % 2 == 0
        self.image = self.icon.create_surface(
            (220, 50, 50),
            (255, 220, 60) if letter_on else (60, 60, 60),
            None,
        )
        self.visible = True
        self.rect.center = (int(self.position.x), int(self.position.y))
        if self.timer <= 0:
            self.kill()

    def draw(self, surface: pygame.Surface) -> None:
        if self.visible:
            surface.blit(self.image, self.rect)

    def collides_with(self, position: pygame.Vector2, radius: float) -> bool:
        if self.timer <= 0:
            return False
        return self.position.distance_to(position) <= (self.radius + radius)


def should_drop_pickup(level_index: int, rng: random.Random) -> bool:
    chance = BOMB_PICKUP_BASE_CHANCE + level_index * BOMB_PICKUP_LEVEL_BONUS
    chance = min(BOMB_PICKUP_MAX_CHANCE, chance)
    return rng.random() < chance


def spawn_pickups_from_split(
    asteroid: "Asteroid",
    state,
    rng: random.Random,
    group: pygame.sprite.Group,
) -> None:
    bomb_cap = getattr(state, "bomb_cap", 5)
    if state.bombs >= bomb_cap:
        return
    level = getattr(state, "level_index", 0)
    if should_drop_pickup(level, rng):
        pickup = BombPickup(asteroid.position)
        group.add(pickup)
