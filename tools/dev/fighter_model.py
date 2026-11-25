"""The Wandering Star, drawn from scratch (25 Nov 2026, Zachary: "just generate the player ship from scratch").

A small 3D model of the fighter (signed distance fields: a pointed fuselage, a bubble canopy, swept delta wings,
twin engine pods with nozzles, canted tail fins), lit and cut into flat tones, so every view the prologue needs comes
from one ship: whole in the ambush, battered after Ivan's salvo (her starboard wing sheared off, a breach in her
back), the wing tumbling away, torn in two for the blind jump, and her front half as a wreck in the crash site, all
the same ship from the same model. The look follows the main menu's fighter (cream hull, orange stripes, a teal
canopy, grey engine pods), drawn to the art style guide: master palette only (tools/dev/prologue_art.py PAL), lit
from the top left, 3-5 tones a material, a #5b332d outline, no noise or dithering.

render(view, parts) -> (Canvas, info): view sets the size and the pose; parts picks whole / battered / front half /
back half / the wing piece. info has the engine ports' and the cut's screen positions.
Run it to see the views: python3 tools/dev/fighter_model.py (writes /tmp/look/fighter_model.png).
"""
import math
import os
import sys

import numpy as np
from scipy.ndimage import binary_erosion

sys.path.insert(0, os.path.dirname(__file__))
from prologue_art import C, Canvas, OUT, check, despeckle, edge  # noqa: E402

# ---------------------------------------------------------------- the model (units: about a pixel at the panel's size)
# x forward (the nose), y to port (left), z up. She is 62 long and 56 across the wings.
NOSE, TAIL = 28.0, -27.0
WING = [(9.0, 4.5), (-11.0, 26.0), (-19.5, 27.0), (-21.0, 4.5)]      # port wing outline (x, y); starboard mirrors it
POD_Y, POD_Z, POD_R, POD_FRONT, POD_BACK = 8.2, -1.0, 3.9, -4.0, -28.5
WING_CUT = -13.5             # the battered ship's starboard wing ends here (y), raggedly


def fuselage_size(x):
    """Half-width and half-height of the fuselage at x: a long pointed nose, a straight middle, a tucked tail."""
    w = np.where(x > 8, 6.0 * np.clip(1 - ((x - 8) / (NOSE - 8)), 0, 1) ** .6, 6.0)
    w = np.where(x < -18, 6.0 - (-18 - x) * .2, w)
    return np.maximum(w, .05), np.maximum(w * .74, .05)


def sd_fuselage(p):
    x, y, z = p
    w, h = fuselage_size(x)
    q = np.sqrt((y / w) ** 2 + (z / h) ** 2)
    d = (q - 1) * np.minimum(w, h) * .85
    return np.maximum(d, np.maximum(x - NOSE, TAIL - x))


def sd_ellipsoid(p, c, r):
    q = [(p[i] - c[i]) / r[i] for i in range(3)]
    k = np.sqrt(q[0] ** 2 + q[1] ** 2 + q[2] ** 2)
    return (k - 1) * min(r) * .9


def sd_poly2(px, py, pts):
    """Signed distance to a 2D convex-ish polygon (negative inside)."""
    d = np.full(px.shape, 1e9)
    s = np.ones(px.shape)
    n = len(pts)
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        wx, wy = px - ax, py - ay
        t = np.clip((wx * ex + wy * ey) / (ex * ex + ey * ey), 0, 1)
        dx, dy = wx - ex * t, wy - ey * t
        d = np.minimum(d, dx * dx + dy * dy)
        c1 = py >= ay
        c2 = py < by
        c3 = ex * wy > ey * wx
        flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
        s = np.where(flip, -s, s)
    return s * np.sqrt(d)


def sd_wings(p, side):
    """One wing (side +1 port, -1 starboard): a thin plate with a little dihedral, thicker at the root."""
    x, y, z = p
    ya = y * side
    d2 = sd_poly2(x, ya, WING)
    zc = .1 * np.clip(ya - 4, 0, None) - .3
    t = .95 - .02 * np.clip(ya - 4, 0, None)
    dz = np.abs(z - zc) - t
    return np.maximum(d2, dz) * .9


def sd_pod(p, side):
    x, y, z = p
    r = np.hypot(y - side * POD_Y, z - POD_Z)
    front = np.clip(x - (POD_FRONT - 6), 0, None)               # the front rounds off over its last 6 units
    rad = POD_R * np.sqrt(np.clip(1 - (front / 6.5) ** 2, 0, 1))
    d = r - rad
    return np.maximum(d, np.maximum(x - POD_FRONT, POD_BACK - x)) * .9


