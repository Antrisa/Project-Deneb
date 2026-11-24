"""Close the one-pixel gaps between the player's hair and head (24 Nov).

Some hairstyles leave a transparent pixel or two between a lock of hair and the cheek, temple or neck,
so the floor shows through. For every hairstyle, cell and top, a transparent pixel next to the hair is
filled when it is
  * enclosed by the character (face + hair + top), or
  * pinched between the face and the hair (face on one side, hair on the opposite side).
The fill copies the darkest neighbouring hair pixel (art and mask), so it reads as the hair's outline.

Runs on the walk sheets (art/player, art/player/body2) and the eating sheets (player_eating/body_1, body_2).
Usage: python3 tools/fix_hair_gaps.py [--dry]
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

STYLES = 10
DRY = "--dry" in sys.argv


def load(p):
    return np.array(Image.open(p).convert("RGBA"))


def fix(folder, cw, ch, cols, rows_per_style, tops_name="tops"):
    hair = load(f"{folder}/hair.png"); hmask = load(f"{folder}/hair_mask.png")
    faces = load(f"{folder}/faces.png")[..., 3] > 0
    tops = load(f"{folder}/{tops_name}.png")[..., 3] > 0
    style_h = ch * rows_per_style
    filled = 0
    for hs in range(STYLES):
        for r in range(rows_per_style):
            for c in range(cols):
                y0 = hs * style_h + r * ch; x0 = c * cw
                sl = (slice(y0, y0 + ch), slice(x0, x0 + cw))
                h = hair[sl][..., 3] > 0
                f = faces[r * ch:(r + 1) * ch, x0:x0 + cw]          # every face slot is the same picture
                near = ndimage.binary_dilation(h)
                gaps = np.zeros_like(h)
                for t in range(STYLES):
                    tp = tops[t * style_h + r * ch:t * style_h + (r + 1) * ch, x0:x0 + cw]
                    body = h | f | tp
                    gaps |= ndimage.binary_fill_holes(body) & ~body & near
                # pinched between face and hair
                head = h | f
                for dy, dx in ((0, 1), (1, 0)):
                    a = np.roll(f, (dy, dx), (0, 1)); b = np.roll(h, (-dy, -dx), (0, 1))
                    a2 = np.roll(h, (dy, dx), (0, 1)); b2 = np.roll(f, (-dy, -dx), (0, 1))
                    gaps |= ~head & ((a & b) | (a2 & b2))
                ys, xs = np.nonzero(gaps)
                for y, x in zip(ys, xs):
                    best = None
                    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < ch and 0 <= xx < cw and h[yy, xx]:
                            px = hair[y0 + yy, x0 + xx]
                            lum = int(px[0]) + int(px[1]) + int(px[2])
                            if best is None or lum < best[0]:
                                best = (lum, yy, xx)
                    if best is None:
                        continue
                    _, yy, xx = best
                    hair[y0 + y, x0 + x] = hair[y0 + yy, x0 + xx]
                    hmask[y0 + y, x0 + x] = hmask[y0 + yy, x0 + xx]
                    filled += 1
    print(folder, "filled", filled)
    if not DRY:
        Image.fromarray(hair).save(f"{folder}/hair.png")
        Image.fromarray(hmask).save(f"{folder}/hair_mask.png")
    return filled


# a filled pixel can pinch the next one, so repeat until nothing changes
for folder, grid in (("art/player", (24, 48, 4, 5)), ("art/player/body2", (24, 48, 4, 5)),
                     ("player_eating/body_1", (48, 68, 4, 4)), ("player_eating/body_2", (48, 68, 4, 4))):
    while fix(folder, *grid) and not DRY:
        pass
