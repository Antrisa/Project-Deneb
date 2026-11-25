"""Mess hall and shop furniture (Zachary, 24 Nov: the mess hall redone in the new style), drawn with lit_props.py's light:
the serving counter with its food wells, the long mess table set with trays, and the menu board.
    python3 tools/dev/prop_art/mess_props.py art/lunar"""
import sys, os, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lit_props import Lit, R, FRAME, BRASS, RUB, DARKM, CREAM, GLOW, TEALG, CYAN, LEAF, TOM, PIPE

WOOD = R("ffdc9e", "eeb066", "c8803f", "975634", "663626", "432226")
STEW = R("ffd09a", "f59a4a", "cc6430", "8e3e2a")
PEAS = R("e8ffa8", "a8dc5c", "6ea83e", "40703a")
MASH = R("fffbe8", "f4e6c0", "dcc490", "a89070")
BOARD = R("4f7a6c", "3c5f56", "2e4846", "223636")
CHALK = np.array([236, 240, 224])


# ---- hand-painted finishing (Zachary, 24 Nov: "make sure the new assets follow the art style and have depth and
# detail"). The light gives the shapes; these paint the C-style detail on top with exact ramp colours, no dither:
# cabinet doors and drawers with a lit top-left bevel and a dark bottom-right one, brass handles, wood grain, the
# lit lip along a top's front edge and the shadow under it, a dark kick plate.
def _c(ramp, i):
    return np.asarray(ramp[max(0, min(len(ramp) - 1, i))], np.uint8)


