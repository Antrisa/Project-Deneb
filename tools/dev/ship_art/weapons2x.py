"""Weapon art at double resolution (Claude, 21 Nov 2026). Zachary: "art for the different weapons like lasers missles and
beams"; guns attach to the hull's sides, FTL-style, where a ship's mounts are.

art/ships/weapons/<id>.png  six frames side by side, barrel pointing right, the mount at the left middle:
    idle, charging 1, charging 2, ready (glowing), firing 1 (recoil, muzzle flash), firing 2.
    Small guns: 64 x 24 a frame (32 x 12 cell px); big guns (Ivan's cannon): 96 x 32. The mount point is
    (6, 12) small, (8, 16) big. Zachary: "models need detail" -- shaded housings, seams, rivets, vents, hoses,
    status and charge lights, banded barrels and muzzle shrouds.
art/ships/shots/missile.png three 16 x 8 frames, flying right (the flame flickers).
art/ships/store/<id>.png    48 x 48 store pictures.

Run from the repo root:  python3 -I tools/dev/ship_art/weapons2x.py .
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from PIL import Image
from pixkit import Pix
import kit2x  # noqa: F401  (adds the olive, rope, cloth, navy and rock colour ramps)

SMALL, BIG = (64, 24), (96, 32)


# ---------------------------------------------------------------- parts

def tip(p, x0, y0, x1, y1, g, frame):
    """The emitter: dark when idle, warming while charging, bright when ready and firing."""
    tone = {0: None, 1: 1, 2: 2, 3: 4, 4: 5, 5: 3}[frame]
    if tone is None:
        p.bevel(p.mask(rect=(x0, y0, x1, y1)), "dark", width=1, face=2, shade_lower=False)
    else:
        p.glow(p.mask(rect=(x0, y0, x1, y1)), g, tone)
        if frame in (3, 4):
            p.glow(p.mask(rect=(x0, y0, x0, y0)), g, 5)


def flash(p, x, y, g, frame, size=5):
    if frame == 4:
        p.glow(p.mask(ellipse=(x, y - size, x + size * 2 + 3, y + size)), g, 2)
        p.glow(p.mask(ellipse=(x + 1, y - size + 2, x + size * 2, y + size - 2)), g, 4)
        p.glow(p.mask(ellipse=(x + 2, y - size // 2, x + size + 1, y + size // 2)), g, 5)
        for dy in (-size - 1, size + 1):                      # sparks off the flash
            p.glow(p.mask(rect=(x + size, y + dy, x + size + 1, y + dy)), g, 4)
    elif frame == 5:
        p.glow(p.mask(ellipse=(x, y - size // 2, x + size + 1, y + size // 2)), g, 2)
        p.glow(p.mask(rect=(x + 1, y - 1, x + 2, y)), g, 4)


def recoil(frame):
    return {4: -3, 5: -1}.get(frame, 0)


def housing(p, x0, y0, x1, y1, mat, seams=(), rivets=True, face=4, width=2):
    p.bevel(p.mask(rect=(x0, y0, x1, y1)), mat, width=width, face=face, shade_lower=False)
    for x in seams:
        p.engrave([(x, y0 + 2), (x, y1 - 2)])
    if rivets:
        for (rx, ry) in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
            p.rivet(rx, ry)


def vents(p, x0, x1, y, n, step=3):
    for k in range(n):
        p.slot(x0, y + k * step, x1, y + k * step)


def barrel(p, x0, x1, yc, h, mat="metal", rings=(), ring_mat="gunmetal"):
    p.tube(p.mask(rect=(x0, yc - h // 2, x1, yc - h // 2 + h - 1)), mat, "x",
           bands=(5, 5, 4, 3, 3, 2, 1) if h >= 5 else (5, 3, 2, 1))
    for x in rings:
        p.tube(p.mask(rect=(x, yc - h // 2 - 1, x + 1, yc - h // 2 + h)), ring_mat, "x", bands=(4, 3, 2, 1))


def hose(p, pts, mat="pipe"):
    m = p._line(pts, width=2)
    p.tube(m, mat, "x", bands=(5, 3, 2), shadow=False)
    x, y = pts[len(pts) // 2]
    p.bevel(p.mask(rect=(x - 1, y - 2, x + 1, y + 2)), "metal", width=1, face=4, shade_lower=False)


def status(p, x, y, g, f):
    """A little status light: off while charging, lit when ready or firing."""
    if f in (3, 4, 5):
        p.glow(p.mask(rect=(x, y, x + 1, y + 1)), g, 4)
    else:
        p.bevel(p.mask(rect=(x, y, x + 1, y + 1)), "dark", width=1, face=2, shade_lower=False)


def charge_bar(p, x, y, n, g, f):
    """A row of charge lights that fill as it charges."""
    lit = {0: 0, 1: n // 3, 2: 2 * n // 3, 3: n, 4: n, 5: n // 2}[f]
    for k in range(n):
        if k < lit:
            p.glow(p.mask(rect=(x + k * 2, y, x + k * 2, y + 1)), g, 3 if k < lit - 1 else 4)
        else:
            p.set_tone(p.mask(rect=(x + k * 2, y, x + k * 2, y + 1)), 1)


def bracket(p, mat="gunmetal", big=False):
    """The clamp that holds the gun to the hull, at the mount (left middle), with bolts and a hazard edge."""
    h = 32 if big else 24
    m = h // 2
    p.bevel(p.mask(rect=(0, m - 8, 11, m + 7)), mat, width=2, face=3, shade_lower=False)
    p.bevel(p.mask(rect=(2, m - 10, 7, m + 9)), "metal", width=1, face=4, shade_lower=False)
    for y in (m - 8, m + 6):
        p.rivet(4, y)
    p.paint(p.mask(rect=(9, m - 7, 10, m + 6)), "yellow")
    for y in range(m - 7, m + 7, 3):
        p.mat[y, 9:11] = "dark"


# ---------------------------------------------------------------- the guns (64 x 24 a frame; the mount at (6, 12))

GLOW = {"burst_laser": "glow_red", "rabble_laser": "glow_green", "heavy_laser": "glow_green", "missile_launcher": "glow",
        "cutting_beam": "glow_red", "heavy_beam": "glow_yellow", "ivan_cannon": "glow_yellow"}


def burst_laser(f):
    """Terran: a white and orange housing, two barrels in a shroud, a charge row."""
    p = Pix(*SMALL); r = recoil(f); g = "glow_red"
    bracket(p)
    housing(p, 10, 3, 34, 20, "white", seams=(18, 28))
    p.paint(p.mask(rect=(13, 3, 16, 20)), "orange")
    vents(p, 20, 26, 6, 3)
    charge_bar(p, 20, 15, 4, g, f)
    status(p, 30, 6, g, f)
    hose(p, [(12, 21), (22, 22), (32, 21)])
    p.bevel(p.mask(rect=(33 + r, 4, 40 + r, 19)), "gunmetal", width=1, face=4, shade_lower=False)
    for y in (8, 15):
        barrel(p, 40 + r, 54 + r, y, 4, "metal", rings=(44 + r, 50 + r))
        p.bevel(p.mask(rect=(54 + r, y - 3, 56 + r, y + 2)), "gunmetal", width=1, face=4, shade_lower=False)
        tip(p, 57 + r, y - 1, 58 + r, y + 1, g, f)
        flash(p, 59 + r, y, g, f, 3)
    return p


def rabble_laser(f):
    """Rabble: a rusty box held with straps and wire, a crooked barrel, a green tip."""
    p = Pix(*SMALL); r = recoil(f); g = "glow_green"
    bracket(p, "rust")
    housing(p, 10, 5, 30, 19, "rust", seams=(20,))
    p.bevel(p.mask(rect=(14, 3, 18, 21)), "strap", width=1, face=4, shade_lower=False)
    p.bevel(p.mask(rect=(23, 9, 29, 15)), "metal", width=1, face=3, shade_lower=False)
    for (x, y) in ((24, 10), (28, 10), (24, 14), (28, 14)):
        p.rivet(x, y)
    status(p, 12, 8, g, f)
    hose(p, [(20, 20), (30, 21), (40, 18)], "strap")
    p.bevel(p.mask(rect=(30 + r, 8, 36 + r, 16)), "gunmetal", width=1, face=4, shade_lower=False)
    barrel(p, 36 + r, 52 + r, 12, 5, "gunmetal", rings=(41 + r, 47 + r), ring_mat="rust")
    p.bevel(p.mask(rect=(52 + r, 9, 55 + r, 15)), "rust", width=1, face=4, shade_lower=False)
    tip(p, 55 + r, 11, 57 + r, 13, g, f)
    flash(p, 58 + r, 12, g, f, 4)
    return p


def heavy_laser(f):
    """A heavy gunmetal block with deep cooling fins and a thick banded barrel."""
    p = Pix(*SMALL); r = recoil(f); g = "glow_green"
    bracket(p)
    housing(p, 10, 1, 36, 22, "gunmetal", seams=(30,))
    for x in range(13, 28, 3):
        p.slot(x, 4, x + 1, 19)
    charge_bar(p, 31, 4, 2, g, f)
    status(p, 32, 18, g, f)
    hose(p, [(14, 0), (26, 1), (36, 0)])
    barrel(p, 36 + r, 54 + r, 12, 9, "metal", rings=(40 + r, 46 + r, 52 + r))
    p.engrave([(38 + r, 9), (52 + r, 9)], highlight=False)
    p.bevel(p.mask(polygon=[(54 + r, 6), (58 + r, 8), (58 + r, 16), (54 + r, 18)]), "gunmetal", width=1, face=4, shade_lower=False)
    tip(p, 58 + r, 10, 60 + r, 14, g, f)
    flash(p, 61 + r, 12, g, f, 5)
    return p


def missile_launcher(f):
    """A launch pod: the missile slides out as it charges and is gone when it fires."""
    p = Pix(*SMALL); g = "glow"
    bracket(p)
    out = {0: 0, 1: 5, 2: 9, 3: 13, 4: -99, 5: -99}[f]
    if out > -99:
        x = 22 + out
        p.tube(p.mask(rect=(x, 8, x + 20, 15)), "white", "x", bands=(5, 5, 4, 3, 2))
        p.paint(p.mask(rect=(x + 4, 8, x + 6, 15)), "red")
        p.bevel(p.mask(polygon=[(x + 20, 8), (x + 26, 11), (x + 26, 12), (x + 20, 15)]), "red", width=1, face=4, shade_lower=False)
        p.bevel(p.mask(polygon=[(x, 6), (x + 4, 8), (x, 8)]), "red", width=1, face=4, shade_lower=False)
        p.bevel(p.mask(polygon=[(x, 17), (x + 4, 15), (x, 15)]), "red", width=1, face=4, shade_lower=False)
    housing(p, 10, 1, 36, 22, "gunmetal", seams=(24,))
    p.paint(p.mask(rect=(12, 2, 22, 3)), "yellow"); p.paint(p.mask(rect=(12, 20, 22, 21)), "yellow")
    for x in range(12, 22, 4):
        p.mat[2:4, x:x + 2] = "dark"; p.mat[20:22, x:x + 2] = "dark"
    p.bevel(p.mask(rect=(30, 5, 40, 18)), "metal", width=1, face=3, shade_lower=False)
    p.bevel(p.mask(rect=(33, 8, 40, 15)), "dark", width=1, face=1, shade_lower=False)
    charge_bar(p, 13, 10, 4, g, f)
    status(p, 26, 6, g, f)
    hose(p, [(14, 23), (26, 22), (34, 23)])
    if f == 4:
        p.glow(p.mask(ellipse=(38, 4, 58, 19)), "glow", 2)
        p.glow(p.mask(ellipse=(40, 7, 52, 16)), "glow", 4)
        p.glow(p.mask(ellipse=(41, 9, 47, 14)), "glow", 5)
    if f == 5:
        p.glow(p.mask(ellipse=(39, 8, 46, 15)), "glow", 1)
    return p


def beam(f, heavy):
    """A capacitor bank, a focusing barrel and a crystal lens that heats up."""
    p = Pix(*SMALL); g = "glow_yellow" if heavy else "glow_red"
    bracket(p)
    mat = "metal" if heavy else "white"
    housing(p, 10, 1 if heavy else 3, 30, 22 if heavy else 20, mat, seams=(20,))
    for k in range(3):                                         # capacitor cells
        y = (4 if heavy else 5) + k * 6
        p.tube(p.mask(rect=(12, y, 18, y + 3)), "trim_blue" if not heavy else "gold", "x", bands=(5, 4, 3, 2))
    charge_bar(p, 22, 6, 4, g, f)
    status(p, 26, 17, g, f)
    hose(p, [(14, 23), (24, 22), (32, 21)])
    barrel(p, 30, 44, 12, 7, "gunmetal", rings=(34, 39))
    p.bevel(p.mask(polygon=[(44, 5), (50, 8), (50, 16), (44, 19)]), "gunmetal", width=1, face=4, shade_lower=False)
    for y in (7, 17):
        p.bevel(p.mask(rect=(44, y - 1, 48, y)), "silver", width=1, face=4, shade_lower=False)
    lens = p.mask(ellipse=(49, 8, 56, 16))
    if f == 0:
        p.dome(lens, "glass")
    else:
        p.glow(lens, g, {1: 1, 2: 2, 3: 4, 4: 5, 5: 4}[f])
        if f >= 3:
            p.glow(p.mask(rect=(51, 10, 52, 11)), g, 5)
    if f in (4, 5):
        p.glow(p.mask(rect=(56, 10, 63, 13)), g, 5 if f == 4 else 3)
        p.glow(p.mask(rect=(56, 11, 63, 12)), "glow_yellow", 5)
    return p


def ivan_cannon(f):
    """Ivan's overcharged cannon: a big breech, a long barrel with gold coils that glow as it charges."""
    p = Pix(*BIG); r = recoil(f) * 2; g = "glow_yellow"
    bracket(p, big=True)
    housing(p, 10 + r, 2, 40 + r, 29, "gunmetal", seams=(20 + r, 32 + r))
    vents(p, 22 + r, 30 + r, 6, 4, 4)
    charge_bar(p, 22 + r, 23, 5, g, f)
    status(p, 34 + r, 6, g, f)
    hose(p, [(12, 31), (26, 30), (40, 31)])
    hose(p, [(12, 0), (26, 1), (40, 0)])
    barrel(p, 40 + r, 82 + r, 16, 11, "metal", rings=(44 + r,))
    for x in (48, 58, 68):
        p.tube(p.mask(rect=(x + r, 9, x + 4 + r, 23)), "gold", "x", bands=(5, 4, 4, 3, 2))
        if f >= 1:
            p.glow(p.mask(rect=(x + 1 + r, 14, x + 3 + r, 18)), g, min(5, 1 + f))
    p.bevel(p.mask(polygon=[(82 + r, 9), (88 + r, 11), (88 + r, 21), (82 + r, 23)]), "gunmetal", width=2, face=4, shade_lower=False)
    tip(p, 88 + r, 13, 90 + r, 19, g, f)
    flash(p, 91 + r, 16, g, f, 6)
    return p


