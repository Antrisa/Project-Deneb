"""Soften Garrick's jaw in profile.

Usage: python3 -I fix_chin.py WALK_IN WALK_OUT ACT_IN ACT_OUT

In each left-facing cell the lower face is a block whose front edge runs straight down for
six rows to the jaw line. The front edge now steps back over the last four rows
(0, 1, 1, 2, 3, 4 pixels), so the chin recedes under the mouth; the outline follows it.
Right-facing walk frames are re-mirrored from the left.
"""
import sys
import numpy as np
from PIL import Image

STEPS = [0, 1, 1, 2, 3, 4]


def left(c, y):
    xs = np.where(c[y, :, 3] > 0)[0]
    return int(xs.min()) if len(xs) else None


def trim(c):
    # the jaw: the longest run of rows in the head sharing the frontmost edge
    best = None
    y = 0
    while y < 28:
        x = left(c, y)
        if x is None:
            y += 1; continue
        y2 = y
        while y2 + 1 < 28 and left(c, y2 + 1) == x:
            y2 += 1
        if y2 - y + 1 >= 5 and (best is None or x < best[2]):
            best = (y, y2, x)
        y = y2 + 1
    if best is None:
        return c, None
    y0, y1, x = best
    rows = list(range(y1 - len(STEPS) + 1, y1 + 1))
    out = c.copy()
    for y, d in zip(rows, STEPS):
        if d == 0:
            continue
        line = c[y, x].copy()
        out[y, x:x + d] = 0
        out[y, x + d] = line
    return out, best


walk = np.array(Image.open(sys.argv[1]).convert("RGBA"))
for r in range(5):
    cell = walk[r * 48:(r + 1) * 48, 48:72].copy()
    new, info = trim(cell)
    print("walk", r, info)
    walk[r * 48:(r + 1) * 48, 48:72] = new
    walk[r * 48:(r + 1) * 48, 72:96] = new[:, ::-1]
Image.fromarray(walk).save(sys.argv[2])

act = np.array(Image.open(sys.argv[3]).convert("RGBA"))
DRINK_LEFT = 3
for f in range(4):
    cell = act[DRINK_LEFT * 48:(DRINK_LEFT + 1) * 48, f * 36:(f + 1) * 36].copy()
    new, info = trim(cell)
    print("act", f, info)
    act[DRINK_LEFT * 48:(DRINK_LEFT + 1) * 48, f * 36:(f + 1) * 36] = new
Image.fromarray(act).save(sys.argv[4])
