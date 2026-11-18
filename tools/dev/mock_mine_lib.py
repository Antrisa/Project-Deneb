"""Mine / North Cave / Caverns layout mock-ups (Nov 2026). Faceted walls only: straight and 45 degrees."""
from PIL import Image, ImageDraw, ImageFont
import math, os, random

OUT = os.environ.get("MOCK_OUT", "mock"); os.makedirs(OUT, exist_ok=True)
S = 12
BG, ROCKBG, WALL = (14, 18, 30), (58, 52, 52), (30, 26, 30)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
FT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)

DIG, HEAD, LOAD, SURV, GATE, NCAVE, CAV, JUNC = (176, 152, 122), (206, 196, 172), (196, 176, 120), (170, 160, 196), (196, 120, 100), (150, 140, 128), (110, 110, 130), (200, 184, 150)
ROCK, PILLAR = (120, 112, 108), (78, 70, 70)
ORE_I, ORE_C, CRYST = (200, 204, 214), (226, 140, 74), (176, 136, 226)
BELT, ANALY, CRATE, LAMP, WATER, FUNG = (52, 52, 62), (90, 200, 210), (170, 130, 80), (255, 226, 120), (70, 140, 200), (140, 220, 140)
DOOR = (250, 220, 90)
WHITE = (236, 236, 240)


class Mock:
    def __init__(self, w, h, title, sub):
        self.im = Image.new("RGB", (w * S, h * S + 74), BG); self.d = ImageDraw.Draw(self.im)
        self.d.text((14, 8), title, fill=(255, 226, 150), font=FT); self.d.text((14, 42), sub, fill=(220, 220, 230), font=FS)
    def P(self, x, y): return (x * S, y * S + 74)
    def poly(self, pts, fill, outline=WALL, w=3): self.d.polygon([self.P(*p) for p in pts], fill=fill, outline=outline, width=w)
    def rect(self, x0, y0, x1, y1, fill, outline=WALL, w=3): self.d.rectangle(self.P(x0, y0) + self.P(x1, y1), fill=fill, outline=outline, width=w)
    def oct(self, x0, y0, x1, y1, fill, cut=3, outline=WALL):
        c = cut
        self.poly([(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)], fill, outline)
    def label(self, x, y, text, font=F, fill=(24, 24, 34), plate=True):
        lines = text.split("\n"); yy = y * S + 74 - 8 * len(lines)
        if plate and fill == (24, 24, 34):
            wmax = max(self.d.textlength(ln, font=font if i == 0 else FS) for i, ln in enumerate(lines))
            hh = 18 + 15 * (len(lines) - 1)
            self.d.rounded_rectangle((x * S - wmax / 2 - 5, yy - 2, x * S + wmax / 2 + 5, yy + hh + 2), 4, fill=(240, 232, 214), outline=(90, 80, 70))
        for i, ln in enumerate(lines):
            f = font if i == 0 else FS
            w = self.d.textlength(ln, font=f); self.d.text((x * S - w / 2, yy), ln, fill=fill, font=f); yy += 18 if i == 0 else 15
    def text(self, x, y, t, fill=WHITE): self.d.multiline_text(self.P(x, y), t, fill=fill, font=FS, spacing=3)
    def door(self, x, y, c=DOOR): self.d.rectangle(self.P(x - .8, y - .8) + self.P(x + .8, y + .8), fill=c, outline=WALL, width=2)
    def dot(self, x, y, c, r=.6, o=WALL): self.d.ellipse(self.P(x - r, y - r) + self.P(x + r, y + r), fill=c, outline=o, width=1)
    def box(self, x, y, w, h, c): self.d.rectangle(self.P(x, y) + self.P(x + w, y + h), fill=c, outline=WALL, width=1)
    def rock(self, x, y, c=ROCK, r=.75):
        k = r * .42
        self.poly([(x - k, y - r), (x + k, y - r), (x + r, y - k), (x + r, y + k), (x + k, y + r), (x - k, y + r), (x - r, y + k), (x - r, y - k)], c, WALL, 1)
    def ore(self, x, y, c): self.poly([(x, y - .85), (x + .85, y), (x, y + .85), (x - .85, y)], c, WALL, 1)
    def person(self, x, y, name):
        self.dot(x, y, (250, 110, 150), .8, (255, 255, 255))
        tx, ty = self.P(x + 1.1, y - .7); w = self.d.textlength(name, font=FS)
        self.d.rounded_rectangle((tx - 2, ty - 1, tx + w + 3, ty + 15), 3, fill=(120, 30, 70)); self.d.text((tx, ty), name, fill=(255, 225, 235), font=FS)
    def belt(self, pts):
        for a, b in zip(pts, pts[1:]):
            self.d.line([self.P(*a), self.P(*b)], fill=BELT, width=int(1.2 * S)); self.d.line([self.P(*a), self.P(*b)], fill=(200, 160, 60), width=2)
    def legend(self, x, y, rows):
        for i, (c, t) in enumerate(rows):
            self.d.rectangle(self.P(x, y + i * 2.2) + self.P(x + 1.4, y + i * 2.2 + 1.4), fill=c, outline=WALL)
            self.d.text(self.P(x + 2.2, y + i * 2.2 - .1), t, fill=WHITE, font=FS)
        return y + len(rows) * 2.2
    def grid(self, x0, y0, x1, y1):
        for x in range(x0, x1 + 1, 10): self.d.line([self.P(x, y0), self.P(x, y1)], fill=(90, 84, 84), width=1)
        for y in range(y0, y1 + 1, 10): self.d.line([self.P(x0, y), self.P(x1, y)], fill=(90, 84, 84), width=1)
    def save(self, name): self.im.save(f"{OUT}/{name}.png"); print("wrote", name)


def inside(poly, x, y):
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c


def octp(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


SHAPES = []          # floor shapes rocks may sit in (set per map)


def scatter(m, x0, y0, x1, y1, n, kinds, seed, avoid=()):
    """rocks and ore dotted over a dig area; kinds = [(colour, weight)]; kept 1.3 tiles inside the walls"""
    r = random.Random(seed); pts = []
    tries = 0
    while len(pts) < n and tries < 6000:
        tries += 1
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        if SHAPES and not any(all(inside(sh, x + dx, y + dy) for dx, dy in ((1.3, 0), (-1.3, 0), (0, 1.3), (0, -1.3), (.95, .95), (-.95, .95), (.95, -.95), (-.95, -.95))) for sh in SHAPES): continue
        if any(ax0 <= x <= ax1 and ay0 <= y <= ay1 for ax0, ay0, ax1, ay1 in avoid): continue
        if any(math.hypot(x - a, y - b) < 2.2 for a, b in pts): continue
        pts.append((x, y))
    tot = sum(w for _, w in kinds)
    for x, y in pts:
        v = r.uniform(0, tot)
        for c, w in kinds:
            if v <= w:
                (m.rock(x, y) if c == ROCK else m.ore(x, y, c)); break
            v -= w


