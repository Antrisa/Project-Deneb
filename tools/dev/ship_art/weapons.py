"""Weapons on the hull, and their shots (Claude, 21 Nov 2026). Zachary: "art for the different weapons like lasers
missiles and beams". Everything points right; the game mirrors it for enemies. The mount is the left middle.

  art/ships/weapons/<id>.png   6 frames side by side: idle, charging 1, charging 2, ready, firing 1, firing 2
                               small weapons 24 x 24 a frame, large ones (beams) 48 x 24
  art/ships/shots/<type>.png   3 frames of 16 x 8, flying right (beams: a 8 x 6 segment and a 8 x 8 end, 2 frames)

Run from the repo root with -I:  python3 -I tools/dev/ship_art/weapons.py . [out dir]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image
from ship_kit import rect, ellipse, poly, line, outline, hexc

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
METAL = {"lite": "#a8a3b0", "mid": "#7a7488", "dark": "#4e4a5a", "block": "#5d5868"}


def frame(w=24):
    return Image.new("RGBA", (w, 24), (0, 0, 0, 0))


def strip(frames):
    w = frames[0].width
    out = Image.new("RGBA", (w * len(frames), 24), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.alpha_composite(f, (i * w, 0))
    return out


def mount(im):
    rect(im, 0, 7, 6, 16, METAL["dark"]); rect(im, 1, 8, 5, 15, METAL["block"]); rect(im, 1, 8, 5, 9, METAL["mid"])


def flash(im, x, y, col, size=3):
    poly(im, [(x, y - size), (x + size + 2, y), (x, y + size)], col)
    rect(im, x, y - 1, x + 1, y + 1, "#fff6e0")


def charge_lights(im, x, y, n, lit, on_col, off_col="#3a3848"):
    for i in range(n):
        rect(im, x + i * 3, y, x + i * 3 + 1, y + 1, on_col if i < lit else off_col)


def laser(kind):
    """burst_laser: two short barrels, red; heavy_laser: one thick barrel, green; rabble_laser: crude, rusty, green."""
    glow = {"burst_laser": "#ff6a5a", "heavy_laser": "#b6ff5a", "rabble_laser": "#7dff8a"}[kind]
    frames = []
    for f in range(6):
        im = frame()
        mount(im)
        recoil = 2 if f == 5 else 0
        lit = [0, 1, 2, 3, 3, 0][f]
        if kind == "burst_laser":
            rect(im, 6, 8, 15, 15, METAL["mid"]); rect(im, 6, 8, 15, 10, METAL["lite"])
            for y in (9, 13):
                rect(im, 15 - recoil, y, 21 - recoil, y + 1, METAL["lite"]); rect(im, 15 - recoil, y + 1, 21 - recoil, y + 1, METAL["dark"])
                if lit >= 3:
                    rect(im, 20 - recoil, y, 21 - recoil, y + 1, glow)
            charge_lights(im, 7, 12, 3, lit, glow)
            if f == 4:
                flash(im, 21, 10, glow); flash(im, 21, 14, glow)
        elif kind == "heavy_laser":
            rect(im, 6, 7, 13, 16, METAL["mid"]); rect(im, 6, 7, 13, 9, METAL["lite"])
            rect(im, 13 - recoil, 9, 22 - recoil, 14, METAL["mid"]); rect(im, 13 - recoil, 9, 22 - recoil, 10, METAL["lite"])
            rect(im, 16 - recoil, 9, 17 - recoil, 14, METAL["dark"])
            if lit >= 3:
                rect(im, 21 - recoil, 10, 22 - recoil, 13, glow)
            charge_lights(im, 7, 12, 2, min(lit, 2), glow)
            if f == 4:
                flash(im, 22, 11, glow, 4)
        else:
            rust = "#8a5a3c"
            rect(im, 6, 8, 12, 15, rust); rect(im, 6, 8, 12, 9, "#a8704c")
            rect(im, 12 - recoil, 10, 20 - recoil, 13, METAL["mid"]); rect(im, 15 - recoil, 9, 16 - recoil, 14, rust)
            if lit >= 3:
                rect(im, 19 - recoil, 11, 20 - recoil, 12, glow)
            charge_lights(im, 7, 12, 2, min(lit, 2), glow)
            if f == 4:
                flash(im, 20, 11, glow)
        frames.append(outline(im))
    return strip(frames)


def missile_launcher():
    """A box with two tubes. Missiles load in one at a time; when ready their red tips blink; firing leaves one tube empty."""
    frames = []
    for f in range(6):
        im = frame()
        mount(im)
        rect(im, 6, 6, 19, 17, METAL["mid"]); rect(im, 6, 6, 19, 8, METAL["lite"]); rect(im, 6, 16, 19, 17, METAL["dark"])
        loaded = [0, 1, 2, 2, 1, 1][f]
        for i, y in enumerate((9, 13)):
            rect(im, 10, y, 20, y + 2, "#2e2c38")
            if i < loaded:
                rect(im, 11, y, 18, y + 2, "#d8d4c8"); rect(im, 19, y, 20, y + 2, "#e6463c" if f != 3 else "#ff9a8a")
        if f == 4:
            flash(im, 20, 10, "#ffb04a", 3)
            rect(im, 0, 3, 3, 5, "#c8c4c0")
        frames.append(outline(im))
    return strip(frames)


def ion_blaster():
    """Blue coils round a short barrel; a crackling orb at the muzzle when ready."""
    frames = []
    for f in range(6):
        im = frame()
        mount(im)
        rect(im, 6, 9, 20, 14, METAL["mid"]); rect(im, 6, 9, 20, 10, METAL["lite"])
        lit = [0, 1, 2, 3, 3, 0][f]
        for i in range(3):
            rect(im, 8 + i * 4, 7, 9 + i * 4, 16, "#5ab4ff" if i < lit else "#2a3a5a")
        if lit >= 3:
            ellipse(im, 19, 9, 23, 14, "#8ad8ff")
        if f == 4:
            flash(im, 21, 11, "#8ad8ff", 4)
        frames.append(outline(im))
    return strip(frames)


def beam_emitter():
    """Large (48 x 24): a long emitter with a lens at the end that fills with light, then lets go."""
    frames = []
    for f in range(6):
        im = frame(48)
        mount(im)
        poly(im, [(6, 6), (34, 8), (40, 10), (40, 13), (34, 15), (6, 17)], METAL["mid"])
        poly(im, [(6, 6), (34, 8), (40, 10), (6, 10)], METAL["lite"])
        for x in (14, 22, 30):
            line(im, [(x, 7), (x, 16)], METAL["dark"])
        lit = [0, 1, 2, 3, 3, 1][f]
        lens = ["#4a3a5a", "#8a5aa8", "#c87ad8", "#ffb0f0"][lit]
        ellipse(im, 38, 8, 45, 15, METAL["dark"]); ellipse(im, 39, 9, 44, 14, lens)
        charge_lights(im, 9, 12, 4, lit + (1 if lit == 3 else 0), "#ff8ae0")
        if f == 4:
            rect(im, 44, 10, 47, 13, "#fff0fa"); rect(im, 45, 9, 47, 14, "#ffb0f0")
        frames.append(outline(im))
    return strip(frames)


def shots():
    """Projectiles, 3 frames of 16 x 8, flying right."""
    out = {}
    def make(draw):
        fs = []
        for f in range(3):
            im = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
            draw(im, f)
            fs.append(im)
        s = Image.new("RGBA", (48, 8), (0, 0, 0, 0))
        for i, im in enumerate(fs):
            s.alpha_composite(im, (i * 16, 0))
        return s
    def bolt(core, edge, thick):
        def d(im, f):
            y0 = 4 - thick // 2
            rect(im, 4 - f, y0, 15, y0 + thick - 1, edge)
            rect(im, 7 - f, y0 + (1 if thick > 2 else 0), 15, y0 + thick - (2 if thick > 2 else 1), core)
            rect(im, 1 - f + 2, 3, 3 - f + 2, 4, edge if f < 2 else core)
        return d
    out["laser"] = make(bolt("#fff0e8", "#ff6a5a", 3))
    out["heavy_laser"] = make(bolt("#f8ffe0", "#b6ff5a", 4))
    out["rabble_laser"] = make(bolt("#f0fff0", "#7dff8a", 2))
    def missile(im, f):
        rect(im, 4, 3, 12, 5, "#d8d4c8"); rect(im, 4, 5, 12, 5, "#a8a4a0"); rect(im, 13, 3, 14, 5, "#e6463c"); rect(im, 15, 4, 15, 4, "#e6463c")
        rect(im, 5, 2, 6, 2, "#7a7488"); rect(im, 5, 6, 6, 6, "#7a7488")
        rect(im, 0 + f % 2, 3, 3, 5, "#ffb04a"); rect(im, 2, 4, 3, 4, "#fff0c0")
    out["missile"] = make(missile)
    def ion(im, f):
        ellipse(im, 8, 1, 14, 7, "#5ab4ff"); ellipse(im, 9, 2, 13, 6, "#c8f0ff")
        for (x, y) in [(6, 2 + f), (7, 6 - f), (5, 4)]:
            rect(im, x, y, x, y, "#8ad8ff")
    out["ion"] = make(ion)
    def cannon(im, f):
        ellipse(im, 6, 1, 15, 7, "#c8901a"); ellipse(im, 8, 2, 14, 5, "#ffd34a"); rect(im, 0 + f, 3, 6, 5, "#ffb04a")
    out["cannon"] = make(cannon)
    # beams: a repeating segment (8 x 6) and the end where it hits (8 x 8), 2 frames each
    seg = Image.new("RGBA", (16, 6), (0, 0, 0, 0))
    for f in range(2):
        rect(seg, f * 8, 0, f * 8 + 7, 5, "#ff8ae0"); rect(seg, f * 8, 1 + f, f * 8 + 7, 4 - f, "#fff0fa")
    out["beam"] = seg
    end = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
    for f in range(2):
        ellipse(end, f * 8, 0, f * 8 + 7, 7, "#ff8ae0"); ellipse(end, f * 8 + 2 - f, 2 - f, f * 8 + 5 + f, 5 + f, "#fff0fa")
    out["beam_end"] = end
    return out


WEAPON_ART = {
    "burst_laser": lambda: laser("burst_laser"),
    "heavy_laser": lambda: laser("heavy_laser"),
    "rabble_laser": lambda: laser("rabble_laser"),
    "missile_launcher": missile_launcher,
    "ion_blaster": ion_blaster,
    "beam_emitter": beam_emitter,
}

if __name__ == "__main__":
    base = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "art/ships"
    (base / "weapons").mkdir(parents=True, exist_ok=True)
    (base / "shots").mkdir(parents=True, exist_ok=True)
    for wid, fn in WEAPON_ART.items():
        fn().save(base / "weapons" / f"{wid}.png")
    for sid, im in shots().items():
        im.save(base / "shots" / f"{sid}.png")
    print("ok")
