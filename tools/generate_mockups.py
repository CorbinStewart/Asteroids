#!/usr/bin/env python3
from __future__ import annotations

import os
import random
import sys
from pathlib import Path
from typing import Tuple

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from constants import (
    NEON_COLORS,
    NEON_GLOW_RADII,
    NEON_LINE_WEIGHTS,
    ORBITRON_FONT_PATH,
    ORBITRON_SEMIBOLD_FONT_PATH,
)
from glow import create_glow_layer

OUTPUT_DIR = Path("docs/mockups")
HUD_MOCKUP_PATH = OUTPUT_DIR / "hud_panel.png"
PLAYFIELD_MOCKUP_PATH = OUTPUT_DIR / "playfield_scene.png"
PICKUP_MOCKUP_PATH = OUTPUT_DIR / "pickup_icon.png"


def lighten(color: Tuple[int, int, int], amount: float = 0.25) -> Tuple[int, int, int]:
    return tuple(min(255, int(c + (255 - c) * amount)) for c in color)


def load_font(path: str, size: int) -> pygame.font.Font:
    try:
        return pygame.font.Font(path, size)
    except (FileNotFoundError, OSError):
        return pygame.font.Font(None, size)


def render_text(text: str, font: pygame.font.Font, color: Tuple[int, int, int]) -> pygame.Surface:
    return font.render(text, True, color)


def blit_glow(
    surface: pygame.Surface,
    shape_surface: pygame.Surface,
    position: Tuple[int, int],
    color: Tuple[int, int, int],
    radius: int,
    alpha: int = 150,
    passes: int = 3,
) -> None:
    glow_surface, offset = create_glow_layer(
        shape_surface,
        color,
        radius=radius,
        alpha=alpha,
        passes=passes,
    )
    surface.blit(glow_surface, (position[0] - offset[0], position[1] - offset[1]), special_flags=pygame.BLEND_ADD)


def draw_triangle(surface: pygame.Surface, center: Tuple[int, int], size: int, color: Tuple[int, int, int]) -> None:
    cx, cy = center
    points = [
        (cx, cy - size),
        (cx - size * 0.7, cy + size),
        (cx + size * 0.7, cy + size),
    ]
    pygame.draw.polygon(surface, color, points, width=NEON_LINE_WEIGHTS["core"])


