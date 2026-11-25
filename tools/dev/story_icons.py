"""Item icons for the main story's rewards (24 Nov 2026): the Sovereign of Hydro-Flora's sprinkler and fruit trees
(scripts/item_data.gd icons 147-153), and Tidelight's forage (154-159). The artist's own icons from art/items/, copied into art/items.png.

Run from the repo root:  python3 -I tools/dev/story_icons.py   (safe to repeat: it rewrites the same slots)
"""
import os
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ATLAS = os.path.join(ROOT, "art", "items.png")
ITEMS = os.path.join(ROOT, "art", "items")
FIRST_SLOT = 147
CELL = 24

# In icon order: [item id, art/items name]
ICONS = [
    ["sprinkler", "sprinkler_basic"],
    ["moon_peach_sapling", "moon_peach_tree_sapling"],
    ["star_apple_sapling", "star_apple_tree_sapling"],
    ["sun_fig_sapling", "sun_fig_tree_sapling"],
    ["moon_peach", "moon_peach"],
    ["star_apple", "star_apple"],
    ["sun_fig", "sun_fig"],
    # Tidelight's forage (tools/tidelight.py), icons 154-159
    ["sun_lily", "sun_lily"],
    ["bio_plankton", "bio_plankton"],
    ["ember_aster", "ember_aster"],
    ["resin", "resin"],
    ["hardwood", "hardwood"],
    ["glow_moss", "glow_moss"],
]


def main():
    atlas = Image.open(ATLAS).convert("RGBA")
    need = FIRST_SLOT + len(ICONS)
    if atlas.width < need * CELL:
        grown = Image.new("RGBA", (need * CELL, CELL), (0, 0, 0, 0))
        grown.paste(atlas, (0, 0))
        atlas = grown
    for i, (item, art) in enumerate(ICONS):
        x = (FIRST_SLOT + i) * CELL
        pic = Image.open(os.path.join(ITEMS, art + ".png")).convert("RGBA")
        atlas.paste(Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0)), (x, 0))
        atlas.paste(pic, (x, 0), pic)
    atlas.save(ATLAS)
    print("icons %d-%d written" % (FIRST_SLOT, need - 1))


if __name__ == "__main__":
    main()
