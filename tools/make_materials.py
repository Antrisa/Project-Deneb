"""Placeholder floor and wall materials for the Engineering sector (Engineering and the Shuttle Bay).
Each is 64 x 64 at the double-detail scale (32 pixels = one tile), so it covers 2 x 2 tiles and must tile
seamlessly. A file that already exists is never touched, so painted art is safe.
    python3 tools/make_materials.py ."""
import os, sys
import numpy as np
from PIL import Image

OUT = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "art", "lunar")
N = 64
y, x = np.mgrid[0:N, 0:N]


def noise(seed, scale=1.0):
    """Seamless value noise: a random 8 x 8 grid, wrapped and blurred."""
    rnd = np.random.default_rng(seed)
    g = rnd.random((8, 8))
    gx, gy = x / 8.0, y / 8.0
    x0, y0 = gx.astype(int), gy.astype(int)
    fx, fy = gx - x0, gy - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = g[y0 % 8, x0 % 8], g[y0 % 8, (x0 + 1) % 8]
    c, d = g[(y0 + 1) % 8, x0 % 8], g[(y0 + 1) % 8, (x0 + 1) % 8]
    smooth = (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
    grain = rnd.random((N, N))
    return (smooth * .7 + grain * .3) * scale


def rgb(c):
    return np.array(c, np.float32)


def shade(img, k):
    return np.clip(img * k[..., None], 0, 255)


def plate_steel():
    """Works hall: diamond (tread) plate in big welded panels."""
    base = np.ones((N, N, 3), np.float32) * rgb((112, 122, 136))
    img = shade(base, .92 + noise(1) * .14)
    u, v = (x + y) % 8, (x - y) % 8                          # raised diamonds
    bump = ((u == 1) | (u == 2)) & ((v >= 3) & (v <= 5))
    img[bump] = img[bump] * 1.18
    img[((u == 3)) & ((v >= 3) & (v <= 5))] *= .78
    seam = (x % 64 == 0) | (y % 64 == 0)
    img[seam] = rgb((60, 66, 78)); img[(x % 64 == 1) | (y % 64 == 1)] *= 1.12
    return img


def ore_floor():
    """Ore processing: scuffed concrete, rust and rock dust, steel edge strips."""
    img = shade(np.ones((N, N, 3), np.float32) * rgb((128, 112, 96)), .85 + noise(2) * .3)
    rust = noise(3) > .62
    img[rust] = img[rust] * .6 + rgb((150, 80, 40)) * .4
    dust = noise(4) > .7
    img[dust] = img[dust] * .7 + rgb((90, 84, 80)) * .3
    crack = (np.abs(((x * 3 + y * 5) % 64) - 32) < 1) & (noise(5) > .55)
    img[crack] *= .6
    edge = (x % 32 == 0) | (y % 32 == 0)
    img[edge] = rgb((88, 80, 74))
    return img


def concrete():
    """Stores, cargo staging and the spare workshops: sealed grey concrete slabs with a painted bay line."""
    img = shade(np.ones((N, N, 3), np.float32) * rgb((150, 150, 146)), .9 + noise(6) * .18)
    img[(x % 32 == 0) | (y % 32 == 0)] = rgb((104, 104, 104))
    stripe = (y >= 60) & (y <= 61) & ((x // 6) % 2 == 0)
    img[stripe] = rgb((214, 176, 60))
    return img


def tech_floor():
    """Tikka's bay: clean blue-grey anti-static panels with corner bolts."""
    img = shade(np.ones((N, N, 3), np.float32) * rgb((118, 134, 152)), .95 + noise(7) * .08)
    lx, ly = x % 32, y % 32
    img[(lx == 0) | (ly == 0)] = rgb((70, 80, 96)); img[(lx == 1) | (ly == 1)] = rgb((160, 174, 190))
    bolt = ((lx - 4) ** 2 + (ly - 4) ** 2 <= 2) | ((lx - 27) ** 2 + (ly - 27) ** 2 <= 2)
    img[bolt] = rgb((180, 186, 196))
    return img


def lino():
    """Crew break room and Tikka's office: warm rubber tiles in two shades."""
    check = ((x // 16) + (y // 16)) % 2 == 0
    img = np.where(check[..., None], rgb((176, 140, 104)), rgb((160, 124, 92)))
    img = shade(img, .95 + noise(8) * .08)
    img[(x % 16 == 0) | (y % 16 == 0)] *= .8
    return img


def grate():
    """Cooling & life support: steel grating over a dark wet sump."""
    img = shade(np.ones((N, N, 3), np.float32) * rgb((40, 52, 60)), .8 + noise(9) * .3)
    bar = (x % 6 <= 1) | (y % 16 <= 1)
    img[bar] = shade(np.ones((N, N, 3), np.float32) * rgb((130, 140, 150)), .9 + noise(10) * .15)[bar]
    img[(x % 32 == 0) | (y % 32 == 0)] = rgb((84, 92, 104))
    return img


def hangar():
    """Shuttle bay: large worn hangar plates, darker scorch, rivet rows."""
    img = shade(np.ones((N, N, 3), np.float32) * rgb((122, 128, 136)), .9 + noise(11) * .16)
    scorch = noise(12) > .72
    img[scorch] *= .82
    img[(x % 64 == 0) | (y % 64 == 0)] = rgb((70, 76, 86)); img[(x % 64 == 1) | (y % 64 == 1)] *= 1.1
    riv = ((x % 8 == 4) & ((y % 64 == 4) | (y % 64 == 60))) | ((y % 8 == 4) & ((x % 64 == 4) | (x % 64 == 60)))
    img[riv] = rgb((170, 176, 186))
    return img


def wall_face():
    """Wall face (the front of a wall, 64 tall = 32 world pixels): riveted steel panels, a pipe along the top,
    a hazard stripe at the foot."""
    img = shade(np.ones((N, N, 3), np.float32) * rgb((116, 120, 128)), .92 + noise(13) * .12)
    img[x % 32 == 0] = rgb((70, 74, 84)); img[x % 32 == 1] *= 1.15
    img[(y >= 6) & (y <= 13)] = rgb((150, 110, 70)); img[y == 6] = rgb((200, 160, 110)); img[y == 13] = rgb((90, 64, 40))
    img[(y >= 8) & (y <= 11) & (x % 32 == 16)] = rgb((60, 60, 66))           # pipe clamps
    riv = ((x % 32 == 4) | (x % 32 == 28)) & ((y == 20) | (y == 46))
    img[riv] = rgb((190, 196, 204))
    hz = y >= 54
    img[hz] = np.where((((x + y) // 6) % 2 == 0)[hz][..., None], rgb((226, 180, 48)), rgb((40, 40, 46)))
    img[y == 53] = rgb((50, 52, 60))
    return img


def roof():
    """Wall tops (the roof seen from above): dark steel plate with bolts."""
    img = shade(np.ones((N, N, 3), np.float32) * rgb((76, 82, 94)), .9 + noise(14) * .14)
    img[(x % 32 == 0) | (y % 32 == 0)] = rgb((50, 54, 64))
    bolt = (x % 16 == 8) & (y % 16 == 8)
    img[bolt] = rgb((130, 136, 148))
    return img


def pad():
    """Ship and drone pads: heat-proof grey plates with yellow guide lines."""
    img = shade(np.ones((N, N, 3), np.float32) * rgb((104, 108, 112)), .9 + noise(15) * .14)
    img[(x % 32 == 0) | (y % 32 == 0)] = rgb((70, 72, 78))
    line = ((x >= 30) & (x <= 33) & ((y // 8) % 2 == 0)) | ((y >= 30) & (y <= 33) & ((x // 8) % 2 == 0))
    img[line] = rgb((226, 180, 48))
    return img


MATERIALS = {'eng_floor_pad': pad, 'eng_floor_plate': plate_steel, 'eng_floor_ore': ore_floor, 'eng_floor_concrete': concrete,
             'eng_floor_tech': tech_floor, 'eng_floor_lino': lino, 'eng_floor_grate': grate, 'eng_floor_hangar': hangar,
             'eng_wall': wall_face, 'eng_roof': roof}

if __name__ == "__main__":
    for name, fn in MATERIALS.items():
        path = os.path.join(OUT, name + ".png")
        if os.path.exists(path):
            continue
        Image.fromarray(np.clip(fn(), 0, 255).astype(np.uint8), "RGB").save(path)
        print("placeholder:", path)
