import os as _os
MOCK = _os.environ.get("MOCK_OUT", "mock"); _os.makedirs(MOCK, exist_ok=True)
from PIL import Image, ImageDraw, ImageFont
import math
S = 12
BG, ROCK, WALL = (14, 18, 30), (92, 84, 102), (36, 40, 54)
PATH, CORE, OBS, MUSEUM, SANCT, LAB, STORE, HOME, SPARE, LIFT, GLASS = (226, 214, 190), (120, 196, 196), (150, 178, 206), (198, 168, 128), (168, 132, 210), (150, 150, 160), (176, 168, 150), (206, 146, 128), (190, 200, 170), (240, 200, 80), (120, 210, 240)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
FS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
FT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)


class Mock:
    def __init__(self, w, h, title, sub):
        self.im = Image.new("RGB", (w * S, h * S + 70), BG); self.d = ImageDraw.Draw(self.im)
        self.d.text((14, 8), title, fill=(255, 226, 150), font=FT); self.d.text((14, 40), sub, fill=(220, 220, 230), font=FS)
    def P(self, x, y): return (x * S, y * S + 70)
    def circ(self, cx, cy, r, fill, outline=WALL, width=3):
        self.d.ellipse(self.P(cx - r, cy - r) + self.P(cx + r, cy + r), fill=fill, outline=outline, width=width)
    def sector(self, cx, cy, r0, r1, a0, a1, fill, outline=WALL, width=3):
        pts = [self.P(cx + r1 * math.cos(math.radians(a)), cy + r1 * math.sin(math.radians(a))) for a in frange(a0, a1)]
        pts += [self.P(cx + r0 * math.cos(math.radians(a)), cy + r0 * math.sin(math.radians(a))) for a in frange(a1, a0)]
        self.d.polygon(pts, fill=fill, outline=outline, width=width)
    def rect(self, x0, y0, x1, y1, fill, outline=WALL, width=3):
        self.d.rectangle(self.P(x0, y0) + self.P(x1, y1), fill=fill, outline=outline, width=width)
    def arc(self, cx, cy, r, a0, a1, fill, width):
        self.d.arc(self.P(cx - r, cy - r) + self.P(cx + r, cy + r), a0, a1, fill=fill, width=width)
    def label(self, x, y, text, font=None, fill=(24, 24, 34)):
        font = font or F; lines = text.split("\n"); yy = y * S + 70 - 9 * len(lines)
        for i, ln in enumerate(lines):
            f = font if i == 0 else FS
            w = self.d.textlength(ln, font=f); self.d.text((x * S - w / 2, yy), ln, fill=fill, font=f); yy += 18 if i == 0 else 15
    def door(self, x, y, locked=False):
        c = (220, 80, 70) if locked else (250, 220, 90)
        self.d.rectangle(self.P(x - .9, y - .9) + self.P(x + .9, y + .9), fill=c, outline=WALL, width=2)
    def dot(self, x, y, c, r=.7):
        self.d.ellipse(self.P(x - r, y - r) + self.P(x + r, y + r), fill=c, outline=WALL, width=1)
    def legend(self, x, y, rows):
        for i, (c, t) in enumerate(rows):
            self.d.rectangle(self.P(x, y + i * 2.2) + self.P(x + 1.4, y + i * 2.2 + 1.4), fill=c, outline=WALL)
            self.d.text(self.P(x + 2.2, y + i * 2.2 - .1), t, fill=(230, 230, 236), font=FS)


def frange(a, b, step=3):
    n = max(2, int(abs(b - a) / step) + 1)
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def pol(cx, cy, r, a): return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))


# ------------------------------------------------------------------ option A: core and ring
m = Mock(96, 66, "Survey Level, option A: S.A.R.A.'s core and a ring",
         "Same idea as the promenade: a round core in the middle, a ring corridor, rooms in wedges round it, the Sanctum in a pod. About 64 x 64 tiles (now 40 x 22).")
cx, cy = 34, 33
m.circ(cx, cy, 31, ROCK, None)
m.circ(cx, cy, 27, WALL, WALL)
m.sector(cx, cy, 13, 26, 212, 328, OBS)                 # observation lounge (north), window on its outer edge
m.arc(cx, cy, 26, 212, 328, GLASS, 10)
m.sector(cx, cy, 13, 24, 150, 208, MUSEUM)              # museum (west)
m.circ(cx - 27.5, cy, 5.5, SANCT)                       # sanctum pod
m.rect(cx - 24.5, cy - 1.5, cx - 21.5, cy + 1.5, SANCT, SANCT, 1)
m.sector(cx, cy, 13, 24, 332, 388, LAB)                 # sealed Terran lab (east)
m.sector(cx, cy, 13, 24, 32, 78, SPARE)                 # spare rooms (south-east)
m.sector(cx, cy, 13, 24, 102, 146, HOME)                # Tar'Besh's quarters (south-west)
m.circ(cx, cy, 11, PATH)                                # ring corridor
m.circ(cx, cy, 7, CORE)                                 # S.A.R.A.'s core
m.rect(cx - 2.5, cy + 10, cx + 2.5, cy + 30, PATH, PATH, 1)  # hall to the lift
m.rect(cx - 4, cy + 26, cx + 4, cy + 31, LIFT)
for a in (270, 180, 0, 55, 124):                        # doors from the ring into each wing
    m.door(*pol(cx, cy, 12, a))
