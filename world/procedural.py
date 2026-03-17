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
        """Generate a custom TEST RUN to showcase all interaction types."""
        route = []
        
        # 1. Very short road with a hitchhiker and a narrative event (police)
        route.append(RoadSegment(
            RoadType.DESERT,
            length_km=15, 
            test_encounters=['hitchhiker', 'police_check']
        ))
        
        # 2. Complete Settlement (Hotel, Shop, Workshop, Recruit)
        route.append(Settlement(
            name="Testing Grounds Hub",
            size=SettlementSize.CITY,
            services=['fuel', 'repair', 'shop', 'rest', 'recruit']
        ))
        
        # 3. Another short road with animals and another hitchhiker
        route.append(RoadSegment(
            RoadType.FOREST,
            length_km=15,
            test_encounters=['deer_crossing', 'hitchhiker']
        ))

        # 4. Small Town with limited services to test partial menus
        route.append(Settlement(
            name="Sleepy Hollow",
            size=SettlementSize.SMALL_TOWN,
            services=['fuel', 'rest']
        ))
        
        # 5. Final long road to win
        route.append(RoadSegment(
            RoadType.HIGHWAY,
            length_km=30,
            test_encounters=['traffic_jam', 'flat_tire']
        ))
        
        return route

    def generate_segment(self, preferred_type=None):
        """Generate a single new segment (for infinite mode)."""
        road_type = preferred_type or random.choice(list(RoadType))
        return RoadSegment(road_type, random.randint(30, 80))