def sd_fin(p, side):
    """A tail fin on each pod, canted outward."""
    x, y, z = p
    cy, cz = side * POD_Y, POD_Z + POD_R * .7
    ang = side * .35
    u = (y - cy) * math.cos(ang) - (z - cz) * math.sin(ang)        # across the fin
    v = (y - cy) * math.sin(ang) + (z - cz) * math.cos(ang)        # up the fin
    d2 = sd_poly2(x, v, [(-27.5, 0.0), (-18.0, 0.0), (-24.5, 6.4), (-28.0, 6.4)])
    return np.maximum(d2, np.abs(u) - .55) * .9


PARTS = ("fuselage", "canopy", "spine", "wing_p", "wing_s", "pod_p", "pod_s", "fin_p", "fin_s")


PIECE_CENTRE = (-12.0, -20.0, .8)        # the middle of the wing piece Ivan shears off


def spun(p, mode):
    """The wing piece tumbling: model points turned about its middle by mode["spin"] (two angles)."""
    a, b = mode["spin"]
    ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
    Rm = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]]) @ np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]])
    c = np.array(PIECE_CENTRE)[:, None]
    return Rm.T @ (p - c) + c


def sd_parts(p, mode):
    if mode.get("spin"):
        p = spun(p, mode)
    d = {"fuselage": sd_fuselage(p), "canopy": sd_ellipsoid(p, (11.0, 0, 3.6), (8.6, 4.0, 3.1)),
         "spine": sd_ellipsoid(p, (-4.0, 0, 2.6), (14.0, 3.6, 2.6)),
         "wing_p": sd_wings(p, 1), "wing_s": sd_wings(p, -1), "pod_p": sd_pod(p, 1), "pod_s": sd_pod(p, -1),
         "fin_p": sd_fin(p, 1), "fin_s": sd_fin(p, -1)}
    x, y, z = p
    if mode.get("wing_off"):                       # the battered ship: the starboard wing ends in a torn edge
        rag = WING_CUT + 1.3 * np.sin(x * .9) + .6 * np.sin(x * 2.1 + 1)
        d["wing_s"] = np.maximum(d["wing_s"], rag - y)
    if mode.get("piece"):                          # only the part that was sheared off
        rag = WING_CUT + 1.3 * np.sin(x * .9) + .6 * np.sin(x * 2.1 + 1)
        return {"wing_s": np.maximum(sd_wings(p, -1), y - rag)}
    cut = mode.get("cut")
    if cut is not None:                            # torn in two across her body: keep the front or the back
        cx, keep = cut
        rag = cx + 1.6 * np.sin(y * .7 + 1.3) + .9 * np.sin(z * 1.1) + .5 * np.sin(y * 1.9)
        for k in d:
            d[k] = np.maximum(d[k], rag - x) if keep == "front" else np.maximum(d[k], x - rag)
    return d


# ---------------------------------------------------------------- the view
def rot(roll, pitch, yaw, elev):
    cr, sr, cp, sp, cy, sy = math.cos(roll), math.sin(roll), math.cos(pitch), math.sin(pitch), math.cos(yaw), math.sin(yaw)
    R = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Pm = np.array([[cp, 0, -sp], [0, 1, 0], [sp, 0, cp]])
    Y = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    se, ce = math.sin(elev), math.cos(elev)
    Cm = np.array([[1, 0, 0], [0, -se, -ce], [0, -ce, se]])       # rows: screen right, screen down, toward you
    return Cm @ Y @ Pm @ R


BATTERED_MODE = {"wing_off": True, "breach": True}     # after Ivan's salvo
PANEL = dict(scale=1.75, roll=.1, pitch=.05, yaw=math.radians(30), elev=math.radians(70), size=(108, 96), dx=6, dy=-12)

TONES = {      # dark to light; the last is only for the brightest glint
    "hull": [C("cream", 0), C("cream", 1), C("cream", 2), C("cream", 3), C("cream", 4)],
    "stripe": [C("copper", 1), C("copper", 1), C("copper", 2), C("copper", 3), C("copper", 4)],
    "glass": [C("teal", 0), C("teal", 1), C("teal", 2), C("teal", 3), C("teal", 4)],
    "pod": [C("rock", 0), C("rock", 1), C("rock", 2), C("rock", 3), C("rock", 4)],
    "nozzle": [C("ink", 0), C("ink", 0), C("ink", 0), C("ink", 1), C("ink", 1)],
    "torn": [C("rock", 0), C("rock", 0), C("rock", 1), C("rock", 1), C("rock", 2)],
    "breach": [C("ink", 0), C("ink", 0), C("ink", 0), C("rock", 0), C("rock", 0)],
}
LIGHT = np.array([-.48, -.62, .62])
LIGHT /= np.linalg.norm(LIGHT)


def project(M, view, p):
    """A model point to the picture's pixels."""
    c = M @ np.array(p, float)
    W, H = view["size"]
    return (W / 2 + c[0] * view["scale"] + view.get("dx", 0), H / 2 + c[1] * view["scale"] + view.get("dy", 0))


