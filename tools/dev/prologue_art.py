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
  fighter_front.png, fighter_back.png    the Wandering Star as the main menu draws her (title/scene/fighter.png,
                        shown 3x like the menu) torn in two across her body for the blind jump
  fighter_intact.png    her as she was before the fight: the menu draws her after it (a breach in the hull, her
                        starboard wing sheared to a stump), so the breach is plated over, the wing is whole again,
                        and her engine ports glow;  wing_piece.png: the wing's outer part, tumbling, 4 frames
  fighter_plume.png     her engine plume as the menu draws it, behind her from each port, 4 frames;  shield.png: 6 frames
  approach.png          the moon you fall to, put together from the main menu's own art (starfield, gas giant, base)
  streak.png            your ship burning in, 4 frames;  impact.png: flash, fireball, thrown rock and dust, 10 frames
  bolt_green.png, bolt_teal.png, bolt_teal_d.png (along her heading), chip.png (a tumbling scrap of hull),
  rock_fg_a.png, rock_fg_b.png (near asteroids drifting past, in the backdrop's own colours), jump_streaks.png
and art/portrait_motherdrone.png. Run: python3 tools/dev/prologue_art.py [--preview]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation, binary_erosion
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
# ---------------------------------------------------------------- the main menu's fighter (Zachary, 24 Nov: "you can
# make the fighter look like the main menu still"): title/scene/fighter.png, shown 3x in the panels as the menu does
TITLE_FIGHTER = os.path.join(ROOT, "title", "scene", "fighter.png")
NOZZLES = ((13.66, 29.18), (21.48, 35.08))    # its two engine ports, in its own pixels (shaders/title/fighter)
PLUME_DIR = (-.879, .477)                      # the exhaust runs down and left, behind her, as in the menu
PLUME_BASE = (21, 3)                           # where a plume frame attaches to a port
FIGHTER_OUTLINE = (0x2c, 0x23, 0x36, 255)      # the menu art's outline colour
# The menu's own plume colours: a pale blue glow round an orange-gold core (shaders/title/fighter.gdshader)
PLUME_BLUE, PLUME_GOLD, NOZZLE_RED = (131, 165, 211), (255, 192, 104), (177, 88, 58)


def _hx(h):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


WING_TURN = (35.5, 24.5)      # her port wing turned half round about this point (her pixels) is her starboard wing


def whole_wing(a):
    """Her starboard wing as it was, from the menu art a: (the wing's pixels, the part of them past her hull's side,
    which gets drawn afresh)."""
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    port = (a[:, :, 3] > 0) & (xx <= 33) & (yy <= 21)
    wing = np.zeros((h, w), bool)
    ys, xs = np.nonzero(port)
    X, Y = np.round(2 * WING_TURN[0] - xs).astype(int), np.round(2 * WING_TURN[1] - ys).astype(int)
    ok = (X >= 0) & (X < w) & (Y >= 0) & (Y < h)
    wing[Y[ok], X[ok]] = True
    k = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    wing |= binary_erosion(binary_dilation(wing, structure=k), structure=k, border_value=0)     # no pinholes
    return wing, wing & (xx >= 47)


def wing_piece():
    """The part of her starboard wing Ivan's salvo shears off (what the whole ship has and the menu's battered one
    hasn't), tumbling: 4 frames, each a quarter turn on, square. Returns the strip and where its first frame's
    top-left sits on her (her pixels)."""
    whole = fighter_intact().a
    menu = np.array(Image.open(TITLE_FIGHTER).convert("RGBA"))
    m = (whole[:, :, 3] > 0) & (menu[:, :, 3] == 0)
    m &= np.mgrid[0:m.shape[0], 0:m.shape[1]][1] >= 44
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min() - 1, xs.max() + 1
    piece = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    sub = m[y0:y1, x0:x1]
    piece[sub] = whole[y0:y1, x0:x1][sub]
    solid = piece[:, :, 3] > 0
    piece[edge(solid)] = FIGHTER_OUTLINE             # the menu art's outline all round, the torn root too
    side = max(piece.shape[:2]) + 2
    sq = np.zeros((side, side, 4), np.uint8)
    py, px = (side - piece.shape[0]) // 2, (side - piece.shape[1]) // 2
    sq[py:py + piece.shape[0], px:px + piece.shape[1]] = piece
    frames = []
    for k in range(4):
        cv = Canvas(side, side)
        cv.a = np.ascontiguousarray(np.rot90(sq, -k))
        frames.append(cv)
    return strip(frames), (int(x0) - px, int(y0) - py)


def fighter_intact():
    """The menu fighter before Ivan finds her (Zachary, 24 Nov: "in the opening scene the ship is already damaged").
    The menu draws her after the fight: a breach in her hull between the orange stripes, two small holes, and her
    starboard wing sheared off to a stump (it sparks there in the menu). Here the breach and the holes are plated over
    by carrying her stripes along her length across them, the wing is whole again (whole_wing), and her engine ports
    glow as the menu's do when she's under power (72 x 49, the menu art's own colours)."""
    a = np.array(Image.open(TITLE_FIGHTER).convert("RGBA"))
    h, w = a.shape[:2]
    W_, c_, s_, p_, o_, O_ = (_hx(k) for k in ("ffebc9", "f1d6af", "d4b5a8", "bd9da6", "ed651c", "ae471d"))
    eq = lambda c: np.all(a == np.array(c), axis=-1)
    dark = eq(_hx("38293f")) | eq(_hx("776575"))
    dmg = np.zeros((h, w), bool)
    for ys, xs in ((slice(13, 24), slice(26, 41)), (slice(15, 19), slice(16, 20)), (slice(30, 33), slice(36, 40))):
        dmg[ys, xs] |= dark[ys, xs]
    out = a.copy()
    edge_px = eq(FIGHTER_OUTLINE)
    for y, x in zip(*np.nonzero(dmg)):
        best = None
        for sgn in (1, -1):                  # along her length (her stripes run that way) to the nearest sound hull
            for k in range(1, 14):
                X, Y = x + sgn * 2 * k, y - sgn * k
                if not (0 <= X < w and 0 <= Y < h) or a[Y, X, 3] == 0 or edge_px[Y, X]:
                    break
                if not dmg[Y, X]:
                    if best is None or k < best[0]:
                        best = (k, a[Y, X])
                    break
        if best is not None:
            out[y, x] = best[1]
    # her starboard wing, whole (Zachary, 25 Nov: "the wing still is not fully intact like the left wing, it has to be
    # whole to then be damaged"). The menu shows only its stump, sheared off along a straight edge. In this view the
    # two wings sit either side of her hull like a turned pair, so the whole wing is her port wing turned half round
    # about her middle (WING_TURN), joined onto the stump, shaded fresh for light from the top left (lit along its top
    # edge, shadowed along its underside) and given her orange stripes: the stump's carried on, and one across it.
    wing, ext = whole_wing(a)
    out[ext] = c_
    U = (a[:, :, 3] > 0) | wing
    up_out = lambda k: np.any([~np.roll(U, i, axis=0) for i in range(1, k + 1)], axis=0)
    dn_out = lambda k: np.any([~np.roll(U, -i, axis=0) for i in range(1, k + 1)], axis=0)
    out[ext & up_out(3)] = W_
    out[ext & dn_out(3)] = s_
    out[ext & dn_out(1)] = p_
    yy, xx = np.mgrid[0:h, 0:w]
    for (x0, y0), half, keep in (((50.5, 30.5), 1.6, ~dn_out(1)), ((56.0, 37.0), 1.5, ~dn_out(2) & ~up_out(1))):
        across = (xx + .5 - x0) * .447 + (yy + .5 - y0) * .894      # her stripes run along her: 2 across, 1 up
        out[ext & keep & (np.abs(across) < half)] = o_
        out[ext & keep & (np.abs(across) < half) & (across > .75)] = O_
    rim = U & ~binary_erosion(U, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]], border_value=0)
    out[rim] = FIGHTER_OUTLINE
    out[ext & ~rim & np.all(a == np.array(FIGHTER_OUTLINE), axis=-1)] = W_    # the stump's cut edge, gone inside
    # the engine ports lit, as the menu lights them: a red-hot bowl with a gold heart
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    pod = eq(_hx("38293f")) | eq(_hx("ae471d")) | eq(_hx("564258"))
    for nx, ny in NOZZLES:
        du, dv = xx + .5 - nx, yy + .5 - ny
        d2 = ((.8 * du + .6 * dv) / 2.7) ** 2 + ((-.6 * du + .8 * dv) / 1.3) ** 2
        out[(d2 < 1) & pod] = NOZZLE_RED + (255,)
        out[(d2 < .35) & pod] = PLUME_GOLD + (255,)
    cv = Canvas(w, h)
    cv.a = out
    return cv


