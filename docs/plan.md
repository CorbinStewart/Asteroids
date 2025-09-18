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
- ✅ **Story D1 – Test harness setup**
  - Add `pytest` configuration and starter tests for `GameState`, `LevelManager`, and HUD layout calculations (mocking surfaces as needed).
  - Document test instructions in `README.md`.
- ✅ **Story D2 – Type hints & linting**
  - Gradually annotate new modules with type hints and integrate tools such as `mypy`, `ruff`, or `black` for style consistency.

## Epic E – Bomb Mechanics & Shockwave Flow
- ✅ **Story E1 – Bomb core systems**
  - Extend `GameState` / `ScoreManager` for bomb charge tracking and input handling.
  - Bind the `B` key to trigger bombs, including cooldown checks and charge consumption.
  - Introduce a central game clock/time-scale helper so slow-motion effects can be applied consistently.
  - Broadcast an activation event so other systems (HUD, FX) can respond.
- ✅ **Story E2 – Shockwave & time dilation**
  - Spawn an expanding shockwave from the ship when a bomb detonates.
  - Apply a temporary global time-scale drop that eases back to normal as the wave dissipates via the shared game clock.
  - Ensure player controls remain responsive while other entities honor the slow-motion multiplier.
- ✅ **Story E3 – Asteroid resolution**
  - Downgrade asteroids hit by the wave: large→two medium, medium→two small, small→destroy.
  - Prevent double-processing and keep score values consistent with standard splits.
- ✅ **Story E4 – Feedback & HUD cues**
  - Add screen shake, flash, and audio hooks synchronized with the wave lifecycle.
  - Enhance HUD bomb indicators (ready, charging, empty) and flash on activation.
  - Integrate the new bomb icon in both HUD and activation effects.
- ✅ **Story E5 – Bomb pickup loop**
  - Introduce a bomb pickup sprite that gently bobs, flickers before expiring, and drifts from the spawn point.
  - Roll drop chances on asteroid destruction with odds that scale per level (base 1% + 0.1% per level, capped as needed), respecting simultaneity limits.
  - Award a stored bomb when the player collects the pickup, up to a configured maximum.
- ✅ **Story E6 – Bomb icon asset**
  - Create a red square icon with a yellow “B” for HUD usage and pickup rendering.
  - Provide helper routines so future HUD modules can recolor or animate the icon easily.
- ✅ **Story E7 – Balancing & regression tests**
  - Cover bomb activation, cooldown, pickup expiration, and wave propagation with automated tests.
  - Verify interactions with transitions, game over, and player invulnerability states.

## Epic F – High-Score Persistence & Progression
- ✅ **Story F1 – Persistence foundation**
  - Define a versioned save schema (JSON or similar) for scores, run stats, and settings.
  - Implement load/update/save helpers with safe defaults when files are missing or corrupt.
  - Document schema versions and upgrade helpers so future migrations remain straightforward.
- ✅ **Story F2 – Leaderboards & HUD surfacing**
  - Track a local leaderboard (top N scores) with metadata such as level reached and bomb usage.
  - Surface personal bests in the HUD or between-level banner (“New high score!”).
- ✅ **Story F3 – Meta progression hooks**
  - Record cumulative milestones (e.g., total asteroids destroyed, total bombs used, levels cleared).
  - Unlock cosmetic or title flags that future features can read (e.g., alternate ship skins).
- ✅ **Story F4 – Settings persistence**
  - Save user preferences: audio levels, control bindings, accessibility toggles.
  - Ensure changes persist across sessions and integrate with future menu work.
- ✅ **Story F5 – Migration & reliability tests**
  - Add tests for schema upgrades and corrupted file recovery.
  - Document backup/fallback behavior for the persistence layer.

- ✅ **Story G1 – Audio manager baseline**
  - Add an `audio_manager` module to centralize sound effect playback with dummy-driver fallback.
  - Hook core events (shots, asteroid hits) to play placeholder SFX.
- ✅ **Story G2 – Dynamic music layers**
  - Implement layered background music that scales with encounter intensity.
  - Adopt a naming convention for music assets (e.g., `bgm_phase01.ogg`, `bgm_boss02.ogg`) and support seamless fade-out/in between randomly selected tracks per level.
- ✅ **Story G3 – SFX library build-out**
  - Integrate unique sounds for shots, asteroid splits by size, bomb detonations, pickups, and UI transitions.
  - Randomize pitch/volume subtly for freshness.
- ✅ **Story G4 – Visual FX framework**
  - Introduce a reusable FX manager with particle helpers, screen shake utilities, and overlay flashes sized for future power-ups.
  - Apply effects to bombs (including outward fragment nudges), asteroid destruction, and level transitions.
- ✅ **Story G5 – Audio & FX settings**
  - Expose volume sliders (music/SFX) and screen-shake toggles, storing prefs via the persistence layer.
  - Provide temporary key shortcuts for mute/unmute before menus arrive.
- ✅ **Story G6 – Accessibility cues**
  - Offer visual substitutes when audio is muted (HUD pulses, icon flashes) and document extension points.
- ✅ **Story G7 – Reliability tests**
  - Add tests ensuring the audio manager handles missing devices and effect lifecycles clean up correctly.
  - Verify event triggers hit the expected audio/FX hooks.

## Epic H – Menus & Settings Experience
- **Story H1 – State manager & title screen**
  - ✅ Introduce a lightweight state machine (title, gameplay, pause, settings).
  - ⬜ Build an animated title screen with a “Press Start” prompt and high-score preview.
- **Story H2 – Pause overlay**
  - ✅ Ensure gameplay freezes cleanly and resumes without side effects.
  - ⬜ Add a translucent pause menu showing resume/restart/quit options plus current run stats.
- ✅ **Story H3 – Run summary screen**
  - Present a post-run breakdown (score, best combo, time survived, bombs detonated, pickups collected) before returning to the title screen.
  - Trigger persistence hooks from Epic F to record leaderboard entries and milestones.
- **Story H4 – Settings UI scaffold**
  - Create reusable UI primitives (buttons, sliders, toggles) with keyboard focus handling.
  - Layout an initial settings menu structure with navigation rails.
- **Story H5 – Audio & display settings**
  - Hook sliders to music/SFX volume and screen-shake intensity; persist changes via the save layer.
  - Provide instant feedback as users adjust values.
- **Story H5a – Display mode options**
  - Allow switching between windowed, windowed-borderless, and fullscreen.
  - Expose common resolution presets (1280×720 baseline, 1600×900, 1920×1080) and persist selection.
- **Story H6 – Control bindings**
  - Allow keyboard remapping with conflict detection and “reset to default” support (gamepad deferred to a future story).
  - Update input handling to respect custom bindings.
- **Story H7 – Accessibility options**
  - Offer colorblind-friendly palettes, reduced FX toggles, and other comfort adjustments.
  - Surface explanatory tooltips or descriptions for each option.
- **Story H8 – Tutorial & info panels**
  - Add a “How to Play” overlay reachable from title/pause menus (controls, bomb mechanics, pickups).
  - Highlight new mechanics (bomb pickups, slow-mo) for onboarding.
- **Story H9 – Navigation tests & polish**
  - Write tests covering state transitions and settings persistence.
  - Verify focus wrap-around, back navigation consistency, and menu/audio interaction edge cases.
