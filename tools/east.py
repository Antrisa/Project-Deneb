"""The East Complex, the station's residential quarter, rebuilt in the promenade style (Zachary, 17 Nov, option B3).

A ring street round a little park with a pavilion in the middle. Built into the ring itself: the mess hall
greenhouse (north: crop beds, an orchard corner and Evarra's herbs) and the fitness centre (south: a gym round a
low-gravity court and running track), so you pass them on every lap. Twelve homes in four little courts at the end of
short diagonal lanes (the ring itself stays a clean circle): in each court a single apartment, a couple's
home and a family house, each its own map, mirrored and refloored from home to home. West, on the walkway in from the Main Level: a good-sized laundry. East: the air reclamation
plant, with a row of broken spacesuit lockers, and the east airlock beyond it (sealed until you have a suit). No schoolroom: the library and the
community room cover that.
Drawn in the promenade style; walls faceted by tools/bake_floor.py."""
import math
import survey
import engineering, spaceport          # their prop sizes
from survey import Room, SIZES
from engineering import chamfer_room
from spaceport import disc, fill, band

WALKABLE = '.shafkoteuj'
SIZES.update({
    'fruit_tree': (2, 3, 1), 'park_tree': (2, 3, 1), 'treadmill': (2, 2, 1), 'weight_bench': (3, 2, 1), 'punching_bag': (1, 2, 1),
    'court_hoop': (2, 3, 1), 'washer': (2, 2, 1), 'laundry_basket': (1, 1, 1), 'scoreboard': (2, 3, 1), 'flowers': (4, 2, 2),
    'bird_bath': (1, 2, 1), 'bench_e': (1, 3, 2), 'bench_w': (1, 3, 2), 'suit_locker_broken': (2, 3, 1), 'shower': (2, 3, 1), 'toilet': (1, 2, 1), 'bath_sink': (1, 2, 1), 'bed_double': (3, 3, 2), 'bunk_bed': (2, 3, 2),
})
CX, CY = 56, 46
HOME_ANGLES = [20, 40, 140, 160, 200, 220, 320, 340]


