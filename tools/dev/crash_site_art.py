"""The crash site's own props (24 Nov 2026, second pass at the prologue: Zachary, "the mother drone area doesnt fit
the art style ... the ship is again at a weird angle and kinda floating not crashed into rock").

The crash now plays in the game itself, on a cavern map built like the others (tools/crash_site.py), so the rock,
the walls and the light are the game's own. These are the two props that map needs, drawn as props are: seen from
the front with the top visible, lit from the top left, master palette only, a #5b332d outline, 3-5 shades a
material, on the 24-pixel grid (shown at two-thirds), no ground shadow painted in.

  crash_wreck.png       8 x 5 tiles (192 x 120): the front half of your ship (the in-world ship art's most broken
                        stage, art/lunar/player_ship.png frame 0), its back torn away, nose ploughed into a heap of
                        broken basalt, a scorched gouge behind it
  mother_drone.png      10 x 6 tiles (240 x 144): the Mother-Drone, a silver seed lying on its side, half sunk in
                        the cavern floor, its lens toward your ship, its veins dark
and its animation strips (same size, drawn over it by the prologue): mother_drone_wake.png (8 frames: the veins
light from the lens outwards and the lens opens), mother_drone_pulse.png (6 frames: light running along them), and
crash_beam.png (4 frames: the beam from the lens to your canopy, sized to the gap between the two props on the map).
Run: python3 tools/dev/crash_site_art.py [--preview]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import binary_erosion

sys.path.insert(0, os.path.dirname(__file__))
from prologue_art import C, Canvas, OUT, poly, lines, disc, sh, edge, check, despeckle, strip  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LUNAR = os.path.join(ROOT, "art", "lunar")
TILE = 24
# where the two props stand on the crash site map (tiles, top-left), so the beam can run between them;
# tools/crash_site.py reads these
WRECK_AT = (7, 12)
DRONE_AT = (25, 8)
WRECK_SIZE = (8, 5)
DRONE_SIZE = (10, 6)

ROCK = [C("rock", 0), C("rock", 1), C("rock", 2), C("rock", 3)]
BASALT = [C("violet", 0), C("rock", 0), C("rock", 1), C("rock", 2)]


def stone(cv, pts, ramp, rnd, light=(-1, -1)):
    """A chunky stone, prop-style: a mid tone, a lit top-left face, a dark bottom-right, a crack, an outline."""
    w, h = cv.w, cv.h
    m = poly(pts, w, h)
    cv.paint(m, ramp[1])
    cv.paint(m & ~sh(m, 4, 4), ramp[2])
    cv.paint(m & ~sh(m, 2, 2) & ~sh(m, 5, 5), ramp[3])
    cv.paint(m & ~sh(m, -4, -3), ramp[0])
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if max(xs) - min(xs) > 14:
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        cv.paint(lines([(cx - 4, cy - 2), (cx + 1, cy + 1), (cx + 3, cy + 5)], 1, w, h) & binary_erosion(m, iterations=2), ramp[0])
    cv.paint(edge(m), OUT)
    return m


def rock_pts(cx, cy, rx, ry, rnd, n=7):
    return [(cx + math.cos(2 * math.pi * k / n + rnd.uniform(-.2, .2)) * rx * rnd.uniform(.8, 1.05),
             cy + math.sin(2 * math.pi * k / n + rnd.uniform(-.2, .2)) * ry * rnd.uniform(.8, 1.05)) for k in range(n)]


# ---------------------------------------------------------------- the wreck
def crash_wreck():
    """Your ship's front half, nose-first in a heap of broken basalt, with the gouge it cut behind it."""
    rnd = random.Random(5)
    w, h = WRECK_SIZE[0] * TILE, WRECK_SIZE[1] * TILE
    cv = Canvas(w, h)
    # the gouge: scorched, broken floor where the hull slid in (flat, under everything)
    gouge = poly([(4, 84), (40, 74), (120, 72), (150, 80), (150, 104), (110, 112), (30, 108), (6, 100)], w, h)
    cv.paint(gouge, C("ink", 0))
    cv.paint(gouge & ~sh(gouge, 0, 3), C("soil", 1))
    for x0 in range(14, 140, 18):
        cv.paint(lines([(x0, 86 + rnd.randint(-3, 3)), (x0 + 12, 90 + rnd.randint(-3, 3))], 2, w, h) & gouge, C("rock", 0))
    # the ship: the in-world ship art's broken stage, its back half torn off along a ragged line
    ship = np.array(Image.open(os.path.join(LUNAR, "player_ship.png")).convert("RGBA"))[:, :168]
    sh_h, sh_w = ship.shape[:2]
    cut = np.array([62 + rnd.randint(-5, 5) + 5 * math.sin(y * .35) for y in range(sh_h)])
    keep = (np.arange(sh_w)[None, :] >= cut[:, None]) & (ship[:, :, 3] > 0)
    ox, oy = 2 - 52, 6                      # where the kept half lands on the prop: torn end at x 10, nose at 118
    part = Canvas(w, h)
    for y in range(sh_h):
        for x in range(sh_w):
            if keep[y, x]:
                X, Y = x + ox, y + oy
                if 0 <= X < w and 0 <= Y < h:
                    part.a[Y, X] = ship[y, x]
    pm = part.a[:, :, 3] > 0
    # the torn end: ripped plating, ribs, a hot edge
    torn = pm & ~sh(pm, 4, 0)
    part.paint(torn, C("rock", 1))
    part.paint(torn & ~sh(pm, 2, 0), C("copper", 2))
    for y in np.nonzero(torn.any(axis=1))[0][::8]:
        x = np.nonzero(torn[y])[0][0]
        part.paint(lines([(x, y), (x - 5, y + 1)], 2, w, h), C("rock", 2))
    # burns and soot over the hull
    for cx, cy, r in ((34, 40, 6), (58, 66, 5), (24, 70, 5)):
        burn = disc(cx, cy, r, w, h) & pm & ~torn
        part.paint(burn, C("ink", 2))
        part.paint(burn & disc(cx + 1, cy + 1, r - 2, w, h), C("ink", 0))
    cv.a[pm] = part.a[pm]
    # the heap the nose ploughed into: broken basalt piled over it, in front and to the right
    for cx, cy, rx, ry in ((128, 70, 22, 16), (150, 84, 20, 15), (122, 96, 18, 12), (164, 62, 16, 12),
                           (176, 92, 14, 11), (104, 108, 16, 10), (140, 106, 15, 10), (186, 74, 10, 9)):
        stone(cv, rock_pts(cx, cy, rx, ry, rnd), BASALT if rnd.random() < .5 else ROCK, rnd)
    # loose chips and a bent strut from the hull
    for cx, cy, r in ((70, 104, 6), (90, 112, 5), (40, 110, 5), (16, 96, 4)):
        stone(cv, rock_pts(cx, cy, r, r * .7, rnd, 5), ROCK, rnd)
    strut = lines([(14, 58), (2, 66), (6, 74)], 3, w, h)
    cv.paint(strut, C("rock", 2))
    cv.paint(edge(strut), OUT)
    # (no palette check: the hull is the artist's own ship art, which has its own colours)
    return cv


