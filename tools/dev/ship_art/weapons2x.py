"""Weapon art at double resolution (Claude, 21 Nov 2026). Zachary: "art for the different weapons like lasers missles and
beams"; guns attach to the hull's sides, FTL-style, where a ship's mounts are.

art/ships/weapons/<id>.png  six frames side by side, barrel pointing right, the mount at the left middle:
    idle, charging 1, charging 2, ready (glowing), firing 1 (recoil, muzzle flash), firing 2.
    Small guns: 48 x 16 a frame (24 x 8 cell px); big guns (Ivan's cannon): 80 x 24. The mount point is
    (4, 8) small, (6, 12) big.
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

SMALL, BIG = (48, 16), (80, 24)
GLOW = {"burst_laser": "glow_red", "rabble_laser": "glow_green", "heavy_laser": "glow_green", "missile_launcher": "glow",
        "cutting_beam": "glow_red", "heavy_beam": "glow_yellow", "ivan_cannon": "glow_yellow"}


def tip(p, x0, y0, x1, y1, g, frame):
    """The emitter: dark when idle, warming while charging, bright when ready and firing."""
    tone = {0: None, 1: 1, 2: 2, 3: 4, 4: 5, 5: 3}[frame]
    if tone is None:
        p.bevel(p.mask(rect=(x0, y0, x1, y1)), "dark", width=1, face=2, shade_lower=False)
    else:
        p.glow(p.mask(rect=(x0, y0, x1, y1)), g, tone)


def flash(p, x, y, g, frame, size=4):
    if frame == 4:
        p.glow(p.mask(ellipse=(x, y - size, x + size * 2 + 2, y + size)), g, 3)
        p.glow(p.mask(ellipse=(x + 1, y - size // 2, x + size + 2, y + size // 2)), g, 5)
    elif frame == 5:
        p.glow(p.mask(ellipse=(x, y - size // 2, x + size, y + size // 2)), g, 2)


def recoil(frame):
    return {4: -2, 5: -1}.get(frame, 0)


def bracket(p, mat="gunmetal"):
    """The clamp that holds a small gun to the hull, at the mount (left middle)."""
    p.bevel(p.mask(rect=(0, 3, 9, 12)), mat, width=1, face=3, shade_lower=False)
    p.rivet(2, 5); p.rivet(2, 10)


def burst_laser(f):
    p = Pix(*SMALL); r = recoil(f); g = GLOW["burst_laser"]
    bracket(p)
    p.bevel(p.mask(rect=(6 + r, 2, 22 + r, 13)), "white", width=1, face=4, shade_lower=False)
    p.paint(p.mask(rect=(10 + r, 2, 12 + r, 13)), "orange")
    for y in (4, 10):
        p.tube(p.mask(rect=(22 + r, y - 1, 34 + r, y + 1)), "metal", "x", bands=(5, 3, 2))
        tip(p, 34 + r, y - 1, 36 + r, y + 1, g, f)
        flash(p, 37 + r, y, g, f, 3)
    return p


def rabble_laser(f):
    p = Pix(*SMALL); r = recoil(f); g = GLOW["rabble_laser"]
    bracket(p, "rust")
    p.bevel(p.mask(rect=(6 + r, 3, 20 + r, 12)), "rust", width=1, face=4, shade_lower=False)
    p.rivet(9 + r, 5); p.rivet(17 + r, 10)
    p.tube(p.mask(rect=(20 + r, 6, 33 + r, 9)), "gunmetal", "x", bands=(4, 3, 2, 1))
    p.bevel(p.mask(rect=(24 + r, 5, 26 + r, 10)), "rust", width=1, face=3, shade_lower=False)
    tip(p, 33 + r, 6, 35 + r, 9, g, f)
    flash(p, 36 + r, 7, g, f, 3)
    return p


def heavy_laser(f):
    p = Pix(*SMALL); r = recoil(f); g = GLOW["heavy_laser"]
    bracket(p)
    p.bevel(p.mask(rect=(6 + r, 1, 24 + r, 14)), "gunmetal", width=2, face=4, shade_lower=False)
    for x in (10, 14, 18):
        p.slot(x + r, 4, x + 1 + r, 11)
    p.tube(p.mask(rect=(24 + r, 4, 38 + r, 11)), "metal", "x", bands=(5, 4, 3, 3, 2, 1))
    p.engrave([(30 + r, 4), (30 + r, 11)])
    tip(p, 38 + r, 5, 40 + r, 10, g, f)
    flash(p, 41 + r, 7, g, f, 4)
    return p


def missile_launcher(f):
    """A pod with a missile: it slides out as the launcher charges, and is gone when it fires."""
    p = Pix(*SMALL); g = GLOW["missile_launcher"]
    bracket(p)
    out = {0: 0, 1: 3, 2: 6, 3: 9, 4: -99, 5: -99}[f]
    if out > -99:
        x = 14 + out
        p.tube(p.mask(rect=(x, 5, x + 14, 10)), "white", "x", bands=(5, 4, 3, 2))
        p.bevel(p.mask(polygon=[(x + 14, 5), (x + 19, 7), (x + 19, 8), (x + 14, 10)]), "red", width=1, face=4, shade_lower=False)
        p.paint(p.mask(rect=(x + 3, 5, x + 4, 10)), "red")
    p.bevel(p.mask(rect=(6, 1, 26, 14)), "gunmetal", width=2, face=4, shade_lower=False)
    p.bevel(p.mask(rect=(20, 3, 28, 12)), "metal", width=1, face=3, shade_lower=False)
    p.slot(22, 6, 27, 9)
    p.paint(p.mask(rect=(8, 2, 18, 3)), "yellow")
    p.paint(p.mask(rect=(8, 12, 18, 13)), "yellow")
    if f == 3:
        p.glow(p.mask(rect=(9, 6, 11, 9)), g, 4)
    if f == 4:
        p.glow(p.mask(ellipse=(26, 3, 40, 12)), "glow", 3)
        p.glow(p.mask(ellipse=(27, 5, 34, 10)), "glow", 5)
    if f == 5:
        p.glow(p.mask(ellipse=(27, 5, 34, 10)), "glow", 1)
    return p


def beam(f, heavy):
    p = Pix(*SMALL); g = GLOW["heavy_beam" if heavy else "cutting_beam"]
    bracket(p)
    h0, h1 = (1, 14) if heavy else (2, 13)
    p.bevel(p.mask(rect=(6, h0, 22, h1)), "metal" if heavy else "white", width=1, face=4, shade_lower=False)
    for y in range(h0 + 2, h1 - 1, 3):
        p.engrave([(8, y), (20, y)], highlight=False)
    # a focusing barrel ending in a crystal lens
    p.tube(p.mask(rect=(22, 5, 32, 10)), "gunmetal", "x", bands=(4, 3, 3, 2, 1))
    p.bevel(p.mask(polygon=[(32, 3), (36, 5), (36, 10), (32, 12)]), "gunmetal", width=1, face=4, shade_lower=False)
    lens = p.mask(ellipse=(35, 4, 40, 11))
    if f == 0:
        p.dome(lens, "glass")
    else:
        p.glow(lens, g, {1: 1, 2: 2, 3: 4, 4: 5, 5: 4}[f])
    if f in (4, 5):
        p.glow(p.mask(rect=(40, 6, 47, 9)), g, 5 if f == 4 else 3)
    return p


def ivan_cannon(f):
    p = Pix(*BIG); r = recoil(f) * 2; g = GLOW["ivan_cannon"]
    p.bevel(p.mask(rect=(0, 4, 14, 19)), "gunmetal", width=2, face=3, shade_lower=False)
    p.rivet(3, 7); p.rivet(3, 16)
    p.bevel(p.mask(rect=(10 + r, 2, 30 + r, 21)), "gunmetal", width=2, face=4, shade_lower=False)
    p.tube(p.mask(rect=(30 + r, 7, 62 + r, 16)), "metal", "x", bands=(5, 5, 4, 3, 3, 2, 2, 1))
    for x in (36, 46, 56):
        p.tube(p.mask(rect=(x + r, 5, x + 3 + r, 18)), "gold", "x", bands=(5, 4, 3, 2))
        if f >= 1:
            p.glow(p.mask(rect=(x + 1 + r, 10, x + 2 + r, 13)), g, min(5, 1 + f))
    p.tube(p.mask(rect=(62 + r, 6, 66 + r, 17)), "gunmetal", "x", bands=(4, 3, 2, 1))
    tip(p, 66 + r, 9, 68 + r, 14, g, f)
    flash(p, 69 + r, 11, g, f, 5)
    return p


GUNS = {
    "burst_laser": burst_laser, "rabble_laser": rabble_laser, "heavy_laser": heavy_laser,
    "missile_launcher": missile_launcher, "cutting_beam": lambda f: beam(f, False), "heavy_beam": lambda f: beam(f, True),
    "ivan_cannon": ivan_cannon,
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
