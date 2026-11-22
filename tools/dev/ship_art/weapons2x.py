"""Weapon art at double resolution (Claude, 21 Nov 2026). Zachary: "art for the different weapons like lasers missles and
beams"; guns attach to the hull's sides, FTL-style, where a ship's mounts are.

art/ships/weapons/<id>.png  six frames side by side, barrel pointing right, the mount at the left middle:
    idle, charging 1, charging 2, ready (glowing), firing 1 (recoil, muzzle flash), firing 2.
    Small guns: 64 x 24 a frame (32 x 12 cell px); big guns (Ivan's cannon): 96 x 32. The mount point is
    (6, 12) small, (8, 16) big. Drawn FTL-style (Zachary: "doesnt read FTL enough"): chunky dark-grey
    shapes with charge lights set into the body.
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


# ---------------------------------------------------------------- parts, FTL-style
# Zachary: "doesnt read FTL enough". FTL's guns are chunky dark-grey shapes with a thick dark outline and few small
# details; what reads is the silhouette and the coloured lights set into the body, which fill up as the gun charges.
# These are our own shapes in that style.

from pixkit import RAMPS
RAMPS.setdefault("steel", ["#26262b", "#36363c", "#48484f", "#5c5c63", "#74747b", "#8e8e94"])
RAMPS.setdefault("steel_dark", ["#1c1c21", "#26262b", "#323238", "#3e3e45", "#4c4c53", "#5c5c63"])

LIT = {0: 0.0, 1: 0.34, 2: 0.67, 3: 1.0, 4: 1.0, 5: 0.0}


def recoil(frame):
    return {4: -3, 5: -1}.get(frame, 0)


def body(p, pts_or_rect, mat="steel", face=4):
    if isinstance(pts_or_rect, tuple):
        m = p.mask(rect=pts_or_rect)
    else:
        m = p.mask(polygon=pts_or_rect)
    p.bevel(m, mat, width=1, face=face, edge_light=5, edge_dark=1, shade_lower=True)
    return m


def lights(p, x0, y0, x1, y1, n, g, f, vertical=False):
    """A dark inset window holding n lights: dim until the charge reaches them, then bright."""
    p.bevel(p.mask(rect=(x0, y0, x1, y1)), "dark", width=1, face=0, edge_light=1, edge_dark=0, shade_lower=False)
    lit = round(LIT[f] * n)
    span = (y1 - y0 - 1) if vertical else (x1 - x0 - 1)
    step = span / n
    for k in range(n):
        a = int((y0 + 1 if vertical else x0 + 1) + k * step)
        b = int((y0 + 1 if vertical else x0 + 1) + (k + 1) * step) - 2
        if vertical:
            r = (x0 + 1, a, x1 - 1, max(a, b))
        else:
            r = (a, y0 + 1, max(a, b), y1 - 1)
        on = (n - 1 - k) < lit if vertical else k < lit
        p.glow(p.mask(rect=r), g, 2 if on else 0)
        if on:
            p.glow(p.mask(rect=(r[0], r[1], r[0], r[1])), g, 4)        # a highlight on each lit light


def muzzle(p, x, y, g, f, size=5):
    if f == 4:
        p.glow(p.mask(ellipse=(x, y - size, x + size * 2 + 2, y + size)), g, 3)
        p.glow(p.mask(ellipse=(x + 2, y - size // 2, x + size + 2, y + size // 2)), g, 5)
    elif f == 5:
        p.glow(p.mask(ellipse=(x, y - 2, x + 4, y + 2)), g, 2)


def mount(p, h=24):
    """The block that fixes the gun to the hull, at the left middle."""
    m = h // 2
    body(p, (0, m - 7, 8, m + 6), "steel_dark", face=4)
    p.set_tone(p.mask(rect=(2, m - 5, 2, m + 4)), 5)


# ---------------------------------------------------------------- the guns (64 x 24 a frame; the mount at (6, 12))

def burst_laser(f):
    p = Pix(*SMALL); r = recoil(f); g = "glow_red"
    mount(p)
    for y in (7, 15):                                          # two short barrels
        body(p, (36 + r, y - 2, 54 + r, y + 2), "steel_dark")
        body(p, (52 + r, y - 3, 56 + r, y + 3))
    body(p, [(8, 4), (34, 4), (40, 8), (40, 19), (8, 19)])
    lights(p, 13, 9, 33, 13, 3, g, f)
    muzzle(p, 57 + r, 7, g, f, 3); muzzle(p, 57 + r, 15, g, f, 3)
    return p


def rabble_laser(f):
    p = Pix(*SMALL); r = recoil(f); g = "glow_green"
    mount(p)
    body(p, (34 + r, 9, 54 + r, 14), "steel_dark")
    body(p, (50 + r, 8, 55 + r, 15))
    body(p, [(8, 6), (30, 6), (36, 9), (36, 16), (26, 19), (8, 19)])
    p.paint(p.mask(rect=(10, 15, 18, 18)), "rust")              # a rusty patch
    lights(p, 14, 9, 30, 12, 3, g, f)
    muzzle(p, 56 + r, 11, g, f, 4)
    return p


def heavy_laser(f):
    p = Pix(*SMALL); r = recoil(f); g = "glow_green"
    mount(p)
    body(p, (36 + r, 7, 56 + r, 16), "steel_dark")
    body(p, (54 + r, 5, 59 + r, 18))
    body(p, [(8, 2), (32, 2), (40, 6), (40, 18), (32, 22), (8, 22)])
    lights(p, 13, 7, 33, 11, 4, g, f)
    lights(p, 13, 14, 33, 18, 4, g, f)
    muzzle(p, 60 + r, 11, g, f, 5)
    return p


def missile_launcher(f):
    p = Pix(*SMALL); g = "glow_green"
    mount(p)
    out = {0: 0, 1: 4, 2: 8, 3: 11, 4: -99, 5: -99}[f]
    if out > -99:                                              # the missile sliding out of the tube
        x = 34 + out
        body(p, (x, 9, x + 12, 14), "white")
        body(p, [(x + 12, 9), (x + 17, 11), (x + 17, 12), (x + 12, 14)], "red")
    body(p, [(8, 3), (40, 3), (44, 7), (44, 17), (40, 21), (8, 21)])
    body(p, (38, 7, 46, 16), "steel_dark")                     # the tube mouth
    p.bevel(p.mask(rect=(41, 9, 46, 14)), "dark", width=1, face=0, edge_light=1, edge_dark=0, shade_lower=False)
    lights(p, 12, 7, 18, 17, 3, g, f, vertical=True)
    lights(p, 22, 7, 34, 11, 2, g, f)
    if f == 4:
        p.glow(p.mask(ellipse=(44, 4, 62, 19)), "glow", 3)
        p.glow(p.mask(ellipse=(46, 8, 54, 15)), "glow", 5)
    return p


def beam(f, heavy):
    p = Pix(*SMALL); g = "glow_yellow" if heavy else "glow_red"
    mount(p)
    # two prongs reaching forward, the beam forms between them
    reach = 58 if heavy else 52
    for y in ((5, 8) if heavy else (6, 8)), ((15, 18) if heavy else (15, 17)):
        body(p, (34, y[0], reach, y[1]), "steel_dark")
    body(p, [(8, 3 if heavy else 4), (34, 3 if heavy else 4), (38, 7), (38, 16), (34, 20 if heavy else 19), (8, 20 if heavy else 19)])
    lights(p, 12, 9, 34, 13, 4 if heavy else 3, g, f)
    if f >= 1:                                                 # the beam forming between the prongs
        p.glow(p.mask(rect=(38, 11, 38 + int(LIT[f] * (reach - 40)) if f < 4 else reach, 12)), g, 2 + min(3, f))
    if f in (4, 5):
        p.glow(p.mask(rect=(38, 10, 63, 13)), g, 4 if f == 4 else 2)
        p.glow(p.mask(rect=(38, 11, 63, 12)), "glow_yellow", 5)
    return p


def ivan_cannon(f):
    p = Pix(*BIG); r = recoil(f) * 2; g = "glow_yellow"
    mount(p, 32)
    body(p, (46 + r, 10, 84 + r, 21), "steel_dark")
    for x in (52, 62, 72):                                     # gold coils, lit as it charges
        body(p, (x + r, 7, x + 4 + r, 24), "gold")
        if f >= 1:
            p.glow(p.mask(rect=(x + 1 + r, 13, x + 3 + r, 18)), g, min(5, 1 + f))
    body(p, (82 + r, 8, 89 + r, 23))
    body(p, [(8, 3), (40, 3), (48, 9), (48, 22), (40, 28), (8, 28)])
    lights(p, 13, 8, 39, 13, 5, g, f)
    lights(p, 13, 18, 39, 23, 5, g, f)
    muzzle(p, 90 + r, 15, g, f, 6)
    return p


def twin_missile(f):
    p = Pix(*SMALL); g = "glow_green"
    mount(p)
    loaded = {0: (0, 0), 1: (8, 0), 2: (11, 5), 3: (11, 11), 4: (-99, -99), 5: (-99, -99)}[f]
    for y, out in ((7, loaded[0]), (16, loaded[1])):
        if out > 0:
            x = 32 + out
            body(p, (x, y - 2, x + 12, y + 2), "white")
            body(p, [(x + 12, y - 2), (x + 16, y), (x + 12, y + 2)], "red")
    body(p, [(8, 1), (38, 1), (42, 5), (42, 18), (38, 22), (8, 22)])
    for y in (7, 16):
        body(p, (36, y - 4, 44, y + 3), "steel_dark")
        p.bevel(p.mask(rect=(40, y - 2, 44, y + 1)), "dark", width=1, face=0, edge_light=1, edge_dark=0, shade_lower=False)
    lights(p, 12, 5, 32, 9, 3, g, min(f, 3) if f < 4 else 4)
    lights(p, 12, 14, 32, 18, 3, g, max(0, f - 2) * 3 if 0 < f < 4 else (4 if f == 4 else 0))
    if f == 4:
        for y in (7, 16):
            p.glow(p.mask(ellipse=(44, y - 5, 58, y + 4)), "glow", 3)
    return p


def ion_blast(f):
    p = Pix(*SMALL); r = recoil(f); g = "glow_teal"
    mount(p)
    body(p, (34 + r, 8, 46 + r, 15), "steel_dark")
    # a round coil housing at the front, its rings lit cyan
    body(p, [(44 + r, 4), (52 + r, 4), (56 + r, 8), (56 + r, 15), (52 + r, 19), (44 + r, 19)])
    for x in (46, 49, 52):
        p.glow(p.mask(rect=(x + r, 6, x + r, 17)), g, 4 if LIT[f] * 3 > (x - 46) / 3 else 0)
    body(p, [(8, 4), (32, 4), (36, 8), (36, 16), (32, 20), (8, 20)])
    lights(p, 13, 10, 31, 14, 3, g, f)
    muzzle(p, 57 + r, 11, "glow_blue", f, 4)
    return p


def toxin_dart(f):
    p = Pix(*SMALL); r = recoil(f); g = "glow_green"
    mount(p)
    body(p, (32 + r, 10, 54 + r, 13), "steel_dark")             # the needle
    body(p, [(54 + r, 10), (60 + r, 11), (60 + r, 12), (54 + r, 13)], "silver")
    body(p, [(8, 5), (30, 5), (34, 9), (34, 15), (30, 19), (8, 19)])
    # the gas tank window, filling green
    lights(p, 12, 8, 28, 16, 4, g, f)
    muzzle(p, 61 + r, 11, g, f, 3)
    return p


def fire_beam(f):
    p = Pix(*SMALL); g = "glow"
    mount(p)
    for y in ((5, 8), (15, 18)):
        body(p, (34, y[0], 54, y[1]), "steel_dark")
        body(p, (50, y[0] - 1, 55, y[1] + 1), "russet")
    body(p, [(8, 3), (34, 3), (38, 7), (38, 16), (34, 20), (8, 20)])
    lights(p, 12, 7, 34, 11, 4, g, f)
    lights(p, 12, 13, 34, 17, 4, "glow_red", f)
    if f >= 1:
        p.glow(p.mask(rect=(38, 11, 38 + int(LIT[f] * 14) if f < 4 else 63, 12)), g, 2 + min(3, f))
    if f in (4, 5):
        p.glow(p.mask(rect=(38, 9, 63, 14)), g, 4 if f == 4 else 2)
        p.glow(p.mask(rect=(38, 11, 63, 12)), "glow_yellow", 5)
    return p


def flak_cannon(f):
    p = Pix(*SMALL); r = recoil(f); g = "glow_red"
    mount(p)
    # a short barrel that flares into a wide mouth
    body(p, (36 + r, 7, 48 + r, 16), "steel_dark")
    body(p, [(48 + r, 7), (56 + r, 2), (56 + r, 21), (48 + r, 16)])
    p.bevel(p.mask(rect=(54 + r, 5, 56 + r, 18)), "dark", width=1, face=0, edge_light=1, edge_dark=0, shade_lower=False)
    # an angled body with a drum on top
    body(p, [(8, 6), (30, 6), (38, 10), (38, 17), (30, 21), (8, 21)])
    body(p, [(14, 1), (28, 1), (30, 6), (12, 6)], "steel_dark")
    lights(p, 12, 11, 32, 15, 3, g, f)
    if f == 4:
        for dy in (-6, 0, 6):
            p.glow(p.mask(ellipse=(57 + r, 8 + dy, 63, 15 + dy)), "glow", 4)
    return p


def chain_laser(f):
    p = Pix(*SMALL); g = "glow_teal"
    mount(p)
    turn = f % 3
    for k in range(3):                                         # three barrels in a ring, turning
        y = (5, 11, 17)[(k + turn) % 3]
        body(p, (34, y - 2, 54, y + 1), "steel_dark" if k else "steel")
        body(p, (52, y - 2, 55, y + 1))
    body(p, (40, 2, 43, 21), "steel_dark")
    body(p, [(8, 3), (32, 3), (36, 7), (36, 16), (32, 20), (8, 20)])
    lights(p, 12, 6, 32, 10, 3, g, f)
    lights(p, 12, 13, 32, 17, 3, g, f)
    muzzle(p, 56, 11, g, f, 4)
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
