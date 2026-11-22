# The title scene's twinkling stars (scripts/title_scene.gd STARS), as the pack's scene.cpp pickStars() finds
# them: one glint per 83x80 cell, pinned to the brightest high-contrast point of the starfield.
#   python3 tools/dev/title_stars.py title/scene/starfield.png
# Prints the table rows to paste into STARS: per cell (12 x 7) x, y, phase, twinkles per loop; -1 for none.
import sys
import numpy as np
from PIL import Image

sky = np.asarray(Image.open(sys.argv[1]).convert('RGBA')).astype(np.float32)
light = (np.float32(.24) * sky[..., 0] + np.float32(.58) * sky[..., 1] + np.float32(.18) * sky[..., 2]).astype(np.float32)
H, W = light.shape
for y0 in range(20, H - 40, 80):
    cells = []
    for x0 in range(220, W - 35, 83):
        ident = (x0 // 83) * 17 + (y0 // 80) * 31
        found = None
        if ident % 5 != 0:
            best, bx, by = np.float32(34), 0, 0
            for y in range(y0, min(y0 + 72, H - 5)):
                for x in range(x0, min(x0 + 76, W - 5)):
                    s = light[y, x] - np.float32(.25) * (light[y, x - 4] + light[y, x + 4] + light[y - 4, x] + light[y + 4, x])
                    if s > best:
                        best, bx, by = s, x, y
            if bx:
                found = f'{bx}, {by}, {(ident % 37) * .24:.2f}, {10 + ident % 11}'
        cells.append(found or '-1, -1, 0, 0')
    print('\t' + ',  '.join(cells) + ',')
