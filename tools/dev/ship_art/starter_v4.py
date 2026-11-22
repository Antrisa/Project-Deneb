"""The starter fighter, v4 (21 Nov 2026). Zachary: shorten the back; lengthen the cockpit if it needs length. Behind
the cockpit is out of reach for the player: it's a single-seat fighter, and the repair drone looks after the bays.
(Other ships are walkable all through.)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixkit import Pix
import numpy as np
from scipy import ndimage
from PIL import Image

W, H = 168, 96
def my(pts): return [(x, H - 1 - y) for x, y in pts]
BODY = [(22, 22), (126, 22), (146, 28), (166, 44), (166, 51), (146, 67), (126, 73), (22, 73)]
WING = [(38, 24), (90, 24), (66, 3), (62, 1), (44, 1), (36, 4)]
BAND = [(62, 24), (74, 24), (58, 2), (52, 2)]
PODS = ((25, 45), (50, 70))
POD_X = (10, 46)
# rooms (cells): the drone's bays in columns 1-3, the cockpit 2 x 2 under a long canopy
ROOMS = {
    "engines": (1, 1, 1, 2), "weapons": (2, 1, 1, 1), "drones": (2, 2, 1, 1),
    "shields": (3, 1, 1, 1), "life": (3, 2, 1, 1), "cockpit": (4, 1, 2, 2),
}
HATCHES = [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (2, 2)), ((2, 1), (3, 1)), ((2, 2), (3, 2)), ((3, 1), (3, 2)), ((3, 1), (4, 1))]

def hull():
    p = Pix(W, H)
    p.bevel(p.mask(polygon=WING), "hull", width=2, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=my(WING)), "hull", width=2, face=3, edge_light=4, shade_lower=False)
    for pts in (BAND, my(BAND)):
        p.paint(p.mask(polygon=pts), "orange")
    p.engrave([(46, 24), (42, 4)]); p.engrave([(46, 71), (42, 91)])
    p.bevel(p.mask(polygon=BODY), "hull", width=3, face=3, edge_light=5)
    p.bevel(p.mask(polygon=[(40, 29), (118, 29), (132, 36), (132, 59), (118, 66), (40, 66)]), "hull", width=2, face=4)
    for x in (52, 70):
        p.paint(p.mask(polygon=[(x, 22), (x + 7, 22), (x + 15, 47), (x + 8, 47)]), "orange")
        p.paint(p.mask(polygon=[(x + 8, 48), (x + 15, 48), (x + 7, 73), (x, 73)]), "orange")
    p.paint(p.mask(polygon=[(156, 38), (166, 44), (166, 51), (156, 57)]), "orange")
    p.engrave([(40, 25), (40, 70)]); p.engrave([(94, 25), (94, 70)]); p.engrave([(150, 31), (150, 64)])
    p.engrave_rect(25, 51, 37, 63)
    for i in range(3):
        p.slot(84, 32 + i * 4, 92, 33 + i * 4)
        p.slot(84, 55 + i * 4, 92, 56 + i * 4)
    for x in range(44, 92, 8):
        p.rivet(x, 26); p.rivet(x, 69)
    for y in (31, 40, 55, 64):
        p.rivet(97, y)
    for (y0, y1) in PODS:
        p.tube(p.mask(rect=(POD_X[0], y0, POD_X[1], y1)), "metal", "x")
        p.paint(p.mask(rect=(20, y0, 24, y1)), "orange")
        for x in (16, 30, 40):
            p.engrave([(x, y0 + 1), (x, y1 - 1)])
        p.slot(32, y0 + 4, 36, y0 + 5)
        p.tube(p.mask(rect=(POD_X[0], y0 + 2, POD_X[0] + 4, y1 - 2)), "dark", "x", shadow=False)
    # a long canopy over the cockpit
    p.bevel(p.mask(ellipse=(98, 31, 152, 64)), "metal", width=2, face=3, shade_lower=False)
    p.dome(p.mask(ellipse=(101, 34, 149, 61)), "glass")
    p.engrave([(125, 35), (125, 60)], highlight=False)          # the canopy's middle strut
    for y in (9, H - 1 - 9):
        p.tube(p.mask(rect=(54, y - 2, 78, y + 2)), "metal", "x", bands=(5, 4, 3, 2, 1))
        p.tube(p.mask(rect=(78, y - 1, 81, y + 1)), "dark", "x", shadow=False)
    for (y0, y1) in PODS:
        cy = (y0 + y1) / 2
        g = p.mask(ellipse=(3, cy - 7, 14, cy + 7)) & (np.mgrid[0:H, 0:W][1] < POD_X[0] + 1)
        p.glow(g, "glow", 2)
        p.glow(p.mask(ellipse=(5, cy - 4, 12, cy + 4)) & g, "glow", 3)
        p.glow(p.mask(ellipse=(7, cy - 2, 12, cy + 2)) & g, "glow", 4)
    p.glow(p.mask(rect=(46, 2, 48, 3)), "glow_green", 3)
    p.glow(p.mask(rect=(46, H - 4, 48, H - 3)), "glow_red", 3)
    return p

def interior(p):
    block = np.zeros((H, W), bool)
    for (cx, cy, cw, ch) in ROOMS.values():
        block[cy * 24:(cy + ch) * 24, cx * 24:(cx + cw) * 24] = True
    frame = ndimage.binary_dilation(block, iterations=3) & ~block & (p.tone >= 0)
    p.mat[frame] = "wall"; p.tone[frame] = 3
    p.tone[frame & ~ndimage.binary_erosion(frame | block, iterations=1)] = 1
    for rid, (cx, cy, cw, ch) in ROOMS.items():
        x0, y0, x1, y1 = cx * 24, cy * 24, (cx + cw) * 24 - 1, (cy + ch) * 24 - 1
        m = p.mask(rect=(x0, y0, x1, y1))
        p.lines[m] = False
        if rid == "cockpit":
            p.mat[m] = "cockpit_deck"; p.tone[m] = 4
            for k in range(cw):
                for j in range(ch):
                    tx, ty = x0 + k * 24, y0 + j * 24
                    p.set_tone(p.mask(rect=(tx, ty, tx + 23, ty)), 5)
                    p.set_tone(p.mask(rect=(tx, ty + 23, tx + 23, ty + 23)), 3)
                    p.set_tone(p.mask(rect=(tx + 23, ty, tx + 23, ty + 23)), 3)
        else:
            # a cramped machinery bay: dark grating floor
            p.mat[m] = "bay"; p.tone[m] = 3
            for yy in range(y0 + 2, y1, 3):
                p.set_tone(p.mask(rect=(x0, yy, x1, yy)), 2)
    # walls between rooms, 2 px; the bulkhead in front of the cockpit is thicker
    wall = np.zeros((H, W), bool)
    def room_at(cell):
        for rid, (cx, cy, cw, ch) in ROOMS.items():
            if cx <= cell[0] < cx + cw and cy <= cell[1] < cy + ch:
                return rid
        return ""
    for rid, (cx, cy, cw, ch) in ROOMS.items():
        for x in range(cx, cx + cw):
            for y in range(cy, cy + ch):
                x0, y0 = x * 24, y * 24
                if room_at((x + 1, y)) != rid: wall[y0:y0 + 24, x0 + 22:x0 + 24] = True
                if room_at((x - 1, y)) != rid: wall[y0:y0 + 24, x0:x0 + 2] = True
                if room_at((x, y + 1)) != rid: wall[y0 + 22:y0 + 24, x0:x0 + 24] = True
                if room_at((x, y - 1)) != rid: wall[y0:y0 + 2, x0:x0 + 24] = True
    wall[24:72, 94:98] = True
    for (a, b) in HATCHES:
        (c1, r1), (c2, r2) = a, b
        if r1 == r2:
            x = max(c1, c2) * 24; y = r1 * 24 + 7
            wall[y:y + 10, x - 2:x + 2] = False
        else:
            y = max(r1, r2) * 24; x = c1 * 24 + 7
            wall[y - 2:y + 2, x:x + 10] = False
    wall &= p.tone >= 0
    p.mat[wall] = "wall"; p.tone[wall] = 1
    def machine(x0, y0, x1, y1, mat="console", light=None, lmat="glow"):
        p.bevel(p.mask(rect=(x0, y0, x1, y1)), mat, width=1, face=3, shade_lower=False)
        if light:
            p.glow(p.mask(rect=light), lmat, 3)
    # engines: two engine cores feeding the pods
    for yy in (27, 51):
        machine(27, yy, 44, yy + 17, "metal", (30, yy + 6, 41, yy + 10), "glow")
        p.engrave([(35, yy + 1), (35, yy + 5)])
    # weapons: the guns' breech and a power coupling
    machine(51, 27, 68, 36, "console", (54, 29, 56, 30), "glow_red"); p.glow(p.mask(rect=(62, 29, 64, 30)), "glow_red", 3)
    machine(54, 39, 65, 44, "pipe")
    # drone bay: the drone's charging pad
    p.bevel(p.mask(ellipse=(52, 52, 67, 67)), "console", width=1, face=3, shade_lower=False)
    p.paint(p.mask(ellipse=(55, 55, 64, 64)), "yellow")
    # shields: a generator coil
    p.bevel(p.mask(ellipse=(76, 27, 91, 42)), "metal", width=1, face=3, shade_lower=False)
    p.dome(p.mask(ellipse=(79, 30, 88, 39)), "blue")
    # oxygen: a tank and pipes
    p.tube(p.mask(rect=(76, 52, 91, 66)), "blue", "x")
    p.engrave([(76, 59), (91, 59)])
    machine(73, 67, 92, 68, "pipe")
    # the cockpit: one seat facing the nose, a console under the canopy
    machine(136, 29, 141, 66, "console", (137, 33, 138, 62), "glow_teal")
    p.bevel(p.mask(rect=(112, 39, 123, 56)), "red", width=1, face=3, shade_lower=False)
    p.bevel(p.mask(rect=(124, 42, 128, 53)), "console", width=1, face=3, shade_lower=False)
    return p

if __name__ == "__main__":
    out = Path("/home/claude/work/ships/v3")
    h = hull().render(); i = interior(hull()).render()
    h.save(out / "hull_v4.png"); i.save(out / "interior_v4.png")
    v3 = Image.open(out / "hull.png")
    sheet = Image.new("RGBA", (168 * 3 * 3 + 40, 96 * 3 + 20), (20, 24, 36, 255))
    for k, im in enumerate((v3, h, i)):
        sheet.alpha_composite(im.resize((168 * 3, 96 * 3), Image.NEAREST), (10 + k * (168 * 3 + 10), 10))
    sheet.save(out / "compare_v4.png")
    print("ok")
