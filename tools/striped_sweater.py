"""Top 4 becomes the "Striped sweater" (24 Nov), replacing the Space tunic.

The tunic's pale sash and flared hem made the wearer look bent forward from the side. The sweater takes the
Workshirt's cut (top 8: long sleeves, the same arms in every walk and action frame), smooths away its placket,
buttons and pocket (a 3x3 median over the cloth), and paints even horizontal stripes across body and sleeves:
every other pair of rows a shade darker. The stripes are laid on the standing frame of each facing and follow
the body's bob and lean in the other frames (the frame is matched to the standing one), so they move with it.
Only the dyed cloth changes (red mask); outline and skin stay as drawn, and the mask is the Workshirt's, so the
sweater takes the top colour like any other top.
Usage: python3 -I tools/striped_sweater.py   (from the game folder; run once)
"""
import numpy as np
from PIL import Image

FW, FH = 24, 48
SRC, DST = 8, 4
DARK = 0.72          # the darker stripe, as a share of the cloth's light
FIRST = 23           # the first stripe row on the standing frame (just under the collar)


def load(p):
    return np.array(Image.open(p).convert("RGBA"))


def offset(stand, cell):
    """The shift that best lays the standing frame's shape over this frame's (the body's bob and lean)."""
    a = stand[..., 3] > 0
    b = cell[..., 3] > 0
    best, at = None, (0, 0)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            sh = np.zeros_like(a)
            ys = slice(max(0, dy), FH + min(0, dy)); yd = slice(max(0, -dy), FH + min(0, -dy))
            xs = slice(max(0, dx), FW + min(0, dx)); xd = slice(max(0, -dx), FW + min(0, -dx))
            sh[ys, xs] = a[yd, xd]
            score = (sh & b).sum() - 0.5 * (sh ^ b).sum()
            if best is None or score > best:
                best, at = score, (dx, dy)
    return at


def restyle(cell, mcell, dy):
    """Smooth the cloth and stripe it; dy is how far this frame sits below the standing one."""
    cloth = (cell[..., 3] > 0) & (mcell[..., 3] > 0) & (mcell[..., 0] > 0)
    # the Workshirt's undyed buttons and pocket tab, set in the cloth, become cloth
    H, W = cloth.shape
    for y, x in zip(*np.nonzero((cell[..., 3] > 0) & (mcell[..., 3] == 0))):
        if 0 < y < H - 1 and 0 < x < W - 1 and sum(cloth[y + j, x + i] for j, i in ((0, 1), (0, -1), (1, 0), (-1, 0))) >= 3:
            nb = [cell[y + j, x + i] for j, i in ((0, 1), (0, -1), (1, 0), (-1, 0)) if cloth[y + j, x + i]]
            cell[y, x] = nb[0]
            mcell[y, x] = (255, 0, 64, 255)
    cloth = (cell[..., 3] > 0) & (mcell[..., 3] > 0) & (mcell[..., 0] > 0)
    src = cell.astype(float)
    out = cell.copy()
    for y, x in zip(*np.nonzero(cloth)):
        ys, xs = slice(max(0, y - 1), y + 2), slice(max(0, x - 1), x + 2)
        nb = src[ys, xs][cloth[ys, xs]][:, :3]
        lum = 0.2126 * nb[:, 0] + 0.7152 * nb[:, 1] + 0.0722 * nb[:, 2]
        pick = nb[np.argsort(lum)[len(lum) // 2]]
        row = y - dy - FIRST
        if row >= 0 and (row // 2) % 2 == 1:
            pick = pick * DARK
        out[y, x, :3] = np.clip(np.round(pick), 0, 255).astype(np.uint8)
    cell[:] = out


def walk():
    a = load("art/player/tops.png"); m = load("art/player/tops_mask.png")
    block = a.shape[0] // 10
    a[DST * block:(DST + 1) * block] = a[SRC * block:(SRC + 1) * block]
    m[DST * block:(DST + 1) * block] = m[SRC * block:(SRC + 1) * block]
    y0 = DST * block
    stands = a[y0:y0 + FH].copy()
    for d in range(4):
        xs = slice(d * FW, (d + 1) * FW)
        for r in range(block // FH):
            cell = a[y0 + r * FH:y0 + (r + 1) * FH, xs]
            _, dy = offset(stands[:, xs], cell)
            restyle(cell, m[y0 + r * FH:y0 + (r + 1) * FH, xs], dy)
    Image.fromarray(a).save("art/player/tops.png"); Image.fromarray(m).save("art/player/tops_mask.png")
    return stands


def action(stands):
    a = load("art/player/action_tops.png"); m = load("art/player/action_tops_mask.png")
    w = 4 * FW
    a[:, DST * w:(DST + 1) * w] = a[:, SRC * w:(SRC + 1) * w]
    m[:, DST * w:(DST + 1) * w] = m[:, SRC * w:(SRC + 1) * w]
    for d in range(4):
        xs = slice(DST * w + d * FW, DST * w + (d + 1) * FW)
        for r in range(a.shape[0] // FH):
            cell = a[r * FH:(r + 1) * FH, xs]
            _, dy = offset(stands[:, d * FW:(d + 1) * FW], cell)
            restyle(cell, m[r * FH:(r + 1) * FH, xs], dy)
    Image.fromarray(a).save("art/player/action_tops.png"); Image.fromarray(m).save("art/player/action_tops_mask.png")
    # the watering forearm stencil is per top: the sweater's arms are the Workshirt's
    wm = load("art/player/watering_arm_mask.png")
    wm[:, DST * w:(DST + 1) * w] = wm[:, SRC * w:(SRC + 1) * w]
    Image.fromarray(wm).save("art/player/watering_arm_mask.png")


action(walk())
print("striped sweater: top", DST)
