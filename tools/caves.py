"""The Mine and the North Cave, rebuilt in the promenade style (Zachary, 17 Nov; mock-ups in tools/dev/mock_mine3.py).

mine     option A, shortened: you come in from Engineering on the east into Job's mine head (lockers, tool crib,
         his desk, ore analyzers). The loading spot sits north of it, where a hopper tips ore onto a conveyor that
         runs out east along the north wall to Engineering's ore processing (it never crosses a walkway). West of
         the head, the main gallery: a clear walkway down the middle, lamps, rocks to cut for stone. The iron bay bulges north
         off the gallery on 45-degree walls (the passage up to the North Cave leaves its top), the copper bay south.
         Zaas's survey room is in the south-west; at the west end, the barricaded cavern gate that Vzz'ket guards.
tunnels  the North Cave, option A without water: one big octagonal chamber round four rock pillars, with four
         ore beds (two iron, two copper) that refill every two days. Map key kept as "tunnels" so the save data,
         Job's quest and the weapon check still work. Its creatures stay until the Caverns exist, because Job's
         "clear the tunnels" quest needs them.
Drawn in the promenade style; walls faceted by tools/bake_floor.py."""
import random
import survey
import engineering                     # its prop sizes
from survey import Room, SIZES
from engineering import chamfer_room

WALKABLE = 'muofhkRu.sp'
SIZES.update({
    'boulder': (2, 2, 1), 'ore_analyzer': (2, 3, 1), 'barricade': (4, 2, 1), 'crystal_cluster': (2, 2, 1),
    'glow_fungus': (1, 1, 1), 'work_light': (1, 2, 1), 'crystal_column': (1, 3, 1), 'stalagmite': (1, 2, 1),
})
ENG_LANDING = (66, 25)                 # where you arrive in the mine from Engineering
MINE_TOP = (28, 3)                     # where you arrive back in the mine from the North Cave
CAVE_LANDING = (30, 36)                # where you arrive in the North Cave
LAKE_STAIR = (34, 37)                  # the old stair under the copper bay, down to the underground lake (x range)
MINE_FROM_LAKE = (35, 45)              # where you arrive back in the mine from the lake
LAKE_LANDING = (31, 5)                 # where you arrive at the lake


