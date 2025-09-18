from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

import pygame

from constants import (
    BOMB_HUD_FLASH_DURATION,
    BOMB_SHAKE_DURATION,
    BOMB_SHAKE_STRENGTH,
    BOMB_TRIGGER_EVENT,
    LEVEL_DEFINITIONS,
    LEVEL_MESSAGE_DURATION,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    STATUS_BAR_HEIGHT,
    VOLUME_ADJUST_STEP,
    SHAKE_ADJUST_STEP,
)
from player import Player, Shot
from asteroid import Asteroid
from asteroidfield import AsteroidField
from game_state import GameState
from level_manager import LevelManager
from score_manager import ScoreManager
from hud import Hud
from game_clock import GameClock
from bomb_wave import BombController
from fx_manager import FXManager
from bomb_pickup import spawn_pickups_from_split
from profile_manager import ProfileManager
from run_summary import show_run_summary
from audio_manager import get_audio_manager
from state_manager import AppStateManager, AppState


@dataclass
class RunContext:
    state: GameState
    score_manager: ScoreManager
    level_manager: LevelManager
    game_clock: GameClock
    bomb_controller: BombController
    fx_manager: FXManager
    updatable: pygame.sprite.Group
    drawable: pygame.sprite.Group
    asteroids: pygame.sprite.Group
    shots: pygame.sprite.Group
    pickups: pygame.sprite.Group
    player: Player
    asteroid_field: AsteroidField
    music_preload_scheduled: bool
    spawn_x: float
    spawn_y: float
    rng: random.Random


