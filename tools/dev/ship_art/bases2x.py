"""Pirate bases and pirate repaints at double resolution, 48 px per cell (Claude, 21 Nov 2026).

  pirate_stronghold   8 x 6: a small asteroid base with turrets (the smaller strongholds after the Nest)
  rabble_nest         10 x 6: the Rabble's main asteroid base, the one-time raid
  piratize2x()        any culture ship, haphazardly repainted by the Rabble (Zachary: "other pirate ships are other
                      cultures' ships like haphazardly repainted with pirate stuff")

Run from the repo root:  python3 -I tools/dev/ship_art/bases2x.py <out dir>
"""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from scipy import ndimage
from pixkit import Pix
from kit2x import (S, mirror, grid, rivet_row, rivet_col, plate, hazard, windows, lit_windows, thruster, nozzle,
                   turret, light, skull, stencil, wear, scorch, cable, sheet)
from story2x import big_skull
import kit2x


def light(p, x, y, mat="glow_red", size=2):
    if 0 <= y < p.h and 0 <= x < p.w and p.tone[y, x] >= 0:
        kit2x.light(p, x, y, mat, size)


def raider(p, x, y, flip=False):
    """A small docked Rabble raider, nose right."""
    body = [(x, y), (x + 40, y - 4), (x + 58, y + 6), (x + 40, y + 16), (x, y + 12)]
    p.bevel(p.mask(polygon=body), "rust", width=2, face=4, shade_lower=False)
    for fy, d in ((y - 1, -1), (y + 13, 1)):
        p.bevel(p.mask(polygon=[(x + 6, fy), (x + 24, fy), (x + 14, fy + 10 * d)]), "gunmetal", width=1, face=4 if d < 0 else 3, shade_lower=False)
    p.paint(p.mask(rect=(x + 2, y + 5, x + 44, y + 7)), "banner")
    p.dome(p.mask(ellipse=(x + 36, y + 1, x + 46, y + 11)), "red")
    p.bevel(p.mask(polygon=[(x + 54, y + 3), (x + 62, y + 6), (x + 54, y + 9)]), "silver", width=1, face=4, shade_lower=False)
    p.tube(p.mask(rect=(x - 4, y + 2, x + 2, y + 10)), "dark", "x", shadow=False)
    for k in range(3):
        p.rivet(x + 10 + k * 9, y + 2)

GLOWS = ["glow", "glow_red", "glow_green", "glow_teal", "glow_yellow", "glow_blue"]


# ---------------------------------------------------------------- rock

def asteroid(p, cx, cy, rx, ry, seed, lumps=7):
    """An irregular rock: a bevelled blob with craters and cracks."""
    rng = np.random.default_rng(seed)
    ang = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    k = np.arange(1, lumps)
    amp = rng.uniform(0.02, 0.09, len(k)) / k ** 0.4
    ph = rng.uniform(0, 2 * np.pi, len(k))
    r = 1 + (amp[None, :] * np.sin(k[None, :] * ang[:, None] + ph[None, :])).sum(1)
    pts = [(cx + rx * r[i] * np.cos(a), cy + ry * r[i] * np.sin(a)) for i, a in enumerate(ang)]
    m = p.mask(polygon=pts)
    p.bevel(m, "rock", width=8, face=3, edge_light=5)
    # mottling
    nz = ndimage.gaussian_filter(rng.random((p.h, p.w)), 6)
    inner = m & (ndimage.distance_transform_edt(m) > 8)
    p.shade(inner & (nz > np.quantile(nz[m], 0.86)), 1)
    p.shade(inner & (nz < np.quantile(nz[m], 0.1)), -1)
    for _ in range(int(rx * ry / 900)):
        x, y = int(rng.integers(cx - rx * 0.8, cx + rx * 0.8)), int(rng.integers(cy - ry * 0.8, cy + ry * 0.8))
        if inner[y, x]:
            q = int(rng.integers(2, 5))
            p.bevel(p.mask(ellipse=(x, y, x + q + 2, y + q)) & inner, "rock", width=1, face=4, shade_lower=False)
    return m


