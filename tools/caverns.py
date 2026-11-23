"""The Caverns (Zachary, 17 Nov): Stardew-style floors under the mine, reached through the cavern gate.

Ten hand-made layouts (the shapes in tools/dev/mock_mine3.py, drawn half as big again), each built three times,
once per depth band, so the game has 30 cavern maps:
    rock   floors 1-15   stalagmite walls, dark chasms, iron and copper, a little quartz
    lush   floors 16-30  mossy walls, giant mushrooms and glowing fungi, overgrown pits, gold appears
    steam  floors 31-44  crystal-blue walls, steam vents, hot pools, titanium and gold
plus floor 45 (`cav_45`), the shore of the underground ocean, where the Harbinger waits.

The game (scripts/main.gd, "the caverns") picks one of the band's ten maps for each floor and scatters rocks,
ore and creatures over the open spots listed here (CAVERNS). The way down is hidden under a rock: each rock
broken has a small chance to show the shaft, rising as fewer are left, and the last rock always shows it.
Drawn in the promenade style; walls faceted by tools/bake_floor.py."""
import math
import random
from collections import deque
import survey
from survey import Room, SIZES
from engineering import chamfer_room

S, M = 1.5, 2                          # mock-up units -> tiles, and the border round each map
W, H = int(M * 2 + 30 * S), int(M * 2 + 22 * S)
WALK = 'mp'                            # cave floor, bridge
SIZES.update({
    'cavern_ladder': (2, 3, 1), 'stalagmite': (1, 2, 1), 'giant_mushroom': (2, 3, 1), 'fern': (1, 1, 1),
    'crystal_column': (1, 3, 1), 'harbinger': (8, 6, 4),
})
BANDS = {
    'rock': dict(title='rock', floor=('mine_rock', None), hole=(5, ('140e12', .88)), walls=('mine_roof', 'mine_wall'),
                 decor=[('stalagmite', 'Stalagmite')]),
    'lush': dict(title='green', floor=('cav_moss', None), hole=(5, ('12301a', .82)), walls=('lush/roof', 'lush/wall'),
                 decor=[('giant_mushroom', 'Giant mushroom'), ('glow_fungus', 'Glowing fungus'), ('glow_fungus', 'Glowing fungus')]),
    'steam': dict(title='steam', floor=('cav_slate', None), hole=('sp_water', ('f0a080', .18)), walls=('steam/roof', 'steam/wall'),
                  decor=[('steam_vent', 'Steam vent'), ('crystal_column', 'Crystal column')]),
}


