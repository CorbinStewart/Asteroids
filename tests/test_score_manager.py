from game_state import GameState
from score_manager import ScoreManager


def test_first_run_does_not_flash():
    state = GameState()
    state.initial_high_score = 0
    manager = ScoreManager(state)

    manager.add_points(100)
    assert state.high_score == 100
    assert state.high_score_beaten is False

    manager.add_points(50)
    assert state.high_score == 150
    assert state.high_score_beaten is False


def test_existing_high_score_triggers_flash():
    state = GameState(high_score=200, initial_high_score=200)
    manager = ScoreManager(state)

    manager.add_points(50)
    assert state.high_score == 200
    assert state.high_score_beaten is False

    manager.add_points(200)
    assert state.high_score == 250
    assert state.high_score_beaten is True
    assert state.high_score_flash_elapsed == 0.0
