"""
WeatherSystem — manages weather state transitions and particle effects.
All visual effects are confined to the gameplay zone (y=120 to y=261).
"""
import pygame
import random
import math

from core.config import BASE_RESOLUTION
W, H = BASE_RESOLUTION

GAME_TOP    = 120
GAME_BOTTOM = 261
GAME_H      = GAME_BOTTOM - GAME_TOP  # 141


class WeatherState:
    SUNNY     = "sunny"
    OVERCAST  = "overcast"
    RAIN      = "rain"
    STORM     = "storm"
    FOG       = "fog"
    SANDSTORM = "sandstorm"  # Desert exclusive
    SNOW      = "snow"       # Mountain exclusive


# Transition weights based on current state
TRANSITIONS = {
    WeatherState.SUNNY:     [(WeatherState.SUNNY, 60), (WeatherState.OVERCAST, 30), (WeatherState.FOG, 10)],
    WeatherState.OVERCAST:  [(WeatherState.OVERCAST, 40), (WeatherState.RAIN, 40), (WeatherState.SUNNY, 20)],
    WeatherState.RAIN:      [(WeatherState.RAIN, 50), (WeatherState.STORM, 20), (WeatherState.OVERCAST, 30)],
    WeatherState.STORM:     [(WeatherState.STORM, 40), (WeatherState.RAIN, 40), (WeatherState.OVERCAST, 20)],
    WeatherState.FOG:       [(WeatherState.FOG, 50), (WeatherState.SUNNY, 30), (WeatherState.OVERCAST, 20)],
    WeatherState.SANDSTORM: [(WeatherState.SANDSTORM, 60), (WeatherState.SUNNY, 40)],
    WeatherState.SNOW:      [(WeatherState.SNOW, 60), (WeatherState.OVERCAST, 40)],
}

BIOME_WEATHERS = {
    "desert":   [WeatherState.SUNNY, WeatherState.SANDSTORM, WeatherState.FOG],
    "village":  [WeatherState.SUNNY, WeatherState.OVERCAST, WeatherState.RAIN],
    "forest":   [WeatherState.OVERCAST, WeatherState.RAIN, WeatherState.FOG],
    "mountain": [WeatherState.SNOW, WeatherState.OVERCAST, WeatherState.STORM],
    "city":     [WeatherState.SUNNY, WeatherState.RAIN, WeatherState.STORM],
}