# ---------------------------------------------------------------- the ten layouts (mock-up units, 30 x 22)
def octp(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def O(x0, y0, x1, y1, c=None, kind='floor'):
    c = c if c is not None else min(x1 - x0, y1 - y0) * .3
    return (kind, octp(x0, y0, x1, y1, c))


def tunnel(pts, w=3.0):
    """A 45-degree tunnel: rectangles and parallelograms for the runs, small octagons at the bends."""
    out, h = [], w / 2
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if y0 == y1: out.append([(min(x0, x1), y0 - h), (max(x0, x1), y0 - h), (max(x0, x1), y0 + h), (min(x0, x1), y0 + h)])
        elif x0 == x1: out.append([(x0 - h, min(y0, y1)), (x0 + h, min(y0, y1)), (x0 + h, max(y0, y1)), (x0 - h, max(y0, y1))])
        else:
            k = h * math.sqrt(2)
            out.append([(x0 - k, y0), (x0 + k, y0), (x1 + k, y1), (x1 - k, y1)])
    for x, y in pts: out.append(octp(x - h, y - h, x + h, y + h, h * .6))
    return [('floor', p) for p in out]


def layouts():
    L = []
    L.append(('Open hollow', [('floor', [(6, 2), (14, 2), (17, 5), (24, 5), (28, 9), (28, 16), (24, 20), (8, 20), (2, 14), (2, 6)]),
                              O(12, 9, 16, 13, kind='solid')], (6, 6)))
    L.append(('Winding tunnel', [O(1, 1, 8, 8)] + tunnel([(5, 5), (12, 5), (15, 8), (9, 14), (9, 18), (19, 18)]) +
              [O(17, 7, 29, 21, 4), O(21, 11, 24, 14, kind='solid')], (4.5, 4.5)))
    sh = [O(1, 2, 29, 21, 5)]
    r = random.Random(3)
    for j, y in enumerate((7, 11.5, 16)):
        for x in ([8, 13, 18, 23] if j % 2 == 0 else [10.5, 15.5, 20.5]):
            if r.random() < .85:
                s = r.uniform(1.4, 2.2); sh.append(O(x - s / 2, y - s / 2, x + s / 2, y + s / 2, s * .3, 'solid'))
    L.append(('Stalagmite hall', sh, (4.5, 6.5)))
    sh = [O(9, 5, 21, 17, 3.5)]
    for a, b in ((4, 4), (26, 4), (4, 18), (26, 18)): sh.append(O(a - 3.3, b - 3.3, a + 3.3, b + 3.3, 1.5))
    for a, b, c, d in ((4, 4, 11, 11), (26, 4, 19, 11), (4, 18, 11, 11), (26, 18, 19, 11)): sh += tunnel([(a, b), (c, d)], 2.6)
    L.append(('Hub and pockets', sh, (4, 4)))
    L.append(('Twin caves', [O(1, 2, 13, 20, 4), O(17, 2, 29, 20, 4), ('floor', [(12, 9.5), (18, 9.5), (18, 12.5), (12, 12.5)]),
                             O(5, 13, 9, 17, kind='solid'), O(21, 5, 25, 9, kind='solid')], (5, 6)))
    L.append(('The ring', [O(1, 1, 29, 21, 6), O(9, 7, 21, 15, 3, 'hole')], (4, 11)))
    sh = [O(1, 7.5, 8, 14.5, 2)] + tunnel([(6, 11), (13, 11)]) + tunnel([(13, 11), (19, 5), (24, 5)], 2.6) + tunnel([(13, 11), (24, 11)], 2.6) \
        + tunnel([(13, 11), (19, 17), (24, 17)], 2.6) + [O(22, 1, 29, 7.5, 2), O(22, 8, 29, 14, 2), O(22, 14.5, 29, 21, 2)]
    L.append(('The fork', sh, (4, 11)))
    L.append(('Crevasse', [O(1, 2, 29, 21, 4), ('hole', [(12, 2), (16, 2), (16, 8), (20, 12), (20, 21), (16, 21), (16, 14), (12, 10)]),
                           ('bridge', [(11, 4.5), (17, 4.5), (17, 6.5), (11, 6.5)]), ('bridge', [(15, 16.5), (21, 16.5), (21, 18.5), (15, 18.5)])],
              (5, 7)))
    L.append(('Terraces', [O(1, 1, 11, 9, 2.5), O(8, 6, 19, 15, 2.5), O(15, 12, 29, 21, 3), O(20, 1, 28, 8, 2)] + tunnel([(16, 9), (19, 6), (22, 6)], 2.6),
              (4.5, 4.5)))
    cells = {(i, j): (1 + i * 10, 1 + j * 11) for i in range(3) for j in range(2)}
    sh = [O(x, y, x + 8, y + 9.5, 2.5) for x, y in cells.values()]
    for a, b in (((0, 0), (0, 1)), ((0, 1), (1, 1)), ((1, 1), (1, 0)), ((1, 0), (2, 0)), ((2, 0), (2, 1))):
        (x0, y0), (x1, y1) = cells[a], cells[b]
        sh += tunnel([(x0 + 4, y0 + 4.75), (x1 + 4, y1 + 4.75)], 2.2)
    L.append(('Honeycomb', sh, (5, 5.5)))
    return L


def fill_poly(F, pts, ch, only=None):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    n = len(pts)
    for y in range(max(0, int(min(ys))), min(len(F), int(max(ys)) + 1)):
        for x in range(max(0, int(min(xs))), min(len(F[0]), int(max(xs)) + 1)):
            px, py, inside = x + .5, y + .5, False
            for i in range(n):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
                if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
                    inside = not inside
            if inside and (only is None or F[y][x] in only):
                F[y][x] = ch


def reachable(room, start):
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen and 0 <= nx < room.W and 0 <= ny < room.H and room.F[ny][nx] in WALK and room.obj[ny][nx] == ' ':
                seen.add((nx, ny)); q.append((nx, ny))
    return seen


def finish(g, room, band, arrive, decor_seed, decor_n=6, walls=None):
    """Ladder, decoration, the open spots for the game to fill, and registration."""
    b = BANDS[band]
    ax, ay = arrive
    room.prop('cavern_ladder', ax - 1, ay - 3, 'Ladder up', 'cav_up', 'Climb back up to the mine')
    room.keep_clear(ax - 2, ay - 1, ax + 2, ay + 2)
    seen = reachable(room, arrive)
    walk_tiles = [(x, y) for y in range(room.H) for x in range(room.W) if room.F[y][x] == 'm']
    assert len(seen & set(walk_tiles)) >= .97 * len(walk_tiles), ('cavern floor is cut in two', room.key, len(seen), len(walk_tiles))
    # decoration where it cannot block a way through: all eight neighbours open, away from the ladder
    rnd = random.Random(decor_seed)
    cand = [p for p in sorted(seen) if room.F[p[1]][p[0]] == 'm' and math.hypot(p[0] - ax, p[1] - ay) > 5
            and all(room.F[p[1] + j][p[0] + i] == 'm' for i in (-2, -1, 0, 1, 2) for j in (-2, -1, 0, 1))]
    rnd.shuffle(cand)
    placed = []
    for x, y in cand:
        if len(placed) >= decor_n: break
        if any(math.hypot(x - a, y - c) < 7 for a, c in placed): continue
        name, title = b['decor'][len(placed) % len(b['decor'])]
        w, h, solid = SIZES[name]
        if room.fits(name, x, y - h + 1):
            room.prop(name, x, y - h + 1, title, None)
            placed.append((x, y))
    seen = reachable(room, arrive)
    spots = sorted([p for p in seen if room.F[p[1]][p[0]] == 'm' and math.hypot(p[0] - ax, p[1] - ay) > 3.5 and (p[0], p[1]) not in room.clear])
    assert len(spots) >= 80, ('too few open spots', room.key, len(spots))
    import bake_floor
    bake_floor.AREA_FLOORS[room.key] = {'m': b['floor'], 'p': (3, ('5a4030', .3)), 'O': b['hole']}
    bake_floor.SECTOR_WALLS[room.key] = walls or b['walls']
    for k in ('AREA_PROPS', 'AREA_ROOF_PROPS', 'AREA_LIGHTS'): g.setdefault(k, {})[room.key] = room.props if k == 'AREA_PROPS' else []
    g.setdefault('EXTRA_THINGS', []).extend(room.things)
    g.setdefault('LUNAR_EXTRA', {})[room.t.title] = room.key
    g['MAP_PARENT'][room.key] = ['mine', 5, 26]                   # shown on the station map at the cavern gate
    keep = sorted(random.Random(decor_seed + 1).sample(spots, min(300, len(spots))))    # plenty for a floor, and keeps map_data.gd small
    return {'up': [ax, ay], 'spots': [list(p) for p in keep], 'band': band}


def build(g):
    survey.WALKABLE = WALK
    maps, bands = {}, {k: [] for k in BANDS}
    T = lambda pts: [(M + x * S, M + y * S) for x, y in pts]
    for n, (name, shapes0, up0) in enumerate(layouts(), 1):
        for mirror in (False, True):                 # every layout also comes mirrored left to right
            shapes = [(k, [(30 - x, y) for x, y in pts][::-1]) for k, pts in shapes0] if mirror else shapes0
            up = (30 - up0[0], up0[1]) if mirror else up0
            for band in BANDS:
                key = 'cav_%d_%s%s' % (n, band, '_m' if mirror else '')
                room = Room(g, key, 'Caverns: %s (%s%s)' % (name.lower(), BANDS[band]['title'], ', mirrored' if mirror else ''), W, H)
                F = room.F
                for y in range(1, H - 1):
                    for x in range(1, W - 1): F[y][x] = '#'
                for kind, ch in (('floor', 'm'), ('hole', 'O'), ('bridge', 'p'), ('solid', '#')):
                    for k, pts in shapes:
                        if k == kind: fill_poly(F, T(pts), ch)
                ux, uy = int(M + up[0] * S), int(M + up[1] * S)
                assert F[uy][ux] == 'm' and F[uy - 2][ux] == 'm', ('ladder spot not on open floor', key)
                room.t.zones.append(['The Caverns', 1, 1, W - 2, H - 2])
                holes = [T(pts) for k, pts in shapes if k == 'hole']
                if holes:
                    g.setdefault('FLOOR_EXTRAS', {})[key] = {'holes': [[list(p) for p in h] for h in holes]}
                maps[key] = finish(g, room, band, (ux, uy), n * 7 + len(band))
                bands[band].append(key)
    # ================================================================== floor 45: the underground ocean
    room = Room(g, 'cav_45', 'Caverns: the underground ocean', W, H)
    F = room.F
    for y in range(1, H - 1):
        for x in range(1, W - 1): F[y][x] = '#'
    chamfer_room(F, 2, 2, W - 3, H - 3, 'm', 6)
    ocean = [(24, 2), (W - 2, 2), (W - 2, H - 2), (31, H - 2), (31, 23), (24, 16)]
    fill_poly(F, ocean, 'O', only='m')
    g.setdefault('FLOOR_EXTRAS', {})['cav_45'] = {'holes': [ocean], 'hole_char': 'O', 'floor_char': 'm', 'lake': True}
    ux, uy = 7, 8
    room.thing('look', 'Underground ocean', 'Look', 28, 26, 50)          # the Harbinger itself is a creature (main.gd)
    room.t.zones.append(['The underground ocean', 1, 1, W - 2, H - 2])
    maps['cav_45'] = finish(g, room, 'steam', (ux, uy), 45, 4, walls=('cav_steam_roof', 'cav_steam_wall'))
    import bake_floor
    bake_floor.AREA_FLOORS['cav_45']['O'] = ('lake/water', ('142236', .35))      # the ocean: deep water like the lake's
    g['CAVERNS'] = {'maps': maps, 'bands': bands, 'last': 45, 'gate': [7, 26], 'boss': [20, 22]}
