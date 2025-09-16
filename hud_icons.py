import pygame


class Icon:
    def draw(self, surface: pygame.Surface, center: tuple[int, int], color) -> None:
        raise NotImplementedError


class TriangleIcon(Icon):
    def __init__(self, size: float) -> None:
        self.size = size

    def draw(self, surface: pygame.Surface, center: tuple[int, int], color) -> None:
        cx, cy = center
        base = self.size * 0.6
        points = [
            (cx, cy - self.size),
            (cx - base, cy + self.size),
            (cx + base, cy + self.size),
        ]
        pygame.draw.polygon(surface, color, points, 2)


class SquareIcon(Icon):
    def __init__(self, size: int) -> None:
        self.size = size

    def draw(self, surface: pygame.Surface, center: tuple[int, int], color) -> None:
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = center
        pygame.draw.rect(surface, color, rect, 2)


class BombIcon(Icon):
    def __init__(self, size: int, line_width: int = 2) -> None:
        self.size = size
        self.line_width = line_width

    def create_surface(
        self,
        stroke_color: tuple[int, int, int],
        letter_color: tuple[int, int, int] | None = None,
        inner_color: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        rect = surface.get_rect()
        if inner_color:
            pygame.draw.rect(surface, inner_color, rect)
        pygame.draw.rect(surface, stroke_color, rect, self.line_width)
        if letter_color:
            font_size = max(10, int(self.size * 0.6))
            font = pygame.font.Font(None, font_size)
            text = font.render("B", True, letter_color)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
        return surface

    def draw(self, surface: pygame.Surface, center: tuple[int, int], color) -> None:
        icon_surface = self.create_surface(color, None)
        rect = icon_surface.get_rect(center=center)
        surface.blit(icon_surface, rect)