def twin_missile(f):
    """Two launch tubes; the top missile loads first, then the bottom."""
    p = Pix(*SMALL)
    bracket(p)
    loaded = {0: (0, 0), 1: (7, 0), 2: (12, 5), 3: (12, 12), 4: (-99, -99), 5: (-99, -99)}[f]
    for y, out in ((7, loaded[0]), (16, loaded[1])):
        if out > 0:
            x = 22 + out
            p.tube(p.mask(rect=(x, y - 2, x + 16, y + 2)), "white", "x", bands=(5, 4, 3, 2, 1))
            p.paint(p.mask(rect=(x + 3, y - 2, x + 4, y + 2)), "red")
            p.bevel(p.mask(polygon=[(x + 16, y - 2), (x + 21, y), (x + 16, y + 2)]), "red", width=1, face=4, shade_lower=False)
    housing(p, 10, 0, 32, 23, "gunmetal", seams=(22,))
    p.paint(p.mask(rect=(12, 11, 20, 12)), "red")
    charge_bar(p, 12, 4, 4, "glow", f)
    charge_bar(p, 12, 18, 4, "glow", max(0, f - 1) if f < 4 else f)
    for y in (7, 16):
        p.bevel(p.mask(rect=(28, y - 4, 38, y + 3)), "metal", width=1, face=3, shade_lower=False)
        p.bevel(p.mask(rect=(31, y - 2, 38, y + 1)), "dark", width=1, face=1, shade_lower=False)
    status(p, 24, 11, "glow", f)
    if f == 4:
        for y in (7, 16):
            p.glow(p.mask(ellipse=(37, y - 5, 52, y + 4)), "glow", 3)
            p.glow(p.mask(ellipse=(38, y - 2, 45, y + 1)), "glow", 5)
    return p


