import pygame
from circleshape import CircleShape
from constants import (
    PLAYER_RADIUS,
    PLAYER_TURN_SPEED,
    PLAYER_SPEED,
    PLAYER_SHOOT_SPEED,
    PLAYER_SHOOT_COOLDOWN,
    PLAYER_RESPAWN_INVULNERABILITY,
    PLAYER_SHIELD_RADIUS_PADDING,
    PLAYER_INVULNERABILITY_FADE_WINDOW,
    SHOT_LIFETIME,
    SHOT_RADIUS,
)

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.timer = 0
        self._invulnerable = False
        self._invulnerability_timer = 0
        self._invulnerability_duration = 0
        self._invulnerability_fading = False
        self._invulnerability_fade_elapsed = 0

    def reset(self, x, y):
        self.position.update(x, y)
        self.velocity.update(0, 0)
        self.rotation = 0
        self.timer = 0
        self.start_invulnerability(PLAYER_RESPAWN_INVULNERABILITY)

    def start_invulnerability(self, duration):
        self._invulnerable = True
        self._invulnerability_timer = duration
        self._invulnerability_duration = duration
        self._invulnerability_fading = False
        self._invulnerability_fade_elapsed = 0

    def end_invulnerability(self):
        self._invulnerable = False
        self._invulnerability_timer = 0
        self._invulnerability_duration = 0
        self._invulnerability_fading = False
        self._invulnerability_fade_elapsed = 0

    @property
    def is_invulnerable(self):
        return self._invulnerable

    def force_invulnerability_fade(self):
        if not self._invulnerable:
            return
        if not self._invulnerability_fading:
            self._invulnerability_fading = True
            self._invulnerability_fade_elapsed = 0
        if self._invulnerability_timer > PLAYER_INVULNERABILITY_FADE_WINDOW:
            self._invulnerability_timer = PLAYER_INVULNERABILITY_FADE_WINDOW
    
    # Speed to rotate the player sprite
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    # Speed to move player forward or backwards
    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt
    
    # Player movement & shooting controls
    def update(self, dt):
        if self._invulnerable:
            self._invulnerability_timer -= dt

            if (
                self._invulnerability_timer <= PLAYER_INVULNERABILITY_FADE_WINDOW
                and not self._invulnerability_fading
            ):
                self._invulnerability_fading = True
                self._invulnerability_fade_elapsed = 0

            if self._invulnerability_fading:
                self._invulnerability_fade_elapsed += dt

            if self._invulnerability_timer <= 0:
                self.end_invulnerability()

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
        self.wrap_position()

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

    def draw(self, screen):
        pygame.draw.polygon(screen, "white", self.triangle(), 2)
        if self._invulnerable and self._invulnerability_duration > 0:
            shield_radius = int(self.radius + PLAYER_SHIELD_RADIUS_PADDING)
            alpha = 255
            if self._invulnerability_fading:
                remaining = max(0.0, min(PLAYER_INVULNERABILITY_FADE_WINDOW, self._invulnerability_timer))
                ratio = remaining / PLAYER_INVULNERABILITY_FADE_WINDOW if PLAYER_INVULNERABILITY_FADE_WINDOW > 0 else 0
                alpha = int(ratio * 255)
            if alpha > 0:
                diameter = shield_radius * 2 + 4
                shield_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
                center = (diameter // 2, diameter // 2)
                pygame.draw.circle(shield_surface, (255, 255, 0, alpha), center, shield_radius, 2)
                rect = shield_surface.get_rect()
                rect.center = (int(self.position.x), int(self.position.y))
                screen.blit(shield_surface, rect)
    
class Shot(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.radius = radius
        self.life_timer = SHOT_LIFETIME
    
    # Drawing bullet sprite
    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    # Adding bullet movement
    def update(self, dt):
        self.position += self.velocity * dt
        self.life_timer -= dt
        self.wrap_position()
        if self.life_timer <= 0:
            self.kill()
