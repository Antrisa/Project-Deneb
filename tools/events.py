"""Build a resident's heart-event sheet (art/npc_<id>_event.png) with the activity rig.

Usage: python3 -I events.py WALK_DIR RIG_DIR OUT_DIR name ...

Rows (the shared event rows, in the handoff's order): talk with hands (down), laugh (down),
sad or teary (down), surprised jump (down), hold out a gift (right), sit on a bench (down),
wave (down). Four frames of 36 x 48 each, like the action sheets. The arms, props and
breathing come from poses.py; this adds the faces (laughing, sad, wide-eyed), a tear, the
jump (the whole figure lifted off the floor) and the bench.
"""
import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poses as P

FH, CW, OX = P.FH, P.CW, P.OX
hexc = P.hexc

P.PROPS["gift"] = P.sprite([".ooooo.", "orrYrro", "oYYYYYo", "orrYrro", "orrYrro", ".ooooo."], P.PROP_PAL)
P.PROPS["bench"] = P.sprite(["o" * 32, "o" + "b" * 30 + "o", "o" + "w" * 30 + "o", "o" * 32,
                             ".oWo" + "." * 24 + ".oWo", ".oWo" + "." * 24 + ".oWo",
                             ".oWo" + "." * 24 + ".oWo", ".oWo" + "." * 24 + ".oWo",
                             ".oWo" + "." * 24 + ".oWo", ".oWo" + "." * 24 + ".oWo",
                             ".ooo" + "." * 24 + ".ooo"], P.PROP_PAL)

# per resident: the front eyes (x, y of the top-left of each two-wide, three-tall eye, viewer's
# left first; the outer column is x on the left eye and x + 1 on the right) and face colours
FACES = {
    "tally": dict(eyes=((9, 18), (15, 18)),
                  colours=dict(skin="#926172", lid="#d39c64", white="#f2c26e", pupil="#1d1019",
                               brow="#341d2a", tear="#93e6ea")),
    # Freya (22 Nov, for her heart events): her eyes are two by two at (10, 13) and (15, 13) with the brows on
    # row 12 (tools/fix_eyes.py); the faces here use the eye rows and the skin row under them
    "freya": dict(eyes=((10, 13), (15, 13)),
                  colours=dict(skin="#f2c29a", lid="#e8d9bd", white="#e6fbff", pupil="#1f3a32",
                               brow="#86593f", tear="#93e6ea")),
}

L_, R_ = "L", "R"
EVENTS = {
    # talking with her hands: the working pair gesturing in turn in front of her chest
    "talk": {"d": [dict(bob=b, L=l, R=r) for b, l, r in zip(
        (0, 0, 1, 0), ((-3, 3), (-4, 1), (-3, 3), (-2, 4)), ((2, 5), (3, 3), (4, 1), (3, 4)))]},
    # laughing: hands on her middle, shoulders bouncing, eyes squeezed shut
    "laugh": {"d": [dict(bob=b, L=(1, l), R=(-1, l)) for b, l in zip((0, 1, 0, 1), (6, 6, 5, 5))]},
    # sad: head bowed, hands held together low, a tear running down
    "sad": {"d": [dict(bob=1, L=(2, 7), R=(-2, 7)) for _ in range(4)]},
    # surprised: a crouch, a jump with both hands thrown up, and the landing
    "jump": {"d": [dict(bob=1, L=(-1, 5), R=(1, 5)), dict(bob=0, L=(-5, -6), R=(5, -6)),
                   dict(bob=0, L=(-5, -7), R=(5, -7)), dict(bob=1, L=(-3, 0), R=(3, 0))]},
    # holding out a gift (seen from the side; the right column is the mirror)
    "gift": {"l": [dict(bob=b, N=(n, 3), props=[("gift", "N", -3, -3, "front")])
                   for b, n in zip((0, 0, 0, 1), (-4, -6, -8, -8))]},
    # sitting on a bench: lowered onto it, hands resting on the seat either side, breathing
    "bench": {"d": [dict(bob=1, L=l, R=r, fixed=[("bench", -4, 35, "back")]) for l, r in zip(
        ((-3, 8), (-3, 7), (-3, 8), (-4, 8)), ((3, 8), (4, 8), (3, 7), (3, 8)))]},
    # waving: one hand up beside the head, swinging
    "wave": {"d": [dict(bob=b, L=(0, 6), R=(r, -9)) for b, r in zip((0, 0, 1, 1), (5, 7, 6, 8))]},
}
# face, tear row (None for no tear) and how far the whole figure is lifted, per frame
EXTRAS = {
    "laugh": [dict(face="laugh")] * 4,
    "sad": [dict(face="sad", tear=t) for t in (None, 0, 1, 2)],
    "jump": [dict(face="wow", lift=l) for l in (0, 3, 2, 1)],
}
ROWS = [("talk", "d"), ("laugh", "d"), ("sad", "d"), ("jump", "d"), ("gift", "r"), ("bench", "d"), ("wave", "d")]


