"""Roof pieces drawn as lit shapes (Zachary, 24 Nov: the code redraws were "low quality and not detailed or shaded").
Every shape writes a surface normal, a height and a colour ramp per pixel; one light from the upper left then picks
each pixel's tone, casts shadows across lower surfaces, adds a shine on metal and glass, and the outline goes on last.
That gives every bolt, leaf and pipe bend its own light and dark side instead of flat fills.
    python3 tools/dev/prop_art/lit_props.py art/lunar     -> the 11 roof_*.png pieces"""
import sys, os, math
import numpy as np
from PIL import Image

def H(s): return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)])
def R(*cs): return [H(c) for c in cs]

FRAME = R("fbf0dc", "e2cba6", "b9a08a", "8c7a80", "625670", "41374f")     # warm steel: cream light, purple dark
BRASS = R("fff5c4", "ffd76e", "eaa940", "c27b2c", "8e5026", "5e3020")
WARM = R("fff6cf", "ffe08c", "f8b85a", "d98a42", "a8603a", "6e3c3a")
TEALG = R("d8fbf4", "9fe0dc", "6cb6c0", "4a88a0", "36607e", "283f5e")
LEAF = R("eaffa0", "b8ea66", "80c44c", "529842", "356c3a", "23462f")
CABB = R("f6ffb4", "d6f272", "a8d452", "76aa44", "4c7c3c", "305236")
TOM = R("ffc09a", "ff7350", "d83c36", "9a2a32", "5e1e2c")
LAV = R("f8d8ff", "d6a0f4", "a86cd6", "7a4cae", "50347e")
SOIL = R("a8704e", "84523c", "623b32", "45282a", "2e1c22")
PIPE = R("f4e6ec", "d2bccc", "a68ea8", "7c6884", "564864", "392e48")
RUB = R("7a7494", "5a5474", "3e3a56", "2a263e")
GLOW = R("ffffff", "fffbe0", "fff0a0", "ffd860")
CYAN = R("e8ffff", "8cf2ff", "38c8e8", "2088b0")
RED = R("ffb0a0", "ff5a48", "c8303a", "7a2030")
CREAM = R("fffdf0", "f2e8d0", "d6c6aa", "a8947e")
OUT, OUT_D = H("4a2430"), H("2e1a2a")
L = np.array([-0.55, -0.7, 0.62]); L = L / np.linalg.norm(L)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


