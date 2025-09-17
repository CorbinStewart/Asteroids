from __future__ import annotations

import random

import pygame

from typing import Iterable, TYPE_CHECKING

from constants import (
    ASTEROID_MIN_RADIUS,
    BOMB_SLOWMO_MIN_SCALE,
    BOMB_WAVE_DURATION,
    BOMB_WAVE_MAX_RADIUS,
)
from game_clock import GameClock
from bomb_pickup import spawn_pickups_from_split

if TYPE_CHECKING:
    from asteroid import Asteroid
    from score_manager import ScoreManager


class BombWave:
    def __init__(self, origin: pygame.Vector2, clock: GameClock) -> None:
        self.origin = pygame.Vector2(origin)
        self._clock = clock
        self.elapsed = 0.0
        self.radius = 0.0
        self.duration = BOMB_WAVE_DURATION
        self.max_radius = BOMB_WAVE_MAX_RADIUS
        self.active = True
        self._clock.set_time_scale(BOMB_SLOWMO_MIN_SCALE)
        self._processed_ids: set[int] = set()

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.duration) if self.duration > 0 else 1.0
        self.radius = self.max_radius * progress
        time_scale = BOMB_SLOWMO_MIN_SCALE + (1.0 - BOMB_SLOWMO_MIN_SCALE) * progress
        self._clock.set_time_scale(time_scale)

    def finish(self) -> None:
        if not self.active:
            return
        self.active = False
        self.radius = self.max_radius
        self._clock.reset_time_scale()
        self._processed_ids.clear()

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(self.origin.x), int(self.origin.y)),
            int(self.radius),
            2,
        )

    def contains_sprite(self, sprite: "Asteroid") -> bool:
        if not self.active:
            return False
        distance = sprite.position.distance_to(self.origin)
        return distance - sprite.radius <= self.radius

    def has_processed(self, sprite: "Asteroid") -> bool:
        return id(sprite) in self._processed_ids

    def mark_processed(self, sprite: "Asteroid") -> None:
        self._processed_ids.add(id(sprite))

    def mark_spawned(self, sprite: "Asteroid") -> None:
        self.mark_processed(sprite)


class BombController:
    def __init__(self, clock: GameClock) -> None:
        self._clock = clock
        self.wave: BombWave | None = None

    def trigger(self, origin: pygame.Vector2) -> None:
        if self.wave and self.wave.active:
            self.wave.finish()
        self.wave = BombWave(origin, self._clock)

    def update(self, dt: float) -> None:
        if not self.wave:
            return
        self.wave.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.wave:
            self.wave.draw(surface)

    def current_wave(self) -> BombWave | None:
        return self.wave

    def apply_wave_effects(
        self,
        asteroids: Iterable["Asteroid"],
        score_manager: "ScoreManager",
        state,
        pickups,
        rng: random.Random,
    ) -> None:
        wave = self.current_wave()
        if not wave:
            return
        asteroid_group = list(asteroids)
        for asteroid in asteroid_group:
            if not wave.contains_sprite(asteroid):
                continue
            if wave.has_processed(asteroid):
                continue
            wave.mark_processed(asteroid)
            if hasattr(state, "asteroids_destroyed"):
                state.asteroids_destroyed += 1
            score_manager.add_asteroid_points(asteroid)
            spawn_pickups_from_split(asteroid, state, rng, pickups)
            if asteroid.radius <= ASTEROID_MIN_RADIUS:
                asteroid.kill()
                continue
            before_ids = {id(a) for a in asteroids}
            asteroid.split()
            if wave.active:
                after_ids = {id(a) for a in asteroids}
                new_ids = after_ids - before_ids
                for spawned in asteroids:
                    if id(spawned) in new_ids:
                        wave.mark_spawned(spawned)
        if wave.elapsed >= wave.duration:
            wave.finish()
            self.wave = None
