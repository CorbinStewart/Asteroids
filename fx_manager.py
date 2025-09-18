from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

import pygame

from constants import STATUS_BAR_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT
from screen_shake import ScreenShake


@dataclass
class OverlayFlash:
    color: pygame.Color
    duration: float
    elapsed: float = 0.0
    max_alpha: int = 200

    def active(self) -> bool:
        return self.elapsed < self.duration

    def update(self, dt: float) -> None:
        self.elapsed += dt

    def alpha(self) -> int:
        if self.duration <= 0:
            return 0
        ratio = max(0.0, 1.0 - (self.elapsed / self.duration))
        return int(self.max_alpha * ratio)

    def draw(self, surface: pygame.Surface) -> None:
        alpha = self.alpha()
        if alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        base = pygame.Color(self.color)
        scale = alpha / 255.0
        additive_color = (
            int(base.r * scale),
            int(base.g * scale),
            int(base.b * scale),
            0,
        )
        overlay.fill(additive_color)
        surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


@dataclass
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    lifetime: float
    color: pygame.Color
    radius: float
    elapsed: float = 0.0

    def alive(self) -> bool:
        return self.elapsed < self.lifetime

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.position += self.velocity * dt

    def draw(self, surface: pygame.Surface) -> None:
        if self.lifetime <= 0:
            return
        progress = max(0.0, min(1.0, self.elapsed / self.lifetime))
        alpha = int(self.color.a * (1.0 - progress))
        if alpha <= 0:
            return
        radius = max(1, int(self.radius * (1.0 - 0.6 * progress)))
        color = pygame.Color(self.color)
        color.a = alpha
        pygame.draw.circle(surface, color, (int(self.position.x), int(self.position.y)), radius)


@dataclass
@dataclass
class PowerLine:
    offset_x: float
    width: int
    color: pygame.Color



@dataclass
class PowerRing:
    radius: float
    width: int
    color: pygame.Color


@dataclass
class ActiveRing:
    start_time: float
    config: PowerRing


class PowerUpEffect:
    def __init__(
        self,
        target: Any,
        tint: tuple[int, int, int],
        *,
        duration: float = 1.0,
        rng: random.Random | None = None,
    ) -> None:
        self.target = target
        self.duration = duration
        self.elapsed = 0.0
        self.tint = pygame.Color(*tint, 255)
        self._rng = rng or random.Random()

        self._line_offsets = [-22, -16, -10, -4, 0, 4, 10, 16, 22]
        line_color = pygame.Color(self.tint)
        line_color.a = 200
        self._lines = [PowerLine(offset, 1, pygame.Color(line_color)) for offset in self._line_offsets]
        self._line_height = 18.0
        self._line_start = -8.0
        self._line_end = 44.0
        self._line_period = 0.3

        ring_colors = [pygame.Color(self.tint), pygame.Color(self.tint), pygame.Color(self.tint)]
        ring_colors[0].a = 200
        ring_colors[1].a = 160
        ring_colors[2].a = 120
        self._ring_palette = [PowerRing(radius=32, width=2, color=color) for color in ring_colors]
        self._ring_height_factor = 0.4
        self._ring_travel_time = 0.8
        self._ring_spawn_threshold = 0.33
        self._ring_palette_index = 0
        self._active_rings: list[ActiveRing] = []
        self._spawn_ring(0.0)

    @property
    def finished(self) -> bool:
        return self.elapsed >= self.duration and not self._active_rings

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self._prune_finished_rings()

        if self.elapsed <= self.duration:
            if not self._active_rings:
                self._spawn_ring(self.elapsed)
            else:
                latest = self._active_rings[-1]
                if self._ring_progress(latest, self.elapsed) >= self._ring_spawn_threshold:
                    self._spawn_ring(self.elapsed)

    def _spawn_ring(self, start_time: float) -> None:
        if not self._ring_palette:
            return
        config = self._ring_palette[self._ring_palette_index % len(self._ring_palette)]
        self._ring_palette_index += 1
        ring = PowerRing(radius=config.radius, width=config.width, color=pygame.Color(config.color))
        self._active_rings.append(ActiveRing(start_time=start_time, config=ring))

    def _ring_progress(self, ring: ActiveRing, elapsed_time: float) -> float:
        progress = (elapsed_time - ring.start_time) / self._ring_travel_time
        return max(0.0, min(1.0, progress))

    def _prune_finished_rings(self) -> None:
        self._active_rings = [ring for ring in self._active_rings if (self.elapsed - ring.start_time) < self._ring_travel_time]

    def draw(self, surface: pygame.Surface) -> None:
        anchor = pygame.Vector2(self.target.position.x, self.target.position.y)
        line_phase = (self.elapsed % self._line_period) / self._line_period
        for idx, line in enumerate(self._lines):
            phase = (line_phase + idx * 0.2) % 1.0
            span = self._line_end - self._line_start
            start = self._line_start + span * phase
            end = min(start + self._line_height, self._line_end)
            bottom = anchor - pygame.Vector2(0, start)
            top = anchor - pygame.Vector2(0, end)
            color = pygame.Color(line.color)
            color.a = int(200 * (1.0 - phase))
            if color.a <= 0:
                continue
            pygame.draw.line(
                surface,
                color,
                (int(bottom.x + line.offset_x), int(bottom.y)),
                (int(top.x + line.offset_x), int(top.y)),
                line.width,
            )

        span = self._line_end - self._line_start
        for ring in self._active_rings:
            progress = self._ring_progress(ring, self.elapsed)
            if progress < 0.0:
                continue
            if progress >= 1.0:
                continue
            center_height = self._line_start + span * progress
            center = anchor - pygame.Vector2(0, center_height)
            radius_scale = 1.0 + 0.08 * progress
            radius = ring.config.radius * radius_scale
            rect = pygame.Rect(0, 0, int(radius * 2), int(radius * self._ring_height_factor))
            rect.center = (int(center.x), int(center.y))
            color = pygame.Color(ring.config.color)
            color.a = int(ring.config.color.a * (1.0 - progress))
            if color.a <= 0:
                continue
            pygame.draw.ellipse(surface, color, rect, max(1, ring.config.width))

