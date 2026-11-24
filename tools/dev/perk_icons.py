"""Stand-in icons for the datapad's Perks tab (24 Nov 2026): art/perks.png, one 24x24 cell per perk or keepsake, in
the order of the "icon" numbers in scripts/perk_data.gd.

Each icon is the thing the resident hands over or uses in the heart event that gives it (Zachary: "the icons will
be stuff like freyas wrench"): Job's pick, Evarra's crown, Owen's hide ledger with its tabs, Stu's desk bell.

Drawn to the Art Style Guide v2's item-icon rules (Project doc echo-landing-art-style-guide.md, sections 2, 7, 9):
  - master palette only (the 68 colours, outline ramp as updated on 21 Nov); every pixel is checked at the end;
  - one 1-px warm dark-brown outline, #5b332d, all the way round; parts inside separated by a darker shade;
  - the object fills about 20 of the 24 pixels, centred; drawn straight on: long upright things stand upright,
    tools with a working end are a side view pointing right; no diagonal icons;
  - one main colour, one accent, a 2-px highlight at the top left; light from the top left, 4 shades a material;
  - low detail: big flat areas, chunky shapes, nothing important thinner than 2 px, no single-pixel specks
    (a clean-up pass removes any the shading leaves); no text, no ground shadow.

Shapes are built from ellipses, boxes and polygons, then shaded as rounded forms by tools/dev/prop_art/pix.py.
Run from the repo root:  python3 -I tools/dev/perk_icons.py   (needs numpy, scipy, Pillow)
Safe to run again: it rewrites the whole sheet. Stand-ins until the artist draws them (Art Fix List row 385).
"""
import os
import sys

# icon number -> what it shows (docs/story/PERKS.md lists these)
ICONS = [
    "Jorvik's FTL stabilizer: brass gimbal rings round a glowing core",           # 0  pioneer_stabilizer
    "Freya's wrench, taped grip",                                                   # 1  master_mechanic
    "A bistro chalkboard sign",                                                     # 2  parisian_bistro_menu
    "Jasper's balloon whisk",                                                       # 3  sous_chefs_blessing
    "A brioche with a sprig of lavender",                                           # 4  honey_lavender_brioche
    "Evarra's wildflower crown",                                                    # 5  green_thumb
    "A jar of wildflower honey, cloth lid",                                         # 6  wildflower_honey
    "A starlight souffle in its ramekin",                                           # 7  starlight_souffle
    "A place set at the family table",                                              # 8  family_table
    "Job's pick",                                                                   # 9  bedrock_strength
    "A jar of glowing xeno-salve",                                                  # 10 xeno_salve
    "A heart with a medic's cross",                                                 # 11 guardian_medic
    "A Star-Knight helm, violet crest",                                             # 12 star_knight_aegis
    "Ix'ali's shield, a heart on it",                                               # 13 chivalric_guard
    "The scouts' folded map, marked with an X",                                     # 14 junior_scout_reports
    "Artie's enamel camp mug, steaming",                                            # 15 thrifty
    "Stu's room key, its bow a five-pointed star",                                 # 16 five_star_partner
    "Ana's pilot wings pin",                                                        # 17 wingmate
    "One of S.A.R.A.'s holo pads, her light above it",                              # 18 concierge
    "Tar'Besh's appraiser's loupe",                                                 # 19 relic_appraisal
    "Zaas's sonar lure, a fish with a glowing eye",                                 # 20 deep_sea_sonar_lure
    "S.A.R.A.'s motion-sensor scope, a blip on it",                                 # 21 monster_radar
    "Ix'ali's spike trap",                                                          # 22 chitin_piercer_traps
    "Bram's grandfather's trade beacon, a lantern",                                 # 23 moogli_trade_beacon
    "Tikka's regulator coil, copper wire wound fine",                               # 24 smelter_overclock
    "A void-silk pillowcase, the glowing thread through it",                        # 25 void_silk_linens
    "Maren's med-stim, a red dose in it",                                           # 26 advanced_med_stims
    "Owen's hide-bound ledger with tabs down the side",                             # 27 library_lore_compendium
    "Tobbin's chisel",                                                              # 28 heirloom_chair
    "A seedling under Merrow's grow strip, blue up, red down",                      # 29 hydro_boost
    "Garrick's sparring glove",                                                     # 30 self_defence
    "Saffi's stew pot, steaming",                                                   # 31 well_fed
    "Freya's wrench pendant",                                                       # 32 wrench_pendant
    "Jasper's apron, two names stitched on the pocket",                             # 33 jasper_apron
    "Evarra's pressed flowers, framed",                                             # 34 pressed_flower_frame
    "Job's carved oar charm, its cord wound round the shaft",                       # 35 oar_charm
    "Quill's brass charm, a compass engraved on it",                                # 36 stethoscope_compass
    "Ix'ali's ceremonial pauldron",                                                 # 37 pauldron
    "The Honorary Scoutmaster badge, a heart on it",                                # 38 scoutmaster_badge
    "Stu's little silver desk bell",                                                # 39 silver_bell
    "Ana's flight jacket",                                                          # 40 flight_jacket
    "The family photo: Jasper, Evarra and you",                                     # 41 family_photo
]

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "dev", "prop_art"))
import pix  # noqa: E402