def render(view=PANEL, mode=None, nozzle_glow=True):
    mode = mode or {}
    M = rot(view["roll"], view["pitch"], view["yaw"], view["elev"])
    W, H = view["size"]
    s = view["scale"]
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    sx = (xs + .5 - W / 2 - view.get("dx", 0)) / s
    sy = (ys + .5 - H / 2 - view.get("dy", 0)) / s
    n = W * H
    cam = np.stack([sx.ravel(), sy.ravel(), np.full(n, 60.0)])
    dirc = np.array([0, 0, -1.0])
    o = M.T @ cam
    dv = M.T @ dirc
    t = np.zeros(n)
    hit = np.zeros(n, bool)
    alive = np.ones(n, bool)
    for _ in range(220):
        idx = np.nonzero(alive)[0]
        if len(idx) == 0:
            break
        p = o[:, idx] + dv[:, None] * t[idx]
        d = np.min(np.stack(list(sd_parts(p, mode).values())), axis=0)
        h = d < .02
        hit[idx[h]] = True
        alive[idx[h]] = False
        t[idx[~h]] += np.maximum(d[~h] * .75, .015)
        far = t > 120
        alive &= ~far
    idx = np.nonzero(hit)[0]
    p = o[:, idx] + dv[:, None] * t[idx]
    parts = sd_parts(p, mode)
    names = list(parts)
    pm = spun(p, mode) if mode.get("spin") else p          # where on her each hit is, for her paint
    which = np.argmin(np.stack([parts[k] for k in names]), axis=0)
    eps = .05
    nrm = np.zeros((3, len(idx)))
    for a in range(3):
        e = np.zeros((3, 1))
        e[a] = eps
        dp = np.min(np.stack(list(sd_parts(p + e, mode).values())), axis=0)
        dm = np.min(np.stack(list(sd_parts(p - e, mode).values())), axis=0)
        nrm[a] = dp - dm
    nrm /= np.linalg.norm(nrm, axis=0) + 1e-9
    ncam = M @ nrm
    lum = np.clip(ncam.T @ LIGHT, -1, 1)
    x, y, z = pm
    mat = np.array(["hull"] * len(idx), dtype=object)
    part = np.array(names, dtype=object)[which]
    mat[part == "canopy"] = "glass"
    mat[np.isin(part, ["pod_p", "pod_s"])] = "pod"
    # her orange: a band across each wing, two stripes down her back, a ring on the nose and on each pod
    wing = np.isin(part, ["wing_p", "wing_s"])
    ya = np.abs(y)
    lead = (x - 7.0) * 23.0 / 21.0 + (ya - 4.0)          # along the leading edge's normal (roughly)
    band = wing & (np.abs((x - 9.0) + (ya - 4.5) * 20.0 / 21.5 + 9.0) < 2.4)
    mat[band] = "stripe"
    back = np.isin(part, ["fuselage", "spine"])
    mat[back & (np.abs(np.abs(y) - 2.6) < .9) & (x > -22) & (x < 2) & (z > 0)] = "stripe"
    mat[back & (x > 18.5) & (x < 21.0)] = "stripe"
    pod = np.isin(part, ["pod_p", "pod_s"])
    mat[pod & (x > -12.5) & (x < -10.0)] = "stripe"
    mat[np.isin(part, ["fin_p", "fin_s"]) & (x < -25.5)] = "stripe"
    # the engine nozzles: the pods' back faces
    rr = np.hypot(np.abs(y) - POD_Y, z - POD_Z)
    nozzle = pod & (x < POD_BACK + .4) & (rr < POD_R - .9)
    mat[nozzle] = "nozzle"
    scorch = np.zeros(len(idx), bool)
    if mode.get("cut") is not None and mode.get("scorch"):   # blackened back from the tear (the wreck)
        cx_, _ = mode["cut"]
        rag_ = cx_ + 1.6 * np.sin(y * .7 + 1.3) + .9 * np.sin(z * 1.1) + .5 * np.sin(y * 1.9)
        scorch |= (x - rag_ < 4.5 + 1.5 * np.sin(y * 1.3 + z)) & (x - rag_ > .3)
    if mode.get("breach"):                                # the battered ship: a hole torn in her back, ribs across
        e = np.sqrt(((x + 4.5) / 5.2) ** 2 + ((y + 1.4) / 2.8) ** 2) - .18 * np.sin(np.arctan2(y + 1.4, x + 4.5) * 5)
        top = np.isin(part, ["fuselage", "spine"]) & (z > .5)
        hole = top & (e < 1)
        rib = hole & (np.abs(((x + 4.5) % 2.6) - 1.3) < .35)
        mat[hole] = "breach"
        mat[rib] = "torn"
        scorch = top & (e >= 1) & (e < 1.7)
    cut = mode.get("cut")
    torn_face = np.zeros(len(idx), bool)
    if cut is not None:                                   # the cut face, and the ribs in it
        cx, keep = cut
        rag = cx + 1.6 * np.sin(y * .7 + 1.3) + .9 * np.sin(z * 1.1) + .5 * np.sin(y * 1.9)
        torn_face = np.abs(x - rag) < .25
        mat[torn_face] = "torn"
    if mode.get("wing_off"):
        rag = WING_CUT + 1.3 * np.sin(x * .9) + .6 * np.sin(x * 2.1 + 1)
        mat[(part == "wing_s") & (np.abs(y - rag) < .3)] = "torn"
    # light into tones: the canopy gets a glint, everything 3-4 steps
    tone = np.digitize(lum, view.get("bands", [.05, .42, .74, .95])) - scorch.astype(int) * 2
    out = np.zeros((H * W, 4), np.uint8)
    for m_name, ramp in TONES.items():
        sel = mat == m_name
        out[idx[sel]] = np.array(ramp)[np.clip(tone[sel], 0, len(ramp) - 1)]
    out[idx[scorch & (mat == "stripe")]] = C("copper", 1)
    cv = Canvas(W, H)
    cv.a = out.reshape(H, W, 4)
    depth = np.full(H * W, -1e9)
    depth[idx] = 60.0 - t[idx]
    depth = depth.reshape(H, W)
    solid = cv.a[:, :, 3] > 0
    partmap = np.full(H * W, -1)
    partmap[idx] = which
    partmap = partmap.reshape(H, W)
    # lines inside her where one part stands in front of another, drawn on the far side
    line = np.zeros((H, W), bool)
    for dy_, dx_ in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nd = np.roll(np.roll(depth, dy_, 0), dx_, 1)
        npart = np.roll(np.roll(partmap, dy_, 0), dx_, 1)
        line |= solid & (nd - depth > 2.2) & (npart >= 0) & (npart != partmap)
    cv.paint(line, OUT)
    cv.paint(edge(solid), OUT)
    despeckle(cv, solid & ~edge(solid) & ~line, passes=2)
    # the ports glowing when she's under power
    matmap = np.full(H * W, "", dtype=object)
    matmap[idx] = mat
    info = {"mat": matmap.reshape(H, W), "ports": [project(M, view, (POD_BACK, sd * POD_Y, POD_Z)) for sd in (1, -1)],
            "axis": tuple((M @ np.array([1.0, 0, 0]))[:2] / np.linalg.norm((M @ np.array([1.0, 0, 0]))[:2])),
            "nose": project(M, view, (NOSE, 0, 0)), "M": M}
    if nozzle_glow and not mode.get("piece"):
        noz = np.zeros(H * W, bool)
        noz[idx[nozzle & ~torn_face]] = True
        noz = noz.reshape(H, W) & ~edge(solid)
        core = noz & binary_erosion(noz, border_value=0)
        cv.paint(noz, C("copper", 2))
        cv.paint(core, C("copper", 4))
        cv.paint(core & binary_erosion(core, border_value=0), C("brass", 4))
    return cv, info


