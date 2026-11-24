"""Stand-in icons for the datapad's Perks tab (24 Nov 2026): art/perks.png, one 24x24 cell per perk or keepsake, in
the order of the "icon" numbers in scripts/perk_data.gd. Each is something of the resident who gave it (Zachary:
"the icons will be stuff like freyas wrench"), drawn here from simple shapes until the artist draws them. The Art
Fix List has a row listing what each one should be.

Run from the repo root:  python3 -I tools/dev/perk_icons.py
Safe to run again: it rewrites the whole sheet.
"""
import math
import os
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "art", "perks.png")
CELL = 24
LINE = (70, 40, 38, 255)

# icon number -> [what it is, shape, main colour, accent colour]
ICONS = [
    ["Jorvik's stabilizer (a brass gyroscope)", "gyro", (200, 160, 70), (120, 180, 220)],
    ["Freya's wrench", "wrench", (170, 178, 190), (230, 120, 60)],
    ["A bistro menu card", "card", (246, 236, 210), (180, 60, 60)],
    ["Jasper's whisk", "whisk", (200, 205, 215), (150, 100, 60)],
    ["A sprig of lavender", "sprig", (160, 120, 210), (90, 150, 80)],
    ["Evarra's trowel", "trowel", (160, 170, 180), (150, 100, 60)],
    ["A jar of wildflower honey", "jar", (240, 180, 50), (250, 240, 220)],
    ["A starlight souffle", "souffle", (240, 210, 140), (250, 250, 230)],
    ["A place set at the family table", "plate", (245, 245, 240), (200, 160, 70)],
    ["Job's work gloves", "glove", (200, 150, 70), (150, 100, 50)],
    ["A jar of xeno-salve", "jar", (120, 210, 170), (250, 240, 220)],
    ["Quill's pressed glowing fern", "sprig", (120, 230, 200), (60, 140, 120)],
    ["A star-knight shield", "shield", (180, 190, 210), (240, 200, 80)],
    ["Ix'ali's star pendant", "star", (240, 200, 80), (140, 110, 60)],
    ["A scouts' map with marks", "card", (230, 220, 180), (80, 140, 80)],
    ["Artie's tin camp mug", "mug", (160, 170, 180), (110, 120, 130)],
    ["Stu's bellhop cap", "cap", (140, 40, 50), (240, 200, 80)],
    ["Ana's navigator's compass", "compass", (210, 180, 90), (230, 70, 60)],
    ["S.A.R.A.'s little holo-moon", "moon", (120, 200, 240), (220, 240, 255)],
    ["Tar'Besh's appraiser's loupe", "loupe", (200, 160, 70), (180, 220, 240)],
    ["Zaas's sonar lure", "lure", (80, 170, 160), (240, 200, 80)],
    ["S.A.R.A.'s motion sensor", "device", (110, 120, 140), (240, 80, 70)],
    ["A chitin-piercer spike", "spike", (200, 190, 160), (120, 90, 60)],
    ["The Moogli trade beacon", "device", (200, 150, 60), (120, 230, 120)],
    ["Tikka's furnace gauge", "gauge", (180, 120, 70), (240, 90, 50)],
    ["Folded void-silk", "cloth", (90, 70, 140), (180, 160, 230)],
    ["Maren's med-stim", "stick", (220, 220, 225), (220, 60, 60)],
    ["Owen's compendium", "book", (120, 70, 50), (230, 200, 120)],
    ["Tobbin's chisel", "stick", (200, 160, 110), (170, 178, 190)],
    ["Merrow's grease pencil", "stick", (90, 150, 110), (60, 60, 70)],
    ["Garrick's chalk", "stick", (245, 245, 240), (200, 200, 195)],
    ["Saffi's soup bowl", "bowl", (210, 130, 70), (240, 200, 120)],
    ["Freya's wrench pendant", "pendant", (190, 196, 205), (220, 200, 120)],
    ["Jasper's cafe apron", "cloth", (240, 235, 220), (200, 70, 60)],
    ["Evarra's pressed flowers, framed", "frame", (160, 110, 70), (230, 120, 170)],
    ["Job's oar charm", "oar", (180, 130, 80), (140, 100, 60)],
    ["Quill's stethoscope compass", "compass", (200, 160, 70), (120, 200, 180)],
    ["Ix'ali's ceremonial pauldron", "shield", (200, 205, 220), (120, 90, 170)],
    ["The Honorary Scoutmaster badge", "star", (90, 150, 80), (240, 200, 80)],
    ["Stu's silver bell", "bell", (210, 215, 225), (150, 155, 170)],
    ["Ana's flight jacket", "cloth", (120, 80, 50), (200, 160, 100)],
    ["The family photo", "frame", (200, 160, 70), (120, 170, 210)],
]


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (255,)


