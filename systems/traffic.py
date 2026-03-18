import pygame
import random
import os
from core.config import BASE_RESOLUTION, ROAD_Y, SPRITES_DIR

W, H = BASE_RESOLUTION

class TrafficVehicle:
    def __init__(self, type_name, x, speed, direction=1):
        self.type = type_name
        self.x = x
        self.speed = speed
        self.direction = direction # 1 = same way, -1 = opposite
        self.lane = 0 if direction == 1 else 1 # 0=near, 1=far
        self.sprite = None
        self._load_sprite()
        
    def _load_sprite(self):
        # Sprites live in the vehicles/ subfolder
        path = os.path.join(SPRITES_DIR, "vehicles", f"v_{self.type}.png")
        if not os.path.exists(path):
            # Fallback: sprites root (legacy)
            path = os.path.join(SPRITES_DIR, f"v_{self.type}.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            # Scale targets
            if self.type == "moped": tw = 49
            elif self.type in ["truck", "dumptruck"]: tw = 161
            else: tw = 102  # sedan, wagon, taxi, police, van…

            th = int(img.get_height() * (tw / img.get_width()))
            scaled = pygame.transform.scale(img, (tw, th))

            # ── Direction / Flip logic ─────────────────────────────────────
            # Si el código original volteaba todos los autos que iban en nuestra dirección (1),
            # significa que nativamente apuntaban hacia la DERECHA y los estábamos rompiendo,
            # o apuntaban a la izquierda y nosotros también voltearemos los que vienen de frente (-1).
            # Ahora: Los que vienen de frente (-1) se voltean. Los que van en nuestra vía (1) no se voltean.
            if self.direction == -1:
                scaled = pygame.transform.flip(scaled, True, False)

            self.sprite = scaled

    def update(self, dt, player_speed):
        # Relative speed
        if self.direction == 1:
            rel_speed = player_speed - self.speed
        else:
            rel_speed = player_speed + self.speed # Approaching speed
            
        # El multiplicador original 10x era extremadamente rápido visualmente.
        # Reducido a 2.5x para mantener una sensación jugable y reactiva sin que se teletransporten.
        self.x -= rel_speed * dt * 2.5
        
    def render(self, surface):
        if self.sprite:
            # Aligned to road lanes (Canales)
            # Lane 0 (Near): 254, Lane 1 (Far): 240
            base_y = 254 if self.lane == 0 else 240
            sy = base_y - self.sprite.get_height()
            surface.blit(self.sprite, (self.x, sy))

class TrafficManager:
    def __init__(self):
        self.vehicles = []
        self.spawn_timer = 0
        self.types = ["sedan", "moped", "police", "truck", "taxi", "wagon", "dumptruck"]
        
    def update(self, dt, player_speed):
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and len(self.vehicles) < 3:
            self.spawn_vehicle()
            self.spawn_timer = random.uniform(5, 15)
            
        for v in self.vehicles[:]:
            v.update(dt, player_speed)
            if v.x < -600 or v.x > W + 600:
                self.vehicles.remove(v)
                
    def spawn_vehicle(self):
        v_type = random.choice(self.types)
        
        # Decide direction
        if random.random() > 0.4:
            # Same direction traffic
            direction = 1
            if random.random() > 0.5:
                # Overtaking us from behind
                x = -200
                speed = random.uniform(85, 115)
            else:
                # We are overtaking it
                x = W + 200
                speed = random.uniform(35, 55)
        else:
            # Opposite direction traffic (approaching)
            direction = -1
            x = W + 400
            speed = random.uniform(60, 90)
            
        self.vehicles.append(TrafficVehicle(v_type, x, speed, direction))
        
    def render(self, surface):
        for v in self.vehicles:
            v.render(surface)