def crater(p, cx, cy, r):
    yy, xx = grid(p)
    inside = ((xx - cx) ** 2 + ((yy - cy) * 1.3) ** 2) < r * r
    inside &= p.mat == "rock"
    p.shade(inside, -1)
    p.shade(inside & (((xx - cx) ** 2 + ((yy - cy) * 1.3) ** 2) < (r * 0.6) ** 2), -1)
    # shadow on the top-left inner wall, a lit rim on the bottom right
    wall = inside & (((xx - cx + 2) ** 2 + ((yy - cy + 2) * 1.3) ** 2) >= (r - 2) ** 2) & (xx + yy < cx + cy)
    p.shade(wall, -1)
    rim = ~inside & (((xx - cx) ** 2 + ((yy - cy) * 1.3) ** 2) < (r + 2) ** 2) & (xx + yy > cx + cy) & (p.mat == "rock")
    p.shade(rim, 1)


def crack(p, pts):
    p.engrave(pts, highlight=True)


def dome_hab(p, cx, cy, r, glass="red", mat="gunmetal"):
    p.bevel(p.mask(ellipse=(cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4)), mat, width=3, face=4, shade_lower=False)
    p.dome(p.mask(ellipse=(cx - r, cy - r, cx + r, cy + r)), glass)
    for a in range(10):
        an = a * np.pi / 5
        p.rivet(int(cx + (r + 2) * np.cos(an)), int(cy + (r + 2) * np.sin(an)))


def pad(p, x0, y0, x1, y1):
    p.bevel(p.mask(rect=(x0, y0, x1, y1)), "gunmetal", width=3, face=4)
    hazard(p, p.mask(rect=(x0 + 3, y0 + 3, x1 - 3, y0 + 7)), step=4)
    hazard(p, p.mask(rect=(x0 + 3, y1 - 7, x1 - 3, y1 - 3)), step=4)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    p.paint(p.mask(ellipse=(cx - 12, cy - 12, cx + 12, cy + 12)) & ~p.mask(ellipse=(cx - 9, cy - 9, cx + 9, cy + 9)), "yellow")
    for (x, y) in ((x0 + 5, y0 + 11), (x1 - 7, y0 + 11), (x0 + 5, y1 - 13), (x1 - 7, y1 - 13)):
        light(p, x, y, "glow_yellow")


def scaffold(p, x0, y0, x1, y1):
    for x in (x0, x1 - 3):
        p.bevel(p.mask(rect=(x, y0, x + 3, y1)), "metal", width=1, face=4, shade_lower=False)
    for y in range(y0, y1 - 6, 10):
        p.paint(p._line([(x0 + 2, y), (x1 - 2, y + 10)], width=1) & (p.tone >= 0), "metal")
        p.bevel(p.mask(rect=(x0, y, x1, y + 2)), "metal", width=1, face=4, shade_lower=False)


def mast_flag(p, x, y, length=30):
    p.paint(p.mask(rect=(x, y - 1, x + 2, y + 1)), "metal")
    flag = [(x, y), (x - length, y - 10), (x - length + 6, y), (x - length, y + 10), (x, y + 4)]
    p.bevel(p.mask(polygon=flag), "banner", width=2, face=3, shade_lower=False)
    p.dome(p.mask(ellipse=(x - 4, y - 4, x + 5, y + 5)), "gold", shadow=True)


# ---------------------------------------------------------------- the strongholds

def pirate_stronghold():
    p = Pix(384, 288)
    rng = random.Random(71)
    asteroid(p, 196, 146, 176, 128, seed=3)
    for (x, y, r) in ((90, 80, 16), (300, 210, 22), (70, 200, 12), (250, 60, 10), (330, 110, 9), (150, 236, 10)):
        crater(p, x, y, r)
    crack(p, [(40, 150), (80, 140), (110, 156)]); crack(p, [(290, 40), (300, 70), (284, 92)])
    # a walled compound on top of the rock
    wall = p.mask(rect=(110, 92, 290, 200))
    p.bevel(wall, "gunmetal", width=4, face=3)
    p.bevel(p.mask(rect=(122, 104, 278, 188)), "rust", width=3, face=4)
    for (r, mat) in (((128, 110, 190, 146), "gunmetal"), ((196, 110, 272, 146), "metal"), ((128, 152, 200, 182), "metal")):
        plate(p, r, mat, face=4, seams=1)
    dome_hab(p, 236, 166, 14)
    lit_windows(p, 136, 122, 5, 10, mat="glow_red"); lit_windows(p, 204, 124, 6, 10, mat="glow_yellow")
    big_skull(p, 150, 156)
    # turrets on the corners of the wall
    for (cx, cy) in ((110, 92), (290, 92), (110, 200), (290, 200)):
        turret(p, cx, cy, r=15, length=34, barrels=False)
    # a landing pad and scaffolding on the rock's edge, a mast with the flag
    pad(p, 300, 120, 352, 172)
    scaffold(p, 52, 108, 84, 180)
    cable(p, 84, 110, 140)
    mast_flag(p, 200, 72)
    dome_hab(p, 70, 220, 10, glass="glass")
    p.bevel(p.mask(ellipse=(300, 210, 330, 240)), "metal", width=2, face=4, shade_lower=False)
    p.dome(p.mask(ellipse=(306, 216, 324, 234)), "white")
    p.engrave([(315, 225), (334, 208)], highlight=False)
    for y in (220, 234):
        p.tube(p.mask(rect=(110, y, 160, y + 10)), "metal", "x")
        p.paint(p.mask(rect=(132, y, 136, y + 10)), "yellow")
    cable(p, 160, 236, 228)
    for (x, y) in ((40, 120), (350, 60), (360, 220), (60, 250)):
        light(p, x, y, "glow_red")
    wear(p, rng, rust=10, grime=0.02, mats=("gunmetal", "metal"), scuffs=10)
    return p


