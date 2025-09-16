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
    font = pygame.font.Font(None, HUD_FONT_SIZE)

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
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    
    # Adding Player object
    player = Player(x, y)

    # Adding AsteroidField object
    asteroid_field = AsteroidField(asteroids)

    def configure_level(index):
        config = LEVEL_DEFINITIONS[index]
        asteroid_field.configure_level(
            config["spawn_total"], config["max_active"], config["speed_multiplier"]
        )

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
            player.reset(x, y)
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

        if asteroid_field.level_complete():
            if level_index + 1 >= total_levels:
                print("All levels cleared! You win!")
                return
            level_index += 1
            player.reset(x, y)
            for shot in shots:
                shot.kill()
            configure_level(level_index)


        # Drawing the group position
        for spr in drawable:
            spr.draw(screen)

        icon_count = lives + (1 if life_loss_active else 0)
        flash_on = True
        if life_loss_active:
            flashes = int(life_loss_elapsed / LIFE_ICON_FLICKER_INTERVAL)
            flash_on = flashes % 2 == 0

        for i in range(icon_count):
            cx = 20 + i * LIFE_ICON_SPACING
            cy = 20 + LIFE_ICON_SIZE
            if life_loss_active and i == icon_count - 1:
                if flash_on:
                    draw_life_icon(screen, cx, cy, LIFE_ICON_FLICKER_COLOR)
            else:
                draw_life_icon(screen, cx, cy, "white")

        level_text = font.render(f"Level {level_index + 1}", True, "white")
        level_pos = level_text.get_rect()
        level_pos.topright = (SCREEN_WIDTH - 20, 20)
        screen.blit(level_text, level_pos)

        pygame.display.flip()

        #Framerate
        dt = (clock.tick(60) / 1000)
    


if __name__ == "__main__":
    main()
    
