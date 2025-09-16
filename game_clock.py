from __future__ import annotations


class GameClock:
    """Global time scaling helper used to drive slow-motion effects."""

    def __init__(self) -> None:
        self._time_scale: float = 1.0

    @property
    def time_scale(self) -> float:
        return self._time_scale

    def set_time_scale(self, scale: float) -> None:
        self._time_scale = max(0.0, scale)

    def reset_time_scale(self) -> None:
        self._time_scale = 1.0

    def scale_dt(self, dt: float) -> float:
        return dt * self._time_scale
