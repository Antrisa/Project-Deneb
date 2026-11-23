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

WALKABLE = '.shafkoteujp'
SIZES.update({
    'fruit_tree': (2, 3, 1), 'park_tree': (2, 3, 1), 'treadmill': (2, 2, 1), 'weight_bench': (3, 2, 1), 'punching_bag': (1, 2, 1),
    'court_hoop': (2, 3, 1), 'washer': (2, 2, 1), 'laundry_basket': (1, 1, 1), 'scoreboard': (2, 3, 1), 'flowers': (4, 2, 2),
    'bird_bath': (1, 2, 1), 'bench_e': (1, 3, 2), 'bench_w': (1, 3, 2), 'suit_locker_broken': (2, 3, 1), 'shower': (2, 3, 1), 'toilet': (1, 2, 1), 'bath_sink': (1, 2, 1), 'bed_double': (3, 3, 2), 'bunk_bed': (2, 3, 2),
    'textiles': (3, 2, 1), 'clothes': (3, 2, 1),
    'fern': (1, 1, 1), 'potted_plant': (1, 2, 1), 'steam_vent': (2, 2, 1), 'signpost': (1, 2, 1), 'boulder': (2, 2, 1), 'cafe_table': (2, 2, 1),
})
# The garden dome (Zachary, 22 Nov, mock-up D3): no farming. A stream from a spring in the north links three
# fishing ponds; stone walking paths loop through the woods to the west; hot springs and the bath house in the
# south-east. The air reclamation plant and the airlock moved south of the walkway to make room.
DX, DY, DR = 152, 46, 40
def stream_x(y): return 158 + 7 * math.sin(y / 9)
CX, CY = 56, 46
HOME_ANGLES = [20, 40, 140, 160, 200, 220, 320, 340]
# Who lives in which home (Zachary, 20 Nov). Artie, Stu and Ana arrive later in the story; their homes are
# ready for them. Home 4 and homes 6 to 8 are still empty.
EAST_RESIDENTS = {1: 'Artie', 2: 'Stu', 3: 'Ana', 4: 'Freya', 5: 'Tikka|Sesska', 6: 'Job', 7: 'Zaas'}
# Freya and Job moved out of Residences B (Zachary, 20 Nov). Job's home is a family house outside, but inside it
# has the medium layout: a big living room with a home gym where the study would be. Zaas moved out too, to
# Home 7 (same idea: the medium layout, with an ocean corner where the study would be).
EAST_KIND = {6: 'couple', 7: 'couple'}
# things of their own, placed in the living room and the bedroom: (prop, x, y, title)
EAST_THINGS = {
    'Artie': [('star_chart', 16.5, 4.5, "Artie's knot board"), ('books', 25, 10, "Artie's library books")],
    'Stu': [('cargo', 16.5, 4.5, 'The hydroponics crate'), ('luggage_cart', 25, 10, "Stu's luggage cart")],
    'Ana': [('star_chart', 16.5, 4.5, "Ana's flight charts"), ('console', 25, 10, "Ana's nav console")],
    'Freya': [('workbench', 16, 4.5, "Freya's bench"), ('tool_cart', 16.5, 14.5, "Freya's tool cart"), ('star_chart', 25, 10, 'Ship schematics')],
}


