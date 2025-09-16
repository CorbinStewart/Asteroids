import os
from typing import Iterator

import pygame
import pytest


@pytest.fixture(autouse=True)
def init_pygame() -> Iterator[None]:
    """Initialize pygame with dummy drivers so surfaces and fonts work in tests."""
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    yield
    pygame.quit()
