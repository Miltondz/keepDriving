"""
Traffic System - Keep Driving.

CONSTANTES DE DIRECCIÓN:
- DIRECTION_SAME = 1    -> Vehículo va en el MISMO sentido que el jugador (hacia la derecha)
- DIRECTION_ONCOMING = -1 -> Vehículo viene en sentido CONTRARIO (desde la derecha hacia la izquierda)

NOTA SOBRE SPRITES:
- Todos los sprites de vehículos tienen el frente apuntando hacia la IZQUIERDA
- Por lo tanto:
  * Para direction = 1 (mismo sentido): NO se voltea el sprite (muestra la parte trasera hacia la derecha)
  * Para direction = -1 (sentido contrario): SE VOLTEA el sprite (muestra el frente hacia la derecha, viene de derecha a izquierda)
"""
import pygame
import random
import os
from core.config import BASE_RESOLUTION, ROAD_Y, SPRITES_DIR, WORLD_DATA

W, H = BASE_RESOLUTION
PLAYER_X = W // 2 - 56

# ============================================================================
# CONSTANTES DE DIRECCIÓN DEL TRÁFICO
# ============================================================================
DIRECTION_SAME = 1      # Vehículo se mueve hacia la derecha (mismo sentido que el jugador)
DIRECTION_ONCOMING = -1 # Vehículo se mueve hacia la izquierda (sentido contrario)

# ============================================================================
# CONSTANTES DE VISUALIZACIÓN
# ============================================================================
# SPRITE_WIDTHS y VEHICLE_WEIGHTS se extraen ahora de WORLD_DATA
VEHICLES_CFG = WORLD_DATA.get("vehicles", {})

SPRITE_WIDTHS = {k: v["width"] for k, v in VEHICLES_CFG.items()}
SPRITE_WIDTH_DEFAULT = 102 

# Posición Y base del renderizado según el carril
LANE_Y_BASE = {
    0: 254,  # Carril del jugador (mismo sentido)
    1: 240,  # Carril contrario (sentido opuesto)
}

# Velocidad del scroll del tráfico en pantalla
TRAFFIC_SCROLL_MULT = 2.5

# Límites de velocidad del tráfico (km/h)
TRAFFIC_SPEED_SAME_MIN = 20   # Velocidad mínima para vehículos en mismo sentido
TRAFFIC_SPEED_SAME_MAX = 75   # Velocidad máxima para vehículos en mismo sentido
TRAFFIC_SPEED_ONCOMING_MIN = 30 # Velocidad mínima para vehículos en sentido contrario
TRAFFIC_SPEED_ONCOMING_MAX = 55 # Velocidad máxima para vehículos en sentido contrario

# ============================================================================
# TIPOS DE VEHÍCULOS DISPONIBLES
# ============================================================================
VEHICLE_TYPES = list(VEHICLES_CFG.keys())
VEHICLE_TYPES_EXCLUDED = ["van"] # El jugador conduce una van

# Pesos de aparición
VEHICLE_WEIGHTS = {k: v["weight"] for k, v in VEHICLES_CFG.items()}

# Número de vehículos recientes a considerar para evitar repeticiones
MIN_VEHICLES_BETWEEN_SAME = 3  # Mínimo de vehículos diferentes antes de repetir el mismo tipo

# ============================================================================
# CLASES
# ============================================================================

