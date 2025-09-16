from types import SimpleNamespace

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, STATUS_BAR_HEIGHT
from game_state import GameState
from hud import Hud


def test_hud_sections_cover_status_bar():
    hud = Hud()

    assert len(hud.sections) == 5
    section_width = SCREEN_WIDTH // 5
    for index, rect in enumerate(hud.sections):
        assert rect.left == index * section_width
        assert rect.width == section_width
        assert rect.top == 0
        assert rect.height == STATUS_BAR_HEIGHT
    assert hud.sections[-1].right == SCREEN_WIDTH

    assert len(hud.hud_stars) == 8
    for x, y, radius, alpha in hud.hud_stars:
        assert 0 <= x <= SCREEN_WIDTH
        assert 0 <= y <= STATUS_BAR_HEIGHT
        assert radius in (1, 2)
        assert 40 <= alpha <= 60


def test_hud_draw_renders_status_bar_gradient():
    hud = Hud()
    state = GameState(score=12345, high_score=67890, bombs=2)
    player = SimpleNamespace(position=pygame.Vector2(SCREEN_WIDTH / 2, STATUS_BAR_HEIGHT + 50))
    level_manager = SimpleNamespace(transition=None)

    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.fill("black")

    hud.draw(surface, state, player, level_manager)

    top_left = surface.get_at((0, 0))
    assert top_left != pygame.Color(0, 0, 0, 255)
