# Changelog

All notable changes to the **Keep Driving** project will be documented in this file.

## [Unreleased] - 2026-03-21

### Added
- **Dynamic Settlement Interior System:**
  - Double-clicking exterior buildings (like gas stations or motels) now perfectly renders their detailed interior.
  - The interior rendering bounds dynamically fit right-aligned at a maximum of `55%` of screen width, completely avoiding clipping with the upper inventory HUD and lower dashboard.
  - A responsive "EXIT" boundary detects clicks logically scaled to the upper right edge of any internal image.
- **Render Cleanups & Engine Visibility Toggles:**
  - Added a `render_car` toggle variable to the `GameRenderer` which natively hides the protagonist's van when docked at a settlement.
  - Prevented traffic objects from spawning or overlapping in the background while the state is strictly `GameState.SETTLEMENT`, creating a much cleaner cinematic aesthetic.

### Fixed
- **Parallax Background Gaps & Crashes:**
  - Shifted all base procedural road layers downwards implicitly by `+10 pixels` to effectively eliminate a recurring blue sky-bar anomaly leaking below the road texture.
  - Resolved an `IndexError` crash occurring during procedural background hill rendering by ensuring the `highway` biome inside `BIOME_PALETTES` contains exactly 3 colors for layer generation.
- **Resolution Import Errors (Unbound Locals):**
  - Cleaned up rogue duplicate imports of native resolution variables inside `_handle_input`, resolving `UnboundLocalErrors` associated with validating global `W` and `H` coordinates.
