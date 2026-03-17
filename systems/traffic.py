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
        path = os.path.join(SPRITES_DIR, f"v_{self.type}.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            # 30% Smaller scale targets
            if self.type == "moped": tw = 49
            elif self.type in ["truck", "dumptruck"]: tw = 161
            else: tw = 102 # Sedan, Wagon, etc.
            
            th = int(img.get_height() * (tw / img.get_width()))
            self.sprite = pygame.transform.scale(img, (tw, th))
            
            # Base sprites face RIGHT. Flip if moving LEFT (towards us).
            if self.direction == -1:
                self.sprite = pygame.transform.flip(self.sprite, True, False)
            # If same direction traffic is moving FASTER than player, it might look like it's reversing
            # but usually they face forward.

    def update(self, dt, player_speed):
        # Relative speed
        if self.direction == 1:
            rel_speed = player_speed - self.speed
        else:
            rel_speed = player_speed + self.speed # Approaching speed
            
        self.x -= rel_speed * dt * 10 
        
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
