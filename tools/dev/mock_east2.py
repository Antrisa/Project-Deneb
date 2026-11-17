import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_east import *
PARK, POND2, PLAY = (150, 196, 120), (120, 190, 220), (230, 170, 120)

def ring_homes(m, cx, cy, r_street_out, n, skip=(), rh=3.2, angles=None):
    for a in (angles or [360 / n * i for i in range(n)]):
        if any(abs((a - s + 180) % 360 - 180) < 1 for s in skip): continue
        x, y = pol(cx, cy, r_street_out + rh + .3, a); m.circ(x, y, rh, HOME); m.door(*pol(cx, cy, r_street_out + .2, a))

def park(m, cx, cy, r, extras=True):
    m.circ(cx, cy, r, PARK)
    if extras:
        m.circ(cx - r * .35, cy + r * .1, r * .28, POND2); m.label(cx - r * .35, cy + r * .1, "pond", FS)
        m.circ(cx + r * .4, cy - r * .2, r * .2, PLAY); m.label(cx + r * .4, cy - r * .2, "play-\nground", FS)
        m.rect(cx - 2, cy - r * .6, cx + 2, cy - r * .45, (200, 170, 120)); m.label(cx, cy - r * .7, "bandstand", FS)
        for a in range(20, 360, 45):
            x, y = pol(cx, cy, r * .82, a); m.dot(x, y, (90, 140, 60), 1)

# ============================================================ B2: bigger ring, 12 homes, shops on the ring
m = Mock(150, 90, "East Complex, B2: a bigger ring with 12 homes, community buildings on the ring",
         "The ring street is the neighbourhood: homes all round it, with the laundry and schoolroom as two of its buildings. A bigger park with a pond and playground. About 120 x 86 tiles.")
m.rect(1, 3, 120, 88, ROCK, None)
cx, cy = 60, 47
m.rect(1, 44, 30, 50, PLAZA); m.label(6, 42, "< Main Level", FS, (240, 240, 240))
m.circ(cx, cy, 25, STREET); park(m, cx, cy, 15)
ring_homes(m, cx, cy, 25, 16, skip=(0, 90, 180, 270, 45, 135))
x, y = pol(cx, cy, 30, 45); oct_(m, x - 5, y - 4, x + 5, y + 4, LAUND, 2); m.label(x, y, "Laundry", FS); m.door(*pol(cx, cy, 25.2, 45))
x, y = pol(cx, cy, 30, 135); oct_(m, x - 5, y - 4, x + 5, y + 4, SCHOOL, 2); m.label(x, y, "School", FS); m.door(*pol(cx, cy, 25.2, 135))
m.circ(cx, 9, 9, GREEN); m.d.pieslice(m.P(cx - 9, 0) + m.P(cx + 9, 18), 180, 260, fill=ORCH, outline=WALL, width=3); m.rect(cx - 3, 17, cx + 3, 22.5, PLAZA)
m.label(cx + 2, 9, "Mess hall\ngreenhouse", FS)
oct_(m, cx - 13, 76, cx + 13, 88, GYM, 3); m.label(cx, 79, "Fitness centre", F); m.label(cx, 84, "gym, low-g court, track", FS); m.rect(cx - 3, 71.5, cx + 3, 76, PLAZA)
m.rect(85, 44, 92, 50, PLAZA); m.rect(92, 30, 120, 60, PLANT); m.label(106, 45, "Air reclamation\nplant", F)
m.rect(98, 60, 104, 68, PLAZA); m.rect(96, 68, 108, 78, AIR); m.label(102, 73, "Airlock", FS)
for x, y in ((35, 47), (cx, 22.5), (cx, 71.5), (85, 47), (92, 47), (101, 60), (101, 68)): m.door(x, y)
m.legend(122, 6, LEG)
m.d.text(m.P(122, 37), "10 homes + laundry + school\nround one ring. Everything\nfaces the park.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/east_option_B2.png")

# ============================================================ B3: the big buildings bulge off the ring
m = Mock(150, 90, "East Complex, B3: the ring with the greenhouse and fitness centre bulging off it",
         "Like the Main Level's corner pods: the greenhouse (north) and fitness centre (south) are big rooms built into the ring itself. A pavilion in the middle of the park. About 116 x 86 tiles.")
m.rect(1, 3, 120, 88, ROCK, None)
cx, cy = 56, 46
m.rect(1, 43, 30, 49, PLAZA); m.label(6, 41, "< Main Level", FS, (240, 240, 240))
m.circ(cx, cy - 26, 14, GREEN); m.d.pieslice(m.P(cx - 14, cy - 40) + m.P(cx + 14, cy - 12), 180, 250, fill=ORCH, outline=WALL, width=3)
m.label(cx + 3, cy - 31, "Mess hall\ngreenhouse", F)
oct_(m, cx - 17, cy + 16, cx + 17, cy + 40, GYM, 6); oct_(m, cx - 11, cy + 25, cx + 11, cy + 37, COURT, 3)
m.label(cx - 11, cy + 21, "Fitness", F); m.label(cx, cy + 31, "low-g court\n& track", FS)
m.circ(cx, cy, 22, STREET); park(m, cx, cy, 12, extras=False)
oct_(m, cx - 4, cy - 3, cx + 4, cy + 3, (200, 170, 120), 2); m.label(cx, cy, "pavilion", FS)
for a in range(15, 360, 60):
    x, y = pol(cx, cy, 8, a); m.dot(x, y, (90, 140, 60), 1)
