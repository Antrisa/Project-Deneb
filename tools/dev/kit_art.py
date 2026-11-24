"""Stand-in art for Kit's 8 (24 Nov 2026), until the artist draws it:

  art/lunar/deputy_badge.png     Kit's deputy badge on its little display stand (24x36, a 1x1 decor piece)
  art/items/deputy_badge.png     its icon, and art/items.png slot 139 (scripts/item_data.gd)

Run from the repo root:  python3 -I tools/dev/kit_art.py
Safe to run again: it rewrites the same files and slot. The Art Fix List has a row for it.
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CELL = 24
SLOT = 139
OUTLINE = (91, 51, 45, 255)


def star(d, cx, cy, r_out, r_in, fill, outline):
    import math
    pts = []
    for k in range(10):
        r = r_out if k % 2 == 0 else r_in
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline)


def badge(size):
    """A tin star painted gold, with a crooked dark band across it (DEPUTY)."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2 - 0.5
    star(d, c, c + 0.5, size * 0.47, size * 0.22, (236, 196, 72, 255), OUTLINE)
    star(d, c - 1, c - 0.5, size * 0.28, size * 0.13, (252, 228, 132, 255), None)
    d.line([(c - size * 0.28, c + 2), (c + size * 0.28, c + 1)], fill=(120, 72, 40, 255), width=2)
    return im


def stand():
    """The badge on a little wooden display stand, for setting down at home. 24x36."""
    im = Image.new("RGBA", (24, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wood, wood_dk = (150, 96, 58, 255), (104, 64, 40, 255)
    d.rectangle([4, 31, 19, 34], fill=wood, outline=wood_dk)
    d.line([(11, 18), (11, 31)], fill=wood_dk, width=2)
    d.rectangle([3, 4, 20, 21], fill=(64, 48, 72, 255), outline=(40, 28, 44, 255))   # a velvet card behind it
    im.alpha_composite(badge(16), (4, 5))
    return im


def main():
    prop = stand()
    prop.save(os.path.join(ROOT, "art", "lunar", "deputy_badge.png"))
    icon = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    icon.alpha_composite(badge(22), (1, 1))
    icon.save(os.path.join(ROOT, "art", "items", "deputy_badge.png"))
    atlas_path = os.path.join(ROOT, "art", "items.png")
    atlas = Image.open(atlas_path).convert("RGBA")
    need = (SLOT + 1) * CELL
    if atlas.width < need:
        grown = Image.new("RGBA", (need, CELL), (0, 0, 0, 0))
        grown.paste(atlas, (0, 0))
        atlas = grown
    atlas.paste(Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0)), (SLOT * CELL, 0))
    atlas.alpha_composite(icon, (SLOT * CELL, 0))
    atlas.save(atlas_path)
    print("kit art written; icon slot %d" % SLOT)


if __name__ == "__main__":
    main()
