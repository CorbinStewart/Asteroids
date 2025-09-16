import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, STATUS_BAR_HEIGHT

# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        # sub-classes must override
        pygame.draw.polygon(screen, "white", self.triangle(), 2)

    def update(self, dt):
        # sub-classes must override
        pass

    # Adding collision check to sprites
    def collision_check(self, other):
        distance = self.position.distance_to(other.position)
        return distance <= self.radius + other.radius

    def wrap_position(self):
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius

        playable_top = STATUS_BAR_HEIGHT
        if self.position.y < playable_top - self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = playable_top - self.radius
