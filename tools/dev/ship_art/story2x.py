"""The story ships at double resolution, 48 px per cell (Claude, 21 Nov 2026). Top-down, nose right.

  starter            the approved fighter (starter.py), redrawn at 2x with the same shape
  ivan_flagship      Ivan (boss), 9 x 6: big and ugly, a heavy gun mount for his overcharged cannon
  ana_corsair        Ana (boss), 7 x 5: sleek and fast, a navigator's ship, big engines, small guns
  loyalist_gunship   Ivan's loyalists, 5 x 4: a Rabble cutter variant with more guns
  covered_fighter    yours after Freya's quest, 9 x 5: the fighter under the tarp in the bay (art/lunar/tarp_fighter.png)

Run from the repo root:  python3 -I tools/dev/ship_art/story2x.py <out dir> [ids]
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from scipy import ndimage
from pixkit import Pix
from kit2x import (S, mirror, grid, rivet_row, rivet_col, plate, hazard, windows, lit_windows, thruster, nozzle,
                   turret, light, skull, stencil, wear, scorch, cable, sheet)
import starter as st1


# ---------------------------------------------------------------- the starter fighter, 7 x 4

def starter():
    p = Pix(336, 192)
    H = p.h
    WING, BAND, BODY = S(st1.WING), S(st1.BAND), S(st1.BODY)
    for pts, face in ((WING, 4), (mirror(WING, H), 3)):
        p.bevel(p.mask(polygon=pts), "hull", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
    for pts in (BAND, mirror(BAND, H)):
        p.paint(p.mask(polygon=pts), "orange")
    for (a, b) in (((92, 48), (84, 8)), ((140, 48), (122, 14)), ((166, 48), (140, 22))):
        p.engrave([a, b]); p.engrave(mirror([a, b], H))
    # flaps along the wings' back edges
    for top in (True, False):
        pts = [(78, 46), (92, 46), (84, 26), (76, 30)]
        p.engrave((pts + pts[:1]) if top else mirror(pts + pts[:1], H))
    rivet_row(p, 96, 160, 44, 8); rivet_row(p, 96, 160, 147, 8)
    # guns near the wing tips
    for y in (18, H - 1 - 18):
        p.bevel(p.mask(rect=(104, y - 6, 132, y + 6)), "metal", width=2, face=4 if y < 96 else 3, shade_lower=False)
        p.tube(p.mask(rect=(130, y - 3, 162, y + 2)), "metal", "x", bands=(5, 4, 3, 2, 1, 1))
        p.tube(p.mask(rect=(160, y - 4, 166, y + 3)), "gunmetal", "x", bands=(4, 3, 2, 1))
        p.slot(110, y - 2, 124, y - 1)
    # the hull
    p.bevel(p.mask(polygon=BODY), "hull", width=5, face=3, edge_light=5)
    p.bevel(p.mask(polygon=[(80, 58), (236, 58), (264, 72), (264, 118), (236, 132), (80, 132)]), "hull", width=3, face=4)
    for x in (104, 140):
        p.paint(p.mask(polygon=[(x, 44), (x + 14, 44), (x + 30, 94), (x + 16, 94)]), "orange")
        p.paint(p.mask(polygon=[(x + 16, 96), (x + 30, 96), (x + 14, 146), (x, 146)]), "orange")
    p.paint(p.mask(polygon=[(312, 76), (332, 88), (332, 102), (312, 114)]), "orange")
    p.engrave([(80, 50), (80, 140)]); p.engrave([(188, 50), (188, 140)]); p.engrave([(300, 62), (300, 128)])
    p.engrave([(82, 76), (186, 76)]); p.engrave([(82, 114), (186, 114)])
    p.engrave_rect(50, 102, 74, 126)
    p.bevel(p.mask(rect=(58, 110, 66, 118)), "metal", width=1, face=3, shade_lower=False)
    for i in range(3):
        p.slot(166, 62 + i * 6, 182, 63 + i * 6); p.slot(166, 116 + i * 6, 182, 117 + i * 6)
    rivet_row(p, 88, 184, 52, 8); rivet_row(p, 88, 184, 138, 8)
    rivet_col(p, 194, 62, 128, 9)
    stencil(p, 200, 136, "07")
    # the pods, ribbed, with orange bands, and their nozzles
    for (y0, y1) in S(st1.PODS):
        p.tube(p.mask(rect=(28, y0, 92, y1)), "metal", "x", bands=(5, 5, 4, 4, 3, 3, 3, 2, 2, 1))
        p.paint(p.mask(rect=(44, y0, 50, y1)), "orange")
        for x in (36, 58, 66, 74, 84):
            p.engrave([(x, y0 + 1), (x, y1 - 1)])
        p.slot(68, y0 + 8, 76, y0 + 10)
        nozzle(p, 16, y0 + 4, 30, y1 - 4, "glow", 13, mat="gunmetal")
    # the long canopy, with struts and a frame
    p.bevel(p.mask(ellipse=(196, 62, 304, 128)), "metal", width=3, face=3, shade_lower=False)
    p.dome(p.mask(ellipse=(202, 68, 298, 122)), "glass")
    p.engrave([(250, 69), (250, 121)], highlight=False)
    p.engrave([(226, 72), (222, 118)], highlight=False); p.engrave([(274, 72), (278, 118)], highlight=False)
    for a in range(14):
        ang = a * np.pi / 7
        p.rivet(int(250 + 52 * np.cos(ang)), int(95 + 31 * np.sin(ang)))
    # running lights
    light(p, 92, 4, "glow_green"); light(p, 92, H - 6, "glow_red")
    light(p, 316, 66, "glow_green"); light(p, 316, 124, "glow_red")
    wear(p, random.Random(2), grime=0.008, mats=("hull",), scuffs=10)
    return p


# ---------------------------------------------------------------- Ivan's flagship, 9 x 6

def big_skull(p, x, y):
    """The Rabble skull painted twice the size."""
    q = Pix(10, 10)
    q.tone[:] = 3
    skull(q, 0, 0)
    for j in range(10):
        for i in range(10):
            for dy in (0, 1):
                for dx in (0, 1):
                    yy, xx = y + j * 2 + dy, x + i * 2 + dx
                    if p.tone[yy, xx] >= 0:
                        p.mat[yy, xx] = q.mat[j, i]; p.tone[yy, xx] = q.tone[j, i]


def ivan_flagship():
    """An old ore hauler the Rabble welded armour, guns and trophies onto. Ivan's overcharged cannon runs down the spine."""
    p = Pix(432, 288)
    H = p.h
    rng = random.Random(31)
    yy, xx = grid(p)
    # a captured Terran wing welded on as armour, under the skirt
    wing = [(176, 226), (246, 226), (232, 272), (204, 282), (184, 276)]
    p.bevel(p.mask(polygon=wing), "white", width=2, face=3, shade_lower=False)
    p.paint(p.mask(polygon=[(208, 226), (218, 226), (212, 276), (204, 278)]), "trim_blue")
    for (x, y) in ((188, 270), (226, 268), (200, 278)):
        p.rivet(x, y)
    # side armour skirts with spikes
    skirt = [(40, 34), (300, 34), (340, 56), (300, 64), (44, 64)]
    for pts, face in ((skirt, 4), (mirror(skirt, H), 3)):
        p.bevel(p.mask(polygon=pts), "gunmetal", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
    for x in range(70, 300, 22):
        p.engrave([(x, 38), (x + 6, 62)]); p.engrave([(x, 249), (x + 6, 225)])
        p.bevel(p.mask(polygon=[(x, 36), (x + 7, 16), (x + 14, 36)]), "silver", width=2, face=4, shade_lower=False)
        if not 170 < x < 250:
            p.bevel(p.mask(polygon=[(x, 251), (x + 7, 271), (x + 14, 251)]), "silver", width=2, face=3, shade_lower=False)
    rivet_row(p, 56, 300, 58, 7); rivet_row(p, 56, 300, 229, 7)
    # the hauler's hull
    body = [(30, 56), (330, 56), (372, 84), (400, 120), (400, 168), (372, 204), (330, 232), (30, 232)]
    bm = p.mask(polygon=body)
    p.bevel(bm, "rust", width=6, face=3, edge_light=5)
    # welded plates in a messy grid
    for (x0, y0, x1, y1, mat) in ((60, 70, 140, 120, "gunmetal"), (60, 168, 138, 218, "rust"), (148, 66, 220, 112, "metal"),
                                  (150, 176, 226, 222, "gunmetal"), (228, 70, 300, 118, "rust"), (232, 170, 306, 220, "metal"),
                                  (96, 124, 128, 164, "metal")):
        plate(p, (x0, y0, x1, y1), mat, bm, face=4 if y0 < 140 else 3, seams=2)
    for (x, y) in ((200, 100), (90, 196), (270, 196), (300, 88), (130, 84)):
        scorch(p, x, y, rng.randint(4, 7))
    # the cannon: a long gold-banded barrel down the spine, on a turret ring, with glowing coils
    p.bevel(p.mask(ellipse=(118, 108, 198, 180)), "gunmetal", width=4, face=4, shade_lower=False)
    for a in range(16):
        ang = a * np.pi / 8
        p.rivet(int(158 + 36 * np.cos(ang)), int(144 + 32 * np.sin(ang)))
    p.bevel(p.mask(rect=(140, 124, 230, 164)), "gunmetal", width=3, face=4)
    p.tube(p.mask(rect=(226, 132, 404, 156)), "metal", "x", bands=(5, 5, 4, 4, 3, 3, 2, 2, 1))
    for x in range(244, 380, 24):
        p.tube(p.mask(rect=(x, 128, x + 8, 160)), "gold", "x", bands=(5, 4, 4, 3, 2, 1))
        p.glow(p.mask(rect=(x + 2, 141, x + 6, 147)), "glow_yellow", 3)
    p.tube(p.mask(rect=(400, 126, 420, 162)), "gunmetal", "x", bands=(4, 4, 3, 3, 2, 1, 1))
    p.tube(p.mask(rect=(416, 136, 422, 152)), "dark", "x", shadow=False)
    for k in range(3):
        p.glow(p.mask(rect=(148 + k * 6, 136, 150 + k * 6, 152)), "glow_yellow", 3 + (k == 1))
    for i in range(4):
        p.slot(170, 130 + i * 8, 214, 131 + i * 8)
    # ram jaws at the front with hazard stripes
    for top in (True, False):
        jaw = [(340, 70), (380, 92), (424, 112), (406, 122), (368, 116), (344, 104)]
        pts = jaw if top else mirror(jaw, H)
        p.bevel(p.mask(polygon=pts), "gunmetal", width=3, face=4 if top else 3, shade_lower=False)
        hazard(p, p.mask(polygon=[(352, 80), (378, 96), (400, 110), (372, 110), (352, 100)] if top else
                         mirror([(352, 80), (378, 96), (400, 110), (372, 110), (352, 100)], H)))
    # the bridge: a welded box with red windows, a big skull, Ivan's banner
    p.bevel(p.mask(polygon=[(300, 96), (344, 96), (360, 112), (360, 124), (300, 124)]), "gunmetal", width=3, face=4)
    p.bevel(p.mask(polygon=[(300, 164), (360, 164), (360, 176), (344, 192), (300, 192)]), "gunmetal", width=3, face=3)
    lit_windows(p, 310, 106, 5, 9, mat="glow_red"); lit_windows(p, 310, 180, 5, 9, mat="glow_red")
    big_skull(p, 70, 176)
    flag = [(130, 100), (84, 112), (96, 120), (82, 130), (130, 126)]
    p.dome(p.mask(ellipse=(124, 106, 136, 118)), "gold", shadow=True)
    p.bevel(p.mask(polygon=flag), "banner", width=2, face=3, shade_lower=False)
    p.paint(p.mask(rect=(98, 116, 118, 118)), "gold")
    # four turrets
    for (cx, cy) in ((110, 92), (260, 94), (112, 196), (262, 196)):
        turret(p, cx, cy, r=16, length=36)
    # cables and pipes, vents
    cable(p, 150, 300, 124); cable(p, 150, 300, 162)
    # engines: four big burners and a smoking stack
    p.bevel(p.mask(rect=(22, 70, 56, 218)), "gunmetal", width=3, face=3)
    for y in range(76, 214, 10):
        p.engrave([(26, y), (52, y)])
    for (y0, y1) in ((72, 104), (110, 140), (148, 178), (184, 216)):
        nozzle(p, 14, y0, 34, y1, "glow", 14, mat="metal")
        p.paint(p.mask(rect=(30, y0, 32, y1)), "yellow")
    light(p, 330, 60, "glow_red"); light(p, 330, 226, "glow_red")
    wear(p, rng, rust=22, grime=0.02, mats=("gunmetal", "metal"), scuffs=24)
    return p


# ---------------------------------------------------------------- Ana's corsair, 7 x 5

def ana_corsair():
    """A sleek dark needle with two big engines and small guns; gold navigation lines and a star-chart dome.
    Ana tore the Rabble insignia off: a scraped red patch where it was."""
    p = Pix(336, 240)
    H = p.h
    rng = random.Random(41)
    # swept blade wings
    wing = [(70, 96), (196, 96), (150, 52), (112, 24), (84, 14), (74, 22)]
    for pts, face in ((wing, 4), (mirror(wing, H), 3)):
        p.bevel(p.mask(polygon=pts), "navy", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
    for top in (True, False):
        line = [(84, 20), (150, 58), (190, 94)]
        p.paint(p._line(line if top else mirror(line, H), width=2), "gold")
        for (a, b) in (((110, 94), (92, 30)), ((140, 94), (120, 46))):
            p.engrave([a, b] if top else mirror([a, b], H))
    # small guns under the wings
    for y in (40, H - 1 - 40):
        p.tube(p.mask(rect=(116, y - 2, 170, y + 2)), "metal", "x", bands=(5, 4, 3, 2, 1))
        p.tube(p.mask(rect=(168, y - 3, 174, y + 3)), "gunmetal", "x", bands=(4, 3, 2, 1))
    # two big engine nacelles
    for (y0, y1) in ((62, 104), (136, 178)):
        p.tube(p.mask(rect=(26, y0, 136, y1)), "gunmetal", "x", bands=(5, 5, 4, 4, 3, 3, 3, 2, 2, 1))
        for x in range(40, 132, 12):
            p.engrave([(x, y0 + 2), (x, y1 - 2)])
        p.paint(p.mask(rect=(110, y0, 114, y1)), "gold")
        p.bevel(p.mask(polygon=[(130, y0), (150, y0 + 6), (150, y1 - 6), (130, y1)]), "gunmetal", width=2, face=4, shade_lower=False)
        p.slot(116, y0 + 10, 126, y0 + 12); p.slot(116, y1 - 12, 126, y1 - 10)
        nozzle(p, 14, y0 + 4, 32, y1 - 4, "glow_blue", 16, mat="metal")
    # the needle hull
    body = [(60, 92), (250, 88), (300, 104), (332, 118), (332, 121), (300, 136), (250, 151), (60, 147)]
    bm = p.mask(polygon=body)
    p.bevel(bm, "navy", width=5, face=3, edge_light=5)
    p.bevel(p.mask(polygon=[(90, 100), (240, 98), (280, 110), (280, 129), (240, 141), (90, 139)]), "navy", width=2, face=4)
    p.paint(p.mask(rect=(64, 118, 320, 120)) & bm, "gold")
    for x in (120, 170, 220):
        p.engrave([(x, 92), (x, 147)])
    rivet_row(p, 70, 240, 96, 9); rivet_row(p, 70, 240, 143, 9)
    for top in (True, False):
        fin = [(60, 96), (96, 96), (80, 84), (64, 82)]
        p.bevel(p.mask(polygon=fin if top else mirror(fin, H)), "navy", width=2, face=4 if top else 3, shade_lower=False)
    for (y0, y1) in ((62, 104), (136, 178)):
        for x in range(60, 104, 6):
            p.bevel(p.mask(rect=(x, y0 - 3 if y0 < 120 else y1 - 1, x + 3, y0 + 1 if y0 < 120 else y1 + 3)), "metal", width=1, face=4, shade_lower=False)
    # the scraped-off insignia: a red patch, scratched
    p.paint(p.mask(ellipse=(132, 102, 156, 116)), "banner")
    for k in range(5):
        p.engrave([(132 + k * 5, 102), (138 + k * 5, 116)], highlight=False)
    # the star-chart dome: dark glass with stars
    p.bevel(p.mask(ellipse=(176, 100, 214, 139)), "gold", width=2, face=4, shade_lower=False)
    p.dome(p.mask(ellipse=(180, 104, 210, 135)), "dark")
    for _ in range(14):
        x, y = rng.randint(184, 206), rng.randint(108, 131)
        p.glow(p.mask(rect=(x, y, x, y)), rng.choice(["glow_yellow", "glow_blue", "glow_teal"]), 4)
    # canopy
    p.bevel(p.mask(polygon=[(236, 104), (284, 110), (306, 119), (284, 129), (236, 135), (250, 119)]), "glass", width=2, face=3, shade_lower=False)
    p.set_tone(p.mask(rect=(254, 108, 274, 110)), 5)
    p.engrave([(262, 107), (262, 132)], highlight=False)
    for i in range(3):
        p.slot(92, 104 + i * 5, 112, 105 + i * 5)
    light(p, 98, 18, "glow_green"); light(p, 98, H - 20, "glow_red"); light(p, 320, 118, "glow_blue")
    wear(p, rng, grime=0.01, mats=("navy", "gunmetal"), scuffs=10)
    return p


# ---------------------------------------------------------------- loyalist gunship, 5 x 4

def loyalist_gunship():
    """Ivan's loyalists: a short, heavy Rabble cutter with four gun turrets and Ivan's gold crown on the skull."""
    p = Pix(240, 192)
    H = p.h
    rng = random.Random(51)
    skirt = [(28, 26), (176, 26), (196, 44), (180, 50), (30, 50)]
    for pts, face in ((skirt, 4), (mirror(skirt, H), 3)):
        p.bevel(p.mask(polygon=pts), "gunmetal", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
    for x in (50, 80, 110, 140):
        p.bevel(p.mask(polygon=[(x, 28), (x + 6, 10), (x + 12, 28)]), "silver", width=2, face=4, shade_lower=False)
        p.bevel(p.mask(polygon=[(x, 163), (x + 6, 181), (x + 12, 163)]), "silver", width=2, face=3, shade_lower=False)
    rivet_row(p, 40, 170, 44, 7); rivet_row(p, 40, 170, 147, 7)
    body = [(22, 46), (180, 46), (214, 72), (230, 92), (230, 99), (214, 119), (180, 145), (22, 145)]
    bm = p.mask(polygon=body)
    p.bevel(bm, "rust", width=5, face=3, edge_light=5)
    for (r, mat) in (((44, 56, 104, 92), "gunmetal"), ((44, 100, 100, 136), "rust"), ((110, 54, 170, 90), "metal"), ((108, 102, 172, 138), "gunmetal")):
        plate(p, r, mat, bm, face=4 if r[1] < 96 else 3, seams=1)
    p.paint(p.mask(rect=(22, 92, 214, 99)) & bm, "banner")
    hazard(p, p.mask(polygon=[(190, 62), (212, 78), (224, 95), (212, 113), (190, 129), (200, 95)]))
    # four turrets
    for (cx, cy) in ((74, 72), (140, 70), (74, 120), (140, 122)):
        turret(p, cx, cy, r=12, length=28)
    # skull with a gold crown, a bridge bubble
    skull(p, 176, 90)
    for (x, h) in ((176, 4), (180, 6), (184, 4)):
        p.paint(p.mask(rect=(x, 89 - h, x + 1, 89)), "gold"); p.set_tone(p.mask(rect=(x, 89 - h, x + 1, 89)), 4)
    p.paint(p.mask(rect=(176, 88, 185, 89)), "gold")
    lit_windows(p, 196, 84, 2, 6, mat="glow_red"); lit_windows(p, 196, 104, 2, 6, mat="glow_red")
    for (x, y) in ((120, 96), (60, 110)):
        scorch(p, x, y, 5)
    # engines
    p.bevel(p.mask(rect=(18, 54, 44, 138)), "gunmetal", width=3, face=3)
    for (y0, y1) in ((58, 86), (106, 134)):
        nozzle(p, 10, y0, 28, y1, "glow", 12)
    p.tube(p.mask(rect=(14, 88, 32, 104)), "rust", "x")
    thruster(p, 14, 90, 102, "glow_red", 8)
    light(p, 186, 32, "glow_red"); light(p, 186, 158, "glow_red")
    wear(p, rng, rust=12, grime=0.02, mats=("gunmetal", "metal"), scuffs=12)
    return p


# ---------------------------------------------------------------- the covered fighter, 9 x 5

def covered_fighter():
    """What's under Freya's tarp: an old long-range Terran fighter with a crew deck. One big engine, swept wings
    set back, a pointed nose; faded white with yellow trim and grey patches."""
    p = Pix(432, 240)
    H = p.h
    rng = random.Random(61)
    # swept wings set back on the hull
    wing = [(150, 90), (270, 90), (236, 44), (196, 10), (170, 6), (160, 14)]
    for pts, face in ((wing, 4), (mirror(wing, H), 3)):
        p.bevel(p.mask(polygon=pts), "hull", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
    for top in (True, False):
        band = [(176, 8), (190, 8), (238, 70), (226, 76)]
        p.paint(p.mask(polygon=band if top else mirror(band, H)), "yellow")
        for (a, b) in (((200, 88), (180, 20)), ((236, 88), (206, 34))):
            p.engrave([a, b] if top else mirror([a, b], H))
        flap = [(158, 86), (190, 86), (180, 56), (162, 60)]
        f = flap + flap[:1]
        p.engrave(f if top else mirror(f, H))
    for y in (24, H - 1 - 24):
        p.bevel(p.mask(rect=(196, y - 7, 228, y + 7)), "gunmetal", width=2, face=4 if y < 120 else 3, shade_lower=False)
        p.tube(p.mask(rect=(226, y - 3, 266, y + 2)), "metal", "x", bands=(5, 4, 3, 2, 1, 1))
        p.tube(p.mask(rect=(264, y - 4, 270, y + 3)), "gunmetal", "x", bands=(4, 3, 2, 1))
        light(p, 176, y - 2, "glow_green" if y < 120 else "glow_red")
    # the long fuselage with the crew deck
    body = [(54, 72), (330, 72), (370, 88), (424, 118), (424, 121), (370, 152), (330, 168), (54, 168)]
    bm = p.mask(polygon=body)
    p.bevel(bm, "hull", width=6, face=3, edge_light=5)
    p.bevel(p.mask(polygon=[(80, 84), (320, 84), (340, 94), (340, 146), (320, 156), (80, 156)]), "hull", width=3, face=4)
    # yellow trim lines, faded grey patches, panel lines
    for y in (100, 138):
        p.paint(p.mask(rect=(60, y, 360, y + 2)) & bm, "yellow")
    for (x0, y0, x1, y1) in ((110, 108, 150, 132), (250, 86, 290, 98), (200, 142, 236, 154)):
        plate(p, (x0, y0, x1, y1), "metal", bm, face=4, width=2)
    for x in (100, 160, 220, 280):
        p.engrave([(x, 86), (x, 154)])
    rivet_row(p, 70, 320, 78, 8); rivet_row(p, 70, 320, 162, 8)
    lit_windows(p, 170, 110, 6, 10, w=4, h=3, mat="glow_yellow", tone=2)
    lit_windows(p, 170, 126, 6, 10, w=4, h=3, mat="glow_yellow", tone=2)
    stencil(p, 296, 112, "T-9")
    for i in range(3):
        p.slot(300, 124 + i * 6, 326, 125 + i * 6)
    # the nose and canopy
    p.bevel(p.mask(polygon=[(340, 98), (382, 106), (404, 119), (382, 133), (340, 141), (352, 119)]), "glass", width=2, face=3, shade_lower=False)
    p.set_tone(p.mask(rect=(358, 104, 378, 106)), 5)
    p.engrave([(366, 103), (366, 136)], highlight=False)
    p.paint(p.mask(polygon=[(404, 112), (424, 118), (424, 121), (404, 127)]), "yellow")
    # a dorsal spine with an antenna and a sensor dish, airlocks on both sides
    p.bevel(p.mask(rect=(96, 114, 290, 125)), "hull", width=2, face=5, shade_lower=False)
    rivet_row(p, 102, 286, 119, 8)
    p.dome(p.mask(ellipse=(300, 88, 318, 104)), "metal", shadow=True)
    p.dome(p.mask(ellipse=(304, 92, 312, 100)), "dark")
    for (y0, y1) in ((72, 84), (156, 168)):
        hazard(p, p.mask(rect=(124, y0, 152, y1)), step=4)
        p.bevel(p.mask(rect=(129, y0 + 3, 147, y1 - 3)), "gunmetal", width=1, face=3, shade_lower=False)
    # one big engine ring at the back, with intakes
    p.bevel(p.mask(ellipse=(30, 78, 96, 162)), "metal", width=5, face=4, shade_lower=False)
    p.bevel(p.mask(ellipse=(40, 88, 86, 152)), "gunmetal", width=3, face=3, shade_lower=False)
    for k in range(6):
        ang = k * np.pi / 3
        p.engrave([(63, 120), (int(63 + 22 * np.cos(ang)), int(120 + 30 * np.sin(ang)))], highlight=False)
    for a in range(16):
        ang = a * np.pi / 8
        p.rivet(int(63 + 30 * np.cos(ang)), int(120 + 38 * np.sin(ang)))
    p.tube(p.mask(rect=(22, 88, 48, 152)), "metal", "x", bands=(5, 5, 4, 4, 3, 3, 3, 2, 2, 1))
    for x in range(28, 46, 5):
        p.engrave([(x, 90), (x, 150)])
    p.tube(p.mask(rect=(20, 96, 28, 144)), "dark", "x", shadow=False)
    thruster(p, 22, 98, 142, "glow", 18)
    for y in (80, 152):
        p.tube(p.mask(rect=(96, y, 140, y + 8)), "dark", "x", shadow=False)
    wear(p, rng, rust=4, grime=0.02, mats=("hull", "metal"), scuffs=16)
    return p


# Rooms and doors for the ships in the game: {id: (col, row, w, h, system)} and ((c1, r1), (c2, r2)), in 48-px
# cells. Must match scripts/ship_data.gd. Doors only where the layout needs them (Zachary, 21 Nov).
INSIDES = {
    # Ivan's flagship, 9 x 6: engines at the back with oxygen and the brig beside them, shields and weapons in the
    # middle, the crew deck with the cannon room above it (Zachary: a room for the special weapon, like FTL)
    # and a hold below, the bridge in the nose.
    "ivan_flagship": (
        {"life": (1, 1, 2, 1, "life"), "engines": (1, 2, 2, 2, "engines"), "brig": (1, 4, 2, 1, ""),
         "shields": (3, 1, 2, 2, "shields"), "weapons": (3, 3, 2, 2, "weapons"),
         "cannon": (5, 1, 2, 1, "cannon"), "crew": (5, 2, 2, 2, ""), "hold_bottom": (5, 4, 2, 1, ""),
         "pilot": (7, 2, 1, 2, "pilot")},
        [((1, 1), (1, 2)), ((1, 3), (1, 4)), ((2, 2), (3, 2)), ((2, 3), (3, 3)), ((4, 2), (5, 2)),
         ((4, 3), (5, 3)), ((6, 1), (6, 2)), ((6, 3), (6, 4)), ((6, 2), (7, 2))],
    ),
}


SHIPS = {
    "starter": (starter, "Starter fighter (7x4)"),
    "ivan_flagship": (ivan_flagship, "Ivan's flagship (9x6)"),
    "ana_corsair": (ana_corsair, "Ana's corsair (7x5)"),
    "loyalist_gunship": (loyalist_gunship, "Loyalist gunship (5x4)"),
    "covered_fighter": (covered_fighter, "Covered fighter, Freya's quest (9x5)"),
}

if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[1] == "--install":
    # python3 -I tools/dev/ship_art/story2x.py --install <repo root> <ship id>...: art/ships/<id>/hull.png, interior.png
    from kit2x import interior
    root = Path(sys.argv[2])
    for sid in sys.argv[3:]:
        fn = SHIPS[sid][0]
        out = root / "art/ships" / sid
        out.mkdir(parents=True, exist_ok=True)
        fn().render().save(out / "hull.png")
        rooms, doors = INSIDES[sid]
        interior(fn(), rooms, doors).render().save(out / "interior.png")
        print("installed", sid)
elif __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/story2x")
    out.mkdir(parents=True, exist_ok=True)
    only = sys.argv[2:] or list(SHIPS)
    items = []
    for sid in only:
        fn, label = SHIPS[sid]
        p = fn()
        p.render().save(out / f"{sid}.png")
        items.append((label, p))
    sheet(items, out / "sheet.png", scale=2, cols=2)
    print("ok", len(items))
