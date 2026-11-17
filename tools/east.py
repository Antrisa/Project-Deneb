"""The East Complex, the station's residential quarter, rebuilt in the promenade style (Zachary, 17 Nov, option B3).

A ring street round a little park with a pavilion in the middle. Built into the ring itself: the mess hall
greenhouse (north: crop beds, an orchard corner and Evarra's herbs) and the fitness centre (south: a gym round a
low-gravity court and running track), so you pass them on every lap. Eight homes round the ring (a small nook in
its outer wall for each front door), each with its own map (home1..home8): an apartment with a living room
and kitchenette, a bedroom and a bathroom. West, on the walkway in from the Main Level: a good-sized laundry. East: the air reclamation
plant, with a row of broken spacesuit lockers, and the east airlock beyond it (sealed until you have a suit). No schoolroom: the library and the
community room cover that.
Drawn in the promenade style; walls faceted by tools/bake_floor.py."""
import math
import survey
import engineering, spaceport          # their prop sizes
from survey import Room, SIZES
from engineering import chamfer_room
from spaceport import disc, fill

WALKABLE = '.shafkoteu'
SIZES.update({
    'fruit_tree': (2, 3, 1), 'park_tree': (2, 3, 1), 'treadmill': (2, 2, 1), 'weight_bench': (3, 2, 1), 'punching_bag': (1, 2, 1),
    'court_hoop': (2, 3, 1), 'washer': (2, 2, 1), 'laundry_basket': (1, 1, 1), 'scoreboard': (2, 3, 1), 'flowers': (4, 2, 2),
    'bird_bath': (1, 2, 1), 'bench_e': (1, 3, 2), 'bench_w': (1, 3, 2), 'suit_locker_broken': (2, 3, 1), 'shower': (2, 3, 1), 'toilet': (1, 2, 1), 'bath_sink': (1, 2, 1),
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
    # eight homes round the ring: a plain circle with a small square nook in its outer wall for each front
    # door. Each door leads to the home's own map, an apartment.
    homes = []
    for i, a in enumerate(HOME_ANGLES):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        if abs(ca) >= abs(sa): facing = 'W' if ca > 0 else 'E'
        else: facing = 'N' if sa > 0 else 'S'
        step = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[facing]
        perp = (0, 1) if facing in 'EW' else (1, 0)
        dx_, dy_ = int(CX + 24.4 * ca), int(CY + 24.4 * sa)
        F[dy_][dx_] = '.'
        for k in range(1, 5):                                        # the nook: 3 tiles wide, back to the street
            for j in (-1, 0, 1):
                x, y = dx_ + step[0] * k + perp[0] * j, dy_ + step[1] * k + perp[1] * j
                if F[y][x] == '#': F[y][x] = '.'
        homes.append((i + 1, (dx_, dy_), facing, True))
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
    # the homes' own maps: a round room each, a bed and a few things waiting for someone
    import bake_floor
    from survey import door_pair
    entries, warps = [], {'east': e.t.warps}
    for n, door, facing, out in homes:
        key = 'home%d' % n
        hm = Room(g, key, 'Home %d' % n, 30, 24)
        H = hm.F
        fill(H, 1, 1, 28, 22, '#')
        chamfer_room(H, 3, 3, 17, 19, 'o', 2)                       # living room
        for y in range(3, 8):                                        # its kitchenette corner
            for x in range(3, 10):
                if H[y][x] == 'o': H[y][x] = 'k'
        chamfer_room(H, 19, 3, 26, 12, 'h', 2)                      # bedroom
        chamfer_room(H, 19, 14, 26, 19, 't', 1)                     # bathroom
        H[10][18] = H[11][18] = 'o'; H[16][18] = H[17][18] = 'o'
        hm_door = (10, 20); H[20][10] = 'o'
        hm.keep_clear(8, 16, 12, 20); hm.keep_clear(16, 9, 20, 12); hm.keep_clear(16, 15, 20, 18)
        P_, N_ = hm.prop, hm.near
        N_('kitchenette', 5.5, 5.5, 'Kitchenette', 'inspect', 'Inspect'); N_('fridge', 9, 5.5, 'Fridge', None)
        N_('table', 6.5, 10.5, 'Dining table', 'seat', 'Sit')
        N_('sofa', 13, 7.5, 'Sofa', 'seat', 'Sit'); N_('cafe_table', 13, 11, 'Coffee table', None); N_('armchair', 15.5, 14.5, 'Armchair', 'seat', 'Sit')
        N_('books', 5, 17, 'Bookshelf', None); N_('plants', 14.5, 18.5, 'Plant', None)
        N_('bed', 21, 6.5, 'Bed', None); N_('wardrobe', 25, 5.5, 'Wardrobe', None); N_('footlocker', 21, 10.5, 'Chest', None)
        N_('plants', 25.5, 11, 'Plant', None)
        N_('shower', 21, 17.5, 'Shower', None); N_('toilet', 24, 16.5, 'Toilet', None); N_('bath_sink', 25.5, 18.5, 'Washbasin', None)
        hm.thing('look', 'Empty home', 'Look', 10, 12, 50)
        hm.t.zones += [['Living room', 3, 3, 17, 19], ['Bedroom', 19, 3, 26, 12], ['Bathroom', 19, 14, 26, 19]]
        warps[key] = hm.t.warps
        door_pair(entries, warps, 'east', door, facing, key, hm_door, 'N', 'Home %d' % n, 'East Complex')
        step = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}[facing]
        g['MAP_PARENT'][key] = ['east', door[0] + step[0], door[1] + step[1]]
        g.setdefault('AREA_PROPS', {})[key] = hm.props
        g.setdefault('AREA_ROOF_PROPS', {})[key] = []
        g.setdefault('AREA_LIGHTS', {})[key] = []
        g.setdefault('EXTRA_THINGS', []).extend(hm.things)
        g.setdefault('LUNAR_EXTRA', {})['Home %d' % n] = key
        bake_floor.AREA_FLOORS[key] = {'o': ('sp_parquet', None), 'k': ('sp_kitchen', None), 'h': ('sp_carpet', None), 't': ('ea_tile', None)}
    g['EAST_ENTRANCES'] = entries
    g.setdefault('AREA_PROPS', {})['east'] = e.props
    g.setdefault('AREA_ROOF_PROPS', {})['east'] = []
    g.setdefault('AREA_LIGHTS', {})['east'] = []
    g.setdefault('EXTRA_THINGS', []).extend(e.things)
