"""Home furnace, manufacturing hub and storage chest for Echo Landing (23 Nov 2026).

Original art in the station's prop style: three-quarter view, lit top planes, each face shaded top to
bottom in 3-4 tones, darker right side, outline #5b332d with #3a2026 under and right. Run:
    python3 home_machines.py <repo>      -> art/lunar/home_furnace.png (+ anim strip, glow), home_hub.png, home_chest.png
"""
import sys, os
import numpy as np
from PIL import Image

def H(s): return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)

OUT, OUT_D = H("4a2430"), H("2e1a2a")
STEEL = [H("ebe3e6"), H("bdb5cb"), H("8f88a8"), H("645d82"), H("443e60")]   # warm "C" style: cream light, purple dark
WOOD = [H("f6c879"), H("dc9a4c"), H("b46a35"), H("8a4a2b"), H("5e2f26")]
BRASS = [H("fff6c4"), H("ffd970"), H("e7a83c"), H("b86f2a")]
FIRE = [H("fff6d0"), H("fff0a0"), H("edc65a"), H("ee8f3e"), H("c8602f"), H("8a3a2a")]
COPPER = [H("ffb27a"), H("ef8442"), H("c45a32"), H("8a3a2e")]
TEAL = [H("8ad6c0"), H("55b0a6"), H("37868f"), H("2c5e76"), H("2b3c61")]
CREAM = [H("fffbea"), H("f4e6c4"), H("dcc49e"), H("b5967e")]
RED = H("e8574a")
GREEN = H("7dff9a")
CLEAR = (0, 0, 0, 0)