m.door(*pol(cx, cy, 12, 0), locked=True)
m.door(cx - 24, cy, locked=True)
m.door(cx, cy + 7)
m.label(cx, cy - 1.5, "S.A.R.A.'s core\nher hologram, consoles")
m.label(*pol(cx, cy, 19.5, 270), "Observation Lounge\ntelescope, sofas, big window")
m.label(cx - 18.5, cy - 4.5, "Museum\nexhibit cases")
m.label(cx - 27.5, cy + .3, "Sanctum\n3 crystals")
m.label(cx + 18.8, cy - 1, "Sealed lab\nTerran signals,\nsensors")
m.label(*pol(cx, cy, 18.5, 55), "Spare rooms\nfuture residents")
m.label(*pol(cx, cy, 18.5, 124), "Tar'Besh's\nquarters")
m.label(cx, cy + 28.5, "Lift down")
m.dot(cx, cy, (200, 255, 255), 1.2)
m.dot(*pol(cx, cy, 23, 270), (60, 60, 70))
for a in (-6, 0, 6): m.dot(cx - 27.5 + a * .45, cy - 2.3, (190, 140, 255), .8)
m.legend(68, 8, [(CORE, "S.A.R.A.'s core (Survey Suite)"), (PATH, "Ring corridor and lift hall"), (OBS, "Observation Lounge, window to space"),
                 (MUSEUM, "Tar'Besh's museum"), (SANCT, "Precursor Sanctum (locked)"), (LAB, "Sealed Terran signals lab (locked)"),
                 (HOME, "Tar'Besh's quarters"), (SPARE, "Spare rooms for later"), (LIFT, "Lift to the Main Level"),
                 ((250, 220, 90), "Door"), ((220, 80, 70), "Locked door")])
m.d.text(m.P(68, 34), "Walk: lift > hall > ring > any wing.\nThe core faces the lift, so S.A.R.A. is\nthe first thing you see.\nThe museum leads on to the Sanctum,\nwhere the crystal scene happens.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/survey_option_A.png")

# ------------------------------------------------------------------ option B: gallery along the window
m = Mock(96, 60, "Survey Level, option B: a curved gallery along one big window",
         "One long curved gallery looks out at the gas giant; the rooms open off its inner side. About 76 x 52 tiles.")
cx, cy = 38, 50
m.sector(cx, cy, 0, 36, 180, 360, ROCK, None)
m.sector(cx, cy, 0, 32, 180, 360, WALL)
m.sector(cx, cy, 23, 31, 195, 345, OBS)                 # gallery
m.arc(cx, cy, 31, 195, 345, GLASS, 10)
m.circ(cx, cy - 15, 8, CORE)                            # S.A.R.A.'s core, opens on to the gallery
m.sector(cx, cy, 9, 22, 190, 238, MUSEUM)
m.circ(*pol(cx, cy, 30, 186), 5, SANCT)
m.sector(cx, cy, 9, 22, 302, 350, LAB)
m.circ(*pol(cx, cy, 30, 354), 4.5, STORE)
m.rect(cx - 2.5, cy - 7, cx + 2.5, cy + 2, PATH, PATH, 1)
m.rect(cx - 4, cy + 1, cx + 4, cy + 6, LIFT)
m.rect(cx - 15, cy - 7, cx - 5, cy + 0, HOME)
m.rect(cx + 5, cy - 7, cx + 15, cy + 0, SPARE)
m.door(cx, cy - 7); m.door(cx, cy - 23); m.door(*pol(cx, cy, 22.5, 214)); m.door(*pol(cx, cy, 22.5, 326), True)
m.door(*pol(cx, cy, 26, 186), True); m.door(cx - 5, cy - 3.5); m.door(cx + 5, cy - 3.5)
m.label(*pol(cx, cy, 27, 270), "Observation gallery\nwindow all along, telescope, sofas")
m.label(cx, cy - 15, "S.A.R.A.'s core")
m.label(*pol(cx, cy, 16, 214), "Museum")
m.label(*pol(cx, cy, 30, 186), "Sanctum")
m.label(*pol(cx, cy, 16, 326), "Sealed lab")
m.label(*pol(cx, cy, 30, 354), "Storage")
m.label(cx - 10, cy - 3.5, "Tar'Besh"); m.label(cx + 10, cy - 3.5, "Spare")
m.label(cx, cy + 3.5, "Lift down")
m.legend(78, 8, [(CORE, "S.A.R.A.'s core"), (OBS, "Observation gallery"), (MUSEUM, "Museum"), (SANCT, "Sanctum (locked)"),
                 (LAB, "Sealed lab (locked)"), (STORE, "Storage"), (HOME, "Tar'Besh's quarters"), (SPARE, "Spare room"), (LIFT, "Lift")])