def build(g):
    survey.WALKABLE = WALKABLE
    e = Room(g, 'east', 'East Complex', 120, 90)
    F, O = e.F, e.obj
    fill(F, 1, 1, 118, 88, '#')
    d = lambda x, y, cx=CX, cy=CY: math.hypot(x + .5 - cx, y + .5 - cy)
    # the greenhouse (north) and the fitness centre (south) are built into the ring, a wall's width outside it
    for y in range(90):
        for x in range(120):
            if math.hypot(x + .5 - CX, y + .5 - (CY - 26)) <= 14 and d(x, y) > 23.2:
                F[y][x] = 'a'
    for y in range(CY + 16, CY + 41):
        for x in range(CX - 17, CX + 18):
            if min(x - (CX - 17), CX + 17 - x) + min(y - (CY + 16), CY + 40 - y) >= 6 and d(x, y) > 23.2:
                F[y][x] = 'f'
    for y in range(CY + 25, CY + 38):
        for x in range(CX - 11, CX + 12):
            if min(x - (CX - 11), CX + 11 - x) + min(y - (CY + 25), CY + 37 - y) >= 3:
                F[y][x] = 'k'                                        # the low-gravity court
    disc(F, CX, CY, 22, '.')                                         # the ring street
    disc(F, CX, CY, 12, 's')                                         # the park
    chamfer_room(F, CX - 4, CY - 3, CX + 4, CY + 3, 'h', 2)          # the pavilion
    for x in (CX - 1, CX, CX + 1):
        for y in range(CY - 24, CY - 21): F[y][x] = 'a' if F[y][x] == '#' else F[y][x]
        for y in range(CY + 22, CY + 25): F[y][x] = 'f' if F[y][x] == '#' else F[y][x]
    # homes (Zachary's sketch): the ring stays a clean circle. In the four diagonal quarters, between the
    # walkways, the greenhouse and the fitness centre, a curved residence block hugs the outside of the ring
    # (its roof tinted, so you see it bulge out); each front door sits in a small entrance porch that bulges a
    # little into the ring street. North-west and south-east: two single apartments each. North-east and
    # south-west: two family houses each. Each door leads to the home's own map (make_home, below).
    homes = []
    n = 0
    # doors sit within about 33 degrees of east or west, where the ring wall runs nearly upright, so the
    # porches meet it cleanly (mirror pairs: 147/162 and 18/33 below, 198/213 and 327/342 above)
    for (lo, hi), kind, doors in (((190, 234), 'single', (198, 213)), ((10, 41), 'single', (18, 33)),
                                  ((306, 350), 'family', (327, 342)), ((139, 170), 'family', (147, 162))):
        for ang in doors:
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            if abs(ca) >= abs(sa): facing = 'W' if ca > 0 else 'E'
            else: facing = 'N' if sa > 0 else 'S'
            step = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[facing]
            perp = (0, 1) if facing in 'EW' else (1, 0)
            bx, by = int(round(CX - .5 + 20.4 * ca)), int(round(CY - .5 + 20.4 * sa))       # the entrance porch: a small block in the street, its sides at 45 degrees
            for k in (0, 1, 2):                                      # widening by a tile each side per row: 45-degree sides
                for j in range(-1 - k, 2 + k):
                    x, y = bx - step[0] * k + perp[0] * j, by - step[1] * k + perp[1] * j
                    if math.hypot(x + .5 - CX, y + .5 - CY) <= 23.5: F[y][x] = '#'
            door = (bx, by); F[by][bx] = '.'                           # the door, in the porch's face, facing the park
            n += 1
            homes.append((n, door, facing, kind))
    RES_BLOCKS = [205.5, 25.5, 334.5, 154.5]                             # each residence: a round block straddling the ring
    import bake_floor
    def east_roofs(px, py):
        import numpy as np
        r = np.hypot(px - CX, py - CY)
        z = np.zeros(px.shape, dtype=np.int64)
        for i, mid in enumerate(RES_BLOCKS):
            bx_, by_ = CX + 24 * math.cos(math.radians(mid)), CY + 24 * math.sin(math.radians(mid))
            z = np.where((np.hypot(px - bx_, py - by_) <= 9.5) & (r >= 22.3), 1 + i % 3, z)
        return z
    # bake_floor.ROOF_ZONE_FN['east'] = east_roofs   # off: the outlines read as odd arcs across the roof (Zachary, 17 Nov)
    # west: the walkway in from the Main Level, and the laundry beside it
    fill(F, 1, 43, 34, 49, 'u')
    chamfer_room(F, 3, 26, 22, 41, 't', 3)                          # the laundry: 19 x 15 tiles
    for x in (11, 12, 13): F[42][x] = 't'
    e.t.warp('A', [(1, y) for y in range(43, 50)], 'main', 0, 0)    # tools/concourse.py sets the landing
    # east: the air reclamation plant and the airlock
    fill(F, 78, 43, 90, 49, 'u')
    chamfer_room(F, 91, 28, 116, 62, 'e', 3)
    fill(F, 99, 63, 101, 69, 'u')
    chamfer_room(F, 94, 70, 106, 80, 'u', 2)
    e.t.zones += [['Mess hall greenhouse', 42, 6, 70, 22], ['Fitness centre', 39, 62, 73, 86], ['Little park', 44, 34, 68, 58],
                  ['Laundry', 3, 26, 22, 41], ['Air reclamation plant', 91, 28, 116, 62], ['East airlock', 94, 70, 106, 80],
                  ['Walkway to the Main Level', 1, 43, 34, 49], ['Ring street', 34, 24, 78, 68]]
    # keep the ring's loop, the doorways and the walkways clear
    e.keep_clear(1, 44, 34, 48); e.keep_clear(78, 44, 91, 48); e.keep_clear(10, 40, 14, 44); e.keep_clear(98, 62, 102, 71)
    e.keep_clear(CX - 2, CY - 26, CX + 2, CY - 20); e.keep_clear(CX - 2, CY + 20, CX + 2, CY + 27)
    for y in range(90):
        for x in range(120):
            if 15.5 <= d(x, y) <= 20.5: e.clear.add((x, y))
    P, N = e.prop, e.near
    # the greenhouse: Merrow's crop beds east, the orchard and Evarra's herbs west
    for fy in (12.5, 16.5):
        for fx in (60, 65): N('hydroponics', fx, fy, 'Mess hall crop beds', 'look', 'Look')
    N('planter_long', 50, 18.5, 'Herb beds', 'look', 'Look'); N('planter_long', 50, 14.5, 'Herb beds', None)
    for fx, fy in ((46, 12), (50, 9.5), (45, 16.5)): N('fruit_tree', fx, fy, 'Fruit tree', 'inspect', 'Inspect')
    N('seed_rack', 63, 8.5, 'Seed rack', None); N('garden_tools', 68, 16.5, 'Garden tools', None); N('water_tank', 59, 20, 'Water tank', None)
    # the park and its pavilion
    for a in range(0, 360, 45):
        N('park_tree', CX + 9.5 * math.cos(math.radians(a + 22)), CY + 9.5 * math.sin(math.radians(a + 22)), 'Tree', None)
    N('bench_s', CX, CY - 6.5, 'Pavilion bench [S]', 'seat', 'Sit'); N('bench_n', CX, CY + 7.5, 'Pavilion bench [N]', 'seat', 'Sit')
    N('flowers', CX - 7, CY - 1, 'Flower bed', 'inspect', 'Inspect'); N('bird_bath', CX + 8, CY + 1.5, 'Bird bath', None)
    for a in (45, 135, 225, 315):
        N('lamp_post', CX + 13 * math.cos(math.radians(a)), CY + 13 * math.sin(math.radians(a)), 'Lamp', None)
    e.thing('look', 'Pavilion', 'Look', CX, CY, 40)
    # the fitness centre: gym round the court
    N('court_hoop', CX - 9, CY + 31.5, 'Hoop', None); N('court_hoop', CX + 10, CY + 31.5, 'Hoop', None)
    e.thing('look', 'Low-gravity court', 'Look', CX, CY + 31, 50)
    for fx in (CX - 13, CX - 10): N('treadmill', fx, CY + 21.5, 'Treadmill', 'look', 'Look')
    N('weight_bench', CX + 11.5, CY + 21.5, 'Weight bench', 'look', 'Look'); N('gym_rack', CX + 12, CY + 39, 'Weights rack', None)
    N('punching_bag', CX - 14.5, CY + 33, 'Punching bag', 'look', 'Look'); N('locker', CX - 12, CY + 39.5, 'Gym lockers', None)
    N('scoreboard', CX + 15, CY + 28, 'Scoreboard', None); N('bench_s', CX - 4, CY + 39.5, 'Bench', 'seat', 'Sit')
    # the laundry: a wall of washers, folding tables, baskets, a bench
    for fx in (6, 9, 12, 15, 18): P('washer', fx - 1, 27, 'Washing machine', 'look' if fx == 12 else None, 'Look')
    for fx in (7, 18): N('table', fx, 34.5, 'Folding table', None)
    for fx, fy in ((11, 33), (14, 33), (5, 38)): N('laundry_basket', fx, fy, 'Laundry basket', None)
    N('bench_n', 17, 39.5, 'Bench [N]', 'seat', 'Sit'); N('plants', 20.5, 37, 'Plant', None)
    # the air reclamation plant
    for fx in (96, 102, 108, 113):
        for fy in (34, 42, 50): N('air_scrubber', fx, fy, 'Air scrubber', 'look' if (fx, fy) == (102, 42) else None, 'Look')
    N('console', 97, 59, 'Plant console', 'look', 'Look'); N('pipe_rack', 108, 58.5, 'Pipe manifold', None); N('breaker_panel', 114, 58, 'Breaker panel')
    N('pump', 94, 31, 'Circulation pump', None)
    for fx in (98, 101, 104, 107, 110): N('suit_locker_broken', fx, 30.5, 'Spacesuit locker (broken)', 'look' if fx == 104 else None, 'Look')
    # the airlock
    P('lab_door', 94, 73, 'Outer airlock door', 'look', 'Look', door=True); N('locker', 104, 73, 'Suit lockers', None); N('cargo', 103, 78.5, 'Crates', None)
    # the homes' own maps (make_home, below)
    import bake_floor
    from survey import door_pair
    entries, warps = [], {'east': e.t.warps}
    LIVING = [None, ('c08a50', .15), ('5a3a24', .25), ('a0a0a0', .25)]
    BEDROOM = ['sp_carpet', 'sp_carpet_red', 'sp_parquet', 'sp_carpet']
    for n, door, facing, kind in homes:
        key = 'home%d' % n
        hm, mirror = make_home(g, key, 'Home %d' % n, kind, n % 2 == 0)
        bake_floor.AREA_FLOORS[key] = {'o': ('sp_parquet', LIVING[n % 4]), 'k': ('sp_kitchen', None), 'h': (BEDROOM[n % 4], None),
                                       'j': (BEDROOM[(n + 1) % 4], ('e0c080', .1)), 't': ('ea_tile', None)}
        hm_door = hm.door
        warps[key] = hm.t.warps
        door_pair(entries, warps, 'east', door, facing, key, hm_door, 'N', 'Home %d' % n, 'East Complex')
        step = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[facing]
        g['MAP_PARENT'][key] = ['east', door[0] + step[0], door[1] + step[1]]
        g.setdefault('AREA_PROPS', {})[key] = hm.props
        g.setdefault('AREA_ROOF_PROPS', {})[key] = []
        g.setdefault('AREA_LIGHTS', {})[key] = []
        g.setdefault('EXTRA_THINGS', []).extend(hm.things)
        g.setdefault('LUNAR_EXTRA', {})['Home %d' % n] = key
    g['EAST_ENTRANCES'] = entries
    g.setdefault('AREA_PROPS', {})['east'] = e.props
    g.setdefault('AREA_ROOF_PROPS', {})['east'] = []
    g.setdefault('AREA_LIGHTS', {})['east'] = []
    g.setdefault('EXTRA_THINGS', []).extend(e.things)


