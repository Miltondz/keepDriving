"""Car physics and state."""
import math

class Car:
    def __init__(self):
        self.speed = 0
        self.max_speed = 170
        self.acceleration = 8
        self.braking = 30
        self.friction = 5
        self.steering_angle = 0
        
    def accelerate(self, dt=0.016):
        """Increase speed with initial resistance."""
        eff_acc = self.acceleration
        if self.speed < 30:
            eff_acc *= 0.4  # Resistance at low speeds
            
        self.speed = min(self.speed + eff_acc * dt * 10, self.max_speed)
        
    def brake(self, dt=0.016):
        """Decrease speed."""
        self.speed = max(self.speed - self.braking * dt * 10, 0)
        
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
