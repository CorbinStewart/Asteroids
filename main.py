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
from game_clock import GameClock
from bomb_wave import BombController
from screen_shake import ScreenShake

def main():
    print("Starting Asteroids!")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    
    # Start the game
    pygame.init()

    # Set screen resolution
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Clock
    frame_clock = pygame.time.Clock()
    game_clock = GameClock()
    bomb_controller = BombController(game_clock)
    screen_shake = ScreenShake()
    world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                if state.use_bomb():
                    pygame.event.post(
                        pygame.event.Event(
                            BOMB_TRIGGER_EVENT,
                            {"origin": (player.position.x, player.position.y)},
                        )
                    )
            if event.type == BOMB_TRIGGER_EVENT:
                data = event.dict
                origin_tuple = data.get("origin")
                if origin_tuple is not None:
                    origin = pygame.Vector2(origin_tuple)
                else:
                    origin = pygame.Vector2(player.position)
                bomb_controller.trigger(origin)
                screen_shake.start(BOMB_SHAKE_DURATION, BOMB_SHAKE_STRENGTH)
                state.trigger_bomb_flash(BOMB_HUD_FLASH_DURATION)

        # Set background colour    
        world_surface.fill("black")
        
        # Updating group postion
        bomb_controller.update(dt)
        bomb_controller.apply_wave_effects(asteroids, score_manager)
        scaled_dt = game_clock.scale_dt(dt)
        updatable.update(scaled_dt)

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

        state.update(scaled_dt)

        level_manager.update(scaled_dt)

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
            spr.draw(world_surface)

        bomb_controller.draw(world_surface)

        screen_shake.update(dt)
        offset_x, offset_y = screen_shake.offset()
        screen.fill("black")
        screen.blit(world_surface, (offset_x, offset_y))

        hud.draw(screen, state, player, level_manager)
        pygame.display.flip()

        #Framerate
        dt = frame_clock.tick(60) / 1000
    


if __name__ == "__main__":
    main()
    
