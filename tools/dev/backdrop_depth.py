"""Push the battle backdrops back behind the ships (24 Nov 2026; Zachary picked option C of
backdrop_depth_options.png): less colour, less contrast, darker, faded toward the deep navy of space, with a
little of the scope's grey-green. Reads art/ships/backdrops/<name>.png (the pack's originals, kept as they are)
and writes art/ships/backdrops/far/<name>.png, which the battle uses. The scope's grid dots and dark edges are
drawn by ui/ship_screen.gd backdrop(). Run from the repo root: python3 -I tools/dev/backdrop_depth.py
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "art", "ships", "backdrops")
OUT = os.path.join(SRC, "far")

COLOUR_KEPT = 0.55                        # how much colour stays (the rest goes grey)
CONTRAST = 0.62                           # how far each pixel stays from the haze
DARKER = 0.80
HAZE = np.array([0.06, 0.08, 0.13])       # the deep navy of space
SCOPE = np.array([0.24, 0.29, 0.27])      # the scope's grey-green
SCOPE_MIX = 0.15


def push_back(im):
    rgb = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    grey = rgb @ np.array([0.299, 0.587, 0.114])
    rgb = rgb * COLOUR_KEPT + grey[..., None] * (1.0 - COLOUR_KEPT)
    rgb = HAZE + (rgb - HAZE) * CONTRAST
    rgb *= DARKER
    rgb = rgb * (1.0 - SCOPE_MIX) + SCOPE * SCOPE_MIX
    return Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = sorted(n for n in os.listdir(SRC) if n.endswith(".png"))
    for n in names:
        push_back(Image.open(os.path.join(SRC, n))).save(os.path.join(OUT, n))
    print(len(names), "backdrops written to art/ships/backdrops/far/")
