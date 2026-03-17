import os
from PIL import Image, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def extract_vehicles(src_path, dest_dir):
    img = Image.open(src_path).convert("RGBA")
    
    # Simple background removal (assuming white/very light background)
    datas = img.getdata()
    new_data = []
    for item in datas:
        # If pixels are near white, make them transparent
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    
    # Now find individual components (roughly)
    # Since they are laid out horizontally, we can split by columns or use a more robust detection
    # For this specific image, I'll use a detection based on bounding boxes of separate clusters
    
    # Find all non-transparent pixels
    import numpy as np
    arr = np.array(img)
    alpha = arr[:,:,3]
    
    # Find columns that have any non-transparent pixel
    cols = np.any(alpha > 0, axis=0)
    
    # Identify ranges of columns
    segments = []
    start = None
    for i, active in enumerate(cols):
        if active and start is None:
            start = i
        elif not active and start is not None:
            if i - start > 10: # Minimum width
                segments.append((start, i))
            start = None
            
    vehicle_names = ["moped", "sedan", "truck", "police", "van"]
    
    for i, (s, e) in enumerate(segments):
        if i >= len(vehicle_names): break
        
        # Crop the segment
        v_img = img.crop((s, 0, e, img.height))
        # Trim vertical empty space
        v_img = trim(v_img)
        
        # Flip horizontally (as requested: "apuntarlos en direccion contraria")
        # The originals are facing Left, flipping makes them face Right
        v_img = v_img.transpose(Image.FLIP_LEFT_RIGHT)
        
        name = vehicle_names[i]
        out_path = os.path.join(dest_dir, f"v_{name}.png")
        v_img.save(out_path)
        print(f"Extracted and flipped {name} to {out_path}")

if __name__ == "__main__":
    src = r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773598630431.png"
    dest = r"c:\Milton\keep_driving\assets\sprites"
    if not os.path.exists(dest): os.makedirs(dest)
    extract_vehicles(src, dest)
