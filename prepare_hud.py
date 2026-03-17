import pygame
import sys
import glob

pygame.init()

# Find the newest media file
files = glob.glob(r'C:\Users\Usuario\.gemini\antigravity\brain\3e8f24d5-9ab5-4909-a128-5d8c8fb6c994\media_*.png')
files.sort(key=lambda x: -int(x.split('media__')[1].split('.png')[0]) if 'media__' in x else 0)

latest = files[0]
print(f"Loading {latest}...")
img = pygame.image.load(latest)

# Scale to 640x99
hud = pygame.transform.smoothscale(img, (640, 99))
import os
os.makedirs("assets/ui", exist_ok=True)
pygame.image.save(hud, "assets/ui/hud_bg.png")
print("Saved scaled HUD to assets/ui/hud_bg.png")
