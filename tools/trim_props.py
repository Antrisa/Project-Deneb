"""Trims the empty margins off the promenade's prop pictures (art/lunar), so each one stands exactly on
its bottom edge and is centred on its tiles. Width and height are kept even, because the game draws
these at half size. Lossless: only fully transparent rows and columns are removed. Run it again after
adding or replacing a prop picture:   python3 tools/trim_props.py ."""
import os, sys
from PIL import Image
SKIP_PREFIX = ("material_", "paving_", "garden_stone", "fountain", "home", "major", "shop")
root = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "art", "lunar")
for name in sorted(os.listdir(root)):
    if not name.endswith(".png") or name.startswith(SKIP_PREFIX):
        continue
    path = os.path.join(root, name)
    im = Image.open(path).convert("RGBA")
    box = im.split()[3].getbbox()
    if box is None:
        continue
    cut = im.crop(box)
    w, h = cut.width + cut.width % 2, cut.height + cut.height % 2
    if (w, h) == im.size and box[:2] == (0, 0):
        continue
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(cut, (0, h - cut.height))          # bottom edge flush; any spare column goes on the right
    out.save(path)
    print("%-22s %3dx%-3d -> %3dx%-3d" % (name, im.width, im.height, w, h))