def fighter_halves():
    """The menu fighter torn in two across its body, between the canopy and the engines (72 x 49 each)."""
    src = np.array(Image.open(TITLE_FIGHTER).convert("RGBA"))
    h, w = src.shape[:2]
    rnd = random.Random(37)
    d = np.array([.884, -.467])
    c = np.array([36.0, 21.0])
    yy, xx = np.mgrid[0:h, 0:w]
    along = (xx - c[0]) * d[0] + (yy - c[1]) * d[1]
    across = (xx - c[0]) * -d[1] + (yy - c[1]) * d[0]
    jag = np.array([rnd.uniform(-1.6, 1.6) for _ in range(80)])
    cutline = jag[np.clip((across + 40).astype(int), 0, 79)]
    solid = src[:, :, 3] > 0
    front_m = solid & (along > cutline)
    back_m = solid & (along <= cutline)
    front, back = Canvas(w, h), Canvas(w, h)
    front.a[front_m] = src[front_m]
    back.a[back_m] = src[back_m]
    for cv, m in ((front, front_m), (back, back_m)):
        near = np.abs(along - cutline) < 2.2
        rim = m & near
        cv.paint(rim, C("rock", 1))                                   # the ship's ribs, bared
        cv.paint(rim & ~edge(m) & (np.abs(along - cutline) < 1.8), C("copper", 3))     # still hot
        cv.paint(edge(m) & near, FIGHTER_OUTLINE)                     # the menu art's own outline on the torn edge
    return front, back


