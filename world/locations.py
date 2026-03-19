"""Location types, road segments, and settlements."""
from enum import Enum, auto
import random

# ============================================================================
# CONSTANTES DE CONFIGURACIÓN (para pruebas)
# ============================================================================

# Distancia entre encuentros - reducir para pruebas más frecuentes
TEST_MODE = True  # Cambiar a False para producción

if TEST_MODE:
    # Modo de prueba: encuentros frecuentes (cada 20-30 segundos a 150+ km/h)
    # A 150 km/h: 20 seg = 0.83 km, 30 seg = 1.25 km
    KM_PER_ENCOUNTER_MIN = 0.8
    KM_PER_ENCOUNTER_MAX = 1.3
    ENCOUNTERS_PER_SEGMENT = 10
else:
    # Modo producción: encuentros cada 30-50 km
    KM_PER_ENCOUNTER_MIN = 30
    KM_PER_ENCOUNTER_MAX = 50
    ENCOUNTERS_PER_SEGMENT = 3


class RoadType(Enum):
    DESERT = "desert"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    HIGHWAY = "highway"
    COASTAL = "coastal"
    CITY = "city"


class SettlementSize(Enum):
    GAS_STATION = "gas_station"
    SMALL_TOWN = "small_town"
    CITY = "city"


# Colores para cada tipo de camino (para representación visual)
ROAD_COLORS = {
    RoadType.DESERT: (200, 150, 80),
    RoadType.FOREST: (80, 150, 80),
    RoadType.MOUNTAIN: (120, 120, 140),
    RoadType.HIGHWAY: (150, 150, 150),
    RoadType.COASTAL: (100, 180, 200),
    RoadType.CITY: (180, 180, 220),
}


class Settlement:
    def __init__(self, name, size, services=None):
        self.name = name
        self.size = size
        self.services = services or []  # 'fuel', 'repair', 'shop', 'rest', 'recruit'
        self.visited = False
        self.position_km = 0  # Posición en el mapa (se asigna dinámicamente)


SETTLEMENTS = [
    # Desert / Lowlands
    Settlement("Dusty Creek", SettlementSize.GAS_STATION, ['fuel', 'rest']),
    Settlement("Redrock Junction", SettlementSize.SMALL_TOWN, ['fuel', 'repair', 'shop', 'recruit']),
    Settlement("Las Piedras", SettlementSize.CITY, ['fuel', 'repair', 'shop', 'rest', 'recruit']),
    # Forest
    Settlement("Pine Hollow", SettlementSize.SMALL_TOWN, ['fuel', 'shop', 'rest']),
    Settlement("Whispering Pines", SettlementSize.GAS_STATION, ['fuel', 'rest']),
    # Mountain roads
    Settlement("Coldwater Pass", SettlementSize.GAS_STATION, ['fuel']),
    Settlement("Summit Ridge", SettlementSize.SMALL_TOWN, ['fuel', 'repair', 'rest']),
    Settlement("Eagle's Nest", SettlementSize.GAS_STATION, ['fuel', 'rest']),
    Settlement("Rocky Heights", SettlementSize.SMALL_TOWN, ['fuel', 'shop', 'repair']),
    # Coastal
    Settlement("Bayside", SettlementSize.CITY, ['fuel', 'repair', 'shop', 'rest', 'recruit']),
    Settlement("Saltmarsh", SettlementSize.GAS_STATION, ['fuel']),
]


class RoadSegment:
    """One traversable stretch of road between two map nodes."""

    # Encounter pools per road type
    ENCOUNTER_POOLS = {
        RoadType.DESERT: [
            'flat_tire', 'hitchhiker', 'heat_shimmer', 'sandstorm',
            'broken_down_car', 'mirage', 'police_check',
        ],
        RoadType.FOREST: [
            'deer_crossing', 'fallen_tree', 'hitchhiker',
            'fog', 'scenic_overview',
        ],
        RoadType.MOUNTAIN: [
            'rockslide', 'fog', 'altitude_trouble', 'hitchhiker',
            'scenic_view', 'fallen_tree', 'steep_grade', 'brake_overheat',
            'sharp_turn', 'wildlife_crossing', 'narrow_bridge',
        ],
        RoadType.HIGHWAY: [
            'traffic_jam', 'aggressive_tailgater', 'police_check', 'hitchhiker',
            'rest_stop', 'radio_signal',
        ],
        RoadType.COASTAL: [
            'hitchhiker', 'fog', 'seagull_attack',
            'scenic_view',
        ],
        RoadType.CITY: [
            'pothole', 'neon_distraction', 'delivery_moped', 'hitchhiker',
            'traffic_light',
        ],
    }

    def __init__(self, road_type: RoadType, length_km=50, test_encounters=None):
        self.road_type = road_type
        self.length_km = length_km

        if test_encounters is not None:
            self.encounters_remaining = list(test_encounters)
        else:
            # Seleccionar encuentros aleatorios del pool
            pool = self.ENCOUNTER_POOLS.get(road_type, [])
            num_encounters = ENCOUNTERS_PER_SEGMENT
            self.encounters_remaining = random.sample(pool, k=min(num_encounters, len(pool)))

        # Calcular distancia entre encuentros
        self.km_per_encounter = random.uniform(KM_PER_ENCOUNTER_MIN, KM_PER_ENCOUNTER_MAX)
        self.distance_since_last = 0.0
        self.km_driven = 0.0

    def tick(self, km_driven) -> str | None:
        """Advance along segment. Returns encounter key or None."""
        self.km_driven += km_driven
        self.distance_since_last += km_driven
        if self.encounters_remaining and self.distance_since_last >= self.km_per_encounter:
            self.distance_since_last = 0.0
            # Nuevo intervalo aleatorio para siguiente encuentro
            self.km_per_encounter = random.uniform(KM_PER_ENCOUNTER_MIN, KM_PER_ENCOUNTER_MAX)
            return self.encounters_remaining.pop(0)
        return None

    @property
    def completed(self):
        return self.km_driven >= self.length_km

    @property
    def distance_to_next_encounter(self) -> float:
        """Distancia restante hasta el próximo encuentro."""
        return max(0, self.km_per_encounter - self.distance_since_last)