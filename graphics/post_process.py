"""
Post-Processing Filter System for Keep Driving.

Grain approach (per user feedback):
  - Pixels are DARK GREY (0-50), NOT white, with very low alpha (8-15).
  - Pre-generate 4 variants; rotate every 5 frames so it "breathes".
  - Use regular blit (no BLEND_RGBA_ADD which brightens everything).
  - Grain is restricted to the GAME ZONE only (y=120-261).

Filters (F10 to cycle):
  0 - OFF
  1 - CRT         (scanlines + vignette)
  2 - FILM GRAIN  (subtle dark noise, 35mm look)
  3 - SEPIA       (warm amber tint + light grain)
  4 - VHS         (blue-grey tint + scanlines + occasional glitch)
  5 - COLD NIGHT  (cool cyan/blue grade)
"""
import pygame
import random

FILTER_NAMES = ["OFF", "CRT", "FILM GRAIN", "SEPIA", "VHS", "COLD NIGHT"]
_NUM_FILTERS  = len(FILTER_NAMES)
_NUM_VARIANTS = 4   # pre-baked grain variants

# Gameplay zone (top UI ends at 120, HUD starts at 261)
GAME_TOP    = 120
GAME_BOTTOM = 261
GAME_H      = GAME_BOTTOM - GAME_TOP   # 141


class PostProcessor:
    def __init__(self, width: int, height: int):
        self.w       = width
        self.h       = height
        self.current = 0
        self._frame  = 0

        # Pre-bake static layers (calculated once)
        self._scanlines = self._make_scanlines(alpha=28)
        self._vignette  = self._make_vignette()
        self._sepia     = self._make_tint((100, 50, 0, 20))   # Cinematographic warm tone
        self._cold      = self._make_tint((8,  28, 75, 22))   # cool blue-cyan

        # Pre-bake grain variants (dark grey noise, very low alpha)
        self._grains = [self._make_grain_variant() for _ in range(_NUM_VARIANTS)]

    # ── Public ───────────────────────────────────────────────────────────────
    def cycle(self):
        self.current = (self.current + 1) % _NUM_FILTERS

    def name(self) -> str:
        return FILTER_NAMES[self.current]

    def apply(self, surface: pygame.Surface):
        self._frame += 1
        idx = self.current
        if   idx == 0: return
        elif idx == 1: self._apply_crt(surface)
        elif idx == 2: # FILM GRAIN
            self._apply_grain(surface)
            surface.blit(self._vignette, (0, 0))
        elif idx == 3: # SEPIA
            surface.blit(self._sepia, (0, 0))
            self._apply_grain(surface)
            surface.blit(self._vignette, (0, 0))
        elif idx == 4: self._apply_vhs(surface)
        elif idx == 5:
            surface.blit(self._cold, (0, 0))

    # ── Builders (called once on init) ────────────────────────────────────────
    def _make_scanlines(self, alpha: int = 28) -> pygame.Surface:
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for y in range(0, self.h, 2):
            pygame.draw.line(s, (0, 0, 0, alpha), (0, y), (self.w, y))
        return s

    def _make_vignette(self) -> pygame.Surface:
        """Dark concentric rects — like the reference code."""
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        # Only darken the game zone edges to avoid touching UI
        gw, gh = self.w, GAME_H
        for i in range(0, 200, 6):
            a = max(0, 200 - i)
            r = i // 2
            pygame.draw.rect(
                s, (0, 0, 0, a),
                (r, GAME_TOP + r, gw - i, gh - i),
                8
            )
        return s

    def _make_tint(self, rgba: tuple) -> pygame.Surface:
        """Full-canvas tint at very low alpha."""
        s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        s.fill(rgba)
        return s

    def _make_grain_variant(self) -> pygame.Surface:
        """
        Pre-baked grain: dark grey pixels (val 0-50), alpha 15.
        Increased density for a celluloid feel.
        """
        s = pygame.Surface((self.w, GAME_H), pygame.SRCALPHA)
        num_pts = (self.w * GAME_H) // 30   # Higher density per user
        for _ in range(num_pts):
            x   = random.randint(0, self.w - 1)
            y   = random.randint(0, GAME_H - 1)
            val = random.randint(0, 50)      # DARK GREY
            alp = 15                         # User recommended alpha
            s.set_at((x, y), (val, val, val, alp))
        return s

    # ── Appliers ─────────────────────────────────────────────────────────────
    def _active_grain(self) -> pygame.Surface:
        """Rotate through grain variants every 5 frames."""
        idx = (self._frame // 5) % _NUM_VARIANTS
        return self._grains[idx]

    def _apply_grain(self, surface: pygame.Surface):
        """Blit grain only over game zone (standard blit, no ADD)."""
        surface.blit(self._active_grain(), (0, GAME_TOP))

    def _apply_crt(self, surface: pygame.Surface):
        surface.blit(self._scanlines, (0, 0))
        surface.blit(self._vignette,  (0, 0))

    def _apply_vhs(self, surface: pygame.Surface):
        # Faint blue-grey tint (full canvas)
        vhs_tint = self._make_tint((6, 10, 42, 30))
        surface.blit(vhs_tint, (0, 0))

        # Wider scanlines in game zone only
        scan = pygame.Surface((self.w, GAME_H), pygame.SRCALPHA)
        for y in range(0, GAME_H, 3):
            pygame.draw.line(scan, (0, 0, 18, 35), (0, y), (self.w, y))
        surface.blit(scan, (0, GAME_TOP))

        # Grain (dark, barely visible)
        self._apply_grain(surface)

        # Glitch: 1 line per 6 frames, small shift
        if self._frame % 6 == 0:
            gy    = random.randint(GAME_TOP, GAME_BOTTOM - 2)
            shift = random.choice([-1, 1, -2, 2])
            row   = surface.subsurface((0, gy, self.w, 1)).copy()
            surface.blit(row, (shift, gy))
