"""The prologue's pictures, second pass (24 Nov 2026, Zachary: "redraw assets in the game art style with depth and
shading, needs better animation, the drone glyphs should be animated").

Drawn in code to the art style guide and to the look of the game's own illustrated art (the space backdrops and the
title scene): only the master palette, forms built from flat facets lit by real light sources (the starlight through
the hole, the fire on your wreck, the drone's violet glow) and cut into 4-6 tones per material, crisp edges, no
noise, no single-pixel specks. Foreground objects (your ship, the drone) have a dark outline; rock is shaded against
the dark the way the backdrops' asteroids are.

The crash itself plays on a cavern map in the game (tools/crash_site.py; its props and the drone's animation are
drawn by tools/dev/crash_site_art.py). This draws what goes over the picture panels and the screen. art/prologue/:
  glyphs.png            the star-glyphs wheeling round you, 12 frames (640 x 360): each ring turns its own way, each
                        glyph spins and twinkles;  glyph_fold.png: folding into the mark, 8 frames;  glyph_mark.png
  sparks.png            sparks from the torn hull, 6 frames;  blink.png: the red emergency light, 2 frames
  star_front.png, star_back.png    the Wandering Star (the game's starter ship) torn in two for the blind jump
  flame.png             an engine flame, 4 frames;  shield.png: Ivan's shield taking a hit, 6 frames
  streak.png            your ship burning in, 4 frames;  impact.png: the impact flash and dust, 8 frames
  bolt_green.png, bolt_teal.png, jump_streaks.png
and art/portrait_motherdrone.png. Run: python3 tools/dev/prologue_art.py [--preview]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion
from scipy.spatial import Delaunay

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(ROOT, "art", "prologue")
W, H = 640, 360

PAL = {
    "ink": ["4a2a28", "5b332d", "6e4238"],
    "cream": ["6e6178", "9c8a8f", "c9b8a6", "e8d9bd", "fff3d6"],
    "teal": ["263a52", "2f5a6e", "3f7f88", "66a7a0", "9fd1bf"],
    "wood": ["3d2426", "6b3a2c", "9a5b36", "c9844a", "e8b46a"],
    "brass": ["5a3a22", "8f5f24", "c99231", "edc65a", "fff0a0"],
    "copper": ["4c2224", "8a3a2a", "c8602f", "ee8f3e", "ffc070"],
    "leaf": ["1f3a32", "2f6a3a", "4f9a3c", "8cc94a", "d2ea7a"],
    "soil": ["33242a", "5a3a33", "86593f", "b08158", "d8b07c"],
    "rock": ["2f2c3d", "4b4659", "6f6878", "9c94a0", "c9c1c4"],
    "berry": ["4a1c2e", "8a2a3a", "c94a4a", "ee7a62", "ffb39a"],
    "violet": ["2c1f4a", "4f3384", "7d55c0", "b085e6", "e0c6ff"],
    "glow": ["1f2f5a", "2f5cab", "4a9be0", "8fd3ff", "e6fbff"],
    "skin": ["6b3a3a", "a85f4f", "d9926e", "f2c29a", "ffe3c8"],
    "skin2": ["3a2026", "5e3430", "86503c", "a8704f", "c99470"],
}
ALLOWED = {h for r in PAL.values() for h in r}


def C(name, i):
    h = PAL[name][i]
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


OUT = C("ink", 1)


class Canvas:
    def __init__(self, w=W, h=H, fill=None):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)
        if fill is not None:
            self.a[:, :] = fill

    def paint(self, mask, c):
        self.a[mask] = c

    def save(self, path):
        Image.fromarray(self.a, "RGBA").save(path)

    def image(self):
        return Image.fromarray(self.a, "RGBA")


def poly(pts, w=W, h=H):
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=1)
    return np.array(im, bool)


def lines(pts, width, w=W, h=H):
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).line([(float(x), float(y)) for x, y in pts], fill=1, width=width, joint="curve")
    return np.array(im, bool)


def disc(cx, cy, r, w=W, h=H):
    yy, xx = np.mgrid[0:h, 0:w]
    return (xx - cx + .5) ** 2 + (yy - cy + .5) ** 2 <= r * r


def sh(m, dx, dy):
    """m moved by (dx, dy); what falls off is outside."""
    out = np.zeros_like(m)
    h, w = m.shape
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = m[ys, xs]
    return out


def edge(m):
    """The pixels of m with a 4-neighbour outside it (its 1-px rim)."""
    return m & ~binary_erosion(m, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]], border_value=0)


def sh_key(k, dx, dy):
    out = np.full_like(k, -1)
    h, w = k.shape
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = k[ys, xs]
    return out


def despeckle(cv, region, passes=2):
    """Pixels inside region whose colour no 4-neighbour shares take the most common neighbour colour."""
    for _ in range(passes):
        a = cv.a
        key = (a[:, :, 0].astype(np.int64) << 24) | (a[:, :, 1].astype(np.int64) << 16) | (a[:, :, 2].astype(np.int64) << 8) | a[:, :, 3]
        n = [sh_key(key, dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        lonely = region & np.all([k != key for k in n], axis=0)
        ys, xs = np.nonzero(lonely)
        for y, x in zip(ys, xs):
            vals = [int(k[y, x]) for k in n if int(k[y, x]) >= 0]
            if not vals:
                continue
            best = max(set(vals), key=vals.count)
            cv.a[y, x] = [(best >> 24) & 255, (best >> 16) & 255, (best >> 8) & 255, best & 255]


def check(cv, name):
    flat = cv.a.reshape(-1, 4)
    seen = {"%02x%02x%02x" % tuple(int(q) for q in p[:3]) for p in flat[flat[:, 3] > 0]}
    bad = seen - ALLOWED
    assert not bad, (name, "colours off the palette", sorted(bad)[:8])


def star(cv, x, y, big=False, c=None):
    c = c or C("cream", 3)
    if big:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            cv.a[y + dy, x + dx] = c
        cv.a[y, x] = C("cream", 4)
    else:
        cv.a[y:y + 2, x:x + 2] = c


def strip(frames):
    """Frames side by side, one picture."""
    w, h = frames[0].w, frames[0].h
    out = Canvas(w * len(frames), h)
    for i, f in enumerate(frames):
        out.a[:, i * w:(i + 1) * w] = f.a
    return out


# ================================================================ the star-glyphs
GLYPH_COLS = (("brass", 3), ("violet", 4), ("violet", 3), ("brass", 4), ("glow", 3))


def glyph(cv, x, y, kind, r, col, turn):
    c = C(*col)
    w, h = cv.w, cv.h

    def rot(pts):
        return [(x + px * math.cos(turn) - py * math.sin(turn), y + px * math.sin(turn) + py * math.cos(turn)) for px, py in pts]
    if kind == 0:      # a ring with a dot and a tick
        m = disc(x, y, r, w, h) & ~disc(x, y, r - 2, w, h)
        m |= disc(x, y, 2, w, h)
        m |= lines(rot([(0, -r - 3), (0, -r + 1)]), 2, w, h)
    elif kind == 1:    # a triangle
        m = lines(rot([(0, -r), (r * .87, r * .5), (-r * .87, r * .5), (0, -r)]), 2, w, h)
    elif kind == 2:    # a four-point star
        m = poly(rot([(0, -r), (r * .25, -r * .25), (r, 0), (r * .25, r * .25), (0, r), (-r * .25, r * .25), (-r, 0), (-r * .25, -r * .25)]), w, h)
    elif kind == 3:    # an arc with three beads
        pts = [(x + math.cos(turn + math.pi * k / 10) * r, y + math.sin(turn + math.pi * k / 10) * r) for k in range(11)]
        m = lines(pts, 2, w, h)
        for k in (0, 5, 10):
            m |= disc(pts[k][0], pts[k][1], 2, w, h)
    else:              # a diamond inside a diamond
        m = lines(rot([(0, -r), (r, 0), (0, r), (-r, 0), (0, -r)]), 2, w, h)
        m |= poly(rot([(0, -r * .4), (r * .4, 0), (0, r * .4), (-r * .4, 0)]), w, h)
    cv.paint(m, c)


def glyph_layout():
    rnd = random.Random(3)
    out = []
    k = 0
    for ring, n, r0, spin in ((120, 9, 13, .4), (178, 12, 10, -.3), (62, 6, 15, .7)):
        for i in range(n):
            out.append(dict(ring=ring, n=n, a0=2 * math.pi * i / n, r=r0 + rnd.randint(-2, 2), kind=k % 5,
                            col=GLYPH_COLS[k % 5], spin=spin * rnd.choice((1, -1)), phase=rnd.random(), dir=1 if spin > 0 else -1))
            k += 1
    return out


def glyph_frames():
    """12 frames: each ring of glyphs turns one step (a full step per loop, so it loops cleanly), each glyph spins
    and twinkles."""
    frames = []
    G = glyph_layout()
    for f in range(12):
        cv = Canvas()
        t = f / 12
        for g in G:
            a = g["a0"] + t * 2 * math.pi / g["n"] * g["dir"]
            x = 320 + math.cos(a) * g["ring"] * 1.5
            y = 180 + math.sin(a) * g["ring"] * .82
            r = g["r"] + (1 if (t + g["phase"]) % 1 < .5 else 0)
            turn = 2 * math.pi / {0: 1, 1: 3, 2: 4, 3: 2, 4: 4}[g["kind"]] * t * (1 if g["spin"] > 0 else -1)
            glyph(cv, x, y, g["kind"], r, g["col"], turn)
        frames.append(cv)
    return strip(frames)


def glyph_fold_frames():
    """8 frames: the glyphs spiral in and shrink to the corner of your sight, where the mark appears."""
    frames = []
    G = glyph_layout()
    tx, ty = 618, 22
    for f in range(8):
        cv = Canvas()
        t = (f + 1) / 8
        for g in G:
            a = g["a0"] + t * 2.4
            x = 320 + math.cos(a) * g["ring"] * 1.5 * (1 - t) + (tx - 320) * t ** 2
            y = 180 + math.sin(a) * g["ring"] * .82 * (1 - t) + (ty - 180) * t ** 2
            glyph(cv, x, y, g["kind"], max(2, g["r"] * (1 - t * .85)), g["col"], a)
        frames.append(cv)
    return strip(frames)


def glyph_mark():
    cv = Canvas(20, 20)
    m = poly([(10, 1), (12, 8), (19, 10), (12, 12), (10, 19), (8, 12), (1, 10), (8, 8)], 20, 20)
    cv.paint(m, C("violet", 3))
    cv.paint(poly([(10, 5), (11, 9), (15, 10), (11, 11), (10, 15), (9, 11), (5, 10), (9, 9)], 20, 20), C("brass", 4))
    cv.paint(edge(m), C("violet", 1))
    return cv


def spark_frames():
    """Sparks spitting from torn wiring: 6 frames, 40 x 40."""
    rnd = random.Random(29)
    frames = []
    for f in range(6):
        cv = Canvas(40, 40)
        for _ in range(4 if f % 2 == 0 else 2):
            a = rnd.uniform(-2.6, -.4)
            r = rnd.uniform(4, 16)
            x, y = 20 + math.cos(a) * r, 22 + math.sin(a) * r
            cv.paint(lines([(20, 22), (x, y)], 1, 40, 40) & ~disc(20, 22, r * .6, 40, 40), C("brass", 4))
            cv.paint(disc(x, y, 1, 40, 40), C("cream", 4))
        if f in (0, 3):
            cv.paint(disc(20, 22, 3, 40, 40), C("brass", 4))
        frames.append(cv)
    return strip(frames)


def blink_frames():
    a = Canvas(10, 10)
    a.paint(disc(5, 5, 4, 10, 10), C("berry", 1))
    a.paint(disc(5, 5, 2, 10, 10), C("berry", 2))
    b = Canvas(10, 10)
    b.paint(disc(5, 5, 4, 10, 10), C("berry", 2))
    b.paint(disc(5, 5, 3, 10, 10), C("berry", 3))
    b.paint(disc(4, 4, 1, 10, 10), C("berry", 4))
    return strip([a, b])


# ---------------------------------------------------------------- the ambush and the jump
def star_halves():
    """The Wandering Star (the starter ship) torn in two along a ragged line behind the canopy."""
    src = np.array(Image.open(os.path.join(ROOT, "art", "ships", "starter", "hull.png")).convert("RGBA"))
    h, w = src.shape[:2]
    rnd = random.Random(31)
    cut = np.array([176 + rnd.randint(-7, 7) + 6 * math.sin(y * .2) for y in range(h)])
    xx = np.arange(w)[None, :]
    front_m = (xx >= cut[:, None]) & (src[:, :, 3] > 0)
    back_m = (xx < cut[:, None]) & (src[:, :, 3] > 0)
    front, back = Canvas(w, h), Canvas(w, h)
    front.a[front_m] = src[front_m]
    back.a[back_m] = src[back_m]
    for cv, m, side in ((front, front_m, 1), (back, back_m, -1)):
        rim = m & ~sh(m, side * 3, 0)            # the torn edge: dark ripped metal, a hot line, ribs
        cv.paint(rim, C("rock", 1))
        cv.paint(rim & ~sh(m, side * 1, 0), C("copper", 3))
        for y in np.nonzero(rim.any(axis=1))[0][::9]:
            xs = np.nonzero(rim[y])[0]
            x = xs[0] if side > 0 else xs[-1]
            cv.paint(lines([(x, y), (x - side * 5, y + 1)], 2, w, h), C("rock", 2))
    return front, back


def flame_frames():
    frames = []
    for f in range(4):
        cv = Canvas(34, 16)
        ln = (22, 28, 24, 31)[f]
        cv.paint(poly([(34, 2), (34, 14), (34 - ln, 8)], 34, 16), C("copper", 2))
        cv.paint(poly([(34, 4), (34, 12), (34 - ln * .7, 8)], 34, 16), C("copper", 3))
        cv.paint(poly([(34, 6), (34, 10), (34 - ln * .4, 8)], 34, 16), C("brass", 4))
        frames.append(cv)
    return strip(frames)


def shield_frames():
    """Ivan's shield taking a hit: an oval shell flashing and fading from where the shot struck (6 frames, 300 x 240)."""
    frames = []
    ell = poly([(150 + math.cos(a) * 146, 120 + math.sin(a) * 116) for a in np.linspace(0, 2 * math.pi, 64)], 300, 240)
    xx = np.mgrid[0:240, 0:300][1]
    for f in range(6):
        cv = Canvas(300, 240)
        shell = ell & ~binary_erosion(ell, iterations=2 + (f < 2))
        if f < 5:
            cv.paint(shell & (xx < 120 + f * 20), C("glow", 3 if f < 2 else 2))
        cv.paint(disc(28, 120, 14 + f * 4, 300, 240) & shell, C("glow", 4) if f < 3 else C("glow", 3))
        frames.append(cv)
    return strip(frames)


