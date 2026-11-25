"""The Spaceport District, rebuilt in the promenade style (Zachary, 17 Nov). Three maps:

west   the district junction (option D): a big octagonal plaza with four empty basins (ponds and gardens later,
       after the undersea ocean), corner kiosks and a beacon mast in the middle. West: Reception and customs
       (S.A.R.A.), then the terminal, whose west side is one long window over the landing pad outside; the
       airlock is sealed until you have a space suit. North-west: the Star dome. North: the agri complex.
       South: the hotel. East: the walkway to the Main Level.
agri   three domes round your front porch (Zachary, 23 Nov): your agri dome (one corner still grows), your
       workshop, and the hot springs and fish ponds. The porch is a big wooden deck at the way in from the
       junction, with your apartment's front door and mailbox on its north side; glass links join it to every
       dome, and every dome to the others.
hotel  option C: a round lobby with a fountain and a curved front desk, the dining room and kitchen, the lounge,
       your office and the manager's suite, a guest corridor and big empty wings to build guest rooms in. The
       kitchen opens onto the dining room and the staff hall behind the desk; the dining room and the lounge each
       have their own way down to the guest corridor.
Drawn in the promenade style; walls faceted by tools/bake_floor.py."""
import math
import survey
import engineering                    # its prop sizes (benches, shelves, workbenches ...)
from survey import Room, SIZES, door_pair
from engineering import chamfer_room

