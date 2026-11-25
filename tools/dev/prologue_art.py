"""The prologue's pictures (24 Nov 2026): the crash cavern with the Mother-Drone, and the small pieces the
cutscene moves over the space panels. Drawn in code to the art style guide (claude/echo-landing-art-style-guide.md):
only the master palette, a #5b332d outline round foreground silhouettes, big flat areas with 2-4 shades, light from
the top left, no single-pixel specks.

The space panels reuse the game's own art (the asteroid and empty backdrops, the cratered moon, Ivan's flagship,
the title screen's fighter); see scripts/heart_events.gd SCENES "prologue". Writes art/prologue/*.png and
art/portrait_motherdrone.png. Run: python3 tools/dev/prologue_art.py [--preview]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion, label

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


def rock_shape(cv, m, ramp, lit=5, dark=4, outline=True, lo=1):
    """A chunky rock mass lit from the top left: mid tone, a light band on its top-left edges, a dark band on
    its bottom-right ones, an outline round it. ramp: (dark, mid, light, highlight) colour tuples."""
    d, mid, li, hi = ramp
    cv.paint(m, mid)
    cv.paint(m & ~sh(m, lit, lit), li)
    cv.paint(m & ~sh(m, 2, 2) & ~sh(m, lit, lit), hi)
    cv.paint(m & ~sh(m, -dark, -dark), d)
    if outline:
        cv.paint(edge(m), OUT)


ROCK = (C("rock", 0), C("rock", 1), C("rock", 2), C("rock", 3))
ROCK_DEEP = (C("rock", 0), C("rock", 1), C("rock", 1), C("rock", 2))
WARM = (C("soil", 0), C("soil", 1), C("soil", 2), C("soil", 3))


def jagged(x0, y0, x1, y1, n, amp, rnd):
    """Points along a rough edge from (x0, y0) to (x1, y1)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        if 0 < i < n:
            x += rnd.uniform(-amp, amp) * .4
            y += rnd.uniform(-amp, amp)
        pts.append((round(x), round(y)))
    return pts


def chunk(cx, cy, r, rnd, sides=7, squash=.75):
    pts = []
    for k in range(sides):
        a = 2 * math.pi * k / sides + rnd.uniform(-.25, .25)
        rr = r * rnd.uniform(.75, 1.1)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * squash))
    return pts


