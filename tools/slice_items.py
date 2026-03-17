from PIL import Image
import os

SPRITES_DIR = r"c:\Milton\keep_driving\assets\sprites"
SRC = r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773614660899.png"

def slice_items():
    img = Image.open(SRC).convert("RGBA")
    w, h = img.size
    
    # 5 items in a row
    strip_w = w // 5
    names = ["thermos", "wheel", "gas_can", "wrench", "food"]
    
    for i in range(5):
        strip = img.crop((i * strip_w, 0, (i+1) * strip_w, h))
        
        # Background removal (white)
        data = strip.getdata()
        new_data = []
        for item in data:
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        strip.putdata(new_data)
        
        bbox = strip.getbbox()
        if bbox:
            final = strip.crop(bbox)
            # Resize item to a standard UI/Game size (e.g. 48px height)
            target_h = 48
            ratio = target_h / final.height
            final = final.resize((int(final.width * ratio), target_h), Image.Resampling.NEAREST) # NEAREST for pixel art
            
            out_path = os.path.join(SPRITES_DIR, f"item_{names[i]}.png")
            final.save(out_path)
            print(f"Saved {out_path}")

if __name__ == "__main__":
    slice_items()