def ion_blast(f):
    """A white housing with a blue stripe and a copper coil round the barrel that lights blue."""
    p = Pix(*SMALL); r = recoil(f); g = "glow_blue"
    bracket(p)
    housing(p, 10, 3, 28, 20, "white", seams=(22,))
    p.paint(p.mask(rect=(12, 3, 15, 20)), "trim_blue")
    charge_bar(p, 17, 15, 3, g, f)
    status(p, 24, 6, g, f)
    hose(p, [(14, 21), (24, 22), (30, 21)], "pipe")
    barrel(p, 28 + r, 50 + r, 12, 7, "gunmetal")
    for x in range(31, 47, 3):
        if f == 0:
            p.tube(p.mask(rect=(x + r, 6, x + 1 + r, 17)), "bronze", "x", bands=(5, 3))
        else:
            p.glow(p.mask(rect=(x + r, 6, x + 1 + r, 17)), g, {1: 1, 2: 2, 3: 4, 4: 5, 5: 3}[f])
    p.bevel(p.mask(ellipse=(49 + r, 6, 57 + r, 17)), "metal", width=1, face=4, shade_lower=False)
    tip(p, 52 + r, 10, 54 + r, 13, g, f)
    flash(p, 57 + r, 12, g, f, 4)
    return p


def toxin_dart(f):
    """A green gas canister with a gauge, feeding a long needle barrel."""
    p = Pix(*SMALL); r = recoil(f); g = "glow_green"
    bracket(p)
    p.tube(p.mask(rect=(11, 1, 27, 22)), "green", "y", bands=(2, 3, 4, 5, 5, 4, 3, 2))
    for y in (4, 19):
        p.paint(p.mask(rect=(11, y, 27, y + 1)), "yellow")
        for x in range(12, 27, 4):
            p.mat[y:y + 2, x:x + 2] = "dark"
    p.bevel(p.mask(ellipse=(15, 8, 23, 15)), "silver", width=1, face=4, shade_lower=False)   # the gauge
    p.engrave([(19, 11), (21, 9)], highlight=False)
    hose(p, [(26, 6), (30, 8), (32, 11)], "green")
    p.bevel(p.mask(rect=(27 + r, 8, 33 + r, 15)), "gunmetal", width=1, face=4, shade_lower=False)
    barrel(p, 33 + r, 52 + r, 12, 4, "metal", rings=(38 + r, 46 + r))
    if f >= 1:
        p.glow(p.mask(rect=(35 + r, 11, 35 + min(16, f * 5) + r, 12)), g, min(5, 1 + f))
    p.bevel(p.mask(polygon=[(52 + r, 10), (59 + r, 12), (52 + r, 13)]), "silver", width=1, face=4, shade_lower=False)
    status(p, 29 + r, 10, g, f)
    if f == 4:
        p.glow(p.mask(ellipse=(57 + r, 7, 63, 17)), g, 2)
        p.glow(p.mask(ellipse=(59 + r, 10, 63, 14)), g, 4)
    return p


