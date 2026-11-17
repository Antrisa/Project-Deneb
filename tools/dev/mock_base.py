from PIL import Image, ImageDraw, ImageFont
import math, os
MOCK = os.environ.get("MOCK_OUT", "mock")
os.makedirs(MOCK, exist_ok=True)
S = 12
BG, ROCK, WALL = (14, 18, 30), (92, 84, 102), (36, 40, 54)
PATH, CORE, OBS, MUSEUM, SANCT, LAB, STORE, HOME, SPARE, LIFT, GLASS = (226, 214, 190), (120, 196, 196), (150, 178, 206), (198, 168, 128), (168, 132, 210), (150, 150, 160), (176, 168, 150), (206, 146, 128), (190, 200, 170), (240, 200, 80), (120, 210, 240)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
FT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)


class Mock:
    def __init__(self, w, h, title, sub):
        self.im = Image.new("RGB", (w * S, h * S + 70), BG); self.d = ImageDraw.Draw(self.im)
        self.d.text((14, 8), title, fill=(255, 226, 150), font=FT); self.d.text((14, 40), sub, fill=(220, 220, 230), font=FS)
    def P(self, x, y): return (x * S, y * S + 70)
    def circ(self, cx, cy, r, fill, outline=WALL, width=3):
        self.d.ellipse(self.P(cx - r, cy - r) + self.P(cx + r, cy + r), fill=fill, outline=outline, width=width)
    def sector(self, cx, cy, r0, r1, a0, a1, fill, outline=WALL, width=3):
        pts = [self.P(cx + r1 * math.cos(math.radians(a)), cy + r1 * math.sin(math.radians(a))) for a in frange(a0, a1)]
        pts += [self.P(cx + r0 * math.cos(math.radians(a)), cy + r0 * math.sin(math.radians(a))) for a in frange(a1, a0)]
        self.d.polygon(pts, fill=fill, outline=outline, width=width)
    def rect(self, x0, y0, x1, y1, fill, outline=WALL, width=3):
        self.d.rectangle(self.P(x0, y0) + self.P(x1, y1), fill=fill, outline=outline, width=width)
    def arc(self, cx, cy, r, a0, a1, fill, width):
        self.d.arc(self.P(cx - r, cy - r) + self.P(cx + r, cy + r), a0, a1, fill=fill, width=width)
    def label(self, x, y, text, font=None, fill=(24, 24, 34)):
        font = font or F; lines = text.split("\n"); yy = y * S + 70 - 9 * len(lines)
        for i, ln in enumerate(lines):
            f = font if i == 0 else FS
            w = self.d.textlength(ln, font=f); self.d.text((x * S - w / 2, yy), ln, fill=fill, font=f); yy += 18 if i == 0 else 15
    def door(self, x, y, locked=False):
        c = (220, 80, 70) if locked else (250, 220, 90)
        self.d.rectangle(self.P(x - .9, y - .9) + self.P(x + .9, y + .9), fill=c, outline=WALL, width=2)
    def dot(self, x, y, c, r=.7):
        self.d.ellipse(self.P(x - r, y - r) + self.P(x + r, y + r), fill=c, outline=WALL, width=1)
    def legend(self, x, y, rows):
        for i, (c, t) in enumerate(rows):
            self.d.rectangle(self.P(x, y + i * 2.2) + self.P(x + 1.4, y + i * 2.2 + 1.4), fill=c, outline=WALL)
            self.d.text(self.P(x + 2.2, y + i * 2.2 - .1), t, fill=(230, 230, 236), font=FS)


def frange(a, b, step=3):
    n = max(2, int(abs(b - a) / step) + 1)
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def pol(cx, cy, r, a): return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))