def fighter_plume_frames():
    """Her engine plume, as the menu draws it: a pale blue glow round an orange-gold core, trailing down and left from
    a port and flickering (4 frames, 24 x 16; it attaches at PLUME_BASE, and is drawn behind her). The menu's own
    colours, in see-through steps."""
    W2, H2 = 24, 16
    frames = []
    yy, xx = np.mgrid[0:H2, 0:W2].astype(float)
    bx, by = PLUME_BASE
    dx, dy = PLUME_DIR
    along = (xx + .5 - bx) * dx + (yy + .5 - by) * dy
    across = (xx + .5 - bx) * -dy + (yy + .5 - by) * dx
    for f in range(4):
        cv = Canvas(W2, H2)
        reach = (15.0, 18.0, 16.0, 19.0)[f]
        sway = (0, .6, -.4, .3)[f]
        z = np.clip(along / reach, 0, 1)
        wdt = 3.4 * (1 - z) ** .8 + .6
        u = np.abs(across - sway * z * z) / wdt
        inside = (along > -1) & (along < reach)
        cv.a[inside & (u < 1)] = PLUME_BLUE + (150,)                         # the glow
        cv.a[inside & (u < .7) & (z < .9)] = PLUME_BLUE + (225,)
        cv.a[inside & (u < .48) & (z < .72)] = PLUME_GOLD + (255,)           # the flame
        cv.a[inside & (u < .26) & (z < .34)] = (255, 236, 196, 255)          # white-hot where it leaves the port
        frames.append(cv)
    return strip(frames)


def approach():
    """The moon you fall to, from the main menu's own art: its starfield (the green storm at its edge), the gas
    giant, and Echo Landing on the moon's rim far off (640 x 360). The menu's art has its own colours."""
    star_ = Image.open(os.path.join(ROOT, "title", "scene", "starfield.png")).convert("RGBA").crop((560, 100, 1200, 460))
    planet = Image.open(os.path.join(ROOT, "title", "scene", "planet.png")).convert("RGBA")
    star_.alpha_composite(planet.crop((0, 0, 330, 300)), (380, 0))
    base = Image.open(os.path.join(ROOT, "title", "scene", "moon_base.png")).convert("RGBA")
    star_.alpha_composite(base, (155, 140))
    cv = Canvas()
    cv.a = np.array(star_)
    return cv


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


