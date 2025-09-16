from pathlib import Path
import random

import pygame
from constants import *
from player import *
from asteroid import *
from asteroidfield import *
from circleshape import *
from game_state import GameState
from level_manager import LevelManager

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
    font_subheader = load_font(ORBITRON_FONT_PATH, SUBHEADER_FONT_SIZE)
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

    state = GameState()

    def make_hud_text(font, text):
        shadow = font.render(text, True, hud_shadow_color).convert_alpha()
        text_surface = font.render(text, True, hud_text_color).convert_alpha()
        return shadow, text_surface

    def draw_subheader(rect, text):
        shadow, surface = make_hud_text(font_subheader, text)
        header_rect = surface.get_rect()
        header_rect.centerx = rect.centerx
        header_rect.top = rect.top + 6
        shadow_rect = header_rect.copy()
        shadow_rect.move_ip(0, 1)
        screen.blit(shadow, shadow_rect)
        screen.blit(surface, header_rect)

    dt = 0

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
    level_manager = LevelManager(state, asteroid_field)

    level_manager.configure_level(state.level_index)

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
            state.lose_life()
            if state.lives <= 0:
                print("Game over!")
                return
            player.reset(spawn_x, spawn_y)

        # Checking for bullet collision
        for ast in asteroids:
            for shot in shots:
                if ast.collision_check(shot):
                    state.add_score(ast.score_value())
                    ast.split()
                    shot.kill()

        state.update(dt)

        level_manager.update(dt)

        if level_manager.should_start_transition():
            if not level_manager.levels_remaining():
                print("All levels cleared! You win!")
                return
            level_manager.apply_level_completion()
            next_level = state.level_index + 1
            player.reset(spawn_x, spawn_y)
            for shot in shots:
                shot.kill()
            level_manager.start_transition(next_level)


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
        section_width = SCREEN_WIDTH // 5
        sections = []
        for i in range(5):
            rect = pygame.Rect(i * section_width, 0, section_width, STATUS_BAR_HEIGHT)
            sections.append(rect)
            border_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(border_surface, (255, 255, 255, 40), border_surface.get_rect(), 1)
            screen.blit(border_surface, rect)

        icon_count = state.lives + (1 if state.life_loss_active else 0)
        flash_on = True
        if state.life_loss_active:
            flashes = int(state.life_loss_elapsed / LIFE_ICON_FLICKER_INTERVAL)
            flash_on = flashes % 2 == 0

        life_section = sections[0]
        draw_subheader(life_section, "LIVES")
        icon_center_y = life_section.centery + 10
        start_x = life_section.centerx
        if icon_count:
            total_spacing = (icon_count - 1) * LIFE_ICON_SPACING
            start_x = life_section.centerx - total_spacing / 2
        for i in range(icon_count):
            cx = start_x + i * LIFE_ICON_SPACING
            if state.life_loss_active and i == icon_count - 1:
                if flash_on:
                    draw_life_icon(screen, cx, icon_center_y, LIFE_ICON_FLICKER_COLOR)
            else:
                draw_life_icon(screen, cx, icon_center_y, "white")

        power_section = sections[1]
        draw_subheader(power_section, "BOMBS")
        bomb_icon_size = 14
        bomb_spacing = 18
        bomb_count = state.bombs
        start_x = power_section.centerx
        if bomb_count:
            total_spacing = (bomb_count - 1) * bomb_spacing
            start_x = power_section.centerx - total_spacing / 2
        for i in range(bomb_count):
            cx = start_x + i * bomb_spacing
            bomb_rect = pygame.Rect(0, 0, bomb_icon_size, bomb_icon_size)
            bomb_rect.center = (cx, power_section.centery + 12)
            pygame.draw.rect(screen, "white", bomb_rect, 2)

        level_number = f"{state.level_index + 1:02d}"
        level_string = f"LEVEL {level_number}"
        level_shadow, level_surface = make_hud_text(font_regular, level_string)
        level_rect = level_surface.get_rect()
        level_section = sections[4]
        level_rect.center = (level_section.centerx, level_section.centery + 8)
        shadow_rect = level_rect.copy()
        shadow_rect.move_ip(0, 1)
        screen.blit(level_shadow, shadow_rect)
        screen.blit(level_surface, level_rect)

        high_string = f"{state.high_score:06d}"
        hi_shadow, hi_surface = make_hud_text(font_regular, high_string)
        hi_rect = hi_surface.get_rect()
        hi_section = sections[2]
        draw_subheader(hi_section, "HIGH SCORE")
        hi_rect.center = (hi_section.centerx, hi_section.centery + 8)
        hi_shadow_rect = hi_rect.copy()
        hi_shadow_rect.move_ip(0, 1)
        screen.blit(hi_shadow, hi_shadow_rect)
        screen.blit(hi_surface, hi_rect)

        score_string = f"{state.score:06d}"
        score_shadow, score_surface = make_hud_text(font_regular, score_string)
        score_rect = score_surface.get_rect()
        score_section = sections[3]
        draw_subheader(score_section, "SCORE")
        score_rect.center = (score_section.centerx, score_section.centery + 8)
        score_shadow_rect = score_rect.copy()
        score_shadow_rect.move_ip(0, 1)
        screen.blit(score_shadow, score_shadow_rect)
        screen.blit(score_surface, score_rect)

        transition = level_manager.transition
        if transition:
            alpha_ratio = max(
                0.0,
                1.0 - (transition.timer / LEVEL_MESSAGE_DURATION),
            )
            alpha = int(255 * alpha_ratio)
            if transition.phase == "top":
                header_shadow, header_surface = make_hud_text(
                    font_semibold, transition.header
                )
                header_shadow.set_alpha(alpha)
                header_surface.set_alpha(alpha)
                top_y = STATUS_BAR_HEIGHT + (
                    (player.position.y - STATUS_BAR_HEIGHT) / 2
                )
                header_rect = header_surface.get_rect()
                header_rect.center = (SCREEN_WIDTH / 2, top_y)
                shadow_rect = header_rect.copy()
                shadow_rect.move_ip(0, 1)
                screen.blit(header_shadow, shadow_rect)
                screen.blit(header_surface, header_rect)
            elif transition.phase == "bottom":
                level_number = f"{transition.next_level + 1:02d}"
                level_string = f"LEVEL {level_number}"
                level_shadow, level_surface = make_hud_text(font_semibold, level_string)
                level_shadow.set_alpha(alpha)
                level_surface.set_alpha(alpha)
                bottom_y = (player.position.y + SCREEN_HEIGHT) / 2
                level_rect = level_surface.get_rect()
                level_rect.center = (SCREEN_WIDTH / 2, bottom_y)
                shadow_rect = level_rect.copy()
                shadow_rect.move_ip(0, 1)
                screen.blit(level_shadow, shadow_rect)
                screen.blit(level_surface, level_rect)

        pygame.display.flip()

        #Framerate
        dt = (clock.tick(60) / 1000)
    


if __name__ == "__main__":
    main()
    