# ---------------------------------------------------------------- the Mother-Drone
DW, DH = DRONE_SIZE[0] * TILE, DRONE_SIZE[1] * TILE
SEED = dict(cx=124.0, cy=70.0, a=104.0, b=46.0)          # the body, before the ground cuts it
GROUND = 104                                             # the floor line across its lower part
LENS = (40, 64, 13)                                      # the lens, on the end toward your ship


def seed_field():
    yy, xx = np.mgrid[0:DH, 0:DW].astype(float)
    u = (xx + .5 - SEED["cx"]) / SEED["a"]
    v = (yy + .5 - SEED["cy"]) / SEED["b"]
    half = np.clip(1 - u * u, 0, None) ** .55 * (1 - .18 * np.clip(u, 0, None))
    return (np.abs(u) <= 1) & (np.abs(v) <= half), u, v, half


def mother_drone():
    rnd = random.Random(13)
    cv = Canvas(DW, DH)
    m, u, v, half = seed_field()
    yy, xx = np.mgrid[0:DH, 0:DW]
    m &= yy < GROUND + 4 + (np.sin(xx * .18) * 2).astype(int)
    vn = np.where(half > 0, v / np.maximum(half, 1e-3), 0)
    nz = np.sqrt(np.clip(1 - u * u * .45 - vn * vn, 0, 1))
    L = np.array([-.45, -.7, .55])
    L /= np.linalg.norm(L)
    dot = np.clip(u * .55 * L[0] + vn * L[1] + nz * L[2], 0, 1)
    tones = [C("rock", 1), C("rock", 2), C("rock", 3), C("rock", 4), C("cream", 4)]
    idx = np.digitize(dot, [.35, .55, .74, .9])
    for k, t in enumerate(tones):
        cv.paint(m & (idx == k), t)
    # a long glint along its back, a faint violet underside, its seams
    cv.paint(m & (dot > .95) & (vn < -.2), C("cream", 4))
    cv.paint(m & (yy > GROUND - 12), C("rock", 1))                       # in the shadow of the ground
    cv.paint(m & (yy > GROUND - 5), C("rock", 0))
    cv.paint(m & (vn > .82) & (yy <= GROUND - 12), C("violet", 1))        # a thin violet rim underneath
    seam = m & ((np.abs(vn + .15) < .05) | (np.abs(u - .1) < .012) | (np.abs(u - .55) < .012) | (np.abs(u + .35) < .012))
    darker = {tones[i]: tones[max(0, i - 1)] for i in range(len(tones))}
    darker[C("violet", 1)] = C("violet", 0)
    ys, xs = np.nonzero(seam & ~edge(m))
    for y, x in zip(ys, xs):
        t = tuple(int(q) for q in cv.a[y, x])
        cv.a[y, x] = darker.get(t, t)
    cv.paint(edge(m), OUT)
    # the lens, dark and shut
    draw_lens(cv, 0)
    # the dark veins
    veins = vein_mask(m)
    cv.paint(veins, C("rock", 1))
    # the floor it's sunk in: basalt slabs heaped round its waist, cracks running out from it
    for cx, cy, rx, ry in ((40, 104, 20, 12), (74, 108, 24, 13), (112, 110, 26, 13), (152, 108, 24, 12),
                           (190, 104, 22, 12), (222, 96, 14, 10), (18, 96, 12, 9), (96, 128, 14, 8),
                           (150, 130, 16, 8), (204, 122, 14, 8), (56, 126, 12, 7),
                           (92, 100, 14, 9), (132, 100, 14, 9), (172, 98, 13, 9)):
        stone(cv, rock_pts(cx, cy, rx, ry, rnd), BASALT if rnd.random() < .6 else ROCK, rnd)
    check(cv, "mother_drone")
    return cv, m, veins


