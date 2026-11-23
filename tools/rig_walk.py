"""Build a resident's side walk (rows 1 to 4, left and right) from rig parts.

Usage: python3 -I rig_walk.py SRC_ART_DIR RIG_DIR OUT_ART_DIR name ...

Reads RIG_DIR/npc_<id>_side.png (body cell, arm cell) and npc_<id>_side.txt (shoulder pivot,
top of the hand, hip row), and writes OUT_ART_DIR/npc_<id>.png with the walk rows replaced.
The standing frames and the front and back walks are copied unchanged.

Rows: 1 contact A, 2 contact B, 3 passing A, 4 passing B (playback 1, 3, 2, 4); facing left.
Contact: the body drops a pixel, the legs stride (one leg forward, one back, the far one in
shade), the arm swings ARM_BACK behind or ARM_FORWARD ahead from the shoulder.
Passing: standing legs, the arm two pixels into its swing.
"""
import sys, os
import numpy as np
from PIL import Image

FW, FH, LEFT = 24, 48, 2
DARK = 0.72
LIFT, TUCK = 2, 3
ARM_FORWARD, ARM_BACK = 5, 4
LEG_W = 6
FOOT_LEN = 6
TRAIL_BACK = 3       # how far behind the hip the lifted foot trails when passing
STRIDE = 4           # how far each foot lands from the hip on a contact step


def span(c, y):
    xs = np.where(c[y, :, 3] > 0)[0]
    return (int(xs.min()), int(xs.max())) if len(xs) else None


