import os
import json

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')

# Game Constants
MAX_FUEL = 100
MAX_SANITY = 100
MAX_HITCHHIKERS = 3
MAX_PASSENGERS = 4
ROAD_Y = 240
DASH_Y = 270
TARGET_FPS = 60
TIME_ACCEL = 0.002

# Window Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BASE_RESOLUTION = (640, 360)

# Load JSON Data (Vehicles and Locations Only)
WORLD_DATA = {}
world_data_path = os.path.join(BASE_DIR, 'data', 'world_assets.json')
if os.path.exists(world_data_path):
    with open(world_data_path, 'r') as f:
        WORLD_DATA = json.load(f)

# Window Settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BASE_RESOLUTION = (640, 360)

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
