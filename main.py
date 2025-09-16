from pathlib import Path
import random

import pygame
from constants import *
from player import *
from asteroid import *
from asteroidfield import *
from circleshape import *

def main():
    print("Starting Asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    
    # Start the game
    pygame.init()

    # Set screen resolution
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Clock
    clock = pygame.time.Clock()

    def load_font(path_str, size):
        path = Path(path_str)
        if path.exists():
            try:
                return pygame.font.Font(path.as_posix(), size)
            except Exception:
                pass
        return pygame.font.Font(None, size)

    font_regular = load_font(ORBITRON_FONT_PATH, HUD_FONT_SIZE)
    font_semibold = load_font(ORBITRON_SEMIBOLD_FONT_PATH, HEADER_FONT_SIZE)
    hud_shadow_color = pygame.Color(120, 160, 255, 70)
    hud_text_color = pygame.Color(255, 255, 255, 220)
    separator_color = pygame.Color(255, 255, 255, 120)
    random.seed(42)
    hud_stars = [
        (
            random.randint(8, SCREEN_WIDTH - 8),
            random.randint(8, STATUS_BAR_HEIGHT - 8),
            random.choice((1, 2)),
            random.randint(40, 60),
        )
        for _ in range(8)
    ]

    dt = 0
    lives = PLAYER_START_LIVES
    life_loss_active = False
    life_loss_elapsed = 0
    level_index = 0
    total_levels = len(LEVEL_DEFINITIONS)

    # Creating object groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    
    # Adding objects to groups
    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable)
    Shot.containers = (shots, updatable, drawable)

    # Setting starting position
    playable_height = SCREEN_HEIGHT - STATUS_BAR_HEIGHT
    spawn_x = SCREEN_WIDTH / 2
    spawn_y = STATUS_BAR_HEIGHT + playable_height / 2
    
    # Adding Player object
    player = Player(spawn_x, spawn_y)

    # Adding AsteroidField object
    asteroid_field = AsteroidField(asteroids)

    def configure_level(index):
        config = LEVEL_DEFINITIONS[index]
        asteroid_field.configure_level(
            config["spawn_total"], config["max_active"], config["speed_multiplier"]
        )

    level_transition = None

    configure_level(level_index)

    def draw_life_icon(surface, cx, cy, color):
        base = LIFE_ICON_SIZE * 0.6
        points = [
            (cx, cy - LIFE_ICON_SIZE),
            (cx - base, cy + LIFE_ICON_SIZE),
            (cx + base, cy + LIFE_ICON_SIZE),
        ]
        pygame.draw.polygon(surface, color, points, 2)

    # Gameplay loop
    while True:
        # Close app window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and player.is_invulnerable:
                player.force_invulnerability_fade()

        # Set background colour    
        screen.fill("black")
        
        # Updating group postion
        updatable.update(dt)

        # Checking for player collision
        player_hit = False
        if not player.is_invulnerable:
            for ast in asteroids:
                if player.collision_check(ast):
                    player_hit = True
                    break

        if player_hit:
            lives -= 1
            if lives <= 0:
                print("Game over!")
                return
            player.reset(spawn_x, spawn_y)
            life_loss_active = True
            life_loss_elapsed = 0

        # Checking for bullet collision
        for ast in asteroids:
            for shot in shots:
                if ast.collision_check(shot):
                    ast.split()
                    shot.kill()

        if life_loss_active:
            life_loss_elapsed += dt
            if life_loss_elapsed >= LIFE_ICON_FLICKER_DURATION:
                life_loss_active = False
                life_loss_elapsed = 0

        if level_transition:
            level_transition["timer"] += dt
            if level_transition["phase"] == "top":
                if level_transition["timer"] >= LEVEL_MESSAGE_DURATION:
                    level_transition["phase"] = "bottom"
                    level_transition["timer"] = 0
            elif level_transition["phase"] == "bottom":
                if level_transition["timer"] >= LEVEL_MESSAGE_DURATION:
                    level_index = level_transition["next_level"]
                    configure_level(level_index)
                    level_transition = None

        if (
            level_transition is None
            and asteroid_field.level_complete()
        ):
            if level_index + 1 >= total_levels:
                print("All levels cleared! You win!")
                return
            next_level = level_index + 1
            player.reset(spawn_x, spawn_y)
            for shot in shots:
                shot.kill()
            level_transition = {
                "next_level": next_level,
                "timer": 0.0,
                "phase": "top",
                "header": random.choice(
                    ["Good Work!", "Nice Shooting!", "Level Complete!"]
                ),
            }


        # Drawing the group position
        for spr in drawable:
            spr.draw(screen)

        gradient_surface = pygame.Surface(
            (SCREEN_WIDTH, STATUS_BAR_HEIGHT), pygame.SRCALPHA
        )
        top_color = pygame.Color(*STATUS_BAR_TOP_COLOR, 255)
        bottom_color = pygame.Color(*STATUS_BAR_BOTTOM_COLOR, 255)
        for y in range(STATUS_BAR_HEIGHT):
            blend = y / max(1, STATUS_BAR_HEIGHT - 1)
            r = int(top_color.r + (bottom_color.r - top_color.r) * blend)
            g = int(top_color.g + (bottom_color.g - top_color.g) * blend)
            b = int(top_color.b + (bottom_color.b - top_color.b) * blend)
            pygame.draw.line(
                gradient_surface,
                (r, g, b, 255),
                (0, y),
                (SCREEN_WIDTH, y),
            )
        pygame.draw.line(
            gradient_surface,
            (255, 255, 255, 60),
            (0, STATUS_BAR_HEIGHT - 2),
            (SCREEN_WIDTH, STATUS_BAR_HEIGHT - 2),
        )
        pygame.draw.line(
            gradient_surface,
            (255, 255, 255, 200),
            (0, STATUS_BAR_HEIGHT - 1),
            (SCREEN_WIDTH, STATUS_BAR_HEIGHT - 1),
        )
        for sx, sy, radius, alpha in hud_stars:
            pygame.draw.circle(
                gradient_surface,
                (255, 255, 255, alpha),
                (sx, sy),
                radius,
            )

        screen.blit(gradient_surface, (0, 0))

        icon_count = lives + (1 if life_loss_active else 0)
        flash_on = True
        if life_loss_active:
            flashes = int(life_loss_elapsed / LIFE_ICON_FLICKER_INTERVAL)
            flash_on = flashes % 2 == 0

        icon_center_y = STATUS_BAR_HEIGHT / 2 + 4
        for i in range(icon_count):
            cx = 40 + i * LIFE_ICON_SPACING
            if life_loss_active and i == icon_count - 1:
                if flash_on:
                    draw_life_icon(screen, cx, icon_center_y, LIFE_ICON_FLICKER_COLOR)
            else:
                draw_life_icon(screen, cx, icon_center_y, "white")

        level_string = "LEVEL " + " " .join(list(str(level_index + 1)))
        level_surface_shadow = font_regular.render(level_string, True, hud_shadow_color)
        level_surface = font_regular.render(level_string, True, hud_text_color)
        level_pos = level_surface.get_rect()
        level_pos.centery = STATUS_BAR_HEIGHT / 2
        level_pos.right = SCREEN_WIDTH - 32
        shadow_pos = level_pos.copy()
        shadow_pos.move_ip(0, 1)
        screen.blit(level_surface_shadow, shadow_pos)
        screen.blit(level_surface, level_pos)

        separator_dot = pygame.Rect(0, 0, 4, 4)
        separator_dot.center = (SCREEN_WIDTH - 180, STATUS_BAR_HEIGHT / 2 + 2)
        separator_surface = pygame.Surface(separator_dot.size, pygame.SRCALPHA)
        pygame.draw.circle(
            separator_surface,
            separator_color,
            (separator_dot.width // 2, separator_dot.height // 2),
            separator_dot.width // 2,
        )
        screen.blit(separator_surface, separator_dot)

        if level_transition:
            alpha_ratio = max(
                0.0,
                1.0 - (level_transition["timer"] / LEVEL_MESSAGE_DURATION),
            )
            alpha = int(255 * alpha_ratio)
            if level_transition["phase"] == "top":
                header_surface_shadow = font_semibold.render(
                    level_transition["header"], True, hud_shadow_color
                ).convert_alpha()
                header_surface_shadow.set_alpha(alpha)
                header_surface = font_semibold.render(
                    level_transition["header"], True, hud_text_color
                ).convert_alpha()
                header_surface.set_alpha(alpha)
                top_y = STATUS_BAR_HEIGHT + (
                    (player.position.y - STATUS_BAR_HEIGHT) / 2
                )
                header_rect = header_surface.get_rect()
                header_rect.center = (SCREEN_WIDTH / 2, top_y)
                shadow_rect = header_rect.copy()
                shadow_rect.move_ip(0, 1)
                screen.blit(header_surface_shadow, shadow_rect)
                screen.blit(header_surface, header_rect)
            elif level_transition["phase"] == "bottom":
                level_string = "LEVEL " + " " .join(
                    list(str(level_transition["next_level"] + 1))
                )
                level_surface_shadow = font_semibold.render(
                    level_string, True, hud_shadow_color
                ).convert_alpha()
                level_surface_shadow.set_alpha(alpha)
                level_surface = font_semibold.render(
                    level_string, True, hud_text_color
                ).convert_alpha()
                level_surface.set_alpha(alpha)
                bottom_y = (player.position.y + SCREEN_HEIGHT) / 2
                level_rect = level_surface.get_rect()
                level_rect.center = (SCREEN_WIDTH / 2, bottom_y)
                shadow_rect = level_rect.copy()
                shadow_rect.move_ip(0, 1)
                screen.blit(level_surface_shadow, shadow_rect)
                screen.blit(level_surface, level_rect)

        pygame.display.flip()

        #Framerate
        dt = (clock.tick(60) / 1000)
    


if __name__ == "__main__":
    main()
    
