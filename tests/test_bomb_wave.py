import random

import pygame

import bomb_wave as bomb_wave_module
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
    assert state.asteroids_destroyed == 1


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
    assert state.asteroids_destroyed == 1

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
    assert state.asteroids_destroyed == 1


def test_wave_triggers_audio_and_fx_hooks(monkeypatch):
    clock = GameClock()
    controller = BombController(clock)
    state = GameState()
    score = ScoreManager(state)
    asteroids = _setup_asteroid_groups()
    pickups = pygame.sprite.Group()
    rng = random.Random(42)

    Asteroid(0, 0, ASTEROID_MIN_RADIUS * 3)

    class DummyAudio:
        def __init__(self) -> None:
            self.asteroid_hits = 0

        def play_asteroid_hit(self) -> None:
            self.asteroid_hits += 1

    class DummyFX:
        def __init__(self) -> None:
            self.explosions: list[tuple[tuple[float, float], float]] = []

        def spawn_asteroid_explosion(self, position: pygame.Vector2, radius: float) -> None:
            self.explosions.append(((position.x, position.y), radius))

    dummy_audio = DummyAudio()
    dummy_fx = DummyFX()

    monkeypatch.setattr(bomb_wave_module, "get_audio_manager", lambda: dummy_audio)

    controller.trigger(pygame.Vector2(0, 0))
    controller.update(BOMB_WAVE_DURATION * 0.5)
    controller.apply_wave_effects(asteroids, score, state, pickups, rng, fx_manager=dummy_fx)

    assert dummy_audio.asteroid_hits == 1
    assert len(dummy_fx.explosions) == 1
    # Running again during the same wave should not double-trigger for spawned fragments.
    controller.apply_wave_effects(asteroids, score, state, pickups, rng, fx_manager=dummy_fx)
    assert dummy_audio.asteroid_hits == 1
    assert len(dummy_fx.explosions) == 1