OUT_PNG = os.path.join(ROOT, "art", "perks.png")
CELL = 24


def _ramp(*hexes):
    return [pix.H(h) for h in hexes]


# The master palette (Echo_Landing_Art_Style_v2.1.zip, echo_landing_palette.hex), dark to light, with the
# outline & ink ramp as updated on 21 Nov (style guide section 2).
PAL = {
    "ink": ["4a2a28", "5b332d", "6e4238"],
    "cream": ["6e6178", "9c8a8f", "c9b8a6", "e8d9bd", "fff3d6"],
    "teal": ["263a52", "2f5a6e", "3f7f88", "66a7a0", "9fd1bf"],
    "wood": ["3d2426", "6b3a2c", "9a5b36", "c9844a", "e8b46a"],
    "brass": ["5a3a22", "8f5f24", "c99231", "edc65a", "fff0a0"],
    "copper": ["4c2224", "8a3a2a", "c8602f", "ee8f3e", "ffc070"],
    "leaf": ["1f3a32", "2f6a3a", "4f9a3c", "8cc94a", "d2ea7a"],
    "soil": ["33242a", "5a3a33", "86593f", "b08158", "d8b07c"],
    "rock": ["2f2c3d", "4b4659", "6f6878", "9c94a0", "c9c1c4"],
    "berry": ["4a1c2e", "8a2a3a", "c94a4a", "ee7a62", "ffb39a"],
    "violet": ["2c1f4a", "4f3384", "7d55c0", "b085e6", "e0c6ff"],
    "glow": ["1f2f5a", "2f5cab", "4a9be0", "8fd3ff", "e6fbff"],
    "skin": ["6b3a3a", "a85f4f", "d9926e", "f2c29a", "ffe3c8"],
    "skin2": ["3a2026", "5e3430", "86503c", "a8704f", "c99470"],
}
PALETTE = np.array([pix.H(h) for r in PAL.values() for h in r])
OUTLINE = pix.H("5b332d")


def R(name, lo=1, hi=5):
    """A shading ramp: the palette ramp `name` from index lo up to (not including) hi; 4 tones by default."""
    return _ramp(*PAL[name][lo:hi])


def C(name, i):
    return pix.H(PAL[name][i])


# ---------------------------------------------------------------- shapes (24x24 boolean masks)

def _mask(draw):
    im = Image.new("L", (CELL, CELL), 0)
    draw(ImageDraw.Draw(im))
    return np.array(im) > 0


def el(cx, cy, rx, ry=None):
    ry = rx if ry is None else ry
    yy, xx = np.mgrid[0:CELL, 0:CELL]
    return ((xx - cx) / (rx + 0.5)) ** 2 + ((yy - cy) / (ry + 0.5)) ** 2 <= 1.0


def box(x0, y0, x1, y1, cut=1):
    """Inclusive box; `cut` pixels off each corner (rounded corners)."""
    m = np.zeros((CELL, CELL), bool)
    m[y0:y1 + 1, x0:x1 + 1] = True
    for k in range(cut):
        n = cut - k
        for (x, y, dx) in ((x0, y0 + k, 1), (x1, y0 + k, -1), (x0, y1 - k, 1), (x1, y1 - k, -1)):
            for j in range(n):
                if 0 <= y < CELL and 0 <= x + dx * j < CELL:
                    m[y, x + dx * j] = False
    return m


def poly(pts):
    return _mask(lambda d: d.polygon(pts, fill=255))


def thick(pts, w):
    return _mask(lambda d: d.line(pts, fill=255, width=w, joint="curve"))


def rows(y0, y1):
    m = np.zeros((CELL, CELL), bool)
    m[y0:y1 + 1, :] = True
    return m


def cols(x0, x1):
    m = np.zeros((CELL, CELL), bool)
    m[:, x0:x1 + 1] = True
    return m


def star(cx, cy, ro, ri, points=5, rot=-np.pi / 2):
    pts = []
    for k in range(points * 2):
        r = ro if k % 2 == 0 else ri
        a = rot + k * np.pi / points
        pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return poly(pts)


def heart(cx, cy, s):
    """A heart about 2*s wide: two round lobes with a notch between them, and a point at the bottom."""
    r = s / 2.0
    lobes = el(cx - r, cy, r - 0.3, r - 0.3) | el(cx + r - 1, cy, r - 0.3, r - 0.3)
    return lobes | poly([(cx - s, cy + 0.5), (cx + s - 1, cy + 0.5), (cx - 0.5, cy + s + 1)])


