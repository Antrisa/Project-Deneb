"""A small renderer for ship art (Claude, 21 Nov 2026). Zachary: the first ship art "looks way too simple"; it has to
look like the other art in the game, whose props have soft multi-shade forms, glossy highlights, wear, and a dark
outline (fuel_tank.png, console.png, coolant_tank.png, tarp_fighter.png).

A picture is built from parts. Each part is a 2D shape with a profile that gives it height (a rounded cylinder, a
bevelled plate, a dome, a box with rounded edges), a base height, and a material. The parts make a height map; the
renderer lights it from the top left, adds ambient occlusion and gloss, then colours each pixel from its material's
ramp (dark to light, hue-shifted: shadows lean violet, highlights warm). Seams, rivets, vents and paint are added on
top. Everything stays at the picture's own pixel size: no scaling, no blur, hard edges.

    from render import Canvas, RAMPS
    c = Canvas(168, 96)
    c.part(polygon=[...], profile="round", radius=12, z=3, height=12, material="hull")
    c.paint(polygon=[...], material="orange")         # recolour, no height change
    c.seam([(x0, y0), (x1, y1)])                      # a groove
    c.rivets([(x, y), ...])
    img = c.render()                                  # RGBA, outlined
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

# Ramps, dark to light, in the game's cozy style (Zachary, 21 Nov: the kitchen set, fridge, chairs and tables are
# "the new art style"): warm, few shades, shadows lean violet or navy, highlights warm cream. Sampled from it.
RAMPS = {
    "hull": ["#513f43", "#7b6b72", "#9c8d93", "#cab8a7", "#e2d4bf", "#f4e7ce", "#fff3dc"],
    "cream": ["#513f43", "#7b6b72", "#9c8d93", "#cab8a7", "#e2d4bf", "#f4e7ce", "#fff3dc"],
    "orange": ["#5b2a20", "#86391f", "#b04e24", "#d0682a", "#e88a3c", "#f6ac5c", "#fcc888"],
    "metal": ["#36252c", "#4e3f46", "#665a62", "#7f747c", "#9a8f94", "#b5aaaa", "#cfc4bc"],
    "steel": ["#2a2c3e", "#3c4256", "#52596e", "#6a7286", "#848a9c", "#a0a4b2", "#bdbfc8"],
    "deck": ["#3e3137", "#513f43", "#655459", "#7b6b72", "#8f8086", "#a3959a", "#b8abad"],
    "dark": ["#2a1c20", "#36252c", "#3e3137", "#4a3a40", "#56464c", "#625258", "#6e5e64"],
    "glass": ["#253a53", "#2e4a60", "#3c5364", "#3f8089", "#53a0a0", "#86cfc4", "#d4f4e8"],
    "blue": ["#1e2a48", "#253a53", "#2e5072", "#3a6a94", "#4e88b2", "#78aacc", "#b0d0e4"],
    "white": ["#513f43", "#7b6b72", "#9c8d93", "#c2b8b4", "#ddd6ce", "#eee8de", "#fcf8f0"],
    "bone": ["#4e3a2e", "#6e5644", "#927660", "#b4987c", "#cdb698", "#e2d0b2", "#f4e7ce"],
    "bronze": ["#452223", "#6e392f", "#8e5432", "#ad775c", "#c8925e", "#dab593", "#eed2aa"],
    "red": ["#36252c", "#5e2a2c", "#8a3634", "#bd4e46", "#d46a58", "#e8907a", "#f6b6a0"],
    "rust": ["#36252c", "#583529", "#6e392f", "#8e4e30", "#9b5c36", "#b87a4c", "#d09a6c"],
    "leaf": ["#1e3a36", "#2a5048", "#36685a", "#468775", "#5aa088", "#7cba9c", "#a8d4b6"],
    "teal": ["#253a53", "#2c4a5c", "#3c5364", "#3f8089", "#53767d", "#6fa0a0", "#9cc8c0"],
    "petal": ["#3e2032", "#5e2c48", "#82405e", "#a65a78", "#c27892", "#da9aac", "#eebcc6"],
    "yellow": ["#4a3020", "#6e4a24", "#94682a", "#b88a34", "#d4aa48", "#e8c66a", "#f6e09a"],
    "green": ["#22362a", "#2e4a34", "#3e6440", "#468775", "#5e9a62", "#80b478", "#a8cc96"],
    "violet": ["#2a1e3a", "#3c2a52", "#523a6c", "#6a4e88", "#8466a2", "#a084bc", "#c0a8d4"],
    "silver": ["#36303e", "#4e4858", "#686272", "#827e8c", "#9e9aa6", "#bab6c0", "#d6d2da"],
    "russet": ["#452223", "#6e392f", "#8e4428", "#ad5a30", "#c8743c", "#dc9456", "#ecb47c"],
    "coral": ["#4a2228", "#6e3034", "#944440", "#bd4e46", "#d46a58", "#e8907a", "#f6b6a0"],
}
OUTLINE = (91, 51, 45, 255)          # #5b332d, the warm dark-brown outline of the new art
# Materials that glow: drawn at full brightness, light ignored.
GLOWS = {
    "glow": ["#ff9a30", "#ffb84a", "#ffd27a", "#fff0c0"],
    "glow_blue": ["#3aa8ff", "#6ac4ff", "#a8e0ff", "#e8f8ff"],
    "glow_teal": ["#11b3aa", "#45e1d5", "#9af4ea", "#e8fffc"],
    "glow_red": ["#e6463c", "#ff6a5a", "#ff9a8a", "#ffd8d0"],
    "glow_green": ["#4ad84a", "#7dff8a", "#b6ffb0", "#f0fff0"],
    "glow_pink": ["#d860c0", "#ff8ae0", "#ffb0f0", "#fff0fa"],
    "glow_yellow": ["#e8b02a", "#ffd86a", "#fff0a4", "#fffbe0"],
}
GLOSSY = {"glass", "blue", "teal", "petal", "violet"}


def _hex(s):
    s = s.lstrip("#")
    return np.array([int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)], dtype=np.float32)


class Canvas:
    def __init__(self, w, h, seed=1, light=(-0.5, -0.75, 0.75), relief=1.8):
        self.w, self.h = w, h
        self.H = np.zeros((h, w), np.float32)                 # height
        self.mask = np.zeros((h, w), bool)                    # anything there at all
        self.mat = np.full((h, w), "", dtype=object)          # material per pixel
        self.wear = np.zeros((h, w), np.float32)              # -1..1 darker/lighter scuffs
        self.lines = np.zeros((h, w), bool)                   # dark part lines (drawn after light)
        self.hilite = np.zeros((h, w), bool)                  # 1-px bright edges
        self.rng = random.Random(seed)
        l = np.array(light, np.float32)
        self.light = l / np.linalg.norm(l)
        self.relief = relief                                  # how strongly slopes catch or lose the light

    # ---- shapes
    def _shape(self, polygon=None, ellipse=None, rect=None, union=None):
        im = Image.new("L", (self.w, self.h), 0)
        d = ImageDraw.Draw(im)
        if polygon is not None:
            d.polygon([tuple(p) for p in polygon], fill=255)
        if ellipse is not None:
            d.ellipse(tuple(ellipse), fill=255)
        if rect is not None:
            d.rectangle(tuple(rect), fill=255)
        m = np.array(im) > 0
        if union is not None:
            m |= union
        return m

    def shape(self, **kw):
        return self._shape(**kw)

    def part(self, polygon=None, ellipse=None, rect=None, shape=None, profile="round", radius=6.0, z=0.0, height=6.0,
             material="hull", axis=None, clip=None, tilt=(0.0, 0.0), edge=False):
        """Add a raised part. profile: round (edges curve over with this radius), bevel (flat top, chamfered edges),
        dome (a sphere cap over the shape), tube (a cylinder along axis 'x' or 'y')."""
        m = shape if shape is not None else self._shape(polygon=polygon, ellipse=ellipse, rect=rect)
        if clip is not None:
            m &= clip
        if not m.any():
            return m
        d = ndimage.distance_transform_edt(m)
        if profile == "round":
            t = np.clip(d / max(radius, 0.5), 0, 1)
            h = height * np.sqrt(1 - (1 - t) ** 2)
        elif profile == "bevel":
            h = height * np.clip(d / max(radius, 0.5), 0, 1)
        elif profile == "dome":
            ys, xs = np.nonzero(m)
            cy, cx = ys.mean(), xs.mean()
            ry, rx = (ys.max() - ys.min() + 1) / 2, (xs.max() - xs.min() + 1) / 2
            yy, xx = np.mgrid[0:self.h, 0:self.w]
            r2 = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
            h = height * np.sqrt(np.clip(1 - r2, 0, 1))
        elif profile == "tube":
            ys, xs = np.nonzero(m)
            yy, xx = np.mgrid[0:self.h, 0:self.w]
            if axis == "y":
                c, r = (xs.min() + xs.max()) / 2, (xs.max() - xs.min() + 1) / 2
                u = (xx - c) / r
            else:
                c, r = (ys.min() + ys.max()) / 2, (ys.max() - ys.min() + 1) / 2
                u = (yy - c) / r
            h = height * np.sqrt(np.clip(1 - u ** 2, 0.05, 1))
        else:
            h = np.full((self.h, self.w), height, np.float32)
        top = z + h
        if tilt != (0.0, 0.0):
            ys, xs = np.nonzero(m)
            yy, xx = np.mgrid[0:self.h, 0:self.w]
            top = top + tilt[0] * (xx - xs.mean()) + tilt[1] * (yy - ys.mean())
        win = m & (~self.mask | (top >= self.H))
        # where a part sits on a lower one, a dark seam marks the join
        seam_edge = m & ~ndimage.binary_erosion(m) & self.mask & (self.H < top - 1.0)
        self.H[win] = top[win]
        self.mat[win] = material
        self.mask |= m
        self.lines |= seam_edge
        if edge:
            self.lines[win & ~ndimage.binary_erosion(m)] = True
        return m

    def flatten(self, polygon=None, ellipse=None, rect=None, shape=None, z=1.0, material="deck"):
        """Cut down to a flat floor (for cut-away interiors)."""
        m = shape if shape is not None else self._shape(polygon=polygon, ellipse=ellipse, rect=rect)
        m &= self.mask
        self.H[m] = z
        self.mat[m] = material
        self.lines[m] = False
        return m

    # ---- surface detail
    def paint(self, polygon=None, ellipse=None, rect=None, shape=None, material="orange", where=None):
        m = shape if shape is not None else self._shape(polygon=polygon, ellipse=ellipse, rect=rect)
        m &= self.mask
        if where is not None:
            m &= np.isin(self.mat, list(where))
        self.mat[m] = material
        return m

    def seam(self, pts, depth=0.9, width=1):
        im = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(im).line([tuple(p) for p in pts], fill=255, width=width)
        m = (np.array(im) > 0) & self.mask
        self.H[m] -= depth
        return m

    def groove_rect(self, x0, y0, x1, y1, depth=0.9):
        for pts in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            self.seam(pts, depth)

    def recess(self, polygon=None, ellipse=None, rect=None, depth=2.0, material="dark"):
        m = self._shape(polygon=polygon, ellipse=ellipse, rect=rect) & self.mask
        self.H[m] -= depth
        if material:
            self.mat[m] = material
        return m

    def rivets(self, pts, size=1, rise=0.8):
        for (x, y) in pts:
            for dy in range(size):
                for dx in range(size):
                    if 0 <= x + dx < self.w and 0 <= y + dy < self.h and self.mask[y + dy, x + dx]:
                        self.H[y + dy, x + dx] += rise

    def vents(self, x0, y0, n, step, w, h, horizontal=True):
        for i in range(n):
            if horizontal:
                self.recess(rect=(x0, y0 + i * step, x0 + w - 1, y0 + i * step + h - 1), depth=1.5, material="dark")
            else:
                self.recess(rect=(x0 + i * step, y0, x0 + i * step + w - 1, y0 + h - 1), depth=1.5, material="dark")

    def scuff(self, n=30, where=None, strength=0.5, size=(1, 3)):
        """Wear: small darker or lighter clusters, so big areas aren't plain."""
        for _ in range(n):
            x, y = self.rng.randrange(self.w), self.rng.randrange(self.h)
            if not self.mask[y, x] or (where and self.mat[y, x] not in where):
                continue
            s = self.rng.choice([-1, -1, 1]) * strength
            ln = self.rng.randint(*size)
            horiz = self.rng.random() < 0.6
            for k in range(ln):
                xx, yy = (x + k, y) if horiz else (x, y + k)
                if 0 <= xx < self.w and 0 <= yy < self.h and self.mask[yy, xx]:
                    self.wear[yy, xx] += s

    def line(self, pts, width=1):
        im = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(im).line([tuple(p) for p in pts], fill=255, width=width)
        self.lines |= (np.array(im) > 0) & self.mask

    # ---- render
    def render(self, outline=True, ao=0.3, ambient=0.3, levels=None):
        H = self.H
        gy, gx = np.gradient(ndimage.gaussian_filter(H, 0.6))
        gy, gx = gy * self.relief, gx * self.relief
        n = np.dstack([-gx, -gy, np.ones_like(H)])
        n /= np.linalg.norm(n, axis=2, keepdims=True)
        diff = np.clip((n * self.light).sum(axis=2), 0, 1)
        # ambient occlusion: lower than the blurred surroundings means darker
        occl = np.clip((ndimage.gaussian_filter(H, 2.5) - H) / 4.0, 0, 1)
        # gloss
        view = np.array([0, 0, 1], np.float32)
        half = self.light + view
        half /= np.linalg.norm(half)
        spec = np.clip((n * half).sum(axis=2), 0, 1) ** 40
        v = ambient + (1 - ambient) * diff - ao * occl + 0.06 * self.wear
        v = np.clip(v, 0, 1)
        out = np.zeros((self.h, self.w, 4), np.float32)
        ys, xs = np.nonzero(self.mask)
        for y, x in zip(ys, xs):
            m = self.mat[y, x] or "hull"
            if m in GLOWS:
                ramp = GLOWS[m]
                k = int(np.clip(v[y, x] * len(ramp) + 0.5, 0, len(ramp) - 1))
                k = max(k, 1)
            else:
                ramp = RAMPS[m]
                val = v[y, x]
                if m in GLOSSY:
                    val = min(1.0, val + 0.9 * spec[y, x])
                else:
                    val = min(1.0, val + 0.25 * spec[y, x])
                steps = len(ramp) if levels is None else levels
                k = int(np.clip(round(val * (len(ramp) - 1)), 0, len(ramp) - 1))
            col = _hex(ramp[k])
            out[y, x, :3] = col
            out[y, x, 3] = 255
        # part lines: one ramp step darker than what they cross, never black
        ln = self.lines & self.mask
        out[ln, :3] *= 0.62
        img = Image.fromarray(out.astype(np.uint8), "RGBA")
        if outline:
            a = np.array(img)
            m = a[:, :, 3] > 0
            ring = ndimage.binary_dilation(m, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]]) & ~m
            a[ring] = OUTLINE
            img = Image.fromarray(a, "RGBA")
        return img.copy()


def glow_dot(img, x, y, material="glow", r=1):
    """A small light, drawn after render (no lighting)."""
    ramp = GLOWS[material]
    px = img.load()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if 0 <= x + dx < img.width and 0 <= y + dy < img.height and px[x + dx, y + dy][3]:
                d = abs(dx) + abs(dy)
                col = _hex(ramp[max(0, len(ramp) - 1 - d)])
                px[x + dx, y + dy] = (int(col[0]), int(col[1]), int(col[2]), 255)