def build(g):
    survey.WALKABLE = WALKABLE
    e = Room(g, 'east', 'East Complex', 198, 90)
    F, O = e.F, e.obj
    fill(F, 1, 1, 196, 88, '#')
    d = lambda x, y, cx=CX, cy=CY: math.hypot(x + .5 - cx, y + .5 - cy)
    # the greenhouse (north) and the fitness centre (south) are built into the ring, a wall's width outside it
    for y in range(90):
        for x in range(198):
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
    # east: the walkway out to the garden dome
    fill(F, 78, 43, 113, 49, 'u')
    garden_dome(F)
    # south of the walkway: the air reclamation plant (moved here, 22 Nov) and the airlock below it
    fill(F, 92, 50, 96, 57, 'u')
    chamfer_room(F, 82, 58, 108, 78, 'e', 3)
    fill(F, 93, 79, 95, 81, 'u')
    chamfer_room(F, 88, 82, 100, 87, 'u', 2)
    e.t.zones += [['Mess hall greenhouse', 42, 6, 70, 22], ['Fitness centre', 39, 62, 73, 86], ['Little park', 44, 34, 68, 58],
                  ['Laundry', 3, 26, 22, 41], ['Air reclamation plant', 82, 58, 108, 78], ['East airlock', 88, 82, 100, 87],
                  ['Walkway to the Main Level', 1, 43, 34, 49], ['Ring street', 34, 24, 78, 68],
                  ['Hot springs', 160, 54, 190, 80], ['Bath house doors', 186, 44, 192, 66], ['Fishing ponds', 140, 10, 176, 76], ['Woods', 113, 10, 140, 82],
                  ['Garden dome', 112, 6, 192, 86]]
    # keep the ring's loop, the doorways and the walkways clear
    e.keep_clear(1, 44, 34, 48); e.keep_clear(78, 44, 113, 48); e.keep_clear(10, 40, 14, 44); e.keep_clear(92, 49, 96, 59); e.keep_clear(93, 77, 95, 83)
    e.keep_clear(CX - 2, CY - 26, CX + 2, CY - 20); e.keep_clear(CX - 2, CY + 20, CX + 2, CY + 27)
    e.keep_clear(113, 44, 191, 48); e.keep_clear(136, 10, 139, 82); e.keep_clear(183, 62, 186, 66)
    for y in range(90):
        for x in range(198):
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
    # the air reclamation plant (moved south of the walkway, 22 Nov)
    for fx in (87, 93, 99, 104):
        for fy in (64, 71): N('air_scrubber', fx, fy, 'Air scrubber', 'look' if (fx, fy) == (93, 64) else None, 'Look')
    N('console', 86, 76, 'Plant console', 'look', 'Look'); N('pipe_rack', 100, 76.5, 'Pipe manifold', None); N('breaker_panel', 106, 76, 'Breaker panel')
    N('pump', 85, 60, 'Circulation pump', None)
    for fx in (98, 101, 104): N('suit_locker_broken', fx, 60.5, 'Spacesuit locker (broken)', 'look' if fx == 101 else None, 'Look')
    # the airlock
    P('lab_door', 89, 84, 'Outer airlock door', 'look', 'Look', door=True); N('locker', 98, 85, 'Suit lockers', None)
    dress_dome(e, N, P)
    # the homes' own maps (make_home, below)
    import bake_floor
    from survey import door_pair
    entries, warps = [], {'east': e.t.warps}
    for n, door, facing, kind in homes:
        key = 'home%d' % n
        kind = EAST_KIND.get(n, kind)
        hm, mirror = make_home(g, key, 'Home %d' % n, kind, n % 2 == 0, EAST_RESIDENTS.get(n, ''))
        slate = kind == 'single' and mirror
        deck = ('home/slate' if slate else 'home/deck', None)
        navy = ('home/navy', None)
        red = ('home/carpet', None)
        bake_floor.AREA_FLOORS[key] = {
            'o': deck, 'k': deck, 'h': navy if slate else red,
            'j': navy if kind == 'family' else deck, 't': ('home/bath', None),
        }
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
    make_bathhouse(g, entries, warps)
    g['EAST_ENTRANCES'] = entries
    g.setdefault('AREA_PROPS', {})['east'] = e.props
    g.setdefault('AREA_ROOF_PROPS', {})['east'] = []
    g.setdefault('AREA_LIGHTS', {})['east'] = []
    g.setdefault('EXTRA_THINGS', []).extend(e.things)


