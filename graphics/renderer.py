"""High-Fidelity Renderer with proper Day/Night lighting.

Night system uses a 'darkness surface' that is applied OVER the scene,
then 'punched through' with soft light polygons for headlights.
This preserves all background imagery while adding atmospheric depth.
"""
import pygame
import math
from core.config import BASE_RESOLUTION, COLORS, ROAD_Y
from graphics.parallax import ParallaxBackground

W, H = BASE_RESOLUTION


class GameRenderer:
    def __init__(self):
        self.parallax = ParallaxBackground()
        self.current_view = 'side'
        # Persistent darkness surface — reused each frame for performance
        self._dark_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        # Persistent light cone surface — drawn INTO darkness to punch holes
        self._light_surf = pygame.Surface((W, H), pygame.SRCALPHA)

    def set_biome(self, biome):
        self.parallax.set_biome(biome)

    def switch_view(self, view_name):
        self.current_view = view_name

    def update(self, dt, speed, weather_state="sunny"):
        self.parallax.update(dt, speed / 100.0, weather_state)

    def render(self, surface, car, car_manager, weather_state="sunny",
               weather_sys=None, time_of_day=0.5, offset=(0, 0), traffic=None):
        ox, oy = offset
        day_factor = max(0.0, math.sin(time_of_day * math.pi))
        is_night   = day_factor < 0.6

        # ── 1. Background / Parallax (no night overlay inside parallax) ──────
        self.parallax.render(surface, weather_state, time_of_day)

        # ── 1.2 Top Interface Placeholder (Zone 0-120) ───────────────────────
        pygame.draw.rect(surface, (10, 12, 15), (0, 0, W, 120))
        font = pygame.font.Font(None, 24)
        lbl = font.render("TOP UI SPACE: 640x120", True, (60, 70, 85))
        surface.blit(lbl, (W // 2 - lbl.get_width() // 2, 50))
        pygame.draw.line(surface, (45, 50, 60), (0, 120), (W, 120), 2)

        # ── 1.5 Traffic ───────────────────────────────────────────────────────
        if traffic:
            traffic.render(surface)

        # ── 2. Player Car ─────────────────────────────────────────────────────
        cx = W // 2 - 56 + ox
        cy = ROAD_Y - 54 + oy
        bounce = int(math.sin(pygame.time.get_ticks() * 0.015) * 1.5) if car.speed > 0 else 0
        car_y = cy + bounce

        if hasattr(self.parallax, "car_cache"):
            surface.blit(self.parallax.car_cache, (cx, car_y))
        else:
            # Procedural fallback
            pygame.draw.rect(surface, (210, 195, 160), (cx, car_y, 112, 50))
            pygame.draw.circle(surface, (20, 20, 25), (cx + 25, car_y + 50), 10)
            pygame.draw.circle(surface, (20, 20, 25), (cx + 87, car_y + 50), 10)

        # ── 3. Night Darkness Layer with Light Holes ──────────────────────────
        if is_night:
            # How dark: 0 at dusk/dawn (day_factor≈0.6), max at midnight
            darkness_alpha = int(190 * (1.0 - day_factor / 0.6))
            darkness_alpha = min(190, max(0, darkness_alpha))

            # Start with transparent darkness canvas
            self._dark_surf.fill((5, 8, 25, darkness_alpha))

            # --- Punch front headlight cone into darkness ---
            hx = cx + 112          # front of van
            hy = car_y + 44        # lower: mid-body of van, not roof
            cone_len  = 180
            cone_half = 22

            self._light_surf.fill((0, 0, 0, 0))
            for step in range(8, 0, -1):
                ratio  = step / 8.0
                l      = int(cone_len * ratio)
                spread = int(cone_half * ratio * 1.4)
                alpha  = int(220 * (1.0 - ratio))
                cone_pts = [
                    (hx, hy),
                    (hx + l, hy - spread),
                    (hx + l, hy + spread),
                ]
                pygame.draw.polygon(
                    self._light_surf,
                    (255, 255, 200, alpha),
                    cone_pts
                )

            # Soft headlight source glow (warm white)
            for r in range(18, 0, -2):
                a = int(160 * (1.0 - r / 18.0))
                pygame.draw.circle(self._light_surf, (255, 255, 180, a), (hx, hy), r)

            # --- Rear red taillight (draw DIRECTLY on surface, not on light_surf)
            # so BLEND_RGBA_SUB doesn't cancel it out
            rx = cx + 2
            ry = car_y + 44  # same vertical level as front light
            for r in range(16, 0, -2):
                a = int(160 * (1.0 - r / 16.0))
                pygame.draw.circle(self._dark_surf, (255, 40, 40, a), (rx, ry), r)

            # Blend front light into darkness (punches hole)
            self._dark_surf.blit(self._light_surf, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

            # Apply tinted darkness over the whole scene
            surface.blit(self._dark_surf, (0, 0))

        # ── 4. Weather Overlays ───────────────────────────────────────────────
        if weather_sys:
            weather_sys.render_over(surface)

    def _render_interior(self, surface, car_manager):
        surface.fill((15, 12, 10))

    def _render_topdown(self, surface):
        surface.fill((30, 40, 30))