class TrafficVehicle:
    """Representa un vehículo individual en el tráfico."""
    
    def __init__(self, type_name, x, speed, direction=DIRECTION_SAME):
        self.type = type_name
        self.x = x
        self.speed = speed
        self.direction = direction  # DIRECTION_SAME o DIRECTION_ONCOMING
        self.lane = 0 if direction == DIRECTION_SAME else 1
        self.sprite = None
        self._load_sprite()

    def _load_sprite(self):
        """Carga y escala el sprite del vehículo, aplicando flip según la dirección."""
        path = os.path.join(SPRITES_DIR, "vehicles", f"v_{self.type}.png")
        if not os.path.exists(path):
            path = os.path.join(SPRITES_DIR, f"v_{self.type}.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            
            # Obtener ancho según el tipo de vehículo
            tw = SPRITE_WIDTHS.get(self.type, SPRITE_WIDTH_DEFAULT)
            
            # Escalar manteniendo proporción
            th = int(img.get_height() * (tw / img.get_width()))
            scaled = pygame.transform.scale(img, (tw, th))

            # ================================================================
            # LÓGICA DE VOLTEO DE SPRITES:
            # Los sprites tienen el frente apuntando a la IZQUIERDA.
            # - direction = DIRECTION_SAME (1): vehículo va hacia la derecha
            #   → Vemos su PARTE TRASERA → NO volteamos
            # - direction = DIRECTION_ONCOMING (-1): vehículo viene de derecha a izquierda
            #   → Vemos su FRENTE → VOLTEAMOS para que apunte hacia la derecha
            # ================================================================
            if self.direction == DIRECTION_ONCOMING:
                scaled = pygame.transform.flip(scaled, True, False)

            self.sprite = scaled

    def update(self, dt, player_speed):
        """Actualiza la posición del vehículo según la velocidad relativa."""
        if self.direction == DIRECTION_SAME:
            # Mismo sentido: velocidad relativa = velocidad del jugador - velocidad del vehículo
            rel_speed = player_speed - self.speed
        else:
            # Sentido contrario: velocidad relativa = velocidad del jugador + velocidad del vehículo
            rel_speed = player_speed + self.speed

        self.x -= rel_speed * dt * TRAFFIC_SCROLL_MULT

    def render(self, surface):
        """Dibuja el vehículo en la superficie dada."""
        if self.sprite:
            base_y = LANE_Y_BASE.get(self.lane, 254)
            sy = base_y - self.sprite.get_height()
            surface.blit(self.sprite, (self.x, sy))


class TrafficManager:
    """Gestiona la creación, actualización y renderizado del tráfico."""
    
    def __init__(self):
        self.vehicles = []
        self.spawn_timer = 0
        
        # Obtener tipos disponibles excluyendo los del jugador
        self.available_types = [t for t in VEHICLE_TYPES if t not in VEHICLE_TYPES_EXCLUDED]
        
        # Historial de tipos de vehículos recentemento spawnados (para evitar repeticiones)
        self.recent_types = []

    def _get_random_type(self):
        """Selecciona un tipo de vehículo al azar, evitando repeticiones recientes."""
        # Filtrar tipos disponibles y construir lista con pesos
        available = [t for t in self.available_types if t not in VEHICLE_TYPES_EXCLUDED]
        
        # Si el tipo más reciente está en el historial reciente, excluirlo temporalmente
        if len(self.recent_types) >= MIN_VEHICLES_BETWEEN_SAME:
            last_type = self.recent_types[-1]
            # Verificar si han pasado suficientes vehículos
            types_since_last = self.recent_types[MIN_VEHICLES_BETWEEN_SAME*-1:]
            if last_type in types_since_last and len(set(types_since_last)) < MIN_VEHICLES_BETWEEN_SAME:
                available = [t for t in available if t != last_type]
        
        # Construir lista con pesos
        weighted_list = []
        for vtype in available:
            weight = VEHICLE_WEIGHTS.get(vtype, 1)
            weighted_list.extend([vtype] * weight)
        
        if not weighted_list:
            weighted_list = available
            
        return random.choice(weighted_list)

    def update(self, dt, player_speed):
        """Actualiza el estado del tráfico."""
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and len(self.vehicles) < 5:
            self.spawn_vehicle()
            self.spawn_timer = random.uniform(2, 5)

        for v in self.vehicles[:]:
            v.update(dt, player_speed)
            # Eliminar vehículos que salgan de la pantalla
            if v.x < -600 or v.x > W + 600:
                self.vehicles.remove(v)

    def spawn_vehicle(self):
        """Crea un nuevo vehículo con posición, velocidad y dirección aleatorias."""
        v_type = self._get_random_type()

        # 60% de probabilidad: mismo sentido | 40%: sentido contrario
        if random.random() > 0.4:
            # === VEHÍCULO EN EL MISMO SENTIDO (hacia la derecha) ===
            direction = DIRECTION_SAME
            
            if random.random() > 0.5:
                # Aparece por la izquierda (detrás del jugador), lo va a adelantar
                x = -200
                lane = 0
                speed = random.uniform(TRAFFIC_SPEED_SAME_MIN, TRAFFIC_SPEED_SAME_MAX)
            else:
                # Aparece por la derecha (delante del jugador), el jugador lo adelanta
                x = W + 200
                lane = random.choice([0, 1])
                speed = random.uniform(TRAFFIC_SPEED_SAME_MIN, TRAFFIC_SPEED_SAME_MAX)
                
            vehicle = TrafficVehicle(v_type, x, speed, direction)
            vehicle.lane = lane
        else:
            # === VEHÍCULO EN SENTIDO CONTRARIO (viene de derecha a izquierda) ===
            direction = DIRECTION_ONCOMING
            x = W + 400
            lane = 1
            speed = random.uniform(TRAFFIC_SPEED_ONCOMING_MIN, TRAFFIC_SPEED_ONCOMING_MAX)
            
            vehicle = TrafficVehicle(v_type, x, speed, direction)
            vehicle.lane = lane

        # Registrar tipo para evitar repeticiones
        self.recent_types.append(v_type)
        # Mantener historial limitado
        if len(self.recent_types) > MIN_VEHICLES_BETWEEN_SAME * 2:
            self.recent_types = self.recent_types[-MIN_VEHICLES_BETWEEN_SAME:]
        
        self.vehicles.append(vehicle)

    def render(self, surface):
        """Dibuja todos los vehículos en la superficie."""
        for v in self.vehicles:
            v.render(surface)
