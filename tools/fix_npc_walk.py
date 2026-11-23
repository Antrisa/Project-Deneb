"""Rebuild resident profile walks (left column, mirrored right) from the standing pose.

Usage: python3 -I fix_npc_walk.py SRC_ART_DIR OUT_ART_DIR

Rows: 0 stand, 1 contact A, 2 contact B, 3 passing A, 4 passing B (playback 1, 3, 2, 4).
Facing left, so forward is -x.

Contact: the body drops one pixel; one leg steps forward and the other back from the hip,
each a single outlined leg cut from the standing pair, the far one in shade; feet keep their
shape. Passing: the standing legs (the lifted foot is hidden behind the planted one).
Residents with a configured hand also swing the near arm from the shoulder (an outlined
sleeve and the hand) with the far hand showing on the other side.
Tails, robes and bags below the hips follow the standing pose with the body.
"""
import sys, os
import numpy as np
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
FW, FH, LEFT = 24, 48, 2
DARK = 0.72
LIFT, TUCK = 2, 3
ARM_FORWARD, ARM_BACK = 5, 4
FAR_HAND = False     # a far hand peeking past the body read as a stray mark at this size
LEG_W = 5            # one leg in profile, outlines included
FOOT_LEN = 6         # one foot, toe to heel

# hip: first leg row below the crotch or hem. hand: x0, x1, y0, y1 of the near hand in the
# standing profile (outline included). shoulder: rows above the hand where the arm pivots.
CAST = {
    "ana": dict(hip=37, hand=(10, 14, 30, 34)),
    "ana_chernog": dict(hip=37, hand=(9, 13, 31, 34)),
    "artie": dict(hip=36, hand=(11, 16, 29, 35)),
    "bram": dict(hip=40, arm=(13, 31, 36)),
    "evarra": dict(hip=39, arm=(12, 24, 33), erase=[(13, 15, 31, 36)]),
    "freya": dict(hip=37, hand=(9, 13, 30, 34)),
    "garrick": dict(hip=37, hand=(9, 15, 31, 35)),
    "ixali": dict(hip=37, hand=(11, 14, 31, 34)),
    "jasper": dict(hip=38, arm=(11, 24, 33)),
    "job": dict(hip=37, hand=(13, 18, 31, 35)),
    "kit": dict(hip=38, arm=(12, 31, 36)),
    "maren": dict(hip=39, arm=(12, 23, 33)),
    "maren_weekend": dict(hip=36, hand=(10, 14, 28, 33)),
    "maren_winter": dict(hip=39, arm=(11, 23, 33), erase=[(9, 13, 30, 34)]),
    "merrow": dict(hip=40, arm=(13, 28, 34)),
    "nub": dict(hip=41, arm=(12, 34, 38)),
    "ooma": dict(hip=41, arm=(11, 26, 35), erase=[(8, 13, 31, 36)]),
    "owen": dict(hip=37, hand=(12, 17, 32, 36)),
    "pip": dict(hip=39, arm=(12, 30, 36), erase=[(10, 14, 33, 38)]),
    "quill": dict(hip=37, arm=(12, 24, 33), erase=[(11, 15, 32, 36)]),
    "rusk": dict(hip=38, arm=(11, 25, 34)),
    "saffi": dict(hip=41, arm=(10, 25, 34)),
    "sara_solid": dict(hip=35, arm=(11, 23, 32), erase=[(9, 13, 29, 33)]),
    "stu": dict(hip=38, hand=(13, 17, 33, 36)),
    "tarbesh": dict(hip=42, arm=(12, 24, 34), erase=[(9, 14, 32, 36)]),
    "tobbin": dict(hip=40, arm=(13, 30, 35)),
    "vzzket": dict(hip=37, arm=(12, 24, 33), erase=[(11, 15, 31, 35)]),
    "zaas": dict(hip=38, hand=(11, 15, 34, 38)),
}


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

def paint_leg(out, s, rows, part, shade, win, leg_w, foot_len):
    """One leg, kept straight from the hip: every trouser row starts at the leg's hip column
    (plus the stride offset), and the foot sits under the ankle where the standing foot sits
    under the standing ankle, so the foot always travels with its leg."""
    src = darken(s) if shade else s
    lo_w, hi_w = win

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
    for dest_y, sy, dx, _ in leg_rows:
        lc = leg_cols(sy)
        if lc is None or not (0 <= dest_y < FH):
            continue
        cols, _ = lc
        for k, sx in enumerate(cols):
            x = home + k + dx
            if s[sy, sx, 3] and 0 <= x < FW:
                out[dest_y, x] = src[sy, sx]
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


