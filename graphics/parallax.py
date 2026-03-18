"""
Ultra-High Fidelity Procedural Parallax with Dynamic Time-of-Day Sky.
Creates a deep, atmospheric road environment using advanced drawing techniques.
"""
import pygame
import random
import math
import os
from core.config import BASE_RESOLUTION, ROAD_Y, SPRITES_DIR

W, H = BASE_RESOLUTION

# Biome-specific color palettes
BIOME_PALETTES = {
    "desert": {
        "sky_top": (10, 40, 80), "sky_bottom": (200, 160, 120),
        "hills": [(140, 100, 60), (120, 80, 40), (100, 60, 30)],
        "field": (180, 160, 120)
    },
    "mountain": {
        "sky_top": (20, 30, 60), "sky_bottom": (160, 180, 210),
        "hills": [(100, 120, 140), (80, 100, 120), (60, 80, 100)],
        "field": (100, 110, 120)
    },
    "forest": {
        "sky_top": (10, 30, 50), "sky_bottom": (120, 160, 130),
        "hills": [(40, 70, 40), (30, 60, 30), (20, 50, 20)],
        "field": (50, 90, 40)
    },
    "coastal": {
        "sky_top": (80, 140, 220), "sky_bottom": (220, 240, 255),
        "hills": [(100, 180, 220), (80, 160, 200), (60, 140, 180)],
        "field": (200, 190, 150)
    },
    "city": {
        "sky_top": (5, 5, 15), "sky_bottom": (20, 20, 40),
        "hills": [(10, 10, 20)],
        "field": (30, 30, 35)
    }
}

