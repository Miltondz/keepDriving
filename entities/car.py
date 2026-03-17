"""Car physics and state."""
import math

class Car:
    def __init__(self):
        self.speed = 0
        self.max_speed = 100
        self.acceleration = 20
        self.braking = 30
        self.friction = 5
        self.steering_angle = 0
        
    def accelerate(self):
        """Increase speed."""
        self.speed = min(self.speed + self.acceleration * 0.1, self.max_speed)
        
    def brake(self):
        """Decrease speed."""
        self.speed = max(self.speed - self.braking * 0.1, 0)
        
    def steer(self, direction):
        """Steer left (-1) or right (1)."""
        self.steering_angle = direction * 15
        
    def update(self, dt):
        """Update car physics."""
        # Apply friction
        if self.speed > 0:
            self.speed = max(0, self.speed - self.friction * dt)
            
        # Return steering to center
        if self.steering_angle != 0:
            self.steering_angle *= 0.9
            if abs(self.steering_angle) < 1:
                self.steering_angle = 0
