"""East Complex with a big agridome to the east (Zachary, 22 Nov): fishing springs, hot springs and a bath house.
The ring, homes, greenhouse, fitness centre and laundry stay as built; the air reclamation plant moves south."""
import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_east import *
FLOWER, BENCH = (226, 170, 200), (170, 130, 96)
PARK, FIELD, FISH, HOT, BATH, DOMEF, DECKC = ((150, 196, 120), (176, 132, 90), (90, 160, 210), (120, 210, 205), (214, 170, 140),
                                              (196, 214, 160), (190, 150, 110))
LEG3 = [(PLAZA, "Walks"), (STREET, "Ring street"), (HOME, "Homes"), (DOMEF, "Dome grass and paths"), (FLOWER, "Flower garden"), ((90, 140, 60), "Trees"), (FISH, "Fishing springs"), (HOT, "Hot springs"), (BATH, "Bath house"), (DECKC, "Fishing docks / decks"),
        (PLANT, "Air reclamation plant"), (AIR, "Airlock"), ((250, 220, 90), "Door")]

def existing(m):
    """The current East Complex, unchanged: walkway in, laundry, ring and park, greenhouse, fitness centre, homes."""
    m.rect(1, 1, 206, 94, ROCK, None)
    cx, cy = 56, 46
    m.rect(1, 43, 34, 49, PLAZA); m.label(6, 41, "< Main Level", FS, (240, 240, 240))
    oct_(m, 3, 26, 22, 41, LAUND, 3); m.label(12, 33, "Laundry", FS)
    m.circ(cx, cy, 22, STREET); m.circ(cx, cy, 12, PARK); m.label(cx, cy, "Park", FS)
    m.circ(cx, cy - 26, 14, GREEN); m.label(cx, cy - 30, "Mess hall\ngreenhouse", FS)
    oct_(m, cx - 17, cy + 16, cx + 17, cy + 40, GYM, 6); m.label(cx, cy + 34, "Fitness centre", FS)
    for a in (18, 33, 147, 162, 198, 213, 327, 342):
        x, y = pol(cx, cy, 25.5, a); m.circ(x, y, 3, HOME)
    return cx, cy

def dome(m, cx, cy, r):
    m.circ(cx, cy, r + 1.2, WALL); m.circ(cx, cy, r, DOMEF)
    for a in range(0, 360, 30):
        x, y = pol(cx, cy, r - .6, a); m.dot(x, y, (240, 240, 236), .5)

def fields(m, x0, y0, x1, y1, rows=True):
    m.rect(x0, y0, x1, y1, FIELD)
    if rows:
        for y in frange(y0 + 1, y1, 2): m.d.line([m.P(x0 + .5, y), m.P(x1 - .5, y)], fill=(140, 100, 66), width=3)

def trees(m, pts):
    for x, y in pts: m.dot(x, y, (90, 140, 60), 1.4)

def springs(m, pts, col, r):
    for x, y in pts: m.circ(x, y, r, col)

# ============================================================ D1: springs in the middle of the dome
m = Mock(230, 96, "East Complex D1: a big garden dome east, the springs at its heart",
         "Dome about 80 tiles across, no farming. A fishing lake in the middle with docks and an island, hot springs in the north-east, the bath house on the east rim, woods and a flower garden round the west. Air plant moved south.")
