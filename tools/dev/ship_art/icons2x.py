"""Room markings, FTL-style (Claude, 21 Nov 2026). Zachary: "the room identity markings as another asset to put on room
like FTL". One sheet, art/ui/ship/icons_systems.png: 32 x 32 icons side by side (double resolution; the game draws
each 16 x 16 cell pixels big in the middle of its room). White with a dark outline, so the game can tint them:
grey when working, red when damaged.

Order (ShipBattle.ROOM_ICONS must match): shields, engines, weapons, life, pilot, drones, cannon, medbay, crew.

Run from the repo root:  python3 -I tools/dev/ship_art/icons2x.py .
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

N = 32
ORDER = ["shields", "engines", "weapons", "life", "pilot", "drones", "cannon", "medbay", "crew"]
OUTLINE = (38, 37, 53, 255)


def blank():
    im = Image.new("L", (N, N), 0)
    return im, ImageDraw.Draw(im)


def shields():
    im, d = blank()
    d.polygon([(6, 5), (16, 2), (26, 5), (26, 15), (22, 23), (16, 29), (10, 23), (6, 15)], fill=255)
    d.polygon([(10, 8), (16, 6), (22, 8), (22, 15), (19, 21), (16, 24), (13, 21), (10, 15)], fill=0)
    d.polygon([(13, 10), (16, 9), (19, 10), (19, 15), (17, 19), (16, 20), (15, 19), (13, 15)], fill=255)
    return im


def engines():
    im, d = blank()
    d.polygon([(12, 4), (28, 7), (28, 25), (12, 28)], fill=255)          # the nozzle, opening left
    d.rectangle([14, 10, 15, 22], fill=0)
    for y, x0 in ((9, 3), (15, 1), (21, 3)):                             # exhaust streaks
        d.rectangle([x0, y, 9, y + 2], fill=255)
    return im


def weapons():
    im, d = blank()
    d.rectangle([4, 10, 22, 17], fill=255)                               # body
    d.rectangle([22, 12, 30, 15], fill=255)                              # barrel
    d.polygon([(8, 17), (14, 17), (12, 27), (6, 27)], fill=255)          # grip
    d.rectangle([7, 12, 18, 13], fill=0)
    return im


def life():
    im, d = blank()
    for (x, y, r) in ((11, 19, 8), (22, 9, 6), (24, 24, 4)):              # oxygen bubbles
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        d.ellipse([x - r + 3, y - r + 3, x + r - 3, y + r - 3], fill=0)
        d.rectangle([x - r // 2 - 1, y - r // 2 - 1, x - r // 2, y - r // 2], fill=255)
    return im


def pilot():
    im, d = blank()
    d.rectangle([7, 4, 13, 22], fill=255)                                # seat back
    d.rectangle([7, 18, 25, 23], fill=255)                               # seat
    d.rectangle([20, 12, 25, 17], fill=255)                              # arm rest
    d.rectangle([14, 23, 17, 28], fill=255)                              # post
    d.rectangle([9, 27, 23, 29], fill=255)                               # base
    return im


def drones():
    im, d = blank()
    d.ellipse([10, 10, 22, 22], fill=255)
    for (x, y) in ((4, 4), (24, 4), (4, 24), (24, 24)):
        d.line([(16, 16), (x + 2, y + 2)], fill=255, width=3)
        d.ellipse([x - 1, y - 1, x + 5, y + 5], fill=255)
    d.ellipse([14, 14, 18, 18], fill=0)
    return im


def cannon():
    im, d = blank()
    d.rectangle([3, 11, 15, 21], fill=255)
    d.rectangle([15, 13, 27, 19], fill=255)
    d.rectangle([26, 11, 30, 21], fill=255)
    for x in (18, 22):
        d.rectangle([x, 12, x + 1, 20], fill=0)
    d.polygon([(6, 1), (8, 5), (12, 3), (10, 7), (4, 6)], fill=255)    # a spark: overcharged
    return im


def medbay():
    im, d = blank()
    d.rectangle([12, 4, 20, 28], fill=255)
    d.rectangle([4, 12, 28, 20], fill=255)
    return im


def crew():
    im, d = blank()
    d.ellipse([11, 3, 21, 13], fill=255)
    d.pieslice([5, 15, 27, 39], 180, 360, fill=255)
    return im


def sheet():
    out = Image.new("RGBA", (N * len(ORDER), N), (0, 0, 0, 0))
    for i, name in enumerate(ORDER):
        m = np.array(globals()[name]()) > 0
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & ~m
        a = np.zeros((N, N, 4), np.uint8)
        a[m] = (255, 255, 255, 255)
        a[ring] = OUTLINE
        out.alpha_composite(Image.fromarray(a, "RGBA"), (i * N, 0))
    return out


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    (root / "art/ui/ship").mkdir(parents=True, exist_ok=True)
    sheet().save(root / "art/ui/ship/icons_systems.png")
    print("ok")
