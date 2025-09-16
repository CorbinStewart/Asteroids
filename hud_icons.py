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
