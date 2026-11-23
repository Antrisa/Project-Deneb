"""Echo Landing prop redo, batch 2: Engineering machines and stock (23 Nov 2026). Chest-style shading; same sizes.
    python3 props_eng.py <repo> [names...]
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home_machines import (C, H, face, seam, bar_v, cyl, band, strip, STEEL, DARK, BRASS, FIRE, COPPER, TEAL, CREAM,
                           WOOD, HULL, GLASS, CYAN, RED, GREEN, CLEAR)
from props_redo import TEALR, YEL, WARM, post, disc, flames, window, glass

STRAP = [STEEL[1], STEEL[2], STEEL[3], STEEL[4], DARK[3]]
ROCK = [H("cfc0b8"), H("a28f97"), H("76677e"), H("52476a"), H("3a3150")]
ORE_FLECK = [H("ee8f3e"), H("edc65a"), H("8fd3c8"), H("eeeaf2")]
REDR = [H("ff9a7a"), H("e8574a"), H("b83a45"), H("7e2a42"), H("552038")]


def box(c, x0, y0, x1, y1, ramp, top=2, side=2, lit=1):
    """A box at three-quarters: lit top plane, banded front, darker right side face."""
    face(c, x0 + 1, y0, x1 - 1 + side, y0 + top - 1, ramp, lit_rows=1, right=0, left_hi=False)
    face(c, x0, y0 + top, x1, y1, ramp, lit_rows=lit, right=0)
    sr = [ramp[2], ramp[3], ramp[3], ramp[4], ramp[4]]
    face(c, x1 + 1, y0 + 1, x1 + side, y1, sr, lit_rows=0, right=0, left_hi=False)


def plinth(c, x0, x1, y, ramp=DARK, h=4, stripe=False):
    face(c, x0 + 1, y, x1 - 1, y + 1, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, x0, y + 2, x1, y + 1 + h, ramp, lit_rows=1, right=3)
    if stripe:
        for x in range(x0 + 2, x1 - 1):
            if (x // 3) % 2 == 0: c.px(x, y + 3, BRASS[1]); c.px(x, y + 4, BRASS[2])


def tank_v(c, x0, x1, y0, y1, ramp, cap=3):
    """An upright cylinder: lit elliptical top, body shaded across, darker toward the bottom."""
    for y in range(y0 + cap, y1 + 1):
        for x in range(x0, x1 + 1):
            col = cyl(x, x0, x1, ramp)
            if y > y1 - 3: col = ramp[min(4, ramp.index(col) + 1)] if col in ramp else col
            c.px(x, y, col)
    cx = (x0 + x1) / 2; rx = (x1 - x0) / 2 + 0.5
    for y in range(y0, y0 + 2 * cap + 1):
        for x in range(x0, x1 + 1):
            if ((x - cx) / rx) ** 2 + ((y - y0 - cap) / (cap + 0.5)) ** 2 <= 1:
                u = (x - x0) / (x1 - x0)
                c.px(x, y, ramp[0] if y < y0 + cap and u < 0.7 else ramp[1])


def chunk(c, x, y, w, h, ramp=ROCK, fleck=None):
    """A lump of rock or ore: lit top-left, banded, dark bottom-right."""
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if (yy == y or yy == y + h - 1) and (xx == x or xx == x + w - 1): continue
            r = (yy - y) / max(1, h - 1); u = (xx - x) / max(1, w - 1)
            t = 0 if r < 0.3 and u < 0.6 else 1 if r < 0.6 else 2
            if u > 0.7: t += 1
            c.px(xx, yy, ramp[min(4, t)])
    if fleck and w > 3:
        c.px(x + w // 2, y + h // 2, fleck); c.px(x + 1, y + 1, fleck if h > 3 else ramp[0])


def ore_heap(c, x0, x1, ytop, ybot, seed=1, flecks=ORE_FLECK, big=False):
    rnd = (seed * 2654435761) & 0xffffffff
    def r():
        nonlocal rnd
        rnd = (rnd * 1103515245 + 12345) & 0x7fffffff
        return rnd
    step = 4 if big else 3
    for row in range(ybot - (5 if big else 4), ytop - 1, -step):
        t = (ybot - row) / max(1, ybot - ytop)
        span = (x1 - x0) * (math.sqrt(max(0.0, 1 - t * t)) if big else (1 - 0.55 * t))
        cx = (x0 + x1) / 2
        x = int(cx - span / 2)
        while x < cx + span / 2 - 2:
            w = (5 + r() % 4) if big else (4 + r() % 3); h = (4 + r() % 2) if big else (3 + r() % 2)
            chunk(c, x, row, w, h, fleck=flecks[r() % len(flecks)] if r() % 3 == 0 else None)
            x += w - 1


def wheel(c, cx, cy, r, frame=0):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= r * r:
                c.px(x, y, DARK[3] if d > (r - 1.5) ** 2 else STEEL[2] if y < cy else STEEL[3])
    c.px(cx, cy, STEEL[0])
    a = frame * 0.785
    c.px(round(cx + math.cos(a) * (r - 2)), round(cy + math.sin(a) * (r - 2)), STEEL[1])


def lamps(c, x, y, cols, frame, gap=3, vertical=False):
    for i, col in enumerate(cols):
        on = (frame + i * 3) % 8 < 5
        px, py = (x, y + i * gap) if vertical else (x + i * gap, y)
        c.px(px, py, col if on else DARK[1])


def gauge(c, x, y, frame=0):
    for yy in range(y, y + 5):
        for xx in range(x, x + 5):
            if (xx - x - 2) ** 2 + (yy - y - 2) ** 2 <= 5:
                c.px(xx, yy, CREAM[0] if yy - y < 2 else CREAM[1] if yy - y < 4 else CREAM[2])
    c.px(x + 2, y + 2, DARK[4]); c.px(x + 3 if frame % 4 < 2 else x + 1, y + 1, RED)


def roller(c, cx, cy, r, frame):
    """A crushing roller seen end-on: toothed ring that turns with the frame."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                ang = math.atan2(y - cy, x - cx) + frame * 0.39
                tooth = math.cos(ang * 8) > 0.3
                if d > r - 1.5: c.px(x, y, STEEL[1] if tooth else DARK[3])
                elif d > r - 3: c.px(x, y, STEEL[2] if y < cy else STEEL[3])
                else: c.px(x, y, DARK[2] if (x + y) % 2 else DARK[3])
    c.px(cx, cy, STEEL[0])