def rabble_nest():
    """The Rabble's main base: a big asteroid with a hangar mouth, a fortress tower, three turret nests, docked
    ships, junk, banners and lights everywhere."""
    p = Pix(480, 288)
    rng = random.Random(81)
    asteroid(p, 236, 146, 214, 118, seed=9, lumps=9)
    asteroid(p, 440, 46, 34, 30, seed=4)
    asteroid(p, 448, 246, 26, 24, seed=5)
    for (x, y, r) in ((70, 90, 20), (120, 230, 14), (380, 220, 18), (330, 50, 12), (40, 170, 10), (210, 262, 9), (420, 140, 10)):
        crater(p, x, y, r)
    crack(p, [(30, 130), (60, 120), (90, 134), (110, 128)]); crack(p, [(360, 30), (370, 60), (350, 80)])
    # the hangar mouth: a dark cave with docking lights and a ship parked inside
    mouth = p.mask(ellipse=(330, 112, 420, 180))
    p.bevel(mouth, "dark", width=4, face=1, edge_light=2, edge_dark=0, shade_lower=False)
    p.bevel(p.mask(ellipse=(318, 104, 432, 188)) & ~mouth, "gunmetal", width=3, face=4, shade_lower=False)
    for a in range(12):
        an = a * np.pi / 6
        light(p, int(375 + 52 * np.cos(an)), int(146 + 38 * np.sin(an)), "glow_yellow" if a % 2 else "glow_red")
    raider(p, 346, 140)
    # the fortress: stacked boxes with a command tower
    p.bevel(p.mask(rect=(130, 80, 300, 212)), "gunmetal", width=5, face=3)
    for (r, mat) in (((142, 92, 214, 140), "rust"), ((220, 92, 290, 136), "metal"), ((142, 146, 210, 200), "metal"),
                     ((216, 142, 290, 200), "rust")):
        plate(p, r, mat, face=4, seams=1)
    p.bevel(p.mask(rect=(186, 118, 246, 174)), "gunmetal", width=4, face=4)
    p.bevel(p.mask(rect=(196, 128, 236, 164)), "metal", width=3, face=4)
    lit_windows(p, 200, 134, 4, 9, mat="glow_red"); lit_windows(p, 200, 154, 4, 9, mat="glow_red")
    big_skull(p, 154, 160)
    for i in range(3):
        p.slot(228, 100 + i * 6, 282, 101 + i * 6)
    hazard(p, p.mask(rect=(130, 212, 300, 220)), step=5)
    # turret nests
    for (cx, cy) in ((130, 80), (300, 80), (130, 212), (300, 212), (60, 140)):
        p.bevel(p.mask(ellipse=(cx - 22, cy - 22, cx + 22, cy + 22)), "gunmetal", width=3, face=4, shade_lower=False)
        turret(p, cx, cy, r=15, length=36, barrels=False)
    # docked raiders, pipes, junk piles, masts
    for (x, y) in ((44, 66), (70, 220), (176, 234)):
        raider(p, x, y)
    dome_hab(p, 340, 70, 12)
    dome_hab(p, 100, 196, 9, glass="glass")
    scaffold(p, 316, 196, 346, 246)
    cable(p, 96, 130, 66); cable(p, 300, 330, 150)
    for _ in range(10):
        x, y = rng.randint(70, 120), rng.randint(110, 196)
        if p.mat[y, x] == "rock":
            p.bevel(p.mask(rect=(x, y, x + rng.randint(5, 10), y + rng.randint(4, 8))), rng.choice(["rust", "metal", "crate_red"]), width=1, face=4, shade_lower=False)
    mast_flag(p, 214, 72, 36); mast_flag(p, 300, 236, 28); mast_flag(p, 440, 24, 24)
    for (x, y) in ((24, 110), (460, 140), (250, 20), (250, 272), (400, 260)):
        light(p, x, y, "glow_red")
    wear(p, rng, rust=16, grime=0.02, mats=("gunmetal", "metal"), scuffs=18)
    return p


