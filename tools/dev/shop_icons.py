"""Item icons for the shop items (23 Nov 2026): geodes and minerals, Rusk's drinks, Jasper's ingredients and
dishes, Sesska's clothes, Ix'ali's armour and the hotel's French dishes (scripts/item_data.gd icons 72-117).

Copies the artist's own icon from art/items/<name>.png where there is one, and otherwise draws a plain
placeholder (a gem, a cup, a bowl or a garment in the item's colour) until the artist draws it. The list of
placeholders is printed, and is the price sheet's Icons tab.

Run from the repo root:  python3 -I tools/dev/shop_icons.py
Running it again rewrites the same slots, so it is safe to repeat.
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ATLAS = os.path.join(ROOT, "art", "items.png")
ITEMS = os.path.join(ROOT, "art", "items")
FIRST_SLOT = 72
CELL = 24
OUTLINE = (91, 51, 45, 255)

# In icon order: [item id, art/items name or None, placeholder shape, colour]
ICONS = [
    ["cavern_geode", "geode_intact", "gem", (110, 100, 120)],
    ["lunar_agate", "lunar_agate", "gem", (200, 196, 182)],
    ["anorthosite", "anorthosite", "gem", (232, 228, 214)],
    ["moon_olivine", "moon_olivine", "gem", (120, 168, 70)],
    ["regolith_jasper", "regolith_jasper", "gem", (164, 82, 56)],
    ["ilmenite", "ilmenite", "gem", (64, 62, 72)],
    ["selenite_rose", "selenite_rose", "gem", (226, 206, 190)],
    ["armalcolite", "armalcolite", "gem", (82, 60, 96)],
    ["orange_glass", "orange_glass", "gem", (232, 130, 50)],
    ["spinel", "spinel", "gem", (222, 98, 140)],
    ["basalt_glass", "basalt_glass", "gem", (40, 40, 48)],
    ["fire_opal", "fire_opal", "gem", (240, 110, 40)],
    ["tranquillityite", "tranquillityite", "gem", (150, 70, 52)],
    ["house_tea", "starleaf_tea_drink", "cup", (150, 110, 60)],
    ["iced_moon_tea", "iced_moon_tea", "glass", (190, 220, 230)],
    ["ginger_brew", "ginger_brew", "cup", (210, 160, 70)],
    ["spacer_fizz", "spacer_fizz", "glass", (70, 150, 220)],
    ["night_watch", "night_watch", "cup", (60, 40, 30)],
    ["anchor_tonic", "anchor_tonic", "bottle", (90, 110, 80)],
    ["captains_reserve", "nebula_wine", "bottle", (120, 40, 60)],
    ["garden_cordial", "garden_cordial", "bottle", (120, 180, 90)],
    ["comet_float", "comet_float", "glass", (150, 200, 240)],
    ["flour", "flour", "bowl", (236, 228, 210)],
    ["milk_powder", "milk_powder", "bowl", (240, 240, 236)],
    ["moon_wheat_bread", "moon_wheat_bread", "bowl", (200, 150, 80)],
    ["crater_potato_mash", "crater_potato_mash", "bowl", (170, 120, 190)],
    ["star_tomato_soup", "star_tomato_soup", "bowl", (210, 70, 60)],
    ["mess_hall_stew", "mess_hall_stew", "bowl", (150, 100, 60)],
    ["station_breakfast", "station_breakfast", "bowl", (220, 180, 90)],
    ["knit_cap", "knit_cap", "hat", (200, 90, 70)],
    ["woven_scarf", "woven_scarf", "hat", (90, 140, 160)],
    ["work_shirt", "work_shirt", "shirt", (110, 130, 150)],
    ["woven_shawl", "woven_shawl", "shirt", (170, 120, 160)],
    ["station_coat", "station_coat", "shirt", (70, 80, 100)],
    ["silk_coat", "silk_coat", "shirt", (190, 210, 220)],
    ["hard_hat", "helmet_basic", "hat", (220, 170, 40)],
    ["padded_vest", "body_armour_basic", "shirt", (140, 110, 80)],
    ["work_boots", "boots_basic", "shirt", (110, 80, 60)],
    ["croissant", "croissant", "bowl", (220, 160, 70)],
    ["french_onion_soup", "french_onion_soup", "bowl", (190, 130, 60)],
    ["quiche_aux_poireaux", "quiche_aux_poireaux", "bowl", (230, 200, 110)],
    ["ratatouille", "ratatouille", "bowl", (200, 80, 50)],
    ["creme_brulee", "creme_brulee", "bowl", (230, 190, 110)],
    ["cassoulet", "cassoulet", "bowl", (150, 90, 50)],
    ["bouillabaisse", "bouillabaisse", "bowl", (220, 120, 60)],
    ["space_bourguignon", "space_bourguignon", "bowl", (120, 40, 40)],
]


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (255,)


def placeholder(shape, colour):
    im = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    base, dark, light = shade(colour, 1.0), shade(colour, 0.7), shade(colour, 1.25)
    if shape == "gem":
        pts = [(12, 4), (19, 10), (12, 20), (5, 10)]
        d.polygon(pts, fill=base, outline=OUTLINE)
        d.polygon([(12, 4), (15, 10), (12, 20), (9, 10)], fill=light)
        d.line([(5, 10), (19, 10)], fill=dark)
    elif shape == "cup":
        d.rectangle([6, 9, 16, 19], fill=base, outline=OUTLINE)
        d.arc([14, 11, 20, 17], 270, 90, fill=OUTLINE)
        d.line([(9, 5), (9, 7)], fill=light)
        d.line([(12, 4), (12, 7)], fill=light)
    elif shape == "glass":
        d.polygon([(6, 6), (18, 6), (16, 20), (8, 20)], fill=base, outline=OUTLINE)
        d.line([(9, 8), (9, 17)], fill=light)
    elif shape == "bottle":
        d.rectangle([10, 3, 14, 8], fill=dark, outline=OUTLINE)
        d.rectangle([7, 8, 17, 21], fill=base, outline=OUTLINE)
        d.rectangle([9, 12, 15, 16], fill=light)
    elif shape == "bowl":
        d.pieslice([4, 4, 20, 20], 0, 180, fill=base, outline=OUTLINE)
        d.line([(5, 12), (19, 12)], fill=OUTLINE)
    elif shape == "hat":
        d.pieslice([5, 6, 19, 22], 180, 360, fill=base, outline=OUTLINE)
        d.rectangle([4, 14, 20, 16], fill=dark, outline=OUTLINE)
    elif shape == "shirt":
        d.polygon([(8, 4), (16, 4), (21, 9), (18, 12), (17, 10), (17, 21), (7, 21), (7, 10), (6, 12), (3, 9)],
                  fill=base, outline=OUTLINE)
        d.line([(12, 5), (12, 20)], fill=dark)
    return im


def main():
    atlas = Image.open(ATLAS).convert("RGBA")
    need = FIRST_SLOT + len(ICONS)
    if atlas.width < need * CELL:
        grown = Image.new("RGBA", (need * CELL, CELL), (0, 0, 0, 0))
        grown.paste(atlas, (0, 0))
        atlas = grown
    missing = []
    for i, (item, art, shape, colour) in enumerate(ICONS):
        x = (FIRST_SLOT + i) * CELL
        atlas.paste(Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0)), (x, 0))
        path = os.path.join(ITEMS, art + ".png") if art else ""
        if art and os.path.exists(path):
            pic = Image.open(path).convert("RGBA")
            if pic.size != (CELL, CELL):
                pic = pic.resize((CELL, CELL), Image.NEAREST)
        else:
            pic = placeholder(shape, colour)
            missing.append(item)
        atlas.paste(pic, (x, 0), pic)
    atlas.save(ATLAS)
    print("icons %d-%d written; placeholders for: %s" % (FIRST_SLOT, need - 1, ", ".join(missing)))


if __name__ == "__main__":
    main()
