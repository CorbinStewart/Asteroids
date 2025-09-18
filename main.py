import random

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
from fx_manager import FXManager
from bomb_pickup import BombPickup, spawn_pickups_from_split
from profile_manager import ProfileManager
from run_summary import show_run_summary
from audio_manager import get_audio_manager

def main() -> bool:
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
    fx_manager = FXManager()
    world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    profile = ProfileManager()
    profile.load()

    state = GameState()
    state.high_score = profile.high_score
    state.initial_high_score = profile.high_score
    state.leaderboard = profile.leaderboard().copy()
    state.apply_settings(profile.settings())
    score_manager = ScoreManager(state, profile)
    hud = Hud()
    audio_manager = get_audio_manager()
    audio_manager.set_sfx_volume(state.sfx_volume)
    audio_manager.set_music_volume(state.music_volume)
    audio_manager.play_level_music(state.level_index, transition_ms=int(LEVEL_MESSAGE_DURATION * 1000))
    music_preload_scheduled = False

    dt = 0

    # Creating object groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    pickups = pygame.sprite.Group()
    
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

    def finalize_run(level_completed: bool = False) -> bool:
        audio_manager.fade_out_music(800)
        if state.score > 0:
            profile.submit_score(
                profile.settings().get("player_name", "ACE"),
                state.score,
                state.level_index + 1,
            )
            state.leaderboard = profile.leaderboard().copy()
        profile.record_milestones(
            asteroids_destroyed=getattr(state, "asteroids_destroyed", 0),
            bombs_used=state.bombs_used,
            pickups_collected=state.pickups_collected,
            time_survived=state.run_time,
        )
        profile.save()
        return show_run_summary(screen, state, profile, level_completed)

    try:
        # Gameplay loop
        while True:
            # Close app window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    restart_requested = finalize_run()
                    return restart_requested
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
                    audio_manager.play_bomb()
                    fx_manager.shake(
                        BOMB_SHAKE_DURATION, BOMB_SHAKE_STRENGTH * state.screen_shake_scale
                    )
                    fx_manager.spawn_bomb_activation(origin)
                    state.trigger_bomb_flash(BOMB_HUD_FLASH_DURATION)

            # Set background colour    
            world_surface.fill("black")

            rng = random.Random()

            # Updating group postion
            scaled_dt = game_clock.scale_dt(dt)
            bomb_controller.update(dt)
            bomb_controller.apply_wave_effects(
                asteroids,
                score_manager,
                state,
                pickups,
                rng,
                fx_manager=fx_manager,
            )
            audio_manager.set_sfx_volume(state.sfx_volume)
            audio_manager.set_music_volume(state.music_volume)
            fx_manager.update(scaled_dt, dt)
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
                    restart_requested = finalize_run()
                    return restart_requested
                player.reset(spawn_x, spawn_y)

            # Checking for bullet collision
            for ast in list(asteroids):
                for shot in list(shots):
                    if ast.collision_check(shot):
                        score_manager.add_asteroid_points(ast)
                        fx_manager.spawn_asteroid_explosion(ast.position, ast.radius)
                        audio_manager.play_asteroid_hit()
                        spawn_pickups_from_split(ast, state, rng, pickups)
                        state.record_asteroid_destroyed()
                        ast.split()
                        shot.kill()

            state.update(scaled_dt)

            level_manager.update(scaled_dt)

            if not music_preload_scheduled and state.level_index + 1 < len(LEVEL_DEFINITIONS):
                spawn_total = LEVEL_DEFINITIONS[state.level_index].get("spawn_total", 0)
                if spawn_total > 0 and state.level_asteroids_destroyed >= spawn_total * 0.5:
                    audio_manager.preload_level_music(state.level_index + 1)
                    music_preload_scheduled = True

            if level_manager.should_start_transition():
                if not level_manager.levels_remaining():
                    print("All levels cleared! You win!")
                    restart_requested = finalize_run(level_completed=True)
                    return restart_requested
                level_manager.apply_level_completion()
                next_level = state.level_index + 1
                player.reset(spawn_x, spawn_y)
                for shot in shots:
                    shot.kill()
                level_manager.start_transition(next_level)
                fx_manager.spawn_level_transition()
                transition_ms = int(LEVEL_MESSAGE_DURATION * 2 * 1000)
                audio_manager.play_level_music(next_level, transition_ms=transition_ms)
                music_preload_scheduled = False


            # Drawing the group position
            for spr in drawable:
                spr.draw(world_surface)
            for pickup in list(pickups):
                pickup.update(scaled_dt)
                if pickup.collides_with(player.position, player.radius):
                    score_manager.add_bombs(1)
                    state.trigger_bomb_flash(BOMB_HUD_FLASH_DURATION)
                    state.record_pickup_collected()
                    fx_manager.spawn_powerup_trail(player, (220, 60, 60))
                    audio_manager.play_bomb_pickup()
                    pickup.kill()
                    continue
                pickup.draw(world_surface)

            bomb_controller.draw(world_surface)
            fx_manager.draw_world(world_surface)

            offset_x, offset_y = fx_manager.offset()
            screen.fill("black")
            screen.blit(world_surface, (offset_x, offset_y))
            fx_manager.draw_overlay(screen)

            hud.draw(screen, state, player, level_manager)
            pygame.display.flip()

            #Framerate
            dt = frame_clock.tick(60) / 1000
    finally:
        profile.save()
        audio_manager.stop_music()
    return False


if __name__ == "__main__":
    restart = True
    while restart:
        restart = main()
