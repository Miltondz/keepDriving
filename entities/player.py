"""Player character — stats, inventory, hitchhikers."""
from core.config import MAX_SANITY, MAX_HITCHHIKERS


class Player:
    def __init__(self, name="Driver"):
        self.name             = name
        self.sanity           = MAX_SANITY
        self.money            = 50
        self.distance_traveled = 0.0      # total km driven this run
        self.current_location = "START"
        self.hitchhikers      = []        # list of Hitchhiker instances

    # ── Stats ──────────────────────────────────────────────────────────────
    def modify_sanity(self, delta: float):
        self.sanity = max(0.0, min(float(MAX_SANITY), self.sanity + delta))

    def earn(self, amount: int):
        self.money = max(0, self.money + amount)

    def spend(self, amount: int) -> bool:
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    # ── Hitchhikers ────────────────────────────────────────────────────────
    def add_hitchhiker(self, hh) -> bool:
        if len(self.hitchhikers) < MAX_HITCHHIKERS:
            self.hitchhikers.append(hh)
            return True
        return False

    def remove_hitchhiker(self, hh):
        if hh in self.hitchhikers:
            self.hitchhikers.remove(hh)

    # ── Per-frame update ───────────────────────────────────────────────────
    def update_travel(self, km: float):
        """Call every tick while in TRAVEL state."""
        self.distance_traveled += km
        
        # Base sanity drain (energy): 1 per 8 km (GDD 5.1)
        self.modify_sanity(-(km / 8.0))

        for hh in list(self.hitchhikers):
            hh.travel(km)
            hh.apply_passive(self, km)

    # ── Checks ─────────────────────────────────────────────────────────────
    @property
    def is_sane(self):
        return self.sanity > 0

    @property
    def hitchhiker_count(self):
        return len(self.hitchhikers)
