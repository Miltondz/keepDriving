"""
Generates an alignment overlay on dash_inferior.png using PRECISE coordinates
derived by looking at the actual pixel positions in the HIGH-RESOLUTION source.
"""
import pygame
import math

pygame.init()
pygame.display.set_mode((640, 115), pygame.HIDDEN)

# Load the actual hi-res source
src = pygame.image.load("assets/ui/dash_inferior.png").convert_alpha()
src_w, src_h = src.get_size()  # 1536x278
scaled = pygame.transform.smoothscale(src, (640, 115))

debug = scaled.copy()

# Scale factor from hi-res to 640x115
sx = 640 / src_w   # ~0.4167
sy = 115 / src_h   # ~0.4137

def sc(orig_x, orig_y, orig_w=None, orig_h=None):
    """Convert hi-res coordinates to 640x115 display coords."""
    x = int(orig_x * sx)
    y = int(orig_y * sy)
    if orig_w is not None and orig_h is not None:
        return x, y, int(orig_w * sx), int(orig_h * sy)
    return x, y

# ── LEFT PANEL ──────────────────────────────────────────────────────
# Looking at asset, ENERGY label is top-left, LED blocks to its right
# In the 1536x278 asset, the energy blocks appear to start around x=130, y=40, blocks are ~22px wide
energy_x, energy_y = sc(130, 40)
block_w, block_h = int(22 * sx), int(26 * sy)
gap = int(6 * sx)
for i in range(8):
    bx = energy_x + i * (block_w + gap)
    pygame.draw.rect(debug, (255, 0, 0), (bx, energy_y, block_w, block_h), 1)

# STATUS row: below ENERGY, starts around y=80 in 1536x278 source  
status_x, status_y = sc(130, 80)
st_w, st_h = int(36 * sx), int(30 * sy)
st_gap = int(8 * sx)
for i in range(5):
    bx = status_x + i * (st_w + st_gap)
    pygame.draw.rect(debug, (0, 255, 0), (bx, status_y, st_w, st_h), 1)

# ── LCD PANEL ───────────────────────────────────────────────────────
# LCD green screen approx x=430 to x=1100 width ~670, y=20 to y=220 height ~200
lcd_x, lcd_y, lcd_w, lcd_h = sc(430, 20, 670, 200)
pygame.draw.rect(debug, (0, 0, 255), (lcd_x, lcd_y, lcd_w, lcd_h), 1)

# ── RIGHT PANEL ─────────────────────────────────────────────────────
# CAR LED blocks top-right of the green screen area
# approximately x=1140, y=40, two rows of 10 blocks ~24x22px each
car_x, car_y = sc(1148, 40)
car_w, car_h = int(24 * sx), int(18 * sy)
car_gap = int(4 * sx)
for idx in range(20):
    row = idx // 10
    col_p = idx % 10
    bx = car_x + col_p * (car_w + car_gap)
    by = car_y + row * (car_h + int(4 * sy))
    pygame.draw.rect(debug, (255, 255, 0), (bx, by, car_w, car_h), 1)

# GAS semi-circular gauge pivot: around x=1400, y=200 in hi-res
gas_x, gas_y = sc(1400, 200)
pygame.draw.circle(debug, (255, 255, 255), (gas_x, gas_y), 4)

pygame.image.save(debug, "assets/ui/align2.png")
print(f"Saved align2.png  — energy={energy_x},{energy_y}  lcd={lcd_x},{lcd_y}  car={car_x},{car_y}  gas={gas_x},{gas_y}")
