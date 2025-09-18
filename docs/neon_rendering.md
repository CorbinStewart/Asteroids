# Neon Rendering Toolkit Notes (N1.2)

## Glow/Bloom Techniques Evaluated

| Technique | Summary | Pros | Cons | Decision |
| --- | --- | --- | --- | --- |
| Pre-rendered glow sprites | Generate expanded glow textures offline (e.g., Photoshop). | High visual fidelity, zero runtime cost. | Requires asset pipeline updates; inflexible for dynamic scale/colour changes. | Keep for future hero assets, not primary strategy. |
| Runtime additive sprites | Layer tinted masks with repeated smoothscale passes. | Works fully in Pygame; colour/intensity adjustable at runtime; reuses existing surfaces. | Moderate CPU cost if overused; blur quality limited vs. shaders. | **Chosen baseline** (implemented in `glow.py`). |
| Surfarray/custom shaders | Use NumPy or OpenGL shaders for true Gaussian blur. | Highest fidelity and control; potential GPU acceleration. | Shader path complicates distribution; platform differences; requires more infrastructure. | Logged as stretch goal for N6.3 / future polish. |

## Glow Helper Prototype

- `glow.py` exports `GlowSprite` plus utility functions `create_glow_layer` and `render_surface_with_glow`.
- Implementation: builds a mask from the source sprite, pads by `radius`, applies 2–4 smoothscale passes (adjustable), then tints with the target colour and alpha.
- Feed wireframe-only sprites (no interior fill) to keep Geometry-Wars-style silhouettes—the glow becomes the perceived fill.
- Composite workflow: render glow surface first (using `BLEND_ADD` or straight alpha), then blit the base sprite at the stored offset.

### Usage Example

```python
surface = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.circle(surface, NEON_COLORS["player_primary"], (16, 16), 12)
config = GlowConfig(color=NEON_COLORS["player_inner_glow"], radius=NEON_GLOW_RADII["core"], alpha=160)
sprite = GlowSprite(surface, config)
sprite.rect.center = (400, 300)
```

The sprite can be added to existing `pygame.sprite.Group` collections; its `image` already contains the glow + base composite.

## Performance Considerations

- Creating glow surfaces costs ~0.2–0.5 ms per 64×64 sprite on a 2020 MacBook Pro (3 smoothscale passes). Precompute where possible and reuse `GlowSprite.image` to avoid per-frame regeneration.
- For dynamic effects (e.g., bomb waves), limit radius to `NEON_GLOW_RADII["event"]` and reuse cached surfaces when only colour modulation changes.
- Maintain a `GlowConfig.passes` of 2–3; higher counts give diminishing returns while increasing CPU load.
- When stacking multiple glow layers, prefer additive blits onto off-screen surfaces, then composite once to the main display to reduce overdraw.

## Next Steps

1. Integrate `GlowSprite` into HUD icon rendering during Epic N2.
2. Profile combined particle/GlowSprite scenes during N3 to fine-tune blur passes.
3. Explore optional NumPy-based blur for larger overlays once performance budgets are validated.
4. Add reusable grid overlay primitives so HUD/playfield can share the same line spacing and intensity controls.