def fire_beam(f):
    """A russet housing with deep cooling fins, a heat lens and a scorched muzzle."""
    p = Pix(*SMALL); g = "glow"
    bracket(p)
    housing(p, 10, 2, 30, 21, "russet", rivets=True)
    for x in (13, 17, 21, 25):
        p.bevel(p.mask(rect=(x, 0, x + 1, 23)), "gunmetal", width=1, face=3, shade_lower=False)
    charge_bar(p, 13, 10, 7, g, f)
    hose(p, [(30, 3), (34, 4), (38, 6)], "pipe")
    barrel(p, 30, 44, 12, 7, "gunmetal", rings=(35, 40))
    p.bevel(p.mask(polygon=[(44, 5), (50, 8), (50, 16), (44, 19)]), "russet", width=1, face=4, shade_lower=False)
    p.shade(p.mask(rect=(46, 8, 49, 16)), -1)
    lens = p.mask(ellipse=(49, 8, 56, 16))
    if f == 0:
        p.dome(lens, "glass")
    else:
        p.glow(lens, g, {1: 1, 2: 2, 3: 4, 4: 5, 5: 4}[f])
    status(p, 26, 17, g, f)
    if f in (4, 5):
        p.glow(p.mask(rect=(56, 9, 63, 14)), g, 4 if f == 4 else 2)
        p.glow(p.mask(rect=(56, 11, 63, 12)), "glow_yellow", 5)
    return p


