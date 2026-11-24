"""The circuit suit (24 Nov): the earlier art's circuit bodysuit details on top 9 ("Circuit suit") and bottom 8
("Tech leggings").

Usage: python3 -I tools/circuit_suit.py [GAME_DIR]

Zachary's favourite outfit from the earlier player art was its circuit bodysuit: a dark suit with panel seams and
small mint lights. The current art's "Circuit suit" had lost them, so this paints them back on in the same places
and colours. The detail is drawn on the standing frame of each facing and carried to every walk and action frame by
matching the frame to the standing one (so it moves with the body), only onto the cloth (never the outline, never
skin). Its mask is cleared, so the lights keep their colour whatever colour the suit is dyed.
"""
import os, sys
import numpy as np
from PIL import Image

GAME = sys.argv[1] if len(sys.argv) > 1 else "."
FW, FH = 24, 48
MINT = (134, 203, 187, 255)     # the old suit's accent lights
SEAM = (48, 36, 49, 255)        # its panel seams, in the outline colour
COLLAR = (164, 172, 178, 255)

# Detail on the standing frame, facing down / up / left (right is left mirrored): (x, y, colour). Copied from
# the earlier art's suit (before the 22 Nov redo): panel seams down the sides of the chest, two lights on the
# chest and one on each shoulder, a lit collar tab, a lit line down the front from the side, and short lit
# stripes on the thighs.
def trace(points, colour):
    return [(x, y, colour) for x, y in points]

def run(x0, y0, x1, y1):
    pts = [(x0, y0)]
    x, y = x0, y0
    while (x, y) != (x1, y1):
        if x != x1:
            x += 1 if x1 > x else -1
        elif y != y1:
            y += 1 if y1 > y else -1
        pts.append((x, y))
    return pts

TOP = {
    0: trace(run(7, 23, 7, 31) + run(16, 23, 16, 31), SEAM)
       + trace([(11, 22), (12, 22)], COLLAR)
       + trace([(10, 25), (13, 25), (5, 26), (18, 26)], MINT),
    1: trace(run(7, 23, 7, 31) + run(16, 23, 16, 31), SEAM)
       + trace([(12, 25), (5, 26), (18, 26)], MINT),
    2: trace(run(13, 24, 13, 31), SEAM)
       + trace(run(9, 23, 9, 28) + [(12, 27)], MINT),
}
BOTTOM = {
    0: trace(run(9, 35, 9, 37) + run(15, 35, 15, 37), MINT),
    1: trace(run(9, 35, 9, 37) + run(15, 35, 15, 37), MINT),
    2: trace(run(12, 36, 12, 37) + run(12, 40, 12, 41), MINT),
}


def pattern(table, d):
    if d < 3:
        return table[d]
    return [(FW - 1 - x, y, c) for x, y, c in table[2]]


def offset(stand, cell):
    """The shift that best lays the standing frame's shape over this frame's (the body's bob and lean)."""
    a = stand[..., 3] > 0
    b = cell[..., 3] > 0
    best, at = -1, (0, 0)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            sh = np.zeros_like(a)
            ys = slice(max(0, dy), FH + min(0, dy)); yd = slice(max(0, -dy), FH + min(0, -dy))
            xs = slice(max(0, dx), FW + min(0, dx)); xd = slice(max(0, -dx), FW + min(0, -dx))
            sh[ys, xs] = a[yd, xd]
            score = (sh & b).sum() - 0.5 * (sh ^ b).sum()
            if score > best:
                best, at = score, (dx, dy)
    return at


def paint(cell, mcell, pts, dx, dy):
    op = cell[..., 3] > 0
    for x, y, c in pts:
        tx, ty = x + dx, y + dy
        if not (1 <= tx < FW - 1 and 1 <= ty < FH - 1):
            continue
        # the cloth only: opaque all round (not the outline), and not skin
        if not (op[ty, tx] and op[ty - 1, tx] and op[ty + 1, tx] and op[ty, tx - 1] and op[ty, tx + 1]):
            continue
        if mcell[ty, tx, 3] == 0 or mcell[ty, tx, 1] > 128:
            continue
        cell[ty, tx] = c
        mcell[ty, tx] = (0, 0, 0, 0)


def do_walk(folder, name, choice, table):
    path = os.path.join(GAME, folder, name + ".png")
    mpath = os.path.join(GAME, folder, name + "_mask.png")
    a = np.array(Image.open(path).convert("RGBA")); m = np.array(Image.open(mpath).convert("RGBA"))
    rows = a.shape[0] // (10 * FH)
    y0 = choice * rows * FH
    for d in range(4):
        xs = slice(d * FW, (d + 1) * FW)
        stand = a[y0:y0 + FH, xs].copy()
        pts = pattern(table, d)
        for r in range(rows):
            cell = a[y0 + r * FH:y0 + (r + 1) * FH, xs]
            mcell = m[y0 + r * FH:y0 + (r + 1) * FH, xs]
            dx, dy = offset(stand, cell)
            paint(cell, mcell, pts, dx, dy)
    Image.fromarray(a).save(path); Image.fromarray(m).save(mpath)
    return a[y0:y0 + FH].copy()


def do_action(folder, choice, stands):
    path = os.path.join(GAME, folder, "action_tops.png")
    mpath = os.path.join(GAME, folder, "action_tops_mask.png")
    a = np.array(Image.open(path).convert("RGBA")); m = np.array(Image.open(mpath).convert("RGBA"))
    rows = a.shape[0] // FH
    for d in range(4):
        xs = slice(choice * 4 * FW + d * FW, choice * 4 * FW + (d + 1) * FW)
        stand = stands[:, d * FW:(d + 1) * FW]
        pts = pattern(TOP, d)
        for r in range(rows):
            cell = a[r * FH:(r + 1) * FH, xs]
            mcell = m[r * FH:(r + 1) * FH, xs]
            dx, dy = offset(stand, cell)
            paint(cell, mcell, pts, dx, dy)
    Image.fromarray(a).save(path); Image.fromarray(m).save(mpath)


for folder in ("art/player", "art/player/body2"):
    stands = do_walk(folder, "tops", 9, TOP)
    do_walk(folder, "bottoms", 8, BOTTOM)
    do_action(folder, 9, stands)
    print(folder, "circuit suit painted")
