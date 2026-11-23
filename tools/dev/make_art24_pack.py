"""Build the art pack for redrawing the environment on the 24-pixel grid.

    python3 tools/dev/make_art24_pack.py . <out_dir>

Writes <out_dir>/ASSET_LIST.csv, references/ (the current art) and starters/ (the same art shrunk to the new
size by tools/dev/to24.py, as a size guide and a starting point). README.md is written by hand.
"""
import csv, glob, os, re, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import to24

root, out = sys.argv[1], sys.argv[2]
md = open(os.path.join(root, "scripts/map_data.gd")).read()
bf = open(os.path.join(root, "tools/bake_floor.py")).read()

titles = {}
for name, title in re.findall(r'\["([a-z0-9_]+)", -?[\d.]+, -?[\d.]+, \d+, \d+, "([^"]*)"', md):
    titles.setdefault(name, title)
foot = {}
for name, w, h in re.findall(r'\["([a-z0-9_]+)", -?[\d.]+, -?[\d.]+, (\d+), (\d+), "', md):
    foot.setdefault(name, (int(w), int(h)))
textures = set(re.findall(r'"([a-z][a-z0-9_]*)"', bf))

BAKED = re.compile(r'^(floor|walls)_(main|top|museum|sanctum|lounge|eng|bay|west|agri|hotel|east|home\d+|mine|tunnels|ncave|cav\w*)$')
rows = []


def add(src, new_rel, category, priority, what, frames=1, tile=False):
    im = Image.open(src)
    w, h = im.size
    nw, nh = to24.new_size(w, h, frames)
    ref = os.path.join("references", new_rel)
    st = os.path.join("starters", new_rel)
    for p in (ref, st):
        os.makedirs(os.path.join(out, os.path.dirname(p)), exist_ok=True)
    im.save(os.path.join(out, ref))
    (to24.shrink_tileable(im) if tile else to24.shrink(im, frames)).save(os.path.join(out, st))
    rows.append([priority, category, new_rel, f"{w}x{h}", f"{nw}x{nh}", frames if frames > 1 else "", what])


still = {}
for f in sorted(glob.glob(os.path.join(root, "art/lunar/*.png"))):
    n = os.path.basename(f)[:-4]
    if BAKED.match(n):
        continue                                    # made by the build from the textures; never drawn by hand
    w, h = Image.open(f).size
    still[n] = w
    if re.match(r'^(material_\d|.*_roof|.*_wall)$', n):
        add(f, f"art/lunar/{n}.png", "wall & roof texture", "A", "Seamless; 2x2 tiles. Roof = top of walls seen from above; wall = the front face.", tile=True)
    elif n.startswith("window_"):
        add(f, f"art/lunar/{n}.png", "window strip", "B", "A long window band set into a wall; the view outside through the glass.")
    elif n in textures and w == h == 64:
        add(f, f"art/lunar/{n}.png", "floor texture", "A", "Seamless floor; 2x2 tiles. Low contrast so furniture stands out.", tile=True)
    elif n in ("player_ship", "tarp_fighter", "leviathan"):
        add(f, f"art/lunar/{n}.png", "ship / large", "B", "Large sheet: keep the frame layout, every frame shrunk the same.", frames=4 if n == "player_ship" else 1)
    else:
        fp = foot.get(n)
        what = titles.get(n, n.replace("_", " "))
        if fp:
            what += f" (stands on {fp[0]}x{fp[1]} tiles)"
        add(f, f"art/lunar/{n}.png", "furniture & prop" if fp else "prop / door / roof piece", "A" if fp else "B", what)

for f in sorted(glob.glob(os.path.join(root, "art/lunar/anim/*.png"))):
    n = os.path.basename(f)[:-4]
    w, _ = Image.open(f).size
    frames = max(1, round(w / still.get(n, w)))
    add(f, f"art/lunar/anim/{n}.png", "animation strip", "A", f"Looping machinery, {frames} frames side by side, 8 fps. Same size frames as the still.", frames=frames)

for f in sorted(glob.glob(os.path.join(root, "art/mess_hall/*.png"))):
    n = os.path.basename(f)[:-4]
    add(f, f"art/mess_hall/{n}.png", "mess hall", "B", f"Mess hall {n.replace('_', ' ')}")

for n in ("stone", "iron_ore", "copper_ore", "carbon", "quartz", "gold_ore", "titanium_ore"):
    f = os.path.join(root, f"art/{n}.png")
    if os.path.exists(f):
        add(f, f"art/{n}.png", "ore & rock node", "A", "2 frames side by side: whole, then cracked (half mined).", frames=2)

f = os.path.join(root, "art/items.png")
if os.path.exists(f):
    im = Image.open(f)
    n_icons = im.size[0] // 32
    add(f, "art/items.png", "item icons", "B", f"{n_icons} icons in a row, each 32x32 now and 24x24 on the new grid.", frames=n_icons)

order = {"A": 0, "B": 1}
rows.sort(key=lambda r: (order[r[0]], r[1], r[2]))
with open(os.path.join(out, "ASSET_LIST.csv"), "w", newline="") as fh:
    cw = csv.writer(fh)
    cw.writerow(["priority", "category", "file (keep this exact path and name)", "old size", "NEW SIZE", "frames", "what it is"])
    cw.writerows(rows)
print(len(rows), "assets")
from collections import Counter
print(Counter(r[1] for r in rows))
