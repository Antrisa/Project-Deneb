import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_west import *

# ============================================================ option D: C's shape, a plain plaza for now
m = Mock(150, 82, "Spaceport District, option D: option C's shape as a plaza (garden later)",
         "The big octagonal junction, crossing walks and corner kiosks of option C. The four basins stay empty for now and can become ponds and gardens later. About 104 x 76 tiles.")
m.rect(1, 3, 112, 80, ROCK, None)
outside(m, 1, 3, 21, 80); pad(m, 10, 40, 8.5)
m.rect(17, 37, 23, 43, AIR); m.label(20, 35, "Airlock", FS, (240, 240, 240)); m.door(17, 40, True)
oct_(m, 23, 20, 37, 60, TERM, 4); window(m, 23.2, 24, 23.2, 56)
m.label(30, 26, "Terminal", F); m.label(30, 55, "gate seats,\nsealed gates", FS)
m.rect(37, 30, 47, 50, RECEP); m.label(42, 47, "Reception\n& customs", FS); m.dot(41, 34, (92, 214, 222), 1.1)
oct_(m, 47, 14, 95, 66, PLAZA, 9)
EMPTY = (170, 164, 150)
for (x0, y0, x1, y1) in ((57, 22, 66, 31), (76, 22, 85, 31), (57, 49, 66, 58), (76, 49, 85, 58)): oct_(m, x0, y0, x1, y1, EMPTY, 2)
m.label(61.5, 26.5, "empty\nbasin", FS); m.label(80.5, 53.5, "empty\nbasin", FS)
m.d.line([m.P(71, 14), m.P(71, 66)], fill=(200, 190, 170), width=1); m.d.line([m.P(47, 40), m.P(95, 40)], fill=(200, 190, 170), width=1)
m.circ(71, 40, 4, (150, 150, 160)); m.label(71, 40, "beacon\nmast", FS)
m.label(71, 35, "District junction", F)
m.label(71, 63, "benches, lamps, signposts; basins become\nponds & gardens after the undersea ocean", FS)
for (x, y) in ((51, 22), (91, 22), (51, 58), (91, 58)): m.rect(x - 2.5, y - 2.5, x + 2.5, y + 2.5, KIOSK)
m.label(91, 17.5, "kiosks", FS)
m.circ(56, 8, 6, STAR); m.label(56, 8, "Star\ndome", FS, (240, 240, 250))
m.rect(66, 3, 92, 10, AGRI); m.label(79, 6.5, "To the agri complex (own map)", FS)
m.rect(56, 70, 90, 79, HOTEL); m.label(73, 74.5, "To the hotel (own map)", FS)
m.rect(95, 37, 112, 43, PLAZA); m.label(104, 35.5, "Main Level >", FS, (240, 240, 240))
for x, y in ((37, 40), (47, 40), (71, 14), (71, 66), (95, 40), (56, 14)): m.door(x, y)
legend(m, 114, 6, "Same footprint as option C.\nThe basins are dry, fenced\nand dusty until the ocean\nquest brings water.")
m.im.save(MOCK + "/west_option_D.png")

# ============================================================ the agri complex: two ways to join dome and workshop
m = Mock(150, 85, "The agri complex (its own map, north of the junction): two ways to join the dome and the workshop",
         "Both are round, in the station's style. The dome is your farm: one corner still grows; the rest is dead planters and broken glass to fix.")
m.rect(1, 3, 72, 80, ROCK, None); m.rect(76, 3, 148, 80, ROCK, None)
# 1: ring complex round the dome, workshop as a wing of the ring
cx, cy = 34, 38
m.circ(cx, cy, 30, PLAZA)
m.circ(cx, cy, 24, ROCK)
m.circ(cx, cy, 22, AGRI)
m.d.pieslice(m.P(cx - 22, cy - 22) + m.P(cx + 22, cy + 22), 130, 220, fill=(110, 170, 80), outline=WALL, width=3)
for a in range(0, 360, 30):
    x, y = pol(cx, cy, 15, a); m.dot(x, y, (130, 110, 90), 1)
for a in (0, 90, 180, 270):
    x, y = pol(cx, cy, 23, a); m.door(x, y)
m.label(cx, cy - 4, "Agri dome", F); m.label(cx - 12, cy + 2, "still\ngrows", FS); m.label(cx + 6, cy + 10, "dead planters\nto restore", FS)
m.label(cx, cy - 27, "ring corridor: seed store, tool room,\nwater tanks, compost, in the ring", FS)
m.circ(64, 18, 9, WORK); m.rect(56, 22, 60, 26, PLAZA); m.label(64, 18, "Your\nworkshop", F)
m.rect(cx - 3, 66, cx + 3, 79, PLAZA); m.door(cx, 79); m.label(cx + 9, 76, "to the junction", FS, (240, 240, 240))
m.door(58.5, 24)
m.label(36, 81.5, "1: a ring round the dome, workshop off the ring", F, (240, 240, 240))
# 2: two domes joined by a glass link
m.circ(102, 40, 22, AGRI)
m.d.pieslice(m.P(80, 18) + m.P(124, 62), 130, 220, fill=(110, 170, 80), outline=WALL, width=3)
for a in range(0, 360, 36):
    x, y = pol(102, 40, 14, a); m.dot(x, y, (130, 110, 90), 1)
m.label(102, 34, "Agri dome", F); m.label(90, 42, "still\ngrows", FS)
m.rect(123, 36, 130, 44, GLASSC); m.label(126.5, 32.5, "glass\nlink", FS, (240, 240, 240))
m.circ(138, 40, 9, WORK); m.label(138, 40, "Your\nworkshop", F)
m.rect(98, 62, 106, 79, PLAZA); m.door(102, 62); m.door(102, 79)
oct_(m, 108, 64, 122, 76, PLAZA, 3); m.label(115, 70, "potting shed\n& seed store", FS); m.door(106, 70)
m.door(123, 40); m.door(130, 40)
m.label(112, 81.5, "2: two domes joined by a glass link", F, (240, 240, 240))
m.im.save(MOCK + "/west_agri_complex.png")
print("ok")
