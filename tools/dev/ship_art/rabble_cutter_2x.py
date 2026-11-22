"""Rabble cutter at double resolution: 48 px per cell, 6 x 4 cells = 288 x 192."""
import sys, random
from pathlib import Path
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import numpy as np
from pixkit import Pix
from cultures import thruster

S = 2
def s(pts): return [(x * S, y * S) for x, y in pts]
def sr(r): return tuple(v * S for v in r)

def hazard(p, m, step=6):
    yy, xx = np.mgrid[0:p.h, 0:p.w]
    m = m & (p.tone >= 0)
    p.mat[m] = "yellow"
    st = m & (((xx + yy) // step) % 2 == 0)
    p.mat[st] = "dark"; p.tone[st] = np.maximum(p.tone[st] - 1, 1)

def rivet_row(p, x0, x1, y, step=6):
    for x in range(x0, x1 + 1, step):
        p.rivet(x, y)

def plate(p, r, mat, clip, face=4, rivets=True, seams=0, rng=None):
    x0, y0, x1, y1 = r
    m = p.mask(rect=r) & clip
    p.bevel(m, mat, width=3, face=face, shade_lower=False)
    if rivets:
        for (rx, ry) in ((x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3)):
            p.rivet(rx, ry)
        rivet_row(p, x0 + 9, x1 - 9, y0 + 3, 8)
    for k in range(seams):
        x = x0 + (k + 1) * (x1 - x0) // (seams + 1)
        p.engrave([(x, y0 + 4), (x, y1 - 4)])

def skull(p, x, y):
    rows = ["..XXXXXX..", ".XXXXXXXX.", "XXXXXXXXXX", "XX..XX..XX", "XX..XX..XX", "XXXXXXXXXX",
            ".XXXX.XXX.", "..XXXXXX..", "..X.XX.X..", "..XXXXXX.."]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if p.tone[y + j, x + i] < 0: continue
            if ch == "X":
                p.mat[y + j, x + i] = "bone"; p.tone[y + j, x + i] = 5 if j < 3 else (4 if j < 7 else 3)
            else:
                p.mat[y + j, x + i] = "dark"; p.tone[y + j, x + i] = 1

def cutter():
    p = Pix(288, 192)
    rng = random.Random(9)
    # armour skirts with spikes
    skirt = s([(14, 14), (96, 14), (112, 24), (100, 26), (18, 26)])
    p.bevel(p.mask(polygon=skirt), "gunmetal", width=3, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=[(x, 191 - y) for x, y in skirt]), "gunmetal", width=3, face=3, edge_light=4, shade_lower=False)
    for x in range(40, 190, 16):
        p.engrave([(x, 30), (x + 4, 50)]); p.engrave([(x, 161), (x + 4, 141)])
    for x in (48, 80, 112, 144, 176):
        p.bevel(p.mask(polygon=[(x, 31), (x + 6, 14), (x + 12, 31)]), "silver", width=2, face=4, shade_lower=False)
        p.bevel(p.mask(polygon=[(x, 160), (x + 6, 177), (x + 12, 160)]), "silver", width=2, face=3, shade_lower=False)
    rivet_row(p, 40, 190, 34, 7); rivet_row(p, 40, 190, 157, 7)
    # engine block and burners
    p.bevel(p.mask(rect=sr((6, 24, 30, 71))), "gunmetal", width=3, face=3)
    p.slot(46, 58, 56, 59); p.slot(46, 63, 56, 64); p.slot(46, 128, 56, 129); p.slot(46, 133, 56, 134)
    for (y0, y1) in ((52, 84), (106, 138)):
        p.tube(p.mask(rect=(4, y0, 40, y1)), "metal", "x", bands=(5, 5, 4, 4, 3, 3, 3, 2, 2, 1))
        p.tube(p.mask(rect=(4, y0 + 4, 12, y1 - 4)), "dark", "x", shadow=False)
        for x in (18, 24, 30):
            p.engrave([(x, y0 + 2), (x, y1 - 2)])
        p.paint(p.mask(rect=(34, y0, 37, y1)), "yellow")
        thruster(p, 4, y0 + 2, y1 - 2, "glow", 13)
    p.tube(p.mask(rect=(8, 88, 28, 102)), "rust", "x")
    p.engrave([(16, 89), (16, 101)])
    thruster(p, 8, 90, 100, "glow_red", 7)
    # the hull wedge
    body = s([(22, 26), (98, 22), (122, 32), (140, 44), (140, 52), (122, 64), (98, 74), (22, 70)])
    bm = p.mask(polygon=body)
    p.bevel(bm, "rust", width=5, face=3, edge_light=5)
    for (x, y) in ((70, 60), (150, 130), (120, 54), (186, 140)):
        p.engrave([(x, y), (x + 6, y + 3), (x + 10, y + 2)], highlight=False)
    # layered armour plates
    plate(p, (60, 58, 120, 92), "gunmetal", bm, seams=1)
    plate(p, (60, 100, 116, 132), "rust", bm, face=3, seams=1)
    plate(p, (124, 56, 184, 88), "metal", bm, seams=2)
    plate(p, (124, 100, 188, 136), "gunmetal", bm, seams=2)
    # vents and a hatch
    for i in range(4):
        p.slot(132, 64 + i * 5, 150, 65 + i * 5)
    p.engrave_rect(140, 108, 162, 128); p.rivet(144, 112); p.rivet(158, 112); p.rivet(144, 124); p.rivet(158, 124)
    p.bevel(p.mask(rect=(148, 116, 154, 119)), "dark", width=1, face=3, shade_lower=False)
    # a crooked patch welded over a hole, with weld beads
    patch = [(86, 104), (106, 100), (110, 116), (92, 120)]
    p.bevel(p.mask(polygon=patch), "metal", width=2, face=3, shade_lower=False)
    for (x, y) in ((88, 105), (96, 103), (104, 101), (108, 108), (109, 114), (100, 118), (93, 118), (90, 112)):
        p.rivet(x, y)
    # stripe and scorch
    p.paint(p.mask(polygon=s([(22, 46), (130, 44), (131, 49), (22, 50)])), "banner")
    p.engrave([(46, 92), (260, 88)], highlight=False); p.engrave([(46, 99), (262, 97)])
    for (cx, cy, r) in ((140, 118, 6), (200, 72, 5), (90, 76, 4)):
        p.shade(p.mask(ellipse=(cx - r - 3, cy - r, cx + r + 3, cy + r)), -2)
        p.shade(p.mask(ellipse=(cx - r // 2, cy - 1, cx + r // 2, cy + 1)), -1)
    # ram prow with hazard stripes and spikes
    ram = s([(104, 30), (122, 32), (143, 46), (143, 50), (122, 64), (104, 66), (114, 48)])
    p.bevel(p.mask(polygon=ram), "gunmetal", width=4, face=4)
    hazard(p, p.mask(polygon=s([(108, 34), (120, 35), (126, 46), (126, 50), (120, 61), (108, 62), (116, 48)])))
    for (y0, y1, x0) in ((66, 80, 254), (86, 106, 270), (112, 126, 254)):
        p.bevel(p.mask(polygon=[(x0, y0), (min(287, x0 + 20), (y0 + y1) // 2), (x0, y1)]), "silver", width=2, face=4, shade_lower=False)
    rivet_row(p, 222, 240, 64, 6); rivet_row(p, 222, 240, 131, 6)
    # gun turrets, twin barrels
    for (cx, cy) in ((150, 68), (156, 120)):
        p.bevel(p.mask(ellipse=(cx - 15, cy - 15, cx + 15, cy + 15)), "gunmetal", width=3, face=4, shade_lower=False)
        p.engrave([(cx - 12, cy), (cx + 12, cy)])
        p.dome(p.mask(ellipse=(cx - 9, cy - 9, cx + 9, cy + 9)), "metal", shadow=False)
        for dy in (-4, 3):
            p.tube(p.mask(rect=(cx + 8, cy + dy, cx + 40, cy + dy + 2)), "metal", "x", bands=(5, 3, 2))
            p.tube(p.mask(rect=(cx + 36, cy + dy - 1, cx + 42, cy + dy + 3)), "gunmetal", "x", bands=(4, 3, 2, 1))
        p.glow(p.mask(rect=(cx - 2, cy - 2, cx + 1, cy + 1)), "glow_red", 3)
    # cockpit bubble, red glass, with a frame and struts
    p.bevel(p.mask(ellipse=(190, 74, 230, 114)), "gunmetal", width=4, face=3, shade_lower=False)
    p.dome(p.mask(ellipse=(196, 80, 224, 108)), "red")
    p.engrave([(210, 81), (210, 107)], highlight=False)
    # cables with clamps along the hull
    for (x0, x1, y) in ((48, 120, 47), (64, 140, 137)):
        p.tube(p.mask(rect=(x0, y, x1, y + 4)), "strap", "x", bands=(5, 4, 2, 1, 1))
        for x in range(x0 + 8, x1, 18):
            p.bevel(p.mask(rect=(x, y - 1, x + 3, y + 5)), "metal", width=1, face=4, shade_lower=False)
    # the mast and flag, a painted skull, running lights
    flag = [(76, 76), (44, 68), (48, 78), (42, 88), (76, 82)]
    p.bevel(p.mask(polygon=flag), "banner", width=2, face=3, shade_lower=False)
    p.dome(p.mask(ellipse=(74, 72, 86, 84)), "metal", shadow=True)
    skull(p, 70, 110)
    for (x, y, c) in ((196, 32, "glow_red"), (196, 158, "glow_red"), (230, 66, "glow_yellow"), (230, 124, "glow_yellow")):
        p.glow(p.mask(rect=(x, y, x + 2, y + 2)), c, 3)

    # weathering: rust creeping onto grey plates, grime dither, drips under rivets
    yy, xx = np.mgrid[0:p.h, 0:p.w]
    grey = np.isin(p.mat, ["gunmetal", "metal"]) & (p.tone >= 2)
    for _ in range(14):
        cx, cy, r = rng.randrange(40, 250), rng.randrange(20, 172), rng.randrange(3, 7)
        blob = grey & ((xx - cx) ** 2 + ((yy - cy) * 1.6) ** 2 < r * r) 
        p.mat[blob] = "rust"; p.tone[blob] = np.clip(p.tone[blob] - 1, 1, 3)
    nr = np.random.default_rng(4).random((p.h, p.w))
    grime = (p.tone >= 3) & np.isin(p.mat, ["gunmetal", "metal", "rust"]) & (nr < 0.05)
    p.shade(grime, -1)
    for (x, y) in ((70, 64), (96, 64), (134, 60), (170, 60), (72, 104), (130, 104), (178, 104)):
        for k in range(1, rng.randrange(4, 9)):
            if p.tone[y + k, x] >= 0: p.mat[y + k, x] = "rust"; p.tone[y + k, x] = max(1, 3 - k // 3)
    # a lashed-down cargo crate and an antenna
    p.bevel(p.mask(rect=(98, 62, 114, 76)), "crate_red", width=2, face=4)
    p.engrave([(99, 69), (113, 69)]); p.engrave([(106, 63), (106, 75)])
    p.paint(p.mask(rect=(97, 66, 115, 67)), "strap")
    p.paint(p.mask(rect=(176, 95, 190, 96)), "metal"); p.glow(p.mask(rect=(174, 94, 176, 97)), "glow_red", 2)
    return p

# Rooms and doors: must match ShipData.ENEMIES["rabble_cutter"] in scripts/ship_data.gd (cells of 24 game px,
# 48 art px). Engines at the back, the cockpit under the red bubble, turrets over the weapons and oxygen rooms.
ROOMS = {
    "engines": (1, 1, 1, 2, "engines"), "crew": (2, 1, 1, 1, "crew"), "shields": (2, 2, 1, 1, "shields"),
    "weapons": (3, 1, 1, 1, "weapons"), "life": (3, 2, 1, 1, "life"), "pilot": (4, 1, 1, 2, "pilot"),
}
DOORS = [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (2, 2)), ((2, 1), (3, 1)), ((2, 2), (3, 2)),
         ((3, 1), (3, 2)), ((3, 1), (4, 1)), ((3, 2), (4, 2))]


if __name__ == "__main__" and len(sys.argv) > 1:
    from kit2x import interior
    root = Path(sys.argv[1])
    out = root / "art/ships/rabble_cutter"
    out.mkdir(parents=True, exist_ok=True)
    cutter().render().save(out / "hull.png")
    interior(cutter(), ROOMS, DOORS).render().save(out / "interior.png")
    print("ok")
elif __name__ == "__main__":
    from PIL import Image
    im = cutter().render()
    im.save("/home/claude/work/ships/one/rabble_cutter_2x.png")
    old = Image.open("/home/claude/work/ships/one/rabble_cutter.png")
    sheet = Image.new("RGBA", (old.width * 3 + im.width * 3 // 2 + 40, 300), (20, 24, 36, 255))
    sheet.alpha_composite(old.resize((old.width * 3, old.height * 3), Image.NEAREST), (10, 6))
    sheet.alpha_composite(im.resize((im.width * 3 // 2, im.height * 3 // 2), Image.NEAREST), (old.width * 3 + 30, 6))
    sheet.save("/home/claude/work/ships/rabble_1x_vs_2x.png")
    im.resize((im.width * 3, im.height * 3), Image.NEAREST).save("/home/claude/work/ships/rabble_2x_zoom.png")