def make_home(g, key, title, kind, mirror, who=''):
    """One home's own map. single: living room with a kitchenette corner, bedroom, bathroom. couple: bigger,
    a double bed and a small study. family: kitchen and dining, living room, a main bedroom, a children's room
    and a bathroom. Even-numbered homes are mirrored, and the floors change from home to home. who: whoever
    lives there ('A|B' for a couple); their bedroom locks until you are friends, and their things go in."""
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
    bed = None
    if kind == 'single':
        room(3, 3, 17, 19, 'o'); room(19, 3, 26, 12, 'h'); room(19, 14, 26, 19, 't', 1)
        for y in range(3, 8):
            for x in range(3, 10):
                if H[y][X(x)] == 'o': tile(x, y, 'k')
        for y in (10, 11, 16, 17): tile(18, y, 'o')
        inner = [(18, 10, 1, 2, 'bedroom'), (18, 16, 1, 2, 'bathroom')]
        door = (X(10), 20); tile(10, 20, 'o')
        put('kitchenette', 5.5, 5.5, 'Kitchenette', 'inspect', 'Inspect'); put('fridge', 9, 5.5, 'Fridge')
        put('table', 6.5, 10.5, 'Dining table', 'seat', 'Sit'); put('sofa', 13, 7.5, 'Sofa', 'seat', 'Sit')
        put('cafe_table', 13, 11, 'Coffee table'); put('armchair', 15.5, 14.5, 'Armchair', 'seat', 'Sit')
        put('books', 5, 17, 'Bookshelf'); put('plants', 14.5, 18.5, 'Plant')
        bed = put('bed', 21, 6.5, "%s's bed" % who if who else 'Bed', 'look' if who else None)
        put('wardrobe', 25, 5.5, 'Wardrobe'); put('footlocker', 21, 10.5, 'Chest')
        for name, fx, fy, t in EAST_THINGS.get(who, []): put(name, fx, fy, t, 'look')
        put('shower', 21, 17.5, 'Shower'); put('toilet', 24, 16.5, 'Toilet'); put('bath_sink', 25.5, 18.5, 'Washbasin')
        hm.keep_clear(X(8) if not mirror else X(12), 16, X(12) if not mirror else X(8), 20)
        zones = [['Living room', 3, 3, 17, 19], ['Bedroom', 19, 3, 26, 12], ['Bathroom', 19, 14, 26, 19]]
    elif kind == 'couple':
        room(3, 3, 20, 21, 'o'); room(22, 3, 30, 13, 'h'); room(22, 15, 30, 21, 't', 1)
        for y in range(3, 10):                                       # kitchenette and study corners, inside the living room
            for x in range(3, 21):
                if H[y][X(x)] == 'o' and (x <= 9 or (x >= 12 and y <= 8)): tile(x, y, 'k' if x <= 9 else 'j')
        for y in (9, 10, 11, 17, 18): tile(21, y, 'o')
        inner = [(21, 9, 1, 3, 'bedroom'), (21, 17, 1, 2, 'bathroom')]
        door = (X(11), 22); tile(11, 22, 'o')
        put('kitchenette', 6, 6, 'Kitchenette', 'inspect', 'Inspect'); put('fridge', 9.5, 5.5, 'Fridge')
        put('table', 7, 12.5, 'Dining table', 'seat', 'Sit')
        if who == 'Job':                                            # a home gym in the study corner
            put('weight_bench', 16.5, 5.5, "Job's weights", 'look'); put('punching_bag', 13, 5.5, 'Punching bag')
            put('cargo', 19, 8.5, 'Box of geodes', 'look')
        elif who == 'Zaas':                                         # his ocean corner
            put('water_tank', 13.5, 5.5, 'Fish tank', 'look'); put('star_chart', 16.5, 5.5, "Zaas's ocean charts", 'look')
            put('telescope', 19, 5.5, "Zaas's telescope", 'look')
        else:
            put('curator_desk', 16.5, 5.5, 'Desk'); put('books', 13.5, 5.5, 'Bookshelf')
        put('sofa', 14.5, 13, 'Sofa', 'seat', 'Sit'); put('cafe_table', 14.5, 16.5, 'Coffee table'); put('armchair', 18.5, 16, 'Armchair', 'seat', 'Sit')
        put('plants', 5, 20, 'Plant'); put('tree_tub', 18.5, 20, 'Potted tree')
        bed = put('bed_double', 25.5, 7.5, "%s's bed" % who.replace('|', ' and ') if who else 'Double bed', 'look' if who else None)
        put('wardrobe', 29.5, 5.5, 'Wardrobe'); put('footlocker', 28.5, 12, 'Chest')
        put('shower', 24, 19.5, 'Shower'); put('toilet', 27, 18.5, 'Toilet'); put('bath_sink', 29.5, 20.5, 'Washbasin')
        zones = [['Living room', 3, 3, 20, 21], ['Bedroom', 22, 3, 30, 13], ['Bathroom', 22, 15, 30, 21]]
    else:
        room(3, 3, 22, 14, 'k'); room(3, 16, 22, 26, 'o'); room(24, 3, 38, 12, 'h'); room(24, 14, 38, 20, 'j'); room(24, 22, 38, 26, 't', 1)
        for x in (11, 12, 13): tile(x, 15, 'o')
        for y in (7, 8, 17, 18, 24): tile(23, y, 'o' if y > 14 else 'k')
        inner = [(23, 7, 1, 2, 'bedroom'), (23, 17, 1, 2, 'sewing room' if who == 'Tikka|Sesska' else 'bedroom'), (23, 24, 1, 1, 'bathroom')]
        door = (X(13), 27); tile(13, 27, 'o')
        put('kitchenette', 6, 5.5, 'Kitchenette', 'inspect', 'Inspect'); put('kitchenette', 11, 5.5, 'Stove'); put('fridge', 15, 5.5, 'Fridge')
        put('table', 9, 10.5, 'Family table', 'seat', 'Sit'); put('table', 15, 10.5, 'Family table', 'seat', 'Sit'); put('plants', 20.5, 6, 'Plant')
        put('sofa', 8, 19.5, 'Sofa', 'seat', 'Sit'); put('sofa', 16, 19.5, 'Sofa', 'seat', 'Sit'); put('cafe_table', 12, 22.5, 'Coffee table')
        put('books', 5, 25, 'Bookshelf'); put('tree_tub', 20.5, 25, 'Potted tree')
        couple = who.replace('|', ' and ')
        bed = put('bed_double', 28.5, 7, "%s's bed" % couple if who else "Parents' bed", 'look' if who else None)
        put('wardrobe', 36.5, 5.5, 'Wardrobe')
        if who == 'Tikka|Sesska':                                   # no children: Sesska's sewing room, Tikka's bench
            put('textiles', 28.5, 17.5, "Sesska's home loom", 'look'); put('clothes', 33.5, 17.5, 'Bolts of bug silk', 'look')
            put('footlocker', 36, 19.5, 'Thread chest', 'look'); put('workbench', 19.5, 24.5, "Tikka's tinkering bench", 'look')
        else:
            put('bunk_bed', 27, 18, "Children's bunk"); put('bunk_bed', 31, 18, "Children's bunk"); put('footlocker', 36, 19, 'Toy chest')
        put('shower', 26, 25, 'Shower'); put('toilet', 30, 24.5, 'Toilet'); put('bath_sink', 33, 24.5, 'Washbasin')
        zones = [['Kitchen', 3, 3, 22, 14], ['Living room', 3, 16, 22, 26], ['Bedroom', 24, 3, 38, 12],
                 ["Sesska's sewing room" if who == 'Tikka|Sesska' else "Children's room", 24, 14, 38, 20], ['Bathroom', 24, 22, 38, 26]]
    if not who: hm.thing('look', 'Empty home', 'Look', door[0], door[1] - 4, 50)
    hm.t.zones += [[t, min(X(a), X(c)), b, max(X(a), X(c)), d] for t, a, b, c, d in zones]
    hm.door = door
    # Doors between rooms (Zachary, 17 Nov): they slide open as you come near. A bedroom door locks when its
    # owner has one and you are not yet friends with them (see BEDROOM_HEARTS in main.gd).
    for x, y, w_, h_, what in inner:
        xs = sorted((X(x), X(x + w_ - 1)))
        g.setdefault('INNER_DOORS', []).append([key, xs[0], y, xs[1] - xs[0] + 1, h_, 'E' if h_ > w_ else 'S',
                                                 who if what == 'bedroom' and (x, y) == inner[0][:2] else '', what])
    # night stops beside the bed for whoever lives here (HOME_SPOTS, used by the schedules in tools/build.py)
    if who and bed:
        from residences import free_spot
        bw, bh, _ = SIZES['bed' if kind == 'single' else 'bed_double']
        doors = {(X(x), yy) for x, y, w_, h_, _ in inner for yy in range(y, y + h_)}
        sides = [(bed[0] + bw + .5, bed[1] + bh - .5), (bed[0] - .5, bed[1] + bh - .5)]
        taken = set()
        for name, (sx, sy) in zip(who.split('|'), sides):
            g.setdefault('HOME_SPOTS', {})[name] = (key,) + free_spot(hm, sx, sy, taken, doors)
    return hm, mirror


