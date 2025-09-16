# Repository Guidelines

## Project Structure & Module Organization
Game entry point sits in `main.py`, which boots the Pygame loop and wires together the gameplay. Core components live beside it: `player.py`, `asteroid.py`, `asteroidfield.py`, `circleshape.py`, and shared values in `constants.py`. Keep new runtime modules flat at the repository root to match the current import expectations. Place reusable assets such as sprites or sounds under `assets/` and reference them using relative paths (for example `assets/ship.png`). Tests belong in `tests/` with mirrored filenames like `tests/test_player.py`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` - create and activate the local development environment.
- `python -m pip install pygame==2.6.1` - install the only runtime dependency listed today.
- `python main.py` - run the game with standard Python tooling.
- `uv run python main.py` - optional helper that reads dependencies from `pyproject.toml` and launches the loop.

## Coding Style & Naming Conventions
Use Python 3.13 features cautiously and stick to 4-space indentation, UTF-8, and Unix newlines. Prefer small, focused modules under about 300 lines. Follow `snake_case` for variables, functions, and modules, and `PascalCase` for classes. Centralize constants in `constants.py` instead of scattering literals. Keep inline comments minimal and informative.

## Testing Guidelines
`pytest` is the expected framework; install it with `python -m pip install pytest` when needed. Place tests in `tests/` and name them `test_<module>.py` with functions like `test_handles_wraparound`. Keep tests deterministic and fast so they can run as part of local loops. Execute the suite via `pytest -q`.

## Commit & Pull Request Guidelines
Write commits with imperative subjects under 72 characters (for example, "Add asteroid split logic") and add a body when explanation helps reviewers. Pull requests should describe motivation, link related issues, and explain validation steps. Include screenshots or short clips when gameplay or UI changes are visible.

## Security & Configuration Tips
Never commit secrets or local artifacts; `.venv/` is already ignored. Favor relative paths to assets to keep portability. Tune gameplay parameters in `constants.py` so designers can tweak frame rate, speeds, and spawn counts from one location.
