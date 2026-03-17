"""
Reliable Asset Downloader for Keep Driving.
Uses basic Pollinations URL format to avoid 401/400 errors.
"""
import urllib.request
import urllib.parse
import os
import time

BASE_URL = "https://gen.pollinations.ai/image"

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(BASE_DIR, "assets", "sprites")

FOLDERS = ["backgrounds", "van", "objects", "ui"]
for folder in FOLDERS:
    os.makedirs(os.path.join(SPRITES_DIR, folder), exist_ok=True)

ASSETS = [
    {"file": "backgrounds/sky_serene.png", "w": 640, "h": 200, "prompt": "high quality pixel art serene sky morning hills distant mountains atmospheric, retro game background"},
    {"file": "backgrounds/sunflower_field.png", "w": 640, "h": 120, "prompt": "high quality pixel art seamless field of sunflowers and grass horizontal strip white background no sky"},
    {"file": "backgrounds/forest_dense.png", "w": 640, "h": 120, "prompt": "high quality pixel art seamless dense forest bushes horizontal strip white background no sky"},
    {"file": "van/car_detailed.png", "w": 200, "h": 100, "prompt": "highly detailed pixel art 80s sedan car beige side view realistic proportions clean lines white background"},
    {"file": "objects/tree_big.png", "w": 128, "h": 160, "prompt": "detailed pixel art large oak tree roadside white background"},
    {"file": "ui/dashboard_base.png", "w": 640, "h": 90, "prompt": "pixel art car dashboard interface bottom bar olive green texture gauges dials retro 90s"},
]

def download(asset):
    prompt_encoded = urllib.parse.quote(asset["prompt"])
    # Simplest possible URL
    url = f"{BASE_URL}/{prompt_encoded}?width={asset['w']}&height={asset['h']}&nologo=true"
    
    out_path = os.path.join(SPRITES_DIR, asset["file"])
    print(f"  ↓ {asset['file']} ... ", end="", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) > 2000:
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"OK ({len(data)//1024}KB)")
    except Exception as e:
        print(f"FAIL: {e}")
    time.sleep(1)

if __name__ == "__main__":
    for asset in ASSETS:
        download(asset)