def poly(F, pts, ch):
    """Fill every tile whose centre lies inside the polygon (corners on tile edges, sides straight or 45 degrees)."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    n = len(pts)
    for y in range(int(min(ys)), int(max(ys)) + 1):
        for x in range(int(min(xs)), int(max(xs)) + 1):
            px, py, inside = x + .5, y + .5, False
            for i in range(n):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
                if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
                    inside = not inside
            if inside:
                F[y][x] = ch


def fill(F, x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): F[y][x] = ch


def pick_spots(room, region, n, seed, gap=3.0, floor='m'):
    """n ore spots inside region (x0, y0, x1, y1): on `floor`, free, not against a wall, apart from each other."""
    x0, y0, x1, y1 = region
    rnd = random.Random(seed)
    cells = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
    rnd.shuffle(cells)
    out = []
    for x, y in cells:
        if len(out) >= n: break
        if room.F[y][x] != floor or not room.free(x, y): continue
        if not all(room.F[y + b][x + a] in WALKABLE and room.free(x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)): continue
        if any((x - a) ** 2 + (y - b) ** 2 < gap * gap for a, b in out): continue
        out.append((x, y))
    assert len(out) == n, ('not enough room for ore', room.key, region, len(out), n)
    for p in out: room.clear.add(p)            # nothing else may stand on an ore vein
    return out


def build(g):
    survey.WALKABLE = WALKABLE
    nodes, enemies = [], []
    # ================================================================== mine: option A, shortened (70 x 50)
    m = Room(g, 'mine', 'The Mine', 70, 50)
    F = m.F
    fill(F, 1, 1, 68, 48, '#')
    IRON = [(15, 19), (15, 11), (21, 5), (39, 5), (45, 11), (45, 19)]
    COPPER = [(23, 33), (23, 41), (29, 47), (43, 47), (49, 41), (49, 33)]
    poly(F, IRON, 'm'); poly(F, COPPER, 'm')
    fill(F, 9, 19, 50, 32, 'm')                                     # the main gallery
    poly(F, [(9, 19), (9, 33), (5, 29), (5, 23)], 'm')              # it narrows into the gate
    chamfer_room(F, 2, 20, 9, 32, 'k', 2)                           # the cavern gate
    fill(F, 5, 24, 50, 27, 'u')                                     # the walkway down the gallery
    chamfer_room(F, 3, 34, 19, 47, 'h', 3)                          # Zaas's survey room
    fill(F, 10, 32, 13, 34, 'h')
    chamfer_room(F, 49, 15, 65, 37, 'f', 3)                         # Job's mine head
    fill(F, 66, 23, 67, 28, 'f')
    poly(F, [(47, 3), (63, 3), (67, 7), (67, 13), (47, 13)], 'o')   # the loading spot
    fill(F, 54, 13, 57, 15, 'o')
    fill(F, 27, 2, 30, 5, 'u')                                      # up to the North Cave
    fill(F, LAKE_STAIR[0], 44, LAKE_STAIR[1], 48, 'u')              # down to the underground lake (sealed until the Leviathan is dead)
    m.t.warp('R', [(68, y) for y in range(24, 28)], 'eng', 3, 36)            # the tunnel off the west end of the hall
    m.t.warp('R', [(x, 1) for x in range(27, 31)], 'tunnels', CAVE_LANDING[0], CAVE_LANDING[1])
    m.t.warp('R', [(x, 48) for x in range(LAKE_STAIR[0], LAKE_STAIR[1] + 1)], 'lake', LAKE_LANDING[0], LAKE_LANDING[1])
    m.t.zones += [['Mine head', 49, 15, 67, 37], ['Loading spot', 47, 3, 67, 14], ['Iron bay', 15, 3, 45, 18],
                  ['Copper bay', 23, 33, 49, 47], ['Survey room', 3, 33, 19, 47], ['Cavern gate', 2, 20, 9, 32],
                  ['Main gallery', 9, 19, 50, 32]]
    # keep the walkway, the doorways and the way up clear
    m.keep_clear(7, 24, 67, 27); m.keep_clear(26, 2, 31, 8); m.keep_clear(9, 30, 14, 36); m.keep_clear(53, 12, 58, 18)
    m.keep_clear(64, 22, 68, 29); m.keep_clear(LAKE_STAIR[0] - 1, 42, LAKE_STAIR[1] + 1, 48)
    # ore: iron in the iron bay, copper in the copper bay, a stray vein or two in the gallery
    for kind, region, n, seed in (('iron_ore', (16, 8, 44, 17), 6, 11), ('copper_ore', (24, 35, 48, 45), 6, 12),
                                  ('copper_ore', (16, 6, 44, 17), 1, 13), ('iron_ore', (24, 35, 48, 45), 1, 14),
                                  ('iron_ore', (12, 20, 46, 22), 1, 15), ('copper_ore', (12, 29, 46, 31), 1, 16)):
        for x, y in pick_spots(m, region, n, seed):
            nodes.append([kind, 'mine', x, y])
    # plain rocks to cut for stone, scattered over both bays and the gallery's edges (they come back each morning)
    for region, n, seed in (((16, 6, 44, 18), 10, 21), ((24, 34, 48, 46), 10, 22), ((10, 20, 47, 22), 3, 23), ((10, 29, 47, 31), 3, 24)):
        for x, y in pick_spots(m, region, n, seed, gap=2.3):
            nodes.append(['stone', 'mine', x, y])
    P, N = m.prop, m.near
    # Job's mine head: his desk and board, lockers, the tool crib, two ore analyzers, a water cooler, a bench
    N('curator_desk', 54.5, 19.5, "Job's desk", 'look', 'Look'); N('star_chart', 58.5, 18.5, 'Dig plan', 'look', 'Look')
    N('ore_analyzer', 62, 19.5, 'Ore analyzer', 'look', 'Look'); N('ore_analyzer', 52, 31.5, 'Ore analyzer', None)
    for fy in (30.5, 34): N('locker', 63.5, fy, 'Miners\' lockers', 'look' if fy == 30.5 else None, 'Look')
    N('parts_rack', 57.5, 34.5, 'Tool crib', 'look', 'Look'); N('tool_cart', 52, 22.5, 'Tool cart', None)
    N('drinking_fountain', 60, 22.5, 'Water cooler', None); N('bench_s', 57, 29.5, 'Bench', 'seat', 'Sit')
    N('hazard_sign', 64, 21.5, 'Sign: hard hats past this point', None)
    # the loading spot: ore bins, the hopper onto the belt, an analyzer, carts
    N('hopper', 61.5, 7.5, 'Ore hopper', 'look', 'Look')
    for fx in (49.5, 52.5): N('ore_pile', fx, 6, 'Ore bin', None)
    N('ore_analyzer', 48.5, 11, 'Ore analyzer', None); N('ore_cart', 53, 11, 'Ore cart', None); N('ore_cart', 59, 12, 'Ore cart', None)
    N('hazard_sign', 65.5, 10, 'Sign: keep clear of the belt', None)
    # the gallery: work lights along both sides, loose boulders in the bays
    for fx in (12, 24, 36, 48):
        N('work_light', fx, 21.5, 'Work light', None); N('work_light', fx, 30.5, 'Work light', None)
    N('ore_cart', 36, 22.5, 'Ore cart', None); N('ore_cart', 20, 30.5, 'Ore cart', None)
    # Zaas's survey room: crystal samples, an analyzer, a console and a map of the deep
    N('crystal_cluster', 6.5, 38, 'Crystal samples', 'inspect', 'Inspect'); N('crystal_cluster', 15.5, 38, 'Crystal samples', None)
    N('ore_analyzer', 15.5, 44, 'Survey analyzer', 'look', 'Look'); N('console', 9, 44.5, 'Survey console', 'look', 'Look')
    N('star_chart', 11, 36.5, 'Map of the deep caverns', 'look', 'Look'); N('storage_shelf', 5.5, 43, 'Sample shelves', None)
    # the cavern gate: barricaded until the Caverns open
    P('barricade', 2, 24, 'Barricade', None)
    m.thing('cav_gate', 'Cavern gate', 'Go down into the Caverns', 4.5, 26, 40)
    N('work_light', 4, 22, 'Work light', None); N('work_light', 4, 31, 'Work light', None)
    N('hazard_sign', 7.5, 22.5, 'Sign: caverns closed', None)
    # the old flooded stair down to the underground lake: sealed (main.gd) until the Leviathan is dead
    N('hazard_sign', LAKE_STAIR[1] + 2.5, 45.5, 'Sign: flooded stair, sealed', None)
    N('work_light', LAKE_STAIR[0] - 2, 45, 'Work light', None)
    m.thing('look', 'Flooded stair', 'Look', MINE_FROM_LAKE[0] + .5, 46.5, 40)
    m.t.zones.insert(0, ['Flooded stair', LAKE_STAIR[0] - 1, 43, LAKE_STAIR[1] + 1, 48])
    # Vzz'ket's camp beside the gate he guards (Zachary, 20 Nov): he sleeps here, on his bedroll
    from residences import free_spot
    mat = N('prayer_mat', 6.5, 30.5, "Vzz'ket's bedroll", 'look', 'Look')
    N('brazier', 8.5, 30.5, 'Camp stove', 'look', 'Look'); N('footlocker', 6, 21.5, "Vzz'ket's kit chest", 'look', 'Look')
    N('cargo', 3.5, 29.5, 'Ration crates', None)
    g.setdefault('HOME_SPOTS', {})["Vzz'ket"] = ('mine',) + free_spot(m, mat[0] + 1, mat[1] + .5, set(), set())
    # the conveyor from the hopper out to Engineering, painted into the floor along the loading spot's north side
    g.setdefault('FLOOR_EXTRAS', {})['mine'] = {'belts': [[(63.5, 8.5), (67.9, 8.5)]], 'rails': [[(9.5, 26), (48.5, 26)]],
                                                'stairs': [(27, 1, 30, 5, 'n'), (LAKE_STAIR[0], 44, LAKE_STAIR[1], 48, 's')]}
    import bake_floor
    bake_floor.CAVE_LIGHTS['mine'] = [(fx, fy - .6, 'warm', 3.6) for fx in (12, 24, 36, 48) for fy in (21.5, 30.5)] + \
        [(4, 21.4, 'warm', 3.2), (4, 30.4, 'warm', 3.2), (8.5, 30.3, 'violet', 3.0), (LAKE_STAIR[0] - 2, 44.4, 'warm', 3.2),
         (6.5, 37.5, 'violet', 2.4), (15.5, 37.5, 'violet', 2.4)]

    # ================================================================== tunnels: the North Cave, option A without water (62 x 40)
    c = Room(g, 'tunnels', 'North Cave', 62, 40)
    C = c.F
    fill(C, 1, 1, 60, 38, '#')
    chamfer_room(C, 4, 3, 58, 34, 'm', 9)
    fill(C, 28, 35, 33, 37, 'u')
    pillars = [(18, 12, 26, 20), (36, 10, 44, 18), (28, 21, 34, 27), (48, 12, 55, 19)]
    for x0, y0, x1, y1 in pillars: chamfer_room(C, x0, y0, x1, y1, '#', 2)
    c.t.warp('R', [(x, 38) for x in range(29, 33)], 'mine', MINE_TOP[0], MINE_TOP[1])
    c.keep_clear(27, 33, 34, 38)
    c.t.zones += [['North Cave', 4, 3, 58, 34], ['Cave mouth', 28, 35, 33, 37]]
    g.setdefault('FLOOR_EXTRAS', {})['tunnels'] = {'stairs': [(28, 35, 33, 38, 's')]}
    # four ore beds: a patch of darker ground with four veins; they refill every two days
    for (bx, by), kind in (((12, 10), 'iron_ore'), ((52, 26), 'iron_ore'), ((12, 26), 'copper_ore'), ((30, 7), 'copper_ore')):
        chamfer_room(C, bx - 3, by - 2, bx + 3, by + 2, 'o', 1)
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            nodes.append([kind, 'tunnels', bx + dx, by + dy, 2]); c.clear.add((bx + dx, by + dy))
        c.keep_clear(bx - 3, by - 2, bx + 3, by + 2)
    for fx, fy in ((8, 18), (55, 18), (22, 30), (40, 30), (20, 5.5), (40, 5.5), (33, 31), (56, 28)):
        c.near('glow_fungus', fx, fy, 'Glowing fungus', None)
        bake_floor.CAVE_LIGHTS.setdefault('tunnels', []).append((fx, fy, 'cyan', 2.8))
    # creatures, for Job's quest: they come back each morning
    for kind, (x, y) in (('bug', (24, 23)), ('bug', (38, 22)), ('bug', (33, 30)), ('bug', (52, 21)), ('bug', (30, 11)),
                         ('lizard', (8, 22)), ('lizard', (9, 15)), ('lizard', (56, 21)), ('lizard', (24, 8)), ('lizard', (43, 7))):
        assert c.free(x, y), ('creature on a blocked tile', kind, x, y)
        enemies.append([kind, 'tunnels', x, y])
        c.keep_clear(x - 1, y - 1, x + 1, y + 1)
    for x, y in pick_spots(c, (6, 5, 56, 32), 14, 31, gap=3.5):          # rocks to cut for stone
        nodes.append(['stone', 'tunnels', x, y])

    lk = build_lake(g)
    for room in (m, c, lk):
        g.setdefault('AREA_PROPS', {})[room.key] = room.props
        g.setdefault('AREA_ROOF_PROPS', {})[room.key] = []
        g.setdefault('AREA_LIGHTS', {})[room.key] = []
        g.setdefault('EXTRA_THINGS', []).extend(room.things)
    g.setdefault('LUNAR_EXTRA', {}).update({'The Mine': 'mine', 'North Cave': 'tunnels', 'Underground Lake': 'lake'})
    g['MAP_PARENT']['lake'] = ['mine', MINE_FROM_LAKE[0], MINE_FROM_LAKE[1]]   # shown on the station map at the flooded stair
    import bake_floor
    bake_floor.AREA_FLOORS['mine'] = {'m': ('mine_rock', None), 'u': ('mine_path', None), 'k': ('mine_rock', ('7a4436', .3)),
                                      'f': ('eng_floor_concrete', ('c8a070', .12)), 'o': ('eng_floor_ore', None),
                                      'h': ('eng_floor_tech', ('8a7ab0', .2)), 'R': ('mine_path', ('6a5a4c', .35))}
    bake_floor.AREA_FLOORS['tunnels'] = {'m': ('mine_rock', ('3a3850', .2)), 'u': ('mine_path', ('3a3850', .2)),
                                         'o': ('mine_rock', ('5a4030', .35)), 'R': ('mine_path', ('6a5a4c', .35))}
    bake_floor.SECTOR_WALLS['mine'] = ('mine/roof', 'mine/wall')
    bake_floor.SECTOR_WALLS['tunnels'] = ('mine_roof', 'mine_wall')
    bake_floor.AREA_FLOORS['lake'] = {'m': ('lake/rock', None), 's': ('lake/shingle', None), 'u': ('mine_path', ('3a4a60', .3)),
                                      'p': ('east/dock', ('2a3448', .35)), 'Y': ('lake/water', None)}
    bake_floor.SECTOR_WALLS['lake'] = ('lake/roof', 'lake/wall')
    g['CAVE_NODES'], g['CAVE_ENEMIES'] = nodes, enemies
    g['MINE_SPOTS'] = {'job': (55, 22), 'zaas': (9, 40), 'vzzket': (8, 27), 'ixali': (11, 28)}
    for who, (x, y) in g['MINE_SPOTS'].items():
        assert m.free(x, y, door=True), ('resident spot blocked', who, x, y)


# ================================================================== the underground lake (Zachary, 22 Nov)
def blob(cx, cy, rx, ry, n, wobble, seed, lo=(2, 2), hi=(61, 43)):
    """An irregular closed outline round (cx, cy): an ellipse with a few slow bumps, clamped to the map."""
    import math
    r = random.Random(seed)
    ph = [r.uniform(0, 6.3) for _ in range(3)]
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + wobble * (.6 * math.sin(3 * a + ph[0]) + .3 * math.sin(5 * a + ph[1]) + .2 * math.sin(7 * a + ph[2]))
        pts.append((min(hi[0], max(lo[0], cx + rx * k * math.cos(a))), min(hi[1], max(lo[1], cy + ry * k * math.sin(a)))))
    return pts


def build_lake(g):
    """Under the copper bay, the old flooded galleries: a wide, still lake in a dark cavern, lit by glowing fungus
    and crystals. You come down the stair on the north side onto the shingle; a long dock runs out into the deep
    water, a short one off the west shore, and an old fishing camp sits on the rocks to the north-east. The cave
    fish live here. The stair is sealed (scripts/main.gd) until the Leviathan is dead."""
    import math
    W, H = 64, 46
    L = Room(g, 'lake', 'The Underground Lake', W, H)
    F = L.F
    fill(F, 1, 1, W - 2, H - 2, '#')
    poly(F, blob(32, 25, 28.5, 18.5, 40, .07, 5), 'm')            # the cavern
    fill(F, 29, 1, 34, 7, 'u')                                    # the stair down from the mine
    # the water and its shingle shore, on straight and 45-degree edges like every other wall and pool in the game
    lake = [(17, 19), (29, 19), (31, 17), (36, 17), (38, 19), (45, 19), (50, 24), (50, 27), (52, 29), (52, 33), (47, 38),
            (38, 38), (36, 40), (27, 40), (25, 38), (18, 38), (14, 34), (14, 30), (12, 28), (12, 24)]
    shore = [(14, 16), (28, 16), (30, 14), (37, 14), (39, 16), (47, 16), (53, 22), (53, 25), (55, 27), (55, 35), (49, 41),
             (39, 41), (37, 43), (26, 43), (24, 41), (17, 41), (11, 35), (11, 32), (9, 30), (9, 21)]
    before = [r[:] for r in F]
    poly(F, shore, 's')               # the shingle shore round the water
    poly(F, lake, 'Y')
    for y in range(H):                                            # shore and water only inside the cavern
        for x in range(W):
            if before[y][x] == '#': F[y][x] = '#'
    for x0, y0, x1, y1, c in ((42, 28, 46, 31, 1), (18, 32, 21, 34, 1)):   # rock stacks standing in the water
        chamfer_room(F, x0, y0, x1, y1, '#', c)
    fill(F, 31, 16, 32, 25, 'p')                                  # the long dock, out into the deep water
    fill(F, 9, 29, 16, 30, 'p')                                   # the short dock off the west shore
    L.t.warp('R', [(x, 1) for x in range(30, 34)], 'mine', MINE_FROM_LAKE[0], MINE_FROM_LAKE[1])
    L.keep_clear(28, 1, 35, 9); L.keep_clear(30, 15, 33, 26); L.keep_clear(8, 28, 17, 31)
    L.t.zones += [['The stair', 29, 1, 34, 7], ['Old fishing camp', 42, 8, 56, 17], ['The long dock', 30, 15, 33, 26],
                  ['West dock', 8, 28, 17, 31], ['The Underground Lake', 1, 1, W - 2, H - 2]]
    P, N = L.prop, L.near
    # the foot of the stair: two work lights left by the old crews, a sign
    N('work_light', 28.5, 7, 'Work light', None); N('work_light', 35.5, 7, 'Work light', None)
    N('signpost', 37, 9.5, 'Signpost: long dock, west dock, fishing camp', 'look', 'Read')
    # the old fishing camp on the rocks: a stove, a bench, crates and barrels, a rack of rods
    N('brazier', 48, 13, 'Camp stove', 'look', 'Look'); N('bench_s', 45.5, 12.5, 'Camp bench [S]', 'seat', 'Sit')
    N('barrel_stack', 52.5, 11, 'Bait barrels', None); N('cargo', 51, 15, 'Fishing crates', 'look', 'Look')
    N('storage_shelf', 43.5, 10, 'Rod rack', 'look', 'Look'); N('work_light', 55, 13.5, 'Work light', None)
    # glowing fungus and crystals round the walls, stalagmites, a few boulders on the shore
    for fx, fy in ((9, 18), (6, 24), (14, 11), (22, 8), (41, 7), (57, 20), (58, 29), (52, 38), (40, 42), (22, 41), (8, 36), (12, 40)):
        N('glow_fungus', fx, fy, 'Glowing fungus', None)
    for fx, fy in ((18, 9), (58, 24), (27, 42), (6, 31)): N('crystal_cluster', fx, fy, 'Glow crystals', 'inspect', 'Inspect')
    for fx, fy in ((47, 41), (15, 14)): N('crystal_column', fx, fy, 'Crystal column', None)
    for fx, fy in ((11, 21), (24, 11), (54, 33), (36, 43), (17, 38)): N('stalagmite', fx, fy, 'Stalagmite', None)
    for fx, fy in ((5, 27), (55, 18)): N('boulder', fx, fy, 'Boulder', None)
    # where to fish: the end of each dock and three spots on the shore
    L.thing('look', 'Fishing spot: deep water', 'Look', 31.5, 25, 36)
    L.thing('look', 'Fishing spot: west dock', 'Look', 16, 29.5, 36)
    for fx, fy in ((53.5, 31), (32, 41.5), (11, 22.5)):
        L.thing('look', 'Fishing spot: the shallows', 'Look', fx, fy, 40)
    L.thing('look', 'The Underground Lake', 'Look', 31.5, 13, 50)
    L.thing('look', 'Old fishing camp', 'Look', 48, 15, 40)
    g.setdefault('FLOOR_EXTRAS', {})['lake'] = {'regions': [('s', [list(p) for p in shore], 'sm')], 'holes': [[list(p) for p in lake]],
                                                'hole_char': 'Y', 'floor_char': 's', 'lake': True, 'stairs': [(29, 1, 34, 7, 'n')]}
    import bake_floor
    bake_floor.CAVE_LIGHTS['lake'] = [(28.5, 7.5, 'warm', 3.5), (35.5, 7.5, 'warm', 3.5), (55, 14, 'warm', 3.5), (48, 13.5, 'violet', 3.6)] + \
        [(x, y, 'cyan', 2.6) for x, y in ((9, 18), (6, 24), (14, 11), (22, 8), (41, 7), (57, 20), (58, 29), (52, 38), (40, 42), (22, 41), (8, 36), (12, 40))] + \
        [(x, y, 'violet', 3.2) for x, y in ((18, 9), (58, 24), (27, 42), (6, 31), (47, 41), (15, 14))]
    assert L.free(*LAKE_LANDING, door=True)
    return L
