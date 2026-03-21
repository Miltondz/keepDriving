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
        """Generate a custom TEST RUN with 3 building types near the start for easy testing."""
        route = []

        # ── TEST BUILDINGS (short segments to reach quickly) ──────────
        # T1. Short road → Gas Station
        route.append(RoadSegment(
            RoadType.DESERT,
            length_km=0.5,
            test_encounters=[]
        ))
        route.append(Settlement(
            name="Roadside Oasis",
            size=SettlementSize.GAS_STATION,
            services=['fuel', 'shop', 'rest']
        ))

        # T2. Short road → Small Town (Mini-Market)
        route.append(RoadSegment(
            RoadType.DESERT,
            length_km=0.5,
            test_encounters=[]
        ))
        route.append(Settlement(
            name="Dusty Creek",
            size=SettlementSize.SMALL_TOWN,
            services=['shop', 'recruit', 'rest']
        ))

        # T3. Short road → City (Hotel)
        route.append(RoadSegment(
            RoadType.HIGHWAY,
            length_km=0.5,
            test_encounters=[]
        ))
        route.append(Settlement(
            name="Las Piedras Hotel",
            size=SettlementSize.CITY,
            services=['rest', 'shop', 'repair', 'recruit']
        ))

        # ── MAIN RUN (mountain biome) ────────────────────────────────
        # 1. Mountain road with multiple encounters
        route.append(RoadSegment(
            RoadType.MOUNTAIN,
            length_km=30,
            test_encounters=[
                'hitchhiker', 'rockslide', 'fog', 'altitude_trouble',
                'fallen_tree', 'sharp_turn', 'wildlife_crossing'
            ]
        ))

        # 2. Mountain settlement
        route.append(Settlement(
            name="Summit Ridge",
            size=SettlementSize.SMALL_TOWN,
            services=['fuel', 'repair', 'rest']
        ))

        # 3. Another mountain road
        route.append(RoadSegment(
            RoadType.MOUNTAIN,
            length_km=25,
            test_encounters=[
                'brake_overheat', 'narrow_bridge', 'hitchhiker',
                'scenic_view', 'fog'
            ]
        ))

        # 4. Mountain gas station
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