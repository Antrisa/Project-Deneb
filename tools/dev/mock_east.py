import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_west import *
HOME, GYM, COURT, GREEN, ORCH, PLANT, SCHOOL, LAUND, STREET = ((206, 160, 128), (150, 170, 210), (120, 160, 200), (140, 196, 110),
    (110, 170, 80), (160, 168, 176), (230, 200, 120), (180, 200, 220), (220, 206, 176))
LEG = [(PLAZA, "Hub and walks"), (STREET, "Residential street"), (HOME, "Homes (front doors; interiors later)"), (GREEN, "Mess hall greenhouse"),
       (ORCH, "Orchard / herb corner"), (GYM, "Fitness centre"), (COURT, "Low-gravity court / track"), (SCHOOL, "Schoolroom (empty for now)"),
       (LAUND, "Laundry"), (PLANT, "Air reclamation plant"), (AIR, "Airlock"), (OUT, "Outside"), ((250, 220, 90), "Door")]

def homes_row(m, x0, y0, n, w, h, up):
    for i in range(n):
        x = x0 + i * (w + 1)
        m.rect(x, y0, x + w, y0 + h, HOME)
        m.d.polygon([m.P(x, y0 if up else y0 + h), m.P(x + w / 2, (y0 - 2.5) if up else (y0 + h + 2.5)), m.P(x + w, y0 if up else y0 + h)], fill=(150, 90, 70), outline=WALL)
        m.door(x + w / 2, y0 + h if up else y0)
        m.label(x + w / 2, y0 + h / 2, "Home", FS)

# ============================================================ option A: a residential street through the middle
m = Mock(150, 86, "East Complex, option A: a residential street from the hub",
         "The Main Level walkway arrives at a round hub. A tree-lined street runs east with homes both sides; greenhouse north, fitness centre south. About 120 x 80 tiles.")
m.rect(1, 3, 120, 84, ROCK, None)
m.rect(1, 40, 14, 46, PLAZA); m.label(6, 38, "< Main Level", FS, (240, 240, 240))
m.circ(24, 43, 10, PLAZA); m.circ(24, 43, 2.5, (120, 210, 240)); m.label(24, 37, "East hub", F)
m.rect(34, 38, 112, 48, STREET); m.label(73, 43, "Crater Row", F)
for x in range(38, 112, 6): m.dot(x, 39.5, (110, 170, 80), .9); m.dot(x, 46.5, (110, 170, 80), .9)
homes_row(m, 38, 28, 6, 10, 9, True); homes_row(m, 38, 49, 6, 10, 9, False)
m.label(70, 23, "", FS)
# greenhouse north of the hub
m.circ(24, 15, 12, GREEN); m.rect(21, 27, 27, 33, PLAZA)
m.d.pieslice(m.P(12, 3) + m.P(36, 27), 180, 270, fill=ORCH, outline=WALL, width=3)
for y in (11, 15, 19):
    m.d.line([m.P(25, y), m.P(33, y)], fill=(90, 140, 60), width=8)
m.label(26, 8, "Mess hall\ngreenhouse", F); m.label(17, 11, "orchard", FS); m.label(17, 19.5, "herbs", FS)
# fitness south of the hub
oct_(m, 10, 58, 40, 82, GYM, 4); m.label(25, 61, "Fitness centre", F)
oct_(m, 14, 66, 36, 80, COURT, 3); m.label(25, 73, "low-g court\n& running track", FS)
m.rect(21, 53, 27, 58, PLAZA)
# east end: plant, school, laundry, airlock
m.rect(112, 30, 120, 56, PLANT); m.label(116, 43, "Air\nreclam-\nation", FS)
m.rect(104, 48, 110, 66, PLAZA); m.rect(44, 63, 110, 66, PLAZA); m.label(77, 64.5, "back lane", FS)
oct_(m, 44, 68, 60, 83, SCHOOL, 3); m.label(52, 75.5, "School-\nroom", F)
oct_(m, 64, 69, 78, 83, LAUND, 3); m.label(71, 76, "Laundry", F)
m.rect(84, 68, 96, 77, AIR); m.label(90, 72.5, "Airlock", FS); m.door(90, 77, True)
m.rect(82, 77, 120, 84, OUT, None)
for x, y in ((14, 43), (24, 27), (24, 33), (24, 53), (24, 58), (112, 43), (52, 66), (71, 66), (90, 66), (107, 48)): m.door(x, y)
m.legend(122, 6, LEG)
m.d.text(m.P(122, 37), "12 front doors on Crater Row:\nroom for every resident\nwithout a home, and more\nlater.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/east_option_A.png")

# ============================================================ option B: a round neighbourhood
m = Mock(150, 86, "East Complex, option B: a round neighbourhood round a little park",
         "Homes face a ring street round a small park; greenhouse north, fitness centre south, plant east. About 116 x 82 tiles.")
m.rect(1, 3, 120, 84, ROCK, None)
cx, cy = 58, 47
m.rect(1, 44, 30, 50, PLAZA); m.label(6, 42, "< Main Level", FS, (240, 240, 240))
m.circ(cx, cy, 28, ROCK)
m.circ(cx, cy, 22, STREET); m.circ(cx, cy, 13, (150, 196, 120)); m.circ(cx, cy, 3, (120, 210, 240))
m.label(cx, cy - 7, "Little park", F); m.label(cx, cy + 6, "benches, trees,\nbandstand", FS)
for a in range(0, 360, 30):
    if a in (0, 90, 180, 270): continue
    x, y = pol(cx, cy, 25.5, a)
    m.circ(x, y, 3.2, HOME); m.door(*pol(cx, cy, 22.2, a))
m.label(cx + 16, cy - 20, "8 homes", FS, (240, 240, 240))
m.label(cx, cy - 17, "Ring street", FS)
m.circ(cx, 12, 8, GREEN); m.d.pieslice(m.P(cx - 8, 4) + m.P(cx + 8, 20), 180, 260, fill=ORCH, outline=WALL, width=3)
m.rect(cx - 3, 19.5, cx + 3, 25, PLAZA); m.label(cx + 2, 11, "Mess hall\ngreenhouse", FS)
oct_(m, cx - 14, 74, cx + 14, 84, GYM, 3); m.label(cx, 77, "Fitness centre", F); m.label(cx, 81, "gym, low-g court, track", FS)
m.rect(cx - 3, 69, cx + 3, 74, PLAZA)
m.rect(86, 44, 92, 50, PLAZA); m.rect(92, 32, 120, 62, PLANT); m.label(106, 47, "Air reclamation\nplant", F)
oct_(m, 8, 58, 26, 74, SCHOOL, 3); m.label(17, 66, "School-\nroom", F); m.rect(15, 50, 19, 58, PLAZA)
oct_(m, 8, 20, 26, 36, LAUND, 3); m.label(17, 28, "Laundry", F); m.rect(15, 36, 19, 44, PLAZA)
m.rect(96, 70, 108, 80, AIR); m.label(102, 75, "Airlock", FS); m.rect(98, 62, 104, 70, PLAZA)
for x, y in ((30, 47), (cx, 25), (cx, 69), (86, 47), (17, 50), (17, 44), (101, 70), (101, 62), (92, 47)): m.door(x, y)
m.legend(122, 6, LEG)
m.d.text(m.P(122, 37), "A cosy cul-de-sac feel:\nevery front door faces the\npark, so residents meet\nthere in the evenings.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/east_option_B.png")
print("ok")
