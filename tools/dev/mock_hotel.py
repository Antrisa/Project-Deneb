import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_west import *
LOBBY, DESK, DINE, KITCH, LOUNGE, SUITE, OFFICE, EMPTY, HALL = ((226, 214, 190), (196, 150, 90), (214, 176, 120), (180, 190, 196),
    (170, 140, 200), (120, 170, 160), (150, 190, 180), (90, 86, 100), (206, 196, 176))
LEG = [(LOBBY, "Entrance lobby"), (DESK, "Front desk area"), (DINE, "Dining room"), (KITCH, "Kitchen"), (LOUNGE, "Lounge"),
       (SUITE, "Your bedroom"), (OFFICE, "Your office"), (HALL, "Corridors"), (EMPTY, "Empty wings: build rooms here"), ((250, 220, 90), "Door")]

def empty(m, x0, y0, x1, y1, t):
    oct_(m, x0, y0, x1, y1, EMPTY, 2)
    for gx in range(int(x0) + 3, int(x1) - 1, 4):
        for gy in range(int(y0) + 3, int(y1) - 1, 4): m.dot(gx, gy, (120, 116, 132), .25)
    m.label((x0 + x1) / 2, (y0 + y1) / 2, t, F, (230, 230, 240))

# ============================================================ option A: grand lobby, wings either side
m = Mock(150, 90, "The hotel, option A: a grand lobby with the guest wings either side",
         "You come in from the junction into a tall lobby with the front desk. Dining and kitchen to the west, lounge to the east, your rooms behind the desk, empty wings for guest rooms. About 120 x 84 tiles.")
m.rect(1, 3, 120, 88, ROCK, None)
m.rect(57, 3, 63, 10, HALL); m.door(60, 3.5); m.label(66, 6, "from the junction", FS, (240, 240, 240))
oct_(m, 44, 10, 76, 34, LOBBY, 5); m.label(60, 14, "Entrance lobby", F)
m.rect(50, 24, 70, 28, DESK); m.label(60, 26, "front desk", FS)
boxes(m, [(51, 29, 6, 2, (120, 90, 70)), (63, 29, 6, 2, (120, 90, 70)), (47, 16, 3, 3, (150, 70, 60)), (70, 16, 3, 3, (150, 70, 60)), (58, 18, 4, 2, (200, 180, 120))])
m.label(53, 31.5, "key board", FS); m.label(66, 31.5, "luggage", FS); m.label(60, 20.5, "bell & sofas", FS)
# your rooms behind the desk
m.rect(50, 34, 70, 37, HALL)
oct_(m, 44, 37, 59, 52, OFFICE, 3); m.label(51.5, 44, "Your\noffice", F)
oct_(m, 61, 37, 76, 52, SUITE, 3); m.label(68.5, 44, "Your\nbedroom", F)
# dining + kitchen west
oct_(m, 14, 10, 42, 34, DINE, 4); m.label(28, 16, "Dining room", F)
for x in (19, 26, 33):
    for y in (21, 28): m.circ(x, y, 1.6, (240, 230, 210))
oct_(m, 14, 36, 34, 50, KITCH, 3); m.label(24, 43, "Kitchen", F)
# lounge east
oct_(m, 78, 10, 106, 34, LOUNGE, 4); m.label(92, 16, "Lounge", F)
boxes(m, [(84, 22, 4, 3, (150, 70, 60)), (92, 22, 4, 3, (150, 70, 60)), (88, 28, 6, 2, (120, 90, 70)), (101, 19, 3, 6, (90, 60, 50))])
m.label(100, 30, "bar & fireplace", FS)
# corridors and empty wings
m.rect(4, 54, 116, 59, HALL); m.label(60, 56.5, "Guest corridor", F)
m.rect(57, 52, 63, 54, HALL)
empty(m, 4, 61, 56, 86, "West guest wing\n(empty)"); empty(m, 64, 61, 116, 86, "East guest wing\n(empty)")
empty(m, 78, 36, 106, 52, "Spare\n(empty)")
for x, y in ((60, 10), (43, 22), (77, 22), (24, 35), (51.5, 37), (68.5, 37), (60, 52), (30, 59), (90, 59), (92, 52), (24, 52)):
    m.door(x, y)
m.rect(22, 50, 26, 54, HALL)
m.legend(122, 6, LEG)
m.d.text(m.P(122, 30), "Empty wings are bare floor\nwith marked plots; later you\nbuild guest rooms, a spa,\nshops... in them.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/hotel_option_A.png")

# ============================================================ option B: an atrium with the rooms round it
m = Mock(150, 90, "The hotel, option B: a big round atrium, everything off it",
         "A tall atrium under a glass dome is the heart: front desk at the entrance, dining, lounge and your rooms round the ring, empty guest wings beyond. About 116 x 84 tiles.")
m.rect(1, 3, 120, 88, ROCK, None)
cx, cy = 60, 44
m.rect(57, 3, 63, 14, HALL); m.door(60, 3.5)
oct_(m, 48, 12, 72, 24, LOBBY, 3); m.label(60, 15, "Entrance", F); m.rect(52, 20, 68, 23, DESK); m.label(60, 21.5, "front desk", FS)
m.circ(cx, cy, 17, LOBBY); m.circ(cx, cy, 5, (120, 210, 240)); m.label(cx, cy, "atrium\nfountain", FS)
m.label(cx, cy - 11, "Atrium", F)
m.d.pieslice(m.P(cx - 30, cy - 30) + m.P(cx + 30, cy + 30), 145, 215, fill=DINE, outline=WALL, width=3); m.circ(cx, cy, 17, LOBBY)
m.circ(cx, cy, 5, (120, 210, 240)); m.label(cx, cy, "atrium\nfountain", FS); m.label(cx, cy - 11, "Atrium", F)
m.label(cx - 24, cy, "Dining\nroom", F)
oct_(m, 14, 30, 26, 58, KITCH, 3) if False else None
m.d.pieslice(m.P(cx - 30, cy - 30) + m.P(cx + 30, cy + 30), -35, 35, fill=LOUNGE, outline=WALL, width=3); m.circ(cx, cy, 17, LOBBY)
m.circ(cx, cy, 5, (120, 210, 240)); m.label(cx, cy, "atrium\nfountain", FS); m.label(cx, cy - 11, "Atrium", F)
m.label(cx + 24, cy, "Lounge", F)
oct_(m, 8, 34, 28, 54, KITCH, 3); m.label(18, 44, "Kitchen", F)
oct_(m, 44, 64, 58, 78, OFFICE, 3); m.label(51, 71, "Your\noffice", F)
oct_(m, 62, 64, 76, 78, SUITE, 3); m.label(69, 71, "Your\nbedroom", F)
m.rect(40, 60.5, 80, 63.5, HALL)
empty(m, 4, 6, 44, 30, "North-west wing\n(empty)"); empty(m, 76, 6, 116, 30, "North-east wing\n(empty)")
empty(m, 4, 60, 40, 86, "South-west wing\n(empty)"); empty(m, 80, 60, 116, 86, "South-east wing\n(empty)")
for x, y in ((60, 12), (60, 27), (31, 44), (29, 44), (89, 44), (60, 61), (51, 64), (69, 64), (44, 22), (76, 22), (40, 62), (80, 62)):
    m.door(x, y)
m.legend(122, 6, LEG)
m.d.text(m.P(122, 30), "Four empty wings round the\natrium; open them up as the\nhotel grows.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/hotel_option_B.png")
print("ok")
