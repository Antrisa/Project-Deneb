"""Item icons for the home machines, shrunk from their props and snapped to the props' own colours."""
import sys
from PIL import Image
import numpy as np
R = sys.argv[1]
def icon(src, out, box=None):
    im = Image.open(src).convert('RGBA')
    if box: im = im.crop(box)
    im = im.crop(im.getbbox())
    s = min(22 / im.width, 22 / im.height)
    w, h = max(1, round(im.width * s)), max(1, round(im.height * s))
    a = np.array(im.resize((w, h), Image.LANCZOS)).astype(int)
    px = np.array(im).reshape(-1, 4); cols = np.unique(px[px[:, 3] > 200][:, :3], axis=0).astype(int)
    o = np.zeros((24, 24, 4), np.uint8); ox, oy = (24 - w) // 2, 24 - h - 1
    for y in range(h):
        for x in range(w):
            if a[y, x, 3] < 110: continue
            d = ((cols - a[y, x, :3]) ** 2).sum(1); o[oy + y, ox + x, :3] = cols[d.argmin()]; o[oy + y, ox + x, 3] = 255
    Image.fromarray(o).save(out)
icon(f'{R}/art/lunar/home_furnace_on.png', f'{R}/art/items/home_furnace.png', (0, 0, 48, 60))
icon(f'{R}/art/lunar/home_hub.png', f'{R}/art/items/home_hub.png')
Image.open(f'{R}/art/lunar/home_chest.png').save(f'{R}/art/items/home_chest.png')
