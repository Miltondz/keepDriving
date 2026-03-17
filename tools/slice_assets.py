import pygame
import os

def slice_strips(input_path, output_dir, prefix):
    pygame.display.init()
    # Dummy display for loading
    pygame.display.set_mode((1, 1), pygame.NOFRAME)
    
    print(f"Loading {input_path}...")
    try:
        source = pygame.image.load(input_path)
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    # Scale to target master resolution
    source = pygame.transform.scale(source, (1920, 1080))
    w, h = source.get_size()
    print(f"Rescaled size: {w}x{h}")
    
    strip_h = 360
    for i in range(3):
        y = i * strip_h
        strip = pygame.Surface((w, strip_h), pygame.SRCALPHA)
        strip.blit(source, (0, 0), (0, y, w, strip_h))
        
        out_name = f"{prefix}_{i+1}.png"
        out_path = os.path.join(output_dir, out_name)
        pygame.image.save(strip, out_path)
        print(f"Saved {out_path}")

if __name__ == "__main__":
    dest = r"c:\Milton\keep_driving\assets\sprites"
    if not os.path.exists(dest): os.makedirs(dest)
    
    # Biome Asset Map: (Source Path, Biome Name)
    biomes = [
        (r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773595701182.jpg", "desert"),
        (r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773606445119.jpg", "village"),
        (r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773606488594.jpg", "city"),
        (r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773606682624.jpg", "forest"),
        (r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773606819649.jpg", "mountain")
    ]
    
    for src, name in biomes:
        slice_strips(src, dest, f"{name}_road")

    # Handle Interiors
    interiors = [
        (r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773606597360.png", "interior_hotel.png"),
        (r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773608393480.png", "interior_garage.png"),
        (r"C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media__1773608439474.png", "interior_shop.png")
    ]
    
    for src, out_name in interiors:
        if os.path.exists(src):
            img = pygame.image.load(src)
            img = pygame.transform.scale(img, (640, 360))
            pygame.image.save(img, os.path.join(dest, out_name))
            print(f"Saved {out_name}")
