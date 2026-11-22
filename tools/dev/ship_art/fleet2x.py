"""The culture ships at double resolution, 48 px per cell (Claude, 21 Nov 2026). Same shapes as cultures.py, with the
extra pixels spent on detail. Top-down, nose right.

Run from the repo root:  python3 -I tools/dev/ship_art/fleet2x.py <out dir>
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from scipy import ndimage
from pixkit import Pix
from kit2x import (S, mirror, grid, rivet_row, rivet_col, plate, hazard, windows, lit_windows, thruster, nozzle,
                   turret, light, stencil, wear, scorch, cable, sheet)


# ---------------------------------------------------------------- Terran Empire: 7 x 4 cells

def terran_patrol():
    p = Pix(336, 192)
    H = p.h
    rng = random.Random(3)
    # sponsons, top and bottom
    spon = S([(26, 24), (118, 24), (104, 6), (60, 6), (46, 2), (32, 2)])
    for pts, face in ((spon, 4), (mirror(spon, H), 3)):
        m = p.mask(polygon=pts)
        p.bevel(m, "white", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
    for y0, y1 in ((14, 22), (169, 177)):
        p.paint(p.mask(polygon=[(124, y0), (208, y0), (214, y1), (130, y1)]), "trim_blue")
        p.engrave([(124, y1 + 2), (214, y1 + 2)])
    for x in (80, 110, 150, 190):
        p.engrave([(x, 12), (x - 6, 46)]); p.engrave([(x, 179), (x - 6, 145)])
    rivet_row(p, 70, 220, 40, 8); rivet_row(p, 70, 220, 151, 8)
    for y in (10, 181):
        p.bevel(p.mask(rect=(176, y - 6, 210, y + 6)), "white", width=2, face=4 if y < 96 else 3, shade_lower=False)
        p.slot(182, y - 2, 198, y - 1)
    # the hull
    body = S([(10, 22), (138, 22), (150, 28), (166, 40), (166, 55), (150, 67), (138, 73), (10, 73)])
    bm = p.mask(polygon=body)
    p.bevel(bm, "white", width=5, face=3, edge_light=5)
    p.bevel(p.mask(polygon=[(60, 56), (216, 56), (224, 64), (224, 126), (216, 134), (60, 134)]), "white", width=3, face=4)
    # panel lines and rivets
    for x in (96, 140, 180):
        p.engrave([(x, 58), (x, 132)])
    p.engrave([(62, 76), (222, 76)]); p.engrave([(62, 114), (222, 114)])
    rivet_row(p, 28, 214, 50, 8); rivet_row(p, 28, 214, 141, 8)
    # the blue band with a white pinstripe, an orange chevron
    p.paint(p.mask(rect=(22, 88, 300, 101)), "trim_blue")
    p.paint(p.mask(rect=(22, 94, 300, 95)), "white")
    for dx in (0, 14):
        p.paint(p.mask(polygon=[(132 + dx, 62), (144 + dx, 62), (158 + dx, 76), (144 + dx, 90), (132 + dx, 90), (146 + dx, 76)]), "orange")
    stencil(p, 70, 64, "TP-07", tone=1)
    # vents and a hatch
    for i in range(3):
        p.slot(186, 62 + i * 5, 210, 63 + i * 5); p.slot(186, 118 + i * 5, 210, 119 + i * 5)
    p.engrave_rect(100, 118, 128, 130)
    p.bevel(p.mask(rect=(110, 122, 118, 125)), "metal", width=1, face=3, shade_lower=False)
    # the bridge
    bridge = [(228, 62), (272, 62), (292, 78), (292, 112), (272, 128), (228, 128)]
    p.bevel(p.mask(polygon=bridge), "white", width=3, face=4)
    p.engrave([(236, 66), (236, 124)])
    windows(p, 244, 80, 6, 7); windows(p, 244, 108, 6, 7)
    p.bevel(p.mask(polygon=[(276, 82), (292, 88), (300, 95), (292, 102), (276, 108)]), "glass", width=1, face=3, shade_lower=False)
    p.set_tone(p.mask(rect=(280, 86, 288, 87)), 5)
    p.dome(p.mask(ellipse=(244, 88, 262, 104)), "white", shadow=True)
    p.dome(p.mask(ellipse=(249, 92, 257, 100)), "trim_blue")
    p.engrave([(262, 96), (272, 92)], highlight=False)
    # nose sensor and lights
    p.bevel(p.mask(polygon=[(312, 86), (330, 94), (330, 97), (312, 105)]), "metal", width=1, face=4, shade_lower=False)
    light(p, 280, 48, "glow_red"); light(p, 280, 142, "glow_green")
    light(p, 40, 46, "glow_red"); light(p, 40, 145, "glow_green")
    # engines: an armoured block with three nozzles
    p.bevel(p.mask(rect=(24, 46, 52, 146)), "metal", width=3, face=3)
    for y in range(52, 140, 12):
        p.engrave([(28, y), (48, y)])
    for (y0, y1) in ((52, 74), (84, 108), (118, 140)):
        nozzle(p, 12, y0, 32, y1, "glow_blue", 12)
    wear(p, rng, grime=0.008, mats=("white",), scuffs=10)
    return p


# ---------------------------------------------------------------- Zaa'sh Junta: 6 x 4

def zaash_skiff():
    p = Pix(288, 192)
    H = p.h
    yy, xx = grid(p)
    # blade fins with bronze edges, ribbed, with bells
    fin = S([(20, 24), (86, 24), (64, 10), (40, 2), (22, 0), (14, 6)])
    for pts, face in ((fin, 4), (mirror(fin, H), 3)):
        p.bevel(p.mask(polygon=pts), "bone", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
    edge = S([(86, 24), (64, 10), (40, 2), (37, 5), (61, 14), (81, 24)])
    p.bevel(p.mask(polygon=edge), "bronze", width=1, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=mirror(edge, H)), "bronze", width=1, face=3, shade_lower=False)
    for (a, b) in (((100, 46), (64, 8)), ((70, 46), (44, 6)), ((130, 46), (100, 22))):
        p.engrave([a, b]); p.engrave(mirror([a, b], H))
    for (x, y) in ((44, 14), (74, 26), (104, 38)):
        for yb in (y, H - 1 - y - 6):
            p.paint(p.mask(rect=(x + 2, yb - 4, x + 2, yb)), "bronze")
            p.dome(p.mask(ellipse=(x - 2, yb, x + 6, yb + 7)), "gold", shadow=True)
    # carapace
    shell = p.mask(ellipse=(12, 40, 256, 150))
    p.bevel(shell, "bone", width=6, face=3, edge_light=5)
    p.bevel(p.mask(ellipse=(40, 56, 224, 134)), "bone", width=3, face=4)
    # scale texture between the ribs
    inner = p.mask(ellipse=(16, 44, 252, 146))
    for x in range(30, 240, 10):
        for y in range(52, 142, 8):
            o = 5 if (y // 8) % 2 else 0
            if inner[y, x + o] and p.tone[y, x + o] >= 3:
                p.engrave([(x + o, y), (x + o + 4, y + 2)], highlight=False)
    # bronze ribs, curved
    for x in (60, 96, 132, 168, 204):
        bend = x - 18 * ((yy - 95.5) / 52.0) ** 2
        rib = (np.abs(xx - bend) <= 2.6) & inner
        p.bevel(rib, "bronze", width=1, face=4, shade_lower=False)
        for y in range(56, 140, 10):
            bx = int(x - 18 * ((y - 95.5) / 52.0) ** 2)
            if rib[y, bx]:
                p.rivet(bx, y)
    # the crescent prow
    prow = S([(116, 24), (130, 26), (143, 40), (143, 55), (130, 69), (116, 71), (127, 58), (131, 47), (127, 37)])
    p.bevel(p.mask(rect=(232, 82, 262, 108)), "bronze", width=2, face=3)
    p.bevel(p.mask(polygon=prow), "bronze", width=3, face=4)
    for k in range(4):
        p.engrave([(240 + k * 5, 56 + k * 3), (240 + k * 5, 136 - k * 3)], highlight=False)
    p.glow(p.mask(ellipse=(270, 92, 278, 100)), "glow_yellow", 3)
    # the shrine: a bronze dome with a glowing eye, a mast with a red banner
    banner = [(116, 88), (72, 78), (80, 92), (72, 106), (116, 100)]
    p.bevel(p.mask(polygon=banner), "banner", width=2, face=3, shade_lower=False)
    for x in (84, 96, 108):
        p.paint(p.mask(rect=(x, 84 + (116 - x) // 8, x + 1, 102 - (116 - x) // 8)), "gold")
    p.bevel(p.mask(ellipse=(108, 76, 144, 112)), "bronze", width=3, face=4, shade_lower=False)
    p.dome(p.mask(ellipse=(114, 82, 138, 106)), "gold", shadow=False)
    p.glow(p.mask(ellipse=(121, 90, 131, 98)), "glow_yellow", 3)
    p.glow(p.mask(rect=(125, 93, 127, 95)), "glow_yellow", 5)
    for a in range(8):
        ang = a * np.pi / 4
        x, y = int(126 + 22 * np.cos(ang)), int(94 + 22 * np.sin(ang))
        p.rivet(x, y)
    # lamps and vents
    for (x, y) in ((108, 66), (108, 122), (180, 70), (180, 118)):
        p.bevel(p.mask(ellipse=(x - 4, y - 4, x + 4, y + 4)), "bronze", width=1, face=4, shade_lower=False)
        p.glow(p.mask(ellipse=(x - 2, y - 2, x + 2, y + 2)), "glow_yellow", 3)
    for i in range(3):
        p.slot(206, 80 + i * 5, 226, 81 + i * 5); p.slot(206, 102 + i * 5, 226, 103 + i * 5)
    # engines: two bronze cowls
    for y in (68, 110):
        p.bevel(p.mask(ellipse=(14, y - 4, 46, y + 18)), "bronze", width=2, face=3)
        p.tube(p.mask(rect=(12, y + 1, 20, y + 13)), "dark", "x", shadow=False)
        thruster(p, 13, y + 1, y + 13, "glow", 12)
    wear(p, random.Random(5), grime=0.01, mats=("bone",), scuffs=8)
    return p


# ---------------------------------------------------------------- Vuultam: 7 x 4

def vuultam_garden():
    p = Pix(336, 192)
    H = p.h
    rng = random.Random(7)
    yy, xx = grid(p)
    # petal fins with veins
    for (x0, x1, tip) in ((60, 164, 8), (140, 236, 20)):
        cx = (x0 + x1) // 2
        top = [(x0, 52), (x1, 52), (cx + 20, tip), (cx - 12, tip - 4)]
        m = p.mask(polygon=top) | p.mask(ellipse=(cx - 32, tip - 8, cx + 36, tip + 24))
        mb = p.mask(polygon=mirror(top, H)) | p.mask(ellipse=(cx - 32, H - 1 - (tip + 24), cx + 36, H - 1 - (tip - 8)))
        for mm, face in ((m, 4), (mb, 3)):
            p.bevel(mm, "petal", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
            d = ndimage.distance_transform_edt(mm)
            p.shade(mm & (d > 3) & (d < 7), 1)
        for dx in (-16, 0, 16):
            p.engrave([(cx, 50), (cx + 4 + dx, tip + 6)], highlight=False)
            p.engrave(mirror([(cx, 50), (cx + 4 + dx, tip + 6)], H), highlight=False)
    # seed-pod hull
    body = p.mask(rect=(28, 44, 280, 147)) | p.mask(ellipse=(224, 44, 332, 147)) | p.mask(ellipse=(12, 44, 76, 147))
    p.bevel(body, "seafoam", width=6, face=3, edge_light=5)
    p.bevel(p.mask(rect=(60, 56, 224, 135)) | p.mask(ellipse=(192, 56, 256, 135)), "seafoam", width=3, face=4)
    # vines along the hull
    for (y, ph) in ((52, 0), (139, 2)):
        pts = [(x, int(y + 3 * np.sin(x / 9 + ph))) for x in range(34, 300, 3)]
        m = p._line(pts, width=2) & body
        p.mat[m] = "crate_green"; p.tone[m] = 3
        for x in range(40, 296, 14):
            ly = int(y + 3 * np.sin(x / 9 + ph))
            leaf = p.mask(ellipse=(x, ly - 4, x + 6, ly)) if (x // 14) % 2 else p.mask(ellipse=(x, ly + 1, x + 6, ly + 5))
            p.bevel(leaf & body, "crate_green", width=1, face=4, shade_lower=False)
    # three garden domes with trees and flowers inside
    for (x0, y0, x1, y1) in ((68, 58, 128, 92), (68, 98, 128, 132), (144, 62, 204, 128)):
        p.bevel(p.mask(ellipse=(x0 - 4, y0 - 4, x1 + 4, y1 + 4)), "metal", width=2, face=3, shade_lower=False)
        for a in range(10):
            ang = a * np.pi / 5
            p.rivet(int((x0 + x1) / 2 + ((x1 - x0) / 2 + 2) * np.cos(ang)), int((y0 + y1) / 2 + ((y1 - y0) / 2 + 2) * np.sin(ang)))
        p.dome(p.mask(ellipse=(x0, y0, x1, y1)), "leafglass")
        inside = p.mask(ellipse=(x0 + 3, y0 + 3, x1 - 3, y1 - 3))
        for _ in range(4):
            tx, ty = rng.randint(x0 + 10, x1 - 12), rng.randint(y0 + 8, y1 - 10)
            crown = p.mask(ellipse=(tx - 5, ty - 5, tx + 5, ty + 4)) & inside
            p.bevel(crown, "crate_green", width=1, face=4, shade_lower=False)
            p.paint(p.mask(rect=(tx, ty + 3, tx + 1, ty + 6)) & inside, "strap")
        for _ in range(14):
            fx, fy = rng.randint(x0 + 6, x1 - 6), rng.randint(y0 + 6, y1 - 6)
            m = p.mask(rect=(fx, fy, fx + 1, fy + 1)) & inside
            p.paint(m, rng.choice(["petal", "gold", "petal", "crate_red"])); p.set_tone(m, 4)
        hl = p.mask(ellipse=(x0 + 6, y0 + 4, x0 + 18, y0 + 9)) & inside
        p.set_tone(hl, 5)
    # water tanks, a vent comb
    for x in (214, 226):
        p.tube(p.mask(rect=(x, 66, x + 8, 124)), "glass", "y", bands=(2, 4, 5, 4, 3, 2))
        p.engrave([(x, 80), (x + 8, 80)]); p.engrave([(x, 110), (x + 8, 110)])
    # the glass nose
    nose = [(248, 78), (296, 86), (314, 95), (296, 105), (248, 113), (262, 95)]
    p.bevel(p.mask(polygon=nose), "glass", width=2, face=3, shade_lower=False)
    p.set_tone(p.mask(rect=(264, 86, 282, 88)), 5)
    p.engrave([(270, 82), (270, 109)], highlight=False)
    light(p, 300, 70, "glow_green"); light(p, 300, 120, "glow_green")
    # root engines at the back
    for y in (62, 110):
        p.dome(p.mask(ellipse=(14, y, 38, y + 22)), "seafoam", shadow=True)
        for k in range(3):
            p.engrave([(18 + k * 6, y + 2), (16 + k * 6, y + 20)], highlight=False)
        thruster(p, 16, y + 4, y + 18, "glow_green", 12)
    wear(p, rng, grime=0.01, mats=("seafoam",), scuffs=6)
    return p


# ---------------------------------------------------------------- Moogli: 6 x 4

def moogli_trader():
    p = Pix(288, 192)
    H = p.h
    rng = random.Random(5)
    yy, xx = grid(p)
    # crates strapped above and below, each with a stencil and slats
    marks = ["0", "7", "3", "5", "8", "2", "9", "4"]
    for i, (x, w) in enumerate(((44, 44), (92, 36), (132, 44), (180, 32))):
        for top in (True, False):
            hgt = 34
            y0 = 6 + rng.randint(0, 12) if top else H - 1 - 42 + rng.randint(0, 6)
            mat = rng.choice(["crate_red", "crate_blue", "crate_green", "crate_violet", "strap"])
            p.bevel(p.mask(rect=(x, y0, x + w, y0 + hgt)), mat, width=3, face=4 if top else 3, shade_lower=False)
            for k in range(1, 4):
                p.engrave([(x + 3, y0 + k * hgt // 4), (x + w - 3, y0 + k * hgt // 4)])
            p.paint(p.mask(rect=(x + w // 2 - 2, y0 + 1, x + w // 2 + 1, y0 + hgt - 1)), "strap")
            stencil(p, x + 4, y0 + 4, marks[(i * 2 + top) % len(marks)], tone=1)
            for (rx, ry) in ((x + 3, y0 + 3), (x + w - 3, y0 + 3), (x + 3, y0 + hgt - 3), (x + w - 3, y0 + hgt - 3)):
                p.rivet(rx, ry)
    # the round hull with a green stripe
    hull = p.mask(ellipse=(16, 28, 264, 162)) | p.mask(rect=(26, 60, 40, 130))
    p.bevel(hull, "gold", width=6, face=3, edge_light=5)
    p.bevel(p.mask(ellipse=(40, 48, 224, 142)), "gold", width=3, face=4)
    p.paint(hull & (xx >= 116) & (xx <= 127), "crate_green")
    p.paint(hull & (xx >= 120) & (xx <= 121), "white")
    # cargo net over the top half
    net = p.mask(ellipse=(52, 54, 108, 136))
    for k in range(-60, 60, 8):
        p.dark_line([(52 + k, 54), (108 + k, 136)]); p.dark_line([(108 - k, 54), (52 - k, 136)])
    p.lines &= ~(~net)
    # straps with buckles
    for y in (42, 148):
        p.bevel(p.mask(rect=(36, y - 3, 224, y + 3)), "strap", width=1, face=3, shade_lower=False)
        for x in (70, 150, 200):
            p.bevel(p.mask(rect=(x, y - 4, x + 6, y + 4)), "gold", width=1, face=4, shade_lower=False)
    # hanging lanterns and a bunting line
    for k, x in enumerate(range(140, 214, 10)):
        y = 64 + int(4 * np.sin(k))
        m = p.mask(rect=(x, y, x + 3, y + 5))
        p.paint(m, ["crate_red", "crate_blue", "gold", "crate_green"][k % 4]); p.set_tone(m, 4)
    p.engrave([(138, 62), (216, 62)], highlight=False)
    for (x, y) in ((150, 120), (180, 124)):
        p.bevel(p.mask(ellipse=(x, y, x + 8, y + 11)), "bronze", width=1, face=4, shade_lower=False)
        p.glow(p.mask(rect=(x + 3, y + 4, x + 5, y + 7)), "glow_yellow", 4)
    # two big frog-eye windows
    for cy in (72, 118):
        p.bevel(p.mask(ellipse=(216, cy - 28, 276, cy + 28)), "strap", width=3, face=3, shade_lower=False)
        for a in range(12):
            ang = a * np.pi / 6
            p.rivet(int(246 + 26 * np.cos(ang)), int(cy + 26 * np.sin(ang)))
        p.dome(p.mask(ellipse=(222, cy - 22, 270, cy + 22)), "glass")
        p.paint(p.mask(ellipse=(240, cy - 10, 262, cy + 10)), "dark")
        p.set_tone(p.mask(ellipse=(242, cy - 8, 260, cy + 8)), 1)
        p.paint(p.mask(rect=(236, cy - 14, 240, cy - 11)), "white"); p.set_tone(p.mask(rect=(236, cy - 14, 240, cy - 11)), 5)
        p.paint(p.mask(rect=(256, cy + 4, 257, cy + 5)), "white"); p.set_tone(p.mask(rect=(256, cy + 4, 257, cy + 5)), 5)
    # vents, an awning hatch
    for i in range(3):
        p.slot(168, 78 + i * 6, 188, 79 + i * 6)
    p.bevel(p.mask(rect=(76, 120, 104, 132)), "crate_red", width=1, face=4, shade_lower=False)
    for x in range(78, 104, 6):
        p.paint(p.mask(rect=(x, 121, x + 2, 131)), "white")
    # a stubby engine
    p.tube(p.mask(rect=(18, 72, 38, 118)), "strap", "x")
    for y in range(76, 116, 8):
        p.engrave([(20, y), (36, y)])
    nozzle(p, 12, 80, 26, 110, "glow", 12, mat="bronze")
    wear(p, rng, grime=0.01, mats=("gold",), scuffs=8)
    return p


# ---------------------------------------------------------------- Ervani: 6 x 4

def ervani_courier():
    p = Pix(288, 192)
    H = p.h
    yy, xx = grid(p)
    rng = random.Random(11)
    # ear fins with cream tips and dark inner ear
    ear = S([(18, 24), (58, 24), (30, 2), (20, 0)])
    for pts, face in ((ear, 4), (mirror(ear, H), 3)):
        p.bevel(p.mask(polygon=pts), "russet", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
    inner = [(48, 46), (100, 46), (60, 12), (48, 8)]
    for pts in (inner, mirror(inner, H)):
        p.bevel(p.mask(polygon=pts), "dark", width=1, face=3, shade_lower=False)
    tip = S([(30, 2), (20, 0), (22, 9), (33, 11)])
    p.paint(p.mask(polygon=tip), "fur"); p.paint(p.mask(polygon=mirror(tip, H)), "fur")
    # the brush tail with a cream tip and a hidden engine
    tail = p.mask(ellipse=(4, 64, 76, 128))
    p.bevel(tail, "russet", width=3, face=3)
    p.paint(p.mask(ellipse=(4, 72, 30, 120)), "fur")
    for k in range(9):
        y = 70 + k * 6
        p.engrave([(36, y), (68, y + 3)], highlight=False)
    # body: russet over cream belly
    body = S([(22, 24), (110, 24), (132, 32), (143, 46), (143, 49), (132, 63), (110, 71), (22, 71)])
    bm = p.mask(polygon=body)
    p.bevel(bm, "russet", width=5, face=4)
    belly = bm & (yy >= 100) & ~(p.mask(polygon=S([(22, 50), (60, 50), (40, 71), (22, 71)])))
    p.paint(belly, "fur")
    edge = belly & ~ndimage.binary_erosion(belly, iterations=1) & (yy < 106)
    p.paint(edge, "russet")
    # fur strokes: short streaks swept back
    for _ in range(140):
        x, y = rng.randint(50, 250), rng.randint(52, 140)
        if bm[y, x] and p.tone[y, x] >= 3:
            p.engrave([(x, y), (x - 5, y + (1 if y > 96 else -1))], highlight=False)
    # tiger stripes
    for x in (92, 124, 156):
        for top in (True, False):
            pts = [(x, 50), (x + 12, 50), (x + 24, 80), (x + 12, 80)]
            p.shade(p.mask(polygon=pts if top else mirror(pts, H)), -2)
    # the snout: cockpit, nose, whiskers
    p.bevel(p.mask(polygon=S([(102, 30), (126, 38), (126, 57), (102, 65), (110, 47)])), "fur", width=3, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=S([(111, 40), (127, 43), (127, 52), (111, 55), (115, 47)])), "glass", width=2, face=3, shade_lower=False)
    p.set_tone(p.mask(rect=(234, 86, 244, 88)), 5)
    p.engrave([(240, 82), (240, 108)], highlight=False)
    p.bevel(p.mask(polygon=[(272, 84), (286, 92), (286, 99), (272, 107)]), "dark", width=1, face=3, shade_lower=False)
    for dy in (-6, 0, 6):
        p.engrave([(262, 95 + dy), (284, 95 + dy * 3)], highlight=False)
    # an amber eye-light on each side, a paw emblem
    for y in (74, 116):
        p.glow(p.mask(ellipse=(214, y - 3, 222, y + 3)), "glow_yellow", 3)
    for (x, y, r) in ((78, 76, 5), (70, 70, 2), (76, 68, 2), (84, 68, 2), (88, 72, 2)):
        p.paint(p.mask(ellipse=(x - r, y - r, x + r, y + r)), "fur")
    # vents, panel lines, a hatch
    p.engrave([(84, 50), (84, 140)]); p.engrave([(188, 52), (188, 138)])
    for i in range(3):
        p.slot(166, 64 + i * 5, 182, 65 + i * 5)
    p.engrave_rect(120, 110, 150, 124)
    # side intakes
    for y in (56, 128):
        p.tube(p.mask(rect=(44, y, 60, y + 12)), "dark", "x", shadow=False)
        thruster(p, 44, y + 2, y + 10, "glow", 8)
    return p


# ---------------------------------------------------------------- Scyldar: 7 x 4

def scyldar_lantern():
    p = Pix(336, 192)
    H = p.h
    yy, xx = grid(p)
    rng = random.Random(13)
    # wide curved manta wings with coral rims, ribs and lantern pods
    wing = [(60, 70), (262, 70), (244, 44), (206, 18), (160, 5), (116, 4), (82, 14), (62, 36)]
    body = p.mask(ellipse=(34, 44, 296, 147)) | p.mask(ellipse=(214, 40, 330, 151))
    for pts, face in ((wing, 4), (mirror(wing, H), 3)):
        m = p.mask(polygon=pts) & ~body
        p.bevel(m, "teal", width=3, face=face, edge_light=5 if face == 4 else 4, shade_lower=False)
        d = ndimage.distance_transform_edt(p.mask(polygon=pts))
        p.paint(m & (d <= 5), "coral")
        p.shade(m & (d <= 1), 1 if face == 4 else 0)
        for x in (96, 132, 168, 204, 236):
            a, b = (x, 66), (x - 22, 10 + abs(x - 150) // 5)
            p.engrave([a, b] if face == 4 else mirror([a, b], H), highlight=False)
        for _ in range(16):
            x, y = rng.randint(80, 230), rng.randint(18, 58)
            if face == 3:
                y = H - 1 - y
            sp = p.mask(ellipse=(x, y, x + 3, y + 2)) & m & (p.mat == "teal")
            p.set_tone(sp, 5)
    for x in (110, 150, 190):
        for y in (20, H - 32):
            p.bevel(p.mask(ellipse=(x - 1, y - 1, x + 11, y + 11)), "bronze", width=1, face=4, shade_lower=False)
            p.glow(p.mask(ellipse=(x + 2, y + 2, x + 8, y + 8)), "glow_yellow", 3)
            p.glow(p.mask(rect=(x + 4, y + 4, x + 5, y + 5)), "glow_yellow", 5)
    # the long tail, segmented, with a coral fluke
    p.tube(p.mask(rect=(12, 88, 60, 103)), "teal", "x")
    for x in range(18, 58, 7):
        p.engrave([(x, 89), (x, 102)])
    p.bevel(p.mask(polygon=[(4, 72), (20, 95), (4, 119), (12, 95)]), "coral", width=1, face=3, shade_lower=False)
    # the body
    p.bevel(body, "teal", width=6, face=3, edge_light=5)
    p.bevel(p.mask(ellipse=(64, 58, 280, 133)), "teal", width=3, face=4)
    for x in (110, 130, 150):
        for pts in ([(x, 62), (x + 4, 62), (x + 12, 78), (x + 8, 78)], mirror([(x, 62), (x + 4, 62), (x + 12, 78), (x + 8, 78)], H)):
            p.bevel(p.mask(polygon=pts), "coral", width=1, face=3, shade_lower=False)
    for x in range(78, 222, 12):
        p.dome(p.mask(ellipse=(x, 91, x + 8, 100)), "teal", shadow=True)
    p.engrave([(70, 84), (220, 82)]); p.engrave([(70, 107), (220, 109)])
    for cy in (72, 118):
        p.bevel(p.mask(ellipse=(274, cy - 14, 306, cy + 14)), "coral", width=2, face=4, shade_lower=False)
        p.dome(p.mask(ellipse=(278, cy - 11, 302, cy + 11)), "dark")
        p.paint(p.mask(rect=(284, cy - 7, 288, cy - 5)), "white"); p.set_tone(p.mask(rect=(284, cy - 7, 288, cy - 5)), 5)
    p.bevel(p.mask(ellipse=(228, 78, 264, 113)), "bronze", width=2, face=4, shade_lower=False)
    p.glow(p.mask(ellipse=(232, 82, 260, 109)), "glow_yellow", 2)
    p.glow(p.mask(ellipse=(238, 88, 254, 103)), "glow_yellow", 4)
    p.glow(p.mask(ellipse=(242, 92, 250, 99)), "glow_yellow", 5)
    for a in range(8):
        ang = a * np.pi / 4
        p.rivet(int(246 + 17 * np.cos(ang)), int(95 + 17 * np.sin(ang)))
    wear(p, rng, grime=0.01, mats=("teal",), scuffs=6)
    return p


# ---------------------------------------------------------------- Arachnay: 6 x 4

def arachnay_weaver():
    p = Pix(288, 192)
    H = p.h
    yy, xx = grid(p)
    # the web between the legs: radial and spiral threads
    web = np.zeros((H, p.w), bool)
    for k in range(6):
        y = 12 + k * 7
        web |= p._line([(52, y + 22), (120, y), (200, y + 16)])
    for x in (80, 120, 160):
        web |= p._line([(x, 52), (x + 4, 10)])
    for m, t in ((web, 4), (web[::-1], 3)):
        p.tone[m] = t; p.mat[m] = "silver"
    # eight jointed legs holding glowing pods
    for (x_root, x_tip, y_tip) in ((80, 40, 14), (116, 94, 11), (152, 162, 11), (184, 224, 16)):
        for top in (True, False):
            yr, yt = (52, y_tip) if top else (H - 1 - 52, H - 1 - y_tip)
            mid = ((x_root + x_tip) // 2, (yr + yt) // 2 + (-8 if top else 8))
            m = p._line([(x_root, yr), mid], width=6) | p._line([mid, (x_tip, yt)], width=4)
            p.bevel(m, "silver", width=1, face=4 if top else 3, shade_lower=False)
            p.dome(p.mask(ellipse=(mid[0] - 4, mid[1] - 4, mid[0] + 4, mid[1] + 4)), "violet", shadow=False)
            for f in (0.3, 0.7):
                hx, hy = int(mid[0] + (x_tip - mid[0]) * f), int(mid[1] + (yt - mid[1]) * f)
                p.engrave([(hx - 2, hy - 2), (hx + 2, hy + 2)], highlight=False)
            p.bevel(p.mask(ellipse=(x_tip - 10, yt - 8, x_tip + 10, yt + 8)), "violet", width=2, face=4 if top else 3, shade_lower=False)
            p.glow(p.mask(ellipse=(x_tip - 4, yt - 3, x_tip + 4, yt + 3)), "glow_teal", 3)
    # abdomen, thorax, head
    p.bevel(p.mask(ellipse=(16, 40, 128, 150)), "violet", width=5, face=3, edge_light=5)
    for k in range(5):
        x = 30 + k * 18
        p.engrave([(x, 48 + abs(2 - k) * 3), (x + 4, 142 - abs(2 - k) * 3)])
    glass = [(40, 66), (84, 66), (66, 94), (84, 124), (40, 124), (58, 94)]
    p.bevel(p.mask(polygon=glass), "red", width=2, face=4, shade_lower=False)
    p.engrave([(46, 70), (78, 70)], highlight=False)
    for (x, y) in ((30, 60), (30, 130), (96, 56), (96, 134), (104, 95)):
        p.dome(p.mask(ellipse=(x - 4, y - 4, x + 4, y + 4)), "silver", shadow=True)
    p.bevel(p.mask(ellipse=(104, 52, 236, 138)), "violet", width=5, face=4)
    p.bevel(p.mask(ellipse=(130, 66, 210, 124)), "violet", width=2, face=4)
    for i in range(3):
        p.slot(150, 80 + i * 5, 180, 81 + i * 5)
    p.bevel(p.mask(ellipse=(216, 60, 286, 130)), "violet", width=4, face=4)
    # mandibles
    for top in (True, False):
        pts = [(270, 78), (286, 82), (284, 90), (276, 88)]
        p.bevel(p.mask(polygon=pts if top else mirror(pts, H)), "silver", width=1, face=4, shade_lower=False)
    # an eye cluster
    for (x, y, r, c) in ((256, 80, 4, "glow_red"), (256, 106, 4, "glow_red"), (268, 86, 3, "glow_teal"),
                         (268, 100, 3, "glow_teal"), (244, 92, 3, "glow_red"), (276, 93, 2, "glow_red"),
                         (246, 72, 2, "glow_teal"), (246, 115, 2, "glow_teal")):
        p.paint(p.mask(ellipse=(x - r - 1, y - r - 1, x + r + 1, y + r + 1)), "dark")
        p.glow(p.mask(ellipse=(x - r, y - r, x + r, y + r)), c, 3)
        p.glow(p.mask(rect=(x - 1, y - 1, x - 1, y - 1)), c, 5)
    # bristles
    rng = random.Random(17)
    for _ in range(60):
        x, y = rng.randint(14, 230), rng.randint(46, 146)
        if p.mat[y, x] == "violet" and p.tone[y, x] >= 3:
            p.engrave([(x, y), (x + 1, y + (2 if y > 95 else -2))], highlight=False)
    # spinnerets at the back
    for y in (80, 104):
        p.tube(p.mask(rect=(10, y, 22, y + 10)), "dark", "x", shadow=False)
        thruster(p, 11, y, y + 10, "glow_teal", 10)
    return p


# ---------------------------------------------------------------- Collective: 8 x 5

def collective_freighter():
    """Bolted-together modules that don't quite match, one from each Collective people, on a green-grey spine."""
    p = Pix(384, 240)
    H = p.h
    rng = random.Random(21)
    # the spine: a long girder truss
    p.bevel(p.mask(rect=(34, 106, 332, 134)), "olive", width=3, face=3)
    p.slot(40, 112, 326, 113)
    for x in range(40, 326, 14):
        p.engrave([(x, 116), (x + 7, 130)]); p.engrave([(x + 7, 116), (x, 130)])

    def strut(x, top, w):
        y0, y1 = (96, 106) if top else (134, 144)
        for sx in (x + 8, x + w - 14):
            p.bevel(p.mask(rect=(sx, y0, sx + 5, y1)), "olive", width=1, face=4 if top else 3, shade_lower=False)

    for top in (True, False):
        sgn = -1 if top else 1
        face = 4 if top else 3
        base = 96 if top else 144
        def box(x0, x1, h, mat):
            y0, y1 = (base - h, base) if top else (base, base + h)
            plate(p, (x0, y0, x1, y1), mat, face=face, seams=1)
            return y0, y1
        # 1. olive crew module with lit windows and a stencil
        strut(56, top, 48)
        y0, y1 = box(56, 104, 66, "olive")
        lit_windows(p, 62, (y0 + 14) if top else (y1 - 18), 4, 10, mat="glow_green")
        stencil(p, 62, (y0 + 26) if top else (y1 - 32), "C-12" if top else "C-40")
        # 2. Vuultam: a seafoam tank under a garden dome
        strut(114, top, 46)
        y0, y1 = box(114, 160, 54, "seafoam")
        cy = (y0 + 24) if top else (y1 - 24)
        p.bevel(p.mask(ellipse=(118, cy - 20, 156, cy + 18)), "metal", width=2, face=face, shade_lower=False)
        p.dome(p.mask(ellipse=(122, cy - 16, 152, cy + 14)), "leafglass")
        for _ in range(6):
            tx, ty = rng.randint(128, 146), rng.randint(cy - 10, cy + 8)
            p.bevel(p.mask(ellipse=(tx - 3, ty - 3, tx + 3, ty + 2)), "crate_green", width=1, face=4, shade_lower=False)
        # 3. Moogli: a stack of strapped crates
        strut(170, top, 44)
        hh = 0
        for k, (w, h, mat) in enumerate(((44, 28, "crate_red"), (36, 24, "crate_blue"), (28, 18, "gold"))):
            x0 = 170 + (44 - w) // 2
            ya, yb = (base - hh - h, base - hh) if top else (base + hh, base + hh + h)
            p.bevel(p.mask(rect=(x0, ya, x0 + w, yb)), mat, width=2, face=face, shade_lower=False)
            p.engrave([(x0 + 3, (ya + yb) // 2), (x0 + w - 3, (ya + yb) // 2)])
            p.paint(p.mask(rect=(x0 + w // 2 - 1, ya + 1, x0 + w // 2 + 1, yb - 1)), "strap")
            hh += h
        # 4. Ervani: a russet pod with a cream band and stripes
        strut(224, top, 44)
        ya, yb = (base - 60, base) if top else (base, base + 60)
        m = p.mask(ellipse=(224, ya - 14, 268, yb + 14)) & p.mask(rect=(224, ya, 268, yb))
        p.bevel(m, "russet", width=3, face=face, shade_lower=False)
        p.paint(m & p.mask(rect=(224, (ya + yb) // 2 - 4, 268, (ya + yb) // 2 + 4)), "fur")
        for k in range(3):
            p.shade(m & p.mask(polygon=[(230 + k * 12, ya + 4), (236 + k * 12, ya + 4), (242 + k * 12, yb - 4), (236 + k * 12, yb - 4)]), -1)
        # 5. Scyldar: a round teal tank with a coral ring; Arachnay: a violet pod bolted to it
        strut(278, top, 40)
        cy = base - 26 if top else base + 26
        p.bevel(p.mask(ellipse=(276, cy - 24, 320, cy + 24)), "teal", width=3, face=face, shade_lower=False)
        p.paint(p.mask(ellipse=(276, cy - 24, 320, cy + 24)) & ~p.mask(ellipse=(281, cy - 19, 315, cy + 19)), "coral")
        p.dome(p.mask(ellipse=(288, cy - 12, 308, cy + 12)), "teal", shadow=False)
        vy = cy - 34 if top else cy + 22
        p.bevel(p.mask(ellipse=(290, vy, 312, vy + 12)), "violet", width=2, face=face, shade_lower=False)
        p.glow(p.mask(rect=(299, vy + 5, 302, vy + 7)), "glow_teal", 3)
    hazard(p, p.mask(rect=(176, 104, 214, 108)))
    # the tug at the front: olive cab with a glass slit
    p.bevel(p.mask(polygon=[(326, 92), (360, 96), (380, 110), (380, 130), (360, 144), (326, 148)]), "olive", width=4, face=4)
    p.bevel(p.mask(polygon=[(344, 108), (370, 112), (376, 120), (370, 128), (344, 132), (350, 120)]), "glass", width=1, face=3, shade_lower=False)
    p.set_tone(p.mask(rect=(352, 112, 362, 113)), 5)
    rivet_col(p, 332, 98, 142, 6)
    light(p, 340, 96, "glow_red"); light(p, 340, 142, "glow_green")
    # the engine block at the back with four mismatched nozzles
    p.bevel(p.mask(rect=(30, 84, 54, 156)), "olive", width=3, face=3)
    for (y0, y1, mat) in ((86, 102, "metal"), (104, 118, "bronze"), (122, 136, "metal"), (140, 154, "gunmetal")):
        nozzle(p, 14, y0, 32, y1, "glow", 12, mat=mat)
    wear(p, rng, rust=10, grime=0.015, mats=("olive", "metal"), scuffs=14)
    return p


# Rooms, doors and gun mounts for the game: rooms {id: (col, row, w, h, system)} and doors ((c1, r1), (c2, r2)) in
# 48-px cells (kit2x.interior cuts them; console_at() places the consoles); mounts in 24-px cell units, where the
# game attaches guns (front pair first). scripts/ship_data.gd CULTURE_SHIPS must match. Doors only where needed.
INSIDES = {
    "terran_patrol": (
        {"engines": (1, 1, 1, 2, "engines"), "shields": (2, 1, 1, 1, "shields"), "life": (2, 2, 1, 1, "life"),
         "crew": (3, 1, 2, 1, ""), "weapons": (3, 2, 2, 1, "weapons"), "pilot": (5, 1, 1, 2, "pilot")},
        [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (3, 1)), ((2, 2), (3, 2)), ((3, 1), (3, 2)), ((4, 1), (5, 1))],
        [(144, 22), (144, 73.5), (107, 5), (107, 90.5)],
    ),
    "zaash_skiff": (
        {"engines": (1, 1, 1, 2, "engines"), "shields": (2, 1, 1, 1, "shields"), "life": (2, 2, 1, 1, "life"),
         "weapons": (3, 1, 1, 1, "weapons"), "crew": (3, 2, 1, 1, ""), "pilot": (4, 1, 1, 2, "pilot")},
        [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (3, 1)), ((2, 2), (3, 2)), ((3, 1), (4, 1))],
        [(110, 25), (110, 70.5), (75, 18), (75, 77.5)],
    ),
    "vuultam_garden": (
        {"engines": (1, 1, 1, 2, "engines"), "life": (2, 1, 2, 2, "life"), "shields": (4, 1, 1, 1, "shields"),
         "weapons": (4, 2, 1, 1, "weapons"), "pilot": (5, 1, 1, 2, "pilot")},
        [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((3, 1), (4, 1)), ((3, 2), (4, 2)), ((4, 1), (5, 1))],
        [(135, 20), (135, 75.5), (110, 20), (110, 75.5)],
    ),
    "moogli_trader": (
        {"engines": (1, 1, 1, 2, "engines"), "life": (2, 1, 1, 1, "life"), "crew": (2, 2, 1, 1, ""),
         "hold": (3, 1, 1, 2, ""), "shields": (4, 1, 1, 1, "shields"), "weapons": (4, 2, 1, 1, "weapons"),
         "pilot": (5, 1, 1, 2, "pilot")},
        [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (3, 1)), ((2, 2), (3, 2)), ((3, 1), (4, 1)), ((3, 2), (4, 2)),
         ((4, 1), (5, 1))],
        [(113, 18), (113, 77.5)],
    ),
    "ervani_courier": (
        {"engines": (1, 1, 1, 2, "engines"), "crew": (2, 1, 1, 1, ""), "life": (2, 2, 1, 1, "life"),
         "shields": (3, 1, 1, 1, "shields"), "weapons": (3, 2, 1, 1, "weapons"), "pilot": (4, 1, 1, 2, "pilot")},
        [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (3, 1)), ((2, 2), (3, 2)), ((3, 1), (4, 1))],
        [(118, 23), (118, 72.5), (80, 21), (80, 74.5)],
    ),
    "scyldar_lantern": (
        {"engines": (1, 1, 1, 2, "engines"), "life": (2, 1, 1, 1, "life"), "crew": (2, 2, 1, 1, ""),
         "shields": (3, 1, 1, 1, "shields"), "weapons": (3, 2, 1, 1, "weapons"), "hold": (4, 1, 1, 2, ""),
         "pilot": (5, 1, 1, 2, "pilot")},
        [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (3, 1)), ((2, 2), (3, 2)), ((3, 1), (4, 1)), ((4, 1), (5, 1))],
        [(131, 18), (131, 77.5), (90, 15), (90, 80.5)],
    ),
    "arachnay_weaver": (
        {"engines": (1, 1, 1, 2, "engines"), "life": (2, 1, 1, 1, "life"), "crew": (2, 2, 1, 1, ""),
         "shields": (3, 1, 1, 1, "shields"), "weapons": (3, 2, 1, 1, "weapons"), "hold": (4, 1, 1, 2, ""),
         "pilot": (5, 1, 1, 2, "pilot")},
        [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (3, 1)), ((2, 2), (3, 2)), ((3, 1), (4, 1)), ((4, 1), (5, 1))],
        [(118, 27), (118, 68.5), (80, 23), (80, 72.5)],
    ),
    "collective_freighter": (
        {"engines": (1, 1, 1, 3, "engines"), "corridor": (2, 2, 5, 1, ""), "life": (2, 1, 1, 1, "life"),
         "shields": (3, 1, 1, 1, "shields"), "hold_top": (4, 1, 2, 1, ""), "weapons": (2, 3, 1, 1, "weapons"),
         "crew": (3, 3, 1, 1, ""), "hold_bottom": (4, 3, 2, 1, ""), "pilot": (7, 2, 1, 1, "pilot")},
        [((1, 2), (2, 2)), ((2, 2), (2, 1)), ((3, 2), (3, 1)), ((4, 2), (4, 1)), ((2, 2), (2, 3)), ((3, 2), (3, 3)),
         ((4, 2), (4, 3)), ((6, 2), (7, 2))],
        [(176, 45), (176, 74.5), (75, 10), (75, 109.5)],
    ),
}


SHIPS = {
    "terran_patrol": (terran_patrol, "Terran patrol (7x4)"),
    "zaash_skiff": (zaash_skiff, "Zaa'sh skiff (6x4)"),
    "vuultam_garden": (vuultam_garden, "Vuultam garden ship (7x4)"),
    "moogli_trader": (moogli_trader, "Moogli trader (6x4)"),
    "ervani_courier": (ervani_courier, "Ervani courier (6x4)"),
    "scyldar_lantern": (scyldar_lantern, "Scyldar lantern ship / Ooma (7x4)"),
    "arachnay_weaver": (arachnay_weaver, "Arachnay weaver (6x4)"),
    "collective_freighter": (collective_freighter, "Collective freighter (8x5)"),
}

if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[1] == "--install":
    # python3 -I tools/dev/ship_art/fleet2x.py --install <repo root> [ids]: art/ships/<id>/hull.png and interior.png,
    # and the Rabble repaint as hull_rabble.png and interior_rabble.png (same rooms)
    from kit2x import interior, save_interior
    from bases2x import piratize2x, PIRATE_SWAPS
    root = Path(sys.argv[2])
    for sid in sys.argv[3:] or list(INSIDES):
        fn = SHIPS[sid][0]
        rooms, doors, _mounts = INSIDES[sid]
        out = root / "art/ships" / sid
        out.mkdir(parents=True, exist_ok=True)
        clean = fn()
        rabble = piratize2x(clean, seed=len(sid), swaps=PIRATE_SWAPS.get(sid))
        clean.render().save(out / "hull.png")
        save_interior(interior(clean.copy(), rooms, doors), out / "interior.png")
        rabble.render().save(out / "hull_rabble.png")
        save_interior(interior(rabble.copy(), rooms, doors), out / "interior_rabble.png")
        print("installed", sid)
elif __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/fleet2x")
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