AXIS = (.884, -.467)          # the menu fighter's nose points this way (up and right)


def jump_streaks():
    """Starlight smeared along your heading as space folds: long streaks up and to the right (640 x 360)."""
    cv = Canvas()
    rnd = random.Random(5)
    dx, dy = AXIS
    for _ in range(70):
        x0, y0 = rnd.uniform(-260, W), rnd.uniform(0, H + 140)
        ln = rnd.uniform(70, 320)
        col = rnd.choice((("cream", 4), ("cream", 3), ("glow", 3), ("violet", 4), ("glow", 4), ("violet", 3)))
        th = rnd.choice((1, 2, 2, 3))
        cv.paint(lines([(x0, y0), (x0 + dx * ln, y0 + dy * ln)], th), C(*col))
        if th >= 2:                                       # a bright head on the thick ones
            cv.paint(disc(x0 + dx * ln, y0 + dy * ln, 1.6), C("cream", 4))
    return cv


def bolt_diag(ramp):
    """A bolt flying along the menu fighter's heading, up and to the right (22 x 14)."""
    cv = Canvas(22, 14)
    a, b = (2, 12), (2 + 18 * AXIS[0], 12 + 18 * AXIS[1])
    cv.paint(lines([a, b], 4, 22, 14), C(ramp, 2))
    cv.paint(lines([(a[0] + 4, a[1] - 2), b], 2, 22, 14), C(ramp, 4))
    cv.paint(disc(b[0], b[1], 1.5, 22, 14), C("cream", 4))
    return cv


def chip_frames():
    """A scrap of hull plating tumbling away from a hit (4 frames, 12 x 12)."""
    frames = []
    for f in range(4):
        cv = Canvas(12, 12)
        a = f * math.pi / 4
        pts = [(6 + math.cos(a + k) * r, 6 + math.sin(a + k) * r * .7) for k, r in ((0, 5), (1.9, 4), (3.3, 5), (4.6, 3.5))]
        m = poly(pts, 12, 12)
        cv.paint(m, C("cream", 3))
        cv.paint(m & ~sh(m, 1, 1), C("cream", 4))
        cv.paint(m & ~sh(m, -1, -1), C("copper", 2) if f % 2 else C("cream", 2))
        cv.paint(edge(m), OUT)
        frames.append(cv)
    return strip(frames)


ROCK_TONES = ("47223b", "814347", "b86a51", "e7b077", "ffe0aa")     # the asteroid backdrop's own rock colours


def rock_fg(seed, w, h):
    """A near asteroid drifting past, shaded like the backdrop's rocks (lit from the top left, 4 tones and a glint,
    a crater or two), but closer, so bigger and sharper. Off the master palette: these are the backdrop's colours."""
    rnd = random.Random(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    u, v = (xx + .5 - w / 2) / (w / 2 - 2), (yy + .5 - h / 2) / (h / 2 - 2)
    ang = np.arctan2(v, u)
    r = np.hypot(u, v)
    lump = 1 + sum(rnd.uniform(.04, .09) * np.sin(ang * k + rnd.uniform(0, 6)) for k in (2, 3, 5))
    m = r <= lump * .96
    z = np.sqrt(np.clip(1 - (r / lump) ** 2, 0, 1))
    nx, ny = u, v
    for _ in range(3):              # a few broad facets: dents in the surface
        cx, cy, cr = rnd.uniform(-.5, .5), rnd.uniform(-.5, .5), rnd.uniform(.25, .45)
        d = np.hypot(u - cx, v - cy)
        k = np.clip(1 - d / cr, 0, 1)
        nx = nx - (u - cx) * k * 1.4
        ny = ny - (v - cy) * k * 1.4
    lum = (-nx * .5 - ny * .65 + z * .55)
    lum = np.round(lum * 3) / 3                       # flat facets, as the backdrop's rocks have
    idx = np.digitize(lum, [-.2, .25, .62, .95])
    cv = Canvas(w, h)
    for i, hx in enumerate(ROCK_TONES):
        cv.paint(m & (idx == i), (int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), 255))
    for k in range(2 if w > 60 else 1):         # one big crater, one small one off to the side (not a face)
        cx, cy = (w * .58, h * .56) if k == 0 else (w * .3, h * .38)
        cr = w * (.11 if k == 0 else .05)
        crater = disc(cx, cy, cr, w, h) & binary_erosion(m, iterations=3)
        cv.paint(crater, (0x81, 0x43, 0x47, 255))
        cv.paint(crater & ~sh(crater, 2, 2), (0x47, 0x22, 0x3b, 255))
        cv.paint(crater & ~sh(crater, -2, -2) & ~sh(crater, 2, 2), (0xb8, 0x6a, 0x51, 255))
    despeckle(cv, m, passes=2)
    return cv


