import os
import sys
from pathlib import Path
from typing import Iterator

import pygame
import pytest

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def init_pygame() -> Iterator[None]:
    """Initialize pygame with dummy drivers so surfaces and fonts work in tests."""
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    try:
        pygame.display.set_mode((1, 1))
    except pygame.error:
        pass
    yield
    pygame.quit()
