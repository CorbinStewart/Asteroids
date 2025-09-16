# Repository Guidelines

## Project Structure & Module Organization
- Entry point: `main.py` (starts the Pygame loop).
- Core modules: `player.py`, `asteroid.py`, `asteroidfield.py`, `circleshape.py`, `constants.py`.
- Root-only layout; no packages yet. If you add assets, place them under `assets/` and reference with relative paths.
- Suggested tests location: `tests/` (see Testing Guidelines).

## Build, Test, and Development Commands
- Python: 3.13 (see `pyproject.toml`).
- Create venv: `python -m venv .venv && source .venv/bin/activate`.
- Install runtime deps: `python -m pip install pygame==2.6.1`.
- Run the game: `python main.py`.
- Using `uv` (optional): `uv run python main.py` (reads deps from `pyproject.toml`).

## Coding Style & Naming Conventions
- Python style: 4-space indentation, UTF-8, Unix line endings.
- Naming: `snake_case` for variables/functions, `PascalCase` for classes, module filenames in `snake_case.py`.
- Keep modules focused (≤ ~300 lines) and prefer small, testable methods.
- Constants live in `constants.py`. Reuse them instead of hardcoding literals.

## Testing Guidelines
- Framework: `pytest` (not yet included). Install with `python -m pip install pytest`.
- Location: create `tests/` with files like `tests/test_player.py`.
- Naming: `test_*.py` files, `test_*` functions. Keep unit tests fast and deterministic.
- Run tests: `pytest -q`.

## Commit & Pull Request Guidelines
- Commits: short, imperative subject lines (e.g., "Add asteroid split logic").
  - Start with a verb; present tense; ≤ 72 chars.
  - Include a body when rationale or context helps reviewers.
- Pull Requests must include:
  - Clear description of changes and motivation; link related issues.
  - How to run/validate (commands, expected behavior). Add a short GIF/screenshot of gameplay when UI changes.
  - Scope discipline: no unrelated refactors; keep diffs focused.

## Security & Configuration Tips
- Do not commit secrets or local artifacts (`.venv/` is already ignored).
- Prefer relative paths for assets; avoid absolute user-specific paths.
- Keep frame rate and screen constants in `constants.py` to centralize tuning.
