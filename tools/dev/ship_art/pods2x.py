"""Boarding pods (Claude, 22 Nov 2026; design in claude/echo-landing-boarding.md, mock-up boarding_mock.png).

art/ships/shots/pod.png         your pod: 2 frames of 58 x 22 (thruster flicker), nose right, the flame on the left.
art/ships/shots/pod_rabble.png  the Rabble's, rust with a red band (the game mirrors it to fly left).
art/ui/ship/pod_tabs.png        the system bar's two tabs over the pods icon, FTL-style, 4 frames of 54 x 50
                                (drawn at 27 x 25 and doubled): launch ready (green), launch charging (grey),
                                recall ready (yellow), recall not ready (grey). A crewmate on the left with a short
                                arched arrow: launch curves away to the right, recall comes back and points down at
                                the crewmate (Zachary: "arrows should be to the side ... and curved to fit").

Run from the repo root:  python3 -I tools/dev/ship_art/pods2x.py .
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit2x  # noqa: F401  (loads the extra colour ramps)
from pixkit import Pix


def pod(mat, trim):
    p = Pix(44, 22)
    p.bevel(p.mask(polygon=[(2, 8), (6, 5), (8, 5), (8, 16), (6, 16), (2, 13)]), "gunmetal", width=1, face=2)
    p.bevel(p.mask(ellipse=(6, 2, 40, 19)), mat, width=2, face=4)
    p.bevel(p.mask(rect=(14, 2, 18, 19)), trim, width=1, face=3)
    p.bevel(p.mask(ellipse=(24, 7, 31, 14)), "glass", width=1, face=3)
    for ty in (4, 10, 16):                           # clamp teeth on the nose
        p.bevel(p.mask(polygon=[(37, ty), (43, ty + 1), (37, ty + 2)]), "gunmetal", width=1, face=3)
    return p.render()


def flame(f):
    im = Image.new("RGBA", (14, 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    reach = 0 if f == 0 else 3
    d.polygon([(13, 7), (reach, 11), (13, 14)], fill=(255, 138, 42))
    d.polygon([(13, 9), (5 + reach, 11), (13, 12)], fill=(255, 232, 168))
    return im


def pod_sheet(mat, trim):
    body = pod(mat, trim)
    out = Image.new("RGBA", (58 * 2, 22), (0, 0, 0, 0))
    for f in range(2):
        out.alpha_composite(flame(f), (f * 58, 0))
        out.alpha_composite(body, (f * 58 + 14, 0))
    return out


ARROW = ["...XXXXXX.......",
         "..XXXXXXXXX.....",
         ".XX......XXX....",
         "XX.........XX...",
         "X........XXXXXXX",
         "..........XXXXX.",
         "...........XXX..",
         "............X..."]
FACE, LINE = (56, 58, 66, 255), (230, 236, 230, 255)
GREY = (120, 122, 130, 255)
GREEN, YELLOW = (120, 212, 106, 255), (255, 196, 80, 255)


def tab(launch, ready):
    im = Image.new("RGBA", (27, 25), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 26, 24), fill=FACE, outline=LINE if ready else GREY, width=2)
    col = (GREEN if launch else YELLOW) if ready else GREY
    hx = 4 if launch else 5
    d.ellipse((hx, 13, hx + 4, 17), fill=LINE if ready else GREY)
    d.rectangle((hx, 18, hx + 4, 21), fill=LINE if ready else GREY)
    ax0 = 8 if launch else 4
    for yy, row in enumerate(ARROW):
        for xx, ch in enumerate(row if launch else row[::-1]):
            if ch == "X":
                d.point((ax0 + xx, 4 + yy), fill=col)
    return im.resize((54, 50), Image.NEAREST)


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    (root / "art/ships/shots").mkdir(parents=True, exist_ok=True)
    (root / "art/ui/ship").mkdir(parents=True, exist_ok=True)
    pod_sheet("white", "orange").save(root / "art/ships/shots/pod.png")
    pod_sheet("rust", "banner").save(root / "art/ships/shots/pod_rabble.png")
    tabs = Image.new("RGBA", (54 * 4, 50), (0, 0, 0, 0))
    for i, (launch, ready) in enumerate(((True, True), (True, False), (False, True), (False, False))):
        tabs.alpha_composite(tab(launch, ready), (i * 54, 0))
    tabs.save(root / "art/ui/ship/pod_tabs.png")
    print("ok")