def draw_lens(cv, frame):
    x, y, r = LENS
    rim = disc(x, y, r, DW, DH)
    cv.paint(rim, C("rock", 2))
    cv.paint(rim & ~sh(rim, 2, 2), C("rock", 4))
    cv.paint(rim & ~sh(rim, -2, -2), C("rock", 1))
    cv.paint(edge(rim), OUT)
    inner = disc(x, y, r - 4, DW, DH)
    cv.paint(inner, C("violet", 0))
    if frame > 0:
        o = 1 + frame * 1.6
        cv.paint(disc(x, y, min(r - 5, o + 1), DW, DH), C("glow", 1))
        cv.paint(disc(x, y, min(r - 6, o), DW, DH), C("glow", 2))
        if frame >= 3:
            cv.paint(disc(x - 1, y - 1, max(1, o - 3), DW, DH), C("glow", 3))
        if frame >= 5:
            cv.paint(disc(x - 1, y - 1, 2, DW, DH), C("glow", 4))
    cv.paint(inner & ~disc(x, y, r - 6, DW, DH), C("violet", 2) if frame else C("violet", 1))
    cv.paint(disc(x - 4, y - 4, 1.5, DW, DH), C("cream", 4) if frame >= 3 else C("violet", 2))
    cv.paint(edge(inner), OUT)


def vein_paths():
    rnd = random.Random(11)
    out = []
    x0, y0, _ = LENS
    for head in (-.55, .0, .5):
        x, y, a = x0 + 12, y0 + head * 10, head * .5
        pts = [(x, y)]
        for step in range(20):
            a += rnd.uniform(-.16, .16) - .05 * (y - y0 - head * 18) / 10
            x += math.cos(a) * 9
            y += math.sin(a) * 4
            pts.append((x, y))
            if step in (6, 13):
                bx, by, ba = x, y, a + rnd.choice((-1, 1)) * .9
                br = [(bx, by)]
                for _ in range(5):
                    ba += rnd.uniform(-.3, .3)
                    bx += math.cos(ba) * 7
                    by += math.sin(ba) * 5
                    br.append((bx, by))
                out.append(br)
        out.append(pts)
    return out


def vein_mask(body):
    m = np.zeros((DH, DW), bool)
    for p in vein_paths():
        m |= lines(p, 2, DW, DH)
    return m & binary_erosion(body, iterations=3) & ~disc(LENS[0], LENS[1], LENS[2] + 1, DW, DH)


def vein_dist(veins):
    """Each vein pixel's distance along the veins from the lens, for the wake."""
    d = np.full((DH, DW), 1e9)
    for p in vein_paths():
        run = math.hypot(p[0][0] - LENS[0], p[0][1] - LENS[1])
        for a, b in zip(p, p[1:]):
            seg = lines([a, b], 2, DW, DH)
            run += math.hypot(b[0] - a[0], b[1] - a[1])
            d[seg] = np.minimum(d[seg], run)
    return np.where(veins, d, 0)