class Lit:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.n = np.zeros((h, w, 3)); s.n[..., 2] = 1
        s.z = np.zeros((h, w)); s.on = np.zeros((h, w), bool)
        s.ramp = np.full((h, w), None, object)
        s.shine = np.zeros((h, w)); s.dith = np.zeros((h, w), bool)
        s.bias = np.zeros((h, w)); s.fixed = np.full((h, w), None, object)
        s.cast = np.ones((h, w), bool)

    def put(s, x, y, nrm, z, ramp, shine=0.0, dith=False, bias=0.0):
        x, y = int(x), int(y)
        if not (0 <= x < s.w and 0 <= y < s.h): return
        v = np.asarray(nrm, float); v = v / (np.linalg.norm(v) + 1e-9)
        s.n[y, x] = v; s.z[y, x] = z; s.on[y, x] = True; s.ramp[y, x] = ramp
        s.shine[y, x] = shine; s.dith[y, x] = dith; s.bias[y, x] = bias; s.fixed[y, x] = None

    def paint(s, x, y, col):
        if 0 <= x < s.w and 0 <= y < s.h:
            s.fixed[y, x] = col; s.on[y, x] = True

    # ---- shapes -------------------------------------------------------------------------------------------
    def slab(s, x0, y0, x1, y1, z, ramp, bevel=1, shine=0.2, bias=0.0, dith=False):
        """A flat raised plate with bevelled edges (top-down)."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                nx = ny = 0.0
                if x - x0 < bevel: nx = -0.7
                elif x1 - x < bevel: nx = 0.7
                if y - y0 < bevel: ny = -0.7
                elif y1 - y < bevel: ny = 0.7
                s.put(x, y, (nx, ny, 1), z, ramp, shine, dith, bias)

    def face(s, x0, y0, x1, y1, z, ramp, bias=0.0):
        """A front (vertical) face in the three-quarter view: faces the viewer and slightly down."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                t = (y - y0) / max(1, y1 - y0)
                s.put(x, y, (0.3 if x1 - x < 1 else 0, 0.05 + 0.45 * t, 0.9), z, ramp, 0.0, True, bias)

    def dome(s, cx, cy, rx, ry, z0, zh, ramp, shine=0.5, bias=0.0):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                u, v = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                d = u * u + v * v
                if d > 1: continue
                w = math.sqrt(1 - d)
                s.put(x, y, (u, v, w * 1.2), z0 + zh * w, ramp, shine, False, bias)

    def bolt(s, x, y, z, ramp=BRASS):
        s.dome(x + 1, y + 1, 1.25, 1.25, z, 1, ramp, 0.9)

    def tube(s, pts, r, z0, ramp, shine=0.8, bias=0.0):
        """A pipe along a polyline of centre points (each pixel takes the nearest segment)."""
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        for y in range(int(min(ys) - r - 1), int(max(ys) + r + 2)):
            for x in range(int(min(xs) - r - 1), int(max(xs) + r + 2)):
                px, py = x + 0.5, y + 0.5; best = None
                for (ax, ay), (bx, by) in zip(pts, pts[1:]):
                    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1
                    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
                    qx, qy = ax + t * dx, ay + t * dy; d = math.hypot(px - qx, py - qy)
                    if best is None or d < best[0]: best = (d, px - qx, py - qy)
                d, ox, oy = best
                if d > r: continue
                w = math.sqrt(max(0, 1 - (d / r) ** 2))
                s.put(x, y, (ox / r, oy / r, w), z0 + r * w, ramp, shine, False, bias)

    def ring(s, cx, cy, r0, r1, z, ramp, shine=0.8):
        for y in range(int(cy - r1 - 1), int(cy + r1 + 2)):
            for x in range(int(cx - r1 - 1), int(cx + r1 + 2)):
                dx, dy = x + 0.5 - cx, y + 0.5 - cy; d = math.hypot(dx, dy)
                if not (r0 <= d <= r1): continue
                m = (r0 + r1) / 2; t = (d - m) / max(0.5, (r1 - r0) / 2)
                s.put(x, y, (dx / (d or 1) * t, dy / (d or 1) * t, 1), z + (1 - abs(t)), ramp, shine)

    # ---- light ------------------------------------------------------------------------------------------
    def render(s, shadow=0.3, outline=True):
        h, w = s.h, s.w
        lit = np.clip((s.n * L).sum(-1), 0, 1)
        val = 0.08 + 0.95 * lit
        yy, xx = np.mgrid[0:h, 0:w]
        val = val + 0.16 * (0.5 - (xx / w * 0.4 + yy / h * 0.6))      # C style: whole piece lit from the top left
        refl = 2 * (s.n * L).sum(-1)[..., None] * s.n - L
        spec = np.clip(refl[..., 2], 0, 1) ** 18
        val = val + s.shine * spec * 0.9 + s.bias
        # cast shadows: march toward the light; anything standing taller than the ray darkens this pixel
        sh = np.zeros((h, w), bool)
        rise = 0.9
        for y in range(h):
            for x in range(w):
                if not s.on[y, x]: continue
                z0 = s.z[y, x]
                for k in range(1, 6):
                    xx, yy = x - k, y - k
                    if xx < 0 or yy < 0: break
                    if s.on[yy, xx] and s.cast[yy, xx] and s.z[yy, xx] > z0 + k * rise + 0.6:
                        sh[y, x] = True; break
        val = np.where(sh, val - shadow, val)
        out = np.zeros((h, w, 4), np.uint8)
        for y in range(h):
            for x in range(w):
                if not s.on[y, x]: continue
                if s.fixed[y, x] is not None:
                    out[y, x, :3] = s.fixed[y, x]; out[y, x, 3] = 255; continue
                ramp = s.ramp[y, x]; n = len(ramp)
                f = (1 - min(1.0, max(0.0, val[y, x]))) * (n - 1)
                i = int(f); fr = f - i
                if s.dith[y, x] and 0.3 < fr < 0.7: i += 1 if fr > BAYER[y % 4, x % 4] else 0
                else: i = int(round(f))
                out[y, x, :3] = ramp[min(n - 1, max(0, i))]; out[y, x, 3] = 255
        # a dark line where a surface drops away below/right of a taller one (crisp pixel-art separation)
        for y in range(1, h):
            for x in range(1, w):
                if not s.on[y, x] or s.fixed[y, x] is not None: continue
                if (s.on[y - 1, x] and s.z[y - 1, x] - s.z[y, x] > 1.4) or (s.on[y, x - 1] and s.z[y, x - 1] - s.z[y, x] > 1.4):
                    r = s.ramp[y, x]; out[y, x, :3] = r[-1]
        if outline:
            sol = out[..., 3] > 0; o = out.copy()
            for y in range(h):
                for x in range(w):
                    if sol[y, x]: continue
                    nb = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                    hit = [(a, b) for a, b in nb if 0 <= a < w and 0 <= b < h and sol[b, a]]
                    if hit:
                        dark = any(b < y or a < x for a, b in hit) and not any(b > y for a, b in hit)
                        o[y, x, :3] = OUT_D if dark else OUT; o[y, x, 3] = 255
            out = o
        return out


