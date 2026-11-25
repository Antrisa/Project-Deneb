"""Stand-in art for the farm's water spigot (25 Nov 2026; Zachary: "the water spigot doesnt look like a water
spigot"): a steel standpipe with a red wheel tap and a brass spout over a drain grate, a puddle under it.
24 x 48 px, one tile wide and two tall like the other 1 x 2 props, in the props' style (dark plum outline,
light from the upper left). Writes art/lunar/water_spigot.png. Run from the repo root:
python3 -I tools/dev/water_spigot_art.py
"""
import os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
W, H = 24, 48
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
px = im.load()

OUT = (58, 32, 44, 255)          # outline, as the other props
STEEL = [(84, 88, 110, 255), (122, 128, 150, 255), (168, 174, 194, 255), (214, 218, 230, 255)]   # dark .. light
GRATE = [(52, 54, 66, 255), (78, 82, 98, 255), (104, 108, 126, 255)]
BRASS = [(150, 92, 40, 255), (214, 150, 62, 255), (246, 206, 120, 255)]
RED = [(122, 34, 36, 255), (196, 58, 46, 255), (238, 118, 88, 255)]
WATER = [(48, 112, 168, 200), (86, 160, 214, 220), (176, 226, 244, 235)]


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = c


def rect(x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(x, y, c)


# the puddle round the grate (drawn first, under everything)
for y in range(41, 47):
    half = [7, 10, 11, 11, 10, 7][y - 41]
    for x in range(12 - half, 12 + half):
        put(x, y, WATER[0] if y >= 45 or x in (12 - half, 12 + half - 1) else WATER[1])
put(5, 43, WATER[2]); put(6, 42, WATER[2]); put(17, 44, WATER[2])
# the drain grate: a square plate seen from above, slots across it
rect(5, 38, 18, 44, OUT)
rect(6, 39, 17, 43, GRATE[1])
rect(6, 39, 17, 39, GRATE[2])
for y in (40, 42):
    for x in range(7, 17):
        put(x, y, GRATE[0] if x % 2 else GRATE[1])
# the standpipe: a round steel post, lit on the left
rect(8, 10, 15, 39, OUT)
for y in range(11, 39):
    put(9, y, STEEL[2]); put(10, y, STEEL[3]); put(11, y, STEEL[2]); put(12, y, STEEL[1]); put(13, y, STEEL[1]); put(14, y, STEEL[0])
# a collar near the bottom and one under the tap
for cy in (34, 15):
    rect(7, cy, 16, cy + 2, OUT)
    rect(8, cy + 1, 15, cy + 1, STEEL[2]); put(9, cy + 1, STEEL[3]); put(15, cy + 1, STEEL[0])
# the cap on top
rect(7, 7, 16, 10, OUT)
rect(8, 8, 15, 9, STEEL[1]); rect(8, 8, 12, 8, STEEL[3])
# the red wheel tap on top: a spoked handwheel seen a little from above
for x in range(4, 20):
    put(x, 3, OUT); put(x, 6, OUT)
for y in range(3, 7):
    put(3, y, OUT); put(20, y, OUT)
rect(4, 4, 19, 5, RED[1]); rect(4, 4, 11, 4, RED[2]); rect(13, 5, 19, 5, RED[0])
rect(11, 2, 12, 7, OUT); put(11, 3, RED[2]); put(12, 3, RED[1])          # the stem through the wheel
put(7, 4, RED[0]); put(16, 5, RED[0])                                      # spokes
# the brass spout: out to the right from under the tap, bending down
rect(15, 17, 21, 21, OUT)
rect(16, 18, 20, 20, BRASS[1]); rect(16, 18, 20, 18, BRASS[2]); rect(16, 20, 20, 20, BRASS[0])
rect(18, 21, 21, 25, OUT)
rect(19, 21, 20, 24, BRASS[1]); put(19, 22, BRASS[2]); put(20, 24, BRASS[0])
# a drip falling from the spout, and one landing
put(19, 27, WATER[1]); put(19, 28, WATER[2])
put(19, 31, WATER[1])
im.save(os.path.join(ROOT, "art", "lunar", "water_spigot.png"))
print("art/lunar/water_spigot.png")
