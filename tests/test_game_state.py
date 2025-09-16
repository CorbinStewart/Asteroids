from game_state import GameState
from constants import LIFE_ICON_FLICKER_DURATION, PLAYER_START_LIVES


def test_reset_for_level_clears_loss_flags():
    state = GameState(
        lives=PLAYER_START_LIVES,
        bombs=1,
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
