import pygame
import random
from asteroid import Asteroid
from constants import *


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

    def __init__(self, asteroids_group):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer = 0.0
        self.asteroids_group = asteroids_group
        self.spawn_limit = 0
        self.max_active = 0
        self.spawned_this_level = 0
        self.speed_multiplier = 1.0

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity
        self.spawned_this_level += 1

    def configure_level(self, spawn_limit, max_active, speed_multiplier):
        self.spawn_limit = max(0, spawn_limit)
        self.max_active = max(1, max_active)
        self.spawned_this_level = 0
        self.spawn_timer = 0.0
        self.speed_multiplier = max(0.1, speed_multiplier)

    def level_complete(self):
        if self.spawn_limit == 0:
            return False
        return (
            self.spawned_this_level >= self.spawn_limit
            and len(self.asteroids_group) == 0
        )

    def update(self, dt):
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
