from __future__ import annotations

import pygame

from assets import load_font
from constants import (
    HEADER_FONT_SIZE,
    HUD_FONT_SIZE,
    HUD_SMALL_FONT_SIZE,
    ORBITRON_FONT_PATH,
    ORBITRON_SEMIBOLD_FONT_PATH,
)
from utils import format_score


class RunSummaryOverlay:
    def __init__(self, state, profile, level_completed: bool) -> None:
        self.state = state
        self.profile = profile
        self.level_completed = level_completed
        self.font_title = load_font(ORBITRON_SEMIBOLD_FONT_PATH, HEADER_FONT_SIZE)
        self.font_regular = load_font(ORBITRON_FONT_PATH, HUD_FONT_SIZE)
        self.font_small = load_font(ORBITRON_FONT_PATH, HUD_SMALL_FONT_SIZE)

    def draw(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        width, height = surface.get_size()
        panel_width = int(width * 0.65)
        panel_height = int(height * 0.65)
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_rect = panel.get_rect(center=(width // 2, height // 2))

        pygame.draw.rect(panel, (20, 24, 48, 220), panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (120, 160, 255, 220), panel.get_rect(), 2, border_radius=12)

        # Title
        title_text = "RUN COMPLETE" if self.level_completed else "RUN SUMMARY"
        title = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title.get_rect(center=(panel_width // 2, 60))
        panel.blit(title, title_rect)

        stats_start_y = title_rect.bottom + 30
        stats = [
            ("Score", format_score(self.state.score)),
            ("High Score", format_score(self.state.high_score)),
            ("Level Reached", f"{self.state.level_index + 1:02d}"),
            ("Time Survived", self._format_time(self.state.run_time)),
            ("Bombs Used", str(self.state.bombs_used)),
            ("Pickups Collected", str(self.state.pickups_collected)),
        ]
        for idx, (label, value) in enumerate(stats):
            text = self.font_regular.render(f"{label}: {value}", True, (200, 220, 255))
            text_rect = text.get_rect()
            text_rect.left = 60
            text_rect.top = stats_start_y + idx * (HUD_FONT_SIZE + 10)
            panel.blit(text, text_rect)

        # Leaderboard
        board_title = self.font_regular.render("TOP SCORES", True, (255, 220, 120))
        board_rect = board_title.get_rect()
        board_rect.right = panel_width - 60
        board_rect.top = stats_start_y
        panel.blit(board_title, board_rect)

        name = self.profile.settings().get("player_name", "ACE")
        latest_score = self.state.score
        latest_level = self.state.level_index + 1
        board = self.profile.leaderboard()[:5]
        for idx, entry in enumerate(board):
            entry_name = entry.get("name", "---")
            entry_score = format_score(entry.get("score", 0))
            entry_level = entry.get("level", 0)
            line = f"{entry_name:<10}  {entry_score}  L{entry_level:02d}"
            is_latest = (
                entry.get("score") == latest_score
                and entry.get("level") == latest_level
                and entry.get("name") == (name[:10] or "ACE")
            )
            color = (255, 255, 255) if is_latest else (180, 200, 255)
            text = self.font_small.render(line, True, color)
            text_rect = text.get_rect()
            text_rect.right = panel_width - 60
            text_rect.top = board_rect.bottom + 10 + idx * (HUD_SMALL_FONT_SIZE + 6)
            panel.blit(text, text_rect)

        # Instructions
        instructions = self.font_small.render(
            "Press ENTER to play again    •    ESC to quit",
            True,
            (200, 200, 200),
        )
        instr_rect = instructions.get_rect(center=(panel_width // 2, panel_height - 40))
        panel.blit(instructions, instr_rect)

        surface.blit(panel, panel_rect)

    @staticmethod
    def _format_time(seconds: float) -> str:
        total_seconds = max(0, int(seconds))
        minutes, secs = divmod(total_seconds, 60)
        return f"{minutes:02d}:{secs:02d}"


def show_run_summary(
    screen: pygame.Surface,
    state,
    profile,
    level_completed: bool,
) -> bool:
    overlay = RunSummaryOverlay(state, profile, level_completed)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return True
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
        dt = clock.tick(60)
        screen.fill("black")
        overlay.draw(screen)
        pygame.display.flip()