def despeckle(cv, region, passes=2):
    """Pixels inside region whose colour no 4-neighbour shares take the most common neighbour colour."""
    for _ in range(passes):
        a = cv.a
        key = (a[:, :, 0].astype(np.int64) << 24) | (a[:, :, 1].astype(np.int64) << 16) | (a[:, :, 2].astype(np.int64) << 8) | a[:, :, 3]
        n = [sh_key(key, dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        lonely = region & np.all([k != key for k in n], axis=0)
        ys, xs = np.nonzero(lonely)
        for y, x in zip(ys, xs):
            vals = [int(k[y, x]) for k in n]
            best = max(set(vals), key=vals.count)
            cv.a[y, x] = [(best >> 24) & 255, (best >> 16) & 255, (best >> 8) & 255, best & 255]


def sh_key(k, dx, dy):
    out = np.full_like(k, -1)
    h, w = k.shape
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = k[ys, xs]
    return out


def star(cv, x, y, big=False, c=None):
    c = c or C("cream", 3)
    if big:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            cv.a[y + dy, x + dx] = c
        cv.a[y, x] = C("cream", 4)
    else:
        cv.a[y:y + 2, x:x + 2] = c


# ---------------------------------------------------------------- the Mother-Drone
# A seed-shaped shell lying on its side, tip up to the right, half sunk in basalt. u runs along it, v across.
DRONE = dict(cx=452.0, cy=236.0, a=138.0, b=70.0, rot=math.radians(-14))
LENS_U, LENS_V, LENS_R = -.60, -.30, 17


def drone_uv(x, y):
    d = DRONE
    dx, dy = x - d["cx"], y - d["cy"]
    c, s = math.cos(d["rot"]), math.sin(d["rot"])
    return (dx * c + dy * s) / d["a"], (-dx * s + dy * c) / d["b"]


def drone_xy(u, v):
    d = DRONE
    c, s = math.cos(d["rot"]), math.sin(d["rot"])
    x, y = u * d["a"], v * d["b"]
    return d["cx"] + x * c - y * s, d["cy"] + x * s + y * c


def drone_mask():
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    d = DRONE
    c, s = math.cos(d["rot"]), math.sin(d["rot"])
    dx, dy = xx + .5 - d["cx"], yy + .5 - d["cy"]
    u = (dx * c + dy * s) / d["a"]
    v = (-dx * s + dy * c) / d["b"]
    half = np.clip(1 - u * u, 0, None) ** .62           # a seed: round in the middle, pointed at both ends
    half = half * (1 - .18 * np.clip(u, 0, None))      # the tip end a little slimmer
    m = (np.abs(u) <= 1) & (np.abs(v) <= half)
    return m, u, v, half


def draw_drone(cv):
    m, u, v, half = drone_mask()
    # shading: an ellipsoid lit from the top left and in front
    vn = np.where(half > 0, v / np.maximum(half, 1e-3), 0)
    nz = np.sqrt(np.clip(1 - u * u * .55 - vn * vn, 0, 1))
    c, s = math.cos(DRONE["rot"]), math.sin(DRONE["rot"])
    nx = u * .7 * c - vn * s
    ny = u * .7 * s + vn * c
    L = np.array([-.55, -.62, .56])
    L = L / np.linalg.norm(L)
    lum = nx * L[0] + ny * L[1] + nz * L[2]
    tones = [C("rock", 1), C("rock", 2), C("rock", 3), C("rock", 4), C("cream", 4)]
    cuts = [-.02, .3, .58, .86]
    idx = np.digitize(lum, cuts)
    for k, t in enumerate(tones):
        cv.paint(m & (idx == k), t)
    # panel seams: a long one down its side, and three rings
    seam = np.zeros_like(m)
    seam |= m & (np.abs(vn - .42) < .022 * 3)
    for uu in (-.30, .40):
        seam |= m & (np.abs(u - uu) < .013) & (np.abs(vn) < .95)
    seam &= ~edge(m)
    darker = {tones[i]: tones[max(0, i - 1)] for i in range(5)}
    ys, xs = np.nonzero(seam)
    for y, x in zip(ys, xs):
        t = tuple(int(q) for q in cv.a[y, x])
        cv.a[y, x] = darker.get(t, t)
    cv.paint(edge(m), OUT)
    return m


def vein_paths(rnd):
    """Branching paths over the shell, from the lens outwards, in (u, v)."""
    paths = []
    starts = [(LENS_U + .12, LENS_V - .22, .1, -.55), (LENS_U + .16, LENS_V + .05, .12, .02),
              (LENS_U + .12, LENS_V + .3, .1, .5), (LENS_U + .02, LENS_V - .38, .02, -.9)]
    for u0, v0, du, dv in starts:
        u, v = u0, v0
        pts = [(u, v)]
        heading = math.atan2(dv, du * 3)
        for step in range(22):
            heading += rnd.uniform(-.35, .35) - .15 * v * (1 if du > .05 else 0)
            u += math.cos(heading) * .075
            v += math.sin(heading) * .09
            if u > .92 or abs(v) > .8:
                break
            pts.append((u, v))
            if step in (5, 11) and rnd.random() < .8:
                bu, bv, bh = u, v, heading + rnd.choice((-.9, .9))
                br = [(bu, bv)]
                for _ in range(6):
                    bh += rnd.uniform(-.3, .3)
                    bu += math.cos(bh) * .07
                    bv += math.sin(bh) * .09
                    if bu > .9 or abs(bv) > .78:
                        break
                    br.append((bu, bv))
                paths.append(br)
        paths.append(pts)
    return paths


def veins_mask(drone, rnd):
    m = np.zeros((H, W), bool)
    for p in vein_paths(rnd):
        m |= lines([drone_xy(u, v) for u, v in p], 2)
    return m & binary_erosion(drone, iterations=2)


def lens_center():
    return drone_xy(LENS_U, LENS_V)


def draw_lens(cv, lit):
    x, y = lens_center()
    x, y = round(x), round(y)
    rim = disc(x, y, LENS_R)
    cv.paint(rim, C("rock", 2))
    cv.paint(rim & ~sh(rim, 3, 3), C("rock", 4))
    cv.paint(edge(rim), OUT)
    inner = disc(x, y, LENS_R - 4)
    if lit:
        cv.paint(inner, C("glow", 2))
        cv.paint(disc(x - 1, y - 1, LENS_R - 7), C("glow", 3))
        cv.paint(disc(x - 1, y - 1, 5), C("glow", 4))
        ring = disc(x, y, LENS_R - 4) & ~disc(x, y, LENS_R - 6)
        cv.paint(ring, C("violet", 3))
        cv.paint(disc(x - 6, y - 6, 2), C("cream", 4))
    else:
        cv.paint(inner, C("violet", 0))
        ring = disc(x, y, LENS_R - 4) & ~disc(x, y, LENS_R - 6)
        cv.paint(ring, C("violet", 1))
        cv.paint(disc(x - 6, y - 6, 2), C("violet", 2))
    cv.paint(edge(inner), OUT)


# ---------------------------------------------------------------- the cavern
def rough(pts, rnd, amp=5, step=14):
    """A hand-made outline roughened: extra points along each side, nudged in and out."""
    out = []
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        seg = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for k in range(seg):
            t = k / seg
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if k:
                nx, ny = -(y1 - y0), x1 - x0
                ln = math.hypot(nx, ny) or 1
                d = rnd.uniform(-amp, amp)
                x, y = x + nx / ln * d, y + ny / ln * d
            out.append((round(x), round(y)))
    return out


def cracks(cv, m, rnd, n, col, length=(10, 26)):
    """A few chunky cracks (2 px) inside a rock mass."""
    ys, xs = np.nonzero(binary_erosion(m, iterations=6))
    if not len(xs):
        return
    for _ in range(n):
        i = rnd.randrange(len(xs))
        x, y = float(xs[i]), float(ys[i])
        pts = [(x, y)]
        a = rnd.uniform(0, math.pi)
        for _ in range(3):
            a += rnd.uniform(-.7, .7)
            ln = rnd.uniform(*length) / 3
            x, y = x + math.cos(a) * ln, y + math.sin(a) * ln
            pts.append((x, y))
        cv.paint(lines(pts, 2) & binary_erosion(m, iterations=3), col)


def cavern():
    rnd = random.Random(7)
    VOID = C("violet", 0)
    cv = Canvas(fill=VOID)
    hole = poly(rough([(176, 0), (296, 0), (288, 18), (270, 30), (246, 38), (214, 36), (192, 26), (180, 14)], rnd, 3, 10))
    cv.paint(hole, C("violet", 1))
    cv.paint(hole & (np.mgrid[0:H, 0:W][0] < 10), C("violet", 2))
    for sx, sy, big in ((196, 12, False), (226, 22, True), (258, 12, False), (280, 6, False), (240, 30, False)):
        star(cv, sx, sy, big)
    # light falling through the hole: what's inside is a step lighter
    shaft = poly([(194, 30), (282, 30), (330, 340), (120, 340)]) & ~hole
    cv.paint(shaft, C("rock", 0))
    # back wall masses, far off: dark, no outline
    backs = []
    for pts in ([(0, 50), (50, 40), (110, 64), (150, 120), (128, 190), (70, 230), (0, 236)],
                [(500, 40), (580, 20), (640, 30), (640, 220), (600, 200), (560, 150), (520, 110)],
                [(300, 50), (350, 40), (420, 56), (470, 100), (450, 150), (380, 150), (320, 110)]):
        m = poly(rough(pts, rnd, 6, 16)) & ~hole
        backs.append(m)
        cv.paint(m, C("rock", 0))
        cv.paint(m & ~sh(m, 4, 4), C("rock", 1))
        cv.paint(m & shaft, C("rock", 1))
        cv.paint(m & shaft & ~sh(m, 4, 4), C("rock", 2))
        cracks(cv, m, rnd, 3, VOID)
    # the broken rim round the hole
    rim = poly(rough([(150, 0), (176, 0), (180, 14), (192, 26), (214, 36), (246, 38), (270, 30), (288, 18), (296, 0), (324, 0),
                      (318, 24), (300, 44), (264, 56), (216, 56), (178, 46), (158, 26)], rnd, 3, 10)) & ~hole
    rock_shape(cv, rim, ROCK_DEEP, lit=3, dark=3)
    # the roof, with stalactites
    roof = poly(rough([(0, 0), (150, 0), (158, 26), (178, 46), (150, 54), (110, 44), (60, 54), (0, 48)], rnd, 4, 14))
    roof |= poly(rough([(324, 0), (640, 0), (640, 34), (560, 44), (480, 36), (400, 50), (334, 42), (318, 24)], rnd, 4, 14))
    rock_shape(cv, roof & ~hole, ROCK_DEEP, lit=3, dark=4)
    for x, y, w, h in ((36, 46, 22, 46), (96, 42, 16, 28), (352, 42, 20, 40), (424, 42, 26, 58), (500, 36, 18, 34), (572, 38, 24, 50)):
        st = poly([(x, y - 6), (x + w, y - 6), (x + w * .66, y + h * .5), (x + w * .5, y + h), (x + w * .3, y + h * .45)])
        rock_shape(cv, st, ROCK_DEEP, lit=3, dark=3)
    # the side walls
    left = poly(rough([(0, 44), (34, 44), (62, 84), (50, 132), (72, 190), (54, 244), (70, 300), (48, 360), (0, 360)], rnd, 5, 14))
    rock_shape(cv, left, ROCK_DEEP, lit=5, dark=4)
    cracks(cv, left, rnd, 4, C("rock", 0))
    right = poly(rough([(612, 34), (640, 34), (640, 360), (600, 360), (586, 300), (606, 240), (588, 182), (614, 120), (596, 64)], rnd, 5, 14))
    rock_shape(cv, right, ROCK_DEEP, lit=5, dark=4)
    cracks(cv, right, rnd, 3, C("rock", 0))
    # the Mother-Drone, half sunk in the floor
    drone = draw_drone(cv)
    veins = veins_mask(drone, random.Random(11))
    cv.paint(veins, C("rock", 1))
    draw_lens(cv, False)
    # the floor: basalt, banked up over the drone's underside
    floor = poly(rough([(0, 360), (0, 316), (60, 306), (120, 300), (180, 302), (240, 296), (296, 288), (326, 266), (366, 252),
                        (420, 258), (470, 252), (520, 244), (566, 250), (606, 268), (640, 278), (640, 360)], rnd, 3, 16))
    rock_shape(cv, floor, ROCK_DEEP, lit=5, dark=5)
    cracks(cv, floor, rnd, 6, C("rock", 0))
    floor_cover = floor.copy()
    # a pool of firelight round the wreck: the floor there warms through the soil ramp
    pool = floor & (((np.mgrid[0:H, 0:W][1] - 130) / 150.0) ** 2 + ((np.mgrid[0:H, 0:W][0] - 300) / 46.0) ** 2 <= 1)
    cv.paint(pool, C("soil", 1))
    cv.paint(pool & ~sh(floor, 5, 5), C("soil", 2))
    cv.paint(pool & ((((np.mgrid[0:H, 0:W][1] - 130) / 90.0) ** 2 + ((np.mgrid[0:H, 0:W][0] - 300) / 26.0) ** 2) <= 1) & sh(floor, 5, 5), C("soil", 2))
    cv.paint(edge(floor) & pool, OUT)
    # basalt blocks banked against the drone and across the floor
    for cx, cy, r in ((350, 268, 16), (392, 266, 28), (444, 260, 26), (494, 252, 26), (542, 258, 22), (306, 280, 14),
                      (582, 282, 16), (260, 308, 12), (34, 328, 14), (472, 326, 16), (556, 334, 22),
                      (318, 338, 12), (400, 348, 14)):
        ch = poly(chunk(cx, cy, r, rnd))
        floor_cover |= ch
        rock_shape(cv, ch, ROCK, lit=3, dark=3)
    # warm rubble under and round the wreck
    for cx, cy, r in ((92, 302, 12), (132, 298, 10), (176, 302, 13), (64, 300, 9), (150, 336, 16), (214, 330, 11), (96, 340, 10)):
        rock_shape(cv, poly(chunk(cx, cy, r, rnd)), WARM, lit=3, dark=3)
    despeckle(cv, ~hole, passes=2)
    star(cv, 226, 22, True)
    # what's still the drone after the floor and blocks went over it
    shown = drone & ~edge(drone)
    keep = np.zeros_like(drone)
    for t in [C("rock", 1), C("rock", 2), C("rock", 3), C("rock", 4), C("cream", 4), C("cream", 0)]:
        keep |= np.all(cv.a == np.array(t, np.uint8), axis=2)
    veins = veins & shown & keep & ~floor_cover
    return cv, drone & ~floor_cover, veins


def drone_lit(drone, veins):
    """Over the cavern: the veins burning gold-violet and the lens open. Fades in and out in the scene."""
    cv = Canvas()
    glow = veins | (edge(veins | sh(veins, 1, 0)) & drone)
    cv.paint(sh(veins, 1, 1) & drone & ~veins, C("violet", 2))
    cv.paint(veins, C("brass", 3))
    core = veins & sh(veins, 1, 0) & sh(veins, 0, 1)
    cv.paint(core, C("brass", 4))
    draw_lens(cv, True)
    del glow
    return cv


def beam():
    """A cone of light from the lens to the wreck's canopy (about (150, 252) on the cavern)."""
    cv = Canvas()
    lx, ly = lens_center()
    tx, ty = 150, 250
    ang = math.atan2(ty - ly, tx - lx)
    px, py = -math.sin(ang), math.cos(ang)
    def cone(w0, w1):
        return poly([(lx + px * w0, ly + py * w0), (tx + px * w1, ty + py * w1), (tx - px * w1, ty - py * w1), (lx - px * w0, ly - py * w0)])
    cv.paint(cone(10, 46), C("violet", 2))
    cv.paint(cone(6, 30), C("violet", 3))
    cv.paint(cone(3, 14), C("violet", 4))
    cv.paint(cone(1, 5), C("cream", 4))
    return cv


GLYPH_COLS = (("brass", 3), ("violet", 4), ("violet", 3), ("brass", 4))


def glyph(cv, x, y, kind, r, col):
    c = C(*col)
    if kind == 0:      # a ring with a dot
        m = disc(x, y, r) & ~disc(x, y, r - 2)
        m |= disc(x, y, 2)
    elif kind == 1:    # a triangle
        m = lines([(x, y - r), (x + r * .87, y + r * .5), (x - r * .87, y + r * .5), (x, y - r)], 2)
    elif kind == 2:    # a four-point star
        m = poly([(x, y - r), (x + r * .25, y - r * .25), (x + r, y), (x + r * .25, y + r * .25), (x, y + r),
                  (x - r * .25, y + r * .25), (x - r, y), (x - r * .25, y - r * .25)])
    elif kind == 3:    # an arc with three beads
        m = disc(x, y, r) & ~disc(x, y, r - 2) & (np.mgrid[0:H, 0:W][0] < y)
        for k in (-1, 0, 1):
            m |= disc(x + k * r * .7, y + r * .5, 2)
    else:              # a diamond inside a diamond
        m = lines([(x, y - r), (x + r, y), (x, y + r), (x - r, y), (x, y - r)], 2)
        m |= poly([(x, y - r * .4), (x + r * .4, y), (x, y + r * .4), (x - r * .4, y)])
    cv.paint(m, c)


def glyphs():
    """The Precursor star-glyphs that swirl over the screen as the drone's beam washes over you."""
    cv = Canvas()
    rnd = random.Random(3)
    k = 0
    for ring, n, r0 in ((110, 9, 13), (170, 12, 10), (60, 6, 15)):
        for i in range(n):
            a = 2 * math.pi * i / n + ring * .01
            x = 320 + math.cos(a) * ring * 1.5
            y = 180 + math.sin(a) * ring * .82
            glyph(cv, x, y, k % 5, r0 + rnd.randint(-2, 2), GLYPH_COLS[k % 4])
            k += 1
    return cv


def glyph_mark():
    cv = Canvas(20, 20)
    m = poly([(10, 1), (12, 8), (19, 10), (12, 12), (10, 19), (8, 12), (1, 10), (8, 8)], 20, 20)
    cv.paint(m, C("violet", 3))
    cv.paint(poly([(10, 5), (11, 9), (15, 10), (11, 11), (10, 15), (9, 11), (5, 10), (9, 9)], 20, 20), C("brass", 4))
    cv.paint(edge(m), C("violet", 1))
    return cv


def fall_streak():
    """Your ship burning in: a white-hot head with a fire tail, up and left of it (48 x 20)."""
    cv = Canvas(48, 20)
    tail = poly([(0, 0), (6, 0), (44, 12), (40, 18), (34, 18)], 48, 20)
    cv.paint(tail, C("copper", 2))
    cv.paint(poly([(10, 2), (14, 2), (44, 13), (38, 16)], 48, 20), C("copper", 3))
    cv.paint(poly([(22, 7), (26, 7), (44, 13), (40, 15)], 48, 20), C("brass", 4))
    head = poly([(36, 11), (44, 10), (47, 14), (44, 18), (37, 17)], 48, 20)
    cv.paint(head, C("cream", 4))
    cv.paint(edge(head), C("copper", 1))
    return cv


def bolt(ramp):
    cv = Canvas(14, 4)
    cv.paint(poly([(0, 1), (13, 0), (13, 3), (0, 2)], 14, 4), C(ramp, 2))
    cv.paint(poly([(4, 1), (13, 1), (13, 2), (4, 2)], 14, 4), C(ramp, 4))
    return cv


def jump_streaks():
    """Light pulled into lines as the drive folds space: long bands across the screen."""
    cv = Canvas()
    rnd = random.Random(5)
    for _ in range(46):
        y = rnd.randint(4, H - 6)
        x0 = rnd.randint(-200, W - 60)
        ln = rnd.randint(60, 260)
        col = rnd.choice((("cream", 4), ("cream", 3), ("glow", 3), ("violet", 4)))
        th = rnd.choice((1, 2, 2, 3))
        cv.paint(poly([(x0, y), (x0 + ln, y), (x0 + ln, y + th), (x0, y + th)]), C(*col))
    return cv


def portrait():
    """The Mother-Drone in the talk box (128 x 128): its lens close up, veins burning out from it."""
    cv = Canvas(128, 128, fill=C("violet", 0))
    yy, xx = np.mgrid[0:128, 0:128].astype(float)
    shell = (xx - 64) ** 2 / 70 ** 2 + (yy - 70) ** 2 / 58 ** 2 <= 1
    nz = np.sqrt(np.clip(1 - (xx - 64) ** 2 / 70 ** 2 - (yy - 70) ** 2 / 58 ** 2, 0, 1))
    lum = -(xx - 64) / 70 * .5 - (yy - 70) / 58 * .55 + nz * .6
    tones = [C("rock", 1), C("rock", 2), C("rock", 3), C("rock", 4), C("cream", 4)]
    idx = np.digitize(lum, [.2, .42, .62, .86])
    for k, t in enumerate(tones):
        cv.paint(shell & (idx == k), t)
    rnd = random.Random(21)
    vm = np.zeros((128, 128), bool)
    for k in range(7):
        a = -2.6 + k * .62 + rnd.uniform(-.1, .1)
        x, y = 64.0, 66.0
        pts = []
        r = 30
        for _ in range(8):
            a += rnd.uniform(-.25, .25)
            pts.append((x + math.cos(a) * r, y + math.sin(a) * r * .85))
            r += 8
        vm |= lines(pts, 2, 128, 128)
    vm &= binary_erosion(shell, iterations=2)
    cv.paint(sh(vm, 1, 1) & shell & ~vm, C("violet", 2))
    cv.paint(vm, C("brass", 3))
    cv.paint(edge(shell), OUT)
    cx, cy = 64, 66
    rim = disc(cx, cy, 28, 128, 128)
    cv.paint(rim, C("rock", 2))
    cv.paint(rim & ~sh(rim, 4, 4), C("rock", 4))
    cv.paint(edge(rim), OUT)
    inner = disc(cx, cy, 21, 128, 128)
    cv.paint(inner, C("glow", 2))
    cv.paint(disc(cx - 2, cy - 2, 15, 128, 128), C("glow", 3))
    cv.paint(disc(cx - 2, cy - 2, 7, 128, 128), C("glow", 4))
    cv.paint(disc(cx, cy, 21, 128, 128) & ~disc(cx, cy, 18, 128, 128), C("violet", 3))
    cv.paint(edge(inner), OUT)
    cv.paint(disc(cx - 10, cy - 10, 3, 128, 128), C("cream", 4))
    despeckle(cv, shell & ~rim, passes=2)
    return cv


def check(cv, name):
    a = cv.a
    seen = {"%02x%02x%02x" % tuple(int(q) for q in p[:3]) for p in a.reshape(-1, 4) if p[3] > 0}
    bad = seen - ALLOWED
    assert not bad, (name, "colours off the palette", sorted(bad)[:8])


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cv, drone, veins = cavern()
    out = {
        "cavern": cv,
        "drone_lit": drone_lit(drone, veins),
        "beam": beam(),
        "glyphs": glyphs(),
        "glyph_mark": glyph_mark(),
        "fall_streak": fall_streak(),
        "bolt_green": bolt("leaf"),
        "bolt_teal": bolt("glow"),
        "jump_streaks": jump_streaks(),
    }
    for name, c in out.items():
        check(c, name)
        c.save(os.path.join(OUT_DIR, name + ".png"))
    p = portrait()
    check(p, "portrait")
    p.save(os.path.join(ROOT, "art", "portrait_motherdrone.png"))
    if "--preview" in sys.argv:
        im = Image.open(os.path.join(OUT_DIR, "cavern.png")).convert("RGBA")
        lit = im.copy()
        lit.alpha_composite(Image.open(os.path.join(OUT_DIR, "drone_lit.png")))
        b = Image.open(os.path.join(OUT_DIR, "beam.png"))
        b.putalpha(b.getchannel("A").point(lambda v: v * 170 // 255))
        lit.alpha_composite(b)
        sheet = Image.new("RGBA", (W, H * 2))
        sheet.paste(im, (0, 0))
        sheet.paste(lit, (0, H))
        sheet.save("/tmp/look/prologue_cavern.png")
        Image.open(os.path.join(ROOT, "art", "portrait_motherdrone.png")).resize((256, 256), 0).save("/tmp/look/portrait_md.png")
    print("wrote", ", ".join(out), "and portrait_motherdrone")


if __name__ == "__main__":
    main()
