"""Echo Landing prop redo (23 Nov 2026). Zachary: "alot of that stuff doesnt fit the art style and doesnt have depth and
shadowing". Every piece is shaded like the storage chest (home_machines.py): lit top rows, each face banded darker
toward the bottom, right columns a step darker, a lit left edge, straps shaded across, seams dark over lit, outline
#5b332d / #3a2026. Same pixel sizes as the pieces they replace, so footprints don't move.
    python3 props_redo.py <repo> [names...]
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home_machines import (C, H, face, seam, bar_v, cyl, band, strip, STEEL, DARK, BRASS, FIRE, COPPER, TEAL, CREAM,
                           WOOD, HULL, GLASS, CYAN, RED, GREEN, CLEAR)

TEALR = [H("8ad6c0"), H("55b0a6"), H("37868f"), H("2c5e76"), H("2b3c61")]
YEL = [H("fff3a8"), H("ffd75e"), H("f0a93a"), H("c2742e"), H("8a4a2a")]
WARM = [H("fff6d0"), H("fff0a0"), H("f4d35e"), H("edc65a")]


def post(c, x0, x1, y0, y1, ramp=STEEL):
    """A round post, shaded across its width."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c.px(x, y, cyl(x, x0, x1, ramp))


def disc(c, cx, cy, rx, ry, ramp, rim=2):
    """A flat round base or table top seen from above at three-quarters: lit back, shaded front rim."""
    for y in range(cy - ry, cy + ry + rim + 1):
        for x in range(cx - rx, cx + rx + 1):
            u = (x - cx) / (rx + 0.5)
            top = ((y - cy) / (ry + 0.5)) ** 2 + u * u <= 1
            side = (((y - rim - cy) / (ry + 0.5)) ** 2 + u * u <= 1) and y > cy
            if top:
                v = (y - cy) / (ry + 0.5)
                t = 0 if v < -0.45 else 1 if v < 0.2 else 2
                if u > 0.6: t += 1
                c.px(x, y, ramp[min(4, t)])
            elif side:
                c.px(x, y, ramp[3] if u < 0.5 else ramp[4])


def flames(c, x0, y0, x1, y1, frame, n_frames=3):
    """Fire inside a window: tongues whose heights shift with the frame, hottest at the bottom."""
    span = y1 - y0
    ph = frame * (6.283 / n_frames)
    for x in range(x0, x1 + 1):
        hgt = span * (0.55 + 0.35 * math.sin(x * 1.7 + ph * 2.1) * math.sin(x * 0.9 - ph * 1.3 + 1.0))
        hgt += 2 if (x - x0) % 5 in (1, 2) else 0
        for y in range(y0, y1 + 1):
            up = y1 - y
            if up > hgt: col = FIRE[5] if (x + y + frame) % 5 else H("5a2a26")
            elif up > hgt * 0.75: col = FIRE[4]
            elif up > hgt * 0.45: col = FIRE[3]
            elif up > hgt * 0.2: col = FIRE[2]
            else: col = FIRE[1]
            c.px(x, y, col)
    for k in range(2):
        c.px(x0 + (3 + k * 5 + frame * 3) % (x1 - x0 + 1), y0 + (1 + k * 2 + frame) % 3, FIRE[1])


