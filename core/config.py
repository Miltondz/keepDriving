"""Global game configuration — High Fidelity Edition."""
import os

# Window Settings
# We use a 16:9 ratio for a modern look, but with pixel-art density
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BASE_RESOLUTION = (640, 360)  # Internal render resolution (2x scaling to window)

TARGET_FPS = 60

# Game Constants
MAX_FUEL = 100
MAX_SANITY = 100
MAX_HITCHHIKERS = 3
MAX_PASSENGERS = 4  # Total seats in vehicle: 1 front + 3 back
ROAD_Y = 240 # Distance from top to road surface base

# Colors (RGB)
COLORS = {
    'bg_night': (10, 8, 20),
    'bg_day': (170, 190, 220),
    'ui_bg': (15, 15, 20),
    'ui_text': (200, 200, 210),
    'ui_highlight': (255, 215, 70),
    'fuel_low': (220, 80, 60),
    'fuel_ok': (80, 210, 100),
}

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')

# Ensure directories exist
for directory in [ASSETS_DIR, SPRITES_DIR]:
    os.makedirs(directory, exist_ok=True)
