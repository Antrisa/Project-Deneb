"""Ship break-up pieces, FTL-style (Claude, 21 Nov 2026). Zachary: "add animation for ship destruction like FTL it breaks
into pieces, with some ship innards attached, for player destruction an emergency jump back to the station with
some bits breaking off".

For every ship picture art/ships/<id>/hull*.png with its cut-away interior*.png beside it, this writes the pieces
the ship breaks into: gib_1.png ... gib_N.png (gib_rabble_1.png ... for hull_rabble.png), each the same size as the
hull and holding only its piece, so the game can place them where they were and drift them apart. Along every torn
edge the piece shows the ship's insides (deck, walls and consoles from the cut-away), a charred rim, sparks, and
pipes and cables hanging out.

For your fighter it also writes the bits that break off before the emergency jump: chip_1.png ... chip_3.png, and
interior_broken.png (the cut-away with those bits gone and their edges torn).

Run from the repo root:  python3 -I tools/dev/ship_art/gibs2x.py .
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

CHAR = np.array([38, 37, 53, 255], np.uint8)
EMBER = [np.array(c, np.uint8) for c in ((255, 176, 74, 255), (255, 106, 90, 255), (255, 216, 106, 255))]
PIPES = [np.array(c, np.uint8) for c in ((122, 110, 82, 255), (154, 138, 100, 255), (90, 82, 60, 255), (178, 52, 46, 255),
                                         (58, 108, 200, 255))]


def _noise(shape, rng, sigma):
    return ndimage.gaussian_filter(rng.random(shape), sigma)


def _seeds(mask, n, rng):
    """n points spread over the mask (farthest-point sampling)."""
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs, ys], 1).astype(float)
    first = pts[rng.integers(len(pts))]
    chosen = [first]
    d = np.linalg.norm(pts - first, axis=1)
    for _ in range(n - 1):
        nxt = pts[int(np.argmax(d))]
        chosen.append(nxt)
        d = np.minimum(d, np.linalg.norm(pts - nxt, axis=1))
    return np.array(chosen)


def _tear(hull, inside, piece, others, rng, band=7):
    """The piece's pixels from the hull, with the insides showing along edges torn from the other pieces."""
    h, w = piece.shape
    out = np.zeros((h, w, 4), np.uint8)
    out[piece] = hull[piece]
    cut = piece & ndimage.binary_dilation(others, structure=np.ones((3, 3)))
    if not cut.any():
        return out
    dist = ndimage.distance_transform_edt(~cut)
    wobble = _noise((h, w), rng, 2.0) * band * 1.4
    show = piece & (dist < band * 0.6 + wobble) & (inside[:, :, 3] > 0)
    innards = inside.copy()
    innards[:, :, :3] = (innards[:, :, :3] * 0.82).astype(np.uint8)            # in shadow, a little darker
    out[show] = innards[show]
    rim = piece & (dist <= 1.0 + (wobble > band * 0.9))
    out[rim] = CHAR
    scorch = piece & (dist > 1) & (dist < 4 + wobble * 0.3) & ~show
    out[scorch, :3] = (out[scorch, :3] * 0.6).astype(np.uint8)
    # sparks along the tear, and pipes and cables hanging out of it
    ys, xs = np.nonzero(cut)
    if len(xs):
        for _ in range(max(2, len(xs) // 40)):
            i = rng.integers(len(xs))
            out[ys[i], xs[i]] = EMBER[rng.integers(len(EMBER))]
        cy, cx = ndimage.center_of_mass(piece)
        for _ in range(max(2, len(xs) // 60)):
            i = rng.integers(len(xs))
            x0, y0 = xs[i], ys[i]
            v = np.array([x0 - cx, y0 - cy], float)
            v = v / (np.linalg.norm(v) + 1e-6)
            v += rng.normal(0, 0.35, 2)
            v = v / (np.linalg.norm(v) + 1e-6)
            col = PIPES[rng.integers(len(PIPES))]
            thick = rng.integers(1, 3)
            length = rng.integers(4, 11)
            for t in range(length):
                px, py = int(round(x0 + v[0] * t)), int(round(y0 + v[1] * t + 0.04 * t * t))     # sagging a little
                for k in range(thick):
                    qx, qy = px + (k if abs(v[1]) > abs(v[0]) else 0), py + (k if abs(v[0]) >= abs(v[1]) else 0)
                    if 0 <= qx < w and 0 <= qy < h and out[qy, qx, 3] == 0:
                        out[qy, qx] = col
            ex, ey = int(round(x0 + v[0] * length)), int(round(y0 + v[1] * length + 0.04 * length * length))
            if 0 <= ex < w and 0 <= ey < h and rng.random() < 0.5:
                out[ey, ex] = EMBER[0]
    # an outline round anything new that sticks out (pipes)
    solid = out[:, :, 3] > 0
    ring = ndimage.binary_dilation(solid, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]]) & ~solid
    near_piece = ndimage.binary_dilation(piece, iterations=12)
    out[ring & near_piece & ~piece] = CHAR
    return out


def break_up(hull_img, inside_img, n, seed):
    hull = np.array(hull_img.convert("RGBA"))
    inside = np.array(inside_img.convert("RGBA"))
    mask = hull[:, :, 3] > 0
    # thin bits (engine glow, antennae) go with whichever piece is nearest; cut on the solid body
    rng = np.random.default_rng(seed)
    seeds = _seeds(ndimage.binary_erosion(mask, iterations=3) if ndimage.binary_erosion(mask, iterations=3).sum() > 200 else mask, n, rng)
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w]
    jag = _noise((h, w), rng, 3.0) * 60.0 + _noise((h, w), rng, 1.0) * 14.0
    d = np.stack([np.hypot(xx - sx, yy - sy) + jag * (1 + 0.3 * i) for i, (sx, sy) in enumerate(seeds)])
    label = np.argmin(d, 0)
    pieces = []
    for i in range(n):
        piece = mask & (label == i)
        # drop specks that came loose from their piece; they join the biggest neighbour
        lab, k = ndimage.label(piece)
        if k > 1:
            sizes = ndimage.sum(piece, lab, range(1, k + 1))
            keep = lab == (1 + int(np.argmax(sizes)))
            label[piece & ~keep] = (i + 1) % n
            piece = keep
        pieces.append(piece)
    pieces = [mask & (label == i) for i in range(n)]
    out = []
    for i, piece in enumerate(pieces):
        others = mask & ~piece
        out.append(Image.fromarray(_tear(hull, inside, piece, others, rng), "RGBA"))
    return out


def chips(hull_img, inside_img, spots, seed):
    """Bits that break off at the given spots: [(x, y, r)], and the cut-away without them."""
    hull = np.array(hull_img.convert("RGBA"))
    inside = np.array(inside_img.convert("RGBA"))
    mask = hull[:, :, 3] > 0
    rng = np.random.default_rng(seed)
    h, w = mask.shape
    yy, xx = np.mgrid[0:h, 0:w]
    jag = _noise((h, w), rng, 1.5) * 10.0
    gone = np.zeros_like(mask)
    bits = []
    for (x, y, r) in spots:
        piece = mask & (np.hypot(xx - x, yy - y) + jag < r)
        gone |= piece
        bits.append(Image.fromarray(_tear(hull, inside, piece, mask & ~piece, rng, band=4), "RGBA"))
    rest = mask & ~gone
    broken = _tear(inside, inside, rest, gone, rng, band=3)
    broken[rest & (broken[:, :, 3] == 0)] = inside[rest & (broken[:, :, 3] == 0)]
    return bits, Image.fromarray(broken, "RGBA")


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    made = 0
    for hull_path in sorted((root / "art/ships").glob("*/hull*.png")):
        inside_path = hull_path.with_name(hull_path.name.replace("hull", "interior"))
        if not inside_path.exists():
            continue
        hull, inside = Image.open(hull_path), Image.open(inside_path)
        area = (np.array(hull)[:, :, 3] > 0).sum()
        n = 3 if area < 30000 else (4 if area < 60000 else 5)
        stem = hull_path.stem.replace("hull", "gib")
        for old in hull_path.parent.glob(stem + "_*.png"):
            old.unlink()
        for i, g in enumerate(break_up(hull, inside, n, seed=len(str(hull_path))), 1):
            g.save(hull_path.with_name(f"{stem}_{i}.png"))
        made += 1
    # your fighter: a wing tip, the end of a pod and a piece of the other wing break off before the jump
    st = root / "art/ships/starter"
    bits, broken = chips(Image.open(st / "hull.png"), Image.open(st / "interior.png"),
                         [(124, 10, 16), (40, 132, 13), (150, 180, 14)], seed=7)
    for i, b in enumerate(bits, 1):
        b.save(st / f"chip_{i}.png")
    broken.save(st / "interior_broken.png")
    print("ok", made, "ships")
