# Repository Guidelines

## Project Structure & Module Organization
Runtime modules live at the repository root to support simple imports. `main.py` boots the Pygame loop and orchestrates `GameState`, `LevelManager`, `ScoreManager`, `BombController`, the HUD, and FX/audio helpers. Core entities inherit from `circleshape.py`; gameplay actors include `player.py`, `asteroid.py`, `asteroidfield.py`, `bomb_wave.py`, and `bomb_pickup.py`. Shared values stay in `constants.py`, while reusable visuals and sounds live under `assets/`. Persisted profiles are written to `save/profile.json`. Tests mirror module names inside `tests/` (for example `tests/test_game_state.py`).

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` – create/activate a local virtual environment.
- `python -m pip install pygame==2.6.1` – install the pinned runtime dependency; add `pytest` when running tests.
- `python main.py` – launch the game with the active interpreter.
- `uv run python main.py` – alternative launcher that reads `pyproject.toml` dependencies.
- `pytest -q` – execute the unit-test suite; runs headless thanks to the dummy SDL driver in `tests/conftest.py`.

## Coding Style & Naming Conventions
Use Python 3.11+ features conservatively, four-space indentation, UTF-8, and Unix newlines. Follow `snake_case` for modules, functions, and variables, and `PascalCase` for classes. Prefer small modules (<300 lines) and keep gameplay tuning knobs in `constants.py`. Derive sprites from `CircleShape` to inherit wrapping/collision helpers. Limit inline comments to clarifying intent; rely on descriptive names instead.

## Testing Guidelines
Tests are written with `pytest` and stored in `tests/`. Name files `test_<module>.py` and functions `test_<behavior>()`. Use deterministic randomness by seeding `random.Random` instances when asserting FX or spawn behavior. Ensure new features expose hooks that can be exercised without launching the full Pygame loop; prefer validating audio/FX through dependency injection or dummy objects.

## Commit & Pull Request Guidelines
Write commits with imperative subjects under 72 characters (for example, `Add asteroid split logic`). Include a body when context or validation details aid reviewers. Pull requests should describe motivation, reference related issues, summarize validation (test commands, gameplay capture), and attach screenshots or clips for visible changes.

## Security & Configuration Tips
Do not commit secrets or local artifacts; `.venv/` and build outputs are ignored already. Use relative asset paths (`assets/sounds/...`) to keep bundles portable. Update tuning values via `constants.py` so designers can iterate without code edits. Persisted profile data is versioned—increment `CURRENT_VERSION` and supply migrations when expanding the schema.