def rng(seed):
    r = np.random.default_rng(seed)
    return r


# ---------------------------------------------------------------------------------------------------------
def curb(s, x0, y0, x1, y1, z=5, t=5, inner=1.0):
    """A raised frame around a recessed opening, rounded across its width like a rail: the outer edge leans out,
    the inner edge leans in, so the top-left rails catch a highlight and the inner bottom-right sides go dark."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            ds = {(-1, 0): x - x0, (1, 0): x1 - x, (0, -1): y - y0, (0, 1): y1 - y}
            d = min(ds.values())
            if d >= t: continue
            ox = sum(k[0] for k, v in ds.items() if v == d); oy = sum(k[1] for k, v in ds.items() if v == d)
            u = (d - (t - 1) / 2) / (t / 2)
            w = math.sqrt(max(0.0, 1 - u * u))
            s.put(x, y, (-u * ox * 1.1, -u * oy * 1.1, w + 0.15), z - 1 + w * 1.5, FRAME, 0.55, True, float(np.sin(x * 12.9 + y * 78.2) * 0.03))


def skylight():
    s = Lit(48, 48)
    g = rng(3)
    # the glass first (recessed, low), lit warm from the room below, cool sky sheen toward the top left
    for y in range(5, 43):
        for x in range(5, 43):
            cx, cy = (x - 24) / 19, (y - 25) / 19
            d = math.hypot(cx, cy)
            s.put(x, y, (0, 0, 1), 0, WARM, 0.0, True, 0.5 - 0.75 * d)
    curb(s, 0, 0, 47, 47, z=5, t=6)
    # cross mullion
    for i in range(6, 42):
        for k, nx in ((-1, -0.7), (0, -0.15), (1, 0.3), (2, 0.8)):
            s.put(23 + k, i, (nx, 0, 1), 3, FRAME, 0.4)
            s.put(i, 23 + k, (0, nx, 1), 3, FRAME, 0.4)
    s.slab(21, 21, 26, 26, 3.5, FRAME, 1, 0.5)
    s.bolt(22, 22, 4)
    # corner plates with bolts, hinge plates on the bottom edge, rivets along the frame
    for (cx, cy) in ((1, 1), (40, 1), (1, 40), (40, 40)):
        s.slab(cx, cy, cx + 6, cy + 6, 6, BRASS, 1, 0.5)
        s.bolt(cx + 2, cy + 2, 6.5)
    for x in (16, 30):
        s.slab(x, 43, x + 3, 46, 6, BRASS, 1, 0.4)
    for k in range(10, 39, 6):
        if abs(k - 24) < 3: continue
        s.dome(k + 0.5, 2.5, 0.9, 0.9, 5, 0.6, FRAME, 0.8)
        s.dome(2.5, k + 0.5, 0.9, 0.9, 5, 0.6, FRAME, 0.8)
        s.dome(45.5, k + 0.5, 0.9, 0.9, 5, 0.6, FRAME, 0.8)
    img = s.render()
    # sky reflections on the glass: a broad pale band and a thin streak in each upper-left pane
    sky = [np.array([255, 252, 236]), np.array([214, 238, 240]), np.array([170, 214, 222])]
    for (ox, oy) in ((6, 6), (25, 6), (6, 25), (25, 25)):
        for k in range(16):
            for j in range(3):
                x, y = ox + 2 + k - j, oy + 14 - k
                if ox <= x < ox + 17 and oy <= y < oy + 17 and s.z[y, x] == 0 and (k + j) % 7 != 6:
                    img[y, x, :3] = (img[y, x, :3] * 0.35 + sky[j] * 0.65).astype(np.uint8)
            x, y = ox + 8 + k, oy + 16 - k
            if k < 9 and ox <= x < ox + 17 and oy <= y < oy + 17 and s.z[y, x] == 0:
                img[y, x, :3] = (img[y, x, :3] * 0.4 + sky[1] * 0.6).astype(np.uint8)
    # weathering: a few scuffs on the frame top
    for _ in range(26):
        x, y = g.integers(1, 47), g.integers(1, 47)
        if s.z[y, x] == 5 and s.ramp[y, x] is FRAME:
            img[y, x, :3] = FRAME[3] if g.random() < 0.6 else FRAME[0]
    return img


def leaf(s, cx, cy, rx, ry, z, ramp, ang=0.0):
    ca, sa = math.cos(ang), math.sin(ang)
    for y in range(int(cy - 4), int(cy + 5)):
        for x in range(int(cx - 4), int(cx + 5)):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            u, v = (dx * ca + dy * sa) / rx, (-dx * sa + dy * ca) / ry
            d = u * u + v * v
            if d > 1: continue
            if s.on[y, x] and s.z[y, x] > z + math.sqrt(1 - d) * 1.5: continue
            w = math.sqrt(1 - d)
            s.put(x, y, (dx / rx * 0.8, dy / ry * 0.8, w + 0.3), z + 1.5 * w, ramp, 0.25)


def greenhouse():
    W, Hh = 96, 63
    s = Lit(W, Hh)
    g = rng(11)
    top = 46  # the glass box's top surface ends here; the planter's front face is below
    # soil beds
    for y in range(4, top - 3):
        for x in range(4, W - 4):
            s.put(x, y, (g.normal(0, 0.25), g.normal(0, 0.25), 1), 0, SOIL, 0, True, -0.05)
    # three bays of plants
    bays = [(6, 30), (35, 60), (65, 90)]
    # left: tomato vines in three rows on stakes
    for row in range(3):
        bx = 9 + row * 8
        for y in range(8, top - 6):
            s.put(bx, y, (0.4, 0, 1), 2, R("d8b080", "a87c58", "7a5640", "4e3a34"), 0.1)
        for k in range(14):
            y = 8 + k * 2.4 + g.uniform(-0.5, 0.5)
            side = -1 if k % 2 else 1
            leaf(s, bx + side * 2.2 + g.uniform(-0.6, 0.6), y, 2.6, 1.6, 2.5 + g.uniform(0, 1.5), LEAF, side * 0.5)
        for k in range(5):
            y = 12 + k * 6 + g.uniform(-1, 1)
            s.dome(bx + (1.6 if k % 2 else -1.6), y, 1.5, 1.5, 4.5, 1.5, TOM, 0.9)
    # middle: four big cabbage heads with outer leaves
    for (cx, cy) in ((41.5, 15), (53.5, 15), (41.5, 31), (53.5, 31)):
        for a in range(7):
            ang = a / 7 * math.tau + g.uniform(-0.2, 0.2)
            leaf(s, cx + math.cos(ang) * 4.3, cy + math.sin(ang) * 4.0, 3.2, 2.0, 1.5, LEAF, ang)
        s.dome(cx, cy, 4.4, 4.2, 3, 3.5, CABB, 0.35)
        for a in range(3):
            ang = a * 2.1 + 0.4
            for t in np.linspace(0.3, 0.95, 5):
                x, y = int(cx + math.cos(ang) * 4.2 * t), int(cy + math.sin(ang) * 4.0 * t)
                if s.ramp[y, x] is CABB: s.bias[y, x] -= 0.12
    # right: lavender bushes with purple spikes
    for (cx, cy) in ((70, 12), (82, 12), (76, 22), (70, 32), (82, 32), (88, 22), (64, 22)):
        for k in range(9):
            ang = k / 9 * math.tau
            leaf(s, cx + math.cos(ang) * 2.5, cy + math.sin(ang) * 2.3, 2.4, 1.2, 1.5, LEAF, ang + 1.57)
        for k in range(6):
            ang = k / 6 * math.tau + 0.3
            for t in range(4):
                s.dome(cx + math.cos(ang) * (1 + t * 1.1), cy + math.sin(ang) * (1 + t * 1.0) - t * 0.4, 1.0, 1.0, 3 + t * 0.5, 0.8, LAV, 0.6)
    # bay dividers (glazing bars), the frame, grow lights on each bay's top edge
    for bx in (32, 62):
        for y in range(3, top):
            for k, nx in ((-1, -0.7), (0, 0), (1, 0.6), (2, 0.9)):
                s.put(bx + k, y, (nx, 0, 1), 7, FRAME, 0.45)
    curb(s, 0, 0, W - 1, top, z=8, t=5)
    for (a, b) in ((10, 26), (41, 55), (71, 86)):
        s.slab(a, 1, b, 3, 9, R("ffffff", "fffbe0", "fff0a0", "ffd860", "d8a848"), 1, 0.2, 0.25)
    for (cx, cy) in ((0, 0), (W - 7, 0), (0, top - 6), (W - 7, top - 6)):
        s.slab(cx, cy, cx + 6, cy + 6, 9, BRASS, 1, 0.5)
        s.bolt(cx + 2, cy + 2, 9.5)
    # planter front face below the glass box
    s.face(0, top + 1, W - 1, Hh - 1, 8, FRAME)
    s.slab(0, top + 1, W - 1, top + 2, 8.5, FRAME, 1, 0.3, 0.12)
    for x in range(2, W - 2):
        s.put(x, Hh - 2, (0, 1, 0.3), 1, FRAME, 0, False, -0.15)
    for (a, b) in ((6, 22), (W - 23, W - 7)):
        for k in range(3):
            y = top + 6 + k * 3
            for x in range(a, b):
                s.put(x, y, (0, -0.8, 0.6), 7, FRAME, 0, False, -0.35)
                s.put(x, y + 1, (0, 0.6, 0.8), 7, FRAME, 0, False, 0.05)
    s.slab(37, top + 5, 58, top + 12, 9, CREAM, 1, 0.3)
    for (lx, col) in ((28, GLOW), (66, R("d6ffe0", "7dff9a", "40c870", "208a50"))):
        s.dome(lx + 1.5, top + 8.5, 1.8, 1.8, 9, 1, col, 1.0, 0.25)
    for x in (3, W - 5):
        for y in (top + 4, Hh - 5):
            s.bolt(x, y, 9)
    img = s.render()
    # glass: a faint cool sheen over the plants, one broad and one thin reflection per bay, label text
    sheen = np.array([210, 236, 246])
    for (a, b) in ((5, 31), (34, 61), (64, 91)):
        for y in range(5, top - 4):
            for x in range(a, b):
                if s.z[y, x] < 7:
                    img[y, x, :3] = (img[y, x, :3] * 0.86 + sheen * 0.14).astype(np.uint8)
        for k in range(30):
            for j in range(3):
                x, y = a + 3 + k - j, top - 6 - k
                if a <= x < b and 5 <= y < top - 4 and s.z[y, x] < 7 and k % 9 != 8:
                    img[y, x, :3] = (img[y, x, :3] * 0.5 + np.array([250, 252, 240]) * 0.5).astype(np.uint8)
            x, y = a + 12 + k, top - 6 - k
            if a <= x < b and 5 <= y < top - 4 and s.z[y, x] < 7 and k < 20:
                img[y, x, :3] = (img[y, x, :3] * 0.55 + np.array([240, 250, 250]) * 0.45).astype(np.uint8)
    for (a, b) in ((5, 31), (34, 61), (64, 91)):
        for x in range(a, b - 1):
            if s.z[5, x] < 7: img[5, x, :3] = (img[5, x, :3] * 0.4 + np.array([250, 250, 236]) * 0.6).astype(np.uint8)
        for y in range(6, top - 5):
            if s.z[y, a] < 7: img[y, a, :3] = (img[y, a, :3] * 0.55 + np.array([236, 246, 244]) * 0.45).astype(np.uint8)
    for x in range(40, 56):
        if x % 3 != 2: img[top + 8, x, :3] = CREAM[3]
        if x % 4 != 3 and x < 51: img[top + 10, x, :3] = CREAM[3]
    return img


def pipe():
    s = Lit(48, 46)
    r = 5.2
    # floor flange (three-quarter view: top plate then a short front face)
    s.slab(2, 35, 24, 40, 2, FRAME, 1, 0.3)
    s.face(2, 41, 24, 44, 2, FRAME)
    for x in (4, 20):
        s.bolt(x, 36, 2.5)
    # vertical run, the elbow, the horizontal run to the right edge
    pts = [(13, 39)] + [(13, 18)]
    for k in range(1, 9):
        a = math.pi + k / 8 * math.pi / 2
        pts.append((25 + 12 * math.cos(a), 18 + 12 * math.sin(a)))
    pts.append((48, 6))
    s.tube(pts, r, 3, PIPE, 0.9)
    # collars with bolts on the straight runs
    for x in (33, 43):
        s.tube([(x, 6), (x + 2.5, 6)], r + 1.2, 3, PIPE, 0.9, -0.05)
        s.dome(x + 1.2, 1.2, 0.9, 0.9, 10, 0.6, BRASS, 0.9)
    s.tube([(13, 25), (13, 27.5)], r + 1.2, 3, PIPE, 0.9, -0.05)
    # the valve: a brass hand wheel on a short stem, facing up out of the pipe
    s.dome(13, 31.5, 2, 2, 8, 1.5, RUB, 0.6)
    s.ring(13, 31.5, 4.2, 5.8, 10, BRASS, 0.9)
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        for t in np.linspace(1.6, 4.4, 5):
            s.put(13 + math.cos(ang) * t, 31.5 + math.sin(ang) * t, (math.cos(ang) * 0.3, math.sin(ang) * 0.3 - 0.2, 1), 10, BRASS, 0.6)
    s.dome(13, 31.5, 1.6, 1.6, 10.5, 1, BRASS, 1.0)
    # a little gauge on the horizontal run and a cyan status lamp
    s.dome(39, 13.5, 3.6, 3.6, 7, 1.5, RUB, 0.6)
    s.dome(39, 13.5, 2.4, 2.4, 8.5, 0.4, CREAM, 0.2, 0.15)
    s.slab(24, 3, 29, 8, 9, RUB, 1, 0.3)
    s.dome(26.5, 5.5, 1.5, 1.2, 9.5, 0.6, CYAN, 1.0, 0.25)
    img = s.render()
    img[13, 39, :3] = RED[2]; img[12, 40, :3] = RED[1]; img[14, 38, :3] = RUB[2]
    # grime: a few darker drips under the collars
    for (x, y) in ((34, 12), (35, 13), (44, 12), (12, 29), (15, 30)):
        if img[y, x, 3]: img[y, x, :3] = (img[y, x, :3] * 0.82).astype(np.uint8)
    return img


# ---- the other eight roof pieces (Zachary, 24 Nov: "good" to the first three) ---------------------------------
PANEL = R("c8dcff", "7fa0ff", "4a68e0", "3048b0", "223482", "18225a")
DARKM = R("a49ab6", "7c7294", "5a5274", "3e3858", "2a2640")


def vcyl(s, x0, x1, y0, y1, z, ramp, shine=0.8, bias=0.0):
    """An upright cylinder's body in the three-quarter view (columns shaded round, faces slightly down)."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u = ((x + 0.5) - (x0 + x1 + 1) / 2) / ((x1 - x0 + 1) / 2)
            w = math.sqrt(max(0.0, 1 - u * u))
            s.put(x, y, (u, 0.25 + 0.2 * (y - y0) / max(1, y1 - y0), w), z * w, ramp, shine, False, bias)