ring_homes(m, cx, cy, 22, 12, angles=[20, 40, 140, 160, 200, 220, 320, 340])
x, y = pol(cx, cy, 30, 180); oct_(m, x - 5, y - 7, x + 1, y - 1, LAUND, 2); m.label(x - 2, y - 4, "Laun-\ndry", FS)
oct_(m, x - 5, y + 1, x + 1, y + 7, SCHOOL, 2); m.label(x - 2, y + 4, "School", FS)
m.rect(78, 43, 90, 49, PLAZA); m.rect(90, 30, 118, 62, PLANT); m.label(104, 46, "Air reclamation\nplant", F)
m.rect(97, 62, 103, 70, PLAZA); m.rect(94, 70, 106, 80, AIR); m.label(100, 75, "Airlock", FS)
for x, y in ((34, 46), (cx, cy - 22), (cx, cy + 22), (78, 46), (90, 46), (100, 62), (100, 70)): m.door(x, y)
m.legend(122, 6, LEG)
m.d.text(m.P(122, 37), "8 homes round the ring.\nGreenhouse and gym are part\nof the ring, so you pass\nthem on every lap.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/east_option_B3.png")

# ============================================================ B4: two rings, homes and activities
m = Mock(150, 90, "East Complex, B4: two rings - a home ring and an activity ring",
         "The ring of homes round its park, and next to it a second, busier ring round a little square: greenhouse, fitness centre, laundry and schoolroom. About 120 x 86 tiles.")
m.rect(1, 3, 120, 88, ROCK, None)
hx, hy, ax, ay = 34, 48, 86, 46
m.rect(1, 45, 15, 51, PLAZA); m.label(7, 43, "< Main Level", FS, (240, 240, 240))
m.circ(hx, hy, 19, STREET); park(m, hx, hy, 11)
ring_homes(m, hx, hy, 19, 12, skip=(180, 0))
m.rect(53, 44, 69, 50, PLAZA)
m.circ(ax, ay, 17, PLAZA); m.circ(ax, ay, 4, (120, 210, 240)); m.label(ax, ay - 8, "Activity square", F)
m.circ(ax, ay - 29, 11, GREEN); m.d.pieslice(m.P(ax - 11, ay - 40) + m.P(ax + 11, ay - 18), 180, 250, fill=ORCH, outline=WALL, width=3)
m.rect(ax - 3, ay - 19.5, ax + 3, ay - 16.5, PLAZA); m.label(ax + 2, ay - 30, "Mess hall\ngreenhouse", FS)
oct_(m, ax - 14, ay + 20, ax + 14, ay + 40, GYM, 4); oct_(m, ax - 9, ay + 26, ax + 9, ay + 38, COURT, 3)
m.rect(ax - 3, ay + 16.5, ax + 3, ay + 20, PLAZA); m.label(ax, ay + 23, "Fitness centre", F)
oct_(m, ax + 20, ay - 10, ax + 32, ay + 0, LAUND, 2); m.label(ax + 26, ay - 5, "Laundry", FS); m.rect(ax + 16.5, ay - 6, ax + 20, ay - 3, PLAZA)
oct_(m, ax + 20, ay + 2, ax + 32, ay + 12, SCHOOL, 2); m.label(ax + 26, ay + 7, "School", FS); m.rect(ax + 16.5, ay + 5, ax + 20, ay + 8, PLAZA)
m.rect(ax - 22, ay + 24, ax - 16, ay + 30, PLANT) if False else None
m.rect(104, 62, 120, 86, PLANT); m.label(112, 74, "Air recl.\nplant", FS); m.rect(99, 56, 105, 62, PLAZA)
oct_(m, 58, 72, 72, 86, AIR, 2); m.label(65, 79, "Airlock", FS); m.rect(63, 50, 67, 72, PLAZA)
for x, y in ((15, 48), (53, 47), (69, 47), (ax, ay - 17), (ax, ay + 17), (ax + 17, ay - 4.5), (ax + 17, ay + 6.5), (102, 56), (65, 72), (65, 50)): m.door(x, y)
m.legend(122, 6, LEG)
m.d.text(m.P(122, 37), "Quiet ring for homes (10),\nbusy ring for the places\nresidents go. Easy to add a\nthird ring later.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/east_option_B4.png")
print("ok")
