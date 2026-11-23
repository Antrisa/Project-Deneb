"""Cavern rocks, ore nodes and boulders, round 3 (23 Nov 2026). Three-quarter view like the rest of the game: each
rock is an angular chunk with a lit top plane, a front face going down to the ground and a shaded side, crisp
straight pixel edges, the master palette and the warm outline #5b332d. Ore nodes carry chunky crystal clusters
standing up out of the rock, in the ore's colours. Sheets: nodes 48 x 24 (whole, rubble), boulders 48 x 40.
Usage: python3 rocks6.py OUTDIR"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from pix import H

OUTLINE, INNER = H("5b332d"), H("3a2026")
#           shadow     side       front      top        top-light  lip
GREY = [H(c) for c in ("2f2c3d", "4b4659", "6f6878", "9c94a0", "b4adb6", "c9c1c4")]
BROWN = [H(c) for c in ("33242a", "5a3a33", "6e4a3a", "86593f", "9c6e4c", "b08158")]
SLATE = [H(c) for c in ("1e2a3a", "2f4a5e", "4b5e70", "6a7c8a", "8a9aa6", "a8b6c0")]
LEAF = [H(c) for c in ("1f3a32", "2f6a3a", "4f9a3c", "8cc94a", "d2ea7a")]
CRYSTAL = {   # dark face, light face, top facet, shine
    "copper_ore": [H("8a3a2a"), H("c8602f"), H("ee8f3e"), H("ffc070")],
    "gold_ore": [H("8f5f24"), H("c99231"), H("edc65a"), H("fff0a0")],
    "iron_ore": [H("3a3448"), H("c9c1c4"), H("eeeaf2"), H("ffffff")],
    "titanium_ore": [H("2f5a6e"), H("3f7f88"), H("66a7a0"), H("9fd1bf")],
    "quartz": [H("9c8a8f"), H("d8d0e0"), H("f0eef8"), H("ffffff")],
    "carbon": [H("1a1820"), H("2f2c3d"), H("4b4659"), H("9c94a0")],
    "lithium_salts": [H("8a2a3a"), H("c94a4a"), H("ee7a62"), H("ffb39a")],
    "silica_sand": [H("9c8a8f"), H("c9b8a6"), H("e8d9bd"), H("fff3d6")],
}
CRYSTAL["quartz"] = [H("9c8a8f"), H("c9b8a6"), H("e8d9bd"), H("fff3d6")]   # cream, as on the quartz icon
CRYSTAL.update({
    "thermal_quartz": [H("8a3a2a"), H("c8602f"), H("ee8f3e"), H("fff0a0")],
    "sulphur": [H("5e5420"), H("8a7a28"), H("dcd256"), H("fbf8c4")],
    "cobalt_60": [H("2f5cab"), H("4a9be0"), H("8fd3ff"), H("e6fbff")],
    "rare_earths": [H("2c1f4a"), H("7d55c0"), H("b085e6"), H("e0c6ff")],
    "aluminium_ore": [H("4b4659"), H("6f6878"), H("9c94a0"), H("c9c1c4")],
    "ice": [H("1f2f5a"), H("4a9be0"), H("8fd3ff"), H("e6fbff")],
    "basalt_core": [H("2f2c3d"), H("4b4659"), H("6f6878"), H("9c94a0")],
    "geode": [H("2c1f4a"), H("4f3384"), H("b085e6"), H("e0c6ff")],
})
PALE = [H(c) for c in ("6f6878", "9c8a8f", "c9b8a6", "d8c8b0", "e8d9bd", "fff3d6")]          # aluminium (anorthite)
SULPH = [H(c) for c in ("7a6a26", "a8962e", "c9bb3c", "dcd256", "ece87e", "fbf8c4")]          # sulphur crust, lemon not gold
ICE = [H(c) for c in ("1f2f5a", "2f5cab", "4a9be0", "8fd3ff", "c4ecff", "e6fbff")]
BASALT = [H(c) for c in ("2f2c3d", "3a3646", "4b4659", "5e5868", "6f6878", "9c94a0")]

SHAPES = {   # planes as hand-placed polygons: top (lit), front (to the ground), side (shade); base row last
    "node": dict(top=[(3, 13), (6, 9), (12, 7), (17, 8), (20, 12), (16, 14), (8, 14)],
                 front=[(3, 13), (8, 14), (16, 14), (17, 21), (3, 21)],
                 side=[(16, 14), (20, 12), (21, 19), (17, 21)], W=24, Hh=24),
    "a": dict(top=[(3, 14), (5, 10), (11, 8), (17, 9), (20, 13), (15, 15), (8, 15)],
              front=[(3, 14), (8, 15), (15, 15), (16, 21), (3, 21)],
              side=[(15, 15), (20, 13), (21, 19), (16, 21)], W=24, Hh=24),
    "b": dict(top=[(7, 11), (11, 7), (17, 7), (20, 10), (17, 12), (10, 13)],
              front=[(7, 11), (10, 13), (17, 12), (18, 21), (7, 21)],
              side=[(17, 12), (20, 10), (21, 19), (18, 21)],
              top2=[(2, 16), (4, 14), (8, 14), (10, 16), (6, 17)], front2=[(2, 16), (6, 17), (10, 16), (10, 21), (2, 21)], W=24, Hh=24),
    "c": dict(top=[(6, 7), (9, 3), (14, 3), (17, 6), (13, 8), (8, 8)],
              front=[(6, 7), (8, 8), (13, 8), (14, 21), (5, 21)],
              side=[(13, 8), (17, 6), (18, 19), (14, 21)], W=24, Hh=24),
    "big": dict(top=[(5, 22), (11, 13), (22, 8), (33, 9), (42, 15), (45, 22), (33, 25), (18, 26)],
                front=[(5, 22), (18, 26), (33, 25), (34, 37), (4, 37)],
                side=[(33, 25), (45, 22), (46, 34), (34, 37)],
                top2=[(1, 30), (4, 27), (11, 27), (15, 30), (8, 31)], front2=[(1, 30), (8, 31), (15, 30), (15, 37), (1, 37)], W=48, Hh=40),
}


def poly(pts, W, Hh):
    im = Image.new("L", (W, Hh), 0); ImageDraw.Draw(im).polygon(pts, fill=255)
    return np.array(im) > 127


def rock(shape, R, seed=0, moss=False):
    S = SHAPES[shape]; W, Hh = S["W"], S["Hh"]
    lab = np.full((Hh, W), ".", "<U1")
    for key, ch in (("side", "s"), ("front", "f"), ("top", "t"), ("front2", "F"), ("top2", "T")):
        if key in S: lab[poly(S[key], W, Hh)] = ch
    m = lab != "."
    img = np.zeros((Hh, W, 4), np.uint8)
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:Hh, 0:W]
    for y, x in zip(*np.nonzero(m)):
        c = lab[y, x]
        if c in "tT":
            tone = 4 if rng.random() > 0.14 else 3
        elif c in "fF":
            col = np.nonzero(lab[:, x] == c)[0]
            depth = (y - col.min()) / max(col.max() - col.min(), 1)
            tone = 3 if depth < 0.35 else 2
        else:
            tone = 1 if y > np.nonzero(lab[:, x] == "s")[0].min() + 1 else 2
        if rng.random() < 0.08: tone = max(0, tone - 1)
        img[y, x, :3] = R[tone]; img[y, x, 3] = 255
    # the lit lip where the top plane meets the front, and the dark seam where the front meets the side
    for y, x in zip(*np.nonzero(np.isin(lab, ["t", "T"]))):
        if y + 1 < Hh and lab[y + 1, x] in "fFs": img[y, x, :3] = R[5]
    for y, x in zip(*np.nonzero(lab == "s")):
        if x > 0 and lab[y, x - 1] in "fF": img[y, x, :3] = R[0]
    for y, x in zip(*np.nonzero(lab == "F")):     # the second chunk stands in front: dark line behind it
        if y > 0 and lab[y - 1, x] == "f": img[y - 1, x, :3] = R[0]
    if moss:
        for y, x in zip(*np.nonzero(np.isin(lab, ["t", "T"]))):
            r_ = rng.random()
            img[y, x, :3] = LEAF[2] if r_ < 0.55 else LEAF[3] if r_ < 0.93 else LEAF[4]
            if y + 1 < Hh and lab[y + 1, x] in "fFs":
                img[y, x, :3] = LEAF[2]
                if (x * 7) % 3 == 0 and y + 2 < Hh and lab[y + 2, x] in "fF": img[y + 1, x, :3] = LEAF[1]
    # outline, and the dark inner line along the ground
    pad = np.pad(m, 1)
    edge = (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]) & ~m
    img[edge, :3] = OUTLINE; img[edge, 3] = 255
    ground = m & ~pad[2:, 1:-1]
    img[ground, :3] = INNER
    return img, lab


def crystal(img, x, y, h, w, C, lean=0):
    """One crystal standing up: a light left face, a dark right face, a pointed top facet; (x, y) is its foot."""
    pts_l, pts_r = [], []
    for k in range(h):
        yy = y - k
        xo = x + int(round(lean * k / max(h, 1)))
        half = w if k < h - w else max(0, w - (k - (h - w)))
        for dx in range(-half, half + 1):
            X = xo + dx
            if 0 <= X < img.shape[1] and 0 <= yy < img.shape[0]:
                c = C[1] if dx < 0 else C[0] if dx > 0 else C[2]
                img[yy, X, :3] = c; img[yy, X, 3] = 255
        if half >= 0:
            pts_l.append((xo - half - 1, yy)); pts_r.append((xo + half + 1, yy))
    tip = (x + int(round(lean)), y - h)
    for (X, Y) in pts_l + pts_r + [tip]:
        if 0 <= X < img.shape[1] and 0 <= Y < img.shape[0] and img[Y, X, 3] == 0 or (0 <= X < img.shape[1] and 0 <= Y < img.shape[0] and tuple(img[Y, X, :3]) not in [tuple(c) for c in C]):
            if 0 <= X < img.shape[1] and 0 <= Y < img.shape[0]:
                img[Y, X, :3] = OUTLINE; img[Y, X, 3] = 255
    sx, sy = x - max(w - 1, 0) + int(round(lean * 0.6)), y - h + w + 1
    if 0 <= sy < img.shape[0]: img[sy, sx, :3] = C[3]


CRYSTALS = {   # hand-drawn prisms: o outline, W shine, L light face, M middle, D dark face
    "big": ["...o...", "..oWo..", ".oWLDo.", "oWLLMDo", "oLLMMDo", "oLLMMDo", "oLLMMDo", "oLLMMDo", "oLLMMDo",
            "oLLMMDo", "oLLMMDo", "oLLMMDo"],
    "mid": ["..o..", ".oWo.", "oWLDo", "oLMDo", "oLMDo", "oLMDo", "oLMDo", "oLMDo"],
    "small": [".o..", "oWo.", "oLDo", "oLDo", "oLDo"],
}


def put_crystal(img, kind, x, y, C, lean=0):
    """Stamp a crystal with its foot centred at (x, y); lean shifts it one pixel sideways every three rows."""
    rows = CRYSTALS[kind]
    pal = {"o": OUTLINE, "W": C[3], "L": C[2], "M": C[1], "D": C[0]}
    h, w = len(rows), len(rows[0])
    for r, row in enumerate(rows):
        dx = int(lean * (h - 1 - r) / 3)
        for c, ch in enumerate(row):
            X, Y = x - w // 2 + c + dx, y - h + 1 + r
            if ch in pal and 0 <= X < img.shape[1] and 0 <= Y < img.shape[0]:
                img[Y, X, :3] = pal[ch]; img[Y, X, 3] = 255


def stamp(img, lab, rows, pal, x, y, only_rock=False):
    for yy, row in enumerate(rows):
        for xx, c in enumerate(row):
            X, Y = x + xx, y + yy
            if c in pal and 0 <= X < img.shape[1] and 0 <= Y < img.shape[0] and (not only_rock or lab[Y, X] != "."):
                img[Y, X, :3] = pal[c]; img[Y, X, 3] = 255


NUG_BIG = [".dd.", "dLWd", "dLMd", ".dd."]
NUG_SMALL = [".d.", "dWd", ".d."]
CUBE = ["oooooo", "oTTTTo", "oFFFSo", "oFFFSo", "oFFFSo", "oooooo"]
CUBE_S = ["ooooo", "oTTTo", "oFFSo", "oFFSo", "ooooo"]


def node(name):
    """Each node after its icon: metals show bold nuggets set into the rock (top and front); quartz, thermal quartz
    and titanium grow crystals; lithium and cobalt-60 grow chunky blocks; silica is a pale sand mound; carbon has
    graphite seams; aluminium is a pale speckled rock; ice a block of ice; basalt a dark column; a geode is split
    open on top to show its crystal; rare earths are flecks of many colours."""
    base = {"aluminium_ore": PALE, "sulphur": SULPH, "ice": ICE, "basalt_core": BASALT}.get(name, GREY)
    shape = "c" if name == "basalt_core" else "node"
    img, lab = rock(shape, base, seed=len(name))
    C = CRYSTAL[name]
    if name == "thermal_quartz":
        put_crystal(img, "big", 12, 12, C, 0)
        put_crystal(img, "mid", 7, 13, C, -1)
        put_crystal(img, "mid", 17, 13, C, 1)
        put_crystal(img, "small", 14, 15, C, 1)
    elif name == "cobalt_60":
        pal = {"o": OUTLINE, "T": C[3], "F": C[2], "S": C[1]}
        stamp(img, lab, CUBE_S, pal, 5, 8); stamp(img, lab, CUBE, pal, 10, 6); stamp(img, lab, CUBE_S, pal, 14, 10)
        for (x, y) in [(11, 7), (6, 9), (15, 11)]: img[y, x, :3] = H("ffffff")
    elif name == "rare_earths":
        cols = [[H("2c1f4a"), H("7d55c0"), H("b085e6"), H("e0c6ff")], [H("4a1c2e"), H("c94a4a"), H("ee7a62"), H("ffb39a")],
                [H("1f2f5a"), H("2f5cab"), H("4a9be0"), H("8fd3ff")], [H("1f3a32"), H("4f9a3c"), H("8cc94a"), H("d2ea7a")]]
        for k, (x, y, big) in enumerate([(5, 9, True), (12, 8, True), (9, 13, False), (15, 12, True), (5, 16, False), (12, 17, True)]):
            c = cols[k % 4]
            stamp(img, lab, NUG_BIG if big else NUG_SMALL, {"d": c[0], "M": c[1], "L": c[2], "W": c[3]}, x, y, only_rock=True)
    elif name == "aluminium_ore":
        for (x, y) in [(6, 10), (7, 10), (12, 9), (15, 11), (16, 11), (9, 12), (5, 16), (6, 17), (12, 16), (13, 17), (15, 18)]:
            if lab[y, x] != ".": img[y, x, :3] = C[0] if (x + y) % 2 else C[1]
    elif name == "ice":
        for (x, y, c) in [(6, 9, 5), (7, 9, 5), (7, 10, 4), (11, 8, 5), (14, 10, 4), (5, 16, 4), (6, 15, 5), (12, 17, 3)]:
            if lab[y, x] != ".": img[y, x, :3] = ICE[c]
    elif name == "basalt_core":
        for y in (11, 16):
            for x in range(24):
                if lab[y, x] in "fFs": img[y, x, :3] = H("6e4238"); 
                if lab[y, x] in "fFs" and lab[y + 1, x] in "fFs": img[y + 1, x, :3] = H("4a2a28")
        for x in (9, 13):
            for y in range(8, 20):
                if lab[y, x] in "fF" and y not in (11, 12, 16, 17): img[y, x, :3] = BASALT[1]
    elif name == "geode":
        # split open on top: a jagged crack with violet crystal inside
        crack = ["..oo.oo..", ".oLWLMLo.", "oMLDLWMDo", ".oDMDMDo.", "..o.oo..."]
        stamp(img, lab, crack, {"o": OUTLINE, "W": C[3], "L": C[2], "M": C[1], "D": C[0]}, 7, 7)
    elif name == "sulphur":
        # a whole lump of pale lemon sulphur crust, speckled like aluminium (Zachary: too like gold before)
        for (x, y) in [(6, 10), (12, 9), (13, 9), (15, 11), (9, 12), (10, 12), (5, 16), (12, 16), (13, 17), (16, 17), (8, 18)]:
            if lab[y, x] != ".": img[y, x, :3] = C[0] if (x + y) % 2 else C[1]
        for (x, y) in [(8, 9), (14, 10), (7, 15), (11, 18)]:
            if lab[y, x] != ".": img[y, x, :3] = C[3]
    elif name == "titanium_ore":
        put_crystal(img, "big", 11, 12, C, 0)
        put_crystal(img, "mid", 16, 13, C, 1)
        put_crystal(img, "small", 7, 14, C, -1)
    elif name == "carbon":
        # dark graphite seams running through the rock, as on the carbon icon
        for pts in ([(6, 10), (7, 10), (8, 11), (9, 11), (10, 11), (11, 10), (12, 10), (13, 11), (14, 11)],
                    [(4, 16), (5, 16), (6, 17), (7, 17), (8, 17), (9, 16), (10, 16), (11, 17), (12, 17), (13, 17), (14, 16)],
                    [(15, 13), (16, 14), (17, 14), (18, 15), (19, 15)]):
            for i, (x, y) in enumerate(pts):
                if lab[y, x] != ".":
                    img[y, x, :3] = C[0]
                    if lab[y + 1, x] != ".": img[y + 1, x, :3] = C[1]
                    if i % 3 == 1 and lab[y - 1, x] != ".": img[y - 1, x, :3] = C[2]
    elif name == "quartz":
        put_crystal(img, "big", 12, 12, C, 0)
        put_crystal(img, "mid", 7, 13, C, -1)
        put_crystal(img, "mid", 17, 13, C, 1)
        put_crystal(img, "small", 10, 15, C, -1)
    elif name == "lithium_salts":
        pal = {"o": OUTLINE, "T": C[3], "F": C[2], "S": C[1]}
        stamp(img, lab, CUBE, pal, 9, 4); stamp(img, lab, CUBE_S, pal, 4, 8); stamp(img, lab, CUBE, pal, 13, 8)
        stamp(img, lab, CUBE_S, pal, 8, 10)
        img[5, 10, :3] = H("ffffff"); img[9, 14, :3] = H("ffffff")
    elif name == "silica_sand":
        yy, xx = np.mgrid[0:24, 0:24] + 0.5
        mound = (((xx - 12) / 8.5) ** 2 + ((yy - 13) / 6.5) ** 2 <= 1) & (yy <= 14)
        pad = np.pad(mound, 1)
        for y, x in zip(*np.nonzero(mound)):
            lit = (x < 12 and y < 11)
            img[y, x, :3] = C[3] if lit and (x + y) % 3 else C[2] if y < 12 else C[1]; img[y, x, 3] = 255
        edge = (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]) & ~mound & (yy < 14)
        img[edge, :3] = OUTLINE; img[edge, 3] = 255
        for (x, y, c) in [(9, 9, "c99231"), (14, 10, "8f5f24"), (11, 12, "c99231"), (16, 12, "c99231"), (7, 12, "8f5f24")]:
            img[y, x, :3] = H(c)
    else:
        pal = {"d": C[0], "M": C[1], "L": C[2], "W": C[3]}
        for (x, y, big) in [(5, 9, True), (11, 7, False), (14, 9, True), (9, 11, False), (4, 15, True), (11, 16, True), (15, 15, False)]:
            stamp(img, lab, NUG_BIG if big else NUG_SMALL, pal, x, y, only_rock=True)
    return np.concatenate([img, rubble(GREY, C)], axis=1)


def rubble(R, C=None):
    W = Hh = 24
    img = np.zeros((Hh, W, 4), np.uint8)
    lab = np.full((Hh, W), ".", "<U1")
    for top, front in [([(4, 18), (6, 16), (9, 16), (10, 18)], [(4, 18), (10, 18), (10, 21), (4, 21)]),
                       ([(11, 19), (13, 17), (17, 17), (18, 19)], [(11, 19), (18, 19), (18, 21), (11, 21)]),
                       ([(9, 15), (11, 14), (13, 15)], [(9, 15), (13, 15), (13, 17), (9, 17)])]:
        lab[poly(front, W, Hh)] = "f"; lab[poly(top, W, Hh)] = "t"
    m = lab != "."
    for y, x in zip(*np.nonzero(m)):
        img[y, x, :3] = R[4] if lab[y, x] == "t" else R[2]; img[y, x, 3] = 255
    pad = np.pad(m, 1)
    edge = (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]) & ~m
    img[edge, :3] = OUTLINE; img[edge, 3] = 255
    img[m & ~pad[2:, 1:-1], :3] = INNER
    if C is not None:
        img[17, 7, :3] = C[2]; img[18, 14, :3] = C[1]; img[18, 15, :3] = C[3]
    return img


def boulder(R, moss=False, seed=3):
    img, lab = rock("big", R, seed=seed, moss=moss)
    for (pts, c) in [([(20, 27), (21, 28), (21, 29), (22, 30), (22, 31), (23, 32)], 0), ([(38, 27), (38, 28), (39, 29), (39, 30)], 0),
                     ([(26, 14), (27, 15), (29, 15)], 3)]:
        for (x, y) in pts:
            if lab[y, x] != ".": img[y, x, :3] = R[c]
    return img


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/rocks6"
    os.makedirs(out, exist_ok=True)
    sv = lambda a, n: Image.fromarray(a, "RGBA").save(os.path.join(out, n + ".png"))
    bands = {"rock": (BROWN, False), "lush": (GREY, True), "steam": (SLATE, False)}
    for band, (R, moss) in bands.items():
        for i, shp in enumerate("abc"):
            whole, _ = rock(shp, R, seed=i * 7 + 1, moss=moss)
            sv(np.concatenate([whole, rubble(R)], axis=1), "stone" if (band, i) == ("rock", 0) else "stone_%s_%d" % (band, i))
        sv(boulder(R, moss), "boulder_" + band)
    for n in ("copper_ore", "iron_ore", "gold_ore", "titanium_ore", "carbon", "quartz", "lithium_salts", "silica_sand",
              "aluminium_ore", "rare_earths", "thermal_quartz", "sulphur", "ice", "basalt_core", "cobalt_60", "geode"):
        sv(node(n), n)
    sv(boulder(GREY, True, seed=5), "boulder")
    print("ok")
