import pygame
import sys

pygame.init()
img = pygame.image.load("assets/sprites/hud_base.png")
w, h = img.get_size()

min_y = h
max_y = 0
for y in range(h):
    for x in range(w):
        c = img.get_at((x, y))
        if c.r > 10 or c.g > 10 or c.b > 10:
            if y < min_y: min_y = y
            if y > max_y: max_y = y

print(f"Content bounding Y: {min_y} to {max_y}")
if min_y <= max_y:
    hud = img.subsurface((0, min_y, w, max_y - min_y + 1))
    pygame.image.save(hud, "assets/ui/hud_bg.png")
    print(f"Saved cropped version as assets/ui/hud_bg.png, height: {max_y - min_y + 1}")
