from dataclasses import dataclass

from constants import LEVEL_DEFINITIONS, LEVEL_MESSAGE_DURATION
from game_state import GameState
from level_manager import LevelManager


class DummyAsteroidField:
    def __init__(self) -> None:
        self.configure_calls: list[tuple[int, int, float]] = []
        self.complete = False

    def configure_level(self, spawn_total: int, max_active: int, speed_multiplier: float) -> None:
        self.configure_calls.append((spawn_total, max_active, speed_multiplier))

    def level_complete(self) -> bool:
        return self.complete


@dataclass
class DummyScoreManager:
    applied: bool = False

    def apply_level_bonus(self) -> None:
        self.applied = True


def test_configure_level_applies_definition() -> None:
    state = GameState()
    field = DummyAsteroidField()
    score = DummyScoreManager()
    manager = LevelManager(state, field, score)

    manager.configure_level(0)

    assert state.level_index == 0
    assert field.configure_calls[-1] == (
        LEVEL_DEFINITIONS[0]["spawn_total"],
        LEVEL_DEFINITIONS[0]["max_active"],
        LEVEL_DEFINITIONS[0]["speed_multiplier"],
    )


def test_transition_advances_and_configures_next_level() -> None:
    state = GameState()
    field = DummyAsteroidField()
    score = DummyScoreManager()
    manager = LevelManager(state, field, score)

    manager.start_transition(1)

    manager.update(LEVEL_MESSAGE_DURATION + 0.1)
    assert manager.transition is not None
    assert manager.transition.phase == "bottom"

    manager.update(LEVEL_MESSAGE_DURATION + 0.1)

    assert manager.transition is None
    assert state.level_index == 1
    assert field.configure_calls[-1] == (
        LEVEL_DEFINITIONS[1]["spawn_total"],
        LEVEL_DEFINITIONS[1]["max_active"],
        LEVEL_DEFINITIONS[1]["speed_multiplier"],
    )


def test_should_start_transition_checks_completion_flag() -> None:
    state = GameState()
    field = DummyAsteroidField()
    score = DummyScoreManager()
    manager = LevelManager(state, field, score)

    field.complete = False
    assert manager.should_start_transition() is False

    field.complete = True
    assert manager.should_start_transition() is True

    manager.start_transition(1)
    assert manager.should_start_transition() is False


def test_apply_level_completion_awards_bonus() -> None:
    state = GameState()
    field = DummyAsteroidField()
    score = DummyScoreManager()
    manager = LevelManager(state, field, score)

    manager.apply_level_completion()

    assert score.applied is True


def test_levels_remaining_reflects_total_levels() -> None:
    state = GameState(level_index=0)
    field = DummyAsteroidField()
    score = DummyScoreManager()
    manager = LevelManager(state, field, score)

    state.level_index = manager.total_levels - 2
    assert manager.levels_remaining() is True

    state.level_index = manager.total_levels - 1
    assert manager.levels_remaining() is False
