"""System and room icons, FTL-style (Claude, 21 Nov 2026). Zachary: "the room identity markings as another asset to put
on room like FTL", then "i like FTLs better ... make it closer to that": chunky solid shapes pixelled on a 16-px
grid with a dark outline, doubled, so they read like FTL's. The same icons mark rooms and sit under the power bars.

One sheet, art/ui/ship/icons_systems.png: 32 x 32 icons side by side (16 x 16 pixelled, doubled). White with a
dark outline so the game can tint them. Order (ShipBattle.ROOM_ICONS must match):
shields, engines, weapons, life, pilot, drones, cannon, medbay, crew, doors, sensors.

Run from the repo root:  python3 -I tools/dev/ship_art/icons2x.py .
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

OUTLINE = (38, 37, 53, 255)

ICONS = {
    "shields": """
....XXXXXX....
..XXXXXXXXXX..
.XX........XX.
.X..XXXXXX..X.
XX.XXXXXXXX.XX
X..XXX.......X
X..XXXXXXX...X
X...XXXXXXX..X
X.......XXX..X
XX.XXXXXXXX.XX
.X..XXXXXX..X.
.XX........XX.
..XXXXXXXXXX..
....XXXXXX....
""",
    "engines": """
.....XXXXXXXX.
....XXXXXXXXX.
XX.XXXXXXXXXX.
XX.XXX..XXXXXX
XX.XXX..XXXXXX
XX.XXX..XXXXXX
XX.XXX..XXXXXX
XX.XXX..XXXXXX
XX.XXX..XXXXXX
XX.XXXXXXXXXX.
....XXXXXXXXX.
.....XXXXXXXX.
""",
    "weapons": """
.XXX..........
.XXXX.........
..XXX.........
..XXXXXXXX.X..
XXXXXXXXXX.XX.
XXXXXXXXXX.XXX
XXXXXXXXXX.XX.
..XXXXXXXX.X..
..XXX.........
.XXXX.........
.XXX..........
""",
    "life": """
.XXXXX........
XXXXXXX.......
XX...XX.......
XX...XX.......
XX...XX.......
XX...XX.XXXX..
XX...XX....XX.
XXXXXXX...XX..
.XXXXX...XX...
........XX....
........XXXXX.
""",
    "pilot": """
..XXXX........
..XXXX........
..XXXX........
..XXXX........
..XXXX...XXX..
..XXXXXXXXXX..
..XXXXXXXXXX..
..XXXXXXXXXX..
......XX......
......XX......
...XXXXXXXX...
...XXXXXXXX...
""",
    "drones": """
XXX........XXX
XXXX......XXXX
XXXXX....XXXXX
.XXXXXXXXXXXX.
..XXX....XXX..
...XX.XX.XX...
...XX.XX.XX...
..XXX....XXX..
.XXXXXXXXXXXX.
XXXXX....XXXXX
XXXX......XXXX
XXX........XXX
""",
    "cannon": """
.X..X.........
..XX..........
.XXXX.........
..XX..........
.X..X.........
XXXXXX........
XXXXXXXXXXXXXX
XXXXXXXXXXXXXX
XXXXXX.X.X.XXX
XXXXXXXXXXXXXX
XXXXXXXXXXXXXX
XXXXXX........
""",
    "medbay": """
.....XXXX.....
.....XXXX.....
.....XXXX.....
.....XXXX.....
XXXXXXXXXXXXXX
XXXXXXXXXXXXXX
XXXXXXXXXXXXXX
XXXXXXXXXXXXXX
.....XXXX.....
.....XXXX.....
.....XXXX.....
.....XXXX.....
""",
    "crew": """
.....XXXX.....
....XXXXXX....
....XXXXXX....
....XXXXXX....
.....XXXX.....
..............
...XXXXXXXX...
..XXXXXXXXXX..
.XXXXXXXXXXXX.
.XXXXXXXXXXXX.
.XXXXXXXXXXXX.
""",
    "doors": """
.XXXXX..XXXXX.
.XXXXX..XXXXX.
.XXXXX..XXXXX.
.XXXXX..XXXXX.
.XXX.X..X.XXX.
.XXX.X..X.XXX.
.XXXXX..XXXXX.
.XXXXX..XXXXX.
.XXXXX..XXXXX.
.XXXXX..XXXXX.
.XXXXX..XXXXX.
""",
    "sensors": """
.....XXXX.....
...XXXXXXXX...
.XXXX....XXXX.
XXX..XXXX..XXX
XX..XXXXXX..XX
XX..XXXXXX..XX
XXX..XXXX..XXX
.XXXX....XXXX.
...XXXXXXXX...
.....XXXX.....
""",
}
ORDER = list(ICONS)


def icon(name):
    rows = ICONS[name].strip("\n").split("\n")
    m = np.zeros((16, 16), bool)
    top = (16 - len(rows)) // 2
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "X":
                m[top + j, 1 + i] = True
    ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & ~m
    a = np.zeros((16, 16, 4), np.uint8)
    a[m] = (255, 255, 255, 255)
    a[ring] = OUTLINE
    return Image.fromarray(a, "RGBA").resize((32, 32), Image.NEAREST)


def sheet():
    out = Image.new("RGBA", (32 * len(ORDER), 32), (0, 0, 0, 0))
    for i, name in enumerate(ORDER):
        out.alpha_composite(icon(name), (i * 32, 0))
    return out


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    (root / "art/ui/ship").mkdir(parents=True, exist_ok=True)
    sheet().save(root / "art/ui/ship/icons_systems.png")
    print("ok", ORDER)