class ParallaxBackground:
    def __init__(self):
        self.biome = "desert"
        self.scroll_x = 0.0
        
        # Pre-cache surfaces
        self.sky_surf = pygame.Surface((W, ROAD_Y))
        self.field_surf = pygame.Surface((W * 2, 110), pygame.SRCALPHA)
        self.car_cache = pygame.Surface((180, 80), pygame.SRCALPHA)
        self.cloud_surfs = []
        
        self._generate_detailed_clouds()
        self._generate_detailed_field()
        self._generate_detailed_car()
        
        self.stars = [(random.randint(0, W), random.randint(0, ROAD_Y), random.uniform(0.5, 1.5)) 
                      for _ in range(120)]
        
        # External assets
        self.ext_segments = []
        self._load_external_assets()

    def _load_external_assets(self):
        """Loads parallax layer strips from sprites/road/.

        Only desert_road_*.png are proper 75px parallax strips.
        Stack alignment:
          desert_road_3 (sky,       75px) → y=15
          desert_road_2 (mountains, 75px) → y=90
          desert_road_1 (road,      75px) → y=165
        """
        self.layers = []
        self.layer_speeds = [1.0, 0.25, 0.05]   # [road, mountains, sky]
        self.layer_ys = [111, 115, 115]

        road_dir = os.path.join(SPRITES_DIR, "road")
        for i in range(1, 4):
            fn = f"{self.biome}_road_{i}.png"
            path = os.path.join(road_dir, fn)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    self.layers.append(img)
                    print(f"✓ Layer {i}: {fn} ({img.get_width()}x{img.get_height()})")
                except Exception as e:
                    print(f"❌ Error loading {fn}: {e}")
            else:
                print(f"⚠️ Not found: {path}")

        if not self.layers:
            print(f"⚠️ NO LAYERS LOADED for biome '{self.biome}'")



        
    def _get_dynamic_sky_colors(self, time_of_day):
        """Calculates sky colors based on time (0.0=mid, 0.5=noon)."""
        palette = BIOME_PALETTES.get(self.biome, BIOME_PALETTES["desert"])
        
        # Day/Night factor
        # 0.5 is noon (full bright), 0.0/1.0 is midnight (dark)
        day_factor = math.sin(time_of_day * math.pi)
        day_factor = max(0.05, day_factor) # Minimum ambient
        
        # Sunset/Sunrise factor
        # Gold/Orange hours around 0.25 and 0.75
        sunset_factor = max(0, 1.0 - abs(day_factor - 0.4) * 5)
        
        top = list(palette["sky_top"])
        bot = list(palette["sky_bottom"])
        
        # Tint based on factor
        for i in range(3):
            top[i] = int(top[i] * day_factor)
            bot[i] = int(bot[i] * day_factor)
            
            # Add gold at sunset
            if sunset_factor > 0:
                bot[0] = int(bot[0] * (1-sunset_factor) + 255 * sunset_factor)
                bot[1] = int(bot[1] * (1-sunset_factor) + 150 * sunset_factor)
        
        return tuple(top), tuple(bot)

    def _render_sky(self, surface, time_of_day):
        top_col, bot_col = self._get_dynamic_sky_colors(time_of_day)
        
        # When using high-fidelity parallax, force the procedural background 
        # to remain sky-colored behind the translucent mountain strip,
        # instead of blending into the procedural sandy ground color.
        # Also fill the ENTIRE screen (H) instead of just down to ROAD_Y.
        bg_height = H if self.layers else ROAD_Y
        if self.layers:
            bot_col = [min(255, int(c * 1.2)) for c in top_col]
        
        # Draw gradient
        for y in range(bg_height):
            t = y / bg_height
            c = [int(top_col[i] * (1-t) + bot_col[i] * t) for i in range(3)]
            pygame.draw.line(surface, c, (0, y), (W, y))

        # City or Hills (Procedural) - skip if using custom high-fi layers
        if not self.layers:
            palette = BIOME_PALETTES.get(self.biome, BIOME_PALETTES["desert"])
            day_factor = max(0.2, math.sin(time_of_day * math.pi))

        
        if self.biome == "city":
            for i in range(2):
                base_col = (10 + i*10, 10 + i*10, 20 + i*10)
                col = [int(c * day_factor) for c in base_col]
                random.seed(42 + i) # Stable city
                for x in range(0, W, 30 + i*20):
                    bw = random.randint(30, 60)
                    bh = random.randint(40, 120) + i*40
                    pygame.draw.rect(surface, col, (x, ROAD_Y - bh, bw, bh))
                    if i == 1 and time_of_day < 0.4 or time_of_day > 0.6:
                        # City windows glow at night
                        for wy in range(ROAD_Y - bh + 5, ROAD_Y - 5, 12):
                            if random.random() > 0.6:
                                pygame.draw.rect(surface, (255, 240, 150), (x+5, wy, 4, 3))
        else:
            # Only draw procedural hills if no external layers are found
            if not self.layers:
                for layer in range(3):
                    base_col = palette["hills"][layer]
                    col = [int(c * day_factor) for c in base_col]
                    pts = [(0, ROAD_Y)]
                    seed = layer * 50
                    for x in range(0, W + 40, 40):
                        noise = math.sin(x * 0.01 + seed) * 25 + math.sin(x * 0.02 + seed) * 12
                        hy = ROAD_Y - 20 - (2-layer)*25 + noise
                        pts.append((x, hy))
                    pts.append((W, ROAD_Y))
                    pygame.draw.polygon(surface, col, pts)

    def _generate_detailed_clouds(self):
        """Load fx_cloud.png sprite, or fall back to procedural puffs."""
        self.cloud_surfs = []
        cloud_path = os.path.join(SPRITES_DIR, "fx", "fx_cloud.png")
        if os.path.exists(cloud_path):
            try:
                base = pygame.image.load(cloud_path).convert_alpha()
                # Use 3 instances at different scales for variety
                for scale in [1.0, 0.75, 1.2]:
                    w = int(base.get_width() * scale)
                    h = int(base.get_height() * scale)
                    self.cloud_surfs.append(pygame.transform.scale(base, (w, h)))
                # Fill to 5 with more copies
                self.cloud_surfs.append(pygame.transform.scale(base, (int(base.get_width() * 0.9), int(base.get_height() * 0.9))))
                self.cloud_surfs.append(pygame.transform.scale(base, (int(base.get_width() * 1.1), int(base.get_height() * 0.85))))
                return
            except Exception as e:
                print(f"Could not load fx_cloud: {e}")
        # Procedural fallback
        for _ in range(5):
            cw, ch = random.randint(100, 220), random.randint(40, 80)
            cs = pygame.Surface((cw, ch), pygame.SRCALPHA)
            for _ in range(30):
                ox = random.randint(20, cw-20); oy = random.randint(15, ch-15)
                rad = random.randint(15, 40)
                pygame.draw.circle(cs, (255, 255, 255, 160), (ox, oy), rad)
            self.cloud_surfs.append(cs)

    def _generate_detailed_field(self):
        palette = BIOME_PALETTES.get(self.biome, BIOME_PALETTES["desert"])
        self.field_surf.fill((0,0,0,0))
        # Base ground
        pygame.draw.rect(self.field_surf, palette["field"], (0, 0, W*2, 110))
        
        for _ in range(3000):
            fx = random.uniform(0, W * 2); fy = random.uniform(10, 100)
            scale = 0.5 + (fy / 100)
            if self.biome == "desert":
                pygame.draw.line(self.field_surf, (40, 70, 20), (fx, fy), (fx, fy + 8), 1)
                pygame.draw.circle(self.field_surf, (220, 190, 30), (fx, fy), 3*scale)
            elif self.biome == "forest":
                 pygame.draw.rect(self.field_surf, (40, 120, 30), (fx, fy, 2, 10*scale))
            else:
                 pygame.draw.circle(self.field_surf, (140, 150, 140), (fx, fy), 2*scale)

    def _generate_detailed_car(self):
        s = self.car_cache
        s.fill((0, 0, 0, 0))
        # Try to load van sprite from vehicles/ subfolder
        path = os.path.join(SPRITES_DIR, "vehicles", "v_van.png")
        if not os.path.exists(path):
            path = os.path.join(SPRITES_DIR, "v_van.png")  # legacy fallback
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                # Reduce size by 30%: 160 * 0.7 = 112
                tgt_w = 112
                tgt_h = int(img.get_height() * (tgt_w / img.get_width()))
                img = pygame.transform.scale(img, (tgt_w, tgt_h))
                
                # Draw shadow first (centered under 112px car)
                pygame.draw.ellipse(s, (0, 0, 0, 100), (10, 68, 112, 8))
                s.blit(img, (10, 70 - tgt_h))
                return
            except Exception as e:
                print(f"Error loading v_van: {e}")

        # Boxy Retro Sedan (Player) - Procedural Fallback 30% smaller
        pygame.draw.ellipse(s, (0, 0, 0, 100), (10, 68, 112, 8)) # Shadow
        pygame.draw.rect(s, (200, 195, 175), (15, 30, 105, 25), border_radius=3) # Body
        pygame.draw.rect(s, (200, 195, 175), (35, 15, 65, 18), border_radius=3) # Cabin
        pygame.draw.rect(s, (140, 180, 210), (40, 18, 25, 12)) # Windows
        pygame.draw.rect(s, (140, 180, 210), (70, 18, 20, 12))
        pygame.draw.rect(s, (40, 40, 45), (10, 45, 112, 6)) # Bumper
        for wx in (35, 95): # Wheels
            pygame.draw.circle(s, (25, 25, 30), (wx, 68), 10)
            pygame.draw.circle(s, (70, 75, 80), (wx, 68), 6)

    def set_biome(self, biome):
        if biome != self.biome:
            self.biome = biome
            self._generate_detailed_field()
            self._load_external_assets()

    def update(self, dt, speed, weather_state="sunny"):
        # COMENTARIO PARA MODIFICAR: 
        # Multiplicador global de velocidad del parallax (fondo del juego).
        # Incrementado de 60 a 160 para que la velocidad del escenario coincida con la sensación de alta velocidad y el mini-radar.
        self.scroll_x += speed * 160.0 * dt
    def render(self, surface, weather_state="sunny", time_of_day=0.5):
        day_factor = max(0, math.sin(time_of_day * math.pi))

        # 0. Always draw procedural sky gradient first as the base background
        # (layers are 75px strips, not full-screen backgrounds)
        self._render_sky(surface, time_of_day)
        
        # 1. Stars at night (behind strips)
        night_t = 1.0 - day_factor
        if night_t > 0.5:
            for sx, sy, sz in self.stars:
                if sy < 90:  # Only above the strips
                    pygame.draw.circle(surface, (255, 255, 250), (sx, sy), 1)

        # 2. Draw parallax strips BACK TO FRONT:
        # Index order in self.layers: [0]=road, [1]=mountains, [2]=sky-horizon
        # Draw order: 2 (sky/horizon), then 1 (mountains), then 0 (road) on top

        if self.layers:
            draw_order = list(reversed(range(len(self.layers))))
            
            for i in draw_order:
                layer = self.layers[i]
                speed_mult = self.layer_speeds[i] if i < len(self.layer_speeds) else 0.5
                total_w = layer.get_width()
                scroll = int(self.scroll_x * speed_mult) % total_w
                y = self.layer_ys[i] if hasattr(self, 'layer_ys') and i < len(self.layer_ys) else 0
                
                surface.blit(layer, (-scroll, y))
                surface.blit(layer, (total_w - scroll, y))  # wrap-around

            # Night darkening is now handled by renderer.py (darkness surface + light holes)
            pass


        # 3. Clouds (always drawn, over sky — shown when no external layers or semi-transparent)
        for i, cs in enumerate(self.cloud_surfs):
            cx = (W // 4 + i * 200 - self.scroll_x * 0.03) % (W + cs.get_width() + 100) - cs.get_width()
            cy = 18 + i * 12 + math.sin(pygame.time.get_ticks() * 0.0007 + i) * 5
            if cy + cs.get_height() < ROAD_Y:  # only draw if above road
                surface.blit(cs, (int(cx), int(cy)))
