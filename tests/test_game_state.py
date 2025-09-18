from game_state import GameState
from constants import LIFE_ICON_FLICKER_DURATION, PLAYER_START_BOMBS, PLAYER_START_LIVES


def test_reset_for_level_clears_loss_flags():
    state = GameState(
        lives=PLAYER_START_LIVES,
        score=250,
        high_score=300,
        level_index=1,
        life_loss_active=True,
        life_loss_elapsed=0.5,
        life_lost_this_level=True,
        initial_high_score=300,
        bombs_used=3,
        pickups_collected=2,
        level_bombs_used=2,
        level_pickups_collected=1,
        level_asteroids_destroyed=4,
        high_score_beaten=True,
        high_score_flash_elapsed=5.0,
    )

    state.reset_for_level(3)

    assert state.level_index == 3
    assert state.life_lost_this_level is False
    assert state.life_loss_active is False
    assert state.life_loss_elapsed == 0.0
    assert state.bombs_used == 3
    assert state.pickups_collected == 2
    assert state.level_bombs_used == 0
    assert state.level_pickups_collected == 0
    assert state.level_asteroids_destroyed == 0
    assert state.high_score_beaten is False
    assert state.high_score_flash_elapsed == 0.0
    assert state.initial_high_score == 300


def test_lose_life_updates_state_flags():
    state = GameState(lives=3)

    state.lose_life()

    assert state.lives == 2
    assert state.life_loss_active is True
    assert state.life_loss_elapsed == 0.0
    assert state.life_lost_this_level is True


def test_add_score_increases_high_score():
    state = GameState(score=10, high_score=25)

    state.add_score(15)
    state.add_score(-5)

    assert state.score == 25
    assert state.high_score == 25
    assert state.high_score_beaten is False


def test_update_turns_off_life_loss_flash():
    state = GameState()
    state.lose_life()

    state.update(LIFE_ICON_FLICKER_DURATION / 2)
    assert state.life_loss_active is True

    state.update(LIFE_ICON_FLICKER_DURATION)
    assert state.life_loss_active is False
    assert state.life_loss_elapsed == 0.0


def test_bombs_initialise_and_consume():
    state = GameState()

    assert state.bombs == PLAYER_START_BOMBS
    assert state.use_bomb() is True
    assert state.bombs == PLAYER_START_BOMBS - 1
    assert state.bombs_used == 1


def test_use_bomb_returns_false_when_empty():
    state = GameState(bombs=0)

    assert state.use_bomb() is False
    assert state.bombs == 0


def test_add_bombs_increases_count_and_caps():
    state = GameState(bombs=0)

    state.add_bombs(2)
    assert state.bombs == 2

    state.add_bombs(10)
    assert state.bombs == state.bomb_cap


def test_bomb_flash_timer_counts_down():
    state = GameState()
    state.trigger_bomb_flash(1.0)
    assert state.bomb_flash_timer == 1.0
    state.update(0.5)
    assert state.bomb_flash_timer == 0.5
    state.update(1.0)
    assert state.bomb_flash_timer == 0.0


def test_record_helpers_track_totals_and_level_counts():
    state = GameState()
    state.record_pickup_collected()
    state.record_asteroid_destroyed()
    assert state.pickups_collected == 1
    assert state.asteroids_destroyed == 1
    assert state.level_pickups_collected == 1
    assert state.level_asteroids_destroyed == 1

    state.reset_for_level(2)
    assert state.pickups_collected == 1
    assert state.asteroids_destroyed == 1
    assert state.level_pickups_collected == 0
    assert state.level_asteroids_destroyed == 0


def test_start_high_score_flash_sets_flag():
    state = GameState()
    state.start_high_score_flash()
    assert state.high_score_beaten is True
    assert state.high_score_flash_elapsed == 0.0
    state.update(1.0)
    assert state.high_score_flash_elapsed > 0


def test_apply_settings_updates_fields():
    state = GameState()
    state.apply_settings(
        {
            "music_volume": 0.2,
            "sfx_volume": 0.8,
            "screen_shake": 0.5,
            "player_name": "Pilot1234567",
        }
    )
    assert state.music_volume == 0.2
    assert state.sfx_volume == 0.8
    assert state.screen_shake_scale == 0.5
    assert state.player_name == "Pilot12345"