def box3(s, x0, y0, x1, y1, depth, z, ramp, shine=0.3):
    """A box seen from above and in front: a bevelled top, then its front face `depth` pixels tall."""
    s.slab(x0, y0, x1, y1 - depth, z, ramp, 1, shine)
    s.face(x0, y1 - depth + 1, x1, y1, z - 1, ramp)


def fan():
    s = Lit(48, 48)
    s.slab(2, 4, 45, 36, 8, FRAME, 2, 0.35)
    s.face(2, 37, 45, 45, 7, DARKM)
    # the round opening, its grille ring and blades spinning under it
    for y in range(6, 36):
        for x in range(6, 42):
            d = math.hypot(x + 0.5 - 24, y + 0.5 - 20.5)
            if d < 14: s.put(x, y, (0, 0, 1), 1, RUB, 0, False, -0.35)
    for b in range(5):
        a0 = b / 5 * math.tau
        for t in np.linspace(3, 12.5, 40):
            for wdt in np.linspace(-0.45, 0.45, 5):
                a = a0 + wdt * (0.9 - t / 25) + t * 0.05
                x, y = 24 + math.cos(a) * t, 20.5 + math.sin(a) * t
                s.put(x, y, (math.cos(a + 1.2) * 0.5, math.sin(a + 1.2) * 0.5, 1), 3, DARKM, 0.6)
    s.dome(24, 20.5, 3.2, 3.2, 4, 1.5, BRASS, 0.9)
    s.ring(24, 20.5, 13.2, 15.4, 8, FRAME, 0.8)
    for k in (-7, 0, 7):
        for x in range(int(24 - math.sqrt(169 - k * k)), int(24 + math.sqrt(169 - k * k)) + 1):
            s.put(x, 20 + k, (0, -0.5, 1), 6, FRAME, 0.6)
            s.put(x, 21 + k, (0, 0.6, 1), 5.5, FRAME, 0.2)
    for (cx, cy) in ((3, 5), (41, 5), (3, 32), (41, 32)):
        s.bolt(cx, cy, 8.5)
    # front: vent slats and a status window
    for k in range(3):
        for x in range(8, 30):
            s.put(x, 38 + k * 2, (0, -0.8, 0.6), 6, DARKM, 0, False, -0.3)
    s.slab(33, 38, 41, 43, 8, RUB, 1, 0.3)
    s.dome(37, 40.5, 2.2, 1.2, 8.5, 0.5, R("eaffd8", "8cff9a", "40c870", "208a50"), 1, 0.2)
    return s.render()


