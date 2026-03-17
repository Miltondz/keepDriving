import os
from PIL import Image, ImageFilter

def smooth_edges(image_path):
    if not os.path.exists(image_path):
        return
    
    # Open image and ensure it has an alpha channel
    img = Image.open(image_path).convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    # Smoothing logic: 
    # Pixels that are almost white in the original (even if already transparent)
    # might carry a "white halo" if they were partially transparent.
    # We want to refine the alpha based on color distance to white.
    
    for item in datas:
        r, g, b, a = item
        # Calculate how "white" the pixel is
        whiteness = (r + g + b) / 3
        
        # if it's very white, make it more transparent
        if whiteness > 245:
            new_a = 0
        elif whiteness > 220:
            # Linear ramp for soft edges
            new_a = int((255 * (245 - whiteness)) / 25)
            if a < new_a: new_a = a # keep existing transparency if more aggressive
        else:
            new_a = a
            
        new_data.append((r, g, b, new_a))
    
    img.putdata(new_data)
    
    # Extra step: Blur the alpha channel slightly to remove jaggies
    alpha = img.split()[-1]
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.5))
    img.putalpha(alpha)
    
    img.save(image_path)
    print(f"Refined and smoothed: {image_path}")

def main():
    sprite_dir = r"c:\Milton\keep_driving\assets\sprites"
    vehicles = [f for f in os.listdir(sprite_dir) if f.startswith("v_") and f.endswith(".png")]
    
    for v in vehicles:
        smooth_edges(os.path.join(sprite_dir, v))

if __name__ == "__main__":
    main()
