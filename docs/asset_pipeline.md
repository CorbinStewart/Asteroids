# Asset Pipeline – Neon Overhaul (N8.1)

This guide defines how we organize and export art/audio assets for the neon visual direction.

## Directory Layout

```
assets/
├─ fonts/                 # Typeface files used in-game
├─ music/                 # Looping BGM tracks (ogg)
├─ sounds/                # Short SFX (wav)
├─ sprites/               # Gameplay sprites (player, asteroids, pickups)
├─ ui/                    # HUD/menu specific artwork
├─ particles/             # Particle sheets, glow bursts
└─ overlays/              # Screen-wide effects, gradients, grids
```

Keep filenames lowercase with underscores: `player_ship_core.png`, `hud_panel_frame.png`, `pickup_bomb_ring.png`.

## Export Settings

- **Format:** Use PNG with alpha for sprites/UI/overlays. Keep glow overscan (8–12 px) to avoid clipping.
- **Resolution:** Author at 2× gameplay scale. Our baseline render (1280×720) downscales cleanly; 1080p support will rely on the extra resolution.
- **Color space:** sRGB, 8-bit. Avoid premultiplied alpha (Pygame expects straight alpha).
- **Naming suffixes:**
  - `_core` for the wireframe stroke.
  - `_glow` for additive bloom variants.
  - `_animNN` for frame sequences (`pickup_bomb_anim00.png`, etc.).

## Audio Assets

- **Music:** OGG Vorbis, 44.1 kHz stereo. Use `bgm_phaseXX.ogg` (`phase01`, `phase02`, …).
- **SFX:** WAV (16-bit), 44.1 kHz mono. Use descriptive prefixes: `player_shot.wav`, `ui_nav_move.wav`.

## Version Control

- Add `.gitkeep` to empty folders so the layout persists before art lands.
- Large source files (PSD, Aseprite) stay out of the repository—store them externally.

## Workflow Notes

1. Export base stroke to `assets/sprites/` or `assets/ui/`.
2. If a dedicated glow mask is required, export `_glow` variant to the same directory; `GlowSprite` can combine both.
3. Update `assets.py` with helpers or path constants when new assets are introduced.
4. Document additions in `docs/style_guide.md` if they affect palette/usage.

Following this structure keeps upcoming HUD/menu work aligned with the neon style and avoids rework when assets scale to higher resolutions.
