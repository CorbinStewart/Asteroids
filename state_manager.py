from __future__ import annotations

from enum import Enum, auto


class AppState(Enum):
    """High-level game views supported by the menu/state flow."""

    TITLE = auto()
    GAMEPLAY = auto()
    PAUSE = auto()
    SETTINGS = auto()
    RUN_SUMMARY = auto()


class AppStateManager:
    """Lightweight stack-based state helper for menu navigation."""

    def __init__(self, initial: AppState) -> None:
        self._stack: list[AppState] = [initial]

    @property
    def current(self) -> AppState:
        return self._stack[-1]

    def push(self, state: AppState) -> None:
        self._stack.append(state)

    def replace(self, state: AppState) -> None:
        self._stack[-1] = state

    def pop(self) -> AppState:
        if len(self._stack) == 1:
            return self._stack[0]
        self._stack.pop()
        return self._stack[-1]

    def reset(self, state: AppState) -> None:
        self._stack = [state]
