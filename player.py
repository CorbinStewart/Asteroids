import pygame
from circleshape import CircleShape
from constants import PLAYER_RADIUS, PLAYER_TURN_SPEED, PLAYER_SPEED, PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN, SHOT_RADIUS

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.timer = 0
    
    # Speed to rotate the player sprite
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    # Speed to move player forward or backwards
    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt
    
    # Player movement & shooting controls
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            if self.timer <= 0:
                self.shoot()
        self.timer -= dt

    # Adding shooting ability
    def shoot(self):
        bullet = Shot(self.position.x, self.position.y,  SHOT_RADIUS)
        velocity = pygame.Vector2(0, 1).rotate(self.rotation)
        bullet.velocity += velocity * PLAYER_SHOOT_SPEED
        self.timer = PLAYER_SHOOT_COOLDOWN
    
    # Drawing player sprite as a triangle
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
class Shot(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.radius = radius
    
    # Drawing bullet sprite
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    # Adding bullet movement
    def update(self, dt):
        self.position += self.velocity * dt