def solar():
    s = Lit(87, 48)
    # rack: two legs per panel and a cross beam, then the panels on top, tilted toward the light
    s.face(4, 38, 82, 41, 4, DARKM)
    for x in (8, 38, 48, 76):
        s.face(x, 38, x + 3, 46, 3, DARKM)
        s.slab(x, 44, x + 3, 46, 2, RUB, 1)
    for (x0, x1) in ((2, 42), (45, 85)):
        for y in range(4, 37):
            for x in range(x0, x1 + 1):
                edge = x in (x0, x1) or y in (4, 36)
                frame = x - x0 < 2 or x1 - x < 2 or y - 4 < 2 or 36 - y < 2
                cell = (x - x0 - 2) % 9 in (0,) or (y - 6) % 8 in (0,)
                if frame:
                    s.put(x, y, (-0.6 if x - x0 < 1 else 0.6 if x1 - x < 1 else 0, -0.6 if y < 5 else 0.6 if y > 35 else -0.15, 1), 6, FRAME, 0.5)
                elif cell:
                    s.put(x, y, (0, -0.35, 1), 5, PANEL, 0.2, False, -0.05)
                else:
                    u = ((x - x0 - 2) % 9) / 9; v = ((y - 6) % 8) / 8
                    s.put(x, y, (0.15 * (u - 0.5), -0.1 + 0.15 * (v - 0.5), 1), 5, PANEL, 0.6, True, -0.42 + 0.25 * (1 - u) * (1 - v))
        s.slab(x0 + 17, 37, x0 + 23, 40, 6, BRASS, 1, 0.5)
    img = s.render()
    for (x0, x1) in ((2, 42), (45, 85)):
        for k in range(26):
            x, y = x0 + 6 + k, 33 - k
            for j in range(2):
                if x0 + 2 <= x + j < x1 - 1 and 6 <= y < 35:
                    img[y, x + j, :3] = (img[y, x + j, :3] * 0.55 + np.array([200, 220, 255]) * 0.45).astype(np.uint8)
    return img


