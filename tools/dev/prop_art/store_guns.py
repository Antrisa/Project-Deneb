"""Ship store pictures (art/ships/store/<weapon>.png, 48 x 48) in the warm C style (Zachary, 24 Nov: "the things
Ooma sells are just placeholders"). Side views, muzzle to the right: lit top rows, faces darker toward the bottom,
straps and seams, warm outline; each kind of weapon has its own shape and its colour from ShipData.
    python3 tools/dev/prop_art/store_guns.py <repo>"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home_machines import C, H, face, seam, bar_v, cyl, STEEL, DARK, BRASS, FIRE, COPPER, CREAM, CYAN, RED, GREEN

GUN = [H("bdb5cb"), H("8f88a8"), H("645d82"), H("443e60"), H("2e2944")]          # gunmetal, a shade darker than steel
RUST = [H("e8946a"), H("c46a42"), H("8e4630"), H("5e2f26"), H("3e1f22")]


def ramp_of(hexcol):
    c = H(hexcol)
    import colorsys
    r, g, b = [v / 255 for v in c[:3]]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    out = []
    for k, dl in enumerate((0.18, 0.06, -0.08, -0.22, -0.34)):
        hh = (h + (0.03 if dl > 0 else -0.04 * (k - 1))) % 1
        rr, gg, bb = colorsys.hls_to_rgb(hh, max(0.05, min(0.95, l + dl)), min(1, s * 1.05))
        out.append((int(rr * 255), int(gg * 255), int(bb * 255), 255))
    return out


def cells(c, x0, y0, n, ramp, w=4, h=3, gap=2):
    """Glowing power cells in a window on the body."""
    for i in range(n):
        x = x0 + i * (w + gap)
        for yy in range(y0, y0 + h):
            for xx in range(x, x + w):
                c.px(xx, yy, ramp[0] if yy == y0 else ramp[1] if yy < y0 + h - 1 else ramp[2])


def body(c, x0, y0, x1, y1, ramp=GUN):
    face(c, x0, y0, x1, y1, ramp, lit_rows=1, right=2)
    seam(c, x0 + 1, x1 - 1, y0 + (y1 - y0) // 2 + 1, ramp)


def barrel(c, x0, x1, yc, r, ramp=GUN):
    for y in range(yc - r, yc + r + 1):
        t = (y - (yc - r)) / max(1, 2 * r)
        col = ramp[0] if t < 0.2 else ramp[1] if t < 0.5 else ramp[2] if t < 0.8 else ramp[3]
        for x in range(x0, x1 + 1):
            c.px(x, y, col)


def ring(c, x, y0, y1, ramp=BRASS):
    for y in range(y0, y1 + 1):
        c.px(x, y, ramp[0] if y == y0 else ramp[1]); c.px(x + 1, y, ramp[2] if y < y1 else ramp[3])


def grip(c, x, y):
    face(c, x, y, x + 5, y + 9, DARK, lit_rows=1, right=2)
    face(c, x + 6, y, x + 9, y + 3, DARK, lit_rows=1, right=1)


def mount(c):
    face(c, 4, 31, 15, 36, DARK, lit_rows=1, right=2)      # the hull mount under the back of the gun
    c.hline(6, 13, 37, DARK[4])


# ------------------------------------------------------------------ one function per weapon
def burst_laser(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 3, 18, 26, 30)
    cells(c, 7, 22, 3, a)
    for i, yc in enumerate((20, 24, 28)):
        barrel(c, 27, 42 - i * 2, yc, 1)
        c.px(43 - i * 2, yc, a[0]); c.px(42 - i * 2, yc, a[1])
    ring(c, 27, 18, 30)
    c.outline(); return c


def chain_laser(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 3, 17, 22, 31)
    cells(c, 6, 22, 2, a, w=5)
    face(c, 23, 16, 27, 32, GUN, lit_rows=1, right=1)          # rotary hub
    for i, yc in enumerate((18, 22, 26, 30)):
        barrel(c, 28, 43, yc, 1, GUN if i % 2 == 0 else STEEL)
    ring(c, 34, 16, 32, BRASS); ring(c, 40, 16, 32, BRASS)
    for yc in (18, 22, 26, 30):
        c.px(44, yc, a[0])
    c.outline(); return c


def cutting_beam(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 3, 19, 24, 29)
    cells(c, 6, 22, 3, a, w=3)
    barrel(c, 25, 36, 24, 3)
    for x in (27, 30, 33):
        ring(c, x, 20, 28, COPPER + [COPPER[3]])
    barrel(c, 37, 43, 24, 1, CREAM + [CREAM[3]])                # the focusing lens tube
    c.px(44, 24, a[0]); c.px(45, 24, a[1])
    c.outline(); return c


def fire_beam(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 3, 18, 24, 30)
    cells(c, 6, 21, 3, FIRE[1:], w=3)
    barrel(c, 25, 34, 24, 3)
    for y in range(18, 31):                                       # flared nozzle
        k = abs(y - 24)
        for x in range(35, 42):
            if k <= 3 + (x - 35) // 2:
                c.px(x, y, GUN[1] if y < 24 else GUN[2] if y < 28 else GUN[3])
    for x, y in ((42, 23), (42, 25), (43, 24), (44, 22), (44, 26), (45, 24)):
        c.px(x, y, FIRE[2 if x < 44 else 1])
    for x in (8, 13, 18):                                          # cooling fins
        c.vline(x, 14, 17, GUN[1]); c.vline(x + 1, 14, 17, GUN[3])
    c.outline(); return c


def flak_cannon(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 3, 17, 26, 31)
    for y in range(21, 35):                                        # drum magazine below
        for x in range(9, 20):
            if ((x - 14.5) / 5.5) ** 2 + ((y - 28) / 6.5) ** 2 <= 1:
                c.px(x, y, BRASS[1] if y < 26 else BRASS[2] if y < 31 else BRASS[3])
    c.px(14, 28, DARK[4])
    barrel(c, 27, 38, 24, 4)
    for y in range(17, 32):                                        # wide flared muzzle
        k = abs(y - 24)
        for x in range(39, 45):
            if k <= 4 + (x - 39):
                c.px(x, y, GUN[1] if y < 24 else GUN[2] if y < 28 else GUN[3])
    c.vline(44, 18, 30, DARK[3])
    cells(c, 21, 20, 1, a, w=4)
    c.outline(); return c


def heavy_beam(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 2, 16, 26, 32)
    cells(c, 5, 20, 4, a, w=4, h=4)
    barrel(c, 27, 34, 24, 5)
    for y in range(20, 29):                                        # long prism emitter
        for x in range(35, 45):
            if abs(y - 24) <= 4 - (x - 35) * 0.35:
                c.px(x, y, a[0] if y < 23 else a[1] if y < 26 else a[2])
    ring(c, 33, 19, 29)
    c.outline(); return c


def heavy_laser(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 2, 17, 25, 31)
    cells(c, 5, 21, 3, a, w=4, h=4)
    barrel(c, 26, 42, 21, 2); barrel(c, 26, 42, 27, 2)
    ring(c, 31, 18, 30); ring(c, 38, 18, 30)
    c.px(43, 21, a[0]); c.px(43, 27, a[0])
    c.outline(); return c


def ion_blast(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 3, 19, 24, 29)
    cells(c, 6, 22, 3, a, w=3)
    barrel(c, 25, 32, 24, 2)
    for y in range(14, 35):                                        # the ion sphere in a ring cage
        for x in range(30, 47):
            d = math.hypot(x - 39, y - 24)
            if d <= 7.5:
                c.px(x, y, CYAN[0] if d < 2.5 else CYAN[1] if d < 4.5 else CYAN[2] if d < 6.3 else CYAN[3])
    for t in range(0, 360, 20):
        x = round(39 + 8.5 * math.cos(math.radians(t))); y = round(24 + 8.5 * math.sin(math.radians(t)))
        c.px(x, y, BRASS[1] if y < 24 else BRASS[3])
    c.px(37, 21, (255, 255, 255, 255))
    c.outline(); return c


def ivan_cannon(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 2, 16, 24, 32, RUST)
    cells(c, 5, 20, 3, a, w=4, h=4)
    barrel(c, 25, 42, 24, 5, GUN)
    for x in (28, 33, 38):
        ring(c, x, 19, 29, BRASS)
    for y in range(18, 31):
        c.px(43, y, BRASS[1] if y < 24 else BRASS[3]); c.px(44, y, BRASS[2])
    c.px(10, 30, BRASS[1]); c.px(17, 30, BRASS[1])                 # rivets on the plating
    c.outline(); return c


def missile(c, x0, yc, n=12):
    for x in range(x0, x0 + n):
        c.px(x, yc - 1, CREAM[0]); c.px(x, yc, CREAM[1]); c.px(x, yc + 1, CREAM[2])
    c.px(x0 + n, yc, RED); c.px(x0 + n - 1, yc - 1, RED); c.px(x0 + n - 1, yc + 1, (184, 58, 69, 255))
    c.px(x0 + 1, yc - 2, DARK[2]); c.px(x0 + 1, yc + 2, DARK[3])


def missile_launcher(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 3, 17, 33, 31)
    cells(c, 6, 20, 2, a, w=4)
    face(c, 30, 20, 38, 28, DARK, lit_rows=1, right=1)            # the tube's mouth
    missile(c, 32, 24, 12)
    c.outline(); return c


def rabble_laser(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 3, 18, 26, 30, GUN)
    for (x, y) in ((6, 21), (7, 21), (18, 27), (19, 27), (12, 19)):   # rust patches and a welded plate
        c.px(x, y, RUST[1])
    face(c, 14, 24, 21, 29, RUST, lit_rows=1, right=1)
    c.px(15, 25, BRASS[1]); c.px(20, 28, BRASS[1])
    cells(c, 6, 23, 1, a, w=6)
    barrel(c, 27, 43, 24, 2)
    c.px(33, 22, RUST[1]); c.px(38, 26, RUST[1])
    c.px(44, 24, a[0])
    c.outline(); return c


def toxin_dart(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 4, 20, 22, 29)
    for y in range(13, 21):                                        # the toxin vial on top
        for x in range(9, 16):
            c.px(x, y, (a[0] if y < 15 else a[1] if y < 18 else a[2]) if 9 < x < 15 else CREAM[2])
    c.hline(9, 15, 12, DARK[2])
    barrel(c, 23, 40, 24, 1)
    for x in range(41, 46):
        c.px(x, 24, STEEL[0] if x < 44 else a[0])
    c.outline(); return c


def twin_missile(acc):
    c = C(48, 48); a = ramp_of(acc); mount(c)
    body(c, 3, 15, 31, 33)
    cells(c, 6, 18, 2, a, w=4)
    for yc in (20, 28):
        face(c, 28, yc - 4, 36, yc + 4, DARK, lit_rows=1, right=1)
        missile(c, 31, yc, 12)
    c.outline(); return c


WEAPONS = {"burst_laser": (burst_laser, "ff6a5a"), "chain_laser": (chain_laser, "45e1d5"), "cutting_beam": (cutting_beam, "ff5a5a"),
           "fire_beam": (fire_beam, "ff8a2a"), "flak_cannon": (flak_cannon, "e0c8a0"), "heavy_beam": (heavy_beam, "ffd34a"),
           "heavy_laser": (heavy_laser, "b6ff5a"), "ion_blast": (ion_blast, "5ac8ff"), "ivan_cannon": (ivan_cannon, "ffd34a"),
           "missile_launcher": (missile_launcher, "ffb04a"), "rabble_laser": (rabble_laser, "7dff8a"), "toxin_dart": (toxin_dart, "9cff5a"),
           "twin_missile": (twin_missile, "ffb04a")}

if __name__ == "__main__":
    repo = sys.argv[1]
    for wid, (fn, acc) in WEAPONS.items():
        fn(acc).save(os.path.join(repo, "art", "ships", "store", wid + ".png"))
    print("ok", len(WEAPONS))