class WeatherSystem:
    def __init__(self):
        self.state            = WeatherState.SUNNY
        self.transition_timer = 0.0
        self.transition_every = 30.0   # seconds between transitions
        self.particles        = []
        self.lightning_active = 0.0
        self.shake_offset     = (0, 0)
        self.fx               = {}     # loaded sprites/surfaces
        self._load_fx()

    # ── Asset Loading ─────────────────────────────────────────────────────────
    def _load_fx(self):
        """Try to load weather sprites; silently skip missing files."""
        import os
        asset_dir = "assets/sprites"
        for name, path in [
            ("cloud",     "cloud.png"),
            ("rain",      "rain_drop.png"),
            ("lightning", "lightning.png"),
        ]:
            full = os.path.join(asset_dir, path)
            if os.path.exists(full):
                try:
                    self.fx[name] = pygame.image.load(full).convert_alpha()
                except Exception:
                    pass

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt, player=None, biome="desert"):
        # dt is in seconds
        self.shake_offset = (0, 0)

        # Advance transition timer
        self.transition_timer += dt
        if self.transition_timer >= self.transition_every:
            self.transition_timer = 0.0
            self._try_transition(biome)

        # Lightning cooldown
        if self.lightning_active > 0:
            self.lightning_active = max(0.0, self.lightning_active - dt)

        # Random lightning in storm
        if self.state == WeatherState.STORM:
            # probability scaled by dt
            if random.random() < 0.12 * dt:
                self.lightning_active = 0.15
                self.shake_offset     = (random.randint(-2, 2), random.randint(-1, 1))

        self._update_particles(dt)


    def _try_transition(self, biome: str):
        """Probabilistically move to next weather state."""
        allowed   = BIOME_WEATHERS.get(biome, list(TRANSITIONS.keys()))
        options   = [(s, w) for (s, w) in TRANSITIONS.get(self.state, []) if s in allowed]
        if not options:
            return
        states  = [o[0] for o in options]
        weights = [o[1] for o in options]
        self.state = random.choices(states, weights=weights)[0]

    def _update_particles(self, dt: float):
        """dt in seconds."""
        count  = 0
        p_type = None
        if self.state in (WeatherState.RAIN, WeatherState.STORM):
            count  = 3
            p_type = 'rain'
        elif self.state == WeatherState.SNOW:
            count  = 2
            p_type = 'snow'
        elif self.state == WeatherState.SANDSTORM:
            count  = 8
            p_type = 'dust'

        for _ in range(count):
            if len(self.particles) < 300:
                if p_type == 'dust':
                    # Horizontal sand/dust — spawns at left edge in game zone
                    self.particles.append({
                        'x':     random.uniform(-20, 0),
                        'y':     random.uniform(GAME_TOP, GAME_BOTTOM - 2),
                        'vx':    random.uniform(200, 440),  # fast horizontal wind
                        'vy':    random.uniform(0, 20),     # slight downward drift only
                        'type':  'dust',
                        'size':  random.randint(1, 2),
                        'alpha': random.randint(70, 150),
                    })
                elif p_type == 'snow':
                    self.particles.append({
                        'x':     random.uniform(0, W),
                        'y':     float(GAME_TOP),
                        'vx':    random.uniform(-15, 15),
                        'vy':    random.uniform(35, 80),
                        'type':  'snow',
                        'size':  1,
                        'alpha': 180,
                    })
                else:  # rain
                    self.particles.append({
                        'x':     random.uniform(-50, W + 50),
                        'y':     float(GAME_TOP - 5),
                        'vx':    random.uniform(30, 70),
                        'vy':    random.uniform(380, 600),
                        'type':  p_type,
                        'size':  1,
                        'alpha': 120,
                    })

        # Move and cull
        for p in self.particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            if p['x'] > W + 30 or p['y'] > GAME_BOTTOM + 5 or p['y'] < GAME_TOP - 10:
                self.particles.remove(p)

    # ── Lighting Filter (legacy — not used in current render pipeline) ─────────
    def get_lighting_filter(self, time_of_day):
        day_brightness = math.sin(time_of_day * math.pi)
        filt = pygame.Surface((W, H), pygame.SRCALPHA)
        if day_brightness < 0.4:
            night_factor = (0.4 - day_brightness) / 0.4
            filt.fill((10, 15, 35, int(180 * night_factor)))
        if self.state == WeatherState.OVERCAST:
            filt.fill((100, 100, 110, 40), special_flags=pygame.BLEND_RGBA_MULT)
        elif self.state == WeatherState.SANDSTORM:
            filt.fill((185, 140, 60, 65))
        elif self.state == WeatherState.STORM:
            filt.fill((20, 20, 40, 90))
            if self.lightning_active > 0:
                filt.fill((240, 245, 255, int(90 * self.lightning_active / 0.15)))
        return filt

    # ── Render ────────────────────────────────────────────────────────────────
    def render_over(self, surface):
        """
        Draw all weather effects ONLY within the gameplay zone (y=120-261).
        Uses an isolated offscreen surface to guarantee no bleed into UI areas.
        """
        GAME_W = surface.get_width()

        # Isolated surface — everything in LOCAL coordinates (y=0 is GAME_TOP)
        gamesurf = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)

        # 1. Sandstorm ambient tint
        if self.state == WeatherState.SANDSTORM:
            gamesurf.fill((185, 140, 60, 55))

        # 2. Clouds (storm / overcast / rain)
        if self.state in (WeatherState.OVERCAST, WeatherState.STORM, WeatherState.RAIN):
            if "cloud" in self.fx:
                for i in range(4):
                    cx = int((i * 200 + pygame.time.get_ticks() * 0.02) % (GAME_W + 200)) - 100
                    gamesurf.blit(self.fx["cloud"], (cx, -10))

        # 3. Storm lightning flash
        if self.state == WeatherState.STORM and self.lightning_active > 0:
            flash_alpha = int(85 * (self.lightning_active / 0.15))
            flash_s = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
            flash_s.fill((240, 245, 255, flash_alpha))
            gamesurf.blit(flash_s, (0, 0))
            if "lightning" in self.fx:
                lx = random.randint(0, GAME_W - 100)
                gamesurf.blit(self.fx["lightning"], (lx, 0))

        # 4. Particles (in local y coordinates)
        for p in self.particles:
            local_y = int(p['y']) - GAME_TOP
            local_x = int(p['x'])
            if local_y < 0 or local_y >= GAME_H:
                continue
            if local_x < -4 or local_x > GAME_W + 4:
                continue
            ptype  = p.get('type', '')
            size   = p.get('size', 1)
            alpha  = p.get('alpha', 120)
            sprite = self.fx.get(ptype)
            if sprite:
                gamesurf.blit(sprite, (local_x, local_y))
            elif ptype == 'dust':
                pygame.draw.circle(gamesurf, (210, 175, 90, alpha), (local_x, local_y), size)
            elif ptype == 'rain':
                pygame.draw.line(gamesurf, (140, 165, 210, alpha),
                                 (local_x, local_y), (local_x + 2, local_y + 7), 1)
            elif ptype == 'snow':
                pygame.draw.circle(gamesurf, (255, 255, 255, alpha), (local_x, local_y), size)

        # 5. Fog layers
        if self.state == WeatherState.FOG:
            for i in range(3):
                fy    = 50 + i * 25
                fog_s = pygame.Surface((GAME_W, 45), pygame.SRCALPHA)
                fog_s.fill((220, 225, 230, 18 + i * 8))
                gamesurf.blit(fog_s, (0, fy))

        # Composite onto main surface
        surface.blit(gamesurf, (0, GAME_TOP))
