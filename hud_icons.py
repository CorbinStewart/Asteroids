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
    def __init__(self, size: int) -> None:
        self.size = size

    def create_surface(self, color: tuple[int, int, int], letter_color: tuple[int, int, int] = (255, 220, 60)) -> pygame.Surface:
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        rect = surface.get_rect()
        pygame.draw.rect(surface, color, rect, border_radius=4)
        font = pygame.font.Font(None, max(10, int(self.size * 0.6)))
        text = font.render("B", True, letter_color)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
        return surface

    def draw(self, surface: pygame.Surface, center: tuple[int, int], color) -> None:
        icon_surface = self.create_surface(color)
        rect = icon_surface.get_rect(center=center)
        surface.blit(icon_surface, rect)
