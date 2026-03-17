import pygame
import sys
import math

pygame.init()
pygame.display.set_mode((100, 100), pygame.HIDDEN)

img = pygame.image.load("assets/ui/dash_inferior.png").convert_alpha()
w, h = img.get_size()
print(f"dash_inferior.png size: {w}x{h}")

# Target size is 640 width
scale = 640 / w
new_h = int(h * scale)
print(f"Scaled size for 640 width: 640x{new_h}")

scaled = pygame.transform.smoothscale(img, (640, new_h))
pygame.image.save(scaled, "assets/ui/dash_inferior_scaled.png")

# Let's find some features: Where are the red pixels inside the energy bar (if any)? 
# Where are the dark empty boxes?
# Scanning row by row...

