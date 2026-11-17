import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_eng2 import Mock, oct_, poly, line, boxes, ROCK, WALL, S, F, FS, FT, frange, pol, LIFTC
from mock_base import *

TERM, GLASSC, RECEP, PLAZA, STAR, HOTEL, AGRI, GARD, WORK, OUT, PAD, KIOSK, POND, AIR = (
    (220, 214, 196), (120, 210, 240), (196, 176, 214), (226, 214, 190), (90, 110, 180), (206, 146, 128), (140, 196, 110),
    (170, 200, 140), (230, 190, 110), (120, 116, 126), (176, 172, 160), (240, 214, 150), (110, 170, 210), (150, 150, 160))
LOCK = (220, 80, 70)
LEG = [(PLAZA, "Halls and plazas"), (TERM, "Terminal / departures"), (GLASSC, "Big windows onto the crater"), (RECEP, "Reception & customs (S.A.R.A.)"),
       (KIOSK, "Empty kiosks (future shops)"), (STAR, "Star dome (observation)"), (AIR, "Airlock"), (OUT, "Moon surface (outside)"), (PAD, "Landing pad"),
       (GARD, "Broken garden"), (POND, "Dry fish ponds"), (AGRI, "Your agri dome (own map)"), (WORK, "Your workshop"), (HOTEL, "Old barracks / future hotel (own map)"),
       ((250, 220, 90), "Door"), (LOCK, "Locked / sealed")]


def window(m, x0, y0, x1, y1):
    m.d.line([m.P(x0, y0), m.P(x1, y1)], fill=GLASSC, width=7)


def outside(m, x0, y0, x1, y1):
    m.rect(x0, y0, x1, y1, OUT, None)
    import random; r = random.Random(4)
    for _ in range(30):
        x, y, rr = r.uniform(x0 + 1, x1 - 1), r.uniform(y0 + 1, y1 - 1), r.uniform(.4, 1.4)
        m.d.ellipse(m.P(x - rr, y - rr) + m.P(x + rr, y + rr), outline=(96, 92, 104), width=2)


def pad(m, cx, cy, r):
    m.circ(cx, cy, r, PAD); m.circ(cx, cy, r - 2, PAD, (220, 180, 60), 3)
    m.d.text(m.P(cx - 1.2, cy - 1.6), "H", fill=(220, 180, 60), font=FT)


def legend(m, x, y, note):
    m.legend(x, y, LEG)
    m.d.text(m.P(x, y + len(LEG) * 2.2 + 1), note, fill=(230, 230, 236), font=FS)


# ============================================================ option A: the terminal hall
m = Mock(150, 82, "Spaceport District, option A: a terminal hall along big crater windows",
         "Like an old airport: a long departures hall looks out over the landing pad; the Main Level walkway arrives into a plaza. About 100 x 76 tiles.")
m.rect(1, 3, 112, 80, ROCK, None)
outside(m, 1, 3, 25, 80); pad(m, 12, 41, 9)
for y, lk, t in ((20, 1, "Gate 2"), (41, 0, "Gate 1"), (62, 1, "Gate 3")):
    m.rect(20 if not lk else 22, y - 2.5, 28, y + 2.5, AIR if not lk else (90, 90, 100))
    m.door(26, y, lk) if lk else m.door(22, y, True)
m.label(12, 52.5, "Landing pad\n(outside: needs a space suit)", FS, (240, 240, 240))
m.label(23.5, 38, "Airlock", FS, (30, 30, 40))
oct_(m, 28, 10, 44, 74, TERM, 4)
window(m, 28.2, 14, 28.2, 70)
for y in (14, 26, 33, 49, 56, 68): boxes(m, [(30, y, 2, 3.5, (150, 160, 180))])
m.label(36, 42, "Departures\nhall", F)
m.label(36, 17, "Gate 2\nsealed", FS); m.label(36, 66, "Gate 3\nsealed", FS)
for y in (22, 30, 54, 62): m.rect(40, y, 44, y + 5, KIOSK)
m.label(42, 27, "kiosks", FS)
# reception & customs between the hall and the plaza
m.rect(44, 33, 60, 51, RECEP)
m.d.line([m.P(52, 33), m.P(52, 40)], fill=(60, 60, 70), width=5); m.d.line([m.P(52, 44), m.P(52, 51)], fill=(60, 60, 70), width=5)
m.dot(50, 38, (92, 214, 222), 1.1); m.label(52, 47.5, "Reception\n& customs", F); m.label(48, 36, "S.A.R.A.", FS)
# arrivals plaza
oct_(m, 60, 26, 86, 58, PLAZA, 6)
m.circ(73, 42, 4, POND); m.label(73, 42, "dry\nfountain", FS)
m.label(73, 31, "Arrivals plaza", F)
m.rect(86, 39, 112, 45, PLAZA); m.label(104, 37.5, "Main Level >", FS, (240, 240, 240))
# star dome NW of the plaza
m.circ(64, 16, 8, STAR); m.label(64, 16, "Star dome", F, (240, 240, 250)); m.rect(62, 23, 66, 27, PLAZA)
# north and south doors to their own maps
m.rect(76, 8, 96, 22, AGRI); m.label(86, 13, "To your agri dome,\nthe broken garden\n& your workshop", FS); m.rect(78, 21, 82, 27, PLAZA)
m.rect(66, 66, 98, 78, HOTEL); m.label(82, 71, "To the old barracks / future hotel", FS); m.rect(70, 57, 74, 67, PLAZA)
for x, y, lk in ((44, 42, 0), (60, 42, 0), (64, 25, 0), (80, 26, 0), (72, 58, 0), (86, 42, 0), (80, 22, 0), (72, 66, 0)): m.door(x, y, lk)
legend(m, 114, 6, "Big windows face the pad; you\nsee ships land once the port\nis fixed. Kiosks become shops\nwhen visitors arrive.")
m.im.save(MOCK + "/west_option_A.png")

