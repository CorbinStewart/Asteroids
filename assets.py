from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pygame

_ASSETS_DIR = Path(__file__).resolve().parent / "assets"

_font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}
_image_cache: Dict[Tuple[str, bool], pygame.Surface] = {}
_sound_cache: Dict[str, pygame.mixer.Sound] = {}


def _path_key(path: str | Path) -> str:
    resolved = _resolve_asset_path(path)
    if resolved is not None:
        return resolved.as_posix()
    return Path(path).as_posix()


def _resolve_asset_path(path: str | Path) -> Path | None:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    if candidate.exists():
        return candidate
    parts = candidate.parts
    if parts and parts[0] == "assets":
        alt = _ASSETS_DIR.joinpath(*parts[1:])
    else:
        alt = _ASSETS_DIR / candidate
    if alt.exists():
        return alt
    return None


def _require_asset(path: str | Path) -> Path:
    resolved = _resolve_asset_path(path)
    if resolved is None:
        raise FileNotFoundError(f"Asset not found: {path}")
    return resolved


def load_font(path: str | Path, size: int) -> pygame.font.Font:
    """Return a cached font, falling back to the default pygame font when missing."""
    key = (_path_key(path), size)
    font = _font_cache.get(key)
    if font is not None:
        return font
    resolved = _resolve_asset_path(path)
    if resolved is not None:
        try:
            font = pygame.font.Font(resolved.as_posix(), size)
        except (FileNotFoundError, pygame.error):
            font = pygame.font.Font(None, size)
    else:
        font = pygame.font.Font(None, size)
    _font_cache[key] = font
    return font


def load_image(path: str | Path, *, convert_alpha: bool = False) -> pygame.Surface:
    """Load and cache an image surface. Conversion is optional to avoid display deps."""
    key = (_path_key(path), convert_alpha)
    surface = _image_cache.get(key)
    if surface is not None:
        return surface
    resolved = _require_asset(path)
    image = pygame.image.load(resolved.as_posix())
    if convert_alpha:
        try:
            image = image.convert_alpha()
        except pygame.error:
            pass
    _image_cache[key] = image
    return image


def load_sound(path: str | Path) -> pygame.mixer.Sound:
    """Load and cache a sound clip from the assets directory."""
    key = _path_key(path)
    sound = _sound_cache.get(key)
    if sound is not None:
        return sound
    resolved = _require_asset(path)
    sound = pygame.mixer.Sound(resolved.as_posix())
    _sound_cache[key] = sound
    return sound


def clear_caches() -> None:
    """Utility for tests to clear memoized assets."""
    _font_cache.clear()
    _image_cache.clear()
    _sound_cache.clear()