# ---------------------------------------------------------------- the uncharted moon
def streak_frames():
    """Your ship's front half burning in: a white-hot head in a shell of fire, a long tail that flickers and breaks
    into sparks, and a smoke trail behind it (4 frames, 112 x 48; the head at about 100, 34)."""
    frames = []
    rnd = random.Random(41)
    hx, hy = 100, 34
    dx, dy = math.cos(math.radians(25)), math.sin(math.radians(25))
    px, py = -dy, dx

    def along(t, off):
        return (hx - dx * t + px * off, hy - dy * t + py * off)
    for f in range(4):
        cv = Canvas(112, 48)
        # smoke behind, broken into puffs that drift with the frame
        for k in range(4):
            t = 46 + k * 10 + (f * 3) % 10
            r = 3 + k * .6
            cx, cy = along(t, (k % 2 * 2 - 1) * 2)
            if cy - r < 1 or cx - r < 1:
                continue
            m = disc(cx, cy, r, 112, 48)
            cv.paint(m, C("rock", 1) if k > 2 else C("rock", 2))
            cv.paint(m & ~sh(m, 1, 1), C("rock", 2) if k > 2 else C("rock", 3))
        wob = (0, 2, 1, 3)[f]
        cv.paint(poly([along(0, -8), along(40, -6), along(70 + wob * 3, -2), along(78 + wob * 2, 0), along(66, 4), along(36, 7), along(0, 9)], 112, 48), C("berry", 2))
        cv.paint(poly([along(2, -6), along(30, -4), along(56 + wob * 3, -1), along(60, 1), along(28, 5), along(2, 7)], 112, 48), C("copper", 3))
        cv.paint(poly([along(4, -4), along(36 + wob * 2, 0), along(4, 4)], 112, 48), C("brass", 4))
        for k in range(5):                                # sparks shed from the tail
            t = rnd.uniform(20, 70)
            x, y = along(t, rnd.uniform(-8, 8))
            cv.paint(disc(x, y, 1, 112, 48), C("brass", 4) if k % 2 else C("copper", 4))
        head = poly([along(-4, 0), along(2, -6), along(10, -4), along(10, 4), along(2, 6)], 112, 48)
        cv.paint(head, C("cream", 4))
        cv.paint(edge(head), C("copper", 3))
        cv.paint(disc(hx - 2, hy - 1, 2, 112, 48), C("cream", 4))
        frames.append(cv)
    return strip(frames)


