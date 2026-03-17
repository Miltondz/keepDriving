import pygame
pygame.init()
pygame.display.set_mode((640, 99), pygame.HIDDEN)
img = pygame.image.load("assets/ui/hud_bg.png")

# Find energy boxes (approx y=23 to 35, x=5 to 100)
def find_runs(y_target, x_start, x_end, threshold=30):
    runs = []
    in_run = False
    start_x = 0
    for x in range(x_start, x_end):
        r, g, b, _ = img.get_at((x, y_target))
        is_dark = (r < threshold and g < threshold and b < threshold)
        if is_dark and not in_run:
            start_x = x
            in_run = True
        elif not is_dark and in_run:
            runs.append((start_x, x - start_x))
            in_run = False
    if in_run:
        runs.append((start_x, x_end - start_x))
    return runs

print("Energy boxes (y=22):", find_runs(22, 5, 120))
print("Energy boxes (y=26):", find_runs(26, 5, 120))
print("Status boxes (y=56):", find_runs(56, 5, 120))
print("Status boxes (y=62):", find_runs(62, 5, 120))
print("Car boxes row 1 (y=22):", find_runs(22, 500, 630))
print("Car boxes row 2 (y=32):", find_runs(32, 500, 630))

# LCD Bounds
lcd_xs = find_runs(30, 150, 450, threshold=40)
print("LCD (y=30 dark):", lcd_xs)

