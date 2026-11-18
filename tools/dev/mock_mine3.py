"""Round 2: compact Mine A, North Cave A without water, ten cavern layouts with depth variants."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_mine_lib import *
from PIL import Image, ImageDraw

MINE_LEG = [(HEAD, "Mine head: lockers, tool crib, Job's desk"), (LOAD, "Loading spot: ore bins + hopper"), (BELT, "Conveyor to Engineering ore processing"),
            (DIG, "Dig floor (rocks regrow overnight)"), (ROCK, "Plain rock (stone)"), (ORE_I, "Iron ore outcrop"), (ORE_C, "Copper ore outcrop"),
            (CRYST, "Crystal samples (Zaas's survey)"), (ANALY, "Ore analyzer"), (SURV, "Survey room (Zaas)"), (GATE, "Cavern gate (Vzz'ket)"),
            (NCAVE, "Passage to the North Cave"), (DOOR, "Way through / warp"), ((250, 110, 150), "Resident's usual spot")]


def mine_head(m, x0, y0, x1, y1):
    m.oct(x0, y0, x1, y1, HEAD, 3)
    m.box(x1 - 4, y0 + 3, 2, 6, (120, 130, 150)); m.box(x1 - 4, y1 - 9, 2, 6, (120, 130, 150))
    m.box(x0 + 3, y0 + 3, 5, 2, (230, 220, 200))
    m.box(x0 + 3, y1 - 5, 4, 2, CRATE); m.dot(x0 + 9, y1 - 4, LAMP)
    for i in range(2): m.box(x0 + 9 + i * 3, y0 + 3, 2, 2, ANALY)
    m.label((x0 + x1) / 2, (y0 + y1) / 2, "Mine head", F); m.person(x0 + 5, y0 + 6.5, "Job")


# ============================================================ Mine A, compact
m = Mock(106, 50, "The Mine, option A (round 2): the gallery, shortened",
         "Same plan as A, squeezed: the gallery is 38 tiles instead of 56 and the bays are deeper to keep the same amount of rock. About 68 x 48 tiles.")
m.rect(0, 0, 68, 50, ROCKBG, None); m.grid(0, 0, 68, 50)
IRON = [(14, 18), (14, 10), (20, 4), (38, 4), (44, 10), (44, 18)]
COPP = [(22, 32), (22, 40), (28, 46), (42, 46), (48, 40), (48, 32)]
m.poly(IRON, DIG); m.poly(COPP, DIG)
m.rect(26, 0, 30, 4, NCAVE)
m.oct(2, 33, 18, 46, SURV, 3); m.rect(9, 31, 13, 33, SURV)
m.rect(8, 18, 50, 32, DIG); m.poly([(8, 18), (8, 32), (4, 28), (4, 22)], DIG)
m.oct(0.5, 19, 9, 31, GATE, 2)
mine_head(m, 48, 14, 64, 36); m.rect(64, 22, 68, 28, HEAD)
m.poly([(46, 2), (62, 2), (66, 6), (66, 12), (46, 12)], LOAD); m.rect(53, 12, 57, 14, LOAD)
m.belt([(62, 7), (68, 7)]); m.box(58, 5, 4, 4, (120, 100, 70))
for i in range(3): m.box(47 + i * 3, 3, 2, 2, CRATE)
m.box(47, 8.5, 2, 2, ANALY); m.label(53, 8, "Loading spot", F)
SHAPES[:] = [IRON]; scatter(m, 15, 5, 43, 17, 34, [(ROCK, 5), (ORE_I, 3), (ORE_C, 1)], 3)
SHAPES[:] = [COPP]; scatter(m, 23, 31, 47, 45, 30, [(ROCK, 5), (ORE_C, 3), (ORE_I, 1)], 5)
SHAPES[:] = [[(8, 18), (50, 18), (50, 32), (8, 32)]]
scatter(m, 10, 19, 48, 31, 12, [(ROCK, 6), (ORE_I, 1), (ORE_C, 1)], 7, avoid=[(8, 22.5, 50, 27.5)] + [(x - 1.5, y - 1.5, x + 1.5, y + 1.5) for x in (14, 26, 38) for y in (18.6, 31.4)])
m.d.line([m.P(10, 25), m.P(48, 25)], fill=(216, 200, 170), width=int(2.6 * S)); m.label(29, 25, "Main gallery", F)
for x in (14, 26, 38): m.dot(x, 18.6, LAMP); m.dot(x, 31.4, LAMP)
m.ore(6, 37, CRYST); m.ore(14, 37, CRYST); m.box(13, 41.5, 3, 2, ANALY); m.label(10, 39, "Survey\nroom", F); m.person(4.5, 42.5, "Zaas")
m.label(4.8, 25, "Gate", F); m.person(3, 20.5, "Vzz'ket"); m.person(10, 29.3, "Ix'ali")
m.label(29, 11, "Iron bay", F); m.label(35, 39, "Copper bay", F)
for x, y in ((28, 1), (1, 25), (67, 25)): m.door(x, y)
m.legend(70, 2, MINE_LEG)
m.text(70, 34, "Walk from the mine head to the\ngate: about 45 tiles (was 64).\nNorth Cave: off the iron bay.\nCaverns: through the west gate.")
m.text(31, 0.2, "^ North Cave", WHITE); m.text(0.5, 47.5, "< Caverns", WHITE); m.text(58, 47.5, "Engineering >", WHITE)
m.save("mine_A2_compact")

# ============================================================ North Cave A, dry
NC_LEG = [(NCAVE, "Cave floor"), (PILLAR, "Rock pillar (solid)"), (ROCK, "Plain rock (stone)"), (ORE_I, "Iron bed (regrows every 2 days)"),
          (ORE_C, "Copper bed (regrows every 2 days)"), (FUNG, "Glowing fungus (light)"), (DOOR, "Back to the Mine")]


def bed(m, x, y, c, n=4, seed=1):
    r = random.Random(seed)
    m.oct(x - 2.6, y - 2.1, x + 2.6, y + 2.1, (130, 120, 112), 1.2, (90, 84, 84))
    for i in range(n): m.ore(x - 1.4 + (i % 2) * 2.8 + r.uniform(-.3, .3), y - .9 + (i // 2) * 1.9, c)


m = Mock(96, 40, "North Cave, option A (round 2): no water",
         "The pool is gone; a fourth pillar takes its place in the north-east. Four ore beds refill every two days. About 60 x 38 tiles.")
m.rect(0, 0, 62, 40, ROCKBG, None)
m.oct(4, 3, 58, 34, NCAVE, 9); m.rect(28, 34, 34, 40, NCAVE)
pil = [(18, 12, 26, 20), (36, 10, 44, 18), (28, 21, 34, 27), (46, 6, 52, 12)]
for p in pil: m.oct(*p, PILLAR, 2)
bed(m, 12, 10, ORE_I, seed=1); bed(m, 50, 24, ORE_I, seed=2); bed(m, 12, 26, ORE_C, seed=3); bed(m, 30, 7, ORE_C, seed=4)
SHAPES[:] = [octp(4, 3, 58, 34, 9)]
scatter(m, 8, 6, 55, 31, 18, [(ROCK, 1)], 31, avoid=[(a - 1, b - 1, c + 1, d + 1) for a, b, c, d in pil] + [(9, 7, 15, 13), (47, 21, 53, 27), (9, 23, 15, 29), (27, 4, 33, 10), (28, 28, 34, 34)])
for x, y in ((8, 18), (56, 18), (22, 30), (40, 30), (20, 5), (40, 4)): m.dot(x, y, FUNG, .7)
m.door(31, 39)
m.legend(64, 2, NC_LEG)
m.text(35, 38, "v The Mine", WHITE)
m.save("northcave_A2_dry")

# ============================================================ caverns: ten layouts
# Each layout is a list of shapes in tile coords inside a 30 x 22 panel:
#   ("floor", pts)  walkable cave floor (overlaps merge into one outline)
#   ("solid", pts)  pillar / stalagmite / rock mass
#   ("hole",  pts)  chasm (rock), overgrown pit (lush) or hot water (steam)
#   ("bridge", pts) plank or rock bridge over a hole
# plus up/down spots.


def tunnel(pts, w=3.0):
    """45-degree tunnel: segments as rectangles / parallelograms, joints as small octagons"""
    out = []; h = w / 2
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if y0 == y1: out.append([(min(x0, x1), y0 - h), (max(x0, x1), y0 - h), (max(x0, x1), y0 + h), (min(x0, x1), y0 + h)])
        elif x0 == x1: out.append([(x0 - h, min(y0, y1)), (x0 + h, min(y0, y1)), (x0 + h, max(y0, y1)), (x0 - h, max(y0, y1))])
        else:
            k = h * math.sqrt(2)                                     # horizontal half-width of a 45-degree band
            out.append([(x0 - k, y0), (x0 + k, y0), (x1 + k, y1), (x1 - k, y1)])
    for x, y in pts: out.append(octp(x - h, y - h, x + h, y + h, h * .6))
    return [("floor", p) for p in out]


def O(x0, y0, x1, y1, c=None, kind="floor"):
    c = c if c is not None else min(x1 - x0, y1 - y0) * .3
    return (kind, octp(x0, y0, x1, y1, c))


def L1():   # open hollow
    return dict(name="1. Open hollow", note="one big notched room",
                shapes=[("floor", [(6, 2), (14, 2), (17, 5), (24, 5), (28, 9), (28, 16), (24, 20), (8, 20), (2, 14), (2, 6)]), O(12, 9, 16, 13, kind="solid")],
                up=(6, 6), down=(24, 15))


def L2():   # twisting tunnel to an opening
    return dict(name="2. Winding tunnel", note="squeeze through, then it opens up",
                shapes=[O(1, 1, 8, 8)] + tunnel([(5, 5), (12, 5), (15, 8), (9, 14), (9, 18), (19, 18)]) + [O(17, 7, 29, 21, 4), O(21, 11, 24, 14, kind="solid")],
                up=(4.5, 4.5), down=(26, 11))


def L3():   # stalagmite hall
    sh = [O(1, 2, 29, 21, 5)]
    r = random.Random(3)
    for j, y in enumerate((7, 11.5, 16)):
        for x in ([8, 13, 18, 23] if j % 2 == 0 else [10.5, 15.5, 20.5]):
            if r.random() < .85: s = r.uniform(1.4, 2.2); sh.append(O(x - s / 2, y - s / 2, x + s / 2, y + s / 2, s * .3, "solid"))
    return dict(name="3. Stalagmite hall", note="a forest of rock columns", shapes=sh, up=(4.5, 6.5), down=(25.5, 17))


def L4():   # hub and pockets
    sh = [O(9, 5, 21, 17, 3.5)]
    for a, b in ((4, 4), (26, 4), (4, 18), (26, 18)):
        sh.append(O(a - 3.3, b - 3.3, a + 3.3, b + 3.3, 1.5))
    sh += tunnel([(4, 4), (11, 11)], 2.6) + tunnel([(26, 4), (19, 11)], 2.6) + tunnel([(4, 18), (11, 11)], 2.6) + tunnel([(26, 18), (19, 11)], 2.6)
    return dict(name="4. Hub and pockets", note="big middle, four little rooms", shapes=sh, up=(4, 4), down=(26, 18))


def L5():   # twin caves
    return dict(name="5. Twin caves", note="two rooms, one narrow neck",
                shapes=[O(1, 2, 13, 20, 4), O(17, 2, 29, 20, 4), ("floor", [(12, 9.5), (18, 9.5), (18, 12.5), (12, 12.5)]),
                        O(5, 13, 9, 17, kind="solid"), O(21, 5, 25, 9, kind="solid")],
                up=(5, 6), down=(25, 16))


def L6():   # ring round a hole
    return dict(name="6. The ring", note="a loop round a deep pit",
                shapes=[O(1, 1, 29, 21, 6), O(9, 7, 21, 15, 3, "hole")], up=(4, 11), down=(26, 11))


def L7():   # fork
    sh = [O(1, 7.5, 8, 14.5, 2)] + tunnel([(6, 11), (13, 11)]) + tunnel([(13, 11), (19, 5), (24, 5)], 2.6) + tunnel([(13, 11), (24, 11)], 2.6) + tunnel([(13, 11), (19, 17), (24, 17)], 2.6)
    sh += [O(22, 1, 29, 7.5, 2), O(22, 8, 29, 14, 2), O(22, 14.5, 29, 21, 2)]
    return dict(name="7. The fork", note="three branches, one way down", shapes=sh, up=(4, 11), down=(26, 4))


def L8():   # crevasse
    return dict(name="8. Crevasse", note="split by a crack, two crossings",
                shapes=[O(1, 2, 29, 21, 4), ("hole", [(12, 2), (16, 2), (16, 8), (20, 12), (20, 21), (16, 21), (16, 14), (12, 10)]),
                        ("bridge", [(11, 4.5), (17, 4.5), (17, 6.5), (11, 6.5)]), ("bridge", [(15, 16.5), (21, 16.5), (21, 18.5), (15, 18.5)])],
                up=(5, 7), down=(25, 16))


def L9():   # terraces
    sh = [O(1, 1, 11, 9, 2.5), O(8, 6, 19, 15, 2.5), O(15, 12, 29, 21, 3), O(20, 1, 28, 8, 2)] + tunnel([(16, 9), (19, 6), (22, 6)], 2.6)
    return dict(name="9. Terraces", note="rooms stepping down the diagonal", shapes=sh, up=(4.5, 4.5), down=(25, 4))


def L10():  # honeycomb
    cells = {(i, j): (1 + i * 10, 1 + j * 11) for i in range(3) for j in range(2)}
    sh = [O(x, y, x + 8, y + 9.5, 2.5) for x, y in cells.values()]
    for a, b in (((0, 0), (0, 1)), ((0, 1), (1, 1)), ((1, 1), (1, 0)), ((1, 0), (2, 0)), ((2, 0), (2, 1))):
        (x0, y0), (x1, y1) = cells[a], cells[b]
        cx0, cy0, cx1, cy1 = x0 + 4, y0 + 4.75, x1 + 4, y1 + 4.75
        sh += tunnel([(cx0, cy0), (cx1, cy1)], 2.2)
    return dict(name="10. Honeycomb", note="little cells, one path through", shapes=sh, up=(5, 5.5), down=(25, 16.5))


LAYOUTS = [L1(), L2(), L3(), L4(), L5(), L6(), L7(), L8(), L9(), L10()]

THEMES = {
    "rock":  dict(t="Floors 1-15: rock", floor=(150, 136, 118), solid=(84, 76, 74), hole=(22, 18, 20), bridge=(150, 110, 70), deco=None,
                  ores=[(ROCK, 6), (ORE_I, 2), (ORE_C, 2)], mob=(200, 90, 90), mobr=.8, solidname="stalagmites", holename="chasm"),
    "lush":  dict(t="Floors 16-30: green and lush", floor=(124, 168, 108), solid=(70, 112, 74), hole=(46, 84, 52), bridge=(130, 100, 60), deco=(60, 110, 60),
                  ores=[(ROCK, 5), (ORE_C, 2), ((210, 210, 220), 2), (CRYST, 1)], mob=(200, 90, 90), mobr=1.0, solidname="giant mushrooms", holename="overgrown pit"),
    "steam": dict(t="Floors 31-44: steamy and watery", floor=(132, 158, 174), solid=(90, 104, 118), hole=(64, 136, 196), bridge=(110, 110, 120), deco=(232, 238, 242),
                  ores=[(ROCK, 5), (CRYST, 2), ((120, 220, 230), 2)], mob=(200, 90, 90), mobr=1.25, solidname="crystal columns", holename="hot pool"),
}


def draw_floor(m, ox, oy, lay, th, seed, mirror=False, title=None):
    W, H = 30, 22
    fx = (lambda x: W - x) if mirror else (lambda x: x)
    T = lambda pts: [(ox + fx(x), oy + 3 + y) for x, y in pts]
    m.rect(ox, oy + 3, ox + W, oy + 3 + H, ROCKBG, None)
    floors = [T(p) for k, p in lay["shapes"] if k == "floor"]
    for p in floors: m.poly(p, th["floor"], WALL, 5)               # outline pass
    for p in floors: m.d.polygon([m.P(*q) for q in p], fill=th["floor"])   # fill pass hides inner seams
    for k, p in lay["shapes"]:
        if k == "hole": m.poly(T(p), th["hole"], WALL, 3)
    for k, p in lay["shapes"]:
        if k == "bridge": m.poly(T(p), th["bridge"], WALL, 2)
        if k == "solid": m.poly(T(p), th["solid"], WALL, 2)
    # placement mask at 4 px per tile
    Q = 4; mk = Image.new("L", (W * Q, H * Q), 0); md = ImageDraw.Draw(mk)
    loc = lambda pts: [(fx(x) * Q, y * Q) for x, y in pts]
    for p in [p for k, p in lay["shapes"] if k == "floor"]: md.polygon(loc(p), fill=255)
    for k, p in lay["shapes"]:
        if k in ("hole", "solid", "bridge"): md.polygon(loc(p), fill=0)
    ux, uy = fx(lay["up"][0]), lay["up"][1]; dx, dy = fx(lay["down"][0]), lay["down"][1]
    for x, y in ((ux, uy), (dx, dy)): md.ellipse(((x - 3) * Q, (y - 3) * Q, (x + 3) * Q, (y + 3) * Q), fill=0)
    ok = lambda x, y: all(0 <= (x + a) * Q < W * Q and 0 <= (y + b) * Q < H * Q and mk.getpixel((int((x + a) * Q), int((y + b) * Q))) == 255
                          for a, b in ((0, 0), (1.1, 0), (-1.1, 0), (0, 1.1), (0, -1.1), (.8, .8), (-.8, .8), (.8, -.8), (-.8, -.8)))
    r = random.Random(seed); pts = []
    for _ in range(5000):
        if len(pts) >= 30: break
        x, y = r.uniform(1, W - 1), r.uniform(1, H - 1)
        if ok(x, y) and all(math.hypot(x - a, y - b) > 2.1 for a, b in pts): pts.append((x, y))
    tot = sum(w for _, w in th["ores"]); mobs = 0
    for i, (x, y) in enumerate(pts):
        X, Y = ox + x, oy + 3 + y
        if th["deco"] and i % 5 == 0:
            m.dot(X, Y, th["deco"], .9 if th["deco"] != (232, 238, 242) else .6, WALL); continue
        if i % 9 == 4 and mobs < 3:
            m.dot(X, Y, th["mob"], th["mobr"]); mobs += 1; continue
        v = r.uniform(0, tot)
        for c, w in th["ores"]:
            if v <= w: (m.rock(X, Y) if c == ROCK else m.ore(X, Y, c)); break
            v -= w
    m.oct(ox + ux - 2, oy + 3 + uy - 1.6, ox + ux + 2, oy + 3 + uy + 1.6, (226, 216, 196), .8); m.label(ox + ux, oy + 3 + uy + .2, "up", FS, plate=False)
    m.oct(ox + dx - 2, oy + 3 + dy - 1.6, ox + dx + 2, oy + 3 + dy + 1.6, (40, 34, 36), .8, (250, 220, 90)); m.label(ox + dx, oy + 3 + dy + .2, "down", FS, WHITE)
    m.label(ox + W / 2, oy + 1.2, title or lay["name"], F, WHITE)
    if not title: m.label(ox + W / 2, oy + 2.5, "", FS, WHITE)


# sheet 1: all ten, rock tier, with a one-line note each
m = Mock(162, 62, "The Caverns: ten main layouts (shown in the rock tier, floors 1-15)",
         "Each cavern floor is one of these ten, picked at random, mirrored half the time, with rocks, ore and creatures scattered fresh on every visit.")
for i, lay in enumerate(LAYOUTS):
    ox, oy = 1 + (i % 5) * 32, 1 + (i // 5) * 30
    draw_floor(m, ox, oy, lay, THEMES["rock"], 100 + i)
    m.label(ox + 15, oy + 26.6, lay["note"], FS, WHITE)
m.save("caverns_layouts_10")

# sheet 2: the same layouts at depth, plus mirroring
m = Mock(162, 80, "The Caverns: one layout, three depths",
         "The shapes stay; the dressing changes. Pillars become stalagmites, giant mushrooms or crystal columns; holes become a chasm, an overgrown pit or a hot pool.")
picks = [(LAYOUTS[2], 7), (LAYOUTS[5], 8), (LAYOUTS[7], 9)]
for row, (lay, sd) in enumerate(picks):
    for col, key in enumerate(("rock", "lush", "steam")):
        ox, oy = 1 + col * 32, 1 + row * 26
        th = THEMES[key]
        draw_floor(m, ox, oy, lay, th, sd * 10 + col, mirror=(col == 1), title=lay["name"].split(". ")[1] + ": " + th["t"].split(": ")[1] + (" (mirrored)" if col == 1 else ""))
# right column: notes
m.text(98, 2, "WHAT CHANGES WITH DEPTH", (255, 226, 150))
m.text(98, 4.5, "Rock (1-15)\n  stalagmites, dark chasms, iron and copper,\n  small creatures.\n\nGreen and lush (16-30)\n  giant mushrooms, ferns and moss, overgrown\n  pits; copper, silver-grey ore, first crystals;\n  creatures a size up.\n\nSteamy and watery (31-44)\n  crystal columns, hot pools you walk round,\n  steam vents; crystal and thermal quartz;\n  the biggest creatures.\n\nFloor 45 is its own hand-made map:\n  the Harbinger, and the shore of the\n  underground ocean.")
m.text(98, 46, "VARIETY FROM 10 LAYOUTS", (255, 226, 150))
m.text(98, 48.5, "- 10 shapes x 3 depths x mirrored\n  = 60 different-looking floors.\n- Middle column shows a mirrored copy.\n- Rocks, ore and creatures are placed\n  fresh each visit, so even a repeat\n  floor plays differently.\n- 'down' marks where the way down sits;\n  how it opens is still to pick.\n- Every 5th floor: a lift stop.")
m.save("caverns_depths")