m.d.text(m.P(66, 30), "Walk: lift > short hall > S.A.R.A.'s core\n> out on to the gallery, then along it\nto the museum or the lab.\nMore window, fewer rooms.", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/survey_option_B.png")

# ------------------------------------------------------------------ option C: the mix
m = Mock(100, 64, "Survey Level, option C: long observation lounge, big museum, S.A.R.A.'s core in the middle",
         "Half-dome like B with a longer lounge; the museum takes the whole west side with the Sanctum joined to its far end. About 84 x 58 tiles.")
cx, cy = 44, 56
m.sector(cx, cy, 0, 38, 180, 360, ROCK, None)
m.sector(cx, cy, 0, 35, 180, 360, WALL)
m.sector(cx, cy, 26, 34, 188, 352, OBS)                 # observation lounge, the whole way round
m.arc(cx, cy, 34, 188, 352, GLASS, 10)
m.sector(cx, cy, 11, 25, 190, 256, MUSEUM)              # museum, big
m.circ(*pol(cx, cy, 30, 181.5), 6, SANCT)               # sanctum, joined to the museum's far end
sx_, sy_ = pol(cx, cy, 23, 186)
m.rect(sx_ - 3.5, sy_ - 2.2, sx_ + .5, sy_ + 2.2, SANCT, SANCT, 1)
m.sector(cx, cy, 11, 25, 290, 350, LAB)                 # sealed lab
m.circ(cx, cy - 18, 10.5, CORE)                         # S.A.R.A.'s core
m.rect(cx - 2.5, cy - 8, cx + 2.5, cy + 1, PATH, PATH, 1)
m.rect(cx - 4, cy, cx + 4, cy + 5, LIFT)
m.rect(cx - 15, cy - 9, cx - 5, cy + 0, HOME)            # Tar'Besh's quarters, beside his museum
m.rect(cx + 5, cy - 9, cx + 15, cy + 0, SPARE)           # spare room
m.door(cx, cy - 8); m.door(cx, cy - 28.5); m.door(*pol(cx, cy, 25.5, 236)); m.door(*pol(cx, cy, 25.5, 312), True)
m.door(sx_ - 2.5, sy_, True); m.door(cx - 5, cy - 4.5); m.door(cx + 5, cy - 4.5); m.door(*pol(cx, cy, 13, 205))
m.label(*pol(cx, cy, 30, 270), "Observation Lounge\nwindow the whole way along: telescope, sofas, star charts")
m.label(cx, cy - 18, "S.A.R.A.'s core\nthe brain of the station\n(close-up in the next picture)")
m.label(*pol(cx, cy, 18, 223), "Tar'Besh's museum\nrows of exhibit cases,\nfossils, relics, wreck parts")
m.label(*pol(cx, cy, 30, 181.5), "Sanctum\n3 crystals")
m.label(*pol(cx, cy, 18, 320), "Sealed lab\nTerran signals\nDirectorate")
m.label(cx - 10, cy - 4.5, "Tar'Besh's\nquarters"); m.label(cx + 10, cy - 4.5, "Spare room")
m.label(cx, cy + 2.5, "Lift down")
m.legend(84, 8, [(CORE, "S.A.R.A.'s core"), (OBS, "Observation Lounge"), (MUSEUM, "Museum"), (SANCT, "Sanctum (locked)"),
                 (LAB, "Sealed lab (locked)"), (HOME, "Tar'Besh's quarters"), (SPARE, "Spare room"), (LIFT, "Lift"),
                 ((250, 220, 90), "Door"), ((220, 80, 70), "Locked door")])
m.d.text(m.P(76, 34), "Walk: lift > hall > S.A.R.A.'s core\n> out on to the lounge > along it to\nthe museum (west) or the lab (east).\nThe museum also has a side door\nto the lift hall, and the Sanctum\nopens only from inside the museum.\nTar'Besh sleeps next to his museum\n(he lives up here now).", fill=(230, 230, 236), font=FS)
m.im.save(MOCK + "/survey_option_C.png")

# ------------------------------------------------------------------ close-up: S.A.R.A.'s core
Z = 34
im = Image.new("RGB", (44 * Z, 26 * Z + 70), BG); d = ImageDraw.Draw(im)
d.text((14, 8), "S.A.R.A.'s core, close-up (21 tiles across)", fill=(255, 226, 150), font=FT)
d.text((14, 40), "The brain of the station: everything in here is hers. Each square is one floor tile.", fill=(220, 220, 230), font=FS)
Q = lambda x, y: (x * Z, y * Z + 70)
c0 = (11.5, 12.5)
def cc(r, fill, outline=WALL, w=3): d.ellipse(Q(c0[0] - r, c0[1] - r) + Q(c0[0] + r, c0[1] + r), fill=fill, outline=outline, width=w)
def box(x0, y0, x1, y1, fill, text="", outline=WALL):
    d.rectangle(Q(x0, y0) + Q(x1, y1), fill=fill, outline=outline, width=2)
    if text:
        lines = text.split("\n"); yy = (y0 + y1) / 2 * Z + 70 - 8 * len(lines)
        for ln in lines:
            w = d.textlength(ln, font=FS); d.text(((x0 + x1) / 2 * Z - w / 2, yy), ln, fill=(20, 20, 30), font=FS); yy += 15
cc(11, WALL); cc(10.5, (200, 214, 214))
for i in range(22):                                      # tile grid
    d.line(Q(c0[0] - 10.5 + i, c0[1] - 10.5) + Q(c0[0] - 10.5 + i, c0[1] + 10.5), fill=(186, 200, 200))
    d.line(Q(c0[0] - 10.5, c0[1] - 10.5 + i) + Q(c0[0] + 10.5, c0[1] - 10.5 + i), fill=(186, 200, 200))
CORES = (160, 200, 340, 20, 60, 120)
for a in CORES + (270,):                                   # glowing data lines in the floor, from the dais to each core and the screen
    x1, y1 = pol(c0[0], c0[1], 8.6, a)
    d.line(Q(*c0) + Q(x1, y1), fill=(70, 220, 230), width=5)
cc(3.2, (120, 210, 220), (60, 110, 130), 4); cc(1.6, (220, 255, 255), (60, 110, 130), 2)
for a in CORES:                                          # six memory cores round the wall
    x, y = pol(c0[0], c0[1], 8.8, a); box(x - .9, y - .9, x + .9, y + .9, (90, 110, 150))
for k, a in enumerate((22.5 + 45 * 6, 22.5 + 45 * 7, 22.5, 22.5 + 45 * 2, 22.5 + 45 * 3, 22.5 + 45 * 4)):
    pass
box(7.5, 1.6, 15.5, 2.8, (40, 70, 100), "")              # big wall screen (north)
d.text(Q(8.1, 1.75), "STATION MAP WALL SCREEN", fill=(160, 230, 240), font=FS)
for x0 in (6.0, 10.5, 15.0):                             # three consoles facing the dais (south)
    box(x0, 16.2, x0 + 2.0, 17.2, (70, 80, 96))
box(2.5, 10.5, 4.4, 14.5, (140, 120, 90), "signal\ntape\narchive")
box(18.6, 10.5, 20.5, 14.5, (100, 120, 140), "sensor\nread-\nouts")
box(3.5, 5.0, 6.0, 6.6, (220, 196, 150), "concierge\ndesk")
d.ellipse(Q(4.4, 4.3) + Q(5.1, 5.0), fill=(240, 200, 80), outline=WALL)
box(17.0, 5.0, 19.5, 6.6, (190, 150, 120), "Paris\npictures")
d.ellipse(Q(6.3, 4.9) + Q(7.0, 5.6), fill=(230, 120, 160), outline=WALL)
box(10.5, 21.2, 12.5, 23.0, (250, 220, 90), "door")
box(10.5, 1.0, 12.5, 1.6, (250, 220, 90))
d.text(Q(10.2, .25), "to the lounge", fill=(230, 230, 236), font=FS)
d.text(Q(10.0, 23.1), "to the lift hall", fill=(230, 230, 236), font=FS)
notes = ["1  Hologram dais (centre): S.A.R.A. stands here, glowing rings.",
         "2  Data lines in the floor pulse from the dais to her memory cores.",
         "3  Six memory cores round the wall: tall racks with lights.",
         "4  Wall screen (north): live station map, the lounge door below.",
         "5  Three operator consoles facing the dais (where you talk to her).",
         "6  Signal tape archive (west): the old listening post's records.",
         "7  Deep-space sensor read-outs (east).",
         "8  Her secret wish: a little concierge desk with a bell and",
         "   flowers, and framed pictures of Paris. She wants a hotel.",
         "Animated: dais rings, data lines, rack lights, screen."]
for i, n in enumerate(notes):
    d.text((23.2 * Z, 70 + (3 + i * .9) * Z), n, fill=(230, 230, 236), font=FS)
im.save(MOCK + "/sara_core_closeup.png")
