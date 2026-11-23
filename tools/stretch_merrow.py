"""Make Merrow taller by repeating rows of her overalls in every cell, feet fixed.

Usage: python3 -I stretch_merrow.py WALK_IN WALK_OUT ACT_IN ACT_OUT

Each listed row (counted up from the cell's lowest pixel) is drawn twice, so everything above
it rises one pixel per repeat. The repeated rows run through her chest, waist and the top of
her overall legs, below the head and above the boots.
"""
import sys
import numpy as np
from PIL import Image

FROM_SOLE = [15, 12, 9, 7]   # sole row 45: rows 30, 33, 36 and 38


def stretch(cell):
    ys = np.where(cell[:, :, 3].max(1) > 0)[0]
    if not len(ys):
        return cell
    sole = int(ys.max())
    dup = {sole - d for d in FROM_SOLE}
    rows = []
    for y in range(cell.shape[0]):
        rows.append(cell[y])
        if y in dup:
            rows.append(cell[y])
    rows = rows[len(dup):]          # drop from the top: feet stay where they were
    return np.array(rows)


def run(src, dst, cw):
    a = np.array(Image.open(src).convert("RGBA"))
    for r in range(a.shape[0] // 48):
        for c in range(a.shape[1] // cw):
            a[r * 48:(r + 1) * 48, c * cw:(c + 1) * cw] = stretch(a[r * 48:(r + 1) * 48, c * cw:(c + 1) * cw].copy())
    Image.fromarray(a).save(dst)


run(sys.argv[1], sys.argv[2], 24)
run(sys.argv[3], sys.argv[4], 36)
