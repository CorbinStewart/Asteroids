# Neon Sci-Fi Visual Direction

This plan captures the changes needed to transition Asteroids from the current vector minimalism to a cohesive neon sci-fi presentation. Each epic assumes prior gameplay systems remain intact; work focuses on art direction, presentation, and audio/FX alignment.

## Epic N1 – Visual Style Foundations
- **Story N1.1 – Style guide & palette**
  - Define the core color palette (player cyan, hazard red/orange, UI violet/blue) plus neutral tones.
  - Document line weights, glow radii, and typography usage (Orbitron hierarchy, alt font options).
  - Produce reference mockups for HUD panel, playfield scene, and pickup icon.
- **Story N1.2 – Rendering toolkit audit**
  - Evaluate Pygame techniques for glow/bloom (additive sprites, layered surfaces, shaders via surfarray).
  - Prototype a reusable `GlowSprite` helper that composites base geometry + glow pass.
  - Ensure performance budget on target machines with multiple glow entities.

## Epic N2 – HUD & UI Rework
- **Story N2.1 – HUD panel redesign**
  - Replace gradient rectangles with neon panels (soft outer glows, subtle grid lines, animated star specks).
  - Update iconography (lives triangles, bomb squares, score digits) with neon outlines and inner glow.
- **Story N2.2 – Typography & effects**
  - Add drop shadows / glow behind HUD text; ensure readability with dynamic backgrounds.
  - Create animated transitions (score increments pulse, level banner slides in/out).
- **Story N2.3 – In-game overlays**
  - Update pause, transition, and game over overlays to match the new HUD style (transparent panels, animated scanlines).

## Epic N3 – Playfield Atmosphere
- **Story N3.1 – Starfield & parallax**
  - Introduce layered starfields (slow parallax, twinkling) using additive sprites.
  - Allow toggles/intensity settings for accessibility.
- **Story N3.2 – Ambient nebula / horizon**
  - Add faint nebula gradients or vignette around the playfield edges to anchor the scene.
  - Ensure contrast remains high for gameplay readability.
- **Story N3.3 – Dynamic lighting cues**
  - Implement screen-wide tint pulses for events (bomb detonation, level change).
  - Tie pulses to game clock so they don’t interfere with slow-mo.

## Epic N4 – Game Object Visuals
- **Story N4.1 – Player ship glow pass**
  - Add inner glow, thruster trails, and subtle particle exhaust tied to velocity.
  - Implement a shader-like shimmer during invulnerability.
- **Story N4.2 – Asteroid treatment**
  - Replace plain circles with faceted neon outlines or gradient fills (larger asteroids have more complex silhouettes).
  - Add hit flashes and destruction particles that match the palette.
- **Story N4.3 – Projectile & bomb FX**
  - Shots become neon bolts with motion blur; bombs emit expanding rings with additive blending.
  - Integrate with existing bomb wave time scaling.

## Epic N5 – Pickup & UI Feedback Enhancements
- **Story N5.1 – Pickup animation suite**
  - Add spin, glow bloom, and trailing particles to pickups (bomb, future power-ups).
  - Implement a radar ping or HUD arrow when pickups spawn off-screen.
- **Story N5.2 – HUD-playfield synchronization**
  - When pickups collected, animate icon travel to HUD (straight line or curved arc).
  - Ensure animations respect slow-mo and pause states.

## Epic N6 – Audio & FX Alignment
- **Story N6.1 – Soundscape update**
  - Expand SFX library with synth-heavy cues matching the neon aesthetic (bomb detonation, pickup, UI clicks).
  - Add subtle reverb/echo to bombs/shots.
- **Story N6.2 – Music layering**
  - Introduce synthwave-inspired tracks with intensity layers; crossfade on level change.
  - Sync tempo or filter sweeps to slow-mo events for immersion.
- **Story N6.3 – Audio-reactive visuals (optional stretch)**
  - Explore waveforms or visualizers in HUD panels reacting to music intensity.

## Epic N7 – Menus & Narrative Framing
- **Story N7.1 – Title screen overhaul**
  - Design animated neon title, rotating asteroid backdrops, and shimmering menu text.
  - Add ambient motion (floating particles, animated grid).
- **Story N7.2 – Settings & tutorial presentation**
  - Apply neon styling to sliders/toggles; include hover glows and focus transitions.
  - Update tutorial overlays with neon callouts and animated diagrams.
- **Story N7.3 – Narrative flavor (optional)**
  - Introduce short lore blurbs or mission briefs leveraging the new aesthetic (e.g., “Neon Sector 9 under siege”).

## Epic N8 – Implementation Logistics
- **Story N8.1 – Asset pipeline**
  - Organize art & SFX assets (textures, glow masks, particle sprites) under `assets/` by category.
  - Document export settings (PNG with transparent glow alpha, recommended sizes).
- **Story N8.2 – Performance & scalability**
  - Profile new effects; add options for low/high fidelity modes.
  - Ensure fallback rendering path (no glow) for low-end machines.
- **Story N8.3 – QA checklist**
  - Compile visual regression checklist (washed-out colors, readability issues, epilepsy-safe flashing).
  - Include before/after screenshot comparisons in docs.

---

This plan intentionally keeps existing gameplay epics intact while providing a roadmap to gradually shift the presentation. Each epic can be scheduled alongside feature work so the transition feels cohesive rather than piecemeal.