def draw_hud_mockup() -> pygame.Surface:
    surface = pygame.Surface((960, 220), pygame.SRCALPHA)
    surface.fill(NEON_COLORS["neutral_mid"])

    panel_rect = pygame.Rect(40, 32, 1100, 136)
    base = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(base, (255, 255, 255, 0), base.get_rect(), border_radius=16)
    blit_glow(
        surface,
        base,
        panel_rect.topleft,
        NEON_COLORS["hud_frame"],
        radius=NEON_GLOW_RADII["hud_outer"],
        alpha=110,
    )
    pygame.draw.rect(surface, NEON_COLORS["hud_fill"], panel_rect, border_radius=16)
    pygame.draw.rect(surface, NEON_COLORS["hud_frame"], panel_rect, width=NEON_LINE_WEIGHTS["hud_outer"], border_radius=16)
    inner_rect = panel_rect.inflate(-28, -28)
    pygame.draw.rect(surface, NEON_COLORS["hud_shadow"], inner_rect, width=NEON_LINE_WEIGHTS["hud_inner"], border_radius=12)

    header_font = load_font(ORBITRON_SEMIBOLD_FONT_PATH, 28)
    value_font = load_font(ORBITRON_SEMIBOLD_FONT_PATH, 36)

    label_y = panel_rect.top + 26
    value_y = label_y + 40

    score_x = panel_rect.left + 48
    high_x = panel_rect.left + 280
    lives_x = panel_rect.left + 520
    bombs_x = panel_rect.left + 760
    wave_x = panel_rect.left + 970

    score_text = header_font.render("SCORE", True, NEON_COLORS["highlight_text"])
    score_value = value_font.render("001250", True, NEON_COLORS["player_primary"])
    surface.blit(score_text, (score_x, label_y))
    surface.blit(score_value, (score_x, value_y))

    high_text = header_font.render("HIGH SCORE", True, NEON_COLORS["highlight_text"])
    high_value = value_font.render("012500", True, NEON_COLORS["player_primary"])
    surface.blit(high_text, (high_x, label_y))
    surface.blit(high_value, (high_x, value_y))

    lives_label = header_font.render("LIVES", True, NEON_COLORS["highlight_text"])
    surface.blit(lives_label, (lives_x, label_y))
    for i in range(3):
        triangle_surface = pygame.Surface((48, 48), pygame.SRCALPHA)
        draw_triangle(triangle_surface, (24, 28), 18, NEON_COLORS["player_primary"])
        tri_pos = (lives_x + 12 + i * 48, panel_rect.top + 64)
        blit_glow(
            surface,
            triangle_surface,
            tri_pos,
            lighten(NEON_COLORS["player_primary"], 0.35),
            radius=NEON_GLOW_RADII["micro"],
            alpha=130,
        )
        surface.blit(triangle_surface, tri_pos)

    bombs_label = header_font.render("BOMBS", True, NEON_COLORS["highlight_text"])
    surface.blit(bombs_label, (bombs_x, label_y))
    for i in range(2):
        ring_surface = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(ring_surface, NEON_COLORS["hazard_secondary"], (24, 24), 18, width=NEON_LINE_WEIGHTS["core"])
        ring_pos = (bombs_x + 20 + i * 62, panel_rect.top + 60)
        blit_glow(
            surface,
            ring_surface,
            ring_pos,
            lighten(NEON_COLORS["hazard_secondary"], 0.35),
            radius=NEON_GLOW_RADII["core"],
            alpha=120,
        )
        surface.blit(ring_surface, ring_pos)
        glyph = render_text("B", value_font, NEON_COLORS["highlight_text"])
        glyph_rect = glyph.get_rect(center=(ring_pos[0] + 24, ring_pos[1] + 24))
        glyph_rect.x += 1
        glyph_rect.y -= 1
        surface.blit(glyph, glyph_rect)

    wave_label = header_font.render("LEVEL", True, NEON_COLORS["highlight_text"])
    wave_value = value_font.render("04", True, NEON_COLORS["player_primary"])
    surface.blit(wave_label, (wave_x, label_y))
    surface.blit(wave_value, (wave_x, value_y))

    return surface


