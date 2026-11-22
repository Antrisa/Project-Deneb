"""Ships for every culture (Claude, 21 Nov 2026). Zachary: one look per people, Claude draws them, he touches them up.
Top-down, nose right, built on 24-px cells. Each ship has a hull picture and FTL-style rooms on the grid.

  Terran Empire       terran_patrol      white hull, blue trim, 45-degree plates, a bridge tower
  Zaa'sh Junta        zaash_skiff        bone and bronze, ribbed like a carapace, a crescent prow, a shrine mast
  Vuultam             vuultam_garden     green-blue and rounded, glass garden domes, petal fins
  Moogli              moogli_trader      round and yellow, crates strapped on, two big frog-eye windows
  Ervani              ervani_courier     russet over cream like a fox, a pointed snout, ear fins and a brush tail
  Scyldar             scyldar_lantern    a teal manta with coral edges and glowing lanterns, a long tail
  Arachnay            arachnay_weaver    a violet spider: round abdomen, eight legs with pods, a web between them
  The Rabble          rabble_cutter      rust and gunmetal, welded plates, a red stripe, spikes

piratize() turns any of them into a Rabble ship: rust, red paint slapped on, welded plates, spikes, a skull.

Run from the repo root with -I:  python3 -I tools/dev/ship_art/cultures.py . [out dir for previews]
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ship_kit import *

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")


def finish(im):
    return outline(im)


def rivets(im, pts, col="#3a3a44"):
    for (x, y) in pts:
        rect(im, x, y, x, y, col)


def window_row(im, x0, y0, n, step, col, lite):
    for i in range(n):
        rect(im, x0 + i * step, y0, x0 + i * step + 2, y0 + 1, col)
        rect(im, x0 + i * step, y0, x0 + i * step, y0, lite)


# ---------------------------------------------------------------- Terran Empire

def terran_patrol():
    im = canvas(7, 4)
    W, H = im.size
    # angular side sponsons (45-degree plates), the guns sit on their front corners
    spon = [(26, 22), (118, 22), (104, 6), (60, 6), (46, 2), (32, 2)]
    shape(im, spon, "#eef0f2", "#eef0f2", None)
    shape(im, mirror_y(spon, H), "#d6dae0", "#d6dae0", None)
    poly(im, [(62, 6), (104, 6), (108, 10), (66, 10)], "#2f6fd0")
    poly(im, mirror_y([(62, 6), (104, 6), (108, 10), (66, 10)], H), "#1f4a90")
    for y in (4, H - 5):
        rect(im, 100, y - 1, 116, y + 1, "#7c8290")
    # the hull: a long chamfered box
    body = [(10, 22), (138, 22), (150, 28), (166, 40), (166, 55), (150, 67), (138, 73), (10, 73)]
    shape(im, body, "#f4f5f7", "#dde0e5", "#aeb4be", split=47.5)
    # blue trim stripe and chamfer lines
    rect(im, 12, 45, 150, 50, "#2f6fd0")
    rect(im, 12, 48, 150, 50, "#1f4a90")
    for x in (48, 96):
        line(im, [(x, 23), (x, 72)], "#c2c7cf")
    # engine block with three nozzles
    rect(im, 0, 26, 18, 69, "#7c8290")
    rect(im, 0, 26, 18, 46, "#959aa6")
    for y in (30, 43, 56):
        rect(im, 0, y, 4, y + 8, "#4a4f5c")
        rect(im, 1, y + 2, 2, y + 6, "#8ad0ff")
    # bridge tower with a row of blue windows
    shape(im, [(116, 30), (138, 30), (146, 38), (146, 57), (138, 65), (116, 65)], "#ffffff", "#e6e9ee", "#b8bec8", split=47.5)
    window_row(im, 124, 40, 5, 4, "#2a5aa8", "#8ad0ff")
    window_row(im, 124, 54, 5, 4, "#2a5aa8", "#8ad0ff")
    # imperial mark: an orange chevron on the spine
    poly(im, [(70, 30), (78, 30), (84, 37), (78, 44), (70, 44), (76, 37)], "#fb7412")
    rivets(im, [(20 + i * 8, 25) for i in range(4)] + [(20 + i * 8, 70) for i in range(4)], "#aeb4be")
    return finish(im)


TERRAN_ROOMS = [
    ("engines", "Engines", "engines", (0, 1, 2, 2)),
    ("weapons", "Weapons", "weapons", (2, 1, 2, 1)),
    ("life", "Oxygen", "life", (2, 2, 1, 1)),
    ("medbay", "Medbay", "medbay", (3, 2, 1, 1)),
    ("shields", "Shields", "shields", (4, 1, 1, 2)),
    ("pilot", "Bridge", "pilot", (5, 1, 1, 2)),
]


# ---------------------------------------------------------------- Zaa'sh Junta

def zaash_skiff():
    im = canvas(6, 4)
    W, H = im.size
    # blade fins, curved back like a carapace's edge
    fin = [(20, 22), (86, 22), (64, 10), (40, 2), (22, 0), (14, 6)]
    shape(im, fin, "#efe6d2", "#efe6d2")
    shape(im, mirror_y(fin, H), "#d8ccb2", "#d8ccb2")
    line(im, [(86, 22), (64, 10), (40, 2)], "#b07a3a")
    line(im, mirror_y([(86, 22), (64, 10), (40, 2)], H), "#8a5a26")
    # the carapace: an oval body
    oval(im, (4, 20, 128, 75), "#f2e9d6", "#dccfb5", "#b5a688", split=47.5)
    # bronze ribs across it
    for x in (26, 44, 62, 80, 98):
        for y in range(22, 74):
            dx = int(3 * ((y - 47.5) / 26.0) ** 2 * 3)
            xx = x - dx
            if im.getpixel((xx, y))[3]:
                im.putpixel((xx, y), hexc("#b07a3a") if y < 48 else hexc("#8a5a26"))
    # the crescent prow blade
    poly(im, [(118, 24), (130, 26), (143, 40), (143, 55), (130, 69), (118, 71), (128, 58), (132, 47), (128, 37)], "#c8904a")
    line(im, [(130, 27), (141, 41)], "#e8b86a")
    # the shrine mast: a bronze ring with a red banner trailing back, and two little bells
    ellipse(im, 60, 41, 70, 51, "#8a5a26")
    ellipse(im, 62, 43, 68, 49, "#e8b86a")
    poly(im, [(60, 44), (40, 40), (44, 46), (40, 52), (60, 48)], "#b03a3a")
    for (x, y) in ((56, 36), (56, 58)):
        ellipse(im, x, y, x + 3, y + 3, "#f2c94c")
    # eye slits at the front
    rect(im, 108, 40, 114, 42, "#3a2a28"); rect(im, 108, 53, 114, 55, "#3a2a28")
    return finish(im)


ZAASH_ROOMS = [
    ("engines", "Engines", "engines", (0, 1, 1, 2)),
    ("life", "Oxygen", "life", (1, 1, 1, 1)),
    ("shields", "Shields", "shields", (1, 2, 1, 1)),
    ("weapons", "Weapons", "weapons", (2, 1, 2, 1)),
    ("shrine", "Shrine", "", (2, 2, 2, 1)),
    ("pilot", "Helm", "pilot", (4, 1, 1, 2)),
]


# ---------------------------------------------------------------- Vuultam

def vuultam_garden():
    im = canvas(7, 4)
    W, H = im.size
    # petal fins, two to a side
    for (x0, x1, tip) in ((30, 82, 4), (70, 118, 10)):
        petal = [(x0, 23), (x1, 23), ((x0 + x1) // 2 + 10, tip), ((x0 + x1) // 2 - 6, tip - 2)]
        m = mask_of(im.size, lambda L: (poly(L, petal, (255, 255, 255, 255)), ellipse(L, (x0 + x1) // 2 - 16, tip - 4, (x0 + x1) // 2 + 18, tip + 12, (255, 255, 255, 255))))
        paint_shaded(im, m, "#f0b4d4", "#f0b4d4")
        mb = mask_of(im.size, lambda L: (poly(L, mirror_y(petal, H), (255, 255, 255, 255)), ellipse(L, (x0 + x1) // 2 - 16, H - 1 - (tip + 12), (x0 + x1) // 2 + 18, H - 1 - (tip - 4), (255, 255, 255, 255))))
        paint_shaded(im, mb, "#d090b4", "#d090b4")
        line(im, [((x0 + x1) // 2, 22), ((x0 + x1) // 2 + 2, tip + 2)], "#c878a8")
        line(im, mirror_y([((x0 + x1) // 2, 22), ((x0 + x1) // 2 + 2, tip + 2)], H), "#a85a88")
    # a rounded body like a seed pod
    m = mask_of(im.size, lambda L: (rect(L, 14, 22, 140, 73, (255, 255, 255, 255)), ellipse(L, 112, 22, 166, 73, (255, 255, 255, 255)), ellipse(L, 2, 22, 34, 73, (255, 255, 255, 255))))
    paint_shaded(im, m, "#7cc8b0", "#5aa894", None, split=47.5)
    inner_edge(im, "#3a7a6c", "bottom", 2)
    # glass garden domes with plants and flowers
    for (x0, y0, x1, y1) in ((36, 28, 66, 46), (36, 50, 66, 68), (76, 32, 104, 63)):
        ellipse(im, x0, y0, x1, y1, "#2a6a5c")
        ellipse(im, x0 + 1, y0 + 1, x1 - 1, y1 - 1, "#bff0d0")
        rng = random.Random(x0 * 7 + y0)
        for _ in range(12):
            px, py = rng.randint(x0 + 4, x1 - 4), rng.randint(y0 + 4, y1 - 4)
            rect(im, px, py, px + 1, py + 1, rng.choice(["#4a9a4a", "#3a8a3a", "#f08ab0", "#ffd86a"]))
        rect(im, x0 + 5, y0 + 3, x0 + 8, y0 + 4, "#f4fff8")
    # cockpit: a leaf-shaped window
    poly(im, [(124, 40), (148, 44), (156, 47), (148, 51), (124, 55), (130, 47)], "#2a6a5c")
    poly(im, [(127, 42), (146, 45), (152, 47), (146, 49), (127, 53), (132, 47)], "#9ee8e0")
    # engines: two soft round vents
    for y in (30, 54):
        ellipse(im, 0, y, 12, y + 12, "#3a7a6c"); ellipse(im, 2, y + 2, 8, y + 9, "#c8ffe0")
    return finish(im)


VUULTAM_ROOMS = [
    ("engines", "Engines", "engines", (0, 1, 1, 2)),
    ("life", "Garden", "life", (1, 1, 2, 1)),
    ("medbay", "Medbay", "medbay", (1, 2, 2, 1)),
    ("shields", "Shields", "shields", (3, 1, 1, 2)),
    ("weapons", "Weapons", "weapons", (4, 1, 1, 1)),
    ("crew", "Quarters", "", (4, 2, 1, 1)),
    ("pilot", "Helm", "pilot", (5, 1, 1, 2)),
]


# ---------------------------------------------------------------- Moogli

def moogli_trader():
    im = canvas(6, 4)
    W, H = im.size
    # crates strapped on top and bottom
    rng = random.Random(5)
    for (x, w) in ((22, 22), (46, 18), (66, 22), (90, 16)):
        for top in (True, False):
            y0 = 4 + rng.randint(0, 6) if top else H - 1 - 22 + rng.randint(0, 4)
            col = rng.choice(["#d8583a", "#3a78c8", "#5aa848", "#c8a050", "#a86ac8"])
            rect(im, x, y0, x + w, y0 + 17, col)
            line(im, [(x, y0 + 8), (x + w, y0 + 8)], "#3a2a20")
            line(im, [(x + w // 2, y0), (x + w // 2, y0 + 17)], "#3a2a20")
    # the round hull
    m = mask_of(im.size, lambda L: (ellipse(L, 6, 14, 132, 81, (255, 255, 255, 255)), rect(L, 2, 30, 20, 65, (255, 255, 255, 255))))
    paint_shaded(im, m, "#f6d45a", "#e0b23a", None, split=47.5)
    inner_edge(im, "#a87e1a", "bottom", 2)
    # green trim band
    for y in range(22, 74):
        for x in range(0, W):
            if im.getpixel((x, y))[3] and 60 <= x <= 64:
                im.putpixel((x, y), hexc("#5aa848") if y < 48 else hexc("#3a8838"))
    # straps over the crates
    for y in (22, 73):
        line(im, [(20, y), (110, y)], "#6a4a2a", 2)
    # two big frog-eye windows at the front
    for (cy, lite) in ((36, True), (59, False)):
        ellipse(im, 112, cy - 12, 138, cy + 12, "#3a2a20")
        ellipse(im, 114, cy - 10, 136, cy + 10, "#7fd0e0" if lite else "#5ab0c0")
        ellipse(im, 122, cy - 5, 132, cy + 5, "#1a3a48")
        rect(im, 118, cy - 7, 121, cy - 5, "#ffffff")
    # a round thruster at the back
    rect(im, 0, 38, 6, 57, "#6a5a3a"); rect(im, 0, 42, 2, 53, "#ffb04a")
    return finish(im)


MOOGLI_ROOMS = [
    ("engines", "Engines", "engines", (0, 1, 1, 2)),
    ("cargo", "Cargo", "", (1, 1, 2, 1)),
    ("life", "Oxygen", "life", (1, 2, 1, 1)),
    ("weapons", "Weapons", "weapons", (2, 2, 1, 1)),
    ("shields", "Shields", "shields", (3, 1, 1, 2)),
    ("pilot", "Cockpit", "pilot", (4, 1, 1, 2)),
]


# ---------------------------------------------------------------- Ervani

def ervani_courier():
    im = canvas(6, 4)
    W, H = im.size
    # ear fins at the back, swept like a fox's ears, cream-tipped
    ear = [(14, 23), (54, 23), (26, 2), (16, 0)]
    shape(im, ear, "#d8642e", "#d8642e")
    shape(im, mirror_y(ear, H), "#b04c20", "#b04c20")
    poly(im, [(26, 2), (16, 0), (18, 8), (28, 10)], "#f6ead8")
    poly(im, mirror_y([(26, 2), (16, 0), (18, 8), (28, 10)], H), "#e0d0b8")
    # the brush tail behind, white-tipped
    m = mask_of(im.size, lambda L: ellipse(L, 0, 36, 30, 59, (255, 255, 255, 255)))
    paint_shaded(im, m, "#d8642e", "#b04c20")
    ellipse(im, 0, 40, 9, 55, "#f6ead8")
    # the body: russet back, cream belly, a pointed snout
    body = [(20, 24), (110, 24), (132, 32), (143, 46), (143, 49), (132, 63), (110, 71), (20, 71)]
    shape(im, body, "#d8642e", "#f0e0c8", None, split=50)
    inner_edge(im, "#c8b8a0", "bottom", 1)
    poly(im, [(136, 42), (143, 46), (143, 49), (136, 53)], "#3a2a28")
    # cream face blaze and a dark window strip
    poly(im, [(104, 30), (126, 38), (126, 57), (104, 65), (112, 47)], "#f6ead8")
    poly(im, [(112, 40), (126, 43), (126, 52), (112, 55), (116, 47)], "#3a4a5a")
    rect(im, 118, 44, 121, 45, "#9ad0e8")
    # flank stripes
    for x in (46, 62, 78):
        poly(im, [(x, 25), (x + 6, 25), (x + 12, 40), (x + 6, 40)], "#a84a1e")
    return finish(im)


ERVANI_ROOMS = [
    ("engines", "Engines", "engines", (0, 1, 1, 2)),
    ("weapons", "Weapons", "weapons", (1, 1, 1, 1)),
    ("life", "Oxygen", "life", (1, 2, 1, 1)),
    ("shields", "Shields", "shields", (2, 1, 1, 2)),
    ("crew", "Cabin", "", (3, 1, 1, 2)),
    ("pilot", "Cockpit", "pilot", (4, 1, 1, 2)),
]


# ---------------------------------------------------------------- Scyldar

def scyldar_lantern():
    im = canvas(7, 4)
    W, H = im.size
    # manta fins: wide and rounded, coral edges, lanterns along them
    fin = [(26, 24), (130, 24), (112, 12), (84, 3), (56, 1), (36, 6)]
    m = mask_of(im.size, lambda L: (poly(L, fin, (255, 255, 255, 255)), ellipse(L, 40, 0, 110, 26, (255, 255, 255, 255))))
    paint_shaded(im, m, "#46b4b0", "#46b4b0")
    mb = mask_of(im.size, lambda L: (poly(L, mirror_y(fin, H), (255, 255, 255, 255)), ellipse(L, 40, H - 27, 110, H - 1, (255, 255, 255, 255))))
    paint_shaded(im, mb, "#2a8a88", "#2a8a88")
    inner_edge(im, "#f07a64", "top", 2)
    for x in (52, 72, 92):
        ellipse(im, x, 5, x + 4, 9, "#ffd86a"); rect(im, x + 1, 6, x + 2, 7, "#fff6c0")
        ellipse(im, x, H - 10, x + 4, H - 6, "#f0c050")
    # the long tail
    poly(im, [(0, 46), (30, 42), (30, 53), (0, 49)], "#2a8a88")
    poly(im, [(0, 46), (30, 42), (30, 47), (0, 47)], "#46b4b0")
    # the body and rounded head
    m2 = mask_of(im.size, lambda L: (rect(L, 26, 22, 130, 73, (255, 255, 255, 255)), ellipse(L, 104, 20, 166, 75, (255, 255, 255, 255))))
    paint_shaded(im, m2, "#58c4c0", "#3a9c9a", None, split=47.5)
    inner_edge(im, "#1c6464", "bottom", 2)
    # coral stripe and gill slits
    for x in (50, 60, 70):
        line(im, [(x, 30), (x + 4, 38)], "#f07a64")
        line(im, [(x, 65), (x + 4, 57)], "#c85a48")
    # eyes
    for cy in (36, 59):
        ellipse(im, 140, cy - 5, 152, cy + 5, "#123a3a"); rect(im, 143, cy - 3, 145, cy - 2, "#bff4f0")
    # lanterns on the head
    ellipse(im, 120, 44, 128, 51, "#ffd86a"); rect(im, 122, 46, 124, 47, "#fff6c0")
    return finish(im)


SCYLDAR_ROOMS = [
    ("engines", "Jets", "engines", (1, 1, 1, 2)),
    ("life", "Water", "life", (2, 1, 1, 1)),
    ("shields", "Shields", "shields", (2, 2, 1, 1)),
    ("weapons", "Weapons", "weapons", (3, 1, 2, 1)),
    ("cargo", "Market", "", (3, 2, 2, 1)),
    ("pilot", "Helm", "pilot", (5, 1, 1, 2)),
]


# ---------------------------------------------------------------- Arachnay

def arachnay_weaver():
    im = canvas(6, 4)
    W, H = im.size
    # the web, strung between the legs
    web = layer(im.size)
    for k in range(4):
        y = 6 + k * 4
        line(web, [(24, y + 10), (60, y), (100, y + 8)], (220, 220, 240, 110))
        line(web, [(24, H - 1 - y - 10), (60, H - 1 - y), (100, H - 1 - y - 8)], (200, 200, 225, 90))
    im.alpha_composite(web)
    # eight legs, four a side, each holding a small pod
    for (x_root, x_tip, y_tip) in ((40, 18, 4), (58, 46, 1), (76, 82, 2), (92, 112, 6)):
        for top in (True, False):
            yr, yt = (24, y_tip) if top else (H - 1 - 24, H - 1 - y_tip)
            line(im, [(x_root, yr), ((x_root + x_tip) // 2, (yr + yt) // 2 + (-3 if top else 3)), (x_tip, yt)], "#c8c8d8" if top else "#a8a8bc", 2)
            ellipse(im, x_tip - 4, yt - 3, x_tip + 4, yt + 3, "#9a7ad8" if top else "#7a5ab8")
    # abdomen (rear), thorax and head
    oval(im, (2, 20, 62, 75), "#9a7ad8", "#7a5ab8", None, split=47.5)
    oval(im, (52, 26, 118, 69), "#a88ae0", "#8a6ac8", None, split=47.5)
    oval(im, (108, 30, 143, 65), "#b49ae8", "#9478d0", None, split=47.5)
    inner_edge(im, "#4a3080", "bottom", 2)
    # silver markings on the abdomen, and the eyes
    poly(im, [(20, 38), (34, 30), (48, 38), (34, 46)], "#d8d8e8")
    poly(im, [(20, 57), (34, 49), (48, 57), (34, 65)], "#b8b8cc")
    for (x, y, c) in ((126, 40, "#e6463c"), (126, 53, "#e6463c"), (134, 43, "#5af0ff"), (134, 50, "#5af0ff"), (120, 46, "#e6463c")):
        ellipse(im, x, y, x + 3, y + 3, c)
    return finish(im)


ARACHNAY_ROOMS = [
    ("engines", "Engines", "engines", (0, 1, 1, 2)),
    ("life", "Oxygen", "life", (1, 1, 1, 1)),
    ("drones", "Drone bay", "drones", (1, 2, 1, 1)),
    ("shields", "Shields", "shields", (2, 1, 1, 2)),
    ("weapons", "Weapons", "weapons", (3, 1, 1, 1)),
    ("crew", "Loom", "", (3, 2, 1, 1)),
    ("pilot", "Cockpit", "pilot", (4, 1, 1, 2)),
]


# ---------------------------------------------------------------- the Rabble

def rabble_cutter():
    im = canvas(5, 4)
    W, H = im.size
    rng = random.Random(9)
    # the lower jaw: a spiked ram plate
    jaw = [(6, 70), (98, 70), (119, 80), (96, 90), (40, 94), (12, 88)]
    shape(im, jaw, "#5a5e66", "#4a4e56")
    for x in (24, 42, 60, 78):
        poly(im, [(x, 92), (x + 7, 92), (x + 2, 95)], "#a8acb4")
    # the body: a rusty wedge, gun deck on top, a ram prow
    body = [(0, 24), (14, 6), (22, 0), (96, 0), (104, 6), (112, 20), (119, 40), (119, 50), (110, 66), (100, 72), (0, 72)]
    shape(im, body, "#8a5a3c", "#6e4430", "#4a2c20", split=36)
    # mismatched plates welded on, with rivets
    for _ in range(10):
        x, y = rng.randint(4, 94), rng.randint(3, 62)
        w, h = rng.randint(8, 22), rng.randint(6, 12)
        col = rng.choice(["#6e727a", "#5a5e66", "#868a92", "#7a4428", "#9a6040"])
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if 0 <= xx < W and 0 <= yy < H and im.getpixel((xx, yy))[3]:
                    im.putpixel((xx, yy), hexc(col))
        rivets(im, [(x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 2), (x + w - 2, y + h - 2)])
    # the red stripe, and the gun deck's dark slot
    poly(im, [(0, 42), (114, 38), (116, 44), (0, 49)], "#b82a20")
    rect(im, 26, 8, 94, 12, "#2e2e38")
    # ram prow spikes
    for (y0, y1, x0) in ((8, 16, 102), (22, 30, 112), (36, 44, 116), (54, 62, 112)):
        poly(im, [(x0, y0), (min(119, x0 + 10), (y0 + y1) // 2), (x0, y1)], "#b8bcc4")
    # a cockpit slit, a skull, and two ragged exhausts
    rect(im, 98, 30, 108, 33, "#e6463c")
    skull(im, 58, 18)
    for y in (30, 54):
        rect(im, 0, y, 5, y + 10, "#3a3a44"); rect(im, 0, y + 3, 2, y + 7, "#ff7a3a")
    return finish(im)


def skull(im, x, y, col="#f0ece0", dark="#262535"):
    rect(im, x + 1, y, x + 5, y, col); rect(im, x, y + 1, x + 6, y + 4, col); rect(im, x + 1, y + 5, x + 5, y + 6, col)
    rect(im, x + 1, y + 2, x + 2, y + 3, dark); rect(im, x + 4, y + 2, x + 5, y + 3, dark); rect(im, x + 3, y + 4, x + 3, y + 4, dark)
    rect(im, x + 2, y + 6, x + 2, y + 6, dark); rect(im, x + 4, y + 6, x + 4, y + 6, dark)


RABBLE_ROOMS = [
    ("weapons", "Gun deck", "weapons", (1, 0, 3, 1)),
    ("engines", "Engines", "engines", (0, 1, 1, 2)),
    ("shields", "Shields", "shields", (1, 1, 1, 1)),
    ("life", "Oxygen", "life", (1, 2, 1, 1)),
    ("crew", "Crew deck", "", (2, 1, 2, 2)),
    ("pilot", "Cockpit", "pilot", (4, 1, 1, 2)),
]


# ---------------------------------------------------------------- pirates: any ship, Rabble-style

def piratize(src, seed=1, swaps=None):
    """A captured ship, haphazardly repainted by the Rabble (Zachary, 21 Nov): its trim colours swapped for Rabble red
    (swaps: {"#from": "#to"}), a panel or two painted over, red paint slapped on in rough strokes with drips, rust,
    welded plates, spikes on the nose and a skull."""
    im = src.copy()
    W, H = im.size
    rng = random.Random(seed)
    px = im.load()
    def on_hull(x, y):
        return 0 <= x < W and 0 <= y < H and px[x, y][3] and px[x, y][:3] != OUTLINE[:3]
    # the culture's trim colours, repainted
    swap = {hexc(k)[:3]: hexc(v) for k, v in (swaps or {}).items()}
    for y in range(H):
        for x in range(W):
            if px[x, y][3] and px[x, y][:3] in swap:
                px[x, y] = swap[px[x, y][:3]]
    # a panel or two painted over in Rabble red, keeping the light and shade under it
    for _ in range(2):
        x, y = rng.randint(W // 6, W - W // 3), rng.randint(4, H - 24)
        w, h = rng.randint(14, 26), rng.randint(10, 18)
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if on_hull(xx, yy):
                    lum = sum(px[xx, yy][:3]) / 765
                    px[xx, yy] = (int(150 + 60 * lum), int(30 + 30 * lum), int(26 + 20 * lum), 255)
    # rough red strokes with drips
    for _ in range(3):
        x0, y0 = rng.randint(W // 6, W - W // 4), rng.randint(H // 5, H - H // 3)
        length, width = rng.randint(18, 34), rng.randint(3, 5)
        dx, dy = rng.choice([(1, 0.4), (1, -0.4), (0.6, 1)])
        for t in range(length):
            cx, cy = int(x0 + dx * t), int(y0 + dy * t)
            w = width + rng.randint(-1, 1)
            for yy in range(cy - w // 2, cy + w // 2 + 1):
                for xx in range(cx - 1, cx + 2):
                    if on_hull(xx, yy):
                        px[xx, yy] = hexc("#b82a20") if yy < H / 2 else hexc("#962018")
            if rng.random() < 0.12:
                for k in range(rng.randint(2, 5)):
                    if on_hull(cx, cy + w // 2 + k):
                        px[cx, cy + w // 2 + k] = hexc("#962018")
    # rust patches
    for _ in range(5):
        cx, cy, r = rng.randint(8, W - 8), rng.randint(8, H - 8), rng.randint(3, 7)
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if on_hull(x, y) and (x - cx) ** 2 + (y - cy) ** 2 + rng.randint(-6, 6) < r * r:
                    c = px[x, y]
                    rust = hexc(rng.choice(["#8a4a2c", "#7a3e24", "#9a5632"]))
                    px[x, y] = tuple(int(c[i] * 0.3 + rust[i] * 0.7) for i in range(3)) + (255,)
    # welded plates with rivets
    for _ in range(4):
        x, y = rng.randint(4, W - 20), rng.randint(4, H - 14)
        w, h = rng.randint(8, 16), rng.randint(6, 10)
        col = hexc(rng.choice(["#6e727a", "#5a5e66", "#7a7e86"]))
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if on_hull(xx, yy):
                    px[xx, yy] = col
        for (rx, ry) in ((x + 1, y + 1), (x + w - 2, y + 1), (x + 1, y + h - 2), (x + w - 2, y + h - 2)):
            if on_hull(rx, ry):
                px[rx, ry] = hexc("#3a3a44")
    skull(im, W // 2 - 3, H // 2 - 14)
    # spikes welded to the nose
    spikes = layer(im.size)
    for y in range(10, H - 8, 12):
        for x in range(W - 1, 0, -1):
            if px[x, y][3] and px[x, y][:3] == OUTLINE[:3]:
                if x + 6 < W:
                    poly(spikes, [(x - 1, y - 2), (x + 6, y), (x - 1, y + 2)], "#a8acb4")
                break
    im.alpha_composite(spikes)
    return im


# The trim each culture's ship loses when the Rabble repaint it.
PIRATE_SWAPS = {
    "terran_patrol": {"#2f6fd0": "#b82a20", "#1f4a90": "#962018", "#fb7412": "#262535"},
    "zaash_skiff": {"#b03a3a": "#262535", "#e8b86a": "#b82a20", "#c8904a": "#7a7e86"},
    "vuultam_garden": {"#f0b4d4": "#b82a20", "#d090b4": "#962018", "#c878a8": "#6a1810", "#a85a88": "#4a1008"},
    "moogli_trader": {"#5aa848": "#b82a20", "#3a8838": "#962018", "#7fd0e0": "#e6463c", "#5ab0c0": "#b82a20"},
    "ervani_courier": {"#a84a1e": "#262535", "#3a4a5a": "#b82a20", "#f6ead8": "#b82a20"},
    "scyldar_lantern": {"#ffd86a": "#e6463c", "#f0c050": "#b82a20", "#f07a64": "#262535", "#c85a48": "#262535"},
    "arachnay_weaver": {"#d8d8e8": "#b82a20", "#b8b8cc": "#962018", "#5af0ff": "#e6463c"},
}

SHIPS = {
    "terran_patrol": (terran_patrol, TERRAN_ROOMS, "Terran Empire", "Terran patrol"),
    "zaash_skiff": (zaash_skiff, ZAASH_ROOMS, "Zaa'sh Junta", "Zaa'sh skiff"),
    "vuultam_garden": (vuultam_garden, VUULTAM_ROOMS, "Vuultam", "Vuultam garden ship"),
    "moogli_trader": (moogli_trader, MOOGLI_ROOMS, "Moogli", "Moogli trader"),
    "ervani_courier": (ervani_courier, ERVANI_ROOMS, "Ervani", "Ervani courier"),
    "scyldar_lantern": (scyldar_lantern, SCYLDAR_ROOMS, "Scyldar", "Scyldar lantern ship"),
    "arachnay_weaver": (arachnay_weaver, ARACHNAY_ROOMS, "Arachnay", "Arachnay weaver"),
    "rabble_cutter": (rabble_cutter, RABBLE_ROOMS, "The Rabble", "Rabble cutter"),
}

if __name__ == "__main__":
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "art/ships"
    out.mkdir(parents=True, exist_ok=True)
    for sid, (fn, rooms, people, name) in SHIPS.items():
        im = fn()
        im.save(out / f"{sid}.png")
        if sid != "rabble_cutter":
            piratize(im, seed=len(sid), swaps=PIRATE_SWAPS.get(sid, {})).save(out / f"{sid}_rabble.png")
    print("ok", len(SHIPS))