def duct():
    s = Lit(60, 30)
    s.face(3, 22, 52, 27, 2, DARKM)
    s.tube([(5, 13), (47, 13)], 9.5, 2, DARKM, 0.9)
    for c0 in (12, 26, 40):
        for x in range(c0, c0 + 3):
            for y in range(2, 25):
                v = (y + 0.5 - 13) / 10.6
                if abs(v) <= 1:
                    w = math.sqrt(1 - v * v)
                    s.put(x, y, (-0.3 if x == c0 else 0.3 if x == c0 + 2 else 0, v, w), 2 + 10.6 * w, FRAME, 0.9)
        s.bolt(c0, 3.4, 13)
    for x in range(5, 46):
        if x % 4 == 1 and not any(c - 1 <= x <= c + 3 for c in (12, 26, 40)):
            for y in range(6, 21):
                if s.ramp[y, x] is DARKM: s.bias[y, x] -= 0.12
    for y in range(4, 23):
        for x in range(1, 5):
            v = (y - 13) / 9.5
            if abs(v) <= 1: s.put(x, y, (-0.6, v * 0.6, 0.6), 2 + 9.5 * math.sqrt(1 - v * v), FRAME, 0.4)
    # an end box with a grille
    box3(s, 46, 4, 58, 27, 6, 14, FRAME, 0.4)
    for y in range(8, 18, 2):
        for x in range(49, 56):
            s.put(x, y, (0, -0.8, 0.6), 12, RUB, 0, False, -0.2)
    s.dome(52, 23.5, 1.5, 1.2, 14, 0.6, CYAN, 1, 0.25)
    return s.render()