def draw(d, shape, main, acc):
    m, a, dk = main + (255,), acc + (255,), shade(main, 0.65)
    if shape == "gyro":
        d.ellipse([4, 4, 19, 19], outline=LINE, width=2)
        d.ellipse([7, 7, 16, 16], fill=m, outline=dk)
        d.line([(4, 12), (19, 12)], fill=a, width=1)
        d.ellipse([10, 10, 13, 13], fill=a)
    elif shape == "wrench":
        d.line([(6, 18), (16, 8)], fill=LINE, width=5)
        d.line([(6, 18), (16, 8)], fill=m, width=3)
        d.ellipse([12, 2, 21, 11], fill=m, outline=LINE)
        d.polygon([(15, 1), (22, 1), (22, 8), (17, 6)], fill=(0, 0, 0, 0))     # the open jaw
        d.ellipse([3, 15, 9, 21], fill=a, outline=LINE)
    elif shape == "card":
        d.rectangle([5, 3, 18, 20], fill=m, outline=LINE)
        for y in (7, 10, 13, 16):
            d.line([(8, y), (15, y)], fill=a)
    elif shape == "whisk":
        d.line([(5, 20), (11, 13)], fill=a, width=3)
        for k in range(3):
            d.ellipse([9 + k, 2 + k, 20 - k, 15 - k], outline=m)
        d.ellipse([9, 2, 20, 15], outline=LINE)
    elif shape == "sprig":
        d.line([(8, 21), (14, 4)], fill=a, width=2)
        for i, y in enumerate((5, 8, 11, 14)):
            x = 14 - i * 2
            d.ellipse([x - 4, y, x - 1, y + 3], fill=m, outline=dk)
            d.ellipse([x + 1, y + 1, x + 4, y + 4], fill=m, outline=dk)
    elif shape == "trowel":
        d.line([(4, 20), (10, 14)], fill=a, width=3)
        d.polygon([(10, 14), (18, 4), (21, 7), (13, 16)], fill=m, outline=LINE)
    elif shape == "jar":
        d.rectangle([7, 5, 16, 7], fill=shade(acc, 0.8), outline=LINE)
        d.rounded_rectangle([5, 7, 18, 20], radius=3, fill=m, outline=LINE)
        d.rectangle([8, 11, 15, 15], fill=a)
    elif shape == "souffle":
        d.rectangle([5, 13, 18, 20], fill=a, outline=LINE)
        d.ellipse([4, 6, 19, 16], fill=m, outline=LINE)
        d.point((11, 8), fill=(255, 255, 255, 255))
    elif shape == "plate":
        d.ellipse([4, 5, 19, 20], fill=m, outline=LINE)
        d.ellipse([7, 8, 16, 17], outline=a)
        d.line([(2, 6), (2, 19)], fill=LINE)
        d.line([(21, 6), (21, 19)], fill=LINE)
    elif shape == "glove":
        d.rounded_rectangle([6, 9, 17, 21], radius=3, fill=m, outline=LINE)
        for x in (7, 10, 13):
            d.rectangle([x, 3, x + 2, 10], fill=m, outline=LINE)
        d.rectangle([16, 8, 19, 13], fill=m, outline=LINE)
        d.line([(6, 18), (17, 18)], fill=a)
    elif shape == "shield":
        d.polygon([(4, 4), (19, 4), (19, 12), (12, 21), (4, 12)], fill=m, outline=LINE)
        d.line([(12, 6), (12, 17)], fill=a, width=2)
        d.line([(7, 10), (16, 10)], fill=a, width=2)
    elif shape in ("star", "pendant"):
        if shape == "pendant":
            d.line([(4, 2), (12, 9), (20, 2)], fill=a)
            cx, cy, ro, ri = 12, 15, 6, 2
            d.line([(12, 10), (12, 20)], fill=LINE, width=4)
            d.line([(12, 10), (12, 20)], fill=m, width=2)
            d.ellipse([9, 8, 15, 13], outline=LINE, fill=m)
            return
        cx, cy, ro, ri = 12, 12, 10, 4
        pts = []
        for k in range(10):
            r = ro if k % 2 == 0 else ri
            ang = -math.pi / 2 + k * math.pi / 5
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        d.polygon(pts, fill=m, outline=LINE)
        d.ellipse([10, 10, 14, 14], fill=a)
    elif shape == "mug":
        d.rectangle([5, 7, 15, 20], fill=m, outline=LINE)
        d.arc([12, 10, 20, 17], -90, 90, fill=LINE, width=2)
        d.line([(5, 9), (15, 9)], fill=a)
        d.line([(8, 2), (9, 5)], fill=(220, 220, 230, 255))
        d.line([(12, 2), (11, 5)], fill=(220, 220, 230, 255))
    elif shape == "cap":
        d.rectangle([5, 8, 18, 17], fill=m, outline=LINE)
        d.rectangle([3, 16, 20, 19], fill=shade(main, 0.7), outline=LINE)
        d.line([(5, 11), (18, 11)], fill=a, width=2)
    elif shape == "compass":
        d.ellipse([3, 3, 20, 20], fill=m, outline=LINE)
        d.ellipse([6, 6, 17, 17], fill=(245, 240, 225, 255))
        d.polygon([(12, 7), (14, 12), (12, 16), (10, 12)], fill=a)
    elif shape == "moon":
        d.ellipse([4, 4, 19, 19], fill=m, outline=shade(main, 0.6))
        d.ellipse([8, 7, 11, 10], fill=shade(main, 0.8))
        d.ellipse([13, 12, 16, 15], fill=shade(main, 0.8))
        d.arc([2, 2, 21, 21], 200, 340, fill=a)
    elif shape == "loupe":
        d.line([(14, 14), (20, 20)], fill=LINE, width=4)
        d.ellipse([3, 3, 15, 15], fill=a, outline=LINE, width=2)
        d.ellipse([3, 3, 15, 15], outline=m)
    elif shape == "lure":
        d.ellipse([5, 8, 19, 16], fill=m, outline=LINE)
        d.polygon([(19, 12), (22, 8), (22, 16)], fill=m, outline=LINE)
        d.ellipse([7, 10, 9, 12], fill=a)
        d.arc([2, 14, 10, 22], 0, 180, fill=LINE)
    elif shape == "device":
        d.rectangle([5, 7, 18, 20], fill=m, outline=LINE)
        d.ellipse([9, 2, 14, 7], fill=a, outline=LINE)
        d.line([(8, 12), (15, 12)], fill=shade(main, 0.6))
        d.line([(8, 15), (15, 15)], fill=shade(main, 0.6))
    elif shape == "spike":
        d.polygon([(12, 2), (16, 14), (8, 14)], fill=m, outline=LINE)
        d.rectangle([7, 14, 17, 18], fill=a, outline=LINE)
        d.line([(12, 18), (12, 22)], fill=LINE, width=2)
    elif shape == "gauge":
        d.ellipse([3, 4, 20, 21], fill=m, outline=LINE)
        d.ellipse([6, 7, 17, 18], fill=(245, 235, 215, 255))
        d.line([(11, 13), (16, 8)], fill=a, width=2)
        d.arc([6, 7, 17, 18], 200, 340, fill=shade(main, 0.6))
    elif shape == "cloth":
        d.polygon([(4, 8), (12, 4), (20, 8), (20, 19), (4, 19)], fill=m, outline=LINE)
        d.line([(4, 12), (20, 12)], fill=a, width=2)
        d.line([(12, 4), (12, 19)], fill=shade(main, 0.75))
    elif shape == "stick":
        d.line([(5, 19), (18, 6)], fill=LINE, width=5)
        d.line([(5, 19), (18, 6)], fill=m, width=3)
        d.line([(16, 8), (20, 4)], fill=a, width=3)
    elif shape == "book":
        d.rectangle([5, 4, 18, 20], fill=m, outline=LINE)
        d.rectangle([5, 4, 7, 20], fill=shade(main, 0.7))
        d.rectangle([10, 8, 15, 11], fill=a)
    elif shape == "bowl":
        d.chord([3, 6, 20, 21], 0, 180, fill=m, outline=LINE)
        d.line([(3, 13), (20, 13)], fill=a, width=2)
        d.line([(9, 4), (10, 9)], fill=(230, 230, 235, 255))
        d.line([(14, 4), (13, 9)], fill=(230, 230, 235, 255))
    elif shape == "frame":
        d.rectangle([3, 4, 20, 20], fill=m, outline=LINE)
        d.rectangle([6, 7, 17, 17], fill=(245, 240, 225, 255))
        d.ellipse([8, 9, 12, 13], fill=a)
        d.ellipse([12, 11, 16, 15], fill=a)
    elif shape == "oar":
        d.line([(5, 20), (15, 7)], fill=m, width=2)
        d.ellipse([13, 2, 20, 11], fill=m, outline=LINE)
        d.line([(2, 6), (12, 2)], fill=a)
    elif shape == "bell":
        d.chord([5, 5, 18, 22], 180, 360, fill=m, outline=LINE)
        d.rectangle([5, 13, 18, 17], fill=m)
        d.line([(4, 17), (19, 17)], fill=LINE, width=2)
        d.ellipse([10, 17, 13, 20], fill=a)
        d.ellipse([10, 2, 13, 5], outline=LINE)
    else:
        raise ValueError(shape)


def main():
    sheet = Image.new("RGBA", (CELL * len(ICONS), CELL), (0, 0, 0, 0))
    for i, (_what, shape, main, acc) in enumerate(ICONS):
        cell = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        draw(ImageDraw.Draw(cell), shape, main, acc)
        sheet.alpha_composite(cell, (i * CELL, 0))
    sheet.save(OUT)
    print("perk icons: %d written to art/perks.png" % len(ICONS))


if __name__ == "__main__":
    main()
