"""Shared pose system: draws every resident's activities in all four directions from rig parts.

Usage: python3 -I poses.py WALK_DIR RIG_DIR OUT_DIR name ...

For each resident the rig gives, per view (d front, u back, l side facing left):
  - a body: the standing frame with the arms taken off and the torso edge closed;
  - shoulder points and the resting hand points;
  - sleeve and skin colours.
Each activity is defined once below as four frames of hand targets (relative to the
shoulders), a body bob, and props. Arms are drawn from shoulder to elbow to hand as outlined
sleeves with a mitten hand, so every resident's arms match their own colours. Right-facing
rows are mirrors of the left. The head and face always come from the standing frame.

Output: OUT_DIR/npc_<id>_act.png, 144 wide, one row per "action facing" label in ROWS, four
36 x 48 frames per row, feet on row 45 at the centre.
"""
import sys, os, math
import numpy as np
from PIL import Image

FW, FH, CW = 24, 48, 36
OX = (CW - FW) // 2

# ----------------------------------------------------------------------------- drawing


def hexc(h, a=255):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [a], dtype=np.uint8)


def put(img, x, y, c):
    if 0 <= x < img.shape[1] and 0 <= y < img.shape[0]:
        img[y, x] = c


def line_pts(p0, p1):
    (x0, y0), (x1, y1) = p0, p1
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(int(round(x0 + (x1 - x0) * i / n)), int(round(y0 + (y1 - y0) * i / n))) for i in range(n + 1)]


def stamp(img, pts, r, c):
    for (x, y) in pts:
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                put(img, x + dx, y + dy, c)


def draw_arm(img, shoulder, hand, elbow_side, pal, width=2, elbow=None):
    """Shoulder to elbow to hand. elbow_side pushes the elbow sideways (+x or -x) so the arm
    bends naturally. Sleeve two pixels wide inside a one-pixel outline, mitten hand."""
    sx, sy = shoulder
    hx, hy = hand
    mx, my = (sx + hx) / 2, (sy + hy) / 2
    length = math.hypot(hx - sx, hy - sy)
    reach = 8.0
    bend = max(0.0, (reach - length) / 2.0)
    ex, ey = int(round(mx + elbow_side * bend)), int(round(my + 0.5))
    if elbow is not None:   # an explicit elbow: upper arm and forearm as two straight pieces
        ex, ey = elbow
    upper = line_pts((sx, sy), (ex, ey))
    lower = line_pts((ex, ey), (hx, hy - 1))
    # a sleeve four pixels wide: outline, two pixels of cloth (lit on the left, the light
    # comes from the top left), outline
    layer = np.zeros_like(img)
    for (x, y) in upper + lower:
        for dx in range(-1, width + 1):
            put(layer, x + dx, y - 1, pal["line"])
            put(layer, x + dx, y + 1, pal["line"])
            put(layer, x + dx, y, pal["line"])
    for (x, y) in upper + lower:
        put(layer, x, y, pal["sleeve_hi"])
        for dx in range(1, width):
            put(layer, x + dx, y, pal["sleeve"])
    # mitten: two by two of skin (with a shaded corner) in a rounded outline
    for dy in range(-1, 3):
        for dx in range(-1, 3):
            corner = dx in (-1, 2) and dy in (-1, 2)
            if not corner:
                put(layer, hx + dx, hy + dy, pal["line"])
    put(layer, hx, hy, pal["skin_hi"])
    put(layer, hx + 1, hy, pal["skin"])
    put(layer, hx, hy + 1, pal["skin"])
    put(layer, hx + 1, hy + 1, pal["skin_lo"])
    over(img, layer)


def over(dst, src):
    m = src[:, :, 3] > 0
    dst[m] = src[m]


def darken(c, k=0.75):
    o = c.copy(); m = o[:, :, 3] > 0
    o[m, :3] = np.round(o[m, :3] * k).astype(o.dtype)
    return o


