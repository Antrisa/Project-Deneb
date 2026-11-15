"""Generates placeholder art and all map data for Echo Landing, and checks the maps.
Usage: python3 build.py <project_dir> [preview_dir]
"""
import json, os, struct, sys, zlib
from collections import deque

OUT = sys.argv[1]
PREV = sys.argv[2] if len(sys.argv) > 2 else None
ART = os.path.join(OUT, "art")
os.makedirs(ART, exist_ok=True)


class Img:
    def __init__(s, w, h, fill=(0, 0, 0, 0)):
        s.w, s.h = w, h
        s.p = [[fill] * w for _ in range(h)]

    def px(s, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < s.w and 0 <= y < s.h:
            s.p[y][x] = c if len(c) == 4 else (c[0], c[1], c[2], 255)

    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s.px(x, y, c)

    def ell(s, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    s.px(x, y, c)

    def blit(s, src, dx, dy, sx=0, sy=0, w=None, h=None):
        w = src.w if w is None else w
        h = src.h if h is None else h
        for y in range(h):
            for x in range(w):
                c = src.p[sy + y][sx + x]
                if c[3] > 0:
                    s.px(dx + x, dy + y, c)

    def save(s, path):
        if os.path.relpath(path, ART).replace(os.sep, "/") in HAND_EDITED or os.path.basename(path) in HAND_EDITED:
            return      # this file is hand-made art: leave it alone
        raw = b"".join(b"\x00" + bytes(v for px in row for v in px) for row in s.p)

        def chunk(t, d):
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n"
                    + chunk(b"IHDR", struct.pack(">IIBBBBB", s.w, s.h, 8, 6, 0, 0, 0))
                    + chunk(b"IDAT", zlib.compress(raw, 9))
                    + chunk(b"IEND", b""))


# Files listed in art/hand_edited.txt belong to the artist and are never overwritten.
HAND_EDITED = set()
_hand = os.path.join(ART, "hand_edited.txt")
if os.path.exists(_hand):
    HAND_EDITED = {ln.strip() for ln in open(_hand) if ln.strip() and not ln.startswith("#")}


def art(name):
    return os.path.join(ART, name)


# ================================================================ tiles
# Each column of tiles.png is 16 wide and 32 tall. The lower half is the tile itself.
# The upper half is only used by tall objects (shelves, lamps, plants...): it is drawn over the
# tile above, in front of characters, so you can walk behind them.
# Floors can have several variations; the game picks one per tile so big areas don't look like a grid.
import random

TILE_COLUMNS = 110
T = Img(16 * TILE_COLUMNS, 32)
TILE_FLOOR, TILE_OBJ, TILE_VARIANTS = {}, {}, {}
SOLID_FLOOR = "~"          # '~' is empty space: solid, never drawn
WALL_FACES = ""            # floor tiles that are front faces (the floor below them gets a shadow)
TALL = ""                  # objects that use the upper half
OUTLINE = (40, 34, 52)
_next = [0]


def outline_img(im, x0=0, y0=0, w=None, h=None):
    """Dark 1px outline around the opaque pixels of a region."""
    w = im.w if w is None else w
    h = im.h if h is None else h
    add = []
    for y in range(h):
        for x in range(w):
            if im.p[y0 + y][x0 + x][3] < 200:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and im.p[y0 + ny][x0 + nx][3] >= 200 and im.p[y0 + ny][x0 + nx][:3] != OUTLINE:
                        add.append((x, y))
                        break
    for (x, y) in add:
        im.px(x0 + x, y0 + y, OUTLINE)


def dk(c, k=0.78):
    return tuple(max(0, int(v * k)) for v in c[:3])


def lt(c, k=1.18):
    return tuple(min(255, int(v * k)) for v in c[:3])


def mixc(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


class Tile:
    def __init__(s, layer, ch, solid=False, face=False, tall=False):
        global SOLID_FLOOR, WALL_FACES, TALL
        s.o = _next[0] * 16
        d = TILE_FLOOR if layer == "f" else TILE_OBJ
        if ch in d:
            assert layer == "f" and d[ch] + TILE_VARIANTS[ch] == _next[0], "variations of a floor must be defined one after another: " + ch
            TILE_VARIANTS[ch] += 1
        else:
            d[ch] = _next[0]
            if layer == "f":
                TILE_VARIANTS[ch] = 1
            if layer == "f" and solid:
                SOLID_FLOOR += ch
            if face:
                WALL_FACES += ch
            if tall:
                TALL += ch
        _next[0] += 1

    def r(s, x0, y0, x1, y1, c):
        T.rect(s.o + max(0, x0), 16 + y0, s.o + min(15, x1), 16 + y1, c)
        return s

    def p(s, x, y, c):
        if 0 <= x < 16 and -16 <= y < 16:
            T.px(s.o + x, 16 + y, c)
        return s

    def ps(s, pts, c):
        for (x, y) in pts:
            s.p(x, y, c)
        return s

    def grad(s, x0, y0, x1, y1, c0, c1):
        for y in range(y0, y1 + 1):
            s.r(x0, y, x1, y, mixc(c0, c1, (y - y0) / max(1, y1 - y0)))
        return s

    def noise(s, cols, n, seed, y0=0, y1=15):
        rnd = random.Random(seed)
        for _ in range(n):
            s.p(rnd.randrange(16), rnd.randrange(y0, y1 + 1), rnd.choice(cols))
        return s

    def ell(s, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    s.p(x, y, c)
        return s

    def outline(s):
        outline_img(T, s.o, 0, 16, 32)
        return s


CAP, CAPD, CAPL = (86, 100, 122), (58, 68, 88), (112, 128, 152)
PANEL, PANELD = (240, 236, 226), (212, 206, 196)
TEALH, TEALC, TEALD2 = (104, 190, 198), (62, 150, 160), (44, 116, 128)
FLOORC = (202, 210, 218)

# ---------------------------------------------------------------- floors you can walk on
for v in range(4):      # station floor
    t = Tile("f", ".").r(0, 0, 15, 15, FLOORC).noise([(196, 204, 212), (208, 216, 224)], 12, 30 + v)
    t.r(0, 0, 15, 0, (224, 230, 236)).r(0, 0, 0, 15, (224, 230, 236)).r(0, 15, 15, 15, (176, 186, 198)).r(15, 0, 15, 15, (176, 186, 198))
    if v == 1:
        t.r(7, 1, 7, 14, (188, 196, 208)).r(8, 1, 8, 14, (214, 222, 230))
    if v == 3:
        t.r(5, 5, 10, 10, (150, 160, 174)).r(5, 5, 10, 5, (120, 130, 146))
        for y in (7, 9):
            t.r(6, y, 9, y, (104, 114, 130)) if v == 3 else None
for v in range(2):      # carpet
    t = Tile("f", ",").r(0, 0, 15, 15, (168, 62, 58)).noise([(150, 52, 52), (182, 74, 64), (158, 56, 54)], 60, 40 + v)
    if v == 0:
        for (cx, cy) in [(4, 4), (12, 12)]:
            t.ps([(cx, cy - 2), (cx - 1, cy - 1), (cx + 1, cy - 1), (cx - 2, cy), (cx + 2, cy), (cx - 1, cy + 1), (cx + 1, cy + 1), (cx, cy + 2)], (222, 160, 90))
            t.p(cx, cy, (236, 196, 120))
    else:
        t.ps([(12, 4), (4, 12)], (222, 160, 90))
for v in range(4):      # metal deck
    t = Tile("f", "f").r(0, 0, 15, 15, (88, 98, 112)).noise([(82, 92, 106), (96, 106, 120)], 16, 50 + v)
    t.r(0, 0, 15, 0, (112, 122, 138)).r(0, 0, 0, 15, (112, 122, 138)).r(0, 15, 15, 15, (64, 72, 86)).r(15, 0, 15, 15, (64, 72, 86))
    if v in (0, 3):
        t.ps([(2, 2), (13, 2), (2, 13), (13, 13)], (140, 150, 164)).ps([(3, 3), (14, 3), (3, 14), (14, 14)], (58, 66, 80))
    if v == 1:
        for k in range(4, 12, 3):
            t.r(k, 5, k + 1, 10, (106, 116, 132)).r(k + 1, 6, k + 1, 10, (70, 78, 92))
    if v == 2:
        t.r(3, 3, 12, 12, (60, 68, 82))
        for y in range(4, 12, 2):
            t.r(4, y, 11, y, (104, 114, 130))
for v in range(3):      # hangar floor
    t = Tile("f", "h").r(0, 0, 15, 15, (112, 120, 132)).noise([(104, 112, 124), (122, 130, 142), (108, 116, 128)], 26, 60 + v)
    t.r(0, 15, 15, 15, (92, 100, 112)).r(15, 0, 15, 15, (92, 100, 112)).r(0, 0, 15, 0, (126, 134, 146))
    if v == 2:
        t.ell(8, 9, 4, 2.5, (90, 96, 110)).ell(7, 8, 2, 1.2, (80, 86, 100))
Tile("f", "u").r(0, 0, 15, 15, (176, 190, 204)).noise([(168, 182, 196), (186, 198, 212)], 14, 65).r(0, 0, 15, 1, (134, 150, 168)).r(0, 2, 15, 2, (196, 208, 220)).r(0, 14, 15, 15, (134, 150, 168)).r(2, 7, 6, 8, TEALC).r(10, 7, 14, 8, TEALC).r(2, 7, 6, 7, TEALH).r(10, 7, 14, 7, TEALH)
for v in range(3):      # soil
    t = Tile("f", "s").r(0, 0, 15, 15, (122, 86, 58)).noise([(98, 68, 46), (146, 106, 72), (110, 76, 52), (134, 96, 64)], 70, 70 + v)
    if v == 0:
        t.ps([(5, 3), (6, 3), (5, 2)], (96, 160, 84)).ps([(11, 10), (11, 9)], (120, 186, 100))
    if v == 1:
        t.ps([(3, 11), (4, 11)], (160, 150, 140)).ps([(10, 4)], (170, 160, 150))
for v in range(3):      # mine floor
    t = Tile("f", "m").r(0, 0, 15, 15, (92, 78, 70)).noise([(76, 64, 60), (108, 92, 82), (84, 70, 64), (100, 86, 76)], 64, 80 + v)
    if v == 1:
        t.ps([(4, 9), (5, 9), (5, 10)], (62, 52, 50)).ps([(4, 8)], (120, 104, 92))
    if v == 2:
        t.ps([(10, 4), (11, 4), (11, 5), (10, 5)], (118, 102, 92)).ps([(11, 6), (10, 6)], (64, 54, 52))
for v in range(3):      # town square paving
    t = Tile("f", "i").r(0, 0, 15, 15, (196, 172, 138)).noise([(184, 160, 128), (208, 186, 152), (190, 166, 132)], 44, 90 + v)
    rects = [[(0, 0, 6, 4), (8, 0, 15, 4), (0, 6, 3, 10), (5, 6, 11, 10), (13, 6, 15, 10), (0, 12, 7, 15), (9, 12, 15, 15)],
             [(0, 0, 4, 5), (6, 0, 11, 5), (13, 0, 15, 5), (0, 7, 8, 10), (10, 7, 15, 10), (0, 12, 5, 15), (7, 12, 15, 15)],
             [(0, 0, 9, 3), (11, 0, 15, 3), (0, 5, 5, 9), (7, 5, 15, 9), (0, 11, 3, 15), (5, 11, 12, 15), (14, 11, 15, 15)]][v]
    for (x0, y0, x1, y1) in rects:
        if y1 < 15:
            t.r(x0, y1 + 1, x1, y1 + 1, (156, 134, 106))
        if x1 < 15:
            t.r(x1 + 1, y0, x1 + 1, y1, (156, 134, 106))
        t.r(x0, y0, x1, y0, (214, 192, 158))
    if v == 2:
        t.ps([(6, 10), (5, 10), (6, 9)], (120, 170, 96))
UPC, DNC = (70, 200, 120), (244, 156, 66)
t = Tile("f", "U").r(0, 0, 15, 15, FLOORC).r(1, 1, 14, 14, (36, 56, 54)).r(1, 1, 14, 1, (60, 90, 84)).r(1, 14, 14, 14, (24, 40, 40))
for i in range(5):
    t.r(7 - i, 4 + i, 8 + i, 4 + i, UPC)
t.r(6, 9, 9, 12, UPC).r(7, 4, 8, 4, (170, 240, 190))
t = Tile("f", "D").r(0, 0, 15, 15, FLOORC).r(1, 1, 14, 14, (62, 46, 38)).r(1, 1, 14, 1, (96, 72, 56)).r(1, 14, 14, 14, (44, 32, 28))
for i in range(5):
    t.r(7 - i, 11 - i, 8 + i, 11 - i, DNC)
t.r(6, 3, 9, 6, DNC).r(6, 3, 9, 3, (255, 210, 150))
t = Tile("f", "A").r(0, 0, 15, 15, (112, 120, 132))
for k in range(16):
    c = (238, 202, 64) if (k // 2) % 2 == 0 else (40, 40, 46)
    t.p(k, 0, c).p(k, 15, c).p(k, 1, c).p(k, 14, c)
t.r(5, 6, 10, 9, (238, 202, 64)).r(5, 6, 10, 6, (255, 236, 150))
t = Tile("f", "R").r(0, 0, 15, 15, (92, 78, 70)).noise([(76, 64, 60), (108, 92, 82)], 30, 95)
for i in range(4):
    for bx in (3, 8):
        t.p(bx + i, 3 + i, (238, 202, 64)).p(bx + i, 12 - i, (238, 202, 64)).p(bx + i + 1, 3 + i, (190, 156, 40)).p(bx + i + 1, 12 - i, (190, 156, 40))

# ---------------------------------------------------------------- walls and other solid ground
for v in range(2):      # wall top
    t = Tile("f", "#", True).r(0, 0, 15, 15, CAP).noise([(92, 106, 128), (80, 94, 116)], 14, 100 + v)
    if v == 1:
        t.ps([(3, 3), (12, 12)], CAPL).ps([(4, 4), (13, 13)], CAPD)


def face(t, v=0):
    t.grad(0, 3, 15, 12, PANEL, PANELD)
    t.r(0, 0, 15, 1, CAP).r(0, 0, 15, 0, CAPL).r(0, 2, 15, 2, CAPD)
    t.r(0, 6, 15, 6, TEALH).r(0, 7, 15, 7, TEALC).r(0, 8, 15, 8, TEALD2)
    t.r(0, 3, 0, 12, (200, 194, 184)).r(1, 3, 1, 12, (246, 242, 234))
    t.r(0, 13, 15, 13, (160, 156, 160)).r(0, 14, 15, 14, (124, 122, 132)).r(0, 15, 15, 15, (90, 88, 102))
    if v == 0:
        t.ps([(4, 4), (12, 4), (4, 11), (12, 11)], (190, 184, 174))
    elif v == 1:    # vent
        t.r(5, 9, 11, 12, (120, 128, 142)).r(5, 9, 11, 9, (86, 94, 110))
        for y in (10, 12):
            t.r(6, y, 10, y, (70, 78, 94))
    elif v == 2:    # small sign
        t.r(5, 9, 10, 12, (52, 62, 90)).r(5, 9, 10, 9, (90, 104, 136)).ps([(6, 10), (7, 11), (8, 10), (9, 11)], (244, 214, 84))
    else:           # light strip
        t.r(5, 3, 10, 4, (255, 240, 180)).r(4, 5, 11, 5, (250, 244, 224)).ps([(5, 3), (10, 3)], (190, 170, 110))
    return t


for v in range(4):
    face(Tile("f", "W", True, True), v)
t = face(Tile("f", "w", True, True), 0).r(2, 4, 13, 12, (70, 84, 106)).r(2, 4, 13, 4, (116, 132, 156)).r(3, 5, 12, 11, (16, 22, 52))
for y in range(7, 12):
    for x in range(3, 13):
        if (x - 11) ** 2 + (y - 16) ** 2 < 92:
            t.p(x, y, (64, 124, 224) if (x + y) % 4 else (128, 176, 242))
t.ps([(5, 6), (9, 5)], (255, 255, 255)).ps([(4, 10), (5, 9), (6, 8)], (60, 70, 110))
for v in range(4):      # moon rock
    t = Tile("f", "r", True).r(0, 0, 15, 15, (118, 120, 130)).noise([(104, 106, 116), (132, 134, 144), (110, 112, 122), (126, 128, 138)], 56, 110 + v)
    if v == 0:
        t.ps([(5, 5), (6, 4), (7, 4), (8, 4), (9, 5)], (88, 90, 100)).ps([(5, 6), (9, 6), (6, 7), (7, 7), (8, 7)], (150, 152, 162)).ps([(6, 5), (7, 5), (8, 5), (6, 6), (7, 6), (8, 6)], (100, 102, 112))
    if v == 1:
        t.ps([(11, 10), (12, 10), (12, 11)], (92, 94, 104)).ps([(11, 11)], (150, 152, 162)).ps([(3, 4)], (150, 152, 162)).ps([(3, 3)], (92, 94, 104))
    if v == 2:
        t.ell(8, 8, 5, 3.5, (104, 106, 116)).ell(8, 9, 4, 2.5, (112, 114, 124)).ps([(4, 6), (5, 5), (6, 5), (7, 4), (8, 4), (9, 4)], (86, 88, 98)).ps([(12, 10), (11, 11), (10, 11), (9, 12)], (148, 150, 160))
t = Tile("f", "d", True).r(0, 0, 15, 15, (64, 104, 124)).r(1, 1, 14, 14, (96, 176, 196)).r(2, 2, 13, 13, (130, 208, 224)).ps([(4, 9), (5, 8), (6, 7), (7, 6), (9, 11), (10, 10)], (226, 248, 252))
t = Tile("f", "g", True, True).grad(0, 3, 15, 14, (190, 240, 248), (140, 212, 228))
t.r(0, 0, 15, 1, (64, 104, 124)).r(0, 0, 15, 0, (104, 150, 170)).r(0, 2, 15, 2, (44, 78, 96)).r(0, 3, 0, 15, (64, 104, 124)).r(0, 15, 15, 15, (50, 86, 104))
t.ps([(4, 11), (5, 10), (6, 9), (7, 8), (8, 7), (10, 12), (11, 11), (12, 10)], (240, 253, 255))
for v in range(2):
    Tile("f", "M", True).r(0, 0, 15, 15, (44, 38, 44)).noise([(54, 46, 52), (36, 30, 36), (48, 42, 48)], 40, 120 + v)
for v in range(2):
    t = Tile("f", "N", True, True).grad(0, 3, 15, 13, (112, 92, 84), (78, 62, 60)).noise([(76, 60, 58), (120, 100, 90), (92, 76, 70)], 40, 124 + v, 4, 13)
    t.r(0, 0, 15, 2, (44, 38, 44)).r(0, 3, 15, 3, (132, 112, 100)).r(0, 14, 15, 15, (56, 44, 46))
    if v == 0:
        t.r(2, 7, 9, 7, (64, 50, 50)).r(8, 11, 14, 11, (64, 50, 50)).r(3, 8, 8, 8, (124, 104, 94))
    else:
        t.r(5, 6, 13, 6, (64, 50, 50)).r(1, 10, 6, 10, (64, 50, 50)).ps([(11, 9), (12, 9)], (150, 130, 116))
t = Tile("f", "Z", True, True).grad(0, 3, 15, 15, (146, 154, 166), (112, 120, 134))
t.r(0, 0, 15, 1, CAP).r(0, 0, 15, 0, CAPL).r(0, 2, 15, 2, CAPD)
for y in range(4, 15, 3):
    t.r(0, y, 15, y, (84, 92, 106)).r(0, y + 1, 15, y + 1, (166, 174, 186))
t.r(0, 15, 15, 15, (66, 72, 86)).ps([(13, 13)], (236, 76, 64)).ps([(13, 12)], (255, 160, 150))
Tile("f", "V", True).r(0, 0, 15, 15, (10, 8, 12)).r(0, 0, 15, 2, (60, 48, 48)).ps([(3, 3), (4, 3), (10, 3), (11, 4), (12, 3)], (60, 48, 48)).ps([(6, 8), (9, 8)], (190, 60, 50))
for v in range(2):      # fountain water
    t = Tile("f", "O", True).r(0, 0, 15, 15, (70, 150, 210)).noise([(96, 176, 228), (56, 130, 192), (82, 162, 218)], 40, 130 + v)
    if v == 0:
        t.r(2, 4, 6, 4, (190, 230, 250)).r(9, 10, 13, 10, (190, 230, 250))
    else:
        t.r(8, 3, 12, 3, (190, 230, 250)).r(3, 11, 6, 11, (190, 230, 250)).r(4, 7, 5, 7, (190, 230, 250))
Tile("f", "B", True).r(0, 0, 15, 15, (150, 150, 160)).r(1, 1, 14, 13, (196, 196, 206)).r(2, 2, 13, 12, (176, 176, 188)).r(1, 1, 14, 1, (224, 224, 232)).r(0, 14, 15, 15, (110, 110, 124)).ps([(4, 5), (10, 9), (7, 11), (12, 4)], (150, 150, 162))
t = Tile("f", "J", True, False, True).r(0, 0, 15, 15, (70, 150, 210)).r(3, 4, 12, 14, (150, 150, 160)).r(4, 4, 11, 13, (196, 196, 206)).r(11, 5, 12, 14, (120, 120, 134))
t.ell(7.5, -3, 5.5, 6, (60, 140, 76)).ell(6.5, -5, 4, 4, (86, 176, 96)).ps([(5, -7), (7, -8), (4, -4), (8, -5), (6, -2)], (150, 222, 130)).ps([(9, -1), (5, 0), (10, -6)], (240, 140, 196))
t.r(7, 3, 8, 6, (110, 80, 56)).r(7, 8, 8, 12, (120, 215, 255))

# ---------------------------------------------------------------- objects (all solid, seen from the front)
t = Tile("o", "c").r(2, 2, 13, 6, (222, 160, 84)).r(2, 2, 13, 2, (246, 200, 124)).r(2, 7, 13, 14, (184, 118, 56)).r(2, 7, 13, 7, (126, 78, 38))
t.r(5, 8, 5, 14, (146, 90, 42)).r(10, 8, 10, 14, (146, 90, 42)).r(2, 14, 13, 14, (140, 86, 40)).r(12, 8, 13, 13, (160, 100, 46)).ps([(3, 3), (12, 3), (3, 5), (12, 5)], (170, 116, 56)).outline()
Tile("o", "t").r(1, 4, 14, 9, (60, 168, 160)).r(1, 4, 14, 4, (130, 220, 208)).r(2, 5, 13, 5, (84, 190, 180)).r(1, 10, 14, 11, (36, 116, 112)).r(2, 12, 3, 14, (28, 90, 90)).r(12, 12, 13, 14, (28, 90, 90)).ps([(5, 7), (6, 7)], (240, 236, 220)).ps([(10, 6)], (240, 180, 90)).outline()
t = Tile("o", "p", tall=True).r(5, 9, 10, 14, (190, 104, 70)).r(5, 9, 10, 9, (224, 142, 104)).r(9, 10, 10, 14, (150, 78, 54)).r(6, 14, 9, 14, (130, 66, 46))
t.ell(7.5, 2, 5.5, 6.5, (52, 132, 76)).ell(7, 0, 4.5, 5, (76, 170, 90)).ell(6, -3, 3, 3, (104, 196, 108))
t.ps([(5, -4), (7, -5), (4, -1), (8, -2), (6, 2), (9, 1)], (160, 228, 136)).ps([(11, 4), (10, 6), (4, 6), (9, 7)], (38, 104, 62)).outline()
t = Tile("o", "k", tall=True).r(1, 6, 14, 14, (70, 84, 110)).r(1, 6, 14, 6, (104, 120, 150)).r(12, 7, 14, 14, (52, 62, 86)).r(1, 13, 14, 14, (46, 56, 78))
t.r(2, 8, 11, 10, (98, 114, 142)).ps([(3, 9)], (240, 90, 80)).ps([(5, 9)], (120, 230, 120)).ps([(7, 9)], (240, 200, 80)).ps([(9, 9)], (120, 200, 250))
t.r(2, -6, 13, 4, (52, 62, 86)).r(3, -5, 12, 3, (16, 34, 66)).r(4, -4, 9, -4, (110, 220, 250)).r(4, -2, 11, -2, (110, 220, 250)).r(4, 0, 7, 0, (70, 170, 220)).r(4, 2, 10, 2, (110, 220, 250)).r(6, 5, 9, 5, (52, 62, 86)).outline()
Tile("o", "b").r(1, 0, 14, 2, (124, 96, 76)).r(1, 0, 14, 0, (160, 128, 102)).r(1, 3, 14, 5, (230, 230, 238)).r(3, 3, 12, 4, (255, 255, 255)).grad(1, 6, 14, 13, (96, 146, 214), (62, 104, 172)).r(1, 6, 14, 6, (140, 182, 236)).r(13, 7, 14, 13, (50, 88, 150)).ps([(4, 9), (9, 11), (6, 12)], (120, 166, 226)).r(1, 14, 14, 15, (90, 70, 58)).outline()
Tile("o", "o").r(1, 2, 14, 6, (186, 96, 70)).r(1, 2, 14, 2, (224, 136, 102)).r(3, 7, 12, 11, (224, 132, 94)).r(3, 7, 12, 7, (244, 164, 124)).r(7, 7, 8, 11, (190, 104, 76)).r(1, 4, 2, 13, (168, 84, 62)).r(13, 4, 14, 13, (150, 72, 54)).r(3, 12, 12, 14, (150, 74, 56)).r(3, 14, 12, 14, (120, 56, 44)).outline()
t = Tile("o", "S", tall=True).r(1, -10, 14, 14, (126, 96, 70)).r(1, -10, 14, -10, (166, 134, 102)).r(13, -9, 14, 14, (98, 74, 54)).r(1, 13, 14, 14, (88, 66, 50))
for i, y in enumerate([-8, -3, 2, 7]):
    t.r(2, y, 12, y + 3, (58, 44, 38))
    rnd = random.Random(200 + i)
    x = 2
    while x < 12:
        w, h = rnd.choice([1, 1, 2]), rnd.choice([2, 3, 3])
        c = rnd.choice([(226, 84, 72), (84, 176, 226), (236, 206, 84), (124, 206, 124), (206, 124, 206), (240, 240, 240), (244, 164, 64), (94, 134, 226)])
        t.r(x, y + 4 - h, min(12, x + w - 1), y + 3, c).r(x, y + 4 - h, x, y + 4 - h, lt(c))
        x += w + rnd.choice([0, 1])
t.outline()
Tile("o", "C").r(0, 3, 15, 8, (226, 206, 170)).r(0, 3, 15, 3, (248, 236, 208)).r(0, 8, 15, 8, (196, 174, 138)).grad(0, 9, 15, 14, (176, 142, 108), (146, 114, 84)).r(0, 9, 15, 9, (116, 90, 68)).r(7, 10, 7, 14, (130, 100, 74)).r(8, 10, 8, 14, (190, 156, 120)).r(0, 15, 15, 15, OUTLINE).r(0, 2, 15, 2, OUTLINE)
t = Tile("o", "T", tall=True).r(7, 4, 8, 13, (70, 72, 86)).r(4, 14, 11, 14, (70, 72, 86)).ps([(5, 13), (10, 13), (6, 12), (9, 12)], (70, 72, 86))
for k in range(11):
    t.r(2 + k, 4 - k, 5 + k, 5 - k, (206, 210, 222)).p(2 + k, 5 - k, (150, 156, 172)).p(5 + k, 4 - k, (236, 240, 248))
t.r(12, -8, 14, -6, (120, 220, 255)).p(13, -7, (230, 250, 255)).outline()
t = Tile("o", "a", tall=True).r(4, 9, 11, 14, (156, 156, 168)).r(4, 9, 11, 9, (204, 204, 216)).r(10, 10, 11, 14, (120, 120, 134)).r(3, 14, 12, 14, (104, 104, 118))
t.r(7, -6, 8, 6, (190, 120, 255)).r(6, -3, 9, 3, (190, 120, 255)).r(5, -1, 10, 1, (190, 120, 255)).ps([(7, -5), (7, -4), (6, -2), (6, -1), (5, 0)], (244, 226, 255)).ps([(9, 2), (8, 4), (8, 5), (10, 1)], (136, 76, 206)).outline()
Tile("o", "G").r(0, 0, 15, 15, (50, 60, 82)).r(0, 0, 15, 0, (84, 98, 124)).r(2, 2, 13, 13, (40, 150, 164)).r(3, 3, 12, 12, (70, 200, 204)).r(5, 5, 10, 10, (150, 245, 235)).r(6, 6, 9, 9, (240, 255, 255)).r(0, 7, 1, 8, (170, 126, 62)).r(14, 7, 15, 8, (170, 126, 62)).r(0, 15, 15, 15, (34, 40, 58))
t = Tile("o", "O").r(2, 9, 13, 14, (134, 102, 82)).r(4, 6, 11, 9, (134, 102, 82)).r(6, 4, 9, 6, (156, 122, 100)).r(9, 10, 13, 14, (104, 78, 64)).r(2, 14, 13, 14, (92, 68, 56))
t.ps([(5, 8), (9, 6), (11, 11), (4, 12), (8, 12)], (240, 180, 72)).ps([(6, 5), (5, 7), (3, 10)], (180, 146, 120)).ps([(5, 9), (9, 7)], (255, 226, 150)).outline()
t = Tile("o", "F", tall=True).r(1, 0, 14, 14, (96, 84, 84)).r(1, 0, 14, 1, (136, 122, 120)).r(12, 2, 14, 14, (70, 60, 62)).r(3, 6, 11, 12, (36, 28, 30)).r(4, 7, 10, 12, (255, 140, 44)).r(5, 9, 9, 12, (255, 220, 110)).r(6, 11, 8, 12, (255, 250, 210))
t.r(1, 13, 14, 14, (64, 54, 56)).r(5, -12, 10, -1, (84, 74, 76)).r(5, -12, 10, -12, (124, 112, 112)).r(9, -11, 10, -1, (62, 54, 56)).r(4, -2, 11, -1, (110, 98, 98)).ps([(3, 3), (12, 3)], (150, 136, 134)).outline()
t = Tile("o", "H", tall=True).r(1, 9, 14, 14, (146, 104, 72)).r(1, 9, 14, 9, (186, 140, 100)).r(12, 10, 14, 14, (112, 80, 56)).r(1, 14, 14, 14, (96, 68, 48))
t.r(2, 2, 13, 8, (58, 140, 74)).ell(4, 1, 2.5, 3, (86, 176, 96)).ell(8, 0, 2.5, 3.5, (72, 160, 86)).ell(12, 1, 2.2, 3, (86, 176, 96))
t.ps([(3, -1), (8, -3), (12, -1), (5, 3), (10, 4)], (150, 222, 130)).ps([(4, 1), (11, 2)], (244, 224, 94)).ps([(8, 1)], (236, 134, 194)).ps([(3, 8), (7, 8), (12, 8), (9, 7)], (38, 104, 62)).outline()
t = Tile("o", "P", tall=True).r(2, -4, 13, 14, (104, 114, 130)).r(2, -4, 13, -3, (146, 156, 172)).r(11, -2, 13, 14, (78, 88, 104)).r(2, 13, 13, 14, (66, 74, 90))
t.r(4, 2, 5, 12, (190, 138, 66)).r(8, 2, 9, 12, (190, 138, 66)).r(4, 6, 9, 7, (190, 138, 66)).r(4, 2, 4, 12, (232, 186, 116)).r(8, 2, 8, 12, (232, 186, 116))
t.r(4, -2, 9, 0, (230, 236, 240)).r(5, -1, 6, -1, (60, 70, 86)).p(8, -1, (230, 70, 60)).ps([(3, -3), (12, -3), (3, 12), (12, 12)], (60, 68, 84)).r(6, -8, 7, -5, (150, 110, 56)).r(6, -8, 9, -8, (150, 110, 56)).outline()
Tile("o", "x").r(2, 9, 7, 13, (124, 126, 136)).r(8, 6, 13, 12, (146, 148, 158)).r(5, 12, 11, 14, (104, 106, 116)).r(8, 6, 13, 6, (184, 186, 196)).r(2, 9, 7, 9, (160, 162, 172)).r(11, 8, 13, 12, (116, 118, 128)).ps([(3, 14), (12, 13)], (90, 92, 102)).outline()
t = Tile("o", "L", tall=True).grad(2, -8, 13, 14, (112, 146, 178), (84, 114, 146)).r(2, -8, 13, -8, (150, 182, 212)).r(7, -7, 8, 14, (58, 84, 114)).r(2, 14, 13, 14, (58, 84, 114))
for x in (3, 9):
    t.r(x, -6, x + 3, -5, (58, 84, 114)).r(x, -3, x + 3, -3, (58, 84, 114))
t.ps([(6, 3), (9, 3)], (240, 240, 248)).ps([(4, 8), (11, 6)], (140, 172, 204)).outline()
t = Tile("o", "y").r(0, 4, 15, 6, (156, 104, 54)).r(0, 4, 15, 4, (196, 142, 86)).r(0, 10, 15, 12, (156, 104, 54)).r(0, 10, 15, 10, (196, 142, 86)).r(2, 2, 3, 14, (112, 74, 38)).r(12, 2, 13, 14, (112, 74, 38))
for k in range(0, 16, 4):
    t.r(k, 7, k + 1, 9, (238, 202, 64))
t.ps([(5, 5), (10, 11)], (90, 60, 30)).outline()
Tile("o", "e").r(3, 10, 6, 11, (124, 134, 150)).r(9, 6, 12, 7, (104, 112, 128)).r(8, 12, 9, 13, (144, 154, 170)).p(5, 5, (124, 134, 150)).ps([(3, 10), (9, 6)], (176, 186, 200)).outline()
t = Tile("o", "K", tall=True).r(0, 4, 15, 15, (70, 84, 110)).r(0, 4, 15, 4, (104, 120, 150)).r(0, 13, 15, 15, (52, 62, 84)).r(2, 6, 13, 11, (98, 114, 142)).ps([(3, 8), (6, 9), (9, 8), (12, 9)], (120, 230, 250)).ps([(4, 10), (10, 10)], (240, 200, 80))
t.r(0, -12, 15, 3, (52, 62, 84)).r(1, -11, 14, 2, (14, 24, 56))
for x in range(1, 15):
    yy = -5 + [0, -1, -3, -1, 0, 2, 4, 2, 0, -2, -1, 0, 1, 0][x - 1]
    t.p(x, yy, (120, 220, 255)).p(x, yy + 1, (50, 110, 170))
t.r(2, 0, 9, 0, (70, 170, 220))
t = Tile("o", "l", tall=True).r(7, -6, 8, 13, (70, 76, 92)).r(8, -6, 8, 13, (50, 56, 70)).r(5, 13, 10, 14, (70, 76, 92)).r(6, 12, 9, 12, (90, 96, 112))
t.r(4, -13, 11, -7, (250, 232, 150)).r(5, -12, 10, -8, (255, 250, 214)).r(4, -14, 11, -14, (90, 96, 112)).r(5, -15, 10, -15, (90, 96, 112)).r(4, -7, 11, -7, (190, 160, 90)).outline()
t = Tile("o", "q", tall=True).r(1, 6, 14, 13, (166, 132, 100)).r(1, 6, 14, 6, (206, 172, 136)).r(1, 7, 14, 7, (120, 94, 70)).r(2, 13, 3, 14, (120, 94, 70)).r(12, 13, 13, 14, (120, 94, 70))
t.ps([(4, 4), (5, 4), (4, 5)], (240, 180, 72)).ps([(8, 5), (9, 4), (9, 5)], (120, 200, 120)).ps([(12, 5)], (110, 160, 240))
t.r(1, -6, 2, 5, (120, 94, 70)).r(13, -6, 14, 5, (120, 94, 70))
for k in range(0, 16, 4):
    t.r(k, -10, k + 1, -5, (220, 90, 80)).r(k + 2, -10, k + 3, -5, (246, 240, 226))
t.r(0, -11, 15, -11, (255, 150, 140)).r(0, -4, 15, -4, (150, 60, 56)).outline()
t = Tile("o", "n", tall=True).r(4, 4, 5, 14, (110, 80, 54)).r(10, 4, 11, 14, (110, 80, 54)).r(1, -9, 14, 4, (150, 110, 74)).r(1, -9, 14, -9, (190, 148, 106)).r(2, -8, 13, 3, (206, 176, 130))
t.r(3, -7, 7, -3, (250, 246, 236)).r(9, -7, 12, -1, (250, 232, 150)).r(3, -1, 7, 2, (170, 210, 240)).ps([(5, -7), (10, -7), (5, -1)], (220, 70, 60)).ps([(4, -5), (5, -5), (6, -5), (4, 0), (5, 1)], (120, 120, 130)).outline()
t = Tile("o", "f").ell(4.5, 11, 3, 2, (60, 190, 170)).r(4, 12, 5, 14, (190, 220, 210)).ell(10.5, 8, 4, 2.5, (80, 220, 196)).r(10, 10, 11, 14, (200, 230, 220))
t.ps([(3, 10), (9, 7), (12, 8)], (200, 255, 240)).ps([(7, 13), (13, 13)], (60, 190, 170)).outline()
t = Tile("o", "v", tall=True)
for k in range(12):
    w = max(0, 4 - k // 3)
    t.r(7 - w, 13 - k, 8 + w, 13 - k, (112, 96, 90) if k % 3 else (132, 114, 104)).p(8 + w, 13 - k, (78, 66, 64))
t.r(4, 14, 11, 14, (78, 66, 64)).outline()
# ---- added after the environment pack. In the hand-made tiles.png these are placeholders in new slots.
OPEN_OBJ = "Eh"          # objects you can walk over: the hologram pad and stools
t = Tile("o", "E").ell(7.5, 11, 6.5, 3.6, (40, 56, 86)).ell(7.5, 11, 5.2, 2.6, (70, 190, 240)).ell(7.5, 11, 3.2, 1.4, (214, 248, 255))
t.r(5, 13, 10, 14, (60, 70, 92)).ps([(2, 11), (13, 11)], (120, 230, 255)).outline()
t = Tile("o", "d").r(0, 3, 15, 10, (176, 128, 84)).r(0, 3, 15, 3, (212, 166, 118)).r(0, 11, 15, 12, (126, 88, 58)).r(1, 13, 2, 14, (96, 66, 44)).r(13, 13, 14, 14, (96, 66, 44))
t.ell(4.5, 6.5, 2.5, 1.6, (244, 244, 246)).ell(4.5, 6.5, 1.3, 0.8, (214, 120, 70)).ell(11, 7, 2.5, 1.6, (244, 244, 246)).ps([(10, 7), (11, 6)], (110, 180, 100)).r(7, 5, 8, 6, (120, 190, 230))
t.r(0, 2, 15, 2, OUTLINE).r(0, 13, 0, 13, OUTLINE)
t = Tile("o", "h").ell(7.5, 9, 4.2, 2.3, (204, 112, 72)).ell(7, 8.4, 3, 1.3, (232, 146, 100)).r(5, 11, 5, 14, (110, 70, 50)).r(10, 11, 10, 14, (110, 70, 50)).outline()
t = Tile("o", "V").r(1, 3, 14, 14, (150, 156, 168)).r(1, 3, 14, 6, (92, 98, 112)).ell(5, 4.6, 2.2, 1.1, (244, 128, 54)).ell(10.5, 4.6, 2.2, 1.1, (56, 60, 72))
t.r(3, 8, 12, 12, (58, 64, 78)).r(5, 9, 10, 11, (255, 176, 80)).ps([(3, 7), (6, 7), (9, 7), (12, 7)], (230, 232, 238)).r(1, 13, 14, 14, (110, 116, 130)).r(3, 0, 7, 2, (196, 202, 212)).r(3, 0, 7, 0, (230, 234, 240)).outline()
t = Tile("o", "W").r(0, 3, 15, 9, (176, 182, 194)).r(0, 3, 15, 3, (214, 220, 230)).r(3, 5, 12, 8, (86, 150, 204)).r(3, 5, 12, 5, (60, 110, 160)).r(7, 0, 8, 4, (214, 220, 230)).r(8, 0, 10, 1, (214, 220, 230))
t.r(0, 10, 15, 14, (128, 134, 150)).r(7, 11, 7, 14, (100, 106, 122)).r(0, 2, 15, 2, OUTLINE).r(0, 15, 15, 15, OUTLINE)
t = Tile("o", "R", tall=True).grad(2, -10, 13, 14, (226, 232, 238), (190, 198, 208)).r(2, -10, 13, -10, (246, 250, 252)).r(12, -9, 13, 14, (164, 172, 184)).r(2, -1, 13, -1, (150, 158, 172))
t.r(10, -6, 10, -3, (120, 128, 142)).r(10, 2, 10, 6, (120, 128, 142)).ps([(5, -6)], (230, 90, 80)).ps([(7, -4)], (240, 200, 90)).r(2, 14, 13, 14, (140, 148, 162)).outline()
t = Tile("o", "m").r(1, 4, 14, 10, (196, 202, 212)).r(1, 4, 14, 4, (228, 232, 238)).r(1, 11, 14, 11, (140, 146, 160)).r(2, 12, 3, 14, (120, 126, 140)).r(12, 12, 13, 14, (120, 126, 140))
t.ell(5, 6.5, 3, 1.7, (214, 160, 90)).ps([(4, 6), (6, 6)], (240, 200, 140)).ps([(10, 6), (11, 7), (12, 6)], (110, 180, 100)).r(9, 9, 12, 9, (220, 224, 232)).outline()
t = Tile("o", "I").r(3, 0, 12, 15, (226, 206, 170)).r(3, 0, 4, 15, (248, 236, 208)).r(11, 0, 12, 15, (176, 142, 108)).r(2, 0, 2, 15, OUTLINE).r(13, 0, 13, 15, OUTLINE).ps([(6, 3), (7, 3)], (240, 180, 72)).ps([(8, 10)], (110, 160, 240))
T.save(art("tiles.png"))

# When tiles.png is hand-made art, the generator does not overwrite it. It only fills in:
#  - slots the artist left empty (tiles added to the game since the art was made), and
#  - the objects named here, whose hand-made versions did not fit how the game uses them.
KEEP_GENERATED = ["o", "C"]      # couch; counter (must join up side by side)
CLEAN_STRAYS = ["l"]             # hand-made objects with stray specks beside them: keep only the main shape


def patch_hand_tiles():
    if "tiles.png" not in HAND_EDITED:
        return
    try:
        from PIL import Image
    except ImportError:
        print("note: Pillow is not installed, so new tiles were not added to the hand-made tiles.png")
        return
    sheet_img = Image.open(art("tiles.png")).convert("RGBA")
    cell = sheet_img.width // TILE_COLUMNS
    gen = Image.new("RGBA", (T.w, T.h))
    gen.putdata([px for row_ in T.p for px in row_])
    slots = [(ch, base + v, False) for ch, base in TILE_FLOOR.items() for v in range(TILE_VARIANTS[ch])]
    slots += [(ch, base, ch in KEEP_GENERATED) for ch, base in TILE_OBJ.items()]
    changed = []
    for ch, idx, force in slots:
        box = (idx * cell, 0, idx * cell + cell, 2 * cell)
        if force or sheet_img.crop(box).getbbox() is None:
            piece = gen.crop((idx * 16, 0, idx * 16 + 16, 32)).resize((cell, 2 * cell), Image.NEAREST)
            if sheet_img.crop(box).tobytes() != piece.tobytes():
                sheet_img.paste(piece, box[:2])
                changed.append(idx)
    # Stray specks beside an object (pixels that bled in from the neighbouring picture) are removed.
    for ch in CLEAN_STRAYS:
        idx = TILE_OBJ[ch]
        box = (idx * cell, 0, idx * cell + cell, 2 * cell)
        part = sheet_img.crop(box)
        px = part.load()
        seen_px, comps = set(), []
        for y in range(part.height):
            for x in range(part.width):
                if px[x, y][3] > 0 and (x, y) not in seen_px:
                    stack, comp = [(x, y)], []
                    seen_px.add((x, y))
                    while stack:
                        cx, cy = stack.pop()
                        comp.append((cx, cy))
                        for dx in (-1, 0, 1):
                            for dy in (-1, 0, 1):
                                nb = (cx + dx, cy + dy)
                                if 0 <= nb[0] < part.width and 0 <= nb[1] < part.height and nb not in seen_px and px[nb][3] > 0:
                                    seen_px.add(nb)
                                    stack.append(nb)
                    comps.append(comp)
        comps.sort(key=len, reverse=True)
        if len(comps) > 1:
            for comp in comps[1:]:
                for (x, y) in comp:
                    px[x, y] = (0, 0, 0, 0)
            sheet_img.paste(part, box[:2])
            changed.append(idx)
    # Floors must cover their whole square. Where a hand-made floor has see-through pixels
    # (the fountain's planted centrepiece, for one), the generated floor goes underneath.
    for ch, base in TILE_FLOOR.items():
        for v in range(TILE_VARIANTS[ch]):
            idx = base + v
            box = (idx * cell, cell, idx * cell + cell, 2 * cell)
            part = sheet_img.crop(box)
            if part.getextrema()[3][0] < 255:
                under = gen.crop((idx * 16, 16, idx * 16 + 16, 32)).resize((cell, cell), Image.NEAREST)
                under.alpha_composite(part)
                if under.tobytes() != part.tobytes():
                    sheet_img.paste(under, box[:2])
                    changed.append(idx)
    if changed:
        sheet_img.save(art("tiles.png"))
        print("filled slots in the hand-made tiles.png:", changed)


patch_hand_tiles()

import math
# ================================================================ animated overlays (4 frames of 16x16 each)
# The game lays these over the still tile: screens flicker, fires burn, the core pulses, water moves.
def tile_part(table, ch, upper):
    im = Img(16, 16)
    im.blit(T, 0, 0, table[ch] * 16, 0 if upper else 16, 16, 16)
    return im


def fx_sheet(name, frames):
    im = Img(16 * len(frames), 16)
    for i, f in enumerate(frames):
        im.blit(f, i * 16, 0)
    im.save(art(name + ".png"))


CYAN, CYAND, SCREEN = (110, 220, 250), (50, 110, 170), (16, 34, 66)
frames = []
for f in range(4):      # console: lines of text typing
    im = tile_part(TILE_OBJ, "k", True)
    im.rect(3, 11, 12, 15, SCREEN)
    im.rect(4, 12, 3 + [6, 8, 4, 7][f], 12, CYAN)
    im.rect(4, 14, 3 + [8, 5, 7, 3][f], 14, CYAN)
    if f % 2 == 0:
        im.px(4 + [8, 5, 7, 3][f], 14, (255, 255, 255))
    frames.append(im)
fx_sheet("fx_console", frames)
frames = []
for f in range(4):      # Sara's big display: a moving signal
    im = tile_part(TILE_OBJ, "K", True)
    im.rect(1, 5, 14, 15, (14, 24, 56))
    for x in range(1, 15):
        yy = 10 + int(round(3 * math.sin((x + f * 3.5) / 2.2)))
        im.px(x, yy, (120, 220, 255)); im.px(x, yy + 1, CYAND)
    im.rect(2, 15, 2 + [5, 7, 3, 6][f], 15, (70, 170, 220))
    frames.append(im)
fx_sheet("fx_display", frames)
frames = []
for f in range(4):      # furnace: fire
    im = tile_part(TILE_OBJ, "F", False)
    im.rect(4, 7, 10, 12, (255, 140, 44))
    im.rect(5, 9 + [0, 1, 0, 1][f], 9, 12, (255, 220, 110))
    im.rect(6, 11 - [1, 0, 1, 0][f], 8, 12, (255, 250, 210))
    for x in ([4, 7, 10], [5, 8], [4, 6, 9], [6, 10])[f]:
        im.px(x, 7, (36, 28, 30))
    for x in ([5, 9], [4, 10], [7], [5, 8])[f]:
        im.px(x, 8, (255, 190, 80))
    frames.append(im)
fx_sheet("fx_furnace", frames)
frames = []
for f in range(4):      # power core: a slow pulse
    im = tile_part(TILE_OBJ, "G", False)
    k = [0.0, 0.4, 0.9, 0.4][f]
    im.rect(3, 3, 12, 12, mixc((70, 200, 204), (120, 235, 235), k))
    im.rect(5, 5, 10, 10, mixc((150, 245, 235), (225, 255, 252), k))
    im.rect(6, 6, 9, 9, (240, 255, 255))
    if f == 2:
        im.rect(7, 4, 8, 11, (255, 255, 255)); im.rect(4, 7, 11, 8, (255, 255, 255))
    frames.append(im)
fx_sheet("fx_core", frames)
frames = []
for f in range(4):      # fountain water: highlights drifting
    im = Img(16, 16, (70, 150, 210, 255))
    rnd = random.Random(900)
    for _ in range(40):
        im.px(rnd.randrange(16), rnd.randrange(16), rnd.choice([(96, 176, 228), (56, 130, 192), (82, 162, 218)]))
    for (x, y, w) in [(2, 4, 5), (9, 10, 5), (11, 2, 3), (4, 13, 3)]:
        for i in range(w):
            im.px((x + i + f * 2) % 16, y + (1 if f % 2 and i == 0 else 0), (190, 230, 250))
    frames.append(im)
fx_sheet("fx_water", frames)

# a soft round glow, used for lamps and screens
GL = Img(64, 64)
for y in range(64):
    for x in range(64):
        d = ((x - 31.5) ** 2 + (y - 31.5) ** 2) ** 0.5 / 31.5
        if d < 1.0:
            GL.px(x, y, (255, 255, 255, int(150 * (1.0 - d) ** 2)))
GL.save(art("glow.png"))

# ================================================================ character sprites (16x32, Stardew proportions)
EYE = (30, 24, 30)


def draw_person(im, ox, oy, c, d="down", step=0, wide=False, short=False, style="short"):
    """One 16x32 frame. d: down/up/left/right. step: 0 standing, 1 and 2 walking (arms swing against the legs)."""
    sk, hr, tp, lg = c["skin"], c["hair"], c["top"], c["legs"]
    sh, arm = c.get("shoes", (50, 44, 56)), c.get("arm", c["top"])
    skd, hrd, hrl = dk(sk, 0.86), dk(hr, 0.78), lt(hr, 1.25)

    def R(x0, y0, x1, y1, col):
        im.rect(ox + x0, oy + y0, ox + x1, oy + y1, col)

    im.ell(ox + 7.5, oy + 30, 5, 1.6, (0, 0, 0, 70))
    hy = 3 if short else 0
    front = d in ("down", "up")
    # legs
    if front:
        l0 = 28 if step == 1 else 29
        r0 = 28 if step == 2 else 29
        R(5, 25, 7, l0, lg); R(8, 25, 10, r0, dk(lg, 0.88)); R(5, l0, 7, l0, sh); R(8, r0, 10, r0, sh)
    elif step == 0:
        R(6, 25, 9, 29, lg); R(8, 25, 9, 28, dk(lg, 0.88)); R(6, 29, 9, 29, sh)
    elif step == 1:
        R(6, 25, 9, 26, lg); R(4, 26, 6, 29, lg); R(9, 26, 11, 29, dk(lg, 0.88)); R(4, 29, 6, 29, sh); R(9, 29, 11, 29, sh)
    else:
        R(6, 25, 9, 26, lg); R(7, 26, 8, 29, lg); R(7, 29, 8, 29, sh)
    # torso
    bx0, bx1 = (4, 11) if wide else (5, 10)
    R(bx0, 16 + hy, bx1, 24, tp); R(bx1, 17 + hy, bx1, 24, dk(tp)); R(bx0, 24, bx1, 24, dk(tp, 0.72)); R(bx0 + 1, 17 + hy, bx0 + 1, 20, lt(tp, 1.12))
    if d == "down":
        R(7, 16 + hy, 8, 16 + hy, sk)
    # arms
    if front:
        ls = 1 if step == 2 else 0
        rs = 1 if step == 1 else 0
        R(bx0 - 2, 17 + hy + ls, bx0 - 1, 22 + ls, arm); R(bx0 - 2, 23 + ls, bx0 - 1, 23 + ls, sk)
        R(bx1 + 1, 17 + hy + rs, bx1 + 2, 22 + rs, dk(arm)); R(bx1 + 1, 23 + rs, bx1 + 2, 23 + rs, skd)
    else:
        ax = {0: 7, 1: 5, 2: 9}[step]
        R(ax, 17 + hy, ax + 1, 22, dk(arm)); R(ax, 23, ax + 1, 23, sk)
    # head, rounded
    R(5, 6 + hy, 10, 15 + hy, sk); R(4, 7 + hy, 11, 14 + hy, sk); R(3, 8 + hy, 12, 13 + hy, sk)
    R(12, 9 + hy, 12, 13 + hy, skd); R(11, 14 + hy, 11, 14 + hy, skd); R(6, 15 + hy, 10, 15 + hy, skd)
    if style != "bald":
        R(4, 4 + hy, 11, 4 + hy, hr); R(3, 5 + hy, 12, 8 + hy, hr); R(5, 5 + hy, 8, 5 + hy, hrl); R(4, 6 + hy, 5, 6 + hy, hrl); R(11, 5 + hy, 12, 8 + hy, hrd)
        if d == "down":
            R(3, 9 + hy, 3, 10 + hy, hr); R(12, 9 + hy, 12, 10 + hy, hrd); R(4, 9 + hy, 6, 9 + hy, hr); R(10, 9 + hy, 11, 9 + hy, hrd)
        elif d == "up":
            R(3, 9 + hy, 12, 13 + hy, hr); R(11, 9 + hy, 12, 13 + hy, hrd); R(4, 14 + hy, 11, 14 + hy, hrd)
        elif d == "left":
            R(8, 9 + hy, 12, 13 + hy, hr); R(11, 9 + hy, 12, 13 + hy, hrd)
        else:
            R(3, 9 + hy, 7, 13 + hy, hr)
        if style == "long":
            if front:
                R(2, 7 + hy, 2, 19 + hy, hr); R(13, 7 + hy, 13, 19 + hy, hrd)
            if d == "up":
                R(3, 14 + hy, 12, 19 + hy, hr); R(5, 15 + hy, 6, 18 + hy, hrl)
            if d == "left":
                R(9, 14 + hy, 13, 19 + hy, hr)
            if d == "right":
                R(2, 14 + hy, 6, 19 + hy, hr)
    if d == "down":
        R(5, 10 + hy, 5, 11 + hy, EYE); R(10, 10 + hy, 10, 11 + hy, EYE); R(7, 13 + hy, 8, 13 + hy, dk(sk, 0.7))
        R(4, 12 + hy, 4, 12 + hy, mixc(sk, (240, 110, 110), 0.35)); R(11, 12 + hy, 11, 12 + hy, mixc(sk, (240, 110, 110), 0.35))
    elif d == "left":
        R(4, 10 + hy, 4, 11 + hy, EYE)
    elif d == "right":
        R(11, 10 + hy, 11, 11 + hy, EYE)


DIRS = ["down", "up", "left", "right"]


def sheet(c, overlay=None, **kw):
    """A full character sheet: 4 columns (down, up, left, right) x 3 rows (standing, step A, step B).
    overlay(R, d) adds species details; it is written for facing left and mirrored for right."""
    im = Img(64, 96)
    for col, d in enumerate(DIRS):
        for step in range(3):
            ox, oy = col * 16, step * 32
            draw_person(im, ox, oy, c, d, step, **kw)
            if overlay:
                def R(x0, y0, x1, y1, colr, ox=ox, oy=oy, d=d):
                    if d == "right":
                        x0, x1 = 15 - x1, 15 - x0
                    im.rect(ox + x0, oy + y0, ox + x1, oy + y1, colr)
                overlay(R, d)
            outline_img(im, ox, oy, 16, 32)
    return im


def sheet_from(small, mirror_left=False, hop=True):
    """A sheet for creatures drawn once (16x24): they hop instead of stepping."""
    im = Img(64, 96)
    for col in range(4):
        src = small
        if mirror_left and col == 2:
            src = Img(small.w, small.h)
            for y in range(small.h):
                for x in range(small.w):
                    src.p[y][x] = small.p[y][small.w - 1 - x]
        for step in range(3):
            im.blit(src, col * 16, step * 32 + 32 - small.h - (1 if (step and hop) else 0))
    return im


# player
PC = {"skin": (238, 192, 152), "hair": (86, 54, 38), "top": (58, 104, 180), "legs": (52, 56, 78)}


def ov_player(R, d):
    R(5, 21, 10, 21, (232, 196, 90))
    if d == "down":
        R(6, 17, 9, 18, (236, 236, 240)); R(7, 19, 8, 20, (236, 236, 240))


P = sheet(PC, ov_player)
P.save(art("player.png"))

SPR = {}

# Sara (hologram, no outline, does not walk)
S = Img(16, 32)
S.ell(7.5, 30, 5, 1.6, (120, 215, 255, 90))
S.rect(4, 29, 11, 31, (90, 100, 120)); S.rect(5, 28, 10, 28, (160, 230, 255))
for y in range(4, 28):
    c = (120, 215, 255, 220 if y % 2 == 0 else 140)
    if y <= 14:
        S.rect(4, y, 11, y, c)
        if 6 <= y <= 13:
            S.rect(3, y, 12, y, c)
    elif y <= 15:
        S.rect(7, y, 8, y, c)
    else:
        half = 3 + (y - 16) // 4
        S.rect(8 - half, y, 7 + half, y, c)
S.rect(5, 10, 5, 11, (255, 255, 255)); S.rect(10, 10, 10, 11, (255, 255, 255)); S.rect(4, 5, 11, 6, (190, 240, 255, 230))
SPR["sara"] = sheet_from(S, hop=False)

# Tikka (Arachnay)
K = Img(16, 24)
BODY, DARK, LEGC = (124, 80, 168), (78, 48, 112), (64, 40, 92)
K.ell(7.5, 22, 6, 1.6, (0, 0, 0, 70))
K.rect(4, 12, 11, 19, BODY); K.rect(5, 11, 10, 20, BODY); K.rect(5, 18, 10, 20, DARK); K.rect(10, 12, 11, 19, DARK); K.rect(5, 12, 6, 13, lt(BODY))
K.rect(4, 3, 11, 10, BODY); K.rect(5, 2, 10, 11, BODY); K.rect(11, 4, 11, 10, DARK); K.rect(5, 3, 7, 3, lt(BODY))
for (x, y) in [(5, 5), (7, 4), (8, 4), (10, 5), (6, 7), (9, 7)]:
    K.px(x, y, (255, 232, 124))
K.rect(6, 9, 6, 10, DARK); K.rect(9, 9, 9, 10, DARK)
for y in [12, 14, 16, 18]:
    K.rect(1, y + 1, 3, y + 1, LEGC); K.px(1, y + 2, LEGC); K.px(3, y, LEGC)
    K.rect(12, y + 1, 14, y + 1, LEGC); K.px(14, y + 2, LEGC); K.px(12, y, LEGC)
K.rect(12, 9, 14, 10, (244, 146, 54)); K.px(14, 8, (210, 218, 228))
outline_img(K)
SPR["tikka"] = sheet_from(K, mirror_left=True)

# Bram (Moogli)
B = Img(16, 24)
GREEN, GDARK, VEST, BELLY = (96, 178, 96), (58, 124, 66), (220, 176, 64), (196, 224, 164)
B.ell(7.5, 22, 6, 1.6, (0, 0, 0, 70))
B.rect(2, 6, 13, 12, GREEN); B.rect(3, 5, 12, 13, GREEN); B.rect(12, 7, 13, 12, GDARK); B.rect(3, 6, 6, 6, lt(GREEN))
B.rect(2, 2, 5, 5, GREEN); B.rect(10, 2, 13, 5, GREEN)
B.rect(3, 3, 4, 4, (255, 255, 255)); B.rect(11, 3, 12, 4, (255, 255, 255)); B.px(4, 4, EYE); B.px(11, 4, EYE)
B.rect(4, 10, 11, 10, GDARK)
B.rect(4, 14, 11, 19, VEST); B.rect(6, 14, 9, 19, BELLY); B.rect(11, 14, 11, 19, dk(VEST)); B.rect(4, 14, 4, 19, lt(VEST))
B.rect(2, 17, 3, 19, GREEN); B.rect(12, 17, 13, 19, GREEN)
B.rect(2, 20, 5, 21, GREEN); B.rect(10, 20, 13, 21, GREEN); B.rect(2, 21, 6, 21, GDARK); B.rect(9, 21, 13, 21, GDARK)
outline_img(B)
SPR["bram"] = sheet_from(B)

# Freya (human)
FSK = (240, 200, 170)


def ov_freya(R, d):
    if d == "down":
        for (x, y) in [(6, 19), (9, 22), (7, 18), (5, 21)]:
            R(x, y, x, y, (96, 96, 100))


SPR["freya"] = sheet({"skin": FSK, "hair": (244, 222, 140), "top": (212, 212, 206), "legs": (74, 84, 108), "arm": FSK}, ov_freya, style="long")

# Job (human miner)
JSK = (112, 74, 52)


def ov_job(R, d):
    R(2, 8, 13, 8, (200, 166, 44))
    if d == "down":
        R(7, 5, 8, 6, (255, 255, 240)); R(5, 19, 10, 19, (240, 230, 120))
    elif d == "up":
        R(5, 19, 10, 19, (240, 230, 120))
    else:
        R(3, 6, 3, 7, (255, 255, 240))


SPR["job"] = sheet({"skin": JSK, "hair": (238, 202, 64), "top": (220, 134, 52), "legs": (62, 62, 74), "arm": JSK}, ov_job, wide=True)

# Evarra (Vuultam)
ESK = (112, 192, 152)


def ov_evarra(R, d):
    if d in ("down", "up"):
        R(4, 25, 11, 27, (124, 92, 154)); R(11, 25, 11, 27, (96, 70, 122))
    else:
        R(5, 25, 10, 27, (124, 92, 154))
    if d == "down":
        for (x, y) in [(3, 12), (12, 12), (4, 13), (11, 13), (3, 10), (12, 10), (4, 14), (11, 14)]:
            R(x, y, x, y, (154, 112, 196))


SPR["evarra"] = sheet({"skin": ESK, "hair": (246, 246, 250), "top": (238, 234, 222), "legs": (124, 92, 154), "arm": ESK}, ov_evarra, style="long")


def zaash(R, d, scale, snout):
    R(4, 5, 11, 5, dk(scale))
    for x in (4, 7, 11):
        R(x, 4, x, 4, dk(scale))
    if d == "down":
        R(4, 11, 11, 14, snout); R(4, 14, 11, 14, dk(snout, 0.8)); R(6, 12, 6, 12, dk(scale, 0.5)); R(9, 12, 9, 12, dk(scale, 0.5))
        R(5, 8, 5, 9, (244, 214, 84)); R(10, 8, 10, 9, (244, 214, 84)); R(5, 9, 5, 9, EYE); R(10, 9, 10, 9, EYE)
        R(5, 10, 5, 10, scale); R(10, 10, 10, 10, scale)
    elif d == "up":
        R(7, 6, 8, 14, dk(scale))
    else:
        R(1, 11, 6, 14, snout); R(1, 14, 6, 14, dk(snout, 0.8)); R(2, 12, 2, 12, dk(scale, 0.5))
        R(4, 8, 4, 9, (244, 214, 84)); R(4, 9, 4, 9, EYE); R(4, 10, 4, 10, scale)


# Tar'Besh (Zaa'sh cleric)
ZG, PURP, GOLD = (124, 154, 84), (112, 62, 152), (224, 184, 64)


def ov_tar(R, d):
    x0, x1 = (3, 12) if d in ("down", "up") else (4, 11)
    R(x0, 16, x1, 29, PURP); R(x1, 16, x1, 29, dk(PURP)); R(x0, 16, x0, 28, lt(PURP)); R(x0, 29, x1, 29, GOLD)
    if d == "down":
        R(7, 16, 8, 29, GOLD)
        for (x, y) in [(5, 21), (10, 25), (5, 27), (10, 19), (4, 24), (9, 28)]:
            R(x, y, x, y, (80, 44, 110))
    zaash(R, d, ZG, (164, 190, 114))


SPR["tarbesh"] = sheet({"skin": ZG, "hair": ZG, "top": PURP, "legs": PURP, "arm": PURP}, ov_tar, style="bald")

# Vzz'ket (Zaa'sh warrior)
VG, ARM, RED = (92, 144, 94), (96, 102, 118), (196, 62, 52)


def ov_vzz(R, d):
    if d in ("down", "up"):
        R(2, 16, 3, 18, RED); R(12, 16, 13, 18, RED)
        R(14, 4, 14, 29, (156, 114, 72)); R(14, 1, 14, 3, (224, 228, 238))
    else:
        R(1, 6, 1, 29, (156, 114, 72)); R(1, 3, 1, 5, (224, 228, 238))
    if d == "down":
        R(4, 20, 11, 20, RED); R(5, 17, 10, 18, lt(ARM))
    zaash(R, d, VG, (134, 180, 128))


SPR["vzzket"] = sheet({"skin": VG, "hair": VG, "top": ARM, "legs": (54, 58, 70), "arm": VG}, ov_vzz, style="bald")

# Jasper (Ervani)
OR, CREAM = (232, 142, 62), (250, 240, 225)


def ov_jasper(R, d):
    R(3, 4, 5, 7, OR); R(10, 4, 12, 7, OR); R(3, 4, 3, 4, (70, 44, 34)); R(12, 4, 12, 4, (70, 44, 34))
    if d == "down":
        R(4, 6, 4, 6, CREAM); R(11, 6, 11, 6, CREAM)
        R(5, 14, 10, 17, CREAM); R(7, 14, 8, 14, EYE); R(7, 16, 8, 16, (190, 150, 130))
        R(13, 21, 14, 26, OR); R(13, 20, 14, 21, CREAM)
    elif d == "up":
        R(7, 22, 8, 27, OR); R(7, 27, 8, 28, CREAM)
    else:
        R(1, 14, 5, 17, CREAM); R(1, 14, 1, 14, EYE)
        R(12, 21, 14, 25, OR); R(14, 20, 14, 21, CREAM)


SPR["jasper"] = sheet({"skin": OR, "hair": OR, "top": CREAM, "legs": (124, 88, 62), "arm": OR}, ov_jasper, short=True)

# Zaas (Scyldari)
TEAL, TEALD = (64, 168, 178), (42, 124, 136)
Q = Img(16, 24)
Q.ell(7.5, 22, 5, 1.6, (0, 0, 0, 70))
Q.rect(4, 4, 11, 13, TEAL); Q.rect(5, 3, 10, 13, TEAL); Q.rect(11, 5, 11, 13, TEALD); Q.rect(5, 5, 6, 5, lt(TEAL))
Q.rect(5, 7, 6, 9, (255, 255, 255)); Q.rect(9, 7, 10, 9, (255, 255, 255)); Q.rect(6, 8, 6, 9, EYE); Q.rect(9, 8, 9, 9, EYE)
for i, x in enumerate([4, 6, 8, 10]):
    Q.rect(x, 14, x + 1, 21, TEAL if i % 2 == 0 else TEALD)
Q.px(3, 21, TEALD); Q.px(12, 21, TEALD)
Q.rect(2, 3, 13, 4, (116, 80, 52)); Q.rect(4, 0, 11, 2, (116, 80, 52)); Q.rect(4, 2, 11, 2, (232, 194, 72)); Q.rect(4, 0, 11, 0, (150, 110, 76))
outline_img(Q)
SPR["zaas"] = sheet_from(Q)

for k, im in SPR.items():
    im.save(art("npc_%s.png" % k))

# ---------------------------------------------------------------- cave creatures (2 walking frames of 16x16, facing left)
BUG = Img(32, 16)
for f in range(2):
    o = f * 16
    BUG.ell(o + 7.5, 14, 5.5, 1.5, (0, 0, 0, 70))
    BUG.ell(o + 8.5, 9, 5, 3.6, (66, 44, 78)); BUG.ell(o + 8, 8, 4, 2.4, (98, 66, 112)); BUG.rect(o + 6, 6, o + 8, 6, (150, 110, 164))
    BUG.rect(o + 2, 8, o + 4, 11, (52, 34, 62)); BUG.px(o + 2, 9, (240, 70, 60)); BUG.px(o + 1, 11, (200, 190, 200)); BUG.px(o + 1, 12, (200, 190, 200))
    BUG.rect(o + 8, 6, o + 8, 12, (52, 34, 62))
    for i, x in enumerate([5, 8, 11]):
        y = 13 if (i + f) % 2 == 0 else 12
        BUG.rect(o + x, 11, o + x, y, (40, 26, 48)); BUG.px(o + x - 1, y, (40, 26, 48))
    outline_img(BUG, o, 0, 16, 16)
BUG.save(art("enemy_bug.png"))
LIZ = Img(32, 16)
LG, LD, LL = (104, 134, 92), (70, 96, 66), (150, 176, 126)
for f in range(2):
    o = f * 16
    LIZ.ell(o + 7.5, 14, 6.5, 1.5, (0, 0, 0, 70))
    LIZ.rect(o + 4, 8, o + 11, 11, LG); LIZ.rect(o + 4, 8, o + 11, 8, LL); LIZ.rect(o + 4, 11, o + 11, 11, LD)
    LIZ.rect(o + 1, 7, o + 4, 10, LG); LIZ.rect(o + 1, 7, o + 3, 7, LL); LIZ.px(o + 2, 8, (250, 220, 90)); LIZ.px(o + 0, 9, LD)
    LIZ.rect(o + 11, 9, o + 13, 10, LG); LIZ.rect(o + 13, 10 - f, o + 15, 10 - f, LD)
    for x in (5, 7, 9):
        LIZ.px(o + x, 7, (190, 120, 70))
    for i, x in enumerate([4, 10]):
        y = 13 if (i + f) % 2 == 0 else 12
        LIZ.rect(o + x, 11, o + x, y, LD); LIZ.px(o + x - 1, y, LD)
    outline_img(LIZ, o, 0, 16, 16)
LIZ.save(art("enemy_lizard.png"))

# ================================================================ portraits (64x64, six expressions each)
# Each portrait file is six 64x64 pictures side by side, in this order.
# A dialogue line can start with one of these in square brackets, e.g. "[happy] Good morning!"
EMOTES = ["neutral", "happy", "sad", "surprised", "love", "angry"]
PORT = {}
WHITE, LASH, PINK = (250, 250, 252), (40, 30, 44), (245, 120, 130)


def backdrop(c):
    im = Img(64, 64)
    for y in range(64):
        im.rect(0, y, 63, y, mixc(lt(c, 1.25), dk(c, 0.75), y / 63))
    return im


def shoulders(im, cloth, top=48, neck=None):
    for y in range(top, 64):
        hw = min(28, 12 + int((y - top) * 1.7))
        im.rect(32 - hw, y, 31 + hw, y, cloth)
        im.rect(31 + hw - 6, y, 31 + hw, y, dk(cloth, 0.8))
        im.rect(32 - hw, y, 33 - hw, y, lt(cloth, 1.14))
    im.rect(20, top, 43, top, lt(cloth, 1.14))
    if neck:
        for i in range(7):
            im.rect(32 - (6 - i), top + i, 31 + (6 - i), top + i, neck)
            im.px(31 - (6 - i), top + i, dk(cloth, 0.7)); im.px(32 + (6 - i), top + i, dk(cloth, 0.7))


def eye(im, cx, cy, e, iris, r=3, white=WHITE, slit=False):
    if e in ("happy", "love"):
        for dx in range(-r, r + 1):
            im.px(cx + dx, cy - 1 + (abs(dx) + 1) // 2, LASH)
            im.px(cx + dx, cy + (abs(dx) + 1) // 2, LASH) if abs(dx) < 2 else None
        return
    h = {"neutral": 2, "sad": 2, "surprised": 3, "angry": 1}[e] + (r - 3)
    im.ell(cx, cy, r + 0.5, h + 0.5, white)
    ir = 1.2 if e == "surprised" else min(2.0 + (r - 3) * 0.6, h + 0.4)
    im.ell(cx, cy, ir, min(h, ir + 0.4), iris)
    if slit:
        im.rect(cx, cy - h + 1, cx, cy + h - 1, (20, 16, 24))
    else:
        im.px(cx, cy, (20, 16, 24))
    im.px(cx - 1, cy - 1, (255, 255, 255))
    for dx in range(-r, r + 1):
        im.px(cx + dx, cy - h - (0 if abs(dx) < r else -1), LASH)
    if e == "angry":
        im.rect(cx - r, cy - h, cx + r, cy - h, LASH)
    if e == "sad":
        im.px(cx - r + 1, cy + h + 1, (120, 190, 250)); im.px(cx - r + 1, cy + h + 2, (120, 190, 250))


def brow(im, cx, cy, e, side, col, thick=1, w=3):
    slope = {"sad": -1.6, "angry": 2.0}.get(e, 0.0)
    lift = {"surprised": -2, "happy": -1, "love": -1}.get(e, 0)
    for dx in range(-w, w + 1):
        inner = -dx * side
        y = cy + lift + int(round(slope * inner / w))
        for t in range(thick):
            im.px(cx + dx, y + t, col)


def mouth(im, cx, cy, e, c=(120, 50, 60), w=4):
    if e == "neutral":
        im.rect(cx - w + 1, cy, cx + w - 1, cy, c); im.px(cx - w, cy - 1, c); im.px(cx + w, cy - 1, c)
    elif e == "happy":
        im.rect(cx - w, cy - 1, cx + w, cy - 1, c)
        for y in range(0, 3):
            hw = w - y - (1 if w > 6 else 0) * y
            im.rect(cx - max(1, hw), cy + y, cx + max(1, hw), cy + y, (150, 50, 60))
        im.rect(cx - w + 1, cy, cx + w - 1, cy, WHITE)
    elif e == "love":
        im.rect(cx - w + 2, cy, cx + w - 2, cy, c); im.px(cx - w + 1, cy - 1, c); im.px(cx + w - 1, cy - 1, c)
    elif e == "sad":
        im.rect(cx - w + 1, cy, cx + w - 1, cy, c); im.px(cx - w, cy + 1, c); im.px(cx + w, cy + 1, c)
    elif e == "surprised":
        im.ell(cx, cy + 1, 2.2, 2.8, (110, 40, 50))
    else:
        im.rect(cx - w, cy - 1, cx + w, cy + 1, c); im.rect(cx - w + 1, cy, cx + w - 1, cy, WHITE)
        for x in range(cx - w + 2, cx + w, 2):
            im.px(x, cy, c)


def blush(im, e, spots, base):
    if e in ("love", "happy"):
        k = 0.55 if e == "love" else 0.25
        for (x, y) in spots:
            im.ell(x, y, 3.5, 1.8, mixc(base, PINK, k))


def marks(im, e):
    if e == "angry":
        for (x0, y0, x1, y1) in [(49, 8, 51, 9), (54, 8, 56, 9), (52, 5, 53, 7), (52, 10, 53, 12)]:
            im.rect(x0, y0, x1, y1, (232, 60, 60))
    elif e == "surprised":
        im.rect(53, 4, 54, 10, (255, 255, 255)); im.rect(53, 12, 54, 13, (255, 255, 255))
    elif e == "love":
        for (x0, y0, x1, y1) in [(49, 6, 51, 8), (53, 6, 55, 8), (49, 8, 55, 9), (50, 10, 54, 10), (51, 11, 53, 11), (52, 12, 52, 12)]:
            im.rect(x0, y0, x1, y1, (245, 110, 140))
        im.px(50, 7, (255, 200, 210))
    elif e == "happy":
        im.rect(52, 5, 52, 11, (255, 236, 150)); im.rect(49, 8, 55, 8, (255, 236, 150))


def strip(frames, name):
    sheet_im = Img(64 * len(frames), 64)
    for i, f in enumerate(frames):
        sheet_im.blit(f, i * 64, 0)
    PORT[name] = sheet_im


def human(bg, skin, hair, cloth, iris, style="short", extra=None, post=None):
    frames = []
    sd, hd, hl = dk(skin, 0.84), dk(hair, 0.72), lt(hair, 1.25)
    for e in EMOTES:
        im = backdrop(bg)
        if style == "long":
            im.ell(32, 30, 21, 23, hd); im.rect(11, 30, 52, 60, hd); im.rect(13, 30, 21, 60, hair); im.rect(15, 32, 16, 58, hl); im.rect(44, 30, 50, 60, hair)
        shoulders(im, cloth, 48, skin)
        im.rect(27, 38, 36, 48, sd); im.rect(27, 38, 31, 48, skin)
        im.ell(17.5, 29, 2.5, 3.5, sd); im.ell(46.5, 29, 2.5, 3.5, sd)
        im.ell(32, 27, 14.5, 16.5, sd); im.ell(30.8, 26.5, 13, 16, skin)
        if post:
            post(im, skin, sd)
        if style == "helmet":
            im.ell(32, 15, 17, 10, dk(hair, 0.85)); im.ell(31, 14, 15.5, 9, hair); im.rect(13, 18, 50, 21, dk(hair, 0.8)); im.rect(13, 18, 50, 18, hl)
            im.ell(32, 12, 4, 3.5, (255, 255, 240)); im.ell(32, 12, 2, 1.8, (255, 255, 255))
        elif style != "bald":
            im.ell(32, 13, 16, 8, hd); im.ell(31, 12.5, 14.5, 7.5, hair)
            for y in range(8, 26):
                for x in range(16, 49):
                    if ((x - 32) / 15.5) ** 2 + ((y - 25) / 17.5) ** 2 <= 1.0 and y <= 18 + 3.2 * abs((x - 27) / 11.0) ** 1.6:
                        im.px(x, y, hd if x > 42 else hair)
            for x in range(21, 37):
                im.px(x, 10 + abs(x - 28) // 5, hl); im.px(x, 11 + abs(x - 28) // 5, hl) if x % 3 else None
        brow(im, 25, 22, e, -1, dk(hair, 0.6) if style not in ("bald", "helmet") else dk(skin, 0.5))
        brow(im, 39, 22, e, 1, dk(hair, 0.6) if style not in ("bald", "helmet") else dk(skin, 0.5))
        eye(im, 25, 28, e, iris); eye(im, 39, 28, e, iris)
        im.px(32, 33, sd); im.px(33, 34, sd); im.px(32, 34, sd)
        blush(im, e, [(22, 34), (42, 34)], skin)
        mouth(im, 32, 39, e, dk(skin, 0.5))
        if extra:
            extra(im, e)
        marks(im, e)
        frames.append(im)
    return frames


# Freya
def freya_extra(im, e):
    for (x, y) in [(22, 32), (24, 33), (40, 33), (42, 32), (26, 32)]:
        im.px(x, y, (206, 150, 122))
    im.rect(18, 56, 20, 57, (90, 90, 96)); im.rect(42, 59, 45, 60, (90, 90, 96)); im.px(36, 24, (110, 110, 116)); im.px(37, 25, (110, 110, 116))


strip(human((84, 96, 112), (240, 200, 170), (244, 222, 140), (205, 205, 200), (60, 150, 100), "long", freya_extra), "freya")
# Job
strip(human((76, 64, 58), (112, 74, 52), (238, 202, 64), (220, 134, 52), (60, 40, 30), "helmet"), "job")


# Evarra: scales shading from green at the brow to purple at the chin
def evarra_post(im, skin, sd):
    for y in range(8, 46):
        k = min(1.0, max(0.0, (y - 12) / 30.0))
        for x in range(14, 50):
            p = im.p[y][x][:3]
            if p == skin or p == sd:
                c = mixc((112, 196, 150), (160, 110, 200), k)
                if p == sd:
                    c = dk(c, 0.84)
                if (x + y * 2) % 6 == 0:
                    c = lt(c, 1.14)
                im.px(x, y, c)


strip(human((96, 124, 112), (112, 196, 150), (246, 246, 250), (238, 234, 222), (130, 70, 170), "long", None, evarra_post), "evarra")

# Sara: a hologram
frames = human((20, 30, 60), (170, 220, 240), (120, 190, 230), (90, 170, 220), (40, 90, 160), "long")
for im in frames:
    for y in range(64):
        for x in range(64):
            p = im.p[y][x]
            lum = (p[0] + p[1] + p[2]) / 765.0
            c = mixc((8, 22, 60), (190, 242, 255), lum ** 1.2)
            if y % 2:
                c = dk(c, 0.8)
            im.px(x, y, c)
strip(frames, "sara")


def zaash_portrait(bg, scale, cloth, trim, armor):
    frames = []
    sd, sn = dk(scale, 0.8), lt(scale, 1.2)
    for e in EMOTES:
        im = backdrop(bg)
        shoulders(im, cloth, 47)
        im.rect(18, 47, 45, 49, trim)
        if armor:
            im.ell(13, 55, 8, 5, trim); im.ell(50, 55, 8, 5, dk(trim, 0.8)); im.rect(26, 52, 37, 58, lt(cloth, 1.2))
        else:
            im.rect(30, 49, 33, 63, trim)
            for (x, y) in [(20, 58), (42, 55), (24, 61), (46, 61)]:
                im.rect(x, y, x + 1, y, dk(cloth, 0.7))
        im.rect(25, 36, 38, 48, sd)
        for (x, h) in [(21, 5), (26, 8), (32, 10), (38, 8), (43, 5)]:
            for i in range(h):
                im.rect(x - (h - i) // 3, 13 - i, x + (h - i) // 3, 13 - i, dk(scale, 0.66))
        im.ell(32, 24, 15.5, 13.5, sd); im.ell(31, 23.5, 14, 13, scale)
        im.ell(32, 38, 12.5, 9.5, sd); im.ell(31.5, 37.5, 11.5, 9, sn)
        im.rect(27, 34, 28, 35, dk(scale, 0.5)); im.rect(36, 34, 37, 35, dk(scale, 0.5))
        for (x, y) in [(24, 14), (30, 13), (38, 15), (20, 20), (44, 21)]:
            im.px(x, y, sn)
        brow(im, 23, 19, e, -1, dk(scale, 0.55), 2, 4); brow(im, 41, 19, e, 1, dk(scale, 0.55), 2, 4)
        eye(im, 23, 25, e, (200, 150, 40), 3, (250, 226, 110), True); eye(im, 41, 25, e, (200, 150, 40), 3, (250, 226, 110), True)
        blush(im, e, [(18, 31), (46, 31)], scale)
        mouth(im, 32, 42, e, dk(scale, 0.4), 7)
        marks(im, e)
        frames.append(im)
    return frames


strip(zaash_portrait((60, 48, 72), (124, 154, 84), (112, 62, 152), (224, 184, 64), False), "tarbesh")
strip(zaash_portrait((70, 52, 50), (92, 144, 94), (96, 102, 118), (196, 62, 52), True), "vzzket")

# Jasper (Ervani)
frames = []
for e in EMOTES:
    im = backdrop((132, 108, 90))
    shoulders(im, CREAM, 49)
    im.rect(24, 47, 39, 50, (214, 70, 60)); im.rect(30, 50, 33, 54, (180, 54, 48))
    for (cx, c) in [(17, OR), (47, dk(OR, 0.84))]:
        for i in range(16):
            im.rect(cx - i // 3, 2 + i, cx + i // 3, 2 + i, c)
        im.rect(cx, 2, cx, 4, (70, 44, 34))
        for i in range(6, 15):
            im.rect(cx - (i - 6) // 4, 4 + i, cx + (i - 6) // 4, 4 + i, (110, 66, 50))
    im.ell(32, 29, 17, 14.5, dk(OR, 0.84)); im.ell(31, 28.5, 15.5, 14, OR)
    im.ell(17, 35, 4.5, 5.5, CREAM); im.ell(47, 35, 4.5, 5.5, dk(CREAM, 0.9))
    im.ell(32, 38, 11, 8, dk(CREAM, 0.9)); im.ell(31.5, 37.5, 10, 7.5, CREAM)
    im.ell(32, 33.5, 2.6, 1.9, (40, 30, 36)); im.px(31, 33, (120, 110, 116)); im.rect(32, 35, 32, 37, (150, 120, 110))
    brow(im, 24, 21, e, -1, dk(OR, 0.6)); brow(im, 40, 21, e, 1, dk(OR, 0.6))
    eye(im, 24, 27, e, (70, 130, 70)); eye(im, 40, 27, e, (70, 130, 70))
    blush(im, e, [(20, 32), (44, 32)], OR)
    mouth(im, 32, 40, e, (130, 80, 76), 4)
    marks(im, e)
    frames.append(im)
strip(frames, "jasper")

# Bram (Moogli)
frames = []
for e in EMOTES:
    im = backdrop((84, 76, 108))
    shoulders(im, VEST, 51)
    im.rect(23, 53, 40, 63, BELLY)
    im.ell(32, 37, 26, 15.5, GDARK); im.ell(31, 36.5, 24.5, 15, GREEN)
    im.ell(18, 20, 9, 9, GDARK); im.ell(17.5, 19.5, 8, 8.5, GREEN); im.ell(46, 20, 9, 9, GDARK); im.ell(45.5, 19.5, 8, 8.5, GREEN)
    im.ell(32, 47, 13, 4, BELLY)
    for (x, y) in [(10, 34), (14, 40), (52, 36), (38, 28), (26, 29)]:
        im.px(x, y, lt(GREEN, 1.2)); im.px(x + 1, y, lt(GREEN, 1.2))
    brow(im, 18, 11, e, -1, GDARK, 2, 5); brow(im, 46, 11, e, 1, GDARK, 2, 5)
    eye(im, 18, 20, e, (70, 46, 30), 5); eye(im, 46, 20, e, (70, 46, 30), 5)
    im.px(29, 31, GDARK); im.px(35, 31, GDARK)
    blush(im, e, [(12, 38), (52, 38)], GREEN)
    mouth(im, 32, 41, e, dk(GREEN, 0.45), 13)
    marks(im, e)
    frames.append(im)
strip(frames, "bram")

# Zaas (Scyldari)
frames = []
for e in EMOTES:
    im = backdrop((36, 70, 104))
    for i, x in enumerate(range(9, 54, 6)):
        c = TEAL if i % 2 == 0 else TEALD
        im.rect(x, 40, x + 4, 63, c); im.rect(x + 4, 40, x + 4, 63, dk(c, 0.84))
        for y in range(46, 62, 5):
            im.px(x + 2, y, lt(TEAL, 1.3))
    im.ell(32, 27, 18, 21.5, TEALD); im.ell(31, 26.5, 16.5, 21, TEAL)
    for (x, y) in [(22, 12), (40, 14), (27, 40), (38, 41), (18, 34)]:
        im.ell(x, y, 1.6, 1.2, lt(TEAL, 1.25))
    im.rect(8, 11, 55, 15, (116, 80, 52)); im.rect(8, 11, 55, 11, (156, 116, 80)); im.rect(17, 1, 46, 11, (116, 80, 52)); im.rect(17, 1, 46, 2, (156, 116, 80))
    im.rect(17, 9, 46, 10, (232, 194, 72)); im.rect(40, 3, 46, 11, (92, 62, 42))
    brow(im, 22, 22, e, -1, TEALD, 2, 4); brow(im, 42, 22, e, 1, TEALD, 2, 4)
    eye(im, 22, 30, e, (30, 60, 110), 5); eye(im, 42, 30, e, (30, 60, 110), 5)
    blush(im, e, [(15, 37), (49, 37)], TEAL)
    mouth(im, 32, 40, e, dk(TEAL, 0.45), 3)
    marks(im, e)
    frames.append(im)
strip(frames, "zaas")

# Tikka (Arachnay)
frames = []
for e in EMOTES:
    im = backdrop((76, 66, 98))
    shoulders(im, DARK, 51)
    im.rect(46, 52, 56, 55, (244, 146, 54)); im.rect(54, 50, 57, 52, (210, 218, 228))
    im.ell(32, 29, 20.5, 20, DARK); im.ell(31, 28.5, 19, 19.5, BODY)
    for (x, y) in [(20, 14), (25, 12), (38, 13), (44, 16), (16, 24)]:
        im.px(x, y, lt(BODY, 1.3)); im.px(x + 1, y + 1, lt(BODY, 1.3))
    for (x, y) in [(15, 20), (26, 15), (38, 15), (49, 20)]:
        if e in ("happy", "love"):
            im.rect(x - 1, y, x + 1, y, LASH)
        else:
            im.ell(x, y, 2.2, 2.2, (255, 232, 124)); im.px(x, y, (60, 30, 20))
    eye(im, 23, 28, e, (150, 80, 30), 4, (255, 232, 124)); eye(im, 41, 28, e, (150, 80, 30), 4, (255, 232, 124))
    blush(im, e, [(16, 35), (48, 35)], BODY)
    gap = 3 if e == "surprised" else (1 if e == "angry" else 0)
    for i in range(7):
        im.rect(27 - gap - i // 3, 40 + i, 29 - gap - i // 3, 40 + i, DARK); im.rect(35 + gap + i // 3, 40 + i, 37 + gap + i // 3, 40 + i, DARK)
    mouth(im, 32, 41, e, dk(BODY, 0.4), 3)
    marks(im, e)
    frames.append(im)
strip(frames, "tikka")

for k, im in PORT.items():
    im.save(art("portrait_%s.png" % k))

# weapons as held in the hand: drawn pointing right, grip at the left end
WS = Img(28, 7)
WS.rect(0, 3, 21, 3, (156, 114, 72)); WS.rect(0, 4, 21, 4, (118, 84, 54)); WS.rect(18, 2, 20, 5, (196, 62, 52))
for i in range(7):
    WS.rect(21 + i, 3 - max(0, (5 - i) // 2), 21 + i, 3 + max(0, (5 - i) // 2), (224, 228, 238))
WS.rect(22, 3, 26, 3, (255, 255, 255))
outline_img(WS)
WS.save(art("weapon_spear.png"))
WW = Img(22, 9)
WW.rect(0, 4, 4, 4, (120, 84, 60)); WW.rect(0, 5, 4, 5, (90, 62, 44)); WW.rect(5, 1, 6, 7, (224, 184, 64)); WW.rect(5, 1, 5, 7, (250, 220, 120))
for i in range(14):
    hw = 2 if i < 10 else (1 if i < 13 else 0)
    WW.rect(7 + i, 4 - hw, 7 + i, 4 + hw, (206, 212, 226))
WW.rect(7, 3, 19, 3, (255, 255, 255)); WW.rect(7, 6, 16, 6, (150, 158, 176))
outline_img(WW)
WW.save(art("weapon_sword.png"))

# ================================================================ wreck (4 frames of 64x32: wrecked -> repaired)
W = Img(256, 32)
HULL, HDARK, STRIPE, BURN = (120, 140, 165), (78, 92, 112), (230, 130, 50), (40, 36, 40)
for stage in range(4):
    o = stage * 64
    for y in range(8, 28):
        inset = abs(y - 18) // 2
        W.rect(o + 6 + inset, y, o + 52 - inset * 2, y, HULL)
    W.rect(o + 10, 24, o + 46, 27, HDARK)
    W.rect(o + 14, 15, o + 40, 16, STRIPE)
    W.rect(o + 40, 10, o + 47, 14, (120, 215, 255) if stage >= 3 else (70, 90, 120))
    if stage >= 3:
        W.rect(o + 41, 11, o + 44, 12, (220, 245, 255))
    for y in range(2, 9):
        W.rect(o + 16 + (8 - y), y, o + 26 + (8 - y) // 2, y, HDARK)
    if stage == 0:
        for (x, y, r) in [(22, 19, 4), (33, 22, 3), (9, 17, 3)]:
            W.ell(o + x, y, r, r, BURN)
        for (x, y) in [(55, 20), (57, 23), (59, 19), (60, 26), (3, 26), (54, 27)]:
            W.rect(o + x, y, o + x + 1, y + 1, HDARK)
    else:
        for (x, y) in [(19, 17), (31, 20), (8, 16)]:
            W.rect(o + x, y, o + x + 6, y + 4, (150, 168, 190))
    if stage >= 2:
        W.rect(o + 3, 14, o + 6, 21, (60, 70, 90))
        W.rect(o + 1, 15, o + 3, 20, (120, 230, 255))
        W.rect(o + 0, 17, o + 0, 18, (220, 250, 255))
    outline_img(W, o, 0, 64, 30)
    W.rect(o + 4, 30, o + 59, 31, (0, 0, 0, 60))
W.save(art("wreck.png"))

# ================================================================ ore veins (2 frames of 16x16: full, worked out)
def ore_sprite(name, vein, glint):
    im = Img(32, 16)
    for f in range(2):
        o = f * 16
        im.ell(o + 7.5, 14, 6.5, 1.6, (0, 0, 0, 70))
        if f == 0:
            im.rect(o + 2, 6, o + 13, 13, (104, 88, 82)); im.rect(o + 4, 3, o + 11, 6, (104, 88, 82)); im.rect(o + 10, 7, o + 13, 13, (82, 68, 66))
            im.rect(o + 4, 3, o + 9, 3, (132, 114, 104))
            for (x, y) in [(4, 8), (5, 8), (6, 9), (7, 5), (8, 5), (8, 6), (10, 10), (11, 10), (5, 12), (6, 12), (9, 12)]:
                im.px(o + x, y, vein)
            for (x, y) in [(5, 7), (8, 4), (10, 9)]:
                im.px(o + x, y, glint)
        else:
            im.rect(o + 3, 10, o + 12, 13, (96, 82, 78)); im.rect(o + 5, 8, o + 9, 10, (96, 82, 78)); im.rect(o + 9, 11, o + 12, 13, (78, 66, 64))
        outline_img(im, o, 0, 16, 16)
    im.save(art(name + ".png"))


ore_sprite("iron_ore", (176, 96, 84), (232, 190, 176))
ore_sprite("copper_ore", (72, 178, 140), (250, 190, 96))

# ================================================================ sounds (16-bit mono WAV)
import math, wave

AUDIO = os.path.join(OUT, "audio")
os.makedirs(AUDIO, exist_ok=True)
RATE = 22050


def save_wav(name, samples):
    with wave.open(os.path.join(AUDIO, name + ".wav"), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32000)) for v in samples))


def tone(freq0, freq1, dur, vol=0.5, shape="sine", decay=4.0):
    out, phase, n = [], 0.0, int(RATE * dur)
    for i in range(n):
        k = i / n
        phase += 2 * math.pi * (freq0 + (freq1 - freq0) * k) / RATE
        v = math.sin(phase)
        if shape == "square":
            v = 1.0 if v > 0 else -1.0
        elif shape == "saw":
            v = (phase / math.pi) % 2.0 - 1.0
        env = math.exp(-decay * k) * min(1.0, i / 40.0) * min(1.0, (n - i) / 60.0)
        out.append(v * vol * env)
    return out


def noise(dur, vol=0.5, smooth=0.2, decay=6.0, seed=1, swell=False):
    rnd, out, last, n = random.Random(seed), [], 0.0, int(RATE * dur)
    for i in range(n):
        k = i / n
        last += (rnd.uniform(-1, 1) - last) * smooth
        env = (math.sin(math.pi * k) if swell else math.exp(-decay * k)) * min(1.0, (n - i) / 60.0)
        out.append(last * vol * env)
    return out


def mix(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0.0) + (b[i] if i < len(b) else 0.0) for i in range(n)]


save_wav("step", noise(0.07, 0.9, 0.25, 9.0, 3))
save_wav("blip", tone(660, 640, 0.045, 0.35, "square", 3.0))
save_wav("click", tone(620, 940, 0.05, 0.4, "sine", 2.0))
save_wav("coin", tone(1320, 1320, 0.07, 0.4, "square", 3.0) + tone(1760, 1760, 0.16, 0.4, "square", 4.0))
save_wav("zap", mix(tone(1100, 260, 0.2, 0.4, "saw", 2.5), noise(0.2, 0.35, 0.6, 5.0, 5)))
save_wav("smelt", mix(noise(0.6, 0.8, 0.08, 0.0, 7, swell=True), tone(90, 140, 0.6, 0.3, "sine", 0.5)))
save_wav("warp", tone(220, 560, 0.3, 0.4, "sine", 1.0))
save_wav("quest", tone(523, 523, 0.09, 0.4, "square", 2.0) + tone(659, 659, 0.09, 0.4, "square", 2.0) + tone(784, 784, 0.09, 0.4, "square", 2.0) + tone(1047, 1047, 0.25, 0.4, "square", 3.0))
save_wav("deny", tone(170, 130, 0.14, 0.45, "square", 2.0))

# ================================================================ item icons, hearts, weapon swing (for the menus and hotbar)
# Order here must match "icon" in scripts/item_data.gd.
IT = Img(16 * 12, 16)


def icon(i):
    o = i * 16

    class I:
        def r(s, x0, y0, x1, y1, c):
            IT.rect(o + x0, y0, o + x1, y1, c); return s

        def ps(s, pts, c):
            for (x, y) in pts:
                IT.px(o + x, y, c)
            return s

        def done(s):
            outline_img(IT, o, 0, 16, 16)
    return I()


i = icon(0)     # mining laser
i.r(2, 8, 9, 11, (150, 158, 172)).r(2, 8, 9, 8, (196, 204, 216)).r(4, 12, 6, 14, (96, 104, 120)).r(10, 9, 12, 10, (90, 98, 112)).r(13, 9, 14, 10, (240, 80, 70)).ps([(14, 8), (15, 9), (14, 11)], (255, 180, 150)).done()
i = icon(1)     # spear
for k in range(10):
    i.ps([(2 + k, 13 - k)], (156, 114, 72))
i.ps([(12, 3), (13, 2), (12, 2), (13, 3), (11, 3), (12, 4), (14, 1)], (224, 228, 238)).ps([(10, 5), (11, 4)], (196, 62, 52)).done()
i = icon(2)     # sword
for k in range(8):
    i.ps([(6 + k, 9 - k), (7 + k, 9 - k)], (224, 228, 238))
i.ps([(4, 9), (5, 10), (6, 11), (7, 12), (5, 9), (6, 10), (7, 11)], (224, 184, 64)).ps([(3, 12), (4, 11), (2, 13), (3, 13)], (120, 84, 60)).done()
for n, (vein, glint) in enumerate([((176, 96, 84), (232, 190, 176)), ((72, 178, 140), (250, 190, 96))]):
    i = icon(3 + n)   # ores
    i.r(3, 6, 12, 12, (104, 88, 82)).r(5, 4, 10, 6, (104, 88, 82)).r(10, 8, 12, 12, (82, 68, 66)).ps([(5, 8), (6, 8), (7, 6), (8, 10), (9, 10), (6, 11)], vein).ps([(6, 7), (9, 9)], glint).done()
for n, (c, hi) in enumerate([((150, 158, 172), (208, 214, 226)), ((214, 132, 70), (246, 186, 120))]):
    i = icon(5 + n)   # bars
    i.r(2, 8, 13, 12, c).r(3, 6, 12, 8, hi).r(2, 12, 13, 12, dk(c)).r(12, 8, 13, 12, dk(c)).done()
i = icon(7)     # hull plate
i.r(2, 3, 13, 12, (120, 140, 165)).r(2, 3, 13, 3, (170, 188, 208)).r(12, 4, 13, 12, (86, 104, 128)).ps([(4, 5), (11, 5), (4, 10), (11, 10)], (60, 72, 92)).r(5, 7, 10, 8, (230, 130, 50)).done()
i = icon(8)     # coil wire
for (x0, y0, x1, y1) in [(4, 3, 11, 4), (3, 5, 4, 10), (11, 5, 12, 10), (4, 11, 11, 12), (6, 6, 9, 6), (6, 9, 9, 9), (6, 7, 6, 8), (9, 7, 9, 8)]:
    i.r(x0, y0, x1, y1, (214, 132, 70))
i.ps([(4, 3), (5, 3), (3, 6), (6, 6)], (250, 196, 130)).done()
i = icon(9)     # chitin
i.r(3, 5, 12, 11, (98, 66, 112)).r(4, 4, 11, 4, (98, 66, 112)).r(4, 12, 11, 12, (66, 44, 78)).r(4, 5, 9, 5, (150, 110, 164)).r(7, 5, 7, 11, (66, 44, 78)).done()
i = icon(10)    # lizard hide
i.r(3, 4, 12, 12, (104, 134, 92)).r(2, 6, 2, 10, (104, 134, 92)).r(13, 6, 13, 10, (70, 96, 66)).r(3, 4, 12, 4, (150, 176, 126)).ps([(5, 6), (8, 7), (10, 6), (6, 9), (9, 10), (5, 11)], (70, 96, 66)).done()
i = icon(11)    # ration pack
i.r(3, 5, 12, 12, (196, 186, 150)).r(3, 5, 12, 5, (230, 222, 190)).r(11, 6, 12, 12, (160, 150, 118)).r(5, 7, 10, 10, (220, 90, 80)).r(6, 8, 9, 9, (250, 240, 226)).done()
IT.save(art("items.png"))

HE = Img(14, 6)
for f, c in enumerate([(232, 70, 90), (70, 74, 96)]):
    for (x, y) in [(1, 0), (2, 0), (4, 0), (5, 0)] + [(x, 1) for x in range(7)] + [(x, 2) for x in range(7)] + [(x, 3) for x in range(1, 6)] + [(x, 4) for x in range(2, 5)] + [(3, 5)]:
        HE.px(f * 7 + x, y, c)
HE.px(1, 1, (255, 170, 180))
HE.save(art("hearts.png"))

# ---- menu and dialogue skin. Each of these can be repainted at any size; the game stretches them to fit.
# ui_panel.png / ui_dialogue.png / ui_portrait_frame.png: a 3x3 grid. Corners stay sharp, edges and middle stretch.
def nine(name, fill, edge, inner, cell_px=16):
    im = Img(cell_px * 3, cell_px * 3)
    n = cell_px * 3
    if fill:
        im.rect(0, 0, n - 1, n - 1, fill)
    for k, c in ((0, edge), (1, inner)):
        im.rect(k, k, n - 1 - k, k, c); im.rect(k, n - 1 - k, n - 1 - k, n - 1 - k, c)
        im.rect(k, k, k, n - 1 - k, c); im.rect(n - 1 - k, k, n - 1 - k, n - 1 - k, c)
    for (x, y) in [(3, 3), (n - 4, 3), (3, n - 4), (n - 4, n - 4)]:
        im.px(x, y, edge)
    im.save(art(name))


nine("ui_panel.png", (16, 22, 46, 248), (127, 212, 255), (44, 70, 112))
nine("ui_dialogue.png", (16, 22, 46, 238), (127, 212, 255), (44, 70, 112))
nine("ui_portrait_frame.png", None, (127, 212, 255), (30, 44, 80), 8)
# ui_slot.png: three 18x18 pictures side by side: empty slot, selected slot, slot being moved
US = Img(54, 18)
for f, c in enumerate([(104, 128, 178), (255, 210, 127), (255, 159, 107)]):
    o = f * 18
    US.rect(o, 0, o + 17, 17, (22, 28, 54, 232)); US.rect(o + 1, 1, o + 16, 16, (30, 38, 70, 232))
    US.rect(o, 0, o + 17, 0, c); US.rect(o, 17, o + 17, 17, c); US.rect(o, 0, o, 17, c); US.rect(o + 17, 0, o + 17, 17, c)
    if f:
        US.rect(o + 1, 1, o + 16, 1, dk(c, 0.7)); US.rect(o + 1, 1, o + 1, 16, dk(c, 0.7))
US.save(art("ui_slot.png"))
# ui_tab.png: two 24x12 pictures side by side (page tab: not chosen, chosen). The middle third stretches.
UT = Img(48, 12)
UT.rect(1, 2, 22, 11, (24, 32, 62, 200)); UT.rect(1, 2, 22, 2, (70, 96, 140)); UT.rect(1, 2, 1, 11, (70, 96, 140)); UT.rect(22, 2, 22, 11, (70, 96, 140))
UT.rect(24, 0, 47, 11, (42, 78, 116)); UT.rect(24, 0, 47, 0, (127, 212, 255)); UT.rect(24, 0, 24, 11, (127, 212, 255)); UT.rect(47, 0, 47, 11, (127, 212, 255)); UT.rect(25, 1, 46, 1, (90, 150, 200))
UT.save(art("ui_tab.png"))

SL = Img(32, 16)    # frame 0: sword arc, frame 1: spear thrust. Both drawn pointing right.
for a in range(-60, 61, 4):
    x = 3 + 9 * math.cos(math.radians(a)); y = 7.5 + 7 * math.sin(math.radians(a))
    SL.px(x, y, (255, 255, 255)); SL.px(x - 1, y, (200, 230, 255, 180))
SL.rect(16 + 1, 7, 16 + 13, 8, (255, 255, 255)); SL.px(16 + 14, 7, (255, 255, 255)); SL.px(16 + 14, 8, (255, 255, 255)); SL.px(16 + 15, 7, (200, 230, 255))
SL.rect(16 + 1, 6, 16 + 8, 6, (200, 230, 255, 160)); SL.rect(16 + 1, 9, 16 + 8, 9, (200, 230, 255, 160))
SL.save(art("slash.png"))
save_wav("swing", noise(0.12, 0.7, 0.35, 0.0, 11, swell=True))
save_wav("hit", mix(tone(320, 120, 0.09, 0.45, "square", 3.0), noise(0.09, 0.5, 0.5, 6.0, 13)))
save_wav("hurt", tone(240, 100, 0.2, 0.5, "saw", 2.0))
save_wav("die", mix(noise(0.22, 0.7, 0.3, 5.0, 17), tone(200, 60, 0.22, 0.35, "square", 2.0)))
save_wav("eat", noise(0.05, 0.6, 0.5, 6.0, 19) + [0.0] * 1200 + noise(0.05, 0.6, 0.5, 6.0, 23) + [0.0] * 1200 + noise(0.06, 0.6, 0.4, 6.0, 29))

# ---- music: simple generated loops, made once. Replace them with real tracks any time
# (an .ogg file with the same name is used in preference to the .wav).
def midi(note):
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    return 440.0 * 2 ** ((names[note[0]] + 12 * (int(note[1]) + 1) - 69) / 12.0)


def render_loop(name, length_s, voices):
    n = int(RATE * length_s)
    buf = [0.0] * n
    for (start, freq, dur, vol, shape, attack, decay) in voices:
        i0, cnt, ph, step = int(start * RATE), int(dur * RATE), 0.0, 2 * math.pi * freq / RATE
        for i in range(cnt):
            ph += step
            v = math.sin(ph) if shape == "sine" else (2 / math.pi) * math.asin(math.sin(ph))
            env = min(1.0, i / (attack * RATE + 1)) * math.exp(-decay * i / cnt) * min(1.0, (cnt - i) / (0.03 * RATE))
            buf[(i0 + i) % n] += v * vol * env
    peak = max(abs(v) for v in buf) or 1.0
    save_wav(name, [v / peak * 0.8 for v in buf])


if not os.path.exists(os.path.join(AUDIO, "music_town.wav")):
    beat = 60.0 / 84.0
    chords = [("C3", "E3", "G3"), ("A2", "C3", "E3"), ("F2", "A2", "C3"), ("G2", "B2", "D3")] * 2
    tune = ["E4 G4 A4 G4 E4 - D4 -", "C4 E4 A4 - G4 E4 - -", "F4 A4 C5 A4 F4 - A4 -", "G4 B4 D5 B4 G4 - - -",
            "E4 G4 C5 G4 E5 - D5 -", "C5 A4 E4 - A4 C5 - -", "A4 C5 F5 C5 A4 - G4 -", "G4 D5 B4 G4 D4 - - -"]
    voices = []
    for bar, chord in enumerate(chords):
        t0 = bar * 4 * beat
        for note in chord:
            voices.append((t0, midi(note) * 2, 4 * beat, 0.10, "sine", 0.5, 1.0))
        voices.append((t0, midi(chord[0]), 1.8 * beat, 0.26, "tri", 0.01, 2.2))
        voices.append((t0 + 2 * beat, midi(chord[0]), 1.8 * beat, 0.2, "tri", 0.01, 2.2))
        for i, note in enumerate(tune[bar].split()):
            if note != "-":
                voices.append((t0 + i * beat / 2, midi(note), 0.9 * beat, 0.17, "tri", 0.005, 3.2))
    render_loop("music_town", 8 * 4 * beat, voices)
if not os.path.exists(os.path.join(AUDIO, "music_under.wav")):
    voices = []
    for k in range(4):
        voices.append((k * 6.0, midi("D2"), 6.0, 0.30, "sine", 2.0, 0.3))
        voices.append((k * 6.0 + 1.5, midi("A2"), 4.5, 0.18, "sine", 1.5, 0.6))
    for (t0, note) in [(1.0, "D5"), (4.2, "F5"), (8.5, "A5"), (11.0, "E5"), (14.3, "D5"), (17.6, "A4"), (20.4, "F5"), (22.5, "C5")]:
        voices.append((t0, midi(note), 2.6, 0.09, "sine", 0.01, 4.0))
        voices.append((t0 + 0.35, midi(note) * 1.5, 2.2, 0.04, "sine", 0.01, 4.0))
    render_loop("music_under", 24.0, voices)

# ================================================================ maps
WALK = set(".,fhusmiUDAR")


class Area:
    def __init__(s, key, title, w, h, fill):
        s.key, s.title, s.w, s.h = key, title, w, h
        s.floor = [[fill] * w for _ in range(h)]
        s.obj = [[" "] * w for _ in range(h)]
        s.zones, s.warps, s.outlines = [], [], []

    def room(s, name, x0, y0, x1, y1, f, wall="#"):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s.floor[y][x] = wall if (x in (x0, x1) or y in (y0, y1)) else f
        if name:
            s.zones.append([name, x0, y0, x1, y1])

    def circle(s, cx, cy, r, f, wall="#"):
        """A round room: floor inside the radius, a ring of wall just outside it (only over rock)."""
        for y in range(s.h):
            for x in range(s.w):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if d <= r:
                    s.floor[y][x] = f
                elif d <= r + 1.3 and s.floor[y][x] not in WALK:
                    s.floor[y][x] = wall

    def carve(s, name, x0, y0, x1, y1, f):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s.floor[y][x] = f
        if name:
            s.zones.append([name, x0, y0, x1, y1])

    def setf(s, ch, cells):
        for (x, y) in cells:
            s.floor[y][x] = ch

    def put(s, ch, cells):
        for (x, y) in cells:
            assert s.floor[y][x] in WALK, (s.key, ch, x, y, s.floor[y][x])
            assert s.obj[y][x] == " ", (s.key, ch, x, y, "occupied")
            s.obj[y][x] = ch

    def mirror(s):
        """Flip the whole area left to right."""
        s.floor = [r[::-1] for r in s.floor]
        s.obj = [r[::-1] for r in s.obj]
        s.zones = [[n, s.w - 1 - x1, y0, s.w - 1 - x0, y1] for (n, x0, y0, x1, y1) in s.zones]
        s.warps = [[s.w - 1 - x, y, a, tx, ty] for (x, y, a, tx, ty) in s.warps]
        s.outlines = [[s.w - x - w, y, w, h] for (x, y, w, h) in s.outlines]

    def warp(s, ch, cells, area, tx, ty):
        for (x, y) in cells:
            s.floor[y][x] = ch
            s.warps.append([x, y, area, tx, ty])


def row(y, xs):
    return [(x, y) for x in xs]


def block(x0, y0, x1, y1):
    return [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]


A = {}

# ---------------------------------------------------------------- main level: the town square
# A very large circular town square with a fountain, rooms touching its rim, and two wings.
# The west wing leads to the Spaceport District map, the east wing to the Agri Dome map.
m = A["main"] = Area("main", "Main Level", 180, 120, "r")
CX, CY, CR = 90, 60, 30.3
m.room("", 14, 57, 60, 63, ".")             # west wing
m.room("", 120, 57, 166, 63, ".")           # east wing
m.circle(CX, CY, CR, "i")                   # the square itself, paved
for y in range(m.h):
    for x in range(m.w):
        d = ((x - CX) ** 2 + (y - CY) ** 2) ** 0.5
        if d <= CR and (58 <= y <= 62 or 88 <= x <= 92 or 5.5 < d <= 8.5 or 18.5 < d <= 20.5):
            m.floor[y][x] = "."             # paths: a cross, a ring round the fountain, and an outer ring
for dy in range(-4, 5):
    for dx in range(-4, 5):
        k = max(abs(dx), abs(dy))
        if k == 4 and abs(dx) == 4 and abs(dy) == 4:
            continue
        m.floor[CY + dy][CX + dx] = "B" if k == 4 else ("J" if k == 0 else "O")
m.room("Apartments", 14, 48, 23, 57, ",")
m.room("Apartments", 23, 48, 32, 57, ",")
m.room("", 32, 48, 40, 57, "f")             # shuttered workshop
m.room("Common area", 40, 40, 64, 57, ",")
m.room("Bram's Sundries", 18, 63, 29, 72, ".")
m.room("Fabrication shop", 29, 63, 40, 72, "f")
m.room("Empty apartment", 40, 63, 50, 72, ",")
m.room("Empty shop", 52, 66, 64, 78, ".")
m.room("Command lift", 86, 18, 94, 29, ".")
m.room("Engineering lift", 86, 91, 94, 102, ".")
m.room("Library", 116, 40, 132, 54, ",")
m.room("", 134, 48, 144, 57, "f")           # abandoned shops
m.room("", 144, 48, 154, 57, "f")
m.room("Apartments", 155, 48, 165, 57, ",")
m.room("Mess hall", 116, 63, 146, 82, ".")
m.zones += [["West wing", 14, 57, 60, 63], ["East wing", 120, 57, 166, 63], ["Town square", 59, 29, 121, 91]]
m.setf(".", [(18, 57), (27, 57), (52, 57), (53, 57), (64, 50), (64, 51), (23, 63), (24, 63), (34, 63), (45, 63),
             (64, 69), (64, 70), (89, 29), (90, 29), (91, 29), (89, 91), (90, 91), (91, 91),
             (116, 48), (116, 49), (160, 57), (130, 63), (131, 63), (116, 68), (116, 69)])
m.setf("Z", [(35, 57), (36, 57), (37, 57), (138, 57), (139, 57), (140, 57), (148, 57), (149, 57), (150, 57)])
m.setf("w", [(17, 48), (18, 48), (26, 48), (27, 48), (48, 40), (49, 40), (56, 40), (57, 40), (122, 40), (123, 40), (126, 40), (127, 40),
             (159, 48), (160, 48)])
# town square fixtures
m.put("l", [(80, 50), (100, 50), (80, 70), (100, 70), (72, 42), (108, 42), (72, 78), (108, 78)])
m.put("o", [(83, 54), (84, 54), (96, 54), (97, 54), (83, 66), (84, 66), (96, 66), (97, 66), (70, 55), (71, 55), (109, 65), (110, 65)])
m.put("p", [(86, 55), (94, 55), (86, 65), (94, 65), (76, 46), (104, 46), (76, 74), (104, 74), (84, 36), (96, 36), (84, 84), (96, 84)])
m.put("q", [(98, 76), (99, 76), (102, 76), (103, 76), (77, 76), (78, 76), (81, 76), (82, 76)])
m.put("c", [(100, 77), (79, 77), (104, 77)])
m.put("n", [(95, 52)])
# apartments
m.put("b", [(15, 49), (22, 49), (24, 49), (31, 49), (41, 71), (156, 49), (164, 49)])
m.put("o", [(21, 54), (157, 55)])
m.put("t", [(29, 55), (162, 51)])
m.put("p", [(15, 56), (31, 56), (49, 64), (164, 56)])
# shuttered workshop and abandoned shops (you can see in, but not get in)
m.put("P", [(34, 51), (35, 51), (38, 54), (136, 51), (146, 53)])
m.put("c", [(38, 50), (142, 50), (152, 55)])
m.put("e", [(36, 54), (140, 53), (148, 50)])
m.put("x", [(137, 55), (145, 50)])
# common area
m.put("o", [(45, 44), (46, 44), (55, 44), (56, 44), (45, 52), (46, 52)])
m.put("t", [(50, 46), (51, 46), (55, 52), (56, 52)])
m.put("p", [(41, 41), (63, 44), (41, 56)])
m.put("S", [(42, 41), (43, 41), (59, 56), (60, 56)])
# Bram's shop: a counter down the middle. Bram stands behind it on the right, facing his customers.
m.put("I", [(25, y) for y in range(65, 71)])
m.put("S", [(28, 65), (28, 67), (28, 69), (27, 71), (28, 71)])
m.put("c", [(19, 71), (20, 71)])
m.put("p", [(19, 64)])
# fabrication shop
m.put("c", [(30, 70), (31, 70), (30, 71), (31, 71)])
m.put("P", [(35, 71), (36, 71)])
m.put("k", [(38, 71), (39, 71)])
m.put("t", [(37, 67)])
# empty shop
m.put("C", row(72, range(55, 61)))
m.put("S", [(53, 67), (54, 67)])
m.put("x", [(57, 75), (61, 74)])
m.put("e", [(55, 76)])
# library
m.put("S", row(41, range(117, 132)) + row(45, [120, 121, 122, 126, 127, 128]) + row(49, [120, 121, 122, 126, 127, 128]))
m.put("t", [(124, 47)])
m.put("o", [(129, 52), (130, 52)])
m.put("p", [(131, 53)])
# mess hall: a kitchen in the top-right corner behind a serving counter (the cooks face the room),
# and dining tables with stools
m.put("C", row(68, range(134, 146)))
m.put("V", [(136, 64), (137, 64)])
m.put("W", [(139, 64)])
m.put("R", [(141, 64)])
m.put("S", [(143, 64), (144, 64)])
m.put("m", [(140, 66)])
m.put("H", [(145, 65), (145, 66)])
SEATS = [120, 121, 125, 126, 130, 131, 135, 136, 140, 141]
for ty in (71, 76):
    m.put("d", row(ty, SEATS))
    m.put("h", row(ty - 1, SEATS) + row(ty + 1, SEATS))
m.put("p", [(117, 64), (117, 81), (145, 81)])
m.put("E", [(90, 65)])                      # Sara's hologram pad by the fountain
# lifts: north goes up to the Survey Level, south goes down to Engineering
m.warp("U", [(90, 20)], "top", 20, 14)
m.warp("D", [(90, 100)], "eng", 34, 8)
# ends of the wings lead to the other two maps
m.warp("A", [(15, y) for y in range(58, 63)], "west", 94, 40)
m.warp("A", [(165, y) for y in range(58, 63)], "east", 5, 35)

# ---------------------------------------------------------------- spaceport district (west map)
# Its own smaller circle with Reception. Spaceport to the left, the Star dome above,
# the old barracks (the future hotel) below. You wake up here.
w = A["west"] = Area("west", "Spaceport District", 100, 80, "r")
w.room("Spaceport", 0, 14, 30, 56, "h")
w.room("", 30, 37, 38, 43, ".")             # spaceport - reception
w.room("", 45, 20, 51, 30, ".")             # star dome - reception
w.room("", 45, 50, 51, 58, ".")             # reception - barracks
w.room("", 58, 37, 98, 43, ".")             # hall back to the town square
w.circle(48, 12, 8.3, "i", "d")             # star dome
w.circle(48, 40, 10.3, ".")                 # reception circle
w.room("", 66, 28, 76, 37, ",")             # private apartments (locked)
w.room("", 76, 28, 86, 37, ",")
w.room("Barracks hall", 20, 58, 80, 65, ".")
w.room("Head officer's quarters", 20, 65, 34, 78, ",")
w.room("Bunk room", 34, 65, 44, 78, ".")
w.room("Bunk room", 44, 65, 54, 78, ".")
w.room("Bunk room", 54, 65, 64, 78, ".")
w.room("Bunk room", 64, 65, 80, 78, ".")
w.zones += [["Reception", 37, 29, 59, 51], ["Star dome", 39, 3, 57, 21], ["West hall", 58, 37, 98, 43]]
w.setf("h", [(30, y) for y in range(38, 43)])
w.setf(".", [(46, 58), (47, 58), (48, 58), (49, 58), (50, 58), (27, 65), (39, 65), (49, 65), (59, 65), (72, 65)])
w.setf("Z", [(70, 37), (71, 37), (72, 37), (80, 37), (81, 37), (82, 37)])
w.setf("w", [(22, 14), (23, 14), (26, 14), (27, 14)])
w.setf("r", [(0, y) for y in range(22, 29)] + [(0, y) for y in range(46, 52)] + row(14, range(6, 14)) + row(56, range(6, 13))
       + [(40, 9), (40, 10), (56, 14), (56, 15), (44, 5), (53, 5)])
# spaceport
w.put("P", [(2, 16), (3, 16), (4, 16), (27, 17), (28, 17), (2, 54), (3, 54), (27, 53), (28, 53)])
w.put("c", [(6, 52), (7, 52), (6, 51), (26, 22), (27, 22), (20, 50)])
w.put("e", [(12, 18), (22, 20), (5, 40), (25, 48), (14, 50), (9, 23), (18, 17)])
w.put("k", [(26, 36), (27, 36)])
w.put("L", [(28, 45), (28, 46)])
w.outlines.append([6, 26, 16, 18])
# star dome
w.put("o", [(44, 10), (45, 10), (51, 10), (52, 10)])
w.put("T", [(48, 6)])
w.put("p", [(42, 13), (54, 13), (48, 16)])
# reception circle
w.put("C", row(36, range(45, 52)))
w.put("p", [(42, 45), (54, 45), (42, 35), (54, 35)])
w.put("o", [(40, 40), (56, 40)])
w.put("l", [(44, 46), (52, 46)])
# private apartments behind shutters
w.put("b", [(67, 29), (85, 29)])
w.put("o", [(73, 33), (78, 33)])
w.put("p", [(75, 29), (77, 29)])
# barracks hall
w.put("p", [(21, 59), (79, 59)])
w.put("C", row(61, range(28, 36)))
w.put("e", [(40, 62), (56, 60), (66, 63), (24, 63)])
w.put("x", [(70, 60), (60, 63)])
# head officer's quarters
w.put("b", [(22, 67)])
w.put("L", [(32, 66), (33, 66)])
w.put("t", [(30, 73), (31, 73)])
w.put("S", [(21, 73), (21, 74)])
w.put("p", [(21, 77), (33, 77)])
w.put("o", [(26, 76), (27, 76)])
# bunk rooms: dusty, some rubble
w.put("b", [(35, 67), (35, 70), (35, 73), (43, 67), (43, 70), (45, 67), (45, 70), (53, 67), (53, 73), (55, 67), (55, 70), (63, 67),
            (65, 67), (65, 70), (65, 73), (79, 67), (79, 70)])
w.put("L", [(43, 77), (53, 77), (63, 77), (79, 77)])
w.put("x", [(38, 75), (39, 75), (48, 72), (58, 74), (59, 74), (70, 72), (74, 76), (75, 76)])
w.put("e", [(40, 69), (50, 76), (57, 69), (68, 68), (72, 74)])
w.put("c", [(77, 66), (78, 66)])
w.put("E", [(26, 70), (48, 35)])
w.warp("A", [(97, y) for y in range(38, 43)], "main", 18, 60)

# ---------------------------------------------------------------- agri dome (east map)
# The broken agri dome, with one corner that still grows. A private villa and a tool shed by the hall.
g = A["east"] = Area("east", "Agri Dome", 90, 70, "r")
g.room("", 1, 32, 32, 38, ".")              # hall from the town square
g.circle(52, 35, 20.3, "s", "d")
for x in range(33, 72):
    for y in range(34, 37):
        if ((x - 52) ** 2 + (y - 35) ** 2) ** 0.5 <= 20.3:
            g.floor[y][x] = "u"             # the old central walkway
g.room("Private villa", 6, 20, 22, 32, ",")
g.room("Tool shed", 8, 38, 18, 46, "f")
g.zones += [["Broken agri dome", 31, 14, 73, 56], ["East hall", 1, 32, 32, 38]]
g.setf("f", [(13, 38)])
g.setf("Z", [(14, 32)])
g.setf("w", [(10, 20), (11, 20), (17, 20), (18, 20)])
ring = [(x, y) for y in range(g.h) for x in range(g.w) if g.floor[y][x] == "d"]
g.setf("r", [c for i, c in enumerate(ring) if (i * 7) % 5 == 0 and c[0] > 44])     # broken panels, away from the entrance
# the corner that still grows
g.put("H", row(31, range(36, 42)) + row(39, range(36, 42)) + row(29, range(38, 42)) + row(41, range(38, 42)))
g.put("p", [(34, 33), (34, 37)])
# the rest: dead planters, rubble, old machines
g.put("x", [(50, 22), (51, 22), (60, 26), (64, 40), (65, 40), (56, 48), (47, 50), (58, 30), (66, 33), (48, 28), (54, 44), (61, 46)])
g.put("e", [(52, 26), (62, 31), (57, 40), (49, 46), (68, 37), (45, 24), (53, 52), (60, 42)])
g.put("P", [(55, 20), (56, 20), (55, 50), (56, 50), (70, 30), (70, 40)])
g.put("c", [(46, 44), (63, 23)])
# villa (locked)
g.put("b", [(7, 21)])
g.put("o", [(12, 25), (13, 25)])
g.put("t", [(17, 24)])
g.put("p", [(21, 21), (7, 31)])
g.put("S", [(20, 30)])
# tool shed
g.put("c", [(9, 44), (10, 44), (9, 45)])
g.put("L", [(16, 39), (17, 39)])
g.put("S", [(9, 39)])
g.warp("A", [(2, y) for y in range(33, 38)], "main", 162, 60)

# ---------------------------------------------------------------- top level
t = A["top"] = Area("top", "Survey Level", 40, 22, "~")
t.room("Artifact lab", 0, 0, 13, 8, ".")
t.room("Survey suite", 13, 0, 26, 8, ".")
t.room("Observatory lounge", 26, 0, 39, 8, ",")
t.room("Tar'Besh's quarters", 0, 12, 9, 19, ",")
t.room("", 9, 12, 17, 19, "f")
t.room("Lift", 17, 12, 23, 18, ".")
t.room("", 23, 12, 31, 19, "f")
t.room("Storage", 31, 12, 39, 19, ".")
t.room("Upper hall", 0, 8, 39, 12, ".")
t.setf(".", row(8, [7, 19, 20, 32]) + row(12, [5, 20, 35]))
t.setf("Z", row(12, [12, 13, 14, 26, 27, 28]))
t.setf("w", row(0, [2, 3, 10, 11, 15, 16, 23, 24, 28, 29, 30, 33, 34, 35, 37]) + [(39, 3), (39, 4), (39, 5)])
t.put("a", [(3, 3), (6, 3), (9, 3), (8, 18)])
t.put("k", [(2, 1), (3, 1), (15, 1), (16, 1), (23, 1), (24, 1)])
t.put("S", [(11, 1), (12, 1), (8, 14)])
t.put("t", [(10, 6), (32, 4), (4, 17)])
t.put("K", row(1, [18, 19, 20, 21]))
t.put("T", [(36, 2)])
t.put("o", [(28, 3), (29, 3), (28, 6), (29, 6)])
t.put("p", [(27, 1), (38, 7), (1, 18), (2, 9), (37, 9)])
t.put("b", [(1, 14)])
t.put("c", [(11, 15), (32, 14), (33, 14), (32, 15), (38, 18)])
t.put("e", [(14, 16), (29, 17)])
t.put("P", [(25, 15)])
t.put("L", [(37, 13), (38, 13)])
t.put("E", [(19, 3)])
t.warp("D", [(20, 16)], "main", 90, 25)

# ---------------------------------------------------------------- engineering level
e = A["eng"] = Area("eng", "Engineering Level", 58, 24, "M")
e.room("Ore processing", 0, 0, 16, 10, "f")
e.room("Power core", 16, 0, 31, 10, "f")
e.room("Lift", 31, 4, 35, 10, ".")
e.room("Engineering bay", 35, 0, 48, 10, "f")
e.room("Stores", 48, 0, 57, 10, "f")
e.room("Station internals", 4, 14, 22, 23, "f")
e.room("Cargo and shuttle bay", 22, 14, 57, 23, "h")
e.room("Engineering corridor", 0, 10, 57, 14, "f")
e.setf("f", row(10, [8, 9, 23, 24, 33, 41, 42, 52]) + row(14, [12, 30, 31, 44, 45]))
e.put("F", row(1, [2, 3, 5, 6]))
e.put("O", [(12, 2), (13, 2), (13, 3), (2, 7), (3, 7)])
e.put("P", [(10, 1), (11, 1), (17, 8), (30, 8), (45, 4), (45, 5),
            (6, 16), (7, 16), (8, 16), (10, 18), (11, 18), (14, 16), (15, 16), (18, 19), (19, 19), (6, 21), (7, 21), (16, 21)])
e.put("G", block(22, 3, 25, 5))
e.put("k", [(18, 1), (19, 1), (28, 1), (29, 1), (36, 1), (37, 1), (20, 15)])
e.put("t", [(40, 1), (41, 1)])
e.put("c", [(14, 8), (47, 8), (47, 9), (55, 2), (56, 2), (56, 3), (54, 8), (23, 15), (24, 15), (23, 16), (56, 22), (55, 22), (56, 21)])
e.put("L", [(49, 1), (50, 1), (51, 1), (34, 15), (35, 15)])
e.put("S", [(53, 1)])
e.put("X", block(40, 18, 43, 19))
e.put("e", [(50, 16), (52, 20), (35, 21), (47, 22)])
e.outlines.append([26, 17, 2, 2])
e.warp("U", [(33, 5)], "main", 90, 95)
e.warp("R", [(1, 11), (1, 12), (1, 13)], "mine", 38, 4)

# ---------------------------------------------------------------- mine
n = A["mine"] = Area("mine", "The Mine", 44, 24, "M")
n.carve("Mine head", 2, 2, 10, 7, "m")
n.carve("", 10, 4, 16, 5, "m")
n.carve("Main dig", 16, 3, 30, 13, "m")
n.carve("", 30, 6, 35, 7, "m")
n.carve("Survey tunnel", 35, 2, 41, 10, "m")
n.carve("", 22, 13, 23, 17, "m")
n.carve("Cavern gate", 16, 17, 30, 21, "m")
n.setf("V", row(22, range(21, 26)))
n.put("y", row(21, range(21, 26)))
n.put("c", [(9, 2), (10, 2), (36, 9)])
n.put("L", [(4, 2)])
n.put("O", [(17, 4), (18, 4), (29, 12), (28, 12), (25, 3), (17, 12)])
n.put("x", [(28, 4), (20, 11), (28, 18), (17, 20)])
n.put("P", [(26, 8)])
n.put("k", [(40, 3)])
n.warp("R", [(2, 3), (2, 4), (2, 5)], "eng", 3, 12)
n.carve("", 20, 1, 21, 2, "m")
n.warp("R", [(20, 1), (21, 1)], "tunnels", 30, 35)
n.mirror()      # you arrive walking left, so the mine continues to the left

# ---------------------------------------------------------------- north tunnels (reached from the top of the mine's main dig)
u = A["tunnels"] = Area("tunnels", "North Tunnels", 60, 40, "M")
u.carve("Tunnel mouth", 26, 32, 35, 37, "m")
u.carve("", 30, 26, 31, 32, "m")
u.carve("Fungus hollow", 20, 19, 40, 27, "m")
u.carve("", 12, 22, 20, 23, "m")
u.carve("Lizard den", 3, 16, 12, 27, "m")
u.carve("", 40, 23, 47, 24, "m")
u.carve("Crystal gallery", 46, 13, 57, 26, "m")
u.carve("", 29, 12, 30, 19, "m")
u.carve("Deep chamber", 21, 3, 38, 12, "m")
u.carve("", 38, 6, 50, 7, "m")
u.carve("", 49, 7, 50, 13, "m")
u.carve("", 30, 38, 31, 38, "m")
u.put("x", [(22, 21), (38, 25), (5, 18), (10, 26), (48, 15), (55, 24), (24, 5), (36, 10)])
u.put("f", [(21, 19), (39, 19), (33, 27), (27, 20), (4, 26), (11, 17), (47, 25), (56, 14), (22, 11), (37, 4), (27, 37), (34, 33)])
u.put("v", [(25, 24), (35, 21), (7, 21), (52, 18), (28, 6), (33, 9), (27, 33), (34, 36), (3, 16), (57, 26)])
u.put("O", [(40, 27), (20, 27), (38, 3)])
u.warp("R", [(30, 38), (31, 38)], "mine", 22, 4)

# ---------------------------------------------------------------- who and what is where
START = ["west", 23, 67]
# name, area, tile x, tile y, talk radius (bigger when they stand behind a counter)
PEOPLE = [
    # Sara appears as a hologram in several places
    ["Sara", "top", 19, 3, 26], ["Sara", "west", 26, 70, 26], ["Sara", "west", 48, 35, 36], ["Sara", "main", 90, 65, 26],
]

# Daily schedules: "HH:MM", area, tile x, tile y, talk radius (36 = behind a counter).
# Before their first time of the day, a resident is at their last entry (where they spent the night).
# Each entry: time they set off, area, tile x, tile y, talk radius (36 = behind a counter),
# the way they face once there (d, u, l, r) and what they do there (work, eat, idle).
# Times are when they set off, so people far away leave earlier to reach dinner by 18:00.
# Lunch is only Job, Freya and Zaas. Dinner at 18:00 is everyone.
SCHEDULES_RAW = {
    "Jasper": [("06:00", "main", 137, 67, 36, "d", "work"), ("14:30", "main", 47, 48, 26, "d", "idle"), ("16:30", "main", 137, 67, 36, "d", "work"),
               ("21:30", "main", 26, 52, 26, "d", "idle")],
    "Evarra": [("06:00", "main", 142, 67, 36, "d", "work"), ("10:00", "east", 38, 33, 26, "u", "work"), ("13:00", "main", 142, 67, 36, "d", "work"),
               ("20:30", "main", 29, 52, 26, "d", "idle")],
    "Bram": [("07:00", "main", 26, 68, 36, "l", "work"), ("17:35", "main", 125, 70, 26, "d", "eat"), ("19:15", "main", 52, 50, 26, "d", "idle"),
             ("22:00", "main", 17, 52, 26, "d", "idle")],
    "Tikka": [("06:00", "eng", 39, 4, 26, "d", "work"), ("17:30", "main", 135, 70, 26, "d", "eat"), ("19:15", "main", 34, 68, 26, "d", "work"),
              ("21:30", "eng", 39, 4, 26, "d", "idle")],
    "Freya": [("06:00", "eng", 44, 5, 26, "r", "work"), ("11:00", "eng", 38, 19, 26, "r", "work"), ("12:30", "main", 140, 70, 26, "d", "eat"),
              ("13:30", "eng", 38, 19, 26, "r", "work"), ("16:30", "eng", 44, 5, 26, "r", "work"), ("17:30", "main", 140, 70, 26, "d", "eat"),
              ("19:15", "main", 58, 47, 26, "d", "idle"), ("21:30", "main", 20, 52, 26, "d", "idle")],
    "Job": [("06:30", "mine", 21, 8, 26, "d", "work"), ("12:00", "main", 120, 70, 26, "d", "eat"), ("13:30", "mine", 21, 8, 26, "d", "work"),
            ("17:15", "main", 120, 70, 26, "d", "eat"), ("19:15", "main", 158, 53, 26, "d", "idle")],
    "Zaas": [("07:00", "mine", 5, 5, 26, "l", "work"), ("12:15", "main", 126, 75, 26, "d", "eat"), ("13:45", "mine", 5, 5, 26, "l", "work"),
             ("17:05", "main", 126, 75, 26, "d", "eat"), ("19:15", "top", 35, 3, 26, "r", "idle"), ("23:00", "main", 162, 53, 26, "d", "idle")],
    "Tar'Besh": [("06:00", "top", 6, 5, 26, "d", "work"), ("17:35", "main", 131, 75, 26, "d", "eat"), ("19:15", "top", 31, 6, 26, "d", "idle"),
                 ("23:00", "top", 3, 15, 26, "d", "idle")],
    "Vzz'ket": [("06:00", "mine", 24, 19, 26, "d", "idle"), ("17:15", "main", 130, 70, 26, "d", "eat"), ("19:00", "mine", 24, 19, 26, "d", "idle"),
                ("22:00", "main", 86, 70, 26, "d", "idle"), ("23:30", "mine", 24, 19, 26, "d", "idle")],
}
SCHEDULES = {}
for who, rows in SCHEDULES_RAW.items():
    out = []
    for (hm, a, x, y, r, face_, act) in rows:
        assert face_ in "dulr" and act in ("work", "eat", "idle"), (who, face_, act)
        out.append([int(hm[:2]) * 60 + int(hm[3:]), a, x, y, r, face_, act])
    assert out == sorted(out, key=lambda e: e[0]), who
    SCHEDULES[who] = out


NODES = [
    ["iron_ore", "mine", 14, 6], ["iron_ore", "mine", 20, 3], ["iron_ore", "mine", 27, 9], ["iron_ore", "mine", 4, 9],
    ["copper_ore", "mine", 19, 13], ["copper_ore", "mine", 26, 7], ["copper_ore", "mine", 7, 3], ["copper_ore", "mine", 13, 10],
    ["iron_ore", "tunnels", 6, 19], ["iron_ore", "tunnels", 51, 22], ["iron_ore", "tunnels", 34, 4], ["iron_ore", "tunnels", 23, 26],
    ["copper_ore", "tunnels", 9, 24], ["copper_ore", "tunnels", 54, 16], ["copper_ore", "tunnels", 25, 9], ["copper_ore", "tunnels", 37, 20],
]
# Creatures: kind, area, tile x, tile y. They come back each morning.
ENEMIES = [
    ["bug", "tunnels", 24, 22], ["bug", "tunnels", 36, 22], ["bug", "tunnels", 33, 25], ["bug", "tunnels", 50, 19], ["bug", "tunnels", 30, 9],
    ["lizard", "tunnels", 6, 22], ["lizard", "tunnels", 8, 18], ["lizard", "tunnels", 53, 23], ["lizard", "tunnels", 26, 6], ["lizard", "tunnels", 35, 7],
]


def tc(x, y):
    return [x * 16 + 8, y * 16 + 8]


# kind, name, hint, area, [px, py], radius
THINGS = [
    ["bed", "Your bunk", "Sleep", "west", tc(22, 67), 26],
    ["wardrobe", "Locker", "Change look", "west", tc(33, 66), 26],
    ["look", "Landing pad", "Look", "west", [14 * 16, 35 * 16], 70],
    ["look", "Star dome", "Look", "west", tc(48, 6), 28],
    ["look", "Old bunks", "Look", "west", tc(45, 67), 24],
    ["look", "Locked apartment", "Look", "west", tc(71, 37), 24],
    ["look", "Locked apartment", "Look", "west", tc(81, 37), 24],
    ["look", "Hotel desk", "Look", "west", tc(32, 61), 26],
    ["pickup", "Crates", "Pick up a crate", "main", tc(31, 70), 26],
    ["look", "Fountain", "Look", "main", [90 * 16 + 8, 60 * 16 + 8], 92],
    ["board", "Bulletin board", "Read the board", "main", tc(95, 52), 24],
    ["look", "Market stall", "Look", "main", [99 * 16, 76 * 16 + 8], 28],
    ["look", "Market stall", "Look", "main", [78 * 16, 76 * 16 + 8], 28],
    ["look", "Shuttered workshop", "Look", "main", tc(36, 57), 24],
    ["look", "Abandoned shop", "Look", "main", tc(139, 57), 24],
    ["look", "Abandoned shop", "Look", "main", tc(149, 57), 24],
    ["look", "Library shelves", "Look", "main", tc(121, 45), 26],
    ["look", "Villa door", "Look", "east", tc(14, 32), 24],
    ["look", "Herb beds", "Look", "east", [39 * 16, 31 * 16 + 8], 30],
    ["look", "Broken agri dome", "Look", "east", [58 * 16, 35 * 16 + 8], 60],
    ["look", "Telescope", "Look", "top", tc(36, 2), 26],
    ["look", "Sealed lab", "Look", "top", tc(13, 12), 24],
    ["wreck", "Your ship", "Your ship", "eng", [42 * 16, 19 * 16], 46],
    ["drop", "Loading pad", "Set down the crate", "eng", [27 * 16, 18 * 16], 22],
    ["look", "Power core", "Look", "eng", [24 * 16, 4 * 16 + 8], 52],
    ["smelt_iron", "Iron furnace", "Smelt iron", "eng", [3 * 16, 1 * 16 + 8], 30],
    ["smelt_copper", "Copper furnace", "Smelt copper", "eng", [6 * 16, 1 * 16 + 8], 30],
    ["look", "Barricade", "Look", "mine", tc(20, 21), 26],
]
WRECK = ["eng", 42 * 16, 20 * 16]      # bottom-centre of the wreck sprite

# ---------------------------------------------------------------- checks
occupied = {(p[1], p[2], p[3]) for p in PEOPLE} | {(n[1], n[2], n[3]) for n in NODES}
for (a, x, y) in occupied:
    assert A[a].floor[y][x] in WALK and (A[a].obj[y][x] == " " or A[a].obj[y][x] in OPEN_OBJ), ("person on bad tile", a, x, y)


def walkable(a, x, y):
    ar = A[a]
    return 0 <= x < ar.w and 0 <= y < ar.h and ar.floor[y][x] in WALK and (ar.obj[y][x] == " " or ar.obj[y][x] in OPEN_OBJ) and (a, x, y) not in occupied


for ar in A.values():
    for (x, y, dest, tx, ty) in ar.warps:
        assert walkable(dest, tx, ty), ("warp lands on bad tile", ar.key, dest, tx, ty)
        assert not any(w[0] == tx and w[1] == ty for w in A[dest].warps), "warp lands on a warp"
assert walkable(*START)
seen, q = {tuple(START)}, deque([tuple(START)])
while q:
    a, x, y = q.popleft()
    nxt = [(a, x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    for (wx, wy, dest, tx, ty) in A[a].warps:
        if (wx, wy) == (x, y):
            nxt = [(dest, tx, ty)]
    for nb in nxt:
        if nb not in seen and walkable(*nb):
            seen.add(nb)
            q.append(nb)
for (item, a, x, y) in NODES:
    assert any((a, x + dx, y + dy) in seen for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), ("cannot reach ore vein", a, x, y)
for (kind, a, x, y) in ENEMIES:
    assert (a, x, y) in seen, ("creature on a bad tile", kind, a, x, y)
spots = {}
for who, rows in SCHEDULES.items():
    for (t_, a, x, y, r, face_, act) in rows:
        assert (a, x, y) in seen, ("schedule spot not reachable", who, a, x, y)
        assert not any(w[0] == x and w[1] == y for w in A[a].warps), ("schedule spot on a pad", who)
        assert spots.setdefault((a, x, y), who) == who, ("two residents share a spot", who, spots[(a, x, y)], a, x, y)
        if r > 26:
            around = (A[a].obj[y - 1][x], A[a].obj[y + 1][x], A[a].obj[y][x - 1], A[a].obj[y][x + 1])
            assert "C" in around or "I" in around, ("radius 36 but no counter beside them", who, a, x, y)
NEAR = ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 2), (0, -2))
for (name, a, x, y, r) in PEOPLE:
    assert any((a, x + dx, y + dy) in seen for dx, dy in NEAR), "cannot reach " + name + " in " + a
for (kind, name, hint, a, pos, r) in THINGS:
    tx, ty = pos[0] // 16, pos[1] // 16
    ok = any((a, tx + dx, ty + dy) in seen for dx in range(-7, 8) for dy in range(-7, 8)
             if ((tx + dx) * 16 + 8 - pos[0]) ** 2 + ((ty + dy) * 16 + 8 - pos[1]) ** 2 <= r * r)
    assert ok, "cannot reach thing " + name
for ar in A.values():
    for w in ar.warps:
        assert (ar.key, w[0], w[1]) in seen, ("warp unreachable", ar.key, w)
    assert all(len(r) == ar.w for r in ar.floor + ar.obj)
print("all people, things and warps reachable;", len(seen), "walkable tiles;", _next[0], "tile images")

# ---------------------------------------------------------------- station map (for the Map page of the menu)
# Every area drawn small on one picture. MAP_LAYOUT says where each area sits: [x, y, pixels per tile].
MAP_LAYOUT = {"west": [0, 36, 0.5], "main": [55, 26, 0.5], "east": [150, 40, 0.5], "top": [80, 0, 1.0], "eng": [84, 90, 1.0], "mine": [34, 90, 1.0],
              "tunnels": [0, 92, 0.5]}
MAP_TITLES = [["Survey Level", 123, 9], ["Spaceport District", 0, 33], ["Town Square", 57, 37], ["Agri Dome", 152, 37], ["Engineering", 146, 104], ["Mine", 36, 88], ["Tunnels", 0, 90]]
MAP_MARKS = [
    [1, "west", 27, 71, "Your quarters"], [2, "west", 15, 35, "Spaceport"], [3, "west", 48, 40, "Reception"],
    [4, "main", 23, 67, "Bram's Sundries"], [5, "main", 34, 67, "Fabrication shop"], [6, "main", 52, 48, "Common area"],
    [7, "main", 124, 47, "Library"], [8, "main", 131, 72, "Mess hall"], [9, "east", 38, 35, "Herb beds"],
    [10, "top", 19, 4, "Sara's suite"], [11, "top", 32, 4, "Observatory"], [12, "eng", 8, 5, "Ore processing"],
    [13, "eng", 41, 5, "Engineering bay"], [14, "eng", 40, 19, "Shuttle bay"], [15, "mine", 20, 8, "Main dig"], [16, "mine", 20, 19, "Cavern gate"], [17, "tunnels", 30, 23, "North tunnels"],
]
MAP_COLORS = {".": (200, 206, 214), ",": (176, 84, 76), "f": (110, 120, 134), "h": (130, 138, 150), "u": (170, 184, 198), "s": (132, 96, 66),
              "m": (124, 106, 94), "i": (196, 172, 138), "U": (238, 202, 64), "D": (238, 202, 64), "A": (238, 202, 64), "R": (238, 202, 64),
              "#": (64, 76, 100), "w": (64, 76, 100), "Z": (64, 76, 100), "d": (110, 190, 210), "O": (70, 150, 210), "J": (70, 150, 210), "B": (170, 170, 182)}
SM = Img(196, 116)
for k, (ox, oy, sc) in MAP_LAYOUT.items():
    ar = A[k]
    step = int(round(1 / sc))
    for y in range(0, ar.h, step):
        for x in range(0, ar.w, step):
            cols = [MAP_COLORS[ar.floor[yy][xx]] for yy in range(y, min(ar.h, y + step)) for xx in range(x, min(ar.w, x + step))
                    if ar.floor[yy][xx] in MAP_COLORS]
            if len(cols) * 2 >= step * step:
                SM.px(ox + x // step, oy + y // step, tuple(sum(c[i] for c in cols) // len(cols) for i in range(3)))
SM.save(art("station_map.png"))

# ---------------------------------------------------------------- write map_data.gd
FACE_OF = {"#": "W", "M": "N", "d": "g"}
for ar in A.values():
    for y in range(ar.h):
        for x in range(ar.w):
            ch = ar.floor[y][x]
            open_below = y + 1 < ar.h and ar.floor[y + 1][x] in WALK
            if ch in FACE_OF and open_below:
                ar.floor[y][x] = FACE_OF[ch]
            elif ch == "w" and not open_below:
                ar.floor[y][x] = "#"

areas = {}
for k, ar in A.items():
    areas[k] = {"title": ar.title, "floor": ["".join(r) for r in ar.floor], "obj": ["".join(r) for r in ar.obj],
                "zones": ar.zones, "warps": ar.warps, "outlines": ar.outlines}
with open(os.path.join(OUT, "scripts", "map_data.gd"), "w") as f:
    f.write("extends RefCounted\n# Generated by tools/build.py - edit that file, not this one.\n")
    f.write("# Each area has two layers of the same size: floor and objects (space = no object).\n\n")
    f.write("const TILE_FLOOR = " + json.dumps(TILE_FLOOR) + "\n")
    f.write("const TILE_OBJ = " + json.dumps(TILE_OBJ) + "\n")
    f.write("const SOLID_FLOOR = " + json.dumps(SOLID_FLOOR) + "\n")
    f.write("const WALL_FACES = " + json.dumps(WALL_FACES) + "\n")
    f.write("const TILE_VARIANTS = " + json.dumps(TILE_VARIANTS) + "\n")
    f.write("const TALL = " + json.dumps(TALL) + "\n")
    f.write("const TILE_COLUMNS = " + json.dumps(TILE_COLUMNS) + "\n")
    f.write("const OPEN_OBJ = " + json.dumps(OPEN_OBJ) + "\n")
    f.write("const START = " + json.dumps(START) + "\n")
    f.write("const WRECK = " + json.dumps(WRECK) + "\n")
    f.write("const PEOPLE = " + json.dumps(PEOPLE) + "\n")
    f.write("const NODES = " + json.dumps(NODES) + "\n")
    f.write("const ENEMIES = " + json.dumps(ENEMIES) + "\n")
    f.write("const MAP_LAYOUT = " + json.dumps(MAP_LAYOUT) + "\n")
    f.write("const MAP_TITLES = " + json.dumps(MAP_TITLES) + "\n")
    f.write("const MAP_MARKS = " + json.dumps(MAP_MARKS) + "\n")
    f.write("const SCHEDULES = {\n" + "".join("\t" + json.dumps(k) + ": " + json.dumps(v) + ",\n" for k, v in SCHEDULES.items()) + "}\n")
    f.write("const THINGS = " + json.dumps(THINGS) + "\n")
    f.write("const AREAS = {\n")
    for k, d in areas.items():
        f.write(json.dumps(k) + ": {\n")
        for key in ("title", "zones", "warps", "outlines"):
            f.write("\t" + json.dumps(key) + ": " + json.dumps(d[key]) + ",\n")
        for key in ("floor", "obj"):
            f.write("\t" + json.dumps(key) + ": [\n" + "".join("\t\t" + json.dumps(r) + ",\n" for r in d[key]) + "\t],\n")
        f.write("},\n")
    f.write("}\n")

# ---------------------------------------------------------------- previews (for checking only)
# Pictures of every area, composed from the real files in art/ the way the game draws them.
if PREV:
    os.makedirs(PREV, exist_ok=True)
    from PIL import Image
    tiles_img = Image.open(art("tiles.png")).convert("RGBA")
    cell = tiles_img.width // TILE_COLUMNS

    def piece(index, upper):
        return tiles_img.crop((index * cell, 0 if upper else cell, index * cell + cell, cell if upper else 2 * cell))

    def frame(name, cols, rows_, col=0, r=0, wide=1):
        im = Image.open(art(name)).convert("RGBA")
        fw, fh = im.width // cols, im.height // rows_
        f_ = im.crop((col * fw, r * fh, col * fw + fw, r * fh + fh))
        return f_.resize((cell * wide, cell * wide * fh // fw), Image.NEAREST)

    ids = {"Sara": "sara", "Tar'Besh": "tarbesh", "Bram": "bram", "Jasper": "jasper", "Evarra": "evarra",
           "Tikka": "tikka", "Freya": "freya", "Job": "job", "Zaas": "zaas", "Vzz'ket": "vzzket"}
    fx_obj = {"k": ("fx_console.png", True), "K": ("fx_display.png", True), "F": ("fx_furnace.png", False), "G": ("fx_core.png", False)}
    for k, ar in A.items():
        im = Image.new("RGBA", (ar.w * cell, ar.h * cell), (11, 16, 38, 255))
        for y in range(ar.h):
            for x in range(ar.w):
                fch, och = ar.floor[y][x], ar.obj[y][x]
                if fch in TILE_FLOOR:
                    nv = TILE_VARIANTS[fch]
                    var = abs((x * 73856093) ^ (y * 19349663)) % (nv * 6)
                    im.alpha_composite(piece(TILE_FLOOR[fch] + (var if var < nv else 0), False), (x * cell, y * cell))
                    if fch == "O":
                        im.alpha_composite(frame("fx_water.png", 4, 1), (x * cell, y * cell))
                if och in TILE_OBJ:
                    im.alpha_composite(piece(TILE_OBJ[och], False), (x * cell, y * cell))
                    if och in fx_obj and not fx_obj[och][1]:
                        im.alpha_composite(frame(fx_obj[och][0], 4, 1), (x * cell, y * cell))
        for (item, a, x, y) in NODES:
            if a == k:
                im.alpha_composite(frame(item + ".png", 2, 1), (x * cell, y * cell))
        first = [[who, rows[0][1], rows[0][2], rows[0][3], 0] for who, rows in SCHEDULES.items()]
        for (name, a, x, y, r) in PEOPLE + first:
            if a == k:
                im.alpha_composite(frame("npc_%s.png" % ids[name], 4, 3), (x * cell, (y - 1) * cell))
        if WRECK[0] == k:
            w_ = frame("wreck.png", 4, 1, wide=4)
            im.alpha_composite(w_, (WRECK[1] * cell // 16 - w_.width // 2, WRECK[2] * cell // 16 - w_.height))
        if START[0] == k:
            im.alpha_composite(frame("player.png", 4, 3), (START[1] * cell, (START[2] - 1) * cell))
        for y in range(1, ar.h):
            for x in range(ar.w):
                for ch, table in ((ar.floor[y][x], TILE_FLOOR), (ar.obj[y][x], TILE_OBJ)):
                    if ch in TALL and ch in table:
                        im.alpha_composite(piece(table[ch], True), (x * cell, (y - 1) * cell))
                och = ar.obj[y][x]
                if och in fx_obj and fx_obj[och][1]:
                    im.alpha_composite(frame(fx_obj[och][0], 4, 1), (x * cell, (y - 1) * cell))
        im.save(os.path.join(PREV, k + ".png"))
