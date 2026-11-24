"""The circuit suit (24 Nov): glowing circuit traces on top 9 ("Circuit suit") and bottom 8 ("Tech leggings").

Usage: python3 -I tools/circuit_suit.py [GAME_DIR]

Zachary's favourite outfit from the earlier player art was the dark suit with glowing cyan circuitry. The current
art's "Circuit suit" top had lost it, so this paints the traces back on: a seam line down the middle with a glowing
node on the chest, branches round the ribs, and lines down the sleeves; the leggings get a line down each leg with
nodes at the knees. The traces are drawn on the standing frame of each facing and carried to every walk and action
frame by matching the frame to the standing one (so they move with the body), only onto the cloth (never the
outline, never skin). Their mask is cleared, so they keep their own glow whatever colour the suit is dyed.
"""
import os, sys
import numpy as np
from PIL import Image

GAME = sys.argv[1] if len(sys.argv) > 1 else "."
FW, FH = 24, 48
LINE = (54, 198, 232, 255)
NODE = (150, 246, 255, 255)

# Traces on the standing frame, facing down / up / left (right is left mirrored): (x, y, colour)
def trace(points, colour=LINE):
    return [(x, y, colour) for x, y in points]

def run(x0, y0, x1, y1):
    pts = []
    x, y = x0, y0
    pts.append((x, y))
    while (x, y) != (x1, y1):
        if x != x1:
            x += 1 if x1 > x else -1
        elif y != y1:
            y += 1 if y1 > y else -1
        pts.append((x, y))
    return pts

TOP = {
    0: trace(run(11, 23, 11, 31) + run(10, 27, 7, 27) + run(7, 28, 7, 30) + run(12, 27, 16, 27) + run(16, 28, 16, 30)
             + run(5, 26, 5, 31) + run(18, 26, 18, 31))
       + trace([(11, 25), (12, 25), (11, 26), (12, 26)], NODE),
    1: trace(run(11, 22, 11, 31) + run(10, 25, 8, 25) + run(8, 26, 8, 29) + run(12, 25, 15, 25) + run(15, 26, 15, 29)
             + run(5, 26, 5, 31) + run(18, 26, 18, 30))
       + trace([(11, 27), (11, 28)], NODE),
    2: trace(run(12, 23, 12, 31) + run(11, 28, 9, 28) + run(9, 29, 9, 31))
       + trace([(12, 25), (12, 26)], NODE),
}
BOTTOM = {
    0: trace(run(8, 34, 8, 40) + run(15, 34, 15, 40)) + trace([(8, 37), (15, 37)], NODE),
    1: trace(run(8, 34, 8, 40) + run(15, 34, 15, 40)) + trace([(8, 37), (15, 37)], NODE),
    2: trace(run(12, 34, 12, 40)) + trace([(12, 37)], NODE),
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
