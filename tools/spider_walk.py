"""The eight-limbed residents (Sesska, Tikka, Eshu) keep their own walks. The passing frames lift
the head a pixel (the row under the chin is doubled), and any limb tip that only touched its
limb at a corner is joined back on. The right-facing column is the left mirrored.
usage: spider_walk.py SRC_DIR OUT_DIR NAME"""
import sys, os
import numpy as np
from PIL import Image

FW, FH = 24, 48
CAST = {
    "sesska": dict(neck=21, join=[(2, 1, 42, 17, 42, 18)]),   # (row, col, y, x, copy y, copy x)
    "tikka": dict(neck=23, join=[]),
    "tally": dict(neck=23, join=[]),
}
src, out, name = sys.argv[1], sys.argv[2], sys.argv[3]
cfg = CAST[name]
a = np.array(Image.open(os.path.join(src, f"npc_{name}.png")).convert("RGBA"))
for row in (3, 4):                       # passing frames
    for col in (0, 1, 2):
        c = a[row * FH:(row + 1) * FH, col * FW:(col + 1) * FW]
        c[0:cfg["neck"]] = c[1:cfg["neck"] + 1].copy()
for (row, col, y, x, cy, cx) in cfg["join"]:
    c = a[row * FH:(row + 1) * FH, col * FW:(col + 1) * FW]
    c[y, x] = c[cy, cx]
a[:, 3 * FW:4 * FW] = np.concatenate([a[r * FH:(r + 1) * FH, 2 * FW:3 * FW][:, ::-1] for r in range(5)])
os.makedirs(out, exist_ok=True)
Image.fromarray(a).save(os.path.join(out, f"npc_{name}.png"))
print(name, "ok")