class FXManager:
    def __init__(self) -> None:
        self.screen_shake = ScreenShake()
        self._flashes: list[OverlayFlash] = []
        self._particles: list[Particle] = []
        self._powerup_effects: list[PowerUpEffect] = []
        self._rng = random.Random()
        self._fireworks_timer = 0.0
        self._fireworks_interval = 0.2
        self._fireworks_accum = 0.0

    def offset(self) -> tuple[int, int]:
        return self.screen_shake.offset()

    def shake(self, duration: float, magnitude: float) -> None:
        self.screen_shake.start(duration, magnitude)

    def trigger_flash(self, color: tuple[int, int, int], duration: float = 0.4, alpha: int = 160) -> None:
        flash = OverlayFlash(pygame.Color(*color), duration, max_alpha=alpha)
        self._flashes.append(flash)

    def spawn_asteroid_explosion(self, position: pygame.Vector2, radius: float) -> None:
        count = max(6, int(radius / 2))
        base_speed = 120 + radius * 2
        for _ in range(count):
            speed = self._rng.uniform(base_speed * 0.6, base_speed * 1.2)
            angle = self._rng.uniform(0, 360)
            velocity = pygame.Vector2(0, -1).rotate(angle) * speed
            lifetime = self._rng.uniform(0.35, 0.6)
            color = pygame.Color(255, 200, 120, 220)
            particle = Particle(pygame.Vector2(position), velocity, lifetime, color, radius=self._rng.uniform(2.5, 4.5))
            self._particles.append(particle)

    def spawn_bomb_activation(self, origin: pygame.Vector2) -> None:
        self.trigger_flash((255, 255, 255), duration=0.3, alpha=80)
        ring_count = 24
        base_speed = 220
        for i in range(ring_count):
            angle = (360 / ring_count) * i + self._rng.uniform(-5, 5)
            velocity = pygame.Vector2(0, -1).rotate(angle) * base_speed
            lifetime = 0.4
            color = pygame.Color(140, 220, 255, 200)
            particle = Particle(pygame.Vector2(origin), velocity, lifetime, color, radius=3.5)
            self._particles.append(particle)

    def spawn_pickup_glow(self, position: pygame.Vector2) -> None:
        for _ in range(12):
            angle = self._rng.uniform(0, 360)
            velocity = pygame.Vector2(0, -1).rotate(angle) * self._rng.uniform(20, 60)
            lifetime = self._rng.uniform(0.35, 0.6)
            color = pygame.Color(255, 255, 200, 160)
            particle = Particle(pygame.Vector2(position), velocity, lifetime, color, radius=2.0)
            self._particles.append(particle)

    def spawn_powerup_trail(self, target: Any, tint: tuple[int, int, int]) -> None:
        effect = PowerUpEffect(target, tint, duration=1.0, rng=self._rng)
        self._powerup_effects.append(effect)

    def spawn_level_transition(self, duration: float = 2.4) -> None:
        self.start_fireworks(duration)

    def update(self, dt: float, real_dt: float | None = None) -> None:
        self.screen_shake.update(real_dt or dt)

        if self._fireworks_timer > 0.0:
            self._fireworks_timer = max(0.0, self._fireworks_timer - dt)
            self._fireworks_accum += dt
            while self._fireworks_accum >= self._fireworks_interval and self._fireworks_timer > 0.0:
                self._fireworks_accum -= self._fireworks_interval
                self._spawn_firework_burst()

        for flash in list(self._flashes):
            flash.update(dt)
            if not flash.active():
                self._flashes.remove(flash)

        alive_particles: list[Particle] = []
        for particle in self._particles:
            particle.update(dt)
            if particle.alive():
                alive_particles.append(particle)
        self._particles = alive_particles

        active_effects: list[PowerUpEffect] = []
        for effect in self._powerup_effects:
            effect.update(dt)
            if not effect.finished:
                active_effects.append(effect)
        self._powerup_effects = active_effects

    def draw_world(self, surface: pygame.Surface) -> None:
        for particle in self._particles:
            particle.draw(surface)
        for effect in self._powerup_effects:
            effect.draw(surface)

    def draw_overlay(self, surface: pygame.Surface) -> None:
        for flash in self._flashes:
            flash.draw(surface)

    def start_fireworks(self, duration: float = 1.2, interval: float = 0.15) -> None:
        self._fireworks_timer = max(0.0, duration)
        self._fireworks_interval = max(0.05, interval)
        self._fireworks_accum = 0.0

    def _spawn_firework_burst(self) -> None:
        x = self._rng.uniform(200, SCREEN_WIDTH - 200)
        y = self._rng.uniform(STATUS_BAR_HEIGHT + 80, SCREEN_HEIGHT - 120)
        base_position = pygame.Vector2(x, y)
        colors = [
            pygame.Color(255, 200, 120, 200),
            pygame.Color(120, 200, 255, 200),
            pygame.Color(255, 120, 200, 200),
        ]
        color = self._rng.choice(colors)
        for _ in range(18):
            angle = self._rng.uniform(0, 360)
            speed = self._rng.uniform(120, 220)
            velocity = pygame.Vector2(0, -1).rotate(angle) * speed
            lifetime = self._rng.uniform(0.6, 1.0)
            particle = Particle(pygame.Vector2(base_position), velocity, lifetime, pygame.Color(color), radius=3.0)
            self._particles.append(particle)
