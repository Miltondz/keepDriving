from PIL import Image
import os

# Target Game Resolution height
TGT_H = 360
SPRITES_DIR = r"c:\Milton\keep_driving\assets\sprites"
ARTIFACTS_DIR = r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994"

# Road (Foreground) layer
road_asset = "media__1773613744978.png"

def process_road_only():
    src_path = os.path.join(ARTIFACTS_DIR, road_asset)
    if not os.path.exists(src_path):
        print(f"Missing {src_path}")
        return

    img = Image.open(src_path).convert("RGBA")
    w, h = img.size
    print(f"Original Size: {w}x{h}")
    
    # We want to scale the image so it fits the height perfectly (360)
    # The original is 1024x75. Scaling 75 to 360 involves a 4.8x zoom.
    
    # Resize keeping aspect ratio
    scale = TGT_H / h
    new_w = int(w * scale)
    
    # Important: Use NEAREST if it's pixel art to avoid blur, or LANCZOS if it's painted.
    # User complained it looked "stretched" and "blurry" before.
    # 1024 -> 4915 spread over a 640 wide screen means we see ~13% of the image at once.
    img_scaled = img.resize((new_w, TGT_H), Image.Resampling.LANCZOS)
    
    out_path = os.path.join(SPRITES_DIR, "desert_road_3.png")
    img_scaled.save(out_path)
    print(f"Saved {out_path} ({new_w}x{TGT_H})")

if __name__ == "__main__":
    process_road_only()
