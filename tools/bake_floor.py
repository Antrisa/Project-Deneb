"""Bakes the promenade's floor picture (art/lunar/floor_main.png) ahead of time.

The game used to work this out pixel by pixel in GDScript (scripts/lunar_paving.gd) the first time you
entered the main level: about eleven million pixels, which is why loading the level took so long. The build now samples native 48px promenade textures.
scripts/lunar_paving.gd is retained as a legacy fallback when the baked picture is missing.

    python3 tools/bake_floor.py .            # bake from scripts/map_data.gd
"""
import json, math, os, re, sys
import numpy as np
from PIL import Image

CX_PX, CY_PX = 1848, 1528                      # fountain centre in world pixels (tile 115.5, 95.5)
COLORS = ["718899", "ded4bc", "b8c3b5", "c6a587", "adb990", "a8bfc0"]
ORIGINS = [(38, 76), (260, 4), (526, 20), (50, 263), (263, 263), (535, 280)]
SPANS = [(20, 20), (18, 18), (50, 50), (70, 12), (18, 18), (50, 50)]
HEX_PALETTE = ["718899", "7c92a2", "667e90", "8599a8", "6f8397", "788e9b"]
# Corner forecourts: squares 13 tiles across, centred on the four diagonal walks (see tools/concourse.py).
FORECOURTS = [(115.5 + sx * 35.0, 95.5 + sy * 35.0) for sx in (-1, 1) for sy in (-1, 1)]
FORECOURT_HALF = 6.5



# Pixels per tile in the baked pictures. 24 since the move to 24x48 characters (18 Nov): every baked floor and
# wall picture is 24 pixels a tile, and the game draws it into its 16-unit tiles at two-thirds scale, so one
# baked pixel is one art pixel like every other picture. Details still designed on the old 16-pixel grid
# (engineering's painted belts and pit) are worked out on that grid and
# spread over the new one, a pixel or two at a time; new floor textures (48x48 = 2x2 tiles) are used 1:1.
PX = 24


def _grid(H, W):
    """Pixel rows and columns of a PX-per-tile picture, and where each falls on the old 16-per-tile grid."""
    Y, X = np.mgrid[0:H, 0:W]
    return Y, X, (Y * 16) // PX, (X * 16) // PX


def _tex_lookup(tex, ys, xs):
    """Sample a floor or wall texture made at its own pixels per tile (48x48 = 24 a tile; old 64x64 = 32)."""
    per_tile = tex.shape[0] / 2.0
    ty = (ys * per_tile / PX).astype(np.int64) % tex.shape[0]
    tx = (xs * per_tile / PX).astype(np.int64) % tex.shape[1]
    return tex[ty, tx]

def hexc(h):
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float32)


def lighten(c, a):
    return c + (1.0 - c) * np.asarray(a, dtype=np.float32)[..., None]


def darken(c, a):
    return c * (1.0 - np.asarray(a, dtype=np.float32)[..., None])


def lerp(c, to, w):
    return c + (to - c) * np.float32(w)


def noise_at(x, y):
    x = x.astype(np.int64); y = y.astype(np.int64)
    return np.abs((x * 374761 + y * 668265) ^ (x * y * 31)) % 101


def roundi(v):
    return (np.sign(v) * np.floor(np.abs(v) + 0.5)).astype(np.int64)


