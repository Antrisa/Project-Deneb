import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_base import *
from mock_eng import CORE_C, HALL, BAY, ORE, LIFE, STORE, SHOP, SPARE, BREAK, LIFTC, RAMP, LOCK

POWER, COOL, BELT = (255, 210, 60), (90, 170, 255), (60, 60, 70)


def oct_(m, x0, y0, x1, y1, fill, cut=3):
    pts = [(x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - cut), (x1 - cut, y1), (x0 + cut, y1), (x0, y1 - cut), (x0, y0 + cut)]
    m.d.polygon([m.P(*p) for p in pts], fill=fill, outline=WALL, width=3)


def poly(m, pts, fill):
    m.d.polygon([m.P(*p) for p in pts], fill=fill, outline=WALL, width=3)


def belt(m, pts, w=1.3):
    for a, b in zip(pts, pts[1:]):
        m.d.line([m.P(*a), m.P(*b)], fill=BELT, width=int(w * S))
        m.d.line([m.P(*a), m.P(*b)], fill=(200, 160, 60), width=2)
    for a, b in zip(pts, pts[1:]):                                   # rollers / arrows along the belt
        n = int(math.hypot(b[0] - a[0], b[1] - a[1]) // 2.5)
        for i in range(1, n + 1):
            t = i / (n + 1); x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            m.dot(x, y, (230, 190, 90), .3)


def line(m, pts, c, w=4, dash=False):
    for a, b in zip(pts, pts[1:]):
        m.d.line([m.P(*a), m.P(*b)], fill=c, width=w)


def boxes(m, items):
    """little furniture blocks: (x, y, w, h, colour)"""
    for x, y, w, h, c in items:
        m.d.rectangle(m.P(x, y) + m.P(x + w, y + h), fill=c, outline=WALL, width=1)


DESK, PANEL, TANK, MACH = (240, 236, 220), (60, 90, 110), (120, 190, 230), (110, 116, 130)

LEG = [(HALL, "Works hall (the rectangle)"), (ORE, "Ore processing"), (CORE_C, "Geothermal power core"), (SHOP, "Tikka's engineering bay"),
       (LIFE, "Life support & cooling"), (STORE, "Stores / cargo staging"), (BREAK, "Crew break room"), (SPARE, "Spare workshops"),
       (LIFTC, "Lift"), (RAMP, "Mine tunnel"), (BAY, "To the shuttle bay")]
LEG2 = [(BELT, "Conveyor belt (ore from the mine)"), (POWER, "Power lines"), (COOL, "Coolant pipes"), ((250, 220, 90), "Door / opening")]


def common_legend(m, x, y):
    m.legend(x, y, LEG)
    for i, (c, t) in enumerate(LEG2):
        yy = y + (len(LEG) + i) * 2.2
        m.d.line([m.P(x, yy + .7), m.P(x + 1.4, yy + .7)], fill=c, width=6)
        m.d.text(m.P(x + 2.2, yy - .1), t, fill=(230, 230, 236), font=FS)


# ============================================================ option C: rectangle spine, rooms bulging out
m = Mock(142, 74, "Engineering, option C: a rectangular hall with the rooms bulging out of it",
         "The hall is the straight part; every room swells out from it with 45-degree walls, big ones big. Mine tunnel west, shuttle bay east. About 112 x 64 tiles.")
hy0, hy1 = 31, 39                                   # the hall
m.rect(1, 3, 112, 72, ROCK, None)
# ore processing: huge bulge west, mine tunnel coming in from the south-west
poly(m, [(10, 14), (24, 8), (34, 8), (38, 12), (38, hy0), (6, hy0), (6, 18)], ORE)
poly(m, [(6, hy1), (24, hy1), (24, 50), (18, 56), (6, 56)], ORE)
m.rect(1, 50, 8, 56, RAMP)
belt(m, [(2, 53), (14, 53), (14, 44), (14, 24), (20, 16), (30, 16)])
boxes(m, [(28, 13, 4, 4, MACH), (33, 13, 3, 4, (180, 90, 60)), (33, 19, 3, 4, (180, 90, 60)), (26, 22, 5, 3, MACH), (17, 26, 5, 3, MACH)])
belt(m, [(30, 24), (30, 28), (36, 28)], 1)
m.label(24, 21, "Ore processing"); m.label(19, 47, "sorting & carts", FS)
m.label(4, 58, "Mine", FS, (230, 230, 236))
# power core: big round chamber north-centre
m.rect(44, 18, 62, hy0, CORE_C)
m.circ(53, 15, 12, CORE_C)
m.circ(53, 15, 4.5, (250, 140, 50))
for a in range(0, 360, 45):
    x, y = pol(53, 15, 8, a); m.dot(x, y, PANEL, .9)                       # panels ringing the core
for x in (45, 49, 57, 61): m.d.rectangle(m.P(x - 1, 24) + m.P(x + 1, 29), fill=PANEL, outline=WALL)
m.label(53, 9.3, "Power core", F)
# cooling: south of the core, pipes crossing under the hall
poly(m, [(42, hy1), (64, hy1), (64, 52), (58, 58), (48, 58), (42, 52)], LIFE)
for x in (47, 53, 59): m.circ(x, 50, 2.6, TANK)
line(m, [(50, 21), (50, 47.4)], COOL, 5); line(m, [(56, 21), (56, 47.4)], COOL, 5)
m.label(53, 55.5, "Cooling & life support", F)
# power lines out of the core to the rooms
line(m, [(44, 26), (40, 26), (40, hy0 + 1), (8, hy0 + 1)], POWER, 3)
line(m, [(62, 26), (66, 26), (66, hy0 + 1), (110, hy0 + 1)], POWER, 3)
line(m, [(53, hy1 - 1), (53, hy1 - 1)], POWER, 3)
# lift: small, between core and Tikka
m.rect(66, 22, 72, hy0, LIFTC); m.label(69, 26, "Lift", FS)
# Tikka's engineering bay: big, north-east, with her office and a drone pit
poly(m, [(74, hy0), (74, 14), (80, 8), (100, 8), (106, 14), (106, hy0)], SHOP)
m.rect(96, 9, 105, 16, (240, 214, 150)); m.label(100.5, 12.5, "office", FS)
boxes(m, [(77, 12, 6, 2.5, DESK), (77, 16, 6, 2.5, DESK), (85, 11, 8, 2, PANEL), (78, 23, 4, 4, MACH), (99, 20, 5, 6, MACH)])
m.circ(90, 21, 4, (210, 170, 90))
m.label(90, 21, "test\nrig", FS); m.label(90, 28.5, "Tikka's engineering bay", F)
# south side: stores, break room, spares, cargo
poly(m, [(26, hy1), (40, hy1), (40, 48), (36, 52), (26, 52)], STORE); m.label(33, 45, "Stores")
oct_(m, 66, hy1, 78, 52, BREAK, 3); m.label(72, 45, "Break\nroom")
oct_(m, 80, hy1, 90, 50, SPARE, 3); m.label(85, 44, "Spare")
oct_(m, 92, hy1, 106, 54, STORE, 3); m.label(99, 46, "Cargo\nstaging")
oct_(m, 26, 8, 40, hy0, SPARE, 3) if False else None
# the hall itself, drawn last so the rooms open into it
m.rect(6, hy0, 108, hy1, HALL)
m.rect(108, hy0 + 1, 112, hy1 - 1, BAY); m.label(110, hy1 + 2.5, "Bay >", FS, (230, 230, 236))
belt(m, [(24, hy1 - 2.5), (99, hy1 - 2.5), (99, hy1 + 4)], 1)                      # refined ore out to cargo
m.label(60, hy0 + 2.6, "Engineering works hall", F)
for x, y in ((22, hy0), (12, hy1), (53, hy0), (53, hy1), (69, hy0), (90, hy0), (33, hy1), (72, hy1), (85, hy1), (99, hy1)):
    m.door(x, y)
common_legend(m, 114, 6)
m.d.text(m.P(114, 41), "Belt: mine > ore room >\nalong the hall > cargo\nstaging > the bay.\nCore glows in the middle;\npower lines run along\nthe hall ceiling (yellow).", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/eng_option_C.png")

# ============================================================ option D: the core as the centrepiece
m = Mock(142, 78, "Engineering, option D: the hall wraps round the power core",
         "The rectangle has a hole in the middle: the core sits in its own deep pit and the hall runs round it. Rooms bulge outward on all sides. About 108 x 70 tiles.")
m.rect(1, 3, 110, 76, ROCK, None)
# outer rectangle hall with a core in the middle
hx0, hy0, hx1, hy1 = 22, 22, 88, 54
m.rect(hx0, hy0, hx1, hy1, HALL)
oct_(m, hx0 + 9, hy0 + 7, hx1 - 9, hy1 - 7, ROCK, 5)
oct_(m, hx0 + 13, hy0 + 9, hx1 - 13, hy1 - 9, CORE_C, 5)
m.circ(55, 38, 5, (250, 140, 50))
for x in range(38, 74, 6): m.d.rectangle(m.P(x, hy0 + 10) + m.P(x + 3, hy0 + 11.5), fill=PANEL, outline=WALL)
for x in range(38, 74, 6): m.d.rectangle(m.P(x, hy1 - 11.5) + m.P(x + 3, hy1 - 10), fill=PANEL, outline=WALL)
for x in (40, 70): m.circ(x, 38, 2.5, TANK)
m.label(55, hy0 + 3.6, "Geothermal power core, down in its pit", F); m.label(66, hy1 - 3.4, "control panels on the rails, coolant tanks at the ends", FS)
for x, y in ((55, hy0 + 7), (55, hy1 - 7)): m.door(x, y)
# ore processing west, belts from the mine
poly(m, [(hx0, hy0 + 2), (14, hy0 - 4), (6, hy0 + 2), (4, 38), (6, hy1 - 2), (14, hy1 + 4), (hx0, hy1 - 2)], ORE)
m.rect(1, 60, 10, 66, RAMP); m.label(5, 68.5, "Mine", FS, (230, 230, 236))
belt(m, [(2, 63), (8, 63), (8, 50), (8, 28), (16, 24)]); belt(m, [(16, 24), (20, 30), (20, 44)], 1)
boxes(m, [(10, 30, 3, 4, (180, 90, 60)), (10, 40, 3, 4, (180, 90, 60)), (14, 34, 4, 4, MACH)])
m.label(13, 22, "Ore\nprocessing")
# Tikka north: biggest room
poly(m, [(30, hy0), (30, 12), (38, 4), (72, 4), (80, 12), (80, hy0)], SHOP)
m.rect(70, 5, 79, 12, (240, 214, 150)); m.label(74.5, 8.5, "office", FS)
boxes(m, [(33, 9, 7, 2.5, DESK), (33, 14, 7, 2.5, DESK), (44, 6, 10, 2, PANEL), (70, 15, 6, 4, MACH)])
m.circ(57, 14, 4.5, (210, 170, 90)); m.label(57, 14, "drone\npit", FS)
m.label(46, 18.5, "Tikka's engineering bay", F)
# lift north-east corner
m.rect(84, 14, 92, hy0, LIFTC); m.label(88, 18, "Lift", FS)
# life support south, big, coolant runs up into the core
poly(m, [(30, hy1), (30, 62), (36, 68), (60, 68), (60, hy1)], LIFE)
for x in (36, 44, 52): m.circ(x, 62, 2.6, TANK)
line(m, [(44, 59.4), (44, hy1 - 9)], COOL, 5); line(m, [(52, 59.4), (52, hy1 - 9)], COOL, 5)
m.label(45, 66, "Cooling & life support")
oct_(m, 62, hy1, 74, 66, BREAK); m.label(68, 60, "Break\nroom")
oct_(m, 76, hy1, 86, 64, SPARE); m.label(81, 59, "Spare")
# east: stores, cargo, the bay
poly(m, [(hx1, hy0 + 2), (96, hy0 - 2), (104, hy0 + 4), (104, 34), (hx1, 34)], STORE); m.label(97, 29, "Stores")
poly(m, [(hx1, 40), (104, 40), (104, hy1 + 2), (96, hy1 + 8), (hx1, hy1 - 2)], STORE); m.label(97, 47, "Cargo\nstaging")
m.rect(104, 35, 110, 39, BAY); m.rect(hx1, 34, 104, 40, HALL); m.label(107, 32, "Bay >", FS, (230, 230, 236))
oct_(m, 2, hy1 + 6, 18, 58, SPARE) if False else None
oct_(m, hx0 - 6, hy1 + 2, hx0 + 6, hy1 + 12, SPARE); m.label(hx0, hy1 + 7, "Spare")
# power lines from the core out along the hall
line(m, [(hx0 + 13, 38), (hx0 + 2, 38), (hx0 + 2, hy0 + 2), (hx1 - 2, hy0 + 2), (hx1 - 2, hy1 - 2), (hx0 + 2, hy1 - 2), (hx0 + 2, 38)], POWER, 3)
belt(m, [(20, hy1 - 1.5), (hx1 - 4, hy1 - 1.5), (96, hy1 + 1)], 1)
for x, y in ((hx0, 30), (hx0, 46), (55, hy0), (88, hy0), (45, hy1), (68, hy1), (81, hy1), (hx1, 28), (hx1, 47), (hx0, hy1)):
    m.door(x, y)
common_legend(m, 114, 6)
m.d.text(m.P(114, 41), "Walk a loop round the core;\nyou can see it from the\nwhole hall. Belt: mine >\nore room > along the south\nhall > cargo staging.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/eng_option_D.png")
print("ok")