cx, cy = existing(m)
m.rect(78, 43, 112, 49, PLAZA); m.label(94, 41, "walkway", FS, (240, 240, 240))
dx, dy, R = 152, 48, 40
dome(m, dx, dy, R)
trees(m, [(126, 16), (133, 12), (140, 10), (122, 22), (120, 30), (128, 26), (136, 20), (122, 62), (128, 68), (134, 74), (120, 70), (140, 78), (130, 58)])
m.circ(128, 36, 5, FLOWER); m.label(128, 36, "flower\ngarden", FS); m.label(128, 66, "woods", FS)
m.rect(132, 52, 140, 54, BENCH); m.label(136, 56, "benches", FS)
m.rect(112, 45, 192, 51, PLAZA, None); m.rect(149, 10, 155, 86, PLAZA, None)          # cross paths
m.circ(152, 48, 13, FISH); m.circ(154, 46, 3.2, DOMEF); trees(m, [(154, 46)])
m.rect(138, 47, 143, 49, DECKC); m.rect(160, 56, 162, 61, DECKC); m.rect(144, 36, 146, 40, DECKC)
m.label(149, 52, "Fishing springs", F)
springs(m, [(170, 22), (178, 28), (168, 31), (176, 36)], HOT, 3.6); m.label(173, 16, "Hot springs", F)
for x, y in ((172, 26), (174, 32)): m.dot(x, y, (250, 250, 250), .5)
oct_(m, 178, 54, 194, 72, BATH, 3); m.label(186, 60, "Bath\nhouse", F); m.door(178, 63)
m.rect(166, 74, 176, 82, HOT); m.label(171, 78, "outdoor\nbath", FS)
# the air reclamation plant, moved south, and the airlock
m.rect(92, 49, 96, 60, PLAZA)
m.rect(82, 60, 108, 84, PLANT); m.label(95, 70, "Air reclamation\nplant (moved south)", FS)
m.rect(92, 84, 98, 88, PLAZA); m.rect(88, 88, 102, 94, AIR); m.label(95, 91, "Airlock", FS)
for x, y in ((34, 47), (78, 46), (112, 48), (94, 60), (95, 84)): m.door(x, y)
m.legend(208, 4, LEG3)
m.im.save(MOCK + "/east_dome_D1.png")

# ============================================================ D2: farm west half, springs east half
m = Mock(230, 96, "East Complex D2: a big garden dome east, woods on one side, springs on the other",
         "No farming. The west half of the dome is woods, a flower meadow and a picnic green; the east half has a big fishing lake with a long dock in the north, hot springs and the bath house in the south. Air plant moved south.")
cx, cy = existing(m)
m.rect(78, 43, 112, 49, PLAZA)
dx, dy, R = 152, 48, 40
dome(m, dx, dy, R)
trees(m, [(120, 24), (126, 18), (132, 14), (124, 32), (138, 22), (130, 28), (138, 60), (142, 64), (146, 58), (140, 70), (146, 70), (124, 64), (130, 72)])
m.label(130, 22, "woods", FS); m.circ(142, 36, 5, FLOWER); m.label(142, 36, "flower\nmeadow", FS)
m.circ(132, 60, 4, (230, 200, 140)); m.label(132, 60, "picnic\ngreen", FS); m.label(143, 76, "woods", FS)
m.rect(112, 45, 160, 51, PLAZA, None)
m.d.ellipse(m.P(154, 14) + m.P(186, 40), fill=FISH, outline=WALL, width=2); m.label(170, 22, "Fishing springs", F)
m.rect(168, 26, 170, 40, DECKC); m.rect(158, 30, 162, 32, DECKC)
for x, y in ((160, 20), (182, 34), (176, 16)): m.dot(x, y, (90, 140, 60), 1.2)
m.rect(160, 46, 166, 80, PLAZA, None); m.rect(160, 51, 190, 55, PLAZA, None)
springs(m, [(168, 62), (176, 60), (172, 70), (182, 66)], HOT, 3.8); m.label(176, 76, "Hot springs", F)
oct_(m, 180, 40, 194, 56, BATH, 3); m.label(187, 47, "Bath\nhouse", F); m.door(187, 56)
m.rect(92, 49, 96, 60, PLAZA)
m.rect(82, 60, 108, 84, PLANT); m.label(95, 70, "Air reclamation\nplant (moved south)", FS)
m.rect(92, 84, 98, 88, PLAZA); m.rect(88, 88, 102, 94, AIR); m.label(95, 91, "Airlock", FS)
for x, y in ((34, 47), (78, 46), (112, 48), (94, 60), (95, 84)): m.door(x, y)
m.legend(208, 4, LEG3)
m.im.save(MOCK + "/east_dome_D2.png")
print("ok")