def bolt(ramp):
    cv = Canvas(18, 5)
    cv.paint(poly([(0, 2), (17, 0), (17, 4), (0, 3)], 18, 5), C(ramp, 2))
    cv.paint(poly([(5, 1), (17, 1), (17, 3), (5, 3)], 18, 5), C(ramp, 4))
    return cv


def jump_streaks():
    cv = Canvas()
    rnd = random.Random(5)
    for _ in range(60):
        y = rnd.randint(4, H - 6)
        x0 = rnd.randint(-200, W - 60)
        ln = rnd.randint(60, 300)
        col = rnd.choice((("cream", 4), ("cream", 3), ("glow", 3), ("violet", 4), ("glow", 4)))
        th = rnd.choice((1, 2, 2, 3))
        cv.paint(poly([(x0, y), (x0 + ln, y), (x0 + ln, y + th), (x0, y + th)]), C(*col))
    return cv


# ---------------------------------------------------------------- the uncharted moon
def streak_frames():
    """Your ship's front half burning in: a white-hot head and a fire tail up and left of it (4 frames, 72 x 32)."""
    frames = []
    for f in range(4):
        cv = Canvas(72, 32)
        wob = (0, 2, 1, 3)[f]
        cv.paint(poly([(0, wob), (10, 0), (66, 19), (60, 28), (50, 28)], 72, 32), C("berry", 2))
        cv.paint(poly([(8, 2 + wob), (16, 3), (66, 20), (56, 25)], 72, 32), C("copper", 3))
        cv.paint(poly([(24, 9), (32, 9 + wob // 2), (66, 20), (60, 23)], 72, 32), C("brass", 4))
        head = poly([(56, 17), (66, 15), (71, 20), (66, 27), (57, 25)], 72, 32)
        cv.paint(head, C("cream", 4))
        cv.paint(edge(head), C("copper", 2))
        frames.append(cv)
    return strip(frames)


def impact_frames():
    """The impact on the moon's face: a flash, then a dust plume rising and spreading (8 frames, 96 x 72)."""
    frames = []
    for f in range(8):
        cv = Canvas(96, 72)
        if f < 2:
            cv.paint(disc(48, 56, 10 + f * 10, 96, 72), C("cream", 4))
            cv.paint(disc(48, 56, 6 + f * 6, 96, 72), C("brass", 4))
        else:
            k = f - 2
            for dx, dy, r in ((-14, -4, 10), (12, -6, 12), (0, -14, 14), (-24, 2, 8), (24, 2, 9)):
                m = disc(48 + dx * (1 + k * .25), 56 + dy * (1 + k * .4), r + k * 3, 96, 72)
                cv.paint(m, C("rock", 2) if k < 4 else C("rock", 1))
                cv.paint(m & ~sh(m, 2, 2), C("rock", 3) if k < 4 else C("rock", 2))
        frames.append(cv)
    return strip(frames)


def portrait():
    """The Mother-Drone in the talk box (128 x 128): its lens close up, veins burning out from it."""
    cv = Canvas(128, 128, fill=C("violet", 0))
    yy, xx = np.mgrid[0:128, 0:128].astype(float)
    shell = (xx - 64) ** 2 / 70 ** 2 + (yy - 70) ** 2 / 58 ** 2 <= 1
    nz = np.sqrt(np.clip(1 - (xx - 64) ** 2 / 70 ** 2 - (yy - 70) ** 2 / 58 ** 2, 0, 1))
    lum = -(xx - 64) / 70 * .45 - (yy - 70) / 58 * .6 + nz * .6
    tones = [C("rock", 0), C("rock", 1), C("rock", 2), C("rock", 3), C("rock", 4), C("cream", 4)]
    idx = np.digitize(lum, [.12, .3, .48, .66, .86])
    for k, t in enumerate(tones):
        cv.paint(shell & (idx == k), t)
    cv.paint(shell & ((yy - 70) / 58 > .55) & (idx <= 2), C("violet", 1))
    rnd = random.Random(21)
    vm = np.zeros((128, 128), bool)
    for k in range(7):
        a = -2.6 + k * .62 + rnd.uniform(-.1, .1)
        pts = []
        r = 30
        for _ in range(8):
            a += rnd.uniform(-.25, .25)
            pts.append((64 + math.cos(a) * r, 66 + math.sin(a) * r * .85))
            r += 8
        vm |= lines(pts, 2, 128, 128)
    vm &= binary_erosion(shell, iterations=2)
    cv.paint(sh(vm, 1, 1) & shell & ~vm, C("violet", 2))
    cv.paint(vm, C("brass", 3))
    cv.paint(edge(shell), C("rock", 0))
    rim = disc(64, 66, 28, 128, 128)
    cv.paint(rim, C("rock", 2))
    cv.paint(rim & ~sh(rim, 4, 4), C("rock", 4))
    cv.paint(rim & ~sh(rim, -3, -3), C("rock", 1))
    cv.paint(edge(rim), C("rock", 0))
    inner = disc(64, 66, 21, 128, 128)
    cv.paint(inner, C("glow", 2))
    cv.paint(disc(62, 64, 15, 128, 128), C("glow", 3))
    cv.paint(disc(62, 64, 7, 128, 128), C("glow", 4))
    cv.paint(inner & ~disc(64, 66, 18, 128, 128), C("violet", 3))
    cv.paint(edge(inner), C("rock", 0))
    cv.paint(disc(54, 56, 3, 128, 128), C("cream", 4))
    despeckle(cv, shell & ~rim, passes=2)
    return cv


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    front, back = star_halves()
    out = {
        "glyphs": glyph_frames(), "glyph_fold": glyph_fold_frames(), "glyph_mark": glyph_mark(),
        "sparks": spark_frames(), "blink": blink_frames(), "star_front": front, "star_back": back,
        "flame": flame_frames(), "shield": shield_frames(), "streak": streak_frames(), "impact": impact_frames(),
        "bolt_green": bolt("leaf"), "bolt_teal": bolt("glow"), "jump_streaks": jump_streaks(),
    }
    for name, c in out.items():
        if name not in ("star_front", "star_back"):     # those two are the game's own ship art, cut in two
            check(c, name)
        c.save(os.path.join(OUT_DIR, name + ".png"))
    for old in ("cavern", "drone_lit", "drone_wake", "drone_pulse", "lens", "violet_light", "beam", "motes", "drip",
                "moon", "fall_streak"):
        p = os.path.join(OUT_DIR, old + ".png")
        if os.path.exists(p):
            os.remove(p)
    p = portrait()
    check(p, "portrait")
    p.save(os.path.join(ROOT, "art", "portrait_motherdrone.png"))
    print("wrote", ", ".join(out), "and portrait_motherdrone")


if __name__ == "__main__":
    main()