class C:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.a = np.zeros((h, w, 4), np.uint8)

    def px(s, x, y, c):
        if 0 <= x < s.w and 0 <= y < s.h:
            s.a[y, x] = c

    def get(s, x, y):
        return tuple(s.a[y, x]) if 0 <= x < s.w and 0 <= y < s.h else CLEAR

    def rect(s, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                s.px(x, y, c)

    def hline(s, x0, x1, y, c):
        s.rect(x0, y, x1, y, c)

    def vline(s, x, y0, y1, c):
        s.rect(x, y0, x, y1, c)

    def outline(s):
        a = s.a
        solid = a[:, :, 3] > 0
        out = np.zeros_like(a)
        for y in range(s.h):
            for x in range(s.w):
                if solid[y, x]:
                    continue
                n = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                hit = [(nx, ny) for nx, ny in n if 0 <= nx < s.w and 0 <= ny < s.h and solid[ny, nx]]
                if hit:
                    # under or right of the shape: the darker line
                    dark = any(ny < y or nx < x for nx, ny in hit) and not any(ny > y for nx, ny in hit)
                    out[y, x] = OUT_D if dark else OUT
        m = out[:, :, 3] > 0
        a[m] = out[m]

    def save(s, path):
        Image.fromarray(s.a, "RGBA").save(path)


def band(ramp, t):
    """t 0 (lit) .. 1 (dark) -> a colour from the ramp."""
    i = min(len(ramp) - 1, max(0, int(round(t * (len(ramp) - 1)))))
    return ramp[i]


def cyl(x, x0, x1, ramp, hi=0.28):
    """Column shading across a cylinder lit from the upper left: brightest at `hi` of the width."""
    u = (x - x0) / max(1, x1 - x0)
    if u < hi:
        t = (hi - u) / hi * 0.55
    else:
        t = (u - hi) / (1 - hi)
    return band(ramp, t)


# ------------------------------------------------------------------ storage chest (24 x 24, one tile)
def chest(c, ox=0, oy=0, body=WOOD, metal=STEEL):
    P = lambda x, y, col: c.px(ox + x, oy + y, col)
    # lid: rounded top, two planks; body: three planks; darker to the right and toward the bottom
    for y in range(2, 22):
        if y == 2: xs = range(4, 20)
        elif y == 3: xs = range(2, 22)
        else: xs = range(1, 23)
        for x in xs:
            right = x >= 20
            if y <= 3: t = 0           # lit top of the lid
            elif y <= 6: t = 1
            elif y == 7: t = 3         # seam
            elif y <= 9: t = 2
            elif y == 10: t = 4        # lid lip shadow
            elif y == 11: t = 3        # shadow under the lid
            elif y <= 14: t = 1 if y == 12 else 2
            elif y == 15: t = 3
            elif y <= 18: t = 2 if y == 16 else 3
            elif y == 19: t = 4
            elif y <= 20: t = 3
            else: t = 4
            if right: t = min(4, t + 1)
            if x == 1 and 3 < y < 21 and t < 4: t = max(0, t - 1)
            P(x, y, body[t])
    # plank grain flecks
    for x, y in [(8, 5), (14, 8), (9, 13), (15, 17), (7, 18), (12, 4)]:
        P(x, y, body[min(4, 3)])
    # steel bands round lid and body
    for bx in (4, 17):
        for y in range(2 if bx == 4 else 2, 22):
            if y == 2 and bx == 4: continue
            for k in range(3):
                t = k + (1 if y >= 11 else 0) + (0 if y > 3 else -1)
                if y == 10: t = 4
                P(bx + k, y, metal[max(0, min(4, t))])
        for y in (5, 14, 18):
            P(bx + 1, y, metal[0])
    # brass latch
    for y in range(8, 14):
        for x in range(10, 14):
            t = 1 if y < 10 else 2
            if x == 13: t = 3
            P(x, y, BRASS[t])
    P(10, 8, BRASS[0]); P(11, 8, BRASS[0])
    P(11, 11, STEEL[4]); P(12, 11, STEEL[4]); P(11, 12, STEEL[4])
    # little steel feet
    for x in (2, 3, 4, 19, 20, 21):
        P(x, 22, metal[3 if x < 19 else 4])


# ------------------------------------------------------------------ shading helpers (the chest's look)
def face(c, x0, y0, x1, y1, ramp, lit_rows=1, right=3, left_hi=True, skip=None):
    """A face shaded like the chest: lit top row(s), then bands darker toward the bottom, right columns a step
    darker, a lit left column. ramp is light -> dark (5 tones)."""
    h = y1 - y0
    for y in range(y0, y1 + 1):
        r = y - y0
        if r < lit_rows: t = 0
        elif r <= h * 0.6: t = 1
        elif r < h: t = 2
        else: t = 3
        for x in range(x0, x1 + 1):
            if skip and skip(x, y): continue
            tt = t
            if x > x1 - right: tt += 1
            elif x == x0 and left_hi and 0 < r < h: tt = max(0, tt - 1)
            if left_hi and right and x == x1 and 0 < r: tt += 1          # bevel: a dark inner right edge
            c.px(x, y, ramp[min(len(ramp) - 1, tt)])


def seam(c, x0, x1, y, ramp):
    """A panel seam: a dark line with a lit line under it, as between the chest's planks."""
    for x in range(x0, x1 + 1):
        c.px(x, y, ramp[-1]); c.px(x, y + 1, ramp[1] if c.get(x, y + 1)[3] else CLEAR)


def bar_v(c, x, y0, y1, ramp, w=3):
    """A vertical metal band shaded across its width, like the chest's straps."""
    for y in range(y0, y1 + 1):
        for k in range(w):
            t = k + (1 if y > (y0 + y1) // 2 else 0)
            c.px(x + k, y, ramp[min(len(ramp) - 1, t)])


HULL = [H("fffbea"), H("f4e6c4"), H("dcc49e"), H("b5967e"), H("8a7080")]     # cream armour panels
DARK = [H("6a6488"), H("4c4668"), H("3a3456"), H("2c2744"), H("211c33")]
CYAN = [H("ffffff"), H("c4f4ff"), H("8fd3ff"), H("4a9be0"), H("2f5cab")]
GLASS = [H("6fd6e0"), H("3a8fb0"), H("2b5a85"), H("23365c")]


# ------------------------------------------------------------------ electric furnace (48 x 60, two tiles)
# Zachary: "it is a electric furnace so no coal. just make an electric furnace" (the plasma one was too sci-fi).
def furnace(frame=0, lit=True):
    c = C(48, 60)
    B = 57
    # plinth with feet
    face(c, 2, B - 8, 43, B - 7, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 2, B - 6, 43, B - 2, DARK, lit_rows=1, right=4)
    for x in range(5, 41, 5):
        c.px(x, B - 4, STEEL[1]); c.px(x + 1, B - 3, DARK[4])
    for x in (3, 4, 5, 6, 39, 40, 41, 42):
        c.px(x, B - 1, DARK[4])
    # body: a heavy steel box. Lit top plane, banded front, darker right side face
    X0, X1, T0, BOT = 5, 35, 15, B - 9
    face(c, X0 + 1, T0, X1 - 1, T0 + 2, STEEL, lit_rows=1, right=0, left_hi=False)     # top plane
    for x in range(X0 + 3, X0 + 13, 2):                                                 # vent slots on top
        c.px(x, T0 + 1, DARK[3])
    face(c, X0, T0 + 3, X1, BOT, STEEL, lit_rows=1, right=0)                            # front
    seam(c, X0, X1, T0 + 3, STEEL)
    face(c, X1 + 1, T0 + 1, X1 + 3, BOT, STEEL[2:] + [DARK[3], DARK[4]], lit_rows=0, right=0, left_hi=False)
    # corner straps with rivets, like the chest
    for bx in (X0, X1 - 2):
        bar_v(c, bx, T0 + 3, BOT, [STEEL[1], STEEL[2], STEEL[3], STEEL[4], DARK[3]], w=3)
        for y in (T0 + 6, (T0 + BOT) // 2, BOT - 3):
            c.px(bx + 1, y, STEEL[0])
    # the door: a raised panel, banded, with a viewport and a brass latch
    dx0, dx1, dy0, dy1 = 10, 29, T0 + 6, BOT - 3
    glow_seam = [FIRE[3], FIRE[2], FIRE[3]][frame % 3] if lit else DARK[3]
    for y in range(dy0 - 1, dy1 + 2):
        for x in (dx0 - 1, dx1 + 1):
            c.px(x, y, glow_seam)
    for x in range(dx0 - 1, dx1 + 2):
        c.px(x, dy0 - 1, glow_seam); c.px(x, dy1 + 1, glow_seam)
    face(c, dx0, dy0, dx1, dy1, STEEL, lit_rows=1, right=3)
    seam(c, dx0, dx1, dy1 - 5, STEEL)
    # viewport: big, so you can watch the flames (Zachary: "make the window bigger to see the flame")
    vx0, vx1, vy0, vy1 = 12, 25, dy0 + 2, dy0 + 16
    import math
    for y in range(vy0, vy1 + 1):
        for x in range(vx0, vx1 + 1):
            if (y in (vy0, vy1)) and (x in (vx0, vx1)): continue
            if x in (vx0, vx1) or y in (vy0, vy1):
                c.px(x, y, DARK[1] if (y == vy0 or x == vx0) else DARK[3])
            elif x in (vx0 + 1, vx1 - 1) or y in (vy0 + 1, vy1 - 1):
                c.px(x, y, DARK[4] if (y == vy0 + 1 or x == vx0 + 1) else DARK[2])
            elif not lit:
                c.px(x, y, DARK[2] if y < (vy0 + vy1) // 2 else DARK[3])
    ix0, ix1, iy0, iy1 = vx0 + 2, vx1 - 2, vy0 + 2, vy1 - 2
    floor_y = iy1 - 2            # the crucible's rim
    if lit:
        span = floor_y - iy0
        for x in range(ix0, ix1 + 1):
            # flame tongues: each column's height wobbles with the frame
            hgt = span * (0.55 + 0.35 * math.sin(x * 1.7 + frame * 2.1) * math.sin(x * 0.9 - frame * 1.3 + 1.0))
            hgt += 2 if (x - ix0) in (3, 4, 7, 8) else 0
            for y in range(iy0, floor_y + 1):
                up = floor_y - y
                if up > hgt: col = FIRE[5] if (x + y + frame) % 5 else H("5a2a26")
                elif up > hgt * 0.75: col = FIRE[4]
                elif up > hgt * 0.45: col = FIRE[3]
                elif up > hgt * 0.2: col = FIRE[2]
                else: col = FIRE[1]
                c.px(x, y, col)
        for k in range(2):                                 # sparks
            sx = ix0 + (3 + k * 5 + frame * 3) % (ix1 - ix0 + 1)
            sy = iy0 + (1 + k * 2 + frame) % 3
            c.px(sx, sy, FIRE[1])
    else:
        for i in range(6):                                 # reflection on the cold glass
            c.px(ix0 + i, iy0 + 5 - i, STEEL[2]); c.px(ix0 + 1 + i, iy0 + 5 - i, STEEL[3])
    # the crucible
    for x in range(ix0 + 1, ix1):
        c.px(x, floor_y + 1, (FIRE[0] if (x + frame) % 3 else FIRE[1]) if lit else DARK[1])
        c.px(x, floor_y + 2, DARK[2])
    c.px(ix0, floor_y + 1, DARK[2]); c.px(ix1, floor_y + 1, DARK[3])
    # latch handle, beside the window
    face(c, dx1 - 3, vy0 + 5, dx1 - 2, vy0 + 9, BRASS + [BRASS[3]], lit_rows=1, right=1)
    c.px(dx1 - 4, vy0 + 7, BRASS[3])
    # hinges on the left of the door
    for y in (dy0 + 2, dy1 - 3):
        c.rect(dx0 - 2, y, dx0, y + 2, STEEL[2]); c.px(dx0 - 2, y, STEEL[0]); c.px(dx0, y + 2, STEEL[4])
    # small hazard plate with a lightning bolt on the lower door
    for y in range(dy1 - 4, dy1):
        for x in range(dx0 + 3, dx0 + 8):
            c.px(x, y, BRASS[1] if y < dy1 - 2 else BRASS[2])
    for (x, y) in [(dx0 + 6, dy1 - 4), (dx0 + 5, dy1 - 3), (dx0 + 6, dy1 - 3), (dx0 + 5, dy1 - 2), (dx0 + 4, dy1 - 1)]:
        c.px(x, y, DARK[4])
    # control box on the top: a dial and two lamps
    cx0, cx1, cy0, cy1 = 22, 34, 6, T0
    face(c, cx0, cy0, cx1, cy0 + 1, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, cx0, cy0 + 2, cx1, cy1, DARK, lit_rows=1, right=2)
    c.hline(cx0, cx1, cy0 + 2, STEEL[3])
    gx, gy = cx0 + 2, cy0 + 3
    for y in range(gy, gy + 5):
        for x in range(gx, gx + 5):
            if (x - gx - 2) ** 2 + (y - gy - 2) ** 2 <= 5:
                c.px(x, y, CREAM[0] if y - gy < 2 else CREAM[1] if y - gy < 4 else CREAM[2])
    c.px(gx + 2, gy + 2, DARK[4])
    c.px(gx + 3 if lit else gx + 1, gy + 1, RED)
    on_blink = lit and frame != 1
    c.px(cx1 - 3, gy + 1, GREEN if lit else DARK[1]); c.px(cx1 - 3, gy + 3, RED if not lit else (BRASS[0] if on_blink else BRASS[2]))
    # power cable: from the right side, down to the floor and into a socket
    for y in range(T0 + 8, B - 2):
        c.px(X1 + 4, y, DARK[1]); c.px(X1 + 5, y, DARK[2]); c.px(X1 + 6, y, DARK[4])
    for y in (T0 + 12, T0 + 13):
        c.hline(X1 + 4, X1 + 6, y, BRASS[1])
    face(c, X1 + 3, T0 + 6, X1 + 7, T0 + 8, STEEL, lit_rows=1, right=1)
    face(c, X1 + 3, B - 3, X1 + 8, B - 1, STEEL, lit_rows=1, right=2)
    c.outline()
    return c


def furnace_glow():
    g = C(48, 60)
    cx, cy = 19, 30
    for y in range(60):
        for x in range(48):
            d = ((x - cx) / 13) ** 2 + ((y - cy) / 12) ** 2
            if d < 1:
                g.px(x, y, (255, 200, 130, int(140 * (1 - d) ** 1.6)))
    return g


# ------------------------------------------------------------------ manufacturing hub (72 x 64, three tiles)
def hub():
    c = C(72, 64)
    B = 61
    # back panel in steel-teal with banded shading, framed by shaded posts and a riveted top rail
    px0, px1, py0, py1 = 7, 62, 5, 31
    face(c, px0, py0, px1, py1, [H("55b0a6"), H("37868f"), H("2c5e76"), H("2b3c61"), H("2a2647")], lit_rows=1, right=3)
    for y in (py0 + 9, py0 + 18):
        seam(c, px0, px1, y, [H("55b0a6"), H("37868f"), H("2c5e76"), H("2b3c61"), H("2a2647")])
    for x in (px0 - 2, px1 - 1):
        bar_v(c, x, py0 - 2, py1 + 3, STEEL, w=3)
    face(c, px0 - 2, py0 - 3, px1 + 1, py0 - 1, STEEL, lit_rows=1, right=2)
    for x in range(px0 + 2, px1, 8):
        c.px(x, py0 - 2, STEEL[0])
    # tools hanging on the panel, each with a lit and a shaded side
    for y in range(9, 19):                      # wrench
        c.px(14, y, STEEL[0]); c.px(15, y, STEEL[2])
    c.rect(12, 8, 17, 9, STEEL[1]); c.px(14, 8, H("37868f")); c.px(15, 8, H("37868f")); c.hline(12, 17, 10, STEEL[3])
    for y in range(9, 14):                      # screwdriver
        c.px(21, y, RED); c.px(22, y, H("a8362e"))
    for y in range(14, 19):
        c.px(21, y, STEEL[0]); c.px(22, y, STEEL[2])
    face(c, 26, 8, 32, 10, STEEL, lit_rows=1, right=2)   # hammer
    for y in range(11, 19):
        c.px(28, y, WOOD[1]); c.px(29, y, WOOD[3])
    for k, (x, y) in enumerate([(52, 9), (53, 8), (54, 8), (55, 9), (56, 10), (56, 11), (55, 12),  # coil of wire
                                (54, 13), (53, 13), (52, 12), (51, 11), (51, 10)]):
        c.px(x, y, COPPER[0] if y < 11 else COPPER[2])
    c.rect(52, 10, 55, 12, COPPER[1]); c.px(52, 10, COPPER[0])
    # screen: bevelled frame and a glass gradient
    face(c, 9, 15, 25, 27, DARK, lit_rows=1, right=2)
    for y in range(17, 26):
        for x in range(11, 24):
            c.px(x, y, GLASS[0] if y < 19 else GLASS[1] if y < 23 else GLASS[2])
    for y, w in [(18, 9), (20, 6), (22, 8)]:
        c.hline(12, 12 + w, y, CYAN[2])
    c.px(22, 18, GREEN); c.hline(11, 14, 17, CYAN[1])
    # worktop: like the chest lid, lit top rows, plank front, dark lip, shadow under it
    tx0, tx1, ty = 2, 69, 32
    face(c, tx0, ty, tx1, ty + 2, WOOD, lit_rows=1, right=0, left_hi=False,
         skip=lambda x, y: y == ty and x in (tx0, tx1))
    face(c, tx0, ty + 3, tx1, ty + 6, WOOD[1:], lit_rows=1, right=4)
    for x in range(tx0 + 6, tx1, 12):
        c.px(x, ty + 4, WOOD[3]); c.px(x, ty + 5, WOOD[3])
    c.hline(tx0, tx1, ty + 7, WOOD[4])
    c.hline(tx0 + 1, tx1 - 1, ty + 8, DARK[4])
    # steel straps over the worktop ends, like the chest's bands
    for x in (tx0 + 3, tx1 - 5):
        bar_v(c, x, ty, ty + 7, STEEL, w=3)
        c.px(x + 1, ty + 2, STEEL[0]); c.px(x + 1, ty + 5, STEEL[0])
    # cabinet: banded steel, three drawers with lit top edges and brass pulls
    cy0 = ty + 9
    face(c, tx0 + 2, cy0, tx1 - 2, B - 2, STEEL, lit_rows=0, right=4)
    for i in range(3):
        dx0 = tx0 + 5 + i * 21
        face(c, dx0, cy0 + 2, dx0 + 17, B - 5, STEEL, lit_rows=1, right=2)
        c.hline(dx0, dx0 + 17, B - 4, DARK[3])
        mid = (cy0 + 2 + B - 5) // 2
        c.hline(dx0 + 6, dx0 + 11, mid, BRASS[1]); c.hline(dx0 + 6, dx0 + 11, mid + 1, BRASS[3])
        c.px(dx0 + 6, mid, BRASS[0]); c.px(dx0 + 11, mid + 1, BRASS[3])
    for x in (tx0 + 2, tx0 + 3, tx0 + 4, tx1 - 4, tx1 - 3, tx1 - 2):
        c.px(x, B - 1, DARK[3]); c.px(x, B, DARK[4])
    # robot arm: shaded base, two copper segments lit on top, steel joints
    bx = 39
    face(c, bx - 4, ty - 4, bx + 4, ty - 1, STEEL, lit_rows=1, right=2)
    def seg(xa, ya, xb, yb):
        n = max(abs(xb - xa), abs(yb - ya))
        for i in range(n + 1):
            x = round(xa + (xb - xa) * i / n); y = round(ya + (yb - ya) * i / n)
            c.px(x - 1, y, COPPER[0]); c.px(x, y, COPPER[1]); c.px(x + 1, y, COPPER[2]); c.px(x, y + 1, COPPER[3])
    seg(bx, ty - 5, bx - 6, 15)
    seg(bx - 6, 15, bx + 10, 13)
    for (jx, jy) in [(bx, ty - 5), (bx - 6, 15), (bx + 10, 13)]:
        c.rect(jx - 1, jy - 1, jx + 1, jy + 1, STEEL[2]); c.px(jx - 1, jy - 1, STEEL[0]); c.px(jx, jy - 1, STEEL[1])
        c.px(jx + 1, jy + 1, STEEL[4]); c.px(jx, jy + 1, STEEL[3])
    gx = bx + 10
    bar_v(c, gx - 1, 15, 21, STEEL, w=3)
    c.rect(gx - 3, 22, gx - 2, 24, STEEL[1]); c.rect(gx + 2, 22, gx + 3, 24, STEEL[3])
    c.px(gx, 25, CYAN[0]); c.px(gx + 1, 26, CYAN[1]); c.px(gx - 1, 26, CYAN[2])   # welding arc
    # parts on the bench, each a little box with a lit top and dark side
    face(c, gx - 4, ty - 3, gx + 4, ty - 1, [H("8ad6c0"), H("55b0a6"), H("37868f"), H("2c5e76"), H("2b3c61")], lit_rows=1, right=2)
    face(c, 54, ty - 5, 61, ty - 1, STEEL, lit_rows=1, right=2)
    c.hline(56, 59, ty - 6, COPPER[1]); c.px(56, ty - 6, COPPER[0])
    face(c, 8, ty - 3, 13, ty - 1, HULL, lit_rows=1, right=2)
    c.px(10, ty - 2, CYAN[2])
    # status lamps on the top rail
    c.px(px1 - 4, py0 - 2, GREEN); c.px(px1 - 7, py0 - 2, BRASS[0]); c.px(px1 - 10, py0 - 2, RED)
    c.outline()
    return c


def strip(frames):
    w, h = frames[0].w, frames[0].h
    s = C(w * len(frames), h)
    for i, f in enumerate(frames):
        s.a[:, i * w:(i + 1) * w] = f.a
    return s


if __name__ == "__main__":
    repo = sys.argv[1]
    lunar = os.path.join(repo, "art/lunar")
    furnace(0, lit=False).save(os.path.join(lunar, "home_furnace.png"))
    strip([furnace(i) for i in range(3)]).save(os.path.join(lunar, "home_furnace_on.png"))
    furnace_glow().save(os.path.join(lunar, "home_furnace_glow.png"))
    hub().save(os.path.join(lunar, "home_hub.png"))
    ch = C(24, 24); chest(ch); ch.outline(); ch.save(os.path.join(lunar, "home_chest.png"))
    print("ok")


# ------------------------------------------------------------------ spaceport comms beacon (72 x 120, eight frames)
# Zachary, 23 Nov: the old lattice mast "looked like an ocean bouey; get rid of that or remake it".
def beacon(frame=0):
    import math
    c = C(72, 120)
    B = 117
    # plinth: lit top plane, banded front, hazard stripe, a hatch, feet
    face(c, 8, B - 20, 63, B - 18, STEEL, lit_rows=1, right=0, left_hi=False)
    face(c, 6, B - 17, 65, B - 3, STEEL, lit_rows=1, right=5)
    seam(c, 6, 65, B - 17, STEEL)
    for x in range(9, 63):
        if (x // 4) % 2 == 0: c.px(x, B - 6, BRASS[1]); c.px(x, B - 5, BRASS[2])
        else: c.px(x, B - 6, DARK[3]); c.px(x, B - 5, DARK[4])
    face(c, 14, B - 14, 27, B - 9, DARK, lit_rows=1, right=2)       # hatch
    c.hline(18, 23, B - 12, BRASS[1]); c.px(18, B - 12, BRASS[0])
    for x in (9, 30, 41, 62):
        c.px(x, B - 15, STEEL[0]); c.px(x + 1, B - 14, STEEL[3])
    face(c, 44, B - 14, 58, B - 9, DARK, lit_rows=1, right=2)       # status panel with lamps
    for i, col in enumerate([GREEN, BRASS[0], CYAN[2]]):
        on = (frame + i) % 4 != 0
        c.px(47 + i * 4, B - 12, col if on else DARK[1])
    for x in (7, 8, 9, 10, 61, 62, 63, 64):
        c.px(x, B - 2, DARK[4]); c.px(x, B - 1, DARK[4])
    # mast: a steel tube shaded across its width, with teal collars and a ladder
    mx0, mx1, top = 31, 40, 26
    for y in range(top, B - 19):
        for x in range(mx0, mx1 + 1):
            c.px(x, y, cyl(x, mx0, mx1, STEEL))
    for cy in (40, 60, 80):
        for y in (cy, cy + 1, cy + 2):
            for x in range(mx0 - 1, mx1 + 2):
                col = cyl(x, mx0 - 1, mx1 + 1, [H("8ad6c0"), H("55b0a6"), H("37868f"), H("2c5e76"), H("2b3c61")])
                if y == cy + 2: col = H("2b3c61") if x > mx1 - 2 else H("2c5e76")
                c.px(x, y, col)
        c.px(mx0, cy + 1, STEEL[0])
    for y in range(top + 4, B - 20):                                 # ladder on the left
        c.px(mx0 - 3, y, STEEL[2]); c.px(mx0 - 2, y, STEEL[3]) if y % 5 else None
        if y % 5 == 0: c.hline(mx0 - 3, mx0 - 1, y, STEEL[1])
    for y in range(top + 6, B - 20):                                 # cable down the right
        c.px(mx1 + 2, y, DARK[2]); c.px(mx1 + 3, y, DARK[4])
    # dish on an arm, facing up and right
    c.hline(mx1 + 1, mx1 + 8, 66, STEEL[2]); c.hline(mx1 + 1, mx1 + 8, 67, STEEL[4]); c.hline(mx1 + 1, mx1 + 8, 65, STEEL[1])
    dcx, dcy = 54, 58
    for y in range(44, 72):
        for x in range(42, 68):
            # an ellipse tipped toward the upper right
            u, v = x - dcx, y - dcy
            a = math.radians(-35)
            ru = u * math.cos(a) - v * math.sin(a); rv = u * math.sin(a) + v * math.cos(a)
            d = (ru / 12.5) ** 2 + (rv / 6.0) ** 2
            if d <= 1:
                if d > 0.78: col = CREAM[3] if rv > 0 else CREAM[1]          # rim: lit above, shaded below
                elif rv < -1: col = CREAM[2]                                  # inside of the bowl, in shadow
                elif rv < 2: col = CREAM[1]
                else: col = CREAM[0]
                c.px(x, y, col)
    for i in range(7):                                                # feed arm to the horn
        c.px(54 + i, 58 - i, STEEL[2]); c.px(55 + i, 58 - i, STEEL[3])
    c.rect(60, 49, 62, 51, BRASS[2]); c.px(60, 49, BRASS[0])
    # antenna crossbar with whips and blinking tips
    face(c, 18, top - 3, 53, top - 1, STEEL, lit_rows=1, right=3)
    for ax, h in ((20, 10), (26, 7), (45, 7), (51, 10)):
        c.vline(ax, top - 3 - h, top - 4, STEEL[1]); c.vline(ax + 1, top - 3 - h, top - 4, STEEL[3])
        blink = (frame // 2 + (ax // 6)) % 2 == 0
        c.px(ax, top - 4 - h, RED if blink else H("6e2a2a")); c.px(ax + 1, top - 4 - h, RED if blink else H("6e2a2a"))
    # beacon lamp housing on top: a capped glass cylinder with a turning light
    lx0, lx1, ly0, ly1 = 30, 41, 8, 22
    face(c, lx0 - 1, ly1, lx1 + 1, ly1 + 3, STEEL, lit_rows=1, right=3)
    face(c, lx0, ly0 - 3, lx1, ly0 - 1, STEEL, lit_rows=1, right=2)
    c.hline(lx0 + 3, lx1 - 3, ly0 - 4, STEEL[1])
    c.px(35, ly0 - 6, STEEL[1]); c.px(36, ly0 - 6, STEEL[2]); c.px(35, ly0 - 5, STEEL[2]); c.px(36, ly0 - 5, STEEL[3])
    beam = frame % 8                     # the lit band sweeps across the glass
    for y in range(ly0, ly1):
        for x in range(lx0, lx1 + 1):
            u = (x - lx0) / (lx1 - lx0)
            near = abs(u * 7 - beam) < 1.3 or abs(u * 7 - beam + 8) < 1.3
            if x in (lx0, lx1) or y in (ly0, ly1 - 1):
                c.px(x, y, DARK[1] if x == lx0 or y == ly0 else DARK[3])
            elif near:
                c.px(x, y, H("fff6d0") if 10 < y < 19 else H("ffd0a0"))
            else:
                c.px(x, y, H("d24b3c") if u < 0.75 else H("a8362e"))
        c.px(lx0 + 2, y, H("ffb0a0") if ly0 < y < ly1 - 1 and not (abs(2 / 11 * 7 - beam) < 1.3) else c.get(lx0 + 2, y))
    for y in (ly0 + 4, ly0 + 9):                                     # guard bars
        c.hline(lx0, lx1, y, DARK[3])
    c.outline()
    return c


def beacon_strip():
    return strip([beacon(i) for i in range(8)])


def wear(c, x0, y0, x1, y1, ramp, seed=1, n=6):
    """Scuffs and chips: a lit pixel beside a dark one, scattered over a face (only on pixels already drawn)."""
    r = (seed * 2654435761) & 0x7fffffff
    for _ in range(n):
        r = (r * 1103515245 + 12345) & 0x7fffffff
        x = x0 + r % max(1, x1 - x0)
        r = (r * 1103515245 + 12345) & 0x7fffffff
        y = y0 + r % max(1, y1 - y0)
        if c.get(x, y)[3] and c.get(x + 1, y)[3]:
            c.px(x, y, ramp[0]); c.px(x + 1, y, ramp[min(len(ramp) - 1, 3)])
