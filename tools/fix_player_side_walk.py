"""Rebuild the player's profile walk rows (left column, mirrored to right) from the standing pose.

Usage: python3 -I fix_player.py SRC_ART_PLAYER_DIR OUT_ART_PLAYER_DIR [--keep-strides]

Rows: 0 stand, 1 contact A, 2 contact B, 3 passing A, 4 passing B (playback 1,3,2,4).
Facing left: forward is -x.
"""
import sys, os, shutil
import numpy as np
from PIL import Image

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SRC, OUT = ARGS[0], ARGS[1]
# --keep-strides keeps the painted contact legs, head and hair (which lean back one pixel) and
# redraws only the contact arms over them, plus the full passing poses.
KEEP_STRIDES = "--keep-strides" in sys.argv
WALK_ROWS = (1, 2, 3, 4)
STRIDE_LEAN = 1      # the painted contact strides carry the head one pixel behind the hips
FW, FH, CH = 24, 48, 10
LEFT = 2

ARM_FORWARD = 6      # hand travel ahead of the hip on a contact step, in pixels
ARM_BACK = 5         # hand travel behind the hip
ARM_SWING = 4        # swings at least this large show the far arm and lift the hand
UPPER_ARM = 10       # rows from the shoulder pivot down to the top of the hand
SHOULDER_ROLL = 1    # the shoulder turns with the swing on a contact step

# Per walk row: body drop (contact rows sit one pixel lower), near-arm hand swing (+ = back),
# leg poses. Contact A: near leg forward, far leg back, near arm back. Contact B: the reverse.
ROWS = {
    1: dict(dy=1, arm=+ARM_BACK, near=("stride", -3), far=("stride", +3)),
    2: dict(dy=1, arm=-ARM_FORWARD, near=("stride", +3), far=("stride", -3)),
    3: dict(dy=0, arm=-2, near=("plant", 0), far=("lift", 0)),
    4: dict(dy=0, arm=+2, near=("lift", 0), far=("plant", 0)),
}
SHOW_FAR_HAND = True
DARK = 0.72          # far limbs sit in shade
BOOT_TOP = 41        # first boot row; the sole is row 45
BOOT_W = 7           # one boot, toe to heel
LIFT = 2             # how far a passing foot leaves the floor
TUCK = 3             # how far the lifted boot trails behind the planted calf
LEG_W = 6            # one trouser leg in profile, outlines included


def load(path):
    return np.array(Image.open(path).convert("RGBA"))


