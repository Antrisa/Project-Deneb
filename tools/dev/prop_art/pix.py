"""A small pixel-art kit for Echo Landing creatures (23 Nov 2026).

Shapes are drawn by hand as letter grids, one letter per pixel and part. The kit then shades every part
as a rounded form lit from the top left, in a 6-tone ramp per material. Each ramp is hue-shifted, with
shadows going plum and lights going warm, like the residents' sheets. Where a part sits in front of
another it adds a soft contact shadow. The outline is the residents' dark plum, a touch lighter on lit
edges. Faces, highlights and other small details are stamped on by hand afterwards.
"""
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, gaussian_filter

H = lambda h: np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
OUT = H("24101a")          # outline, as on the residents
OUT_LIT = H("3a1e27")      # outline on lit top/left edges
LASH, PUPIL, PUPIL2 = H("2c1119"), H("2f161e"), H("4a2f3d")
SCLERA, SCLERA2, BLUSH = H("e4cbb9"), H("f8ddca"), H("e8857a")


def ramp(*stops, n=6):
    """n colours through the given stops (dark to light), evenly spaced."""
    st = [H(s) if isinstance(s, str) else np.array(s, float) for s in stops]
    out = []
    for i in range(n):
        t = i / (n - 1) * (len(st) - 1)
        k = min(int(t), len(st) - 2); f = t - k
        out.append(st[k] * (1 - f) + st[k + 1] * f)
    return out


def grid(rows, w=None, h=None):
    """A list of strings to a 2-D char array (padded with '.')."""
    w = w or max(len(r) for r in rows); h = h or len(rows)
    a = np.full((h, w), ".", "<U1")
    for y, r in enumerate(rows[:h]):
        for x, c in enumerate(r[:w]): a[y, x] = c
    return a


def overlay(base, top, dx=0, dy=0):
    """Paste grid `top` on `base` (non-'.' cells win), shifted."""
    out = base.copy(); h, w = top.shape
    for y in range(h):
        for x in range(w):
            c = top[y, x]
            if c != ".":
                X, Y = x + dx, y + dy
                if 0 <= X < out.shape[1] and 0 <= Y < out.shape[0]: out[Y, X] = c
    return out


def shift(g, dx, dy):
    out = np.full_like(g, "."); return overlay(out, g, dx, dy)


def mirror(g, swap=None):
    out = g[:, ::-1].copy()
    if swap:
        for a, b in swap.items():
            m1, m2 = out == a, out == b; out[m1] = b; out[m2] = a
    return out


LIGHT = np.array([-0.62, -0.78, 0.95]); LIGHT /= np.linalg.norm(LIGHT)


