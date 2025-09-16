from __future__ import annotations

import random
from typing import Tuple


class ScreenShake:
    def __init__(self) -> None:
        self.timer = 0.0
        self.duration = 0.0
        self.magnitude = 0.0
        self._rng = random.Random()

    def start(self, duration: float, magnitude: float) -> None:
        self.duration = max(0.0, duration)
        self.timer = self.duration
        self.magnitude = max(0.0, magnitude)

    def update(self, dt: float) -> None:
        if self.timer <= 0.0:
            return
        self.timer -= dt
        if self.timer <= 0.0:
            self.timer = 0.0
            self.magnitude = 0.0

    def offset(self) -> Tuple[int, int]:
        if self.timer <= 0.0 or self.magnitude <= 0.0:
            return (0, 0)
        decay = self.timer / self.duration if self.duration > 0 else 0.0
        strength = self.magnitude * decay
        ox = self._rng.uniform(-strength, strength)
        oy = self._rng.uniform(-strength, strength)
        return int(ox), int(oy)