def sprite(rows, pal):
    h, w = len(rows), max(len(r) for r in rows)
    img = np.zeros((h, w, 4), dtype=np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != "." and ch != " ":
                img[y, x] = hexc(pal[ch])
    return img


def blit(dst, spr, x, y):
    h, w = spr.shape[:2]
    for j in range(h):
        for i in range(w):
            if spr[j, i, 3]:
                put(dst, x + i, y + j, spr[j, i])


# ----------------------------------------------------------------------------- props

PROP_PAL = {"r": "#d65a4a", "R": "#9c3a30", "Y": "#b08a3a", "o": "#1f2b2e", "c": "#9fd3cf", "t": "#4f8f8c", "T": "#2f5e5c", "w": "#b07a46",
            "W": "#7a4f2c", "g": "#7fb85a", "G": "#4a7d36", "y": "#e6c36a", "b": "#d9a066",
            "B": "#a86f3c", "s": "#93e6ea", "m": "#8f969c", "M": "#5d646b", "l": "#c5ccd2"}
PROPS = {
    "bowl": sprite([".ooooo.", "occcccо".replace("о", "o"), "ottttto", ".oTTTo."], PROP_PAL),
    "spoon": sprite(["w", "w", "w", "W"], PROP_PAL),
    "food": sprite([".oo.", "obbo", "oBBo", ".oo."], PROP_PAL),
    "herb": sprite([".g.", "gGg", ".G.", ".W."], PROP_PAL),
    "can_side": sprite(["..oooo....", ".olllmo...", "ommmmmmooo", "oMMMMMo.ml", ".ooooo...."], PROP_PAL),
    "can_front": sprite([".oooo.", "olllmo", "ommmmo", "oMMMMo", ".oooo."], PROP_PAL),
    "drop": sprite(["s", "s"], PROP_PAL),
    # a frying pan seen from the front (handle out to the left, where the hand holds it) and
    # from the side (handle to the right), a morsel tossed out of it, and a spatula
    "pan": sprite(["...oooooo.", "oooMmmmmMo", "...oMMMMo."], PROP_PAL),
    "pan_side": sprite([".oooooo...", "oMmmmmMooo", ".oMMMMo..."], PROP_PAL),
    "morsel": sprite(["yb", "bB"], PROP_PAL),
    "spatula": sprite(["mm", "ll", ".W", ".W"], PROP_PAL),
    # bar things: a rag, a glass with a drink, a bottle upright and tipped, the pour
    "rag": sprite(["llll", "mlml"], PROP_PAL),
    "glass": sprite(["o..o", "oyyo", "oyyo", ".oo."], PROP_PAL),
    "glass_low": sprite(["o..o", "o..o", "oyyo", ".oo."], PROP_PAL),
    "bottle": sprite([".o.", "oto", "oto", "oTo", "oTo", ".o."], PROP_PAL),
    "bottle_tip": sprite(["...oo", "..oto", ".oTo.", "oTo..", "oo..."], PROP_PAL),
    "pour": sprite(["y", "y"], PROP_PAL),
    # workshop: hammer (head up), a plank, a sketch pad and a pencil
    "hammer": sprite(["MMM", "oWo", ".W.", ".W."], PROP_PAL),
    "plank": sprite(["wwwwwww", "WWWWWWW"], PROP_PAL),
    "pad": sprite(["ooooo", "ollll", "olmll", "ollll", "ooooo"], PROP_PAL),
    "pencil": sprite(["y", "y", "W"], PROP_PAL),
    # a valve wheel, its spokes turning (+ then x); side on it is an upright ring
    "valve": sprite([".ooooo.", "o..m..o", "o..m..o", "ommMmmo", "o..m..o", "o..m..o", ".ooooo."], PROP_PAL),
    "valve_x": sprite([".ooooo.", "om...mo", "o.m.m.o", "o..M..o", "o.m.m.o", "om...mo", ".ooooo."], PROP_PAL),
    "valve_side": sprite([".o.", "omo", "omo", "oMo", "omo", "omo", ".o."], PROP_PAL),
    # a crayon, a sheet of paper, a ball
    "crayon": sprite(["r", "R"], PROP_PAL),
    "paper": sprite(["oooo", "ollo", "ollo", "oooo"], PROP_PAL),
    "ball": sprite([".r.", "rRr", ".r."], PROP_PAL),
    # a ledger (a brown book open on a pale page), a mug of coffee
    "ledger": sprite(["oooooo", "oWllWo", "oWllWo", "oWllWo", "oooooo"], PROP_PAL),
    # a letter, and a small wooden crate
    "letter": sprite(["ooooo", "ollyo", "ooooo"], PROP_PAL),
    "crate": sprite(["ooooooo", "owwwwwo", "owWwWwo", "owwwwwo", "ooooooo"], PROP_PAL),
    # a suitcase hanging by its handle, and a desk bell
    "suitcase": sprite([".ooo.", ".o.o.", "ooooooo", "oWWyWWo", "oWWWWWo", "oWWWWWo", "ooooooo"], PROP_PAL),
    "bell": sprite(["..o..", ".oyo.", "oyyyo", "ooooo"], PROP_PAL),
    # a length of rope being knotted
    "rope": sprite([".oo.", "oWWo", "oWWo", ".oWo", "..o."], PROP_PAL),
    # flickers of firelight on warming hands
    "ember": sprite(["y.", ".s"], PROP_PAL),
    "ember2": sprite([".y", "s."], PROP_PAL),
    # a spear held upright: the blade at the top, the shaft below (held about two thirds down)
    "spear": sprite([".l.", "mlm", "mlm", ".m."] + [".W."] * 19, PROP_PAL),
    # a spyglass: seen end-on over the eye, from the side tilted up, from the side level, and
    # from behind its far end showing above the hat
    "spy_d": sprite([".oo.", "oyyo", "oMMo", ".oo."], PROP_PAL),
    "spy_up": sprite(["....oo", "...oyo", "..oMo.", ".oMo..", "oMo...", "oo...."], PROP_PAL),
    "spy_h": sprite(["oooooo", "yMMMMo", "oooooo"], PROP_PAL),
    "spy_back": sprite([".oo.", "oMMo", "oMMo", "oyyo"], PROP_PAL),
    # a pickaxe: the head across the top of the handle
    "pick": sprite(["MMMMM", "M.W.M", "..W..", "..W..", "..W.."], PROP_PAL),
    # a welding torch (nozzle up, from the hand) and its sparks, two ways
    "torch": sprite(["m", "M", "o", "W"], PROP_PAL),
    "sparks1": sprite(["y.y", ".s.", "y.."], PROP_PAL),
    "sparks2": sprite([".y.", "s.y", ".y."], PROP_PAL),
    # a console desk: from the front a panel of lit keys in front of her, from behind the
    # desk edge showing either side of her, from the side its end
    "console_front": sprite(["oooooooooooooooo", "olmglmlmslmlmgmo", "oMMMMMMMMMMMMMMo", "oooooooooooooooo"], PROP_PAL),
    "console_back": sprite(["o" * 30, "o" + "lmlmsmlmlmgmlmlmlmsmlmlmgmlm" + "o", "o" + "M" * 28 + "o", "o" * 30], PROP_PAL),
    "console_side": sprite(["oooooo", "olmglo", "oMMMMo", "oooooo"], PROP_PAL),
    # a jar of supplies: a wooden lid over a glass of something teal
    "jar": sprite([".ooo.", "oWWWo", "occto", "otTTo", ".ooo."], PROP_PAL),
    # Sesska's hand loom seen from the front (beam, warp threads, the cloth growing at the
    # bottom), seen from the side (the frame edge on), and her shuttle
    "loom": sprite([".oooooooooooo.", "owwwwwwwwwwwwo", "oWWWWWWWWWWWWo", "oy.y.y.y.y.y.o",
                    "o.y.y.y.y.y.yo", "oy.y.y.y.y.y.o", "orrrrrrrrrrrro", "oRRRRRRRRRRRRo",
                    "owwwwwwwwwwwwo", ".o..........o."], PROP_PAL),
    "loom_side": sprite(["ooo", "owo", "oWo", "oyo", "oyo", "oyo", "oro", "oRo", "owo", "o.o"], PROP_PAL),
    "shuttle": sprite(["oooo", "obbo", "oooo"], PROP_PAL),
    # a spanner, a chess piece
    "spanner": sprite(["m.m", "mmm", ".M.", ".M.", ".M."], PROP_PAL),
    "piece": sprite([".o.", "olo", "olo", "ooo"], PROP_PAL),
    # a medical scanner with its light
    "scanner": sprite(["oooo", "ossm", "oooo"], PROP_PAL),
    # a blade: upright, and level pointing ahead (side view, to the left); a cloth
    "blade_v": sprite(["l", "l", "l", "l", "m", "W"], PROP_PAL),
    "blade_h": sprite(["llllmW"], PROP_PAL),
    "blade_flat": sprite(["Wmllllll"], PROP_PAL),
    # a toy robot, a hand-held game with its glow
    "toy": sprite([".oo.", "oMMo", "omMo", "o..o"], PROP_PAL),
    "device": sprite(["oooo", "ossо".replace("о", "o"), "oooo"], PROP_PAL),
    "glow": sprite(["s.s", ".s."], PROP_PAL),
    "glow2": sprite([".s.", "s.s"], PROP_PAL),
    # a broom: handle and straw head, upright and swept to one side
    "broom": sprite([".W.", ".W.", ".W.", ".W.", ".W.", ".W.", "oyo", "yYy", "yYy"], PROP_PAL),
    "broom_tilt": sprite(["...W", "...W", "..W.", "..W.", ".W..", ".W..", "oyo.", "yYy.", "yYy."], PROP_PAL),
    "mug": sprite(["oooo.", "obbooo", "oBBo.o", "oBBoo.", "oooo.."], PROP_PAL),
    "valve_side2": sprite([".o.", "olo", "omo", "oMo", "omo", "olo", ".o."], PROP_PAL),
}

# ----------------------------------------------------------------------------- activities
# Hand targets are (dx, dy) from each shoulder; for the front and back views the two arms
# are "L" (viewer's left) and "R"; for the side view "N" is the near arm and "F" the far arm.
# Props: (name, which hand it follows, dx, dy, layer) with layer "front" or "back".
# Every activity has four frames that differ, as the game's test requires.

REST = {
    "d": [dict(bob=0, L=(-1, 7), R=(1, 7)), dict(bob=0, L=(-1, 7), R=(1, 6)),
          dict(bob=1, L=(-1, 7), R=(1, 7)), dict(bob=1, L=(-1, 6), R=(1, 7))],
    "u": [dict(bob=0, L=(-1, 7), R=(1, 7)), dict(bob=0, L=(-1, 6), R=(1, 7)),
          dict(bob=1, L=(-1, 7), R=(1, 7)), dict(bob=1, L=(-1, 7), R=(1, 6))],
    "l": [dict(bob=0, N=(0, 8)), dict(bob=0, N=(-1, 8)), dict(bob=1, N=(0, 8)), dict(bob=1, N=(1, 8))],
}
EAT = {
    "d": [dict(bob=0, L=(2, 5), R=(1, 7), props=[("food", "L", -1, -3, "front")]),
          dict(bob=0, L=(3, 0), R=(1, 7), props=[("food", "L", -1, -3, "front")]),
          dict(bob=0, L=(3, -2), R=(1, 7), props=[("food", "L", -1, -3, "front")]),
          dict(bob=1, L=(3, 0), R=(1, 7), props=[("food", "L", -1, -3, "front")])],
    "u": [dict(bob=0, L=(2, 5), R=(1, 7)), dict(bob=0, L=(3, 1), R=(1, 7)),
          dict(bob=0, L=(3, -1), R=(1, 7)), dict(bob=1, L=(3, 1), R=(1, 7))],
    "l": [dict(bob=0, N=(-3, 5), props=[("food", "N", -2, -3, "front")]),
          dict(bob=0, N=(-4, 1), props=[("food", "N", -2, -3, "front")]),
          dict(bob=0, N=(-4, -1), props=[("food", "N", -2, -3, "front")]),
          dict(bob=1, N=(-4, 1), props=[("food", "N", -2, -3, "front")])],
}
MIX = {
    "d": [dict(bob=0, L=(3, 6), R=(-2, 4), props=[("bowl", "L", -1, -1, "front"), ("spoon", "R", 0, -4, "back")]),
          dict(bob=0, L=(3, 6), R=(-3, 5), props=[("bowl", "L", -1, -1, "front"), ("spoon", "R", 0, -4, "back")]),
          dict(bob=1, L=(3, 6), R=(-2, 6), props=[("bowl", "L", -1, -1, "front"), ("spoon", "R", 0, -4, "back")]),
          dict(bob=1, L=(3, 6), R=(-1, 5), props=[("bowl", "L", -1, -1, "front"), ("spoon", "R", 0, -4, "back")])],
    "u": [dict(bob=0, L=(2, 5), R=(-2, 4)), dict(bob=0, L=(2, 5), R=(-3, 5)),
          dict(bob=1, L=(2, 5), R=(-2, 6)), dict(bob=1, L=(2, 5), R=(-1, 5))],
    "l": [dict(bob=0, N=(-4, 5), F=(-5, 6), props=[("bowl", "F", -3, -1, "front"), ("spoon", "N", 0, -4, "front")]),
          dict(bob=0, N=(-5, 4), F=(-5, 6), props=[("bowl", "F", -3, -1, "front"), ("spoon", "N", 0, -4, "front")]),
          dict(bob=1, N=(-6, 5), F=(-5, 6), props=[("bowl", "F", -3, -1, "front"), ("spoon", "N", 0, -4, "front")]),
          dict(bob=1, N=(-5, 6), F=(-5, 6), props=[("bowl", "F", -3, -1, "front"), ("spoon", "N", 0, -4, "front")])],
}
HERBS = {
    "d": [dict(bob=0, L=(-3, -6), R=(1, 7), props=[("herb", "L", -1, -4, "front")]),
          dict(bob=0, L=(-3, -8), R=(1, 7), props=[("herb", "L", -1, -4, "front")]),
          dict(bob=0, L=(-1, 7), R=(3, -6), props=[("herb", "R", -1, -4, "front")]),
          dict(bob=0, L=(-1, 7), R=(3, -8), props=[("herb", "R", -1, -4, "front")])],
    "u": [dict(bob=0, L=(0, -6), R=(1, 7), props=[("herb", "L", -1, -4, "front")]),
          dict(bob=0, L=(1, -8), R=(1, 7), props=[("herb", "L", -1, -4, "front")]),
          dict(bob=0, L=(-1, 7), R=(0, -6), props=[("herb", "R", -1, -4, "front")]),
          dict(bob=0, L=(-1, 7), R=(-1, -8), props=[("herb", "R", -1, -4, "front")])],
    "l": [dict(bob=0, N=(-3, -6), props=[("herb", "N", -1, -4, "front")]),
          dict(bob=0, N=(-4, -8), props=[("herb", "N", -1, -4, "front")]),
          dict(bob=0, N=(-2, 2)), dict(bob=0, N=(-3, -3))],
}


def can_frame(t, view):
    drops = [("drop", None, 0, 0, "front")]
    return drops


GARDEN = {
    "d": [dict(bob=0, L=(2, 6), R=(-2, 6), props=[("can_front", "L", -1, -2, "front")], drops=(0, 8)),
          dict(bob=0, L=(2, 6), R=(-2, 6), props=[("can_front", "L", -1, -2, "front")], drops=(1, 8)),
          dict(bob=1, L=(2, 6), R=(-2, 6), props=[("can_front", "L", -1, -2, "front")], drops=(2, 8)),
          dict(bob=1, L=(2, 6), R=(-2, 6), props=[("can_front", "L", -1, -2, "front")], drops=(3, 8))],
    # from behind, the can is held out to the side so it and the water show past the body
    "u": [dict(bob=0, L=(-5, 5), R=(1, 7), props=[("can_front", "L", -3, -2, "front")], drops=(0, 8)),
          dict(bob=0, L=(-5, 5), R=(1, 7), props=[("can_front", "L", -3, -2, "front")], drops=(1, 8)),
          dict(bob=1, L=(-5, 5), R=(1, 7), props=[("can_front", "L", -3, -2, "front")], drops=(2, 8)),
          dict(bob=1, L=(-5, 5), R=(1, 7), props=[("can_front", "L", -3, -2, "front")], drops=(3, 8))],
    "l": [dict(bob=0, N=(-4, 6), props=[("can_side", "N", -8, -2, "front")], drops=(0, 0)),
          dict(bob=0, N=(-4, 6), props=[("can_side", "N", -8, -2, "front")], drops=(1, 0)),
          dict(bob=1, N=(-4, 6), props=[("can_side", "N", -8, -2, "front")], drops=(2, 0)),
          dict(bob=1, N=(-4, 6), props=[("can_side", "N", -8, -2, "front")], drops=(3, 0))],
}

def _cook(view):
    """Pan in one hand, spatula in the other; a morsel is tossed and caught."""
    toss = (-2, -5, -7, -4)
    if view == "d":
        return [dict(bob=b, L=(3, 5), R=(-3, r), props=[("pan", "L", -1, -1, "front"),
                                                       ("morsel", "L", 4, t, "front"),
                                                       ("spatula", "R", 0, -4, "back")])
                for b, r, t in zip((0, 0, 1, 1), (4, 3, 4, 5), toss)]
    if view == "u":
        # facing the stove: the pan is held out to the side so it shows past the body
        return [dict(bob=b, L=(-5, 5), R=(2, 4), props=[("pan", "L", -1, -1, "front"),
                                                       ("morsel", "L", 4, t, "front")])
                for b, t in zip((0, 0, 1, 1), toss)]
    return [dict(bob=b, N=(-4, 5), F=(-5, f), props=[("pan_side", "N", -8, -1, "front"),
                                                    ("morsel", "N", -5, t, "front"),
                                                    ("spatula", "F", 0, -4, "back")])
            for b, f, t in zip((0, 0, 1, 1), (4, 3, 4, 5), toss)]


COOK = {v: _cook(v) for v in "dul"}

# wiping the bar: one hand rests on the counter, the other rubs a rag back and forth
WIPE = {
    "d": [dict(bob=b, L=(3, 6), R=(r, 6), props=[("rag", "R", -1, 1, "front")])
          for b, r in zip((0, 0, 1, 1), (-2, -4, -6, -4))],
    "u": [dict(bob=b, L=(1, 6), R=(r, 6), props=[("rag", "R", -1, 1, "back")])
          for b, r in zip((0, 0, 1, 1), (2, 4, 6, 4))],
    # side: upper arm hanging, forearm level along the counter (no long diagonal sleeve)
    "l": [dict(bob=b, N=(n, 7), N_elbow=(-1, 6), props=[("rag", "N", -2, 1, "front")])
          for b, n in zip((0, 0, 1, 1), (-6, -8, -10, -8))],
}
# pouring a drink: glass held low in one hand, the bottle tipped over it in the other
POUR = {
    # the glass held low in front, the bottle right above it: upright, tipped with the drink
    # running into the glass, then upright again
    "d": [dict(bob=0, L=(4, 7), R=(-6, 1), props=[("glass_low", "L", -1, -3, "front"), ("bottle", "R", -1, -6, "front")]),
          dict(bob=0, L=(4, 7), R=(-6, 1), props=[("glass_low", "L", -1, -3, "front"), ("bottle_tip", "R", -2, -3, "front"),
                                                ("pour", "L", 1, -5, "front")]),
          dict(bob=1, L=(4, 7), R=(-6, 1), props=[("glass", "L", -1, -3, "front"), ("bottle_tip", "R", -2, -3, "front"),
                                                ("pour", "L", 1, -5, "front")]),
          dict(bob=1, L=(4, 7), R=(-6, 1), props=[("glass", "L", -1, -3, "front"), ("bottle", "R", -1, -6, "front")])],
    # from behind the pouring happens in front of him, out of sight: both hands and the glass
    # are behind his body; the raised elbow shows at his side and the bottle's neck pokes up
    # past his shoulder as he tips it
    "u": [dict(bob=0, L=(2, 6), R=(3, 1), hide=("R",), props=[("bottle", "R", -1, -6, "back")]),
          dict(bob=0, L=(2, 6), R=(5, -1), hide=("R",), props=[("bottle_tip", "R", -4, -6, "back")]),
          dict(bob=1, L=(2, 6), R=(5, -1), hide=("R",), props=[("bottle_tip", "R", -4, -6, "back")]),
          dict(bob=1, L=(2, 6), R=(3, 1), hide=("R",), props=[("bottle", "R", -1, -6, "back")])],
    "l": [dict(bob=0, N=(-6, 1), F=(-6, 7), props=[("glass_low", "F", -2, -3, "front"), ("bottle", "N", -1, -6, "front")]),
          dict(bob=0, N=(-6, 1), F=(-6, 7), props=[("glass_low", "F", -2, -3, "front"), ("bottle_tip", "N", 0, -3, "front"),
                                                 ("pour", "F", -1, -5, "front")]),
          dict(bob=1, N=(-6, 1), F=(-6, 7), props=[("glass", "F", -2, -3, "front"), ("bottle_tip", "N", 0, -3, "front"),
                                                 ("pour", "F", -1, -5, "front")]),
          dict(bob=1, N=(-6, 1), F=(-6, 7), props=[("glass", "F", -2, -3, "front"), ("bottle", "N", -1, -6, "front")])],
}
# relaxing: one hand at the side, the other resting at the chin (scratching the back of the
# head when seen from behind)
RELAX = {
    "d": [dict(bob=0, L=(-1, 7), R=(-4, -5)), dict(bob=0, L=(-1, 7), R=(-4, -6)),
          dict(bob=1, L=(-1, 7), R=(-4, -5)), dict(bob=1, L=(-1, 6), R=(-3, -6))],
    "u": [dict(bob=0, L=(-1, 7), R=(-2, -12)), dict(bob=0, L=(-1, 7), R=(-3, -13)),
          dict(bob=1, L=(-1, 7), R=(-2, -12)), dict(bob=1, L=(-1, 6), R=(-1, -13))],
    "l": [dict(bob=0, N=(-3, -5)), dict(bob=0, N=(-3, -6)), dict(bob=1, N=(-3, -5)), dict(bob=1, N=(-2, -6))],
}
# beckoning: one hand raised in front, curling in toward the body and out again
BECKON = {
    "d": [dict(bob=b, L=(0, 7), R=(-3, r), props=[]) for b, r in zip((0, 0, 1, 1), (-1, -3, -2, 0))],
    # from behind the raised hand shows beside the head
    "u": [dict(bob=b, L=(0, 7), R=(r, -9)) for b, r in zip((0, 0, 1, 1), (3, 1, 2, 4))],
    "l": [dict(bob=b, N=(n, -1)) for b, n in zip((0, 0, 1, 1), (-6, -4, -5, -7))],
}
# waving: a hand up beside the head, swung side to side
WAVE = {
    # the hand is held out past the side of the head, clear of the face
    "d": [dict(bob=b, L=(0, 7), R=(r, -7)) for b, r in zip((0, 0, 1, 1), (4, 6, 5, 7))],
    "u": [dict(bob=b, L=(0, 7), R=(r, -7)) for b, r in zip((0, 0, 1, 1), (3, 5, 4, 6))],
    # from the side the hand is held up out in front, below the face
    "l": [dict(bob=b, N=(n, -3)) for b, n in zip((0, 0, 1, 1), (-8, -10, -9, -11))],
}
# sorting the mail: a stack of letters in one hand, the other taking one and slotting it away
MAIL = {
    "d": [dict(bob=b, L=(1, 5), R=r, props=[("letter", "L", -2, -1, "front")] + ([("letter", "R", -2, -1, "front")] if k else []))
          for b, r, k in zip((0, 0, 1, 1), ((1, 4), (3, 1), (5, -1), (3, 3)), (1, 1, 1, 0))],
    # from behind the working limbs move at her sides, a letter showing as it is slotted away
    "u": [dict(bob=b, L=(-1, 6), R=r, props=([("letter", "R", -2, -1, "front")] if k else []))
          for b, r, k in zip((0, 0, 1, 1), ((1, 4), (2, 1), (3, -1), (2, 3)), (1, 1, 1, 0))],
    "l": [dict(bob=b, N=n, F=(-2, 5), props=[("letter", "N", -3, -1, "front")])
          for b, n in zip((0, 0, 1, 1), ((-3, 4), (-5, 1), (-6, -1), (-4, 3)))],
}
# a crate of parcels: held in front with both hands and hefted up onto a shelf and back
CRATE = {
    "d": [dict(bob=b, L=(-1, y), R=(1, y), props=[("crate", "L", -1, -2, "front")])
          for b, y in zip((1, 0, 0, 1), (6, 3, 0, 3))],
    "u": [dict(bob=b, L=(-1, y), R=(1, y)) for b, y in zip((1, 0, 0, 1), (6, 4, 2, 4))],
    "l": [dict(bob=b, N=(-4, y), props=[("crate", "N", -5, -2, "front")])
          for b, y in zip((1, 0, 0, 1), (6, 3, 0, 3))],
}
# carrying luggage: a suitcase held by its handle at his side, lifted a little with each step
LUGGAGE = {
    "d": [dict(bob=b, L=(0, l), R=(1, r), props=[("suitcase", "R", -3, 1, "front")])
          for b, l, r in zip((0, 0, 1, 1), (7, 6, 7, 8), (7, 6, 7, 8))],
    "u": [dict(bob=b, L=(0, l), R=(1, r), props=[("suitcase", "R", -3, 1, "front")])
          for b, l, r in zip((0, 0, 1, 1), (7, 6, 7, 8), (7, 6, 7, 8))],
    "l": [dict(bob=b, N=(-1, n), props=[("suitcase", "N", -3, 1, "front")])
          for b, n in zip((0, 0, 1, 1), (7, 6, 7, 8))],
}
# ringing the desk bell: the hand raised over it and brought down on top
BELL = {
    "d": [dict(bob=b, L=(0, 7), R=(-5, r), fixed=[("bell", 9, 33, "mid")])
          for b, r in zip((0, 0, 0, 1), (3, 1, 4, 3))],
    "u": [dict(bob=b, L=(0, l), R=(-5, 4), hide=("R",)) for b, l in zip((0, 0, 1, 1), (7, 6, 7, 8))],
    "l": [dict(bob=b, N=(-7, n), fixed=[("bell", 6, 32, "mid")])
          for b, n in zip((0, 0, 0, 1), (4, 2, 5, 4))],
}
# tying knots: both hands working a length of rope in front of him, pulling it tight
KNOTS = {
    "d": [dict(bob=b, L=(3, l), R=(-3, r), props=[("rope", "L", 0, -2, "front")])
          for b, l, r in zip((0, 0, 1, 1), (5, 4, 5, 6), (5, 6, 4, 5))],
    "u": [dict(bob=b, L=(2, l), R=(-2, r)) for b, l, r in zip((0, 0, 1, 1), (6, 5, 6, 7), (6, 7, 5, 6))],
    "l": [dict(bob=b, N=(-5, n), F=(-4, f), props=[("rope", "N", -2, -2, "front")])
          for b, n, f in zip((0, 0, 1, 1), (5, 4, 5, 6), (5, 6, 4, 5))],
}
# at the campfire: hands held out to the warmth, rubbed together, firelight flickering on them
CAMPFIRE = {
    "d": [dict(bob=b, L=(l, 3), R=(-l, 3), props=[(e, "L", 1, -2, "front")])
          for b, l, e in zip((0, 0, 1, 1), (4, 5, 4, 3), ("ember", "ember2", "ember", "ember2"))],
    "u": [dict(bob=b, L=(2, r), R=(-2, r)) for b, r in zip((0, 0, 1, 1), (5, 4, 5, 6))],
    "l": [dict(bob=b, N=(n, 2), F=(n + 1, 3), props=[(e, "N", -2, -2, "front")])
          for b, n, e in zip((0, 0, 1, 1), (-6, -7, -6, -5), ("ember", "ember2", "ember", "ember2"))],
}
# recovering: getting his breath back, hands braced low on his legs, shoulders heaving
RECOVER = {
    "d": [dict(bob=b, L=(2, l), R=(-2, r)) for b, l, r in zip((1, 0, 0, 1), (8, 7, 7, 8), (8, 7, 6, 7))],
    "u": [dict(bob=b, L=(1, l), R=(-1, r)) for b, l, r in zip((1, 0, 0, 1), (8, 7, 7, 8), (8, 7, 6, 7))],
    "l": [dict(bob=b, N=(-2, n), F=(-1, 8)) for b, n in zip((1, 0, 0, 1), (8, 7, 6, 7))],
}
# on guard: the spear held upright at the side (from the side, out in front of him, its
# shaft clear of his face), a small shift of weight and grip
GUARD = {
    "d": [dict(bob=b, L=(0, l), R=(2, r), props=[("spear", "R", 0, -17, "front")])
          for b, l, r in zip((0, 0, 1, 1), (7, 6, 7, 8), (6, 6, 5, 6))],
    "u": [dict(bob=b, L=(0, l), R=(2, r), props=[("spear", "R", 0, -17, "front")])
          for b, l, r in zip((0, 0, 1, 1), (7, 6, 7, 8), (6, 6, 5, 6))],
    "l": [dict(bob=b, N=(-11, n), props=[("spear", "N", -1, -17, "front")])
          for b, n in zip((0, 0, 1, 1), (3, 2, 3, 4))],
}
# stopping on patrol: the spear lifted and its butt planted on the floor
WALK_STOP = {
    "d": [dict(bob=b, L=(0, 7), R=(2, r), props=[("spear", "R", 0, -17, "front")])
          for b, r in zip((0, 0, 1, 1), (6, 4, 6, 7))],
    "u": [dict(bob=b, L=(0, 7), R=(2, r), props=[("spear", "R", 0, -17, "front")])
          for b, r in zip((0, 0, 1, 1), (6, 4, 6, 7))],
    "l": [dict(bob=b, N=(-11, n), props=[("spear", "N", -1, -17, "front")])
          for b, n in zip((0, 0, 1, 1), (3, 0, 3, 4))],
}
# pondering: a hand at the chin, tapping, the other arm across under it
PONDER = {
    "d": [dict(bob=b, L=(4, 5), R=r) for b, r in zip((0, 0, 1, 1), ((-6, -6), (-6, -5), (-6, -6), (-5, -6)))],
    # from behind the thinking hand is at the chin, out of sight; the other hangs
    "u": [dict(bob=b, L=l, R=(-6, -6), hide=("R",)) for b, l in zip((0, 0, 1, 1), ((0, 7), (0, 6), (0, 7), (1, 7)))],
    "l": [dict(bob=b, N=n, F=(-3, 5)) for b, n in zip((0, 0, 1, 1), ((-7, -5), (-7, -4), (-7, -5), (-6, -5)))],
}
# surveying: a scanner held out and swept slowly across the ground ahead, its screen
# flickering
SURVEY = {
    "d": [dict(bob=b, L=(3, 6), R=(r, 4), props=[("scanner", "R", -1, -1, "front"), (g, "R", 0, -3, "front")])
          for b, r, g in zip((0, 0, 1, 1), (-3, -1, 1, -1), ("glow", "glow2", "glow", "glow2"))],
    # from behind the arm reaches out to the side with the scanner
    "u": [dict(bob=b, L=(0, 7), R=(r, 1), props=[("scanner", "R", -1, -1, "front"), (g, "R", 0, -3, "front")])
          for b, r, g in zip((0, 0, 1, 1), (4, 6, 7, 5), ("glow", "glow2", "glow", "glow2"))],
    "l": [dict(bob=b, N=(-6, n), F=(-3, 5), props=[("scanner", "N", -3, -1, "front"), (g, "N", -2, -3, "front")])
          for b, n, g in zip((0, 0, 1, 1), (3, 2, 3, 4), ("glow", "glow2", "glow", "glow2"))],
}
# stargazing: a spyglass raised to the eye and turned slowly across the sky
STARGAZE = {
    # one hand holds the spyglass to the eye, the other hangs
    "d": [dict(bob=b, L=l, R=r, props=[("spy_d", "L", -1, -2, "front")])
          for b, l, r in zip((0, 0, 1, 1), ((4, -10), (4, -11), (5, -10), (4, -10)), ((1, 7), (1, 6), (1, 7), (2, 7)))],
    # from behind both hands are at the face, out of sight; the far end of the spyglass shows
    # above the hat, moving across the sky
    "u": [dict(bob=b, L=(4, 4), R=(-4, 4), hide=("L", "R"), fixed=[("spy_back", x, 5, "front")])
          for b, x in zip((0, 0, 1, 1), (9, 10, 11, 10))],
    "l": [dict(bob=b, N=(-6, -8), props=[("spy_up", "N", -4, -5 + t, "front")])
          for b, t in zip((0, 0, 1, 1), (0, -1, 0, 1))],
}
# observing: a spyglass held level to the eye, looking out ahead
OBSERVE = {
    "d": [dict(bob=b, L=l, R=r, props=[("spy_d", "L", -1, -2, "front")])
          for b, l, r in zip((0, 0, 1, 1), ((4, -10), (3, -10), (4, -10), (5, -10)), ((1, 7), (1, 6), (1, 7), (2, 7)))],
    "u": [dict(bob=b, L=(4, 4), R=(-4, 4), hide=("L", "R"), fixed=[("spy_back", x, 7, "front")])
          for b, x in zip((0, 0, 1, 1), (9, 10, 11, 10))],
    "l": [dict(bob=b, N=n, F=(-4, -8), props=[("spy_h", "N", -6, -2, "front")])
          for b, n in zip((0, 0, 1, 1), ((-6, -9), (-7, -9), (-6, -8), (-6, -9)))],
}
# mining: the pickaxe swung up over the shoulder and brought down into the rock
MINE = {
    "d": [dict(bob=b, L=(4, l), R=(-4, r), props=[("pick", "R", -2, -5, "front")])
          for b, l, r in zip((0, 0, 1, 1), (6, 4, 6, 5), (-6, -2, 6, -1))],
    # from behind the pick shows over the shoulder when raised; the strike is out of sight
    "u": [dict(bob=0, L=(2, 6), R=(0, -8), props=[("pick", "R", -2, -5, "front")]),
          dict(bob=0, L=(2, 6), R=(1, -5), props=[("pick", "R", -2, -5, "front")]),
          dict(bob=1, L=(2, 6), R=(1, 4), hide=("R",), props=[]),
          dict(bob=1, L=(2, 6), R=(1, -4), props=[("pick", "R", -2, -5, "front")])],
    "l": [dict(bob=b, N=n, props=[("pick", "N", -2, -5, "front")])
          for b, n in zip((0, 0, 1, 1), ((2, -8), (-3, -5), (-7, 5), (-3, -3)))],
}
# welding: the torch held to the work, sparks spitting from it; the other hand steadies the
# piece
WELD = {
    "d": [dict(bob=b, L=(3, 6), R=r, props=[("torch", "R", 0, -3, "front"), (s, "R", -1, 2, "front")])
          for b, r, s in zip((0, 0, 1, 1), ((-3, 5), (-2, 5), (-3, 6), (-4, 5)), ("sparks1", "sparks2", "sparks1", "sparks2"))],
    # from behind the work is in front of her: her arms reach forward at her sides and the
    # sparks show either side of her
    "u": [dict(bob=b, L=l, R=r, fixed=[(s, x, y, "front")])
          for b, l, r, s, x, y in zip((0, 0, 1, 1), ((1, 6), (1, 5), (1, 6), (2, 6)), ((-1, 6), (-2, 6), (-1, 5), (-1, 6)),
                                      ("sparks1", "sparks2", "sparks2", "sparks1"), (2, 19, 3, 20), (30, 29, 31, 30))],
    "l": [dict(bob=b, N=n, props=[("torch", "N", 0, -3, "front"), (s, "N", -3, 1, "front")])
          for b, n, s in zip((0, 0, 1, 1), ((-6, 4), (-6, 5), (-7, 4), (-6, 3)), ("sparks1", "sparks2", "sparks1", "sparks2"))],
}
# at the anvil: the hammer raised high and brought down, the other hand holding the piece
HAMMER = {
    "d": [dict(bob=b, L=(4, 7), R=(-4, r), props=[("hammer", "R", -1, -4, "front")])
          for b, r in zip((0, 0, 1, 1), (-3, 1, 5, 1))],
    "u": [dict(bob=0, L=(2, 6), R=(0, -7), props=[("hammer", "R", -1, -4, "front")]),
          dict(bob=0, L=(2, 6), R=(1, -5), props=[("hammer", "R", -1, -4, "front")]),
          dict(bob=1, L=(2, 6), R=(1, 3), hide=("R",), props=[]),
          dict(bob=1, L=(2, 6), R=(1, -5), props=[("hammer", "R", -1, -4, "front")])],
    "l": [dict(bob=b, N=(-5, n), F=(-6, 7), props=[("hammer", "N", -1, -4, "front")])
          for b, n in zip((0, 0, 1, 1), (-3, 1, 5, 1))],
}
# at a console: hands on the keys, tapping in turn
CONSOLE = {
    "d": [dict(bob=b, L=(1, l), R=(-1, r), fixed=[("console_front", 4, 33, "mid")])
          for b, l, r in zip((0, 0, 1, 1), (6, 5, 6, 6), (6, 6, 6, 5))],
    # from behind the desk shows either side of her and her hands work at its edges
    "u": [dict(bob=b, L=(-2, l), R=(2, r), fixed=[("console_back", -3, 31, "back")])
          for b, l, r in zip((0, 0, 1, 1), (5, 4, 5, 5), (5, 5, 5, 4))],
    "l": [dict(bob=b, N=(-5, n), F=(-4, 5), fixed=[("console_side", -4, 32, "mid")])
          for b, n in zip((0, 0, 1, 1), (5, 4, 5, 6))],
}
# tinkering: a gadget held in one hand, poked at with a spanner in the other
TINKER = {
    "d": [dict(bob=b, L=(1, 5), R=r, props=[("device", "L", -1, -2, "front"), ("spanner", "R", -1, -4, "front")])
          for b, r in zip((0, 0, 1, 1), ((-2, 4), (-3, 3), (-2, 4), (-1, 3)))],
    "u": [dict(bob=b, L=l, R=r) for b, l, r in zip(
        (0, 0, 1, 1), ((-1, 6), (0, 5), (-1, 6), (-1, 5)), ((1, 6), (1, 5), (0, 6), (1, 7)))],
    "l": [dict(bob=b, N=n, F=f, props=[("device", "N", -2, -2, "front")])
          for b, n, f in zip((0, 0, 1, 1), ((-5, 4), (-5, 3), (-5, 4), (-6, 4)), ((-3, 2), (-4, 1), (-3, 2), (-2, 1)))],
}
# behind the shop counter: both hands resting on it, fingers drumming in turn
COUNTER = {
    "d": [dict(bob=b, L=(4, l), R=(-4, r)) for b, l, r in zip((0, 0, 1, 1), (6, 5, 6, 6), (6, 6, 6, 5))],
    "u": [dict(bob=b, L=(4, l), R=(-4, r), hide=("L", "R")) for b, l, r in zip((0, 0, 1, 1), (6, 5, 6, 6), (6, 6, 6, 5))],
    "l": [dict(bob=b, N=(-5, n), F=(-4, 4)) for b, n in zip((0, 0, 1, 1), (4, 3, 4, 5))],
}
# restocking: a jar lifted from low down up onto a shelf, the hand coming back for the next
RESTOCK = {
    "d": [dict(bob=1, L=(-1, 7), R=(-2, 6), props=[("jar", "R", -1, -3, "front")]),
          dict(bob=0, L=(-1, 7), R=(-2, 1), props=[("jar", "R", -1, -3, "front")]),
          dict(bob=0, L=(-1, 7), R=(-2, -5), props=[("jar", "R", -1, -3, "front")]),
          dict(bob=0, L=(-1, 7), R=(-3, -2))],
    "u": [dict(bob=1, L=(-1, 7), R=(1, 6)),
          dict(bob=0, L=(-1, 7), R=(1, -1), props=[("jar", "R", -2, -3, "front")]),
          dict(bob=0, L=(-1, 7), R=(0, -8), props=[("jar", "R", -2, -3, "front")]),
          dict(bob=0, L=(-1, 7), R=(1, -5))],
    "l": [dict(bob=1, N=(-4, 6), props=[("jar", "N", -4, -3, "front")]),
          dict(bob=0, N=(-5, 1), props=[("jar", "N", -4, -3, "front")]),
          dict(bob=0, N=(-5, -5), props=[("jar", "N", -4, -3, "front")]),
          dict(bob=0, N=(-4, -2))],
}
# weaving at a hand loom: the shuttle is passed from hand to hand across the warp
WEAVE = {
    "d": [dict(bob=b, L=(l, 7), R=(r, 7), fixed=[("loom", 5, 33, "mid")], props=[("shuttle", s, -1, -1, "front")])
          for b, l, r, s in zip((0, 0, 1, 1), (-3, -1, 1, -1), (-1, 1, 3, 1), ("L", "L", "R", "R"))],
    # from behind: the loom is in front of her; the working limbs move at her sides
    "u": [dict(bob=b, L=l, R=r) for b, l, r in zip(
        (0, 0, 1, 1), ((-1, 8), (0, 7), (1, 8), (0, 9)), ((-1, 9), (0, 8), (1, 7), (0, 8)))],
    "l": [dict(bob=b, N=(n, 7), F=(n - 1, 6), fixed=[("loom_side", -1, 32, "mid")])
          for b, n in zip((0, 0, 1, 1), (-5, -6, -7, -6))],
}
# chatting: one hand turning over in the air as she talks, the other at her chest
CHAT = {
    "d": [dict(bob=b, L=(1, 6), R=r) for b, r in zip((0, 0, 1, 1), ((3, 1), (5, -1), (4, 0), (6, 1)))],
    "u": [dict(bob=b, L=(1, 4), R=r) for b, r in zip((0, 0, 1, 1), ((5, 1), (7, -1), (6, 0), (8, 1)))],
    "l": [dict(bob=b, N=n, F=(-2, 5)) for b, n in zip((0, 0, 1, 1), ((-5, 2), (-7, 0), (-6, 1), (-8, 2)))],
}
# building: a plank held steady in one hand, a hammer raised and brought down with the other
BUILD = {
    "d": [dict(bob=b, L=(4, 7), R=(-4, r), props=[("plank", "L", -3, 2, "front"), ("hammer", "R", -1, -4, "front")])
          for b, r in zip((0, 0, 1, 1), (-3, 1, 5, 1))],
    # from behind the hammer shows over the shoulder when raised; the strike is out of sight
    "u": [dict(bob=0, L=(2, 6), R=(0, -7), props=[("hammer", "R", -1, -4, "front")]),
          dict(bob=0, L=(2, 6), R=(1, -5), props=[("hammer", "R", -1, -4, "front")]),
          dict(bob=1, L=(2, 6), R=(1, 3), hide=("R",), props=[]),
          dict(bob=1, L=(2, 6), R=(1, -5), props=[("hammer", "R", -1, -4, "front")])],
    "l": [dict(bob=b, N=(-5, n), F=(-6, 7), props=[("plank", "F", -6, 2, "front"), ("hammer", "N", -1, -4, "front")])
          for b, n in zip((0, 0, 1, 1), (-3, 1, 5, 1))],
}
# sketching: a pad held up in one hand, the pencil moving over it in the other
SKETCH = {
    "d": [dict(bob=b, L=(3, 4), R=(r, 4), props=[("pad", "L", -2, -3, "front"), ("pencil", "R", 0, -3, "front")])
          for b, r in zip((0, 0, 1, 1), (-3, -2, -4, -3))],
    # from behind the pad is held out to the side, tilting as he draws
    "u": [dict(bob=b, L=(-4, l), R=(1, 4), props=[("pad", "L", -3, -3, "front")])
          for b, l in zip((0, 0, 1, 1), (2, 1, 1, 2))],
    "l": [dict(bob=b, N=(n, 3), F=(-6, 4), props=[("pad", "F", -3, -3, "back"), ("pencil", "N", 0, -3, "front")])
          for b, n in zip((0, 0, 1, 1), (-5, -4, -6, -5))],
}
# turning a valve wheel: both hands on the rim, going round
VALVE = {
    "d": [dict(bob=b, L=(4 + l[0], 3 + l[1]), R=(-4 + r[0], 3 + r[1]),
               props=[(w, "L", 0, -3, "front")])
          for b, l, r, w in zip((0, 0, 1, 1), ((0, 1), (1, 0), (0, -1), (-1, 0)),
                                ((0, -1), (-1, 0), (0, 1), (1, 0)), ("valve", "valve_x", "valve", "valve_x"))],
    # from behind the wheel and hands are in front of him; his elbows work out at his sides
    "u": [dict(bob=b, L=l, R=r, hide=("L", "R"))
          for b, l, r in zip((0, 0, 1, 1), ((3, 3), (4, 2), (3, 3), (2, 4)), ((-2, 4), (-3, 3), (-4, 2), (-3, 3)))],
    "l": [dict(bob=b, N=(-6 + n[0], 2 + n[1]), F=(-6 + f[0], 3 + f[1]), props=[(w, "N", -4, -3, "front")])
          for b, n, f, w in zip((0, 0, 1, 1), ((0, -1), (-1, 0), (0, 1), (1, 0)),
                                ((0, 1), (1, 0), (0, -1), (-1, 0)), ("valve_side", "valve_side2", "valve_side", "valve_side2"))],
}
# tending plants: reaching low, one hand then the other, a leaf in hand
TEND = {
    "d": [dict(bob=0, L=(2, 9), R=(-1, 7), props=[("herb", "L", -1, -4, "front")]),
          dict(bob=1, L=(2, 10), R=(-1, 7), props=[("herb", "L", -1, -4, "front")]),
          dict(bob=0, L=(1, 7), R=(-2, 9), props=[("herb", "R", -1, -4, "front")]),
          dict(bob=1, L=(1, 7), R=(-2, 10), props=[("herb", "R", -1, -4, "front")])],
    # from behind: one hand reaches out to the side, low, to a plant beside him
    "u": [dict(bob=b, L=(l, 8), R=(1, 7), props=[("herb", "L", -1, -4, "front")])
          for b, l in zip((0, 0, 1, 1), (-5, -6, -6, -5))],
    "l": [dict(bob=b, N=(n, 9), props=[("herb", "N", -1, -4, "front")])
          for b, n in zip((0, 0, 1, 1), (-5, -6, -6, -5))],
}
# drawing: paper held in one hand, a crayon scribbling in the other
DRAW = {
    "d": [dict(bob=b, L=(3, 3), R=(r, 2), props=[("paper", "L", -2, -3, "front"), ("crayon", "R", 0, -2, "front")])
          for b, r in zip((0, 0, 1, 1), (-3, -2, -4, -3))],
    # from behind: drawing on the wall in front of him, the crayon hand up beside his head
    "u": [dict(bob=b, L=(1, 6), R=(r, -6), props=[("crayon", "R", 0, -2, "front")])
          for b, r in zip((0, 0, 1, 1), (3, 4, 4, 3))],
    "l": [dict(bob=b, N=(n, 1), F=(-6, 3), props=[("paper", "F", -3, -3, "back"), ("crayon", "N", 0, -2, "front")])
          for b, n in zip((0, 0, 1, 1), (-5, -4, -6, -5))],
}
# playing: bouncing a ball, the hand pats it down and it comes back up
PLAY = {
    # the ball is bounced out beside him: in the hand, dropping, on the floor, coming back up
    "d": [dict(bob=b, L=(-1, 7), R=(3, h), props=[("ball", "R", -1, t, "front")])
          for b, h, t in zip((0, 1, 0, 1), (4, 5, 4, 3), (1, 3, 4, 2))],
    "u": [dict(bob=b, L=(-1, 7), R=(4, h), props=[("ball", "R", -1, t, "front")])
          for b, h, t in zip((0, 1, 0, 1), (4, 5, 4, 3), (1, 3, 4, 2))],
    "l": [dict(bob=b, N=(-6, h), props=[("ball", "N", -1, t, "front")])
          for b, h, t in zip((0, 1, 0, 1), (4, 5, 4, 3), (1, 3, 4, 2))],
}
# keeping the ledger: the book held open in one hand, writing in it with the other
LEDGER = {
    "d": [dict(bob=b, L=(3, 4), R=(r, 4), props=[("ledger", "L", -3, -3, "front"), ("pencil", "R", 0, -3, "front")])
          for b, r in zip((0, 0, 1, 1), (-3, -2, -4, -3))],
    # from behind: the book is in front of him; his writing elbow works at his side
    "u": [dict(bob=b, L=(2, 4), R=r, hide=("L", "R"))
          for b, r in zip((0, 0, 1, 1), ((2, 3), (4, 2), (4, 2), (2, 3)))],
    "l": [dict(bob=b, N=(n, 3), F=(-6, 4), props=[("ledger", "F", -4, -3, "back"), ("pencil", "N", 0, -3, "front")])
          for b, n in zip((0, 0, 1, 1), (-5, -4, -6, -5))],
}
# on patrol: hands clasped behind the back, rocking a little on his heels
PATROL = {
    "d": [dict(bob=b, L=(3, l), R=(-3, l), hide=("L", "R")) for b, l in zip((0, 0, 1, 1), (6, 5, 5, 6))],
    # from behind the clasped hands show on the small of his back
    "u": [dict(bob=b, L=(5, l), R=(-5, l)) for b, l in zip((0, 0, 1, 1), (6, 5, 5, 6))],
    "l": [dict(bob=b, N=(n, 6)) for b, n in zip((0, 0, 1, 1), (3, 4, 4, 3))],
}
# a drink: the mug lifted to the mouth and lowered
DRINK = {
    "d": [dict(bob=0, L=(2, 5), R=(1, 7), props=[("mug", "L", -2, -2, "front")]),
          dict(bob=0, L=(3, 0), R=(1, 7), props=[("mug", "L", -2, -2, "front")]),
          dict(bob=0, L=(3, -3), R=(1, 7), props=[("mug", "L", -2, -2, "front")]),
          dict(bob=1, L=(3, 0), R=(1, 7), props=[("mug", "L", -2, -2, "front")])],
    "u": [dict(bob=0, L=(2, 5), R=(1, 7)), dict(bob=0, L=(3, 1), R=(1, 7)),
          dict(bob=0, L=(3, -1), R=(1, 7)), dict(bob=1, L=(3, 1), R=(1, 7))],
    "l": [dict(bob=0, N=(-3, 5), props=[("mug", "N", -3, -2, "front")]),
          dict(bob=0, N=(-4, 1), props=[("mug", "N", -3, -2, "front")]),
          dict(bob=0, N=(-4, -2), props=[("mug", "N", -3, -2, "front")]),
          dict(bob=1, N=(-4, 1), props=[("mug", "N", -3, -2, "front")])],
}
# sweeping: both hands on the broom handle, the head swept side to side along the floor
SWEEP = {
    "d": [dict(bob=b, L=(4 + s, 6), R=(-4 + s, 4), props=[(br, "L", -1, 1, "front")])
          for b, s, br in zip((0, 0, 1, 1), (0, -1, 0, 1), ("broom", "broom_tilt", "broom", "broom_tilt"))],
    # from behind: the broom is in front of her; its head shows past her side as it swings
    "u": [dict(bob=b, L=(2, 6), R=(r, 4), hide=("L", "R"), props=[("broom", "R", 0, 3, "back")])
          for b, r in zip((0, 0, 1, 1), (2, 4, 5, 3))],
    "l": [dict(bob=b, N=(n, 5), F=(n + 1, 3), props=[(br, "N", -2, 1, "front")])
          for b, n, br in zip((0, 0, 1, 1), (-5, -6, -7, -6), ("broom", "broom_tilt", "broom", "broom_tilt"))],
}
# browsing the shelves: a hand reaches up to the goods, takes something down to look at
BROWSE = {
    "d": [dict(bob=0, L=(-1, 7), R=(-3, -3)), dict(bob=0, L=(-1, 7), R=(-4, -5)),
          dict(bob=1, L=(3, 3), R=(-3, 3), props=[("food", "L", 1, -3, "front")]),
          dict(bob=1, L=(3, 2), R=(-3, 2), props=[("food", "L", 1, -3, "front")])],
    "u": [dict(bob=0, L=(-1, 7), R=(1, -7)), dict(bob=0, L=(-1, 7), R=(0, -9)),
          dict(bob=1, L=(-1, 7), R=(2, -6)), dict(bob=1, L=(-1, 6), R=(1, -8))],
    "l": [dict(bob=0, N=(-4, -4)), dict(bob=0, N=(-5, -6)), dict(bob=1, N=(-4, 1), props=[("food", "N", -2, -3, "front")]),
          dict(bob=1, N=(-4, 0), props=[("food", "N", -2, -3, "front")])],
}
# watching: hands folded in front, breathing
WATCH = {
    "d": [dict(bob=b, L=(4, h), R=(-4, h)) for b, h in zip((0, 0, 1, 1), (6, 5, 5, 6))],
    "u": [dict(bob=b, L=(4, h), R=(-4, h), hide=("L", "R")) for b, h in zip((0, 0, 1, 1), (6, 5, 5, 6))],
    "l": [dict(bob=b, N=(-2, h), F=(-3, h)) for b, h in zip((0, 0, 1, 1), (6, 5, 5, 6))],
}
# playing with a toy: held up in both hands, turned and lifted
TOY = {
    "d": [dict(bob=b, L=(3, h), R=(-3, h), props=[("toy", "L", 0, -3, "front")])
          for b, h in zip((0, 0, 1, 1), (3, 1, 2, 4))],
    # from behind: the toy is held out at his side, below his big head, turned and lifted
    "u": [dict(bob=b, L=(-5, h), R=(1, 6), props=[("toy", "L", -2, -3, "front")])
          for b, h in zip((0, 0, 1, 1), (1, -1, 0, 2))],
    "l": [dict(bob=b, N=(-4, h), F=(-5, h), props=[("toy", "N", -2, -3, "front")])
          for b, h in zip((0, 0, 1, 1), (3, 1, 2, 4))],
}
# a hand-held hologame: both hands on it at the chest, the glow over it flickering
HOLOGAME = {
    "d": [dict(bob=b, L=(3, 3), R=(-3, 3), props=[("device", "L", 0, -1, "front"), (g, "L", 0, -4, "front")])
          for b, g in zip((0, 0, 1, 1), ("glow", "glow2", "glow", "glow2"))],
    # from behind: the game is in front of him; only its glow shows over his shoulder
    "u": [dict(bob=b, L=(2, 3), R=(-2, 3), hide=("L", "R"), props=[(g, "R", 2, -9, "front")])
          for b, g in zip((0, 0, 1, 1), ("glow", "glow2", "glow", "glow2"))],
    "l": [dict(bob=b, N=(-4, 3), F=(-5, 3), props=[("device", "N", -2, -1, "front"), (g, "N", -2, -4, "front")])
          for b, g in zip((0, 0, 1, 1), ("glow", "glow2", "glow", "glow2"))],
}
# polishing a blade: held level in one hand, a cloth run along it with the other
POLISH = {
    "d": [dict(bob=b, L=(4, 4), R=(r, 4), props=[("blade_flat", "L", -1, 0, "front"), ("rag", "R", -1, 0, "front")])
          for b, r in zip((0, 0, 1, 1), (-1, -3, -5, -3))],
    # from behind: the blade is in front of her; the polishing elbow works at her side
    "u": [dict(bob=b, L=(2, 4), R=r, hide=("L", "R"))
          for b, r in zip((0, 0, 1, 1), ((2, 3), (4, 2), (4, 2), (2, 3)))],
    "l": [dict(bob=b, N=(n, 4), F=(-7, 4), props=[("blade_h", "F", -6, 0, "back"), ("rag", "N", -1, 0, "front")])
          for b, n in zip((0, 0, 1, 1), (-3, -5, -7, -5))],
}
# sparring: a practice blade on guard, raised, struck down, back to guard
SPAR = {
    "d": [dict(bob=0, L=(1, 6), R=(-3, 2), props=[("blade_v", "R", 0, -6, "front")]),
          dict(bob=0, L=(1, 6), R=(2, -3), props=[("blade_v", "R", 0, -6, "front")]),
          dict(bob=1, L=(1, 6), R=(-4, 5), props=[("blade_flat", "R", -6, 0, "front")]),
          dict(bob=1, L=(1, 6), R=(-3, 3), props=[("blade_v", "R", 0, -6, "front")])],
    # from behind the raised blade shows over her shoulder; the strike is in front of her
    "u": [dict(bob=0, L=(1, 6), R=(2, -4), props=[("blade_v", "R", 0, -6, "front")]),
          dict(bob=0, L=(1, 6), R=(1, -7), props=[("blade_v", "R", 0, -6, "front")]),
          dict(bob=1, L=(1, 6), R=(-1, 4), hide=("R",)),
          dict(bob=1, L=(1, 6), R=(2, -4), props=[("blade_v", "R", 0, -6, "front")])],
    "l": [dict(bob=0, N=(-3, 3), props=[("blade_v", "N", 0, -6, "front")]),
          dict(bob=0, N=(-6, -3), props=[("blade_v", "N", 0, -6, "front")]),
          dict(bob=1, N=(-7, 2), props=[("blade_h", "N", -6, 0, "front")]),
          dict(bob=1, N=(-4, 3), props=[("blade_v", "N", 0, -6, "front")])],
}
# treating a patient: the scanner held out low in one hand and passed slowly over them,
# the other hand steadying; the light flickers
TREAT = {
    "d": [dict(bob=b, L=(3 + s, 6), R=(-3, 5), props=[("scanner", "L", -1, -1, "front"), (g, "L", 0, -3, "front")])
          for b, s, g in zip((0, 0, 1, 1), (0, 1, 2, 1), ("glow", "glow2", "glow", "glow2"))],
    # from behind: the patient is in front of her; her elbows work at her sides
    "u": [dict(bob=b, L=l, R=(-3, 5), hide=("L", "R"))
          for b, l in zip((0, 0, 1, 1), ((-2, 4), (-3, 3), (-4, 4), (-3, 5)))],
    "l": [dict(bob=b, N=(n, 6), F=(-5, 5), props=[("scanner", "N", -3, -1, "front"), (g, "N", -2, -3, "front")])
          for b, n, g in zip((0, 0, 1, 1), (-5, -6, -7, -6), ("glow", "glow2", "glow", "glow2"))],
}
# sorting: a book taken from one hand to the other and set down
SORT = {
    "d": [dict(bob=0, L=(3, 5), R=(-1, 7), props=[("ledger", "L", -2, -3, "front")]),
          dict(bob=0, L=(5, 2), R=(-4, 3), props=[("ledger", "L", -2, -3, "front")]),
          dict(bob=1, L=(1, 7), R=(-5, 3), props=[("ledger", "R", -3, -3, "front")]),
          dict(bob=1, L=(1, 7), R=(-3, 5), props=[("ledger", "R", -3, -3, "front")])],
    # from behind: the books are on the shelf in front of him; a hand reaches up to it
    "u": [dict(bob=0, L=(-1, 7), R=(1, 7)), dict(bob=0, L=(-1, 7), R=(1, -8)),
          dict(bob=1, L=(-1, 7), R=(2, -9)), dict(bob=1, L=(-1, 6), R=(1, -7))],
    "l": [dict(bob=0, N=(-4, 4), props=[("ledger", "N", -4, -3, "front")]),
          dict(bob=0, N=(-5, 1), props=[("ledger", "N", -4, -3, "front")]),
          dict(bob=1, N=(-5, -2), props=[("ledger", "N", -4, -3, "front")]),
          dict(bob=1, N=(-3, 6))],
}
# reading: a book held open at the chest in both hands, a page turned now and then
READ = {
    "d": [dict(bob=b, L=(4, 3), R=(-4, r), props=[("ledger", "L", -1, -3, "front")])
          for b, r in zip((0, 0, 1, 1), (3, 2, 3, 1))],
    # from behind: the book is in front of him; his elbows show at his sides
    "u": [dict(bob=b, L=l, R=r, hide=("L", "R"))
          for b, l, r in zip((0, 0, 1, 1), ((-2, 4), (-2, 4), (-3, 3), (-2, 4)), ((2, 4), (3, 3), (2, 4), (2, 4)))],
    "l": [dict(bob=b, N=(-5, n), F=(-6, 3), props=[("ledger", "N", -4, -3, "front")])
          for b, n in zip((0, 0, 1, 1), (3, 2, 3, 1))],
}
# shelving: a book lifted up to a high shelf and pushed in, the hand coming back down
SHELVE = {
    "d": [dict(bob=0, L=(-1, 7), R=(-3, 2), props=[("ledger", "R", -3, -3, "front")]),
          dict(bob=0, L=(-1, 7), R=(-2, -4), props=[("ledger", "R", -3, -3, "front")]),
          dict(bob=1, L=(-1, 7), R=(-2, -6), props=[("ledger", "R", -3, -3, "front")]),
          dict(bob=1, L=(-1, 7), R=(-3, -2))],
    # from behind the book goes up past his head to the shelf in front of him
    "u": [dict(bob=0, L=(-1, 7), R=(1, -4), props=[("ledger", "R", -2, -3, "front")]),
          dict(bob=0, L=(-1, 7), R=(1, -7), props=[("ledger", "R", -2, -3, "front")]),
          dict(bob=1, L=(-1, 7), R=(0, -9), props=[("ledger", "R", -2, -3, "front")]),
          dict(bob=1, L=(-1, 7), R=(1, -6))],
    "l": [dict(bob=0, N=(-4, 2), props=[("ledger", "N", -4, -3, "front")]),
          dict(bob=0, N=(-5, -3), props=[("ledger", "N", -4, -3, "front")]),
          dict(bob=1, N=(-5, -6), props=[("ledger", "N", -4, -3, "front")]),
          dict(bob=1, N=(-4, -2))],
}
# at the workbench: both hands working low in front with a spanner
BENCH = {
    "d": [dict(bob=b, L=(3, l), R=(-3, r), props=[("spanner", "R", -1, -4, "front")])
          for b, l, r in zip((0, 0, 1, 1), (6, 5, 6, 7), (6, 7, 5, 6))],
    "u": [dict(bob=b, L=l, R=r, hide=("L", "R"))
          for b, l, r in zip((0, 0, 1, 1), ((-2, 5), (-3, 4), (-2, 5), (-2, 4)), ((2, 4), (2, 5), (3, 4), (2, 5)))],
    "l": [dict(bob=b, N=(n, 6), F=(-6, 6), props=[("spanner", "N", -1, -4, "front")])
          for b, n in zip((0, 0, 1, 1), (-5, -6, -7, -6))],
}
# chess: thinking, reaching to the board, moving a piece, sitting back
CHESS = {
    "d": [dict(bob=0, L=(-1, 7), R=(-4, -3)), dict(bob=0, L=(-1, 7), R=(-3, 6)),
          dict(bob=1, L=(-1, 7), R=(-5, 6), props=[("piece", "R", -1, -3, "front")]),
          dict(bob=1, L=(-1, 7), R=(-3, 4))],
    "u": [dict(bob=0, L=(-1, 7), R=(1, 7)), dict(bob=0, L=(-1, 7), R=(-2, 5), hide=("R",)),
          dict(bob=1, L=(-1, 7), R=(-3, 5), hide=("R",)), dict(bob=1, L=(-1, 6), R=(1, 7))],
    "l": [dict(bob=0, N=(-3, -3)), dict(bob=0, N=(-6, 6)),
          dict(bob=1, N=(-8, 6), props=[("piece", "N", -1, -3, "front")]),
          dict(bob=1, N=(-4, 4))],
}
ALIAS = {"valve_d": "valve", "valve_l": "valve", "study": "ledger"}
# tuning a thruster: the spanner turned at a fitting, the other hand steadying the housing
TUNE = {
    "d": [dict(bob=b, L=(2, 5), R=r, props=[("spanner", "R", -1, -4, "front")])
          for b, r in zip((0, 0, 1, 1), ((-3, 4), (-2, 2), (-3, 4), (-4, 3)))],
    # from behind the fitting is above her: both hands reach up beside her head, the
    # spanner showing over them as it turns
    "u": [dict(bob=b, L=(0, -4), R=(0, r), props=[("spanner", "R", -1, -4, "front")])
          for b, r in zip((0, 0, 1, 1), (-6, -8, -6, -5))],
    "l": [dict(bob=b, N=n, F=(-7, -3), props=[("spanner", "N", -1, -4, "front")])
          for b, n in zip((0, 0, 1, 1), ((-10, -5), (-11, -7), (-10, -5), (-9, -4)))],
}
# charting a course at the console: one hand on the keys, the other tracing the route across
# the glowing chart
CHART = {
    "d": [dict(bob=b, L=(1, 6), R=(r, 5), fixed=[("console_front", 4, 33, "mid")], props=[(g, "R", 0, -2, "front")])
          for b, r, g in zip((0, 0, 1, 1), (-3, -1, 1, -1), ("glow", "glow2", "glow", "glow2"))],
    "u": [dict(bob=b, L=(-2, 5), R=(r, 5), fixed=[("console_back", -3, 31, "back")], props=[(g, "R", 0, -2, "back")])
          for b, r, g in zip((0, 0, 1, 1), (2, 3, 4, 3), ("glow", "glow2", "glow", "glow2"))],
    "l": [dict(bob=b, N=(n, 8), F=(-4, 6), fixed=[("console_side", -1, 32, "mid")], props=[(g, "N", -1, -2, "front")])
          for b, n, g in zip((0, 0, 1, 1), (-6, -8, -7, -8), ("glow", "glow2", "glow", "glow2"))],
}
# explaining: one hand held out to the side, palm open toward what she is showing, the other
# at her waist
EXPLAIN = {
    "d": [dict(bob=b, L=(0, 6), R=r) for b, r in zip((0, 0, 1, 1), ((5, 1), (6, 0), (6, 1), (5, 2)))],
    "u": [dict(bob=b, L=(0, 6), R=r) for b, r in zip((0, 0, 1, 1), ((5, 1), (6, 0), (6, 1), (5, 2)))],
    "l": [dict(bob=b, N=n) for b, n in zip((0, 0, 1, 1), ((-7, 2), (-8, 1), (-8, 2), (-7, 3)))],
}
# talking: a hand held out in front, palm up, moving with the words
TALK = {
    "d": [dict(bob=b, L=(0, 6), R=r) for b, r in zip((0, 0, 1, 1), ((-2, 3), (-1, 2), (-2, 2), (-3, 3)))],
    "u": [dict(bob=b, L=(0, 6), R=r, hide=("R",)) for b, r in zip((0, 0, 1, 1), ((-2, 3), (-1, 2), (-2, 2), (-3, 3)))],
    "l": [dict(bob=b, N=n) for b, n in zip((0, 0, 1, 1), ((-5, 3), (-6, 2), (-5, 2), (-4, 3)))],
}
# hands clasped together in front of her chest
CLASP = {
    "d": [dict(bob=b, L=(3, l), R=(-3, l)) for b, l in zip((0, 0, 1, 1), (2, 1, 2, 3))],
    "u": [dict(bob=b, L=(3, l), R=(-3, l), hide=("L", "R")) for b, l in zip((0, 1, 1, 0), (2, 1, 2, 3))],
    "l": [dict(bob=b, N=(-3, n), F=(-2, n)) for b, n in zip((0, 0, 1, 1), (2, 1, 2, 3))],
}
# greeting: a hand raised high and a small bow of the head
GREET = {
    "d": [dict(bob=b, L=(0, 6), R=(r, -10)) for b, r in zip((0, 1, 2, 1), (3, 4, 4, 3))],
    "u": [dict(bob=b, L=(0, 6), R=(r, -10)) for b, r in zip((0, 1, 2, 1), (3, 4, 4, 3))],
    # from the side the hand is held up out in front of her face, clear of it
    "l": [dict(bob=b, N=(n, -6)) for b, n in zip((0, 1, 2, 1), (-9, -10, -10, -9))],
}
ACTIVITIES = {"explain": EXPLAIN, "talk": TALK, "clasp": CLASP, "greet": GREET, "tune": TUNE, "chart": CHART, "mail": MAIL, "crate": CRATE, "luggage": LUGGAGE, "bell": BELL, "knots": KNOTS, "campfire": CAMPFIRE, "recover": RECOVER, "guard": GUARD, "walk_stop": WALK_STOP, "ponder": PONDER, "survey": SURVEY, "stargaze": STARGAZE, "observe": OBSERVE, "mine": MINE, "weld": WELD, "hammer": HAMMER, "console": CONSOLE, "tinker": TINKER, "counter": COUNTER, "restock": RESTOCK, "weave": WEAVE, "chat": CHAT, "wave": WAVE, "shelve": SHELVE, "bench": BENCH, "chess": CHESS, "sort": SORT, "read": READ, "treat": TREAT, "polish": POLISH, "spar": SPAR, "toy": TOY, "hologame": HOLOGAME, "sweep": SWEEP, "browse": BROWSE, "watch": WATCH, "ledger": LEDGER, "patrol": PATROL, "drink": DRINK, "draw": DRAW, "play": PLAY, "valve": VALVE, "tend": TEND, "build": BUILD, "sketch": SKETCH, "beckon": BECKON, "wipe": WIPE, "pour": POUR, "cook": COOK, "relax": RELAX, "rest": REST, "eat": EAT, "mix": MIX, "herbs": HERBS, "garden": GARDEN}

# ----------------------------------------------------------------------------- rigs


def body_without_arms(cell, boxes, line, fill_sides=False, fill_span=None):
    """Take the arm boxes off a standing frame and close the torso edge with the outline.
    fill_sides: for a long coat, the coat's side panels (hidden behind the arms) are carried
    straight up from the row below each box, so taking the arms off leaves no notch."""
    out = cell.copy()
    rows = set()
    for (x0, x1, y0, y1) in boxes:
        out[y0:y1 + 1, x0:x1 + 1] = 0
        rows |= set(range(y0, y1 + 1))
    if isinstance(fill_sides, str):
        # a plain jacket: the cloth behind the arms is filled in one tone inside the
        # standing frame's own outline, so no fold of the old sleeve is left behind
        for (x0, x1, y0, y1) in boxes:
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    # a pixel in from the old sleeve's outer edge: the jacket is a little
                    # narrower than the arm that hung over it
                    inside = cell[y, max(x - 1, 0), 3] and cell[y, min(x + 1, cell.shape[1] - 1), 3]
                    if fill_span is not None:
                        inside = fill_span[0] <= x <= fill_span[1]
                    if inside and not out[y, x, 3]:
                        out[y, x] = hexc(fill_sides)
    elif fill_sides:
        for (x0, x1, y0, y1) in boxes:
            below = out[y1 + 1]
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    if below[x, 3] and not out[y, x, 3]:
                        out[y, x] = below[x]
    for y in rows:
        xs = np.where(out[y, :, 3] > 0)[0]
        if len(xs):
            out[y, xs.min()] = line
            out[y, xs.max()] = line
    return out


RIGS = {
    "evarra": dict(
        pal=dict(line="#381f2a", sleeve="#716a5a", sleeve_hi="#928a71",
                 skin="#dbb1ca", skin_lo="#bf8dc1", skin_hi="#eed8e3"),
        # front and back: arms come off at the sides
        d=dict(arms=[(2, 7, 26, 36), (17, 22, 26, 36)], L=(7, 27), R=(17, 27)),
        u=dict(arms=[(1, 6, 26, 36), (17, 22, 26, 36)], L=(6, 27), R=(17, 27)),
        l=dict(N=(12, 25), F=(13, 25)),
        hip=dict(d=36, u=36, l=37),
        sleep=dict(eyes=[(10, 14, 2, 3), (15, 14, 2, 3)], skin="#d6a2c3", lash="#4b2737",
                   neck=22, top=29),
    ),
    "rusk": dict(
        pal=dict(line="#2a1219", sleeve="#ddbd9d", sleeve_hi="#f6d3ad",
                 skin="#e67543", skin_lo="#c65933", skin_hi="#e79568"),
        d=dict(arms=[(0, 5, 26, 35), (18, 23, 26, 35)], L=(5, 27), R=(18, 27)),
        u=dict(arms=[(0, 5, 26, 35), (17, 23, 26, 35)], L=(5, 27), R=(17, 27)),
        l=dict(N=(12, 23), F=(13, 23)),
        hip=dict(d=41, u=41, l=40),
        sleep=dict(eyes=[(8, 13, 2, 3), (14, 13, 2, 3)], skin="#e67543", lash="#2a1a12",
                   neck=21, top=30),
    ),
    "ooma": dict(
        pal=dict(line="#2f1b29", sleeve="#59385d", sleeve_hi="#7c4554",
                 skin="#b86d70", skin_lo="#a95a64", skin_hi="#d0868a"),
        d=dict(arms=[(2, 5, 26, 34), (6, 7, 31, 34), (18, 21, 26, 34), (18, 19, 31, 34)], L=(6, 26), R=(17, 26)),
        u=dict(arms=[(1, 4, 26, 39), (19, 22, 26, 39)], L=(5, 26), R=(18, 26)),
        l=dict(N=(12, 25), F=(13, 25)),
        hip=dict(d=42, u=42, l=42),
        sleep=dict(eyes=[(10, 14, 2, 3), (15, 14, 2, 3)], skin="#b86d70", lash="#130518",
                   neck=24, top=32),
    ),
    "tobbin": dict(
        pal=dict(line="#361f1d", sleeve="#ebc287", sleeve_hi="#fbe1b4",
                 skin="#c88b42", skin_lo="#a06f3c", skin_hi="#e9ac58"),
        d=dict(arms=[(0, 5, 28, 38), (18, 23, 28, 38)], L=(5, 29), R=(18, 29)),
        u=dict(arms=[(0, 5, 28, 38), (18, 23, 28, 38)], L=(5, 29), R=(18, 29)),
        l=dict(N=(14, 29), F=(15, 29)),
        hip=dict(d=42, u=42, l=42),
        arm_w=3,   # puffed sleeves
        sleep=dict(eyes=[(8, 17, 2, 3), (14, 17, 2, 3)], skin="#c88b42", lash="#2e1c1c",
                   neck=28, top=34),
    ),
    "merrow": dict(
        pal=dict(line="#270e16", sleeve="#c7cea2", sleeve_hi="#f6edc7",
                 skin="#94bb9a", skin_lo="#698b7a", skin_hi="#b5d6ba"),
        d=dict(arms=[(1, 5, 25, 38), (17, 22, 25, 38)], L=(5, 26), R=(17, 26)),
        u=dict(arms=[(1, 6, 25, 38), (17, 22, 25, 38)], L=(6, 26), R=(17, 26)),
        l=dict(N=(14, 24), F=(15, 24)),
        hip=dict(d=42, u=42, l=39),
        sleep=dict(eyes=[(7, 12, 2, 3), (14, 12, 2, 3)], skin="#94bb9a", lash="#18070e",
                   neck=23, top=30),
    ),
    "nub": dict(
        pal=dict(line="#26101a", sleeve="#766f32", sleeve_hi="#938d41",
                 skin="#cec75f", skin_lo="#a79640", skin_hi="#e1d981"),
        d=dict(arms=[(3, 6, 33, 40), (17, 20, 33, 40)], L=(6, 34), R=(17, 34)),
        u=dict(arms=[(3, 6, 33, 40), (17, 20, 33, 40)], L=(6, 34), R=(17, 34)),
        l=dict(N=(12, 33), F=(13, 33)),
        hip=dict(d=42, u=42, l=42),
        sleep=dict(eyes=[(8, 23, 2, 3), (14, 23, 2, 3)], skin="#cec75f", lash="#180411",
                   neck=32, top=38),
    ),
    "garrick": dict(
        pal=dict(line="#28192a", sleeve="#3c2f45", sleeve_hi="#4a4058",
                 skin="#eca26a", skin_lo="#cf8d60", skin_hi="#fbb972"),
        d=dict(arms=[(0, 5, 26, 36), (18, 23, 26, 36)], L=(5, 27), R=(18, 27)),
        u=dict(arms=[(0, 5, 26, 36), (17, 23, 26, 36)], L=(5, 27), R=(17, 27)),
        l=dict(N=(11, 20), F=(12, 20)),
        hip=dict(d=41, u=42, l=37),
        sleep=dict(eyes=[(8, 10, 2, 3), (14, 10, 2, 3)], skin="#eca26a", lash="#1d0e22",
                   neck=17, top=30),
    ),
    "saffi": dict(
        pal=dict(line="#401d20", sleeve="#a77159", sleeve_hi="#b2836c",
                 skin="#dfb89a", skin_lo="#c9a185", skin_hi="#f2c6a2"),
        # only her forearms come off (rows 28-31); below them, at her hips, the walk builder
        # has already painted in the top of her skirt where her hands hung
        d=dict(arms=[(2, 6, 28, 31), (16, 20, 28, 31)], L=(5, 28), R=(17, 28)),
        u=dict(arms=[(2, 6, 28, 31), (16, 20, 28, 31)], L=(5, 28), R=(17, 28)),
        l=dict(N=(10, 24), F=(11, 24)),
        hip=dict(d=42, u=42, l=42),
        sleep=dict(eyes=[(8, 15, 2, 3), (14, 15, 2, 3)], skin="#976f62", lash="#1f2a1a",
                   neck=23, top=31),
    ),
    "tally": dict(
        # like Sesska and Tikka she keeps all eight of her own limbs and works with a thin
        # pair from under her chest (from behind, from her sides)
        pal=dict(line="#1d1019", sleeve="#7a5171", sleeve_hi="#926172",
                 skin="#a06474", skin_lo="#623d4d", skin_hi="#ad7771"),
        d=dict(arms=[], L=(9, 26), R=(14, 26)),
        u=dict(arms=[], L=(6, 25), R=(17, 25)),
        l=dict(N=(8, 26), F=(10, 26)),
        hip=dict(d=33, u=33, l=33), arm_w=1, u_center_rule=True, breathe=("rest",),
        override={
            # to her mouth tentacles and down again
            "eat d": [dict(bob=b, L=l, R=(-1, 6), props=[("food", "L", -1, -3, "front")])
                      for b, l in zip((0, 0, 0, 1), ((1, 5), (2, 1), (2, -2), (2, 1)))],
            "eat l": [dict(bob=b, N=n, props=[("food", "N", -2, -3, "front")])
                      for b, n in zip((0, 0, 0, 1), ((-2, 4), (-3, 0), (-3, -2), (-3, 0)))],
            # from behind her working hands are in front of her, drawn behind the body so
            # only what shows past her sides is seen; nothing lies across her back
            "eat u": [dict(bob=b, L=(1, 6), R=r, hide=("L", "R"))
                      for b, r in zip((0, 0, 1, 1), ((1, 7), (3, -3), (-4, -6), (3, -3)))],
            "mail u": [dict(bob=b, L=(1, 6), R=r, hide=("L", "R"),
                            props=[("letter", "R", -2, -4, "back")] if k else [])
                       for b, r, k in zip((0, 0, 1, 1), ((2, 2), (3, -2), (4, -5), (1, 7)), (1, 1, 1, 0))],
            # from behind the crate is lifted up over her cap onto a high shelf
            "crate u": [dict(bob=b, L=(1, l), R=(-2, l), hide=("L", "R"),
                             fixed=[("crate", 8, y, "back")] if y is not None else [])
                        for b, l, y in zip((1, 0, 0, 1), (6, -17, -21, -17), (None, 5, 1, 5))],
        },
        sleep=dict(eyes=[(9, 18, 2, 3), (15, 18, 2, 3)], skin="#926172", lash="#341d2a",
                   neck=23, top=31),
    ),
    "stu": dict(
        pal=dict(line="#211016", sleeve="#703846", sleeve_hi="#7d4552",
                 skin="#acb34c", skin_lo="#777c3a", skin_hi="#c3bc5e"),
        # slim drawn arms set flush against the coat
        d=dict(arms=[(2, 7, 27, 32), (16, 21, 27, 32)], L=(5, 27), R=(16, 27)),
        u=dict(arms=[(2, 7, 27, 32), (16, 21, 27, 32)], L=(6, 27), R=(16, 27)),
        l=dict(N=(15, 25), F=(16, 25)),
        hip=dict(d=39, u=39, l=39), u_center_rule=True, keep_hidden_sleeve=True,
        override={
            # his wide mouth sits high above his shoulders (row 18): food is brought well up
            "eat d": [dict(bob=b, L=l, R=(1, 7), props=[("food", "L", -1, -3, "front")])
                      for b, l in zip((0, 0, 0, 1), ((3, 5), (5, -2), (6, -7), (5, -3)))],
            "eat l": [dict(bob=b, N=n, props=[("food", "N", -2, -3, "front")])
                      for b, n in zip((0, 0, 0, 1), ((-3, 5), (-6, -2), (-8, -6), (-6, -3)))],
            # from behind, the eating hand is in front of him: its sleeve hangs at his side
            "eat u": [dict(bob=b, L=(3, 6), R=(0, r), hide=("L",)) for b, r in zip((0, 0, 1, 1), (7, 6, 7, 8))],
        },
        # the coat's edge carries up behind the arms from below them
        carry_up={"d": [(6, 7, 27, 32, 33), (16, 17, 27, 32, 33)],
                  "u": [(6, 7, 27, 32, 33), (16, 17, 27, 32, 33)]},
        sleep=dict(eyes=[(7, 12, 3, 3), (15, 12, 3, 3)], skin="#919647", lash="#211016",
                   neck=20, top=28),
    ),
    "ana": dict(
        pal=dict(line="#2f161e", sleeve="#422a34", sleeve_hi="#4b323b",
                 skin="#e1a378", skin_lo="#aa7d67", skin_hi="#f9c59b"),
        # her pilot's jacket: the sleeves come off its sides and the cloth behind them is
        # filled in its own tone, the jacket a little narrower than the old sleeves
        d=dict(arms=[(4, 7, 24, 30), (16, 19, 24, 30)], L=(5, 24), R=(18, 24)),
        u=dict(arms=[(4, 7, 24, 30), (16, 19, 24, 30)], L=(5, 24), R=(18, 24)),
        l=dict(N=(12, 23), F=(13, 23)),
        hip=dict(d=36, u=36, l=35), u_center_rule=True, keep_hidden_sleeve=True,
        fill_sides=True, fill_tone="#3c232c", fill_span=(5, 18),
        sleep=dict(eyes=[(8, 13, 2, 3), (14, 13, 2, 3)], skin="#e1a378", lash="#2f161e",
                   neck=22, top=30),
    ),
    "sara_solid": dict(
        pal=dict(line="#1d202c", sleeve="#375c6a", sleeve_hi="#48717c",
                 skin="#98e2e3", skin_lo="#6fbfc5", skin_hi="#b5e4e4"),
        # S.A.R.A.'s solid body: her slim suit arms come out from under her long hair; they
        # are taken off below it and drawn from there, so nothing is drawn over the hair
        d=dict(arms=[(6, 8, 26, 32), (18, 20, 26, 32)], L=(8, 27), R=(18, 27)),
        u=dict(arms=[(4, 6, 26, 33), (16, 18, 26, 33)], L=(6, 27), R=(16, 27)),
        l=dict(N=(11, 22), F=(12, 22)),
        # drawn from below the hair, a hanging arm is shorter: the hand rests where hers did
        hang=-3,
        hip=dict(d=34, u=34, l=34), u_center_rule=True, keep_hidden_sleeve=True,
        override={
            # her arms are drawn from below her hair, so the food is brought further up
            "eat d": [dict(bob=b, L=l, R=(0, 6), props=[("food", "L", -1, -3, "front")])
                      for b, l in zip((0, 0, 0, 1), ((2, 5), (4, -3), (4, -8), (4, -4)))],
            "eat l": [dict(bob=b, N=n, props=[("food", "N", -2, -3, "front")])
                      for b, n in zip((0, 0, 0, 1), ((-3, 5), (-5, -1), (-6, -4), (-5, -1)))],
            # from behind, a raised hand is past the side of her hair; the arm goes behind it
            "wave u": [dict(bob=b, L=(0, 6), R=(r, -10), hide=("R",)) for b, r in zip((0, 0, 1, 1), (6, 8, 7, 9))],
            "greet u": [dict(bob=b, L=(0, 6), R=(r, -10), hide=("R",)) for b, r in zip((0, 1, 2, 1), (6, 7, 7, 6))],
        },
        sleep=dict(eyes=[(9, 12, 2, 3), (15, 12, 2, 3)], skin="#8dd7da", lash="#141521",
                   neck=19, top=27),
    ),
    "artie": dict(
        pal=dict(line="#2e151a", sleeve="#913642", sleeve_hi="#ad4533",
                 skin="#eda470", skin_lo="#d57b4f", skin_hi="#f8bd83"),
        d=dict(arms=[(3, 7, 23, 30), (17, 21, 23, 30)], L=(5, 24), R=(18, 24)),
        u=dict(arms=[(3, 7, 23, 30), (17, 21, 23, 30)], L=(5, 24), R=(18, 24)),
        l=dict(N=(14, 22), F=(15, 22)),
        hip=dict(d=39, u=40, l=40), u_center_rule=True, keep_hidden_sleeve=True,
        # from behind, reading: the book is held in front of him (his upper arms at his
        # sides), one hand now and then lowered from it
        override={"read u": [dict(bob=b, L=(2, 5), R=r, hide=h) for b, r, h in zip(
            (0, 0, 1, 1), ((2, 5), (0, 6), (2, 5), (1, 6)), (("L", "R"), ("L",), ("L", "R"), ("L",)))]},
        sleep=dict(eyes=[(8, 14, 2, 3), (14, 14, 2, 3)], skin="#eda470", lash="#2e151a",
                   neck=19, top=27),
    ),
    "vzzket": dict(
        pal=dict(line="#1e0e16", sleeve="#802931", sleeve_hi="#a83338",
                 skin="#b59748", skin_lo="#876a3d", skin_hi="#caa750"),
        # the arms come off below the shoulder plates; the tunic's edge carries up behind them
        d=dict(arms=[(0, 6, 25, 31), (17, 23, 25, 31)], L=(3, 25), R=(18, 25)),
        u=dict(arms=[(0, 6, 25, 31), (17, 23, 25, 31)], L=(3, 25), R=(18, 25)),
        l=dict(N=(13, 25), F=(14, 25)),
        hip=dict(d=40, u=40, l=40), u_center_rule=True, arm_w=3,
        carry_up={"d": [(5, 7, 26, 31, 32), (17, 19, 26, 31, 32)],
                  "u": [(5, 7, 26, 31, 32), (16, 18, 26, 31, 32)]},
        sleep=dict(eyes=[(10, 12, 2, 3), (16, 12, 2, 3)], skin="#b59748", lash="#1f140f",
                   neck=18, top=26),
    ),
    "tarbesh": dict(
        pal=dict(line="#2e181d", sleeve="#712b41", sleeve_hi="#7c3245",
                 skin="#b3944d", skin_lo="#92753f", skin_hi="#d8a857"),
        # the wide robe sleeves come off; the robe's own edge (from below them) carries up
        d=dict(arms=[(0, 5, 26, 32), (18, 23, 26, 32)], L=(3, 25), R=(18, 25)),
        u=dict(arms=[(0, 5, 26, 32), (18, 23, 26, 32)], L=(3, 25), R=(18, 25)),
        l=dict(N=(12, 23), F=(13, 23)),
        hip=dict(d=42, u=42, l=42), u_center_rule=True, fill_sides=True, keep_hidden_sleeve=True,
        arm_w=3,   # wide robe sleeves
        # from behind, the eating hand is in front of him: its sleeve hangs at his side
        override={"eat u": [dict(bob=b, L=(3, 2), R=(0, r), hide=("L",)) for b, r in zip((0, 0, 1, 1), (7, 6, 7, 8))]},
        sleep=dict(eyes=[(8, 13, 2, 3), (15, 13, 2, 3)], skin="#b3944d", lash="#2e181d",
                   neck=20, top=28),
    ),
    "zaas": dict(
        pal=dict(line="#251a24", sleeve="#4c8881", sleeve_hi="#63ad9e",
                 skin="#5da395", skin_lo="#406c6b", skin_hi="#73bdab"),
        # the arms sit flush against the vest
        d=dict(arms=[(3, 7, 31, 38), (17, 21, 31, 38)], L=(6, 31), R=(17, 31)),
        u=dict(arms=[(3, 7, 31, 37), (16, 20, 31, 37)], L=(6, 31), R=(16, 31)),
        l=dict(N=(13, 31), F=(14, 31)),
        hip=dict(d=40, u=40, l=40), u_center_rule=True,
        override={
            # to the little beak among the face tentacles (row 22) and down again
            "eat d": [dict(bob=b, L=l, R=(1, 7), props=[("food", "L", -1, -3, "front")])
                      for b, l in zip((0, 0, 0, 1), ((3, 5), (6, -1), (8, -7), (6, -2)))],
            "eat l": [dict(bob=b, N=n, props=[("food", "N", -2, -3, "front")])
                      for b, n in zip((0, 0, 0, 1), ((-3, 5), (-6, -1), (-8, -7), (-6, -2)))],
        },
        sleep=dict(eyes=[(10, 20, 2, 3), (16, 20, 2, 3)], skin="#50978d", lash="#251a24",
                   neck=30, top=37),
    ),
    "job": dict(
        pal=dict(line="#2f151f", sleeve="#eb7130", sleeve_hi="#fc7e31",
                 skin="#b66037", skin_lo="#8e4c2f", skin_hi="#c56734"),
        # his arms are long (to row 36): hanging hands go four pixels lower than the others,
        # so the arm hangs straight down his side instead of bowing out at the elbow
        # sleeves and forearms come off; below the forearms (from row 33) the overalls' own
        # edge (x 5, 18) stays
        d=dict(arms=[(0, 5, 21, 32), (0, 4, 33, 36), (18, 23, 21, 32), (19, 23, 33, 36)], L=(3, 22), R=(18, 22)),
        u=dict(arms=[(0, 5, 21, 32), (0, 3, 33, 36), (18, 23, 21, 32), (20, 23, 33, 36)], L=(3, 22), R=(18, 22)),
        l=dict(N=(15, 22), F=(16, 22)),
        hip=dict(d=40, u=40, l=40), u_center_rule=True, hang=4,
        # the overalls' sides (edge and cloth) run up behind his arms to their top at row 27
        carry_up={"d": [(5, 6, 27, 32, 33), (17, 18, 27, 32, 33)],
                  "u": [(4, 6, 27, 32, 33), (17, 19, 27, 32, 33)]},
        arm_w=3,   # chunky sleeves
        sleep=dict(eyes=[(8, 13, 2, 3), (14, 13, 2, 3)], skin="#b66037", lash="#2f151f",
                   neck=19, top=27),
    ),
    "freya": dict(
        pal=dict(line="#5e3430", sleeve="#f2c29a", sleeve_hi="#f2c29a",
                 skin="#d9926e", skin_lo="#b08158", skin_hi="#f2c29a"),
        # only the bare upper arm and the bracer are taken off; her belt and baggy trousers
        # beside them stay
        d=dict(arms=[(5, 8, 21, 26), (4, 7, 27, 29), (16, 19, 21, 26), (17, 20, 27, 29)], L=(7, 22), R=(16, 22)),
        u=dict(arms=[(5, 8, 21, 27), (4, 7, 28, 30), (16, 19, 21, 27), (17, 20, 28, 30)], L=(7, 22), R=(16, 22)),
        l=dict(N=(11, 22), F=(12, 22)),
        hip=dict(d=41, u=41, l=40), u_center_rule=True,
        sleep=dict(eyes=[(10, 13, 2, 3), (15, 13, 2, 3)], skin="#f2c29a", lash="#5e3430",
                   neck=20, top=27),
    ),
    "tikka": dict(
        # like Sesska she keeps all eight of her own limbs and works with a thin pair from
        # under her chest (from behind, from her sides)
        pal=dict(line="#1f0d17", sleeve="#7b3c60", sleeve_hi="#a65679",
                 skin="#ad5a84", skin_lo="#84415f", skin_hi="#c36d77"),
        d=dict(arms=[], L=(9, 27), R=(14, 27)),
        u=dict(arms=[], L=(6, 26), R=(17, 26)),
        l=dict(N=(6, 28), F=(8, 28)),
        hip=dict(d=34, u=34, l=34), arm_w=1, u_center_rule=True, breathe=("rest",),
        override={
            # to her mouth (the short tentacles under her face) and down again
            "eat d": [dict(bob=b, L=l, R=(-1, 6), props=[("food", "L", -1, -3, "front")])
                      for b, l in zip((0, 0, 0, 1), ((1, 5), (2, 1), (2, -2), (2, 1)))],
            "eat l": [dict(bob=b, N=n, props=[("food", "N", -2, -3, "front")])
                      for b, n in zip((0, 0, 0, 1), ((-2, 4), (-3, 0), (-3, -2), (-3, 0)))],
            "eat u": [dict(bob=b, L=(3, 2), R=(1, r), hide=("L",)) for b, r in zip((0, 0, 1, 1), (8, 7, 8, 9))],
        },
        sleep=dict(eyes=[(8, 16, 2, 3), (14, 16, 2, 3)], skin="#a65679", lash="#2f1423",
                   neck=23, top=32),
    ),
    "bram": dict(
        pal=dict(line="#2f1419", sleeve="#d9cd83", sleeve_hi="#f8e9bc",
                 skin="#a6aa4d", skin_lo="#7d7649", skin_hi="#b1b852"),
        d=dict(arms=[(1, 6, 32, 40), (17, 22, 32, 40)], L=(3, 32), R=(18, 32)),
        u=dict(arms=[(1, 6, 32, 40), (17, 22, 32, 40)], L=(3, 32), R=(18, 32)),
        l=dict(N=(14, 32), F=(15, 32)),
        hip=dict(d=42, u=42, l=41),
        arm_w=3,   # puffed sleeves
        # his wide mouth sits low (row 25), so food and drink are brought higher than for the
        # others
        override={
            "eat d": [dict(bob=b, L=l, R=(1, 7), props=[("food", "L", -1, -3, "front")])
                      for b, l in zip((0, 0, 0, 1), ((3, 5), (5, 0), (6, -5), (5, -1)))],
            "eat l": [dict(bob=b, N=n, props=[("food", "N", -2, -3, "front")])
                      for b, n in zip((0, 0, 0, 1), ((-3, 5), (-5, 0), (-6, -5), (-5, -1)))],
            "drink d": [dict(bob=b, L=l, R=(1, 7), props=[("mug", "L", -2, -2, "front")])
                        for b, l in zip((0, 0, 0, 1), ((3, 5), (5, 0), (6, -5), (5, -1)))],
            "drink l": [dict(bob=b, N=n, props=[("mug", "N", -3, -2, "front")])
                        for b, n in zip((0, 0, 0, 1), ((-3, 5), (-5, 0), (-6, -5), (-5, -1)))],
        },
        sleep=dict(eyes=[(6, 17, 3, 3), (16, 17, 3, 3)], skin="#8c9049", lash="#2f1419",
                   neck=28, top=36),
    ),
    "sesska": dict(
        # she keeps all eight of her own limbs; the pair she works with comes from under the
        # front of her poncho (from behind, from her sides) and is drawn thin like her limbs,
        # with her pale limb tips
        pal=dict(line="#1d0e15", sleeve="#8d6572", sleeve_hi="#ae7789",
                 skin="#e8bfa3", skin_lo="#cfa091", skin_hi="#f4d8c0"),
        d=dict(arms=[], L=(9, 28), R=(14, 28)),
        u=dict(arms=[], L=(6, 25), R=(17, 25)),
        l=dict(N=(7, 27), F=(9, 27)),
        hip=dict(d=33, u=33, l=33), arm_w=1, u_center_rule=True, breathe=("rest",),
        override={
            # to her mouth (her fangs at row 21-22) and down again; the other hand at her chest
            "eat d": [dict(bob=b, L=l, R=(-1, 6), props=[("food", "L", -1, -3, "front")])
                      for b, l in zip((0, 0, 0, 1), ((1, 4), (2, 0), (2, -3), (2, 0)))],
            "eat l": [dict(bob=b, N=n, props=[("food", "N", -2, -3, "front")])
                      for b, n in zip((0, 0, 0, 1), ((-2, 4), (-3, 0), (-3, -3), (-3, 0)))],
            # from behind: the eating hand is in front of her, out of sight; the other hangs
            "eat u": [dict(bob=b, L=(3, 2), R=(1, r), hide=("L",)) for b, r in zip((0, 0, 1, 1), (8, 7, 8, 9))],
        },
        sleep=dict(eyes=[(8, 14, 2, 3), (16, 14, 2, 3)], skin="#b88a94", lash="#36212c",
                   neck=21, top=30),
    ),
    "pip": dict(
        pal=dict(line="#2e0d10", sleeve="#a64337", sleeve_hi="#b34d3b",
                 skin="#eca56f", skin_lo="#da9261", skin_hi="#f2c194"),
        d=dict(arms=[(5, 7, 31, 37), (16, 18, 31, 37)], L=(7, 31), R=(16, 31)),
        u=dict(arms=[(4, 6, 31, 39), (15, 18, 31, 38)], L=(6, 31), R=(16, 31)),
        l=dict(N=(12, 30), F=(13, 30)),
        hip=dict(d=41, u=41, l=40), u_center_rule=True,
        sleep=dict(eyes=[(9, 23, 2, 3), (14, 23, 2, 3)], skin="#eca56f", lash="#2a1414",
                   neck=29, top=33),
    ),
    "kit": dict(
        pal=dict(line="#2c0a0f", sleeve="#ae6741", sleeve_hi="#bd8a62",
                 skin="#e7c4a0", skin_lo="#a25d3d", skin_hi="#fdd7af"),
        d=dict(arms=[(5, 8, 31, 36), (16, 19, 31, 36)], L=(8, 31), R=(16, 31)),
        u=dict(arms=[(5, 8, 31, 36), (16, 19, 31, 36)], L=(8, 31), R=(16, 31)),
        l=dict(N=(12, 32), F=(13, 32)),
        hip=dict(d=42, u=43, l=42),
        sleep=dict(eyes=[(8, 23, 2, 3), (15, 23, 2, 3)], skin="#ae6741", lash="#2c0a0f",
                   neck=31, top=36),
    ),
    "ixali": dict(
        pal=dict(line="#220d18", sleeve="#8c4937", sleeve_hi="#a5633d",
                 skin="#ddb74e", skin_lo="#b79543", skin_hi="#ebc659"),
        d=dict(arms=[(2, 7, 27, 35), (18, 22, 27, 35)], L=(6, 27), R=(18, 27)),
        u=dict(arms=[(0, 4, 27, 35), (17, 21, 27, 35)], L=(5, 27), R=(17, 27)),
        l=dict(N=(11, 22), F=(12, 22)),
        hip=dict(d=41, u=40, l=40),
        sleep=dict(eyes=[(9, 12, 2, 3), (16, 12, 2, 3)], skin="#ddb74e", lash="#1f140f",
                   neck=21, top=30),
    ),
    "maren": dict(
        fill_sides=True,   # the long coat carries on behind her arms
        pal=dict(line="#44222b", sleeve="#e9c2a8", sleeve_hi="#fdf3d5",
                 skin="#e0a686", skin_lo="#c8968a", skin_hi="#f2d2b6"),
        # only the lower sleeves come off: her hair lies over her shoulders
        d=dict(arms=[(1, 6, 29, 36), (18, 22, 29, 36)], L=(5, 25), R=(18, 25)),
        u=dict(arms=[(1, 5, 29, 36), (18, 22, 29, 36)], L=(5, 25), R=(18, 25)),
        l=dict(N=(11, 24), F=(12, 24)),
        hip=dict(d=39, u=39, l=39),
        sleep=dict(eyes=[(9, 13, 2, 3), (15, 13, 2, 3)], skin="#e0a686", lash="#2a1a14",
                   neck=20, top=30),
        # from behind, her hair and coat hide her arms entirely: eating, the elbow lifts out
        # to her side so the frames still differ
        override={"eat u": [dict(bob=b, L=l, R=(1, 7), hide=("L",))
                            for b, l in zip((0, 0, 1, 1), ((-1, 5), (-3, 2), (-4, 0), (-3, 2)))]},
    ),
    "maren_weekend": dict(
        pal=dict(line="#4b2023", sleeve="#e9b795", sleeve_hi="#f9ca93",
                 skin="#dca991", skin_lo="#c19189", skin_hi="#f9ca93"),
        d=dict(arms=[(3, 7, 25, 32), (16, 20, 25, 32)], L=(7, 25), R=(16, 25)),
        u=dict(arms=[(2, 6, 25, 32), (17, 20, 25, 32)], L=(6, 25), R=(17, 25)),
        l=dict(N=(12, 24), F=(13, 24)),
        hip=dict(d=32, u=32, l=34),
        sleep=dict(eyes=[(9, 13, 2, 3), (15, 13, 2, 3)], skin="#e0a686", lash="#2a1a14",
                   neck=20, top=30),
    ),
    "maren_winter": dict(
        fill_sides=True,   # the long coat carries on behind her arms
        pal=dict(line="#2d3235", sleeve="#35494e", sleeve_hi="#364e53",
                 skin="#f3cca2", skin_lo="#c8968a", skin_hi="#f9ddbb"),
        d=dict(arms=[(1, 6, 27, 33), (17, 22, 27, 33)], L=(5, 24), R=(18, 24)),
        u=dict(arms=[(1, 5, 27, 33), (17, 22, 27, 33)], L=(5, 24), R=(18, 24)),
        l=dict(N=(11, 23), F=(12, 23)),
        hip=dict(d=39, u=39, l=39),
        sleep=dict(eyes=[(9, 13, 2, 3), (15, 13, 2, 3)], skin="#e0a686", lash="#2a1a14",
                   neck=20, top=30),
        override={"eat u": [dict(bob=b, L=l, R=(1, 7), hide=("L",))
                            for b, l in zip((0, 0, 1, 1), ((-1, 5), (-3, 2), (-4, 0), (-3, 2)))]},
    ),
    "quill": dict(
        fill_sides=True,     # the lab coat carries on behind his arms
        u_center_rule=True,  # from behind, his arms at his sides are drawn over the coat
        pal=dict(line="#160c14", sleeve="#fadcc0", sleeve_hi="#fff5d9",
                 skin="#6a8579", skin_lo="#485550", skin_hi="#a1bfae"),
        d=dict(arms=[(2, 7, 28, 35), (16, 20, 28, 35)], L=(7, 26), R=(16, 26)),
        u=dict(arms=[(3, 7, 28, 34), (16, 20, 28, 34)], L=(7, 26), R=(16, 26)),
        l=dict(N=(12, 24), F=(13, 24)),
        hip=dict(d=38, u=38, l=38),
        sleep=dict(eyes=[(8, 13, 2, 3), (14, 13, 2, 3)], skin="#9ea999", lash="#0b0206",
                   neck=20, top=30),
        # from behind, eating: the hand goes to his mouth in front of him; the arm shows
        # as the elbow lifting out at his side
        override={"eat u": [dict(bob=b, L=l, R=(1, 7))
                            for b, l in zip((0, 0, 1, 1), ((-3, 4), (-4, 1), (-4, -1), (-4, 1)))]},
    ),
    "owen": dict(
        pal=dict(line="#2a0e15", sleeve="#c56d2d", sleeve_hi="#e28530",
                 skin="#eba877", skin_lo="#ca946f", skin_hi="#f4c295"),
        # the arms hang where his old sleeves were, at the jacket's outer edge
        d=dict(arms=[(1, 6, 28, 33), (17, 22, 28, 33)], L=(4, 27), R=(19, 27)),
        u=dict(arms=[(1, 6, 28, 33), (17, 22, 28, 33)], L=(4, 27), R=(19, 27)),
        l=dict(N=(14, 24), F=(15, 24)),
        hip=dict(d=41, u=43, l=38), fill_sides=True, fill_tone="#a75928", fill_span=(4, 19), u_center_rule=True,
        # from behind: at the bench his elbows work at his sides; eating, the spoon hand is
        # in front of him, out of sight
        override={"bench u": [dict(bob=b, L=l, R=r) for b, l, r in zip(
                      (0, 0, 1, 1), ((2, 6), (3, 5), (2, 6), (2, 5)), ((-2, 6), (-2, 5), (-3, 5), (-2, 6)))],
                  "eat u": [dict(bob=b, L=l, R=r, hide=("L",)) for b, l, r in zip(
                      (0, 0, 1, 1), ((3, 5), (5, 2), (6, 0), (5, 2)), ((-1, 7), (-1, 6), (-1, 7), (-2, 7)))]},
        sleep=dict(eyes=[(9, 14, 2, 3), (14, 14, 2, 3)], skin="#eba877", lash="#2a1a14",
                   neck=21, top=31),
    ),
    "jasper": dict(
        pal=dict(line="#401a21", sleeve="#e8c4a2", sleeve_hi="#fde1bd",
                 skin="#f5823a", skin_lo="#ac552f", skin_hi="#fa9449"),
        # the boxes take in the hem's outline row (37) so it doesn't stick out past the body
        d=dict(arms=[(1, 5, 26, 37), (17, 21, 26, 37)], L=(5, 27), R=(17, 27)),
        u=dict(arms=[(1, 5, 26, 37), (17, 21, 26, 37)], L=(5, 27), R=(17, 27)),
        l=dict(N=(10, 25), F=(11, 25)),
        hip=dict(d=38, u=38, l=37),
        sleep=dict(eyes=[(7, 14, 2, 3), (14, 14, 2, 3)], skin="#f5823a", lash="#2a1510",
                   neck=23, top=30),
    ),
}

ROWS = {
    "evarra": ["mix d", "herbs u", "rest d", "eat d", "garden u"],
    "jasper": ["cook d", "relax d", "rest d", "eat d"],
    "rusk": ["wipe d", "eat d", "pour d", "rest d"],
    "ooma": ["beckon u", "eat d"],
    "tobbin": ["build d", "eat u", "sketch d", "rest d"],
    "owen": ["shelve u", "eat d", "bench d", "rest d", "chess r"],
    "quill": ["sort d", "eat d", "read u", "rest d", "read l"],
    "maren": ["treat d", "eat d", "rest d"],
    "maren_weekend": ["treat d", "eat d", "rest d"],
    "maren_winter": ["treat d", "eat d", "rest d"],
    "ixali": ["polish d", "eat d", "spar l", "rest d"],
    # S.A.R.A.'s solid body: her old sheet's eight rows (not yet used by the game)
    "sara_solid": ["wave d", "read d", "explain d", "rest d", "talk d", "clasp d", "eat d", "greet d"],
    "ana": ["tune u", "chart u", "eat d", "drink l", "rest d", "eat u", "recover u"],
    "tally": ["mail d", "crate d", "eat d", "rest d", "mail u", "eat u"],
    "stu": ["luggage d", "bell d", "sweep d", "eat d", "rest d", "eat u"],
    "artie": ["knots d", "read u", "campfire d", "eat d", "rest d", "eat u", "recover u"],
    "vzzket": ["guard r", "eat d", "walk_stop d"],
    "tarbesh": ["study u", "eat d", "ponder u", "rest d", "chess l"],
    "zaas": ["survey u", "eat d", "stargaze u", "rest d", "observe l"],
    "job": ["mine u", "eat d", "drink u", "rest d"],
    "freya": ["weld u", "hammer u", "eat d", "drink u", "rest d"],
    "tikka": ["console u", "eat d", "tinker d", "rest r"],
    "bram": ["counter l", "eat d", "drink u", "rest d", "restock l"],
    "sesska": ["weave d", "eat d", "chat l", "rest l"],
    "pip": ["study u", "play d", "wave u", "eat d", "rest d", "hologame u"],
    "kit": ["study u", "play d", "toy d", "eat u", "rest d", "hologame d"],
    "saffi": ["sweep d", "browse d", "watch l", "eat u", "rest d", "browse u"],
    "garrick": ["ledger u", "patrol d", "eat u", "drink l", "rest d"],
    "nub": ["draw u", "play d", "eat u", "rest d"],
    "merrow": ["valve_d d", "tend u", "valve_l l", "eat u", "rest d", "garden u"],
}
DIRS = "dulr"
BARE = {}


# ----------------------------------------------------------------------------- sleep
# Lying in bed, seen from above: the front view with the eyes closed (the game draws the bed
# and the blanket over them). Breathing: the chest rises a pixel, the head follows a frame
# later.
SHEET = dict(line="#4a4038", fold="#f6f2ea", sheet="#ddd6cb", shade="#bdb4a7")
SLEEP_BREATH = [(0, 0), (1, 0), (1, 1), (0, 1)]   # (chest up, head up) per frame


def close_eyes(cell, eyes, skin, lash):
    """Each eye (x, y, w, h) is painted over with skin and a lash line across its middle."""
    for (x, y, w, h) in eyes:
        cell[y:y + h, x:x + w] = skin
        cell[y + h // 2, x:x + w] = lash
    return cell


def sheet_layer(body, top, pal):
    """A sheet from row 'top' down to the feet: a folded-over edge across the chest, two
    pixels wider than the body each side there, narrowing a pixel toward the feet, with
    rounded corners and a soft shadow under the fold."""
    xs = np.where(body[top:top + 4, :, 3].any(0))[0]
    x0, x1 = xs.min() - 2, xs.max() + 2
    layer = np.zeros_like(body)
    bottom = 45
    for y in range(top, bottom + 1):
        taper = 1 if y > top + 6 else 0
        a, b = x0 + taper, x1 - taper
        if y in (top, bottom):
            a, b = a + 1, b - 1          # rounded corners
        for x in range(a, b + 1):
            if x in (a, b) or y in (top, bottom):
                c = pal["line"]
            elif y <= top + 2:
                c = pal["fold"]
            elif y == top + 3 or x in (a + 1, b - 1) or y == bottom - 1:
                c = pal["shade"]
            else:
                c = pal["sheet"]
            put(layer, x, y, c)
        if y == top + 6 or y == top + 7:   # the step where the sheet narrows
            put(layer, x0 + (1 if y == top + 7 else 0), y, pal["line"])
            put(layer, x1 - (1 if y == top + 7 else 0), y, pal["line"])
    return layer, x0, x1


FIST = ["MhsM", "MslM", ".MM."]


def fist_on(layer, x, y, pal):
    for j, row in enumerate(FIST):
        for i, ch in enumerate(row):
            if ch != ".":
                put(layer, x + i, y + j, pal[{"M": "line", "h": "skin_hi", "s": "skin", "l": "skin_lo"}[ch]])


def render_sleep(walk, name):
    """The whole standing front frame (with its fists) and the eyes closed; the bed and the
    blanket over them are the game's. Breathing: the chest rises a pixel (the row below it
    stretches), the head follows a frame later (the neck stretches)."""
    rig = RIGS[name]
    s = rig["sleep"]
    cell = walk[0:FH, 0:FW].copy()
    close_eyes(cell, s["eyes"], hexc(s["skin"]), hexc(s["lash"]))
    neck, top = s["neck"], s["top"]
    frames = []
    for chest, head in SLEEP_BREATH:
        body = cell.copy()
        if chest:
            body[neck - 1:top] = cell[neck:top + 1]
        if head:
            hl = np.zeros_like(cell); hl[:neck - 2] = cell[1:neck - 1]
            body[:neck - 1] = 0
            over(body, hl)
            body[neck - 2] = body[neck - 1] if chest else cell[neck - 1]
        out = np.zeros((FH, CW, 4), dtype=np.uint8)
        out[:, OX:OX + FW] = body
        frames.append(out)
    return frames


def render_breath(walk, rig_dir, name, view):
    """Resting with her working hands tucked away under her poncho: only her breath moves,
    as in sleep (the chest rises a pixel, the head follows a frame later), eyes open."""
    rig = RIGS[name]
    s = rig["sleep"]
    v = "l" if view in "lr" else view
    if v == "l":
        cell = np.array(Image.open(os.path.join(rig_dir, f"npc_{name}_side.png")).convert("RGBA"))[:, :FW].copy()
    else:
        col = 0 if v == "d" else 1
        cell = walk[0:FH, col * FW:(col + 1) * FW].copy()
    neck, top = s["neck"], s["top"]
    frames = []
    for chest, head in SLEEP_BREATH:
        body = cell.copy()
        if chest:
            body[neck - 1:top] = cell[neck:top + 1]
        if head:
            hl = np.zeros_like(cell); hl[:neck - 2] = cell[1:neck - 1]
            body[:neck - 1] = 0
            over(body, hl)
            body[neck - 2] = body[neck - 1] if chest else cell[neck - 1]
        out = np.zeros((FH, CW, 4), dtype=np.uint8)
        out[:, OX:OX + FW] = body
        frames.append(out)
    if view == "r":
        frames = [f[:, ::-1].copy() for f in frames]
    return frames


def view_body(walk, rig_dir, name, view, rig):
    if view == "l":
        sheet = np.array(Image.open(os.path.join(rig_dir, f"npc_{name}_side.png")).convert("RGBA"))
        return sheet[:, :FW].copy()
    col = 0 if view == "d" else 1
    cell = walk[0:FH, col * FW:(col + 1) * FW].copy()
    if BARE.get(name) is not None:   # the standing frame before the walk's fists were drawn
        cell = BARE[name][:, col * FW:(col + 1) * FW].copy()
    fill = rig.get("fill_sides", False)
    fill = (view in fill) if isinstance(fill, tuple) else fill
    if rig.get("fill_tone") and fill:
        fill = rig["fill_tone"]
    body = body_without_arms(cell, rig[view]["arms"], hexc(rig["pal"]["line"]), fill,
                             rig.get("fill_span"))
    # an edge of the clothes carried straight up from a row below (Job's overalls run up
    # his sides behind the arms)
    for (x0, x1, y0, y1, src) in rig.get("carry_up", {}).get(view, []):
        for y in range(y0, y1 + 1):
            body[y, x0:x1 + 1] = body[src, x0:x1 + 1]
    return body


def render(walk, rig_dir, name, act, view):
    act = ALIAS.get(act, act)
    if act == "sleep":
        return render_sleep(walk, name)
    rig = RIGS[name]
    if act in rig.get("breathe", ()):
        return render_breath(walk, rig_dir, name, view)
    pal = {k: hexc(v) for k, v in rig["pal"].items()}
    base = view_body(walk, rig_dir, name, "l" if view in "lr" else view, rig)
    v = "l" if view in "lr" else view
    frames = []
    specs = rig.get("override", {}).get(f"{act} {v}", ACTIVITIES[act][v])
    for spec in specs:
        cell = np.zeros((FH, CW, 4), dtype=np.uint8)
        bob = spec.get("bob", 0)
        hip = rig["hip"][v]
        # breathing and leaning move the body above the hips; the legs stay planted
        body = base.copy()
        if bob:
            upper = base.copy(); upper[hip:] = 0
            body = base.copy(); body[:hip] = 0
            shifted_upper = np.zeros_like(base); shifted_upper[bob:] = upper[:FH - bob]
            over(body, shifted_upper)
        back_layer = np.zeros_like(cell)
        front_layer = np.zeros_like(cell)
        arms_back = np.zeros_like(cell)
        arms_front = np.zeros_like(cell)
        hands = {}
        if v in "du":
            for side, elbow in (("L", -1), ("R", 1)):
                sx, sy = rig[v][side]
                dx, dy = spec[side]
                if dy >= 6:
                    dy += rig.get("hang", 0)   # long arms hang (and rest low) further down
                    if rig.get("hang") and abs(dx) <= 1:
                        dx = 0   # and straight: a one-pixel kink near the hand reads as a bump
                sh = (sx + OX, sy + bob)
                hd = (sx + OX + dx, sy + bob + dy)
                hands[side] = hd
                # on the back view, hands in front of the body are hidden behind it
                hidden = side in spec.get("hide", ())   # hands behind the back, or in front when seen from behind
                if v == "u" and rig.get("u_center_rule"):
                    # an arm hanging at the side stays in view over the coat; only a hand
                    # brought in front of the body (near its middle) goes out of sight
                    in_front = dy > -4 and abs(sx + dx - 12) <= 4
                else:
                    in_front = v == "u" and dy > -4 and abs(dx) < 4
                target = arms_back if (in_front or hidden) else arms_front
                draw_arm(target, sh, hd, elbow, pal, width=rig.get("arm_w", 2))
                if v == "u" and (in_front or hidden) and rig.get("keep_hidden_sleeve"):
                    # a wide sleeve still hangs at the side when its hand is out of sight in
                    # front: the standing frame's own sleeve is put back on that side
                    col = 1
                    src = (BARE[name] if BARE.get(name) is not None else walk)[0:FH, col * FW:(col + 1) * FW]
                    x0, x1, y0, y1 = rig["u"]["arms"][0 if side == "L" else 1]
                    piece = np.zeros_like(body)
                    piece[y0:y1 + 1, x0:x1 + 1] = src[y0:y1 + 1, x0:x1 + 1]
                    if bob:
                        moved = np.zeros_like(piece); moved[bob:] = piece[:FH - bob]; piece = moved
                    over(body, piece)
        else:
            nx, ny = rig["l"]["N"]
            fx, fy = rig["l"]["F"]
            if "F" in spec:
                dx, dy = spec["F"]
                hands["F"] = (fx + OX + dx, fy + bob + dy)
                draw_arm(arms_back, (fx + OX, fy + bob), hands["F"], -1, pal, width=rig.get("arm_w", 2))
                arms_back = darken(arms_back)
            dx, dy = spec["N"]
            if dy >= 6:
                dy += rig.get("hang", 0)
            hands["N"] = (nx + OX + dx, ny + bob + dy)
            el = spec.get("N_elbow")
            el = (nx + OX + el[0], ny + bob + el[1]) if el else None
            draw_arm(arms_front, (nx + OX, ny + bob), hands["N"], 1 if dx >= 0 else -1, pal, width=rig.get("arm_w", 2), elbow=el)
        for (pname, hand, pdx, pdy, layer) in spec.get("props", []):
            hx, hy = hands[hand]
            target = front_layer if layer == "front" else back_layer
            blit(target, PROPS[pname], hx + pdx, hy + pdy)
        if "drops" in spec:
            t, dx0 = spec["drops"]
            hx, hy = hands["L" if v in "du" else "N"]
            base_x = hx + (-9 if v == "l" else 0)
            for i in range(3):
                k = (t + i * 2) % 6
                put(front_layer, base_x - (k if v == "l" else 0) - (2 if v == "u" else 0), hy + 2 + k, hexc(PROP_PAL["s"]))
        mid_layer = np.zeros_like(cell)
        for (pname, px, py, layer) in spec.get("fixed", []):
            target = {"front": front_layer, "back": back_layer, "mid": mid_layer}[layer]
            blit(target, PROPS[pname], OX + px, py)
        over(cell, back_layer)
        over(cell, arms_back)
        body_cell = np.zeros_like(cell); body_cell[:, OX:OX + FW] = body
        over(cell, body_cell)
        over(cell, mid_layer)
        over(cell, arms_front)
        over(cell, front_layer)
        frames.append(cell)
    if view == "r":
        frames = [f[:, ::-1].copy() for f in frames]
    return frames


if __name__ == "__main__":
    WALK, RIG, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(OUT, exist_ok=True)
    for name in sys.argv[4:]:
        walk = np.array(Image.open(os.path.join(WALK, f"npc_{name}.png")).convert("RGBA"))
        bare_path = os.path.join(WALK, f"npc_{name}_bare.png")
        BARE[name] = np.array(Image.open(bare_path).convert("RGBA")) if os.path.exists(bare_path) else None
        labels = list(ROWS[name])
        # every activity in every direction; the published rows keep their places at the top
        # labels that are the same activity under another name (Merrow's valve_d and valve_l
        # are both the valve) get their missing directions once, under the first name
        done_acts = set()
        for act in dict.fromkeys(l.split()[0] for l in ROWS[name]):
            canon = ALIAS.get(act, act)
            if canon in done_acts:
                continue
            done_acts.add(canon)
            have = {l.split()[1] for l in labels if ALIAS.get(l.split()[0], l.split()[0]) == canon}
            for d in DIRS:
                lab = f"{act} {d}"
                if d not in have and lab not in labels:
                    labels.append(lab)
        if "sleep" in RIGS[name] and "sleep d" not in labels:
            labels.append("sleep d")   # in bed, seen from above: one direction
        sheet = np.zeros((FH * len(labels), CW * 4, 4), dtype=np.uint8)
        for r, lab in enumerate(labels):
            act, d = lab.split()
            for f, cell in enumerate(render(walk, RIG, name, act, d)):
                sheet[r * FH:(r + 1) * FH, f * CW:(f + 1) * CW] = cell
        Image.fromarray(sheet).save(os.path.join(OUT, f"npc_{name}_act.png"))
        with open(os.path.join(OUT, f"npc_{name}_act_rows.txt"), "w") as fh:
            fh.write("\n".join(labels) + "\n")
        print(name, len(labels), "rows")