def piece_frames(view=PANEL, n=6, side=52):
    """The sheared-off wing tumbling, n frames (side x side), turning a full round over them; and where on her
    picture the first frame's top-left sits (her pixels)."""
    M = rot(view["roll"], view["pitch"], view["yaw"], view["elev"])
    cx, cy = project(M, view, PIECE_CENTRE)
    frames = []
    for k in range(n):
        a = 2 * math.pi * k / n
        # the piece's middle at the frame's middle
        v = dict(view, size=(side, side), dx=view.get("dx", 0) + side / 2 - cx + (view["size"][0] - side) / 2,
                 dy=view.get("dy", 0) + side / 2 - cy + (view["size"][1] - side) / 2)
        frames.append(render(v, {"piece": True, "spin": (a, a * .5)})[0])
    return frames, (int(round(cx - side / 2)), int(round(cy - side / 2)))


def views():
    """Every picture of her the prologue uses, for a look."""
    from PIL import Image
    shots = [render()[0], render(mode={"wing_off": True, "breach": True}, nozzle_glow=False)[0],
             render(mode={"piece": True})[0], render(mode={"cut": (-3.0, "front"), "wing_off": True, "breach": True})[0],
             render(mode={"cut": (-3.0, "back"), "wing_off": True}, nozzle_glow=False)[0]]
    W, H = PANEL["size"]
    sheet = Image.new("RGBA", (W * len(shots), H), (14, 12, 30, 255))
    for i, c in enumerate(shots):
        sheet.alpha_composite(c.image(), (i * W, 0))
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save("/tmp/look/fighter_model.png")
    for c in shots:
        check(c, "fighter")


if __name__ == "__main__":
    views()
