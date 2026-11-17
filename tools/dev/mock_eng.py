import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_base import *
CORE_C, HALL, BAY, ORE, LIFE, STORE, SHOP, SUITE, SPARE, BREAK, LIFTC, RAMP = (230, 120, 80), (226, 214, 190), (150, 170, 196), (196, 150, 110), (120, 196, 196), (176, 168, 150), (230, 190, 110), (168, 132, 210), (190, 200, 170), (206, 146, 128), (240, 200, 80), (140, 120, 100)
LOCK = (220, 80, 70)
LEG = [(HALL, "Engineering hall / corridors"), (CORE_C, "Geothermal power core"), (BAY, "Shuttle bay (your ship)"), (SUITE, "Shipwright's Suite (locked, restored later)"),
       (ORE, "Ore processing (furnaces)"), (LIFE, "Life support & heating pumps"), (SHOP, "Tikka's engineering bay"), (STORE, "Stores"),
       (BREAK, "Crew break room & lockers"), (SPARE, "Spare workshops (future residents)"), (LIFTC, "Lift to the promenade"), (RAMP, "Ramp down to the mine"),
       ((250, 220, 90), "Door"), (LOCK, "Locked door")]

# ---------------------------------------------------------------- option A: round hall, wings off it
m = Mock(112, 70, "Engineering, option A: a round hall with the wings around it",
         "Like the promenade: the lift opens into a round engineering hall; every room is a wing off its ring. The shuttle bay is its own big map. About 80 x 66 tiles (now 58 x 24).")
cx, cy = 40, 34
m.circ(cx, cy, 33, ROCK, None)
m.rect(cx - 9, 3, cx + 9, cy - 13, CORE_C); m.circ(cx, 12, 8, CORE_C)                   # power core, north
m.rect(cx + 13, cy - 6, cx + 34, cy + 6, BAY)                                            # shuttle bay link, east
m.rect(cx + 22, cy - 13, cx + 34, cy - 7, SUITE)
m.rect(cx - 33, cy - 7, cx - 13, cy + 7, ORE)                                            # ore processing, west
m.rect(cx - 37, cy - 3, cx - 33, cy + 3, RAMP)
m.rect(cx - 9, cy + 13, cx + 9, cy + 28, LIFE)                                           # life support, south
for (x0, y0, x1, y1, c) in ((cx - 27, cy - 21, cx - 15, cy - 11, SHOP), (cx + 15, cy + 11, cx + 27, cy + 21, STORE),
                            (cx - 27, cy + 11, cx - 15, cy + 21, BREAK), (cx + 15, cy - 25, cx + 25, cy - 16, SPARE),
                            (cx - 25, cy + 22, cx - 15, cy + 30, SPARE), (cx + 15, cy + 22, cx + 25, cy + 30, SPARE)):
    m.rect(x0, y0, x1, y1, c)
m.circ(cx, cy, 13, HALL)
m.rect(cx - 3, cy - 3, cx + 3, cy + 3, LIFTC)
for (x, y, lk) in ((cx, cy - 13, 0), (cx + 13, cy, 0), (cx - 13, cy, 0), (cx, cy + 13, 0), (cx - 11, cy - 9, 0), (cx + 11, cy + 9, 0), (cx - 11, cy + 9, 0),
                   (cx + 10, cy - 10, 0), (cx + 28, cy - 7, 1), (cx - 16, cy + 22, 0), (cx + 16, cy + 22, 0)):
    m.door(x, y, bool(lk))
m.label(cx, 12, "Geothermal\npower core\nturbines, heat vents")
m.label(cx + 24, cy, "To the shuttle bay\n(its own big map)")
m.label(cx + 28, cy - 10, "Shipwright's\nSuite")
m.label(cx - 23, cy, "Ore processing\nfurnaces, crusher")
m.label(cx - 35, cy + 5.5, "Mine ramp", FS, (230, 230, 236))
m.label(cx, cy + 21, "Life support\nheating pumps,\nair & water")
m.label(cx - 21, cy - 16, "Tikka's\nengineering bay")
m.label(cx + 21, cy + 16, "Stores")
m.label(cx - 21, cy + 16, "Break room\n& lockers")
m.label(cx + 20, cy - 20.5, "Spare\nworkshop"); m.label(cx - 20, cy + 26, "Spare\nworkshop"); m.label(cx + 20, cy + 26, "Spare\nworkshop")
m.label(cx, cy + 6, "Engineering hall", F)
m.label(cx, cy, "Lift")
m.legend(80, 6, LEG)
m.d.text(m.P(80, 39), "Walk: lift > hall > any wing in a few steps.\nThe big pieces (core, ore, life support)\nsit on the four sides; small rooms on\nthe diagonals. Three spare workshops\nfor new residents and activities.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/eng_option_A.png")

# ---------------------------------------------------------------- option B: one long works floor
m = Mock(112, 62, "Engineering, option B: one long works floor between the mine and the hangar",
         "A wide industrial spine: mine ramp at the west end, the shuttle bay (its own big map) through doors at the east end, rooms either side. About 96 x 44 tiles.")
y0 = 22
m.rect(2, 4, 100, 44, ROCK, None)
m.rect(6, y0, 96, y0 + 7, HALL)
m.rect(2, y0 + 1, 6, y0 + 6, RAMP)
m.rect(96, y0 - 4, 100, y0 + 11, BAY)
m.rect(24, 8, 38, y0 - 1, CORE_C); m.circ(31, 15, 5, CORE_C)
north = [(8, 22, ORE, "Ore processing\nfurnaces, crusher"), (24, 38, CORE_C, "Geothermal\npower core"), (40, 46, LIFTC, "Lift"),
         (48, 62, SHOP, "Tikka's\nengineering bay"), (64, 74, SPARE, "Spare\nworkshop"), (76, 94, SUITE, "Shipwright's\nSuite")]
south = [(8, 26, LIFE, "Life support\nheating pumps"), (28, 38, STORE, "Stores"), (40, 52, BREAK, "Break room\n& lockers"),
         (54, 64, SPARE, "Spare\nworkshop"), (66, 76, SPARE, "Spare\nworkshop"), (78, 94, STORE, "Cargo\nstaging")]
for x0, x1, c, t in north:
    top = 8 if c not in (LIFTC,) else 14
    if c != CORE_C: m.rect(x0, top, x1, y0 - 1, c)
    m.door((x0 + x1) / 2, y0 - 1, c == SUITE); m.label((x0 + x1) / 2, (top + y0) / 2, t)
for x0, x1, c, t in south:
    m.rect(x0, y0 + 8, x1, 40, c); m.door((x0 + x1) / 2, y0 + 8); m.label((x0 + x1) / 2, (y0 + 48) / 2, t)
m.label(51, y0 + 3.5, "Engineering works floor: pipes overhead, cranes, carts", F)
m.label(4, y0 + 9, "Mine", FS, (230, 230, 236)); m.label(98, y0 + 13, "Shuttle bay >", FS, (230, 230, 236))
m.legend(4, 46, LEG[:7]); m.legend(56, 46, LEG[7:])
m.im.save(MOCK + "/eng_option_B.png")