def flak_cannon(f):
    """An olive autoloader with a shell feed and a short, wide flared barrel."""
    p = Pix(*SMALL); r = recoil(f); g = "glow"
    bracket(p)
    housing(p, 10, 1, 32, 22, "olive", seams=(24,))
    for y in (4, 8, 12, 16):                                   # shells in the feed
        p.tube(p.mask(rect=(13, y, 21, y + 2)), "bronze", "x", bands=(5, 4, 3))
        p.bevel(p.mask(rect=(21, y, 22, y + 2)), "red", width=1, face=4, shade_lower=False)
    status(p, 27, 5, g, f)
    charge_bar(p, 25, 17, 3, g, f)
    hose(p, [(14, 23), (24, 22), (32, 23)], "strap")
    barrel(p, 32 + r, 46 + r, 12, 11, "gunmetal", rings=(36 + r, 41 + r))
    p.bevel(p.mask(polygon=[(46 + r, 6), (53 + r, 2), (53 + r, 21), (46 + r, 17)]), "gunmetal", width=2, face=4, shade_lower=False)
    tip(p, 51 + r, 5, 52 + r, 18, g, f)
    if f == 4:
        for dy in (-6, 0, 6):
            p.glow(p.mask(ellipse=(54 + r, 8 + dy, 62 + r, 15 + dy)), g, 4)
    elif f == 5:
        p.glow(p.mask(ellipse=(54 + r, 9, 58 + r, 14)), g, 2)
    return p