# ------------------------------------------------------------------ animated machines (8 frames)
def ore_crusher(f):
    c = C(68, 80); B = 77
    plinth(c, 2, 65, B - 6, stripe=True)
    box(c, 4, 34, 60, B - 7, YEL, top=3, side=3)
    seam(c, 4, 60, 37, YEL)
    for bx in (4, 57):
        bar_v(c, bx, 37, B - 7, STRAP, w=3)
    window(c, 9, 40, 52, 60)
    for y in range(42, 59):
        for x in range(11, 51): c.px(x, y, DARK[3] if (x + y) % 3 else DARK[4])
    roller(c, 21, 50, 8, f); roller(c, 40, 50, 8, -f)
    for k in range(3):                                                  # crushed bits falling between
        c.px(30 + k % 2, 52 + (f * 2 + k * 3) % 7, ORE_FLECK[k % 3])
    # funnel on top, full of ore
    for y in range(14, 34):
        k = (y - 14) / 20
        x0 = round(6 + k * 12); x1 = round(61 - k * 12)
        for x in range(x0, x1 + 1):
            r = y - 14
            t = 0 if r < 2 else 1 if r < 10 else 2
            if x > x1 - 3: t += 1
            c.px(x, y, STEEL[min(4, t)])
    c.hline(6, 61, 14, STEEL[0])
    ore_heap(c, 9, 58, 5, 16, seed=f // 4 + 3)
    face(c, 44, 63, 55, B - 9, DARK, lit_rows=1, right=2)
    lamps(c, 47, 66, [GREEN, BRASS[0], RED], f)
    gauge(c, 10, 64, f)
    c.outline(); return c


def coolant_tank(f):
    c = C(66, 98); B = 95
    plinth(c, 4, 61, B - 6, stripe=False)
    tank_v(c, 8, 55, 10, B - 7, STEEL, cap=5)
    for by in (30, 60, B - 14):
        for y in (by, by + 1, by + 2):
            for x in range(7, 57):
                col = cyl(x, 7, 56, TEALR) if y < by + 2 else TEALR[3]
                c.px(x, y, col)
        for x in range(10, 55, 6): c.px(x, by + 1, TEALR[0])
    # sight glass: coolant level with rising bubbles
    window(c, 15, 36, 22, 57)
    for y in range(38, 56):
        for x in range(17, 21): c.px(x, y, CYAN[2] if y > 42 else DARK[3])
    for k in range(3):
        by_ = 55 - (f * 2 + k * 5) % 13
        if by_ > 42: c.px(17 + k % 3, by_, CYAN[0])
    gauge(c, 34, 40, f)
    # pipe elbow on the cap
    post(c, 28, 35, 2, 9)
    for x in range(28, 48): c.px(x, 2, STEEL[1]); c.px(x, 3, STEEL[2]); c.px(x, 4, STEEL[3])
    face(c, 44, 2, 48, 14, STEEL, lit_rows=1, right=2)
    c.rect(27, 6, 36, 7, BRASS[2]); c.hline(27, 36, 6, BRASS[1])
    face(c, 38, 64, 50, 72, CREAM, lit_rows=1, right=1)                 # label plate
    c.hline(40, 47, 67, CREAM[3]); c.hline(40, 45, 69, CREAM[3])
    c.outline(); return c


def breaker_panel(f):
    c = C(44, 82); B = 79
    plinth(c, 2, 41, B - 5)
    box(c, 4, 4, 37, B - 6, STEEL, top=3, side=3)
    seam(c, 4, 37, 7, STEEL)
    face(c, 8, 10, 33, B - 12, DARK, lit_rows=1, right=2)            # inner panel
    for row in range(6):
        y = 13 + row * 9
        for col in range(3):
            x = 11 + col * 7
            face(c, x, y, x + 4, y + 5, STEEL, lit_rows=1, right=1)
            up = (row * 3 + col + f // 2) % 5 != 0
            c.px(x + 2, y + (1 if up else 4), STEEL[0])
            on = (row * 5 + col * 3 + f) % 8 < 6
            c.px(x + 2, y + 7, (GREEN if (row + col) % 3 else RED) if on else DARK[1])
    for y in range(B - 11, B - 7):
        for x in range(8, 34):
            if (x // 3 + y) % 2 == 0: c.px(x, y, BRASS[1])
    c.px(36, 40, BRASS[1]); c.px(36, 41, BRASS[2]); c.px(36, 42, BRASS[3])
    c.outline(); return c


def pump(f):
    c = C(42, 72); B = 69
    plinth(c, 3, 38, B - 5, stripe=True)
    tank_v(c, 8, 31, 28, B - 6, TEALR, cap=3)
    seam(c, 8, 31, 46, TEALR)
    gauge(c, 17, 36, f)
    # piston head going up and down
    lift = [0, 1, 2, 3, 3, 2, 1, 0][f]
    post(c, 17, 22, 10 + lift, 28)
    face(c, 13, 7 + lift, 26, 10 + lift, STEEL, lit_rows=1, right=2)
    c.hline(15, 24, 6 + lift, STEEL[1])
    # outlet pipe to the right
    for x in range(31, 41):
        c.px(x, 52, STEEL[1]); c.px(x, 53, STEEL[2]); c.px(x, 54, STEEL[3])
    face(c, 34, 50, 36, 56, BRASS + [BRASS[3]], lit_rows=1, right=1)
    c.outline(); return c


def hopper(f):
    c = C(74, 100); B = 97
    # legs
    for lx in (6, 64):
        bar_v(c, lx, 38, B - 1, STRAP, w=4)
    c.hline(6, 67, 70, STEEL[2]); c.hline(6, 67, 71, STEEL[4])
    # funnel
    for y in range(14, 62):
        k = max(0, (y - 30) / 32)
        x0 = round(5 + k * 24); x1 = round(68 - k * 24)
        for x in range(x0, x1 + 1):
            r = y - 14
            t = 0 if r < 2 else 1 if r < 20 else 2 if r < 40 else 3
            if x > x1 - 3: t += 1
            if x == x0: t = max(0, t - 1)
            c.px(x, y, STEEL[min(4, t)])
    seam(c, 5, 68, 30, STEEL)
    c.hline(5, 68, 14, STEEL[0])
    ore_heap(c, 8, 65, 4, 16, seed=7)
    face(c, 28, 38, 45, 44, CREAM, lit_rows=1, right=1)                 # label
    c.hline(30, 41, 41, CREAM[3])
    # chute and falling ore
    face(c, 31, 62, 42, 70, STEEL, lit_rows=1, right=2)
    for k in range(3):
        y = 72 + (f * 3 + k * 7) % 14
        chunk(c, 34 + (k * 2) % 4, y, 3, 3, fleck=ORE_FLECK[k])
    # collection bin
    box(c, 22, 84, 49, B - 1, REDR, top=2, side=2)
    ore_heap(c, 24, 48, 80, 85, seed=2)
    c.outline(); return c


def sorting_machine(f):
    c = C(100, 80); B = 77
    plinth(c, 2, 97, B - 5, stripe=True)
    box(c, 4, 34, 92, B - 6, STEEL, top=3, side=3)
    seam(c, 4, 92, 37, STEEL)
    # conveyor on top, three bins sunk into it
    for y in range(24, 34):
        for x in range(6, 91):
            t = 0 if y < 26 else 1 if y < 31 else 2
            c.px(x, y, DARK[t + 1])
    for x in range(6, 91):
        if (x + f * 2) % 6 == 0: c.px(x, 27, DARK[4]); c.px(x, 28, DARK[4])
    for i, fl in enumerate([ORE_FLECK[0], ORE_FLECK[1], ORE_FLECK[2]]):
        x0 = 12 + i * 27
        box(c, x0, 14, x0 + 19, 25, TEALR if i == 1 else STEEL, top=2, side=2)
        for k in range(4):
            chunk(c, x0 + 2 + k * 4, 11 + (k % 2), 4, 3, fleck=fl)
    for k in range(5):
        x = 8 + (k * 17 + f * 2) % 80
        chunk(c, x, 29, 4, 3, fleck=ORE_FLECK[k % 3])
    # front: read-out, buttons, chutes
    window(c, 10, 44, 34, 56); glass(c, 12, 46, 32, 54)
    for i in range(5):
        h = 2 + (i * 3 + f) % 5
        c.vline(14 + i * 4, 53 - h, 53, CYAN[2])
    lamps(c, 42, 48, [GREEN, BRASS[0], CYAN[2], RED, GREEN], f, gap=4)
    for i in range(3):
        face(c, 60 + i * 10, 44, 67 + i * 10, 52, DARK, lit_rows=1, right=1)
        c.hline(61 + i * 10, 66 + i * 10, 47, ORE_FLECK[i])
    gauge(c, 12, 61, f)
    c.outline(); return c


def slag_bin(f):
    c = C(50, 52); B = 49
    plinth(c, 2, 47, B - 4)
    box(c, 4, 14, 42, B - 5, STEEL, top=3, side=3)
    for bx in (4, 39):
        bar_v(c, bx, 17, B - 5, STRAP, w=3)
    # glowing slag inside, pulsing
    pulse = [0, 1, 2, 1, 0, 1, 2, 1][f]
    for y in range(10, 17):
        for x in range(7, 39):
            t = (x * 3 + y * 5 + f) % 7
            c.px(x, y, FIRE[2 + (t + pulse) % 3] if y > 11 else FIRE[4])
    c.hline(5, 41, 9, DARK[2])
    face(c, 14, 26, 32, 34, YEL, lit_rows=1, right=2)                   # hot warning plate
    c.hline(17, 28, 30, DARK[4])
    c.outline(); return c


def cargo_loader(f):
    c = C(68, 72); B = 69
    # mast and forks on the left; the forks rise and fall
    for mx in (5, 11):
        bar_v(c, mx, 4, B - 10, STRAP, w=3)
    lift = [0, 2, 4, 6, 6, 4, 2, 0][f]
    fy = B - 22 - lift
    face(c, 2, fy, 16, fy + 2, STEEL, lit_rows=1, right=1)
    box(c, 3, fy - 10, 13, fy - 1, WOOD, top=2, side=1)                # crate on the forks
    c.hline(3, 13, fy - 5, WOOD[3])
    # body and cab
    box(c, 18, 32, 58, B - 9, YEL, top=3, side=3)
    seam(c, 18, 58, 35, YEL)
    box(c, 30, 8, 54, 31, YEL, top=2, side=2)
    window(c, 33, 12, 51, 26); glass(c, 35, 14, 49, 24)
    c.px(40, 4, RED if f % 4 < 2 else REDR[3]); c.rect(39, 5, 41, 7, STEEL[2])      # beacon
    for y in range(40, 52, 3):
        c.hline(22, 34, y, YEL[3])
    wheel(c, 24, B - 6, 5, f); wheel(c, 52, B - 6, 5, f)
    c.outline(); return c


def geo_core(f):
    c = C(116, 108); B = 105
    plinth(c, 2, 113, B - 7, stripe=True, h=5)
    box(c, 6, 72, 106, B - 8, STEEL, top=3, side=3)
    seam(c, 6, 106, 75, STEEL)
    for i in range(4):
        face(c, 12 + i * 24, 80, 29 + i * 24, B - 12, DARK, lit_rows=1, right=2)
        lamps(c, 15 + i * 24, 84, [GREEN, CYAN[2], BRASS[0]], f + i, gap=4)
        gauge(c, 20 + i * 24, 89, f + i)
    # core column with a glowing window, pulsing
    post(c, 36, 79, 18, 71, STEEL)
    for by in (24, 60):
        for y in (by, by + 1, by + 2):
            for x in range(34, 82):
                c.px(x, y, cyl(x, 34, 81, TEALR) if y < by + 2 else TEALR[3])
    window(c, 44, 30, 71, 58)
    pulse = [0, 1, 2, 3, 3, 2, 1, 0][f]
    for y in range(32, 57):
        for x in range(46, 70):
            d = abs(x - 57.5) / 12 + abs(y - 44) / 14
            t = d - pulse * 0.08
            col = FIRE[0] if t < 0.25 else FIRE[1] if t < 0.45 else FIRE[2] if t < 0.65 else FIRE[3] if t < 0.85 else FIRE[4]
            c.px(x, y, col)
    for y in (37, 44, 51):
        c.hline(46, 69, y, DARK[3])
    # dome cap
    for y in range(4, 19):
        k = (y - 4) / 14
        hw = round(12 + k * 10)
        for x in range(58 - hw, 58 + hw + 1):
            u = (x - (58 - hw)) / (2 * hw)
            t = 0 if y < 8 and u < 0.6 else 1 if u < 0.55 else 2 if u < 0.85 else 3
            c.px(x, y, STEEL[t])
    post(c, 55, 60, 0, 4)
    # pipes either side
    for side in (0, 1):
        x0 = 14 if side == 0 else 88
        for y in range(30, 72):
            for x in range(x0, x0 + 8): c.px(x, y, cyl(x, x0, x0 + 7, STEEL))
        for x in range(x0 + (8 if side == 0 else -10), x0 + (20 if side == 0 else 0)):
            for y in range(36, 42): c.px(x, y, STEEL[1] if y < 38 else STEEL[2] if y < 40 else STEEL[3])
        c.hline(x0 - 1, x0 + 8, 50, BRASS[1]); c.hline(x0 - 1, x0 + 8, 51, BRASS[3])
    c.outline(); return c


def pipe_rack(f):
    c = C(72, 36); B = 33
    for sx in (6, 34, 62):
        bar_v(c, sx, 6, B - 3, STRAP, w=3)
        face(c, sx - 2, B - 3, sx + 4, B - 1, DARK, lit_rows=1, right=1)
    for i, (py, ramp) in enumerate([(8, STEEL), (16, TEALR), (24, COPPER + [COPPER[3]])]):
        for y in range(py, py + 5):
            r = y - py
            for x in range(2, 70):
                t = 0 if r == 0 else 1 if r < 2 else 2 if r < 4 else 3
                c.px(x, y, ramp[min(len(ramp) - 1, t)])
        for jx in (20, 50):
            c.vline(jx, py, py + 4, ramp[min(len(ramp) - 1, 3)]); c.vline(jx + 1, py, py + 4, ramp[0])
    # a valve whose lamp blinks
    face(c, 44, 3, 48, 7, REDR, lit_rows=1, right=1)
    c.px(46, 1, GREEN if f % 4 < 2 else DARK[1])
    c.outline(); return c


def air_scrubber(f):
    c = C(46, 78); B = 75
    plinth(c, 2, 43, B - 5)
    box(c, 4, 6, 38, B - 6, STEEL, top=3, side=3)
    seam(c, 4, 38, 9, STEEL)
    # big fan behind a grille, blades turning
    cx, cy, r = 21, 28, 13
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                if d > r - 1.5: c.px(x, y, DARK[1] if y < cy else DARK[3]); continue
                ang = math.atan2(y - cy, x - cx) + f * 0.39
                blade = math.cos(ang * 4) > 0.45
                col = (STEEL[1] if y < cy else STEEL[2]) if blade else DARK[3]
                if d < 3: col = BRASS[1] if y < cy else BRASS[2]
                c.px(x, y, col)
    for y in range(cy - r + 2, cy + r - 1, 4):
        for x in range(cx - r + 1, cx + r):
            if math.hypot(x - cx, y - cy) < r - 1: c.px(x, y, DARK[2])
    # filter vents below and a status strip
    for y in range(46, B - 10, 3):
        c.hline(9, 33, y, DARK[3]); c.hline(9, 33, y + 1, STEEL[0])
    lamps(c, 10, B - 9, [GREEN, CYAN[2], BRASS[0]], f, gap=3)
    c.outline(); return c


def ore_analyzer(f):
    c = C(46, 78); B = 75
    plinth(c, 2, 43, B - 5)
    box(c, 4, 30, 38, B - 6, STEEL, top=3, side=3)
    seam(c, 4, 38, 33, STEEL)
    window(c, 8, 38, 34, 52); glass(c, 10, 40, 32, 50)
    pts = [(10 + i * 2, 48 - int(4 * abs(math.sin(i * 0.7 + f * 0.6)))) for i in range(12)]
    for x, y in pts: c.px(x, y, CYAN[1])
    lamps(c, 10, 57, [GREEN, BRASS[0], RED], f, gap=4)
    face(c, 24, 56, 34, 64, DARK, lit_rows=1, right=1)
    c.hline(26, 31, 60, BRASS[1])
    # glass dome on top with a sample and a scanning line
    face(c, 8, 26, 34, 29, STEEL, lit_rows=1, right=2)
    for y in range(6, 26):
        for x in range(9, 34):
            if ((x - 21.5) / 12.5) ** 2 + ((y - 26) / 20) ** 2 <= 1:
                edge = ((x - 21.5) / 11.3) ** 2 + ((y - 26) / 18.6) ** 2 > 1
                c.px(x, y, CYAN[3] if edge else (GLASS[0] if x < 18 and y < 18 else GLASS[1]))
    chunk(c, 17, 19, 9, 6, fleck=ORE_FLECK[1])
    sy = 9 + (f * 2) % 16
    for x in range(10, 33):
        if ((x - 21.5) / 12.5) ** 2 + ((sy - 26) / 20) ** 2 <= 1: c.px(x, sy, CYAN[0])
    c.px(13, 12, CYAN[0]); c.px(14, 11, CYAN[0])
    c.outline(); return c


def launch_console(f):
    c = C(72, 52); B = 49
    plinth(c, 2, 69, B - 4)
    box(c, 4, 22, 64, B - 5, STEEL, top=2, side=3)
    seam(c, 4, 64, 24, STEEL)
    # sloped desk top with screens and buttons
    for y in range(10, 22):
        k = (y - 10) / 12
        for x in range(round(8 - k * 4), round(61 + k * 3) + 1):
            r = y - 10
            t = 0 if r < 2 else 1 if r < 7 else 2
            c.px(x, y, DARK[t])
    for i in range(3):
        window(c, 11 + i * 16, 4, 24 + i * 16, 14)
        glass(c, 13 + i * 16, 6, 22 + i * 16, 12)
        c.hline(14 + i * 16, 14 + i * 16 + (f + i * 3) % 7, 9, CYAN[1])
    lamps(c, 12, 18, [GREEN, BRASS[0], RED, CYAN[2], GREEN, BRASS[0], RED, CYAN[2], GREEN, BRASS[0], RED, CYAN[2]], f, gap=4)
    # launch lever
    lv = [0, 0, 1, 2, 2, 1, 0, 0][f]
    post(c, 56, 57, 3 + lv, 12)
    c.rect(55, 1 + lv, 58, 3 + lv, REDR[1]); c.px(55, 1 + lv, REDR[0])
    for y in range(30, B - 7, 4):
        c.hline(10, 30, y, STEEL[3])
    face(c, 40, 29, 58, 38, YEL, lit_rows=1, right=2)
    c.hline(43, 54, 33, DARK[4])
    c.outline(); return c


ANIMATED = {"ore_crusher": ore_crusher, "coolant_tank": coolant_tank, "breaker_panel": breaker_panel, "pump": pump,
            "hopper": hopper, "sorting_machine": sorting_machine, "slag_bin": slag_bin, "cargo_loader": cargo_loader,
            "geo_core": geo_core, "pipe_rack": pipe_rack, "air_scrubber": air_scrubber, "ore_analyzer": ore_analyzer,
            "launch_console": launch_console}

# ------------------------------------------------------------------ static stock and furniture
def crate(c, x0, y0, x1, y1, ramp=WOOD, straps=True):
    """A crate shaded like the chest: lit lid, banded planks, a darker right side, steel straps at the ends."""
    box(c, x0, y0, x1, y1, ramp, top=2, side=2)
    for y in range(y0 + 2 + 3, y1, 4):
        c.hline(x0, x1, y, ramp[3])
    if straps:
        for bx in (x0 + 1, x1 - 2):
            bar_v(c, bx, y0, y1, STRAP, w=2)


def ore_cart():
    c = C(40, 40); B = 37
    ore_heap(c, 6, 33, 5, 14, seed=11)
    box(c, 3, 12, 33, 30, REDR, top=2, side=3)
    seam(c, 3, 33, 14, REDR)
    for bx in (3, 30):
        bar_v(c, bx, 14, 30, STRAP, w=3)
    c.hline(3, 36, 31, DARK[3])
    wheel(c, 10, B - 3, 4); wheel(c, 28, B - 3, 4)
    c.outline(); return c


def ore_pile():
    c = C(68, 36)
    ore_heap(c, 3, 64, 4, 34, seed=5, big=True)
    c.outline(); return c


def ingot_stack():
    c = C(46, 40); B = 37
    face(c, 3, B - 6, 41, B - 5, WOOD, lit_rows=1, right=0, left_hi=False)           # pallet
    face(c, 2, B - 4, 42, B - 1, WOOD[1:], lit_rows=1, right=3)
    for x in (6, 21, 37): c.vline(x, B - 4, B - 1, WOOD[4])
    ramps = [BRASS + [BRASS[3]], COPPER + [COPPER[3]], STEEL]
    for row in range(4):
        y = B - 11 - row * 6
        n = 4 - row
        for i in range(n):
            x = 5 + row * 4 + i * 9
            r = ramps[(row + i) % 3]
            face(c, x + 1, y, x + 7, y + 1, r, lit_rows=1, right=0, left_hi=False)
            face(c, x, y + 2, x + 8, y + 4, r, lit_rows=1, right=2)
    c.outline(); return c


def barrel(c, x0, y0, x1, y1, ramp):
    tank_v(c, x0, x1, y0, y1, ramp, cap=2)
    for by in (y0 + 7, y1 - 5):
        for x in range(x0, x1 + 1):
            c.px(x, by, cyl(x, x0, x1, STEEL)); c.px(x, by + 1, STEEL[3])
    c.rect((x0 + x1) // 2 - 1, y0 + 1, (x0 + x1) // 2, y0 + 2, DARK[3])


def barrel_stack():
    c = C(42, 52); B = 50
    barrel(c, 2, 24, 19, B - 1, TEALR)
    barrel(c, 21, 26, 38, B - 1, REDR)
    barrel(c, 11, 1, 28, 25, YEL)
    c.outline(); return c


def sack(c, x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (y in (y0, y1)) and (x in (x0, x1)): continue
            r = (y - y0) / max(1, y1 - y0); u = (x - x0) / max(1, x1 - x0)
            t = 0 if r < 0.3 and u < 0.7 else 1 if r < 0.7 else 2
            if u > 0.75: t += 1
            c.px(x, y, CREAM[min(3, t)])
    c.hline(x0 + 2, x1 - 2, y0 + 1, CREAM[2]); c.px((x0 + x1) // 2, y0, CREAM[3])


def pallet():
    c = C(46, 42); B = 39
    face(c, 3, B - 6, 41, B - 5, WOOD, lit_rows=1, right=0, left_hi=False)
    face(c, 2, B - 4, 42, B - 1, WOOD[1:], lit_rows=1, right=3)
    for x in (6, 21, 37): c.vline(x, B - 4, B - 1, WOOD[4])
    sack(c, 4, 20, 20, 33); sack(c, 21, 21, 39, 33); sack(c, 12, 9, 30, 21)
    c.outline(); return c


def cargo():
    c = C(44, 40)
    crate(c, 2, 14, 21, 36)
    crate(c, 23, 20, 38, 36, TEALR)
    crate(c, 7, 2, 20, 13, WOOD, straps=False)
    c.outline(); return c


def shelves(c, x0, x1, y0, y1, levels):
    for bx in (x0, x1 - 2):
        bar_v(c, bx, y0, y1, STRAP, w=3)
    for ly in levels:
        face(c, x0, ly, x1, ly + 1, BRASS + [BRASS[3]], lit_rows=1, right=2)
        c.hline(x0, x1, ly + 2, DARK[3])


def parts_rack():
    c = C(66, 80); B = 78
    shelves(c, 3, 60, 4, B - 1, [24, 48, 72])
    for i in range(3):                                                    # coils of cable
        cx = 12 + i * 15
        for y in range(10, 24):
            for x in range(cx - 6, cx + 7):
                d = math.hypot(x - cx, (y - 17) * 1.1)
                if 3 < d <= 6.5: c.px(x, y, COPPER[0] if y < 15 else COPPER[1] if y < 20 else COPPER[2])
    for i in range(3):                                                    # parts boxes
        crate(c, 7 + i * 17, 35, 20 + i * 17, 47, [TEALR, STEEL, REDR][i], straps=False)
    for i in range(4):                                                    # pipes and plates
        face(c, 7 + i * 13, 60, 17 + i * 13, 71, STEEL if i % 2 else TEALR, lit_rows=1, right=2)
    c.outline(); return c


def fuel_tank():
    c = C(32, 84); B = 82
    face(c, 3, B - 5, 28, B - 4, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 2, B - 3, 29, B - 1, DARK, lit_rows=1, right=3)
    tank_v(c, 3, 14, 14, B - 6, TEALR, cap=2)
    tank_v(c, 16, 27, 18, B - 6, REDR, cap=2)
    for x0, y0 in ((6, 9), (19, 13)):
        post(c, x0, x0 + 4, y0, y0 + 6); c.rect(x0 - 1, y0 - 1, x0 + 5, y0, BRASS[1])
    for y in (40, 41):
        c.hline(2, 29, y, STEEL[2] if y == 40 else STEEL[4])
    face(c, 5, 50, 12, 58, CREAM, lit_rows=1, right=1); face(c, 18, 52, 25, 60, CREAM, lit_rows=1, right=1)
    c.outline(); return c


def welding_rig():
    c = C(40, 68); B = 65
    face(c, 3, B - 12, 36, B - 11, STEEL, lit_rows=1, right=0, left_hi=False)    # cart deck
    face(c, 2, B - 10, 37, B - 7, REDR, lit_rows=1, right=3)
    wheel(c, 8, B - 3, 3); wheel(c, 31, B - 3, 3)
    tank_v(c, 4, 12, 10, B - 13, REDR, cap=2)
    tank_v(c, 14, 22, 14, B - 13, TEALR, cap=2)
    for x0, y0 in ((6, 6), (16, 10)):
        post(c, x0, x0 + 4, y0, y0 + 4)
    box(c, 24, 30, 35, B - 13, STEEL, top=2, side=1)                              # welder unit
    gauge(c, 27, 35)
    c.px(28, 44, GREEN); c.px(31, 44, RED)
    for i in range(14):                                                           # hose coil
        a = i * 0.45
        c.px(round(29 + math.cos(a) * 5), round(22 + math.sin(a) * 5), DARK[2])
    c.outline(); return c


def tool_cart():
    c = C(38, 46); B = 43
    box(c, 3, 8, 31, B - 6, REDR, top=3, side=3)
    for i in range(4):
        y = 13 + i * 7
        face(c, 5, y, 29, y + 5, REDR, lit_rows=1, right=2)
        c.hline(13, 21, y + 2, STEEL[1]); c.hline(13, 21, y + 3, STEEL[3])
    for x, h in ((8, 5), (14, 3), (22, 6)):                                       # tools on top
        c.vline(x, 8 - h, 7, STEEL[1]); c.vline(x + 1, 8 - h, 7, STEEL[3])
    wheel(c, 8, B - 3, 3); wheel(c, 28, B - 3, 3)
    c.outline(); return c


def locker():
    c = C(50, 80); B = 78
    face(c, 3, B - 4, 44, B - 3, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 2, B - 2, 45, B, DARK, lit_rows=1, right=3)
    box(c, 3, 3, 42, B - 5, TEALR, top=3, side=3)
    c.vline(22, 6, B - 5, TEALR[4]); c.vline(23, 6, B - 5, TEALR[1])
    for x0 in (6, 25):
        for y in range(10, 18, 2):
            c.hline(x0 + 2, x0 + 12, y, TEALR[4]); c.hline(x0 + 2, x0 + 12, y + 1, TEALR[0])
        face(c, x0 + 3, 24, x0 + 11, 29, CREAM, lit_rows=1, right=1)
        bar_v(c, x0 + 12, 36, 48, BRASS + [BRASS[3]], w=2)
    c.outline(); return c


def storage_shelf():
    c = C(66, 84); B = 82
    shelves(c, 3, 60, 4, B - 1, [26, 52, 78])
    for lvl, y1 in enumerate((25, 51, 77)):
        for i in range(3):
            w = 14
            x0 = 7 + i * 17
            crate(c, x0, y1 - 11, x0 + w - 2, y1 - 1, [WOOD, TEALR, REDR][(lvl + i) % 3], straps=(i % 2 == 0))
    c.outline(); return c


def water_tank():
    c = C(38, 48); B = 46
    face(c, 3, B - 5, 34, B - 4, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 2, B - 3, 35, B - 1, DARK, lit_rows=1, right=3)
    tank_v(c, 5, 30, 6, B - 6, CREAM + [CREAM[3]], cap=3)
    window(c, 9, 16, 14, 36)
    for y in range(18, 35): c.px(11, y, CYAN[2] if y > 22 else DARK[3]); c.px(12, y, CYAN[1] if y > 22 else DARK[3])
    for by in (12, B - 10):
        for x in range(5, 31): c.px(x, by, cyl(x, 5, 30, TEALR)); c.px(x, by + 1, TEALR[3])
    face(c, 30, 30, 35, 33, BRASS + [BRASS[3]], lit_rows=1, right=1)
    c.px(33, 34, CYAN[1])
    c.outline(); return c


STATIC = {"ore_cart": ore_cart, "ore_pile": ore_pile, "ingot_stack": ingot_stack, "barrel_stack": barrel_stack,
          "pallet": pallet, "cargo": cargo, "parts_rack": parts_rack, "fuel_tank": fuel_tank, "welding_rig": welding_rig,
          "tool_cart": tool_cart, "locker": __import__("style_v2_demo").locker, "storage_shelf": storage_shelf, "water_tank": water_tank}

if __name__ == "__main__":
    repo = sys.argv[1]
    want = sys.argv[2:] or list(ANIMATED) + list(STATIC)
    lunar = os.path.join(repo, "art/lunar")
    for n in want:
        if n in ANIMATED:
            fn = ANIMATED[n]
            fn(0).save(os.path.join(lunar, n + ".png"))
            strip([fn(i) for i in range(8)]).save(os.path.join(lunar, "anim", n + ".png"))
        else:
            STATIC[n]().save(os.path.join(lunar, n + ".png"))
    print("ok", len(want))
