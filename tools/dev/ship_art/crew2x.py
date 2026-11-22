"""Crew for the ship battles, FTL-style (Claude, 22 Nov 2026). Zachary: "crew art, we can use mini people sprites like ftl
and player in a space suit so we don't gotta worry about customization."

Each sheet is art/ships/crew/<id>.png: 48 x 48 frames (drawn on a 24-px grid and doubled, so they're chunky like
FTL's crew), 4 across, 9 rows. The figure stands in the middle of its frame; one crew member fills one room cell.

  row 0  walk down   4      row 3  idle (facing down)   2      row 6  at a console, facing down  2
  row 1  walk up     4      row 4  at a console, up      2      row 7  repairing (tool, sparks)   4
  row 2  walk right  4      row 5  at a console, right   2      row 8  knocked out                1
  (left is right, mirrored)

Run from the repo root:  python3 -I tools/dev/ship_art/crew2x.py .
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

OUT = (38, 37, 53, 255)
G = 24


def hexc(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def shade(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c[:3]) + (255,)


# Who: skin (head and hands), suit (body and arms), legs, and extras drawn on top.
CREW = {
    # you: a dark grey space suit with orange (Zachary), a teal visor and a backpack
    "player": dict(skin="#e8e6ee", suit="#4c4c56", legs="#3c3c46", trim="#ea6e1a", helmet=True, helmet_col="#5c5c66",
                   visor="#3aa2ac", pack=True, shoulders="#ea6e1a"),
    "human": dict(skin="#d8a07a", suit="#8e8a96", legs="#4c4a58", hair="#4a3424"),
    # Freya, as her NPC: long wavy blonde hair in a ponytail, goggles up on her head, a dark tank top with brown
    # overall straps, grey work trousers, brown boots
    "freya": dict(skin="#f0c8a0", suit="#3c3a42", legs="#55555f", hair="#e8b440", hair_long=True, ponytail=True,
                  goggles_up=True, straps="#7a5230", boots="#6e4a2c"),
    # Ana, as her NPC: dark messy hair with a red streak, a black jacket over a white shirt, navy trousers
    "ana": dict(skin="#d8a888", suit="#1e1e26", legs="#2a2e48", hair="#2a1e24", hair_long=True, streak="#a03040",
                jacket=True, boots="#5a5a64"),
    "rabble_pirate": dict(skin="#c8906a", suit="#6e4a34", legs="#3a3036", bandana="#b03434", trim="#962828"),
    "terran_marine": dict(skin="#e2e5ec", suit="#c6cbd6", legs="#80869a", helmet=True, visor="#2a52a8", trim="#3a6cc8"),
    "zaash": dict(skin="#7aa65a", suit="#925426", legs="#6e3c1c", crest="#c8b08c", trim="#cc8c44"),
    # Arachnay: a person's top half on a spider's legs
    "arachnay": dict(skin="#8666bc", suit="#523682", legs="#3c2664", extra_arms=True, eyes="#ff6a5a", spider=True),
    "moogli": dict(skin="#6aa652", suit="#4e8a3e", legs="#3a6c30", round=True, big_eyes=True, trim="#d8a82a"),
    "ervani": dict(skin="#d0682c", suit="#e8d8c0", legs="#923a16", ears=True, muzzle="#f8eedc", tail=True),
    "vuultam": dict(skin="#74bca2", suit="#3a806c", legs="#2a6456", hair="#2e6a4a", fronds="#4e8a3e", trim="#c46a96"),
    "scyldar": dict(skin="#46a4a4", suit="#246e70", legs="#1a5658", fin="#de7856", trim="#de7856"),
}


class Canvas:
    def __init__(self):
        self.a = np.zeros((G, G, 4), np.uint8)

    def px(self, x, y, c):
        if 0 <= x < G and 0 <= y < G:
            self.a[y, x] = c

    def rect(self, x0, y0, x1, y1, c, lit=True):
        """A filled box, lit from the top left: a lighter top row, a darker right column."""
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                k = 1.0
                if lit and y == y0:
                    k = 1.15
                if lit and x == x1 and x1 > x0:
                    k = 0.78
                self.px(x, y, shade(c, k))

    def ellipse(self, x0, y0, x1, y1, c, lit=True):
        cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + 0.5, (y1 - y0) / 2 + 0.5
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                u, v = (x - cx) / rx, (y - cy) / ry
                if u * u + v * v <= 1.0:
                    k = 1.0
                    if lit and (u + v) < -0.55:
                        k = 1.2
                    elif lit and (u + v) > 0.55:
                        k = 0.78
                    self.px(x, y, shade(c, k))

    def outline(self):
        m = self.a[:, :, 3] > 0
        ring = np.zeros_like(m)
        ring[1:, :] |= m[:-1, :]; ring[:-1, :] |= m[1:, :]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
        ring &= ~m
        self.a[ring] = OUT

    def image(self):
        self.outline()
        return Image.fromarray(self.a, "RGBA").resize((G * 2, G * 2), Image.NEAREST)


def figure(c, who, facing, step=0, arms="swing", work=0):
    """One crew member. facing: down, up, right. step: 0..3 of a walk. arms: swing, up (at a console), tool."""
    w = CREW[who]
    skin, suit, legs = hexc(w["skin"]), hexc(w["suit"]), hexc(w["legs"])
    trim = hexc(w["trim"]) if "trim" in w else None
    rnd = w.get("round", False)
    bob = 1 if step in (1, 3) else 0
    top = 4 + bob
    # legs
    if w.get("spider"):
        # a round abdomen behind and four thin legs a side, stepping in turn
        if facing != "down":
            c.ellipse(5 if facing == "right" else 8, top + 10, 11 if facing == "right" else 15, top + 16, legs)
            c.px(7 if facing == "right" else 11, top + 12, hexc(w["eyes"]))
        for k in range(3):
            lift = 1 if (k + step) % 2 else 0
            for side in (-1, 1):
                if facing == "right" and side == -1 and k < 1:
                    continue
                # each leg goes up to a knee, then down to its foot, spread wide and apart
                x0, y0 = 11 + side * 2, top + 11 + k
                xm, ym = 11 + side * (5 + 2 * k), top + 8 + 2 * k - lift
                x1, y1 = 11 + side * (7 + 2 * k), top + 13 + 2 * k - lift
                for (xa, ya, xb, yb) in ((x0, y0, xm, ym), (xm, ym, x1, y1)):
                    n = max(abs(xb - xa), abs(yb - ya), 1)
                    for t in range(n + 1):
                        c.px(round(xa + (xb - xa) * t / n), round(ya + (yb - ya) * t / n), shade(legs, 0.9 + 0.1 * (k % 2)))
    elif facing == "right":
        fwd = {0: 0, 1: 2, 2: 0, 3: -2}[step]
        c.rect(11 + fwd // 2, top + 13, 12 + fwd // 2, top + 17, legs)
        c.rect(11 - fwd // 2, top + 13, 12 - fwd // 2, top + 17, shade(legs, 0.8))
        if "boots" in w:
            c.rect(11 + fwd // 2, top + 17, 13 + fwd // 2, top + 17, hexc(w["boots"]), lit=False)
            c.rect(11 - fwd // 2, top + 17, 13 - fwd // 2, top + 17, shade(hexc(w["boots"]), 0.8), lit=False)
    else:
        lift = {0: (0, 0), 1: (1, 0), 2: (0, 0), 3: (0, 1)}[step]
        c.rect(9, top + 13, 10, top + 17 - lift[0], legs)
        c.rect(13, top + 13, 14, top + 17 - lift[1], legs)
        if "boots" in w:
            c.rect(9, top + 17 - lift[0], 10, top + 17 - lift[0], hexc(w["boots"]), lit=False)
            c.rect(13, top + 17 - lift[1], 14, top + 17 - lift[1], hexc(w["boots"]), lit=False)
    # a tail behind (Ervani)
    if w.get("tail") and facing != "down":
        c.ellipse(4 if facing == "right" else 10, top + 11, 9 if facing == "right" else 13, top + 16, skin)
        c.px(4 if facing == "right" else 11, top + 15, hexc(w["muzzle"]))
    # body
    if rnd:
        c.ellipse(7, top + 6, 16, top + 14, suit)
    elif facing == "right":
        c.rect(9, top + 7, 14, top + 13, suit)
    else:
        c.rect(8, top + 7, 15, top + 13, suit)
    if trim and not rnd:
        if facing == "right":
            c.rect(9, top + 11, 14, top + 11, trim, lit=False)
        else:
            c.rect(8, top + 11, 15, top + 11, trim, lit=False)
    if w.get("jacket") and facing != "up":
        c.rect(11, top + 7, 12, top + 12, hexc("#ecebe6"), lit=False)        # her white shirt under the jacket
    if "straps" in w:                                                         # Freya's overall straps
        st = hexc(w["straps"])
        if facing == "right":
            c.rect(11, top + 7, 11, top + 13, st, lit=False)
        else:
            c.rect(9, top + 7, 9, top + 12, st, lit=False); c.rect(14, top + 7, 14, top + 12, st, lit=False)
            c.rect(9, top + 12, 14, top + 13, st, lit=False)
    if "shoulders" in w and facing != "up":                                  # orange shoulder pads on your suit
        sh = hexc(w["shoulders"])
        if facing == "right":
            c.rect(11, top + 7, 13, top + 8, sh)
        else:
            c.rect(8, top + 7, 9, top + 8, sh); c.rect(14, top + 7, 15, top + 8, sh)
    if w.get("pack") and facing in ("up", "right"):
        if facing == "up":
            c.rect(9, top + 7, 14, top + 12, hexc("#c4c0cc"))
            c.rect(10, top + 8, 13, top + 9, trim, lit=False)
        else:
            c.rect(7, top + 7, 8, top + 12, hexc("#c4c0cc"))
    # arms
    def arm(x, y0, y1, col):
        c.rect(x, y0, x, y1, col)
        c.px(x, y1 + 1, skin if not w.get("helmet") else shade(suit, 0.9))
    swing = {0: 0, 1: 1, 2: 0, 3: -1}[step] if arms == "swing" else 0
    if facing == "right":
        if arms == "up":
            c.rect(14, top + 8, 16, top + 8, suit)
            c.px(17, top + 8 - (work % 2), skin)
        else:
            arm(12 + swing, top + 8, top + 11, shade(suit, 0.9))
    elif arms == "up":                                    # reaching to a console in front (up) or below (down)
        dy = -(work % 2)
        if facing == "up":
            arm(7, top + 5 + dy, top + 8, suit); arm(16, top + 5 - dy - 1, top + 8, suit)
        else:
            arm(7, top + 9, top + 12 + dy, suit); arm(16, top + 9, top + 12 - dy - 1, suit)
    elif arms == "tool":
        arm(7, top + 8, top + 11, suit)
        c.rect(16, top + 9, 17, top + 10, suit)
        c.rect(17, top + 11, 18, top + 12, hexc("#9898ac"))           # a wrench
        c.px(19, top + 13, hexc("#9898ac"))
        if work % 2 == 0:
            for (sx, sy) in ((20, top + 12), (21, top + 14), (19, top + 15)):
                c.px(sx, sy, hexc("#ffd86a"))
        else:
            c.px(20, top + 14, hexc("#ffb04a"))
    else:
        arm(7, top + 8 + max(0, -swing), top + 11 + swing, suit)
        arm(16, top + 8 + max(0, swing), top + 11 - swing, suit)
    if w.get("extra_arms"):                                 # Arachnay: a second, lower pair
        if facing == "right":
            c.px(13, top + 12, skin); c.px(14, top + 13, skin)
        else:
            c.rect(6, top + 11, 6, top + 13, skin); c.rect(17, top + 11, 17, top + 13, skin)
    # head
    hx0, hx1 = (9, 15) if facing == "right" else (8, 15)
    hy0, hy1 = top - 1, top + 6
    if rnd:
        hy0, hy1 = top + 1, top + 7
    if w.get("helmet"):
        c.ellipse(hx0 - 1, hy0 - 1, hx1 + 1, hy1, hexc(w["helmet_col"]) if "helmet_col" in w else suit)
        visor = hexc(w["visor"])
        if facing == "down":
            c.rect(hx0 + 1, hy0 + 2, hx1 - 1, hy0 + 4, visor, lit=False)
            c.px(hx0 + 1, hy0 + 2, hexc("#c8f4f4"))
        elif facing == "right":
            c.rect(hx0 + 3, hy0 + 2, hx1, hy0 + 4, visor, lit=False)
            c.px(hx0 + 3, hy0 + 2, hexc("#c8f4f4"))
        if trim:
            if who == "player":                                   # an orange stripe over the helmet
                c.rect((hx0 + hx1) // 2, hy0 - 1, (hx0 + hx1) // 2 + 1, hy0 + 1, trim, lit=False)
            else:
                c.px(hx0 + 1, hy0, trim)
        return
    c.ellipse(hx0, hy0, hx1, hy1, skin)
    eye = hexc("#1a1924")
    if "hair" in w:
        hair = hexc(w["hair"])
        long_ = w.get("hair_long", False)
        if facing == "up":
            c.ellipse(hx0 - (1 if long_ else 0), hy0 - (1 if long_ else 0), hx1 + (1 if long_ else 0), hy1 + (2 if long_ else -1), hair)
            if w.get("ponytail"):
                c.rect((hx0 + hx1) // 2 - 1, hy1, (hx0 + hx1) // 2 + 1, hy1 + 4, hair)
        else:
            c.rect(hx0, hy0 - (1 if long_ else 0), hx1, hy0 + 1, hair)
            if long_:                                                   # falling past the face to the shoulders
                if facing == "down":
                    c.rect(hx0 - 1, hy0, hx0, hy1 + 2, hair); c.rect(hx1, hy0, hx1 + 1, hy1 + 2, hair)
                else:
                    c.rect(hx0 - 1, hy0, hx0 + 2, hy1 + 2, hair)
                    if w.get("ponytail"):
                        c.rect(hx0 - 3, hy0 + 2, hx0 - 1, hy1 + 3, hair)
            elif facing == "right":
                c.rect(hx0, hy0, hx0 + 2, hy0 + 4, hair)
        if "streak" in w and facing != "up":                            # Ana's red streak
            c.rect(hx0 + 1, hy0 - (1 if long_ else 0), hx0 + 2, hy0 + 2, hexc(w["streak"]), lit=False)
        if w.get("goggles_up"):                                         # Freya's goggles pushed up on her head
            g1, g2 = hexc("#c4c0cc"), hexc("#7a5230")
            if facing == "right":
                c.rect(hx0 + 2, hy0 - 1, hx1, hy0 - 1, g2, lit=False); c.rect(hx1 - 2, hy0 - 2, hx1 - 1, hy0 - 1, g1, lit=False)
            elif facing == "down":
                c.rect(hx0, hy0, hx1, hy0, g2, lit=False)
                c.rect(hx0 + 1, hy0 - 1, hx0 + 2, hy0, g1, lit=False); c.rect(hx1 - 2, hy0 - 1, hx1 - 1, hy0, g1, lit=False)
            else:
                c.rect(hx0, hy0 + 1, hx1, hy0 + 1, g2, lit=False)
    if "bandana" in w:
        c.rect(hx0, hy0, hx1, hy0 + 1, hexc(w["bandana"]))
        if facing != "down":
            c.px(hx0 - 1 if facing == "right" else hx1 + 1, hy0 + 2, hexc(w["bandana"]))
    if "crest" in w:                                         # Zaa'sh: a bone ridge over the head
        for x in range(hx0 + 1, hx1, 2):
            c.px(x, hy0 - 1, hexc(w["crest"]))
    if "fronds" in w:                                        # Vuultam: leaves on the head
        fr = hexc(w["fronds"])
        c.px(hx0, hy0 - 1, fr); c.px(hx0 + 3, hy0 - 2, fr); c.px(hx1, hy0 - 1, fr); c.px(hx0 + 4, hy0 - 1, fr)
        c.px(hx1 - 1, hy0 - 2, hexc(w["trim"]))
    if "fin" in w:                                           # Scyldar: a fin along the head
        for y in range(hy0 - 1, hy0 + 3):
            c.px((hx0 + hx1) // 2, y, hexc(w["fin"]))
    if w.get("ears"):                                        # Ervani: fox ears and a pale muzzle
        c.px(hx0, hy0 - 1, skin); c.px(hx0, hy0 - 2, skin); c.px(hx1, hy0 - 1, skin); c.px(hx1, hy0 - 2, skin)
        if facing == "down":
            c.rect(hx0 + 2, hy0 + 4, hx1 - 2, hy1, hexc(w["muzzle"]), lit=False)
            c.px((hx0 + hx1) // 2, hy0 + 4, eye)
        elif facing == "right":
            c.rect(hx1 - 1, hy0 + 3, hx1 + 1, hy0 + 5, hexc(w["muzzle"]), lit=False)
            c.px(hx1 + 1, hy0 + 3, eye)
    if w.get("big_eyes") and facing != "right":           # Moogli: big frog eyes bulging on top of the head
        for x in (hx0 - 1, hx1 - 2):
            c.ellipse(x, hy0 - 3, x + 3, hy0 + 1, skin)
            if facing == "down":
                c.rect(x + 1, hy0 - 2, x + 2, hy0, hexc("#f6f7fa"), lit=False)
                c.px(x + 2 if x < hx0 else x + 1, hy0 - 1, eye)
    if facing == "down":
        if w.get("big_eyes"):
            c.rect(hx0 + 2, hy0 + 4, hx1 - 2, hy0 + 4, shade(skin, 0.7), lit=False)       # a wide smile
        elif "eyes" in w:
            for (x, y) in ((hx0 + 2, hy0 + 2), (hx1 - 2, hy0 + 2), (hx0 + 3, hy0 + 3), (hx1 - 3, hy0 + 3)):
                c.px(x, y, hexc(w["eyes"]))
        else:
            c.px(hx0 + 2, hy0 + 3, eye); c.px(hx1 - 2, hy0 + 3, eye)

    elif facing == "right":
        if "eyes" in w:
            c.px(hx1 - 1, hy0 + 2, hexc(w["eyes"])); c.px(hx1, hy0 + 3, hexc(w["eyes"]))
        elif w.get("big_eyes"):
            c.ellipse(hx1 - 2, hy0 - 2, hx1, hy0 + 1, skin)
            c.px(hx1, hy0 - 1, hexc("#f6f7fa")); c.px(hx1, hy0, eye)
        elif not w.get("ears"):
            c.px(hx1 - 1, hy0 + 3, eye)



def frame(who, pose, i):
    c = Canvas()
    if pose == "walk_down":
        figure(c, who, "down", i)
    elif pose == "walk_up":
        figure(c, who, "up", i)
    elif pose == "walk_right":
        figure(c, who, "right", i)
    elif pose == "idle":
        figure(c, who, "down", 1 if i else 0, arms="swing")
    elif pose == "work_up":
        figure(c, who, "up", 0, arms="up", work=i)
    elif pose == "work_right":
        figure(c, who, "right", 0, arms="up", work=i)
    elif pose == "work_down":
        figure(c, who, "down", 0, arms="up", work=i)
    elif pose == "repair":
        figure(c, who, "down", 0, arms="tool", work=i)
    elif pose == "down":
        figure(c, who, "down", 0)
        c.a = np.rot90(c.a, 1).copy()                        # lying on their side
        c.a = np.roll(c.a, 3, axis=0)
    return c.image()


ROWS = [("walk_down", 4), ("walk_up", 4), ("walk_right", 4), ("idle", 2), ("work_up", 2), ("work_right", 2),
        ("work_down", 2), ("repair", 4), ("down", 1)]


def sheet(who):
    out = Image.new("RGBA", (48 * 4, 48 * len(ROWS)), (0, 0, 0, 0))
    for r, (pose, n) in enumerate(ROWS):
        for i in range(n):
            out.alpha_composite(frame(who, pose, i), (i * 48, r * 48))
    return out


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    (root / "art/ships/crew").mkdir(parents=True, exist_ok=True)
    for who in CREW:
        sheet(who).save(root / f"art/ships/crew/{who}.png")
    print("ok", len(CREW))