def tank():
    s = Lit(46, 72)
    # base ring and feet
    s.face(3, 62, 42, 69, 3, DARKM)
    s.slab(3, 58, 42, 63, 4, FRAME, 1, 0.4)
    for x in (6, 36):
        s.bolt(x, 59, 4.5)
    vcyl(s, 5, 40, 14, 58, 18, TEALG, 0.9, -0.05)
    # straps around the body, a dome top, a valve and a level window
    for y in (22, 44):
        vcyl(s, 4, 41, y, y + 2, 19, FRAME, 0.8)
    s.dome(22.5, 14, 18, 7, 18, 5, TEALG, 0.9)
    s.dome(22.5, 12, 4.2, 2.6, 23, 2, FRAME, 0.8)
    s.dome(22.5, 11.6, 2, 1.3, 25, 1, BRASS, 1)
    for y in range(27, 41):
        for x in range(30, 34):
            s.put(x, y, (0.5, 0.25, 0.8), 17, CYAN if y > 32 else RUB, 0.6, False, -0.1 if y > 32 else -0.2)
    img = s.render()
    # a water-drop badge
    for y in range(28, 39):
        for x in range(12, 21):
            dx, dy = x + 0.5 - 16.5, y + 0.5 - 34.5
            if (dx * dx + dy * dy < 12 and dy > -1.5) or (dy <= -1.5 and abs(dx) < (dy + 6.5) * 0.55):
                img[y, x, :3] = CYAN[1] if dx + dy < -2 else CYAN[2] if dx + dy < 2 else CYAN[3]
    return img


