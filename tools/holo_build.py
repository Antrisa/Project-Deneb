"""Rebuild S.A.R.A.'s projector clips (sara/animations/*_body.png) from her solid body.

Usage: python3 -I holo_build.py ORIG_ANIM_DIR SOLID_WALK_DIR RIG_DIR OUT_DIR [clip ...]

Her solid body (npc_sara_solid.png, redone face, slim arms drawn by the activity rig) is the
figure; below the knee she fizzes out into dithered light. Each of the 33 clips keeps the
original's timing and effects, read frame by frame from the original strip:
- the gesture: how far each original frame is from her resting pose (0) toward the clip's
  held pose (1) moves the drawn hands the same way; poses that sway or alternate (talking,
  swiping, waving) add their own small motion while held
- the eyes (open, closed, glancing), the nod and tilt of the head, the hair sway, and the
  whole figure's float up and down
- the projection: each row's brightness and tint (the scanline bands, standby's dimming,
  the reconnect flicker, the glitch colours), each row's transparency, the rows that are
  gone (dissolve, materialize) and, in the glitches, rows jogged sideways
Frames are 40 x 48 at art scale, written as 80 x 96 with each pixel a 2 x 2 block, the
figure on the same bottom-centre anchor, as the originals.
"""
import sys, os, glob, math
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import poses as P

ORIG, WALK, RIG, OUT = sys.argv[1:5]
ONLY = sys.argv[5:]
FW, FH, N = 40, 48, 24
PAD = 8 - P.OX          # the 24-wide figure sits at x 8..31 of the 40-wide frame (head centre 20.5)
NAME = "sara_solid"
HOLO = "sara_holo"
import copy
P.RIGS[HOLO] = copy.deepcopy(P.RIGS[NAME])
P.RIGS[HOLO]["d"]["L"] = (8, 21)
P.RIGS[HOLO]["d"]["R"] = (18, 21)
P.RIGS[HOLO]["hang"] = 0
P.RIGS[HOLO]["override"] = {}


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def load(path):
    return np.array(Image.open(path).convert("RGBA"))[0::2, 0::2].astype(float)


ref = load(os.path.join(ORIG, "idle_body.png"))[:, 0:FW]
HY0, HY1, HX0, HX1 = 4, 18, 12, 31


