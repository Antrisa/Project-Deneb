"""Item icons for the hotel's walls, doors and furniture (scripts/item_data.gd icons 123-135, 24 Nov 2026).

Each icon is the piece's own prop art (art/lunar/<art>.png, as scripts/hotel.gd FURNITURE draws it) shrunk to
fit a 24-pixel slot of art/items.png. Run from the repo root:  python3 -I tools/dev/hotel_icons.py
Safe to run again: it rewrites the same slots.
"""
import os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ATLAS = os.path.join(ROOT, "art", "items.png")
CELL = 24
FIRST = 123
ART = ["hotel_wall_piece", "inner_door_s_frame", "bed", "bed_double_steel", "armchair", "dresser_steel", "wardrobe",
       "desk_steel", "bedside_lamp", "bookshelf_steel", "potted_plant", "fern", "rug_berry"]


def icon(name):
    pic = Image.open(os.path.join(ROOT, "art", "lunar", name + ".png")).convert("RGBA")
    box = pic.getbbox()
    if box:
        pic = pic.crop(box)
    scale = min(1.0, (CELL - 2) / max(pic.width, pic.height))
    if scale < 1.0:
        pic = pic.resize((max(1, round(pic.width * scale)), max(1, round(pic.height * scale))), Image.LANCZOS)
    out = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    out.alpha_composite(pic, ((CELL - pic.width) // 2, (CELL - pic.height) // 2))
    return out


def main():
    atlas = Image.open(ATLAS).convert("RGBA")
    need = (FIRST + len(ART)) * CELL
    if atlas.width < need:
        grown = Image.new("RGBA", (need, CELL), (0, 0, 0, 0))
        grown.paste(atlas, (0, 0))
        atlas = grown
    for i, name in enumerate(ART):
        x = (FIRST + i) * CELL
        atlas.paste(Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0)), (x, 0))
        atlas.alpha_composite(icon(name), (x, 0))
    atlas.save(ATLAS)
    print("hotel icons %d-%d written" % (FIRST, FIRST + len(ART) - 1))


if __name__ == "__main__":
    main()
