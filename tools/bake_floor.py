"""Bakes the promenade's floor picture (art/lunar/floor_main.png) ahead of time.

The game used to work this out pixel by pixel in GDScript (scripts/lunar_paving.gd) the first time you
entered the main level: about eleven million pixels, which is why loading the level took so long. This is
the same calculation in Python with numpy, run by tools/build.py. scripts/lunar_paving.gd is kept as the
reference and as a fallback when the picture is missing.

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


def bake(rows, art_dir, style="new", strip=128):
    baker = Baker(art_dir)
    H, W = len(rows) * 16, len(rows[0]) * 16
    if style != "v11":
        rows = wall_border_chars(rows)
    chars = np.array([[ord(c) for c in row] for row in rows], dtype=np.int32)
    img = np.zeros((H, W, 4), dtype=np.uint8)
    smooth = lambda t: t * t * (3 - 2 * t)
    for y0 in range(0, H, strip):
        y, x = np.mgrid[y0:min(H, y0 + strip), 0:W]
        ch = chars[y // 16, x // 16]
        draw = ~np.isin(ch, [ord(c) for c in "#Wz~"])
        if not draw.any():
            continue
        x, y, ch = x[draw], y[draw], ch[draw]
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
        pocket = np.maximum(wp, np.maximum(wh, wu))
        kind = np.where(pocket > 0.5, np.where(wp == pocket, 3, np.where(wh == pocket, 4, 5)), kind)
        on_route = (radius < 174) | ((route < 40) & ((radius < 480) | (ch == ord(".")) | (ch == ord("a"))))
        on_route |= fore > 0                                   # forecourts are paved like the walks
        kind = np.where(on_route, 1, kind)
        color = baker.swatch(kind, x, y)
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
        rgb = np.clip(color * 255.0, 0, 255).astype(np.uint8)
        img[y, x, :3] = rgb; img[y, x, 3] = 255
    return Image.fromarray(img, "RGBA")


def rows_from_map_data(path):
    src = open(path, encoding="utf-8").read()
    i = src.index('"main": {', src.index("const AREAS"))
    a = src.index('"floor": [', i)
    return json.loads(re.sub(r",\s*\]$", "]", src[a + 9: src.index("]", a) + 1]))


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    style = sys.argv[3] if len(sys.argv) > 3 else "new"
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(root, "art", "lunar", "floor_main.png")
    bake(rows_from_map_data(os.path.join(root, "scripts", "map_data.gd")), os.path.join(root, "art", "lunar"), style).save(out)
    print("floor picture:", out)


# ---------------------------------------------------------------- other levels in the promenade style
# Each floor character gets one of the six paving families (0 hex, 1 ivory, 2 sage, 3 decking, 4 stone,
# 5 blue-grey slabs), optionally tinted.
AREA_FLOORS = {
    "top": {"i": (0, None), "f": (3, None), ".": (1, None), "D": (1, None)},
    "lounge": {"u": (5, None)},
    "museum": {"h": (4, None), ".": (1, None), "f": (3, None)},
    "sanctum": {"s": (4, ("6f5a9a", 0.32)), "i": (0, ("8a6fc0", 0.30))},
    "eng": {".": (5, ("5f6a78", 0.30)), "f": (4, ("8a8f96", 0.25)), "R": (3, ("6a5a4c", 0.35)), "i": (5, ("5f6a78", 0.30)), "U": (5, None),
            "o": (4, ("8a6e58", 0.30)), "k": (5, ("6a3a2c", 0.45)), "q": (5, ("140e12", 0.88)), "j": (5, ("4a4e58", 0.35)),
            "a": (1, ("d8b070", 0.25)), "h": (3, ("b08a68", 0.15))},
    "bay": {"u": (5, ("7a828c", 0.22)), "a": (1, ("d8b070", 0.25)), "p": (3, None), "f": (4, None), "i": (5, None)},
}


def bake_area(key, rows, art_dir, extras=None):
    baker = Baker(art_dir)
    table = AREA_FLOORS[key]
    rows = wall_border_chars(rows)
    H, W = len(rows) * 16, len(rows[0]) * 16
    chars = np.array([[ord(c) for c in row] for row in rows], dtype=np.int32)
    y, x = np.mgrid[0:H, 0:W]
    ch = chars[y // 16, x // 16]
    img = np.zeros((H, W, 4), dtype=np.uint8)
    for c, (kind, tint) in table.items():
        m = ch == ord(c)
        if not m.any():
            continue
        xs, ys = x[m], y[m]
        col = baker.swatch(np.full(xs.shape, kind), xs, ys)
        if tint:
            col = lerp(col, hexc(tint[0]), tint[1])
        img[ys, xs, :3] = np.clip(col * 255.0, 0, 255).astype(np.uint8); img[ys, xs, 3] = 255
    extras = extras or {}
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
    if "core" in extras:
        _engineering_extras(img, ch, x, y, extras)
    return Image.fromarray(img, "RGBA")


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


def window_strip(width_px, planet_x, seed=7):
    """The view through a long curved window: one strip 32 pixels tall across the whole level, so the
    gas giant lines up from one window tile to the next. Frame and sill top and bottom, mullions every tile."""
    import random
    rnd = random.Random(seed)
    W, H = width_px, 32
    img = np.zeros((H, W, 4), dtype=np.uint8)
    y, x = np.mgrid[0:H, 0:W]
    sky = np.stack([10 + y * 0.6, 14 + y * 0.8, 34 + y * 1.4], axis=-1)
    img[..., :3] = sky.astype(np.uint8); img[..., 3] = 255
    for _ in range(W // 6):                                   # stars
        sx, sy = rnd.randrange(W), rnd.randrange(6, 26)
        img[sy, sx, :3] = (230, 232, 250) if rnd.random() < .7 else (250, 220, 170)
    # The gas giant: a big disc rising from below, banded blue and white.
    cx, cy, R = planet_x, 300.0, 320.0
    d = np.hypot(x + .5 - cx, y + .5 - cy)
    inside = d < R
    band = ((y + (x - cx) ** 2 / 2600.0) / 3.0).astype(int) % 5
    pal = np.array([[96, 150, 206], [150, 196, 232], [74, 120, 186], [196, 222, 240], [110, 166, 214]], dtype=np.uint8)
    col = pal[band]
    shade = np.clip(1.0 - (d / R) ** 6 * 0.35, 0, 1)[..., None]
    img[inside, :3] = (col[inside] * shade[inside]).astype(np.uint8)
    rim = inside & (d > R - 2.2)
    img[rim, :3] = (210, 236, 250)
    # frame: lintel, sill and a mullion on every tile edge
    img[0:5, :, :3] = (176, 168, 150); img[5, :, :3] = (90, 96, 112)
    img[H - 6:H, :, :3] = (176, 168, 150); img[H - 7, :, :3] = (220, 214, 196)
    for mx in range(0, W, 16):
        img[:, mx:mx + 2, :3] = (150, 144, 128)
    return Image.fromarray(img, "RGBA")


# ---------------------------------------------------------------- smooth walls
# Walls used to be drawn tile by tile, so every curve and every 45-degree wall was a staircase. Here the
# tile map's walls are smoothed (a soft blur of the solid tiles, cut at half way), which turns stairs into
# straight diagonals and steps into curves, and then drawn the way the game drew them: a roof lifted 16
# pixels, a wall face 32 pixels tall wherever floor lies in front, side edges, seams between roof plates
# and a soft shadow on the floor. Collision is still the tile grid. The game draws this picture over the
# floor (scripts/lunar_ground.gd); repainting material_1.png (roof) or material_2.png (wall face) still works.
SOLID = "#Wzw"
WALL_TINTS = ["ffffff", "e1e7ec", "ede2d5"]
ROOF_TINTS = ["ffffff", "dbe4ee", "f0e9df", "c6d3e2"]


def _roof_zone(key, tx, ty):
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


def bake_walls(key, rows, art_dir, window=None, sigma=15.0, style="facet"):
    from scipy.ndimage import gaussian_filter
    rows = ["".join(r) for r in rows]
    th, tw = len(rows), len(rows[0])
    H, W = th * 16, tw * 16
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
        B = gaussian_filter(np.repeat(np.repeat(tiles.astype(np.float32), 16, 0), 16, 1), sigma, mode="constant", cval=0.0) > 0.5
    else:
        # Faceted: every edge is straight or exactly 45 degrees. A wall tile open on two neighbouring sides
        # (and on the corner between them) loses that corner as a half-tile triangle, so a staircase of
        # single steps becomes one straight diagonal. The tiles beside a doorway stay square.
        B = np.repeat(np.repeat(tiles, 16, 0), 16, 1)
        door_near = np.zeros_like(tiles)
        dg = open_ & gap
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                door_near |= np.roll(np.roll(dg, dy, 0), dx, 1)
        def opn(dx, dy):
            return ~sol(dx, dy)
        v, u = np.mgrid[0:16, 0:16]
        tri = {"tl": (u + v) < 16, "tr": ((15 - u) + v) < 16, "bl": (u + (15 - v)) < 16, "br": ((15 - u) + (15 - v)) < 16}
        cut = {"tl": opn(-1, 0) & opn(0, -1) & opn(-1, -1), "tr": opn(1, 0) & opn(0, -1) & opn(1, -1),
               "bl": opn(-1, 0) & opn(0, 1) & opn(-1, 1), "br": opn(1, 0) & opn(0, 1) & opn(1, 1)}
        for k_, m_ in cut.items():
            m_ = tiles & m_ & ~door_near
            for ty, tx in zip(*np.nonzero(m_)):
                B[ty * 16:(ty + 1) * 16, tx * 16:(tx + 1) * 16] &= ~tri[k_]
    if style == "smooth":
        B &= ~np.repeat(np.repeat(open_ & gap, 16, 0), 16, 1)
    def up(m, k):                       # m moved up by k pixels (row y takes row y+k)
        out = np.zeros_like(m); out[:H - k] = m[k:]; return out
    def down(m, k):
        out = np.zeros_like(m); out[k:] = m[:H - k]; return out
    def left(m, k=1):
        out = np.zeros_like(m); out[:, :W - k] = m[:, k:]; return out
    def right(m, k=1):
        out = np.zeros_like(m); out[:, k:] = m[:, :W - k]; return out
    roof_lift = up(B, 16)
    Wl = B | roof_lift
    face = Wl & ~up(B, 32)
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
    mat_roof = np.asarray(Image.open(os.path.join(art_dir, "material_1.png")).convert("RGB"), dtype=np.float32) / 255.0
    mat_wall = np.asarray(Image.open(os.path.join(art_dir, "material_2.png")).convert("RGB"), dtype=np.float32) / 255.0
    # roof: the material, tinted by roof plate
    zone = _roof_zone(key, xx // 16, (yy + 16) // 16)
    tint = np.stack([hexc(h) for h in ROOF_TINTS])[zone % 4]
    rc = mat_roof[(yy + 16) % 64, xx % 64] * tint
    out[roof, :3] = rc[roof]
    # wall face: the material stretched over 32 pixels, or the window view where the wall is a window
    by = np.clip(bottom, 0, H - 1)
    v = np.clip(31 - (by - yy), 0, 31)
    fty, ftx = by // 16, xx // 16
    wt = np.stack([hexc(h) for h in WALL_TINTS])[np.abs(((ftx // 3) * 73856093) ^ (fty * 19349663)) % 3]
    fc = mat_wall[v * 2, (xx % 32) * 2] * wt
    if window is not None:
        win = np.asarray(window.convert("RGB"), dtype=np.float32) / 255.0
        is_win = chars[np.clip(fty, 0, th - 1), np.clip(ftx, 0, tw - 1)] == ord("w")
        wc = win[np.clip(v, 0, win.shape[0] - 1), np.clip(xx, 0, win.shape[1] - 1)]
        fc = np.where(is_win[..., None], wc, fc)
    out[face, :3] = fc[face]
    out[Wl, 3] = 1.0
    # seams between roof plates
    zr = left(zone.astype(np.int32)); seam_x = roof & left(roof) & (zone != zr)
    out[seam_x, :3] = hexc("36434f"); out[right(seam_x), :3] = np.where(right(roof)[right(seam_x)][:, None], hexc("a9b6c2"), out[right(seam_x), :3])
    zd = up(zone.astype(np.int32), 1); seam_y = roof & up(roof, 1) & (zone != zd)
    out[seam_y, :3] = hexc("36434f")
    # edges: dark on the left side of a wall, light on the right, an outline round the roof's top, a lip
    # where roof meets face, and a dark line where the face meets the floor
    lft = Wl & ~right(Wl); out[lft | (Wl & right(lft)), :3] = hexc("394756")
    rgt = Wl & ~left(Wl); out[rgt | (Wl & left(rgt)), :3] = hexc("7c828a")
    top = roof & ~down(Wl, 1); out[top, :3] = hexc("2b3442"); out[roof & down(top, 1), :3] = hexc("b8c4cf")
    lip = face & down(roof, 1); out[lip, :3] = hexc("dcc1a1"); out[face & down(lip, 1), :3] = hexc("59667b")
    foot = face & ~up(face, 1) & up(~Wl, 1); out[foot, :3] = hexc("2b3442")
    # soft shadow on the floor in front of each wall face
    shadow = ~Wl & (down(B, 1) | down(B, 2) | down(B, 3) | down(B, 4))
    out[shadow, :3] = (0.1, 0.12, 0.18); out[shadow, 3] = 0.22
    return Image.fromarray(np.clip(out * 255.0, 0, 255).astype(np.uint8), "RGBA")


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


def crater_strip(width_px, seed=5):
    """The view out of the shuttle bay's windows: black sky and stars, the gas giant low on one side, the far
    rim of the crater, and the grey crater floor close up. One strip 32 pixels tall across the whole map."""
    import random
    rnd = random.Random(seed)
    W, H = width_px, 32
    img = np.zeros((H, W, 4), dtype=np.uint8)
    y, x = np.mgrid[0:H, 0:W]
    img[..., :3] = np.stack([6 + y * 0.5, 8 + y * 0.6, 20 + y * 1.0], axis=-1).astype(np.uint8); img[..., 3] = 255
    for _ in range(W // 5):
        sx, sy = rnd.randrange(W), rnd.randrange(6, 20)
        img[sy, sx, :3] = (230, 232, 250)
    cx, cy, R = W * 0.78, 200.0, 190.0
    d = np.hypot(x + .5 - cx, y + .5 - cy); inside = d < R
    band = ((y + (x - cx) ** 2 / 3000.0) / 3.0).astype(int) % 5
    pal = np.array([[96, 150, 206], [150, 196, 232], [74, 120, 186], [196, 222, 240], [110, 166, 214]], dtype=np.uint8)
    img[inside, :3] = pal[band][inside]
    # far crater rim: a ragged grey line, then the near floor
    rim = 18 + (np.sin(x / 37.0) * 2 + np.sin(x / 11.0 + 1.3) * 1.2).astype(int)
    far = (y >= rim) & (y < 22)
    img[far, :3] = (118, 114, 124)
    near = y >= 22
    shade = (150 - (y - 22) * 3).clip(100, 160)
    img[near, 0] = shade[near]; img[near, 1] = (shade - 6)[near]; img[near, 2] = (shade + 4)[near]
    for _ in range(W // 9):
        bx, by = rnd.randrange(W), rnd.randrange(23, 26)
        img[by:by + 1, bx:bx + 3, :3] = (96, 92, 100)
    img[0:5, :, :3] = (176, 168, 150); img[5, :, :3] = (90, 96, 112)
    img[H - 6:H, :, :3] = (176, 168, 150); img[H - 7, :, :3] = (220, 214, 196)
    for mx in range(0, W, 16):
        img[:, mx:mx + 2, :3] = (150, 144, 128)
    return Image.fromarray(img, "RGBA")
