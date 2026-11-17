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
    "museum": {"h": (4, None), "s": (4, ("6f5a9a", 0.32)), "f": (3, None)},
}


def bake_area(key, rows, art_dir, extras=None):
    baker = Baker(art_dir)
    table = AREA_FLOORS[key]
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
    return Image.fromarray(img, "RGBA")


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
