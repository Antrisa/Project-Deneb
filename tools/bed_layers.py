"""Split each bed picture into the part in front of a sleeper: art/lunar/<bed>_blanket.png.

Usage: python3 -I tools/bed_layers.py [GAME_DIR]

Stardew-style beds: whoever is in bed stands under the covers. The game draws the whole bed behind
them (art/lunar/<bed>.png, unchanged) and this blanket layer in front: the covers from their top
edge down, the footboard and the legs. Same size as the bed picture, so the two line up; drawn
together over an empty bed they look exactly like the bed alone.
"""
import os, sys
import numpy as np
from PIL import Image

GAME = sys.argv[1] if len(sys.argv) > 1 else "."
# the first row of the covers (their dark top edge), counted from the top of the picture
BLANKET_TOP = {"bed": 33, "bed_double": 33, "bed_double_steel": 33}

for name, top in BLANKET_TOP.items():
    src = os.path.join(GAME, "art", "lunar", f"{name}.png")
    a = np.array(Image.open(src).convert("RGBA"))
    out = np.zeros_like(a)
    out[top:] = a[top:]
    Image.fromarray(out).save(os.path.join(GAME, "art", "lunar", f"{name}_blanket.png"))
    print(name, "blanket from row", top)
