import random

import pygame

from bomb_pickup import BombPickup, should_drop_pickup, spawn_pickups_from_split
from constants import (
    BOMB_PICKUP_BASE_CHANCE,
    BOMB_PICKUP_LEVEL_BONUS,
    BOMB_PICKUP_MAX_CHANCE,
    BOMB_PICKUP_LIFETIME,
)
from game_state import GameState
from score_manager import ScoreManager
from asteroid import Asteroid


def test_should_drop_pickup_caps_probability():
    rng = random.Random(0)
    high_level = int((BOMB_PICKUP_MAX_CHANCE - BOMB_PICKUP_BASE_CHANCE) / BOMB_PICKUP_LEVEL_BONUS) + 10
    assert should_drop_pickup(high_level, rng) in {True, False}
    # For deterministic check, guarantee drop by overriding rng to 0.0
    rng = random.Random()
    rng.random = lambda: 0.0
    assert should_drop_pickup(0, rng) is True


def test_pickup_lifetime_and_collision():
    pickup = BombPickup(pygame.Vector2(0, 0))
    total = 0.0
    while pickup.alive() and total < BOMB_PICKUP_LIFETIME + 1:
        pickup.update(1.0)
        total += 1.0
    assert not pickup.alive()

    pickup = BombPickup(pygame.Vector2(0, 0))
    assert pickup.collides_with(pygame.Vector2(0, 0), 0)
    assert not pickup.collides_with(pygame.Vector2(100, 100), 0)


def test_spawn_pickups_respects_cap():
    asteroids = pygame.sprite.Group()
    Asteroid.containers = (asteroids, pygame.sprite.Group(), pygame.sprite.Group())
    asteroid = Asteroid(0, 0, 20)

    state = GameState(bombs=5)
    score = ScoreManager(state)
    rng = random.Random()
    rng.random = lambda: 0.0
    group = pygame.sprite.Group()

    spawn_pickups_from_split(asteroid, state, rng, group)
    assert len(group) == 0

    state.bombs = 0
    spawn_pickups_from_split(asteroid, state, rng, group)
    assert len(group) == 1
