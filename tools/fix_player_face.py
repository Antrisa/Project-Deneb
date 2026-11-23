"""Give the player's two bodies the residents' face (the character redo of 21-22 Nov).

Usage: python3 -I tools/fix_player_face.py [GAME_DIR]

art/player/faces.png and art/player/body2/faces.png hold the head and neck for every walk row
(4 directions across, 5 rows, 10 identical choices down) with a mask that recolours them in the
character screen (green = skin, blue = eyes). For each body:
- front: the little mouth is painted out (skin), and one blush pixel goes on each cheek, under
  the outer edge of each eye; the eyes (two wide, three tall, looking ahead) and brows stay
- side: the eye becomes two by two (its bottom row painted skin), the mouth at the edge of the
  profile is painted out, one blush pixel behind the eye
The blush is painted in the skin mask's "painted hue" mode (green, blue 64), so it is a pinker
shade of whatever skin colour is chosen. The head sways and bobs on the walk rows: each frame's
head is found against the standing frame and the same pixels are changed there. The right
column stays the mirror of the left.
"""
import os, sys
import numpy as np
from PIL import Image

GAME = sys.argv[1] if len(sys.argv) > 1 else "."
FW, FH, ROWS, CHOICES = 24, 48, 5, 10
SKIN_MASK = (0, 255, 64, 255)
BLUSH = (207, 163, 170, 255)        # times the skin colour / 185: a little redder than the skin

BODIES = {
    "art/player": dict(
        front=dict(skin=[((11, 18), (10, 18)), ((12, 18), (13, 18))], blush=[(8, 17), (15, 17)]),
        side=dict(skin=[((7, 16), (9, 16)), ((8, 16), (9, 16)), ((6, 18), (8, 18)), ((7, 18), (8, 18))],
                  blush=[(9, 17)])),
    "art/player/body2": dict(
        front=dict(skin=[((11, 17), (10, 17)), ((12, 17), (13, 17))], blush=[(8, 16), (15, 16)]),
        side=dict(skin=[((5, 15), (7, 15)), ((6, 15), (7, 15)), ((5, 17), (7, 17)), ((6, 17), (7, 17))],
                  blush=[(7, 16)])),
}


def offset(stand, frame):
    """How far the head moved from the standing frame (dx, dy)."""
    best = None
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            s = np.roll(np.roll(stand, dy, 0), dx, 1)
            d = int(np.abs(s[6:20].astype(int) - frame[6:20].astype(int)).sum())
            if best is None or d < best[0]:
                best = (d, dx, dy)
    return best[1], best[2]


def fix(folder):
    cfg = BODIES[folder]
    path = os.path.join(GAME, folder, "faces.png")
    mpath = os.path.join(GAME, folder, "faces_mask.png")
    art = np.array(Image.open(path).convert("RGBA"))
    mask = np.array(Image.open(mpath).convert("RGBA"))
    src_art, src_mask = art.copy(), mask.copy()
    for c in range(CHOICES):
        for col, view in ((0, "front"), (2, "side")):
            y0 = c * ROWS * FH
            stand = src_art[y0:y0 + FH, col * FW:(col + 1) * FW]
            for r in range(ROWS):
                ry = y0 + r * FH
                frame = src_art[ry:ry + FH, col * FW:(col + 1) * FW]
                dx, dy = offset(stand, frame)
                X = lambda x: col * FW + x + dx
                Y = lambda y: ry + y + dy
                # every pixel changed (and every skin pixel copied) is the same as in the standing frame
                for (x, y) in [p for pair in cfg[view]["skin"] for p in pair] + cfg[view]["blush"]:
                    assert (src_art[Y(y), X(x)] == stand[y, x]).all(), (folder, c, r, view, x, y)
                for (x, y), (sx, sy) in cfg[view]["skin"]:
                    art[Y(y), X(x)] = src_art[Y(sy), X(sx)]
                    mask[Y(y), X(x)] = src_mask[Y(sy), X(sx)]
                for (x, y) in cfg[view]["blush"]:
                    art[Y(y), X(x)] = BLUSH
                    mask[Y(y), X(x)] = SKIN_MASK
        # the right column is the left mirrored
        for r in range(ROWS):
            ry = c * ROWS * FH + r * FH
            art[ry:ry + FH, 3 * FW:4 * FW] = art[ry:ry + FH, 2 * FW:3 * FW][:, ::-1]
            mask[ry:ry + FH, 3 * FW:4 * FW] = mask[ry:ry + FH, 2 * FW:3 * FW][:, ::-1]
    Image.fromarray(art).save(path)
    Image.fromarray(mask).save(mpath)
    print(folder, "faces done")


for folder in BODIES:
    fix(folder)