def body(img, x0, y0, x1, y1, ramp, grain=False, seed=1):
    """A front face: lit top row, a darker band at the foot, the right-hand column in shade."""
    img[y0:y1 + 1, x0:x1 + 1, :3] = _c(ramp, 2)
    img[y0, x0:x1 + 1, :3] = _c(ramp, 1)
    img[y1 - 1, x0:x1 + 1, :3] = _c(ramp, 3)
    img[y1, x0:x1 + 1, :3] = _c(ramp, 4)
    img[y0 + 1:y1, x1, :3] = _c(ramp, 3)
    if grain:
        g = np.random.default_rng(seed)
        for _ in range((x1 - x0) * (y1 - y0) // 18):
            x, y, L = g.integers(x0 + 1, x1 - 2), g.integers(y0 + 2, y1 - 2), g.integers(2, 6)
            img[y, x:min(x1 - 1, x + L), :3] = _c(ramp, 3)


def panel(img, x0, y0, x1, y1, ramp, handle=None, knob=BRASS):
    """An inset door or drawer: lit top and left edge, dark bottom and right edge, a handle."""
    img[y0:y1 + 1, x0:x1 + 1, :3] = _c(ramp, 2)
    img[y0, x0:x1 + 1, :3] = _c(ramp, 4); img[y0:y1 + 1, x0, :3] = _c(ramp, 4)        # the recess's shadowed rim
    img[y0 + 1, x0 + 1:x1, :3] = _c(ramp, 3)
    img[y1, x0:x1 + 1, :3] = _c(ramp, 1); img[y0:y1 + 1, x1, :3] = _c(ramp, 1)        # its lit far rim
    if handle == 'bar':
        cx, cy = (x0 + x1) // 2, y0 + 3
        img[cy, cx - 3:cx + 3, :3] = _c(knob, 1); img[cy + 1, cx - 3:cx + 3, :3] = _c(knob, 3)
    elif handle == 'knob':
        cx, cy = x1 - 3, (y0 + y1) // 2
        img[cy, cx, :3] = _c(knob, 0); img[cy, cx + 1, :3] = _c(knob, 2); img[cy + 1, cx:cx + 2, :3] = _c(knob, 3)


def lip(img, x0, x1, y, ramp):
    """The front edge of a top: a bright lit line, then the shadow it throws on the face below."""
    img[y, x0:x1 + 1, :3] = _c(ramp, 0)
    img[y + 1, x0:x1 + 1, :3] = _c(ramp, 1)
    img[y + 2, x0:x1 + 1, :3] = _c(ramp, 4)


def kick(img, x0, x1, y0, y1):
    img[y0:y1 + 1, x0:x1 + 1, :3] = _c(DARKM, 3)
    img[y0, x0:x1 + 1, :3] = _c(DARKM, 2)


def doors(img, x0, y0, x1, y1, ramp, n, handle='knob', gap=2):
    w = (x1 - x0 + 1 - gap * (n - 1)) // n
    for k in range(n):
        a = x0 + k * (w + gap)
        panel(img, a, y0, a + w - 1, y1, ramp, handle)


def serving_counter():
    s = Lit(72, 52)
    # front face: warm steel panels, a brass trim along the top, a dark kick plate
    s.face(1, 24, 70, 50, 6, FRAME)
    for x in (24, 48):
        for y in range(27, 47):
            s.put(x, y, (-0.7, 0.3, 0.6), 6, FRAME, 0, False, -0.25)
            s.put(x + 1, y, (0.7, 0.3, 0.6), 6, FRAME, 0, False, 0.1)
    s.face(1, 47, 70, 50, 5, RUB)
    s.slab(0, 22, 71, 25, 9, BRASS, 1, 0.6)
    # the counter top and three food wells
    s.slab(0, 8, 71, 22, 8, FRAME, 1, 0.4, 0.05)
    g = np.random.default_rng(5)
    for (x0, food) in ((4, STEW), (27, PEAS), (50, MASH)):
        s.slab(x0, 11, x0 + 17, 20, 6, PIPE, 1, 0.8, -0.1)
        for k in range(22 if food is PEAS else 7):
            if food is PEAS:
                s.dome(x0 + 3 + g.uniform(0, 12), 14 + g.uniform(0, 4), 1.4, 1.3, 6.5, 1, food, 0.8)
            else:
                s.dome(x0 + 4 + g.uniform(0, 10), 14 + g.uniform(0, 4), 3.4, 2.4, 6.5, 1.4, food, 0.6)
        s.slab(x0 + 13, 9, x0 + 14, 15, 9, PIPE, 0, 0.9)                         # a ladle handle
        s.dome(x0 + 13.5, 16, 2.2, 1.6, 8, 1, PIPE, 0.9)
    # sneeze guard on the cook's side: brass posts, a glass top, a warm heat-lamp strip
    for x in (2, 35, 68):
        s.slab(x, 0, x + 1, 10, 13, BRASS, 0, 0.8)
    s.slab(1, 0, 70, 4, 14, TEALG, 1, 0.9, 0.15)
    s.slab(6, 5, 65, 6, 13, GLOW, 0, 0.3, 0.3)
    img = s.render()
    for k in range(0, 60, 14):
        for j in range(3):
            if 0 <= 1 + j < 4: img[1 + j, 6 + k + j, :3] = (255, 255, 240)
    body(img, 1, 26, 70, 46, FRAME)
    doors(img, 4, 29, 67, 44, FRAME, 3, 'bar')
    for x in range(8, 64, 4):                            # a vent strip along the foot
        img[45, x:x + 2, :3] = _c(FRAME, 4)
    kick(img, 1, 70, 47, 50)
    return img


def mess_table():
    s = Lit(54, 34)
    for x in (3, 47):                                   # legs
        s.face(x, 24, x + 3, 32, 2, DARKM)
    s.face(1, 19, 52, 24, 6, WOOD)                       # the table's front edge
    s.slab(0, 0, 53, 19, 7, WOOD, 1, 0.35, 0.05)
    for y in (6, 13):                                    # plank seams
        for x in range(2, 52):
            s.put(x, y, (0, -0.6, 0.8), 7, WOOD, 0, False, -0.25)
    # two trays, each with a bowl, a cup and a bread roll
    for (tx, food) in ((5, STEW), (30, PEAS)):
        s.slab(tx, 3, tx + 18, 15, 8, PIPE, 1, 0.7)
        s.dome(tx + 6, 9, 4.2, 3.4, 8.5, 2.2, CREAM, 0.7)
        s.dome(tx + 6, 8.6, 3, 2.3, 10.5, 0.8, food, 0.7)
        s.dome(tx + 14, 7, 2.2, 2.2, 8.5, 3, R("e8f6ff", "a8d8f0", "70a8d0", "4a7aa8"), 0.9)
        s.dome(tx + 14, 12, 2.6, 1.8, 8.5, 1.6, WOOD, 0.4, 0.15)
    img = s.render()
    body(img, 1, 19, 52, 24, WOOD, True, 3)
    lip(img, 1, 52, 18, WOOD)
    for x in (3, 47):                                    # legs: lit left side, shaded right
        img[25:33, x, :3] = _c(DARKM, 1); img[25:33, x + 1:x + 3, :3] = _c(DARKM, 2); img[25:33, x + 3, :3] = _c(DARKM, 3)
    return img


def menu_board():
    s = Lit(50, 72)
    for x in (6, 40):                                    # stand legs
        s.face(x, 52, x + 3, 71, 2, WOOD)
    s.slab(0, 4, 49, 56, 6, WOOD, 2, 0.4)                # frame
    s.face(4, 8, 45, 52, 5, BOARD)                       # chalkboard
    s.slab(2, 56, 47, 59, 6, WOOD, 1, 0.3)               # chalk ledge
    s.dome(10, 56.5, 2.5, 1, 7, 0.6, CREAM, 0.3)
    s.slab(16, 0, 33, 4, 7, BRASS, 1, 0.7)               # a little lamp on top
    s.dome(24.5, 4, 6, 2.2, 7, 1, GLOW, 0.4, 0.2)
    img = s.render()
    def chalk(x0, x1, y, gap=5):
        for x in range(x0, x1):
            if (x - x0) % gap != gap - 1: img[y, x, :3] = CHALK
    for x in range(12, 38):
        if x % 4 != 3: img[12, x, :3] = (255, 214, 120); img[13, x, :3] = (232, 176, 90)
    for i, y in enumerate((20, 27, 34, 41)):
        chalk(8, 30 + (i * 3) % 7, y, 6 - i % 2)
        img[y, 36:40, :3] = (255, 214, 120)
    # a bowl doodle
    for x in range(30, 41):
        img[48, x, :3] = CHALK
    for k in range(5):
        img[47 - k // 2, 30 + k, :3] = CHALK; img[47 - k // 2, 40 - k, :3] = CHALK
    for k in range(3):
        img[44 - k, 33 + k * 2, :3] = (210, 220, 210)
    return img


SILK = [R("ffd6f0", "f08ac8", "c0509a", "7e3070"), R("d8f4ff", "7cc8f0", "3e8ac8", "2a5a8e"),
        R("fff0b0", "f4c850", "c88a2a", "8a5226"), R("dcffd0", "8ad870", "4e9a44", "2e6036")]
STEELB = R("e8f0f8", "b8c8dc", "8496b4", "5c6a8c", "3e4766", "2a2e48")


def counter_front(s, w, z=6, ramp=WOOD):
    """A shop counter's body: a lit top with a front face, panels and a kick plate (w pixels wide, 52 tall)."""
    s.face(1, 26, w - 2, 50, z, ramp)
    for x in range(12, w - 8, 22):
        for y in range(30, 46):
            s.put(x, y, (-0.7, 0.3, 0.6), z, ramp, 0, False, -0.25)
            s.put(x + 1, y, (0.7, 0.3, 0.6), z, ramp, 0, False, 0.1)
    s.face(1, 47, w - 2, 50, z - 1, DARKM)
    s.slab(0, 10, w - 1, 26, z + 2, ramp, 1, 0.45, 0.05)


def finish_counter(img, w, ramp, n=3, handle='knob', grain=True):
    body(img, 1, 26, w - 2, 46, ramp, grain)
    lip(img, 1, w - 2, 25, ramp)
    doors(img, 4, 30, w - 5, 44, ramp, n, handle)
    kick(img, 1, w - 2, 47, 50)


def fabric_counter():
    """Sesska's counter: bolts of bug silk, a folded stack and a spool on a warm wood top."""
    s = Lit(72, 52)
    counter_front(s, 72)
    for k, col in enumerate(SILK):                       # bolts of cloth lying along the top
        y = 12 + (k % 2) * 6; x0 = 4 + k * 9
        s.tube([(x0, y + 2), (x0 + 16, y + 2)], 3.2, 9, col, 0.6)
    s.slab(44, 13, 58, 18, 10, SILK[0], 1, 0.4)
    s.slab(45, 18, 59, 22, 10, SILK[1], 1, 0.4)
    s.dome(65, 15, 3.5, 3.5, 9, 3, BRASS, 0.8)
    s.dome(65, 15, 1.4, 1.4, 12, 1, CREAM, 0.6)
    img = s.render()
    finish_counter(img, 72, WOOD, 3, 'bar')
    for x in range(8, 64, 3):                            # a tape measure hanging over the front edge
        img[27, x, :3] = (248, 216, 96) if x % 6 else (120, 70, 40)
    return img


def arms_counter():
    """Ix'ali's counter: a steel case with a glass top over blades and a blaster on felt."""
    s = Lit(72, 52)
    counter_front(s, 72, 6, STEELB)
    s.slab(3, 11, 68, 24, 8, R("7a3048", "5c2440", "421c34", "2e1426"), 1, 0.1)      # felt bed
    s.tube([(8, 15), (30, 19)], 1.4, 9, STEELB, 1.0)                                   # a blade
    s.slab(30, 17, 34, 21, 9.5, BRASS, 1, 0.8)
    s.tube([(42, 15), (52, 15)], 2.2, 9, DARKM, 0.9)                                    # a blaster
    s.slab(52, 13, 57, 21, 9.5, DARKM, 1, 0.6)
    s.dome(46, 15, 1.2, 1.2, 11, 0.5, CYAN, 1, 0.2)
    s.tube([(14, 21), (24, 21)], 1, 9, BRASS, 0.9)                                     # a dagger
    img = s.render()
    finish_counter(img, 72, STEELB, 3, 'knob', False)
    for x in range(4, 68):                               # the glass lid: a pale rim and two glints
        img[11, x, :3] = (220, 244, 250)
    for k in range(8):
        for j in (0, 1):
            img[13 + k, 20 + k + j * 26, :3] = (236, 250, 255)
    return img


def side_counter():
    """One length of Bram's counter, seen end-on: it runs north to south down the middle of his shop."""
    s = Lit(26, 50)
    s.face(2, 40, 23, 49, 5, WOOD)                       # the near end
    s.slab(1, 0, 24, 40, 7, WOOD, 1, 0.4, 0.05)          # the long top
    for y in range(4, 38):
        s.put(4, y, (-0.6, 0, 0.8), 7, WOOD, 0, False, -0.2)
    g = np.random.default_rng(9)
    for y in (6, 20, 32):                                # jars and a tin on it
        s.dome(9 + g.uniform(-1, 1), y, 3, 2.6, 8, 4, R("e8f8ff", "a8d8ea", "6aa8c8", "3e6e94"), 1.0)
        s.dome(9, y - 1.5, 2.2, 1.2, 12, 0.8, [SILK[2], TOM, PEAS][int(y) % 3], 0.6)
        s.dome(18, y + 2, 2.4, 2.4, 8, 3, BRASS, 0.8)
    img = s.render()
    body(img, 2, 41, 23, 46, WOOD, True, 5)
    lip(img, 2, 23, 40, WOOD)
    panel(img, 5, 43, 20, 46, WOOD, 'bar')
    kick(img, 2, 23, 47, 49)
    for y in range(2, 38, 3):                            # wood grain along the top
        img[y, 6 + (y * 7) % 11:9 + (y * 7) % 11, :3] = _c(WOOD, 3)
    return img


def weapon_rack():
    """A wall rack in the armoury: two blasters and a blade hung on pegs, a shelf of charge packs below."""
    s = Lit(70, 76)
    for x in (4, 63):
        s.face(x, 6, x + 3, 74, 3, DARKM)
    s.face(6, 4, 63, 60, 2, R("6a4a56", "553a48", "40303c", "2e2230"))               # back board
    for y in (6, 30, 54):
        s.slab(4, y, 66, y + 3, 6, STEELB, 1, 0.6)
    for (x0, x1, y) in ((10, 34, 16), (38, 60, 16)):     # blasters
        s.tube([(x0, y), (x1, y)], 2.6, 8, DARKM, 0.9)
        s.slab(x1 - 6, y, x1 - 1, y + 8, 8.5, DARKM, 1, 0.5)
        s.dome(x0 + 6, y, 1.2, 1.2, 10.5, 0.5, CYAN, 1, 0.2)
    s.tube([(12, 42), (54, 42)], 1.6, 8, STEELB, 1.0)    # a blade
    s.slab(52, 39, 58, 45, 9, BRASS, 1, 0.8)
    s.face(8, 57, 61, 70, 6, STEELB)                     # shelf of charge packs
    for x in range(12, 58, 8):
        s.slab(x, 59, x + 5, 66, 8, R("fff0c0", "ffd060", "e09a30", "a86020"), 1, 0.6)
    img = s.render()
    board = R("7a5866", "6a4a56", "553a48", "40303c", "2e2230")
    for y in range(8, 56, 4):                            # pegboard holes where nothing hangs
        for x in range(10, 62, 4):
            if s.z[y, x] <= 2.5 and s.z[y + 1, x] <= 2.5: img[y, x, :3] = _c(board, 4); img[y + 1, x, :3] = _c(board, 1)
    body(img, 8, 57, 61, 70, STEELB)
    for x in range(12, 58, 8):
        img[59:67, x:x + 6, :3] = _c(R("fff0c0", "ffd060", "e09a30", "a86020", "6a3a20"), 2)
        img[59, x:x + 6, :3] = (255, 240, 192); img[59:67, x + 5, :3] = (168, 96, 32); img[66, x:x + 6, :3] = (106, 58, 32)
        img[62, x + 1:x + 4, :3] = (60, 40, 50)
    return img


STONE = R("fbf2e6", "e4d4c0", "bfa894", "8e7a74", "605262", "3e3448")
CLOTH = R("f0e0ff", "b890e8", "8460c0", "5a3e8e", "3a2a62")


def altar():
    """The quiet room's altar: a stone table under a long cloth, candles, a bowl of flowers and a silver moon."""
    s = Lit(74, 60)
    s.face(2, 34, 71, 58, 5, STONE)
    for x in range(8, 66, 14):                           # carved panels
        for y in range(38, 54):
            s.put(x, y, (-0.7, 0.2, 0.6), 5, STONE, 0, False, -0.2)
    s.slab(0, 20, 73, 34, 8, STONE, 1, 0.4)
    s.slab(24, 20, 49, 34, 8.5, CLOTH, 1, 0.3)            # the runner down the middle
    s.face(25, 35, 48, 52, 7, CLOTH)
    for y in range(38, 50, 4):
        for x in range(27, 47):
            if (x + y) % 6 < 2: s.put(x, y, (0, 0.2, 0.9), 7, BRASS, 0.5)
    s.dome(37, 9, 8, 8, 10, 3, R("ffffff", "eef2ff", "c8d0ec", "98a0c8", "6a6e98"), 0.9)   # the moon disc
    s.dome(40, 7, 4, 4, 12.5, 1.2, R("eef2ff", "c8d0ec", "98a0c8"), 0.6, -0.1)
    s.face(35, 16, 38, 22, 9, BRASS)
    for x in (8, 18, 56, 66):                            # candles in brass cups
        s.slab(x - 2, 23, x + 2, 26, 9, BRASS, 1, 0.8)
        s.face(x - 1, 14, x + 1, 23, 9, CREAM)
        s.dome(x, 12, 1.4, 2.2, 11, 1, GLOW, 1, 0.3)
    s.dome(60, 28, 4, 3, 9, 3, LEAF, 0.4)
    for (fx, fy) in ((58, 26), (61, 27), (59, 29), (63, 28)):
        s.dome(fx, fy, 1.4, 1.4, 12, 1, R("ffe0f0", "f8a0d0", "d060a0", "903070"), 0.6)
    img = s.render()
    body(img, 2, 35, 71, 55, STONE)
    lip(img, 2, 71, 34, STONE)
    for (a, b) in ((6, 20), (53, 67)):                   # carved stone panels either side of the runner
        panel(img, a, 39, b, 52, STONE)
        img[45, a + 4:b - 3, :3] = _c(STONE, 3); img[46, a + 4:b - 3, :3] = _c(STONE, 1)
    body(img, 25, 35, 48, 54, CLOTH)                     # the runner hanging down the front
    for y in range(38, 52, 3):
        for x in range(28, 46):
            if (x + y) % 4 == 0: img[y, x, :3] = _c(BRASS, 1)
    img[53, 25:49:2, :3] = _c(BRASS, 2)                  # fringe
    kick(img, 2, 71, 56, 58)
    return img


def candle_stand():
    """A tall brass candle stand, three candles lit."""
    s = Lit(24, 52)
    s.dome(12, 48, 7, 3, 1, 2, BRASS, 0.9)
    s.slab(11, 16, 13, 47, 4, BRASS, 0, 0.9)
    s.tube([(3, 16), (21, 16)], 1.4, 5, BRASS, 0.9)
    for x in (4, 12, 20):
        s.face(x - 1, 8, x + 1, 15, 6, CREAM)
        s.dome(x, 6, 1.3, 2.2, 8, 1, GLOW, 1, 0.3)
    return s.render()


IRON = R("d8dcec", "a4a8c4", "767a9a", "50526e", "34344c", "222234")


def anvil():
    """Ix'ali's arc-anvil on a squat stand, a hammer resting on it, the face still warm."""
    s = Lit(28, 30)
    s.face(8, 18, 19, 28, 3, DARKM)                      # the stand
    s.slab(5, 26, 22, 29, 1, DARKM, 1, 0.3)
    s.slab(2, 8, 25, 13, 8, IRON, 1, 0.9)                 # the face, with a horn to the left
    s.face(6, 14, 21, 17, 7, IRON)
    s.dome(3, 10.5, 3, 2.4, 8, 2, IRON, 0.9)
    s.slab(13, 9, 21, 11, 9, R("fff0b0", "ffb050", "e06a30", "9a3a28"), 0, 0.6, 0.15)   # glowing where it was struck
    s.slab(6, 2, 9, 8, 10, WOOD, 1, 0.5)                  # the hammer
    s.slab(3, 0, 12, 3, 11, IRON, 1, 0.9)
    img = s.render()
    body(img, 6, 14, 21, 17, IRON)
    return img


def fitting_stool():
    """Sesska's fitting stool: a low round dais with a brass rim, for standing on while she pins hems."""
    s = Lit(26, 20)
    s.face(2, 9, 23, 18, 2, WOOD)
    for y in range(1, 15):                               # the round top, flat, seen from above and in front
        for x in range(1, 25):
            u, v = (x + 0.5 - 13) / 12, (y + 0.5 - 8) / 6.5
            d = u * u + v * v
            if d <= 1:
                s.put(x, y, (u * 0.3 if d > 0.7 else 0, v * 0.3 if d > 0.7 else 0, 1), 5, BRASS if d > 0.72 else WOOD,
                      0.6 if d > 0.72 else 0.2)
    img = s.render()
    body(img, 2, 15, 23, 18, WOOD)
    for y in range(4, 12, 3):                            # grain on the top
        img[y, 8 + y % 5:13 + y % 5, :3] = _c(WOOD, 3)
    return img


# ---- the library (25 Nov) ----------------------------------------------------------------------------------------
DARKWOOD = R("e8b088", "b77a5a", "8a5244", "613a3c", "43283a", "2e1c2e")
BOOKS = [R("ffb4a0", "e8584a", "a83440", "6e2234"), R("b8e0ff", "5a9ae0", "34609e", "243e6a"),
         R("e8ffb0", "8cc85a", "4e8a40", "305830"), R("fff0b0", "f0c050", "b88030", "7a5028"),
         R("f0d0ff", "b080e0", "7850a8", "4c3474"), R("ffe0c8", "e8a070", "b06a48", "744036"),
         R("e0f0f0", "a8c4c8", "72888e", "4a5862")]


def _books(img, x0, x1, y_floor, height, seed):
    """A row of book spines standing on a shelf: lit left edge, dark right edge, a title band, the odd one leaning."""
    g = np.random.default_rng(seed)
    x = x0
    while x <= x1 - 2:
        w = int(g.integers(2, 5))
        if x + w > x1 + 1: w = x1 + 1 - x
        h = int(height - g.integers(0, 4))
        ramp = BOOKS[int(g.integers(0, len(BOOKS)))]
        if g.random() < 0.08:            # a gap, or a book lying flat
            if g.random() < 0.5:
                img[y_floor - 2:y_floor + 1, x:min(x1 + 1, x + 6), :3] = _c(ramp, 2)
                img[y_floor - 2, x:min(x1 + 1, x + 6), :3] = _c(ramp, 1)
                img[y_floor, x:min(x1 + 1, x + 6), :3] = _c(ramp, 3)
            x += 4
            continue
        top = y_floor - h + 1
        img[top:y_floor + 1, x:x + w, :3] = _c(ramp, 2)
        img[top:y_floor + 1, x, :3] = _c(ramp, 1)
        img[top:y_floor + 1, x + w - 1, :3] = _c(ramp, 3)
        img[top, x:x + w, :3] = _c(ramp, 1)
        band = top + 2 + int(g.integers(0, 3))
        if band < y_floor - 1:
            img[band, x:x + w, :3] = _c(BRASS, 1) if g.random() < 0.5 else _c(ramp, 0)
        x += w


def library_shelf(seed=3, ramp=WOOD, rows=4):
    """A tall wooden bookcase, four shelves of books, a carved top."""
    s = Lit(72, 78)
    s.face(1, 6, 70, 77, 3, ramp)
    s.slab(0, 0, 71, 6, 6, ramp, 1, 0.5)                   # the crown
    img = s.render()
    body(img, 1, 7, 70, 76, ramp)
    for x0, x1 in ((1, 4), (67, 70)):                      # side posts: lit on the left
        img[7:77, x0:x1 + 1, :3] = _c(ramp, 2); img[7:77, x0, :3] = _c(ramp, 1); img[7:77, x1, :3] = _c(ramp, 3)
    inner = R(*["%02x%02x%02x" % tuple(int(v * 0.62) for v in ramp[i]) for i in range(len(ramp))])
    for k in range(rows):
        y0 = 9 + k * 17
        img[y0:y0 + 14, 5:67, :3] = _c(inner, 3)           # the back of the shelf, in shadow
        img[y0, 5:67, :3] = _c(inner, 4)
        _books(img, 6, 65, y0 + 12, 12, seed * 10 + k)
        img[y0 + 13, 5:67, :3] = _c(ramp, 1)              # the shelf board, lit edge
        img[y0 + 14, 5:67, :3] = _c(ramp, 3)
        img[y0 + 15, 5:67, :3] = _c(ramp, 4)
    img[76, 1:71, :3] = _c(ramp, 4)
    return img


def archive_shelf():
    """The archive: dark old wood behind glass doors, scroll tubes and boxes, a brass plaque."""
    img = library_shelf(7, DARKWOOD, 4)
    glass = np.array([200, 236, 240])
    for x0 in (6, 37):                                     # two glass doors over the shelves
        for y in range(9, 74):
            for x in range(x0, x0 + 29):
                img[y, x, :3] = (img[y, x, :3] * 0.72 + glass * 0.28).astype(np.uint8)
        img[9:74, x0, :3] = _c(BRASS, 2); img[9:74, x0 + 28, :3] = _c(BRASS, 3)
        img[9, x0:x0 + 29, :3] = _c(BRASS, 1); img[73, x0:x0 + 29, :3] = _c(BRASS, 3)
        for k in range(10):
            img[12 + k, x0 + 4 + k, :3] = (240, 252, 255)
            img[30 + k, x0 + 14 + k // 2, :3] = (220, 244, 248)
    img[40:43, 34:38, :3] = _c(BRASS, 1); img[43, 34:38, :3] = _c(BRASS, 3)      # the lock
    img[1:5, 26:46, :3] = _c(BRASS, 2); img[1, 26:46, :3] = _c(BRASS, 0); img[4, 26:46, :3] = _c(BRASS, 3)
    for x in range(28, 44, 3):
        img[2:4, x, :3] = _c(DARKWOOD, 4)
    return img


def school_desk():
    """A pupil's desk with a glowing lesson screen."""
    s = Lit(26, 30)
    for x in (3, 20):
        s.face(x, 16, x + 2, 29, 2, DARKM)
    s.face(1, 12, 24, 16, 5, WOOD)
    s.slab(0, 2, 25, 12, 6, WOOD, 1, 0.4)
    s.slab(5, 3, 20, 9, 7, RUB, 1, 0.3)
    img = s.render()
    body(img, 1, 13, 24, 16, WOOD)
    lip(img, 1, 24, 12, WOOD)
    img[4:9, 6:20, :3] = _c(CYAN, 2)
    img[4, 6:20, :3] = _c(CYAN, 1)
    for y in (5, 7):
        img[y, 8:8 + (11 if y == 5 else 7), :3] = _c(CYAN, 0)
    img[8, 6:20, :3] = _c(CYAN, 3)
    return img


def reading_table():
    """A long reading table: an open book, a stack of three, a little green-shaded lamp."""
    s = Lit(76, 32)
    for x in (4, 68):
        s.face(x, 22, x + 3, 31, 2, DARKM)
    s.face(1, 17, 74, 22, 6, WOOD)
    s.slab(0, 0, 75, 17, 7, WOOD, 1, 0.35)
    s.slab(8, 4, 30, 13, 8, CREAM, 1, 0.2)              # the open book
    s.slab(44, 3, 56, 7, 9, BOOKS[1], 1, 0.4)
    s.slab(45, 7, 57, 11, 8.5, BOOKS[0], 1, 0.4)
    s.slab(44, 11, 56, 14, 8, BOOKS[3], 1, 0.4)
    s.dome(66, 4, 5, 3, 11, 2, R("d8ffd0", "7cd890", "3e9a60", "246a40"), 0.9)   # the lamp shade
    s.slab(65, 6, 66, 12, 9, BRASS, 0, 0.8)
    s.dome(65.5, 12.5, 3, 1.5, 8, 1, BRASS, 0.8)
    img = s.render()
    body(img, 1, 18, 74, 22, WOOD)
    lip(img, 1, 74, 17, WOOD)
    img[5:12, 19, :3] = _c(CREAM, 3)                     # the open book's spine and lines of text
    for y in range(6, 12, 2):
        img[y, 10:18, :3] = _c(CREAM, 2); img[y, 21:29, :3] = _c(CREAM, 2)
    for x in (4, 68):
        img[23:32, x, :3] = _c(DARKM, 1); img[23:32, x + 1:x + 3, :3] = _c(DARKM, 2); img[23:32, x + 3, :3] = _c(DARKM, 3)
    return img


def lesson_board():
    """Owen's lesson board: a chalkboard on a stand with letters, sums and a ringed planet."""
    img = menu_board()
    board = R("4f7a6c", "3c5f56", "2e4846", "223636")
    img[9:52, 5:45, :3] = _c(board, 2)
    img[9, 5:45, :3] = _c(board, 1); img[51, 5:45, :3] = _c(board, 3)
    ch = np.array([236, 240, 224])
    A = ["010", "101", "111", "101", "101"]; B = ["110", "101", "110", "101", "110"]; C_ = ["011", "100", "100", "100", "011"]
    for i, glyph in enumerate((A, B, C_)):
        for y, row in enumerate(glyph):
            for x, c in enumerate(row):
                if c == "1": img[13 + y, 9 + i * 5 + x, :3] = ch
    for y, row in enumerate(["01000", "11011", "01000", "01011", "11100"]):        # 1+1=2, roughly
        for x, c in enumerate(row):
            if c == "1": img[22 + y, 9 + x, :3] = (255, 214, 120)
    cx, cy = 33, 22                                          # a ringed planet
    for y in range(-4, 5):
        for x in range(-4, 5):
            if 12 <= x * x + y * y <= 20: img[cy + y, cx + x, :3] = ch
    for x in range(-8, 9):
        img[cy + (x // 4), cx + x, :3] = (255, 214, 120) if abs(x) > 4 else img[cy + (x // 4), cx + x, :3]
    for x in range(9, 40, 1):                                # a line of "writing"
        if x % 5 != 4: img[34, x, :3] = ch
        if x % 4 != 3 and x < 30: img[40, x, :3] = ch
    return img


def lumen_fern():
    """A potted luminescent fern from the east domes, its fronds glowing a soft teal."""
    s = Lit(28, 40)
    s.face(7, 28, 20, 39, 3, R("f0b090", "d07a58", "a0523e", "6e3432"))         # the pot
    s.slab(5, 24, 22, 29, 5, R("f8c8a0", "e08a60", "b05c40", "783a34"), 1, 0.4)
    fr = R("e8fff8", "9ef0e0", "4cc8c0", "2e8a9a", "245e78")
    g = np.random.default_rng(5)
    for k in range(9):                                     # fronds arching out of the pot
        ang = -math.pi / 2 + (k - 4) * 0.33
        for t in np.linspace(0, 1, 9):
            x = 13.5 + math.cos(ang) * 13 * t + (k - 4) * t * t * 1.5
            y = 25 + math.sin(ang) * 20 * t + 9 * t * t
            s.dome(x, y, 1.5 - t * 0.6, 1.2, 6 + t, 1, fr, 0.6)
    img = s.render()
    body(img, 7, 30, 20, 39, R("f0b090", "d07a58", "a0523e", "6e3432", "4e2a2e"))
    return img


def lumen_fern_glow():
    yy, xx = np.mgrid[0:56, 0:56]
    d = np.hypot((xx - 28) / 26.0, (yy - 26) / 24.0)
    a = np.clip(1 - d, 0, 1) ** 1.6
    out = np.zeros((56, 56, 4), np.uint8)
    out[..., 0], out[..., 1], out[..., 2] = 190, 255, 240
    out[..., 3] = (a * 150).astype(np.uint8)
    return out


PROPS = (("serving_counter", serving_counter), ("mess_table", mess_table), ("menu_board", menu_board),
         ("fabric_counter", fabric_counter), ("arms_counter", arms_counter), ("side_counter", side_counter),
         ("weapon_rack", weapon_rack), ("altar", altar), ("candle_stand", candle_stand),
         ("anvil", anvil), ("bench_fitting", fitting_stool),
         ("library_shelf", library_shelf), ("archive_shelf", archive_shelf), ("school_desk", school_desk),
         ("reading_table", reading_table), ("lesson_board", lesson_board), ("lumen_fern", lumen_fern),
         ("lumen_fern_glow", lumen_fern_glow))
if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/r5"
    os.makedirs(out, exist_ok=True)
    for name, fn in PROPS:
        Image.fromarray(fn(), "RGBA").save(os.path.join(out, name + ".png"))
