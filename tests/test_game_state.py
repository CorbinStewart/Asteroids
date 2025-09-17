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
    )

    state.reset_for_level(3)

    assert state.level_index == 3
    assert state.life_lost_this_level is False
    assert state.life_loss_active is False
    assert state.life_loss_elapsed == 0.0


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
