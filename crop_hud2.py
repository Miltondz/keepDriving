import pygame
import os

pygame.init()
pygame.display.set_mode((100, 100), pygame.HIDDEN)

# The user's original image (the crop of the dashboard, not a gameplay screenshot)
img = pygame.image.load("assets/sprites/hud_base.png").convert_alpha()
w, h = img.get_size()
print(f"Original user uploaded image size: {w}x{h}")

# The user uploaded image looks like the HUD itself.
# Let's scale it to exactly exactly 640 x 99 width and save it to assets/ui/hud_bg.png
# Wait... if the image is 638x348, maybe it's the full screenshot but with only the bottom part?
# Let's see the alpha or the black pixels. 
# Oh wait, the user's uploaded image was 638x116 maybe?
# Let's do a crop automatically by ignoring completely dark top rows.
min_y = h
max_y = 0
for y in range(h):
    for x in range(w):
        c = img.get_at((x, y))
        if c.r > 10 or c.g > 10 or c.b > 10:
            if y < min_y: min_y = y
            if y > max_y: max_y = y

if min_y <= max_y:
    hud = img.subsurface((0, min_y, w, max_y - min_y + 1))
    print(f"Content bounding Y: {min_y} to {max_y}")
    # Now scale nicely to 640 width
    ratio = 640 / w
    new_h = int((max_y - min_y + 1) * ratio)
    hud_scaled = pygame.transform.smoothscale(hud, (640, new_h))
    
    os.makedirs("assets/ui", exist_ok=True)
    pygame.image.save(hud_scaled, "assets/ui/hud_bg_scaled.png")
    print(f"Saved scaled cropped version to assets/ui/hud_bg_scaled.png, new size: {hud_scaled.get_size()}")
else:
    print("Blank image")
