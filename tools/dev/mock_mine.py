import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_eng2 import Mock, oct_, poly, line, boxes, ROCK, WALL, S, F, FS, FT, pol, BELT, belt
from mock_base import *
import random
DIG, HEAD, WATER, ICE, GATE, TUNNEL, CRYST, FUNG, LAKE, RUIN, RAIL, SAFE = ((176, 150, 120), (210, 190, 150), (120, 180, 210), (200, 230, 240),
    (200, 90, 80), (150, 130, 120), (170, 130, 220), (150, 190, 110), (60, 130, 190), (190, 180, 150), (90, 80, 70), (230, 210, 120))
ORE_I, ORE_C = (190, 190, 200), (220, 140, 80)
LEG = [(HEAD, "Mine head (from Engineering)"), (DIG, "Worked galleries"), (RAIL, "Ore cart rails"), (BELT, "Conveyor to Engineering"),
       (WATER, "Zaas's water works"), (ICE, "Ice seam (water source)"), (ORE_I, "Iron veins"), (ORE_C, "Copper veins"), (CRYST, "Crystal veins"),
       (GATE, "Barricade / cavern gate"), (TUNNEL, "To the North Tunnels"), (SAFE, "Rest stop (lamps, water, bench)"), ((250, 220, 90), "Door / way through")]

def blob(m, cx, cy, rx, ry, fill, seed=1, pts=18):
    r = random.Random(seed); P = []
    for i in range(pts):
        a = 2 * math.pi * i / pts; k = r.uniform(.8, 1.1)
        P.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    poly(m, P, fill)

def veins(m, pts, c):
    for x, y in pts: m.d.polygon([m.P(x, y - .8), m.P(x + .8, y), m.P(x, y + .8), m.P(x - .8, y)], fill=c, outline=WALL)

def rail(m, pts):
    for a, b in zip(pts, pts[1:]):
        m.d.line([m.P(*a), m.P(*b)], fill=RAIL, width=int(.9 * S))
        n = int(math.hypot(b[0] - a[0], b[1] - a[1]) / 1.2)
        for i in range(n + 1):
            t = i / max(n, 1); x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            m.d.line([m.P(x - .6, y), m.P(x + .6, y)] if abs(b[1] - a[1]) > abs(b[0] - a[0]) else [m.P(x, y - .6), m.P(x, y + .6)], fill=(150, 120, 80), width=3)

# ============================================================ mine A: the main haulage
m = Mock(150, 82, "The Mine, option A: a main haulage with galleries off it",
         "Like a real mine: one long rail tunnel from the mine head, worked galleries branching off it, the water works and the two ways on (North Tunnels, the cavern gate). About 110 x 76 tiles.")
m.rect(1, 3, 112, 80, (60, 54, 52), None)
oct_(m, 96, 34, 110, 48, HEAD, 3); m.label(103, 38, "Mine head", F); m.label(103, 43, "tool crib, Job's\nshed, lockers", FS)
m.rect(110, 39, 112, 43, HEAD); m.label(106, 50, "> Engineering", FS, (240, 240, 240))
blob(m, 60, 41, 38, 4.5, DIG, 3, 24)
rail(m, [(98, 41), (24, 41)]); m.label(60, 38.5, "Main haulage", F)
belt(m, [(110, 44.5), (98, 44.5), (80, 44.5)], 1)
blob(m, 72, 20, 13, 9, DIG, 5); m.label(72, 17, "Main dig", F); veins(m, [(64, 15), (70, 12), (78, 14), (82, 21), (66, 25), (76, 26)], ORE_I)
veins(m, [(62, 20), (80, 17)], ORE_C); m.rect(70, 29, 74, 37, DIG); rail(m, [(72, 37), (72, 24)])
blob(m, 40, 21, 11, 8, DIG, 7); m.label(40, 18, "Copper stope", F); veins(m, [(33, 18), (38, 14), (46, 16), (35, 25), (45, 25)], ORE_C)
m.rect(38, 28, 42, 37, DIG)
blob(m, 48, 63, 14, 9, WATER, 9); m.label(48, 60, "Zaas's water works", F); m.label(48, 66, "pumps, filters, pipes up\nto the station", FS)
m.rect(46, 45, 50, 54, DIG)
m.rect(30, 63.5, 37, 67.5, WATER); blob(m, 26, 66, 7, 6, ICE, 11); m.label(26, 66, "ice\nseam", FS)
blob(m, 80, 62, 9, 7, SAFE, 13); m.label(80, 62, "Rest stop", FS); m.rect(78, 45, 82, 55, DIG)
blob(m, 12, 41, 8, 9, DIG, 15); m.label(12, 36, "Survey\nend", FS); veins(m, [(9, 45), (14, 47)], CRYST)
m.rect(6, 50, 18, 54, GATE); m.label(12, 52, "cavern gate", FS); m.label(12, 57.5, "v The Caverns", FS, (240, 240, 240))
m.rect(10, 4, 14, 32, TUNNEL); m.label(16, 8, "^ North Tunnels", FS, (240, 240, 240))
for x, y in ((110, 41), (12, 50), (12, 32)): m.door(x, y)
m.legend(114, 6, LEG)
m.d.text(m.P(114, 36), "Straight and practical: you\nfollow the rails in, every\nworking area is one turn off\nthe haulage. Vzz'ket guards\nthe gate at the far end.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/mine_option_A.png")

