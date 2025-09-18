from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pygame

try:
    import numpy as _np
except Exception:  # pragma: no cover - numpy optional in runtime
    _np = None

_Color = Tuple[int, int, int]


def _blur_surface(surface: pygame.Surface, *, passes: int = 3, shrink: float = 0.65) -> pygame.Surface:
    """Apply a cheap smooth-scale blur to approximate a glow spread."""
    result = surface.copy()
    for _ in range(max(1, passes)):
        width, height = result.get_size()
        scaled_size = (
            max(1, int(width * shrink)),
            max(1, int(height * shrink)),
        )
        result = pygame.transform.smoothscale(result, scaled_size)
        result = pygame.transform.smoothscale(result, (width, height))
    return result


def create_glow_layer(
    source: pygame.Surface,
    color: _Color,
    *,
    radius: int = 8,
    alpha: int = 180,
    passes: int = 3,
) -> tuple[pygame.Surface, Tuple[int, int]]:
    """Build a standalone glow surface for the given sprite surface.

    Returns the glow surface and the offset at which the original sprite should be
    blitted to align with the glow.
    """
    if radius <= 0:
        empty = pygame.Surface(source.get_size(), pygame.SRCALPHA)
        return empty, (0, 0)

    mask = pygame.mask.from_surface(source)
    if mask.count() == 0:
        empty = pygame.Surface(source.get_size(), pygame.SRCALPHA)
        return empty, (0, 0)

    mask_surface = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
    width, height = mask_surface.get_size()
    glow = pygame.Surface((width + radius * 2, height + radius * 2), pygame.SRCALPHA)
    glow.blit(mask_surface, (radius, radius))

    blurred = _blur_surface(glow, passes=passes)
    if _np is not None:
        alpha_values = pygame.surfarray.array_alpha(blurred).astype("uint16", copy=True)
        tinted = pygame.Surface(blurred.get_size(), pygame.SRCALPHA)
        rgb_view = pygame.surfarray.pixels3d(tinted)
        rgb_view[:] = color
        del rgb_view
        scaled_alpha = (alpha_values * alpha) // 255
        alpha_view = pygame.surfarray.pixels_alpha(tinted)
        _np.copyto(alpha_view, scaled_alpha.astype("uint8"))
        del alpha_view
    else:  # Fallback when numpy unavailable
        tinted = blurred.copy()
        tinted.fill((*color, 0), special_flags=pygame.BLEND_RGBA_MULT)
        if alpha < 255:
            alpha_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, alpha))
            tinted.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted, (radius, radius)


def render_surface_with_glow(
    source: pygame.Surface,
    color: _Color,
    *,
    radius: int = 8,
    alpha: int = 180,
    passes: int = 3,
) -> tuple[pygame.Surface, Tuple[int, int]]:
    """Return a composite surface containing glow + source."""
    glow_surface, offset = create_glow_layer(source, color, radius=radius, alpha=alpha, passes=passes)
    composite = glow_surface.copy()
    composite.blit(source, offset)
    return composite, offset


@dataclass
class GlowConfig:
    color: _Color
    radius: int = 8
    alpha: int = 180
    passes: int = 3


class GlowSprite(pygame.sprite.Sprite):
    """Sprite wrapper that composites a glow around a base surface."""

    def __init__(self, base_surface: pygame.Surface, config: GlowConfig) -> None:
        super().__init__()
        self._base = base_surface
        self.config = config
        self.image, self._base_offset = render_surface_with_glow(
            self._base,
            config.color,
            radius=config.radius,
            alpha=config.alpha,
            passes=config.passes,
        )
        self.rect = self.image.get_rect()

    def update_base(self, base_surface: pygame.Surface) -> None:
        """Replace the base surface and rebuild the glow composite."""
        self._base = base_surface
        self.image, self._base_offset = render_surface_with_glow(
            self._base,
            self.config.color,
            radius=self.config.radius,
            alpha=self.config.alpha,
            passes=self.config.passes,
        )
        self.rect.size = self.image.get_size()

    def draw(self, surface: pygame.Surface, position: Tuple[int, int]) -> None:
        """Convenience method to blit the sprite at a position without groups."""
        rect = self.rect.copy()
        rect.topleft = (position[0] - self._base_offset[0], position[1] - self._base_offset[1])
        surface.blit(self.image, rect)
