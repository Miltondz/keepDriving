import os
import pygame
from core.engine import KeepDrivingEngine, GameState
from core.config import SCREEN_WIDTH, SCREEN_HEIGHT

def capture_test_frame(output_path, distance=0):
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    
    pygame.init()
    engine = KeepDrivingEngine()
    engine.setup()
    
    # Start in TRAVEL state
    engine.state = GameState.TRAVEL
    engine.car.speed = 70 
    engine.player.distance_traveled = distance
    
    # Force spawn specific vehicles
    from systems.traffic import TrafficVehicle
    engine.traffic.vehicles.append(TrafficVehicle("dumptruck", 450, 40))
    engine.traffic.vehicles.append(TrafficVehicle("taxi", 50, 90))
    
    # Run a few updates
    dt = 0.05
    for _ in range(20):
        engine._update(dt)
    
    # Render
    engine._render()
    pygame.image.save(engine.canvas, output_path)
    pygame.quit()
    print(f"Captured {output_path} at distance {distance}")

if __name__ == "__main__":
    base = r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994"
    shots = [
        ("desert_v2.png", 50),
        ("village_v1.png", 250),
        ("forest_v1.png", 450),
        ("mountain_v1.png", 650),
        ("city_v1.png", 900)
    ]
    for filename, dist in shots:
        capture_test_frame(os.path.join(base, filename), dist)
