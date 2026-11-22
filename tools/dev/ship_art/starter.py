"""The starter fighter, redrawn after the intro movie (Claude, 21 Nov 2026): plane wings with an orange band, a teal
bubble canopy near the nose, twin engine pods sticking out behind, cream hull with orange chevrons. Top-down, nose
right, 7 x 4 cells (168 x 96). Zachary: Claude draws the ships, he touches them up.

Run from the repo root with -I:  python3 -I tools/dev/ship_art/starter.py .
Writes art/ships/starter/hull.png (with thruster glow), art/ships/starter/interior.png (the cut-away; the game
draws the doors) and art/lunar/player_ship.png (4 repair stages for the Shuttle Bay, wrecked to repaired)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ship_kit import *

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
W, H = 7 * CELL, 4 * CELL      # 168 x 96
P = {
    "lite": "#f5ebde", "mid": "#e2d4c7", "shade": "#c6b8ae", "dark": "#a99b94",
    "pod": "#958e95", "pod_lite": "#aaa3aa", "pod_dark": "#7a7480",
    "orange": "#fb7412", "orange_dk": "#c4560e",
    "teal": "#2a9aa6", "teal_lite": "#86dde0", "teal_dk": "#1b5f6b",
    "vent": "#3a3848", "glow": "#ffb04a", "glow_hot": "#fff0c0",
}

# ---- silhouette pieces (picture pixels)
# Zachary, 21 Nov: "in the art its got like regular plane wings and the thrusters go back behind the ship".
BODY = [(24, 22), (140, 22), (152, 30), (167, 45), (167, 50), (152, 65), (140, 73), (24, 73)]
WING_TOP = [(58, 23), (114, 23), (84, 2), (80, 0), (60, 0), (54, 2)]
WING_BOT = mirror_y(WING_TOP, H)
POD_TOP = (0, 26, 56, 45)      # the engine pods sit on the body's back corners and stick out behind it
POD_BOT = (0, 50, 56, 69)

def hull():
    im = canvas(7, 4)
    # wings: the upper one catches the light, the lower one is in shade
    poly(im, WING_TOP, P["lite"])
    poly(im, WING_BOT, P["mid"])
    FLAP = [(58, 23), (70, 23), (64, 3), (56, 3)]
    poly(im, FLAP, P["mid"]); poly(im, mirror_y(FLAP, H), P["shade"])
    BAND = [(84, 23), (96, 23), (76, 1), (70, 1)]
    poly(im, BAND, P["orange"]); poly(im, mirror_y(BAND, H), P["orange_dk"])
    # weapon hardpoints near the wing tips, pointing forward (the game draws the weapon over them)
    for y in (9, H - 1 - 9):
        rect(im, 74, y - 2, 92, y + 2, P["pod_dark"])
        rect(im, 76, y - 1, 90, y + 1, P["pod"])
    # the body: lit top half, shaded bottom half
    poly(im, BODY, P["mid"])
    poly(im, [(24, 22), (140, 22), (152, 30), (167, 45), (167, 47), (24, 47)], P["lite"])
    # orange chevrons across the back
    for x in (60, 80):
        poly(im, [(x, 23), (x + 8, 23), (x + 17, 47), (x + 9, 47)], P["orange"])
        poly(im, [(x + 9, 48), (x + 17, 48), (x + 8, 72), (x, 72)], P["orange_dk"])
    # panel lines and the dark vent grid on the spine
    line(im, [(50, 23), (50, 72)], P["shade"])
    line(im, [(112, 26), (112, 69)], P["shade"])
    for i in range(4):
        for j in range(2):
            rect(im, 98 + i * 4, 34 + j * 5, 100 + i * 4, 36 + j * 5, P["vent"])
    # twin engine pods, out behind the body
    for (x0, y0, x1, y1), lite in ((POD_TOP, True), (POD_BOT, False)):
        rect(im, x0 + 3, y0, x1, y1, P["pod_lite"] if lite else P["pod"])
        rect(im, x0 + 3, y0 + (y1 - y0) // 2 + 1, x1, y1, P["pod"] if lite else P["pod_dark"])
        rect(im, x0, y0 + 2, x0 + 5, y1 - 2, P["pod_dark"])        # the exhaust bell
        rect(im, x0 + 12, y0, x0 + 13, y1, P["pod_dark"])
        rect(im, x0 + 30, y0, x0 + 31, y1, P["pod_dark"])
        rect(im, x0 + 14, y0 + 3, x0 + 28, y0 + 5, P["orange"] if lite else P["orange_dk"])
    # canopy: a teal bubble near the nose
    ellipse(im, 116, 34, 150, 61, P["teal_dk"])
    ellipse(im, 118, 35, 149, 59, P["teal"])
    ellipse(im, 122, 37, 136, 45, P["teal_lite"])
    rect(im, 124, 38, 127, 39, "#e8fbfb")
    # nose tip
    poly(im, [(160, 41), (167, 45), (167, 50), (160, 54)], P["orange"])
    return outline(im)

def glow(im, frame=0):
    """Thruster glow at the pod backs (drawn outside the hull, to the left)."""
    g = layer(im.size)
    for (x0, y0, x1, y1) in (POD_TOP, POD_BOT):
        cy = (y0 + y1) // 2
        rect(g, x0 + 1, cy - 5, x0 + 4, cy + 5, P["glow"])
        rect(g, x0 + 1, cy - 2, x0 + 3, cy + 2, P["glow_hot"])
    return g

# ---- interior: FTL-style rooms on the grid (cells: col, row)
ROOMS = {
    "engines": {"cells": [(1, 1), (1, 2)], "label": "Engines", "sys": "engines"},
    "weapons": {"cells": [(2, 1), (3, 1)], "label": "Weapons", "sys": "weapons"},
    "drones": {"cells": [(2, 2)], "label": "Drone bay", "sys": "drones"},
    "life": {"cells": [(3, 2)], "label": "Oxygen", "sys": "life"},
    "shields": {"cells": [(4, 1), (4, 2)], "label": "Shields", "sys": "shields"},
    "cockpit": {"cells": [(5, 1), (5, 2)], "label": "Cockpit", "sys": "pilot"},
}
# doors between neighbouring cells of different rooms: ((col, row), (col, row))
DOORS = [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (2, 2)), ((3, 1), (3, 2)), ((3, 1), (4, 1)), ((3, 2), (4, 2)), ((4, 1), (5, 1))]
FLOOR = {"cockpit": "#d9d2c4", "default": "#8f8b9c"}

def room_of(cell):
    for rid, r in ROOMS.items():
        if cell in r["cells"]:
            return rid
    return None

def interior(base):
    im = base.copy()
    d = layer(im.size)
    for rid, r in ROOMS.items():
        for (c, rr) in r["cells"]:
            x0, y0 = c * CELL, rr * CELL
            rect(d, x0, y0, x0 + 23, y0 + 23, FLOOR.get(rid, FLOOR["default"]))
            # floor plates
            for k in (6, 12, 18):
                line(d, [(x0, y0 + k), (x0 + 23, y0 + k)], (0, 0, 0, 18) if rid == "cockpit" else (255, 255, 255, 18))
    # walls on every cell edge between different rooms, and round the outside of the rooms
    wall = (38, 37, 53, 255)
    for rid, r in ROOMS.items():
        for (c, rr) in r["cells"]:
            x0, y0 = c * CELL, rr * CELL
            for (dc, dr, edge) in ((1, 0, "e"), (-1, 0, "w"), (0, 1, "s"), (0, -1, "n")):
                if room_of((c + dc, rr + dr)) == rid:
                    continue
                if edge == "e": rect(d, x0 + 22, y0, x0 + 23, y0 + 23, wall)
                if edge == "w": rect(d, x0, y0, x0 + 1, y0 + 23, wall)
                if edge == "s": rect(d, x0, y0 + 22, x0 + 23, y0 + 23, wall)
                if edge == "n": rect(d, x0, y0, x0 + 23, y0 + 1, wall)
    # doors: a gap in the wall where each door sits; the game draws the door itself (open, closed or locked)
    for (a, b) in DOORS:
        (c1, r1), (c2, r2) = a, b
        if r1 == r2:
            x = max(c1, c2) * CELL
            y = r1 * CELL + 7
            rect(d, x - 2, y, x + 1, y + 9, FLOOR["default"])
        else:
            y = max(r1, r2) * CELL
            x = c1 * CELL + 7
            rect(d, x, y - 2, x + 9, y + 1, FLOOR["default"])
    # what's in each room
    cx = lambda c: c * CELL
    # engines: one engine core per pod
    for yy in (CELL + 6, 2 * CELL + 6):
        rect(d, cx(1) + 3, yy, cx(1) + 20, yy + 11, "#5d5868"); rect(d, cx(1) + 5, yy + 2, cx(1) + 18, yy + 9, "#7a7488"); rect(d, cx(1) + 7, yy + 4, cx(1) + 16, yy + 7, P["glow"])
    # weapons: a gun rack with two charging cells
    rect(d, cx(2) + 6, CELL + 5, cx(3) + 17, CELL + 10, "#5d5868")
    rect(d, cx(2) + 9, CELL + 6, cx(2) + 14, CELL + 9, "#e6463c"); rect(d, cx(3) + 9, CELL + 6, cx(3) + 14, CELL + 9, "#e6463c")
    # drone bay: charging pad
    ellipse(d, cx(2) + 5, 2 * CELL + 5, cx(2) + 18, 2 * CELL + 18, "#5d5868"); ellipse(d, cx(2) + 8, 2 * CELL + 8, cx(2) + 15, 2 * CELL + 15, "#f2c94c")
    # oxygen: a tank
    ellipse(d, cx(3) + 6, 2 * CELL + 5, cx(3) + 17, 2 * CELL + 16, "#5d5868"); ellipse(d, cx(3) + 8, 2 * CELL + 7, cx(3) + 15, 2 * CELL + 14, "#7fc8e8")
    # shields: generator
    ellipse(d, cx(4) + 4, CELL + 14, cx(4) + 19, CELL + 33, "#5d5868"); ellipse(d, cx(4) + 7, CELL + 18, cx(4) + 16, CELL + 29, "#5ab4ff")
    # cockpit: a seat facing the nose, a console, under the canopy
    rect(d, cx(5) + 4, CELL + 18, cx(5) + 12, CELL + 29, "#6a5e58"); rect(d, cx(5) + 16, CELL + 14, cx(5) + 19, CELL + 33, "#3a3848")
    rect(d, cx(5) + 17, CELL + 17, cx(5) + 18, CELL + 30, P["teal_lite"])
    im.alpha_composite(d)
    return im

def scorch(im, spots, seed):
    """Dark burn marks on the hull (opaque pixels only)."""
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
                    px[x, y] = hexc("#262535")
                elif dd < r:
                    px[x, y] = hexc("#5a4a48")
                elif dd < r + 2:
                    c = px[x, y]
                    px[x, y] = (int(c[0] * 0.75), int(c[1] * 0.72), int(c[2] * 0.72), 255)

def erase(im, pts):
    """Cut a piece off (wreck stages)."""
    m = layer(im.size)
    poly(m, pts, (255, 255, 255, 255))
    px, mp = im.load(), m.load()
    for y in range(im.height):
        for x in range(im.width):
            if mp[x, y][3]:
                px[x, y] = (0, 0, 0, 0)

def tidy_cut(im):
    """After a cut, drop outline pixels left floating where the piece was (outline() then redraws the edge)."""
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][:3] != OUTLINE[:3] or px[x, y][3] == 0:
                continue
            keep = False
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < im.width and 0 <= ny < im.height and px[nx, ny][3] and px[nx, ny][:3] != OUTLINE[:3]:
                        keep = True
            if not keep:
                px[x, y] = (0, 0, 0, 0)

def primer(im, pts, col="#a7a2a6"):
    """Repainted panels still in grey primer (repair stages)."""
    m = layer(im.size)
    poly(m, pts, (255, 255, 255, 255))
    px, mp = im.load(), m.load()
    base = hexc(col)
    for y in range(im.height):
        for x in range(im.width):
            if mp[x, y][3] and px[x, y][3]:
                c = px[x, y]
                if c[:3] != OUTLINE[:3]:
                    shade = (c[0] + c[1] + c[2]) / 3 / 255
                    px[x, y] = (int(base[0] * (0.7 + 0.35 * shade)), int(base[1] * (0.7 + 0.35 * shade)), int(base[2] * (0.7 + 0.35 * shade)), 255)

def stages():
    """The Shuttle Bay's four repair stages: wrecked, patched, nearly there, repaired."""
    clean = hull()
    s3 = clean.copy()
    s2 = clean.copy()
    primer(s2, mirror_y(WING_TOP, H))                       # a new lower wing, not painted yet
    scorch(s2, [(40, 32, 3)], 2)
    s1 = clean.copy()
    primer(s1, mirror_y(WING_TOP, H))
    primer(s1, [(0, 50), (56, 50), (56, 70), (0, 70)])       # the lower pod rebuilt in primer
    scorch(s1, [(40, 32, 4), (88, 40, 3), (130, 60, 3)], 3)
    s0 = clean.copy()
    erase(s0, [(58, 75), (114, 75), (88, 95), (52, 95)])     # the lower wing snapped off at the root
    erase(s0, [(0, 50), (24, 50), (24, 70), (0, 70)])         # the lower pod's back end is gone
    tidy_cut(s0)
    s0 = outline(s0)
    scorch(s0, [(40, 32, 5), (70, 58, 6), (96, 36, 4), (128, 56, 4), (150, 46, 3), (30, 60, 4)], 4)
    px = s0.load()                                            # a crack across the canopy
    for (x, y) in [(124, 41), (125, 42), (126, 43), (127, 44), (128, 45), (129, 46), (130, 47), (131, 48), (132, 49), (128, 42), (130, 41)]:
        px[x, y] = hexc("#d8f4f4")
    sheet = Image.new("RGBA", (W * 4, H), (0, 0, 0, 0))
    for i, st in enumerate((s0, s1, s2, s3)):
        sheet.alpha_composite(st, (i * W, 0))
    return sheet

if __name__ == "__main__":
    h = hull()
    full = layer(h.size); full.alpha_composite(h); full.alpha_composite(glow(h))
    out = ROOT / "art/ships/starter"
    out.mkdir(parents=True, exist_ok=True)
    full.save(out / "hull.png")
    interior(full).save(out / "interior.png")
    stages().save(ROOT / "art/lunar/player_ship.png")
    print("ok", h.size)
