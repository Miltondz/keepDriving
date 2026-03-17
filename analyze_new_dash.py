import pygame
import os

pygame.init()
pygame.display.set_mode((640, 360), pygame.HIDDEN)

img = pygame.image.load("assets/ui/dash_inferior.png").convert_alpha()
w, h = img.get_size()
scale = 640 / w
new_h = int(h * scale)
scaled = pygame.transform.smoothscale(img, (640, new_h))

# Find the regions by scanning for color patterns or just save a grid test
# Let's save a version with a grid to help identify coordinates
grid_surf = scaled.copy()
for x in range(0, 640, 20):
    pygame.draw.line(grid_surf, (255, 0, 0, 100), (x, 0), (x, new_h))
for y in range(0, new_h, 20):
    pygame.draw.line(grid_surf, (255, 0, 0, 100), (0, y), (640, y))

pygame.image.save(grid_surf, "assets/ui/dash_inferior_grid.png")
print(f"Saved assets/ui/dash_inferior_grid.png (size: 640x{new_h})")
