from __future__ import annotations

import random
from typing import List, Sequence, Tuple

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH, STATUS_BAR_HEIGHT

Star = Tuple[int, int, int, int]


def wrap_position(position: pygame.Vector2, radius: float) -> None:
    """Wrap an object around the screen bounds, accounting for the HUD bar."""
    if position.x < -radius:
        position.x = SCREEN_WIDTH + radius
    elif position.x > SCREEN_WIDTH + radius:
        position.x = -radius

    playable_top = STATUS_BAR_HEIGHT
    if position.y < playable_top - radius:
        position.y = SCREEN_HEIGHT + radius
    elif position.y > SCREEN_HEIGHT + radius:
        position.y = playable_top - radius


def create_star_field(
    count: int,
    width: int,
    height: int,
    rng: random.Random | None = None,
    margin: int = 8,
    radius_choices: Sequence[int] = (1, 2),
    alpha_range: Tuple[int, int] = (40, 60),
) -> List[Star]:
    """Return a deterministic set of star positions for HUD background elements."""
    if rng is None:
        rng = random.Random()

    min_alpha, max_alpha = alpha_range
    min_alpha = max(0, min_alpha)
    max_alpha = max(min_alpha, max_alpha)
    choices = tuple(radius_choices) if radius_choices else (1,)

    stars: List[Star] = []
    for _ in range(max(0, count)):
        x = rng.randint(margin, max(margin, width - margin))
        y = rng.randint(margin, max(margin, height - margin))
        radius = rng.choice(choices)
        alpha = rng.randint(min_alpha, max_alpha)
        stars.append((x, y, radius, alpha))
    return stars


def format_score(value: int, width: int = 6) -> str:
    """Format the score using zero padding to keep HUD alignment consistent."""
    width = max(1, width)
    value = max(0, value)
    return f"{value:0{width}d}"
