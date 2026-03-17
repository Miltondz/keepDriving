import pygame
import os

pygame.init()
pygame.display.set_mode((640, 360), pygame.HIDDEN)

hud_bg = pygame.image.load("assets/ui/hud_bg.png").convert_alpha()
debug_surf = hud_bg.copy()

# ENERGY blocks (red)
start_x, start_y = 55, 23
block_w, block_h, gap = 8, 11, 2
for i in range(8):
    bx = start_x + i * (block_w + gap)
    pygame.draw.rect(debug_surf, (255, 0, 0, 200), (bx, start_y, block_w, block_h), 1)

# STATUS squares (green)
st_x, st_y = 55, 43
st_w, st_h, st_gap = 15, 13, 3
for i in range(5):
    bx = st_x + i * (st_w + st_gap)
    pygame.draw.rect(debug_surf, (0, 255, 0, 200), (bx, st_y, st_w, st_h), 1)

# LCD panel (blue)
lx, ly = 163, 10
inner_lcd_w = 265
pygame.draw.rect(debug_surf, (0, 0, 255, 200), (lx, ly, inner_lcd_w, 55), 1)

# CAR blocks (yellow)
cx, cy = 480, 18
cw, ch, cgap = 8, 9, 2
for idx in range(20):
    row = idx // 10
    col_pos = idx % 10
    bx = cx + col_pos * (cw + cgap)
    by = cy + row * (ch + cgap)
    pygame.draw.rect(debug_surf, (255, 255, 0, 200), (bx, by, cw, ch), 1)

# GAS pivot (white dot)
pygame.draw.circle(debug_surf, (255, 255, 255), (571, 89), 4)

pygame.image.save(debug_surf, "assets/ui/hud_alignment_test.png")
print("Saved alignment test image")
