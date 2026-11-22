"""The Rabble cutter, ship 1 of the one-by-one redraw (Claude, 21 Nov 2026): 6 x 4 cells, more detail. Draft."""
import sys, random
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import numpy as np
from pixkit import Pix
from cultures import thruster, skull, mirror

def hazard(p, m, step=4):
    yy, xx = np.mgrid[0:p.h, 0:p.w]
    m = m & (p.tone >= 0)
    p.mat[m] = "yellow"
    stripe = m & (((xx + yy) // step) % 2 == 0)
    p.mat[stripe] = "dark"; p.tone[stripe] = np.maximum(p.tone[stripe] - 1, 1)

def rabble_cutter():
    p = Pix(144, 96)
    rng = random.Random(9)
    # side armour skirts (lower layer), top and bottom, with spikes along their edges
    skirt = [(14, 14), (96, 14), (112, 24), (100, 26), (18, 26)]
    p.bevel(p.mask(polygon=skirt), "gunmetal", width=2, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=mirror(skirt, 96)), "gunmetal", width=2, face=3, edge_light=4, shade_lower=False)
    for x in (24, 40, 56, 72, 88):
        p.bevel(p.mask(polygon=[(x, 15), (x + 3, 8), (x + 6, 15)]), "silver", width=1, face=4, shade_lower=False)
        p.bevel(p.mask(polygon=[(x, 80), (x + 3, 87), (x + 6, 80)]), "silver", width=1, face=3, shade_lower=False)
    # engine block at the back: two big burners and a small mismatched one
    p.bevel(p.mask(rect=(6, 24, 30, 71)), "gunmetal", width=2, face=3)
    for (y0, y1) in ((26, 42), (53, 69)):
        p.tube(p.mask(rect=(2, y0, 20, y1)), "metal", "x")
        p.tube(p.mask(rect=(2, y0 + 2, 6, y1 - 2)), "dark", "x", shadow=False)
        for x in (10, 15):
            p.engrave([(x, y0 + 1), (x, y1 - 1)])
        thruster(p, 2, y0 + 1, y1 - 1, "glow", 7)
    p.tube(p.mask(rect=(4, 44, 14, 51)), "rust", "x")
    thruster(p, 4, 45, 50, "glow_red", 4)
    # the main hull: a rusty wedge
    body = [(22, 26), (98, 22), (122, 32), (140, 44), (140, 52), (122, 64), (98, 74), (22, 70)]
    bm = p.mask(polygon=body)
    p.bevel(bm, "rust", width=3, face=3, edge_light=5)
    # armour plates, layered and mismatched
    plates = [((30, 29, 60, 46), "gunmetal"), ((30, 50, 58, 66), "rust"), ((62, 28, 92, 44), "metal"), ((62, 50, 94, 68), "gunmetal")]
    for (r, mat) in plates:
        m = p.mask(rect=r) & bm
        p.bevel(m, mat, width=2, face=4, shade_lower=False)
        x0, y0, x1, y1 = r
        for (rx, ry) in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2), ((x0 + x1) // 2, y0 + 2)):
            p.rivet(rx, ry)
    # a small patch plate welded crooked over a hole
    p.bevel(p.mask(polygon=[(44, 52), (54, 50), (56, 58), (46, 60)]), "metal", width=1, face=3, shade_lower=False)
    p.rivet(46, 53); p.rivet(53, 52); p.rivet(48, 58)
    # the red stripe across the hull, and scorch marks
    p.paint(p.mask(polygon=[(22, 46), (130, 44), (131, 49), (22, 50)]), "banner")
    for (cx, cy) in ((70, 58), (100, 36)):
        m = p.mask(ellipse=(cx - 3, cy - 2, cx + 3, cy + 2))
        p.shade(m, -2)
    # the ram prow, with hazard stripes and big spikes
    ram = [(104, 30), (122, 32), (143, 46), (143, 50), (122, 64), (104, 66), (114, 48)]
    p.bevel(p.mask(polygon=ram), "gunmetal", width=2, face=4)
    hazard(p, p.mask(polygon=[(108, 34), (120, 35), (126, 46), (126, 50), (120, 61), (108, 62), (116, 48)]))
    for (y0, y1, x0) in ((34, 40, 128), (44, 52, 136), (56, 62, 128)):
        p.bevel(p.mask(polygon=[(x0, y0), (min(143, x0 + 10), (y0 + y1) // 2), (x0, y1)]), "silver", width=1, face=4, shade_lower=False)
    # the gun deck: two turrets on the top plate, barrels forward
    for (cx, cy) in ((74, 34), (78, 60)):
        p.bevel(p.mask(ellipse=(cx - 7, cy - 7, cx + 7, cy + 7)), "gunmetal", width=2, face=4, shade_lower=False)
        p.dome(p.mask(ellipse=(cx - 4, cy - 4, cx + 4, cy + 4)), "metal", shadow=False)
        p.tube(p.mask(rect=(cx + 4, cy - 2, cx + 20, cy - 1)), "metal", "x", bands=(5, 3))
        p.tube(p.mask(rect=(cx + 4, cy + 1, cx + 20, cy + 2)), "metal", "x", bands=(4, 2))
    # the cockpit: a red-tinted bubble, off to one side
    p.bevel(p.mask(ellipse=(96, 38, 114, 56)), "gunmetal", width=2, face=3, shade_lower=False)
    p.dome(p.mask(ellipse=(98, 40, 112, 54)), "red")
    # cables and exhaust pipes along the hull
    p.tube(p.mask(rect=(24, 23, 60, 25)), "strap", "x", bands=(4, 2, 1))
    p.tube(p.mask(rect=(32, 68, 70, 70)), "strap", "x", bands=(4, 2, 1))
    # a mast with the Rabble's flag, and a skull painted on the top plate
    p.dome(p.mask(ellipse=(38, 36, 44, 42)), "metal", shadow=True)
    flag = p.mask(polygon=[(38, 38), (22, 34), (24, 39), (21, 44), (38, 41)])
    p.tone[flag] = 3; p.mat[flag] = "banner"
    p.set_tone(p.mask(polygon=[(38, 38), (22, 34), (23, 36), (38, 39)]), 4)
    skull(p, 26, 36) if False else None
    skull(p, 66, 32 + 0) if False else None
    skull(p, 34, 54)
    # vents on the back plate
    for i in range(3):
        p.slot(64, 47 + i * 0 - 9 + i * 0, 64, 47) if False else None
    for i in range(3):
        p.slot(84 - i * 0, 38 + i * 0, 84, 38) if False else None
    p.slot(32, 30, 40, 31); p.slot(32, 33, 40, 34)
    # running lights
    p.glow(p.mask(rect=(98, 16, 99, 17)), "glow_red", 3); p.glow(p.mask(rect=(98, 78, 99, 79)), "glow_red", 3)
    return p

if __name__ == "__main__":
    from PIL import Image
    old = Image.open("/home/claude/work/ships/cult2/rabble_cutter.png")
    new = rabble_cutter().render()
    new.save("/home/claude/work/ships/one/rabble_cutter.png")
    sheet = Image.new("RGBA", (old.width * 4 + new.width * 4 + 30, 96 * 4 + 20), (20, 24, 36, 255))
    sheet.alpha_composite(old.resize((old.width * 4, old.height * 4), Image.NEAREST), (10, 10))
    sheet.alpha_composite(new.resize((new.width * 4, new.height * 4), Image.NEAREST), (old.width * 4 + 20, 10))
    sheet.save("/home/claude/work/ships/one/rabble_compare.png")