def hatch():
    s = Lit(48, 48)
    box3(s, 1, 2, 46, 46, 6, 5, DARKM)
    curb(s, 1, 2, 46, 40, z=6, t=5)
    s.slab(6, 7, 41, 35, 4, FRAME, 1, 0.35, -0.08)
    # hazard stripes along the bottom of the lid, a handle bar, hinges at the top
    for y in range(29, 34):
        for x in range(8, 40):
            col = BRASS if ((x + y) // 3) % 2 == 0 else RUB
            s.put(x, y, (0, 0, 1), 4.2, col, 0.2, False, 0.1 if col is BRASS else 0)
    s.tube([(15, 19), (32, 19)], 2.2, 5, FRAME, 0.9)
    for x in (13, 32):
        s.slab(x, 16, x + 3, 22, 5, DARKM, 1, 0.4)
    for x in (10, 32):
        s.slab(x, 4, x + 6, 8, 7, BRASS, 1, 0.5)
    for (cx, cy) in ((7, 8), (38, 8), (7, 24), (38, 24)):
        s.bolt(cx, cy, 5)
    s.dome(24, 43.5, 1.6, 1.2, 5, 0.5, R("ffe0c0", "ff9a48", "e05a30", "902a28"), 1, 0.25)
    return s.render()


def dish():
    s = Lit(42, 60)
    s.face(5, 52, 36, 57, 3, DARKM)
    s.slab(5, 48, 36, 53, 4, FRAME, 1, 0.4)
    for x in (7, 32):
        s.bolt(x, 49, 4.5)
    vcyl(s, 16, 25, 32, 49, 6, DARKM, 0.8)
    s.dome(20.5, 33, 7, 3.5, 7, 2, FRAME, 0.7)
    # the bowl: tilted toward the upper left, concave, so its inside is lit on the lower right
    cx, cy, rx, ry = 20, 19, 17, 15
    for y in range(2, 36):
        for x in range(1, 41):
            u, v = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d = u * u + v * v
            if d > 1: continue
            rim = d > 0.82
            if rim:
                s.put(x, y, (u * 0.8, v * 0.8, 0.6), 12, BRASS, 0.7)
            else:
                s.put(x, y, (-u * 0.9, -v * 0.9, 1), 10 + 2 * d, FRAME, 0.5, True, -0.05)
    for a in (0.6, 2.4, 4.3):
        for t in np.linspace(0, 1, 14):
            ex, ey = cx + math.cos(a) * 12, cy + math.sin(a) * 10
            x, y = ex + (cx + 5 - ex) * t, ey + (cy - 6 - ey) * t
            s.put(x, y, (0, -0.3, 1), 13 + t * 4, DARKM, 0.6)
    s.dome(cx + 5, cy - 6, 2.6, 2.6, 17, 1.5, BRASS, 1)
    s.dome(cx + 5, cy - 6, 1, 1, 18.6, 0.5, R("ffd0c8", "ff6a58", "c03038", "7a2030"), 1, 0.2)
    return s.render()


def utilbox():
    s = Lit(48, 42)
    # pipe out the right side and down into the roof
    s.tube([(28, 22), (41, 22), (41, 38)], 3.6, 2, PIPE, 0.9)
    s.tube([(41, 33), (41, 35)], 4.6, 2, PIPE, 0.9, -0.05)
    s.slab(35, 37, 47, 41, 1, FRAME, 1, 0.3)
    box3(s, 4, 6, 32, 38, 10, 10, FRAME, 0.4)
    # a screen on the top, a latch and an orange tag on the front
    s.slab(8, 9, 28, 24, 10.5, RUB, 1, 0.3)
    for y in range(11, 23):
        for x in range(10, 27):
            s.put(x, y, (0, 0, 1), 10.2, TEALG, 0.2, True, 0.2 - 0.5 * ((x - 10) / 17 * 0.5 + (y - 11) / 12 * 0.5))
    s.slab(9, 31, 17, 34, 11, DARKM, 1, 0.5)
    s.slab(24, 30, 28, 35, 11, BRASS, 1, 0.5)
    for (x, y) in ((5, 7), (29, 7), (5, 25), (29, 25)):
        s.bolt(x, y, 10.5)
    img = s.render()
    for k in range(6):
        img[13 + k, 12 + k, :3] = (img[13 + k, 12 + k, :3] * 0.4 + np.array([230, 255, 250]) * 0.6).astype(np.uint8)
        img[19 + k // 2, 16 + k, :3] = CYAN[1]
    return img


def lights():
    s = Lit(60, 12)
    s.face(1, 8, 58, 10, 2, DARKM)
    s.slab(1, 3, 58, 8, 3, FRAME, 1, 0.4)
    for x in (12, 30, 48):
        s.slab(x - 5, 2, x + 5, 8, 4, DARKM, 1, 0.3)
        s.dome(x + 0.5, 4.5, 4, 2.6, 4.5, 1.8, GLOW + [BRASS[2]], 1.0, 0.3)
    for x in (3, 55):
        s.bolt(x, 4, 3.5)
    return s.render()


EIGHT = (("roof_fan", fan), ("roof_solar", solar), ("roof_duct", duct), ("roof_tank", tank), ("roof_hatch", hatch),
         ("roof_dish", dish), ("roof_box", utilbox), ("roof_lights", lights))
if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/r3"
    os.makedirs(out, exist_ok=True)
    for name, fn in (("roof_skylight", skylight), ("roof_garden", greenhouse), ("roof_pipe", pipe)) + EIGHT:
        Image.fromarray(fn(), "RGBA").save(os.path.join(out, name + ".png"))
