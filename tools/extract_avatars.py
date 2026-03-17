"""
Extract individual character avatars from the two source images.
Image 1: 3 avatars in a row (mechanic, kid, agent)
Image 2: 6 avatars in 2 rows x 3 cols (cop, hiker_guy, hiker_girl, old_man, goth_girl, gas_worker)

Strategy: detect the true content boundaries by scanning for non-white pixels,
then split evenly. For each cell, trim white margins so the crop starts exactly
at the outer black border of each avatar frame. Finally, resize all outputs to
TARGET_SIZE using NEAREST so the pixel art stays crisp.

Usage: python tools/extract_avatars.py <image1_path> <image2_path>
"""

import sys
from PIL import Image
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sprites', 'portraits')
WHITE_THRESHOLD = 230   # pixels above this on all channels are considered white/background
TARGET_SIZE = (128, 128)  # all avatars will be saved at this size


def is_white(r, g, b):
    return r > WHITE_THRESHOLD and g > WHITE_THRESHOLD and b > WHITE_THRESHOLD


def tight_crop(img_rgba, box):
    """
    Given a rough bounding box (x0,y0,x1,y1), find the tightest rectangle
    that excludes the outer white margin, snapping to the first non-white pixel
    on each side.
    """
    x0, y0, x1, y1 = box
    pixels = img_rgba.load()

    # Scan from left
    left = x0
    for x in range(x0, x1):
        if any(not is_white(*pixels[x, y][:3]) for y in range(y0, y1)):
            left = x
            break

    # Scan from right
    right = x1 - 1
    for x in range(x1 - 1, x0, -1):
        if any(not is_white(*pixels[x, y][:3]) for y in range(y0, y1)):
            right = x
            break

    # Scan from top
    top = y0
    for y in range(y0, y1):
        if any(not is_white(*pixels[x, y][:3]) for x in range(x0, x1)):
            top = y
            break

    # Scan from bottom
    bottom = y1 - 1
    for y in range(y1 - 1, y0, -1):
        if any(not is_white(*pixels[x, y][:3]) for x in range(x0, x1)):
            bottom = y
            break

    return (left, top, right + 1, bottom + 1)


def find_rough_boxes(img, n_cols, n_rows):
    """
    Find the overall content bounding box (ignoring white background),
    then divide it evenly into a grid of n_cols x n_rows cells.
    """
    w, h = img.size
    pixels = img.load()

    left, top, right, bottom = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            if not is_white(r, g, b):
                if x < left:   left = x
                if x > right:  right = x
                if y < top:    top = y
                if y > bottom: bottom = y

    content_w = right - left + 1
    content_h = bottom - top + 1
    cell_w = content_w // n_cols
    cell_h = content_h // n_rows

    boxes = []
    for row in range(n_rows):
        for col in range(n_cols):
            x0 = left + col * cell_w
            y0 = top + row * cell_h
            x1 = x0 + cell_w
            y1 = y0 + cell_h
            boxes.append((x0, y0, x1, y1))

    return boxes


def extract_avatars(img_path, n_cols, n_rows, names):
    img = Image.open(img_path).convert("RGBA")
    rough_boxes = find_rough_boxes(img, n_cols, n_rows)

    saved = []
    for (rough_box, name) in zip(rough_boxes, names):
        # Snap tightly to the black border, removing white margins
        tight_box = tight_crop(img, rough_box)
        cropped = img.crop(tight_box)

        # Resize to uniform TARGET_SIZE using NEAREST to preserve pixel art crispness
        resized = cropped.resize(TARGET_SIZE, Image.NEAREST)

        out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        resized.save(out_path)
        print(f"  Saved {name}.png  crop={tight_box}  raw_size={cropped.size}  -> {TARGET_SIZE}")
        saved.append(out_path)
    return saved


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_avatars.py <image1> <image2>")
        sys.exit(1)

    img1 = sys.argv[1]
    img2 = sys.argv[2]

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\n[Image 1] Extracting 3 avatars from: {img1}")
    extract_avatars(img1, n_cols=3, n_rows=1,
                    names=["mechanic", "kid", "agent"])

    print(f"\n[Image 2] Extracting 6 avatars from: {img2}")
    extract_avatars(img2, n_cols=3, n_rows=2,
                    names=["cop", "hiker_guy", "hiker_girl", "old_man", "goth_girl", "gas_worker"])

    print(f"\nDone! All {len(['mechanic','kid','agent','cop','hiker_guy','hiker_girl','old_man','goth_girl','gas_worker'])} avatars saved to: {OUTPUT_DIR}")
    print(f"All resized to: {TARGET_SIZE[0]}x{TARGET_SIZE[1]}px")