# Rooms, doors and gun mounts for the game (as fleet2x.INSIDES): the stations' rooms sit inside the fortress walls,
# their guns go on the turret rings (front ones first). scripts/ship_data.gd ENEMIES must match.
INSIDES = {
    "pirate_stronghold": (
        {"shields": (3, 2, 1, 1, "shields"), "life": (3, 3, 1, 1, "life"), "crew": (4, 2, 1, 2, ""),
         "weapons": (5, 2, 1, 1, "weapons"), "pilot": (5, 3, 1, 1, "pilot")},
        [((3, 2), (4, 2)), ((3, 3), (4, 3)), ((4, 2), (5, 2)), ((4, 3), (5, 3))],
        [(147, 41), (147, 103), (57, 40), (57, 104)],
    ),
    "rabble_nest": (
        {"shields": (3, 2, 1, 1, "shields"), "life": (3, 3, 1, 1, "life"), "crew": (4, 2, 1, 2, ""),
         "weapons": (5, 2, 1, 1, "weapons"), "pilot": (5, 3, 1, 1, "pilot"), "dock": (6, 2, 1, 2, ""),
         "hangar": (7, 2, 2, 2, "")},
        [((3, 2), (4, 2)), ((3, 3), (4, 3)), ((4, 2), (5, 2)), ((4, 3), (5, 3)), ((5, 2), (6, 2)), ((6, 2), (7, 2))],
        [(152, 40), (152, 104), (67, 40), (67, 106), (30, 70)],
    ),
}


# ---------------------------------------------------------------- Rabble repaints of any ship

PIRATE_SWAPS = {
    "terran_patrol": {"trim_blue": "banner", "orange": "dark"},
    "zaash_skiff": {"bronze": "rust", "gold": "silver"},
    "vuultam_garden": {"petal": "banner", "leafglass": "glass"},
    "moogli_trader": {"crate_green": "banner", "crate_blue": "gunmetal", "crate_violet": "rust"},
    "ervani_courier": {"fur": "bone", "glass": "red"},
    "scyldar_lantern": {"coral": "banner"},
    "arachnay_weaver": {"silver": "rust", "glow_teal": "glow_red"},
    "collective_freighter": {"seafoam": "gunmetal", "olive": "rust"},
}


