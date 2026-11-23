"""Demo: the same locker and fridge drawn with the things that make cozy pixel art read richer:
hue-shifted ramps (warm highlights, purple shadows), more saturation, inset bevels on every panel (1px light top/left,
1px dark bottom/right), a bright rim along top edges, glints, wear and small clutter, softened corners,
and a painted contact shadow. Original art; principles only."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home_machines import C, H
OUT = H("3b1f2b")
TEAL = [H("c8f0d8"), H("8ad6c0"), H("55b0a6"), H("37868f"), H("2c5e76"), H("2b3c61"), H("2a2647")]
STEEL = [H("fbf3e2"), H("d6cfdc"), H("a69fba"), H("7a7398"), H("564f75"), H("3c3657"), H("2a2440")]
BRASS = [H("fff6c4"), H("ffd970"), H("e7a83c"), H("b86f2a"), H("7d4122")]
CREAMH = [H("fffbea"), H("f4e6c4"), H("dcc49e"), H("b5967e")]
REDH = [H("ff9a7a"), H("e8574a"), H("b83a45"), H("7e2a42")]


def panel(c, x0, y0, x1, y1, ramp, base=2):
    """A flat panel with an inset bevel and a soft top-to-bottom shade: the core of the look."""
    for y in range(y0, y1 + 1):
        t = base + (1 if (y - y0) > (y1 - y0) * 0.6 else 0)
        for x in range(x0, x1 + 1):
            c.px(x, y, ramp[t])
    for x in range(x0, x1 + 1):
        c.px(x, y0, ramp[base - 1]); c.px(x, y1, ramp[base + 2])
    for y in range(y0, y1 + 1):
        c.px(x0, y, ramp[base - 1]); c.px(x1, y, ramp[base + 2])
    c.px(x0, y0, ramp[base - 2] if base >= 2 else ramp[0])


def outline(c):
    import numpy as np
    a = c.a; solid = a[:, :, 3] > 0
    for y in range(c.h):
        for x in range(c.w):
            if solid[y, x]: continue
            if any(0 <= x + dx < c.w and 0 <= y + dy < c.h and solid[y + dy, x + dx] for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                a[y, x] = OUT


def contact_shadow(c, x0, x1, y):
    return   # the game paints a soft shadow under every prop (prop_fx.gd), so none in the art


def locker():
    c = C(50, 80)
    X0, X1, Y0, Y1 = 4, 41, 5, 74
    # side face (right), hue-shifted darker
    for y in range(Y0 + 2, Y1 + 1):
        for x in (X1 + 1, X1 + 2, X1 + 3):
            c.px(x, y, TEAL[5] if x < X1 + 3 else TEAL[6])
    # top plane with a warm rim
    for y in range(Y0 - 3, Y0):
        for x in range(X0 + 1, X1 + 3):
            c.px(x, y, TEAL[1] if y > Y0 - 3 else TEAL[0])
    # body and two doors with inset bevels
    for y in range(Y0, Y1 + 1):
        for x in range(X0, X1 + 1):
            c.px(x, y, TEAL[3])
    for dx0, dx1 in ((X0 + 2, 21), (24, X1 - 2)):
        panel(c, dx0, Y0 + 2, dx1, Y1 - 4, TEAL, base=2)
        # vents: each slot dark with a light lip under it
        for y in range(Y0 + 6, Y0 + 15, 3):
            for x in range(dx0 + 3, dx1 - 2):
                c.px(x, y, TEAL[5]); c.px(x, y + 1, TEAL[1])
        # name card with a bit of handwriting
        panel(c, dx0 + 4, Y0 + 19, dx1 - 4, Y0 + 24, CREAMH, base=1)
        for x in range(dx0 + 6, dx1 - 6, 2): c.px(x, Y0 + 21, H("7a5a6a"))
        # handle with a glint
        for y in range(Y0 + 30, Y0 + 40):
            c.px(dx1 - 3, y, BRASS[1] if y < Y0 + 33 else BRASS[2]); c.px(dx1 - 2, y, BRASS[3])
        c.px(dx1 - 3, Y0 + 30, BRASS[0])
        # scuffs and a rivet row
        for (sx, sy) in ((dx0 + 3, Y1 - 12), (dx0 + 8, Y1 - 9), (dx0 + 5, Y0 + 48)):
            c.px(sx, sy, TEAL[1]); c.px(sx + 1, sy, TEAL[4])
        for x in range(dx0 + 2, dx1 - 1, 5): c.px(x, Y1 - 6, TEAL[1])
    # gap between doors, AO under the top lip
    for y in range(Y0, Y1 - 3): c.px(22, y, TEAL[6]); c.px(23, y, TEAL[4])
    for x in range(X0, X1 + 1): c.px(x, Y0, TEAL[5])
    # sticker and a magnet clip on the right door
    panel(c, 30, Y0 + 44, 35, Y0 + 49, REDH, base=1); c.px(32, Y0 + 46, H("fff6c4"))
    # kick plate and feet
    for y in range(Y1 - 3, Y1 + 1):
        for x in range(X0, X1 + 1): c.px(x, y, STEEL[4] if y < Y1 else STEEL[5])
    for x in range(X0, X1 + 1, 3): c.px(x, Y1 - 3, STEEL[3])
    outline(c)
    contact_shadow(c, X0 - 1, X1 + 4, Y1 + 2)
    return c


def fridge():
    c = C(36, 70)
    X0, X1, Y0, Y1 = 2, 29, 4, 65
    for y in range(Y0 + 1, Y1 + 1):
        for x in (X1 + 1, X1 + 2, X1 + 3): c.px(x, y, STEEL[4] if x < X1 + 3 else STEEL[5])
    for y in range(Y0 - 3, Y0):
        for x in range(X0 + 1, X1 + 3): c.px(x, y, STEEL[1] if y > Y0 - 3 else STEEL[0])
    for y in range(Y0, Y1 + 1):
        for x in range(X0, X1 + 1): c.px(x, y, STEEL[3])
    panel(c, X0 + 1, Y0 + 1, X1 - 1, Y0 + 18, STEEL, base=2)
    panel(c, X0 + 1, Y0 + 21, X1 - 1, Y1 - 4, STEEL, base=2)
    # brushed-metal streaks
    for (x, y0, l) in ((6, 28, 9), (11, 40, 12), (8, 8, 6), (17, 50, 7)):
        for y in range(y0, y0 + l): c.px(x, y, STEEL[1])
    # handles with glints
    for (ya, yb) in ((Y0 + 5, Y0 + 15), (Y0 + 25, Y0 + 42)):
        for y in range(ya, yb):
            c.px(X1 - 4, y, BRASS[1] if y < ya + 3 else BRASS[2]); c.px(X1 - 3, y, BRASS[3])
        c.px(X1 - 4, ya, BRASS[0])
    # display: dark glass, lit edge, readout
    panel(c, 5, Y0 + 4, 15, Y0 + 10, [H("6fd6e0"), H("3a8fb0"), H("2b5a85"), H("23365c"), H("1d2440"), H("1a1a33"), H("15142a")], base=3)
    for x in range(7, 11): c.px(x, Y0 + 7, H("a8f4ff"))
    c.px(13, Y0 + 6, H("7dff9a"))
    # clutter: a photo, a magnet, a child's drawing, a jar on top
    panel(c, 6, Y0 + 26, 13, Y0 + 34, CREAMH, base=1)
    for y in range(Y0 + 28, Y0 + 33):
        for x in range(7, 12): c.px(x, y, H("8fd6ff") if y < Y0 + 31 else H("7bc77a"))
    c.px(9, Y0 + 25, REDH[1])
    panel(c, 15, Y0 + 30, 22, Y0 + 37, CREAMH, base=1)
    for (x, y) in ((17, Y0 + 32), (18, Y0 + 33), (19, Y0 + 32), (20, Y0 + 34)): c.px(x, y, REDH[1])
    c.px(16, Y0 + 29, H("5ab0ff"))
    for y in range(Y0 - 9, Y0 - 2):
        for x in range(6, 12): c.px(x, y, H("e0f4ff") if x < 8 else H("9cc7e0") if x < 11 else H("6f8fb5"))
    for x in range(6, 12): c.px(x, Y0 - 10, REDH[1])
    # kick plate with vents
    for y in range(Y1 - 3, Y1 + 1):
        for x in range(X0, X1 + 1): c.px(x, y, STEEL[5] if y < Y1 else STEEL[6])
    for x in range(X0 + 2, X1 - 1, 2): c.px(x, Y1 - 2, STEEL[3])
    outline(c)
    contact_shadow(c, X0 - 1, X1 + 4, Y1 + 2)
    return c


if __name__ == "__main__":
    from PIL import Image
    import subprocess, io
    repo = "/home/claude/project-deneb"
    out = []
    for n, fn in (("locker", locker), ("fridge", fridge)):
        old = Image.open(io.BytesIO(subprocess.run(["git", "-C", repo, "show", f"HEAD:art/lunar/{n}.png"], capture_output=True).stdout)).convert("RGBA")
        mine = Image.open(f"{repo}/art/lunar/{n}.png").convert("RGBA")
        v2 = Image.fromarray(fn().a, "RGBA")
        out += [old, mine, v2]
    W = sum(i.width + 10 for i in out) + 20; Hh = max(i.height for i in out) + 8
    bg = Image.new("RGBA", (W, Hh), (176, 128, 86, 255))
    x = 6
    for i, im in enumerate(out):
        bg.alpha_composite(im, (x, Hh - 4 - im.height)); x += im.width + 10 + (20 if i == 2 else 0)
    bg.resize((W * 4, Hh * 4), Image.NEAREST).save("/tmp/prev/style_v2_demo.png")
