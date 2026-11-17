"""The Spaceport District, rebuilt in the promenade style (Zachary, 17 Nov). Three maps:

west   the district junction (option D): a big octagonal plaza with four empty basins (ponds and gardens later,
       after the undersea ocean), corner kiosks and a beacon mast in the middle. West: Reception and customs
       (S.A.R.A.), then the terminal, whose west side is one long window over the landing pad outside; the
       airlock is sealed until you have a space suit. North-west: the Star dome. North: the agri complex.
       South: the hotel. East: the walkway to the Main Level.
agri   three domes round a central storage shed: your agri dome (one corner still grows), your workshop, and
       the hot springs and fish ponds. Glass links join the shed to the agri dome and every dome to the others;
       the way in from the junction crosses the workshop-springs link at a small crossroads.
hotel  the old barracks, the future hotel: the long hall (front desk), the head officer's quarters (you start
       here), three bunk rooms, a big lower bunk room and the old drill hall (the lounge later).
Drawn in the promenade style; walls faceted by tools/bake_floor.py."""
import math
import survey
import engineering                    # its prop sizes (benches, shelves, workbenches ...)
from survey import Room, SIZES, door_pair
from engineering import chamfer_room

WALKABLE = '.pfhuAasmo'
SIZES.update({
    'kiosk': (3, 3, 2), 'seed_rack': (2, 2, 1), 'garden_tools': (2, 2, 1), 'hydroponics': (3, 2, 1), 'planter_long': (4, 2, 1),
    'tree_tub': (2, 2, 1), 'lamp_post': (1, 2, 1), 'waiting_seat_w': (1, 3, 2), 'waiting_seat_e': (1, 3, 2), 'market_counter': (3, 2, 1),
    'view_bench': (3, 2, 1),
    'customs_desk': (3, 2, 1), 'stanchion': (1, 1, 1), 'departures_board': (4, 2, 1), 'beacon_mast': (3, 4, 2),
    'planter_dead': (3, 2, 1), 'rubble': (2, 1, 1), 'glass_shards': (2, 1, 0), 'shipping_bin': (2, 2, 1), 'steam_vent': (1, 1, 1),
    'bunk_bed': (2, 3, 2), 'armchair': (2, 2, 1), 'footlocker': (2, 1, 1), 'gym_rack': (3, 2, 1),
})


def disc(F, cx, cy, r, ch, only=None):
    for y in range(len(F)):
        for x in range(len(F[0])):
            if math.hypot(x + .5 - cx, y + .5 - cy) <= r and (only is None or F[y][x] in only):
                F[y][x] = ch


def band(F, a, b, half, ch, only='#'):
    """A straight corridor `half` tiles either side of the line a-b (tile centres), cut through rock."""
    (ax, ay), (bx, by) = a, b
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    for y in range(len(F)):
        for x in range(len(F[0])):
            px, py = x + .5, y + .5
            t = max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / L2))
            if math.hypot(px - (ax + t * vx), py - (ay + t * vy)) <= half and F[y][x] in only:
                F[y][x] = ch


