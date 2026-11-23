"""Item icons for the relics (museum pieces) and the ship-salvage items (23 Nov 2026).

Since 23 Nov the relic pictures in art/museum/ are the finished hand-drawn art (the art tools' relics4.py), so this
script no longer draws them: it only copies them, and the salvage icons, into art/items.png. The old placeholder
drawing functions are kept below for reference but not used.

Draws each relic as a 24x24 picture in art/museum/<name>.png (the case shows it) and adds the relics and the
salvage items to the end of the hand-made art/items.png, in the order of NEW_ICONS below (their "icon" numbers in
scripts/item_data.gd start at FIRST_SLOT). The salvage icons are the artist's own from art/items/; only the relics
are drawn here, in the museum pictures' style (flat colours, one light and one dark shade, a brown outline).
They are placeholders until the artist draws the relics.

Run from the repo root:  python3 -I tools/dev/relic_art.py
Running it again rewrites the same slots, so it is safe to repeat.
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ART = os.path.join(ROOT, "art")
FIRST_SLOT = 31
OUTLINE = (91, 51, 45, 255)

# colour ramps: (dark, base, light)
RAMP = {
    "gold": ((143, 95, 36), (201, 146, 49), (237, 198, 90)),
    "steel": ((111, 104, 120), (156, 160, 172), (214, 218, 226)),
    "bone": ((156, 138, 143), (201, 184, 166), (232, 217, 189)),
    "teal": ((38, 88, 98), (63, 127, 136), (159, 209, 191)),
    "red": ((140, 48, 52), (201, 74, 74), (232, 120, 110)),
    "wood": ((90, 58, 34), (143, 95, 36), (184, 128, 70)),
    "black": ((36, 34, 44), (58, 55, 68), (92, 88, 104)),
    "green": ((60, 110, 60), (100, 168, 80), (170, 224, 120)),
    "glass": ((120, 150, 160), (176, 206, 212), (236, 248, 250)),
    "navy": ((24, 38, 58), (38, 58, 82), (70, 96, 126)),
    "maroon": ((84, 30, 40), (128, 46, 56), (170, 72, 76)),
}


class Pic:
    def __init__(self):
        self.k = {}                      # (x, y) -> ramp name, drawn in order (later on top)

    def _mask(self, draw_fn):
        m = Image.new("L", (24, 24), 0)
        draw_fn(ImageDraw.Draw(m))
        return [(x, y) for y in range(24) for x in range(24) if m.getpixel((x, y)) > 127]

    def ell(self, box, ramp):
        for p in self._mask(lambda d: d.ellipse(box, fill=255)):
            self.k[p] = ramp
        return self

    def rect(self, box, ramp):
        for p in self._mask(lambda d: d.rectangle(box, fill=255)):
            self.k[p] = ramp
        return self

    def poly(self, pts, ramp):
        for p in self._mask(lambda d: d.polygon(pts, fill=255)):
            self.k[p] = ramp
        return self

    def line(self, pts, ramp, w=1):
        for p in self._mask(lambda d: d.line(pts, fill=255, width=w)):
            self.k[p] = ramp
        return self

    def px(self, pts, ramp):
        for p in pts:
            self.k[p] = ramp
        return self

    def cut(self, pts):
        for p in pts:
            self.k.pop(p, None)
        return self

    def image(self):
        im = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
        for (x, y), r in self.k.items():
            dark, base, light = RAMP[r]
            up = self.k.get((x, y - 1)) == r and self.k.get((x - 1, y)) == r
            down = self.k.get((x, y + 1)) == r and self.k.get((x + 1, y)) == r
            c = light if not up else dark if not down else base
            im.putpixel((x, y), c + (255,))
        # outline: any empty pixel touching a drawn one (4 ways)
        for y in range(24):
            for x in range(24):
                if (x, y) in self.k:
                    continue
                if any((x + dx, y + dy) in self.k for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    im.putpixel((x, y), OUTLINE)
        return im


def pilgrim_bell():          # a small silver bell on a teal cord, with a tassel
    p = Pic().line([(12, 1), (12, 5)], "teal").ell((7, 5, 17, 13), "steel").poly([(7, 9), (17, 9), (19, 17), (5, 17)], "steel")
    p.rect((4, 17, 20, 18), "steel").line([(12, 18), (12, 22)], "teal")
    return p.ell((10, 18, 14, 22), "teal")


def station_crest():          # a steel plate with the station's red star
    p = Pic().rect((3, 5, 20, 18), "steel").cut([(3, 5), (20, 5), (3, 18), (20, 18)])
    p.poly([(11, 7), (13, 11), (17, 11), (14, 13), (15, 17), (11, 14), (8, 17), (9, 13), (6, 11), (10, 11)], "red")
    return p.px([(5, 7), (18, 7), (5, 16), (18, 16)], "black")


def duellist_bell():          # a gold hand bell with a red ribbon
    p = Pic().rect((11, 2, 12, 7), "wood").poly([(6, 18), (7, 10), (11, 7), (13, 7), (17, 10), (18, 18)], "gold")
    p.rect((5, 18, 19, 19), "gold").ell((10, 19, 14, 22), "gold")
    return p.poly([(13, 8), (19, 6), (21, 9), (17, 10)], "red").poly([(17, 10), (20, 14), (18, 15)], "red")


def convoy_charm():           # a carved wooden charm on a string, with a teal bead
    p = Pic().line([(12, 1), (12, 5)], "black").ell((10, 4, 14, 8), "teal")
    p.poly([(12, 8), (18, 13), (16, 21), (8, 21), (6, 13)], "wood")
    return p.line([(9, 14), (15, 14)], "bone").line([(12, 11), (12, 19)], "bone")


def garden_seeds():           # a stoppered jar of glowing green seeds
    p = Pic().rect((7, 7, 16, 21), "glass").rect((9, 3, 14, 6), "wood")
    p.ell((8, 13, 15, 21), "green")
    return p.px([(9, 16), (12, 15), (14, 17), (10, 19), (13, 19)], "gold")


def rabble_flag():            # a torn black banner on a pole
    p = Pic().line([(4, 2), (4, 22)], "wood", 2)
    p.poly([(6, 3), (20, 3), (17, 7), (20, 11), (16, 12), (18, 15), (6, 15)], "black")
    p.ell((10, 5, 14, 9), "bone").rect((11, 9, 13, 10), "bone")
    return p.line([(8, 11), (16, 14)], "bone").line([(16, 11), (8, 14)], "bone")


def bone_dice():              # two bone dice
    p = Pic().rect((3, 9, 11, 17), "bone").rect((12, 6, 20, 14), "bone")
    p.px([(5, 11), (9, 15), (7, 13)], "maroon")
    return p.px([(14, 8), (18, 8), (14, 12), (18, 12)], "maroon")


def star_compass():           # a brass compass with a teal face and a red needle
    p = Pic().ell((3, 3, 20, 20), "gold").ell((6, 6, 17, 17), "teal").rect((10, 1, 13, 3), "gold")
    return p.poly([(12, 7), (13, 12), (11, 12)], "red").poly([(11, 12), (13, 12), (12, 16)], "bone")


def captain_signet():         # a gold ring with a red stone
    p = Pic().ell((4, 7, 19, 21), "gold").cut([(x, y) for y in range(24) for x in range(24)
                                              if (x - 11.5) ** 2 / 25 + (y - 14.5) ** 2 / 20 < 1])
    return p.ell((8, 3, 15, 9), "red").px([(10, 5)], "glass")


def gold_tooth():             # a big gold fang on a cord
    p = Pic().line([(3, 6), (8, 4), (16, 4), (21, 6)], "black")
    p.poly([(7, 5), (17, 5), (16, 11), (13, 20), (11, 20), (8, 11)], "gold")
    return p.line([(10, 7), (11, 14)], "bone")


def captain_log():            # a battered maroon log book with a gold clasp
    p = Pic().rect((4, 3, 18, 20), "maroon").rect((19, 4, 20, 20), "bone")
    p.rect((7, 7, 15, 10), "gold").rect((16, 11, 20, 13), "gold")
    return p.px([(5, 18), (6, 19)], "bone")


# Order = slots in items.png from FIRST_SLOT. Salvage items use the artist's icons from art/items/.
NEW_ICONS = [
    ("scrap", None), ("circuit_board", None), ("lithium_cell", None), ("rare_earths", None),
    ("helium_3", None), ("cobalt_60", None), ("void_sapphire", None),
    ("relic_pilgrim_bell", pilgrim_bell), ("relic_station_crest", station_crest),
    ("relic_duellist_bell", duellist_bell), ("relic_convoy_charm", convoy_charm),
    ("relic_garden_seeds", garden_seeds), ("relic_rabble_flag", rabble_flag), ("relic_bone_dice", bone_dice),
    ("relic_star_compass", star_compass), ("relic_captain_signet", captain_signet),
    ("relic_gold_tooth", gold_tooth), ("relic_captain_log", captain_log),
    ("hydro_bed", None),                                                     # slot 49 (23 Nov): the hydroponic bed
    ("silica_sand", None), ("lithium_salts", None),                          # slots 50-51 (23 Nov): new cavern ores
]


def main():
    items_path = os.path.join(ART, "items.png")
    items = Image.open(items_path).convert("RGBA")
    cell = items.height
    need = FIRST_SLOT + len(NEW_ICONS)
    out = Image.new("RGBA", (max(items.width // cell, need) * cell, cell), (0, 0, 0, 0))
    out.paste(items.crop((0, 0, FIRST_SLOT * cell, cell)), (0, 0))
    os.makedirs(os.path.join(ART, "museum"), exist_ok=True)
    for i, (name, fn) in enumerate(NEW_ICONS):
        if name.startswith("relic_"):
            pic = Image.open(os.path.join(ART, "museum", name.replace("relic_", "") + ".png")).convert("RGBA")
        else:
            pic = Image.open(os.path.join(ART, "items", name + ".png")).convert("RGBA")
        if pic.size != (cell, cell):
            pic = pic.resize((cell, cell), Image.NEAREST)
        out.paste(pic, ((FIRST_SLOT + i) * cell, 0))
    out.save(items_path)
    print("items.png: %d icons; relic pictures in art/museum/" % (out.width // cell))


if __name__ == "__main__":
    main()