def drone_strips(body, veins):
    dist = vein_dist(veins)
    far = dist[veins].max()
    glow = sh(veins, 1, 1) & binary_erosion(body, iterations=2) & ~veins
    wake, pulse = [], []
    for f in range(8):
        cv = Canvas(DW, DH)
        lit = veins & (dist <= far * (f + 1) / 8)
        cv.paint(glow & sh(lit, 1, 1), C("violet", 2))
        cv.paint(lit, C("brass", 3))
        cv.paint(veins & (dist > far * f / 8) & (dist <= far * (f + 1) / 8), C("brass", 4))
        draw_lens(cv, min(5, f))
        wake.append(cv)
    for f in range(6):
        cv = Canvas(DW, DH)
        band = veins & ((dist / far * 3 - f / 6) % 1 < .22)
        cv.paint(glow, C("violet", 2))
        cv.paint(veins, C("brass", 3))
        cv.paint(band, C("brass", 4))
        cv.paint(glow & sh(band, 1, 1), C("violet", 3))
        draw_lens(cv, 5)
        pulse.append(cv)
    return strip(wake), strip(pulse)


def beam():
    """The beam from the lens to your canopy, in map art pixels (24 to a tile), 4 frames. Returns the strip and the
    tile (x, y) of its top-left corner."""
    lx = DRONE_AT[0] * TILE + LENS[0]
    ly = DRONE_AT[1] * TILE + LENS[1]
    tx = WRECK_AT[0] * TILE + 96               # the canopy, on the wreck prop
    ty = WRECK_AT[1] * TILE + 44
    x0, y0 = int(min(lx, tx) // TILE) - 1, int(min(ly, ty) // TILE) - 2
    x1, y1 = int(max(lx, tx) // TILE) + 2, int(max(ly, ty) // TILE) + 3
    w, h = (x1 - x0) * TILE, (y1 - y0) * TILE
    lx, ly, tx, ty = lx - x0 * TILE, ly - y0 * TILE, tx - x0 * TILE, ty - y0 * TILE
    ang = math.atan2(ty - ly, tx - lx)
    px, py = -math.sin(ang), math.cos(ang)
    length = math.hypot(tx - lx, ty - ly)
    yy, xx = np.mgrid[0:h, 0:w]
    along = ((xx - lx) * math.cos(ang) + (yy - ly) * math.sin(ang)) / length

    def cone(w0, w1):
        return poly([(lx + px * w0, ly + py * w0), (tx + px * w1, ty + py * w1), (tx - px * w1, ty - py * w1),
                     (lx - px * w0, ly - py * w0)], w, h)
    frames = []
    for f in range(4):
        cv = Canvas(w, h)
        wob = (0, 2, 3, 1)[f]
        outer = cone(6, 30 + wob)
        cv.paint(outer, C("violet", 2))
        cv.paint(cone(4, 18 + wob), C("violet", 3))
        cv.paint(cone(2, 8), C("violet", 4))
        cv.paint(cone(1, 3), C("cream", 4))
        cv.paint(outer & (((along * 6 - f / 4) % 1) < .18) & ~cone(2, 8), C("violet", 4))
        frames.append(cv)
    return strip(frames), (x0, y0)


def main():
    wreck = crash_wreck()
    wreck.save(os.path.join(LUNAR, "crash_wreck.png"))
    drone, body, veins = mother_drone()
    drone.save(os.path.join(LUNAR, "mother_drone.png"))
    wake, pulse = drone_strips(body, veins)
    b, at = beam()
    out = {"mother_drone_wake": wake, "mother_drone_pulse": pulse, "crash_beam": b}
    os.makedirs(os.path.join(ROOT, "art", "prologue"), exist_ok=True)
    for name, cv in out.items():
        check(cv, name)
        cv.save(os.path.join(ROOT, "art", "prologue", name + ".png"))
    print("beam at tile", at, "size", b.w // 4, b.h)
    if "--preview" in sys.argv:
        s = Image.new("RGBA", (DW * 2 + 20, DH + 130), (60, 56, 80, 255))
        s.alpha_composite(wreck.image(), (0, 0))
        s.alpha_composite(drone.image(), (DW + 20, 0))
        lit = drone.image()
        lit.alpha_composite(Image.open(os.path.join(ROOT, "art", "prologue", "mother_drone_pulse.png")).crop((0, 0, DW, DH)))
        s.alpha_composite(lit, (DW + 20, 0) if False else (0, 124))
        s.resize((s.width * 2, s.height * 2), Image.NEAREST).save("/tmp/look/crash_props.png")


if __name__ == "__main__":
    main()