def lum(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def darken(c):
    o = c.copy(); m = o[:, :, 3] > 0
    o[m, :3] = np.round(o[m, :3] * DARK).astype(o.dtype)
    return o


def shifted(c, dx, dy):
    out = np.zeros_like(c)
    h, w = c.shape[:2]
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = c[ys0:ys1, xs0:xs1]
    return out


def over(dst, src):
    m = src[:, :, 3] > 0
    dst[m] = src[m]


def foot_top(s):
    for y in range(45, 37, -1):
        a, b = span(s, y), span(s, y - 1)
        if a is None or b is None:
            return y
        if (b[1] - b[0]) < (a[1] - a[0]) - 1 or b[0] > a[0]:
            return y
    return 43


def legs_window(s, hip, ft):
    """Columns of the standing leg pair: the narrowest span between the hip and the feet."""
    best = None
    for y in range(hip, ft):
        sp = span(s, y)
        if sp and (best is None or sp[1] - sp[0] < best[1] - best[0]):
            best = sp
    return best or span(s, ft - 1)


# ----------------------------------------------------------------------------- legs


def paint_leg(out_final, s, rows, part, shade, win, leg_w, foot_len):
    """One leg, kept straight from the hip: every trouser row starts at the leg's hip column
    (plus the stride offset), and the foot sits under the ankle where the standing foot sits
    under the standing ankle, so the foot always travels with its leg."""
    src = darken(s) if shade else s
    lo_w, hi_w = win
    out = np.zeros_like(out_final)

    def leg_cols(sy):
        sp = span(s, sy)
        if sp is None:
            return None
        lo, hi = max(sp[0], lo_w - 1), min(sp[1], hi_w + 1)
        inner = list(range(lo + 1, hi)) or [lo]
        k = leg_w - 2
        if part == "front":
            pick = [inner[min(len(inner) - 1, i)] for i in range(k)]
            base = lo
        else:
            pick = [inner[max(0, len(inner) - k + i)] for i in range(k)]
            base = hi - leg_w + 1
        return [lo] + pick + [hi], base

    leg_rows = [r for r in rows if not r[3]]
    foot_rows = [r for r in rows if r[3]]
    home = leg_cols(leg_rows[0][1])[1] if leg_rows else None
    ankle_sy = leg_rows[-1][1] if leg_rows else None
    prev = 0
    for dest_y, sy, dx, _ in leg_rows:
        lc = leg_cols(sy)
        if lc is None or not (0 <= dest_y < FH):
            prev = dx
            continue
        cols, _ = lc
        # a steep leg steps several pixels between rows; widen each row over the step so the
        # leg keeps its full thickness on the slant instead of thinning to a staircase
        shifts = range(min(prev, dx), max(prev, dx) + 1)
        for sh in sorted(shifts, key=lambda v: abs(v - dx), reverse=True):
            for k, sx in enumerate(cols):
                x = home + k + sh
                if not (s[sy, sx, 3] and 0 <= x < FW):
                    continue
                inner = 0 < k < len(cols) - 1
                # the in-between copies use the leg's fill, the outline only at the true edges
                if sh == dx or inner:
                    out[dest_y, x] = src[sy, sx]
                elif not out[dest_y, x, 3]:
                    out[dest_y, x] = src[sy, cols[1] if len(cols) > 2 else sx]
        lo_edge = home + min(prev, dx)
        hi_edge = home + max(prev, dx) + len(cols) - 1
        for x in (lo_edge, hi_edge):
            if 0 <= x < FW:
                out[dest_y, x] = src[sy, cols[0] if x == lo_edge else cols[-1]]
        prev = dx
    if not foot_rows:
        return
    ankle = leg_cols(ankle_sy) if ankle_sy is not None else None
    for dest_y, sy, dx, _ in foot_rows:
        sp = span(s, sy)
        if sp is None or not (0 <= dest_y < FH):
            continue
        lo, hi = sp
        n = min(foot_len, hi - lo + 1)
        cols = list(range(lo, lo + n - 1)) + [hi]
        # toe offset from the ankle, as in the standing pose (front of the paired legs)
        ankle_lo = span(s, ankle_sy)[0] if ankle_sy is not None else lo
        base = (home if home is not None else lo) + (lo - max(ankle_lo, lo_w - 1))
        for k, sx in enumerate(cols):
            x = base + k + dx
            if s[sy, sx, 3] and 0 <= x < FW:
                out[dest_y, x] = src[sy, sx]
    # the ankle never pokes out past the shoe: trim the leg rows just above the foot to the
    # foot's own width
    feet_y = [r[0] for r in foot_rows if 0 <= r[0] < FH]
    if feet_y:
        fy = min(feet_y)
        xs = np.where(out[fy, :, 3] > 0)[0]
        if len(xs):
            fx0, fx1 = int(xs.min()), int(xs.max())
            for y in (fy - 1, fy - 2):
                if 0 <= y < FH:
                    out[y, :fx0] = 0
                    out[y, fx1 + 1:] = 0
    over(out_final, out)


def stride_rows(hip, ft, D, dy, extend=0):
    legs = [hip] * extend + list(range(hip, ft))
    hip = hip - extend
    n = ft - (hip + dy)
    rows = []
    for i in range(n):
        sy = legs[min(len(legs) - 1, int(round(i * (len(legs) - 1) / max(1, n - 1))))]
        f = (i + 1) / n
        rows.append((hip + dy + i, sy, int(np.sign(D) * np.floor(abs(D) * f + 0.5)), False))
    rows += [(y, y, D, True) for y in range(ft, 46)]
    return rows


def lower_body(s, hip, ft, win, row, extend=0):
    """Everything below the hips for one walk row (left-facing). With extend, the striding
    legs start that many rows higher, in front of a long coat's hem, as if the coat parts."""
    out = np.zeros_like(s)
    dy = 1 if row in (1, 2) else 0
    # tails, hems, bags: standing pose outside the leg column, with the body
    rest = s.copy(); rest[:hip] = 0
    for y in range(hip, 46):
        sp = span(s, y)
        if sp is None:
            continue
        lo, hi = (max(sp[0], win[0] - 1), min(sp[1], win[1] + 1)) if y < ft else sp
        rest[y, lo:hi + 1] = 0
    if row in (1, 2):
        leg_len = ft - hip + extend
        # short legs below a long coat cannot reach as far without lying flat
        D = max(2, min(STRIDE, leg_len - 1))
        leg_w = LEG_W if (win[1] - win[0] + 1) >= 6 else LEG_W - 1
        foot_len = FOOT_LEN
        near, far = (-D, D) if row == 1 else (D, -D)
        for d, shade in ((far, True), (near, False)):
            part = "front" if d < 0 else "back"
            paint_leg(out, s, stride_rows(hip, ft, d, dy, extend), part, shade, win, leg_w, foot_len)
    else:
        # the trailing leg bends back from the hip with its foot lifted off the floor, joined
        # to the body all the way (in shade when it is the far leg); the planted leg stands in
        # front of it
        leg_w = LEG_W if (win[1] - win[0] + 1) >= 6 else LEG_W - 1
        lifted = [(y - LIFT, sy, dx, isfoot) for (y, sy, dx, isfoot) in stride_rows(hip, ft, TRAIL_BACK, 0)]
        lifted = [r for r in lifted if r[0] >= hip]
        paint_leg(out, s, lifted, "back", row == 3, win, leg_w, FOOT_LEN)
        legs = s.copy(); legs[:hip] = 0
        over(out, legs)
    over(out, shifted(rest, 0, dy))
    return out


# ----------------------------------------------------------------------------- arms


def swing_arm(strip, pivot, hand_top, h, lift):
    """Swing an arm sprite from the shoulder. The upper arm turns about the pivot; on the
    forward swing the elbow bends so the forearm and hand reach further ahead and rise, on the
    back swing the arm stays straight. Rows are mapped top to bottom without gaps, so the
    sleeve never tears or folds back on itself."""
    out = np.zeros_like(strip)
    rows = [y for y in range(FH) if strip[y, :, 3].any() and y >= pivot - 1]
    if not rows:
        return out
    span_ = max(1, hand_top - pivot)
    elbow = 0.5
    forward = h < 0
    bend = -1 if (forward and abs(h) >= ARM_BACK) else 0
    roll = int(np.sign(h)) if abs(h) >= ARM_BACK else 0
    placed = []
    for y in rows:
        f = min(1.0, max(0.0, (y - pivot) / span_))
        if f <= elbow:
            v = roll + (h * elbow - roll) * (f / elbow)
            up = lift * (f / elbow) * 0.5
        else:
            g = (f - elbow) / (1 - elbow)
            v = h * elbow + (h + bend - h * elbow) * g
            up = lift * (0.5 + 0.5 * g)
        if y >= hand_top:
            v, up = h + bend, lift
        dx = int(np.sign(v) * np.floor(abs(v) + 0.5))
        placed.append((y, dx, int(round(up))))
    last_dest = None
    for (y, dx, up) in placed:
        dest = y - up
        if last_dest is not None and dest <= last_dest:
            dest = last_dest + 1 if dest < last_dest else dest
        for d in range((last_dest + 1) if last_dest is not None else dest, dest + 1):
            for x in range(FW):
                if strip[y, x, 3] and 0 <= x + dx < FW and 0 <= d < FH:
                    out[d, x + dx] = strip[y, x]
        last_dest = dest
    return out


def build(body, arm, pivot, hand_top, hip, row, extend=0):
    s = body
    ft = foot_top(s)
    if ft - hip < 2:
        ft = min(45, hip + 2)
    win = legs_window(s, hip, ft)
    dy = 1 if row in (1, 2) else 0
    out = lower_body(s, hip, ft, win, row, extend if row in (1, 2) else 0)
    upper = s.copy(); upper[hip:] = 0
    up = shifted(upper, 0, dy)
    if extend and row in (1, 2):
        # the legs' top rows stay in front of the hem
        legs_top = out.copy(); legs_top[hip + dy:] = 0
        over(out, up)
        over(out, legs_top)
    else:
        over(out, up)
    h = {1: ARM_BACK, 2: -ARM_FORWARD, 3: -2, 4: 2}[row]
    lift = (2 if h < 0 else 1) if abs(h) >= ARM_BACK else 0
    over(out, shifted(swing_arm(arm, pivot[1], hand_top, h, lift), 0, dy))
    return out


def read_rig(rig_dir, name):
    sheet = np.array(Image.open(os.path.join(rig_dir, f"npc_{name}_side.png")).convert("RGBA"))
    vals = {}
    for line in open(os.path.join(rig_dir, f"npc_{name}_side.txt")):
        k, *v = line.split()
        vals[k] = [int(x) for x in v]
    return (sheet[:, :FW].copy(), sheet[:, FW:].copy(), tuple(vals["pivot"]), vals["hand_top"][0],
            vals["hip"][0], vals.get("leg_extend", [0])[0])


if __name__ == "__main__":
    SRC, RIG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(OUT, exist_ok=True)
    for name in sys.argv[4:]:
        body, arm, pivot, hand_top, hip, extend = read_rig(RIG, name)
        a = np.array(Image.open(os.path.join(SRC, f"npc_{name}.png")).convert("RGBA"))
        for row in (1, 2, 3, 4):
            new = build(body, arm, pivot, hand_top, hip, row, extend)
            a[row * FH:(row + 1) * FH, LEFT * FW:(LEFT + 1) * FW] = new
            a[row * FH:(row + 1) * FH, (LEFT + 1) * FW:(LEFT + 2) * FW] = new[:, ::-1]
        # the side standing pose is the parts at rest, so it matches the walk
        stand = body.copy(); over(stand, arm)
        a[0:FH, LEFT * FW:(LEFT + 1) * FW] = stand
        a[0:FH, (LEFT + 1) * FW:(LEFT + 2) * FW] = stand[:, ::-1]
        Image.fromarray(a).save(os.path.join(OUT, f"npc_{name}.png"))
        print(name, "ok")