class GameApp:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.frame_clock = pygame.time.Clock()
        self.hud = Hud()
        self.profile = ProfileManager()
        self.profile.load()
        self.audio_manager = get_audio_manager()
        self.state_manager = AppStateManager(AppState.TITLE)
        self.active_run: Optional[RunContext] = None
        self.running = True

        self.title_font = pygame.font.Font(None, 72)
        self.body_font = pygame.font.Font(None, 32)

    def run(self) -> None:
        while self.running:
            dt = self.frame_clock.tick(60) / 1000.0
            events = pygame.event.get()
            current = self.state_manager.current

            if current == AppState.TITLE:
                self._handle_title(events)
            elif current == AppState.GAMEPLAY:
                self._handle_gameplay(events, dt)
            elif current == AppState.PAUSE:
                self._handle_pause(events)
            elif current == AppState.SETTINGS:
                self._handle_settings(events)
            else:
                # RUN_SUMMARY handled via blocking helper; fall back to title.
                self.state_manager.reset(AppState.TITLE)

        self.profile.save()
        self.audio_manager.stop_music()
        pygame.quit()

    # --- State handlers -------------------------------------------------

    def _handle_title(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                    return
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._start_new_run()
                    if self.active_run is not None:
                        self.state_manager.replace(AppState.GAMEPLAY)
                    return
                if event.key == pygame.K_s:
                    self.state_manager.push(AppState.SETTINGS)
                    return

        self.screen.fill("black")
        title = self.title_font.render("Asteroids", True, (255, 255, 255))
        prompt = self.body_font.render("Press ENTER to start", True, (200, 200, 200))
        settings_hint = self.body_font.render("Press S for settings", True, (160, 160, 160))
        high_score = self.body_font.render(
            f"High Score: {self.profile.high_score}", True, (180, 200, 255)
        )

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        settings_rect = settings_hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        score_rect = high_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

        self.screen.blit(title, title_rect)
        self.screen.blit(prompt, prompt_rect)
        self.screen.blit(settings_hint, settings_rect)
        self.screen.blit(high_score, score_rect)
        pygame.display.flip()

    def _handle_settings(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    self.state_manager.pop()
                    return

        self.screen.fill("black")
        title = self.title_font.render("Settings", True, (255, 255, 255))
        hint_lines = [
            "Settings coming soon.",
            "Press ESC to return.",
        ]
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
        for idx, line in enumerate(hint_lines):
            text = self.body_font.render(line, True, (200, 200, 200))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + idx * 40))
            self.screen.blit(text, rect)
        pygame.display.flip()

    def _handle_pause(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    self.state_manager.pop()
                    return
                if event.key == pygame.K_s:
                    self.state_manager.push(AppState.SETTINGS)
                    return
                if event.key == pygame.K_q:
                    self._abandon_run()
                    self.state_manager.reset(AppState.TITLE)
                    return

        if self.active_run is not None:
            self._draw_world(self.active_run)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        text = self.body_font.render("Paused - ESC to resume", True, (255, 255, 255))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, rect)
        pygame.display.flip()

    def _handle_gameplay(self, events: list[pygame.event.Event], dt: float) -> None:
        ctx = self.active_run
        if ctx is None:
            self._start_new_run()
            ctx = self.active_run
            if ctx is None:
                return

        state = ctx.state
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if ctx.player.is_invulnerable:
                    ctx.player.force_invulnerability_fade()
                if event.key == pygame.K_ESCAPE:
                    self.state_manager.push(AppState.PAUSE)
                    return
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    state.set_music_volume(state.music_volume + VOLUME_ADJUST_STEP)
                    self.audio_manager.set_music_volume(state.music_volume)
                    self.profile.update_settings(
                        music_volume=state.music_volume,
                        music_volume_previous=state.music_volume_previous,
                    )
                if event.key == pygame.K_MINUS:
                    state.set_music_volume(state.music_volume - VOLUME_ADJUST_STEP)
                    self.audio_manager.set_music_volume(state.music_volume)
                    self.profile.update_settings(
                        music_volume=state.music_volume,
                        music_volume_previous=state.music_volume_previous,
                    )
                if event.key == pygame.K_0:
                    state.toggle_music_mute()
                    self.audio_manager.set_music_volume(state.music_volume)
                    self.profile.update_settings(
                        music_volume=state.music_volume,
                        music_volume_previous=state.music_volume_previous,
                    )
                if event.key == pygame.K_LEFTBRACKET:
                    state.set_sfx_volume(state.sfx_volume - VOLUME_ADJUST_STEP)
                    self.audio_manager.set_sfx_volume(state.sfx_volume)
                    self.profile.update_settings(
                        sfx_volume=state.sfx_volume,
                        sfx_volume_previous=state.sfx_volume_previous,
                    )
                if event.key == pygame.K_RIGHTBRACKET:
                    state.set_sfx_volume(state.sfx_volume + VOLUME_ADJUST_STEP)
                    self.audio_manager.set_sfx_volume(state.sfx_volume)
                    self.profile.update_settings(
                        sfx_volume=state.sfx_volume,
                        sfx_volume_previous=state.sfx_volume_previous,
                    )
                if event.key == pygame.K_BACKSLASH:
                    state.toggle_sfx_mute()
                    self.audio_manager.set_sfx_volume(state.sfx_volume)
                    self.profile.update_settings(
                        sfx_volume=state.sfx_volume,
                        sfx_volume_previous=state.sfx_volume_previous,
                    )
                if event.key == pygame.K_SEMICOLON:
                    state.adjust_screen_shake(-SHAKE_ADJUST_STEP)
                    self.profile.update_settings(screen_shake=state.screen_shake_scale)
                if event.key == pygame.K_QUOTE:
                    state.adjust_screen_shake(SHAKE_ADJUST_STEP)
                    self.profile.update_settings(screen_shake=state.screen_shake_scale)
                if event.key == pygame.K_b:
                    if state.use_bomb():
                        pygame.event.post(
                            pygame.event.Event(
                                BOMB_TRIGGER_EVENT,
                                {"origin": (ctx.player.position.x, ctx.player.position.y)},
                            )
                        )
                if event.key == pygame.K_m:
                    state.toggle_music_mute()
                    self.audio_manager.set_music_volume(state.music_volume)
                    self.profile.update_settings(
                        music_volume=state.music_volume,
                        music_volume_previous=state.music_volume_previous,
                    )
                if event.key == pygame.K_n:
                    state.toggle_sfx_mute()
                    self.audio_manager.set_sfx_volume(state.sfx_volume)
                    self.profile.update_settings(
                        sfx_volume=state.sfx_volume,
                        sfx_volume_previous=state.sfx_volume_previous,
                    )
            if event.type == BOMB_TRIGGER_EVENT:
                data = getattr(event, "dict", {})
                origin_tuple = data.get("origin")
                origin = (
                    pygame.Vector2(origin_tuple)
                    if origin_tuple is not None
                    else pygame.Vector2(ctx.player.position)
                )
                ctx.bomb_controller.trigger(origin)
                self.audio_manager.play_bomb()
                ctx.fx_manager.shake(
                    BOMB_SHAKE_DURATION,
                    BOMB_SHAKE_STRENGTH * state.screen_shake_scale,
                )
                ctx.fx_manager.spawn_bomb_activation(origin)
                state.trigger_bomb_flash(BOMB_HUD_FLASH_DURATION)

        scaled_dt = ctx.game_clock.scale_dt(dt)
        ctx.bomb_controller.update(dt)
        ctx.bomb_controller.apply_wave_effects(
            ctx.asteroids,
            ctx.score_manager,
            state,
            ctx.pickups,
            ctx.rng,
            fx_manager=ctx.fx_manager,
        )
        self.audio_manager.set_sfx_volume(state.sfx_volume)
        self.audio_manager.set_music_volume(state.music_volume)
        ctx.fx_manager.update(scaled_dt, dt)
        ctx.updatable.update(scaled_dt)

        player_hit = False
        if not ctx.player.is_invulnerable:
            for ast in ctx.asteroids:
                if ctx.player.collision_check(ast):
                    player_hit = True
                    break

        if player_hit:
            state.lose_life()
            if state.lives <= 0:
                self._end_run(ctx)
                return
            ctx.player.reset(ctx.spawn_x, ctx.spawn_y)

        for ast in list(ctx.asteroids):
            for shot in list(ctx.shots):
                if ast.collision_check(shot):
                    ctx.score_manager.add_asteroid_points(ast)
                    ctx.fx_manager.spawn_asteroid_explosion(ast.position, ast.radius)
                    self.audio_manager.play_asteroid_hit()
                    spawn_pickups_from_split(ast, state, ctx.rng, ctx.pickups)
                    state.record_asteroid_destroyed()
                    ast.split()
                    shot.kill()

        state.update(scaled_dt)
        ctx.level_manager.update(scaled_dt)

        if not ctx.music_preload_scheduled and state.level_index + 1 < len(LEVEL_DEFINITIONS):
            spawn_total = LEVEL_DEFINITIONS[state.level_index].get("spawn_total", 0)
            if spawn_total > 0 and state.level_asteroids_destroyed >= spawn_total * 0.5:
                self.audio_manager.preload_level_music(state.level_index + 1)
                ctx.music_preload_scheduled = True

        if ctx.level_manager.should_start_transition():
            if not ctx.level_manager.levels_remaining():
                self._end_run(ctx, level_completed=True)
                return
            ctx.level_manager.apply_level_completion()
            next_level = state.level_index + 1
            ctx.player.reset(ctx.spawn_x, ctx.spawn_y)
            for shot in ctx.shots:
                shot.kill()
            ctx.level_manager.start_transition(next_level)
            ctx.fx_manager.spawn_level_transition()
            transition_ms = int(LEVEL_MESSAGE_DURATION * 2 * 1000)
            self.audio_manager.play_level_music(next_level, transition_ms=transition_ms)
            ctx.music_preload_scheduled = False

        for pickup in list(ctx.pickups):
            pickup.update(scaled_dt)
            if pickup.collides_with(ctx.player.position, ctx.player.radius):
                ctx.score_manager.add_bombs(1)
                state.trigger_bomb_flash(BOMB_HUD_FLASH_DURATION)
                state.record_pickup_collected()
                ctx.fx_manager.spawn_powerup_trail(ctx.player, (220, 60, 60))
                self.audio_manager.play_bomb_pickup()
                pickup.kill()
                continue

        self._draw_world(ctx)
        pygame.display.flip()

    # --- Helpers --------------------------------------------------------

    def _start_new_run(self) -> None:
        state = GameState()
        state.high_score = self.profile.high_score
        state.initial_high_score = self.profile.high_score
        state.leaderboard = self.profile.leaderboard().copy()
        state.apply_settings(self.profile.settings())

        score_manager = ScoreManager(state, self.profile)
        game_clock = GameClock()
        bomb_controller = BombController(game_clock)
        fx_manager = FXManager()

        updatable = pygame.sprite.Group()
        drawable = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        shots = pygame.sprite.Group()
        pickups = pygame.sprite.Group()

        Player.containers = (updatable, drawable)
        Asteroid.containers = (asteroids, updatable, drawable)
        AsteroidField.containers = (updatable,)
        Shot.containers = (shots, updatable, drawable)

        playable_height = SCREEN_HEIGHT - STATUS_BAR_HEIGHT
        spawn_x = SCREEN_WIDTH / 2
        spawn_y = STATUS_BAR_HEIGHT + playable_height / 2
        player = Player(spawn_x, spawn_y)

        asteroid_field = AsteroidField(asteroids)
        level_manager = LevelManager(state, asteroid_field, score_manager)
        level_manager.configure_level(state.level_index)

        self.audio_manager.set_sfx_volume(state.sfx_volume)
        self.audio_manager.set_music_volume(state.music_volume)
        transition_ms = int(LEVEL_MESSAGE_DURATION * 1000)
        self.audio_manager.play_level_music(state.level_index, transition_ms=transition_ms)

        self.active_run = RunContext(
            state=state,
            score_manager=score_manager,
            level_manager=level_manager,
            game_clock=game_clock,
            bomb_controller=bomb_controller,
            fx_manager=fx_manager,
            updatable=updatable,
            drawable=drawable,
            asteroids=asteroids,
            shots=shots,
            pickups=pickups,
            player=player,
            asteroid_field=asteroid_field,
            music_preload_scheduled=False,
            spawn_x=spawn_x,
            spawn_y=spawn_y,
            rng=random.Random(),
        )

    def _draw_world(self, ctx: RunContext) -> None:
        self.world_surface.fill("black")
        for spr in ctx.drawable:
            spr.draw(self.world_surface)
        for pickup in ctx.pickups:
            pickup.draw(self.world_surface)
        ctx.bomb_controller.draw(self.world_surface)
        ctx.fx_manager.draw_world(self.world_surface)

        offset_x, offset_y = ctx.fx_manager.offset()
        self.screen.fill("black")
        self.screen.blit(self.world_surface, (offset_x, offset_y))
        ctx.fx_manager.draw_overlay(self.screen)
        self.hud.draw(self.screen, ctx.state, ctx.player, ctx.level_manager)

    def _abandon_run(self) -> None:
        if self.active_run is None:
            return
        self.audio_manager.fade_out_music(400)
        self.audio_manager.stop_music()
        self.active_run = None

    def _end_run(self, ctx: RunContext, *, level_completed: bool = False) -> None:
        self.audio_manager.fade_out_music(800)
        state = ctx.state
        if state.score > 0:
            self.profile.submit_score(
                self.profile.settings().get("player_name", "ACE"),
                state.score,
                state.level_index + 1,
            )
            state.leaderboard = self.profile.leaderboard().copy()
        self.profile.record_milestones(
            asteroids_destroyed=getattr(state, "asteroids_destroyed", 0),
            bombs_used=state.bombs_used,
            pickups_collected=state.pickups_collected,
            time_survived=state.run_time,
        )
        self.profile.save()

        restart = show_run_summary(self.screen, state, self.profile, level_completed)
        self.active_run = None

        if restart:
            self._start_new_run()
            if self.active_run is not None:
                self.state_manager.replace(AppState.GAMEPLAY)
        else:
            self.state_manager.reset(AppState.TITLE)


def main() -> None:
    app = GameApp()
    app.run()


if __name__ == "__main__":
    main()
