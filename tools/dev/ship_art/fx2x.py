"""Battle effects, FTL-style (Claude, 22 Nov 2026). Zachary: "space combat animations ... fire on the ship".

art/ships/fx/fire.png   4 frames of 24 x 24, looping: a small fire; the game puts three in each burning cell.
art/ships/fx/smoke.png  4 frames of 24 x 24, looping: smoke rising from a damaged or burning room.
art/ships/fx/hit.png    6 frames of 48 x 48: a shot hitting the hull: flash, fireball, debris, smoke.

Fire and smoke are at the ships' own pixel size, like the crew (Zachary, 22 Nov: smaller); the hit is doubled. Run from the repo root:  python3 -I tools/dev/ship_art/fx2x.py .
"""
import sys, math, random
from pathlib import Path
import numpy as np
from PIL import Image

G = 24
FIRE = [(106, 26, 16, 255), (226, 69, 31, 255), (255, 138, 42, 255), (255, 216, 106, 255), (255, 244, 192, 255)]


def up2(a):
    return Image.fromarray(a, "RGBA").resize((G * 2, G * 2), Image.NEAREST)


def up1(a):
    return Image.fromarray(a, "RGBA")


def flame(a, cx, base, h, w, phase):
    """One tongue of flame: wide at the floor, flickering to a point; red rim, orange, yellow, a pale core."""
    for y in range(base - h, base + 1):
        t = (base - y) / max(1, h)                       # 0 at the floor, 1 at the tip
        sway = math.sin(t * 3.0 + phase) * 1.2 * t
        half = w * (1.0 - t ** 1.4)
        for x in range(int(cx - half - 1), int(cx + half + 2)):
            d = abs(x - (cx + sway)) / max(0.6, half)
            if d > 1.0:
                continue
            if d > 0.78 or t > 0.85:
                col = FIRE[1]
            elif d > 0.5 or t > 0.6:
                col = FIRE[2]
            elif d > 0.25 or t > 0.35:
                col = FIRE[3]
            else:
                col = FIRE[4]
            if 0 <= x < G and 0 <= y < G:
                a[y, x] = col


def outline(a, col):
    m = a[:, :, 3] > 0
    ring = np.zeros_like(m)
    ring[1:, :] |= m[:-1, :]; ring[:-1, :] |= m[1:, :]; ring[:, 1:] |= m[:, :-1]; ring[:, :-1] |= m[:, 1:]
    a[ring & ~m] = col


def fire():
    out = Image.new("RGBA", (G * 4, G), (0, 0, 0, 0))
    for f in range(4):
        a = np.zeros((G, G, 4), np.uint8)
        rng = random.Random(f)
        for i, cx in enumerate((5, 11, 17, 8, 14)):
            h = [9, 13, 10, 7, 8][i] + int(3 * math.sin(f * 1.6 + i * 2.1))
            w = 3.2 if i < 3 else 2.4
            flame(a, cx + (f + i) % 2, 21, h, w, f * 1.4 + i)
        for _ in range(3):                                   # embers drifting up
            x, y = rng.randint(3, 20), rng.randint(2, 9)
            a[y, x] = FIRE[3 if rng.random() < 0.5 else 2]
        outline(a, FIRE[0])
        out.alpha_composite(up1(a), (f * G, 0))
    return out


def smoke():
    """Three puffs rising and swelling, evenly spaced so the 4 frames loop."""
    out = Image.new("RGBA", (G * 4, G), (0, 0, 0, 0))
    for f in range(4):
        a = np.zeros((G, G, 4), np.uint8)
        for i in range(3):
            k = ((f + i * 4) % 12) / 12.0            # 0 at the floor, 1 at the ceiling
            cy = 19 - k * 17
            cx = 9 + i * 3 + 2.0 * math.sin(k * 5 + i)
            r = 2.2 + k * 3.4
            alpha = int(190 * (1.0 - k * 0.75))
            for y in range(G):
                for x in range(G):
                    d = (x - cx) ** 2 + (y - cy) ** 2
                    if d <= r * r and a[y, x, 3] < alpha:
                        lit = (x - cx) + (y - cy) < -r * 0.3
                        g = 176 if lit else 138
                        a[y, x] = (g, g - 4, g + 2, alpha)
        out.alpha_composite(up1(a), (f * G, 0))
    return out


def hit():
    out = Image.new("RGBA", (48 * 6, 48), (0, 0, 0, 0))
    rng = random.Random(4)
    debris = [(rng.uniform(0, 2 * math.pi), rng.uniform(4, 10)) for _ in range(7)]
    for f in range(6):
        a = np.zeros((G, G, 4), np.uint8)
        c = 12
        r = [3, 6, 8, 9, 8, 6][f]
        for y in range(G):
            for x in range(G):
                d = math.hypot(x - c, y - c) + 0.8 * math.sin(x * 1.7 + y * 2.3 + f)
                if d <= r:
                    t = d / max(1, r)
                    if f == 0:
                        col = (255, 255, 240, 255)
                    elif f >= 4:
                        g = 96 + int(40 * (1 - t))
                        col = (g, g - 6, g - 10, int(220 * (1 - (f - 4) * 0.4)))
                    elif t < 0.35:
                        col = FIRE[4] if f < 2 else FIRE[3]
                    elif t < 0.65:
                        col = FIRE[3] if f < 2 else FIRE[2]
                    else:
                        col = FIRE[2] if f < 3 else FIRE[1]
                    a[y, x] = col
        if 1 <= f <= 4:                                       # debris flying out
            for ang, sp in debris:
                x = int(c + math.cos(ang) * sp * f * 0.55)
                y = int(c + math.sin(ang) * sp * f * 0.55)
                if 0 <= x < G and 0 <= y < G:
                    a[y, x] = (200, 196, 210, 255) if f < 3 else (120, 116, 130, 255)
        if f < 4:
            outline(a, FIRE[0])
        out.alpha_composite(up2(a), (f * 48, 0))
    return out


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    (root / "art/ships/fx").mkdir(parents=True, exist_ok=True)
    fire().save(root / "art/ships/fx/fire.png")
    smoke().save(root / "art/ships/fx/smoke.png")
    hit().save(root / "art/ships/fx/hit.png")
    print("ok")
