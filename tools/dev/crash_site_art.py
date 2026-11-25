"""The crash site's own props and overlays (24 Nov 2026; third pass at the prologue, Zachary: "still needs more
detail and quality, you can make the fighter look like the main menu still").

The crash plays in the game itself, on a cavern map built like the others (tools/crash_site.py), so the rock, the
walls and the light are the game's own. Props are drawn as props are: seen from the front with the top visible, lit
from the top left, a #5b332d outline, 3-5 shades a material, on the 24-pixel grid (shown at two-thirds), no ground
shadow painted in. The fighter and her scrap keep the main menu's own colours and outline (title/scene/fighter.png).

  crash_wreck.png       11 x 7 tiles: your fighter's front half as the main menu draws her, redrawn at three times
                        the size (Scale3x, lines back to one pixel), torn across the body, scorched back from the
                        tear, ribs and wires bared, a crack across the canopy, nose buried in a heap of basalt, rubble
                        along her belly, the gouge she cut and the scrap she shed behind her
  mother_drone.png      13 x 8 tiles: the Mother-Drone, a silver seed lying on its side, half sunk in the floor: raised
                        ribs round it, a channel of engraved glyphs along its side, an aperture lens toward your ship,
                        dark veins, violet crystal grown out of the cracks in its shell and a crown of it where the tail
                        broke open, cracks in the floor round it with violet light in them
  wreck_plate.png, wreck_wing.png    scrap from your fighter, flat on the floor;  rock_chips.png: broken basalt
and the strips and overlays the prologue lays over the map (art/prologue/): mother_drone_wake.png (8 frames: the
veins light from the lens outwards, the blades turn and the iris opens, the crystals catch the light last),
mother_drone_pulse.png (6 frames: light running along the veins, the crystals shimmering in turn, the blades turning),
crash_beam.png (4 frames, lens to canopy), light_shaft.png and motes.png (the cool light through the hole you made,
with dust turning in it; drawn as light), grit.png (grit trickling from the broken roof), drone_glow.png (the violet
light on the floor round the drone when it wakes; drawn as light).
Run: python3 tools/dev/crash_site_art.py
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
WRECK_AT = (5, 10)
DRONE_AT = (24, 8)
WRECK_SIZE = (11, 7)
DRONE_SIZE = (13, 8)

ROCK = [C("rock", 0), C("rock", 1), C("rock", 2), C("rock", 3)]
BASALT = [C("violet", 0), C("rock", 0), C("rock", 1), C("rock", 2)]
MOONROCK = [C("soil", 0), C("soil", 1), C("soil", 2), C("soil", 3)]      # the cavern's own warm grey-brown rock


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
CANOPY = [143.0, 80.0]                         # the canopy's middle on the wreck prop (set when it's drawn)
TEAR = [98.0, 113.0]                           # the middle of her torn end on the prop (set when it's drawn)
# her front half lying in the rubble: nose up and to the right as in the panels, dipped into the rock and listing,
# from the game's own angle, three and a half times the panels' model scale (tools/dev/fighter_model.py)
WRECK_VIEW = dict(scale=3.5, roll=.45, pitch=-.2, yaw=math.radians(33), elev=math.radians(58), dx=-23, dy=23)


def crash_wreck():
    """Your fighter's front half (the model in tools/dev/fighter_model.py, torn where the blind jump tore her),
    nose buried in a heap of broken rock, her torn end toward you, scorched and glowing, wires hanging out of it, the
    canopy cracked, a gouge behind her and scrap thrown about."""
    rnd = random.Random(5)
    w, h = WRECK_SIZE[0] * TILE, WRECK_SIZE[1] * TILE
    cv = Canvas(w, h)
    # the gouge she cut coming in from the lower left: churned, scorched floor (flat, under everything)
    gouge = poly([(0, 140), (20, 126), (50, 116), (80, 108), (100, 112), (102, 140), (72, 156), (36, 164), (0, 166)], w, h)
    cv.paint(gouge, C("soil", 0))                                       # its far wall, in shadow
    cv.paint(gouge & ~sh(gouge, 0, 3), C("soil", 1))                     # churned rock
    cv.paint(gouge & ~sh(gouge, 0, -3) & sh(gouge, 0, 3), C("soil", 2))  # the near lip, catching the light
    scorch = lines([(2, 152), (40, 140), (70, 130), (96, 124)], 4, w, h) & gouge & ~edge(gouge)
    cv.paint(scorch, C("ink", 0))
    for x0 in range(4, 96, 12):
        y0 = 150 - x0 * .3 + rnd.randint(-4, 4)
        cv.paint(lines([(x0, y0), (x0 + 7, y0 - 2)], 2, w, h) & gouge & ~scorch, C("soil", 0))
    # the ship (tools/dev/fighter_model.py): her front half as she was torn off in the jump, battered, lying where she
    # ploughed in, nose down and listing, seen from the game's own angle
    import fighter_model
    view = dict(WRECK_VIEW, size=(w, h))
    ship, info = fighter_model.render(view, dict(fighter_model.BATTERED_MODE, cut=(-3.0, "front"), scorch=True),
                                      nozzle_glow=False)
    pm = ship.a[:, :, 3] > 0
    mat = info["mat"]
    nose = info["nose"]
    # stones behind her nose (drawn first)
    for cx, cy, rx, ry in ((nose[0] + 6, nose[1] - 14, 14, 11), (nose[0] + 30, nose[1] - 4, 13, 10),
                           (nose[0] - 16, nose[1] - 10, 10, 8), (nose[0] + 44, nose[1] + 16, 10, 8)):
        stone(cv, rock_pts(cx, cy, rx, ry, rnd), MOONROCK if rnd.random() < .7 else BASALT, rnd)
    torn = mat == "torn"
    hull = np.isin(mat, ["hull", "stripe"])
    hot = torn & (sh(hull, 1, 0) | sh(hull, -1, 0) | sh(hull, 0, 1) | sh(hull, 0, -1)) & ~edge(pm)
    ship.paint(hot, C("copper", 3))                                  # the tear, still glowing
    ship.paint(hot & ~sh(hot, 1, 1), C("brass", 4))
    ty, tx = np.nonzero(torn)
    TEAR[:] = [float(tx.mean()), float(ty.mean())] if len(tx) else TEAR
    # wires hanging out of the tear
    for k, col in enumerate((C("copper", 2), C("teal", 2), C("berry", 2))):
        x0, y0 = TEAR[0] - 4 + k * 5, TEAR[1] - 2 + k * 4
        wire = lines([(x0, y0), (x0 - 6, y0 + 7 + k), (x0 - 9, y0 + 15 + k * 2)], 1, w, h) & ~pm
        cv.paint(wire, col)
    # a crack across the canopy
    glass = mat == "glass"
    gy, gx = np.nonzero(glass)
    if len(gx):
        cx0, cy0 = gx.mean(), gy.mean()
        crack = lines([(cx0 - 10, cy0 - 3), (cx0 - 2, cy0 + 1), (cx0 + 2, cy0 + 6), (cx0 + 9, cy0 + 8)], 1, w, h)
        crack |= lines([(cx0 - 2, cy0 + 1), (cx0 + 7, cy0 - 5)], 1, w, h)
        ship.paint(crack & glass & ~edge(glass), C("teal", 4))
        CANOPY[:] = [float(cx0), float(cy0)]
    shadow = sh(pm, 3, 5) & ~pm                  # where she lies on the floor: a dark contact shadow
    cv.paint(shadow, C("rock", 0))
    cv.a[pm] = ship.a[pm]
    # the heap her nose ploughed into, piled over the tip, and rubble along her belly so she sits in the rock
    nx, ny = nose
    for cx, cy, rx, ry in ((nx + 30, ny - 6, 12, 9), (nx + 44, ny + 14, 9, 8), (nx + 4, ny + 2, 19, 14),
                           (nx + 26, ny + 12, 18, 13), (nx - 10, ny + 22, 13, 9), (nx + 12, ny + 30, 19, 13),
                           (nx + 40, ny + 34, 14, 10)):
        stone(cv, rock_pts(cx, cy, rx, ry, rnd), MOONROCK if rnd.random() < .7 else BASALT, rnd)
    for k, x in enumerate(range(int(TEAR[0]) + 6, int(TEAR[0]) + 62, 11)):   # rubble along her belly: she sits in the rock
        col = np.nonzero(pm[:, x])[0]
        if not len(col):
            continue
        r = (6, 8, 7, 9, 6, 8)[k % 6]
        stone(cv, rock_pts(x + 2, col.max() + 1, r * 1.4, r * .85, rnd, 6), MOONROCK if rnd.random() < .75 else BASALT, rnd)
    # scrap she shed, flat in the gouge: a torn hull plate with its orange stripe, a bent fin, a canopy shard
    plate = poly([(26, 142), (46, 134), (54, 144), (34, 152)], w, h)
    cv.paint(plate, C("cream", 2))
    cv.paint(plate & ~sh(plate, 0, 2), C("cream", 3))
    cv.paint(plate & lines([(30, 145), (50, 138)], 3, w, h), C("copper", 3))
    cv.paint(edge(plate), OUT)
    fin = poly([(60, 156), (76, 148), (82, 152), (68, 162)], w, h)
    cv.paint(fin, C("cream", 1))
    cv.paint(fin & ~sh(fin, 1, 2), C("cream", 2))
    cv.paint(edge(fin), OUT)
    shard = poly([(10, 156), (18, 152), (16, 160)], w, h)
    cv.paint(shard, C("teal", 2))
    cv.paint(shard & ~sh(shard, 1, 1), C("teal", 4))
    cv.paint(edge(shard), OUT)
    check(cv, "crash_wreck")
    return cv


# ---------------------------------------------------------------- the Mother-Drone
DW, DH = DRONE_SIZE[0] * TILE, DRONE_SIZE[1] * TILE
SEED = dict(cx=170.0, cy=86.0, a=128.0, b=54.0)          # the body, before the ground cuts it
GROUND = 128                                             # the floor line across its lower part
LENS = (58, 84, 17)                                      # the lens, on the blunt end toward your ship
RIBS = (-.56, -.27, .02, .3, .55)                        # raised bands round the body (u, along its length)
# violet growths out of the cracks, and a crown of them where the tail broke open: x, y, width, length, lean
CRYSTALS = ((224, 48, 8, 18, -.9), (236, 42, 12, 32, -.4), (250, 50, 9, 24, .15), (262, 60, 8, 18, .6),
            (130, 36, 7, 17, -.3), (142, 40, 5, 11, .4),
            (284, 78, 11, 30, .2), (294, 88, 10, 26, .7), (274, 84, 8, 20, -.4), (298, 100, 8, 18, 1.1), (286, 104, 7, 14, .5))
GLYPHS = ((1, 0, 1, 1, 1, 1), (1, 1, 0, 1, 0, 1), (0, 1, 1, 1, 1, 0), (1, 1, 1, 0, 1, 0), (1, 0, 0, 1, 1, 1), (0, 1, 0, 1, 1, 1))


def seed_field():
    yy, xx = np.mgrid[0:DH, 0:DW].astype(float)
    u = (xx + .5 - SEED["cx"]) / SEED["a"]
    v = (yy + .5 - SEED["cy"]) / SEED["b"]
    # blunt at the lens end, drawn out to a point at the tail
    half = np.clip(1 - u * u, 0, None) ** np.where(u < 0, .42, .62) * (1 - .3 * np.clip(u, 0, None))
    return (np.abs(u) <= 1) & (np.abs(v) <= half), u, v, half


def crystal(cv, x, y, w, ln, lean, glow=0):
    """A violet crystal shard growing up out of the shell, prop-style: lit face, dark face, a glint."""
    tip = (x + lean * ln * .6, y - ln)
    pts = [(x - w / 2, y), (x - w / 2 + 1, y - ln * .7), tip, (x + w / 2, y - ln * .72), (x + w / 2, y)]
    m = poly(pts, cv.w, cv.h)
    left = poly([(x - w / 2, y), (x - w / 2 + 1, y - ln * .7), tip, (x + lean * 2, y)], cv.w, cv.h) & m
    base = [C("violet", 1), C("violet", 2), C("violet", 3)] if glow == 0 else [C("violet", 2), C("violet", 3), C("violet", 4)]
    cv.paint(m, base[0])
    cv.paint(left, base[1])
    cv.paint(left & ~sh(left, 2, 0), base[2])
    cv.paint(lines([(x + lean * 2, y - 2), tip], 1, cv.w, cv.h) & m, base[2] if glow == 0 else C("cream", 4))
    cv.paint(edge(m), OUT)
    return m


def mother_drone():
    rnd = random.Random(13)
    cv = Canvas(DW, DH)
    yy, xx = np.mgrid[0:DH, 0:DW]
    # the floor round it, under everything: cracks running out from where it struck, a faint violet light in them
    for k in range(9):
        a = math.pi * (.05 + k * .11) + rnd.uniform(-.06, .06)
        x0, y0 = SEED["cx"] + math.cos(a) * 100, GROUND + 6 + math.sin(a) * 18
        pts = [(x0, y0)]
        for _ in range(4):
            a += rnd.uniform(-.35, .35)
            x0 += math.cos(a) * 14
            y0 += abs(math.sin(a)) * 9 + 3
            pts.append((x0, y0))
        crk = lines(pts, 2, DW, DH)
        cv.paint(crk, C("ink", 0))
        cv.paint(crk & ~sh(crk, 0, 1), C("violet", 1))
    m, u, v, half = seed_field()
    m &= yy < GROUND + 4 + (np.sin(xx * .18) * 2).astype(int)
    vn = np.where(half > 0, v / np.maximum(half, 1e-3), 0)
    nz = np.sqrt(np.clip(1 - u * u * .45 - vn * vn, 0, 1))
    L = np.array([-.45, -.7, .55])
    L /= np.linalg.norm(L)
    dot = np.clip(u * .55 * L[0] + vn * L[1] + nz * L[2], 0, 1)
    tones = [C("rock", 1), C("rock", 2), C("rock", 3), C("rock", 4), C("cream", 4)]
    idx = np.digitize(dot, [.35, .55, .74, .94])
    # raised ribs round the body: a band a tone lighter, its far side a tone darker (a bevel)
    for r0 in RIBS:
        core = np.abs(u - r0) < .022
        far = (u - r0 >= .022) & (u - r0 < .034)
        near = (r0 - u >= .022) & (r0 - u < .03)
        idx = np.where(m & core, np.minimum(idx + 1, 4), idx)
        idx = np.where(m & far, np.maximum(idx - 2, 0), idx)
        idx = np.where(m & near, np.maximum(idx - 1, 0), idx)
    # the glyph band: a sunken channel along its side between the ribs
    band = m & (vn > -.02) & (vn < .2)
    edges_ = [-1] + list(RIBS) + [1]
    between = np.zeros_like(m)
    for lo, hi in zip(edges_, edges_[1:]):
        between |= (u > lo + .04) & (u < hi - .04)
    chan = band & between
    idx = np.where(chan, np.maximum(idx - 1, 0), idx)
    for k, t in enumerate(tones):
        cv.paint(m & (idx == k), t)
    cv.paint(m & (dot > .9) & (dot <= .94) & (vn < -.45) & (vn > -.6) & ~chan, C("cream", 4))   # a glint along its back
    cv.paint(chan & sh(chan, 0, 1) & ~sh(chan, 0, 2), C("rock", 1))     # the channel's top lip in shadow
    cv.paint(m & (yy > GROUND - 14), C("rock", 1))                       # in the shadow of the ground
    cv.paint(m & (yy > GROUND - 6), C("rock", 0))
    cv.paint(m & (vn > .8) & (yy <= GROUND - 14), C("violet", 1))        # violet light from below, on its belly
    # engraved glyphs in the channel, in rows like writing
    ys_c, xs_c = np.nonzero(chan)
    if len(xs_c):
        for gx in range(int(xs_c.min()) + 3, int(xs_c.max()) - 3, 7):
            col = chan[:, gx]
            if not col.any():
                continue
            gy = int(np.nonzero(col)[0].mean()) - 2
            g = GLYPHS[(gx // 7) % len(GLYPHS)]
            for i, on in enumerate(g):
                if on:
                    px, py = gx + (i % 2) * 2, gy + (i // 2) * 2
                    if chan[py:py + 2, px:px + 2].all():
                        cv.a[py:py + 2, px:px + 2] = C("rock", 4)
    # its seams
    seam = m & ((np.abs(vn + .2) < .04) & ~between)
    cv.paint(seam & ~edge(m), C("rock", 1))
    cv.paint(edge(m), OUT)
    # cracks across the top of the shell, and the crystals that have grown out of them
    for pts in (((214, 40), (226, 46), (238, 44), (252, 54), (266, 60)), ((226, 46), (230, 58), (222, 66)),
                ((238, 44), (246, 34)), ((126, 36), (136, 40), (148, 38))):
        crk = lines(pts, 1, DW, DH) & binary_erosion(m, iterations=2)
        cv.paint(sh(crk, 0, 1) & m & ~crk, C("rock", 4))
        cv.paint(crk, OUT)
    hollow = disc(286, 96, 13, DW, DH) & m
    cv.paint(hollow, C("violet", 0))
    cv.paint(hollow & ~sh(hollow, -2, -2), C("violet", 1))
    cv.paint(edge(hollow), OUT)
    for x, y, w_, ln, lean in CRYSTALS:
        crystal(cv, x, y, w_, ln, lean)
    # the lens, dark and shut
    draw_lens(cv, 0)
    # the dark veins
    veins = vein_mask(m)
    cv.paint(veins, C("rock", 1))
    # the floor it's sunk in: basalt slabs heaped round its waist
    for cx, cy, rx, ry in ((54, 126, 20, 12), (88, 132, 24, 13), (128, 136, 26, 13), (170, 136, 24, 12),
                           (212, 132, 24, 12), (252, 124, 20, 11), (284, 114, 14, 10), (30, 116, 12, 9),
                           (110, 156, 14, 8), (168, 160, 16, 8), (232, 152, 14, 8), (70, 152, 12, 7),
                           (106, 124, 14, 9), (150, 126, 14, 9), (192, 124, 13, 9), (234, 120, 13, 9), (292, 136, 9, 7)):
        stone(cv, rock_pts(cx, cy, rx, ry, rnd), BASALT if rnd.random() < .6 else ROCK, rnd)
    for x, y, w_, ln, lean in ((22, 132, 6, 14, -.4), (30, 134, 4, 9, .3), (290, 128, 6, 15, .4), (282, 132, 4, 9, -.2),
                               (196, 164, 5, 11, .2)):
        crystal(cv, x, y, w_, ln, lean)
    check(cv, "mother_drone")
    return cv, m, veins


def draw_lens(cv, frame, spin=None):
    """The lens: a bevelled rim, a ring of eight aperture blades, the iris (dark and shut at frame 0, opening and
    lighting as the frames go)."""
    x, y, r = LENS
    yy, xx = np.mgrid[0:DH, 0:DW]
    rim = disc(x, y, r, DW, DH)
    cv.paint(rim, C("rock", 2))
    cv.paint(rim & ~sh(rim, 2, 2), C("rock", 4))
    cv.paint(rim & ~sh(rim, -2, -2), C("rock", 1))
    cv.paint(edge(rim), OUT)
    ring = disc(x, y, r - 3, DW, DH)
    ang = (np.arctan2(yy + .5 - y, xx + .5 - x) + math.pi + (frame if spin is None else spin) * .12) % (math.pi / 4)
    cv.paint(ring, C("rock", 3))
    cv.paint(ring & (ang > math.pi / 8), C("rock", 2))
    cv.paint(ring & (ang < .09), OUT)
    open_r = r - 8 + min(frame, 5) * .6
    inner = disc(x, y, open_r, DW, DH)
    cv.paint(inner, C("violet", 0))
    if frame > 0:
        o = 1 + frame * 1.5
        cv.paint(disc(x, y, min(open_r - 1, o + 1), DW, DH), C("glow", 1))
        cv.paint(disc(x, y, min(open_r - 2, o), DW, DH), C("glow", 2))
        if frame >= 3:
            cv.paint(disc(x - 1, y - 1, max(1, o - 3), DW, DH), C("glow", 3))
        if frame >= 5:
            cv.paint(disc(x - 1, y - 1, 2.5, DW, DH), C("glow", 4))
    cv.paint(inner & ~disc(x, y, open_r - 2, DW, DH), C("violet", 2) if frame else C("violet", 1))
    cv.paint(disc(x - 4, y - 4, 1.5, DW, DH), C("cream", 4) if frame >= 3 else C("violet", 2))
    cv.paint(edge(inner), OUT)


def vein_paths():
    rnd = random.Random(11)
    out = []
    x0, y0, _ = LENS
    for head in (-.7, -.3, .5):
        x, y, a = x0 + LENS[2] - 4, y0 + head * 14, head * .5
        pts = [(x, y)]
        for step in range(20):
            a += rnd.uniform(-.16, .16) - .05 * (y - y0 - head * 26) / 10
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
        if f >= 5:                                    # the light reaches the crystals last
            for k, (x, y, w_, ln, lean) in enumerate(CRYSTALS):
                if k % 3 <= f - 5:
                    crystal(cv, x, y, w_, ln, lean, glow=1)
        draw_lens(cv, min(5, f), spin=f)
        wake.append(cv)
    for f in range(6):
        cv = Canvas(DW, DH)
        band = veins & ((dist / far * 3 - f / 6) % 1 < .22)
        cv.paint(glow, C("violet", 2))
        cv.paint(veins, C("brass", 3))
        cv.paint(band, C("brass", 4))
        cv.paint(glow & sh(band, 1, 1), C("violet", 3))
        for k, (x, y, w_, ln, lean) in enumerate(CRYSTALS):     # the crystals shimmer in turn
            if (k + f) % 3:
                crystal(cv, x, y, w_, ln, lean, glow=1)
        draw_lens(cv, 5, spin=7 + f * (math.pi / 4 / 6 / .12))   # the blades turn, a full step in six frames
        pulse.append(cv)
    return strip(wake), strip(pulse)


def beam():
    """The beam from the lens to your canopy, in map art pixels (24 to a tile), 4 frames. Returns the strip and the
    tile (x, y) of its top-left corner."""
    lx = DRONE_AT[0] * TILE + LENS[0]
    ly = DRONE_AT[1] * TILE + LENS[1]
    tx = WRECK_AT[0] * TILE + CANOPY[0]        # the canopy, on the wreck prop
    ty = WRECK_AT[1] * TILE + CANOPY[1]
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


# ---------------------------------------------------------------- what the prologue lays over the map
# (world sprites: art pixels, shown at two-thirds like the props; "add" ones are light, added to what's under them,
# so they're drawn dark: a dark blue adds a little cool light)
SHAFT_AT = (7.5, 1.0)                    # tiles: the light from the hole you came through, falling on the wreck


def light_shaft():
    """Cool light falling through the hole in the roof onto your wreck: a slanted column in three soft steps,
    ending in a pool on the floor round the ship (7 x 14 tiles, additive: dark colours add a little light)."""
    w, h = 7 * TILE, 14 * TILE
    cv = Canvas(w, h)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    top_c, bot_c = 70.0, 90.0                         # its middle at the top and at the floor (it slants a little)
    floor_y = h - 40
    t = np.clip(yy / floor_y, 0, 1)
    mid = top_c + (bot_c - top_c) * t
    half = 30 + 34 * t
    d = np.abs(xx - mid) / half
    col = (yy < floor_y) & (d < 1)
    pool = ((xx - bot_c) / 80) ** 2 + ((yy - floor_y) / 30) ** 2
    cv.paint((col & (d >= .55)) | ((pool <= 1) & ~col), C("rock", 0))
    cv.paint((col & (d < .55)) | (pool <= .5), C("violet", 0))
    cv.paint((col & (d < .22)) | (pool <= .18), C("glow", 0))
    return cv


def motes():
    """Dust turning slowly in the shaft of light (8 frames, the shaft's size, additive): 2-pixel motes drifting down
    and sideways, each twinkling as it turns."""
    w, h = 7 * TILE, 14 * TILE
    rnd = random.Random(61)
    dots = [(rnd.uniform(40, 120), rnd.uniform(10, h - 60), rnd.uniform(0, 6.28), rnd.choice((("glow", 2), ("rock", 2), ("glow", 1))))
            for _ in range(26)]
    frames = []
    for f in range(8):
        cv = Canvas(w, h)
        for x, y, ph, col in dots:
            X = x + math.sin(ph + f * .785) * 3
            Y = (y + f * 2) % (h - 60) + 6
            if (f + int(ph * 3)) % 4 != 0:
                cv.a[int(Y):int(Y) + 2, int(X):int(X) + 2] = C(*col)
        frames.append(cv)
    return strip(frames)


def grit():
    """Grit trickling from the broken roof onto the wreck, now and then (12 frames, 2 x 14 tiles): a few chips fall,
    a little puff where they land, then nothing for a while."""
    w, h = 2 * TILE, 14 * TILE
    frames = []
    land = h - 56
    for f in range(12):
        cv = Canvas(w, h)
        if f < 6:
            for k, (x, dy) in enumerate(((20, 0), (28, 26), (16, 48))):
                y = (f * 50 - dy)
                if 0 <= y < land:
                    m = disc(x, y, 2 if k == 0 else 1.5, w, h)
                    cv.paint(m, C("rock", 2))
                    cv.paint(m & ~sh(m, 1, 1), C("rock", 3))
        if f in (5, 6, 7):
            k = f - 5
            for dx in (-6 - k * 3, 6 + k * 3, 0):
                m = disc(24 + dx, land - 2 - k * 2, 3 - k * .6, w, h)
                cv.paint(m, C("rock", 2) if k < 2 else C("rock", 1))
        frames.append(cv)
    return strip(frames)


def drone_glow(drone):
    """The violet light the Mother-Drone throws on the floor round it when it wakes (additive, its prop's size plus
    two tiles each way), in two soft steps, brightest under the lens. It lights only the floor: where the drone
    and its slabs are, it's left clear, so the light doesn't wash over them."""
    w, h = DW + 4 * TILE, DH + 4 * TILE
    cv = Canvas(w, h)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    cx, cy = 2 * TILE + SEED["cx"], 2 * TILE + GROUND + 10
    ang = np.arctan2((yy - cy) / 64, (xx - cx) / 186)
    wob = 1 + .07 * np.sin(ang * 7 + .5) + .05 * np.sin(ang * 13)          # a ragged edge, not a disc
    e = (((xx - cx) / 176) ** 2 + ((yy - cy) / 58) ** 2) / wob ** 2
    lx, ly = 2 * TILE + LENS[0], 2 * TILE + GROUND + 4
    lens = ((xx - lx) / 56) ** 2 + ((yy - ly) / 22) ** 2
    cv.paint((e <= 1) | (lens <= 1), C("violet", 0))
    cv.paint(lens <= .45, C("violet", 1))
    solid = np.zeros((h, w), bool)
    solid[2 * TILE:2 * TILE + DH, 2 * TILE:2 * TILE + DW] = drone.a[:, :, 3] > 0
    cv.a[solid] = 0
    return cv


def scrap_props():
    """Scrap thrown off your fighter in the crash, flat on the cavern floor:
    wreck_plate (2 x 1 tiles: a torn hull plate with its orange stripe) and wreck_wing (3 x 2: a wing tip, bent)."""
    out = {}
    cv = Canvas(48, 24)
    plate = poly([(4, 14), (26, 6), (44, 10), (38, 20), (12, 22)], 48, 24)
    cv.paint(plate, C("cream", 2))
    cv.paint(plate & ~sh(plate, 0, 2), C("cream", 3))
    cv.paint(plate & ~sh(plate, -2, -2) & ~sh(plate, 0, 2), C("cream", 4))
    cv.paint(plate & lines([(8, 16), (40, 10)], 3, 48, 24), C("copper", 3))
    cv.paint(plate & lines([(8, 18), (40, 12)], 1, 48, 24), C("copper", 2))
    for x, y in ((14, 18), (30, 12)):
        cv.a[y:y + 2, x:x + 2] = C("cream", 1)
    cv.paint(edge(plate), OUT)
    out["wreck_plate"] = cv
    cv = Canvas(72, 48)
    wing = poly([(4, 34), (40, 10), (66, 6), (54, 22), (30, 40), (10, 44)], 72, 48)
    bend = lines([(22, 40), (46, 12)], 1, 72, 48) & wing
    cv.paint(wing, C("cream", 2))
    cv.paint(wing & ~sh(wing, 0, 3), C("cream", 3))
    cv.paint(wing & ~sh(wing, -3, -3) & ~sh(wing, 0, 3), C("cream", 4))
    cv.paint(wing & lines([(26, 30), (56, 12)], 4, 72, 48), C("copper", 3))
    cv.paint(bend, C("cream", 1))
    torn = wing & (poly([(0, 30), (16, 24), (20, 48), (0, 48)], 72, 48))
    cv.paint(torn, C("rock", 1))
    cv.paint(edge(wing), OUT)
    out["wreck_wing"] = cv
    rnd = random.Random(71)
    cv = Canvas(48, 24)
    for cx, cy, rx, ry in ((14, 15, 9, 6), (32, 13, 8, 6), (24, 19, 7, 4), (41, 18, 5, 4), (7, 19, 4, 3)):
        stone(cv, rock_pts(cx, cy, rx, ry, rnd, 6), MOONROCK if rnd.random() < .7 else BASALT, rnd)
    out["rock_chips"] = cv
    return out


def main():
    wreck = crash_wreck()
    wreck.save(os.path.join(LUNAR, "crash_wreck.png"))
    drone, body, veins = mother_drone()
    drone.save(os.path.join(LUNAR, "mother_drone.png"))
    wake, pulse = drone_strips(body, veins)
    for name, cv in scrap_props().items():
        cv.save(os.path.join(LUNAR, name + ".png"))
    b, at = beam()
    out = {"mother_drone_wake": wake, "mother_drone_pulse": pulse, "crash_beam": b, "light_shaft": light_shaft(),
           "motes": motes(), "grit": grit(), "drone_glow": drone_glow(drone)}
    os.makedirs(os.path.join(ROOT, "art", "prologue"), exist_ok=True)
    for name, cv in out.items():
        check(cv, name)
        cv.save(os.path.join(ROOT, "art", "prologue", name + ".png"))
    print("beam at tile", at, "size", b.w // 4, b.h, "canopy", CANOPY)
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
