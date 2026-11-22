"""Helpers for ship art at double resolution: 48 art pixels per room cell (Claude, 21 Nov 2026).
Zachary: "lets double the pixels", then "lets do all the ships before we add to game".
Built on pixkit.py (materials, tones, bevels, tubes, domes).
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from pixkit import Pix, RAMPS

CELL = 48
RAMPS.setdefault("olive", ["#2a3226", "#3a4434", "#4e5a46", "#647058", "#7e8a6e", "#9caa88"])
RAMPS.setdefault("rope", ["#4a3a22", "#66522e", "#82693c", "#9c824c", "#b49c62", "#ccb67e"])
RAMPS.setdefault("cloth", ["#5a4a3a", "#76624c", "#927c60", "#ac9676", "#c4b08e", "#dccaaa"])
RAMPS.setdefault("navy", ["#141a2e", "#1c2540", "#263354", "#33446a", "#465a84", "#60769e"])
RAMPS.setdefault("rock", ["#2a2526", "#3a3334", "#4c4344", "#5e5454", "#726868", "#8a7f7c"])


def S(pts, k=2):
    return [(x * k, y * k) for x, y in pts]


def mirror(pts, h):
    return [(x, h - 1 - y) for x, y in pts]


def grid(p):
    return np.mgrid[0:p.h, 0:p.w]


def rivet_row(p, x0, x1, y, step=6):
    for x in range(x0, x1 + 1, step):
        p.rivet(x, y)


def rivet_col(p, x, y0, y1, step=6):
    for y in range(y0, y1 + 1, step):
        p.rivet(x, y)


def plate(p, r, mat, clip=None, face=4, width=3, rivets=True, seams=0, vertical=True):
    """A raised armour plate with corner rivets, a rivet row along the top and seams across it."""
    x0, y0, x1, y1 = r
    m = p.mask(rect=r)
    if clip is not None:
        m &= clip
    if m.sum() == 0:
        return m
    p.bevel(m, mat, width=width, face=face, shade_lower=False)
    if rivets:
        for (rx, ry) in ((x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3)):
            p.rivet(rx, ry)
        if x1 - x0 > 24:
            rivet_row(p, x0 + 9, x1 - 9, y0 + 3, 8)
    for k in range(seams):
        if vertical:
            x = x0 + (k + 1) * (x1 - x0) // (seams + 1)
            p.engrave([(x, y0 + 4), (x, y1 - 4)])
        else:
            y = y0 + (k + 1) * (y1 - y0) // (seams + 1)
            p.engrave([(x0 + 4, y), (x1 - 4, y)])
    return m


def hazard(p, m, step=6):
    yy, xx = grid(p)
    m = m & (p.tone >= 0)
    p.mat[m] = "yellow"
    st = m & (((xx + yy) // step) % 2 == 0)
    p.mat[st] = "dark"
    p.tone[st] = np.maximum(p.tone[st] - 1, 1)


def windows(p, x0, y, n, step, w=4, h=2, mat="glass"):
    """A row of lit port windows, each with a frame, a bright top-left pixel."""
    for i in range(n):
        x = x0 + i * step
        f = p.mask(rect=(x - 1, y - 1, x + w, y + h)) & (p.tone >= 0)
        p.tone[f] = np.maximum(p.tone[f] - 2, 0)
        m = p.mask(rect=(x, y, x + w - 1, y + h - 1))
        p.paint(m, mat)
        p.set_tone(m, 4)
        p.set_tone(p.mask(rect=(x, y, x + 1, y)), 5)


def lit_windows(p, x0, y, n, step, w=3, h=2, mat="glow_yellow", tone=3):
    for i in range(n):
        x = x0 + i * step
        f = p.mask(rect=(x - 1, y - 1, x + w, y + h)) & (p.tone >= 0)
        p.tone[f] = np.maximum(p.tone[f] - 2, 0)
        p.glow(p.mask(rect=(x, y, x + w - 1, y + h - 1)), mat, tone)


def thruster(p, x0, y0, y1, mat="glow", depth=14):
    """An exhaust glow behind the back edge at x0, between y0 and y1."""
    cy, r = (y0 + y1) / 2, (y1 - y0) / 2
    yy, xx = grid(p)
    g = p.mask(ellipse=(x0 - depth, cy - r, x0 + depth, cy + r)) & (xx < x0) & (p.tone < 0)
    p.glow(g, mat, 2)
    p.glow(p.mask(ellipse=(x0 - depth + 3, cy - r * 0.65, x0 + depth, cy + r * 0.65)) & g, mat, 3)
    p.glow(p.mask(ellipse=(x0 - depth + 6, cy - r * 0.35, x0 + depth, cy + r * 0.35)) & g, mat, 4)
    p.glow(p.mask(ellipse=(x0 - depth + 9, cy - r * 0.15, x0 + depth, cy + r * 0.15)) & g, mat, 5)


def nozzle(p, x0, y0, x1, y1, glow="glow", depth=14, mat="metal"):
    """A ribbed engine nozzle pointing left, with a dark throat and its exhaust."""
    p.tube(p.mask(rect=(x0, y0, x1, y1)), mat, "x", bands=(5, 5, 4, 4, 3, 3, 3, 2, 2, 1))
    for x in range(x0 + 6, x1 - 2, 5):
        p.engrave([(x, y0 + 1), (x, y1 - 1)])
    p.tube(p.mask(rect=(x0, y0 + 3, x0 + 4, y1 - 3)), "dark", "x", shadow=False)
    thruster(p, x0, y0 + 2, y1 - 2, glow, depth)


def turret(p, cx, cy, r=14, mat="gunmetal", barrel="metal", length=30, twin=True, light="glow_red"):
    p.bevel(p.mask(ellipse=(cx - r, cy - r, cx + r, cy + r)), mat, width=3, face=4, shade_lower=False)
    p.engrave([(cx - r + 3, cy), (cx + r - 3, cy)])
    p.dome(p.mask(ellipse=(cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6)), barrel, shadow=False)
    for dy in ((-4, 3) if twin else (-1,)):
        p.tube(p.mask(rect=(cx + r // 2, cy + dy, cx + length, cy + dy + 2)), barrel, "x", bands=(5, 3, 2))
        p.tube(p.mask(rect=(cx + length - 4, cy + dy - 1, cx + length + 2, cy + dy + 3)), mat, "x", bands=(4, 3, 2, 1))
    if light:
        p.glow(p.mask(rect=(cx - 2, cy - 2, cx + 1, cy + 1)), light, 3)


def light(p, x, y, mat="glow_red", size=2):
    p.glow(p.mask(rect=(x, y, x + size - 1, y + size - 1)), mat, 4)


def skull(p, x, y, big=True):
    rows = (["..XXXXXX..", ".XXXXXXXX.", "XXXXXXXXXX", "XX..XX..XX", "XX..XX..XX", "XXXXXXXXXX",
             ".XXXX.XXX.", "..XXXXXX..", "..X.XX.X..", "..XXXXXX.."] if big else
            [".XXXXX.", "XXXXXXX", "X..X..X", "XXX.XXX", ".XXXXX.", ".X.X.X."])
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            yy, xx = y + j, x + i
            if not (0 <= yy < p.h and 0 <= xx < p.w) or p.tone[yy, xx] < 0:
                continue
            if ch == "X":
                p.mat[yy, xx] = "bone"; p.tone[yy, xx] = 5 if j < 3 else (4 if j < 7 else 3)
            else:
                p.mat[yy, xx] = "dark"; p.tone[yy, xx] = 1


DIGITS = {"0": ["XXX", "X.X", "X.X", "X.X", "XXX"], "1": [".X.", "XX.", ".X.", ".X.", "XXX"],
          "2": ["XXX", "..X", "XXX", "X..", "XXX"], "3": ["XXX", "..X", ".XX", "..X", "XXX"],
          "4": ["X.X", "X.X", "XXX", "..X", "..X"], "5": ["XXX", "X..", "XXX", "..X", "XXX"],
          "6": ["XXX", "X..", "XXX", "X.X", "XXX"], "7": ["XXX", "..X", ".X.", ".X.", ".X."],
          "8": ["XXX", "X.X", "XXX", "X.X", "XXX"], "9": ["XXX", "X.X", "XXX", "..X", "XXX"],
          "-": ["...", "...", "XXX", "...", "..."], "T": ["XXX", ".X.", ".X.", ".X.", ".X."],
          "P": ["XX.", "X.X", "XX.", "X..", "X.."], "M": ["X.X", "XXX", "XXX", "X.X", "X.X"],
          "C": [".XX", "X..", "X..", "X..", ".XX"], "E": ["XXX", "X..", "XX.", "X..", "XXX"]}


def stencil(p, x, y, text, mat=None, tone=1):
    """Tiny 3x5 painted letters: dark by default, or a material."""
    for c in text:
        rows = DIGITS.get(c)
        if rows:
            for j, row in enumerate(rows):
                for i, ch in enumerate(row):
                    if ch == "X" and p.tone[y + j, x + i] >= 0:
                        if mat:
                            p.mat[y + j, x + i] = mat
                        p.tone[y + j, x + i] = tone
        x += 4


def wear(p, rng, rust=0, grime=0.04, mats=("gunmetal", "metal"), scuffs=0):
    """Weathering: rust patches on the given materials, sparse dark grime, light scuffs."""
    yy, xx = grid(p)
    on = np.isin(p.mat, list(mats)) & (p.tone >= 2)
    for _ in range(rust):
        cx, cy, r = rng.randrange(20, p.w - 20), rng.randrange(10, p.h - 10), rng.randrange(3, 7)
        blob = on & ((xx - cx) ** 2 + ((yy - cy) * 1.6) ** 2 < r * r)
        p.mat[blob] = "rust"; p.tone[blob] = np.clip(p.tone[blob] - 1, 1, 3)
    if grime:
        nr = np.random.default_rng(rng.randrange(1 << 30)).random((p.h, p.w))
        g = (p.tone >= 3) & np.isin(p.mat, list(mats)) & (nr < grime)
        p.shade(g, -1)
    for _ in range(scuffs):
        x, y = rng.randrange(20, p.w - 20), rng.randrange(10, p.h - 10)
        if p.mat[y, x] in mats:
            p.engrave([(x, y), (x + rng.randrange(3, 8), y + rng.randrange(-2, 3))], highlight=False)


def scorch(p, cx, cy, r):
    p.shade(p.mask(ellipse=(cx - r - 3, cy - r, cx + r + 3, cy + r)), -2)
    p.shade(p.mask(ellipse=(cx - r // 2, cy - 1, cx + r // 2, cy + 1)), -1)


def cable(p, x0, x1, y, mat="strap", clamps=18, clamp_mat="metal"):
    p.tube(p.mask(rect=(x0, y, x1, y + 4)), mat, "x", bands=(5, 4, 2, 1, 1))
    for x in range(x0 + 8, x1, clamps):
        p.bevel(p.mask(rect=(x, y - 1, x + 3, y + 5)), clamp_mat, width=1, face=4, shade_lower=False)


def sheet(items, path, scale=2, cols=2, pad=16, bg=(20, 24, 36, 255), label=True):
    """Lay the ships out on one sheet, nearest-neighbour scaled."""
    from PIL import Image, ImageDraw
    ims = [(name, p.render() if hasattr(p, "render") else p) for name, p in items]
    cw = max(im.width for _, im in ims) * scale + pad
    ch = max(im.height for _, im in ims) * scale + pad + (14 if label else 0)
    rows = (len(ims) + cols - 1) // cols
    out = Image.new("RGBA", (cw * cols + pad, ch * rows + pad), bg)
    d = ImageDraw.Draw(out)
    for i, (name, im) in enumerate(ims):
        x, y = pad + (i % cols) * cw, pad + (i // cols) * ch
        if label:
            d.text((x, y), name, fill=(200, 205, 220, 255))
            y += 14
        out.alpha_composite(im.resize((im.width * scale, im.height * scale), Image.NEAREST), (x, y))
    out.save(path)
    return out


# ---------------------------------------------------------------- cut-away interiors, FTL-simple

def interior(p, rooms, doors, cell=CELL, wall_mat="wall"):
    """Cut the rooms into a hull picture: a dark frame round the rooms, deck floors, 4-px walls on the cell edges
    with door gaps (the game draws the doors), and one machine per system. Keeps in step with the game: rooms are
    {id: (col, row, w, h, sys)}, doors are ((c1, r1), (c2, r2)); a door gap is 7..17 of every 24 cell px, scaled."""
    from scipy import ndimage as nd
    k = cell / 24.0
    H, W = p.h, p.w
    block = np.zeros((H, W), bool)
    for (cx, cy, cw, ch, _) in rooms.values():
        block[cy * cell:(cy + ch) * cell, cx * cell:(cx + cw) * cell] = True
    frame = nd.binary_dilation(block, iterations=int(3 * k)) & ~block
    p.mat[frame] = wall_mat; p.tone[frame] = 3
    p.tone[frame & ~nd.binary_erosion(frame | block, iterations=1)] = 1
    p.lines[block] = False
    for rid, (cx, cy, cw, ch, sysname) in rooms.items():
        x0, y0, x1, y1 = cx * cell, cy * cell, (cx + cw) * cell - 1, (cy + ch) * cell - 1
        m = p.mask(rect=(x0, y0, x1, y1))
        p.mat[m] = "deck"; p.tone[m] = 3
        # floor tiles: a light top edge and a dark bottom edge per half cell
        step = cell // 2
        for tx in range(x0, x1, step):
            for ty in range(y0, y1, step):
                p.set_tone(p.mask(rect=(tx, ty, tx + step - 1, ty)), 4)
                p.set_tone(p.mask(rect=(tx, ty + step - 1, tx + step - 1, ty + step - 1)), 2)
                p.set_tone(p.mask(rect=(tx + step - 1, ty, tx + step - 1, ty + step - 1)), 2)
    def room_at(c):
        for rid, (cx, cy, cw, ch, _) in rooms.items():
            if cx <= c[0] < cx + cw and cy <= c[1] < cy + ch:
                return rid
        return ""
    wall = np.zeros((H, W), bool)
    t = int(2 * k)
    for rid, (cx, cy, cw, ch, _) in rooms.items():
        for x in range(cx, cx + cw):
            for y in range(cy, cy + ch):
                x0, y0 = x * cell, y * cell
                if room_at((x + 1, y)) != rid: wall[y0:y0 + cell, x0 + cell - t:x0 + cell] = True
                if room_at((x - 1, y)) != rid: wall[y0:y0 + cell, x0:x0 + t] = True
                if room_at((x, y + 1)) != rid: wall[y0 + cell - t:y0 + cell, x0:x0 + cell] = True
                if room_at((x, y - 1)) != rid: wall[y0:y0 + t, x0:x0 + cell] = True
    g0, g1 = int(7 * k), int(17 * k)
    for (a, b) in doors:
        (c1, r1), (c2, r2) = a, b
        if r1 == r2:
            x = max(c1, c2) * cell; y = r1 * cell
            wall[y + g0:y + g1, x - t:x + t] = False
        else:
            y = max(r1, r2) * cell; x = c1 * cell
            wall[y - t:y + t, x + g0:x + g1] = False
    wall &= p.tone >= 0
    p.mat[wall] = wall_mat; p.tone[wall] = 1
    for rid, (cx, cy, cw, ch, sysname) in rooms.items():
        machine(p, sysname, cx * cell, cy * cell, cw * cell, ch * cell, k)
    return p


def machine(p, sysname, x, y, w, h, k):
    """The system's console or machine against the room's back wall (the left side; the cockpit's at the front)."""
    t = int(2 * k) + 2
    def box(x0, y0, x1, y1, mat="console"):
        p.bevel(p.mask(rect=(x0, y0, x1, y1)), mat, width=1, face=3, shade_lower=False)
    cy = y + h // 2
    if sysname == "engines":
        for yy in range(y + t + 2, y + h - t - 20, 24):
            box(x + t + 2, yy, x + t + 22, yy + 18, "metal")
            p.glow(p.mask(rect=(x + t + 6, yy + 6, x + t + 18, yy + 11)), "glow", 3)
    elif sysname == "weapons":
        box(x + t + 2, y + t + 2, x + t + 14, y + h - t - 3, "console")
        for yy in range(y + t + 6, y + h - t - 6, 8):
            p.glow(p.mask(rect=(x + t + 5, yy, x + t + 10, yy + 2)), "glow_red", 3)
        box(x + w // 2 - 6, y + t + 2, x + w // 2 + 6, y + t + 10, "pipe")
    elif sysname == "shields":
        p.bevel(p.mask(ellipse=(x + w // 2 - 14, cy - 14, x + w // 2 + 14, cy + 14)), "metal", width=2, face=3, shade_lower=False)
        p.dome(p.mask(ellipse=(x + w // 2 - 9, cy - 9, x + w // 2 + 9, cy + 9)), "blue")
    elif sysname == "life":
        p.tube(p.mask(rect=(x + t + 2, cy - 12, x + w - t - 3, cy + 10)), "blue", "x")
        p.engrave([(x + t + 2, cy - 1), (x + w - t - 3, cy - 1)])
        box(x + t + 2, y + h - t - 8, x + w - t - 3, y + h - t - 4, "pipe")
    elif sysname == "pilot":
        box(x + w - t - 12, y + t + 2, x + w - t - 3, y + h - t - 3, "console")
        p.glow(p.mask(rect=(x + w - t - 10, y + t + 8, x + w - t - 7, y + h - t - 9)), "glow_teal", 3)
        for sy in ([cy - 4] if h <= 48 else [y + h // 4 - 4, y + 3 * h // 4 - 4]):
            box(x + w - t - 34, sy - 8, x + w - t - 20, sy + 12, "red")
    elif sysname == "drones":
        p.bevel(p.mask(ellipse=(x + w // 2 - 15, cy - 15, x + w // 2 + 15, cy + 15)), "console", width=1, face=3, shade_lower=False)
        p.paint(p.mask(ellipse=(x + w // 2 - 9, cy - 9, x + w // 2 + 9, cy + 9)), "yellow")
    elif sysname in ("", "crew"):
        # bunks along the top wall, a locker
        for bx in range(x + t + 4, x + w - t - 20, 22):
            box(bx, y + t + 2, bx + 18, y + t + 12, "cloth")
            box(bx + 1, y + t + 3, bx + 5, y + t + 11, "white")
        box(x + w - t - 10, y + h - t - 20, x + w - t - 3, y + h - t - 3, "metal")