def save(arr, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(arr.astype(np.uint8), "RGBA").save(path)


def shifted(cell, dx, dy):
    out = np.zeros_like(cell)
    h, w = cell.shape[:2]
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = cell[ys0:ys1, xs0:xs1]
    return out


def over(dst, src):
    m = src[:, :, 3] > 0
    dst[m] = src[m]


def over2(dst_a, dst_m, src_a, src_m):
    """Layer art and its mask together, so unmasked (painted) pixels clear the mask under them."""
    m = src_a[:, :, 3] > 0
    dst_a[m] = src_a[m]
    dst_m[m] = src_m[m]


def darken(cell):
    out = cell.copy()
    m = out[:, :, 3] > 0
    out[m, :3] = np.round(out[m, :3] * DARK).astype(out.dtype)
    return out


def blit_row(dst, src_row, y, dx):
    """Copy one source row into dst row y shifted by dx (opaque pixels only)."""
    w = src_row.shape[0]
    for x in range(w):
        if src_row[x, 3] > 0 and 0 <= x + dx < w and 0 <= y < dst.shape[0]:
            dst[y, x + dx] = src_row[x]


# ---------------------------------------------------------------- legs (bottoms layer)

def hip_line(art):
    """First row that belongs to the swinging legs: just below a skirt's flare, else row 36."""
    widths = []
    for y in range(30, 41):
        xs = np.where(art[y, :, 3] > 0)[0]
        widths.append(xs.max() - xs.min() + 1 if len(xs) else 0)
    leg_w = widths[-1]
    for y in range(40, 33, -1):
        if widths[y - 30] > leg_w + 2:
            return y + 1
    return 34


def row_span(art, y):
    xs = np.where(art[y, :, 3] > 0)[0]
    return (int(xs.min()), int(xs.max())) if len(xs) else None


def paint_leg(out_a, out_m, art, mask, rows, part, shade):
    """Paint one profile leg. rows: list of (dest_y, src_y, front_x).
    Trouser rows are LEG_W wide with an outline on both sides, sampled from the standing row:
    the front leg takes the front half of the paired legs, the back leg the back half.
    Boot rows take BOOT_W pixels from the toe of the standing boot."""
    src = darken(art) if shade else art
    ankle_front = None
    for dest_y, sy, fx in rows:
        span = row_span(art, sy)
        if span is None:
            continue
        lo, hi = span
        if sy >= BOOT_TOP:
            # toe sits where the standing toe sits relative to the standing ankle
            ref = row_span(art, BOOT_TOP - 1)
            toe = fx + (lo - ref[0]) if ref else fx
            n = min(BOOT_W, hi - lo + 1)
            for k in range(n):
                sx = lo + k if k < n - 1 else hi
                x = toe + k
                if 0 <= x < 24 and art[sy, sx, 3]:
                    out_a[dest_y, x] = src[sy, sx]; out_m[dest_y, x] = mask[sy, sx]
            continue
        width = min(LEG_W, hi - lo + 1)
        for k in range(width):
            if k == 0:
                sx = lo
            elif k == width - 1:
                sx = hi
            else:
                sx = lo + k if part == "front" else hi - (width - 1 - k)
            x = fx + k
            if 0 <= x < 24 and art[sy, sx, 3]:
                out_a[dest_y, x] = src[sy, sx]; out_m[dest_y, x] = mask[sy, sx]


def leg_rows(art, kind, part, D, yh, dy):
    """(dest_y, src_y, front_x) for each row of one leg."""
    trousers = list(range(yh, BOOT_TOP))
    boots = list(range(BOOT_TOP, 46))
    def home(sy):
        lo, hi = row_span(art, sy)
        return lo if part in ("front", "full") else max(lo, hi - LEG_W + 1)
    if kind == "plant":
        return [(y, y, None) for y in trousers + boots]
    if kind == "stride":
        n_dest = BOOT_TOP - (yh + dy)
        out = []
        for i in range(n_dest):
            sy = trousers[min(len(trousers) - 1, int(round(i * (len(trousers) - 1) / max(1, n_dest - 1))))]
            f = (i + 1) / n_dest
            dx = int(np.sign(D) * np.floor(abs(D) * f + 0.5))
            out.append((yh + dy + i, sy, home(trousers[0]) + dx if i < n_dest - 1 else home(trousers[0]) + D))
        out[-1] = (out[-1][0], out[-1][1], home(trousers[0]) + D)
        foot = home(trousers[0]) + D
        out += [(y, y, foot) for y in boots]
        return out
    if kind == "lift":
        # The knee bends: the boot rises LIFT pixels and trails behind the hip.
        n_dest = BOOT_TOP - LIFT - yh
        out = []
        for i in range(n_dest):
            sy = trousers[min(len(trousers) - 1, int(round(i * (len(trousers) - 1) / max(1, n_dest - 1))))]
            dx = 0 if i < n_dest - 2 else (1 if i == n_dest - 2 else 2)
            out.append((yh + i, sy, home(trousers[0]) + dx))
        foot = home(trousers[0]) + TUCK
        out += [(y - LIFT, y, foot) for y in boots]
        return out
    raise ValueError(kind)


def build_bottoms(art, mask, row):
    p = ROWS[row]
    yh = hip_line(art)
    dy = p["dy"]
    out_a = np.zeros_like(art)
    out_m = np.zeros_like(mask)
    # Passing: the planted leg keeps the standing silhouette in full colour, and the lifted boot
    # tucks up behind its calf (in shade when it is the far leg). Contact: far leg first, in
    # shade, then the near leg. The hips go over both.
    order = (("far", True), ("near", False))
    if any(p[w][0] == "lift" for w in ("near", "far")):
        lifted = "near" if p["near"][0] == "lift" else "far"
        order = ((lifted, lifted == "far"), ("near" if lifted == "far" else "far", False))
    for which, shade in order:
        kind, D = p[which]
        if kind == "plant":
            legs_a = art.copy(); legs_a[:yh] = 0
            over2(out_a, out_m, legs_a, mask)
            continue
        part = "front" if (kind == "stride" and D < 0) else "back"
        paint_leg(out_a, out_m, art, mask, leg_rows(art, kind, part, D, yh, dy), part, shade)
    hips_a = art.copy(); hips_a[yh:] = 0
    hips_m = mask.copy(); hips_m[yh:] = 0
    over2(out_a, out_m, shifted(hips_a, 0, dy), shifted(hips_m, 0, dy))
    return out_a, out_m


# ---------------------------------------------------------------- arms (tops layer)

def arm_geometry(art, mask):
    skin = (mask[:, :, 3] > 0) & (mask[:, :, 0] == 0) & (mask[:, :, 1] > 0) & (art[:, :, 3] > 0)
    ys, xs = np.where(skin[31:40])
    ys = ys + 31
    return dict(x0=int(xs.min()), x1=int(xs.max()), top=int(ys.min()), bottom=int(ys.max()))


def lum(px):
    return 0.2126 * px[0] + 0.7152 * px[1] + 0.0722 * px[2]


def swing(arm_a, arm_m, rows, pivot, top, h, lift, roll):
    """Rotate an arm strip about the shoulder: the shoulder rolls `roll` pixels, each lower row
    moves in proportion to its distance from the pivot, the hand moves as one piece, and at a
    full swing the forearm and hand rise on the arc."""
    sa = np.zeros_like(arm_a); sm = np.zeros_like(arm_m)
    span = max(1, top - pivot)
    for y in rows:
        if y >= top:
            dx, ry = h, -lift
        else:
            f = (y - pivot) / span
            v = roll + (h - roll) * f
            dx = int(np.sign(v) * np.floor(abs(v) + 0.5))
            ry = -lift if f > 0.6 else (-(lift // 2) if f > 0.3 else 0)
        for x in range(24):
            if arm_a[y, x, 3] and 0 <= x + dx < 24 and 0 <= y + ry < 48:
                sa[y + ry, x + dx] = arm_a[y, x]; sm[y + ry, x + dx] = arm_m[y, x]
    # close any one-row tear the arc opened between the forearm and the hand
    for y in range(47, 0, -1):
        for x in range(24):
            if sa[y, x, 3] and not sa[y - 1, x, 3] and y - 1 >= pivot and y - 2 >= 0 and sa[y - 2, x, 3]:
                sa[y - 1, x] = sa[y, x]; sm[y - 1, x] = sm[y, x]
    return sa, sm


def build_tops(art, mask, row):
    p = ROWS[row]
    h, dy = p["arm"], p["dy"]
    g = arm_geometry(art, mask)
    back = int(max(np.where(art[g["top"] - 5, :, 3] > 0)[0]))
    # A tunic sleeve lies over the body; a jacket or tee sleeve runs down the back of the body.
    covered = g["x1"] <= back
    pivot = g["top"] - UPPER_ARM
    band = range(g["x0"], (g["x1"] if covered else back) + 1)
    rows = range(pivot, g["bottom"] + 1)
    skin = lambda y, x: mask[y, x, 3] > 0 and mask[y, x, 0] == 0 and mask[y, x, 1] > 0
    cloth = lambda y, x: mask[y, x, 3] > 0 and mask[y, x, 0] > 0

    # the darkest cloth and skin in the arm are its outlines
    arm_px = [(y, x) for y in rows for x in band if art[y, x, 3]]
    def darkest(test):
        c = [(lum(art[y, x]), y, x) for (y, x) in arm_px if test(y, x)]
        return min(c)[1:] if c else None
    cloth_line, skin_line = darkest(cloth), darkest(skin)

    # the strip that moves, outlined on both sides so it reads against the body
    arm_a = np.zeros_like(art); arm_m = np.zeros_like(mask)
    for y in rows:
        xs = [x for x in band if art[y, x, 3]]
        if not xs:
            continue
        for x in xs:
            arm_a[y, x] = art[y, x]; arm_m[y, x] = mask[y, x]
        if y < g["top"]:
            for x in (xs[0], xs[-1]):
                line = skin_line if skin(y, x) and skin_line else cloth_line
                if line and not (art[y, x, 3] and mask[y, x, 3] == 0):
                    arm_a[y, x] = art[line]; arm_m[y, x] = mask[line]

    # the body behind the arm: cloth of the same row, closed by the back outline
    base_a = art.copy(); base_m = mask.copy()
    for y in rows:
        for x in band:
            base_a[y, x] = 0; base_m[y, x] = 0
    hem = max([y for y in range(48) if art[y, g["x0"] - 1, 3]] or [0])
    for y in rows:
        if y > hem:
            continue
        body = [x for x in range(24) if x not in band and art[y, x, 3] and cloth(y, x)]
        if not body:
            continue
        tones = sorted(body, key=lambda x: lum(art[y, x]))
        fill = tones[len(tones) // 2]
        for x in band:
            if not art[y, x, 3]:
                continue
            if x < back:
                base_a[y, x] = art[y, fill]; base_m[y, x] = mask[y, fill]
            elif x == back and cloth_line:
                base_a[y, x] = art[cloth_line]; base_m[y, x] = mask[cloth_line]
    if covered:
        # under a tunic hand the hem keeps its trim
        for y in range(g["top"], g["bottom"] + 1):
            for x in band:
                if art[y, x, 3]:
                    src = (y, g["x0"] - 1)
                    if y == g["bottom"] and art[src][3]:
                        base_a[y, x] = art[src]; base_m[y, x] = mask[src]

    def lift_for(v):
        return (2 if v < 0 else 1) if abs(v) >= ARM_SWING else 0

    def roll_for(v):
        return int(np.sign(v)) * SHOULDER_ROLL if abs(v) >= ARM_SWING else 0

    out_a = np.zeros_like(art); out_m = np.zeros_like(mask)
    if SHOW_FAR_HAND and abs(h) >= ARM_SWING:
        # the far arm swings the other way behind the body; its hand clears the silhouette
        far_h = ARM_BACK if h < 0 else -ARM_FORWARD
        far_a, far_m = swing(arm_a, arm_m, rows, pivot, g["top"], far_h, lift_for(far_h), roll_for(far_h))
        over2(out_a, out_m, darken(far_a), far_m)
    over2(out_a, out_m, base_a, base_m)
    near_a, near_m = swing(arm_a, arm_m, rows, pivot, g["top"], h, lift_for(h), roll_for(h))
    over2(out_a, out_m, near_a, near_m)
    lean = STRIDE_LEAN if (KEEP_STRIDES and row in (1, 2)) else 0
    return shifted(out_a, lean, dy), shifted(out_m, lean, dy)


def build_shift(art, mask, row):
    dy = ROWS[row]["dy"]
    return shifted(art, 0, dy), shifted(mask, 0, dy)


# ---------------------------------------------------------------- atlases

def process_walk_layer(folder, name, builder, rows=None):
    art = load(os.path.join(SRC, folder, name + ".png"))
    mask = load(os.path.join(SRC, folder, name + "_mask.png"))
    for c in range(CH):
        y0 = c * 5 * FH
        stand_a = art[y0:y0 + FH, LEFT * FW:(LEFT + 1) * FW].copy()
        stand_m = mask[y0:y0 + FH, LEFT * FW:(LEFT + 1) * FW].copy()
        for row in (rows or WALK_ROWS):
            a, m = builder(stand_a, stand_m, row)
            ys = y0 + row * FH
            art[ys:ys + FH, 2 * FW:3 * FW] = a
            mask[ys:ys + FH, 2 * FW:3 * FW] = m
            art[ys:ys + FH, 3 * FW:4 * FW] = a[:, ::-1]
            mask[ys:ys + FH, 3 * FW:4 * FW] = m[:, ::-1]
    save(art, os.path.join(OUT, folder, name + ".png"))
    save(mask, os.path.join(OUT, folder, name + "_mask.png"))


def process_carry(folder, rows=None):
    art = load(os.path.join(SRC, folder, "action_tops.png"))
    mask = load(os.path.join(SRC, folder, "action_tops_mask.png"))
    for c in range(CH):
        x0 = c * 4 * FW + LEFT * FW
        stand_a = art[0:FH, x0:x0 + FW].copy()
        stand_m = mask[0:FH, x0:x0 + FW].copy()
        for row in (rows or WALK_ROWS):
            a, m = build_shift(stand_a, stand_m, row)
            ys = row * FH
            art[ys:ys + FH, x0:x0 + FW] = a
            mask[ys:ys + FH, x0:x0 + FW] = m
            art[ys:ys + FH, x0 + FW:x0 + 2 * FW] = a[:, ::-1]
            mask[ys:ys + FH, x0 + FW:x0 + 2 * FW] = m[:, ::-1]
    save(art, os.path.join(OUT, folder, "action_tops.png"))
    save(mask, os.path.join(OUT, folder, "action_tops_mask.png"))


for folder in ("", "body2"):
    kept = (3, 4) if KEEP_STRIDES else None
    process_walk_layer(folder, "bottoms", build_bottoms, kept)
    process_walk_layer(folder, "tops", build_tops)
    process_walk_layer(folder, "faces", build_shift, kept)
    process_walk_layer(folder, "hair", build_shift, kept)
    process_carry(folder, kept)
print("ok")