def garden_dome(F):
    """The garden dome's floor: grass, a cross of paved walks, the stream and its ponds (Y), docks and a footbridge (p), the
    stepping-stone paths through the woods, the hot springs, and the bath house's block on the east rim."""
    H, W = len(F), len(F[0])
    disc(F, DX, DY, DR, 's')                                                    # grass under the glass
    fill(F, 113, 44, 191, 48, '.')                                               # the walk in, across to the bath house door in the east rim
    for y in range(10, 83):                                                      # the walk north to south through the west side
        for x in range(136, 140):
            if math.hypot(x + .5 - DX, y + .5 - DY) <= DR - 2: F[y][x] = '.'
    for y in range(7, 86):                                                       # the stream: three tiles wide
        sx = stream_x(y)
        for x in range(int(sx) - 1, int(sx) + 2):
            if math.hypot(x + .5 - DX, y + .5 - DY) <= DR - 1: F[y][x] = 'Y'
    disc(F, stream_x(9), 9, 2.6, 'Y')                                            # the spring it rises from
    for (py, rx, ry) in ((22, 7, 5), (32, 6, 4), (68, 7, 5)):                     # three fishing ponds on the stream
        px = stream_x(py)
        for y in range(py - ry - 1, py + ry + 2):
            for x in range(int(px - rx - 1), int(px + rx + 2)):
                if ((x + .5 - px) / rx) ** 2 + ((y + .5 - py) / ry) ** 2 <= 1: F[y][x] = 'Y'
    for (x0, y0, x1, y1) in ((int(stream_x(22)) - 9, 21, int(stream_x(22)) - 6, 23), (int(stream_x(32)) + 5, 31, int(stream_x(32)) + 8, 33),
                             (int(stream_x(68)) - 9, 67, int(stream_x(68)) - 6, 69)):
        fill(F, x0, y0, x1, y1, 'p')                                             # a little dock into each pond
    for x in range(int(stream_x(46)) - 3, int(stream_x(46)) + 4):                # the footbridge on the walk in
        for y in range(44, 49):
            if F[y][x] == 'Y': F[y][x] = 'p'
    # stepping-stone paths: a loop through the north woods and one round the picnic green in the south woods
    for loop in ([(139, 28), (133, 25), (127, 27), (121, 23), (123, 15), (130, 12), (136, 14), (139, 20)],
                 [(136, 63), (134, 70), (128, 73), (121, 71), (118, 64), (120, 56), (127, 53), (134, 56)]):
        pts = loop + [loop[0]]
        for (a, b) in zip(pts, pts[1:]):
            n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) * 2 + 1
            for k in range(n + 1):
                x = round(a[0] + (b[0] - a[0]) * k / n); y = round(a[1] + (b[1] - a[1]) * k / n)
                if F[y][x] == 's': F[y][x] = 'j'
    # the forest pond, apart from the stream, for other kinds of fish (Zachary, 22 Nov), with a small dock
    for y in range(56, 71):
        for x in range(119, 137):
            if ((x + .5 - 127.5) / 7.2) ** 2 + ((y + .5 - 63) / 5.4) ** 2 <= 1: F[y][x] = 'Y'
    fill(F, 127, 55, 128, 57, 'p')
    # the hot springs: warm pools on a paved terrace below the bath house
    disc(F, 179, 64, 11.5, '.', only='s')
    for (x, y, r) in ((172, 60, 3.0), (179, 56.5, 2.8), (175, 68, 3.2), (183, 65, 3.0), (180, 72.5, 2.6)):
        disc(F, x, y, r, 'O')
    # the bath house is built into the dome's east rim (its own map): a front door at the end of the walk and a
    # springs door in the rim beside the hot springs
    F[BATH_FRONT[1]][BATH_FRONT[0]] = '.'; F[BATH_BACK[1]][BATH_BACK[0]] = '.'