def paint_face(cell, name, bob, kind, tear=None):
    f = FACES[name]
    c = {k: hexc(v) for k, v in f["colours"].items()}
    for i, (ex, ey) in enumerate(f["eyes"]):
        x, y = ex + OX, ey + bob
        outer, inner = (x, x + 1) if i == 0 else (x + 1, x)
        if kind == "laugh":
            # squeezed shut: an arch, the lash across the middle and down at the outer side
            cell[y:y + 3, x:x + 2] = c["skin"]
            cell[y + 1, x:x + 2] = c["pupil"]
            cell[y + 2, outer] = c["pupil"]
        elif kind == "sad":
            # the outer brow drops over the lid; the eye looks down
            cell[y, outer] = c["brow"]
            cell[y, inner] = c["lid"]
            cell[y + 1, inner] = c["pupil"]
            if tear is not None and i == 0:
                cell[y + 3 + tear, inner] = c["tear"]
        elif kind == "wow":
            # wide eyes: all white with a small pupil
            cell[y:y + 3, x:x + 2] = c["white"]
            cell[y + 1, inner] = c["pupil"]


def lift(cell, n):
    if not n:
        return cell
    out = np.zeros_like(cell)
    out[:FH - n] = cell[n:]
    return out


def build(walk_dir, rig_dir, out_dir, name):
    walk = np.array(Image.open(os.path.join(walk_dir, f"npc_{name}.png")).convert("RGBA"))
    bare = os.path.join(walk_dir, f"npc_{name}_bare.png")
    P.BARE[name] = np.array(Image.open(bare).convert("RGBA")) if os.path.exists(bare) else None
    sheet = np.zeros((FH * len(ROWS), CW * 4, 4), np.uint8)
    for r, (act, view) in enumerate(ROWS):
        key = f"ev_{act}"
        P.ACTIVITIES[key] = EVENTS[act]
        frames = P.render(walk, rig_dir, name, key, view)
        specs = EVENTS[act]["l" if view in "lr" else view]
        extras = EXTRAS.get(act, [{}] * 4)
        for i, cell in enumerate(frames):
            ex = extras[i]
            if ex.get("face"):
                paint_face(cell, name, specs[i].get("bob", 0), ex["face"], ex.get("tear"))
            cell = lift(cell, ex.get("lift", 0))
            sheet[r * FH:(r + 1) * FH, i * CW:(i + 1) * CW] = cell
    Image.fromarray(sheet).save(os.path.join(out_dir, f"npc_{name}_event.png"))
    print(name, "event", len(ROWS), "rows")


if __name__ == "__main__":
    WALK, RIG, OUT = sys.argv[1:4]
    os.makedirs(OUT, exist_ok=True)
    for n in sys.argv[4:]:
        build(WALK, RIG, OUT, n)
