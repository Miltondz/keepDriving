"""Car resource management."""
from core.config import *
from core.events import events, EVENTS

class CarManager:
    def __init__(self, player, car):
        self.player = player
        self.car = car
        self.fuel = MAX_FUEL
        self.condition = 100

    def update(self, dt):
        """Update car resources."""
        if self.car.speed > 0:
            km_this_frame = (self.car.speed / 3600.0) * dt
            # Base fuel consumption: 0.45 units per km (much more visible)
            # Higher speed = higher penalty
            speed_penalty = 1.0 + max(0, (self.car.speed - 90) / 60.0)
            fuel_consumption = km_this_frame * 0.45 * speed_penalty
            
            self.fuel = max(0.0, self.fuel - fuel_consumption)
            
            # Car condition decay at high speeds
            if self.car.speed > 110:
                wear = (self.car.speed - 110) * 0.0001 * dt
                self.condition = max(0.0, self.condition - wear)
            
            events.emit(EVENTS['FUEL_CHANGED'])

    def spend_fuel(self, amount):
        """Deduct fuel."""
        if self.fuel >= amount:
            self.fuel -= amount
            events.emit(EVENTS['FUEL_CHANGED'])
            return True
        return False

    def refuel(self, amount):
        """Add fuel up to max."""
        self.fuel = min(MAX_FUEL, self.fuel + amount)
        events.emit(EVENTS['FUEL_CHANGED'])