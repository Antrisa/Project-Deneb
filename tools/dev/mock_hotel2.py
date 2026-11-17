import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_hotel import *

# ============================================================ option C: A's plan, round lobby
m = Mock(150, 90, "The hotel, option C: option A's plan with a round lobby",
         "The lobby is a round hall under a glass dome, the front desk curving along its back. Dining and kitchen west, lounge east, your rooms behind the desk, guest wings south. About 120 x 84 tiles.")
m.rect(1, 3, 120, 88, ROCK, None)
cx, cy = 60, 24
m.rect(57, 3, 63, 9, HALL); m.door(60, 3.5)
m.circ(cx, cy, 15, LOBBY); m.circ(cx, cy - 2, 3.2, (120, 210, 240)); m.label(cx, cy - 2, "fountain", FS)
m.arc(cx, cy, 11, 25, 155, DESK, int(2.6 * S)); m.label(cx, cy + 12.5, "front desk", FS)
boxes(m, [(48, 15, 3, 3, (150, 70, 60)), (69, 15, 3, 3, (150, 70, 60)), (47, 26, 3, 3, (150, 70, 60)), (70, 26, 3, 3, (150, 70, 60))])
m.label(cx, cy - 9, "Round lobby", F)
oct_(m, 12, 10, 42, 34, DINE, 4); m.label(27, 15, "Dining room", F)
for x in (18, 25, 32):
    for y in (21, 28): m.circ(x, y, 1.6, (240, 230, 210))
oct_(m, 12, 36, 32, 50, KITCH, 3); m.label(22, 43, "Kitchen", F)
oct_(m, 78, 10, 108, 34, LOUNGE, 4); m.label(93, 15, "Lounge", F)
boxes(m, [(84, 21, 4, 3, (150, 70, 60)), (92, 21, 4, 3, (150, 70, 60)), (88, 27, 6, 2, (120, 90, 70)), (103, 18, 3, 6, (90, 60, 50))])
m.rect(57, 39, 63, 42, HALL)
oct_(m, 42, 42, 58, 54, OFFICE, 3); m.label(50, 48, "Your\noffice", F)
oct_(m, 62, 42, 78, 54, SUITE, 3); m.label(70, 48, "Your\nbedroom", F)
m.rect(42, 40, 78, 42, HALL)
empty(m, 82, 36, 108, 52, "Spare\n(empty)")
m.rect(4, 56, 116, 61, HALL); m.label(60, 58.5, "Guest corridor", F); m.rect(57, 54, 63, 56, HALL)
empty(m, 4, 63, 56, 86, "West guest wing\n(empty)"); empty(m, 64, 63, 116, 86, "East guest wing\n(empty)")
m.rect(20, 50, 24, 56, HALL)
for x, y in ((60, 9), (42, 22), (45, 22), (75, 22), (78, 22), (22, 35), (50, 42), (70, 42), (60, 39), (95, 52), (30, 61), (90, 61), (60, 54), (22, 50)):
    m.door(x, y)
m.rect(42, 21, 45, 24, HALL); m.rect(75, 21, 78, 24, HALL)
m.legend(122, 6, LEG)
m.im.save(MOCK + "/hotel_option_C.png")

# ============================================================ option D: A's lobby, then a round atrium as the hub
m = Mock(150, 90, "The hotel, option D: a grand lobby opening into a round atrium",
         "Check in at the front desk in the lobby, then walk through into a round atrium: dining west, lounge east, your rooms south, guest wings in the four corners. About 120 x 86 tiles.")
m.rect(1, 3, 120, 88, ROCK, None)
m.rect(57, 3, 63, 8, HALL); m.door(60, 3.5)
oct_(m, 44, 8, 76, 24, LOBBY, 4); m.label(60, 11.5, "Entrance lobby", F)
m.rect(50, 16, 70, 19, DESK); m.label(60, 17.5, "front desk", FS)
boxes(m, [(47, 12, 3, 3, (150, 70, 60)), (70, 12, 3, 3, (150, 70, 60)), (51, 20, 5, 2, (120, 90, 70)), (64, 20, 5, 2, (120, 90, 70))])
m.label(53.5, 22.8, "key board", FS); m.label(66.5, 22.8, "luggage", FS)
cx, cy = 60, 45
m.rect(56, 24, 64, 30, LOBBY)
m.circ(cx, cy, 16, LOBBY); m.circ(cx, cy, 4.5, (120, 210, 240)); m.label(cx, cy, "fountain", FS); m.label(cx, cy - 10, "Atrium", F)
oct_(m, 14, 32, 40, 58, DINE, 4); m.label(27, 37, "Dining room", F)
for x in (20, 27, 34):
    for y in (43, 50): m.circ(x, y, 1.6, (240, 230, 210))
oct_(m, 14, 62, 40, 80, KITCH, 3); m.label(27, 71, "Kitchen", F)
oct_(m, 80, 32, 106, 58, LOUNGE, 4); m.label(93, 37, "Lounge", F)
boxes(m, [(86, 43, 4, 3, (150, 70, 60)), (94, 43, 4, 3, (150, 70, 60)), (90, 50, 6, 2, (120, 90, 70)), (101, 40, 3, 6, (90, 60, 50))])
m.rect(40, 43, 44, 47, LOBBY); m.rect(76, 43, 80, 47, LOBBY)
m.rect(56, 60, 64, 64, HALL)
oct_(m, 44, 64, 58, 78, OFFICE, 3); m.label(51, 71, "Your\noffice", F)
oct_(m, 62, 64, 76, 78, SUITE, 3); m.label(69, 71, "Your\nbedroom", F)
m.rect(44, 62, 76, 64, HALL)
empty(m, 4, 6, 40, 28, "North-west wing\n(empty)"); empty(m, 80, 6, 116, 28, "North-east wing\n(empty)")
empty(m, 80, 62, 116, 86, "South-east wing\n(empty)")
m.rect(40, 14, 44, 18, HALL); m.rect(76, 14, 80, 18, HALL)
m.rect(76, 66, 80, 70, HALL)
for x, y in ((60, 8), (60, 24), (60, 29.5), (40, 45), (44, 45), (76, 45), (80, 45), (60, 61), (51, 64), (69, 64), (40, 16), (80, 16), (80, 68), (27, 58), (27, 62)):
    m.door(x, y)
m.rect(25, 58, 29, 62, HALL)
m.legend(122, 6, LEG)
m.im.save(MOCK + "/hotel_option_D.png")
print("ok")
