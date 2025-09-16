# Project Plan

## Epic A – Core State Architecture
- ✅ **Story A1 – GameState foundation**
  - Create `game_state.py` with a `GameState` dataclass that tracks lives, bombs, score, high score, level, timers, and flags (e.g., `life_lost_this_level`).
  - Add methods `reset_for_level(level)`, `lose_life()`, `add_score(amount)`, `apply_level_bonus()`, and `update(dt)` for timer bookkeeping.
  - Refactor `main.py` to instantiate `GameState` and call these methods instead of mutating globals directly.
- ✅ **Story A2 – LevelManager extraction**
  - Create `level_manager.py` that owns level configuration, completion detection, bonus calculation, and transition state.
  - Replace level-specific logic in `main.py` with `LevelManager.update(dt, player, shots)` and expose helpers such as `is_transitioning` and `current_header()`.
- ✅ **Story A3 – ScoreManager / persistence**
  - Introduce a `ScoreManager` (or extend `GameState`) to encapsulate scoring rules and prepare for high-score persistence.
  - Provide methods for asteroid hits, life-loss penalties, and level completion bonuses; update `GameState` or HUD consumers accordingly.
  - Stub persistence hooks for saving/loading high scores.

## Epic B – HUD Componentization
- ✅ **Story B1 – HUD class skeleton**
  - Move HUD logic into `hud.py` with a `Hud` class storing fonts, colors, and star positions.
  - Expose `hud.update(game_state, dt)` and `hud.draw(surface, game_state, level_manager)`.
- ✅ **Story B2 – Panel rendering & text helpers**
  - Migrate gradient, panel borders, shadowed text, and layout constants into `hud.py` (or a dedicated config module).
  - Replace inline drawing in `main.py` with reusable helpers like `draw_glow_text` and `draw_subheader`.
- ✅ **Story B3 – Icon sprites & power-up placeholders**
  - Implement icon helpers or sprite subclasses for lives, bombs, and future power-ups.
  - Allow the HUD to render icons based on counts provided by `GameState`.
  - Leave hooks for additional HUD modules (e.g., shields, upgrades).

## Epic C – Asset & Utility Organization
- ✅ **Story C1 – Asset loader**
  - Create `assets.py` with cached loaders for fonts, images, and sounds (starting with Orbitron fonts).
  - Update modules to request assets through this helper rather than calling `pygame.font.Font` directly.
- ✅ **Story C2 – Utility module**
  - Move reusable helpers (wrapping, random star creation, score formatting) into `utils.py`.
  - Update dependencies to import from `utils`; add tests as utilities grow.

## Epic D – Testing & Tooling
- **Story D1 – Test harness setup**
  - Add `pytest` configuration and starter tests for `GameState`, `LevelManager`, and HUD layout calculations (mocking surfaces as needed).
  - Document test instructions in `README.md`.
- **Story D2 – Type hints & linting**
  - Gradually annotate new modules with type hints and integrate tools such as `mypy`, `ruff`, or `black` for style consistency.

## Epic E – Future Feature Work
- **Story E1 – Bomb mechanics**: Implement actual bomb usage, cooldowns, and HUD updates.
- **Story E2 – High-score persistence**: Save/load high scores from disk once architecture supports it.
- **Story E3 – Audio & FX**: Trigger sounds or HUD animations on scoring and level transitions.
- **Story E4 – Menu/Settings**: Build title/pause menu leveraging the new modular architecture.
