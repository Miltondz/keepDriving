"""World map — manages the player's position in the generated route."""
from world.procedural import WorldGenerator
from world.locations import RoadSegment, Settlement


class WorldMap:
    """Tracks player progress through the procedurally generated route."""

    def __init__(self, seed=None, num_segments=8):
        gen = WorldGenerator(seed=seed)
        self.route = gen.generate_run(num_segments)
        self.index = 0           # current position in route
        self.total_km = 0.0      # total distance driven this run

    @property
    def current_node(self):
        if self.index < len(self.route):
            return self.route[self.index]
        return None

    @property
    def is_road(self):
        return isinstance(self.current_node, RoadSegment)

    @property
    def is_settlement(self):
        return isinstance(self.current_node, Settlement)

    @property
    def at_end(self):
        return self.index >= len(self.route)

    def advance_km(self, km) -> str | None:
        """Drive km on current road segment. Returns encounter key or None."""
        node = self.current_node
        if not isinstance(node, RoadSegment):
            return None
        self.total_km += km
        encounter = node.tick(km)
        if node.completed:
            self.index += 1   # move to next node (settlement or next road)
        return encounter

    def leave_settlement(self):
        """Player leaves current settlement."""
        if self.is_settlement:
            self.current_node.visited = True
            self.index += 1

    def progress_fraction(self):
        """0.0 → 1.0 progress through the whole run."""
        return min(1.0, self.index / len(self.route))
