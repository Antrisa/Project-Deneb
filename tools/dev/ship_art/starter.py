"""The starter fighter (Claude, 21 Nov 2026; approved by Zachary). After the intro movie: plane wings with an orange
band, twin engine pods out behind, a teal canopy. Crisp pixel art with shading and depth (tools/dev/ship_art/pixkit.py).
Zachary: shorter at the back, a longer cockpit; behind the cockpit is out of reach for the player (a single-seat
fighter): the repair drone looks after the bays. Other ships are walkable all through.

Run from the repo root with -I:  python3 -I tools/dev/ship_art/starter.py .
Writes art/ships/starter/hull.png (thrusters lit), art/ships/starter/interior.png (the cut-away; the game draws the
hatches) and art/lunar/player_ship.png (4 repair stages for the Shuttle Bay, wrecked to repaired, engines off).
Rooms and hatches here must match ShipData.STARTER in scripts/ship_data.gd."""
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

def hull(lit=True):
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
        if not lit:
            break
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

# ---------------------------------------------------------------- the Shuttle Bay's repair stages

OUTLINE = (38, 37, 53, 255)


def _scorch(im, spots, seed):
    import random
    rng = random.Random(seed)
    px = im.load()
    for (cx, cy, r) in spots:
        for y in range(cy - r - 2, cy + r + 3):
            for x in range(cx - r - 2, cx + r + 3):
                if not (0 <= x < im.width and 0 <= y < im.height) or px[x, y][3] == 0:
                    continue
                dd = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 + rng.uniform(-1.2, 1.2)
                if dd < r * 0.55:
                    px[x, y] = (38, 37, 53, 255)
                elif dd < r:
                    px[x, y] = (90, 74, 72, 255)
                elif dd < r + 2:
                    c = px[x, y]
                    px[x, y] = (int(c[0] * 0.75), int(c[1] * 0.72), int(c[2] * 0.72), 255)


def _primer(im, mask_pts):
    """Panels replaced but not painted yet: grey primer that keeps the shading."""
    from PIL import ImageDraw
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).polygon(mask_pts, fill=255)
    px, mp = im.load(), m.load()
    for y in range(im.height):
        for x in range(im.width):
            if mp[x, y] and px[x, y][3] and px[x, y][:3] != OUTLINE[:3]:
                c = px[x, y]
                lum = (c[0] + c[1] + c[2]) / 765
                g = int(110 + 90 * lum)
                px[x, y] = (g, g - 4, g + 6, 255)


def _cut(im, pts):
    """Cut a piece off, then redraw the outline along the cut."""
    from PIL import ImageDraw
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    a = np.array(im)
    cut = np.array(m) > 0
    a[cut] = 0
    solid = (a[:, :, 3] > 0) & ~np.all(a[:, :, :3] == OUTLINE[:3], axis=2)
    keep = ndimage.binary_dilation(solid, structure=np.ones((3, 3)))
    a[~keep] = 0
    ring = ndimage.binary_dilation(a[:, :, 3] > 0, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]]) & (a[:, :, 3] == 0)
    a[ring] = OUTLINE
    return Image.fromarray(a, "RGBA").copy()


def stages():
    clean = hull(lit=False).render()
    s3 = clean.copy()
    s2 = clean.copy()
    _primer(s2, [tuple(p) for p in my(WING)])                   # a new lower wing, not painted yet
    _scorch(s2, [(34, 33, 3)], 2)
    s1 = clean.copy()
    _primer(s1, [tuple(p) for p in my(WING)])
    _primer(s1, [(10, 50), (46, 50), (46, 70), (10, 70)])       # the lower pod rebuilt
    _scorch(s1, [(34, 33, 4), (78, 40, 3), (112, 60, 3)], 3)
    s0 = _cut(clean.copy(), [(38, 75), (92, 75), (70, 95), (34, 95)])     # the lower wing snapped off
    s0 = _cut(s0, [(0, 49), (24, 49), (24, 71), (0, 71)])                 # the lower pod's back end gone
    _scorch(s0, [(34, 33, 5), (62, 58, 6), (86, 36, 4), (112, 56, 4), (150, 46, 3), (30, 60, 4)], 4)
    px = s0.load()
    for (x, y) in [(110, 40), (111, 41), (112, 42), (113, 43), (114, 44), (115, 45), (116, 46), (117, 47), (114, 41), (116, 40)]:
        px[x, y] = (216, 244, 244, 255)                          # a crack across the canopy
    sheet = Image.new("RGBA", (W * 4, H), (0, 0, 0, 0))
    for k, st in enumerate((s0, s1, s2, s3)):
        sheet.alpha_composite(st, (k * W, 0))
    return sheet


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    out = root / "art/ships/starter"
    out.mkdir(parents=True, exist_ok=True)
    hull().render().save(out / "hull.png")
    interior(hull()).render().save(out / "interior.png")
    stages().save(root / "art/lunar/player_ship.png")
    print("ok")