BATH_FRONT, BATH_BACK = (192, 46), (187, 64)


def dress_dome(e, N, P):
    """Trees, flowers, benches and lamps for the garden dome, and things to look at by the water."""
    import random
    rng = random.Random(22)
    # the woods west of the north-south walk: trees round the stepping-stone loops
    spots = [(118, 18), (124, 20), (128, 16), (133, 19), (126, 31), (119, 30), (132, 30), (121, 11), (134, 9),
             (116, 52), (123, 50), (131, 77), (124, 77), (117, 74), (133, 51), (128, 80), (135, 79), (120, 79)]
    for (x, y) in spots:
        e.near('park_tree', x + rng.uniform(-.6, .6), y, 'Tree', None)
    for (x, y) in ((122, 21), (131, 22), (127, 13), (118, 60), (136, 68), (123, 74)):
        e.near('fern', x, y, 'Fern', None)
    for (x, y) in ((117, 25), (129, 34), (132, 72)): e.near('boulder', x, y, 'Mossy boulder', None)
    # the flower meadow and the picnic green
    for (x, y) in ((124, 38), (130, 38), (127, 41), (121, 41), (133, 41)): e.near('flowers', x, y, 'Wildflowers', 'inspect', 'Inspect')
    e.near('bench_s', 127, 35, 'Meadow bench [S]', 'seat', 'Sit')
    e.near('cafe_table', 131, 52, 'Picnic table', 'look', 'Look'); e.near('bench_s', 124, 52, 'Pond bench [S]', 'seat', 'Sit')
    e.thing('look', 'Forest pond', 'Look', 127.5, 57, 40)                            # at the end of its dock
    # by the water: benches, lamps and the fishing spots
    for (dx_, py) in ((-6, 22), (5, 32), (-6, 68)):                              # at the end of each pond's dock
        e.thing('look', 'Fishing pond', 'Look', int(stream_x(py)) + dx_ + (0 if dx_ > 0 else 0), py, 40)
    e.thing('look', 'The spring', 'Look', stream_x(9), 9, 40); e.thing('look', 'Stream', 'Look', stream_x(56), 56, 40)
    e.near('bench_s', 147, 40, 'Pond bench [S]', 'seat', 'Sit'); e.near('bench_n', 168, 53, 'Bench [N]', 'seat', 'Sit')
    e.near('signpost', 141, 42, 'Signpost: ponds, springs, bath house', 'look', 'Read')
    for (x, y) in ((116, 42), (134, 42), (144, 51), (170, 42), (141, 20), (141, 72)): e.near('lamp_post', x, y, 'Lamp', None)
    for (x, y) in ((172, 18), (178, 28), (165, 80), (150, 82), (186, 30)): e.near('park_tree', x, y, 'Tree', None)
    for (x, y) in ((146, 30), (169, 37), (160, 60), (147, 62)): e.near('flowers', x, y, 'Flowers', None)
    # the hot springs
    for (x, y) in ((176, 61), (179, 66), (185, 70)): e.near('steam_vent', x, y, 'Steam from the springs', None)
    e.thing('look', 'Hot springs', 'Look', 178, 63, 60)
    e.near('bench_n', 185, 75, 'Springs bench [N]', 'seat', 'Sit'); e.near('potted_plant', 171, 55, 'Plant', None)
    e.thing('look', 'Bath house', 'Look', 189, 45, 40)