def piratize2x(src, seed=1, swaps=None):
    p = src.copy()
    rng = random.Random(seed)
    W, H = p.w, p.h
    solid = p.tone >= 0
    for a, b in (swaps or {}).items():
        p.mat[(p.mat == a) & solid] = b
    hull = solid & ~np.isin(p.mat, GLOWS + ["dark", "glass", "leafglass"])
    ys, xs = np.nonzero(hull)
    x_lo, x_hi, y_lo, y_hi = xs.min(), xs.max(), ys.min(), ys.max()
    # slapped-on red paint: blotches, then rough brush strokes with drips
    for _ in range(3):
        x, y = rng.randint(x_lo + 20, x_hi - 60), rng.randint(y_lo + 20, y_hi - 40)
        m = p.mask(ellipse=(x, y, x + rng.randint(30, 50), y + rng.randint(18, 30))) & hull
        p.mat[m] = "banner"
    for _ in range(4):
        x0, y0 = rng.randint(x_lo + 20, x_hi - 70), rng.randint(y_lo + 30, y_hi - 30)
        dx, dy = rng.choice([(56, 18), (56, -18), (30, 44), (60, 4)])
        m = p._line([(x0, y0), (x0 + dx // 2, y0 + dy // 2 + rng.randint(-4, 4)), (x0 + dx, y0 + dy)], width=rng.randint(5, 8)) & hull
        p.mat[m] = "banner"
        for _ in range(4):
            t = rng.random()
            cx, cy = int(x0 + dx * t), int(y0 + dy * t) + 3
            p.mat[p.mask(rect=(cx, cy, cx + 1, cy + rng.randint(3, 8))) & hull] = "banner"
    # rust and scorches
    on = hull & np.isin(p.mat, ["white", "hull", "bone", "gold", "seafoam", "teal", "russet", "violet", "gunmetal", "metal", "navy", "olive", "fur"])
    yy, xx = grid(p)
    for _ in range(14):
        cx, cy, r = rng.randint(x_lo, x_hi), rng.randint(y_lo, y_hi), rng.randint(4, 9)
        blob = on & ((xx - cx) ** 2 + ((yy - cy) * 1.5) ** 2 < r * r)
        p.mat[blob] = "rust"; p.tone[blob] = np.clip(p.tone[blob] - 1, 1, 3)
    for _ in range(4):
        x, y = rng.randint(x_lo + 10, x_hi - 10), rng.randint(y_lo + 10, y_hi - 10)
        if hull[y, x]:
            scorch(p, x, y, rng.randint(4, 7))
    # welded plates
    for _ in range(5):
        x, y = rng.randint(x_lo + 10, x_hi - 40), rng.randint(y_lo + 10, y_hi - 30)
        w, h = rng.randint(18, 30), rng.randint(14, 20)
        m = p.mask(rect=(x, y, x + w, y + h)) & hull
        if m.sum() > 0.8 * (w + 1) * (h + 1):
            p.bevel(m, rng.choice(["gunmetal", "metal"]), width=2, face=3, shade_lower=False)
            for (rx, ry) in ((x + 2, y + 2), (x + w - 2, y + 2), (x + 2, y + h - 2), (x + w - 2, y + h - 2), (x + w // 2, y + 2), (x + w // 2, y + h - 2)):
                p.rivet(rx, ry)
    # spikes along the nose and the top and bottom edges
    for y in range(y_lo + 16, y_hi - 10, 18):
        row = np.nonzero(p.tone[y] >= 0)[0]
        if len(row) and row.max() + 14 < W:
            x = int(row.max())
            p.bevel(p.mask(polygon=[(x - 2, y - 4), (x + 12, y), (x - 2, y + 4)]), "silver", width=1, face=4, shade_lower=False)
    for x in range(x_lo + 40, x_hi - 40, 34):
        col = np.nonzero(p.tone[:, x] >= 0)[0]
        if len(col) and col.min() > 12:
            y = int(col.min())
            p.bevel(p.mask(polygon=[(x - 4, y + 2), (x, y - 10), (x + 4, y + 2)]), "silver", width=1, face=4, shade_lower=False)
        if len(col) and col.max() < H - 12:
            y = int(col.max())
            p.bevel(p.mask(polygon=[(x - 4, y - 2), (x, y + 10), (x + 4, y - 2)]), "silver", width=1, face=3, shade_lower=False)
    # the skull, painted big on the middle of the hull
    big_skull(p, int(xs.mean()) - 10, int(ys.mean()) - 24)
    return p


if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[1] == "--install":
    # python3 -I tools/dev/ship_art/bases2x.py --install <repo root>: art/ships/<id>/hull.png and interior.png
    from kit2x import interior, save_interior
    root = Path(sys.argv[2])
    for sid, fn in (("pirate_stronghold", pirate_stronghold), ("rabble_nest", rabble_nest)):
        rooms, doors, _mounts = INSIDES[sid]
        out = root / "art/ships" / sid
        out.mkdir(parents=True, exist_ok=True)
        fn().render().save(out / "hull.png")
        save_interior(interior(fn(), rooms, doors), out / "interior.png")
        print("installed", sid)
elif __name__ == "__main__":
    import fleet2x
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/bases2x")
    out.mkdir(parents=True, exist_ok=True)
    items = []
    for sid, fn in (("pirate_stronghold", pirate_stronghold), ("rabble_nest", rabble_nest)):
        p = fn()
        p.render().save(out / f"{sid}.png")
        items.append((sid, p))
    sheet(items, out / "bases_sheet.png", scale=2, cols=1)
    reps = []
    for sid, (fn, label) in fleet2x.SHIPS.items():
        q = piratize2x(fn(), seed=len(sid), swaps=PIRATE_SWAPS.get(sid))
        q.render().save(out / f"{sid}_rabble.png")
        reps.append((label.split(" (")[0] + ", Rabble repaint", q))
    sheet(reps, out / "repaints_sheet.png", scale=2, cols=2)
    print("ok")
