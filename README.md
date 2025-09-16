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
