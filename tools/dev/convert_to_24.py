"""One-off move of the game's art onto the 24-pixels-a-tile grid (18 Nov 2026).

Art drawn at 32 a tile (most of it) is shrunk with tools/dev/to24.py; the few placeholders the build still
draws at 16 a tile are enlarged by 1.5 (nearest). Sprite sheets are converted one frame at a time, so frames
stay the same size. UI art and portraits are not touched (the interface keeps its own scale). Baked floor
and wall pictures are not touched either: tools/build.py bakes them again at 24 a tile.

    python3 tools/dev/convert_to_24.py .            # converts in place and prints what it did

Afterwards every converted file is listed in art/hand_edited.txt, so the build's placeholder generator
leaves it alone. Run once; running again would shrink the art a second time.
"""
import glob, os, re, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import to24

root = sys.argv[1]
A = lambda *p: os.path.join(root, "art", *p)
done = []


def grid(img, cols, rows, fn):
    w, h = img.size
    fw, fh = w // cols, h // rows
    cells = [[fn(img.crop((c * fw, r * fh, (c + 1) * fw, (r + 1) * fh))) for c in range(cols)] for r in range(rows)]
    nw, nh = cells[0][0].size
    out = Image.new("RGBA", (nw * cols, nh * rows))
    for r in range(rows):
        for c in range(cols):
            out.paste(cells[r][c], (c * nw, r * nh))
    return out


def down(cell):
    return to24.shrink(cell)


def up(cell):
    w, h = cell.size
    return cell.convert("RGBA").resize((w * 3 // 2, h * 3 // 2), Image.NEAREST)


def convert(path, cols=1, rows=1, fn=down, tile=False):
    if not os.path.exists(path):
        return
    img = Image.open(path).convert("RGBA")
    out = to24.shrink_tileable(img) if tile else grid(img, cols, rows, fn)
    out.save(path)
    done.append((os.path.relpath(path, A()), img.size, out.size))


# Characters and the player (walk sheets 4 x 3; action sheets 4 x rows of 48x64; layer sheets 4 x rows of 32x64)
for f in sorted(glob.glob(A("npc_*.png"))):
    w, h = Image.open(f).size
    convert(f, 4, h // 64)
convert(A("player.png"), 4, 3)
for f in sorted(glob.glob(A("player", "*.png")) + glob.glob(A("player", "body2", "*.png"))):
    w, h = Image.open(f).size
    convert(f, w // 32, h // 64)
# Creatures, effects, ores, items, weapons, the wreck, the old tile sheet
for n in ("enemy_bug", "enemy_lizard", "iron_ore", "copper_ore", "slash"):
    convert(A(n + ".png"), 2, 1)
for n in ("enemy_harbinger", "enemy_spore_crawler", "enemy_vent_crab", "carbon", "gold_ore", "quartz", "stone", "titanium_ore"):
    convert(A(n + ".png"), 2, 1, fn=up)                  # build placeholders made at 16 a tile
for f in sorted(glob.glob(A("fx_*.png"))):
    convert(f, 4, 1)
convert(A("items.png"), Image.open(A("items.png")).size[0] // 32, 1)
convert(A("weapon_spear.png")); convert(A("weapon_sword.png"))
convert(A("wreck.png"), 4, 1)
convert(A("tiles.png"), Image.open(A("tiles.png")).size[0] // 32, 2)
# The station: props, machines, doors, floors and walls (not the baked level pictures, made by the build)
bf = open(os.path.join(root, "tools", "bake_floor.py")).read()
textures = set(re.findall(r'"([a-z][a-z0-9_]*)"', bf))
BAKED = re.compile(r'^(floor|walls|window)_')
still_w = {}
for f in sorted(glob.glob(A("lunar", "*.png"))):
    n = os.path.basename(f)[:-4]
    if BAKED.match(n) and not (n in textures):
        continue
    if n in ("paving_painted", "garden_stone"):
        continue                                          # sampled by the main level's 16-grid floor pattern
    w, h = Image.open(f).size
    still_w[n] = w
    if (n in textures or re.match(r'^(material_\d|.*_roof|.*_wall)$', n)) and w == h == 64:
        convert(f, tile=True)
    elif n == "player_ship":
        convert(f, 4, 1)
    else:
        convert(f)
for f in sorted(glob.glob(A("lunar", "anim", "*.png"))):
    n = os.path.basename(f)[:-4]
    w, _ = Image.open(f).size
    convert(f, max(1, round(w / still_w.get(n, w))), 1)
for f in sorted(glob.glob(A("mess_hall", "*.png"))):
    convert(f)
# S.A.R.A.'s hologram clips: 24 frames side by side
for f in sorted(glob.glob(os.path.join(root, "sara", "animations", "*.png"))):
    convert(f, 24, 1)

hand = A("hand_edited.txt")
have = {l.strip() for l in open(hand) if l.strip() and not l.startswith("#")}
new = [d[0].replace(os.sep, "/") for d in done if d[0].replace(os.sep, "/") not in have and os.path.basename(d[0]) not in have]
with open(hand, "a") as fh:
    fh.write("\n# Moved onto the 24-pixel grid by tools/dev/convert_to_24.py (18 Nov 2026): keep, don't regenerate.\n")
    for n in new:
        if not n.startswith(".."):
            fh.write(n + "\n")
print("converted %d files; %d newly protected" % (len(done), len(new)))
for d in done[:8]:
    print("  ", d)