# ============================================================ option B: round hub, like the promenade
m = Mock(150, 82, "Spaceport District, option B: a round hub with four wings",
         "Matches the Main Level: a round hub, spokes out to the terminal (west), the gardens (north), the barracks (south) and the Main Level (east). About 100 x 76 tiles.")
m.rect(1, 3, 112, 80, ROCK, None)
outside(m, 1, 3, 23, 80); pad(m, 11, 42, 9)
cx, cy = 66, 42
m.rect(18, 39, 24, 45, AIR); m.label(21, 37, "Airlock", FS, (240, 240, 240)); m.door(18, 42, True)
oct_(m, 24, 24, 40, 60, TERM, 4); window(m, 24.2, 28, 24.2, 56)
m.label(32, 30, "Terminal", F); m.label(32, 54, "gate seats,\nsealed gates", FS)
m.rect(40, 32, 50, 52, RECEP); m.d.line([m.P(45, 32), m.P(45, 39)], fill=(60, 60, 70), width=5); m.d.line([m.P(45, 45), m.P(45, 52)], fill=(60, 60, 70), width=5)
m.label(45, 49, "Customs", FS); m.dot(43, 36, (92, 214, 222), 1.1)
m.rect(50, 39, 54, 45, PLAZA)
for a in (45, 135, 225, 315):
    x, y = pol(cx, cy, 17, a); m.circ(x, y, 4, KIOSK)
m.circ(cx, cy, 13, PLAZA); m.circ(cx, cy, 4, POND); m.label(cx, cy, "dry\nfountain", FS)
m.label(cx, cy - 8.5, "District hub", F)
m.rect(cx - 2.5, 6, cx + 2.5, cy - 12.5, PLAZA); m.rect(cx - 2.5, cy + 12.5, cx + 2.5, 70, PLAZA); m.rect(cx + 12.5, cy - 2.5, 112, cy + 2.5, PLAZA)
m.rect(cx - 12, 4, cx + 12, 10, AGRI); m.label(cx, 7, "To your agri dome, garden & workshop", FS)
m.rect(cx - 16, 70, cx + 16, 79, HOTEL); m.label(cx, 74.5, "To the old barracks / future hotel", FS)
m.circ(44, 14, 8, STAR); m.label(44, 14, "Star dome", F, (240, 240, 250)); m.rect(50, 18, 58, 22, PLAZA)
x, y = pol(cx, cy, 17, 45); m.label(x, y, "kiosk", FS)
m.label(104, cy - 4, "Main Level >", FS, (240, 240, 240))
for x, y in ((40, 42), (50, 42), (cx, 10), (cx, 70), (cx - 13, cy), (54, 20)): m.door(x, y)
legend(m, 114, 6, "Four kiosks on the diagonals;\nthe star dome off the north\nspoke. Same look as the Main\nLevel's rings and spokes.")
m.im.save(MOCK + "/west_option_B.png")

# ============================================================ option C: the garden court at the heart
m = Mock(150, 82, "Spaceport District, option C: the broken garden is the heart of the district",
         "Everything opens off a big courtyard under cracked glass, with the dry fish ponds in the middle. Restoring it is visible progress right where everyone walks. About 104 x 76 tiles.")
