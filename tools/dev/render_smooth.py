# Picture of a promenade-style map as the game should draw it with baked floor and walls (no game code run).
# Drawn at one art pixel per pixel: 24 pixels a tile, the game's art grid since 18 Nov 2026 (the game's own
# world counts 16 units a tile and shows art at two-thirds; on screen that is the same picture).
import json, re, sys, math, os
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None
P, KEY, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(P + '/scripts/map_data.gd', encoding='utf-8').read()
def const(name): return json.loads(re.search(r'^const %s = (.*)$' % name, src, re.M).group(1))
i = src.index('"%s": {' % KEY, src.index('const AREAS'))
def rows(tag):
    a = src.index('"%s": [' % tag, i)
    return json.loads(re.sub(r',\s*\]$', ']', src[a + len(tag) + 4: src.index(']', a) + 1]))
F, O = rows('floor'), rows('obj')
H, W = len(F), len(F[0]); S = 24
L = P + '/art/lunar/'
tile_obj = json.loads(re.search(r'^const TILE_OBJ = (\{.*?\})$', src, re.M | re.S).group(1)); TALL = const('TALL')
if KEY == 'main':
    props, roofp, lights = const('CONCOURSE_PROPS'), const('ROOF_PROPS'), const('ROOF_LIGHTS')
else:
    props, roofp, lights = const('AREA_PROPS')[KEY], const('AREA_ROOF_PROPS')[KEY], const('AREA_LIGHTS')[KEY]
im = Image.new('RGBA', (W * S, H * S), (16, 20, 30, 255))
moon = Image.open(L + 'material_3.png').convert('RGBA'); mt = moon.width // 2
def moon_at(x, y):
    if KEY != 'main': return True
    if math.hypot(x - 115, y - 95) < 68: return True
    return any(math.hypot(x - 115 - sx * 39.6, y - 95 - sy * 39.6) < 25 for sx in (-1, 1) for sy in (-1, 1))
for y in range(H):
    for x in range(W):
        near = any(0 <= y + dy < H and 0 <= x + dx < W and F[y + dy][x + dx] == '~' for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        if (F[y][x] == '~' or (F[y][x] in '#Wzw' and near)) and moon_at(x, y):
            im.paste(moon.crop(((x % 2) * mt, (y % 2) * mt, (x % 2) * mt + mt, (y % 2) * mt + mt)).resize((S, S), Image.NEAREST), (x * S, y * S))
def baked(name):
    b = Image.open(L + name).convert('RGBA')
    return b if b.width == W * S else b.resize((W * S, H * S), Image.NEAREST)
im.alpha_composite(baked('floor_%s.png' % KEY))
im.alpha_composite(baked('walls_%s.png' % KEY))
skys = [Image.open(L + '%s.png' % n).convert('RGBA') for n in ('roof_skylight', 'roof_skylight_round') if os.path.exists(L + n + '.png')]
for lx, ly in lights: im.alpha_composite(skys[(lx * 7 + ly * 3) % len(skys)], (lx * S, max(0, ly * S - S)))
tiles = Image.open(P + '/art/tiles.png').convert('RGBA'); cell = tiles.height // 2
def tile(idx, x, y, top):
    t = tiles.crop((idx * cell, 0 if top else cell, idx * cell + cell, cell if top else 2 * cell)).resize((S, S), Image.NEAREST)
    im.alpha_composite(t, (x * S, y * S))
for y in range(H):
    for x in range(W):
        ch = O[y][x]
        if ch != 'x' and ch in tile_obj:
            tile(tile_obj[ch], x, y, False)
            if ch in TALL: tile(tile_obj[ch], x, y - 1, True)
def sprite(name, x, y, w, h, lift=0):
    s = Image.open(L + '%s.png' % name).convert('RGBA')
    im.alpha_composite(s, (max(0, x * S + (w * S - s.width) // 2), max(0, (y + h) * S - s.height - lift)))
for p in roofp: sprite(p[0], p[1], p[2], p[3], p[4], S)
for p in sorted(props, key=lambda p: p[2] + p[4]): sprite(*p[:5])
im.save(OUT)
