"""Rebuild the passing poses (rows 3 and 4) of resident profile walks.

Usage: python3 -I fix_npc_passing.py SRC_ART_DIR OUT_ART_DIR name[:hip] ...

The painted contact strides and everything above the hips of each passing frame (arms, bob)
are kept. From the hips down the passing frame takes the standing pose, whose legs stand
together, and the lifted boot tucks up behind the planted calf so only its heel shows
(in shade for the far leg in passing A, in full colour for the near leg in passing B).
Right-facing frames are mirrors of the left.
"""
import sys, os
import numpy as np
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
FW, FH, LEFT = 24, 48, 2
LIFT, TUCK, DARK = 2, 3, 0.72


def span(c, y):
    xs = np.where(c[y, :, 3] > 0)[0]
    return (int(xs.min()), int(xs.max())) if len(xs) else None


def width(c, y):
    s = span(c, y)
    return 0 if s is None else s[1] - s[0] + 1


def foot_top(s):
    """First row of the feet: walking up from the sole until the profile narrows to the ankle."""
    for y in range(45, 36, -1):
        if width(s, y - 1) < width(s, y) - 1 or (span(s, y - 1) and span(s, y) and span(s, y - 1)[0] > span(s, y)[0]):
            return y
    return 42


def hip_row(stand, frame):
    """Where the painted passing frame's legs start to differ from the standing legs."""
    for y in range(28, 46):
        if width(frame, y) and width(frame, y) < width(stand, y) - 2:
            # step up while the rows still differ (the top of the thin leg)
            while y > 28 and not np.array_equal(frame[y - 1], stand[y - 1]):
                y -= 1
            return y
    return 38


def build(stand, frame, row, hip):
    out = frame.copy()
    out[hip:] = 0
    ft = foot_top(stand)
    # the lifted boot, behind everything
    heel = np.zeros_like(stand)
    for y in range(ft, 46):
        for x in range(FW):
            if stand[y, x, 3] and 0 <= x + TUCK < FW:
                heel[y - LIFT, x + TUCK] = stand[y, x]
    if row == 3:
        m = heel[:, :, 3] > 0
        heel[m, :3] = np.round(heel[m, :3] * DARK).astype(heel.dtype)
    legs = stand.copy()
    legs[:hip] = 0
    m = heel[:, :, 3] > 0
    out[m] = heel[m]
    m = legs[:, :, 3] > 0
    out[m] = legs[m]
    # anything the painted frame drew above the hips stays on top (hands, coat tails)
    top = frame.copy(); top[hip:] = 0
    m = top[:, :, 3] > 0
    out[m] = top[m]
    return out


for arg in sys.argv[3:]:
    name, _, h = arg.partition(":")
    a = np.array(Image.open(os.path.join(SRC, f"npc_{name}.png")).convert("RGBA"))
    stand = a[0:FH, LEFT * FW:(LEFT + 1) * FW].copy()
    for row in (3, 4):
        frame = a[row * FH:(row + 1) * FH, LEFT * FW:(LEFT + 1) * FW].copy()
        hip = int(h) if h else hip_row(stand, frame)
        new = build(stand, frame, row, hip)
        a[row * FH:(row + 1) * FH, LEFT * FW:(LEFT + 1) * FW] = new
        a[row * FH:(row + 1) * FH, (LEFT + 1) * FW:(LEFT + 2) * FW] = new[:, ::-1]
        print(name, row, "hip", hip, "feet", foot_top(stand))
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(a).save(os.path.join(OUT, f"npc_{name}.png"))
