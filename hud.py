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
    def __init__(self):
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

    def _load_font(self, path_str, size):
        path = Path(path_str)
        if path.exists():
            try:
                return pygame.font.Font(path.as_posix(), size)
            except Exception:
                pass
        return pygame.font.Font(None, size)

    def make_hud_text(self, font, text):
        shadow = font.render(text, True, self.hud_shadow_color).convert_alpha()
        text_surface = font.render(text, True, self.hud_text_color).convert_alpha()
        return shadow, text_surface

    def draw_subheader(self, surface, rect, text):
        shadow, header = self.make_hud_text(self.font_subheader, text)
        header_rect = header.get_rect()
        header_rect.centerx = rect.centerx
        header_rect.top = rect.top + 6
        shadow_rect = header_rect.copy()
        shadow_rect.move_ip(0, 1)
        surface.blit(shadow, shadow_rect)
        surface.blit(header, header_rect)

    def draw_life_icon(self, surface, cx, cy, color):
        base = LIFE_ICON_SIZE * 0.6
        points = [
            (cx, cy - LIFE_ICON_SIZE),
            (cx - base, cy + LIFE_ICON_SIZE),
            (cx + base, cy + LIFE_ICON_SIZE),
        ]
        pygame.draw.polygon(surface, color, points, 2)

    def draw_gradient(self, surface):
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
            pygame.draw.circle(
                gradient_surface,
                (255, 255, 255, alpha),
                (sx, sy),
                radius,
            )
        surface.blit(gradient_surface, (0, 0))

    def draw_sections(self, surface):
        section_width = SCREEN_WIDTH // 5
        sections = []
        for i in range(5):
            rect = pygame.Rect(i * section_width, 0, section_width, STATUS_BAR_HEIGHT)
            sections.append(rect)
            border_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                border_surface,
                self.section_border_color,
                border_surface.get_rect(),
                1,
            )
            surface.blit(border_surface, rect)
        return sections

    def draw(self, surface, state, player, level_manager):
        self.draw_gradient(surface)
        sections = self.draw_sections(surface)

        life_section, power_section, hi_section, score_section, level_section = sections

        icon_count = state.lives + (1 if state.life_loss_active else 0)
        flash_on = True
        if state.life_loss_active:
            flashes = int(state.life_loss_elapsed / LIFE_ICON_FLICKER_INTERVAL)
            flash_on = flashes % 2 == 0

        self.draw_subheader(surface, life_section, "LIVES")
        icon_center_y = life_section.centery + 10
        start_x = life_section.centerx
        if icon_count:
            total_spacing = (icon_count - 1) * LIFE_ICON_SPACING
            start_x = life_section.centerx - total_spacing / 2
        for i in range(icon_count):
            cx = start_x + i * LIFE_ICON_SPACING
            if state.life_loss_active and i == icon_count - 1 and flash_on:
                self.draw_life_icon(surface, cx, icon_center_y, LIFE_ICON_FLICKER_COLOR)
            else:
                self.draw_life_icon(surface, cx, icon_center_y, "white")

        self.draw_subheader(surface, power_section, "BOMBS")
        bomb_icon_size = 14
        bomb_spacing = 18
        bomb_count = state.bombs
        start_x = power_section.centerx
        if bomb_count:
            total_spacing = (bomb_count - 1) * bomb_spacing
            start_x = power_section.centerx - total_spacing / 2
        for i in range(bomb_count):
            cx = start_x + i * bomb_spacing
            bomb_rect = pygame.Rect(0, 0, bomb_icon_size, bomb_icon_size)
            bomb_rect.center = (cx, power_section.centery + 12)
            pygame.draw.rect(surface, "white", bomb_rect, 2)

        level_number = f"{state.level_index + 1:02d}"
        level_shadow, level_surface = self.make_hud_text(
            self.font_regular, f"LEVEL {level_number}"
        )
        level_rect = level_surface.get_rect()
        level_rect.center = (level_section.centerx, level_section.centery + 8)
        shadow_rect = level_rect.copy()
        shadow_rect.move_ip(0, 1)
        surface.blit(level_shadow, shadow_rect)
        surface.blit(level_surface, level_rect)

        hi_shadow, hi_surface = self.make_hud_text(
            self.font_regular, f"{state.high_score:06d}"
        )
        hi_rect = hi_surface.get_rect()
        self.draw_subheader(surface, hi_section, "HIGH SCORE")
        hi_rect.center = (hi_section.centerx, hi_section.centery + 8)
        hi_shadow_rect = hi_rect.copy()
        hi_shadow_rect.move_ip(0, 1)
        surface.blit(hi_shadow, hi_shadow_rect)
        surface.blit(hi_surface, hi_rect)

        score_shadow, score_surface = self.make_hud_text(
            self.font_regular, f"{state.score:06d}"
        )
        score_rect = score_surface.get_rect()
        self.draw_subheader(surface, score_section, "SCORE")
        score_rect.center = (score_section.centerx, score_section.centery + 8)
        score_shadow_rect = score_rect.copy()
        score_shadow_rect.move_ip(0, 1)
        surface.blit(score_shadow, score_shadow_rect)
        surface.blit(score_surface, score_rect)

        transition = level_manager.transition
        if transition:
            alpha_ratio = max(0.0, 1.0 - (transition.timer / LEVEL_MESSAGE_DURATION))
            alpha = int(255 * alpha_ratio)
            if transition.phase == "top":
                header_shadow, header_surface = self.make_hud_text(
                    self.font_semibold, transition.header
                )
                header_shadow.set_alpha(alpha)
                header_surface.set_alpha(alpha)
                top_y = STATUS_BAR_HEIGHT + (
                    (player.position.y - STATUS_BAR_HEIGHT) / 2
                )
                header_rect = header_surface.get_rect()
                header_rect.center = (SCREEN_WIDTH / 2, top_y)
                shadow_rect = header_rect.copy()
                shadow_rect.move_ip(0, 1)
                surface.blit(header_shadow, shadow_rect)
                surface.blit(header_surface, header_rect)
            elif transition.phase == "bottom":
                level_number = f"{transition.next_level + 1:02d}"
                level_shadow_text, level_surface_text = self.make_hud_text(
                    self.font_semibold, f"LEVEL {level_number}"
                )
                level_shadow_text.set_alpha(alpha)
                level_surface_text.set_alpha(alpha)
                bottom_y = (player.position.y + SCREEN_HEIGHT) / 2
                level_rect = level_surface_text.get_rect()
                level_rect.center = (SCREEN_WIDTH / 2, bottom_y)
                shadow_rect = level_rect.copy()
                shadow_rect.move_ip(0, 1)
                surface.blit(level_shadow_text, shadow_rect)
                surface.blit(level_surface_text, level_rect)