def stride_rows(hip, ft, D, dy):
    legs = list(range(hip, ft))
    n = ft - (hip + dy)
    rows = []
    for i in range(n):
        sy = legs[min(len(legs) - 1, int(round(i * (len(legs) - 1) / max(1, n - 1))))]
        f = (i + 1) / n
        rows.append((hip + dy + i, sy, int(np.sign(D) * np.floor(abs(D) * f + 0.5)), False))
    rows += [(y, y, D, True) for y in range(ft, 46)]
    return rows


def lower_body(s, hip, ft, win, row):
    """Everything below the hips for one walk row (left-facing)."""
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
        leg_len = ft - hip
        D = 3 if leg_len >= 4 else 2
        leg_w = LEG_W if (win[1] - win[0] + 1) >= 6 else LEG_W - 1
        foot_len = FOOT_LEN
        near, far = (-D, D) if row == 1 else (D, -D)
        for d, shade in ((far, True), (near, False)):
            part = "front" if d < 0 else "back"
            paint_leg(out, s, stride_rows(hip, ft, d, dy), part, shade, win, leg_w, foot_len)
    else:
        # the lifted foot stays hidden behind the planted leg
        legs = s.copy(); legs[:hip] = 0
        over(out, legs)
    over(out, shifted(rest, 0, dy))
    return out


# ----------------------------------------------------------------------------- arms

