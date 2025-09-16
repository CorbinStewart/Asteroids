import pygame
from constants import *
from player import *
from asteroid import *
from asteroidfield import *
from circleshape import *
from game_state import GameState
from level_manager import LevelManager
from score_manager import ScoreManager
from hud import Hud

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

    state = GameState()
    score_manager = ScoreManager(state)
    hud = Hud()

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
    level_manager = LevelManager(state, asteroid_field, score_manager)
    level_manager.configure_level(state.level_index)

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
                    score_manager.add_asteroid_points(ast)
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

        hud.draw(screen, state, player, level_manager)
        pygame.display.flip()

        #Framerate
        dt = (clock.tick(60) / 1000)
    


if __name__ == "__main__":
    main()
    