HEARTS = {
    7: [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."],
    9: [".##...##.", "####.####", "#########", "#########", ".#######.", "..#####..", "...###...", "....#...."],
}


def small_heart(x0, y0, w):
    """A hand-pixelled heart, w = 7 or 9 wide, its top left at (x0, y0)."""
    m = np.zeros((CELL, CELL), bool)
    for y, row in enumerate(HEARTS[w]):
        for x, ch in enumerate(row):
            if ch == "#":
                m[y0 + y, x0 + x] = True
    return m


def bottom_edge(mask):
    """The lowest pixel of each column of a mask."""
    out = np.zeros_like(mask)
    for x in range(CELL):
        ys = np.nonzero(mask[:, x])[0]
        if len(ys):
            out[ys.max(), x] = True
    return out


# ---------------------------------------------------------------- canvas

class Icon:
    CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def __init__(self):
        self.g = np.full((CELL, CELL), ".", "<U1")
        self.parts = {}
        self.marks = []          # (mask, colour) painted flat after shading: lines, glints, stitches
        self.n = 0

    def add(self, mask, ramp, **opt):
        """A shaded part painted over what's there (later parts are in front)."""
        ch = self.CHARS[self.n]
        self.n += 1
        self.g[mask] = ch
        p = dict(ramp=ramp, z=self.n)
        p.update(opt)
        self.parts[ch] = p
        return ch

    def cut(self, mask):
        """Make pixels empty again (holes, the jaw of a wrench)."""
        self.g[mask] = "."

    def mark(self, mask, colour):
        self.marks.append((mask, colour))

    def px(self, pts, colour):
        m = np.zeros((CELL, CELL), bool)
        for x, y in pts:
            m[y, x] = True
        self.mark(m, colour)

    def glint(self, x, y, colour=None, horizontal=True):
        """The 2-px highlight at the top left."""
        self.px([(x, y), (x + 1, y)] if horizontal else [(x, y), (x, y + 1)], colour if colour is not None
                else C("cream", 4))

    def render(self):
        img = pix.render(self.g, self.parts, out=(OUTLINE, OUTLINE)).astype(float)
        body = (self.g != ".")
        _despeckle(img, body)
        marked = np.zeros_like(body)
        for m, col in self.marks:
            img[m, :3] = col
            img[m, 3] = 255
            marked |= m
        _despeckle(img, body & ~marked, eight=True)
        return img.astype(np.uint8)


def _specks(img):
    """Pixels (not the outline) unlike all eight neighbours: the single-pixel specks the style guide rules out."""
    out = []
    for y in range(CELL):
        for x in range(CELL):
            if img[y, x, 3] == 0 or (img[y, x, :3] == OUTLINE).all():
                continue
            me = tuple(img[y, x])
            nb = [tuple(img[y + dy, x + dx]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                  if (dx or dy) and 0 <= y + dy < CELL and 0 <= x + dx < CELL]
            if me not in nb:
                out.append((x, y))
    return out


def _despeckle(img, body, eight=False):
    """No single-pixel specks: a body pixel unlike all its neighbours (four, or eight) takes its most common
    neighbour colour."""
    for _ in range(3):
        changed = False
        rgb = [tuple(v) for v in img[:, :, :3].reshape(-1, 3).astype(int)]
        rgb = np.array(rgb).reshape(CELL, CELL, 3)
        for y in range(1, CELL - 1):
            for x in range(1, CELL - 1):
                if not body[y, x]:
                    continue
                me = tuple(rgb[y, x])
                near = ([(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy] if eight
                        else [(1, 0), (-1, 0), (0, 1), (0, -1)])
                if me in [tuple(rgb[y + dy, x + dx]) for dx, dy in near]:
                    continue
                if (rgb[y, x] == OUTLINE).all():
                    continue
                n8 = [tuple(rgb[y + dy, x + dx]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                      if (dx or dy) and body[y + dy, x + dx]]
                if not n8:
                    continue
                best = max(set(n8), key=n8.count)
                img[y, x, :3] = best
                changed = True
        if not changed:
            break


# ---------------------------------------------------------------- the icons

def i_stabilizer():
    c = Icon()
    c.add(box(9, 19, 15, 21), R("rock"))                                         # stand
    c.add(box(11, 17, 13, 19, 0), R("rock"))
    c.add(el(12, 10, 8, 8) & ~el(12, 10, 5, 5), R("brass"), spec=C("brass", 4), spec_n=2)
    c.add(box(4, 9, 20, 11, 0) & ~el(12, 10, 3, 3), R("copper"))                 # the gimbal band
    c.add(el(12, 10, 3, 3), R("glow"), spec=C("glow", 4), spec_n=2)              # the core
    return c


def i_wrench():
    c = Icon()
    c.add(box(2, 10, 13, 14, 1), R("rock"))                                       # handle
    c.add(box(3, 10, 8, 14, 0) & box(2, 10, 13, 14, 1), R("copper"))              # orange tape
    head = el(17, 12, 5, 6)
    c.add(head, R("rock"), spec=C("rock", 4), spec_n=2)
    c.cut(box(19, 10, 23, 14, 0))                                                 # the jaw, open to the right
    return c


def i_chalkboard():
    c = Icon()
    c.add(thick([(6, 21), (8, 6)], 2), R("wood"))                                  # A-frame legs
    c.add(thick([(18, 21), (16, 6)], 2), R("wood"))
    c.add(box(4, 3, 20, 16, 1), R("wood"), spec=C("wood", 4), spec_n=2)
    c.add(box(6, 5, 18, 14, 0), R("teal", 0, 3), flat=0.6)                        # the slate
    c.mark(box(8, 7, 14, 7, 0), C("cream", 3))                                     # chalk: today's dishes
    c.mark(box(8, 9, 16, 9, 0), C("cream", 3))
    c.mark(box(8, 11, 12, 11, 0), C("cream", 3))
    return c


def i_whisk():
    c = Icon()
    c.add(box(10, 14, 13, 21, 1), R("wood"))                                      # handle
    c.add(box(10, 12, 13, 14, 0), R("brass"))                                     # ferrule
    wires = (el(11.5, 7, 4.5, 6) & ~el(11.5, 7.5, 2.5, 4)) | box(11, 2, 12, 12, 0)
    c.add(wires, R("cream"), spec=C("cream", 4), spec_n=2)
    return c


def i_brioche():
    c = Icon()
    c.add(el(11, 14, 8, 4.5) & rows(0, 15), R("wood", 2, 5) + [C("brass", 4)], spec=C("cream", 4), spec_n=2)
    c.add(el(11, 8.5, 3.5, 3), R("wood", 2, 5) + [C("brass", 4)], spec=C("cream", 4), spec_n=2)   # its top knot
    c.add(poly([(3.5, 15), (18.5, 15), (16.5, 21), (5.5, 21)]), R("cream"))       # paper case
    for x in (7, 10, 13, 16):
        c.mark(box(x, 16, x, 20, 0) & poly([(3.5, 15), (18.5, 15), (16.5, 21), (5.5, 21)]), C("cream", 1))
    c.add(thick([(15, 9), (20, 3)], 2), R("leaf"))                                 # lavender sprig
    c.add(el(19.5, 3.5, 2, 2), R("violet"))
    c.add(el(17, 6, 2, 2), R("violet"))
    return c


def i_crown():
    c = Icon()
    c.add(el(12, 12, 9, 7) & ~el(12, 12, 5, 3.5), R("leaf"))
    for (x, y), col in zip([(4.5, 12), (12, 5.5), (19.5, 12), (8.5, 18), (15.5, 18), (6.5, 7), (17.5, 7)],
                           ["berry", "brass", "violet", "cream", "berry", "violet", "brass"]):
        c.add(el(x, y, 2.2, 2.2), R(col))
    return c


def i_honey():
    c = Icon()
    c.add(box(5, 8, 19, 21, 2), R("brass"), spec=C("brass", 4), spec_n=2)          # the honey in its jar
    c.add(box(4, 3, 20, 8, 1), R("berry"))                                         # cloth lid
    c.add(box(4, 7, 20, 8, 0), R("wood"))                                          # twine
    c.add(box(8, 12, 16, 17, 1), R("cream"), flat=0.5)                              # label
    return c


def i_souffle():
    c = Icon()
    c.add(box(6, 8, 18, 14, 0) | el(12, 8, 6, 4.5), R("wood", 2, 5) + [C("brass", 4)], spec=C("cream", 4),
          spec_n=2)                                                                  # risen above the dish
    c.add(box(4, 14, 20, 21, 1), R("cream"))                                       # fluted ramekin
    for x in (7, 10, 13, 16):
        c.mark(box(x, 15, x, 20, 0), C("cream", 2))
    c.mark(box(20, 2, 20, 4, 0) | box(19, 3, 21, 3, 0), C("brass", 4))             # a star of light
    return c


def i_place():
    c = Icon()
    c.add(el(12, 12, 6, 6), R("cream"), spec=C("cream", 4), spec_n=2)              # plate
    c.add(el(12, 12, 3.5, 3.5), R("cream", 1, 4))                                  # its well
    c.add(el(12, 12, 2, 1.5), R("leaf"))                                           # something green
    c.add(box(2, 10, 3, 20, 0), R("rock"))                                         # fork handle
    c.add(box(2, 3, 4, 10, 1), R("rock"))                                          # fork head
    c.cut(box(3, 3, 3, 6, 0))
    c.add(box(20, 11, 21, 20, 0), R("rock"))                                       # knife
    c.add(box(19, 3, 21, 11, 1), R("rock"), spec=C("rock", 4), spec_n=2)
    return c


def i_pick():
    c = Icon()
    c.add(box(11, 6, 13, 21, 1), R("wood"))
    c.add(box(11, 16, 13, 20, 0), R("soil"))                                       # leather wrap
    c.add(thick([(3, 10), (6, 6), (12, 4), (18, 6), (21, 10)], 3), R("rock"), spec=C("rock", 4), spec_n=2)
    c.add(box(10, 3, 14, 7, 1), R("brass"))                                        # collar
    return c


def i_salve():
    c = Icon()
    c.add(box(4, 9, 20, 20, 2), R("teal", 1, 5), spec=C("glow", 4), spec_n=2)     # the salve, through the glass
    c.add(box(3, 5, 21, 9, 1), R("rock"), spec=C("rock", 4), spec_n=2)              # screw lid
    c.add(box(7, 12, 17, 17, 1), R("cream"), flat=0.5)                              # label
    c.add(el(12, 14.5, 2.5, 1.2), R("leaf"))                                        # the lichen leaf on it
    return c


def i_medic_heart():
    c = Icon()
    c.add(heart(12.5, 7.5, 9), R("berry"), spec=C("berry", 4), spec_n=2)
    c.add(box(11, 6, 13, 14, 0) | box(8, 9, 16, 11, 0), R("cream", 2, 5))
    return c


def i_helm():
    c = Icon()
    c.add(box(4, 5, 20, 21, 2), R("cream"), flat=0.3, spec=C("cream", 4), spec_n=2)   # a flat-topped great helm
    c.add(box(4, 5, 20, 9, 2), R("cream", 1, 5), flat=0.3)                           # its brow plate
    c.add(box(10, 1, 14, 5, 1), R("violet"), spec=C("violet", 4), spec_n=2)          # crest
    c.mark(box(6, 12, 18, 13, 0) & ~box(11, 12, 12, 13, 0), C("ink", 0))            # the visor slit
    c.mark(box(11, 15, 12, 20, 0), C("cream", 2))                                     # centre ridge
    return c


def i_shield():
    c = Icon()
    c.add(poly([(3, 3), (21, 3), (21, 11), (16.5, 17.5), (12, 21.5), (7.5, 17.5), (3, 11)]), R("brass"))
    c.add(poly([(5, 5), (19, 5), (19, 11), (15.5, 15.5), (12, 18.5), (8.5, 15.5), (5, 11)]), R("rock"),
          spec=C("rock", 4), spec_n=2)
    c.add(small_heart(8, 7, 9), R("berry", 2, 5), flat=0.5)
    return c


def i_map():
    c = Icon()
    c.add(poly([(3, 5), (9, 3), (9, 19), (3, 21)]), R("soil", 2, 5) + [C("cream", 4)])
    c.add(poly([(9, 3), (15, 5), (15, 21), (9, 19)]), R("soil", 1, 5))
    c.add(poly([(15, 5), (21, 3), (21, 19), (15, 21)]), R("soil", 2, 5) + [C("cream", 4)])
    c.add(el(6, 9, 2, 3), R("leaf"))                                                # the woods
    c.add(el(11.5, 15, 2, 1.5), R("teal"))                                          # the lake
    c.px([(16, 8), (19, 8), (17, 9), (18, 9), (17, 10), (18, 10), (16, 11), (19, 11)], C("berry", 2))   # X
    return c


def i_mug():
    c = Icon()
    c.add(el(17, 13, 3.5, 4) & ~el(17, 13, 1.5, 2), R("teal"))                     # handle
    c.add(box(3, 8, 16, 20, 1), R("teal"), spec=C("teal", 4), spec_n=2)
    c.add(box(3, 8, 16, 9, 0), R("cream"))                                          # enamel rim
    c.mark(box(7, 3, 8, 4, 0) | box(8, 5, 9, 6, 0), C("cream", 4))                  # steam
    c.mark(box(11, 2, 12, 3, 0) | box(12, 4, 13, 5, 0), C("cream", 3))
    return c


def i_key():
    c = Icon()
    c.add(star(6.5, 11.5, 6, 3, 5) & ~box(6, 11, 7, 12, 0), R("brass"), spec=C("brass", 4), spec_n=2)
    c.add(box(11, 10, 21, 12, 0), R("brass"))                                      # shaft
    c.add(box(15, 13, 16, 16, 0) | box(18, 13, 19, 15, 0), R("brass", 1, 4))      # the bit
    return c


def i_wings():
    c = Icon()
    for side in (-1, 1):
        for k, (y, x_out) in enumerate([(6, 10), (9, 9), (12, 7)]):
            x0, x1 = (12 - x_out, 9) if side < 0 else (15, 12 + x_out)
            c.add(box(x0, y, x1, y + 2, 1), R("brass"))
    c.add(el(12, 10, 4, 4.5), R("brass"), spec=C("brass", 4), spec_n=2)
    c.add(el(12, 10, 2, 2.5), R("teal", 2, 5) + [C("glow", 4)])
    return c


def i_holopad():
    c = Icon()
    c.add(box(3, 16, 21, 19, 0) | el(12, 19, 9, 2), R("rock"))                    # the pad
    c.add(el(12, 16, 9, 2.5), R("rock", 2, 5))
    c.add(el(12, 16, 5.5, 1.2), R("glow", 2, 5))
    c.add(box(11, 9, 12, 14, 0), R("glow", 3, 5))                                   # light
    c.add(el(12, 7, 4.5, 4.5), R("glow", 1, 5), spec=C("glow", 4), spec_n=2)
    return c


def i_loupe():
    c = Icon()
    c.add(box(11, 15, 13, 21, 1), R("wood"))
    c.add(box(10, 14, 14, 15, 0), R("brass"))
    c.add(el(12, 8, 7, 7) & ~el(12, 8, 4.5, 4.5), R("brass"))
    c.add(el(12, 8, 4.5, 4.5), R("glow", 2, 5) + [C("glow", 4)], flat=0.3)
    c.glint(9, 5)
    c.glint(9, 6, horizontal=False)
    return c


def i_lure():
    c = Icon()
    c.add(thick([(12, 16), (12, 20), (14, 21), (16, 20), (16, 18)], 2), R("brass"))   # hook
    c.add(poly([(6, 12), (2, 7), (2, 17)]), R("teal"))                            # tail
    c.add(poly([(9, 8), (13, 4), (14, 8)]), R("teal", 0, 4))                       # fin
    c.add(el(12.5, 12, 7.5, 4.5), R("teal"), spec=C("teal", 4), spec_n=2)
    c.add(box(9, 8, 10, 16, 0) & el(12.5, 12, 7.5, 4.5), R("brass"))               # band
    c.add(box(16, 10, 17, 11, 0), [C("glow", 3), C("glow", 4)], flat=1.0)           # the eye that sings
    return c


def i_scope():
    c = Icon()
    c.add(box(3, 3, 21, 21, 3), R("rock"))
    c.add(el(12, 12, 7, 7), R("teal", 0, 3), flat=0.4)
    c.add(poly([(12, 12), (12, 5), (16, 6), (18, 9)]), R("teal", 3, 5))            # the sweep
    c.mark(box(7, 14, 8, 15, 0), C("berry", 3))                                     # something below
    for x, y in ((4, 4), (19, 4), (4, 19), (19, 19)):
        c.mark(box(x, y, x + 1, y + 1, 0), C("rock", 4))                            # bolts
    return c


def i_spikes():
    c = Icon()
    c.add(poly([(3.5, 16), (6.5, 5), (9.5, 16)]), R("cream"))
    c.add(poly([(14.5, 16), (17.5, 5), (20.5, 16)]), R("cream"))
    c.add(poly([(8.5, 17), (12, 2), (15.5, 17)]), R("cream"), spec=C("cream", 4), spec_n=2)
    c.add(box(3, 16, 21, 21, 1), R("wood"))
    for x in (5, 18):
        c.mark(box(x, 18, x + 1, 19, 0), C("brass", 3))
    return c


def i_lantern():
    c = Icon()
    c.add(el(12, 3, 3, 2) & ~el(12, 3, 1.3, 0.6), R("brass"))                    # ring
    c.add(box(6, 17, 18, 20, 1), R("brass"))                                       # base
    c.add(box(7, 8, 17, 17, 0), R("leaf", 2, 5) + [C("cream", 4)], flat=0.3)      # the light
    c.add(box(7, 8, 8, 17, 0) | box(16, 8, 17, 17, 0), R("brass"))               # frame
    c.add(poly([(5, 9), (9, 5), (15, 5), (19, 9)]), R("brass"), spec=C("brass", 4), spec_n=2)
    return c


def i_coil():
    c = Icon()
    c.add(box(7, 6, 17, 18, 0), R("copper"), spec=C("copper", 4), spec_n=2)
    for y in (9, 12, 15):
        c.mark(box(7, y, 17, y, 0), C("copper", 1))                                # the windings
    c.add(box(3, 3, 7, 21, 2), R("rock"))
    c.add(box(17, 3, 21, 21, 2), R("rock"))
    return c


def i_pillow():
    c = Icon()
    c.add(poly([(2, 5), (12, 7), (22, 5), (19.5, 12), (22, 19), (12, 17), (2, 19), (4.5, 12)]), R("violet"),
          bulge=1.6, spec=C("violet", 4), spec_n=2)
    c.mark(box(5, 11, 19, 12, 0) & ~box(8, 11, 8, 12, 0) & ~box(12, 11, 12, 12, 0) & ~box(16, 11, 16, 12, 0),
           C("glow", 3))                                                            # the glowing thread
    return c


def i_stim():
    c = Icon()
    c.add(box(2, 7, 3, 17, 0), R("rock"))                                            # thumb flange
    c.add(box(3, 11, 6, 13, 0), R("rock"))                                           # plunger
    c.add(box(6, 7, 17, 17, 1), R("cream"), spec=C("cream", 4), spec_n=2)            # the barrel
    c.add(box(9, 9, 16, 15, 1), R("berry", 1, 5))                                    # the dose
    c.add(box(17, 10, 19, 14, 1), R("rock"))                                         # tip
    c.add(box(20, 11, 21, 13, 0), R("rock", 2, 5))
    for x in (11, 14):
        c.mark(box(x, 7, x, 8, 0), C("cream", 1))                                    # markings
    return c


def i_ledger():
    c = Icon()
    c.add(box(18, 5, 21, 7, 1), R("teal"))                                          # tabs
    c.add(box(18, 10, 21, 12, 1), R("berry"))
    c.add(box(18, 15, 21, 17, 1), R("brass"))
    c.add(box(4, 3, 18, 21, 1), R("soil"), spec=C("soil", 4), spec_n=2)            # hide cover
    c.add(box(4, 3, 6, 21, 1), R("soil", 0, 4))                                     # spine
    c.add(poly([(12, 8), (15.5, 11.5), (12, 15), (8.5, 11.5)]), R("brass"))
    return c


def i_chisel():
    c = Icon()
    c.add(box(2, 9, 10, 15, 2), R("wood"), spec=C("wood", 4), spec_n=2)
    c.add(box(10, 9, 12, 15, 0), R("brass"))
    c.add(box(13, 10, 18, 14, 0), R("rock"))
    c.add(poly([(18, 10), (21.5, 11), (21.5, 13), (18, 14)]), R("rock", 2, 5) + [C("cream", 4)])
    return c


def i_growlight():
    c = Icon()
    c.add(box(3, 2, 21, 5, 1), R("rock"), spec=C("rock", 4), spec_n=2)            # the strip
    c.add(box(4, 6, 20, 6, 0), [C("glow", 3)] * 2, flat=1.0)                       # blue up
    c.add(box(4, 7, 20, 7, 0), [C("berry", 3)] * 2, flat=1.0)                      # red down
    c.add(el(12, 20, 7, 2), R("soil"))
    c.add(box(11, 13, 12, 19, 0), R("leaf"))
    c.add(el(8.5, 13, 3, 2), R("leaf"))
    c.add(el(15.5, 12, 3, 2), R("leaf"), spec=C("leaf", 4), spec_n=2)
    return c


def i_glove():
    c = Icon()
    c.add(box(7, 15, 17, 21, 1), R("cream"))                                       # cuff
    c.add(box(7, 15, 17, 16, 0), R("brass"))
    c.add(el(12.5, 9, 7, 7), R("berry"), spec=C("berry", 4), spec_n=2)
    c.add(el(5.5, 11, 2.5, 3.5), R("berry"))                                       # thumb
    return c


def i_stewpot():
    c = Icon()
    c.add(box(2, 11, 4, 13, 1) | box(20, 11, 22, 13, 1), R("rock"))               # handles
    c.add(box(5, 10, 19, 18, 0) | el(12, 18, 7, 2.5), R("copper"), spec=C("copper", 4), spec_n=2)
    c.add(box(4, 8, 20, 10, 1), R("copper", 2, 5))                                  # rim
    c.add(el(12, 8.5, 6.5, 1), R("soil", 2, 5))                                     # the stew
    c.mark(box(9, 2, 10, 3, 0) | box(8, 4, 9, 5, 0), C("cream", 4))                 # steam
    c.mark(box(14, 3, 15, 4, 0) | box(15, 5, 16, 6, 0), C("cream", 3))
    return c


def i_wrench_pendant():
    c = Icon()
    c.add(el(12, 3, 2.5, 2) & ~box(12, 3, 12, 3, 0), R("brass"))                  # bail
    c.add(box(10, 5, 14, 15, 1), R("cream"), spec=C("cream", 4), spec_n=2)
    c.add(el(12, 17.5, 5, 4), R("cream"))
    c.cut(box(11, 19, 13, 23, 0))                                                    # the jaw
    return c


def i_apron():
    c = Icon()
    c.add(thick([(8, 6), (9, 3), (15, 3), (16, 6)], 2), R("cream", 0, 4))          # neck strap
    c.add(box(2, 11, 22, 12, 0), R("berry"))                                         # ties
    c.add(box(8, 5, 16, 11, 1) | poly([(6, 12), (18, 12), (19.5, 21), (4.5, 21)]), R("cream"),
          spec=C("cream", 4), spec_n=2)
    c.add(box(9, 14, 15, 19, 1), R("cream", 1, 5))                                  # the pocket
    c.mark(box(10, 15, 13, 15, 0), C("berry", 2))                                   # two names
    c.mark(box(11, 17, 14, 17, 0), C("teal", 2))
    return c


def i_flower_frame():
    c = Icon()
    c.add(box(3, 3, 21, 21, 1), R("wood"), spec=C("wood", 4), spec_n=2)
    c.add(box(6, 6, 18, 18, 0), R("cream", 2, 5), flat=0.6)
    c.mark(box(9, 12, 9, 16, 0) | box(15, 11, 15, 16, 0) | box(10, 16, 14, 16, 0), C("leaf", 2))   # stems
    c.add(el(9, 10, 2, 2), R("berry"))
    c.add(el(15, 9, 2, 2), R("violet"))
    c.add(el(12, 13, 2, 2), R("brass"))
    c.glint(7, 7)
    return c


def _along(x0, y0, x1, y1, half_len, half_w):
    """An ellipse lying along the line from (x0, y0) to (x1, y1), centred on its middle."""
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    a = np.arctan2(y1 - y0, x1 - x0)
    pts = [(cx + half_len * np.cos(t) * np.cos(a) - half_w * np.sin(t) * np.sin(a),
            cy + half_len * np.cos(t) * np.sin(a) + half_w * np.sin(t) * np.cos(a)) for t in np.linspace(0, 2 * np.pi, 40)]
    return poly(pts)


def i_oar():
    # long and thin, so it lies on the diagonal like a fishing rod (style guide section 9)
    c = Icon()
    c.add(thick([(4, 20), (14, 10)], 3), R("wood"))                                 # shaft
    c.add(el(3.5, 20.5, 1.6, 1.6), R("wood"))                                       # grip
    c.add(_along(12, 12, 21, 3, 7, 3.6), R("wood"), spec=C("wood", 4), spec_n=2)    # the blade
    c.add(thick([(6, 16), (8, 18)], 2), R("teal"))                                  # its cord, wound round
    return c


def i_charm():
    c = Icon()
    c.add(el(12, 3, 2.5, 2) & ~box(12, 3, 12, 3, 0), R("brass"))
    c.add(el(12, 13, 8, 8), R("brass"), spec=C("brass", 4), spec_n=2)
    c.add(el(12, 13, 5.5, 5.5), R("brass", 1, 4), flat=0.5)
    c.add(star(12, 13, 5, 1.6, 4, rot=-np.pi / 2), R("teal", 1, 5))                 # the compass
    return c


def i_pauldron():
    # a domed cap with two lames below it, each wider, flaring out like a shoulder guard
    c = Icon()
    lame2 = poly([(4.5, 13), (19.5, 13), (22.5, 20.5), (1.5, 20.5)]) & el(12, 3, 14, 18)
    lame1 = poly([(6.5, 9), (17.5, 9), (20.5, 16), (3.5, 16)]) & el(12, 1, 12, 15)
    for lame in (lame2, lame1):
        c.add(lame, R("cream"))
        c.mark(bottom_edge(lame), C("violet", 2))
    cap = el(12, 9, 6, 6.5) & rows(2, 12)
    c.add(cap, R("cream"), spec=C("cream", 4), spec_n=2)
    c.mark(bottom_edge(cap), C("violet", 2))
    c.add(star(12, 7.5, 2.6, 1.2, 4), R("violet", 2, 5), flat=0.5)
    return c


def i_badge():
    c = Icon()
    c.add(el(12, 12, 9, 9), R("brass"), spec=C("brass", 4), spec_n=2)
    c.add(el(12, 12, 6.5, 6.5), R("leaf"))
    c.add(small_heart(8, 8, 9), R("berry", 2, 5), flat=0.5)
    return c


def i_bell():
    c = Icon()
    c.add(box(3, 16, 21, 20, 1), R("wood"))
    c.add(el(12, 16, 7, 7) & rows(8, 16), R("cream"), spec=C("cream", 4), spec_n=2)
    c.add(box(11, 5, 12, 9, 0), R("rock"))                                         # plunger
    c.add(el(11.5, 4.5, 2, 1.5), R("rock", 2, 5))
    return c


def i_jacket():
    c = Icon()
    c.add(poly([(5, 7), (1.5, 11), (2, 20), (5, 20)]) | poly([(19, 7), (22.5, 11), (22, 20), (19, 20)]),
          R("wood", 0, 4))                                                            # sleeves
    c.add(poly([(7, 4), (17, 4), (19, 7), (19, 20), (5, 20), (5, 7)]), R("wood"), spec=C("wood", 4), spec_n=2)
    c.add(box(5, 18, 19, 20, 0), R("wood", 0, 3))                                   # waistband
    c.add(poly([(6.5, 4), (12, 10), (17.5, 4), (16, 2.5), (12, 6), (8, 2.5)]), R("cream"))   # fleece collar
    c.mark(box(12, 10, 12, 17, 0), C("wood", 1))                                    # zip
    c.mark(box(12, 10, 12, 11, 0), C("brass", 3))
    return c


def i_photo():
    c = Icon()
    c.add(box(3, 3, 21, 21, 1), R("brass"), spec=C("brass", 4), spec_n=2)
    c.add(box(6, 6, 18, 18, 0), R("cream", 2, 5), flat=0.6)
    c.add(box(6, 14, 9, 18, 1), R("berry"))                                         # three of you
    c.add(box(10, 14, 13, 18, 1), R("teal"))
    c.add(box(14, 14, 17, 18, 1), R("leaf"))
    for x, skin, hair in ((7.5, "skin", "brass"), (11.5, "skin", "soil"), (15.5, "skin2", "ink")):
        c.add(el(x, 11, 1.8, 2), R(skin, 1, 5))
        hair_r = [C("ink", 1), C("ink", 2)] if hair == "ink" else R(hair, 1, 4)
        c.add(el(x, 11, 1.8, 2) & rows(8, 9), hair_r)
    return c


DRAW = [i_stabilizer, i_wrench, i_chalkboard, i_whisk, i_brioche, i_crown, i_honey, i_souffle, i_place, i_pick,
        i_salve, i_medic_heart, i_helm, i_shield, i_map, i_mug, i_key, i_wings, i_holopad, i_loupe, i_lure,
        i_scope, i_spikes, i_lantern, i_coil, i_pillow, i_stim, i_ledger, i_chisel, i_growlight, i_glove,
        i_stewpot, i_wrench_pendant, i_apron, i_flower_frame, i_oar, i_charm, i_pauldron, i_badge, i_bell,
        i_jacket, i_photo]


def check(img, i):
    """The style guide's checklist for one icon: palette only, the outline, and the size it fills."""
    a = img[:, :, 3] > 0
    cols_used = img[a][:, :3].astype(int)
    off = [tuple(c) for c in cols_used if not (np.abs(PALETTE - c).sum(1) == 0).any()]
    assert not off, "icon %d: colours outside the palette %s" % (i, sorted(set(off))[:4])
    ys, xs = np.nonzero(a)
    w, h = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    assert max(w, h) >= 19, "icon %d fills only %dx%d" % (i, w, h)
    sp = _specks(img)
    assert not sp, "icon %d: single-pixel specks at %s" % (i, sp)


def main():
    assert len(DRAW) == len(ICONS)
    sheet = np.zeros((CELL, CELL * len(DRAW), 4), np.uint8)
    for i, fn in enumerate(DRAW):
        img = fn().render()
        check(img, i)
        sheet[:, i * CELL:(i + 1) * CELL] = img
    Image.fromarray(sheet, "RGBA").save(OUT_PNG)
    print("perk icons: %d written to art/perks.png" % len(DRAW))


if __name__ == "__main__":
    main()
