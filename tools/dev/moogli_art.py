"""Stand-in art for Tobbin, Merrow & Nub's heart events (24 Nov 2026), until the artist draws them:

  art/lunar/heirloom_chair.png   Tobbin's 8: the first real-wood chair (chair_s re-coloured: pale birch, a blue seat)
  art/lunar/nub_drawing.png      Nub's 8: his drawing in a frame Tobbin made from a broken plastic chair, on an easel
  art/items/real_wood.png        Tobbin's planks (his shop, after his 4)
  art/items.png slots 136-138    real_wood, heirloom_chair, nub_drawing (scripts/item_data.gd)

Run from the repo root:  python3 -I tools/dev/moogli_art.py
Safe to run again: it rewrites the same files and slots. The Art Fix List has a row for each.
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LUNAR = os.path.join(ROOT, "art", "lunar")
ITEMS = os.path.join(ROOT, "art", "items")
ATLAS = os.path.join(ROOT, "art", "items.png")
CELL = 24
SLOTS = {"real_wood": 136, "heirloom_chair": 137, "nub_drawing": 138}
OUTLINE = (91, 51, 45, 255)


def heirloom_chair():
    """chair_s with its wood turned pale birch and its red seat a soft bluebark blue."""
    src = Image.open(os.path.join(LUNAR, "chair_s.png")).convert("RGBA")
    out = src.copy()
    px = out.load()
    birch = [(40, (88, 58, 42)), (100, (200, 152, 98)), (195, (246, 224, 172))]

    def ramp(lum):
        for (l0, c0), (l1, c1) in zip(birch, birch[1:]):
            if lum <= l1:
                t = max(0.0, (lum - l0) / (l1 - l0))
                return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))
        return birch[-1][1]

    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            lum = 0.3 * r + 0.59 * g + 0.11 * b
            if r > 150 and b >= g - 3:                          # the red seat
                k = min(1.3, lum / 85.0)
                px[x, y] = (int(64 * k), int(128 * k), int(178 * k), a)
            elif b > g + 15:                                    # the seat's shadow
                px[x, y] = (36, 62, 104, a) if lum > 40 else (26, 40, 72, a)
            else:                                               # the wood, pale like birch
                px[x, y] = ramp(lum) + (a,)
    return out


def nub_drawing():
    """A child's drawing (the Landing under the dome) in a grey plastic frame, on a small wooden easel. 24x36."""
    im = Image.new("RGBA", (24, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wood, wood_dk = (150, 96, 58, 255), (104, 64, 40, 255)
    # easel legs and cross-bar
    d.line([(6, 20), (3, 35)], fill=wood_dk)
    d.line([(17, 20), (20, 35)], fill=wood_dk)
    d.line([(12, 20), (12, 34)], fill=wood)
    d.line([(5, 27), (18, 27)], fill=wood)
    # the frame: grey-white plastic (the chair that broke)
    d.rectangle([1, 2, 22, 21], fill=(206, 210, 214, 255), outline=(120, 124, 132, 255))
    d.rectangle([3, 4, 20, 19], fill=(250, 248, 238, 255))
    # crayon: the dome, a tree, a ship with a smile, a tall person and three small round Moogli
    d.arc([3, 6, 20, 26], 180, 360, fill=(110, 170, 220, 255))
    d.line([(4, 18), (19, 18)], fill=(120, 190, 90, 255))
    d.rectangle([6, 13, 6, 17], fill=(140, 90, 50, 255))
    d.ellipse([4, 9, 8, 13], fill=(80, 170, 80, 255))
    d.polygon([(13, 15), (19, 15), (17, 12), (14, 12)], fill=(230, 80, 70, 255))
    im.putpixel((15, 13), (60, 120, 200, 255))
    d.line([(10, 11), (10, 17)], fill=(60, 60, 70, 255))
    im.putpixel((10, 10), (60, 60, 70, 255))
    for x, c in ((8, (220, 160, 70)), (12, (150, 190, 140)), (17, (220, 200, 90))):
        im.putpixel((x, 17), c + (255,))
        im.putpixel((x, 16), c + (255,))
    return im


def real_wood():
    """Three pale planks with grain, stacked. 24x24."""
    im = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (y, shade) in enumerate(((5, 0), (10, 14), (15, 6))):
        x0 = 2 + (i % 2) * 2
        body = (222 - shade, 184 - shade, 130 - shade, 255)
        d.rectangle([x0, y, x0 + 18, y + 4], fill=body, outline=OUTLINE)
        d.line([(x0 + 3, y + 2), (x0 + 9, y + 2)], fill=(176, 132, 84, 255))
        d.line([(x0 + 11, y + 1), (x0 + 15, y + 1)], fill=(190, 146, 96, 255))
        im.putpixel((x0 + 13, y + 3), (160, 116, 70, 255))
    return im


def shrink(pic):
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
    chair = heirloom_chair()
    chair.save(os.path.join(LUNAR, "heirloom_chair.png"))
    drawing = nub_drawing()
    drawing.save(os.path.join(LUNAR, "nub_drawing.png"))
    wood = real_wood()
    wood.save(os.path.join(ITEMS, "real_wood.png"))
    icons = {"real_wood": wood, "heirloom_chair": shrink(chair), "nub_drawing": shrink(drawing)}
    for name in ("heirloom_chair", "nub_drawing"):
        icons[name].save(os.path.join(ITEMS, name + ".png"))
    atlas = Image.open(ATLAS).convert("RGBA")
    need = (max(SLOTS.values()) + 1) * CELL
    if atlas.width < need:
        grown = Image.new("RGBA", (need, CELL), (0, 0, 0, 0))
        grown.paste(atlas, (0, 0))
        atlas = grown
    for name, slot in SLOTS.items():
        x = slot * CELL
        atlas.paste(Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0)), (x, 0))
        atlas.alpha_composite(icons[name], (x, 0))
    atlas.save(ATLAS)
    print("moogli art written; icons %s" % ", ".join("%s %d" % kv for kv in SLOTS.items()))


if __name__ == "__main__":
    main()
