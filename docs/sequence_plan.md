# Execution Sequence: Menu & Neon Overhaul

This document captures the agreed-upon order for wrapping Epic H (Menus & Settings) while rolling out the Neon visual direction (Epics N1–N8). Each phase builds prerequisites for the next to avoid rework.

## Phase 0 – Core State Plumbing (H)
- ✅ Deliver the lightweight state machine portion of **H1** so gameplay can swap between title, gameplay, pause, and settings shells.
- ⬜ Defer the styled title screen from H1 until the neon art direction is locked.

## Phase 1 – Visual Foundations (N)
- ✅ Ship **N1.1** and **N1.2** to document palette, typography, glow specs, and a reusable glow toolkit.
  - ✅ Capture palette / line-weight / typography guidance in `docs/style_guide.md` (**N1.1**).
  - ✅ Produce reference mockups for HUD, playfield, pickup (**N1.1**).
  - ✅ Audit rendering toolkit and prototype glow helper (**N1.2**).
- ✅ Complete **N8.1** to organize asset exports/naming before new HUD and menu art lands.

## Phase 2 – UI Component Kit (N)
- Execute **N2.1** and **N2.2** to rebuild HUD panels, icons, and text treatments in the neon style.
- Apply **N2.3** to restyle in-game overlays, validating modal flows with the new toolkit.

## Phase 3 – World Atmosphere & Feedback (N)
- Add backdrop and lighting work from **N3.1–N3.3** to align playfield ambience with the UI look.
- Refresh ships, asteroids, projectiles, and pickup feedback via **N4.1–N4.3** and **N5.1–N5.2** so game objects match the neon aesthetic.

## Phase 4 – Audio Alignment (N)
- Update audio cues and music layers with **N6.1** and **N6.2** so upcoming menu sliders preview the synthwave soundscape.
- Defer optional audio-reactive visuals (**N6.3**) until after core menus ship.

## Phase 5 – Neon Menu Presentation (N)
- Produce title/menu/tutor mockups and assets through **N7.1** and **N7.2**, giving the implementation team concrete neon UI designs.
- Fold narrative flavor from **N7.3** alongside tutorial work if desired.

## Phase 6 – Menu & Settings Functionality (H)
- Finish **H2**, **H4**, and **H5** (pause overlay, settings scaffold, audio/display controls) reusing the neon widgets.
- Add **H5a** for display mode/resolution management ahead of control/accessibility settings.
- Follow with **H6**, **H7**, and **H8** to ship bindings, accessibility options, and tutorial overlays on top of the styled components.
- Conclude with **H9** navigation/persistence tests to lock UX behavior.

## Phase 7 – Performance & QA (N)
- Execute **N8.2** and **N8.3** to profile the new effects, add fidelity toggles, and capture before/after references.

This sequence ensures the neon art direction arrives before menu-heavy feature work, keeping implementation aligned with the final visual identity.
