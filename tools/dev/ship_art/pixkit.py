"""Crisp pixel-art ships with shading and depth (Claude, 21 Nov 2026). Zachary: the flat version was better because it
is pixel art; it "just needs shading and depth and some more detail", like FTL's ships.

Every pixel has a material and a tone (0 darkest .. 5 brightest); colours come from a 6-colour ramp per material at
the end, so paint (stripes, decals) follows the shading underneath it. Parts:
  bevel   a flat face with chamfered edges, lit from the top left (top and left edges bright, bottom and right dark)
  tube    a cylinder lying along x or y: banded light to dark across it
  dome    a glass bubble with a highlight
Parts drawn over others cast a 2-px shadow down and to the right onto what's below. Engraved panel lines, rivets,
vents and recessed slots are drawn on top. The outline goes round the whole silhouette.
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

RAMPS = {
    "hull": ["#6a5e62", "#8f8285", "#b0a3a2", "#cbbfb7", "#e4d8cc", "#f6ede2"],
    "metal": ["#46404f", "#5e5868", "#767080", "#8e8898", "#a8a3b2", "#c4c0cc"],
    "orange": ["#6e2a0e", "#9c3c10", "#c45414", "#ea6e1a", "#fa8a30", "#fdab58"],
    "glass": ["#123e48", "#1b5f6b", "#25808c", "#3aa2ac", "#6acdd4", "#c8f4f4"],
    "dark": ["#1a1924", "#232230", "#2e2d3b", "#393847", "#454453", "#52505f"],
    "bay": ["#2c2a36", "#363442", "#423f4e", "#4e4b5a", "#5a5766", "#686574"],
    "pipe": ["#3e3a2e", "#5a5240", "#7a6e52", "#9a8a64", "#b8a678", "#d4c290"],
    "deck": ["#8a857f", "#a29d95", "#bab5ac", "#cdc8bf", "#ddd9d0", "#ebe8e0"],
    "cockpit_deck": ["#8a8278", "#a49b8e", "#bdb3a4", "#d2c8b8", "#e2d9c9", "#efe8da"],
    "wall": ["#232230", "#2e2d3b", "#3d3c4b", "#504f5f", "#666576", "#7e7d8c"],
    "console": ["#2e3a3c", "#3e4c4c", "#506262", "#647a76", "#7e948c", "#9cb0a6"],
    "screen": ["#11585e", "#167479", "#11a0a0", "#3cc8c0", "#86e6dc", "#e0fff8"],
    "red": ["#4e1210", "#721a14", "#96241a", "#b82e20", "#d8442e", "#ee6a4a"],
    "yellow": ["#64420c", "#8c5e10", "#b47e16", "#d8a020", "#f0c234", "#fadc62"],
    "green": ["#1c4014", "#2a5a1c", "#3a7626", "#4e9232", "#68ac44", "#8cc65e"],
    "blue": ["#162a5c", "#1f3f86", "#2a58b0", "#3a74d0", "#5a96e6", "#8ab8f4"],
}
EMISSIVE = {
    "glow": ["#c85a14", "#f08a2a", "#ffb04a", "#ffd27a", "#ffe8a8", "#fff6d8"],
    "glow_red": ["#a82a20", "#e6463c", "#ff6a5a", "#ff9a8a", "#ffc0b4", "#ffe4dc"],
    "glow_green": ["#2a8a2a", "#4ad84a", "#7dff8a", "#b6ffb0", "#d8ffd4", "#f0fff0"],
    "glow_teal": ["#0e7a76", "#11b3aa", "#45e1d5", "#9af4ea", "#c8fbf4", "#e8fffc"],
}
OUTLINE = "#262535"
LIGHT = np.array([-0.62, -0.78])          # from the top left (x right, y down)


def _hex(s):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), 255)


class Pix:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.tone = np.full((h, w), -1, np.int16)
        self.mat = np.full((h, w), "", dtype=object)
        self.lines = np.zeros((h, w), bool)

    # ---- masks
    def mask(self, polygon=None, ellipse=None, rect=None):
        im = Image.new("L", (self.w, self.h), 0)
        d = ImageDraw.Draw(im)
        if polygon is not None:
            d.polygon([tuple(p) for p in polygon], fill=255)
        if ellipse is not None:
            d.ellipse(tuple(ellipse), fill=255)
        if rect is not None:
            d.rectangle(tuple(rect), fill=255)
        return np.array(im) > 0

    def _place(self, m, tone, mat, shadow=True):
        if shadow:
            below = self.tone >= 0
            cast = np.zeros_like(m)
            cast[2:, 2:] = m[:-2, :-2]
            cast[1:, 1:] |= m[:-1, :-1]
            cast &= below & ~m
            self.tone[cast] = np.maximum(self.tone[cast] - 1, 0)
        self.tone[m] = tone[m]
        self.mat[m] = mat
        self.lines[m] = False

    # ---- parts
    def bevel(self, m, mat, width=2, face=4, edge_light=5, edge_dark=2, shadow=True, shade_lower=True):
        """A flat face with chamfered edges. shade_lower: the lower half of the face a step darker (a rounded top)."""
        if isinstance(m, dict):
            m = self.mask(**m)
        dist = ndimage.distance_transform_edt(m)
        gy, gx = np.gradient(ndimage.gaussian_filter(dist, 0.8))
        nrm = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
        # outward normal is minus the gradient of the inside distance
        dot = (-gx / nrm) * LIGHT[0] + (-gy / nrm) * LIGHT[1]
        tone = np.full((self.h, self.w), face, np.int16)
        if shade_lower:
            ys, xs = np.nonzero(m)
            mid = (ys.min() + ys.max()) / 2.0
            yy = np.mgrid[0:self.h, 0:self.w][0]
            tone[(yy > mid)] = face - 1
        rim = m & (dist <= width)
        tone[rim & (dot > 0.35)] = edge_light
        tone[rim & (dot <= 0.35) & (dot >= -0.35)] = face - 1
        tone[rim & (dot < -0.35)] = edge_dark
        tone[m & (dist <= 1) & (dot < -0.35)] = edge_dark - 1
        self._place(m, tone, mat, shadow)
        return m

    def tube(self, m, mat, axis="x", shadow=True, bands=(5, 4, 4, 3, 3, 2, 1)):
        if isinstance(m, dict):
            m = self.mask(**m)
        ys, xs = np.nonzero(m)
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        if axis == "x":
            u = (yy - ys.min()) / max(1, ys.max() - ys.min())
        else:
            u = (xx - xs.min()) / max(1, xs.max() - xs.min())
        idx = np.clip((u * len(bands)).astype(int), 0, len(bands) - 1)
        tone = np.array(bands, np.int16)[idx]
        self._place(m, tone, mat, shadow)
        return m

    def dome(self, m, mat, shadow=False):
        if isinstance(m, dict):
            m = self.mask(**m)
        ys, xs = np.nonzero(m)
        cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
        ry, rx = (ys.max() - ys.min()) / 2 + 0.5, (xs.max() - xs.min()) / 2 + 0.5
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        u, v = (xx - cx) / rx, (yy - cy) / ry
        r = np.sqrt(u ** 2 + v ** 2)
        lit = -(u * 0.6 + v * 0.8)                 # brighter toward the top left
        tone = np.full((self.h, self.w), 3, np.int16)
        tone[lit > 0.15] = 4
        tone[lit < -0.35] = 2
        tone[(r > 0.82)] = 1
        tone[(r > 0.82) & (lit > 0.2)] = 3
        # a crescent highlight and a glint
        hl = ((u + 0.32) ** 2 / 0.09 + (v + 0.38) ** 2 / 0.03) < 1
        tone[hl] = 5
        self._place(m, tone, mat, shadow)
        return m

    # ---- surface
    def paint(self, m, mat, where=None):
        if isinstance(m, dict):
            m = self.mask(**m)
        m = m & (self.tone >= 0)
        if where is not None:
            m &= np.isin(self.mat, list(where))
        self.mat[m] = mat
        return m

    def shade(self, m, delta):
        if isinstance(m, dict):
            m = self.mask(**m)
        m = m & (self.tone >= 0)
        self.tone[m] = np.clip(self.tone[m] + delta, 0, 5)

    def set_tone(self, m, t):
        if isinstance(m, dict):
            m = self.mask(**m)
        m = m & (self.tone >= 0)
        self.tone[m] = t

    def engrave(self, pts, highlight=True):
        """A panel line: a dark groove with a bright lip under it."""
        g = self._line(pts)
        if highlight:
            lip = np.zeros_like(g)
            lip[1:, 1:] = g[:-1, :-1]
            lip &= ~g & (self.tone >= 0)
            self.tone[lip] = np.minimum(self.tone[lip] + 1, 5)
        g &= self.tone >= 0
        self.tone[g] = np.maximum(self.tone[g] - 2, 0)

    def engrave_rect(self, x0, y0, x1, y1):
        self.engrave([(x0, y0), (x1, y0)]); self.engrave([(x1, y0), (x1, y1)])
        self.engrave([(x0, y1), (x1, y1)]); self.engrave([(x0, y0), (x0, y1)])

    def _line(self, pts, width=1):
        im = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(im).line([tuple(p) for p in pts], fill=255, width=width)
        return np.array(im) > 0

    def dark_line(self, pts, width=1):
        self.lines |= self._line(pts, width) & (self.tone >= 0)

    def rivet(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h and self.tone[y, x] >= 0:
            self.tone[y, x] = max(int(self.tone[y, x]) - 2, 0)
            if x > 0 and y > 0 and self.tone[y - 1, x - 1] >= 0:
                self.tone[y - 1, x - 1] = 5

    def slot(self, x0, y0, x1, y1):
        """A recessed slot: dark inside, a bright lip along its bottom edge, a shadow along its top."""
        m = self.mask(rect=(x0, y0, x1, y1)) & (self.tone >= 0)
        self.mat[m] = "dark"
        self.tone[m] = 2
        self.tone[m & self.mask(rect=(x0, y0, x1, y0))] = 0
        lip = self.mask(rect=(x0, y1 + 1, x1, y1 + 1)) & (self.tone >= 0) & (self.mat != "dark")
        self.tone[lip] = np.minimum(self.tone[lip] + 1, 5)

    def glow(self, m, mat="glow", tone=3):
        if isinstance(m, dict):
            m = self.mask(**m)
        self.mat[m] = mat
        self.tone[m] = tone

    # ---- out
    def render(self, outline=True):
        out = np.zeros((self.h, self.w, 4), np.uint8)
        for y, x in zip(*np.nonzero(self.tone >= 0)):
            m = self.mat[y, x] or "hull"
            ramp = EMISSIVE.get(m) or RAMPS[m]
            out[y, x] = _hex(ramp[int(np.clip(self.tone[y, x], 0, 5))])
        ln = self.lines & (self.tone >= 0)
        out[ln, :3] = (out[ln, :3] * 0.55).astype(np.uint8)
        if outline:
            m = out[:, :, 3] > 0
            ring = ndimage.binary_dilation(m, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]]) & ~m
            glow_px = np.isin(self.mat, list(EMISSIVE)) & m
            near_glow = ndimage.binary_dilation(glow_px, iterations=1)
            out[ring & ~near_glow] = _hex(OUTLINE)
        return Image.fromarray(out, "RGBA").copy()
