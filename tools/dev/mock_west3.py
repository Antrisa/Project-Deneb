import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_west import *
SHED, SPRING, STEAM = (200, 176, 140), (120, 200, 210), (236, 244, 248)
m = Mock(150, 88, "The agri complex: three domes round a central storage shed (its own map, north of the junction)",
         "Walk in from the junction to a crossroads: workshop left, springs right, the shed straight on and the agri dome beyond it. The domes also link to each other. About 100 x 84 tiles.")
m.rect(1, 3, 110, 86, ROCK, None)
sx, sy = 55, 52                                            # the central shed
domes = [("agri", 55, 23, 19), ("work", 24, 64, 13), ("spring", 86, 64, 15)]
for key, x, y, r in domes[:1]:                             # the shed links straight to the agri dome
    a = math.atan2(y - sy, x - sx); ax, ay = sx + 8 * math.cos(a), sy + 8 * math.sin(a); bx, by = x - r * math.cos(a), y - r * math.sin(a)
    m.d.line([m.P(ax, ay), m.P(bx, by)], fill=WALL, width=int(6.4 * S)); m.d.line([m.P(ax, ay), m.P(bx, by)], fill=GLASSC, width=int(5 * S))
    m.door(bx, by); m.door(ax, ay)
# dome-to-dome links: agri to workshop, agri to springs, and workshop to springs (it crosses the way in)
def link(x1, y1, r1, x2, y2, r2):
    a = math.atan2(y2 - y1, x2 - x1)
    ax, ay = x1 + r1 * math.cos(a), y1 + r1 * math.sin(a); bx, by = x2 - r2 * math.cos(a), y2 - r2 * math.sin(a)
    m.d.line([m.P(ax, ay), m.P(bx, by)], fill=WALL, width=int(6.4 * S)); m.d.line([m.P(ax, ay), m.P(bx, by)], fill=GLASSC, width=int(5 * S))
    return (ax, ay), (bx, by)
ring_doors = []
for (x1, y1, r1), (x2, y2, r2) in (((55, 23, 19), (24, 64, 13)), ((55, 23, 19), (86, 64, 15)), ((24, 64, 13), (86, 64, 15))):
    ring_doors += link(x1, y1, r1, x2, y2, r2)
# agri dome
m.circ(55, 23, 19, AGRI)
m.d.pieslice(m.P(36, 4) + m.P(74, 42), 150, 230, fill=(110, 170, 80), outline=WALL, width=3)
for a in range(0, 360, 30):
    x, y = pol(55, 23, 12, a); m.dot(x, y, (130, 110, 90), 1)
m.label(58, 17, "Agri dome", F); m.label(44, 22, "still\ngrows", FS); m.label(62, 31, "dead planters, broken glass", FS)
# workshop dome
m.circ(24, 64, 13, WORK)
boxes(m, [(16, 58, 6, 2, (240, 236, 220)), (25, 57, 6, 2, (240, 236, 220)), (17, 66, 4, 4, (110, 116, 130)), (27, 67, 4, 4, (110, 116, 130))])
m.label(24, 73, "Your workshop", F)
# hot springs & fish ponds dome
m.circ(86, 64, 15, (176, 196, 170))
oct_(m, 77, 54, 89, 64, SPRING, 3); m.label(83, 59, "hot spring\npool", FS)
for (x0, y0, x1, y1) in ((88, 64, 97, 71), (78, 67, 86, 74)): oct_(m, x0, y0, x1, y1, POND, 2)
m.label(92.5, 67.5, "fish\npond", FS); m.label(82, 70.5, "fish\npond", FS)
for x, y in ((80, 53), (85, 52), (88, 54)): m.dot(x, y, STEAM, .7)
m.label(86, 75.5, "Hot springs & ponds", F)
# central storage shed
oct_(m, sx - 8, sy - 7, sx + 8, sy + 7, SHED, 3)
boxes(m, [(sx - 6, sy - 5, 3, 3, (150, 120, 90)), (sx + 3, sy - 5, 3, 3, (150, 120, 90)), (sx - 6, sy + 2, 3, 3, (120, 150, 110)), (sx + 3, sy + 2, 3, 3, (120, 150, 110))])
m.label(sx, sy, "Storage\nshed", F)
# entrance from the junction (it crosses the workshop-springs link at a small crossroads)
m.rect(sx - 3, sy + 7, sx + 3, 86, PLAZA); m.door(sx, sy + 7); m.door(sx, 85.5)
m.rect(sx - 3, 61.5, sx + 3, 66.5, GLASSC); m.label(sx + 8, 69, "crossroads", FS, (240, 240, 240))
for x, y in ring_doors: m.door(x, y)
m.label(sx + 10, 83, "to the junction", FS, (240, 240, 240))
m.legend(114, 6, [(SHED, "Storage shed: seeds, tools, feed, shipping crate"), (AGRI, "Agri dome: your farm"), (WORK, "Your workshop"),
                   (SPRING, "Hot spring (geothermal)"), (POND, "Fish ponds"), (GLASSC, "Glass links"), ((250, 220, 90), "Door")])
m.d.text(m.P(114, 25), "The shed is the hub, and the\ndomes link to each other in a\nring, so you never have to\ndouble back. The springs dome can\nstart dry and cracked, then\nwarm up and fill with fish\nas you restore it.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/west_agri_three_domes.png")
print("ok")