m.rect(1, 3, 112, 80, ROCK, None)
outside(m, 1, 3, 21, 80); pad(m, 10, 40, 8.5)
m.rect(17, 37, 23, 43, AIR); m.label(20, 35, "Airlock", FS, (240, 240, 240)); m.door(17, 40, True)
oct_(m, 23, 20, 37, 60, TERM, 4); window(m, 23.2, 24, 23.2, 56)
m.label(30, 26, "Terminal", F); m.label(30, 56, "gates", FS)
m.rect(37, 30, 47, 50, RECEP); m.label(42, 47, "Reception\n& customs", FS); m.dot(41, 34, (92, 214, 222), 1.1)
oct_(m, 47, 14, 95, 66, GARD, 9)
m.d.line([m.P(56, 14), m.P(56, 66)], fill=(200, 220, 230), width=1); m.d.line([m.P(86, 14), m.P(86, 66)], fill=(200, 220, 230), width=1)
for (x0, y0, x1, y1) in ((58, 24, 66, 30), (74, 22, 84, 29), (62, 46, 72, 54), (78, 44, 86, 52)): oct_(m, x0, y0, x1, y1, POND, 2)
m.rect(56, 36, 86, 42, PLAZA); m.rect(68, 14, 74, 66, PLAZA)
m.label(71, 33, "Garden court", F); m.label(71, 60, "dead planters, cracked glass roof,\nfour dry fish ponds", FS)
for (x, y) in ((50, 22), (90, 22), (50, 58), (90, 58)): m.rect(x - 2, y - 2, x + 2, y + 2, KIOSK)
m.circ(56, 8, 6, STAR); m.label(56, 8, "Star\ndome", FS, (240, 240, 250))
m.rect(66, 3, 92, 10, AGRI); m.label(79, 6.5, "To your agri dome & workshop", FS)
m.rect(56, 70, 90, 79, HOTEL); m.label(73, 74.5, "To the old barracks / future hotel", FS)
m.rect(95, 37, 112, 43, PLAZA); m.label(104, 35.5, "Main Level >", FS, (240, 240, 240))
for x, y in ((37, 40), (47, 40), (71, 14), (71, 66), (95, 40), (56, 14)): m.door(x, y)
legend(m, 114, 6, "Fix the ponds and planters\nand the district's heart turns\ngreen. The terminal and pad\nstay on the west side.")
m.im.save(MOCK + "/west_option_C.png")

# ============================================================ the wing maps (same for every option)
m = Mock(150, 82, "Spaceport District: the wings that become their own maps (same for every option)",
         "Behind doors, like the museum and the shuttle bay: your gardens and workshop to the north, the old barracks to the south.")
m.rect(1, 3, 70, 80, ROCK, None); m.rect(74, 3, 148, 80, ROCK, None)
# north: agri dome, broken garden (if not the court), workshop
m.circ(24, 34, 20, AGRI); m.label(24, 22, "Your agri dome", F)
m.d.pieslice(m.P(4, 14) + m.P(44, 54), 120, 210, fill=(110, 170, 80), outline=WALL, width=3)
m.label(13, 38, "the corner\nthat still\ngrows", FS)
for x, y in ((28, 30), (33, 38), (22, 45), (34, 28)): m.dot(x, y, (130, 110, 90), 1.2)
m.label(28, 48, "dead planters, rubble,\nbroken glass to fix", FS)
m.rect(44, 30, 50, 36, PLAZA); oct_(m, 50, 18, 68, 50, WORK, 4); m.label(59, 24, "Your\nworkshop", F)
boxes(m, [(52, 28, 5, 2, (240, 236, 220)), (60, 28, 5, 2, (240, 236, 220)), (53, 40, 4, 4, (110, 116, 130)), (61, 42, 4, 4, (110, 116, 130))])
m.rect(20, 55, 28, 66, PLAZA); m.door(24, 66); m.label(24, 69, "back to the district", FS, (240, 240, 240))
m.door(44, 33); m.door(50, 33)
m.label(35, 76, "North wing: one map", F, (240, 240, 240))
m.d.text(m.P(4, 6), "With option A or B, the broken garden and its dry fish ponds\nare in this map too, between the dome and the workshop.", fill=(230, 230, 236), font=FS)
# south: barracks / hotel
m.rect(78, 10, 144, 18, PLAZA); m.label(111, 14, "Hotel hall (the barracks' old corridor; front desk)", FS)
m.rect(78, 18, 94, 34, (226, 170, 150)); m.label(86, 25, "Head\nofficer's\nquarters\n(you start\nhere)", FS)
for i, x in enumerate((94, 104, 114)):
    m.rect(x, 18, x + 10, 34, HOTEL); m.label(x + 5, 26, "Bunk\nroom", FS)
m.rect(124, 18, 144, 46, (190, 130, 112)); m.label(134, 32, "Old drill hall\n(big, empty:\nthe hotel's\nlounge later)", FS)
m.rect(78, 34, 124, 46, HOTEL); m.label(101, 40, "Bunk rooms (later: guest rooms)", FS)
for x in (86, 99, 109, 119): m.door(x, 18)
m.door(124, 30); m.door(101, 34)
m.rect(108, 4, 114, 10, PLAZA); m.door(111, 10); m.label(111, 6.5, "", FS)
m.label(111, 52, "South wing: one map", F, (240, 240, 240))
m.d.text(m.P(78, 56), "Your quarters stay the head officer's room in the\nold barracks. The hall becomes the hotel's front\ndesk once the port is fixed; the bunk rooms become\nguest rooms; the drill hall becomes the lounge.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/west_wings.png")
print("ok")