def corr(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return (a * b).sum() / d if d else 0.0


def align(f):
    best = (-2, 0, 0)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            w = f[HY0 + dy:HY1 + dy, HX0 + dx:HX1 + dx]
            r = ref[HY0:HY1, HX0:HX1]
            best = max(best, (corr(lum(w) * (w[..., 3] > 0), lum(r) * (r[..., 3] > 0)), dx, dy))
    return best


def tint_fit(f, y, ox, oy, d, x0=13, x1=29):
    """Robust per-channel linear fit from the original idle row to this frame's row y + oy."""
    if not (0 <= y < FH and 0 <= y + oy < FH):
        return None
    xs = [x for x in range(x0, x1) if ref[y, x, 3] > 0 and 0 <= x + ox + d < FW and f[y + oy, x + ox + d, 3] > 0]
    if len(xs) < 5:
        return None
    a = np.array([ref[y, x, :3] for x in xs]); b = np.array([f[y + oy, x + ox + d, :3] for x in xs])
    keep = np.ones(len(xs), bool)
    for _ in range(3):
        fit = []
        for ch in range(3):
            A = np.vstack([a[keep, ch], np.ones(keep.sum())]).T
            (m, c), *_ = np.linalg.lstsq(A, b[keep, ch], rcond=None)
            fit.append((m, c))
        pred = np.stack([a[:, ch] * fit[ch][0] + fit[ch][1] for ch in range(3)], 1)
        err = np.abs(pred - b).sum(1)
        keep = err <= max(np.percentile(err, 70), 6)
    if (err < 30).mean() < 0.6:
        return None
    # read from her head and middle only (the arms differ from the idle frame); a fit that is
    # all but plain is taken as plain
    if all(abs(m - 1) < 0.06 and abs(c) < 8 for m, c in fit):
        return [(1.0, 0.0)] * 3
    return fit


def row_alpha(f, y):
    v = f[y, :, 3]; v = v[v > 0]
    return float(np.median(v)) if len(v) else 0.0


# ---------------------------------------------------------------- reading the originals
REF_ALPHA = [row_alpha(ref, y) for y in range(FH)]
for y in range(FH):          # the idle frame's own dim scanline rows count as full
    if y < 26 and 0 < REF_ALPHA[y] < 240:
        REF_ALPHA[y] = 250.0
REF_LEVEL = 250.0
ARMBOX = (18, 36)            # rows where the original arms move


def arm_mask(f, oy):
    m = np.zeros((FH, FW), bool)
    for y in range(*ARMBOX):
        if 0 <= y + oy < FH:
            row = f[y + oy, :, 3] > 0
            row[15:26] = False       # her body
            m[y] = row
    return m


def eyes_state(f, ox, oy):
    """open / closed / look_l / look_r from the original's eye row (13)."""
    Y = 13 + oy
    if not (0 <= Y < FH):
        return "open"
    out = []
    for ex in (17, 23):
        X = ex + ox
        if not (0 <= X + 1 < FW) or f[Y, X, 3] == 0:
            return "open"
        l0, l1 = lum(f[Y, X, :3]), lum(f[Y, X + 1, :3])
        out.append(None if abs(l0 - l1) <= 25 else (0 if l0 < l1 else 1))
    if out[0] is None and out[1] is None:
        return "closed"
    if out == [1, 0]:
        return "open"
    if out == [0, 0]:
        return "look_l"
    if out == [1, 1]:
        return "look_r"
    return "open"


def read_clip(name):
    a = load(os.path.join(ORIG, f"{name}_body.png"))
    frames = [a[:, i * FW:(i + 1) * FW] for i in range(N)]
    info = []
    for f in frames:
        c, ox, oy = align(f)
        info.append(dict(c=c, ox=ox, oy=oy if c > 0.45 else 0, ox_ok=c > 0.45))
    rest = arm_mask(frames[0], info[0]["oy"])
    dists = [int((arm_mask(f, i["oy"]) ^ rest).sum()) for f, i in zip(frames, info)]
    top = max(dists) or 1
    for k, (f, i) in enumerate(zip(frames, info)):
        i["p"] = min(1.0, dists[k] / top)
        # tilting her head moves only the hair and brow above her eyes: the eyes are read
        # where they stay
        ex_ox = i["ox"] - (1 if name == "head_tilt" and i["ox"] != info[0]["ox"] else 0)
        i["eyes"] = eyes_state(f, ex_ox, i["oy"]) if i["ox_ok"] else "open"
    return frames, info


# ---------------------------------------------------------------- the gestures
# The arms hang from her shoulders: L (8, 21), R (18, 21) on the 24-wide figure, drawn whole
# (in front of her hair), so every gesture moves from the shoulder. The offsets are from the
# shoulder.
REST = dict(L=(0, 7), R=(0, 7))


def lerp(a, b, t):
    return (int(round(a[0] + (b[0] - a[0]) * t)), int(round(a[1] + (b[1] - a[1]) * t)))


def wob(i, amp=1):
    return [0, amp, 0, -amp][(i // 2) % 4]


def held(i, info):
    return info[i]["p"] > 0.85


def pose_rest(i, info):
    return dict(REST)


def toward(L, R, sway=None):
    def f(i, info):
        p = info[i]["p"]
        l, r = lerp(REST["L"], L, p), lerp(REST["R"], R, p)
        if sway and held(i, info):
            l = (l[0] + sway[0] * wob(i), l[1] + sway[1] * wob(i))
            r = (r[0] + sway[2] * wob(i + 2), r[1] + sway[3] * wob(i + 2))
        return dict(L=l, R=r)
    return f


GESTURES = {
    "idle": pose_rest, "blink": pose_rest, "hair_sway": pose_rest, "glance_left": pose_rest,
    "glance_right": pose_rest, "head_tilt": pose_rest, "nod": pose_rest,
    "materialize": pose_rest, "dissolve": pose_rest, "reconnect": pose_rest,
    "standby": pose_rest, "wake": pose_rest, "glitch_scan": pose_rest,
    "glitch_echo": pose_rest, "glitch_recover": pose_rest, "glitch_interrupt": pose_rest,
    # hands clasped together in front of her waist
    "clasp_hands": toward((4, 5), (-4, 5)),
    # both arms stretched up beside her head
    "stretch": toward((-4, -9), (4, -9)),
    # a wave beside her head
    "greeting": toward((0, 7), (6, -5), sway=(0, 0, 1, 0)),
    # one hand held out to the side, palm open
    "explain": toward((0, 7), (7, 1), sway=(0, 0, 0, 1)),
    # both hands out, moving in turn with her words
    "talk_both": toward((-6, 2), (6, 2), sway=(0, 1, 0, 1)),
    # hands out at her sides, palms up
    "shrug": toward((-6, 3), (6, 3)),
    # laughing: hands to her middle
    "laugh": toward((3, 5), (-3, 5)),
    # a hand at her chin, the other across under it
    "thinking": toward((4, 5), (-4, -2)),
    # the eight with projected objects: the hand goes where the original's hand was, so the
    # objects stay on it
    "summon_screen": toward((0, 7), (7, 0)),
    "swipe_panels": toward((0, 7), (7, 0), sway=(0, 0, 2, 0)),
    "rotate_moon": toward((0, 7), (7, 1), sway=(0, 0, 0, 1)),
    "unfold_map": toward((-3, 5), (3, 5)),
    "warning": toward((0, 7), (7, -1)),
    "conjure_teacup": toward((0, 7), (7, 1)),
    "admire_flower": toward((0, 7), (7, 1)),
    "paris_daydream": toward((0, 7), (6, 0)),
    "glitch_hand": toward((0, 7), (7, 1)),
}

# ---------------------------------------------------------------- the face and head
EYES = ((9, 12), (15, 12))   # on the 24-wide figure; two wide, three tall
COL = {k: P.hexc(v) for k, v in dict(skin="#8dd7da", lid="#c6e4de", white="#d8f8f2", pupil="#141521",
                                     iris="#2c5d6f", iris_lo="#203746", lash="#141521").items()}


def paint_eyes(cell, state, x0):
    for k, (ex, ey) in enumerate(EYES):
        x = ex + x0
        if state == "closed":
            cell[ey:ey + 3, x:x + 2] = COL["skin"]
            cell[ey + 1, x:x + 2] = COL["lash"]
        elif state in ("look_l", "look_r"):
            iris_x = x if state == "look_l" else x + 1
            white_x = x + 1 if iris_x == x else x
            cell[ey, white_x] = COL["lid"]; cell[ey, iris_x] = COL["pupil"]
            cell[ey + 1, white_x] = COL["white"]; cell[ey + 1, iris_x] = COL["iris"]
            cell[ey + 2, white_x] = COL["white"]; cell[ey + 2, iris_x] = COL["iris_lo"]


NECK = 19


def shift_rows(cell, y0, y1, dx=0, dy=0):
    """Move rows y0..y1-1 by (dx, dy); what they leave behind is filled from the row they
    came from (no holes)."""
    part = cell[y0:y1].copy()
    moved = np.roll(part, dx, axis=1)
    if dx > 0:
        moved[:, :dx] = 0
    elif dx < 0:
        moved[:, dx:] = 0
    out = cell.copy()
    out[y0:y1] = 0
    for k in range(y1 - y0):
        t = y0 + k + dy
        if 0 <= t < FH:
            m = moved[k, :, 3] > 0
            out[t][m] = moved[k][m]
    if dy > 0:      # the neck stretches down under a nodding head
        for t in range(y0, y0 + dy):
            pass
    return out


# ---------------------------------------------------------------- the fade below the knee
FADE_FROM, FADE_TO = 35, 45


def fade(cell):
    out = cell.copy()
    for y in range(FADE_FROM, FH):
        t = (y - FADE_FROM + 1) / (FADE_TO - FADE_FROM + 1)
        a = max(0.0, 1.0 - t) ** 1.1
        for x in range(FW):
            if out[y, x, 3] == 0:
                continue
            # the fizz: thinning checks as she fades (every other pixel, then fewer)
            drop = (t > 0.25 and (x + y) % 2 == 0) or (t > 0.6 and (x + 2 * y) % 4 == 1)
            if drop:
                out[y, x, 3] = 0
            else:
                out[y, x, 3] = int(round(out[y, x, 3] * a))
    return out


# ---------------------------------------------------------------- projection effects
JOG_CLIPS = {"glitch_scan", "glitch_echo", "glitch_hand", "glitch_interrupt", "glitch_recover", "reconnect"}


def project(cell, f, inf, name):
    """Copy the original frame's projection onto the rebuilt one, row by row in screen space."""
    out = cell.astype(float)
    ox, oy = inf["ox"], inf["oy"]
    alphas = [row_alpha(f, y) for y in range(FH)]
    # the frame's overall brightness: each row against the same row of the idle frame (works
    # while only part of her is there, dissolving or materializing)
    ratios = [alphas[y] / REF_ALPHA[y - oy] * REF_LEVEL for y in range(FH)
              if alphas[y] > 0 and 0 <= y - oy < FH and REF_ALPHA[y - oy] > 0]
    level = float(np.percentile(ratios, 75)) if ratios else 0.0
    for y in range(FH):
        src = y - oy                       # the original's content row on this screen row
        if not (0 <= src < FH):
            continue
        r = REF_ALPHA[src]
        m = alphas[y]
        if r > 0 and m == 0:
            factor = 0.0                   # dissolved away
        elif r > 0:
            factor = m / (r * (level / REF_LEVEL)) if level else 0.0
            factor = min(1.15, factor) * level / REF_LEVEL
        else:
            factor = level / REF_LEVEL
        d_used, fit = 0, None
        # colours are read from the body rows only; the fizz below keeps its own (its
        # brightness still follows the row's transparency)
        for d in (((0, -1, 1, -2, 2, -3, 3) if name in JOG_CLIPS else (0, -1, 1)) if src < 28 else ()):
            fit = tint_fit(f, src, ox, oy, d)
            if fit is not None:
                d_used = d
                break
        row = out[y].copy()
        if fit is not None:
            for ch in range(3):
                row[:, ch] = np.clip(row[:, ch] * fit[ch][0] + fit[ch][1], 0, 255)
        row[:, 3] = np.clip(row[:, 3] * factor, 0, 255)
        if name in JOG_CLIPS and d_used:
            row = np.roll(row, d_used, axis=0)
        out[y] = row
    out[out[:, :, 3] < 1] = 0
    return np.round(out).astype(np.uint8)


# ---------------------------------------------------------------- building a clip
def build_clip(name, walk):
    frames, info = read_clip(name)
    gesture = GESTURES[name]
    specs = []
    for i in range(N):
        g = gesture(i, info)
        specs.append(dict(bob=0, L=g["L"], R=g["R"]))
    P.ACTIVITIES["holo"] = {"d": specs}
    drawn = P.render(walk, RIG, HOLO, "holo", "d")
    # the arms are drawn whole, from the shoulder, in front of her hair
    rest_oy = info[0]["oy"]
    strip = np.zeros((FH, FW * N, 4), np.uint8)
    for i, c36 in enumerate(drawn):
        cell = np.zeros((FH, FW, 4), np.uint8)
        cell[:, PAD:PAD + P.CW] = c36[:, :FW - PAD] if PAD + P.CW > FW else c36
        x0 = 8
        inf = info[i]
        paint_eyes(cell, inf["eyes"], x0)
        if name == "nod":
            cell = shift_rows(cell, 0, NECK, 0, inf["oy"] - rest_oy)
        if name == "head_tilt" and inf["ox"] != info[0]["ox"]:
            cell = shift_rows(cell, 0, 12, inf["ox"] - info[0]["ox"], 0)
        if name == "hair_sway":
            k = int(round(inf["p"] * 2))
            if k:
                d = 1 if (i // 4) % 2 == 0 else -1
                for side in ((0, x0 + 6), (x0 + 18, FW)):
                    part = cell[14:28, side[0]:side[1]].copy()
                    cell[14:28, side[0]:side[1]] = 0
                    sh = np.roll(part, d, axis=1)
                    cell[14:28, side[0]:side[1]] = sh
        cell = fade(cell)
        lift = 0 if name == "nod" else inf["oy"] - rest_oy
        if lift:
            moved = np.zeros_like(cell)
            if lift < 0:
                moved[:FH + lift] = cell[-lift:]
            else:
                moved[lift:] = cell[:FH - lift]
            cell = moved
        cell = project(cell, frames[i], inf, name)
        strip[:, i * FW:(i + 1) * FW] = cell
    return strip


def main():
    walk = np.array(Image.open(os.path.join(WALK, f"npc_{NAME}.png")).convert("RGBA"))
    bare = os.path.join(WALK, f"npc_{NAME}_bare.png")
    P.BARE[NAME] = np.array(Image.open(bare).convert("RGBA")) if os.path.exists(bare) else None
    P.BARE[HOLO] = P.BARE[NAME]
    os.makedirs(OUT, exist_ok=True)
    names = ONLY or sorted(os.path.basename(p)[:-9] for p in glob.glob(os.path.join(ORIG, "*_body.png")))
    for n in names:
        strip = build_clip(n, walk)
        big = np.repeat(np.repeat(strip, 2, 0), 2, 1)
        Image.fromarray(big).save(os.path.join(OUT, f"{n}_body.png"))
        print(n, "ok")


main()
