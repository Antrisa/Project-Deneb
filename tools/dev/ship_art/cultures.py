"""Ships for every culture (Claude, 21 Nov 2026), in the approved fighter's style: crisp pixel art with shading,
depth and detail (tools/dev/ship_art/pixkit.py). Zachary: one look per people; Claude draws, he touches up.
Top-down, nose right, on 24-px cells.

  Terran Empire     terran_patrol      white hull, blue trim, chamfered plates, a bridge tower, blue thrusters
  Zaa'sh Junta      zaash_skiff        bone carapace with bronze ribs, blade fins, a crescent prow, a shrine mast
  Vuultam           vuultam_garden     a seed-pod hull in sea green, glass garden domes, petal fins
  Moogli            moogli_trader      round and yellow, crates strapped on, two big frog-eye windows
  Ervani            ervani_courier     russet over cream like a fox: a pointed snout, ear fins, a brush tail
  Scyldar           scyldar_lantern    a teal manta with coral edges and glowing lanterns, a long tail
  Arachnay          arachnay_weaver    a violet spider: round abdomen, eight legs holding pods, a web between
  The Rabble        rabble_cutter      a rusty wedge of welded plates, a red stripe, a spiked ram

piratize() turns any of them into a Rabble ship (Zachary: "other pirate ships are other cultures' ships,
haphazardly repainted with pirate stuff"): its trim repainted red, panels painted over, rough red strokes, rust,
welded plates, spikes on the nose and a skull.

Run from the repo root with -I:  python3 -I tools/dev/ship_art/cultures.py . [preview dir]
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from scipy import ndimage
from pixkit import Pix

GLOWS = ["glow", "glow_red", "glow_green", "glow_teal", "glow_yellow", "glow_blue"]


def mirror(pts, h):
    return [(x, h - 1 - y) for x, y in pts]


def yx(p):
    return np.mgrid[0:p.h, 0:p.w]


def windows(p, x0, y, n, step, mat="glass"):
    for i in range(n):
        m = p.mask(rect=(x0 + i * step, y, x0 + i * step + 2, y + 1))
        p.paint(m, mat)
        p.set_tone(m, 4)
        p.set_tone(p.mask(rect=(x0 + i * step, y, x0 + i * step, y)), 5)


def thruster(p, x0, y0, y1, mat="glow", depth=8):
    """A round exhaust glow behind the back edge at x0, between y0 and y1."""
    cy, r = (y0 + y1) / 2, (y1 - y0) / 2
    yy, xx = yx(p)
    g = p.mask(ellipse=(x0 - depth, cy - r, x0 + depth, cy + r)) & (xx < x0) & (p.tone < 0)
    p.glow(g, mat, 2)
    p.glow(p.mask(ellipse=(x0 - depth + 2, cy - r * 0.6, x0 + depth, cy + r * 0.6)) & g, mat, 3)
    p.glow(p.mask(ellipse=(x0 - depth + 4, cy - r * 0.3, x0 + depth, cy + r * 0.3)) & g, mat, 4)


def skull(p, x, y):
    rows = [".XXXXX.", "XXXXXXX", "X..X..X", "XXX.XXX", ".XXXXX.", ".X.X.X."]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            yy, xx = y + j, x + i
            if not (0 <= yy < p.h and 0 <= xx < p.w) or p.tone[yy, xx] < 0:
                continue
            if ch == "X":
                p.mat[yy, xx] = "bone"; p.tone[yy, xx] = 5 if j < 2 else 4
            else:
                p.mat[yy, xx] = "dark"; p.tone[yy, xx] = 1


# ---------------------------------------------------------------- Terran Empire

def terran_patrol():
    p = Pix(168, 96)
    H = p.h
    spon = [(26, 24), (118, 24), (104, 6), (60, 6), (46, 2), (32, 2)]
    p.bevel(p.mask(polygon=spon), "white", width=2, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=mirror(spon, H)), "white", width=2, face=3, edge_light=4, shade_lower=False)
    trim = [(62, 7), (104, 7), (108, 11), (66, 11)]
    p.paint(p.mask(polygon=trim), "trim_blue"); p.paint(p.mask(polygon=mirror(trim, H)), "trim_blue")
    for y in (5, H - 6):
        p.tube(p.mask(rect=(96, y - 2, 118, y + 2)), "metal", "x", bands=(5, 4, 3, 2, 1))
        p.tube(p.mask(rect=(118, y - 1, 121, y + 1)), "dark", "x", shadow=False)
    p.engrave([(46, 23), (40, 6)]); p.engrave(mirror([(46, 23), (40, 6)], H))
    body = [(10, 22), (138, 22), (150, 28), (166, 40), (166, 55), (150, 67), (138, 73), (10, 73)]
    p.bevel(p.mask(polygon=body), "white", width=3, face=3, edge_light=5)
    p.bevel(p.mask(polygon=[(30, 28), (108, 28), (112, 32), (112, 63), (108, 67), (30, 67)]), "white", width=2, face=4)
    p.paint(p.mask(rect=(12, 45, 150, 50)), "trim_blue")
    p.paint(p.mask(polygon=[(70, 31), (78, 31), (84, 38), (78, 45), (70, 45), (76, 38)]), "orange")
    p.bevel(p.mask(polygon=[(114, 31), (136, 31), (146, 39), (146, 56), (136, 64), (114, 64)]), "white", width=2, face=4)
    windows(p, 122, 40, 5, 4); windows(p, 122, 54, 5, 4)
    p.engrave([(48, 23), (48, 72)]); p.engrave([(90, 23), (90, 72)])
    for x in range(16, 108, 8):
        p.rivet(x, 25); p.rivet(x, 70)
    for i in range(2):
        p.slot(92, 32 + i * 4, 104, 33 + i * 4); p.slot(92, 58 + i * 4, 104, 59 + i * 4)
    p.bevel(p.mask(rect=(8, 25, 20, 70)), "metal", width=2, face=3)
    for y in (28, 42, 56):
        p.tube(p.mask(rect=(8, y, 13, y + 10)), "dark", "x", shadow=False)
        thruster(p, 8, y, y + 10, "glow_blue", 7)
    return p


# ---------------------------------------------------------------- Zaa'sh Junta

def zaash_skiff():
    p = Pix(144, 96)
    H = p.h
    fin = [(20, 24), (86, 24), (64, 10), (40, 2), (22, 0), (14, 6)]
    p.bevel(p.mask(polygon=fin), "bone", width=2, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=mirror(fin, H)), "bone", width=2, face=3, edge_light=4, shade_lower=False)
    edge = [(86, 24), (64, 10), (40, 2), (36, 5), (60, 14), (80, 24)]
    p.paint(p.mask(polygon=edge), "bronze"); p.paint(p.mask(polygon=mirror(edge, H)), "bronze")
    p.engrave([(50, 23), (32, 4)]); p.engrave(mirror([(50, 23), (32, 4)], H))
    p.bevel(p.mask(ellipse=(6, 20, 128, 75)), "bone", width=4, face=3, edge_light=5)
    p.bevel(p.mask(ellipse=(20, 28, 112, 67)), "bone", width=2, face=4)
    yy, xx = yx(p)
    inside = p.mask(ellipse=(8, 22, 126, 73))
    for x in (30, 48, 66, 84, 102):
        bend = x - 9 * ((yy - 47.5) / 26.0) ** 2
        p.paint((np.abs(xx - bend) <= 1.2) & inside, "bronze")
    p.bevel(p.mask(polygon=[(116, 24), (130, 26), (143, 40), (143, 55), (130, 69), (116, 71), (127, 58), (131, 47), (127, 37)]), "bronze", width=2, face=4)
    p.bevel(p.mask(polygon=[(58, 44), (36, 39), (40, 46), (36, 53), (58, 50)]), "banner", width=1, face=3, shade_lower=False)
    p.dome(p.mask(ellipse=(57, 40, 69, 52)), "bronze", shadow=True)
    for (x, y) in ((54, 35), (54, 58)):
        p.glow(p.mask(ellipse=(x, y, x + 3, y + 3)), "glow_yellow", 3)
    p.slot(106, 40, 113, 41); p.slot(106, 54, 113, 55)
    for y in (36, 54):
        thruster(p, 8, y, y + 6, "glow", 6)
    return p


# ---------------------------------------------------------------- Vuultam

def vuultam_garden():
    p = Pix(168, 96)
    H = p.h
    for (x0, x1, tip) in ((30, 82, 4), (70, 118, 10)):
        cx = (x0 + x1) // 2
        top = [(x0, 26), (x1, 26), (cx + 10, tip), (cx - 6, tip - 2)]
        m = p.mask(polygon=top) | p.mask(ellipse=(cx - 16, tip - 4, cx + 18, tip + 12))
        p.bevel(m, "petal", width=2, face=4, shade_lower=False)
        mb = p.mask(polygon=mirror(top, H)) | p.mask(ellipse=(cx - 16, H - 1 - (tip + 12), cx + 18, H - 1 - (tip - 4)))
        p.bevel(mb, "petal", width=2, face=3, edge_light=4, shade_lower=False)
        p.engrave([(cx, 25), (cx + 2, tip + 2)], highlight=False)
        p.engrave(mirror([(cx, 25), (cx + 2, tip + 2)], H), highlight=False)
    body = p.mask(rect=(14, 22, 140, 73)) | p.mask(ellipse=(112, 22, 166, 73)) | p.mask(ellipse=(6, 22, 38, 73))
    p.bevel(body, "seafoam", width=4, face=3, edge_light=5)
    p.bevel(p.mask(rect=(30, 28, 112, 67)) | p.mask(ellipse=(96, 28, 128, 67)), "seafoam", width=2, face=4)
    rng = random.Random(7)
    for (x0, y0, x1, y1) in ((34, 29, 64, 46), (34, 49, 64, 66), (72, 31, 102, 64)):
        p.bevel(p.mask(ellipse=(x0 - 2, y0 - 2, x1 + 2, y1 + 2)), "metal", width=1, face=3, shade_lower=False)
        p.dome(p.mask(ellipse=(x0, y0, x1, y1)), "leafglass")
        for _ in range(10):
            px, py = rng.randint(x0 + 4, x1 - 4), rng.randint(y0 + 5, y1 - 4)
            m = p.mask(rect=(px, py, px + 1, py + 1))
            p.paint(m, rng.choice(["crate_green", "crate_green", "petal", "gold"]))
            p.set_tone(m, 3)
    p.bevel(p.mask(polygon=[(124, 39), (148, 43), (157, 47), (148, 52), (124, 56), (131, 47)]), "glass", width=1, face=3, shade_lower=False)
    p.set_tone(p.mask(rect=(132, 43, 140, 44)), 5)
    for y in (31, 55):
        p.dome(p.mask(ellipse=(8, y, 18, y + 10)), "seafoam", shadow=True)
        thruster(p, 8, y + 2, y + 8, "glow_green", 5)
    return p


# ---------------------------------------------------------------- Moogli

def moogli_trader():
    p = Pix(144, 96)
    H = p.h
    rng = random.Random(5)
    for (x, w) in ((22, 22), (46, 18), (66, 22), (90, 16)):
        for top in (True, False):
            y0 = 3 + rng.randint(0, 6) if top else H - 1 - 21 + rng.randint(0, 3)
            mat = rng.choice(["crate_red", "crate_blue", "crate_green", "gold", "crate_violet"])
            p.bevel(p.mask(rect=(x, y0, x + w, y0 + 17)), mat, width=2, face=4 if top else 3, shade_lower=False)
            p.engrave([(x + 2, y0 + 8), (x + w - 2, y0 + 8)])
    hull = p.mask(ellipse=(8, 14, 132, 81)) | p.mask(rect=(6, 30, 20, 65))
    p.bevel(hull, "gold", width=4, face=3, edge_light=5)
    p.bevel(p.mask(ellipse=(20, 24, 112, 71)), "gold", width=2, face=4)
    yy, xx = yx(p)
    p.paint(hull & (xx >= 58) & (xx <= 63), "crate_green")
    for y in (21, 74):
        p.bevel(p.mask(rect=(18, y - 1, 112, y + 1)), "strap", width=1, face=3, shade_lower=False)
    for cy in (36, 59):
        p.bevel(p.mask(ellipse=(110, cy - 13, 138, cy + 13)), "strap", width=2, face=3, shade_lower=False)
        p.dome(p.mask(ellipse=(113, cy - 10, 135, cy + 10)), "glass")
        p.paint(p.mask(ellipse=(121, cy - 5, 131, cy + 5)), "dark")
        p.paint(p.mask(rect=(118, cy - 7, 120, cy - 6)), "white")
        p.set_tone(p.mask(rect=(118, cy - 7, 120, cy - 6)), 5)
    p.slot(84, 33, 94, 34); p.slot(84, 38, 94, 39)
    p.tube(p.mask(rect=(4, 38, 12, 57)), "strap", "x")
    thruster(p, 4, 41, 54, "glow", 6)
    return p


# ---------------------------------------------------------------- Ervani

def ervani_courier():
    p = Pix(144, 96)
    H = p.h
    ear = [(18, 24), (58, 24), (30, 2), (20, 0)]
    p.bevel(p.mask(polygon=ear), "russet", width=2, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=mirror(ear, H)), "russet", width=2, face=3, edge_light=4, shade_lower=False)
    tip = [(30, 2), (20, 0), (22, 9), (33, 11)]
    p.paint(p.mask(polygon=tip), "fur"); p.paint(p.mask(polygon=mirror(tip, H)), "fur")
    p.bevel(p.mask(ellipse=(4, 34, 36, 61)), "russet", width=2, face=3)
    p.paint(p.mask(ellipse=(4, 38, 14, 57)), "fur")
    body = [(22, 24), (110, 24), (132, 32), (143, 46), (143, 49), (132, 63), (110, 71), (22, 71)]
    p.bevel(p.mask(polygon=body), "russet", width=3, face=4)
    yy, xx = yx(p)
    p.paint(p.mask(polygon=body) & (yy >= 50), "fur")
    p.paint(p.mask(polygon=[(136, 42), (143, 46), (143, 49), (136, 53)]), "dark")
    p.bevel(p.mask(polygon=[(102, 30), (126, 38), (126, 57), (102, 65), (110, 47)]), "fur", width=2, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=[(111, 40), (127, 43), (127, 52), (111, 55), (115, 47)]), "glass", width=1, face=3, shade_lower=False)
    p.set_tone(p.mask(rect=(117, 43, 121, 44)), 5)
    for x in (46, 62, 78):
        p.shade(p.mask(polygon=[(x, 25), (x + 6, 25), (x + 12, 40), (x + 6, 40)]), -2)
    p.engrave([(42, 25), (42, 70)]); p.engrave([(94, 25), (94, 70)])
    p.slot(84, 32, 92, 33); p.slot(84, 36, 92, 37)
    for y in (28, 60):
        p.tube(p.mask(rect=(22, y, 30, y + 7)), "dark", "x", shadow=False)
    return p


# ---------------------------------------------------------------- Scyldar

def scyldar_lantern():
    p = Pix(168, 96)
    H = p.h
    fin_pts = [(26, 26), (130, 26), (112, 12), (84, 3), (56, 1), (36, 6)]
    fin = p.mask(polygon=fin_pts) | p.mask(ellipse=(40, 0, 110, 26))
    p.bevel(fin, "teal", width=2, face=4, shade_lower=False)
    finb = p.mask(polygon=mirror(fin_pts, H)) | p.mask(ellipse=(40, H - 27, 110, H - 1))
    p.bevel(finb, "teal", width=2, face=3, edge_light=4, shade_lower=False)
    yy, xx = yx(p)
    for m in (fin, finb):
        d = ndimage.distance_transform_edt(m)
        p.paint(m & (d <= 3) & (np.abs(yy - 47.5) > 30), "coral")
    for x in (52, 72, 92):
        p.glow(p.mask(ellipse=(x, 5, x + 4, 9)), "glow_yellow", 3)
        p.glow(p.mask(ellipse=(x, H - 10, x + 4, H - 6)), "glow_yellow", 2)
    p.tube(p.mask(rect=(0, 44, 30, 51)), "teal", "x")
    body = p.mask(rect=(26, 22, 130, 73)) | p.mask(ellipse=(104, 20, 166, 75))
    p.bevel(body, "teal", width=4, face=3, edge_light=5)
    p.bevel(p.mask(rect=(40, 29, 120, 66)) | p.mask(ellipse=(108, 29, 150, 66)), "teal", width=2, face=4)
    for x in (52, 62, 72):
        p.paint(p.mask(polygon=[(x, 30), (x + 2, 30), (x + 6, 38), (x + 4, 38)]), "coral")
        p.paint(p.mask(polygon=[(x, 65), (x + 2, 65), (x + 6, 57), (x + 4, 57)]), "coral")
    for cy in (36, 59):
        p.dome(p.mask(ellipse=(139, cy - 6, 153, cy + 6)), "dark")
        p.paint(p.mask(rect=(142, cy - 4, 144, cy - 3)), "white")
        p.set_tone(p.mask(rect=(142, cy - 4, 144, cy - 3)), 5)
    p.glow(p.mask(ellipse=(118, 43, 128, 52)), "glow_yellow", 3)
    p.glow(p.mask(ellipse=(121, 45, 125, 49)), "glow_yellow", 5)
    return p


# ---------------------------------------------------------------- Arachnay

def arachnay_weaver():
    p = Pix(144, 96)
    H = p.h
    for k in range(4):
        y = 7 + k * 4
        pts = [(26, y + 10), (60, y), (100, y + 8)]
        m = p._line(pts)
        p.tone[m] = 4; p.mat[m] = "silver"
        mb = p._line(mirror(pts, H))
        p.tone[mb] = 3; p.mat[mb] = "silver"
    for (x_root, x_tip, y_tip) in ((40, 18, 5), (58, 46, 2), (76, 82, 3), (92, 112, 7)):
        for top in (True, False):
            yr, yt = (26, y_tip) if top else (H - 1 - 26, H - 1 - y_tip)
            mid = ((x_root + x_tip) // 2, (yr + yt) // 2 + (-3 if top else 3))
            m = p._line([(x_root, yr), mid, (x_tip, yt)], width=3)
            p.bevel(m, "silver", width=1, face=4 if top else 3, shade_lower=False)
            p.dome(p.mask(ellipse=(x_tip - 5, yt - 4, x_tip + 5, yt + 4)), "violet", shadow=True)
    p.bevel(p.mask(ellipse=(4, 20, 62, 75)), "violet", width=3, face=3, edge_light=5)
    p.bevel(p.mask(ellipse=(52, 26, 118, 69)), "violet", width=3, face=4)
    p.bevel(p.mask(ellipse=(108, 30, 143, 65)), "violet", width=3, face=4)
    for pts in ([(18, 38), (32, 30), (46, 38), (32, 46)], [(18, 57), (32, 49), (46, 57), (32, 65)]):
        p.paint(p.mask(polygon=pts), "silver")
    for (x, y, c) in ((126, 40, "glow_red"), (126, 53, "glow_red"), (134, 43, "glow_teal"), (134, 50, "glow_teal"), (119, 46, "glow_red")):
        p.glow(p.mask(ellipse=(x, y, x + 3, y + 3)), c, 3)
    p.engrave([(62, 34), (62, 61)]); p.engrave([(110, 37), (110, 58)])
    for y in (40, 52):
        thruster(p, 5, y, y + 5, "glow_teal", 4)
    return p


# ---------------------------------------------------------------- the Rabble

def rabble_cutter():
    p = Pix(120, 96)
    rng = random.Random(9)
    jaw = [(6, 70), (98, 70), (119, 80), (96, 90), (40, 94), (12, 88)]
    p.bevel(p.mask(polygon=jaw), "gunmetal", width=2, face=3, shade_lower=False)
    for x in (24, 42, 60, 78):
        p.bevel(p.mask(polygon=[(x, 91), (x + 7, 91), (x + 3, 95)]), "silver", width=1, face=4, shade_lower=False)
    body = [(4, 24), (16, 6), (24, 0), (96, 0), (104, 6), (112, 20), (119, 40), (119, 50), (110, 66), (100, 72), (4, 72)]
    bm = p.mask(polygon=body)
    p.bevel(bm, "rust", width=3, face=3, edge_light=5)
    for _ in range(9):
        x, y = rng.randint(6, 90), rng.randint(4, 60)
        w, h = rng.randint(10, 22), rng.randint(7, 12)
        m = p.mask(rect=(x, y, x + w, y + h)) & bm
        p.bevel(m, rng.choice(["gunmetal", "metal", "rust", "gunmetal"]), width=1, face=rng.choice([3, 4]), shade_lower=False)
        for (rx, ry) in ((x + 2, y + 2), (x + w - 2, y + 2), (x + 2, y + h - 2), (x + w - 2, y + h - 2)):
            p.rivet(rx, ry)
    p.paint(p.mask(polygon=[(4, 42), (116, 38), (117, 44), (4, 49)]), "banner")
    p.slot(26, 8, 94, 11)
    for (y0, y1, x0) in ((8, 16, 102), (22, 30, 111), (36, 44, 114), (54, 62, 111)):
        p.bevel(p.mask(polygon=[(x0, y0), (min(119, x0 + 9), (y0 + y1) // 2), (x0, y1)]), "silver", width=1, face=4, shade_lower=False)
    p.glow(p.mask(rect=(98, 30, 108, 32)), "glow_red", 3)
    skull(p, 55, 17)
    for y in (30, 54):
        p.tube(p.mask(rect=(4, y, 9, y + 10)), "dark", "x", shadow=False)
        thruster(p, 4, y, y + 10, "glow", 5)
    return p


# ---------------------------------------------------------------- pirates: any ship, Rabble-style

PIRATE_SWAPS = {
    "terran_patrol": {"trim_blue": "banner", "orange": "dark"},
    "zaash_skiff": {"bronze": "rust", "banner": "dark"},
    "vuultam_garden": {"petal": "banner", "leafglass": "glass"},
    "moogli_trader": {"crate_green": "banner", "crate_blue": "gunmetal", "crate_violet": "rust"},
    "ervani_courier": {"fur": "bone", "glass": "banner"},
    "scyldar_lantern": {"coral": "dark"},
    "arachnay_weaver": {"silver": "banner"},
}


def piratize(src, seed=1, swaps=None):
    p = src.copy()
    rng = random.Random(seed)
    W, H = p.w, p.h
    solid = p.tone >= 0
    for a, b in (swaps or {}).items():
        p.mat[(p.mat == a) & solid] = b
    hull = solid & ~np.isin(p.mat, GLOWS) & (p.mat != "dark")
    for _ in range(2):
        x, y = rng.randint(W // 6, W - W // 3), rng.randint(6, H - 24)
        p.mat[p.mask(rect=(x, y, x + rng.randint(14, 24), y + rng.randint(10, 16))) & hull] = "banner"
    for _ in range(3):
        x0, y0 = rng.randint(W // 6, W - W // 4), rng.randint(H // 5, H - H // 3)
        dx, dy = rng.choice([(26, 10), (26, -10), (14, 24)])
        p.mat[p._line([(x0, y0), (x0 + dx, y0 + dy)], width=rng.randint(3, 4)) & hull] = "banner"
        for _ in range(3):
            t = rng.random()
            cx, cy = int(x0 + dx * t), int(y0 + dy * t) + 2
            p.mat[p.mask(rect=(cx, cy, cx, cy + rng.randint(2, 4))) & hull] = "banner"
    for _ in range(6):
        cx, cy, r = rng.randint(8, W - 8), rng.randint(8, H - 8), rng.randint(3, 6)
        p.mat[p.mask(ellipse=(cx - r, cy - r, cx + r, cy + r)) & hull] = "rust"
    for _ in range(4):
        x, y = rng.randint(4, W - 20), rng.randint(6, H - 16)
        w, h = rng.randint(8, 14), rng.randint(6, 9)
        m = p.mask(rect=(x, y, x + w, y + h)) & hull
        if m.sum() > 20:
            p.bevel(m, rng.choice(["gunmetal", "metal"]), width=1, face=3, shade_lower=False)
            for (rx, ry) in ((x + 1, y + 1), (x + w - 1, y + 1), (x + 1, y + h - 1), (x + w - 1, y + h - 1)):
                p.rivet(rx, ry)
    for y in range(12, H - 10, 11):
        xs = np.nonzero(p.tone[y] >= 0)[0]
        if len(xs) and xs.max() + 7 < W:
            x = int(xs.max())
            p.bevel(p.mask(polygon=[(x - 1, y - 2), (x + 6, y), (x - 1, y + 2)]), "silver", width=1, face=4, shade_lower=False)
    ys, xs = np.nonzero(hull)
    skull(p, int(xs.mean()) - 3, int(ys.mean()) - 14)
    return p


SHIPS = {
    "terran_patrol": (terran_patrol, "Terran Empire", "Terran patrol"),
    "zaash_skiff": (zaash_skiff, "Zaa'sh Junta", "Zaa'sh skiff"),
    "vuultam_garden": (vuultam_garden, "Vuultam", "Garden ship"),
    "moogli_trader": (moogli_trader, "Moogli", "Moogli trader"),
    "ervani_courier": (ervani_courier, "Ervani", "Ervani courier"),
    "scyldar_lantern": (scyldar_lantern, "Scyldar", "Lantern ship"),
    "arachnay_weaver": (arachnay_weaver, "Arachnay", "Weaver"),
    "rabble_cutter": (rabble_cutter, "The Rabble", "Rabble cutter"),
}

if __name__ == "__main__":
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(sys.argv[1] if len(sys.argv) > 1 else ".") / "art/ships"
    out.mkdir(parents=True, exist_ok=True)
    for sid, (fn, people, name) in SHIPS.items():
        p = fn()
        p.render().save(out / f"{sid}.png")
        if sid != "rabble_cutter":
            piratize(p, seed=len(sid), swaps=PIRATE_SWAPS.get(sid)).render().save(out / f"{sid}_rabble.png")
    print("ok", len(SHIPS))
