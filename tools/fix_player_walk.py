"""The player's walk toward and away from the camera, redrawn in the residents' style (22 Nov).

Usage: python3 -I tools/fix_player_walk.py [GAME_DIR]

The old down and up walk frames swayed the head and body from side to side, twisted the jacket,
and swung the hands out sideways at the waist, so walking up or down looked glitchy. Each of those
four frames (rows 1-4 of the down and up columns) is now built from the standing frame (row 0),
the way the residents' walks are:

- contact steps (rows 1 and 2): everything above the shins drops a pixel; one foot lifts a pixel.
- passing steps (rows 3 and 4): everything above the shins rises a pixel; the same foot lifts two.

Rows 1 and 3 lift the screen-right foot walking down and the screen-left foot walking up; rows 2
and 4 the other one. Every layer (bottoms, faces, tops, hair) and its mask gets the same change,
for every choice on both bodies. The carry rows 1-4 of action_tops.png, which are drawn over these
walk frames, become carry row 0 moved up or down by the same pixel.
"""
import os, sys
import numpy as np
from PIL import Image

GAME = sys.argv[1] if len(sys.argv) > 1 else "."
FW, FH, ROWS, CHOICES = 24, 48, 5, 10
DIRS = (0, 1)                      # down, up
SHIN = 40                          # rows from here down stay put (the feet stand on the floor)
SPLIT = 12                         # x below this is the screen-left leg
BOB = {1: 1, 2: 1, 3: -1, 4: -1}   # contact steps drop, passing steps rise
LIFT = {1: 1, 2: 1, 3: 2, 4: 2}


def shifted(cell, dy):
    out = np.zeros_like(cell)
    if dy > 0:
        out[dy:] = cell[:-dy]
    elif dy < 0:
        out[:dy] = cell[-dy:]
    else:
        out[:] = cell
    return out


def step(stand, row, d, legs):
    dy = BOB[row]
    out = shifted(stand, dy)
    if not legs:
        return out
    out[SHIN:] = stand[SHIN:]
    right = (row in (1, 3)) == (d == 0)
    xs = slice(SPLIT, FW) if right else slice(0, SPLIT)
    lift = LIFT[row]
    side = out[SHIN - lift:, xs].copy()
    out[SHIN - lift:, xs] = 0
    out[SHIN - lift:FH - lift, xs] = side[lift:]
    return out


def walk(folder):
    for name in ("bottoms", "faces", "tops", "hair"):
        for suffix in ("", "_mask"):
            path = os.path.join(GAME, folder, name + suffix + ".png")
            a = np.array(Image.open(path).convert("RGBA"))
            for c in range(CHOICES):
                y0 = c * ROWS * FH
                for d in DIRS:
                    xs = slice(d * FW, (d + 1) * FW)
                    stand = a[y0:y0 + FH, xs].copy()
                    for row in range(1, ROWS):
                        a[y0 + row * FH:y0 + (row + 1) * FH, xs] = step(stand, row, d, name == "bottoms")
            Image.fromarray(a).save(path)


def carry(folder):
    for suffix in ("", "_mask"):
        path = os.path.join(GAME, folder, "action_tops" + suffix + ".png")
        a = np.array(Image.open(path).convert("RGBA"))
        for c in range(CHOICES):
            for d in DIRS:
                xs = slice(c * 4 * FW + d * FW, c * 4 * FW + (d + 1) * FW)
                held = a[0:FH, xs].copy()
                for row in range(1, 5):
                    a[row * FH:(row + 1) * FH, xs] = shifted(held, BOB[row])
        Image.fromarray(a).save(path)


for folder in ("art/player", "art/player/body2"):
    walk(folder)
    carry(folder)
    print(folder, "walk redone")
