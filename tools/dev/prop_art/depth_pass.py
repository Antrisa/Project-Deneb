"""Depth pass (23 Nov 2026): give an existing prop the warm "C" look without losing its hand-placed detail.
Zachary chose the "C" test (warm highlights, purple shadows, bevels): this applies the colour and light parts of it
to art that was drawn by hand.
  1. hue shift: light tones lean warm (toward yellow), dark tones lean purple; a little more saturation;
  2. a rim of light on top edges (a pixel whose pixel above is empty or outline);
  3. each face darkens toward its bottom and toward its right edge (runs of non-outline pixels);
  4. the outline becomes the warm dark of the C style.
Works per pixel and per run, so the frames of an animation strip stay in step.
    python3 depth_pass.py <in.png> <out.png> [--frames N]
"""
import sys, colorsys
import numpy as np
from PIL import Image

OUT = np.array([0x4a, 0x24, 0x30])


def lum(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


def shift(c, k_dark=0.0):
    """Hue-shift one colour: light -> warm, dark -> purple; more saturation; darken by k_dark (0..1)."""
    r, g, b = [v / 255.0 for v in c]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0.0, l * (1.0 - k_dark))
    target = 0.13 if l > 0.5 else 0.75          # yellow / purple
    pull = abs(l - 0.5) * 0.5 * (0.5 + s)      # stronger at the ends, weaker for greys
    dh = ((target - h + 0.5) % 1.0) - 0.5
    h = (h + dh * pull) % 1.0
    s = min(1.0, s * 1.25 + (0.07 if s > 0.05 else 0.04))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5))


def is_outline(c):
    return lum(c) < 0.2


def process(a):
    h, w = a.shape[:2]
    rgb = a[:, :, :3].astype(int)
    alpha = a[:, :, 3]
    solid = alpha > 0
    out = a.copy()
    line = np.zeros((h, w), bool)
    for y in range(h):
        for x in range(w):
            if solid[y, x] and is_outline(rgb[y, x]):
                # a dark pixel next to transparency is outline
                if any(not (0 <= x + dx < w and 0 <= y + dy < h) or not solid[y + dy, x + dx]
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    line[y, x] = True
    inner = solid & ~line
    # vertical runs: position within the face, top to bottom
    vpos = np.zeros((h, w)); hpos = np.zeros((h, w)); vlen = np.zeros((h, w)); hlen = np.zeros((h, w))
    for x in range(w):
        y = 0
        while y < h:
            if inner[y, x]:
                y0 = y
                while y < h and inner[y, x]: y += 1
                n = y - y0
                for k in range(n):
                    vpos[y0 + k, x] = k / max(1, n - 1); vlen[y0 + k, x] = n
            else:
                y += 1
    for y in range(h):
        x = 0
        while x < w:
            if inner[y, x]:
                x0 = x
                while x < w and inner[y, x]: x += 1
                n = x - x0
                for k in range(n):
                    hpos[y, x0 + k] = k / max(1, n - 1); hlen[y, x0 + k] = n
            else:
                x += 1
    for y in range(h):
        for x in range(w):
            if not solid[y, x]:
                continue
            c = tuple(rgb[y, x])
            if line[y, x]:
                out[y, x, :3] = OUT if lum(c) < 0.16 else shift(c, 0.0)
                continue
            k = 0.0
            if vlen[y, x] >= 6:
                k += max(0.0, vpos[y, x] - 0.45) * 0.42          # lower part of a face darker
            if hlen[y, x] >= 6 and hpos[y, x] > 0.84:
                k += 0.16                                          # right edge of a face
            col = shift(c, k)
            # rim light along top edges
            above = (y == 0) or (not solid[y - 1, x]) or line[y - 1, x]
            if above and lum(c) > 0.18:
                r, g, b = col
                col = (min(255, int(r * 1.18 + 30)), min(255, int(g * 1.15 + 24)), min(255, int(b * 1.02 + 10)))
            elif y >= 1 and line[y - 1, x] is False and y >= 2 and ((not solid[y - 2, x]) or line[y - 2, x]) and lum(c) > 0.3:
                pass
            if hlen[y, x] >= 6 and hpos[y, x] == 0 and lum(c) > 0.2 and not above:
                r, g, b = col
                col = (min(255, int(r * 1.08 + 8)), min(255, int(g * 1.07 + 6)), min(255, b + 2))
            out[y, x, :3] = col
    return out


def run(src, dst, frames=1):
    im = np.array(Image.open(src).convert("RGBA"))
    w = im.shape[1] // frames
    res = np.concatenate([process(im[:, i * w:(i + 1) * w]) for i in range(frames)], axis=1)
    Image.fromarray(res.astype(np.uint8), "RGBA").save(dst)


if __name__ == "__main__":
    f = 1
    if "--frames" in sys.argv:
        f = int(sys.argv[sys.argv.index("--frames") + 1])
    run(sys.argv[1], sys.argv[2], f)
