"""Reference sheets of the game's own art, for whoever draws Everlight Falls (ChatGPT or an artist), 28 Nov 2026.
Zachary: ChatGPT was "having a hard time getting the artstyle down", so the handoff doc carries pictures of the real
art at a readable zoom, labelled with their true sizes. Writes PNGs to the folder given (not into the game).
Run from the repo root: python3 -I tools/dev/everlight_refs.py OUT_DIR
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG = (232, 217, 189, 255)          # station cream e8d9bd
INK = (74, 42, 40, 255)            # 4a2a28
QUIET = (110, 66, 56, 255)         # 6e4238
sys.path.insert(0, os.path.dirname(__file__))
from prologue_art import PAL       # noqa: E402  the master palette


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def art(path):
    return Image.open(os.path.join(ROOT, path)).convert("RGBA")


def zoom(im, k):
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def titled(body, title, note, width=None):
    w = max(width or 0, body.width + 48)
    out = Image.new("RGBA", (w, body.height + 110), BG)
    d = ImageDraw.Draw(out)
    d.text((24, 18), title, font=font(26, True), fill=INK)
    d.text((24, 56), note, font=font(17), fill=QUIET)
    out.alpha_composite(body, (24, 92))
    return out


def shelf(items, k, max_w, label_size=15, tiles=True):
    """Pictures in rows, zoomed k times, each with its name and true size under it."""
    rows, row, x = [], [], 0
    for name, im in items:
        cw = max(im.width * k, 170) + 28
        if row and x + cw > max_w:
            rows.append(row); row, x = [], 0
        row.append((name, im, cw)); x += cw
    rows.append(row)
    heights = [max(im.height * k for _, im, _ in r) + 56 for r in rows]
    out = Image.new("RGBA", (max_w, sum(heights)), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    y = 0
    for r, h in zip(rows, heights):
        x = 0
        for name, im, cw in r:
            big = zoom(im, k)
            out.alpha_composite(big, (x, y + h - 56 - big.height))
            show_tiles = tiles
            tiles = "%g x %g tiles" % (round(im.width / 24 * 2) / 2, round(im.height / 24 * 2) / 2)
            d.text((x, y + h - 50), name, font=font(label_size, True), fill=INK)
            size = "%d x %d px" % (im.width, im.height) + (" (%s)" % tiles if show_tiles else "")
            d.text((x, y + h - 30), size, font=font(label_size - 2), fill=QUIET)
            x += cw
        y += h
    return out


def props(out):
    names = ["park_tree", "park_tree_autumn", "fruit_tree", "boulder", "flowers", "planter_long", "home_chest",
             "bench_n", "lamp_post", "barrel_stack", "cargo", "market_counter", "brazier", "beacon_mast",
             "crystal_cluster", "glow_fungus"]
    body = shelf([(n, art("art/lunar/%s.png" % n)) for n in names], 4, 1500)
    titled(body, "Echo Landing props: match this look",
           "Shown 4x. Warm dark-brown outline, big flat areas, 2-3 shades per material, light from the top left, no ground shadows.",
           1548).save(os.path.join(out, "everlight_ref_1_props.png"))


def characters(out):
    sheet = art("art/npc_freya.png")
    freya = art("art/portrait_freya.png").crop((0, 0, 128, 128))
    jasper = art("art/portrait_jasper.png").crop((0, 0, 128, 128))
    body = shelf([("Freya: walk sheet", sheet)], 4, 520, tiles=False)
    faces = shelf([("Freya: portrait", freya), ("Jasper: the model portrait", jasper)], 2, 620, tiles=False)
    canvas = Image.new("RGBA", (body.width + faces.width + 40, max(body.height, faces.height)), (0, 0, 0, 0))
    canvas.alpha_composite(body, (0, 0)); canvas.alpha_composite(faces, (body.width + 40, 0))
    titled(canvas, "Characters: 24 x 48 sprites, 128 x 128 portraits",
           "Walk sheet shown 4x: columns face down, up, left, right; rows are standing, then 4 walk frames. Portraits shown 2x."
           ).save(os.path.join(out, "everlight_ref_2_characters.png"))


def scale(out):
    """A patch of plain grass, 14 x 8 tiles, with a person and props at their true sizes on a 24-px grid."""
    tw, th = 14, 8
    green = tuple(int(PAL["leaf"][2][i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    path = tuple(int(PAL["soil"][3][i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    g = Image.new("RGBA", (tw * 24, th * 24), green)
    d = ImageDraw.Draw(g)
    d.rectangle((0, 6 * 24, tw * 24, 7 * 24 - 1), fill=path)
    grid = Image.new("RGBA", g.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for x in range(0, tw * 24, 24):
        gd.line((x, 0, x, th * 24), fill=(255, 243, 214, 60))
    for y in range(0, th * 24, 24):
        gd.line((0, y, tw * 24, y), fill=(255, 243, 214, 60))
    g.alpha_composite(grid)
    freya = art("art/npc_freya.png").crop((0, 0, 24, 48))

    def stand(im, tx, ty_bottom):      # centred on its tile column, standing on the bottom of tile row ty_bottom
        g.alpha_composite(im, (int(tx * 24 + 12 - im.width / 2), ty_bottom * 24 - im.height))
    stand(art("art/lunar/park_tree.png"), 1.5, 5)
    stand(art("art/lunar/lamp_post.png"), 4, 6)
    stand(freya, 5.5, 6)
    stand(art("art/lunar/bench_n.png"), 7.5, 6)
    stand(art("art/lunar/home_chest.png"), 9, 6)
    stand(art("art/lunar/market_counter.png"), 11.5, 6)
    stand(art("art/lunar/boulder.png"), 12.5, 8)
    stand(art("art/lunar/flowers.png"), 9.5, 4)
    big = zoom(g, 4)
    titled(big, "Scale and view: 24-pixel tiles, seen top-down at three-quarters",
           "Shown 4x with the tile grid. A person is 1 x 2 tiles; a tree about 2 x 3.5; a stall 3 x 2. Every object shows its front and its top."
           ).save(os.path.join(out, "everlight_ref_3_scale.png"))


def palette(out):
    sw, gap = 64, 8
    names = list(PAL.keys())
    body = Image.new("RGBA", (5 * (sw + gap) + 170, len(names) * (sw // 2 + 30)), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    for r, name in enumerate(names):
        y = r * (sw // 2 + 30)
        d.text((0, y + 6), name, font=font(16, True), fill=INK)
        for i, h in enumerate(PAL[name]):
            x = 150 + i * (sw + gap)
            col = tuple(int(h[j:j + 2], 16) for j in (0, 2, 4))
            d.rectangle((x, y, x + sw, y + sw // 2), fill=col, outline=(110, 66, 56), width=1)
            d.text((x, y + sw // 2 + 4), "#" + h, font=font(12), fill=QUIET)
    titled(body, "The master palette: 68 colours, 14 ramps",
           "Use only these. Each ramp runs dark to light; shadows lean purple, highlights lean yellow.", 960).save(
        os.path.join(out, "everlight_ref_4_palette.png"))


def first_pass(out, views):
    a, b = (Image.open(v).convert("RGBA") for v in views)
    k = 0.75
    a = a.resize((int(a.width * k), int(a.height * k)), Image.NEAREST)
    b = b.resize((int(b.width * k), int(b.height * k)), Image.NEAREST)
    body = Image.new("RGBA", (a.width + b.width + 24, a.height), (0, 0, 0, 0))
    body.alpha_composite(a, (0, 0)); body.alpha_composite(b, (a.width + 24, 0))
    titled(body, "Today's first pass (placeholder art): layout only, do not copy",
           "Village and forest as the game draws them now. The ground is too speckled and the forest floor too flat; the new art replaces all of it."
           ).save(os.path.join(out, "everlight_ref_5_first_pass.png"))


if __name__ == "__main__":
    dest = sys.argv[1]
    os.makedirs(dest, exist_ok=True)
    props(dest); characters(dest); scale(dest); palette(dest)
    if len(sys.argv) > 3:
        first_pass(dest, sys.argv[2:4])
    print("written to", dest)
