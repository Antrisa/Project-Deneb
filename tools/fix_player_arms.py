"""Two fixes to the player's arms (22 Nov), for every top on both bodies.

Usage: python3 -I tools/fix_player_arms.py [GAME_DIR]

- Walking away (up), the contact steps had the elbows bent and the hands behind the back. Those two
  rows of tops.png (and its mask) are now the standing frame's top, dropped a pixel with the body as
  on the residents' walk: arms at the sides, hands by the hips.
- Carrying, seen from the side, both arms were drawn up beside the head. Only the near arm shows
  now: the far one (behind the head) is taken out of action_tops.png's carry rows (0-4) above the
  shoulders, so the hair shows there. The right column stays the mirror of the left.
"""
import os, sys
import numpy as np
from PIL import Image

GAME = sys.argv[1] if len(sys.argv) > 1 else "."
FW, FH, ROWS, CHOICES = 24, 48, 5, 10
BACK, LEFT, RIGHT = 1, 2, 3
CARRY_ROWS = range(5)


def walk_back(folder):
    for name in ("tops.png", "tops_mask.png"):
        path = os.path.join(GAME, folder, name)
        a = np.array(Image.open(path).convert("RGBA"))
        for c in range(CHOICES):
            y0 = c * ROWS * FH
            stand = a[y0:y0 + FH, BACK * FW:(BACK + 1) * FW]
            dropped = np.zeros_like(stand)
            dropped[1:] = stand[:-1]
            for r in (1, 2):                      # contact A and B
                a[y0 + r * FH:y0 + (r + 1) * FH, BACK * FW:(BACK + 1) * FW] = dropped
        Image.fromarray(a).save(path)


def carry_side(folder):
    art_path = os.path.join(GAME, folder, "action_tops.png")
    mask_path = os.path.join(GAME, folder, "action_tops_mask.png")
    art = np.array(Image.open(art_path).convert("RGBA"))
    mask = np.array(Image.open(mask_path).convert("RGBA"))
    for c in range(CHOICES):
        x0 = c * 4 * FW
        for r in CARRY_ROWS:
            ys = slice(r * FH, (r + 1) * FH)
            cell = art[ys, x0 + LEFT * FW:x0 + (LEFT + 1) * FW]
            mcell = mask[ys, x0 + LEFT * FW:x0 + (LEFT + 1) * FW]
            # the shoulders: the first row where the top runs across the middle
            joined = next(y for y in range(FH) if cell[y, 11, 3] and cell[y, 12, 3])
            cell[:joined, 12:] = 0
            mcell[:joined, 12:] = 0
            art[ys, x0 + RIGHT * FW:x0 + (RIGHT + 1) * FW] = cell[:, ::-1]
            mask[ys, x0 + RIGHT * FW:x0 + (RIGHT + 1) * FW] = mcell[:, ::-1]
    Image.fromarray(art).save(art_path)
    Image.fromarray(mask).save(mask_path)


for folder in ("art/player", "art/player/body2"):
    walk_back(folder)
    carry_side(folder)
    print(folder, "arms done")
