from PIL import Image
import os
import numpy as np

SPRITES_DIR = r"c:\Milton\keep_driving\assets\sprites"
ARTIFACTS_DIR = r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994"

# Asset mapping (confirmed by pixel analysis):
# 959 = Road strip -> 74% transparent, only road visible -> FRONT layer
# 972 = Mountains  -> 64% transparent, only mountains visible -> MID layer  
# 978 = Sky        ->  0% transparent, full solid sky -> BACK layer (full screen)

GAME_W = 4096   # Wide tiles = fewer visible seams
GAME_H = 360    # Full game canvas height

layers = [
    ("media__1773613744959.png", 1, "road"),       # Road  -> FRONT, 74% transparent
    ("media__1773613744972.png", 2, "mountains"),   # Mountains -> MID, 64% transparent
    ("media__1773613744978.png", 3, "sky"),         # Sky -> BACK, solid, horizon strip
]

def process():
    for src_fn, layer_num, role in layers:
        src_path = os.path.join(ARTIFACTS_DIR, src_fn)
        if not os.path.exists(src_path):
            print(f"Missing: {src_path}")
            continue
        
        img = Image.open(src_path).convert("RGBA")
        w, h = img.size
        # Retro 2x scale for ALL layers using NEAREST neighbor.
        # This matches the chunky pixel-art look of the reference truck image
        # and expands the 75px strips to 150px to fill the screen properly.
        scale = 2
        w, h = w * scale, h * scale
        img = img.resize((w, h), Image.Resampling.NEAREST)
        
        tiled = Image.new("RGBA", (GAME_W, h), (0, 0, 0, 0 if role != 'sky' else 255))

        for x in range(0, GAME_W, w):
            # CRITICAL: pass img as mask to preserve alpha transparency
            tiled.paste(img, (x, 0), img)
        out = tiled




        out_name = f"desert_road_{layer_num}.png"
        out_path = os.path.join(SPRITES_DIR, out_name)
        out.save(out_path)
        
        # Verify saved alpha
        saved = Image.open(out_path).convert("RGBA")
        import numpy as np
        alpha = np.array(saved)[:,:,3]
        transparent_pct = 100 * np.sum(alpha < 10) // alpha.size
        print(f"  -> Saved {out_path} ({out.size[0]}x{out.size[1]}), transparent={transparent_pct}%")


if __name__ == "__main__":
    process()