WALKABLE = '.pfhuAasmoiktei'
SIZES.update({
    'water_spigot': (1, 2, 1),         # the farm's standpipe by the field dome's door (25 Nov)
    'kiosk': (3, 3, 2), 'seed_rack': (2, 2, 1), 'garden_tools': (2, 2, 1), 'hydroponics': (3, 2, 1), 'planter_long': (4, 2, 1),
    'tree_tub': (1, 2, 1), 'lamp_post': (1, 2, 1), 'waiting_seat_w': (1, 3, 2), 'waiting_seat_e': (1, 3, 2), 'market_counter': (3, 2, 1),
    'view_bench': (2, 2, 1),
    'customs_desk': (3, 2, 1), 'stanchion': (1, 1, 1), 'departures_board': (4, 2, 1), 'beacon_mast': (3, 4, 2),
    'planter_dead': (3, 2, 1), 'rubble': (2, 1, 0), 'mailbox': (1, 2, 1), 'flowers': (4, 2, 2), 'glass_shards': (2, 1, 0), 'shipping_bin': (2, 2, 1), 'steam_vent': (1, 1, 1),
    'bunk_bed': (2, 3, 2), 'armchair': (2, 2, 1), 'footlocker': (2, 1, 1), 'gym_rack': (3, 2, 1),
    'front_desk': (5, 2, 1), 'front_desk_l': (3, 2, 1), 'front_desk_r': (3, 2, 1), 'key_board': (2, 2, 1), 'luggage_cart': (2, 2, 1),
    'sofa': (3, 2, 1), 'fireplace': (3, 3, 1), 'fridge': (2, 3, 1), 'bar_table': (3, 2, 1), 'cafe_table': (2, 2, 1),
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
    N('telescope', 58, 6, 'Telescope', 'look', 'Look through it'); N('view_bench', 56, 9.5, 'Bench', 'seat', 'Sit')
    N('star_chart', 62, 9, 'Star chart', 'look', 'Look')

    # ================================================================== agri: three domes round your front porch
    # Zachary, 23 Nov (mock-up B, with his change: "move the central circle down to make a giant front porch area"):
    # the storage shed that sat between the domes moved down to the way in and grew into a big wooden front porch.
    # On its north side, your apartment's front door (the apartment is its own map: tools/residences.py,
    # aptPlayer) and the glass link up to your agri dome; west, the workshop; east, the hot springs; south, a short
    # walkway to the junction (the map is 84 tiles tall now, was 90, so the walk in from the junction is 6 tiles
    # instead of 28). The shed's seed rack, tools and stores stand on the porch.
    # Then (Zachary, 23 Nov, on mock-up B: "keep the middle circle that orignal size but move it down to the bottom
    # intersecting hallway, then place the home on the top right of that circle"): the porch is the old shed's size
    # (17 x 15), sitting on the crossing where the workshop-springs link meets the way in from the junction, and your
    # apartment is a building of its own on its top-right corner, with a plank roof and a sided front
    # (bake_floor.HOUSE_FRONTS), its door opening onto the porch. Then ("soften the sharp edges of the house, remove
    # the wood flooring from the porch make it like the left circle"): the roof's corners are cut at 45 degrees,
    # the house's corner on the porch is cut too, and the porch is floored like your workshop ('f'). Then ("raise
    # the house entrance by a few so its even with the other side, remove all the set dressing from middle circle
    # only items there are the shipping bin in the lower left and the mailbox on the lower right. for co op lets
    # also fill in the top left to make another house"): the porch is a whole circle again with the two houses
    # either side of the link up to your field, their fronts level along its top; yours on the right, a second
    # player's on the left (aptCoop, locked until co-op exists). The seed rack and garden tools moved to the field
    # dome, by its door; the workbench is in your workshop.
    a = Room(g, 'agri', 'Agri Complex', 110, 84)
    F = a.F
    fill(F, 1, 1, 108, 82, '#')
    disc(F, 55, 23, 19, 'a')                                     # your agri dome
    disc(F, 24, 64, 13, 'f')                                     # your workshop
    disc(F, 86, 64, 15, 's')                                     # hot springs and fish ponds
    porch = (47, 57, 63, 71)
    chamfer_room(F, porch[0], porch[1], porch[2], porch[3], 'f', 3)   # the front porch, floored like the workshop
    chamfer_room(F, 77, 54, 89, 63, 'O', 3)                      # the hot spring
    chamfer_room(F, 89, 65, 97, 72, 'Y', 2); chamfer_room(F, 77, 67, 85, 74, 'Y', 2)   # fish ponds
    band(F, (55, 23), (24, 64), 1.6, 'u'); band(F, (55, 23), (86, 64), 1.6, 'u'); band(F, (24, 64), (86, 64), 1.6, 'u')
    fill(F, 54, 40, 56, 56, 'u')                                 # porch up to the agri dome (3 wide, centred)
    fill(F, 54, 72, 56, 81, 'u')                                 # the way in, from the junction
    agri_in = (55, 82); F[agri_in[1]][agri_in[0]] = 'u'
    # The storage dome (Zachary, 23 Nov: "a storage circle ... above the bottom left circle connected by two
    # hallways"), between your field and your workshop, with a hallway to each. It and the hot springs and fish
    # ponds are broken and sealed until S.A.R.A. repairs them (scripts/station_repair.gd): sliding doors with red
    # lights where their hallways meet them (INNER_DOORS, owner "repair:<id>"), and wreckage inside that her
    # drones clear (SEALED_ROOMS).
    disc(F, 20, 30, 13, 'f')                                     # the storage dome, the workshop's size (Zachary, 23 Nov)
    rock = lambda x0, y0, x1, y1: [F[y].__setitem__(x, 'u') for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if F[y][x] == '#']
    rock(34, 28, 40, 31)                                         # hallway east to your agri dome
    rock(19, 44, 21, 51)                                         # hallway south to your workshop
    sealed = []                                                  # (x, y, w, h, facing, repair)
    F[28][33] = F[31][33] = '#'; F[29][33] = F[30][33] = 'u'; sealed.append((33, 29, 1, 2, 'E', 'storage'))
    F[43][19] = F[43][21] = '#'; F[43][20] = 'u'; sealed.append((20, 43, 1, 1, 'S', 'storage'))
    # the hot springs and fish ponds: a door where the link from the porch meets them, and a bulkhead across the
    # glass link down from your agri dome
    F[62][70] = F[65][70] = '#'; F[63][70] = F[64][70] = 'u'; sealed.append((70, 63, 1, 2, 'E', 'ponds'))
    cross = 46
    run = [x for x in range(60, 80) if F[cross][x] == 'u']
    door_x = next(x for x in run if F[cross - 1][x] == 'u' and F[cross + 1][x] == 'u' and x not in (run[0], run[-1]))
    for x in run:
        F[cross][x] = 'u' if x == door_x else '#'
    sealed.append((door_x, cross, 1, 1, 'S', 'ponds'))
    for x, y, w_, h_, facing, rid in sealed:
        g.setdefault('INNER_DOORS', []).append(['agri', x, y, w_, h_, facing, 'repair:' + rid, rid])
    g['SEALED_ROOMS'] = {'storage': ['agri', 7, 17, 33, 43], 'ponds': ['agri', 71, 47, 102, 80]}
    # Two houses either side of the link up to your field, mirror images about the porch's middle (x 55), their
    # fronts along the porch's top (y 56) and wrapping round its cut corners: yours on the right (aptPlayer), and on
    # the left one for a second player when co-op comes (aptCoop). Their roofs run back to the field dome.
    home_door, coop_door = (59, 56), (51, 56)
    for d in (home_door, coop_door): F[d[1]][d[0]] = 'f'
    g['PLAYER_HOME_DOOR'] = ('agri', home_door)
    g['COOP_HOME_DOOR'] = ('agri', coop_door)
    import bake_floor
    bake_floor.HOUSE_FRONTS['agri'] = [
        {"roof": (57, 43, 67, 57), "cuts": (2, 2, 0, 3), "front": (57, 43, 63, 59), "roof_art": 'hotel/cap_mix', "wall_art": 'east/wall'},
        {"roof": (43, 43, 53, 57), "cuts": (2, 2, 3, 0), "front": (47, 43, 53, 59), "roof_art": 'hotel/cap_mix', "wall_art": 'east/wall'}]
    # The blocks behind them, between the glass links, stay roof rather than bare moon, right down to the porch and
    # the workshop and hot springs links (Zachary, 23 Nov: no gaps at the houses' lower outer corners).
    house = {(x, y) for x in list(range(57, 73)) + list(range(36, 54)) for y in range(34, 62)}
    # Outside the domes and links is bare moon, with a two-tile station wall round everything inside.
    inside = {(x, y) for y in range(84) for x in range(110) if F[y][x] not in '#Q~'}
    for y in range(1, 83):
        for x in range(1, 109):
            if F[y][x] == '#' and (x, y) not in house and not any((x + dx, y + dy) in inside for dx in range(-2, 3) for dy in range(-2, 3)):
                F[y][x] = 'Q'
    a.t.zones += [['Agri dome', 36, 4, 74, 42], ['Front porch', porch[0], porch[1], porch[2], porch[3]], ['Your workshop', 11, 51, 37, 77],
                  ['Hot springs & fish ponds', 71, 49, 101, 79], ['Storage dome', 7, 17, 33, 43], ['Glass link', 1, 1, 108, 82]]
    for x, y, w_, h_, facing, rid in sealed:
        a.keep_clear(x - 2, y - 2, x + w_ + 1, y + h_ + 1)
    a.keep_clear(32, 27, 41, 32)          # the storage hallway's mouth in the dome
    a.keep_clear(53, 38, 57, 60)          # the link up to the dome, and its mouth
    a.keep_clear(53, 66, 57, 82)          # the way in
    a.keep_clear(36, 62, 74, 65)          # workshop - porch - hot springs
    a.keep_clear(49, 56, 61, 59)          # the two front doors and the way to them
    # Your field (21 Nov): 10 x 12 tiles in the west of the dome, farmed one tile at a time like Stardew (till,
    # plant, water, harvest; scripts/main.gd and scripts/agri_terrain.gd). One tile is one character wide.
    # Its x, y, w, h start on even tiles, so the soil art's 2 x 2-tile frame pieces line up round it.
    field = (40, 14, 10, 12)
    g.setdefault('FARM_FIELDS', {})['agri'] = list(field)
    a.keep_clear(field[0] - 1, field[1] - 1, field[0] + field[2], field[1] + field[3])
    a.t.zones.insert(0, ['Your field', field[0], field[1], field[0] + field[2] - 1, field[1] + field[3] - 1])
    P, N = a.prop, a.near
    # No set dressing anywhere in the district (Zachary, 23 Nov: "remove all the set dressings like i said except
    # the sale bin and message box"). What's left works: the shipping crate and the message pad on the porch, the
    # seed rack, garden tools and irrigation valve for your field, and the workbench that opens the Crafting page.
    # The water spigot that fills your watering can (24 Nov). Since 25 Nov a standpipe of its own beside the dome's
    # door, out of the soil's way (Zachary: "should be at like entrance to farm so it doesnt take up to much farm
    # space"; it was a hydroponic bed in the middle of the field). Art: tools/dev/water_spigot_art.py.
    N('water_spigot', 57.5, 40.5, 'Water spigot', 'garden', 'Fill your can')
    a.thing('look', 'Broken agri dome', 'Look', 58, 22, 60)
    # By the dome's door: the seed rack and the garden tools (they were on the porch until 23 Nov).
    N('seed_rack', 51, 38.5, 'Seed rack', 'seeds', 'Take seeds'); N('garden_tools', 59.5, 38.5, 'Garden tools', 'farm_tools', 'Take')
    # The front porch holds only the shipping crate (lower left) that Bram empties overnight, and your message pad
    # (lower right), which is your mailbox (scripts/mail_reader.gd) (Zachary, 23 Nov).
    N('shipping_bin', 50, 69.5, 'Shipping crate', 'ship', 'Ship to Bram')
    N('terminal', 60.5, 69.5, 'Message pad', 'mail', 'Read your mail')
    # your workshop: the workbench opens the Crafting page
    N('workbench', 19.5, 58.5, 'Workbench', 'craft', 'Craft')
    # Wreckage in the two broken domes. S.A.R.A.'s drones clear it the night they repair the dome (main.gd
    # _sync_station: any prop inside a SEALED_ROOMS box goes once that repair is done). Not solid, so it can't
    # trap anyone once the doors open.
    for fx, fy in ((79, 52), (93, 57), (88, 66), (75, 70), (96, 72), (86, 77)): N('rubble', fx, fy, 'Rubble', None)
    for fx, fy in ((84, 51.5), (98, 64), (81, 74), (91, 70)): N('glass_shards', fx, fy, 'Broken glass', None)
    for fx, fy in ((13, 22), (26, 21), (10, 31), (29, 35), (17, 39), (23, 27)): N('rubble', fx, fy, 'Rubble', None)
    for fx, fy in ((18, 24), (27, 30), (12, 36), (21, 33)): N('glass_shards', fx, fy, 'Broken glass', None)
    a.thing('look', 'Hot spring', 'Look', 83, 64.5, 40); a.thing('look', 'Fish ponds', 'Look', 87, 72.5, 40)

    # ================================================================== hotel (option C, Zachary 17 Nov)
    # A round lobby under a glass dome with a fountain and the front desk curving along its back; the dining
    # room and kitchen to the west, the lounge to the east, your office and the manager's suite behind the desk, a long
    # guest corridor and big empty wings (and a spare room) to build guest rooms in later.
    h = Room(g, 'hotel', 'Hotel', 120, 90)
    F = h.F
    fill(F, 1, 1, 118, 88, '#')
    hotel_in = (60, 1)
    fill(F, 59, 2, 61, 9, 'u'); F[hotel_in[1]][hotel_in[0]] = 'u'
    disc(F, 60, 24, 15, 'i')                                     # the round lobby
    for y in range(17, 27):                                      # its fountain: an octagon, no circles (Zachary, 22 Nov)
        for x in range(55, 66):
            dx, dy = abs(x + .5 - 60), abs(y + .5 - 21.5)
            if max(dx, dy, (dx + dy) / 1.4142) < 3.2: F[y][x] = 'O'
    chamfer_room(F, 12, 10, 41, 33, 'p', 4)                      # dining room
    fill(F, 42, 22, 45, 24, 'u')
    chamfer_room(F, 12, 36, 31, 49, 'k', 3)                      # kitchen
    fill(F, 21, 34, 23, 35, 'u')                                 # kitchen to dining room
    fill(F, 32, 40, 41, 41, 'u')                                 # kitchen to the staff hall behind the desk
    fill(F, 6, 21, 11, 23, 'u'); fill(F, 6, 21, 8, 55, 'u')      # dining room down to the guest corridor
    chamfer_room(F, 78, 10, 108, 33, 'h', 4)                     # lounge
    fill(F, 75, 22, 77, 24, 'u')
    fill(F, 59, 39, 61, 41, 'u'); fill(F, 42, 40, 78, 41, 'u')   # the staff hall behind the desk
    chamfer_room(F, 42, 43, 57, 54, 'o', 3); F[42][50] = 'o'     # your office
    chamfer_room(F, 63, 43, 78, 54, 't', 3); F[42][70] = 't'     # the manager's suite (was your bedroom until 23 Nov)
    fill(F, 59, 42, 61, 55, 'u')
    chamfer_room(F, 84, 36, 108, 52, 'e', 2); fill(F, 94, 53, 96, 55, 'u')   # spare room (empty)
    fill(F, 80, 34, 82, 55, 'u')                                 # lounge down to the guest corridor
    fill(F, 4, 56, 116, 60, 'u')                                 # guest corridor
    chamfer_room(F, 4, 63, 56, 86, 'e', 2); chamfer_room(F, 64, 63, 116, 86, 'e', 2)   # empty guest wings
    for x in (29, 30, 31, 89, 90, 91): F[61][x] = F[62][x] = 'u'
    h.t.zones += [['Hotel lobby', 45, 9, 75, 39], ['Dining room', 12, 10, 41, 33], ['Kitchen', 12, 36, 31, 49], ['Lounge', 78, 10, 108, 33],
                  ['Your office', 42, 43, 57, 54], ["Manager's suite", 63, 43, 78, 54], ['Spare room', 84, 36, 108, 52],
                  ['Guest corridor', 4, 56, 116, 60], ['West guest wing', 4, 63, 56, 86], ['East guest wing', 64, 63, 116, 86]]
    h.keep_clear(58, 2, 62, 12); h.keep_clear(40, 21, 47, 25); h.keep_clear(73, 21, 80, 25); h.keep_clear(57, 36, 63, 57)
    h.keep_clear(42, 39, 78, 42); h.keep_clear(19, 32, 25, 37); h.keep_clear(5, 20, 12, 57); h.keep_clear(30, 39, 42, 42); h.keep_clear(79, 32, 83, 57); h.keep_clear(4, 56, 116, 60)
    h.keep_clear(27, 60, 33, 64); h.keep_clear(87, 60, 93, 64); h.keep_clear(92, 51, 98, 56)
    P, N = h.prop, h.near
    # the lobby: the curved front desk (key boards behind it), sofas and armchairs round the fountain, a luggage cart
    P('front_desk', 58, 33, 'Front desk', 'look', 'Look'); P('front_desk_l', 52, 31, 'Front desk', None); P('front_desk_r', 66, 31, 'Front desk', None)
    N('key_board', 56, 37, 'Room keys', 'look', 'Look'); N('key_board', 65, 37, 'Room keys', None)
    N('luggage_cart', 52.5, 36.5, 'Luggage cart', None)
    for fx, fy, name in ((52, 15, 'sofa'), (68, 15, 'sofa'), (49, 22.5, 'armchair'), (71, 22.5, 'armchair')):
        N(name, fx, fy, 'Sofa' if name == 'sofa' else 'Armchair', 'seat', 'Sit')
    for fx, fy in ((47.5, 29), (72.5, 29), (54, 11.5), (66, 11.5)): N('tree_tub', fx, fy, 'Potted tree', None)
    h.thing('look', 'Lobby fountain', 'Look', 60, 25, 40)
    # dining room: tables, a buffet counter, plants
    for fx in (20, 27, 34):
        for fy in (19, 27): N('cafe_table', fx, fy, 'Dining table', 'seat', 'Sit')
    N('market_counter', 26.5, 12.5, 'Buffet counter', 'look', 'Look'); N('tree_tub', 15, 13, 'Potted tree', None); N('tree_tub', 38, 13, 'Potted tree', None)
    # kitchen
    N('kitchenette', 16.5, 39.5, 'Stove and sink', 'inspect', 'Inspect'); N('kitchenette', 26.5, 39.5, 'Stove and sink', None)
    N('fridge', 29, 46, 'Cold store', 'look', 'Look'); N('table', 18.5, 45.5, 'Prep table', None); N('storage_shelf', 14.5, 47.5, 'Pantry shelves', None)
    # lounge: sofas, armchairs, the bar and the fireplace
    N('fireplace', 93.5, 12.5, 'Fireplace', 'look', 'Look'); N('sofa', 89, 19, 'Sofa', 'seat', 'Sit'); N('sofa', 98, 19, 'Sofa', 'seat', 'Sit')
    N('armchair', 86, 26, 'Armchair', 'seat', 'Sit'); N('armchair', 101, 26, 'Armchair', 'seat', 'Sit'); N('cafe_table', 93.5, 25, 'Coffee table', None)
    N('bar_table', 104, 30.5, 'Bar', 'look', 'Look'); N('books', 82, 13.5, 'Bookshelf', None); N('tree_tub', 106, 14, 'Potted tree', None)
    # your office
    N('curator_desk', 49.5, 46.5, 'Your desk', 'look', 'Look'); N('star_chart', 55, 46, 'Hotel plans', 'look', 'Look')
    N('books', 45, 46.5, 'Ledgers', None); N('armchair', 46, 52, 'Armchair', 'seat', 'Sit'); N('plants', 53.5, 52.5, 'Plant', 'inspect', 'Inspect')
    # the manager's suite: your bedroom until you moved into your apartment by the farm (23 Nov)
    P('bed', 65, 44, 'Suite bed', 'look', 'Look'); P('wardrobe', 75, 43, 'Suite wardrobe', None)
    N('footlocker', 65, 49.5, 'Footlocker', None); N('armchair', 75, 52, 'Armchair', 'seat', 'Sit'); N('plants', 66.5, 52.5, 'Plant', 'inspect', 'Inspect')
    # the empty spaces: bare floor marked out for building, a few crates
    N('cargo', 87, 39, 'Crates', None); N('cargo', 7, 66, 'Crates', None); N('cargo', 113, 66, 'Crates', None)
    for (fx, fy, t) in ((95, 44, 'Spare room'), (30, 74, 'West guest wing'), (90, 74, 'East guest wing')):
        h.thing('look', t, 'Look', fx, fy, 60)

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
