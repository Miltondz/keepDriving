import os
from PIL import Image, ImageChops
import numpy as np

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def extract_vehicles_v2(src_path, dest_dir):
    img = Image.open(src_path).convert("RGBA")
    
    # Simple background removal
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    
    arr = np.array(img)
    alpha = arr[:,:,3]
    cols = np.any(alpha > 0, axis=0)
    
    segments = []
    start = None
    for i, active in enumerate(cols):
        if active and start is None:
            start = i
        elif not active and start is not None:
            if i - start > 10:
                segments.append((start, i))
            start = None
            
    vehicle_names = ["taxi", "wagon", "dumptruck"]
    
    for i, (s, e) in enumerate(segments):
        if i >= len(vehicle_names): break
        
        v_img = img.crop((s, 0, e, img.height))
        v_img = trim(v_img)
        
        # Flip to face Right (direction of travel)
        v_img = v_img.transpose(Image.FLIP_LEFT_RIGHT)
        
        name = vehicle_names[i]
        out_path = os.path.join(dest_dir, f"v_{name}.png")
        v_img.save(out_path)
        print(f"Extracted and flipped {name} to {out_path}")

if __name__ == "__main__":
    src = r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773601825109.png"
    dest = r"c:\Milton\keep_driving\assets\sprites"
    if not os.path.exists(dest): os.makedirs(dest)
    extract_vehicles_v2(src, dest)
