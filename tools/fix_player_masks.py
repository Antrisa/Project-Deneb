"""Fixes the player layer masks: a pixel only counts as skin (green) if the art there is skin-toned.
Grey details that were marked as skin (collars, seams, buckles) become part of the main colour (red).
    python3 tools/fix_player_masks.py <project folder>
"""
import sys
from PIL import Image
folder = sys.argv[1] + "/art/player/"
for k in ("tops", "bottoms", "hair"):
    art = Image.open(folder + k + ".png").convert("RGBA")
    mask = Image.open(folder + k + "_mask.png").convert("RGBA")
    ap, mp = art.load(), mask.load()
    changed = 0
    for y in range(art.height):
        for x in range(art.width):
            mr, mg, mb, ma = mp[x, y]
            if ma and not mr and mg:
                r, g, b, a = ap[x, y]
                if not (r - b >= 24 and r > g):          # not a warm skin tone
                    mp[x, y] = (255, 0, 0, 255)
                    changed += 1
    mask.save(folder + k + "_mask.png")
    print(k, "mask: fixed", changed, "pixels")