def impact_frames():
    """The strike on the moon's face: a white flash, a fireball, rock thrown out on arcs, then a dust plume that
    rises, spreads and thins (10 frames, 160 x 112; ground zero at 80, 96). Nothing reaches the frame's edge."""
    frames = []
    rnd = random.Random(43)
    W2, H2, gx, gy = 160, 112, 80, 96
    chunks = [(rnd.uniform(-2.9, -.25), rnd.uniform(26, 50), rnd.uniform(1.5, 3)) for _ in range(9)]
    puffs = ((-16, -6, 11), (16, -8, 12), (0, -16, 14), (-32, 0, 8), (32, 0, 9), (-8, -30, 10), (10, -32, 9))
    for f in range(10):
        cv = Canvas(W2, H2)
        if f >= 2:                                            # the dust: puffs rising and spreading, darkening
            k = f - 2
            dark = k >= 5
            for ox, oy, rr in puffs:
                if oy < -20 and k < 2:
                    continue
                cy = gy + oy * (1 + k * .14) - k * 1.5
                r = min(rr + k * 1.8, 22) * (1 - max(0, f - 7) * .2)      # thinning away at the end
                cy = min(max(cy, r + 3), H2 - r - 4)
                cx = min(max(gx + ox * (1 + k * .16), r + 3), W2 - r - 4)
                m = disc(cx, cy, r, W2, H2)
                cv.paint(m, C("rock", 1) if dark else C("rock", 2))
                cv.paint(m & ~sh(m, 3, 3), C("rock", 2) if dark else C("rock", 3))
                cv.paint(m & ~sh(m, 5, 6) & ~sh(m, 2, 2), C("rock", 3) if dark else C("rock", 4))
        if f <= 1:
            r = 8 + f * 10
            cv.paint(disc(gx, gy - 12, r + 6, W2, H2), C("brass", 4))
            cv.paint(disc(gx, gy - 12, r, W2, H2), C("cream", 4))
        if 1 <= f <= 4:                                       # the fireball, rolling up out of the dust
            k = f - 1
            for ox, oy, rr in ((0, -10, 13), (-11, -4, 9), (11, -4, 9), (0, -22, 8)):
                m = disc(gx + ox * (1 + k * .25), gy + oy * (1 + k * .35), max(3, rr + 2 - k * 2), W2, H2)
                cv.paint(m, C("copper", 2) if k > 1 else C("copper", 3))
                cv.paint(m & ~sh(m, 2, 3), C("copper", 3) if k > 1 else C("brass", 3))
                cv.paint(m & ~sh(m, 4, 5), C("brass", 4) if k < 2 else C("copper", 4))
        for a, sp, rr in chunks:                              # rock thrown out on arcs
            if 1 <= f <= 7:
                t = f / 7
                x = gx + math.cos(a) * sp * t * 1.5
                y = gy - 6 + math.sin(a) * sp * t * 1.3 + 40 * t * t
                if 4 < x < W2 - 5 and 4 < y < H2 - 5:
                    m = disc(x, y, rr, W2, H2)
                    cv.paint(m, C("rock", 1))
                    cv.paint(m & ~sh(m, 1, 1), C("rock", 3))
        assert not cv.a[0, :, 3].any() and not cv.a[-1, :, 3].any() and not cv.a[:, 0, 3].any() and not cv.a[:, -1, 3].any(), f
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
    ffront, fback = fighter_halves()
    piece, piece_at = wing_piece()
    print("wing piece: frames of", piece.h, "; its first frame's top-left on her at", piece_at)
    out = {
        "fighter_intact": fighter_intact(), "fighter_front": ffront, "fighter_back": fback, "wing_piece": piece,
        "fighter_plume": fighter_plume_frames(), "approach": approach(),
        "bolt_teal_d": bolt_diag("glow"), "chip": chip_frames(), "rock_fg_a": rock_fg(3, 96, 70), "rock_fg_b": rock_fg(8, 40, 30),
        "glyphs": glyph_frames(), "glyph_fold": glyph_fold_frames(), "glyph_mark": glyph_mark(),
        "sparks": spark_frames(), "blink": blink_frames(), "shield": shield_frames(), "streak": streak_frames(), "impact": impact_frames(),
        "bolt_green": bolt("leaf"), "bolt_teal": bolt("glow"), "jump_streaks": jump_streaks(),
    }
    for name, c in out.items():
        if name not in ("fighter_intact", "fighter_front", "fighter_back", "fighter_plume", "wing_piece", "approach",
                        "rock_fg_a", "rock_fg_b"):    # the menu's and the backdrop's own colours
            check(c, name)
        c.save(os.path.join(OUT_DIR, name + ".png"))
    for old in ("cavern", "drone_lit", "drone_wake", "drone_pulse", "lens", "violet_light", "beam", "drip",
                "moon", "fall_streak", "star_front", "star_back", "flame", "fighter_flame"):
        p = os.path.join(OUT_DIR, old + ".png")
        if os.path.exists(p):
            os.remove(p)
    p = portrait()
    check(p, "portrait")
    p.save(os.path.join(ROOT, "art", "portrait_motherdrone.png"))
    print("wrote", ", ".join(out), "and portrait_motherdrone")


if __name__ == "__main__":
    main()
