#!/usr/bin/env python3
"""Makes placeholder layers for the player, at the same build as the residents.

    python3 tools/make_player_layers.py <project folder> [preview.png]

Writes art/player/{bottoms,tops,faces,hair}.png and their _mask.png files:
4 directions across (down, up, left, right), 10 choices down, 32x64 cells.
In a mask: red = the layer's main colour, green = skin, blue = eyes. Pixels with no mask keep their own colour.

This is NOT run by tools/build.py, so art you draw over these files is never overwritten.
Needs Pillow (pip install pillow).

Where the body sits in a 32x64 cell (front view):
    hair top  y 6-8        head  x 8-23, y 10-26      eyes  y 17-19
    neck      y 26-30      torso x 9-22, y 28-45      arms  x 6-8 and x 23-25, hands y 43-45
    legs      x 9-14 and x 17-22, y 42-54             boots y 55-62
When walking the game lifts rows 54-63 of the bottoms (the feet) and moves the other layers up 1.
"""
import sys
from PIL import Image

# What a pixel is made of: P = the layer's main colour, S = skin, E = eye colour, or a fixed (r, g, b).
P, S, E = "P", "S", "E"
GREY = {P: 140, S: 185, E: 150}          # the grey that comes out as exactly the chosen colour
MASK = {P: (255, 0, 0, 255), S: (0, 255, 0, 255), E: (0, 0, 255, 255)}
SHADE = [0.42, 0.74, 1.0, 1.18]          # outline, shadow, plain, highlight
BOOT = (124, 82, 52)
WHITE = (236, 238, 244)
LASH = (40, 30, 44)
METAL = (150, 158, 172)
CYAN = (110, 230, 240)