def shade_part(mask, n_tones, bulge=1.0, r=None, top=0.25, flat=0.0, light=LIGHT, lo=None, hi=None, profile="dome"):
    """Tone index (0..n-1) for each pixel of `mask`, from a rounded height field lit from the top left."""
    d = distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    R = r or max(d.max(), 1.0)
    t = np.clip(d / R, 0, 1)
    if profile == "linear":          # planar facets (a cut stone): the distance field's straight skeleton
        h = np.minimum(d, R) * bulge
    else:
        h = np.sqrt(np.clip(1 - (1 - t) ** 2, 0, 1)) * R * bulge
        h = gaussian_filter(h, 0.8) * mask + h * 0  # keep it soft at joins
    gy, gx = np.gradient(h)
    nrm = np.dstack([-gx, -gy, np.ones_like(h)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    I = nrm @ light
    ys = np.nonzero(mask)[0]
    if len(ys):
        y0, y1 = ys.min(), ys.max() + 1e-6
        yy = np.arange(mask.shape[0])[:, None] * np.ones(mask.shape)
        I = I - top * (yy - y0) / max(y1 - y0, 1)       # lit from above as well: tops lighter
    I = I * (1 - flat) + flat * 0.8
    v = I[mask]
    a = lo if lo is not None else np.percentile(v, 3)
    b = hi if hi is not None else np.percentile(v, 99)
    q = np.clip((I - a) / max(b - a, 1e-6), 0, 0.999)
    idx = (q * n_tones).astype(int)
    return np.where(mask, idx, -1)


def render(g, parts, lines=None, stamps=None, outline=True, out=None):
    """g: char grid. parts: {char: dict(ramp=[...], z=int, bulge, r, top, spec=colour or None, ao=True)}.
    lines: {char: colour} painted flat on top after outlining (thin stalks, cracks).
    stamps: list of (x, y, [rows], {char: colour}) painted last (eyes, highlights)."""
    h, w = g.shape
    img = np.zeros((h, w, 4), float)
    zmap = np.full((h, w), -999)
    order = sorted(parts.items(), key=lambda kv: kv[1].get("z", 0))
    tone = np.full((h, w), -1); owner = np.full((h, w), ".", "<U1")
    for ch, p in order:
        m = g == ch
        if not m.any(): continue
        n = len(p["ramp"])
        idx = shade_part(m, n, p.get("bulge", 1.0), p.get("r"), p.get("top", 0.25), p.get("flat", 0.0),
                         p.get("light", LIGHT), p.get("lo"), p.get("hi"), p.get("profile", "dome"))
        tone[m] = idx[m]; owner[m] = ch; zmap[m] = p.get("z", 0)
    # contact shadow: a part's pixels next to a part in front of it go darker
    for ch, p in order:
        if not p.get("ao", True): continue
        m = owner == ch
        z = p.get("z", 0)
        front = (zmap > z) & (owner != ".") & ~np.isin(owner, p.get("ao_ignore", []))
        if not front.any(): continue
        d = distance_transform_edt(~front)
        tone[m & (d <= 1.0)] = np.maximum(tone[m & (d <= 1.0)] - 2, 0)
        tone[m & (d > 1.0) & (d <= 2.0)] = np.maximum(tone[m & (d > 1.0) & (d <= 2.0)] - 1, 0)
    for ch, p in parts.items():
        m = owner == ch
        if not m.any(): continue
        R = p["ramp"]
        for y, x in zip(*np.nonzero(m)):
            img[y, x, :3] = R[tone[y, x]]; img[y, x, 3] = 255
        if p.get("spec") is not None:
            # a small glossy highlight on the brightest top-left pixels
            mm = m & (tone == len(R) - 1)
            ys, xs = np.nonzero(mm)
            if len(ys):
                score = -(xs + ys * 1.2)
                keep = np.argsort(score)[: p.get("spec_n", 3)]
                for k in keep: img[ys[k], xs[k], :3] = p["spec"]
    body = owner != "."
    if lines:
        for ch, col in lines.items():
            body_l = g == ch
            body = body | (body_l & False)
    if outline:
        pad = np.pad(body, 1)
        nb = (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]) & ~body
        lit = (pad[2:, 1:-1] | pad[1:-1, 2:]) & ~(pad[:-2, 1:-1]) & ~(pad[1:-1, :-2])  # body below/right = top/left edge
        for y, x in zip(*np.nonzero(nb)):
            o, ol = (out if out is not None else (OUT, OUT_LIT))
            img[y, x, :3] = ol if lit[y, x] and y < h * 0.6 else o; img[y, x, 3] = 255
        # dark line between parts where the back part is much darker than the front isn't needed: AO does it
    if lines:
        for ch, col in lines.items():
            for y, x in zip(*np.nonzero(g == ch)):
                img[y, x, :3] = col; img[y, x, 3] = 255
    if stamps:
        for (sx, sy, rows, pal) in stamps:
            for yy, row in enumerate(rows):
                for xx, c in enumerate(row):
                    if c in pal and 0 <= sx + xx < w and 0 <= sy + yy < h:
                        img[sy + yy, sx + xx, :3] = pal[c]; img[sy + yy, sx + xx, 3] = 255
    return img.astype(np.uint8)


def eyes_front(cx_l, cx_r, y, blush=True):
    """Resident eyes: a lash line, then 2 x 3 eyes (light outer column, dark inner column), blush below."""
    pal = {"L": LASH, "d": PUPIL, "e": PUPIL2, "s": SCLERA, "S": SCLERA2, "b": BLUSH}
    st = [(cx_l, y, ["LL", "sd", "Se", "Se"] + (["b."] if blush else []), pal),
          (cx_r, y, ["LL", "ds", "eS", "eS"] + ([".b"] if blush else []), pal)]
    return st


def eyes_cute(xl, xr, y, blush=True, big=False):
    """Creature eyes: glossy dark 2 x 3 (3 x 3 when big) with a shine at the top left and a blush below."""
    pal = {"d": PUPIL, "e": PUPIL2, "h": H("fff6e6"), "b": BLUSH}
    rows = ["hdd", "ddd", "dde"] if big else ["hd", "dd", "de"]
    st = [(xl, y, rows, pal), (xr, y, rows, pal)]
    if blush:
        st += [(xl - 1, y + 3, ["b"], pal), (xr + len(rows[0]), y + 3, ["b"], pal)]
    return st


def eye_side(x, y, big=False):
    pal = {"d": PUPIL, "e": PUPIL2, "h": H("fff6e6")}
    return [(x, y, ["hdd", "ddd", "dde"] if big else ["hd", "dd", "de"], pal)]


def sheet(frames, fw, fh):
    """frames[col][row] -> RGBA array; 4 columns x 5 rows like the residents."""
    out = np.zeros((fh * 5, fw * 4, 4), np.uint8)
    for c, col in enumerate(frames):
        for r, f in enumerate(col):
            out[r * fh:(r + 1) * fh, c * fw:(c + 1) * fw] = f
    return Image.fromarray(out, "RGBA")