class Baker:
    def __init__(self, art_dir):
        self.painted = np.asarray(Image.open(os.path.join(art_dir, "paving_painted.png")).convert("RGB"), dtype=np.float32) / 255.0
        self.stone = np.asarray(Image.open(os.path.join(art_dir, "garden_stone.png")).convert("RGB"), dtype=np.float32) / 255.0

    def texture_color(self, kind, x, y, base, seed):
        ox, oy = ORIGINS[kind]; sx, sy = SPANS[kind]
        ax = ox + np.mod(x + seed * 7, sx); ay = oy + np.mod(y + seed * 3, sy)
        return lerp(base, self.painted[ay, ax], 0.48)

    def brick(self, kind, x, y):
        width = [8, 11, 11, 13, 7, 11][kind]; height = [7, 6, 8, 4, 7, 8][kind]
        row = np.floor_divide(y, height)
        shifted = x + np.where(row % 2 == 1, width // 2, 0)
        col = np.floor_divide(shifted, width)
        seed = noise_at(col, row)
        variant = noise_at(col + 37, row - 19) % 3
        base = np.broadcast_to(hexc(COLORS[kind]), x.shape + (3,)).copy()
        base = darken(lighten(base, (seed % 7) * 0.009), (seed % 5) * 0.008)
        base = np.where((variant == 1)[..., None], lerp(base, hexc("a9b7b4"), 0.07), base)
        base = np.where((variant == 2)[..., None], lerp(base, hexc("bda482"), 0.07), base)
        base = self.texture_color(kind, x, y, base, seed)
        xx = np.mod(shifted, width); yy = np.mod(y, height)
        out = np.where((noise_at(x, y) > 97)[..., None], lighten(base, 0.035), base)
        # The rules below are in reverse order: in the GDScript the first one that matches wins.
        v2 = variant == 2
        out = np.where((v2 & (xx == 1) & (yy == height - 2))[..., None], darken(base, 0.24), out)
        out = np.where((v2 & (yy == 2 + seed % max(1, height - 4)) & (xx >= 3 + seed % 3) & (xx <= 6 + seed % 3))[..., None], darken(base, 0.085), out)
        v1 = variant == 1
        out = np.where((v1 & (xx == width - 3) & (yy == height - 3))[..., None], lerp(base, hexc("b9aa83"), 0.4), out)
        out = np.where((v1 & ((yy == 2) | (yy == height - 2)) & (xx > 2) & (xx < width - 2))[..., None], darken(base, 0.055), out)
        out = np.where(((xx == width - 1) & (seed % 3 == 0))[..., None], darken(base, 0.04), out)
        out = np.where((yy == 1)[..., None], lighten(base, 0.18), out)
        out = np.where(((xx == 0) | (yy == 0))[..., None], darken(base, 0.24), out)
        return out

    def stone_paver(self, x, y):
        cx = np.floor_divide(x, 32); cy = np.floor_divide(y, 32)
        variant = noise_at(cx, cy) % 3
        c = self.stone[np.mod(y, self.stone.shape[0]), np.mod(x, self.stone.shape[1])]
        c = np.where((variant == 1)[..., None], lighten(c, 0.025), c)
        return np.where((variant == 2)[..., None], darken(c, 0.025), c)

    def hex_paver(self, x, y):
        R = 6.0; xf = x.astype(np.float64); yf = y.astype(np.float64)
        q = (2.0 / 3.0 * xf) / R; r = (-xf / 3.0 + math.sqrt(3.0) * yf / 3.0) / R; s = -q - r
        iq, ir, iz = roundi(q), roundi(r), roundi(s)
        dq, dr, dz = np.abs(iq - q), np.abs(ir - r), np.abs(iz - s)
        a = (dq > dr) & (dq > dz); b = ~a & (dr > dz)
        iq = np.where(a, -ir - iz, iq); ir = np.where(b, -iq - iz, ir)
        lx = (xf - R * 1.5 * iq).astype(np.float32); ly = (yf - R * math.sqrt(3.0) * (ir + iq * 0.5)).astype(np.float32)
        edge = np.float32(R * 0.8660254) - np.maximum(np.abs(ly), np.abs(lx) * np.float32(0.8660254) + np.abs(ly) * np.float32(0.5))
        seed = noise_at(iq, ir); variant = noise_at(iq + 37, ir - 19) % 3
        pal = np.stack([hexc(h) for h in HEX_PALETTE])
        base = self.texture_color(0, x, y, pal[seed % 6], seed)
        out = np.where((noise_at(x, y) > 98)[..., None], lighten(base, 0.025), base)
        mx = (seed % 7 - 3).astype(np.float32); my = ((seed // 7) % 7 - 3).astype(np.float32)
        out = np.where(((variant == 2) & (np.abs(lx - mx) < 2.0) & (np.abs(ly - my) < 0.55))[..., None], darken(base, 0.085), out)
        stud = np.where((seed % 2 == 1)[..., None], hexc("9aaea5"), hexc("b9a475"))
        out = np.where(((variant == 1) & (np.abs(lx) < 1.6) & (ly > 3.0) & (ly < 4.5))[..., None], stud, out)
        out = np.where(((variant == 1) & (edge > 2.1) & (edge < 2.8))[..., None], darken(base, 0.13), out)
        out = np.where((edge < 1.35)[..., None], np.where((ly < 0)[..., None], lighten(base, 0.23), darken(base, 0.18)), out)
        return np.where((edge < 0.65)[..., None], hexc("364957"), out)

    def swatch(self, kind, x, y):
        out = np.zeros(x.shape + (3,), dtype=np.float32)
        for k in range(6):
            m = kind == k
            if not m.any():
                continue
            xs, ys = x[m], y[m]
            out[m] = self.hex_paver(xs, ys) if k == 0 else self.stone_paver(xs, ys) if k == 4 else self.brick(k, xs, ys)
        return out


def court_inset(px, py, side):
    dx = (px - 115.5) * side; dy = (py - 95.5) * side
    r = np.hypot(dx, dy)
    return np.minimum(np.minimum(r - 14.0, 24.5 - r), np.minimum(-dx - 3.25, (dx - dy) * 0.70710678 - 3.25))


FORECOURT_ROUND = 5.5        # outer corner rounded, except the mess hall's (north-east)


def forecourt_inset(px, py):
    out = np.full(px.shape, -1e9, dtype=np.float32)
    for fx, fy in FORECOURTS:
        inset = np.minimum(FORECOURT_HALF - np.abs(px - fx), FORECOURT_HALF - np.abs(py - fy))
        if not (fx > 115.5 and fy < 95.5):
            qx = (px - fx) * (1 if fx > 115.5 else -1); qy = (py - fy) * (1 if fy > 95.5 else -1)
            c = FORECOURT_HALF - FORECOURT_ROUND
            corner = (qx > c) & (qy > c)
            inset = np.where(corner, np.minimum(inset, FORECOURT_ROUND - np.hypot(qx - c, qy - c)), inset)
        out = np.maximum(out, inset)
    return out


def in_polygon(px, py, pts):
    inside = np.zeros(px.shape, dtype=bool); j = len(pts) - 1
    for i, (ax, ay) in enumerate(pts):
        bx, by = pts[j]
        with np.errstate(divide="ignore", invalid="ignore"):
            cross = ((ay > py) != (by > py)) & (px < (bx - ax) * (py - ay) / (by - ay) + ax)
        inside ^= cross; j = i
    return inside


PROMENADE_MATERIALS = (
    ("plaza_hex", "plaza_hex_plug", "plaza_hex_repair"),
    ("fountain_walk", "fountain_walk_grip", "fountain_walk_plate"),
    ("ring_sage", "ring_sage_brass_dash", "ring_sage_replacement"),
    ("station_deck", "station_deck_a", "station_deck_b"),
    ("garden_stone", "garden_stone_moss", "garden_stone_mineral"),
    ("games_slab", "games_slab_pegs", "games_slab_course_marks"),
)


def bake(rows, art_dir, style="new", strip=128):
    if style == "v11":
        baker = Baker(art_dir)
    else:
        tiles = np.array([
            [np.asarray(Image.open(os.path.join(art_dir, "promenade", name + ".png")).convert("RGB"))
             for name in family]
            for family in PROMENADE_MATERIALS
        ])
        if tiles.shape != (6, 3, 2 * PX, 2 * PX, 3):
            raise ValueError("Promenade materials must be 48x48 RGB tiles")
    H, W = len(rows) * PX, len(rows[0]) * PX
    if style != "v11":
        rows = wall_border_chars(rows)
    chars = np.array([[ord(c) for c in row] for row in rows], dtype=np.int32)
    img = np.zeros((H, W, 4), dtype=np.uint8)
    smooth = lambda t: t * t * (3 - 2 * t)
    for y0 in range(0, H, strip):
        Yn, Xn = np.mgrid[y0:min(H, y0 + strip), 0:W]
        ch = chars[Yn // PX, Xn // PX]
        draw = ~np.isin(ch, [ord(c) for c in "#Wz~"])
        if not draw.any():
            continue
        Yn, Xn, ch = Yn[draw], Xn[draw], ch[draw]
        if style == "v11":
            y, x = (Yn * 16) // PX, (Xn * 16) // PX
        else:
            # Distances below are world units; sample geometry at each native pixel centre.
            y = (Yn + 0.5) * (16.0 / PX) - 1.0
            x = (Xn + 0.5) * (16.0 / PX) - 1.0
        dxp = (x + 1 - CX_PX).astype(np.float32); dyp = (y + 1 - CY_PX).astype(np.float32)
        radius = np.hypot(dxp, dyp)
        spoke = np.minimum(np.minimum(np.abs(dxp), np.abs(dyp)), np.minimum(np.abs(dxp - dyp), np.abs(dxp + dyp)) * np.float32(0.70710678))
        route = np.where(radius < 480, np.minimum(spoke, np.abs(radius - 152) + 20), spoke)
        kind = np.where((ch == ord("a")) | (radius > 490), 2, 0)
        # weights(): bilinear share of p / h / u tiles round the pixel
        gx = (x + 1) / 16.0 - 0.5; gy = (y + 1) / 16.0 - 0.5
        tx = np.floor(gx).astype(np.int64); ty = np.floor(gy).astype(np.int64)
        fx = smooth(gx - tx); fy = smooth(gy - ty)
        wp = np.zeros(x.shape); wh = np.zeros(x.shape); wu = np.zeros(x.shape)
        for ddy in (0, 1):
            for ddx in (0, 1):
                cy_, cx_ = ty + ddy, tx + ddx
                ok = (cy_ >= 0) & (cy_ < len(rows)) & (cx_ >= 0) & (cx_ < len(rows[0]))
                c = np.where(ok, chars[np.clip(cy_, 0, len(rows) - 1), np.clip(cx_, 0, len(rows[0]) - 1)], 0)
                w = (fx if ddx else 1 - fx) * (fy if ddy else 1 - fy)
                wp += np.where(c == ord("p"), w, 0); wh += np.where(c == ord("h"), w, 0); wu += np.where(c == ord("u"), w, 0)
        px = (x + 1) / 16.0; py = (y + 1) / 16.0
        if style == "v11":
            court = np.full(x.shape, -1.0)
            wh = in_polygon(px, py, [(99, 72), (101, 70), (110, 70), (110, 81), (108, 83), (105, 80), (99, 74)]).astype(float)
            games = (px > 115) & (py > 100)
            wu = np.where(games, in_polygon(px, py, [(118, 112), (120, 110), (125, 110), (130, 115), (130, 119), (120, 119), (118, 117)]).astype(float), wu)
            fore = np.full(x.shape, -1.0)
        else:
            g1 = court_inset(px, py, 1.0); g2 = court_inset(px, py, -1.0)
            court = np.maximum(g1, g2)
            wh = np.where(g1 > 0, 1.0, 0.0)
            wu = np.where(g2 > 0, 1.0, np.where(px > 70.0, 0.0, wu))
            fore = forecourt_inset(px, py)
        # The porches in front of the doors used to be rounded pockets of their own paving (they looked like
        # stray arches on the floor); now they are paved like the walks (Zachary, 22 Nov: no circles).
        porch = wp > 0.5
        wp = np.zeros_like(wp)
        pocket = np.maximum(wp, np.maximum(wh, wu))
        kind = np.where(pocket > 0.5, np.where(wp == pocket, 3, np.where(wh == pocket, 4, 5)), kind)
        on_route = (radius < 174) | ((route < 40) & ((radius < 480) | (ch == ord(".")) | (ch == ord("a"))))
        on_route |= fore > 0                                   # forecourts are paved like the walks
        if style != "v11": on_route |= porch
        kind = np.where(on_route, 1, kind)
        if style == "v11":
            color = baker.swatch(kind, x, y)
        else:
            span = 2 * PX
            seed = noise_at(Xn // span, Yn // span)
            variant = (seed >= 75).astype(int) + (seed >= 88)
            color = tiles[kind, variant, Yn % span, Xn % span].astype(np.float32) / 255.0
        edge_band = on_route & (route > 36) & (radius >= 170) & ~(fore > 0)
        color = np.where(edge_band[..., None], np.where((route > 38)[..., None], hexc("a99579"), hexc("f1dfbc")), color)
        b = (wp > 0.39) & (wp < 0.61) & (route > 44)
        color = np.where(b[..., None], np.where((pocket < 0.49)[..., None], hexc("928d7a"), hexc("e6d6b6")), color)
        b = (court > 0) & (court < 0.125)
        color = np.where(b[..., None], np.where((court < 0.0625)[..., None], hexc("8f8a78"), hexc("e6d6b6")), color)
        # Forecourt border: the same two pixels, left open where a walk runs into it.
        b = (fore > 0) & (fore < 0.125) & (route > 40)
        color = np.where(b[..., None], np.where((fore < 0.0625)[..., None], hexc("a99579"), hexc("f1dfbc")), color)
        b = on_route & (route < 3) & (np.floor(radius).astype(np.int64) % 96 < 4) & (radius > 175)
        color = np.where(b[..., None], hexc("c7ad70"), color)
        if style != "v11":
            # The walks and forecourts sit a little proud of the plaza: a soft shadow falls off their edges.
            off = ~on_route
            ds = np.where(radius < 480, np.minimum(np.where(radius >= 174, route - 40, 99), np.maximum(radius - 174, 0) + 99 * (radius < 174)), route - 40)
            ds = np.minimum(ds, np.where(fore > -9, -fore * 16, 99))
            k = np.clip(1 - ds / 8.0, 0, 1) * off
            color = color * (1 - .2 * k[..., None] ** 1.5)
        rgb = np.clip(color * 255.0, 0, 255).astype(np.uint8)
        img[Yn, Xn, :3] = rgb; img[Yn, Xn, 3] = 255
    return Image.fromarray(img, "RGBA")


def rows_from_map_data(path):
    src = open(path, encoding="utf-8").read()
    i = src.index('"main": {', src.index("const AREAS"))
    a = src.index('"floor": [', i)
    return json.loads(re.sub(r",\s*\]$", "]", src[a + 9: src.index("]", a) + 1]))


# ---------------------------------------------------------------- other levels in the promenade style
# Each floor character gets one of the six paving families (0 hex, 1 ivory, 2 sage, 3 decking, 4 stone,
# 5 blue-grey slabs), optionally tinted.
AREA_FLOORS = {
    "top": {"i": (0, None), "f": (3, None), ".": (1, None), "D": (1, None)},
    "lounge": {"u": (5, None)},
    "museum": {"h": (4, None), ".": (1, None), "f": (3, None)},
    "sanctum": {"s": (4, ("6f5a9a", 0.32)), "i": (0, ("8a6fc0", 0.30))},
    "eng": {".": ("eng_floor_plate", None), "R": ("eng_floor_plate", ("6a5a4c", 0.20)), "i": ("eng_floor_plate", None), "U": ("eng_floor_plate", None),
            "o": ("eng_floor_ore", None), "f": ("eng_floor_concrete", None), "t": ("eng_floor_tech", None), "h": ("eng_floor_lino", None),
            "e": ("eng_floor_grate", None), "k": ("eng_floor_plate", ("6a3a2c", 0.45)), "q": (5, ("140e12", 0.88)),
            "j": ("eng_floor_plate", ("4a4e58", 0.25)), "a": ("eng_floor_pad", None)},
    "bay": {"u": ("eng_floor_hangar", None), "a": ("eng_floor_pad", None), "p": ("eng_floor_plate", None), "f": ("eng_floor_tech", None), "i": ("eng_floor_hangar", None)},
    "west": {".": ("arrivals/terminal", None), "p": ("arrivals/plaza", None), "f": ("arrivals/carpet", None), "h": ("arrivals/carpet_blue", None), "u": ("arrivals/terminal", None),
             "A": ("arrivals/plaza", None), "Q": ("sp_moon", None), "V": ("eng_floor_pad", None), "g": ("arrivals/glass", None), "Y": ("arrivals/basin", None)},
    "agri": {"Q": ("agri/moon", None), "a": ("agri/soil", None), "h": ("eng_floor_concrete", None), "f": ("eng_floor_concrete", ("c8a070", 0.15)), "s": ("agri/spa", None),
             "u": ("sp_terminal", None), "O": ("agri/water", ("70c8d0", 0.25)), "Y": ("agri/water", None)},
    "east": {".": ("sp_plaza", None), "s": ("ea_grass", None), "h": ("ea_deck", None), "a": ("sp_soil", None), "f": ("ea_rubber", None),
             "k": ("ea_court", None), "o": ("ea_deck", None), "t": ("ea_tile", None), "e": ("eng_floor_grate", None), "u": ("sp_terminal", None),
             "A": ("sp_terminal", None), "Y": ("agri/water", None), "O": ("agri/water", ("70c8d0", 0.25)), "p": ("east/dock", None),
             "j": ("east/stones", None)},
    "hotel": {
        "u": ("hotel/warm_deck_mix", None), "i": ("hotel/warm_deck_mix", None),
        "O": ("sp_water", ("70c8d0", 0.25)), "p": ("hotel/dining_mineral_mix", None),
        "k": ("hotel/kitchen_ceramic_mix", None), "h": ("hotel/warm_deck_mix", None),
        "o": ("hotel/warm_deck_mix", None), "t": ("hotel/navy_mix", None),
        "e": ("hotel/subfloor_mix", None),
    },
}



# ---------------------------------------------------------------- cavern floor variety (23 Nov 2026)
def _value_noise(H, W, cell, seed):
    """Smooth 0..1 noise (bilinear value noise, numpy only), deterministic per seed."""
    r = np.random.default_rng(seed)
    gh, gw = H // cell + 3, W // cell + 3
    g = r.random((gh, gw))
    yy = np.arange(H) / cell; xx = np.arange(W) / cell
    y0 = np.floor(yy).astype(int); x0 = np.floor(xx).astype(int)
    fy = (yy - y0)[:, None]; fx = (xx - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy


CAVE_DECOR = {   # dirt colour, tint strength, pebble light/mid/dark, extra kind
    "rock": ("8a6a4a", .15, ("b8a690", "7a6a5c", "3e3430"), None),
    "lush": ("3e3020", .55, ("8a9a78", "56664a", "2a3424"), "moss"),
    "steam": ("5a5a62", .78, ("aab4bc", "6e7884", "343c46"), "crust"),
    "lake": ("3a4048", .5, ("98a8b4", "5e6c78", "2c3440"), None),
}


def _cave_variety(img, ch, key, art_dir, Xn, Yn):
    """Break the cavern floor up: sunken dirt patches with a shadowed lip, pebbles, hairline cracks, and per band
    moss with tufts and glow-caps (green) or pale mineral crust and damp spots (steam)."""
    band = "lush" if "lush" in key else "steam" if ("steam" in key or key == "cav_45") else "lake" if key == "lake" else "rock"
    dirt_hex, dirt_k, peb, extra = CAVE_DECOR[band]
    H, W = ch.shape
    floor = ch == ord("m")
    if not floor.any():
        return
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(key))
    rng = np.random.default_rng(seed)
    n1 = _value_noise(H, W, 44, seed) * .86 + _value_noise(H, W, 15, seed + 1) * .14
    dirt = floor & (n1 > (0.66 if band == "steam" else 0.63))
    tex = np.asarray(Image.open(os.path.join(art_dir, "mine_path.png")).convert("RGB")) / 255.
    col = tex[Yn % tex.shape[0], Xn % tex.shape[1]]
    col = col * (1 - dirt_k) + hexc(dirt_hex) * dirt_k
    img[dirt, :3] = np.clip(col[dirt] * 255, 0, 255).astype(np.uint8)
    up = np.roll(dirt, 1, 0); lf = np.roll(dirt, 1, 1); dn = np.roll(dirt, -1, 0); rt = np.roll(dirt, -1, 1)
    shade = dirt & (~up | ~lf)                 # the stone lip casts a line of shadow into the dirt
    light = dirt & (~dn | ~rt) & ~shade        # and the far edge catches the light
    img[shade, :3] = (img[shade, :3] * .62).astype(np.uint8)
    img[light, :3] = np.clip(img[light, :3].astype(int) * 1.18, 0, 255).astype(np.uint8)
    outer = floor & ~dirt & (np.roll(dirt, -1, 0) | np.roll(dirt, -1, 1))
    img[outer, :3] = (img[outer, :3] * .8).astype(np.uint8)
    # a second, lighter variant: worn patches of the stone itself
    n2 = _value_noise(H, W, 28, seed + 7)
    worn = floor & ~dirt & (n2 > 0.72)
    img[worn, :3] = np.clip(img[worn, :3].astype(int) * 1.08 + 4, 0, 255).astype(np.uint8)
    pl, pm, pd = (np.array(hexc(c)) * 255 for c in peb)
    def put(x, y, c):
        if 0 <= y < H and 0 <= x < W and floor[y, x]: img[y, x, :3] = c
    # pebbles: more on and around the dirt
    near = dirt | outer
    count = int(floor.sum() / 260)
    ys, xs = np.nonzero(floor)
    for _ in range(count):
        k = rng.integers(len(ys)); y, x = ys[k], xs[k]
        if not near[y, x] and rng.random() < 0.6: continue
        big = rng.random() < 0.35
        put(x, y, pl); put(x + 1, y, pm); put(x, y + 1, pm); put(x + 1, y + 1, pd)
        if big: put(x + 2, y, pm); put(x + 2, y + 1, pd); put(x, y + 2, pd); put(x + 1, y + 2, pd)
    # hairline cracks
    for _ in range(int(floor.sum() / 9000) + 2):
        k = rng.integers(len(ys)); y, x = ys[k], xs[k]
        dx, dy = (1, 0) if rng.random() < .5 else (1, 1)
        for i in range(int(rng.integers(6, 16))):
            put(x, y, pd); x += dx; y += dy if rng.random() < .5 else 0
    if extra == "moss":
        n3 = _value_noise(H, W, 22, seed + 11)
        moss = floor & ~dirt & (n3 > 0.72)
        g = np.array(hexc("4a7a38")) * 255; g2 = np.array(hexc("5e9a44")) * 255
        img[moss, :3] = (img[moss, :3] * .68 + np.where(((Xn + Yn) % 3 == 0)[moss][:, None], g2, g) * .32).astype(np.uint8)
        tuft = [np.array(hexc(c)) * 255 for c in ("3e6a32", "6fa84c", "9cc870")]
        cap = [np.array(hexc(c)) * 255 for c in ("2a5a5e", "8fe3d2", "e6fff6")]
        for _ in range(int(floor.sum() / 700)):
            k = rng.integers(len(ys)); y, x = ys[k], xs[k]
            if rng.random() < 0.8:
                put(x, y, tuft[1]); put(x + 1, y - 1, tuft[2]); put(x + 2, y, tuft[1]); put(x + 1, y, tuft[0])
            else:
                put(x, y, cap[2]); put(x + 1, y, cap[1]); put(x, y + 1, cap[0])
    elif extra == "crust":
        n3 = _value_noise(H, W, 18, seed + 11)
        crust = floor & ~dirt & (n3 > 0.8)
        c1 = np.array(hexc("c8b090")) * 255
        img[crust, :3] = (img[crust, :3] * .7 + c1 * .3).astype(np.uint8)
        edge = crust & ~(np.roll(crust, 1, 0) & np.roll(crust, -1, 0) & np.roll(crust, 1, 1) & np.roll(crust, -1, 1))
        img[edge, :3] = np.clip(img[edge, :3].astype(int) + 22, 0, 255).astype(np.uint8)
        n4 = _value_noise(H, W, 10, seed + 13)
        damp = floor & ~dirt & ~crust & (n4 > 0.8)
        img[damp, :3] = (img[damp, :3] * .78).astype(np.uint8)


def _soil_variety(img, ch, Xn, Yn):
    """The Agri dome's soil (23 Nov): all of it can be dug, so it stays plain dirt, broken up by soft damp (darker)
    and dry (lighter) patches, a scatter of pebbles and the odd sprouting weed."""
    soil = ch == ord("a")
    if not soil.any():
        return
    H, W = ch.shape
    damp = soil & (_value_noise(H, W, 38, 901) > 0.71)
    img[damp, :3] = (img[damp, :3] * .86).astype(np.uint8)
    dry = soil & ~damp & (_value_noise(H, W, 30, 902) > 0.7)
    img[dry, :3] = np.clip(img[dry, :3].astype(int) * 1.07 + 3, 0, 255).astype(np.uint8)
    rng = np.random.default_rng(903)
    ys, xs = np.nonzero(soil)
    peb = [np.array(hexc(c)) * 255 for c in ("9a8e84", "6e645e", "463e3a")]
    weed = [np.array(hexc(c)) * 255 for c in ("3e6a32", "6fa84c")]
    def put(x, y, c):
        if 0 <= y < H and 0 <= x < W and soil[y, x]: img[y, x, :3] = c
    for _ in range(int(soil.sum() / 900)):
        k = rng.integers(len(ys)); y, x = ys[k], xs[k]
        put(x, y, peb[0]); put(x + 1, y, peb[1]); put(x + 1, y + 1, peb[2])
    for _ in range(int(soil.sum() / 4000)):
        k = rng.integers(len(ys)); y, x = ys[k], xs[k]
        put(x, y, weed[1]); put(x + 1, y - 1, weed[1]); put(x + 1, y, weed[0]); put(x + 2, y, weed[1])


def bake_area(key, rows, art_dir, extras=None):
    baker = Baker(art_dir)
    table = AREA_FLOORS[key]
    rows = wall_border_chars(rows)
    H, W = len(rows) * PX, len(rows[0]) * PX
    chars = np.array([[ord(c) for c in row] for row in rows], dtype=np.int32)
    Yn, Xn, y, x = _grid(H, W)
    ch = chars[Yn // PX, Xn // PX]
    img = np.zeros((H, W, 4), dtype=np.uint8)
    def paint(c, m):
        kind, tint = table[c]
        ys, xs = Yn[m], Xn[m]
        if isinstance(kind, str):                                 # a sector material: art/lunar/<kind>.png, 2x2 tiles
            tex = np.asarray(Image.open(os.path.join(art_dir, kind + ".png")).convert("RGB"), dtype=np.float32) / 255.0
            if kind.startswith("agri/"):
                # Pick one complete two-tile swatch per map block, on the native grid.
                span = 2 * PX
                variant = ((xs // span * 17) ^ (ys // span * 29)) % (tex.shape[1] // span)
                col = tex[ys % span, variant * span + xs % span]
            elif kind.startswith(("hotel/", "residential/")):
                # These atlases have multiple two-tile swatches, each already on the 24px grid.
                col = tex[ys % tex.shape[0], xs % tex.shape[1]]
            else:
                col = _tex_lookup(tex, ys, xs)
                if ((key in ("eng", "bay") and kind.startswith("eng_floor_"))
                        or (key == "east" and kind.startswith("ea_"))
                        or kind.startswith("arrivals/")):
                    index = (xs // (2*PX) * 7 + ys // (2*PX) * 3) % 11
                    # Index 2 also lands on a whole panel in the small East pavilion.
                    first = 2 if key == "east" else 3
                    for value, suffix in ((first, "_a"), (8, "_b")):
                        use = index == value
                        variant = np.asarray(Image.open(os.path.join(art_dir, kind + suffix + ".png"))) / 255.
                        col[use] = _tex_lookup(variant, ys[use], xs[use])
        else:
            col = baker.swatch(np.full(xs.shape, kind), x[m], y[m])
        if tint:
            col = lerp(col, hexc(tint[0]), tint[1])
        img[ys, xs, :3] = np.clip(col * 255.0, 0, 255).astype(np.uint8); img[ys, xs, 3] = 255
    for c in table:
        m = ch == ord(c)
        if m.any():
            paint(c, m)
    if key == "hotel":
        _hotel_finishes(img, art_dir)
    if key.startswith("cav_") or key in ("mine", "tunnels", "lake"):
        _cave_variety(img, ch, key, art_dir, Xn, Yn)
    if key == "agri":
        _soil_variety(img, ch, Xn, Yn)
    extras = extras or {}
    for rc, pts, among in extras.get("regions", []):
        # A floor kind laid on a true outline rather than by tiles (the lake's shingle shore): pixels of the
        # listed floor kinds inside the outline get rc, those outside it get the first other kind listed.
        X, Y = (Xn + .5) / PX, (Yn + .5) / PX
        m = np.zeros((H, W), dtype=bool); n = len(pts)
        for i in range(n):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
            if y1 == y2: continue
            m ^= ((y1 > Y) != (y2 > Y)) & (X < x1 + (Y - y1) * (x2 - x1) / (y2 - y1))
        area = np.zeros((H, W), dtype=bool)
        for c in among: area |= ch == ord(c)
        other = [c for c in among if c != rc][0]
        paint(rc, area & m); paint(other, area & ~m)
    if "holes" in extras:
        # Pits and pools drawn on their true 45-degree outlines (the tiles only say where you cannot walk):
        # hole tiles outside the outline get the cave floor, floor tiles inside it get the hole, and a dark lip
        # runs round the edge. extras["holes"]: [[(x, y), ...] in tiles], extras["hole_char"], extras["floor_char"].
        hc, fc = extras.get("hole_char", "O"), extras.get("floor_char", "m")
        inside = np.zeros((H, W), dtype=bool)
        X, Y = (Xn + .5) / PX, (Yn + .5) / PX
        for pts in extras["holes"]:
            m = np.zeros((H, W), dtype=bool)
            n = len(pts)
            for i in range(n):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
                if y1 == y2:
                    continue
                cross = ((y1 > Y) != (y2 > Y)) & (X < x1 + (Y - y1) * (x2 - x1) / (y2 - y1))
                m ^= cross
            inside |= m
        area = (ch == ord(hc)) | (ch == ord(fc))
        paint(fc, area & ~inside & (ch == ord(hc)))
        paint(hc, area & inside & (ch == ord(fc)))
        sh = inside.copy()
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            sh &= np.roll(np.roll(inside, dy, 0), dx, 1)
        lip = inside & ~sh & area
        if extras.get("lake"):
            _lake_water(img, inside, area, ch, ord(fc), Xn, Yn, key=key, art_dir=art_dir)
        else:
            img[lip, :3] = (img[lip, :3] * .35).astype(np.uint8)
    if "data_lines" in extras:
        # Glowing lines in S.A.R.A.'s floor, from her dais out to each memory core, and a ring round the dais.
        glow = np.zeros((H, W), dtype=bool)
        for (ax, ay), (bx, by) in extras["data_lines"]:
            ax, ay, bx, by = ax * 16, ay * 16, bx * 16, by * 16
            vx, vy = bx - ax, by - ay
            t = np.clip(((x - ax) * vx + (y - ay) * vy) / float(vx * vx + vy * vy), 0, 1)
            glow |= np.hypot(x - (ax + t * vx), y - (ay + t * vy)) < 1.6
        dx, dy = extras["dais"][0] * 16, extras["dais"][1] * 16
        rr = np.hypot(x - dx, y - dy)
        glow |= (np.abs(rr - 46) < 1.2) | (np.abs(rr - 58) < 0.8)
        glow &= ch == ord("i")
        img[glow, :3] = (92, 214, 222)
    if "rails" in extras:
        _rail_extras(img, ch, x, y, extras)
    if "stairs" in extras:
        _stair_extras(img, Xn, Yn, extras["stairs"])
    if "core" in extras:
        _engineering_extras(img, ch, x, y, extras)
    elif "belts" in extras:
        _belt_extras(img, ch, x, y, extras)
    return Image.fromarray(img, "RGBA")


def _hotel_finishes(img, art_dir):
    """Place the lobby inlay, lounge rug, hearth, service panels and sills in map coordinates."""
    def texture(name):
        return np.asarray(Image.open(os.path.join(art_dir, "hotel", name + ".png")).convert("RGB"))

    # The fountain coping covers the staircase at the edge of the water tiles: an octagon, eight facets of
    # stone, like every other shape in the game (Zachary, 22 Nov: no circles).
    radius = 5.6 * PX
    cx, cy = 60 * PX, int(21.5 * PX)
    extent = int(np.ceil(radius))
    patch = img[cy-extent:cy+extent, cx-extent:cx+extent, :3]
    yy, xx = np.indices(patch.shape[:2])
    dx, dy = xx + .5 - extent, yy + .5 - extent
    rr = np.maximum(np.maximum(np.abs(dx), np.abs(dy)), (np.abs(dx) + np.abs(dy)) / np.sqrt(2)) / PX
    angle = np.arctan2(dy, dx)
    wedge = np.floor((angle + np.pi + np.pi / 8) * 4 / np.pi).astype(int)
    for index, name in enumerate(("mineral", "mineral_a", "mineral_b")):
        stone = texture(name)
        mask = (rr >= 3.04) & (rr < 5.15) & (wedge % 3 == index)
        patch[mask] = stone[yy[mask] % stone.shape[0], xx[mask] % stone.shape[1]]
    joints = np.abs(np.sin(4 * (angle - np.pi / 8))) * rr * PX / 4 < .9          # at the octagon's corners
    patch[(rr >= 3.22) & (rr < 5.15) & joints] = (161, 152, 134)
    water = texture("basin_water")
    wet = rr < 3.04
    patch[wet] = water[yy[wet] % water.shape[0], xx[wet] % water.shape[1]]
    patch[(rr >= 3.04) & (rr < 3.16)] = (75, 102, 106)
    patch[(rr >= 3.16) & (rr < 3.29)] = (192, 181, 152)
    patch[(rr >= 5.10) & (rr < 5.18)] = (147, 135, 111)
    # Ripples spreading from the middle, then an eight-sided plinth with a spout of water on it.
    for r0, c0 in ((2.35, (96, 150, 150)), (1.75, (84, 136, 138))):
        patch[(np.abs(rr - r0) < .05) & wet] = c0
    plinth = rr < 1.05
    stone_ = texture("mineral")
    patch[plinth] = stone_[yy[plinth] % stone_.shape[0], xx[plinth] % stone_.shape[1]]
    lit = plinth & (dy + dx < 0) & (rr > .82)
    patch[lit] = np.clip(patch[lit].astype(int) + 28, 0, 255)
    shade_ = plinth & (dy + dx > 0) & (rr > .82)
    patch[shade_] = (patch[shade_] * .72).astype(np.uint8)
    patch[(rr >= 1.05) & (rr < 1.2)] = (40, 70, 74)                         # its shadow line in the water
    bowl = rr < .55
    patch[bowl] = (78, 140, 146)
    patch[rr < .28] = (176, 222, 220)                                         # the spout
    patch[(rr < .14)] = (236, 250, 246)

    for name, tx, ty, w, h, cut, edge in (
        ("red_carpet_mix", 93.35, 21.7, 9.4, 5.5, .7, (102, 65, 62)),
        ("hearth_slate_mix", 93.5, 12.1, 4.9, 2.44, .8, (122, 114, 94)),
    ):
        x0, x1 = round((tx-w)*PX), round((tx+w)*PX)
        y0, y1 = round((ty-h)*PX), round((ty+h)*PX)
        region = img[y0:y1, x0:x1]
        y, x = np.mgrid[y0:y1, x0:x1]
        fx = w*PX - np.abs(x + .5 - tx*PX)
        fy = h*PX - np.abs(y + .5 - ty*PX)
        depth = np.minimum(np.minimum(fx, fy), (fx + fy - cut*PX) / np.sqrt(2))
        inside = (depth >= 0) & (region[..., 3] != 0)
        tex = texture(name)
        region[inside, :3] = tex[y[inside] % tex.shape[0], x[inside] % tex.shape[1]]
        region[inside & (depth < 1.5), :3] = edge
    for index, name in enumerate(("service_panel_a", "service_panel", "service_panel_b")):
        tile = np.asarray(Image.fromarray(texture(name)).resize((36, 36), Image.Resampling.NEAREST))
        x, y = 51*PX + index*36, 47*PX
        img[y:y+36, x:x+36, :3] = tile
    for tx, name in ((29, "sill_a"), (89, "sill_b")):
        tex = texture(name)
        img[63*PX:63*PX+tex.shape[0], tx*PX:tx*PX+tex.shape[1], :3] = tex


def _lake_water(img, inside, area, ch, shore, Xn, Yn, key=None, art_dir=None):
    """The underground lake (22 Nov): deeper and darker towards the middle, a pale shallow rim, a thin wet line
    where the water meets the shingle, darker wet stones along the shore, and faint glints on the surface."""
    from scipy.ndimage import distance_transform_edt, gaussian_filter
    rgb = img[..., :3].astype(np.float32)
    water = inside & area
    din = distance_transform_edt(water)
    dout = distance_transform_edt(~water)
    deep = np.clip(din / 70.0, 0, 1)
    rgb[water] *= (1 - .5 * deep[water])[:, None]
    rim = water & (din < 12)
    k = (1 - din[rim] / 12.0) ** 1.5 * .38
    rgb[rim] = rgb[rim] * (1 - k[:, None]) + np.array([96, 170, 178])[None, :] * k[:, None]
    edge = water & (din < 2.2)
    rgb[edge] = rgb[edge] * .35 + np.array([170, 226, 222]) * .65
    wet = (ch == shore) & ~water & (dout < 14)
    rgb[wet] *= (.62 + .38 * np.clip(dout[wet] / 14.0, 0, 1) ** .8)[:, None]
    dock = ch == ord("p")
    sh = np.zeros_like(water)
    for k in range(1, 10): sh |= np.roll(np.roll(dock, k, 0), k // 2, 1)
    sh &= water & ~dock
    rgb[sh] *= .45
    rnd = np.random.default_rng(45)
    gl = water & (din > 10) & (rnd.random(water.shape) < .0016)
    for dx in (0, 1, 2):
        g2 = np.roll(gl, dx, 1) & water
        rgb[g2] = rgb[g2] * .3 + np.array([150, 230, 235]) * .7
    img[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    painted = _docks(img, dock, water, Xn, Yn) if dock.any() else np.zeros_like(water)
    if key and art_dir:
        # The water's outline, for the animated surface the game lays over it (area.gd, shaders/water_surface).
        # tools/build.py clears it under the baked walls once they exist.
        m = water & ~painted
        Image.fromarray((m * 255).astype(np.uint8), "L").save(os.path.join(art_dir, "watermask_%s.png" % key))


DOCK_WOOD = ["2e1e18", "4a3226", "684834", "866044", "a67c56", "c49c70"]


def _docks(img, dock, water, Xn, Yn):
    """Each dock (23 Nov): planks across its width with dark gaps, grain and nails, lit on the left and shaded on
    the right; a thick front face where it ends over the water; posts going down into the water with a pale ripple
    ring where they meet it; and mooring posts standing up at the corners. Returns the pixels painted over water."""
    from scipy.ndimage import label
    W = [np.array(hexc(c)) * 255 for c in DOCK_WOOD]
    H_, W_ = dock.shape
    painted = np.zeros_like(dock)
    lab, n = label(dock)
    def put(x, y, c, over_water=True):
        if 0 <= y < H_ and 0 <= x < W_ and (dock[y, x] or (over_water and water[y, x])):
            img[y, x, :3] = c
            if water[y, x]: painted[y, x] = True
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        vertical = (y1 - y0) > (x1 - x0)
        for y, x in zip(ys, xs):
            a = (y - y0) if vertical else (x - x0)       # along the dock
            plank = a // 4
            if a % 4 == 3:
                c = W[0]
            else:
                tone = 3 + ((plank * 7) % 5 == 0) - ((plank * 11) % 7 == 0)
                across = (x - x0) if vertical else (y - y0)
                width = (x1 - x0) if vertical else (y1 - y0)
                if across <= 1: tone = 4                        # lit edge
                elif across >= width - 1: tone = 1              # shaded edge
                if (x * 7 + y * 3 + plank * 13) % 17 == 0: tone -= 1
                c = W[max(0, min(5, tone))]
                if a % 4 == 1 and across in (3, width - 3): c = W[0]          # nails
            img[y, x, :3] = c
        # the front face: under the end (a long dock) or the whole south side (a side dock)
        RIP, RIP2 = np.array([150, 220, 222]), np.array([100, 170, 182])
        for x in range(x0, x1 + 1):
            for k in range(1, 8):
                put(x, y1 + k, W[2] if k == 1 else W[1] if k < 6 else W[0])
            if (x - x0) % 8 == 0:
                for k in range(2, 6): put(x, y1 + k, W[0])                 # board joints on the face
        def piling(px, top, depth):
            # a round post going down into the water: lit on the left, a ripple ring where it meets the water
            for k in range(depth):
                put(px, top + k, W[3]); put(px + 1, top + k, W[2]); put(px + 2, top + k, W[1]); put(px + 3, top + k, W[0])
            for dx in range(-1, 5): put(px + dx, top + depth, RIP)
            put(px - 2, top + depth - 1, RIP2); put(px + 5, top + depth - 1, RIP2)
            put(px - 1, top + depth + 1, RIP2); put(px + 4, top + depth + 1, RIP2)
        posts = [x0 + 2, x1 - 5] if vertical else list(range(x0 + 4, x1 - 3, 48))
        for px in posts:
            piling(px, y1 + 8, 7)
        if vertical:
            # pilings along both sides of a long dock, every two tiles, standing just clear of the deck
            for py in range(y0 + 20, y1 - 6, 48):
                piling(x0 - 4, py, 6)
                piling(x1 + 1, py, 6)
        # mooring posts standing up at the outer corners
        for (cx, cy) in ([(x0 + 1, y1 - 3), (x1 - 3, y1 - 3)] if vertical else [(x0 + 1, y0 + 1), (x1 - 3, y0 + 1)]):
            for dy in range(3):
                for dx in range(3):
                    put(cx + dx, cy + dy, W[5] if dy == 0 and dx < 2 else W[3] if dy < 2 else W[1], over_water=False)
    return painted


def _stair_extras(img, Xn, Yn, stairs):
    """Rough steps cut in the rock (22 Nov): a lit nose and a dark riser every few pixels, fading into the
    dark towards the end that leaves the map. stairs: [(x0, y0, x1, y1, 'n' or 's')] in tiles, inclusive."""
    rgb = img[..., :3].astype(np.float32)
    for x0, y0, x1, y1, way in stairs:
        m = (Xn >= x0 * PX) & (Xn < (x1 + 1) * PX) & (Yn >= y0 * PX) & (Yn < (y1 + 1) * PX)
        ys = Yn - y0 * PX
        step = ys % 10
        rgb[m & (step == 0)] = rgb[m & (step == 0)] * .45
        rgb[m & (step == 1)] = rgb[m & (step == 1)] * .7
        rgb[m & (step == 2)] = np.clip(rgb[m & (step == 2)] * 1.25 + 12, 0, 255)
        span = (y1 + 1 - y0) * PX
        f = np.clip(ys / float(span), 0, 1) if way == "s" else np.clip(1 - ys / float(span), 0, 1)
        rgb[m] *= (1 - .7 * f[m] ** 1.5)[:, None]
        edge = m & ((Xn - x0 * PX < 3) | ((x1 + 1) * PX - Xn <= 3))         # dark edges where the steps meet the rock
        rgb[edge] *= .55
    img[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)


def _rail_extras(img, ch, x, y, extras):
    """Mine rails (22 Nov): timber sleepers across the walkway, two steel rails along it, lit on top."""
    walk = (ch != ord("#")) & (ch != ord("~"))
    rgb = img[..., :3].astype(np.float32)
    for ax, ay, bx, by in _segments(extras["rails"]):
        vx, vy = bx - ax, by - ay
        L = max(1e-6, (vx * vx + vy * vy) ** .5)
        ux, uy = vx / L, vy / L
        along = (x - ax) * ux + (y - ay) * uy
        side = (x - ax) * -uy + (y - ay) * ux                  # signed distance across the track
        on = walk & (along >= 0) & (along <= L)
        ties = on & (np.abs(side) < 7.5) & ((along % 7) < 3.2)
        tie_top = ties & ((along % 7) < 1.0)
        tie_lo = ties & ((along % 7) > 2.4)
        rgb[on & (np.abs(side) < 8.5) & ((along % 7) >= 3.2) & ((along % 7) < 3.9)] *= .72   # shadow behind each sleeper
        rgb[ties] = (104, 74, 50); rgb[tie_top] = (138, 104, 72); rgb[tie_lo] = (70, 48, 34)
        for off in (-4.5, 4.5):
            r_ = on & (np.abs(side - off) < 1.1)
            rgb[r_] = (92, 94, 104)
            rgb[r_ & (side - off < -0.2)] = (176, 182, 192)
            rgb[on & (side - off >= 1.1) & (side - off < 2.0)] *= .6
    img[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)


def _belt_extras(img, ch, x, y, extras):
    """Conveyor belts on their own (the mine's loading spot), drawn the same way as Engineering's."""
    walk = (ch != ord("#")) & (ch != ord("~"))
    rgb = img[..., :3].astype(np.float32)
    for ax, ay, bx, by in _segments(extras["belts"]):
        dd, along = _near_segment(x, y, ax, ay, bx, by)
        m2 = (dd < 5) & walk
        rgb[(dd < 6.5) & walk] = (34, 34, 40)
        rgb[m2] = (64, 66, 74)
        rgb[m2 & (along % 6 < 1.2)] = (118, 122, 132)
        rgb[(dd >= 5) & (dd < 6.5) & walk & (along % 10 < 5)] = (220, 170, 50)
    img[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)


def _segments(lines):
    for pts in lines:
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            yield ax * 16, ay * 16, bx * 16, by * 16


def _near_segment(x, y, ax, ay, bx, by):
    """Distance from each pixel to the segment, and how far along it the nearest point lies (pixels)."""
    vx, vy = bx - ax, by - ay
    L = max(1e-6, (vx * vx + vy * vy) ** .5)
    t = np.clip(((x - ax) * vx + (y - ay) * vy) / (L * L), 0, 1)
    return np.hypot(x - (ax + t * vx), y - (ay + t * vy)), t * L


def _engineering_extras(img, ch, x, y, extras):
    """Engineering: the sunken core's glow, the railing round the pit, stair treads, coolant pipes under
    floor grates, cable trays and the conveyor belts (drawn last, on top)."""
    walk = (ch != ord("#")) & (ch != ord("~")) & (ch != ord("q"))
    rgb = img[..., :3].astype(np.float32)
    # the core's glow, strongest down in the pit
    cx, cy = extras["core"][0] * 16, extras["core"][1] * 16
    d = np.hypot((x - cx) / 1.6, y - cy)
    pit = (ch == ord("k")) | (ch == ord("q")) | (ch == ord("j"))
    k = np.clip(1 - d / 230.0, 0, 1)[..., None] * np.where(pit, .55, .12)[..., None]
    rgb = rgb * (1 - k) + np.array([255, 130, 50], np.float32) * k
    # the drop and the pit floor, as true 45-degree octagons (the tiles only say where you can walk)
    def octagon(x0, y0, x1, y1, cut):
        X, Y = x / 16.0, y / 16.0
        return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1) & (np.minimum(X - x0, x1 - X) + np.minimum(Y - y0, y1 - Y) >= cut)
    stairs = ch == ord("j")
    outer, inner = octagon(*extras["pit"][0]), octagon(*extras["pit"][1])
    hall_c = rgb[(ch == ord(".")) & ~outer].mean(axis=0)
    floor_c = rgb[(ch == ord("k")) & inner].mean(axis=0)
    q = ch == ord("q")
    rgb[q & ~outer] = hall_c                                    # stepped corners outside the octagon look like hall
    plate = ((x % 32 == 0) | (y % 24 == 0)).astype(np.float32)        # the pit floor: big plates, one surface
    pf = inner & ~stairs
    kk = np.clip(1 - d / 230.0, 0, 1) * .55
    rgb[pf] = (floor_c * (1 - .18 * plate[pf, None])) * (1 - kk[pf, None]) + np.array([255, 130, 50], np.float32) * kk[pf, None]
    drop = outer & ~inner & ~stairs
    depth = np.zeros(drop.shape, np.float32)                    # darker near the pit floor's edge, as if looking down a wall
    for r in range(1, 6):
        depth = np.maximum(depth, octagon(extras["pit"][1][0] - r * .45, extras["pit"][1][1] - r * .45, extras["pit"][1][2] + r * .45,
                                           extras["pit"][1][3] + r * .45, extras["pit"][1][4]) * (1 - r / 6.0))
    rgb[drop] = np.array([30, 22, 26], np.float32) * (1 - depth[drop, None] * .5) + np.array([120, 60, 30], np.float32) * depth[drop, None] * .5
    # stair treads
    rgb[stairs & (x % 4 == 0)] *= 0.6
    # railing just outside the drop: a dark lip and a steel rail
    lip = octagon(extras["pit"][0][0] - .1, extras["pit"][0][1] - .1, extras["pit"][0][2] + .1, extras["pit"][0][3] + .1, extras["pit"][0][4]) & ~outer
    rail = octagon(extras["pit"][0][0] - .3, extras["pit"][0][1] - .3, extras["pit"][0][2] + .3, extras["pit"][0][3] + .3, extras["pit"][0][4]) & ~outer & ~lip
    gap = (np.abs(y / 16.0 - 38.5) < 1.6)                       # no rail across the stairways
    rgb[lip & ~gap] = (60, 64, 76); rgb[rail & ~gap] = (182, 190, 202)
    # coolant pipes under grates, cable trays
    for lines, (col, half) in ((extras.get("pipes", []), ((70, 150, 230), 3.0)), (extras.get("cables", []), ((214, 176, 60), 1.6))):
        for ax, ay, bx, by in _segments(lines):
            dd, along = _near_segment(x, y, ax, ay, bx, by)
            m = (dd < half + 1.2) & walk
            rgb[m] = rgb[m] * .5
            m2 = (dd < half) & walk
            rgb[m2] = col
            if half > 2:
                rgb[m2 & (along % 8 < 1.5)] = (40, 60, 90)          # the grate over the pipe
    # conveyor belts
    for ax, ay, bx, by in _segments(extras.get("belts", [])):
        dd, along = _near_segment(x, y, ax, ay, bx, by)
        m = (dd < 6.5) & walk
        rgb[m] = (34, 34, 40)
        m2 = (dd < 5) & walk
        rgb[m2] = (64, 66, 74)
        rgb[m2 & (along % 6 < 1.2)] = (118, 122, 132)               # rollers
        rgb[(dd >= 5) & (dd < 6.5) & walk & (along % 10 < 5)] = (220, 170, 50)   # hazard edge
    img[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)


def lounge_window_strip(map_width, art_dir):
    """Align the bottom two blocks of the quiet sky with the baked lounge wall."""
    with Image.open(os.path.join(art_dir, "lounge_sky", "clear.png")) as atlas:
        frame_height = atlas.height // 32
        view = atlas.crop((0, frame_height // 2, atlas.width, frame_height))
    left = 9 * PX
    view = view.resize((57 * PX, 2 * PX), Image.Resampling.NEAREST)
    strip = Image.new("RGB", (map_width * PX, 2 * PX))
    strip.paste(view, (left, 0))
    return strip


# ---------------------------------------------------------------- smooth walls
# Walls used to be drawn tile by tile, so every curve and every 45-degree wall was a staircase. Here the
# tile map's walls are smoothed (a soft blur of the solid tiles, cut at half way), which turns stairs into
# straight diagonals and steps into curves, and then drawn the way the game drew them: a roof lifted 16
# pixels, a wall face 32 pixels tall wherever floor lies in front, side edges, seams between roof plates
# and a soft shadow on the floor. Collision is still the tile grid. The game draws this picture over the
# floor (scripts/lunar_ground.gd); repainting material_1.png (roof) or material_2.png (wall face) still works.
SOLID = "#Wzw"
# Levels with their own wall materials: (roof, wall face), files in art/lunar. Others use material_1 / material_2.
SECTOR_WALLS = {"eng": ("eng_roof", "eng_wall"), "bay": ("eng_roof", "eng_wall"), "main": ("promenade/roof", "promenade/wall"),
                "hotel": ("hotel/cap_mix", "hotel/hotel_enamel_mix"), "west": ("arrivals/roof", "arrivals/wall"), "east": ("east/roof", "east/wall"),
                "agri": ("agri/roof", "agri/wall"), "top": ("material_1", "material_2"), "museum": ("material_1", "material_2"),
                "lounge": ("material_1", "material_2"), "sanctum": ("material_1", "material_2")}
WALL_TINTS = ["ffffff", "e1e7ec", "ede2d5"]
ROOF_TINTS = ["ffffff", "dbe4ee", "f0e9df", "c6d3e2"]


ROOF_ZONE_FN = {}             # level key -> fn(tx, ty) giving roof zones, set by tools/east.py and others
# Buildings that stand inside a map and are drawn in their own materials, not the map's walls (23 Nov: your
# apartment on the agri complex's front porch): key -> [{"roof": (x0, y0, x1, y1), "cuts": (top-left, top-right,
# bottom-left, bottom-right), "front": (x0, y0, x1, y1), "roof_art": ..., "wall_art": ...}], tiles inclusive.
# The roof's corners are cut at 45 degrees by `cuts` tiles, so the building reads soft-edged rather than as a hard
# rectangle; the wall faces of the tiles in `front` are drawn in wall_art.
HOUSE_FRONTS = {}


def _roof_zone(key, tx, ty):
    if key in ROOF_ZONE_FN:
        return ROOF_ZONE_FN[key](tx, ty)
    if key != "main":
        return np.zeros(tx.shape, dtype=np.int64)
    zone = np.zeros(tx.shape, dtype=np.int64)
    dx, dy = tx + 0.5 - 115.5, ty + 0.5 - 95.5
    a = np.degrees(np.arctan2(dy, dx)) % 360.0
    inner = np.hypot(dx, dy) < 45.0
    zone = np.where(inner, (a // 45).astype(np.int64) % 8, 8 + (((a + 11.25) % 360.0) // 22.5).astype(np.int64) % 16)
    for sx in (-1, 1):
        for sy in (-1, 1):
            zone = np.where(np.hypot(tx - 115 - sx * 39.6, ty - 95 - sy * 39.6) <= 14.0, 24, zone)
    return zone


# Edge colours for the baked walls. Homes use the warm set that matches the cozy props (22 Nov 2026).
COOL_EDGES = dict(seam="36434f", seam_hi="a9b6c2", left="394756", right="7c828a", top="2b3442", top_hi="b8c4cf",
                  lip="dcc1a1", lip_lo="59667b", foot="2b3442")
HOME_EDGES = dict(seam="3b2a2e", seam_hi="8c7470", left="4a3634", right="8a6f66", top="3a2626", top_hi="9c8278",
                  lip="e8d2b0", lip_lo="7a5640", foot="3a2626")
PROM_EDGES = dict(seam="1f3434", seam_hi="6f9a92", left="243c3c", right="5f8580", top="1c2c2e", top_hi="7fa49c",
                  lip="f0dcb8", lip_lo="5a7470", foot="2a2622")
ENG_EDGES = dict(seam="16242a", seam_hi="5f7d86", left="1c2e34", right="557178", top="141c22", top_hi="6a8088",
                 lip="9fc4c0", lip_lo="2a3c40", foot="1e1a18")
CAVE_EDGES = dict(seam="241a16", seam_hi="6e5a4c", left="2c211c", right="6a5648", top="1e1612", top_hi="7a6450",
                  lip="b49a7c", lip_lo="3a2c24", foot="1a1210")
LUSH_EDGES = dict(seam="17221a", seam_hi="5a7454", left="1c2a1e", right="58704e", top="121a14", top_hi="6a8460",
                  lip="9ab486", lip_lo="2a3a2a", foot="141a12")
STEAM_EDGES = dict(seam="161e2a", seam_hi="5a6e86", left="1a2432", right="566a84", top="121820", top_hi="6a7e98",
                   lip="a8bcd0", lip_lo="2a3646", foot="12161e")
LAKE_EDGES = dict(seam="0e1820", seam_hi="4a6a7c", left="101c26", right="4a6676", top="0a1218", top_hi="5e8294",
                  lip="9cc8d4", lip_lo="1e3440", foot="0a1016")
def cave_edges(key):
    """Mine, tunnels, caverns and the underground lake: rock edges by cavern kind."""
    if key.startswith("cav_"):
        return LUSH_EDGES if "lush" in key else STEAM_EDGES if ("steam" in key or key == "cav_45") else CAVE_EDGES
    if key == "lake":
        return LAKE_EDGES
    return CAVE_EDGES if key in ("mine", "tunnels") else None

# Cave atmosphere (22 Nov): the colour of the deep shadow, of the haze that hangs in the air, and of the light
# from the wall lanterns; which floor characters are bare rock (rubble and grit go only there); and the lights
# placed by the map builders, CAVE_LIGHTS[key] = [(x, y in tiles, kind, radius in tiles)].
CAVE_MOOD = {"mine": dict(ao=(.12, .07, .05), mist=(.62, .5, .38), mist_a=.16, dark=.24, lamp=(1.0, .78, .46), rock="mkuR"),
             "tunnels": dict(ao=(.05, .05, .09), mist=(.36, .4, .56), mist_a=.2, dark=.3, lamp=(1.0, .8, .5), rock="muo"),
             "rock": dict(ao=(.08, .05, .06), mist=(.5, .42, .4), mist_a=.2, dark=.28, lamp=(1.0, .78, .48), rock="m"),
             "lush": dict(ao=(.03, .08, .05), mist=(.42, .7, .5), mist_a=.22, dark=.26, lamp=(.7, 1.0, .72), rock="m"),
             "steam": dict(ao=(.04, .06, .1), mist=(.74, .84, .94), mist_a=.26, dark=.24, lamp=(.7, .9, 1.0), rock="m"),
             "lake": dict(ao=(.02, .05, .08), mist=(.4, .66, .74), mist_a=.24, dark=.26, lamp=(.55, .95, 1.0), rock="ms")}
LIGHT_COLOURS = {"warm": ((1.0, .8, .5), .48), "fire": ((1.0, .62, .32), .5), "cyan": ((.45, 1.0, .95), .34),
                 "violet": ((.82, .62, 1.0), .34), "green": ((.6, 1.0, .55), .32)}
CAVE_LIGHTS = {}
def cave_mood(key):
    if key.startswith("cav_"):
        return CAVE_MOOD["lush" if "lush" in key else "steam" if ("steam" in key or key == "cav_45") else "rock"]
    return CAVE_MOOD.get(key)
COZY_EDGES = {"main": PROM_EDGES, "eng": ENG_EDGES, "bay": ENG_EDGES, "hotel": HOME_EDGES, "west": ENG_EDGES, "east": HOME_EDGES,
              "agri": ENG_EDGES, "top": PROM_EDGES, "museum": HOME_EDGES, "lounge": HOME_EDGES, "sanctum": PROM_EDGES}          # areas re-done in the cozy style that are not homes, with their own edge set
def is_home(key):
    """Homes, apartments, flats and the bar: wallpapered rooms with the warm wall set."""
    return key.startswith(("home", "apt", "flat")) or key in ("bar", "bathhouse")

def bake_walls(key, rows, art_dir, window=None, sigma=15.0, style="facet"):
    from scipy.ndimage import gaussian_filter
    rows = ["".join(r) for r in rows]
    th, tw = len(rows), len(rows[0])
    H, W = th * PX, tw * PX
    tiles = np.array([[c in SOLID for c in r] for r in rows])
    chars = np.array([[ord(c) for c in r] for r in rows], dtype=np.int32)
    open_ = ~tiles & (chars != ord("~"))
    def sol(dx, dy):
        out = np.zeros_like(tiles)
        ys, xs = slice(max(0, -dy), th - max(0, dy)), slice(max(0, -dx), tw - max(0, dx))
        out[ys, xs] = tiles[max(0, dy):th - max(0, -dy) if max(0, -dy) else th, max(0, dx):tw - max(0, -dx) if max(0, -dx) else tw]
        return out
    gap = (sol(-1, 0) & sol(1, 0)) | (sol(0, -1) & sol(0, 1)) | (sol(-1, 0) & sol(2, 0)) | (sol(-2, 0) & sol(1, 0)) | \
          (sol(0, -1) & sol(0, 2)) | (sol(0, -2) & sol(0, 1))
    if style == "smooth":
        B = gaussian_filter(np.repeat(np.repeat(tiles.astype(np.float32), PX, 0), PX, 1), sigma * PX / 16.0, mode="constant", cval=0.0) > 0.5
    else:
        # Faceted: every edge is straight or exactly 45 degrees. A wall tile open on two neighbouring sides
        # (and on the corner between them) loses that corner as a half-tile triangle, so a staircase of
        # single steps becomes one straight diagonal. The tiles beside a doorway stay square.
        B = np.repeat(np.repeat(tiles, PX, 0), PX, 1)
        door_near = np.zeros_like(tiles)
        dg = open_ & gap
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                door_near |= np.roll(np.roll(dg, dy, 0), dx, 1)
        def opn(dx, dy):
            return ~sol(dx, dy)
        v, u = np.mgrid[0:PX, 0:PX]
        tri = {"tl": (u + v) < PX, "tr": ((PX - 1 - u) + v) < PX, "bl": (u + (PX - 1 - v)) < PX, "br": ((PX - 1 - u) + (PX - 1 - v)) < PX}
        # Only cut a corner that is part of a real staircase: the wall carries on diagonally on at least one
        # side. Cutting the lone corner at the end of a straight wall made sawtooth ends and odd notches.
        cut = {"tl": opn(-1, 0) & opn(0, -1) & opn(-1, -1) & (sol(-1, 1) | sol(1, -1)),
               "tr": opn(1, 0) & opn(0, -1) & opn(1, -1) & (sol(1, 1) | sol(-1, -1)),
               "bl": opn(-1, 0) & opn(0, 1) & opn(-1, 1) & (sol(-1, -1) | sol(1, 1)),
               "br": opn(1, 0) & opn(0, 1) & opn(1, 1) & (sol(1, -1) | sol(-1, 1))}
        for k_, m_ in cut.items():
            # (22 Nov) door_near was worked out but never used, so the wall either side of a doorway or lift
            # was cut into a triangle that looked walkable and wasn't, e.g. the core entrance on the Survey
            # Level and the Engineering lift. Those tiles now stay square, matching where you can walk.
            m_ = tiles & m_ & ~door_near
            for ty, tx in zip(*np.nonzero(m_)):
                B[ty * PX:(ty + 1) * PX, tx * PX:(tx + 1) * PX] &= ~tri[k_]
    if style == "smooth":
        B &= ~np.repeat(np.repeat(open_ & gap, PX, 0), PX, 1)
    def up(m, k):                       # m moved up by k pixels (row y takes row y+k)
        out = np.zeros_like(m); out[:H - k] = m[k:]; return out
    def down(m, k):
        out = np.zeros_like(m); out[k:] = m[:H - k]; return out
    def left(m, k=1):
        out = np.zeros_like(m); out[:, :W - k] = m[:, k:]; return out
    def right(m, k=1):
        out = np.zeros_like(m); out[:, k:] = m[:, :W - k]; return out
    roof_lift = up(B, PX)
    Wl = B | roof_lift
    face = Wl & ~up(B, 2 * PX)
    roof = Wl & ~face
    # Where each face pixel's wall meets the floor (its bottom edge), scanning up from the bottom.
    bottom = np.full((H, W), -1, dtype=np.int32)
    edge = B & ~up(B, 1)
    last = np.full(W, -1, dtype=np.int32)
    for y in range(H - 1, -1, -1):
        last = np.where(edge[y], y, last)
        last = np.where(Wl[y], last, -1)
        bottom[y] = last
    yy, xx = np.mgrid[0:H, 0:W]
    out = np.zeros((H, W, 4), dtype=np.float32)
    home = is_home(key)
    cozy = home or key in COZY_EDGES or cave_edges(key) is not None              # warm shading: AO, room falloff, lamp light
    roof_name, wall_name = SECTOR_WALLS.get(key, ("home/roof", "home/wall") if home else ("material_1", "material_2"))
    mat_roof = np.asarray(Image.open(os.path.join(art_dir, roof_name + ".png")).convert("RGB"), dtype=np.float32) / 255.0
    mat_wall = np.asarray(Image.open(os.path.join(art_dir, wall_name + ".png")).convert("RGB"), dtype=np.float32) / 255.0
    plain = key == "main" or key in SECTOR_WALLS or home                           # sector materials are used as painted, no tints
    varied_walls = key in ("main", "eng", "bay", "mine") or roof_name in ("lush/roof", "steam/roof", "home/roof", "promenade/roof", "hotel/cap_mix", "arrivals/roof", "east/roof", "agri/roof", "material_1", "mine_roof", "lake/roof")
    # roof: the material, tinted by roof plate
    zone = ROOF_ZONE_FN[key](xx / float(PX), (yy + PX) / float(PX)) if key in ROOF_ZONE_FN else _roof_zone(key, xx // PX, (yy + PX) // PX)
    tint = np.stack([hexc(h) for h in (["ffffff"] * 4 if plain else ROOF_TINTS)])[zone % 4]
    rc = _tex_lookup(mat_roof, yy + PX, xx) * tint
    if varied_walls:
        indices = ((xx // (2*PX))*7 + ((yy+PX) // (2*PX))*3) % 11
        for index, suffix in ((3, "_a"), (8, "_b")):
            mask = roof & (indices == index)
            tile = np.asarray(Image.open(os.path.join(art_dir, roof_name + suffix + ".png"))) / 255.
            rc[mask] = tile[(yy[mask]+PX) % (2*PX), xx[mask] % (2*PX)]
    for hf_ in HOUSE_FRONTS.get(key, []):
        hx0, hy0, hx1, hy1 = hf_["roof"]
        ctl, ctr, cbl, cbr = hf_["cuts"]
        mr_ = np.asarray(Image.open(os.path.join(art_dir, hf_["roof_art"] + ".png")).convert("RGB"), dtype=np.float32) / 255.0
        rx_, ry_ = xx + .5, yy + PX + .5                              # the roof pixel's place on the tile grid
        l_, r_ = rx_ - hx0 * PX, (hx1 + 1) * PX - rx_
        t_, b_ = ry_ - hy0 * PX, (hy1 + 1) * PX - ry_
        in_ = roof & (l_ >= 0) & (r_ >= 0) & (t_ >= 0) & (b_ >= 0) & (l_ + t_ >= ctl * PX) & (r_ + t_ >= ctr * PX) \
            & (l_ + b_ >= cbl * PX) & (r_ + b_ >= cbr * PX)
        rc[in_] = _tex_lookup(mr_, yy + PX, xx)[in_]
    out[roof, :3] = rc[roof]
    # wall face: the material stretched over 32 pixels, or the window view where the wall is a window
    by = np.clip(bottom, 0, H - 1)
    v = np.clip(2 * PX - 1 - (by - yy), 0, 2 * PX - 1)               # 0 at the top of the face, down to its foot
    fty, ftx = by // PX, xx // PX
    wt = np.stack([hexc(h) for h in (["ffffff"] * 3 if plain else WALL_TINTS)])[np.abs(((ftx // 3) * 73856093) ^ (fty * 19349663)) % 3]
    # The wall texture is 2 tiles square and covers the 2-tile-tall face once top to bottom.
    fc = mat_wall[(v * mat_wall.shape[0]) // (2 * PX), ((xx % (2 * PX)) * mat_wall.shape[1]) // (2 * PX)] * wt
    if key == "hotel":
        # End-to-end wall modules follow the corridor; the unfinished wings show bare ribs.
        fc = mat_wall[v, xx % mat_wall.shape[1]]
        wing = face & (by >= 62*PX)
        steel = np.asarray(Image.open(os.path.join(art_dir, "hotel/exposed_steel_mix.png"))) / 255.
        fc[wing] = steel[v[wing], xx[wing] % steel.shape[1]]
    if varied_walls:
        indices = ((xx // (2*PX))*7 + (by // PX)*3) % 11
        for index, suffix in ((3, "_a"), (8, "_b")):
            mask = face & (indices == index)
            if key == "hotel": mask &= ~wing                         # no paintings or sconces on the bare ribs
            tile = np.asarray(Image.open(os.path.join(art_dir, wall_name + suffix + ".png"))) / 255.
            fc[mask] = tile[v[mask], xx[mask] % (2*PX)]
    for hf_ in HOUSE_FRONTS.get(key, []):
        hx0, hy0, hx1, hy1 = hf_["front"]
        mw_ = np.asarray(Image.open(os.path.join(art_dir, hf_["wall_art"] + ".png")).convert("RGB"), dtype=np.float32) / 255.0
        in_ = face & (ftx >= hx0) & (ftx <= hx1) & (fty >= hy0) & (fty <= hy1 + 1)
        fw_ = mw_[(v * mw_.shape[0]) // (2 * PX), ((xx % (2 * PX)) * mw_.shape[1]) // (2 * PX)]
        fc[in_] = fw_[in_]
    if window is not None:
        win = np.asarray(window.convert("RGB"), dtype=np.float32) / 255.0
        is_win = chars[np.clip(fty, 0, th - 1), np.clip(ftx, 0, tw - 1)] == ord("w")
        wc = win[np.clip(v, 0, win.shape[0] - 1), np.clip(xx, 0, win.shape[1] - 1)]
        fc = np.where(is_win[..., None], wc, fc)
    if cozy:
        # Cozy depth on the wall face: lit just under the cornice, darker towards the floor, with a soft
        # occlusion where a face runs into a wall that comes forward at either end.
        if cave_edges(key) is not None:
            # Rock faces: an overhang shadow just under the lip, then darker the lower the face goes.
            g = np.clip(1.02 - (v / (2.0 * PX - 1)) * .42, .58, 1.02) * (.7 + .3 * np.clip((v - 2) / 7.0, 0, 1))
        else:
            g = np.clip(1.08 - (v / (2.0 * PX - 1)) * .3, .78, 1.08)
        fc = fc * g[..., None]
        from scipy.ndimage import distance_transform_edt
        side = np.zeros((H, W), np.float32)
        for k in range(1, 7):
            side = np.maximum(side, ((right(Wl & ~face, k) | left(Wl & ~face, k)) & face) * (1 - (k - 1) / 6.0))
        fc = fc * (1 - .3 * side[..., None])
    out[face, :3] = fc[face]
    out[Wl, 3] = 1.0
    # seams between roof plates
    E = HOME_EDGES if home else COZY_EDGES.get(key) or cave_edges(key) or COOL_EDGES
    zr = left(zone.astype(np.int32)); seam_x = roof & left(roof) & (zone != zr)
    out[seam_x, :3] = hexc(E["seam"]); out[right(seam_x), :3] = np.where(right(roof)[right(seam_x)][:, None], hexc(E["seam_hi"]), out[right(seam_x), :3])
    zd = up(zone.astype(np.int32), 1); seam_y = roof & up(roof, 1) & (zone != zd)
    out[seam_y, :3] = hexc(E["seam"])
    # edges: dark on the left side of a wall, light on the right, an outline round the roof's top, a lip
    # where roof meets face, and a dark line where the face meets the floor
    lft = Wl & ~right(Wl); out[lft | (Wl & right(lft)), :3] = hexc(E["left"])
    rgt = Wl & ~left(Wl); out[rgt | (Wl & left(rgt)), :3] = hexc(E["right"])
    top = roof & ~down(Wl, 1); out[top, :3] = hexc(E["top"]); out[roof & down(top, 1), :3] = hexc(E["top_hi"])
    lip = face & down(roof, 1); out[lip, :3] = hexc(E["lip"]); out[face & down(lip, 1), :3] = hexc(E["lip_lo"])
    foot = face & ~up(face, 1) & up(~Wl, 1); out[foot, :3] = hexc(E["foot"])
    # soft shadow on the floor in front of each wall face
    if cozy:
        # Cozy shading on the floor: ambient occlusion that fades out from every wall, deeper in front of the
        # wall faces, a gentle darkening towards the edges of each room, and warm pools of light under the lamps.
        from scipy.ndimage import distance_transform_edt
        floor = ~Wl & (chars[np.clip(yy // PX, 0, th - 1), np.clip(xx // PX, 0, tw - 1)] != ord("~"))
        d = distance_transform_edt(~B)
        mood = cave_mood(key)
        below = np.zeros((H, W), np.float32)
        for k in range(1, 21):
            below = np.maximum(below, down(B, k) * (1 - (k - 1) / 20.0) ** 1.5)
        if mood:
            # Caves: deeper, cooler occlusion that reaches further from the rock, and the dark of the cave itself.
            a = .46 * np.exp(-d / 14.0) + .26 * np.clip(1 - d / 64.0, 0, 1) + mood["dark"] + .3 * below
            a = np.where(floor, np.clip(a, 0, .8), 0)
            out[floor, :3] = mood["ao"]; out[floor, 3] = a[floor]
        else:
            a = .42 * np.exp(-d / 7.0) + .16 * np.clip(1 - d / 72.0, 0, 1)
            a = a + .24 * below
            a = np.where(floor, np.clip(a, 0, .62), 0)
            out[floor, :3] = (0.22, 0.1, 0.08); out[floor, 3] = a[floor]
        # light pools: under the wall lamps (the _b wall variant), a warm glow on the floor
        lamp = face & (((xx // (2*PX))*7 + (by // PX)*3) % 11 == 8)
        foot_lamp = lamp & ~up(face, 1) & up(~Wl, 1)
        ly, lx = np.nonzero(foot_lamp)
        if len(lx):
            cols = {}
            for y_, x_ in zip(ly, lx): cols.setdefault((x_ // (2*PX), y_), []).append(x_)
            dry = chars[np.clip(yy // PX, 0, th - 1), np.clip(xx // PX, 0, tw - 1)] != ord("Y")
            for (_, y_), xs_ in cols.items():
                if max(xs_) - min(xs_) < 30: continue                # straight walls only, not the 45-degree ones
                cx = (min(xs_) + max(xs_)) / 2.0
                r_ = ((xx - cx) / 26.0) ** 2 + ((yy - (y_ + 8)) / 14.0) ** 2
                glow = floor & (r_ < 1) & (yy > y_) & dry
                k_ = (1 - r_[glow]) * .3
                base = out[glow, :3] * out[glow, 3][:, None]
                warm = np.array(mood["lamp"] if mood else (1.0, .82, .52))
                na = np.clip(out[glow, 3] * (1 - k_) + k_, 0, 1)
                out[glow, :3] = (base * (1 - k_)[:, None] + warm * k_[:, None]) / np.maximum(na, 1e-6)[:, None]
                out[glow, 3] = na
        if mood:
            _cave_atmosphere(key, out, floor, face, B, d, chars, E, mood, xx, yy, th, tw)
    else:
        shadow = ~Wl & (down(B, 1) | down(B, 2) | down(B, 3) | down(B, 4))
        out[shadow, :3] = (0.1, 0.12, 0.18); out[shadow, 3] = 0.22
    # The top of a thick wall leans one tile up over the floor north of it (the bottom row of the room above).
    # People there walk under it, so that part goes in a layer drawn in front of them (walls_<key>_top.png,
    # area.gd), except round doors, which are drawn among the people themselves (Zachary, 22 Nov).
    global LAST_TOP
    over = roof & ~B
    cutm = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in DOOR_CUTS.get(key, []):
        cutm[max(0, int(y0 * PX)):max(0, int(y1 * PX)), max(0, int(x0 * PX)):max(0, int(x1 * PX))] = True
    over &= ~cutm
    del cutm
    img8 = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    del out
    top = np.zeros_like(img8); top[over] = img8[over]
    LAST_TOP = Image.fromarray(top, "RGBA")
    return Image.fromarray(img8, "RGBA")


DOOR_CUTS = {}      # key -> [(x0, y0, x1, y1) in tiles]: no overhead wall top here (doors), set by build.py
LAST_TOP = None     # the overhead part of the walls bake_walls made last


def _over(out, m, col, k):
    """Lay colour col over the overlay pixels m with strength k (per pixel), keeping it a proper alpha blend."""
    a0 = out[m, 3]; kk = np.clip(k, 0, 1)
    na = a0 + kk * (1 - a0)
    out[m, :3] = (out[m, :3] * (a0 * (1 - kk))[:, None] + np.asarray(col)[None, :] * kk[:, None]) / np.maximum(na, 1e-6)[:, None]
    out[m, 3] = na


def _cave_atmosphere(key, out, floor, face, B, d, chars, E, mood, xx, yy, th, tw):
    """Caves (22 Nov): a coloured haze drifting over the bare rock, rubble and grit piled at the foot of the walls,
    loose stones over the open floor, and pools of light round the lamps, fungus and crystals."""
    from scipy.ndimage import gaussian_filter, zoom
    H, W = floor.shape
    rnd = np.random.default_rng(abs(hash_key(key)) % (2 ** 31))
    tch = chars[np.clip(yy // PX, 0, th - 1), np.clip(xx // PX, 0, tw - 1)]
    rock = np.zeros((H, W), bool)
    for c in mood["rock"]:
        rock |= tch == ord(c)
    rock &= floor
    soft_rock = gaussian_filter(rock.astype(np.float32), 10)
    # haze: slow blotches of coloured air, thicker away from the lights (added below, after the lights)
    n = rnd.random((H // 24 + 3, W // 24 + 3)).astype(np.float32)
    n = gaussian_filter(n, 1.2)
    n = zoom(n, 24, order=1)[:H, :W]
    n = (n - n.min()) / max(1e-6, float(n.max() - n.min()))
    haze = np.clip((n - .15) / .85, 0, 1) ** 1.2 * mood["mist_a"] * soft_rock
    # rubble at the wall foot and grit over the open rock
    rock_hi, rock_lo, rock_mid = hexc(E["top_hi"]), hexc(E["foot"]), hexc(E["right"])
    def stone(x, y, w, h, base):
        if y + h + 1 >= H or x + w + 1 >= W or x < 1 or y < 1: return
        if not floor[y:y + h + 1, x:x + w + 1].all(): return
        out[y:y + h, x:x + w, :3] = base; out[y:y + h, x:x + w, 3] = 1.0
        out[y, x:x + w - 1, :3] = np.clip(base * .55 + rock_hi * .6, 0, 1)            # lit top
        out[y + h - 1, x + 1:x + w, :3] = base * .62                                    # shaded underside
        out[y + h, x + 1:x + w + 1, :3] = rock_lo; out[y + h, x + 1:x + w + 1, 3] = .55  # cast shadow
        out[y + 1:y + h, x + w, :3] = rock_lo; out[y + 1:y + h, x + w, 3] = np.maximum(out[y + 1:y + h, x + w, 3], .45)
    foot_band = rock & (d > 0.5) & (d < 13)
    ys, xs = np.nonzero(foot_band)
    if len(xs):
        pick = rnd.choice(len(xs), size=min(len(xs), len(xs) // 18), replace=False)
        for i in pick:
            near = d[ys[i], xs[i]] < 6
            w = int(rnd.integers(3, 7 if near else 5)); h = max(2, w - int(rnd.integers(1, 3)))
            base = np.clip(rock_mid * rnd.uniform(.62, .95), 0, 1)
            stone(int(xs[i]), int(ys[i]), w, h, base)
    open_rock = rock & (d >= 9)
    ys, xs = np.nonzero(open_rock)
    if len(xs):
        pick = rnd.choice(len(xs), size=len(xs) // 700, replace=False)
        for i in pick:
            stone(int(xs[i]), int(ys[i]), int(rnd.integers(2, 4)), 2, np.clip(rock_mid * rnd.uniform(.6, .9), 0, 1))
    # light: lantern variants on the walls are done above; here the map's own lamps, fungus and crystals
    lit = np.zeros((H, W), np.float32)
    for (lx, ly, kind, rad) in CAVE_LIGHTS.get(key, []):
        col, strength = LIGHT_COLOURS[kind]
        cx, cy = lx * PX, ly * PX
        R = rad * PX
        y0, y1 = int(max(0, cy - R)), int(min(H, cy + R + 1)); x0, x1 = int(max(0, cx - R)), int(min(W, cx + R + 1))
        if y0 >= y1 or x0 >= x1: continue
        sub = (slice(y0, y1), slice(x0, x1))
        r_ = np.hypot(xx[sub] - cx, (yy[sub] - cy) * 1.25) / R
        k = np.clip(1 - r_, 0, 1) ** 1.7
        lit[sub] = np.maximum(lit[sub], k)
        fl = floor[sub] & (k > 0)
        if fl.any():
            o = out[sub]
            o[fl, 3] *= (1 - .92 * k[fl])                        # lift the dark
            _over(o, fl, col, k[fl] * strength)
            out[sub] = o
        fa = face[sub] & (k > 0)                                # and light the rock face beside it
        if fa.any():
            o = out[sub]
            o[fa, :3] = np.clip(o[fa, :3] * (1 + .55 * k[fa, None]) + np.asarray(col)[None, :] * .12 * k[fa, None], 0, 1)
            out[sub] = o
    haze *= (1 - .7 * np.clip(lit, 0, 1))
    m = floor & (haze > .004)
    _over(out, m, mood["mist"], haze[m])


def hash_key(key):
    h = 7
    for c in key: h = (h * 131 + ord(c)) % 1000003
    return h


def wall_border_chars(rows):
    """Wall tiles next to floor take their neighbours' floor character, so the floor picture also covers
    the bits of wall tile the smoothed walls leave open."""
    rows = [list(r) for r in rows]
    th, tw = len(rows), len(rows[0])
    out = [r[:] for r in rows]
    for y in range(th):
        for x in range(tw):
            if rows[y][x] in SOLID:
                seen = {}
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if 0 <= y + dy < th and 0 <= x + dx < tw and rows[y + dy][x + dx] not in SOLID + "~":
                            c = rows[y + dy][x + dx]; seen[c] = seen.get(c, 0) + (2 if dx == 0 or dy == 0 else 1)
                if seen:
                    out[y][x] = max(seen, key=seen.get)
    return ["".join(r) for r in out]


def bay_window_strip(map_width, art_dir):
    """Use the quiet view's first native frame for the static wall bake."""
    with Image.open(os.path.join(art_dir, "bay_sky", "quiet.png")) as atlas:
        if atlas.width != map_width * PX or atlas.height % (2 * PX):
            raise ValueError("Shuttle Bay window atlas does not fit the current map")
        return atlas.crop((0, 0, atlas.width, 2 * PX))


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    style = sys.argv[3] if len(sys.argv) > 3 else "new"
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "art", "lunar", "floor_main.png")
    bake(rows_from_map_data(os.path.join(root, "scripts", "map_data.gd")), os.path.join(root, "art", "lunar"), style).save(out)
    print("floor picture:", out)
