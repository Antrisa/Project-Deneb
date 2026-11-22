"""The starter fighter, v3 (Claude, 21 Nov 2026): crisp pixel art with shading, depth and detail (Zachary: the flat
version was better as pixel art, it just needed shading, depth and detail; the back was a little too long; keep the
interior simple like FTL). Draft for Zachary to check; the mock-up writes to the scratch folder."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixkit import Pix
import numpy as np
from scipy import ndimage
from PIL import Image

W, H = 168, 96
def my(pts): return [(x, H - 1 - y) for x, y in pts]
BODY = [(22, 22), (138, 22), (150, 30), (166, 45), (166, 50), (150, 65), (138, 73), (22, 73)]
WING = [(56, 24), (112, 24), (84, 3), (80, 1), (60, 1), (52, 4)]
BAND = [(82, 24), (94, 24), (74, 2), (68, 2)]
PODS = ((25, 45), (50, 70))
POD_X = (8, 50)
ROOMS = [(1, 1, 1, 2), (2, 1, 2, 1), (2, 2, 1, 1), (3, 2, 1, 1), (4, 1, 1, 2), (5, 1, 1, 2)]
DOORS = [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (2, 2)), ((3, 1), (3, 2)), ((3, 1), (4, 1)), ((3, 2), (4, 2)), ((4, 1), (5, 1))]

def hull():
    p = Pix(W, H)
    # wings: upper lit, lower in shade
    p.bevel(p.mask(polygon=WING), "hull", width=2, face=4, shade_lower=False)
    p.bevel(p.mask(polygon=my(WING)), "hull", width=2, face=3, edge_light=4, shade_lower=False)
    for pts in (BAND, my(BAND)):
        p.paint(p.mask(polygon=pts), "orange")
    for pts, up in ((WING, True), (my(WING), False)):
        p.engrave([(66, 24 if up else 71), (60, 4 if up else 91)])          # the flap line
    # the body
    p.bevel(p.mask(polygon=BODY), "hull", width=3, face=3, edge_light=5)
    # a raised spine plate down the middle: lighter, with its own bevel and a shadow off its lower edge
    p.bevel(p.mask(polygon=[(48, 29), (130, 29), (142, 37), (142, 58), (130, 66), (48, 66)]), "hull", width=2, face=4)
    for x in (60, 80):
        p.paint(p.mask(polygon=[(x, 22), (x + 8, 22), (x + 17, 47), (x + 9, 47)]), "orange")
        p.paint(p.mask(polygon=[(x + 9, 48), (x + 17, 48), (x + 8, 73), (x, 73)]), "orange")
    p.paint(p.mask(polygon=[(156, 38), (166, 45), (166, 50), (156, 57)]), "orange")
    p.engrave([(50, 25), (50, 70)]); p.engrave([(112, 25), (112, 70)]); p.engrave([(140, 27), (140, 68)])
    p.engrave([(25, 47), (49, 47)])
    p.engrave_rect(28, 51, 44, 64)                                          # a hatch on the back
    for i in range(3):
        p.slot(96, 32 + i * 4, 108, 33 + i * 4)
        p.slot(96, 55 + i * 4, 108, 56 + i * 4)
    for x in range(54, 110, 8):
        p.rivet(x, 26); p.rivet(x, 69)
    for y in (30, 40, 55, 65):
        p.rivet(116, y)
    # engine pods, out behind the body
    for (y0, y1) in PODS:
        m = p.mask(rect=(POD_X[0], y0, POD_X[1], y1))
        p.tube(m, "metal", "x")
        p.paint(p.mask(rect=(20, y0, 25, y1)), "orange")
        for x in (14, 34, 44):
            p.engrave([(x, y0 + 1), (x, y1 - 1)])
        p.slot(28, y0 + 4, 32, y0 + 5)
        # the exhaust bell
        p.tube(p.mask(rect=(POD_X[0], y0 + 2, POD_X[0] + 4, y1 - 2)), "dark", "x", shadow=False)
    # canopy: a metal frame and a glass bubble
    p.bevel(p.mask(ellipse=(114, 32, 152, 63)), "metal", width=2, face=3, shade_lower=False)
    p.dome(p.mask(ellipse=(117, 35, 149, 60)), "glass")
    # guns near the wing tips
    for y in (9, H - 1 - 9):
        p.tube(p.mask(rect=(70, y - 2, 94, y + 2)), "metal", "x", bands=(5, 4, 3, 2, 1))
        p.tube(p.mask(rect=(94, y - 1, 97, y + 1)), "dark", "x", shadow=False)
    # thruster glow, behind the pods
    for (y0, y1) in PODS:
        cy = (y0 + y1) / 2
        g = p.mask(ellipse=(1, cy - 7, 12, cy + 7)) & (np.mgrid[0:H, 0:W][1] < POD_X[0] + 1)
        p.glow(g, "glow", 2)
        p.glow(p.mask(ellipse=(3, cy - 4, 10, cy + 4)) & g, "glow", 3)
        p.glow(p.mask(ellipse=(5, cy - 2, 10, cy + 2)) & g, "glow", 4)
    # wing-tip lights
    p.glow(p.mask(rect=(62, 2, 64, 3)), "glow_green", 3)
    p.glow(p.mask(rect=(62, H - 4, 64, H - 3)), "glow_red", 3)
    return p

def interior(p):
    block = np.zeros((H, W), bool)
    for (cx, cy, cw, ch) in ROOMS:
        block[cy * 24:(cy + ch) * 24, cx * 24:(cx + cw) * 24] = True
    # the thick outer wall round the rooms, like FTL's
    frame = ndimage.binary_dilation(block, iterations=3) & ~block & (p.tone >= 0)
    p.mat[frame] = "wall"; p.tone[frame] = 3
    outer = frame & ~ndimage.binary_erosion(frame | block, iterations=1)
    p.tone[outer] = 1
    # floors: one tile per cell
    for (cx, cy, cw, ch) in ROOMS:
        x0, y0, x1, y1 = cx * 24, cy * 24, (cx + cw) * 24 - 1, (cy + ch) * 24 - 1
        m = p.mask(rect=(x0, y0, x1, y1))
        p.mat[m] = "cockpit_deck" if cx == 5 else "deck"
        p.tone[m] = 4
        p.lines[m] = False
        for k in range(cw):
            for j in range(ch):
                tx, ty = x0 + k * 24, y0 + j * 24
                p.set_tone(p.mask(rect=(tx, ty, tx + 23, ty)), 5)            # each tile's lit top edge
                p.set_tone(p.mask(rect=(tx, ty + 23, tx + 23, ty + 23)), 3)  # and its darker bottom
                p.set_tone(p.mask(rect=(tx + 23, ty, tx + 23, ty + 23)), 3)
    # walls between rooms: 2 px, dark, with gaps for the doors
    wall = np.zeros((H, W), bool)
    def room_at(cell):
        for i, (cx, cy, cw, ch) in enumerate(ROOMS):
            if cx <= cell[0] < cx + cw and cy <= cell[1] < cy + ch:
                return i
        return -1
    for i, (cx, cy, cw, ch) in enumerate(ROOMS):
        for x in range(cx, cx + cw):
            for y in range(cy, cy + ch):
                x0, y0 = x * 24, y * 24
                if room_at((x + 1, y)) != i: wall[y0:y0 + 24, x0 + 22:x0 + 24] = True
                if room_at((x - 1, y)) != i: wall[y0:y0 + 24, x0:x0 + 2] = True
                if room_at((x, y + 1)) != i: wall[y0 + 22:y0 + 24, x0:x0 + 24] = True
                if room_at((x, y - 1)) != i: wall[y0:y0 + 2, x0:x0 + 24] = True
    for (a, b) in DOORS:
        (c1, r1), (c2, r2) = a, b
        if r1 == r2:
            x = max(c1, c2) * 24; y = r1 * 24 + 7
            wall[y:y + 10, x - 2:x + 2] = False
        else:
            y = max(r1, r2) * 24; x = c1 * 24 + 7
            wall[y - 2:y + 2, x:x + 10] = False
    wall &= p.tone >= 0
    p.mat[wall] = "wall"; p.tone[wall] = 1
    # a few consoles against the walls (FTL keeps them small; the game draws the system icons)
    def console(x0, y0, x1, y1, screen=None, scol="screen"):
        p.bevel(p.mask(rect=(x0, y0, x1, y1)), "console", width=1, face=3, shade_lower=False, shadow=True)
        if screen:
            p.glow(p.mask(rect=screen), scol, 3)
    console(26, 26, 31, 45, (28, 29, 29, 42), "glow")            # engines
    console(26, 50, 31, 69, (28, 53, 29, 66), "glow")
    console(52, 26, 91, 30, None); p.glow(p.mask(rect=(56, 27, 60, 28)), "glow_red", 3); p.glow(p.mask(rect=(83, 27, 87, 28)), "glow_red", 3)
    p.bevel(p.mask(ellipse=(53, 53, 66, 66)), "console", width=1, face=3, shade_lower=False)          # drone pad
    p.paint(p.mask(ellipse=(56, 56, 63, 63)), "yellow")
    p.dome(p.mask(ellipse=(84, 59, 93, 68)), "blue")                                                 # oxygen tank
    console(113, 28, 117, 67, (114, 32, 115, 63), "glow_teal")                                         # shields panel
    console(137, 30, 141, 65, (138, 33, 139, 62), "glow_teal")                                         # flight console
    p.bevel(p.mask(rect=(124, 41, 131, 54)), "red", width=1, face=3, shade_lower=False)                # the seat
    return p

if __name__ == "__main__":
    out = Path("/home/claude/work/ships/v3")
    h = hull().render()
    i = interior(hull()).render()
    h.save(out / "hull.png"); i.save(out / "interior.png")
    old = Image.open("/home/claude/project-deneb/art/ships/starter/hull.png")
    ftl = Image.open("/mnt/user-data/uploads/b843a5f6-image.png").convert("RGBA").crop((60, 30, 690, 440))
    sheet = Image.new("RGBA", (168 * 3 * 3 + 40, 96 * 3 + 20), (20, 24, 36, 255))
    for k, im in enumerate((old, h, i)):
        sheet.alpha_composite(im.resize((168 * 3, 96 * 3), Image.NEAREST), (10 + k * (168 * 3 + 10), 10))
    sheet.save(out / "compare.png")
    print("ok")