def chain_laser(f):
    """Three barrels in a spinning ring: each frame turns them a step."""
    p = Pix(*SMALL); g = "glow_teal"
    bracket(p)
    housing(p, 10, 2, 30, 21, "metal", seams=(20,))
    p.paint(p.mask(rect=(24, 2, 27, 21)), "teal")
    p.bevel(p.mask(ellipse=(13, 7, 19, 16)), "gunmetal", width=1, face=3, shade_lower=False)   # the motor
    p.glow(p.mask(rect=(15, 11, 16, 12)), g, 1 + min(4, f))
    charge_bar(p, 12, 18, 4, g, f)
    hose(p, [(14, 1), (22, 0), (30, 1)], "pipe")
    turn = f % 3
    for k in range(3):
        y = (6, 12, 18)[(k + turn) % 3]
        barrel(p, 30, 52, y, 4, "gunmetal" if k else "metal")
        tip(p, 52, y - 1, 53, y + 1, g, f)
    for x in (36, 46):
        p.bevel(p.mask(rect=(x, 2, x + 2, 21)), "teal", width=1, face=4, shade_lower=False)
    flash(p, 54, 12, g, f, 5)
    return p


GUNS = {
    "burst_laser": burst_laser, "rabble_laser": rabble_laser, "heavy_laser": heavy_laser,
    "missile_launcher": missile_launcher, "cutting_beam": lambda f: beam(f, False), "heavy_beam": lambda f: beam(f, True),
    "ivan_cannon": ivan_cannon, "twin_missile": twin_missile, "ion_blast": ion_blast, "toxin_dart": toxin_dart,
    "fire_beam": fire_beam, "flak_cannon": flak_cannon, "chain_laser": chain_laser,
}


