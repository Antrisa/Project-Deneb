import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_eng2 import *

m = Mock(150, 80, "Engineering, option E: C's ore processing and life support round D's sunken power core",
         "The hall loops round the core pit; the ore rooms fill the west end with belts from the mine; cooling and life support bulge out south of the core. About 118 x 72 tiles.")
m.rect(1, 3, 120, 78, ROCK, None)
hx0, hy0, hx1, hy1 = 40, 24, 100, 52                  # the hall loop
cx, cy = 70, 38
# --- ore processing (as in C): big north-west room, sorting room below, mine tunnel in the south-west
poly(m, [(10, 14), (24, 8), (34, 8), (40, 14), (40, 34), (6, 34), (6, 18)], ORE)
poly(m, [(6, 40), (40, 40), (40, 52), (32, 60), (6, 60)], ORE)
m.rect(6, 34, 40, 40, HALL)                            # short hall from the loop to the ore rooms
m.rect(1, 54, 8, 60, RAMP); m.label(4, 62, "Mine", FS, (230, 230, 236))
belt(m, [(2, 57), (14, 57), (14, 46), (14, 26), (20, 18), (30, 18)])
boxes(m, [(28, 14, 4, 4, MACH), (33, 14, 3, 4, (180, 90, 60)), (33, 20, 3, 4, (180, 90, 60)), (26, 24, 5, 3, MACH), (18, 27, 5, 3, MACH)])
belt(m, [(30, 26), (30, 30), (37, 30)], 1)
boxes(m, [(22, 44, 4, 3, MACH), (28, 44, 4, 3, MACH), (22, 52, 6, 3, (150, 130, 110))])
m.label(25, 11.5, "Ore processing"); m.label(29, 50, "sorting\n& carts", FS)
# --- Tikka's bay: the whole north side, with her office
poly(m, [(48, hy0), (48, 12), (54, 6), (90, 6), (96, 12), (96, hy0)], SHOP)
m.rect(86, 7, 95, 14, (240, 214, 150)); m.label(90.5, 10.5, "office", FS)
boxes(m, [(51, 10, 7, 2.5, DESK), (51, 15, 7, 2.5, DESK), (61, 8, 10, 2, PANEL), (86, 17, 6, 4, MACH), (51, 19, 4, 3, MACH)])
m.circ(75, 15, 4.5, (210, 170, 90)); m.label(75, 15, "drone\npit", FS)
m.label(66, 21, "Tikka's engineering bay", F)
# --- lift north-east, stores & cargo east, the bay
m.rect(102, 14, 110, hy0, LIFTC); m.label(106, 18.5, "Lift", FS)
poly(m, [(hx1, hy0 + 2), (108, hy0 + 2), (114, 30), (114, 35), (hx1, 35)], STORE); m.label(108, 31, "Stores")
poly(m, [(hx1, 41), (114, 41), (114, hy1), (106, hy1 + 8), (hx1, hy1 + 8)], STORE); m.label(108, 49, "Cargo\nstaging")
m.rect(hx1, 35, 116, 41, HALL); m.rect(116, 35, 120, 41, BAY); m.label(117, 33, "Bay >", FS, (230, 230, 236))
# --- cooling & life support (shape from C) south of the core
poly(m, [(58, hy1), (82, hy1), (82, 64), (76, 70), (64, 70), (58, 64)], LIFE)
for x in (64, 70, 76): m.circ(x, 63, 2.6, TANK)
m.label(70, 68, "Cooling & life support", F)
# --- break room, spares
poly(m, [(40, hy1), (57, hy1), (57, 70), (47, 74), (36, 74), (30, 68), (30, 62), (40, 54)], BREAK)
boxes(m, [(32, 63, 2, 6, (80, 110, 140)), (34, 71, 9, 2, DESK), (45, 70, 6, 2, (200, 120, 90))])
for tx, ty in ((44, 56), (50, 56), (44, 62), (50, 62)):
    boxes(m, [(tx, ty, 3.5, 2.5, (230, 200, 150))])
m.label(47, 67, "Crew break room", F); m.label(40, 70.5, "kitchenette, lockers", FS)
oct_(m, 84, hy1, 96, 64, SPARE); m.label(90, 58, "Spare")
oct_(m, 98, hy1 + 9, 110, 70, SPARE); m.label(104, 65, "Spare")
# --- the hall loop and the sunken core
m.rect(hx0, hy0, hx1, hy1, HALL)
oct_(m, hx0 + 8, hy0 + 6, hx1 - 8, hy1 - 6, ROCK, 5)                         # the pit rim (railings)
oct_(m, hx0 + 12, hy0 + 9, hx1 - 12, hy1 - 9, (150, 70, 50), 4)              # pit floor, deeper
m.circ(cx, cy, 5.5, CORE_C); m.circ(cx, cy, 3, (255, 160, 60))
for x in range(54, 88, 6):
    m.d.rectangle(m.P(x, hy0 + 6.4) + m.P(x + 3, hy0 + 7.8), fill=PANEL, outline=WALL)
    m.d.rectangle(m.P(x, hy1 - 7.8) + m.P(x + 3, hy1 - 6.4), fill=PANEL, outline=WALL)
for x in (56, 84): m.circ(x, cy, 2.4, TANK)
for a in (0, 90, 180, 270): line(m, [pol(cx, cy, 5.5, a), pol(cx, cy, 9, a)], POWER, 3)
m.label(cx, hy0 + 3.4, "Geothermal power core, down in its pit", F)
m.label(55, hy1 - 3.2, "panels on the railings; stairs down at both ends", FS)
for x, y in ((hx0 + 8, cy), (hx1 - 8, cy)): m.door(x, y)                     # stairs into the pit
line(m, [(66, hy1 - 9), (66, 60.4)], COOL, 5); line(m, [(74, hy1 - 9), (74, 60.4)], COOL, 5)
line(m, [(hx0 + 2, hy0 + 2), (hx1 - 2, hy0 + 2), (hx1 - 2, hy1 - 2), (hx0 + 2, hy1 - 2), (hx0 + 2, hy0 + 2)], POWER, 3)
line(m, [(hx0 + 2, 37), (8, 37)], POWER, 3)
# refined ore out along the south hall to cargo
belt(m, [(37, 30), (37, 50.5), (hx1 - 3, 50.5), (106, 53)], 1)
for x, y in ((24, 34), (24, 40), (hx0, 37), (72, hy0), (106, hy0), (hx1, 30), (hx1, 47), (70, hy1), (48, hy1), (90, hy1), (104, hy1 + 8.6)):
    m.door(x, y)
common_legend(m, 123, 6)
m.d.text(m.P(123, 41), "Lift > the hall loop, core\nglowing in its pit in the\nmiddle; two stairways down.\nBelt: mine > sorting >\nore processing > south hall\n> cargo staging > the bay.\nCoolant: tanks > core.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/eng_option_E.png")
print("ok")
