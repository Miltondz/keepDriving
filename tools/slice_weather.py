from PIL import Image, ImageOps
import os

SPRITES_DIR = r"c:\Milton\keep_driving\assets\sprites"
SRC = r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773614191650.png"

def slice_weather():
    img = Image.open(SRC).convert("RGBA")
    w, h = img.size
    
    # Simple horizontal split into 4
    strip_w = w // 4
    names = ["rain", "snow", "lightning", "cloud"]
    
    for i in range(4):
        strip = img.crop((i * strip_w, 0, (i+1) * strip_w, h))
        
        # Remove white background (approximate)
        # We look for pixels where R, G, B are all > 240
        data = strip.getdata()
        new_data = []
        for item in data:
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        strip.putdata(new_data)
        
        # Auto-crop to content
        bbox = strip.getbbox()
        if bbox:
            final = strip.crop(bbox)
            # Resize appropriately
            # Rain/Snow should be small (16-32px)
            # Cloud/Lightning should be medium (64-128px)
            if names[i] in ["rain", "snow"]:
                target_h = 32
            else:
                target_h = 128
                
            ratio = target_h / final.height
            final = final.resize((int(final.width * ratio), target_h), Image.Resampling.LANCZOS)
            
            out_path = os.path.join(SPRITES_DIR, f"fx_{names[i]}.png")
            final.save(out_path)
            print(f"Saved {out_path}")

if __name__ == "__main__":
    slice_weather()
