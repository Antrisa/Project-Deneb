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
    "freya": dict(hem=40, rows={
        0: dict(L=(-1, 7), R=(1, 7)),
        1: dict(L=(-2, 5), R=(0, 9)),       # right leg trails: right hand forward, left back
        2: dict(L=(0, 9), R=(2, 5)),        # left leg trails
        3: dict(L=(-1, 6), R=(1, 8)),       # on their way back through
        4: dict(L=(-1, 8), R=(1, 6)),
    }),
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
        for side, elbow in (("L", -1), ("R", 1)):
            sx, sy = rig["d"][side]
            dx, dy = hands[side]
            P.draw_arm(layer, (sx, sy + bob), (sx + dx, sy + bob + dy), elbow, pal,
                       width=rig.get("arm_w", 2), thick=True)
        P.over(cell, layer)
        walk[row * FH:(row + 1) * FH, 0:FW] = cell
    Image.fromarray(walk).save(path)


if __name__ == "__main__":
    for n in sys.argv[2:]:
        build(sys.argv[1], n)
        print(n, "ok")
