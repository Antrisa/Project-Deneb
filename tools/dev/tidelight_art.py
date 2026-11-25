"""Tidelight's floors (24 Nov 2026): sand, sunset grass and the forest floor of the night side, 48 x 48 and seamless,
for tools/tidelight.py (art/lunar/tidelight/*.png). Drawn in code to the art style guide's floor rules: 3-4 palette
colours each, texture from small hand-placed clusters (no noise), joints and shadows one shade darker, never black.
Run: python3 tools/dev/tidelight_art.py [--preview]
"""
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from prologue_art import C, check, Canvas  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "art", "lunar", "tidelight")
S = 48


def put(cv, x, y, c):
    cv.a[y % S, x % S] = c


def cluster(cv, x, y, shape, c):
    for dx, dy in shape:
        put(cv, x + dx, y + dy, c)


DOT2 = [(0, 0), (1, 0)]
DOT3 = [(0, 0), (1, 0), (0, 1)]
PEBBLE = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]
TUFT = [(1, 0), (0, 1), (1, 1), (2, 1)]
BLADE = [(0, 0), (0, 1), (1, 1)]


def scatter(cv, rnd, n, shape, col, hl=None, avoid=None):
    for _ in range(n):
        x, y = rnd.randrange(S), rnd.randrange(S)
        cluster(cv, x, y, shape, col)
        if hl is not None:
            put(cv, x, y, hl)


def sand():
    """Warm sand in the endless sunset: soil-ramp base, rippled bands, shells and pebbles."""
    rnd = random.Random(11)
    cv = Canvas(S, S, fill=C("soil", 3))
    for _ in range(16):                             # wind ripples: short curved dashes, staggered
        x, y = rnd.randrange(S), rnd.randrange(S)
        ln = rnd.randint(5, 9)
        for k in range(ln):
            put(cv, x + k, y + (1 if 1 < k < ln - 2 else 0), C("soil", 2))
    scatter(cv, rnd, 10, DOT2, C("soil", 4))
    scatter(cv, rnd, 5, PEBBLE, C("soil", 2), C("soil", 4))
    scatter(cv, rnd, 3, DOT3, C("berry", 4))          # pink shell chips
    return cv


def grass():
    """Village grass, gold in the low sun: leaf greens warmed with brass tufts."""
    rnd = random.Random(23)
    cv = Canvas(S, S, fill=C("leaf", 2))
    scatter(cv, rnd, 26, TUFT, C("leaf", 3))
    scatter(cv, rnd, 14, BLADE, C("brass", 3))
    scatter(cv, rnd, 10, DOT2, C("leaf", 1))
    scatter(cv, rnd, 4, DOT3, C("berry", 3))          # little red flowers
    return cv


def forest():
    """The forest floor toward the night side: deep leaf litter, moss and a few violet glows."""
    rnd = random.Random(37)
    cv = Canvas(S, S, fill=C("leaf", 0))
    scatter(cv, rnd, 22, PEBBLE, C("soil", 1))
    scatter(cv, rnd, 18, TUFT, C("leaf", 1))
    scatter(cv, rnd, 8, BLADE, C("teal", 1))
    scatter(cv, rnd, 3, DOT3, C("violet", 3))         # glowing spores
    return cv


def main():
    os.makedirs(OUT, exist_ok=True)
    tiles = {"sand": sand(), "grass": grass(), "forest": forest()}
    for name, cv in tiles.items():
        check(cv, name)
        cv.save(os.path.join(OUT, name + ".png"))
    if "--preview" in sys.argv:
        sheet = Image.new("RGBA", (S * 3 * 3, S * 3))
        for i, name in enumerate(tiles):
            t = Image.open(os.path.join(OUT, name + ".png"))
            for yy in range(3):
                for xx in range(3):
                    sheet.paste(t, (i * S * 3 + xx * S, yy * S))
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save("/tmp/look/tidelight_floors.png")
    print("wrote", ", ".join(tiles))


if __name__ == "__main__":
    main()
