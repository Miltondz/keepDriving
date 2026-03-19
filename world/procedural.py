"""Procedural world generator — creates varied road segments and routes."""
import random
from world.locations import RoadType, RoadSegment, Settlement, SettlementSize, SETTLEMENTS


class WorldGenerator:
    """Generates a sequence of road segments and settlements for a run."""

    BIOME_TRANSITIONS = {
        RoadType.DESERT: [RoadType.HIGHWAY, RoadType.MOUNTAIN],
        RoadType.HIGHWAY: [RoadType.DESERT, RoadType.FOREST, RoadType.COASTAL],
        RoadType.FOREST: [RoadType.MOUNTAIN, RoadType.HIGHWAY],
        RoadType.MOUNTAIN: [RoadType.FOREST, RoadType.COASTAL],
        RoadType.COASTAL: [RoadType.HIGHWAY, RoadType.DESERT],
    }

    def __init__(self, seed=None):
        random.seed(seed)
        self.seed = seed

    def generate_run(self, total_target_km=1500):
        """Generate a custom TEST RUN to showcase mountain biome and frequent events."""
        route = []

        # 1. Mountain road with multiple encounters (testing MOUNTAIN biome)
        route.append(RoadSegment(
            RoadType.MOUNTAIN,
            length_km=30,
            test_encounters=[
                'hitchhiker', 'rockslide', 'fog', 'altitude_trouble',
                'fallen_tree', 'sharp_turn', 'wildlife_crossing'
            ]
        ))

        # 2. Mountain settlement with services
        route.append(Settlement(
            name="Summit Ridge",
            size=SettlementSize.SMALL_TOWN,
            services=['fuel', 'repair', 'rest']
        ))

        # 3. Another mountain road with more events
        route.append(RoadSegment(
            RoadType.MOUNTAIN,
            length_km=25,
            test_encounters=[
                'brake_overheat', 'narrow_bridge', 'hitchhiker',
                'scenic_view', 'fog'
            ]
        ))

        # 4. Small mountain gas station
        route.append(Settlement(
            name="Eagle's Nest",
            size=SettlementSize.GAS_STATION,
            services=['fuel', 'rest']
        ))

        # 5. Final mountain stretch
        route.append(RoadSegment(
            RoadType.MOUNTAIN,
            length_km=20,
            test_encounters=[
                'altitude_trouble', 'rockslide', 'hitchhiker'
            ]
        ))

        return route

    def generate_segment(self, preferred_type=None):
        """Generate a single new segment (for infinite mode)."""
        road_type = preferred_type or random.choice(list(RoadType))
        return RoadSegment(road_type, random.randint(30, 80))