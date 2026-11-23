import sys
import numpy as np
from PIL import Image
src, out, still = sys.argv[1], sys.argv[2], sys.argv[3]
a = Image.open(src).convert("RGBA")
S = 8; BG = (150, 170, 150, 255)
frames = []
for r in (1, 3, 2, 4):
    f = Image.new("RGBA", (4 * 24 * S + 3 * 16, 48 * S), BG)
    for c in range(4):
        cell = a.crop((c * 24, r * 48, c * 24 + 24, r * 48 + 48)).resize((24 * S, 48 * S), Image.NEAREST)
        f.alpha_composite(cell, (c * (24 * S + 16), 0))
    frames.append(f.convert("RGB"))
frames[0].save(out, save_all=True, append_images=frames[1:], duration=150, loop=0)
# still: front and back, all five rows
s = Image.new("RGBA", (5 * (24 * S + 8), 2 * (48 * S + 8)), BG)
for c in range(2):
    for r in range(5):
        cell = a.crop((c * 24, r * 48, c * 24 + 24, r * 48 + 48)).resize((24 * S, 48 * S), Image.NEAREST)
        s.alpha_composite(cell, (r * (24 * S + 8), c * (48 * S + 8)))
s.convert("RGB").save(still)
