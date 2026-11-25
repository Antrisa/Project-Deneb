"""Item icons for Sesska's clothes (Zachary, 24 Nov: her stock was placeholders): knit cap, woven scarf, work shirt,
woven shawl, station coat, cavern-silk coat. 24 x 24 in the item style: light from the upper left, 3-4 flat tones per
material, a lit top edge, faces darker toward the bottom and right, warm dark outline.
    python3 tools/dev/prop_art/sesska_icons.py <repo>   (writes art/items/<id>.png; then run tools/dev/shop_icons.py)"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home_machines import C, H, BRASS, CREAM, STEEL

S = 24


def mask(poly):
    im = Image.new("L", (S, S), 0)
    ImageDraw.Draw(im).polygon(poly, fill=255)
    return np.array(im) > 0


def fill(c, m, ramp, rim=True, right=2):
    """Flat tones: lit top rows, mid, darker lower third, a step darker along the right edge of each row."""
    ys, xs = np.nonzero(m)
    y0, y1 = ys.min(), ys.max()
    for y, x in zip(ys, xs):
        t = (y - y0) / max(1, y1 - y0)
        k = 0 if t < 0.15 else 1 if t < 0.6 else 2
        row = xs[ys == y]
        if x > row.max() - right: k += 1
        if x == row.min() and 0.1 < t < 0.9: k = max(0, k - 1)
        c.px(x, y, ramp[min(len(ramp) - 1, k)])
    if rim:
        for x in range(S):
            col = np.nonzero(m[:, x])[0]
            if len(col): c.px(x, col.min(), ramp[0])


RED = [H("ff9a7a"), H("e8574a"), H("b83a45"), H("7e2a42")]
TEAL = [H("8ad6c0"), H("55b0a6"), H("37868f"), H("2c5e76")]
DENIM = [H("a8c4e8"), H("6f8fc8"), H("4d63a0"), H("343f74")]
PLUM = [H("d6a0d0"), H("a86aa8"), H("7a4680"), H("4e2a5a")]
NAVY = [H("7a86b8"), H("4f5a8c"), H("363f68"), H("252a4a")]
PEARL = [H("fbf4ff"), H("e0d4f0"), H("bfb0dc"), H("8e7eb8")]


def knit_cap():
    c = C(S, S)
    dome = mask([(5, 14), (6, 9), (9, 6), (12, 5), (15, 6), (18, 9), (19, 14)])
    fill(c, dome, RED)
    for x in range(7, 18, 2):                       # knit rows
        c.px(x, 9, RED[2]); c.px(x + 1, 11, RED[2])
    brim = mask([(4, 14), (20, 14), (20, 18), (4, 18)])
    fill(c, brim, [H("ffd0b8"), H("f4a088"), H("d06a62"), H("9a4452")], right=2)
    for x in range(5, 20, 2):                       # ribbing
        c.vline(x, 15, 17, H("c25a58"))
    for y in range(1, 6):                           # pom-pom
        for x in range(9, 16):
            if (x - 12) ** 2 + (y - 3) ** 2 <= 7:
                c.px(x, y, CREAM[0] if y < 3 and x < 13 else CREAM[1] if y < 5 else CREAM[2])
    c.outline(); return c


def woven_scarf():
    c = C(S, S)
    loop = mask([(4, 6), (9, 3), (16, 3), (20, 7), (18, 11), (12, 9), (7, 10), (6, 14)])
    tail = mask([(6, 11), (11, 10), (12, 20), (7, 21)])
    tail2 = mask([(13, 9), (18, 10), (17, 19), (12, 18)])
    fill(c, loop, TEAL); fill(c, tail, TEAL); fill(c, tail2, TEAL)
    for y in (13, 16):                              # station-colour stripes
        for x in range(6, 19):
            if c.get(x, y)[3]: c.px(x, y, BRASS[1]); c.px(x, y + 1, CREAM[1]) if c.get(x, y + 1)[3] else None
    for x in (7, 9, 11, 12, 14, 16):                # fringe
        c.px(x, 21 if x < 12 else 20, CREAM[2]); c.px(x, 22 if x < 12 else 21, CREAM[3])
    c.outline(); return c


def work_shirt():
    c = C(S, S)
    shirt = mask([(7, 3), (10, 4), (14, 4), (17, 3), (22, 7), (20, 11), (18, 10), (18, 21), (6, 21), (6, 10), (4, 11), (2, 7)])
    fill(c, shirt, DENIM)
    c.vline(12, 5, 20, DENIM[3])                    # placket and buttons
    for y in (7, 11, 15, 19): c.px(13, y, CREAM[1])
    for x0 in (7, 14):                              # chest pockets
        c.hline(x0, x0 + 3, 9, DENIM[3]); c.vline(x0, 9, 12, DENIM[3]); c.vline(x0 + 3, 9, 12, DENIM[3]); c.hline(x0, x0 + 3, 12, DENIM[3])
        c.hline(x0 + 1, x0 + 2, 10, DENIM[0])
    for (x, y) in ((9, 4), (10, 5), (11, 6), (15, 4), (14, 5), (13, 6)):   # collar
        c.px(x, y, DENIM[0])
    c.outline(); return c


def woven_shawl():
    c = C(S, S)
    shawl = mask([(2, 5), (22, 5), (12, 19)])
    fill(c, shawl, PLUM)
    c.hline(3, 21, 5, PLUM[0])
    for (cx, cy) in ((8, 8), (16, 8), (12, 12)):    # Sesska's diamond pattern
        for (dx, dy) in ((0, -2), (-1, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, 2)):
            c.px(cx + dx, cy + dy, BRASS[1] if dy < 0 else BRASS[2])
        c.px(cx, cy, CREAM[1])
    for i, (x, y) in enumerate(((4, 7), (6, 9), (8, 11), (10, 13), (11, 16), (13, 16), (14, 13), (16, 11), (18, 9), (20, 7))):
        c.px(x - 1, y + 1, CREAM[2]); c.px(x - 1, y + 2, CREAM[3])   # fringe along the edges
    for y in range(19, 23): c.px(12, y, CREAM[2 if y < 21 else 3])
    c.outline(); return c


def long_coat(ramp, sheen=None):
    c = C(S, S)
    coat = mask([(7, 2), (10, 3), (14, 3), (17, 2), (21, 6), (20, 13), (18, 12), (19, 22), (5, 22), (6, 12), (4, 13), (3, 6)])
    fill(c, coat, ramp)
    for (x, y) in ((9, 3), (10, 5), (11, 7), (12, 9), (15, 3), (14, 5), (13, 7)):   # lapels
        c.px(x, y, ramp[0] if x < 12 else ramp[2])
    c.vline(12, 9, 21, ramp[3])
    return c


def station_coat():
    c = long_coat(NAVY)
    for y in (11, 14, 17): c.px(13, y, BRASS[1]); c.px(14, y, BRASS[3])
    c.hline(6, 18, 15, H("2a1d2e")); c.px(12, 15, BRASS[0]); c.px(11, 15, BRASS[1])   # belt and buckle
    c.hline(5, 7, 13, NAVY[0]); c.hline(17, 19, 13, NAVY[2])                          # cuffs
    c.outline(); return c


def silk_coat():
    c = long_coat(PEARL)
    for (x, y, col) in ((7, 8, "8fd8ff"), (8, 9, "8fd8ff"), (9, 13, "ffb0e0"), (10, 14, "ffb0e0"), (15, 10, "8fd8ff"),
                        (16, 11, "c8a8ff"), (14, 17, "ffb0e0"), (8, 18, "c8a8ff"), (16, 19, "8fd8ff")):
        c.px(x, y, H(col))                          # the silk's shimmer
    for (x, y) in ((6, 6), (18, 15), (10, 20)):
        c.px(x, y, (255, 255, 255, 255))            # glints
    for y in (11, 14, 17): c.px(13, y, CREAM[0])
    c.outline(); return c


ICONS = {"knit_cap": knit_cap, "woven_scarf": woven_scarf, "work_shirt": work_shirt, "woven_shawl": woven_shawl,
         "station_coat": station_coat, "silk_coat": silk_coat}

if __name__ == "__main__":
    repo = sys.argv[1]
    for n, fn in ICONS.items():
        fn().save(os.path.join(repo, "art", "items", n + ".png"))
    print("ok", len(ICONS))