def strip(fn):
    frames = [fn(f).render() for f in range(6)]
    w, h = frames[0].size
    out = Image.new("RGBA", (w * 6, h), (0, 0, 0, 0))
    for i, im in enumerate(frames):
        out.alpha_composite(im, (i * w, 0))
    return out


def missile_shot():
    out = Image.new("RGBA", (48, 8), (0, 0, 0, 0))
    for f in range(3):
        p = Pix(16, 8)
        p.tube(p.mask(rect=(4, 2, 12, 5)), "white", "x", bands=(5, 4, 3, 2))
        p.bevel(p.mask(polygon=[(12, 2), (15, 3), (15, 4), (12, 5)]), "red", width=1, face=4, shade_lower=False)
        p.paint(p.mask(rect=(5, 1, 6, 6)), "red")
        p.glow(p.mask(ellipse=(0, 2 - (f == 1), 4, 5 + (f == 1))), "glow", 3)
        p.glow(p.mask(rect=(2 + f % 2, 3, 3 + f % 2, 4)), "glow", 5)
        out.alpha_composite(p.render(), (f * 16, 0))
    return out


def store_picture(fn):
    """The ready frame, doubled again, on a 48 x 48 tile, tilted up a little like an item icon."""
    im = fn(3).render()
    big = im.resize((im.width, im.height), Image.NEAREST)
    big = big.rotate(18, resample=Image.NEAREST, expand=True)
    bb = big.getbbox()
    big = big.crop(bb)
    s = min(46 / big.width, 46 / big.height, 1.0)
    if s < 1.0:
        big = big.resize((max(1, int(big.width * s)), max(1, int(big.height * s))), Image.NEAREST)
    out = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    out.alpha_composite(big, ((48 - big.width) // 2, (48 - big.height) // 2))
    return out


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    for d in ("weapons", "shots", "store"):
        (root / "art/ships" / d).mkdir(parents=True, exist_ok=True)
    for wid, fn in GUNS.items():
        strip(fn).save(root / f"art/ships/weapons/{wid}.png")
        store_picture(fn).save(root / f"art/ships/store/{wid}.png")
    missile_shot().save(root / "art/ships/shots/missile.png")
    print("ok", len(GUNS))
