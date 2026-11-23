"""Benches with solid backs (23 Nov).

Usage: python3 -I tools/solid_bench_backs.py [GAME_DIR]

The slatted benches (bench_n, bench_s) had see-through gaps between their slats, so someone sitting
behind a bench showed through in stripes. Each gap (a run of empty pixels at most 3 tall with slats
above and below, inside the bench's outline) is filled with a darkened copy of the slat above it.
The tall space under the seat stays open.
"""
import os, sys
import numpy as np
from PIL import Image

GAME = sys.argv[1] if len(sys.argv) > 1 else "."
MAX_GAP = 3
for name in ("bench_n", "bench_s"):
    path = os.path.join(GAME, "art", "lunar", name + ".png")
    a = np.array(Image.open(path).convert("RGBA"))
    op = a[..., 3] > 0
    H, W = op.shape
    out = a.copy()
    filled = 0
    for y in range(H):
        xs = np.nonzero(op[y])[0]
        if len(xs) < 2:
            continue
        for x in range(xs[0], xs[-1] + 1):
            if op[y, x]:
                continue
            above = [yy for yy in range(y - 1, max(-1, y - MAX_GAP - 1), -1) if op[yy, x]]
            below = [yy for yy in range(y + 1, min(H, y + MAX_GAP + 1)) if op[yy, x]]
            if above and below and below[0] - above[0] - 1 <= MAX_GAP:
                c = a[above[0], x].astype(int)
                out[y, x] = (c[0] * 55 // 100, c[1] * 55 // 100, c[2] * 55 // 100, 255)
                filled += 1
    Image.fromarray(out).save(path)
    print(name, "gaps filled:", filled)
