"""Fit each ship's gun mounts so the gun sits on the hull plating, back from where it was, clear of the dark frame
round the rooms (Zachary, 22 Nov: "little further back so its attached to the ship just not the interior outline").
Prints the new mounts per ship and writes a preview sheet. Usage: python3 -I tools/dev/ship_art/fit_mounts.py . <preview.png> [--write]   (--write updates ship_data.gd and the INSIDES)"""
import sys, re
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as nd
R = Path(sys.argv[1]); prev = sys.argv[2]; write = "--write" in sys.argv
src = (R / "scripts/ship_data.gd").read_text()
gun_img = Image.open(R / "art/ships/weapons/burst_laser.png").crop((3 * 64, 0, 4 * 64, 24))
gun = np.array(gun_img)[:, :, 3] > 0
MOUNT = np.array([6, 12])
# each ship block: find "art": "res://art/ships/<id>/hull.png" ... "mounts": [...]
blocks = []
for m in re.finditer(r'"mounts": \[([^\]]*)\]', src):
    start = src.rfind('"art": "res://art/ships/', 0, m.start())
    art = re.match(r'"art": "res://art/ships/([\w]+)/hull\.png"', src[start:]).group(1)
    pts = [tuple(float(v) for v in p) for p in re.findall(r'Vector2\(([\d.]+), ([\d.]+)\)', m.group(1))]
    blocks.append((art, m.span(1), pts))
sheet = []
new_src = src
for art, span, pts in blocks:
    d = R / "art/ships" / art
    hull = np.array(Image.open(d / "hull.png").convert("RGBA"))[:, :, 3] > 0
    frame = np.array(Image.open(d / "frame.png").convert("RGBA"))[:, :, 3] > 0
    inside = np.array(Image.open(d / "interior.png").convert("RGBA")).astype(int)
    hull_px = np.array(Image.open(d / "hull.png").convert("RGBA")).astype(int)
    cut = (np.abs(inside - hull_px).sum(axis=2) > 0) & (inside[:, :, 3] > 0)        # the cut-away: rooms and frame
    nogo = nd.binary_dilation(nd.binary_fill_holes(nd.binary_closing(cut, iterations=3)), iterations=1)
    H, W = hull.shape
    cy = H / 2.0
    def spot(x, side, need=0.6, min_dy=0):
        """The smallest step out from the hull's middle at which a gun with its mount at art x fits on this side:
        clear of the rooms and their frame, its back half on the hull. None if it doesn't fit there."""
        for dy in range(min_dy, int(H // 2)):
            for y in ([int(cy) - dy] if side < 0 else [int(cy) + dy]):
                o = (x - MOUNT[0], y - MOUNT[1])
                x0, y0 = int(o[0]), int(o[1])
                if x0 < 0 or y0 < 0 or y0 + 24 > H:
                    continue
                w = min(64, W - x0)
                if w <= 30:
                    continue
                g = gun[:, :w]
                if (g & nogo[y0:y0 + 24, x0:x0 + w]).any():
                    continue
                rear = g[:, :30]
                if (rear & hull[y0:y0 + 24, x0:x0 + 30]).sum() < need * rear.sum():
                    continue
                return y
        return None
    out = [None] * len(pts)
    for side in (-1, 1):
        idx = [n for n, (mx, my) in enumerate(pts) if (my * 2 - cy) * side > 12]
        idx.sort(key=lambda n: -pts[n][0])               # front-most first
        cands = []
        for x in range(W - 20, 10, -1):
            y = spot(x, side)
            if y is not None:
                cands.append((x, y))
        last = None
        for n in idx:
            pick = None
            for (x, y) in cands:
                if x > pts[n][0] * 2 + 4:                # never further forward than it was
                    continue
                if last is not None and x > last - 66:   # keep guns on one side apart
                    continue
                pick = (x, y)
                break
            if pick is None:
                out[n] = None
                continue
            out[n] = (pick[0] / 2.0, pick[1] / 2.0, True)
            last = pick[0]
        # anything left: anywhere on this side its back third is on the hull, clear of the guns already placed
        placed = [o[0] * 2 for m2, o in enumerate(out) if m2 in idx and o is not None]
        for n in idx:
            if out[n] is not None:
                continue
            got = None
            for x in range(W - 20, 10, -1):
                if any(abs(x - px) < 66 for px in placed):
                    continue
                y = spot(x, side, 0.3, 14)
                if y is not None:
                    got = (x, y)
                    break
            if got is None:
                out[n] = (pts[n][0], pts[n][1], False)
            else:
                out[n] = (got[0] / 2.0, got[1] / 2.0, True)
                placed.append(got[0])
    for n, v in enumerate(out):
        if v is None:
            out[n] = (pts[n][0], pts[n][1], True)        # a gun on the middle line (a nose gun) stays
    print(art, [(round(a, 1), round(b, 1), ok) for a, b, ok in out])
    text = ", ".join("Vector2(%s, %s)" % (("%g" % a), ("%g" % b)) for a, b, _ in out)
    new_src = new_src.replace(src[span[0]:span[1]], text, 1) if write else new_src
    if write:
        old_py = "[" + ", ".join("(%g, %g)" % (a, b) for a, b in pts) + "]"
        new_py = "[" + ", ".join("(%g, %g)" % (a, b) for a, b, _ in out) + "]"
        for f in ("fleet2x.py", "bases2x.py", "story2x.py"):
            q = R / "tools/dev/ship_art" / f
            t = q.read_text()
            if t.count(old_py) == 1:
                q.write_text(t.replace(old_py, new_py))
                print("  also", f)
    # preview
    im = Image.open(d / "interior.png").convert("RGBA")
    for a, b, ok in out:
        im.alpha_composite(gun_img, (int(a * 2 - 6), int(round(b * 2 - 12))))
    im.alpha_composite(Image.open(d / "frame.png").convert("RGBA"))
    sheet.append(im)
if write:
    (R / "scripts/ship_data.gd").write_text(new_src)
Wt = max(i.width for i in sheet) + 80
cols = 3
rows = (len(sheet) + cols - 1) // cols
Ht = max(i.height for i in sheet) + 20
pg = Image.new("RGBA", (Wt * cols, Ht * rows), (12, 14, 24, 255))
for n, im in enumerate(sheet):
    pg.alpha_composite(im, ((n % cols) * Wt + 60, (n // cols) * Ht + 10))
pg.save(prev)