def window(c, x0, y0, x1, y1):
    """A dark bevelled frame: lit top/left edge, dark bottom/right."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (y in (y0, y1)) and (x in (x0, x1)): continue
            if x in (x0, x1) or y in (y0, y1):
                c.px(x, y, DARK[1] if (y == y0 or x == x0) else DARK[3])
            elif x in (x0 + 1, x1 - 1) or y in (y0 + 1, y1 - 1):
                c.px(x, y, DARK[4] if (y == y0 + 1 or x == x0 + 1) else DARK[2])


def glass(c, x0, y0, x1, y1, ramp=GLASS):
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        for x in range(x0, x1 + 1):
            c.px(x, y, ramp[0] if t < 0.25 else ramp[1] if t < 0.6 else ramp[2])
    c.hline(x0, x0 + max(1, (x1 - x0) // 3), y0, ramp[0] if ramp is not GLASS else CYAN[2])


# ------------------------------------------------------------------ street furniture
def lamp_post():
    c = C(24, 88)
    face(c, 5, 80, 18, 81, STEEL, lit_rows=1, right=0, left_hi=False)          # base: top plane
    face(c, 4, 82, 19, 86, DARK, lit_rows=1, right=3)
    post(c, 9, 14, 24, 79)
    for y in (48, 49, 50):
        for x in range(8, 16):
            c.px(x, y, cyl(x, 8, 15, TEALR) if y < 50 else TEALR[3])
    # lamp head: cap, warm light panel in a frame, bottom cap
    face(c, 5, 4, 18, 6, STEEL, lit_rows=1, right=2)
    c.hline(8, 15, 3, STEEL[1]); c.px(11, 2, STEEL[1]); c.px(12, 2, STEEL[2])
    window(c, 5, 7, 18, 20)
    for y in range(9, 19):
        t = (y - 9) / 9
        for x in range(7, 17):
            c.px(x, y, WARM[0] if t < 0.3 else WARM[1] if t < 0.65 else WARM[2])
        c.px(16, y, WARM[3])
    c.vline(11, 9, 18, BRASS[2]); c.vline(12, 9, 18, BRASS[3])            # mullion
    face(c, 6, 21, 17, 23, STEEL, lit_rows=1, right=2)
    c.outline()
    return c


def signpost():
    c = C(40, 58)
    face(c, 13, 52, 26, 53, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 12, 54, 27, 56, DARK, lit_rows=1, right=3)
    post(c, 18, 21, 4, 51)
    face(c, 17, 2, 22, 3, STEEL, lit_rows=1, right=1)
    def sign(x0, x1, y0, right_arrow):
        h = 7
        for y in range(y0, y0 + h + 1):
            r = y - y0
            for x in range(x0, x1 + 1):
                # arrow point on one end
                d = (x - (x1 - 4)) if right_arrow else ((x0 + 4) - x)
                if d > 0 and d > min(r, h - r): continue
                t = 0 if r == 0 else 1 if r < 4 else 2 if r < h else 3
                if (right_arrow and x > x1 - 3) or (not right_arrow and x > x1 - 2): t += 1
                c.px(x, y, TEALR[min(4, t)])
        # arrow glyph and lettering in cream
        mid = y0 + 3
        ax = x1 - 9 if right_arrow else x0 + 4
        for i in range(4):
            c.px(ax + (i if right_arrow else 4 - i), mid + (0), CREAM[1])
        c.px(ax + (3 if right_arrow else 1), mid - 1, CREAM[1]); c.px(ax + (3 if right_arrow else 1), mid + 1, CREAM[2])
        lx = x0 + 3 if right_arrow else x0 + 10
        for i in range(0, 6, 2):
            c.px(lx + i, mid, CREAM[2]); c.px(lx + i, mid + 1, CREAM[3])
        # brass clamp to the post
        c.rect(17, y0 + 2, 22, y0 + 4, BRASS[2]); c.hline(17, 22, y0 + 2, BRASS[1]); c.px(17, y0 + 2, BRASS[0])
    sign(19, 38, 7, True)
    sign(1, 20, 19, False)
    sign(19, 38, 31, True)
    c.outline()
    return c


def mailbox(back=False):
    c = C(28, 44)
    face(c, 8, 38, 19, 39, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 7, 40, 20, 42, DARK, lit_rows=1, right=3)
    post(c, 11, 16, 26, 37)
    # the terminal box: lit top plane, banded teal front, darker right side
    face(c, 3, 5, 22, 7, TEALR, lit_rows=1, right=0, left_hi=False)
    face(c, 3, 8, 22, 25, TEALR, lit_rows=1, right=3)
    seam(c, 3, 22, 8, TEALR)
    face(c, 23, 6, 24, 25, [TEALR[3], TEALR[3], TEALR[4], TEALR[4], TEALR[4]], lit_rows=0, right=0, left_hi=False)
    for bx in (3, 20):
        bar_v(c, bx, 8, 25, [STEEL[1], STEEL[2], STEEL[3], STEEL[4], DARK[3]], w=2)
    if not back:
        c.rect(7, 11, 18, 12, DARK[4]); c.hline(7, 18, 13, BRASS[1]); c.px(7, 13, BRASS[0])     # letter slot
        window(c, 7, 15, 15, 22)
        glass(c, 9, 17, 13, 20)
        c.px(12, 18, GREEN)
        for y in (16, 19):
            c.px(17, y, BRASS[1]); c.px(18, y, BRASS[3])                                  # buttons
    else:
        for y in range(12, 23, 2):
            c.hline(7, 18, y, TEALR[4]); c.hline(7, 18, y + 1, TEALR[1])                  # vents on the back
    c.outline()
    return c


def stanchion():
    c = C(20, 32)
    disc(c, 6, 27, 4, 2, STEEL, rim=1)
    post(c, 4, 7, 6, 26)
    face(c, 3, 3, 8, 5, STEEL, lit_rows=1, right=2)
    c.hline(4, 7, 2, STEEL[1])
    for x in range(9, 20):                                                           # belt to the next post
        c.px(x, 8, TEALR[1]); c.px(x, 9, TEALR[2]); c.px(x, 10, TEALR[4])
    c.outline()
    return c


def hazard_sign():
    c = C(22, 56)
    face(c, 6, 50, 15, 51, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 5, 52, 16, 54, DARK, lit_rows=1, right=3)
    post(c, 9, 12, 20, 49)
    # warning triangle, banded yellow with a dark rim and a "!"
    top, bot = 2, 19
    for y in range(top, bot + 1):
        half = (y - top) * 10 // (bot - top)
        for x in range(10 - half, 11 + half + 1):
            edge = x in (10 - half, 11 + half) or y == bot
            r = y - top
            t = 0 if r < 3 else 1 if r < 8 else 2 if r < 14 else 3
            if x > 11 + half - 2: t += 1
            c.px(x, y, DARK[3] if edge else YEL[min(4, t)])
    c.vline(10, 7, 13, DARK[4]); c.vline(11, 7, 13, DARK[3]); c.rect(10, 15, 11, 16, DARK[4])
    c.outline()
    return c


def bin_():
    c = C(22, 30)
    face(c, 3, 4, 18, 6, TEALR, lit_rows=1, right=0, left_hi=False)                  # lid top
    face(c, 2, 7, 19, 9, TEALR, lit_rows=1, right=3)                                  # lid rim
    c.rect(8, 5, 13, 5, TEALR[4])                                                      # slot
    face(c, 3, 10, 18, 27, STEEL, lit_rows=1, right=3)
    seam(c, 3, 18, 10, STEEL)
    for y in (13, 24):
        c.hline(3, 18, y, TEALR[2]); c.hline(3, 18, y + 1, TEALR[3])
    for (x, y) in [(10, 16), (11, 16), (13, 18), (13, 19), (8, 19), (8, 20), (11, 21), (12, 21)]:   # recycle mark
        c.px(x, y, CREAM[1])
    c.outline()
    return c


def bollard_light():
    c = C(20, 36)
    face(c, 3, 30, 16, 31, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 2, 32, 17, 34, DARK, lit_rows=1, right=3)
    face(c, 5, 13, 14, 29, STEEL, lit_rows=1, right=2)
    seam(c, 5, 14, 13, STEEL)
    for bx in (5, 12):
        bar_v(c, bx, 14, 29, [STEEL[1], STEEL[2], STEEL[3], STEEL[4], DARK[3]], w=2)
    window(c, 5, 5, 14, 12)
    for y in range(7, 11):
        for x in range(7, 13):
            c.px(x, y, WARM[0] if y < 8 else WARM[1] if y < 10 else WARM[2])
    face(c, 4, 2, 15, 4, STEEL, lit_rows=1, right=2)
    c.outline()
    return c


def telescope():
    c = C(48, 68)
    # pedestal mount
    face(c, 14, 60, 31, 61, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 13, 62, 32, 65, DARK, lit_rows=1, right=3)
    post(c, 19, 26, 38, 59)
    for y in (46, 47):
        for x in range(18, 28): c.px(x, y, cyl(x, 18, 27, TEALR) if y == 46 else TEALR[3])
    face(c, 16, 33, 29, 37, STEEL, lit_rows=1, right=2)                              # fork head
    # the tube, angled up to the right, shaded across its thickness (filled pixel by pixel, no gaps)
    ax, ay, bx2, by2 = 8, 42, 44, 10
    L = math.hypot(bx2 - ax, by2 - ay); ux, uy = (bx2 - ax) / L, (by2 - ay) / L
    for y in range(0, 50):
        for x in range(0, 48):
            dx, dy = x - ax, y - ay
            along = dx * ux + dy * uy
            across = -dx * uy + dy * ux          # negative = upper-left side (lit)
            if along < 0 or along > L: continue
            r = 3.5 if along > 7 else 2.3
            if abs(across) > r: continue
            t = (across + r) / (2 * r)
            col = STEEL[0] if t < 0.2 else STEEL[1] if t < 0.45 else STEEL[2] if t < 0.75 else STEEL[3]
            if 15 < along < 18 or 31 < along < 34:
                col = TEALR[0] if t < 0.3 else TEALR[2] if t < 0.7 else TEALR[3]
            if along > L - 2:
                col = BRASS[1] if t < 0.5 else BRASS[3]
            c.px(x, y, col)
    c.px(bx2 + 1, by2 - 1, CYAN[1])
    c.outline()
    return c


# ------------------------------------------------------------------ tables
def table():
    c = C(44, 42)
    # laminate top: lit top plane, banded, a front edge and a dark lip
    face(c, 2, 9, 41, 21, CREAM + [CREAM[3]], lit_rows=2, right=0, left_hi=False)
    face(c, 2, 22, 41, 24, STEEL, lit_rows=1, right=4)
    c.hline(2, 41, 25, DARK[3])
    for lx in (4, 36):
        bar_v(c, lx, 26, 39, [STEEL[1], STEEL[2], STEEL[3], STEEL[4], DARK[3]], w=4)
    c.hline(8, 35, 33, STEEL[2]); c.hline(8, 35, 34, STEEL[4])                         # stretcher
    # a mug and a tablet on top
    face(c, 9, 11, 13, 15, TEALR, lit_rows=1, right=1); c.px(14, 13, TEALR[3])
    face(c, 24, 13, 33, 16, DARK, lit_rows=1, right=2); c.hline(25, 31, 14, CYAN[2])
    c.outline()
    return c


def cafe_table(tall=False):
    w, h = (30, 54) if tall else (30, 36)
    c = C(w, h)
    top_y = 8
    base_y = h - 4
    disc(c, 15, base_y - 1, 7, 2, STEEL, rim=1)
    post(c, 13, 17, top_y + 5, base_y - 2)
    # round top seen at three-quarters: lit back, banded toward the front, a darker edge band and lip
    rx, ry = 13, 4
    for y in range(top_y - ry, top_y + ry + 3):
        for x in range(15 - rx, 15 + rx + 1):
            u = (x - 15) / (rx + 0.5)
            on_top = ((y - top_y) / (ry + 0.5)) ** 2 + u * u <= 1
            on_edge = (((y - 2 - top_y) / (ry + 0.5)) ** 2 + u * u <= 1) and y > top_y
            if on_top:
                v = (y - top_y) / (ry + 0.5)
                t = 0 if v < -0.5 else 1 if v < 0.35 else 2
                if u > 0.7: t += 1
                c.px(x, y, CREAM[min(3, t)])
            elif on_edge:
                c.px(x, y, WOOD[2] if y < top_y + ry + 2 and u < 0.6 else WOOD[3] if u < 0.6 else WOOD[4])
    # a cup and saucer
    c.hline(9, 13, top_y, CREAM[3]); face(c, 10, top_y - 3, 12, top_y - 1, TEALR, lit_rows=1, right=1)
    if tall:
        c.rect(18, top_y - 5, 19, top_y - 1, BRASS[2]); c.px(18, top_y - 5, BRASS[0])
    c.outline()
    return c


# ------------------------------------------------------------------ fridge
def fridge():
    c = C(36, 70)
    B = 67
    face(c, 3, 2, 31, 4, STEEL, lit_rows=1, right=0, left_hi=False)                  # top plane
    face(c, 32, 3, 34, B - 2, [STEEL[2], STEEL[3], STEEL[3], STEEL[4], STEEL[4]], lit_rows=0, right=0, left_hi=False)
    face(c, 2, 5, 31, 22, STEEL, lit_rows=1, right=3)                                 # freezer door
    face(c, 2, 24, 31, B - 4, STEEL, lit_rows=1, right=3)                             # main door
    c.hline(2, 31, 23, DARK[4])
    face(c, 2, B - 3, 31, B - 1, DARK, lit_rows=1, right=3)                           # kick plate
    for x in range(5, 29, 3):
        c.px(x, B - 2, DARK[4])
    # handles: brass bars down the right of each door
    for (y0, y1) in ((8, 19), (27, 44)):
        bar_v(c, 26, y0, y1, BRASS + [BRASS[3]], w=2)
    # teal status panel with a temperature read-out
    window(c, 5, 8, 17, 14)
    glass(c, 7, 10, 15, 12)
    c.hline(8, 11, 11, CYAN[1]); c.px(14, 10, GREEN)
    # a note and a magnet
    face(c, 8, 30, 15, 38, CREAM, lit_rows=1, right=1)
    c.hline(9, 13, 32, CREAM[3]); c.hline(9, 14, 34, CREAM[3]); c.px(11, 29, RED)
    c.outline()
    return c


# ------------------------------------------------------------------ Engineering furnace (56 x 88, 8 frames)
def eng_furnace(frame=0):
    c = C(56, 88)
    B = 85
    face(c, 2, B - 7, 53, B - 6, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 2, B - 5, 53, B - 1, DARK, lit_rows=1, right=4)
    for x in range(5, 51):
        if (x // 3) % 2 == 0: c.px(x, B - 3, BRASS[1]); c.px(x, B - 2, BRASS[2])
    # body
    X0, X1, T0, BOT = 5, 46, 36, B - 8
    face(c, X0 + 1, T0, X1 - 1, T0 + 2, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, X0, T0 + 3, X1, BOT, STEEL, lit_rows=1, right=0)
    seam(c, X0, X1, T0 + 3, STEEL)
    face(c, X1 + 1, T0 + 1, X1 + 4, BOT, STEEL[2:] + [DARK[3], DARK[4]], lit_rows=0, right=0, left_hi=False)
    for bx in (X0, X1 - 2):
        bar_v(c, bx, T0 + 3, BOT, [STEEL[1], STEEL[2], STEEL[3], STEEL[4], DARK[3]], w=3)
        for y in (T0 + 6, (T0 + BOT) // 2, BOT - 3):
            c.px(bx + 1, y, STEEL[0])
    # big door with a wide window
    dx0, dx1, dy0, dy1 = 10, 41, T0 + 6, BOT - 3
    seamcol = [FIRE[3], FIRE[2], FIRE[3], FIRE[4]][frame % 4]
    for y in range(dy0 - 1, dy1 + 2):
        c.px(dx0 - 1, y, seamcol); c.px(dx1 + 1, y, seamcol)
    c.hline(dx0 - 1, dx1 + 1, dy0 - 1, seamcol); c.hline(dx0 - 1, dx1 + 1, dy1 + 1, seamcol)
    face(c, dx0, dy0, dx1, dy1, STEEL, lit_rows=1, right=3)
    window(c, 13, dy0 + 2, 38, dy0 + 22)
    flames(c, 15, dy0 + 4, 36, dy0 + 17, frame, n_frames=8)
    for x in range(16, 36):                                                             # crucible
        c.px(x, dy0 + 18, FIRE[0] if (x + frame) % 3 else FIRE[1]); c.px(x, dy0 + 19, DARK[2]); c.px(x, dy0 + 20, DARK[3])
    seam(c, dx0, dx1, dy1 - 5, STEEL)
    face(c, dx1 - 4, dy0 + 9, dx1 - 2, dy0 + 14, BRASS + [BRASS[3]], lit_rows=1, right=1)
    for y in (dy0 + 2, dy1 - 3):
        c.rect(dx0 - 2, y, dx0, y + 2, STEEL[2]); c.px(dx0 - 2, y, STEEL[0]); c.px(dx0, y + 2, STEEL[4])
    # extraction hood and duct above
    for y in range(18, T0):
        k = (y - 18) / (T0 - 18)
        x0 = round(20 - k * 14); x1 = round(35 + k * 13)
        for x in range(x0, x1 + 1):
            r = y - 18
            t = 0 if r < 2 else 1 if r < 9 else 2
            if x > x1 - 3: t += 1
            if x == x0: t = max(0, t - 1)
            c.px(x, y, STEEL[min(4, t)])
    c.hline(6, 48, T0 - 1, DARK[3])
    post(c, 22, 33, 0, 17)
    for y in (4, 5):
        for x in range(21, 35): c.px(x, y, cyl(x, 21, 34, BRASS) if y == 4 else BRASS[3])
    for y in (12, 13):
        for x in range(21, 35): c.px(x, y, cyl(x, 21, 34, TEALR) if y == 12 else TEALR[3])
    # control panel on the right side
    face(c, X1 + 1, T0 + 8, X1 + 4, T0 + 20, DARK, lit_rows=1, right=1)
    c.px(X1 + 2, T0 + 11, GREEN); c.px(X1 + 2, T0 + 14, BRASS[0] if frame % 2 else BRASS[2]); c.px(X1 + 2, T0 + 17, RED)
    c.outline()
    return c


def eng_furnace_glow():
    g = C(56, 88)
    cx, cy = 25, 52
    for y in range(88):
        for x in range(56):
            d = ((x - cx) / 18) ** 2 + ((y - cy) / 16) ** 2
            if d < 1: g.px(x, y, (255, 200, 130, int(140 * (1 - d) ** 1.6)))
    return g


PIECES = {
    "lamp_post": lamp_post, "signpost": signpost, "mailbox": mailbox, "mailbox_n": lambda: mailbox(back=True),
    "stanchion": stanchion, "hazard_sign": hazard_sign, "bin": bin_, "bollard_light": bollard_light,
    "telescope": telescope, "table": table, "cafe_table": cafe_table, "bar_table": lambda: cafe_table(tall=True),
    "fridge": __import__("style_v2_demo").fridge,
}
ANIMATED = {"furnace": (eng_furnace, 8)}
GLOWS = {"furnace": eng_furnace_glow}

if __name__ == "__main__":
    repo = sys.argv[1]
    want = sys.argv[2:] or list(PIECES) + list(ANIMATED)
    lunar = os.path.join(repo, "art/lunar")
    for n in want:
        if n in PIECES:
            PIECES[n]().save(os.path.join(lunar, n + ".png"))
        elif n in ANIMATED:
            fn, k = ANIMATED[n]
            fn(0).save(os.path.join(lunar, n + ".png"))
            strip([fn(i) for i in range(k)]).save(os.path.join(lunar, "anim", n + ".png"))
        if n in GLOWS:
            GLOWS[n]().save(os.path.join(lunar, n + "_glow.png"))
    print("ok", len(want))
