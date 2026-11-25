"""Item icons for Rusk's drinks and Job's geode minerals (24 Nov 2026; they were placeholder shapes). 24 x 24 in the
item style of the artist's icons (moon_opal, nebula_wine): rounded chunky forms, light from the upper left, 3-4 flat
tones per material, a glint, warm dark outline.
    python3 tools/dev/prop_art/shop_extra_icons.py <repo>   (art/items/<id>.png; then tools/dev/shop_icons.py)"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from home_machines import C, H, CREAM, BRASS, STEEL

S = 24
WHITE = (255, 255, 255, 255)
Y, X = np.mgrid[0:S, 0:S].astype(float)


def ramp(hexes):
    return [H(h) for h in hexes]


def poly(pts):
    im = Image.new("L", (S, S), 0); ImageDraw.Draw(im).polygon(pts, fill=255); return np.array(im) > 0


def ell(cx, cy, rx, ry):
    return ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 <= 1


def lit(c, m, r, lx=-0.45, ly=-0.55, bands=(0.35, 0.7, 1.0)):
    """Round-form shading: tone by distance from a light point at the upper left of the shape."""
    ys, xs = np.nonzero(m)
    cx, cy = xs.mean(), ys.mean(); w = max(1, np.ptp(xs)); h = max(1, np.ptp(ys))
    px, py = cx + lx * w * 0.5, cy + ly * h * 0.5
    for y, x in zip(ys, xs):
        d = math.hypot((x - px) / w, (y - py) / h) * 1.4
        k = 0 if d < bands[0] * 0.6 else 1 if d < bands[0] + 0.25 else 2 if d < bands[1] + 0.3 else 3
        c.px(x, y, r[min(len(r) - 1, k)])


def flat(c, m, r):
    """Flat-sided shading: lit top, darker bottom, darker right edge."""
    ys, xs = np.nonzero(m); y0, y1 = ys.min(), ys.max()
    for y, x in zip(ys, xs):
        t = (y - y0) / max(1, y1 - y0); row = xs[ys == y]
        k = 0 if t < 0.15 else 1 if t < 0.55 else 2
        if x >= row.max() - 1: k += 1
        if x == row.min() and 0.1 < t < 0.9: k = max(0, k - 1)
        c.px(x, y, r[min(len(r) - 1, k)])


def glint(c, x, y, big=False):
    c.px(x, y, WHITE)
    if big: c.px(x + 1, y, WHITE); c.px(x, y + 1, WHITE)


def done(c):
    c.outline(); return c


# ------------------------------------------------------------------ minerals
def lunar_agate():
    c = C(S, S); m = ell(12, 13, 9, 8); lit(c, m, ramp(["e6e0d4", "c8c2b6", "a29c94", "7a7470"]))
    for i, r in enumerate((6.5, 4.5, 2.5)):                     # the sliced face: concentric bands
        band = (((X - 12) / r) ** 2 + ((Y - 13) / (r * 0.85)) ** 2 <= 1) & ~(((X - 12) / (r - 1)) ** 2 + ((Y - 13) / ((r - 1) * 0.85)) ** 2 <= 1)
        for y, x in zip(*np.nonzero(band & m)): c.px(x, y, H(["fff6e4", "8e8a92", "fff6e4"][i]))
    glint(c, 8, 9); return done(c)


def anorthosite():
    c = C(S, S)
    for pts, r in (([(5, 20), (5, 9), (8, 6), (10, 9), (10, 20)], 0), ([(11, 20), (11, 5), (14, 2), (17, 5), (17, 20)], 1),
                   ([(17, 20), (17, 11), (19, 9), (21, 11), (21, 20)], 2)):
        flat(c, poly(pts), ramp(["fffaf0", "ece6da", "cfc6b8", "a89e94"]))
    flat(c, poly([(3, 19), (22, 19), (21, 22), (4, 22)]), ramp(["a8a0a8", "8a8290", "6e6678", "524a5c"]))
    glint(c, 12, 6); glint(c, 6, 10); return done(c)


def faceted(c, cx, cy, rx, ry, r):
    m = ell(cx, cy, rx, ry); lit(c, m, r)
    for y, x in zip(*np.nonzero(m)):                            # a table facet and side facets
        if abs(x - cx) + abs(y - cy) * rx / ry < rx * 0.45: c.px(x, y, r[0] if y < cy else r[1])
    return m


def cut_gem(c, r):
    """A cut gem seen at three-quarters: a flat table on top, crown facets, a pointed pavilion below."""
    flat(c, poly([(5, 9), (8, 5), (16, 5), (19, 9), (12, 21)]), r)
    flat(c, poly([(8, 5), (16, 5), (14, 8), (10, 8)]), [r[0], r[0], r[1], r[1]])        # the table
    for (a, b) in (((5, 9), (19, 9)), ((10, 8), (12, 21)), ((14, 8), (12, 21))):
        ImageDraw.Draw(Image.new("L", (1, 1)))
    c.hline(5, 19, 9, r[2])
    for i in range(12):
        c.px(round(10 + i * 2 / 12), 9 + i, r[2]); c.px(round(14 - i * 2 / 12), 9 + i, r[3])


def moon_olivine():
    c = C(S, S); cut_gem(c, ramp(["d4f08a", "9cc84e", "6e9a34", "466a24"])); glint(c, 9, 6, True); glint(c, 7, 10); return done(c)


def regolith_jasper():
    c = C(S, S); m = poly([(4, 13), (7, 7), (13, 5), (19, 8), (21, 14), (16, 20), (8, 20)]); lit(c, m, ramp(["e89070", "c4624a", "984234", "6a2c2a"]))
    c.hline(6, 19, 13, H("6a2c2a")); c.hline(7, 18, 12, H("e89070"))         # a polished cut face
    for (x, y) in ((8, 11), (14, 10), (11, 15), (16, 14), (7, 15), (13, 17)): c.px(x, y, H("f4d0b0"))
    glint(c, 8, 9); return done(c)


def ilmenite():
    c = C(S, S)
    flat(c, poly([(6, 8), (12, 5), (19, 8), (19, 17), (12, 20), (6, 17)]), ramp(["8a8a9a", "5a5a6a", "3c3c4a", "26262f"]))
    for i in range(5): c.px(8 + i, 9 - i // 2, H("c8ccd8"))        # metallic sheen
    c.vline(12, 6, 19, H("26262f")); glint(c, 9, 8); return done(c)


def selenite_rose():
    c = C(S, S); rr = ramp(["fff4ee", "f4d8cc", "dcb4a8", "b08880"])
    for a in range(0, 360, 45):                                    # petals round a centre
        px, py = 12 + 6 * math.cos(math.radians(a)), 12 + 6 * math.sin(math.radians(a))
        lit(c, ell(px, py, 3.6, 2.4) , rr)
    lit(c, ell(12, 12, 3, 3), ramp(["fffaf6", "f8e4dc", "e0c4b8", "b89488"]))
    glint(c, 10, 9); return done(c)


def armalcolite():
    c = C(S, S)
    flat(c, poly([(9, 21), (7, 8), (11, 3), (15, 8), (14, 21)]), ramp(["8e72a8", "5e4878", "40305a", "2a1e40"]))
    flat(c, poly([(14, 21), (15, 11), (18, 8), (20, 12), (18, 21)]), ramp(["7a6094", "4e3c68", "362a4e", "241a36"]))
    c.vline(11, 5, 20, H("b89ad8")); glint(c, 10, 6); return done(c)


def orange_glass():
    c = C(S, S); r = ramp(["ffd08a", "f49a44", "d46a2a", "9a4422"])
    for (x, y, s) in ((8, 15, 3.2), (14, 15, 3.4), (11, 10, 3.2), (17, 10, 2.6), (5, 10, 2.4), (11, 19, 2.6), (18, 17, 2.2)):
        m = ell(x, y, s, s); lit(c, m, r); c.px(round(x - s * 0.4), round(y - s * 0.4), WHITE)
    return done(c)


def spinel():
    c = C(S, S); rr = ramp(["ffb0d0", "ea6a9a", "c03e70", "8a2450"])
    flat(c, poly([(12, 3), (20, 12), (12, 21), (4, 12)]), rr)
    for y, x in zip(*np.nonzero(poly([(12, 3), (12, 21), (4, 12)]))): c.px(x, y, rr[0] if y < 12 else rr[1])
    c.hline(5, 19, 12, rr[3]); glint(c, 9, 8, True); return done(c)


def basalt_glass():
    c = C(S, S)
    flat(c, poly([(4, 18), (9, 5), (13, 9), (19, 4), (21, 15), (14, 21)]), ramp(["5a5a72", "33333f", "22222c", "16161e"]))
    for (x, y) in ((9, 8), (10, 10), (17, 8), (16, 11), (12, 16)): c.px(x, y, H("9aa8d0"))
    glint(c, 9, 7); glint(c, 18, 6); return done(c)


def fire_opal():
    c = C(S, S); cut_gem(c, ramp(["ffc070", "f08a38", "cc5a24", "8e3420"]))
    for (x, y, col) in ((11, 10, "fff0a0"), (12, 12, "ff5a3a"), (13, 11, "ffd060"), (12, 14, "ffd060"), (11, 16, "ff5a3a"), (15, 10, "fff0a0")):
        c.px(x, y, H(col))                                         # the flame inside
    glint(c, 9, 6, True); return done(c)


def tranquillityite():
    c = C(S, S); r = ramp(["d8846a", "aa5440", "7e3a30", "542426"])
    for (x0, y0, x1, y1) in ((7, 21, 5, 6), (11, 21, 11, 3), (15, 21, 18, 5), (13, 21, 15, 9), (9, 21, 8, 10)):
        flat(c, poly([(x0 - 1, y0), (x1 - 1, y1 + 1), (x1, y1), (x1 + 1, y1 + 1), (x0 + 1, y0)]), r)
    flat(c, poly([(4, 19), (20, 19), (19, 22), (5, 22)]), ramp(["a8a0a8", "8a8290", "6e6678", "524a5c"]))
    glint(c, 11, 4); return done(c)


# ------------------------------------------------------------------ drinks
GLASS = ramp(["f0fbff", "c8e4ee", "9cc0d0", "7898aa"])


def tall_glass(c, liquid, top=6, ice=False):
    g = poly([(7, top), (17, top), (16, 21), (8, 21)])
    flat(c, g, GLASS)
    liq = poly([(8, top + 3), (16, top + 3), (15, 20), (9, 20)])
    flat(c, liq, liquid)
    c.vline(8, top + 1, 19, GLASS[0])                              # the glass's lit edge
    if ice:
        for (x, y) in ((10, top + 4), (13, top + 6)):
            c.px(x, y, GLASS[0]); c.px(x + 1, y, GLASS[1]); c.px(x, y + 1, GLASS[1]); c.px(x + 1, y + 1, GLASS[2])
    return g


def mug(c, body, liquid):
    flat(c, poly([(5, 9), (16, 9), (16, 20), (5, 20)]), body)
    for (x, y) in ((17, 11), (18, 11), (19, 12), (19, 13), (19, 14), (19, 15), (18, 16), (17, 16)): c.px(x, y, body[2])
    c.hline(6, 15, 9, liquid[1]); c.hline(7, 14, 10, liquid[2])
    for (x, y) in ((8, 6), (9, 5), (8, 4), (12, 6), (13, 5), (12, 3)): c.px(x, y, CREAM[1])   # steam


def bottle(c, glass, label, cork=True):
    flat(c, poly([(7, 10), (10, 7), (10, 3), (14, 3), (14, 7), (17, 10), (17, 21), (7, 21)]), glass)
    if cork: flat(c, poly([(10, 1), (14, 1), (14, 4), (10, 4)]), ramp(["e8c08a", "c8965a", "9a6a3c", "6e4a2a"]))
    flat(c, poly([(8, 13), (16, 13), (16, 18), (8, 18)]), label)
    c.vline(8, 11, 20, glass[0])


def iced_moon_tea():
    c = C(S, S); tall_glass(c, ramp(["f4d08a", "dca050", "b87a34", "8a5424"]), ice=True)
    c.vline(15, 2, 8, H("e8574a")); c.px(16, 2, H("e8574a"))       # straw
    return done(c)


def ginger_brew():
    c = C(S, S); mug(c, ramp(["f4ead6", "dcccb0", "b8a488", "8e7a64"]), ramp(["f4c060", "dca040", "b87a2c"]))
    c.px(9, 15, H("dca040")); c.px(10, 15, H("dca040")); return done(c)


def spacer_fizz():
    c = C(S, S); tall_glass(c, ramp(["8ad8ff", "4aa8f0", "2a78d0", "1e50a0"]))
    for (x, y) in ((10, 12), (13, 15), (11, 17), (14, 11), (12, 9)): c.px(x, y, WHITE)
    return done(c)


def night_watch():
    c = C(S, S); mug(c, ramp(["6a78b0", "4a5690", "343e6c", "242a4a"]), ramp(["6a4430", "3a2418", "1e120c"]))
    c.px(9, 14, BRASS[1]); c.px(10, 14, BRASS[1]); c.px(11, 13, BRASS[2]); return done(c)   # a moon on the mug


def anchor_tonic():
    c = C(S, S); bottle(c, ramp(["8aa878", "5e7c52", "40583a", "2a3a28"]), ramp(["fffaf0", "ece2d0", "cfc0a8", "a89880"]))
    for (x, y) in ((12, 14), (12, 15), (12, 16), (11, 17), (13, 17), (10, 16), (14, 16), (11, 14), (13, 14)): c.px(x, y, H("343f74"))
    return done(c)


def garden_cordial():
    c = C(S, S); bottle(c, ramp(["c8f0a0", "94cc6a", "6a9e48", "466e30"]), ramp(["fffaf0", "ece2d0", "cfc0a8", "a89880"]))
    for (x, y) in ((11, 16), (12, 15), (13, 14), (12, 16), (13, 15), (14, 15)): c.px(x, y, H("4e8a3a"))
    return done(c)


def comet_float():
    c = C(S, S); tall_glass(c, ramp(["8ad8ff", "4aa8f0", "2a78d0", "1e50a0"]), top=9)
    lit(c, ell(12, 8, 5, 3.5), ramp(["fffcf4", "f4ecdc", "dccfb8", "b8a890"]))   # the scoop of ice cream
    c.px(12, 4, H("e8574a")); c.px(13, 4, H("b83a45"))                           # a cherry
    for (x, y) in ((11, 14), (14, 16), (12, 18)): c.px(x, y, WHITE)
    c.vline(16, 2, 9, H("ffd970")); return done(c)


ICONS = {n: f for n, f in globals().items() if n in (
    "lunar_agate anorthosite moon_olivine regolith_jasper ilmenite selenite_rose armalcolite orange_glass spinel "
    "basalt_glass fire_opal tranquillityite iced_moon_tea ginger_brew spacer_fizz night_watch anchor_tonic "
    "garden_cordial comet_float").split()}

if __name__ == "__main__":
    repo = sys.argv[1]
    for n, fn in ICONS.items():
        fn().save(os.path.join(repo, "art", "items", n + ".png"))
    print("ok", len(ICONS))
