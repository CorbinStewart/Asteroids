import random

import pygame

from bomb_wave import BombController, BombWave
from game_clock import GameClock
from constants import (
    ASTEROID_MIN_RADIUS,
    ASTEROID_SCORE_LARGE,
    ASTEROID_SCORE_SMALL,
    BOMB_SLOWMO_MIN_SCALE,
    BOMB_WAVE_DURATION,
    BOMB_WAVE_MAX_RADIUS,
)
from asteroid import Asteroid
from score_manager import ScoreManager
from game_state import GameState


def test_bomb_wave_time_scale_and_completion():
    clock = GameClock()
    controller = BombController(clock)

    controller.trigger(pygame.Vector2(100, 100))
    wave = controller.current_wave()
    assert wave is not None
    assert clock.time_scale == BOMB_SLOWMO_MIN_SCALE

    score = ScoreManager(GameState())
    controller.update(BOMB_WAVE_DURATION / 2)
    wave = controller.current_wave()
    assert wave is not None
    assert BOMB_SLOWMO_MIN_SCALE <= clock.time_scale <= 1.0
    assert wave.radius > 0

    controller.update(BOMB_WAVE_DURATION)
    controller.apply_wave_effects([], score, GameState(), pygame.sprite.Group(), random.Random())
    assert controller.current_wave() is None
    assert clock.time_scale == 1.0


def test_bomb_wave_radius_reaches_max():
    clock = GameClock()
    wave = BombWave(pygame.Vector2(0, 0), clock)
    wave.update(BOMB_WAVE_DURATION)
    assert abs(wave.radius - BOMB_WAVE_MAX_RADIUS) < 1e-3


def _setup_asteroid_groups():
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    Asteroid.containers = (asteroids, updatable, drawable)
    return asteroids


def test_wave_destroys_small_asteroid_and_awards_points():
    clock = GameClock()
    controller = BombController(clock)
    state = GameState()
    score = ScoreManager(state)
    asteroids = _setup_asteroid_groups()
    pickups = pygame.sprite.Group()
    rng = random.Random()

    small = Asteroid(0, 0, ASTEROID_MIN_RADIUS)

    controller.trigger(pygame.Vector2(0, 0))
    controller.update(0.5)
    controller.apply_wave_effects(asteroids, score, state, pickups, rng)

    assert not small.alive()
    assert state.score == ASTEROID_SCORE_SMALL


def test_wave_only_reduces_large_asteroid_once():
    clock = GameClock()
    controller = BombController(clock)
    state = GameState()
    score = ScoreManager(state)
    asteroids = _setup_asteroid_groups()
    pickups = pygame.sprite.Group()
    rng = random.Random()

    large = Asteroid(0, 0, ASTEROID_MIN_RADIUS * 3)

    controller.trigger(pygame.Vector2(0, 0))
    controller.update(0.5)
    controller.apply_wave_effects(asteroids, score, state, pickups, rng)

    spawned = list(asteroids)
    assert large not in spawned
    assert len(spawned) == 2
    assert all(a.radius < large.radius for a in spawned)
    assert state.score == ASTEROID_SCORE_LARGE

    # Apply again; the new fragments should not be processed further by the same wave.
    controller.apply_wave_effects(asteroids, score, state, pickups, rng)
    assert len([a for a in asteroids if a.alive()]) == 2


def test_wave_can_spawn_pickup_when_drop_occurs():
    clock = GameClock()
    controller = BombController(clock)
    state = GameState(bombs=0)
    score = ScoreManager(state)
    asteroids = _setup_asteroid_groups()
    pickups = pygame.sprite.Group()
    rng = random.Random()
    rng.random = lambda: 0.0  # ensure drop

    small = Asteroid(0, 0, ASTEROID_MIN_RADIUS)

    controller.trigger(pygame.Vector2(0, 0))
    controller.update(0.5)
    controller.apply_wave_effects(asteroids, score, state, pickups, rng)

    assert len(pickups) == 1