def make_home(g, key, title, kind, mirror):
    """One home's own map. single: living room with a kitchenette corner, bedroom, bathroom. couple: bigger,
    a double bed and a small study. family: kitchen and dining, living room, a main bedroom, a children's room
    and a bathroom. Even-numbered homes are mirrored, and the floors change from home to home."""
    W, Hh = {'single': (30, 24), 'couple': (34, 26), 'family': (42, 30)}[kind]
    hm = Room(g, key, title, W, Hh)
    H = hm.F
    fill(H, 1, 1, W - 2, Hh - 2, '#')
    X = (lambda x: W - 1 - x) if mirror else (lambda x: x)
    FX = (lambda fx: W - fx) if mirror else (lambda fx: fx)
    def room(x0, y0, x1, y1, ch, k=0):   # square rooms: chamfers on one-tile walls between rooms left stray roof bits
        a, b = sorted((X(x0), X(x1)))
        chamfer_room(H, a, y0, b, y1, ch, k)
    def tile(x, y, ch): H[y][X(x)] = ch
    def put(name, fx, fy, t, kd=None, hint='Look'): return hm.near(name, FX(fx), fy, t, kd, hint)
    if kind == 'single':
        room(3, 3, 17, 19, 'o'); room(19, 3, 26, 12, 'h'); room(19, 14, 26, 19, 't', 1)
        for y in range(3, 8):
            for x in range(3, 10):
                if H[y][X(x)] == 'o': tile(x, y, 'k')
        for y in (10, 11, 16, 17): tile(18, y, 'o')
        door = (X(10), 20); tile(10, 20, 'o')
        put('kitchenette', 5.5, 5.5, 'Kitchenette', 'inspect', 'Inspect'); put('fridge', 9, 5.5, 'Fridge')
        put('table', 6.5, 10.5, 'Dining table', 'seat', 'Sit'); put('sofa', 13, 7.5, 'Sofa', 'seat', 'Sit')
        put('cafe_table', 13, 11, 'Coffee table'); put('armchair', 15.5, 14.5, 'Armchair', 'seat', 'Sit')
        put('books', 5, 17, 'Bookshelf'); put('plants', 14.5, 18.5, 'Plant')
        put('bed', 21, 6.5, 'Bed'); put('wardrobe', 25, 5.5, 'Wardrobe'); put('footlocker', 21, 10.5, 'Chest')
        put('shower', 21, 17.5, 'Shower'); put('toilet', 24, 16.5, 'Toilet'); put('bath_sink', 25.5, 18.5, 'Washbasin')
        hm.keep_clear(X(8) if not mirror else X(12), 16, X(12) if not mirror else X(8), 20)
        zones = [['Living room', 3, 3, 17, 19], ['Bedroom', 19, 3, 26, 12], ['Bathroom', 19, 14, 26, 19]]
    elif kind == 'couple':
        room(3, 3, 20, 21, 'o'); room(22, 3, 30, 13, 'h'); room(22, 15, 30, 21, 't', 1)
        for y in range(3, 10):                                       # kitchenette and study corners, inside the living room
            for x in range(3, 21):
                if H[y][X(x)] == 'o' and (x <= 9 or (x >= 12 and y <= 8)): tile(x, y, 'k' if x <= 9 else 'j')
        for y in (9, 10, 11, 17, 18): tile(21, y, 'o')
        door = (X(11), 22); tile(11, 22, 'o')
        put('kitchenette', 6, 6, 'Kitchenette', 'inspect', 'Inspect'); put('fridge', 9.5, 5.5, 'Fridge')
        put('table', 7, 12.5, 'Dining table', 'seat', 'Sit'); put('curator_desk', 16.5, 5.5, 'Desk'); put('books', 13.5, 5.5, 'Bookshelf')
        put('sofa', 14.5, 13, 'Sofa', 'seat', 'Sit'); put('cafe_table', 14.5, 16.5, 'Coffee table'); put('armchair', 18.5, 16, 'Armchair', 'seat', 'Sit')
        put('plants', 5, 20, 'Plant'); put('tree_tub', 18.5, 20, 'Potted tree')
        put('bed_double', 25.5, 7.5, 'Double bed'); put('wardrobe', 29.5, 5.5, 'Wardrobe'); put('footlocker', 28.5, 12, 'Chest')
        put('shower', 24, 19.5, 'Shower'); put('toilet', 27, 18.5, 'Toilet'); put('bath_sink', 29.5, 20.5, 'Washbasin')
        zones = [['Living room', 3, 3, 20, 21], ['Bedroom', 22, 3, 30, 13], ['Bathroom', 22, 15, 30, 21]]
    else:
        room(3, 3, 22, 14, 'k'); room(3, 16, 22, 26, 'o'); room(24, 3, 38, 12, 'h'); room(24, 14, 38, 20, 'j'); room(24, 22, 38, 26, 't', 1)
        for x in (11, 12, 13): tile(x, 15, 'o')
        for y in (7, 8, 17, 18, 24): tile(23, y, 'o' if y > 14 else 'k')
        door = (X(13), 27); tile(13, 27, 'o')
        put('kitchenette', 6, 5.5, 'Kitchenette', 'inspect', 'Inspect'); put('kitchenette', 11, 5.5, 'Stove'); put('fridge', 15, 5.5, 'Fridge')
        put('table', 9, 10.5, 'Family table', 'seat', 'Sit'); put('table', 15, 10.5, 'Family table', 'seat', 'Sit'); put('plants', 20.5, 6, 'Plant')
        put('sofa', 8, 19.5, 'Sofa', 'seat', 'Sit'); put('sofa', 16, 19.5, 'Sofa', 'seat', 'Sit'); put('cafe_table', 12, 22.5, 'Coffee table')
        put('books', 5, 25, 'Bookshelf'); put('tree_tub', 20.5, 25, 'Potted tree')
        put('bed_double', 28.5, 7, "Parents' bed"); put('wardrobe', 36.5, 5.5, 'Wardrobe')
        put('bunk_bed', 27, 18, "Children's bunk"); put('bunk_bed', 31, 18, "Children's bunk"); put('footlocker', 36, 19, 'Toy chest')
        put('shower', 26, 25, 'Shower'); put('toilet', 30, 24.5, 'Toilet'); put('bath_sink', 33, 24.5, 'Washbasin')
        zones = [['Kitchen', 3, 3, 22, 14], ['Living room', 3, 16, 22, 26], ['Bedroom', 24, 3, 38, 12], ["Children's room", 24, 14, 38, 20], ['Bathroom', 24, 22, 38, 26]]
    hm.thing('look', 'Empty home', 'Look', door[0], door[1] - 4, 50)
    hm.t.zones += [[t, min(X(a), X(c)), b, max(X(a), X(c)), d] for t, a, b, c, d in zones]
    hm.door = door
    return hm, mirror
