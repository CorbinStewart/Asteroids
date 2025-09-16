# Asteroids

## Development Setup
- Create a virtual environment:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  ```
- Install runtime dependencies:
  ```bash
  python -m pip install pygame==2.6.1
  ```
- (Optional) use `uv` to run the game with dependencies from `pyproject.toml`:
  ```bash
  uv run python main.py
  ```

## Running the Game
```bash
python main.py
```

## Running Tests
Install `pytest` if needed and run the suite:
```bash
python -m pip install pytest
pytest -q
```

## Code Quality Tools
Install optional tooling for type checks and linting:
```bash
python -m pip install mypy ruff black
```

- Run static type checks:
  ```bash
  mypy .
  ```
- Run linting (imports/pep):
  ```bash
  ruff check .
  ```
- Format code:
  ```bash
  black .
  ```

## Asset Organization
- Fonts: place under `assets/fonts/`
- Music stems/tracks: `assets/music/`
- Sound effects: `assets/sounds/`
- Use consistent naming (e.g., `bgm_phase01.ogg`, `sfx_shot_small.wav`) so loaders can select variants predictably.
- Reference assets via relative paths (for example `assets/sounds/bomb.wav`);
  the loader resolves these subfolders automatically.