class Cell:
    """One 32x64 picture being drawn: {(x, y): (material, shade)}."""

    def __init__(self):
        self.px = {}

    def dot(self, x, y, mat, sh=2):
        if 0 <= x < 32 and 0 <= y < 64:
            self.px[(x, y)] = (mat, sh)

    def rect(self, x0, y0, x1, y1, mat, sh=2):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.dot(x, y, mat, sh)

    def oval(self, x0, y0, x1, y1, mat, sh=2, keep=None):
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        rx, ry = (x1 - x0 + 1) / 2.0, (y1 - y0 + 1) / 2.0
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0 and (keep is None or keep(x, y)):
                    self.dot(x, y, mat, sh)

    def clear(self, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px.pop((x, y), None)

    def shade(self, x0, y0, x1, y1, sh):
        """Changes the shade of what is already there."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if (x, y) in self.px:
                    self.px[(x, y)] = (self.px[(x, y)][0], sh)

    def outline(self, skip_bottom_from=99):
        """Darkens the pixels on the edge of the shape."""
        edge = [k for k in self.px
                if any((k[0] + dx, k[1] + dy) not in self.px for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for k in edge:
            if k[1] < skip_bottom_from:
                self.px[k] = (self.px[k][0], 0)

    def mirrored(self):
        c = Cell()
        c.px = {(31 - x, y): v for (x, y), v in self.px.items()}
        return c

    def paste(self, art, mask, ox, oy):
        for (x, y), (mat, sh) in self.px.items():
            f = SHADE[sh]
            if mat in GREY:
                g = min(255, int(round(GREY[mat] * f)))
                art.putpixel((ox + x, oy + y), (g, g, g, 255))
                mask.putpixel((ox + x, oy + y), MASK[mat])
            else:
                art.putpixel((ox + x, oy + y), tuple(min(255, int(round(v * f))) for v in mat) + (255,))


# ---------------------------------------------------------------- bottoms
# d: 0 = facing down, 1 = facing up, 2 = facing left (right is the mirror of left)

BOTTOMS = [  # name, where the cloth ends, narrow legs, skirt, top of boot, detail
    ("Work pants", 54, False, False, 55, ""),
    ("Cargo pants", 54, False, False, 55, "pockets"),
    ("Flight trousers", 54, False, False, 55, "stripe"),
    ("Fitted trousers", 54, True, False, 55, ""),
    ("Explorer shorts", 49, False, False, 56, ""),
    ("Utility skirt", 50, False, True, 56, "pockets"),
    ("Expedition pants", 51, False, False, 52, ""),
    ("Mechanic trousers", 54, False, False, 55, "knees"),
    ("Tech leggings", 54, True, False, 55, "lines"),
    ("Cuffed trousers", 54, False, False, 55, "cuffs"),
]


def bottoms(v, d):
    name, end, narrow, skirt, boot_top, detail = BOTTOMS[v]
    c = Cell()
    n = 1 if narrow else 0
    if d < 2:
        legs = [(9 + n, 14 - n), (17 + n, 22 - n)]
        for (x0, x1) in legs:                       # bare legs first, cloth goes over them
            c.rect(x0, 46, x1, 55, S)
            c.shade(x1, 46, x1, 55, 1)
        c.rect(9, 42, 22, 47, P)                    # hips
        if skirt:
            c.rect(8, 44, 23, end, P)
            c.shade(8, end, 23, end, 1)
        else:
            for (x0, x1) in legs:
                c.rect(x0, 46, x1, end, P)
                c.shade(x1, 46, x1, end, 1)         # shadow down one side of each leg
            c.rect(15, 48, 16, 55, P, 0)            # the dark gap between the legs
            c.clear(15, min(end, 54) + 1, 16, 55)
            if not narrow:
                c.clear(15, 54, 16, 55)
        c.rect(9, 42, 22, 43, P, 1)                 # waistband (hidden under most tops)
        if detail == "pockets":
            c.rect(9 + n, 48, 11, 51, P, 1); c.rect(20, 48, 22 - n, 51, P, 1)
        elif detail == "stripe":
            c.rect(9, 46, 9, end, P, 3); c.rect(22, 46, 22, end, P, 3)
        elif detail == "knees":
            c.rect(10, 50, 13, 52, P, 1); c.rect(18, 50, 21, 52, P, 1)
        elif detail == "lines":
            c.rect(11, 47, 11, end, CYAN); c.rect(20, 47, 20, end, CYAN)
        elif detail == "cuffs":
            c.rect(9, 53, 14, 54, P, 3); c.rect(17, 53, 22, 54, P, 3)
        for (x0, x1) in ((8, 14), (17, 23)):        # boots
            c.rect(x0, boot_top, x1, 62, BOOT)
            c.rect(x0, boot_top, x1, boot_top, BOOT, 3)
            c.rect(x0, 62, x1, 62, BOOT, 1)
        if d == 1:
            c.shade(9, 44, 22, 45, 1)
    else:
        c.rect(11 + n, 46, 20 - n, 55, S)
        c.rect(11, 42, 20, 47, P)
        if skirt:
            c.rect(10, 44, 21, end, P)
            c.shade(10, end, 21, end, 1)
        else:
            c.rect(11 + n, 46, 20 - n, end, P)
            c.shade(18 - n, 46, 20 - n, end, 1)     # the far leg, in shadow
        c.rect(11, 42, 20, 43, P, 1)
        if detail == "pockets":
            c.rect(13, 48, 16, 51, P, 1)
        elif detail == "stripe":
            c.rect(15, 46, 15, end, P, 3)
        elif detail == "knees":
            c.rect(11, 50, 14, 52, P, 1)
        elif detail == "lines":
            c.rect(14, 47, 14, end, CYAN)
        elif detail == "cuffs":
            c.rect(11, 53, 20, 54, P, 3)
        c.rect(11, boot_top, 20, 62, BOOT)          # boot, toe pointing left
        c.rect(9, 59, 20, 62, BOOT)
        c.rect(11, boot_top, 20, boot_top, BOOT, 3)
        c.rect(9, 62, 20, 62, BOOT, 1)
    c.outline()
    return c


# ---------------------------------------------------------------- tops

TOPS = [  # name, where the sleeve ends (28 = no sleeves, 42 = long), hem, detail
    ("Crew tee", 33, 45, ""),
    ("Utility vest", 28, 45, "vest"),
    ("Flight jacket", 42, 46, "jacket"),
    ("Mechanic coveralls", 42, 47, "bib"),
    ("Space tunic", 36, 49, "belt"),
    ("Hoodie", 42, 46, "hood"),
    ("Expedition coat", 42, 51, "fur"),
    ("Light armor", 42, 45, "armor"),
    ("Workshirt", 37, 46, "buttons"),
    ("Circuit suit", 42, 45, "circuit"),
]


def tops(v, d):
    name, sleeve, hem, detail = TOPS[v]
    c = Cell()
    if d < 2:
        for (x0, x1) in ((6, 8), (23, 25)):         # arms: skin, then the sleeve over it
            c.rect(x0, 29, x1, 45, S)
            if sleeve > 28:
                c.rect(x0, 29, x1, sleeve, P)
                c.rect(x0, sleeve, x1, sleeve, P, 1)
        c.rect(9, 28, 22, hem, P)                   # body
        c.rect(7, 28, 24, 30, P if sleeve > 28 else S)      # shoulders
        if sleeve == 28:
            c.rect(9, 28, 22, 30, P)
        c.shade(20, 31, 22, hem, 1)                 # shadow down one side
        c.shade(9, hem, 22, hem, 1)
        if d == 0:
            c.rect(14, 28, 17, 28, S)               # neckline
            if detail == "vest":
                c.rect(15, 29, 16, hem, P, 0); c.rect(10, 38, 13, 41, P, 1); c.rect(18, 38, 21, 41, P, 1)
            elif detail == "jacket":
                c.rect(15, 30, 16, hem, METAL); c.rect(11, 28, 13, 30, P, 3); c.rect(18, 28, 20, 30, P, 3)
                c.rect(9, hem - 1, 22, hem, P, 1)
            elif detail == "bib":
                c.rect(11, 29, 12, 34, P, 1); c.rect(19, 29, 20, 34, P, 1); c.rect(11, 34, 20, 40, P, 3)
                c.dot(11, 34, METAL); c.dot(20, 34, METAL)
            elif detail == "belt":
                c.rect(9, 42, 22, 43, BOOT); c.rect(15, 42, 16, 43, METAL)
            elif detail == "hood":
                c.rect(11, 27, 13, 30, P, 1); c.rect(18, 27, 20, 30, P, 1); c.rect(11, 39, 20, 43, P, 1)
                c.dot(14, 31, WHITE); c.dot(17, 31, WHITE); c.dot(14, 33, WHITE); c.dot(17, 33, WHITE)
            elif detail == "fur":
                c.rect(10, 27, 13, 30, WHITE); c.rect(18, 27, 21, 30, WHITE); c.rect(15, 31, 16, hem, P, 0)
            elif detail == "armor":
                c.rect(11, 30, 20, 38, METAL); c.rect(11, 38, 20, 38, METAL, 1); c.rect(15, 31, 16, 36, CYAN)
            elif detail == "buttons":
                c.rect(12, 28, 13, 30, P, 3); c.rect(18, 28, 19, 30, P, 3)
                for y in (32, 36, 40, 44):
                    c.dot(15, y, WHITE)
                c.rect(18, 34, 21, 37, P, 1)
            elif detail == "circuit":
                c.rect(12, 31, 12, 40, CYAN); c.rect(12, 40, 19, 40, CYAN); c.rect(19, 34, 19, 40, CYAN)
                c.dot(19, 33, WHITE)
        else:
            if detail == "hood":
                c.rect(10, 26, 21, 34, P, 1); c.rect(11, 27, 20, 33, P)
            elif detail == "fur":
                c.rect(10, 27, 21, 30, WHITE)
            elif detail == "armor":
                c.rect(11, 30, 20, 38, METAL); c.rect(11, 38, 20, 38, METAL, 1)
            elif detail == "belt":
                c.rect(9, 42, 22, 43, BOOT)
            elif detail == "bib":
                c.rect(11, 29, 12, 36, P, 1); c.rect(19, 29, 20, 36, P, 1)
            elif detail == "circuit":
                c.rect(15, 30, 16, 42, CYAN)
        if detail == "armor":
            c.rect(5, 27, 9, 32, METAL); c.rect(22, 27, 26, 32, METAL)
            c.rect(5, 32, 9, 32, METAL, 1); c.rect(22, 32, 26, 32, METAL, 1)
        if detail == "circuit":
            c.rect(6, 41, 8, 41, CYAN); c.rect(23, 41, 25, 41, CYAN)
        c.outline(skip_bottom_from=99)
        for (x0, x1) in ((6, 8), (23, 25)):         # hands stay skin-coloured, with a dark edge
            c.rect(x0, 43, x1, 45, S)
            c.rect(x0, 45, x1, 45, S, 1)
        c.rect(9, 31, 9, min(hem, 42), P, 0)        # the line between arm and body
        c.rect(22, 31, 22, min(hem, 42), P, 0)
    else:
        c.rect(11, 28, 20, hem, P)
        c.shade(18, 30, 20, hem, 1)
        c.shade(11, hem, 20, hem, 1)
        if detail == "hood":
            c.rect(18, 26, 22, 33, P, 1)
        elif detail == "fur":
            c.rect(11, 27, 20, 30, WHITE)
        elif detail == "belt":
            c.rect(11, 42, 20, 43, BOOT)
        elif detail == "armor":
            c.rect(11, 31, 13, 38, METAL)
        elif detail == "jacket":
            c.rect(11, hem - 1, 20, hem, P, 1)
        c.outline()
        c.rect(12, 30, 18, 43, P, 0)                # arm, drawn over the body with a dark edge
        c.rect(13, 30, 17, 45, S)
        if sleeve > 28:
            c.rect(13, 30, 17, sleeve, P)
            c.rect(13, sleeve, 17, sleeve, P, 1)
        else:
            c.rect(13, 29, 17, 30, P)
        if detail == "armor":
            c.rect(12, 27, 18, 32, METAL); c.rect(12, 32, 18, 32, METAL, 1)
        if detail == "circuit":
            c.rect(13, 41, 17, 41, CYAN); c.rect(15, 31, 15, 40, CYAN)
        c.rect(13, 45, 17, 45, S, 1)
        c.rect(12, 43, 12, 45, S, 0); c.rect(18, 43, 18, 45, S, 0)
    return c


# ---------------------------------------------------------------- faces

FACES = ["Soft oval", "Square", "Freckled", "Angular", "Heart-shaped", "High cheekbones", "Rounded", "Mature",
         "Strong chin", "Cheek scar"]
SCAR = (168, 84, 74)


def faces(v, d):
    name = FACES[v]
    c = Cell()
    if d < 2:
        c.rect(13, 25, 18, 30, S, 1)                # neck, in the chin's shadow
        if name == "Rounded":
            c.oval(7, 10, 24, 26, S)
        else:
            c.oval(8, 10, 23, 26, S)
        if name == "Square":
            c.rect(9, 19, 22, 25, S); c.rect(10, 26, 21, 26, S)
        elif name == "Strong chin":
            c.rect(10, 22, 21, 26, S); c.rect(12, 27, 19, 27, S)
        elif name in ("Angular", "Heart-shaped"):
            cut = 2 if name == "Angular" else 3
            for y in range(21, 27):
                k = (y - 20) * cut // 3
                c.clear(8, y, 8 + k, y); c.clear(23 - k, y, 23, y)
            if name == "Heart-shaped":
                c.rect(7, 14, 7, 18, S); c.rect(24, 14, 24, 18, S)
            c.rect(13, 25, 18, 30, S, 1)
            c.rect(14, 25, 17, 26, S)
        c.outline()
        c.rect(14, 27, 17, 30, S, 1)
        if d == 0:
            for (white, a, b) in ((10, 11, 12), (21, 20, 19)):       # eyes
                c.rect(min(white, b), 17, max(white, b), 17, LASH)
                c.rect(white, 18, white, 19, WHITE)
                c.rect(min(a, b), 18, max(a, b), 19, E)
                c.dot(b, 19, E, 1); c.dot(a, 19, E, 1)
            c.dot(15, 21, S, 1)                                      # nose
            c.rect(14, 23, 17, 23, (176, 96, 92))                    # mouth
            c.rect(10, 21, 11, 21, S, 3); c.rect(20, 21, 21, 21, S, 3)
            if name == "Freckled":
                for (x, y) in ((10, 21), (12, 22), (11, 23), (19, 22), (21, 21), (20, 23), (15, 20)):
                    c.dot(x, y, S, 1)
            elif name == "High cheekbones":
                c.rect(9, 20, 12, 20, S, 3); c.rect(19, 20, 22, 20, S, 3)
                c.rect(10, 22, 12, 22, S, 1); c.rect(19, 22, 21, 22, S, 1)
            elif name == "Mature":
                c.rect(10, 20, 12, 20, S, 1); c.rect(19, 20, 21, 20, S, 1)
                c.dot(12, 23, S, 1); c.dot(19, 23, S, 1); c.rect(13, 14, 18, 14, S, 1)
            elif name == "Cheek scar":
                c.dot(20, 20, SCAR); c.dot(21, 21, SCAR); c.dot(21, 22, SCAR); c.dot(22, 23, SCAR)
    else:
        c.rect(13, 25, 17, 30, S, 1)
        c.oval(8, 10, 22, 26, S)
        if name in ("Square", "Strong chin"):
            c.rect(9, 20, 15, 26, S)
            if name == "Strong chin":
                c.rect(8, 24, 13, 27, S)
        elif name == "Rounded":
            c.rect(8, 19, 10, 24, S)
        elif name in ("Angular", "Heart-shaped"):
            c.clear(8, 23, 9, 26); c.clear(10, 25, 10, 26)
        c.rect(7, 20, 7, 21, S)                                      # nose
        c.outline()
        c.rect(14, 27, 16, 30, S, 1)
        c.rect(10, 17, 12, 17, LASH)                                 # eye
        c.rect(10, 18, 11, 19, E); c.dot(12, 18, WHITE); c.dot(12, 19, WHITE); c.dot(10, 19, E, 1)
        c.rect(9, 23, 10, 23, (176, 96, 92))                         # mouth
        c.dot(18, 19, S, 1); c.dot(18, 20, S, 1)                     # ear
        if name == "Freckled":
            c.dot(11, 21, S, 1); c.dot(13, 22, S, 1); c.dot(12, 23, S, 1)
        elif name == "High cheekbones":
            c.rect(11, 20, 14, 20, S, 3); c.rect(11, 22, 13, 22, S, 1)
        elif name == "Mature":
            c.rect(10, 20, 12, 20, S, 1); c.dot(12, 23, S, 1)
    return c


# ---------------------------------------------------------------- hair

HAIR = ["Side part", "Tousled crop", "Short curls", "Bob", "Shoulder length", "Ponytail", "Bun", "Undercut",
        "Textured coils", "Long waves"]
LENGTH = {"Bob": 28, "Shoulder length": 33, "Long waves": 40}


def hair(v, d):
    name = HAIR[v]
    c = Cell()
    big = name in ("Short curls", "Textured coils")
    huge = name == "Textured coils"
    x0, x1, top = (5, 26, 5) if huge else ((6, 25, 7) if big else (7, 24, 8))
    length = LENGTH.get(name, 0)
    if d == 0:
        def fringe(x):
            if name == "Side part":
                return 14 if x < 14 else 16
            if name == "Tousled crop":
                return 15 if x % 3 == 0 else 14
            if name == "Undercut":
                return 13 if x < 18 else 15
            if name in ("Bob", "Shoulder length", "Long waves"):
                return 15
            return 14 + (1 if big and x % 2 == 0 else 0)
        burn = 12 if name == "Undercut" else 20
        c.oval(x0, top, x1, 26, P, 2,
               keep=lambda x, y: y <= fringe(x) or ((x <= 8 or x >= 23) and y <= burn))
        if length:
            for y in range(16, length + 1):
                w = 1 if (name == "Long waves" and (y // 3) % 2 == 0) else 0
                c.rect(6 - w, y, 8, y, P); c.rect(23, y, 25 + w, y, P)
        if name == "Bun":
            c.oval(12, 3, 19, 10, P)
        elif name == "Ponytail":
            c.rect(23, 9, 26, 13, P)
        elif name == "Tousled crop":
            for x in (10, 13, 17, 21):
                c.dot(x, top - 1, P)
        elif name == "Side part":
            c.rect(13, 9, 13, 13, P, 1)
    elif d == 1:
        nape = 17 if name == "Undercut" else 26
        c.oval(x0, top, x1, 27, P, 2, keep=lambda x, y: y <= nape)
        if name == "Undercut":
            c.oval(8, 10, 23, 26, P, 1, keep=lambda x, y: 17 < y <= 23)
        if length:
            c.rect(6, 16, 25, length, P)
            if name == "Long waves":
                for y in range(18, length, 6):
                    c.rect(5, y, 5, y + 2, P); c.rect(26, y, 26, y + 2, P)
                for x in (10, 15, 20):
                    c.rect(x, 24, x, length - 1, P, 1)
        if name == "Bun":
            c.oval(12, 3, 19, 10, P)
        elif name == "Ponytail":
            c.oval(13, 20, 18, 37, P); c.rect(14, 20, 17, 21, METAL)
        elif name == "Tousled crop":
            for x in (10, 13, 17, 21):
                c.dot(x, top - 1, P)
    else:
        # Facing left: the face is on the left, the back of the head on the right.
        fr = 13 if name == "Undercut" else (15 if length else 14)
        back = 16 if name == "Undercut" else 26
        c.oval(x0 + 1, top, x1 - 1, 27, P, 2,
               keep=lambda x, y: y <= fr or (x >= 15 and y <= back) or (x >= 13 and y <= 19 and name != "Undercut"))
        if name == "Undercut":
            c.oval(9, 10, 22, 26, P, 1, keep=lambda x, y: x >= 16 and 16 < y <= 22)
        if length:
            c.rect(15, 16, 23, length, P)
            if name == "Long waves":
                for y in range(18, length, 6):
                    c.rect(24, y, 24, y + 2, P)
                c.rect(19, 24, 19, length - 1, P, 1)
        if name == "Bun":
            c.oval(17, 4, 24, 11, P)
        elif name == "Ponytail":
            c.oval(21, 14, 27, 31, P); c.rect(21, 15, 22, 17, METAL)
        elif name == "Tousled crop":
            for x in (10, 13, 17, 20):
                c.dot(x, top - 1, P)
    c.outline()
    # Some light and dark so it reads as hair.
    for (x, y), (mat, sh) in list(c.px.items()):
        if mat == P and sh == 2:
            if big and (x + y) % 3 == 0:
                c.px[(x, y)] = (P, 1 if (x * 7 + y * 3) % 2 else 3)
            elif y <= top + 3 and (x + y) % 5 == 0:
                c.px[(x, y)] = (P, 3)
    return c


# ---------------------------------------------------------------- writing the files

MAKERS = {"bottoms": bottoms, "tops": tops, "faces": faces, "hair": hair}


def build(folder):
    out = {}
    for k, fn in MAKERS.items():
        art = Image.new("RGBA", (128, 640), (0, 0, 0, 0))
        mask = Image.new("RGBA", (128, 640), (0, 0, 0, 0))
        for v in range(10):
            for d in range(4):
                cell = fn(v, 2).mirrored() if d == 3 else fn(v, d)
                cell.paste(art, mask, d * 32, v * 64)
        art.save("%s/art/player/%s.png" % (folder, k))
        mask.save("%s/art/player/%s_mask.png" % (folder, k))
        out[k] = (art, mask)
    return out


# The same rules the game uses (scripts/player_maker.gd), for the preview picture.
PRIMARY = {"hair": "hairColor", "tops": "topColor", "bottoms": "bottomColor", "faces": "skinColor"}
DIV = [140.0, 185.0, 150.0]


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def sheet(layers, look):
    strips = {}
    for k, (art, mask) in layers.items():
        a = art.crop((0, look[k] * 64, 128, look[k] * 64 + 64)).copy()
        m = mask.crop((0, look[k] * 64, 128, look[k] * 64 + 64))
        targets = [rgb(look[PRIMARY[k]]), rgb(look["skinColor"]), rgb(look["eyeColor"])]
        ap, mp = a.load(), m.load()
        for y in range(64):
            for x in range(128):
                r, g, b, al = ap[x, y]
                mr, mg, mb, ma = mp[x, y]
                if al and ma:
                    kind = 0 if mr else (1 if mg else 2)
                    f = (0.2126 * r + 0.7152 * g + 0.0722 * b) / DIV[kind]
                    ap[x, y] = tuple(max(0, min(255, int(round(t * f)))) for t in targets[kind]) + (al,)
        strips[k] = a
    out = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    for phase in range(3):
        for d in range(4):
            f = Image.new("RGBA", (32, 64), (0, 0, 0, 0))

            def put(src, sx, sy, w, h, dx, dy):
                part = src.crop((sx, sy, sx + w, sy + h))
                f.alpha_composite(part, (max(dx, 0), max(dy, 0)),
                                  (max(-dx, 0), max(-dy, 0), min(w, 32 - dx), min(h, 64 - dy)))
            bt, sx = strips["bottoms"], d * 32
            if phase == 0:
                put(bt, sx, 0, 32, 64, 0, 0)
            else:
                put(bt, sx, 0, 32, 54, 0, 0)
                if d < 2:
                    put(bt, sx, 54, 16, 10, 0, 54 - (2 if phase == 1 else 0))
                    put(bt, sx + 16, 54, 16, 10, 16, 54 - (2 if phase == 2 else 0))
                else:
                    step = -2 if phase == 1 else 2
                    put(bt, sx, 54, 32, 10, step, 53)
                    put(bt, sx, 54, 32, 10, -step, 54)
            bob = -1 if phase else 0
            for k in ("tops", "faces", "hair"):
                put(strips[k], sx, 0, 32, 64, 0, bob)
            out.alpha_composite(f, (d * 32, phase * 64))
    return out


if __name__ == "__main__":
    folder = sys.argv[1]
    layers = build(folder)
    print("wrote 8 files to %s/art/player" % folder)
    if len(sys.argv) > 2:
        hairs = ["#b5432e", "#68452f", "#111418", "#e8c36a", "#d9d9df", "#5a6fb0", "#8c5a2e", "#2b1d16", "#7a3f8f", "#c98a3d"]
        skins = ["#efb583", "#f6d0b0", "#a5683c", "#e0a070", "#7d4a2a", "#f0c6a0", "#c68652", "#59341f", "#efb583", "#f6d0b0"]
        topc = ["#4c8f4a", "#b5432e", "#578d99", "#c96a2e", "#7a3f8f", "#3f6fb3", "#d0a030", "#30343c", "#d9d9df", "#e07aa8"]
        botc = ["#3f5a8a", "#30343c", "#657081", "#6b4a2e", "#c9b38a", "#7a2e2e", "#4a6a4a", "#30343c", "#3f5a8a", "#8a8f99"]
        pic = Image.new("RGBA", (5 * 136 + 4, 4 * 68 + 4), (30, 34, 48, 255))
        for i in range(10):
            look = {"hair": i, "faces": i, "tops": i, "bottoms": i, "hairColor": hairs[i], "skinColor": skins[i],
                    "topColor": topc[i], "bottomColor": botc[i], "eyeColor": "#54b7c4"}
            sh = sheet(layers, look)
            pic.alpha_composite(sh.crop((0, 0, 128, 64)), (4 + (i % 5) * 136, 4 + (i // 5) * 136))
            pic.alpha_composite(sh.crop((0, 64, 128, 128)), (4 + (i % 5) * 136, 72 + (i // 5) * 136))
        pic.resize((pic.width * 3, pic.height * 3), Image.NEAREST).save(sys.argv[2])
