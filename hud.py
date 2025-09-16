from pathlib import Path
import random

import pygame

from constants import (
    HEADER_FONT_SIZE,
    HUD_FONT_SIZE,
    ORBITRON_FONT_PATH,
    ORBITRON_SEMIBOLD_FONT_PATH,
    STATUS_BAR_BOTTOM_COLOR,
    STATUS_BAR_HEIGHT,
    STATUS_BAR_TOP_COLOR,
    SUBHEADER_FONT_SIZE,
    LIFE_ICON_SPACING,
    LIFE_ICON_SIZE,
    LIFE_ICON_FLICKER_COLOR,
    LIFE_ICON_FLICKER_INTERVAL,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    LEVEL_MESSAGE_DURATION,
)


class Hud:
    def __init__(self) -> None:
        self.font_regular = self._load_font(ORBITRON_FONT_PATH, HUD_FONT_SIZE)
        self.font_subheader = self._load_font(ORBITRON_FONT_PATH, SUBHEADER_FONT_SIZE)
        self.font_semibold = self._load_font(ORBITRON_SEMIBOLD_FONT_PATH, HEADER_FONT_SIZE)
        self.hud_shadow_color = pygame.Color(120, 160, 255, 70)
        self.hud_text_color = pygame.Color(255, 255, 255, 220)
        self.section_border_color = (255, 255, 255, 40)

        rng = random.Random(42)
        self.hud_stars = [
            (
                rng.randint(8, SCREEN_WIDTH - 8),
                rng.randint(8, STATUS_BAR_HEIGHT - 8),
                rng.choice((1, 2)),
                rng.randint(40, 60),
            )
            for _ in range(8)
        ]
        section_width = SCREEN_WIDTH // 5
        self.sections = [
            pygame.Rect(i * section_width, 0, section_width, STATUS_BAR_HEIGHT)
            for i in range(5)
        ]

    def _load_font(self, path_str: str, size: int) -> pygame.font.Font:
        path = Path(path_str)
        if path.exists():
            try:
                return pygame.font.Font(path.as_posix(), size)
            except Exception:
                pass
        return pygame.font.Font(None, size)

    def make_hud_text(self, font, text: str):
        shadow = font.render(text, True, self.hud_shadow_color).convert_alpha()
        text_surface = font.render(text, True, self.hud_text_color).convert_alpha()
        return shadow, text_surface

    def draw_subheader(self, surface, rect, text: str):
        shadow, header = self.make_hud_text(self.font_subheader, text)
        header_rect = header.get_rect()
        header_rect.centerx = rect.centerx
        header_rect.top = rect.top + 6
        shadow_rect = header_rect.copy()
        shadow_rect.move_ip(0, 1)
        surface.blit(shadow, shadow_rect)
        surface.blit(header, header_rect)

    def _draw_gradient(self, surface):
        gradient_surface = pygame.Surface((SCREEN_WIDTH, STATUS_BAR_HEIGHT), pygame.SRCALPHA)
        top_color = pygame.Color(*STATUS_BAR_TOP_COLOR, 255)
        bottom_color = pygame.Color(*STATUS_BAR_BOTTOM_COLOR, 255)
        for y in range(STATUS_BAR_HEIGHT):
            blend = y / max(1, STATUS_BAR_HEIGHT - 1)
            r = int(top_color.r + (bottom_color.r - top_color.r) * blend)
            g = int(top_color.g + (bottom_color.g - top_color.g) * blend)
            b = int(top_color.b + (bottom_color.b - top_color.b) * blend)
            pygame.draw.line(gradient_surface, (r, g, b, 255), (0, y), (SCREEN_WIDTH, y))
        pygame.draw.line(
            gradient_surface,
            (255, 255, 255, 60),
            (0, STATUS_BAR_HEIGHT - 2),
            (SCREEN_WIDTH, STATUS_BAR_HEIGHT - 2),
        )
        pygame.draw.line(
            gradient_surface,
            (255, 255, 255, 200),
            (0, STATUS_BAR_HEIGHT - 1),
            (SCREEN_WIDTH, STATUS_BAR_HEIGHT - 1),
        )
        for sx, sy, radius, alpha in self.hud_stars:
            pygame.draw.circle(gradient_surface, (255, 255, 255, alpha), (sx, sy), radius)
        surface.blit(gradient_surface, (0, 0))

    def _draw_panel_borders(self, surface):
        for rect in self.sections:
            border_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                border_surface,
                self.section_border_color,
                border_surface.get_rect(),
                1,
            )
            surface.blit(border_surface, rect)

    def _draw_value_panel(self, surface, rect, subheader, text, font):
        if subheader:
            self.draw_subheader(surface, rect, subheader)
        shadow, rendered = self.make_hud_text(font, text)
        rendered_rect = rendered.get_rect()
        rendered_rect.center = (rect.centerx, rect.centery + 8)
        shadow_rect = rendered_rect.copy()
        shadow_rect.move_ip(0, 1)
        surface.blit(shadow, shadow_rect)
        surface.blit(rendered, rendered_rect)

    def _draw_life_icon(self, surface, cx, cy, color):
        base = LIFE_ICON_SIZE * 0.6
        points = [
            (cx, cy - LIFE_ICON_SIZE),
            (cx - base, cy + LIFE_ICON_SIZE),
            (cx + base, cy + LIFE_ICON_SIZE),
        ]
        pygame.draw.polygon(surface, color, points, 2)

    def _draw_lives(self, surface, rect, state):
        self.draw_subheader(surface, rect, "LIVES")
        icon_count = state.lives + (1 if state.life_loss_active else 0)
        flash_on = True
        if state.life_loss_active:
            flashes = int(state.life_loss_elapsed / LIFE_ICON_FLICKER_INTERVAL)
            flash_on = flashes % 2 == 0
        icon_center_y = rect.centery + 10
        start_x = rect.centerx
        if icon_count:
            total_spacing = (icon_count - 1) * LIFE_ICON_SPACING
            start_x = rect.centerx - total_spacing / 2
        for i in range(icon_count):
            cx = start_x + i * LIFE_ICON_SPACING
            color = LIFE_ICON_FLICKER_COLOR if state.life_loss_active and i == icon_count - 1 and flash_on else "white"
            self._draw_life_icon(surface, cx, icon_center_y, color)

    def _draw_bombs(self, surface, rect, state):
        self.draw_subheader(surface, rect, "BOMBS")
        bomb_icon_size = 14
        bomb_spacing = 18
        count = state.bombs
        start_x = rect.centerx
        if count:
            total_spacing = (count - 1) * bomb_spacing
            start_x = rect.centerx - total_spacing / 2
        for i in range(count):
            cx = start_x + i * bomb_spacing
            bomb_rect = pygame.Rect(0, 0, bomb_icon_size, bomb_icon_size)
            bomb_rect.center = (cx, rect.centery + 12)
            pygame.draw.rect(surface, "white", bomb_rect, 2)

    def _draw_transition_text(self, surface, text, alpha, center_y):
        shadow, rendered = self.make_hud_text(self.font_semibold, text)
        shadow.set_alpha(alpha)
        rendered.set_alpha(alpha)
        rect = rendered.get_rect()
        rect.center = (SCREEN_WIDTH / 2, center_y)
        shadow_rect = rect.copy()
        shadow_rect.move_ip(0, 1)
        surface.blit(shadow, shadow_rect)
        surface.blit(rendered, rect)

    def draw(self, surface, state, player, level_manager):
        self._draw_gradient(surface)
        self._draw_panel_borders(surface)
        life_section, power_section, hi_section, score_section, level_section = self.sections

        self._draw_lives(surface, life_section, state)
        self._draw_bombs(surface, power_section, state)

        self._draw_value_panel(
            surface,
            hi_section,
            "HIGH SCORE",
            f"{state.high_score:06d}",
            self.font_regular,
        )

        self._draw_value_panel(
            surface,
            score_section,
            "SCORE",
            f"{state.score:06d}",
            self.font_regular,
        )

        self._draw_value_panel(
            surface,
            level_section,
            "",
            f"LEVEL {state.level_index + 1:02d}",
            self.font_regular,
        )

        transition = level_manager.transition
        if transition:
            alpha_ratio = max(0.0, 1.0 - (transition.timer / LEVEL_MESSAGE_DURATION))
            alpha = int(255 * alpha_ratio)
            if transition.phase == "top":
                self._draw_transition_text(
                    surface,
                    transition.header,
                    alpha,
                    STATUS_BAR_HEIGHT + (player.position.y - STATUS_BAR_HEIGHT) / 2,
                )
            elif transition.phase == "bottom":
                self._draw_transition_text(
                    surface,
                    f"LEVEL {transition.next_level + 1:02d}",
                    alpha,
                    (player.position.y + SCREEN_HEIGHT) / 2,
                )