def swing_arm(strip, pivot, hand_top, h, lift):
    out = np.zeros_like(strip)
    span_ = max(1, hand_top - pivot)
    roll = int(np.sign(h)) if abs(h) >= ARM_BACK else 0
    for y in range(FH):
        if not strip[y, :, 3].any():
            continue
        if y >= hand_top:
            dx, ry = h, -lift
        else:
            f = (y - pivot) / span_
            v = roll + (h - roll) * f
            dx = int(np.sign(v) * np.floor(abs(v) + 0.5))
            ry = -lift if f > 0.6 else (-(lift // 2) if f > 0.3 else 0)
        for x in range(FW):
            if strip[y, x, 3] and 0 <= x + dx < FW and 0 <= y + ry < FH:
                out[y + ry, x + dx] = strip[y, x]
    # close a one-row tear opened by the arc
    for y in range(FH - 1, 1, -1):
        for x in range(FW):
            if out[y, x, 3] and not out[y - 1, x, 3] and out[y - 2, x, 3] and y - 1 >= pivot:
                out[y - 1, x] = out[y, x]
    return out


def upper_body(s, hip, hand, row):
    """Standing pose above the hips, with the arm swung for this row (left-facing)."""
    body = s.copy(); body[hip:] = 0
    if not hand:
        return body
    h = {1: ARM_BACK, 2: -ARM_FORWARD, 3: -2, 4: 2}[row]
    x0, x1, y0, y1 = hand
    pivot = y0 - 8
    # the arm: the hand box and the sleeve above it, outlined on both sides
    strip = np.zeros_like(s)
    for y in range(pivot, y1 + 1):
        for x in range(x0, x1 + 1):
            if s[y, x, 3]:
                strip[y, x] = s[y, x]
    dark = min(((lum(s[y, x]), y, x) for y in range(pivot, y1 + 1) for x in range(x0, x1 + 1) if s[y, x, 3]))
    line = s[dark[1], dark[2]].copy()
    for y in range(pivot, y0):
        xs = [x for x in range(x0, x1 + 1) if strip[y, x, 3]]
        if xs:
            strip[y, xs[0]] = line; strip[y, xs[-1]] = line
    # the body behind the arm: the row's middle cloth tone, closed with the outline at the back
    base = body.copy()
    torso_back = span(s, y0 - 1)[1]
    for y in range(pivot, y1 + 1):
        sp = span(s, y)
        others = [x for x in range(FW) if s[y, x, 3] and not (x0 <= x <= x1)]
        tones = sorted(others, key=lambda x: lum(s[y, x]))
        fill = s[y, tones[len(tones) // 2]] if tones else None
        back = torso_back if y >= y0 else (sp[1] if sp else x1)
        for x in range(x0, x1 + 1):
            if not s[y, x, 3]:
                continue
            if fill is None or x > back:
                base[y, x] = 0
            elif x == back:
                base[y, x] = line
            else:
                base[y, x] = fill
    base[hip:] = 0
    lift = (2 if h < 0 else 1) if abs(h) >= ARM_BACK else 0
    out = np.zeros_like(s)
    if FAR_HAND and abs(h) >= ARM_BACK:
        fh = ARM_BACK if h < 0 else -ARM_FORWARD
        far = swing_arm(strip, pivot, y0, fh, 2 if fh < 0 else 1)
        over(out, darken(far))
    over(out, base)
    over(out, swing_arm(strip, pivot, y0, h, lift))
    return out


def face_tone(s):
    """A skin or fur tone from the front of the face, for a drawn hand."""
    ys = np.where(s[:, :, 3].max(1) > 0)[0]
    top = int(ys.min())
    best = None
    for y in range(top + 5, top + 15):
        sp = span(s, y)
        if not sp:
            continue
        for x in (sp[0] + 1, sp[0] + 2):
            p = s[y, x]
            if p[3] and (best is None or lum(p) > lum(best)):
                best = p.copy()
    return best


def draw_arm(s, shoulder, hand_y, h, lift, body):
    """A chunky sleeve from the shoulder to a mitten hand h pixels ahead (-) or behind (+), in
    the body's own cloth tones. Its edges are a shade of the cloth where they cross the body
    and the dark outline where they stand clear of it."""
    sx, sy = shoulder
    seg = [s[y, x] for y in range(sy, hand_y + 1) for x in range(FW) if s[y, x, 3]]
    line = min(seg, key=lum).copy()
    cloth = sorted([p for p in seg if lum(p) > lum(line) + 25], key=lum) or [line]
    mid = cloth[len(cloth) // 2].copy()
    light = cloth[min(len(cloth) - 1, (len(cloth) * 4) // 5)].copy()
    shade = mid.copy(); shade[:3] = np.round(shade[:3] * 0.7)
    skin = face_tone(s)
    skin_dark = skin.copy(); skin_dark[:3] = np.round(skin_dark[:3] * 0.8)
    out = np.zeros_like(s)
    hy = hand_y - lift
    n = max(1, hy - sy)
    roll = int(np.sign(h)) if abs(h) >= ARM_BACK else 0

    def edge(y, x):
        return shade if body[y, x, 3] else line

    for i in range(n + 1):
        y = sy + i
        f = i / n
        v = roll + (h - roll) * f
        cx = sx + int(np.sign(v) * np.floor(abs(v) + 0.5))
        for x, kind in ((cx - 2, "e"), (cx - 1, light), (cx, mid), (cx + 1, "e")):
            if 0 <= x < FW and 0 <= y < FH:
                out[y, x] = edge(y, x) if isinstance(kind, str) else kind
    # the hand: a three-wide mitten in the face tone at the end of the sleeve
    hx = sx + h
    for y in range(hy, hy + 4):
        for x in range(hx - 2, hx + 3):
            if not (0 <= x < FW and 0 <= y < FH):
                continue
            if y == hy + 3 or x in (hx - 2, hx + 2):
                out[y, x] = line
            else:
                out[y, x] = skin_dark if (x == hx + 1 or y == hy + 2) else skin
    return out


def overlay_arms(body, s, arm, row):
    shoulder, hand_y = arm[:2], arm[2]
    h = {1: ARM_BACK, 2: -ARM_FORWARD, 3: -2, 4: 2}[row]
    lift = (2 if h < 0 else 1) if abs(h) >= ARM_BACK else 0
    out = np.zeros_like(s)
    if FAR_HAND and abs(h) >= ARM_BACK:
        # only the far hand shows, past the chest or the back
        fh = ARM_BACK + 2 if h < 0 else -(ARM_FORWARD + 1)
        far = draw_arm(s, shoulder, hand_y, fh, 2 if fh < 0 else 1, body)
        far[:hand_y - 2] = 0
        over(out, darken(far))
    over(out, body)
    over(out, draw_arm(s, shoulder, hand_y, h, lift, body))
    return out


def erase_boxes(s, boxes):
    """Paint over a resident's own hand where a drawn arm replaces it: inside the body the
    row's middle cloth tone, outside it nothing, with the outline closing the new edge."""
    out = s.copy()
    for (x0, x1, y0, y1) in boxes:
        for y in range(y0, y1 + 1):
            others = [x for x in range(FW) if s[y, x, 3] and not (x0 <= x <= x1)]
            if not others:
                out[y, x0:x1 + 1] = 0
                continue
            lo, hi = min(others), max(others)
            line = min((s[y, x] for x in others), key=lum).copy()
            tones = sorted(others, key=lambda x: lum(s[y, x]))
            fill = s[y, tones[len(tones) // 2]].copy()
            for x in range(x0, x1 + 1):
                if not s[y, x, 3]:
                    continue
                if x < lo or x > hi:
                    out[y, x] = 0
                elif x in (lo, hi):
                    out[y, x] = line
                else:
                    out[y, x] = fill
    return out


HAND_ONLY = {"freya", "garrick", "zaas"}   # painted arms that read better with only the hand moving


def mitten(s, cx, top):
    """A five-by-four mitten in the face tone with an outline, as a sprite-sized layer."""
    skin = face_tone(s)
    dark = skin.copy(); dark[:3] = np.round(dark[:3] * 0.8)
    seg = [s[y, x] for y in range(FH) for x in range(FW) if s[y, x, 3]]
    line = min(seg, key=lum).copy()
    out = np.zeros_like(s)
    for y in range(top, top + 4):
        for x in range(cx - 2, cx + 3):
            if 0 <= x < FW and 0 <= y < FH:
                if y == top + 3 or x in (cx - 2, cx + 2) or y == top:
                    out[y, x] = line if (y == top + 3 or x in (cx - 2, cx + 2)) else skin
                else:
                    out[y, x] = dark if (x == cx + 1 or y == top + 2) else skin
    return out


def hand_swing(body, s, hand, row):
    """Swing only the hand: ahead of the body or behind it, joined to the body by a short
    cuff of the body's cloth where it stands clear, and lifted a little on the full swing."""
    h = {1: ARM_BACK, 2: -ARM_FORWARD, 3: -2, 4: 2}[row]
    lift = (2 if h < 0 else 1) if abs(h) >= ARM_BACK else 0
    moved = shifted(hand, h, -lift)
    ys, xs = np.where(moved[:, :, 3] > 0)
    out = body.copy()
    if len(ys):
        top = int(ys.min())
        rows = range(top, min(FH, top + 3))
        seg = [s[y, x] for y in rows for x in range(FW) if s[y, x, 3]]
        if seg:
            line = min(seg, key=lum).copy()
            cloth = sorted([p for p in seg if lum(p) > lum(line) + 25], key=lum) or [line]
            mid = cloth[len(cloth) // 2].copy()
            hx0, hx1 = int(xs.min()), int(xs.max())
            for i, y in enumerate(rows):
                sp = span(body, y)
                if sp is None:
                    continue
                if hx1 < sp[0]:
                    gap = range(hx1 + 1, sp[0])
                elif hx0 > sp[1]:
                    gap = range(sp[1] + 1, hx0)
                else:
                    continue
                for x in gap:
                    out[y, x] = mid if i == 1 else line
    over(out, moved)
    return out


def build(s, cfg, row, painted):
    hip = cfg["hip"]
    if "erase" in cfg:
        s = erase_boxes(s, cfg["erase"])
    ft = foot_top(s)
    if ft - hip < 2:
        ft = min(45, hip + 2)
    win = legs_window(s, hip, ft)
    dy = 1 if row in (1, 2) else 0
    out = lower_body(s, hip, ft, win, row)
    if "arm" in cfg or cfg.get("name") in HAND_ONLY:
        # the body without its hand, then the hand alone swings ahead or behind
        body = s.copy(); body[hip:] = 0
        if "hand" in cfg:
            x0, x1, y0, y1 = cfg["hand"]
            hand = np.zeros_like(s)
            hand[y0:y1 + 1, x0:x1 + 1] = s[y0:y1 + 1, x0:x1 + 1]
            body = erase_boxes(s, [(x0, x1, y0, y1)]); body[hip:] = 0
        else:
            sx, sy, hy = cfg["arm"]
            hand = mitten(s, sx, hy)
        full = out.copy()
        over(full, shifted(body, 0, dy))
        return shifted(hand_swing(shifted(full, 0, -dy), s, hand, row), 0, dy)
    up = upper_body(s, hip, cfg.get("hand"), row)
    # the upper body (and a swung hand) sits over the hips and legs
    over(out, shifted(up, 0, dy))
    return out


os.makedirs(OUT, exist_ok=True)
for name, cfg in CAST.items():
    cfg = dict(cfg, name=name)
    a = np.array(Image.open(os.path.join(SRC, f"npc_{name}.png")).convert("RGBA"))
    s = a[0:FH, LEFT * FW:(LEFT + 1) * FW].copy()
    for row in (1, 2, 3, 4):
        painted = a[row * FH:(row + 1) * FH, LEFT * FW:(LEFT + 1) * FW].copy()
        new = build(s, cfg, row, painted)
        a[row * FH:(row + 1) * FH, LEFT * FW:(LEFT + 1) * FW] = new
        a[row * FH:(row + 1) * FH, (LEFT + 1) * FW:(LEFT + 2) * FW] = new[:, ::-1]
    Image.fromarray(a).save(os.path.join(OUT, f"npc_{name}.png"))
print("ok")
