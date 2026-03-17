"""Location types, road segments, and settlements."""
from enum import Enum, auto
import random


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


class Settlement:
    def __init__(self, name, size, services=None):
        self.name = name
        self.size = size
        self.services = services or []  # 'fuel', 'repair', 'shop', 'rest', 'recruit'
        self.visited = False


SETTLEMENTS = [
    Settlement("Dusty Creek", SettlementSize.GAS_STATION,
               ['fuel', 'rest']),
    Settlement("Redrock Junction", SettlementSize.SMALL_TOWN,
               ['fuel', 'repair', 'shop', 'recruit']),
    Settlement("Las Piedras", SettlementSize.CITY,
               ['fuel', 'repair', 'shop', 'rest', 'recruit']),
    Settlement("Pine Hollow", SettlementSize.SMALL_TOWN,
               ['fuel', 'shop', 'rest']),
    Settlement("Coldwater Pass", SettlementSize.GAS_STATION,
               ['fuel']),
    Settlement("Bayside", SettlementSize.CITY,
               ['fuel', 'repair', 'shop', 'rest', 'recruit']),
]


class RoadSegment:
    """One traversable stretch of road between two map nodes."""

    # Encounter pools per road type
    ENCOUNTER_POOLS = {
        RoadType.DESERT: [
            'flat_tire', 'hitchhiker', 'heat_shimmer', 'sandstorm',
            'broken_down_car', 'roadkill_detour', 'mirage', 'police_check',
        ],
        RoadType.FOREST: [
            'deer_crossing', 'fallen_tree', 'hitchhiker', 'campfire_smoke',
            'fog', 'muddy_road', 'scenic_overlook', 'logging_truck',
        ],
        RoadType.MOUNTAIN: [
            'rockslide', 'fog', 'altitude_trouble', 'hitchhiker',
            'scenic_view', 'brake_overheat', 'wildlife_crossing', 'snow_patch',
        ],
        RoadType.HIGHWAY: [
            'traffic_jam', 'aggressive_tailgater', 'police_check', 'hitchhiker',
            'construction_zone', 'rest_stop', 'radio_signal', 'fuel_price_war',
        ],
        RoadType.COASTAL: [
            'hitchhiker', 'fog', 'seagull_attack', 'washed_road',
            'scenic_view', 'beach_detour', 'broken_bridge', 'fisherman',
        ],
        RoadType.CITY: [
            'pothole', 'street_racer', 'neon_distraction', 'delivery_moped',
            'pedestrian_crossing', 'traffic_light', 'hitchhiker', 'billboard_flash',
        ],
    }

    def __init__(self, road_type: RoadType, length_km=50, test_encounters=None):
        self.road_type = road_type
        self.length_km = length_km
        if test_encounters is not None:
            self.encounters_remaining = list(test_encounters)
        else:
            self.encounters_remaining = random.sample(
                self.ENCOUNTER_POOLS[road_type],
                k=random.randint(3, 5)
            )
        self.km_per_encounter = length_km / (len(self.encounters_remaining) + 1)
        self.distance_since_last = 0.0
        self.km_driven = 0.0

    def tick(self, km_driven) -> str | None:
        """Advance along segment. Returns encounter key or None."""
        self.km_driven += km_driven
        self.distance_since_last += km_driven
        if self.encounters_remaining and self.distance_since_last >= self.km_per_encounter:
            self.distance_since_last = 0.0
            return self.encounters_remaining.pop(0)
        return None

    @property
    def completed(self):
        return self.km_driven >= self.length_km