def make_bathhouse(g, entries, warps):
    """The bath house's own map (bigger, 22 Nov): an entrance hall with the desk, men's and women's changing rooms,
    each opening onto the bath hall, which has a big pool and a steamy hot pool, and a back door out onto the
    hot springs."""
    from survey import door_pair
    import bake_floor
    W, Hh = 56, 32
    b = Room(g, 'bathhouse', 'Bath House', W, Hh)
    H = b.F
    fill(H, 1, 1, W - 2, Hh - 2, '#')
    chamfer_room(H, 3, 3, 15, 28, 'o', 2)                                        # the entrance hall
    chamfer_room(H, 18, 3, 27, 13, 't'); chamfer_room(H, 18, 16, 27, 26, 't')    # men's (north) and women's (south) changing rooms
    for y in (7, 8): H[y][16] = 'o'; H[y][17] = 't'; H[y][28] = 't'
    for y in (20, 21): H[y][16] = 'o'; H[y][17] = 't'; H[y][28] = 't'
    chamfer_room(H, 29, 3, 52, 28, 't', 2)                                       # the bath hall
    chamfer_room(H, 32, 6, 44, 15, 'Y', 2)                                       # the big pool (cooler water)
    chamfer_room(H, 40, 19, 50, 25, 'O', 2)                                      # the steamy hot pool (warm, pale water)
    front, back = (9, 29), (46, 29)
    H[29][9] = 'o'; H[29][46] = 't'
    b.keep_clear(8, 25, 10, 28); b.keep_clear(45, 25, 47, 28)
    for y0 in (6, 19): b.keep_clear(15, y0, 18, y0 + 3); b.keep_clear(27, y0, 30, y0 + 3)
    N = b.near
    N('front_desk_l', 9, 15, 'Bath house desk', 'look', 'Look'); N('potted_plant', 4, 26, 'Plant', None); N('potted_plant', 14, 26, 'Plant', None)
    N('bench_s', 6, 21, 'Bench', 'seat', 'Sit'); N('fern', 4, 5, 'Fern', None); N('signpost', 13, 9, 'Sign: changing rooms this way', 'look', 'Read')
    for x in (19, 22, 25): N('locker', x, 4, "Locker (men's)", 'look' if x == 22 else None, 'Look')
    for x in (19, 22, 25): N('locker', x, 17, "Locker (women's)", 'look' if x == 22 else None, 'Look')
    N('bench_s', 22, 11.5, "Changing bench (men's)", 'seat', 'Sit'); N('bench_s', 22, 24.5, "Changing bench (women's)", 'seat', 'Sit')
    b.thing('look', "Men's changing room", 'Look', 19, 8, 40); b.thing('look', "Women's changing room", 'Look', 19, 21, 40)
    for x in (31, 47): N('shower', x, 4, 'Shower', 'look' if x == 31 else None, 'Look')
    for (x, y) in ((39, 20), (51, 18), (45, 26.5)): N('steam_vent', x, y, 'Steam', None)
    N('bench_s', 34, 22, 'Poolside bench', 'seat', 'Sit'); N('bench_s', 34, 26.5, 'Poolside bench', 'seat', 'Sit')
    N('potted_plant', 30, 27, 'Plant', None); N('fern', 51, 12, 'Fern', None)
    b.thing('look', 'The big pool', 'Look', 38, 16.5, 40); b.thing('look', 'The steamy pool', 'Look', 45, 18, 40)
    b.t.zones += [['Entrance hall', 3, 3, 15, 28], ["Men's changing room", 18, 3, 27, 13], ["Women's changing room", 18, 16, 27, 26],
                  ['Bath hall', 29, 3, 52, 28]]
    bake_floor.AREA_FLOORS['bathhouse'] = {'o': ('home/deck', None), 't': ('home/bath', None), 'Y': ('agri/water', None),
                                           'O': ('agri/water', ('b8e0d8', 0.45))}
    warps['bathhouse'] = b.t.warps
    door_pair(entries, warps, 'east', BATH_FRONT, 'W', 'bathhouse', front, 'N', 'Bath house', 'Garden dome')
    door_pair(entries, warps, 'east', BATH_BACK, 'W', 'bathhouse', back, 'N', 'Bath house (springs door)', 'Hot springs')
    g['MAP_PARENT']['bathhouse'] = ['east', BATH_FRONT[0] - 1, BATH_FRONT[1]]
    g.setdefault('AREA_PROPS', {})['bathhouse'] = b.props
    g.setdefault('AREA_ROOF_PROPS', {})['bathhouse'] = []
    g.setdefault('AREA_LIGHTS', {})['bathhouse'] = []
    g.setdefault('EXTRA_THINGS', []).extend(b.things)
    g.setdefault('LUNAR_EXTRA', {})['Bath House'] = 'bathhouse'
