import pygame
import sys
pygame.init()

W, H = 640, 99
surf = pygame.image.load("assets/ui/hud_bg.png").convert()

# Energy slots: 10 blocks (x=10, y=32, w=7, h=14, gap=2)
for i in range(10):
    pygame.draw.rect(surf, (255, 0, 0, 100), (9 + i*9, 26, 7, 14), 1)

# Status slots: 5 blocks
for i in range(5):
    pygame.draw.rect(surf, (0, 255, 0, 100), (9 + i*18, 62, 16, 16), 1)

# LCD
pygame.draw.rect(surf, (0, 0, 255, 100), (160, 10, 310, 50), 1)

# Car blocks: 10x2
for r in range(2):
    for c in range(10):
        pygame.draw.rect(surf, (255, 255, 0, 100), (525 + c*8, 23 + r*10, 6, 8), 1)

# Gas pivot
pygame.draw.circle(surf, (255, 0, 255), (570, 80), 3)

pygame.image.save(surf, "test_hud_overlay.png")
print("Saved test_hud_overlay.png")
