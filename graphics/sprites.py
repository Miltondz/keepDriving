"""Sprite loading and management utilities."""
import pygame
import os
from core.config import ASSETS_DIR

def load_sprite(path, colorkey=None, scale=None):
    """Load a sprite from the assets directory."""
    full_path = os.path.join(ASSETS_DIR, 'sprites', path)
    try:
        image = pygame.image.load(full_path).convert_alpha()
        if colorkey is not None:
            image.set_colorkey(colorkey)
        if scale is not None:
            image = pygame.transform.scale(image, scale)
        return image
    except FileNotFoundError:
        # Return a placeholder surface if sprite not found
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 0, 255), surf.get_rect(), 2)
        return surf

def load_spritesheet(path, frame_width, frame_height):
    """Load a spritesheet and split into frames."""
    sheet = load_sprite(path)
    frames = []
    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()
    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            frame = sheet.subsurface((x, y, frame_width, frame_height))
            frames.append(frame)
    return frames