# ============================================================ D3: D2 with a stream and fishing ponds instead of one lake
import math as _m
m = Mock(230, 96, "East Complex D3: a garden dome with a stream, fishing ponds, hot springs and a bath house",
         "No farming. A stream rises at a spring in the north, winds south and links three fishing ponds. Stone walking paths loop through the woods to the west, past a flower meadow and a picnic green; hot springs and the bath house in the south-east.")
cx, cy = existing(m)
m.rect(78, 43, 112, 49, PLAZA)
dx, dy, R = 152, 48, 40
dome(m, dx, dy, R)
trees(m, [(120, 24), (126, 18), (132, 14), (124, 32), (138, 20), (130, 28), (128, 22), (134, 20), (120, 18), (136, 26),
          (124, 64), (130, 72), (136, 66), (120, 58), (140, 76), (146, 80), (128, 64), (134, 72), (126, 74), (120, 68)])
m.circ(132, 38, 5, FLOWER); m.label(132, 38, "flower\nmeadow", FS)
m.circ(130, 60, 4, (230, 200, 140)); m.label(130, 60, "picnic\ngreen", FS)
# a stone walking path winding through the trees: a loop through the north woods and the south woods
STONE = (200, 194, 180)
loop = [(140, 30), (134, 26), (128, 28), (123, 24), (125, 17), (131, 14), (137, 16), (140, 22),
        (140, 30)]
loop2 = [(140, 66), (136, 70), (130, 67), (124, 70), (122, 64), (126, 56), (133, 55), (138, 58), (140, 66)]
for path in (loop, loop2):
    for (a, b) in zip(path, path[1:]):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) / 1.6) + 1
        for k in range(n):
            x = a[0] + (b[0] - a[0]) * k / n; y = a[1] + (b[1] - a[1]) * k / n
            m.d.ellipse(m.P(x - .6, y - .5) + m.P(x + .6, y + .5), fill=STONE, outline=(120, 114, 104), width=1)
m.label(118, 12, "stone path", FS); m.label(117, 74, "stone path", FS)
# the stream: a sine path from a spring in the north to the south rim, with ponds along it
pts = [(156 + 7 * _m.sin(t / 9), t) for t in range(10, 86)]
m.d.line([m.P(x, y) for x, y in pts], fill=FISH, width=22)
m.circ(156, 10.5, 2.6, FISH); m.label(163, 9, "spring", FS)
for (px, py, rx, ry) in ((150, 24, 7, 5), (164, 47, 8, 6), (152, 70, 7, 5)):
    m.d.ellipse(m.P(px - rx, py - ry) + m.P(px + rx, py + ry), fill=FISH, outline=WALL, width=2)
m.label(150, 24, "pond", FS); m.label(164, 47, "pond", FS); m.label(152, 70, "pond", FS)
for (x0, y0, x1, y1) in ((143, 20, 145, 23), (170, 50, 173, 52), (145, 72, 147, 75)): m.rect(x0, y0, x1, y1, DECKC)
# paths with footbridges over the stream
m.rect(112, 45, 192, 50, PLAZA, None)
m.rect(140, 28, 144, 88, PLAZA, None)
for (bx, by) in ((157, 47.5),): m.rect(bx - 5, by - 3, bx + 5, by + 3, DECKC)
m.label(176, 44, "footbridge", FS)
springs(m, [(172, 64), (180, 60), (176, 72), (186, 68)], HOT, 3.8); m.label(180, 78, "Hot springs", F)
oct_(m, 180, 40, 194, 56, BATH, 3); m.label(187, 47, "Bath\nhouse", F); m.door(184, 56)
m.rect(92, 49, 96, 60, PLAZA)
m.rect(82, 60, 108, 84, PLANT); m.label(95, 70, "Air reclamation\nplant (moved south)", FS)
m.rect(92, 84, 98, 88, PLAZA); m.rect(88, 88, 102, 94, AIR); m.label(95, 91, "Airlock", FS)
for x, y in ((34, 47), (78, 46), (112, 48), (94, 60), (95, 84)): m.door(x, y)
m.legend(208, 4, LEG3)
m.im.save(MOCK + "/east_dome_D3.png")
print("ok3")
