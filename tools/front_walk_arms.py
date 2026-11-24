"""Give a resident's front walk (column 0) real arm swings, drawn with the pose rig's arms.

Usage: python3 -I front_walk_arms.py ART_DIR name ...

The painted standing frame (kept as ART_DIR/npc_<id>_bare.png the first time this runs, so the
action and event builders keep cutting from it) has its arms and resting fists taken off as in
tools/poses.py (view_body), and both arms are drawn back on with poses.draw_arm (thick), so
both sides match. Per row: 0 stand, 1 contact A, 2 contact B, 3 passing A, 4 passing B
(playback 1, 3, 2, 4). On a contact the body drops a pixel, the hand on the trailing leg's side
swings forward (toward us: lower and in) and the other swings back (higher and out); passing
rows hang at rest. The legs below the hem are the walk's own.
"""
import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poses as P

FW, FH = 24, 48
# per resident: the hem row of the standing frame (legs start below it), and the hand targets
# (dx, dy from each shoulder) per row: L and R as seen by the viewer
SWING = {
    # a straight arm hangs from the shoulder past the elbow (2 left/right of it, 4 down); the
    # forward arm bends at the elbow, its forearm coming toward us so the hand rises in front of
    # the belt; the back arm stays straight, its hand a pixel higher and out behind the hip
    "freya": dict(hem=40, elbow=(-1, 4), rows={
        0: dict(L="rest", R="rest"),
        1: dict(L="back", R="forward"),     # right leg trails: right hand forward, left back
        2: dict(L="forward", R="back"),     # left leg trails
        3: dict(L="rest", R="rest"),
        4: dict(L="rest", R="rest"),
    }, hands={"rest": (-1, 7), "forward": (1, 5), "back": (-2, 6)},
        bracer=("#86593f", "#6b3a2c")),     # her leather bracers cover the forearms
}
BOB = {0: 0, 1: 1, 2: 1, 3: 0, 4: 0}


def build(art, name):
    path = os.path.join(art, f"npc_{name}.png")
    bare_path = os.path.join(art, f"npc_{name}_bare.png")
    walk = np.array(Image.open(path).convert("RGBA"))
    if not os.path.exists(bare_path):
        Image.fromarray(walk[0:FH]).save(bare_path)          # the painted standing row
    P.BARE[name] = np.array(Image.open(bare_path).convert("RGBA"))
    rig = P.RIGS[name]
    pal = {k: P.hexc(v) for k, v in rig["pal"].items()}
    body = P.view_body(walk, None, name, "d", rig)
    cfg = SWING[name]
    hem = cfg["hem"]
    for row, hands in cfg["rows"].items():
        bob = BOB[row]
        cell = walk[row * FH:(row + 1) * FH, 0:FW].copy()
        upper = np.zeros_like(body)
        upper[bob:hem + 1 + bob] = body[0:hem + 1]
        cell[:hem + 1 + bob] = 0
        P.over(cell, upper)
        layer = np.zeros_like(cell)
        for side, sign in (("L", 1), ("R", -1)):
            sx, sy = rig["d"][side]
            dx, dy = cfg["hands"][hands[side]]
            ex, ey = cfg["elbow"]
            # the viewer's right arm is the left one mirrored (the arm is drawn from its left
            # edge, so the mirror is a pixel further in)
            hx, elx = (sx + dx, sx + ex) if sign > 0 else (sx - dx, sx - ex)
            one = np.zeros_like(layer)
            P.draw_arm(one, (sx, sy + bob), (hx, sy + bob + dy), 0, pal,
                       width=rig.get("arm_w", 2), elbow=(elx, sy + bob + ey), thick=True)
            if cfg.get("bracer"):
                lit, dark = (P.hexc(c) for c in cfg["bracer"])
                line = pal["line"]
                w = rig.get("arm_w", 2)
                fore = P.line_pts((elx, sy + bob + ey), (hx, sy + bob + dy - 1))
                top = min(y for _, y in fore)
                for (x, y) in fore:
                    for j in range(w):
                        for i in range(w):
                            yy, xx = y + j, x + i
                            if 0 <= yy < FH and 0 <= xx < FW and one[yy, xx, 3] and (one[yy, xx] != line).any():
                                one[yy, xx] = lit if yy == top else dark
            P.over(layer, one)
        P.over(cell, layer)
        walk[row * FH:(row + 1) * FH, 0:FW] = cell
    Image.fromarray(walk).save(path)


if __name__ == "__main__":
    for n in sys.argv[2:]:
        build(sys.argv[1], n)
        print(n, "ok")