# ============================================================ mine B: the round shaft
m = Mock(150, 82, "The Mine, option B: a great round shaft with galleries all round it",
         "The station's circle, underground: a wide shaft with a ramp spiralling down its wall and a cage lift in the middle; galleries open off it on every side. About 106 x 78 tiles.")
m.rect(1, 3, 112, 80, (60, 54, 52), None)
cx, cy = 56, 42
m.circ(cx, cy, 16, DIG); m.circ(cx, cy, 10, (40, 34, 34)); m.circ(cx, cy, 3, HEAD)
m.arc(cx, cy, 13, 0, 330, RAIL, int(1.3 * S)); m.label(cx, cy - 6.5, "the shaft\n(drop: no going in)", FS, (240, 240, 240)); m.label(cx, cy, "cage\nlift", FS)
m.label(cx + 22, cy - 13, "spiral ramp\nround the wall", FS, (240, 240, 240))
oct_(m, 92, 34, 108, 50, HEAD, 3); m.label(100, 40, "Mine head", F); m.label(100, 45, "tool crib, lockers", FS); m.rect(72, 39, 92, 45, DIG)
m.rect(108, 39, 112, 45, HEAD); m.label(104, 52, "> Engineering", FS, (240, 240, 240))
blob(m, 56, 11, 15, 7, DIG, 3); m.label(56, 8, "Main dig", F); m.rect(54, 17, 58, 26, DIG)
veins(m, [(46, 10), (52, 7), (62, 8), (68, 12), (50, 15), (63, 15)], ORE_I); veins(m, [(58, 12)], ORE_C)
blob(m, 22, 22, 13, 9, DIG, 5); m.label(22, 19, "Copper stope", F); veins(m, [(14, 20), (20, 16), (28, 18), (17, 27), (27, 26)], ORE_C)
m.d.line([m.P(33, 27), m.P(43, 34)], fill=DIG, width=int(4 * S))
m.rect(98, 69, 104, 73, WATER); blob(m, 88, 68, 14, 8, WATER, 9); m.label(88, 66, "Zaas's water works", F); blob(m, 106, 72, 5, 5, ICE, 11)
m.d.line([m.P(67, 53), m.P(78, 62)], fill=DIG, width=int(4 * S))
blob(m, 22, 64, 12, 9, CRYST, 13); m.label(22, 61, "Crystal seam", F); m.label(22, 67, "survey: Tar'Besh's\nsamples", FS)
m.d.line([m.P(32, 58), m.P(44, 50)], fill=DIG, width=int(4 * S))
m.rect(54, 58, 58, 72, DIG); m.rect(46, 72, 66, 78, GATE); m.label(56, 75, "cavern gate", FS); m.label(56, 80.5, "v The Caverns", FS, (240, 240, 240))
m.rect(4, 38, 40, 42, DIG); m.rect(1, 36, 5, 44, TUNNEL); m.label(10, 34.5, "< North Tunnels", FS, (240, 240, 240))
blob(m, 80, 22, 6, 5, SAFE, 15); m.label(80, 22, "rest\nstop", FS); m.d.line([m.P(70, 30), m.P(77, 25)], fill=DIG, width=int(3 * S))
for x, y in ((108, 42), (56, 72), (5, 40)): m.door(x, y)
m.legend(114, 6, LEG)
m.d.text(m.P(114, 36), "The circle motif again, but\nrough-cut rock. The shaft is\na landmark: the lift goes\ndown to the caverns later.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/mine_option_B.png")

# ============================================================ the sector: three maps
m = Mock(150, 82, "The mine sector: three maps", "Each is its own map; the mine is the hub. Creatures only beyond the mine. Not to scale.")
m.rect(1, 3, 148, 80, (40, 36, 38), None)
blob(m, 74, 40, 16, 10, DIG, 2); m.label(74, 37, "The Mine", FT); m.label(74, 43, "ore, Job, Zaas, Vzz'ket\nsafe: no creatures", FS)
m.rect(90, 38, 110, 42, HEAD); m.label(118, 40, "Engineering >", F, (240, 240, 240))
blob(m, 30, 18, 22, 13, TUNNEL, 4, 22); m.label(30, 10, "North Tunnels", F)
for (x, y, t) in ((18, 16, "Lizard den"), (32, 20, "Fungus hollow"), (44, 14, "Crystal gallery"), (28, 26, "Tunnel mouth")): m.label(x, y, t, FS)
m.label(30, 33.5, "bugs & lizards; Job's quest: clear 6 (needs a weapon)", FS, (240, 240, 240))
m.d.line([m.P(46, 26), m.P(62, 34)], fill=DIG, width=int(3 * S))
blob(m, 100, 64, 34, 14, (70, 76, 90), 6, 26); m.label(100, 55, "The Caverns (new)", F, (240, 240, 250))
blob(m, 110, 66, 16, 7, LAKE, 8); m.label(110, 66, "the underground sea\n(Zaas was right)", FS, (240, 240, 250))
blob(m, 80, 66, 8, 6, RUIN, 10); m.label(80, 66, "Precursor\nruins", FS)
veins(m, [(88, 72), (92, 58), (126, 60), (72, 60)], CRYST)
m.label(100, 77, "behind the cavern gate: crystals, ruins, bigger creatures, and the water\nthat fills the junction's basins and the hot springs later", FS, (240, 240, 240))
m.d.line([m.P(78, 49), m.P(88, 55)], fill=GATE, width=int(3 * S)); m.label(88, 51, "cavern gate", FS, (240, 240, 240))
m.im.save(MOCK + "/mine_sector.png")
print("ok")
