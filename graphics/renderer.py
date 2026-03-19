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
        self.avatar_cache = {} # Name -> scaled Surface

    def set_biome(self, biome):
        self.parallax.set_biome(biome)

    def switch_view(self, view_name):
        self.current_view = view_name

    def update(self, dt, speed, weather_state="sunny"):
        self.parallax.update(dt, speed, weather_state)

    def render(self, surface, car, car_manager, weather_state="sunny",
               weather_sys=None, time_of_day=0.5, offset=(0, 0), traffic=None, upcoming_encounter=None):
        ox, oy = offset
        day_factor = max(0.0, math.sin(time_of_day * math.pi))
        is_night   = day_factor < 0.6
        road_y_pos = ROAD_Y + oy

        # ── 1. Background / Parallax (no night overlay inside parallax) ──────
        self.parallax.render(surface, weather_state, time_of_day)

        # ── 1.2 Top Interface Placeholder (Zone 0-120) ───────────────────────
        # pygame.draw.rect(surface, (10, 12, 15), (0, 0, W, 120))  # This was a placeholder, now we have HUD/Upper
        
        # ── 1.4 Road Objects (Encounter Pre-visualization) ──────────────────
        if upcoming_encounter:
            dist = upcoming_encounter['dist']
            threshold = 0.4 # Appear at 400m
            if dist < threshold:
                # Progress from 0.0 (far right) to 1.0 (approaching car)
                # car is at rx + rw*0.25 (approx 110 + 370*0.25 = 202)
                # W = 640. So we want to go from 640 to 200.
                progress = (threshold - dist) / threshold # 0.0 to 1.0
                screen_x = W - progress * (W - 200)
                scale = 0.2 + progress * 1.0 # 0.2 to 1.2
                
                if 'hitchhiker' in upcoming_encounter['key']:
                    self._draw_road_object(surface, "agent", screen_x, road_y_pos, scale)
                else:
                    self._draw_road_object(surface, "marker", screen_x, road_y_pos, scale)

        # ── 1.5 Traffic ───────────────────────────────────────────────────────
        if traffic:
            traffic.render(surface)

        # ── 2. Player Car ─────────────────────────────────────────────────────
        cx = W // 2 - 56 + ox
        cy = road_y_pos - 54
        bounce = int(math.sin(pygame.time.get_ticks() * 0.015) * 1.5) if car.speed > 0 else 0
        car_y = cy + bounce

        if hasattr(self.parallax, "car_cache"):
            surface.blit(self.parallax.car_cache, (cx, car_y))
        else:
            pygame.draw.rect(surface, (210, 195, 160), (cx, car_y, 112, 50))
            pygame.draw.circle(surface, (20, 20, 25), (cx + 25, car_y + 50), 10)
            pygame.draw.circle(surface, (20, 20, 25), (cx + 87, car_y + 50), 10)

        # ── 3. Night Darkness Layer with Light Holes ──────────────────────────
        if is_night:
            darkness_alpha = int(190 * (1.0 - day_factor / 0.6))
            darkness_alpha = min(190, max(0, darkness_alpha))
            self._dark_surf.fill((5, 8, 25, darkness_alpha))

            hx, hy = cx + 112, car_y + 44
            self._light_surf.fill((0, 0, 0, 0))
            cone_len, cone_half = 180, 22
            for step in range(8, 0, -1):
                ratio = step / 8.0
                l, s = int(cone_len * ratio), int(cone_half * ratio * 1.4)
                a = int(220 * (1.0 - ratio))
                pygame.draw.polygon(self._light_surf, (255, 255, 200, a), [(hx, hy), (hx+l, hy-s), (hx+l, hy+s)])
            for r in range(18, 0, -2):
                pygame.draw.circle(self._light_surf, (255, 255, 180, int(160 * (1.0 - r/18.0))), (hx, hy), r)

            # Taillight
            rx, ry = cx + 2, car_y + 44
            for r in range(16, 0, -2):
                pygame.draw.circle(self._dark_surf, (255, 40, 40, int(160 * (1.0 - r/16.0))), (rx, ry), r)

            self._dark_surf.blit(self._light_surf, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            surface.blit(self._dark_surf, (0, 0))

        # ── 4. Weather Overlays ───────────────────────────────────────────────
        if weather_sys:
            weather_sys.render_over(surface)

    def _render_interior(self, surface, car_manager):
        surface.fill((15, 12, 10))

    def _render_topdown(self, surface):
        surface.fill((30, 40, 30))
    def _draw_road_object(self, surface, type_key, x, y, scale):
        """Draw an object on the roadside."""
        base_size = 48
        sz = int(base_size * scale)
        rect = pygame.Rect(x, y - sz, sz, sz)
        
        if type_key == "marker":
            # Just a teal/blue square for locations
            pygame.draw.rect(surface, (100, 200, 255), rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)
        else:
            # Draw a silhouette or simple person shape
            px = x + sz // 2
            pygame.draw.circle(surface, (240, 240, 240), (px, y - sz + sz // 4), sz // 4)
            pygame.draw.rect(surface, (240, 240, 240), (px - sz // 4, y - sz // 2, sz // 2, sz // 2))

    def render_dialogue(self, surface, dialogue_line):
        if not dialogue_line: return
        # Simple dialogue bubble at bottom center
        font = pygame.font.Font(None, 24)
        txt = font.render(f"{dialogue_line.speaker}: {dialogue_line.text}", True, (255, 255, 255))
        
        bw = txt.get_width() + 20
        bh = txt.get_height() + 10
        bx = (W - bw) // 2
        by = H - 150
        
        pygame.draw.rect(surface, (20, 20, 30), (bx, by, bw, bh))
        pygame.draw.rect(surface, (100, 100, 120), (bx, by, bw, bh), 2)
        surface.blit(txt, (bx + 10, by + 5))