def draw_playfield_mockup() -> pygame.Surface:
    surface = pygame.Surface((960, 540), pygame.SRCALPHA)
    surface.fill(NEON_COLORS["neutral_base"])

    # Grid overlay
    grid = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for x in range(0, surface.get_width(), 40):
        pygame.draw.line(grid, (*NEON_COLORS["hud_shadow"], 40), (x, 0), (x, surface.get_height()))
    for y in range(0, surface.get_height(), 40):
        pygame.draw.line(grid, (*NEON_COLORS["hud_shadow"], 40), (0, y), (surface.get_width(), y))
    surface.blit(grid, (0, 0))

    # Nebula pulses
    nebula = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(nebula, (*NEON_COLORS["hud_frame"], 70), (240, 200), 240, width=4)
    pygame.draw.circle(nebula, (*NEON_COLORS["hazard_secondary"], 60), (720, 360), 220, width=4)
    surface.blit(nebula, (0, 0), special_flags=pygame.BLEND_ADD)

    rng = random.Random(42)
    for _ in range(140):
        x = rng.randint(0, surface.get_width() - 1)
        y = rng.randint(0, surface.get_height() - 1)
        color = (*NEON_COLORS["highlight_text"], rng.randint(40, 90))
        surface.fill(color, (x, y, 2, 2))

    # Player ship.
    draw_triangle(surface, (480, 320), 24, NEON_COLORS["player_primary"])
    player_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
    draw_triangle(player_surface, (40, 46), 28, NEON_COLORS["player_primary"])
    blit_glow(
        surface,
        player_surface,
        (440, 280),
        lighten(NEON_COLORS["player_primary"], 0.35),
        radius=NEON_GLOW_RADII["core"],
        alpha=150,
    )
    surface.blit(player_surface, (440, 280))

    # Shots.
    for offset in (-60, -30, 0):
        shot_pos = (480 + offset, 220 - offset // 3)
        pygame.draw.circle(surface, NEON_COLORS["player_primary"], shot_pos, 4, width=1)
        pygame.draw.circle(surface, NEON_COLORS["player_inner_glow"], shot_pos, 2)

    # Asteroids.
    for radius, center, color in [
        (52, (360, 280), NEON_COLORS["hazard_primary"]),
        (36, (620, 200), NEON_COLORS["hazard_secondary"]),
    ]:
        circle_surface = pygame.Surface((radius * 2 + 6, radius * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, color, (radius + 3, radius + 3), radius, width=NEON_LINE_WEIGHTS["core"])
        blit_glow(
            surface,
            circle_surface,
            (center[0] - radius - 3, center[1] - radius - 3),
            lighten(color, 0.35),
            radius=NEON_GLOW_RADII["core"],
            alpha=130,
        )
        surface.blit(circle_surface, (center[0] - radius - 3, center[1] - radius - 3))

    # Bomb wave ring.
    pygame.draw.circle(surface, NEON_COLORS["highlight_text"], (480, 320), 140, width=2)
    pygame.draw.circle(surface, NEON_COLORS["highlight_text"], (480, 320), 180, width=1)

    return surface


def draw_pickup_mockup() -> pygame.Surface:
    surface = pygame.Surface((256, 256), pygame.SRCALPHA)
    surface.fill(NEON_COLORS["neutral_mid"])

    ring_surface = pygame.Surface((160, 160), pygame.SRCALPHA)
    pygame.draw.circle(ring_surface, NEON_COLORS["hazard_secondary"], (80, 80), 60, width=NEON_LINE_WEIGHTS["core"])
    pygame.draw.circle(ring_surface, NEON_COLORS["hazard_secondary"], (80, 80), 32, width=NEON_LINE_WEIGHTS["hud_inner"])
    blit_glow(
        surface,
        ring_surface,
        (48, 48),
        lighten(NEON_COLORS["hazard_secondary"], 0.35),
        radius=NEON_GLOW_RADII["event"],
        alpha=130,
        passes=4,
    )
    surface.blit(ring_surface, (48, 48))

    font = load_font(ORBITRON_SEMIBOLD_FONT_PATH, 92)
    glyph = render_text("B", font, NEON_COLORS["highlight_text"])
    glyph_rect = glyph.get_rect(center=(128, 128))
    glyph_rect.x += 5
    glyph_rect.y -= 3
    surface.blit(glyph, glyph_rect)

    orbit = pygame.Surface((160, 160), pygame.SRCALPHA)
    pygame.draw.circle(orbit, NEON_COLORS["player_highlight"], (80, 80), 74, width=1)
    blit_glow(surface, orbit, (48, 48), lighten(NEON_COLORS["player_highlight"], 0.2), radius=NEON_GLOW_RADII["event"], alpha=80)
    surface.blit(orbit, (48, 48))

    return surface


def main() -> None:
    pygame.init()
    pygame.font.init()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    hud = draw_hud_mockup()
    playfield = draw_playfield_mockup()
    pickup = draw_pickup_mockup()

    pygame.image.save(hud, HUD_MOCKUP_PATH.as_posix())
    pygame.image.save(playfield, PLAYFIELD_MOCKUP_PATH.as_posix())
    pygame.image.save(pickup, PICKUP_MOCKUP_PATH.as_posix())

    pygame.quit()


if __name__ == "__main__":
    main()
