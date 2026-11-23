"""Couches in the warm C style (Zachary 23 Nov: "i dont like the couches they can be redone"). Same sizes and seat
heights as before (main.gd SEATS: sofa hips at y 18, armchair 19, view_bench 22)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home_machines import C, H
from style_v2_demo import outline, STEEL, BRASS, CREAMH

VEL = [H("bdf0d6"), H("86d4bc"), H("55b0a6"), H("3a8a92"), H("2d627a"), H("2b3f63"), H("2a2647")]   # teal velvet
WOODF = [H("f6c879"), H("dc9a4c"), H("b46a35"), H("8a4a2b"), H("5e2f26")]
ROSE = [H("ffd6c4"), H("ffa38a"), H("e86a62"), H("b84652"), H("7e2a42")]


def rounded(c, x0, y0, x1, y1, ramp, top_t=1, mid_t=2, low_t=3, corner=1, rim=True, side_dark=0):
    """A soft padded block: rounded corners, lit rim on top, mid tone, darker lower third, darker right edge."""
    h = y1 - y0
    for y in range(y0, y1 + 1):
        r = y - y0
        for x in range(x0, x1 + 1):
            if corner and r < corner and (x - x0 < corner - r or x1 - x < corner - r): continue
            if corner and h - r < corner and (x - x0 < corner - (h - r) or x1 - x < corner - (h - r)): continue
            t = top_t if r <= max(1, h // 4) else mid_t if r <= h * 0.66 else low_t
            if x >= x1 - side_dark: t += 1
            if x == x0 and 0 < r < h: t = max(0, t - 1)
            c.px(x, y, ramp[min(len(ramp) - 1, t)])
    if rim:
        for x in range(x0 + corner, x1 - corner + 1):
            c.px(x, y0, ramp[0])


def tufts(c, x0, x1, ys, ramp):
    for y in ys:
        for x in range(x0, x1 + 1, 5):
            c.px(x, y, ramp[5]); c.px(x, y - 1, ramp[1])


def couch(w, seats, back_top=3, seat_top=16):
    c = C(w, 34)
    X0, X1 = 1, w - 2
    # back: one long padded block, cushions in front of it
    rounded(c, X0 + 3, back_top, X1 - 3, seat_top, VEL, top_t=2, mid_t=3, low_t=4, corner=2, side_dark=1)
    cw = (X1 - X0 - 14) // seats
    for i in range(seats):
        bx0 = X0 + 7 + i * cw; bx1 = bx0 + cw - 1
        rounded(c, bx0, back_top + 2, bx1, seat_top - 1, VEL, top_t=1, mid_t=2, low_t=4, corner=2)
        tufts(c, bx0 + 3, bx1 - 2, (back_top + 6, back_top + 10), VEL)
        c.hline(bx0 + 1, bx1 - 1, seat_top - 1, VEL[5])                       # shadow where back meets seat
        # seat cushion: lit top surface, a dark seam, then the cushion's front face in shade
        rounded(c, bx0, seat_top, bx1, seat_top + 7, VEL, top_t=1, mid_t=2, low_t=4, corner=1, side_dark=0)
        for x in range(bx0 + 1, bx1):
            c.px(x, seat_top + 3, VEL[4]); c.px(x, seat_top + 4, VEL[3])
        c.vline(bx1, seat_top + 1, seat_top + 7, VEL[5])
    # arms: rounded, lit tops, the right one in shade
    rounded(c, X0, back_top + 6, X0 + 6, seat_top + 11, VEL, top_t=1, mid_t=3, low_t=4, corner=2)
    rounded(c, X1 - 6, back_top + 6, X1, seat_top + 11, VEL, top_t=2, mid_t=4, low_t=5, corner=2, side_dark=1)
    c.vline(X0 + 6, back_top + 9, seat_top + 9, VEL[5])                          # inner face of the left arm
    c.vline(X1 - 6, back_top + 9, seat_top + 9, VEL[4])
    # base skirt and wooden feet
    for y in range(seat_top + 8, seat_top + 12):
        for x in range(X0 + 6, X1 - 5):
            c.px(x, y, VEL[5] if y < seat_top + 11 else VEL[6])
    c.hline(X0 + 6, X1 - 6, seat_top + 8, VEL[4])
    for fx in (X0 + 2, X1 - 3):
        for y in range(seat_top + 12, 33):
            c.px(fx, y, WOODF[1]); c.px(fx + 1, y, WOODF[3])
    return c


def pillow(c, x0, y0):
    for y in range(y0, y0 + 7):
        for x in range(x0, x0 + 8):
            if (y in (y0, y0 + 6)) and (x in (x0, x0 + 7)): continue
            t = 0 if y == y0 else 1 if y < y0 + 3 else 2 if y < y0 + 5 else 3
            if x == x0 + 7: t += 1
            c.px(x, y, ROSE[min(4, t)])
    for (x, y) in ((x0 + 2, y0 + 2), (x0 + 5, y0 + 2), (x0 + 3, y0 + 4)):
        c.px(x, y, CREAMH[0])


def sofa():
    c = couch(56, 2)
    pillow(c, 9, 10)
    outline(c)
    return c


def armchair():
    c = couch(32, 1, back_top=3, seat_top=17)
    outline(c)
    return c


def view_bench():
    c = C(64, 46)
    X0, X1 = 3, 60
    # steel frame and legs
    for lx in (6, 30, 55):
        for y in range(32, 45):
            c.px(lx, y, STEEL[2]); c.px(lx + 1, y, STEEL[3]); c.px(lx + 2, y, STEEL[4])
    for y in range(30, 33):
        for x in range(X0, X1 + 1): c.px(x, y, STEEL[1] if y == 30 else STEEL[3] if y == 31 else STEEL[5])
    # low back and two long cushions
    rounded(c, X0 + 1, 6, X1 - 1, 18, VEL, top_t=1, mid_t=3, low_t=4, corner=2, side_dark=1)
    c.hline(X0 + 2, X1 - 2, 18, VEL[5])
    tufts(c, X0 + 4, X1 - 4, (10, 14), VEL)
    for i in range(2):
        bx0 = X0 + i * 29; bx1 = bx0 + 27
        rounded(c, bx0, 19, bx1, 29, VEL, top_t=1, mid_t=2, low_t=4, corner=1)
        for x in range(bx0 + 1, bx1):
            c.px(x, 23, VEL[4]); c.px(x, 24, VEL[3])
    c.px(X0 + 28, 20, VEL[5])
    outline(c)
    return c


PIECES = {"sofa": sofa, "armchair": armchair, "view_bench": view_bench}

if __name__ == "__main__":
    repo = sys.argv[1]
    for n, fn in PIECES.items():
        fn().save(os.path.join(repo, "art/lunar", n + ".png"))
    print("ok")