def fill(F, x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            F[y][x] = ch


def build(g):
    survey.WALKABLE = WALKABLE
    entries = []
    # ================================================================== west: the district junction
    w = Room(g, 'west', 'Spaceport District', 112, 82)
    F = w.F
    fill(F, 1, 1, 110, 80, '#')
    fill(F, 1, 1, 20, 80, 'Q')                                   # outside: bare moon (vacuum)
    disc(F, 10, 40, 8.5, 'V')                                    # the landing pad
    chamfer_room(F, 22, 20, 37, 60, '.', 4)                      # the terminal
    for y in range(24, 57): F[y][21] = 'g'                       # one long window over the pad
    fill(F, 16, 37, 21, 43, '#'); fill(F, 17, 38, 21, 42, 'f')   # the airlock
    chamfer_room(F, 39, 30, 46, 50, 'f', 2)                      # Reception and customs
    for y in (39, 40, 41): F[y][38] = F[y][47] = 'f'
    chamfer_room(F, 48, 15, 94, 65, 'p', 9)                      # the junction plaza
    for (x0, y0, x1, y1) in ((57, 22, 66, 31), (76, 22, 85, 31), (57, 49, 66, 58), (76, 49, 85, 58)):
        chamfer_room(F, x0, y0, x1, y1, 'Y', 2)                  # empty basins: ponds and gardens one day
    disc(F, 58, 7, 6.2, 'h')                                     # the Star dome
    fill(F, 57, 12, 59, 15, 'u')
    fill(F, 70, 4, 72, 15, 'u')                                  # to the agri complex
    fill(F, 70, 65, 72, 77, 'u')                                 # to the hotel
    fill(F, 95, 38, 110, 42, 'p')                                # the walkway to the Main Level
    agri_door, hotel_door = (71, 3), (71, 78)
    F[agri_door[1]][agri_door[0]] = F[hotel_door[1]][hotel_door[0]] = 'u'
    w.t.warp('A', [(111, y) for y in range(38, 43)], 'main', 0, 0)   # tools/concourse.py sets the landing
    w.t.zones += [['Landing pad (outside)', 1, 30, 20, 50], ['Terminal', 22, 20, 37, 60], ['Airlock', 17, 38, 21, 42],
                  ['Reception', 39, 30, 46, 50], ['District junction', 48, 15, 94, 65], ['Star dome', 52, 1, 64, 13],
                  ['Walkway to the Main Level', 95, 38, 111, 42]]
    w.keep_clear(22, 38, 50, 42); w.keep_clear(48, 38, 111, 42); w.keep_clear(69, 3, 73, 20); w.keep_clear(69, 60, 73, 78)
    w.keep_clear(56, 11, 60, 18); w.keep_clear(17, 38, 24, 42)
    P, N = w.prop, w.near
    # terminal: gate seats facing the window, the departures board, two sealed gates, two empty kiosks
    P('departures_board', 28, 20, 'Departures board', 'look', 'Look')
    for y in (25, 29, 45, 49):
        for x in (25, 29): P('waiting_seat_w', x, y, 'Gate seat [W]', 'seat', 'Sit')
    P('lab_door', 22, 25, 'Gate 2 (sealed)', 'look', 'Look', door=True); P('lab_door', 22, 53, 'Gate 3 (sealed)', 'look', 'Look', door=True)
    N('kiosk', 35, 25.5, 'Empty kiosk', 'look', 'Look'); N('kiosk', 35, 57.5, 'Empty kiosk', 'look', 'Look')
    N('tree_tub', 34, 34.5, 'Potted tree', None); N('tree_tub', 34, 47.5, 'Potted tree', None); N('bin', 36, 37.5, 'Bin', None)
    P('lab_door', 17, 39, 'Outer airlock door', 'look', 'Look', door=True)
    w.thing('look', 'Landing pad', 'Look outside', 23, 44, 40); w.thing('look', 'Landing pad', 'Look outside', 23, 33, 40)
    # Reception and customs: S.A.R.A.'s desk, a customs line of stanchions with a gap for the way through
    N('customs_desk', 41.5, 33.5, 'Customs desk', 'look', 'Look'); N('customs_desk', 41.5, 48.5, 'Customs desk', None)
    for y in (31, 33, 35, 37, 43, 45, 47, 49): P('stanchion', 44, y, 'Customs line', None)
    w.thing('look', 'Customs gate', 'Look', 44, 40, 24)
    # the junction: beacon mast, corner kiosks, benches by the basins, lamps, trees, signposts
    P('beacon_mast', 70, 37, 'Beacon mast', 'look', 'Look', door=True)
    for fx, fy in ((53.5, 27), (88.5, 27), (53.5, 57), (88.5, 57)): N('kiosk', fx, fy, 'Empty kiosk', 'look', 'Look')
    for fx, fy in ((61.5, 34), (80.5, 34)): N('bench_n', fx, fy, 'Bench [N]', 'seat', 'Sit')
    for fx, fy in ((61.5, 47), (80.5, 47)): N('bench_s', fx, fy, 'Bench [S]', 'seat', 'Sit')
    for fx, fy in ((66, 20.5), (76, 20.5), (66, 61.5), (76, 61.5), (52, 34), (52, 47), (90, 34), (90, 47)): N('lamp_post', fx, fy, 'Lamp', None)
    for fx, fy in ((56, 40), (86, 44.5)): N('tree_tub', fx, fy, 'Potted tree', None)
    N('signpost', 74, 19.5, 'Signpost: agri complex', None); N('signpost', 74, 63.5, 'Signpost: hotel', None); N('signpost', 92, 37.5, 'Signpost: Main Level', None)
    N('drinking_fountain', 88, 44.5, 'Water point', 'inspect', 'Inspect'); N('bin', 54, 44, 'Bin', None)
    for fx, fy in ((61.5, 26.5), (80.5, 26.5), (61.5, 53.5), (80.5, 53.5)): w.thing('look', 'Empty basin', 'Look', fx, fy + (5 if fy < 40 else -5), 40)
    # the Star dome
    N('telescope', 58, 6, 'Telescope', 'look', 'Look through it'); N('view_bench', 54.5, 10.5, 'Bench', 'seat', 'Sit')
    N('star_chart', 62, 9, 'Star chart', 'look', 'Look')

    # ================================================================== agri: three domes round the storage shed
    a = Room(g, 'agri', 'Agri Complex', 110, 90)
    F = a.F
    fill(F, 1, 1, 108, 88, '#')
    disc(F, 55, 23, 19, 'a')                                     # your agri dome
    disc(F, 24, 64, 13, 'f')                                     # your workshop
    disc(F, 86, 64, 15, 's')                                     # hot springs and fish ponds
    chamfer_room(F, 47, 45, 63, 59, 'h', 3)                      # the storage shed
    chamfer_room(F, 77, 54, 89, 63, 'O', 3)                      # the hot spring
    chamfer_room(F, 89, 65, 97, 72, 'Y', 2); chamfer_room(F, 77, 67, 85, 74, 'Y', 2)   # fish ponds
    band(F, (55, 23), (24, 64), 1.6, 'u'); band(F, (55, 23), (86, 64), 1.6, 'u'); band(F, (24, 64), (86, 64), 1.6, 'u')
    band(F, (55, 40), (55, 47), 1.6, 'u')                        # shed to agri dome
    fill(F, 54, 60, 56, 87, 'u')                                 # the way in, from the junction
    agri_in = (55, 88); F[agri_in[1]][agri_in[0]] = 'u'
    a.t.zones += [['Agri dome', 36, 4, 74, 42], ['Storage shed', 47, 45, 63, 59], ['Your workshop', 11, 51, 37, 77],
                  ['Hot springs & fish ponds', 71, 49, 101, 79], ['Glass link', 1, 1, 108, 88]]
    a.keep_clear(53, 60, 57, 88); a.keep_clear(36, 62, 74, 66); a.keep_clear(53, 38, 57, 47)
    P, N = a.prop, a.near
    # the agri dome: the west corner still grows; the rest is dead planters, rubble and broken glass
    for ang in (165, 195, 215):
        x, y = 55 + 11 * math.cos(math.radians(ang)), 23 + 11 * math.sin(math.radians(ang))
        N('hydroponics', x, y, 'Your crop beds', 'garden', 'Water')
    N('planter_long', 43, 31.5, 'Herb bed', 'inspect', 'Inspect')
    for ang in range(250, 520, 30):
        x, y = 55 + 12 * math.cos(math.radians(ang)), 23 + 12 * math.sin(math.radians(ang))
        N('planter_dead', x, y, 'Dead planter', 'inspect', 'Inspect')
    for fx, fy in ((60, 12), (66, 22), (57, 34), (48, 9), (64, 31)): N('rubble', fx, fy, 'Rubble', None)
    for fx, fy in ((53, 14), (62, 18), (68, 28), (59, 27)): N('glass_shards', fx, fy, 'Broken glass', None)
    a.thing('look', 'Broken agri dome', 'Look', 58, 22, 60)
    # the storage shed
    N('shipping_bin', 52, 48, 'Shipping crate', 'look', 'Look'); N('seed_rack', 58.5, 48, 'Seed rack', 'look', 'Look')
    N('garden_tools', 61, 52, 'Garden tools', None); N('storage_shelf', 50, 56.5, 'Shed shelving', None)
    N('barrel_stack', 61, 57, 'Feed barrels', None); N('cargo', 58, 56.5, 'Crates', None)
    # your workshop
    N('workbench', 19.5, 58.5, 'Workbench', 'look', 'Look'); N('workbench', 27.5, 58.5, 'Workbench', None)
    N('tool_cart', 15, 65, 'Tool cart', None); N('welding_rig', 32, 67, 'Welding rig'); N('parts_rack', 20, 72.5, 'Parts rack', None)
    N('locker', 29, 72.5, 'Tool locker', None); N('pipe_rack', 24, 66.5, 'Pipe stock', None)
    # hot springs and fish ponds
    for fx, fy in ((79, 53.5), (85, 52.5), (90, 54.5)): N('steam_vent', fx, fy, 'Steam vent', None)
    N('bench_n', 84, 77, 'Bench [N]', 'seat', 'Sit'); N('plants', 96, 59, 'Fern', 'inspect', 'Inspect'); N('plants', 75, 72, 'Fern', 'inspect', 'Inspect')
    a.thing('look', 'Hot spring', 'Look', 83, 64.5, 40); a.thing('look', 'Fish ponds', 'Look', 87, 72.5, 40)

    # ================================================================== hotel: the old barracks
    h = Room(g, 'hotel', 'Hotel', 72, 48)
    F = h.F
    fill(F, 1, 1, 70, 46, '#')
    chamfer_room(F, 5, 10, 69, 17, 'u', 2)                       # the hotel hall
    hotel_in = (37, 9); F[hotel_in[1]][hotel_in[0]] = 'u'
    chamfer_room(F, 5, 19, 19, 33, 'h', 2); F[18][12] = 'h'      # the head officer's quarters (yours)
    for x0 in (21, 31, 41):
        chamfer_room(F, x0, 19, x0 + 8, 33, 'f', 1); F[18][x0 + 4] = 'f'
    chamfer_room(F, 51, 19, 69, 45, 'm', 3)                      # the old drill hall
    for x in range(58, 63): F[18][x] = 'm'
    chamfer_room(F, 5, 35, 49, 45, 'f', 2)                       # the big lower bunk room
    for y in (38, 39, 40): F[y][50] = 'f'
    h.t.zones += [['Hotel hall', 5, 10, 69, 17], ["Head officer's quarters", 5, 19, 19, 33], ['Bunk room', 21, 19, 49, 33],
                  ['Old drill hall', 51, 19, 69, 45], ['Bunk room', 5, 35, 49, 45]]
    h.keep_clear(35, 10, 39, 12); h.keep_clear(5, 12, 69, 15)
    for x in (12, 25, 35, 45): h.keep_clear(x - 1, 16, x + 1, 20)
    h.keep_clear(57, 16, 63, 21); h.keep_clear(48, 37, 52, 41)
    P, N = h.prop, h.near
    N('market_counter', 30.5, 11.5, 'Old front desk', 'look', 'Look'); N('tree_tub', 8, 11.5, 'Potted tree', None); N('tree_tub', 66, 11.5, 'Potted tree', None)
    N('armchair', 44, 11.5, 'Armchair', 'seat', 'Sit'); N('armchair', 48, 11.5, 'Armchair', 'seat', 'Sit')
    # your quarters
    P('bed', 6, 20, 'Your bunk', 'bed', 'Sleep'); P('wardrobe', 16, 19, 'Locker', 'wardrobe', 'Change look')
    N('footlocker', 7.5, 24.5, 'Footlocker', None); N('armchair', 16, 31, 'Armchair', 'seat', 'Sit'); N('books', 7, 31.5, 'Old manuals', None)
    N('plants', 12.5, 31.5, 'Plant', 'inspect', 'Inspect')
    # bunk rooms, dusty
    for x0 in (21, 31, 41):
        N('bunk_bed', x0 + 1.5, 22.5, 'Old bunks', 'look', 'Look'); N('bunk_bed', x0 + 6.5, 22.5, 'Old bunks', None)
        N('bunk_bed', x0 + 1.5, 30.5, 'Old bunks', None); N('footlocker', x0 + 6.5, 31.5, 'Footlocker', None)
    for fx in (9, 15, 21, 27, 33, 39):
        N('bunk_bed', fx, 38.5, 'Old bunks', None)
    for fx in (11, 23, 35): N('rubble', fx, 44, 'Rubble', None)
    N('locker', 45, 44.5, 'Old lockers', None)
    # the old drill hall: empty, a few weights, crates
    N('gym_rack', 55.5, 22.5, 'Old weights rack', None); N('cargo', 66, 22, 'Crates', None); N('cargo', 66, 43.5, 'Crates', None)
    N('rubble', 57, 41, 'Rubble', None); N('bench_s', 60.5, 44, 'Bench', None)
    h.thing('look', 'Old drill hall', 'Look', 60, 32, 60)

    # ================================================================== doors and links
    warps = {'west': w.t.warps, 'agri': a.t.warps, 'hotel': h.t.warps}
    door_pair(entries, warps, 'west', agri_door, 'S', 'agri', agri_in, 'N', 'Agri complex', 'Spaceport District')
    door_pair(entries, warps, 'west', hotel_door, 'N', 'hotel', hotel_in, 'S', 'Hotel', 'Spaceport District')
    g['MAP_PARENT']['agri'] = ['west', agri_door[0], agri_door[1] + 1]
    g['MAP_PARENT']['hotel'] = ['west', hotel_door[0], hotel_door[1] - 1]
    for room in (w, a, h):
        g.setdefault('AREA_PROPS', {})[room.key] = room.props
        g.setdefault('AREA_ROOF_PROPS', {})[room.key] = []
        g.setdefault('AREA_LIGHTS', {})[room.key] = []
        g.setdefault('EXTRA_THINGS', []).extend(room.things)
    g['SPACEPORT_ENTRANCES'] = entries
