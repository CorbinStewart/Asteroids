import pygame
import random
from circleshape import CircleShape
from constants import *

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.radius = radius
    
    # Drawing asteroid sprite
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    # Adding asteroid movement
    def update(self, dt):
        self.position += self.velocity * dt

    # Asteroid spliting logic
    def split(self):
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