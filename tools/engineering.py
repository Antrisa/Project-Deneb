"""Engineering (area "eng") and the shuttle bay (area "bay"), approved by Zachary on 17 Nov.

eng  option E (Zachary, 17 Nov): a rectangular works hall looping round the geothermal power core, sunk in
     its own pit (stairs down at both ends, panels and coolant tanks inside). Rooms bulge out on 45-degree walls:
     ore processing (two rooms, a conveyor belt from the mine's ore chute in the south-west; the mine tunnel runs west off the hall), Tikka's big engineering bay
     with her office and a drone pad (north), lift, stores, cargo staging and the corridor to the shuttle bay (east),
     a big crew break room, cooling & life support piped up into the pit, and two spare workshops (south).
bay  the shuttle bay, its own map: a hangar cut into the crater wall, with big windows along the north wall
     either side of the launch doors, your ship on its pad, a bigger fighter under a tarp, Freya's work area,
     the launch control booth and the (locked) Shipwright's Suite.
Drawn in the promenade style; walls faceted by tools/bake_floor.py."""
import math
import survey
from survey import Room, SIZES, door_pair

survey.WALKABLE = 'uihsmf.apRokjte'
SIZES.update({
    'geo_core': (5, 4, 3), 'furnace': (2, 3, 1), 'ore_crusher': (3, 3, 2), 'ore_cart': (2, 2, 1), 'pump': (2, 3, 1),
    'pipe_rack': (3, 2, 1), 'locker': (2, 3, 1), 'tool_cart': (2, 2, 1), 'welding_rig': (2, 3, 1), 'fuel_tank': (2, 3, 1),
    'parts_rack': (3, 3, 1), 'launch_console': (3, 2, 1), 'air_scrubber': (2, 3, 1), 'mag_clamp': (1, 1, 0),
    'workbench': (3, 2, 1), 'table': (3, 2, 1), 'trolley': (2, 2, 1), 'water_tank': (2, 2, 1), 'bollard_light': (1, 1, 1),
    'bin': (1, 1, 1), 'drinking_fountain': (1, 2, 1), 'lamp_post': (1, 2, 1), 'bench_s': (2, 2, 1), 'chair_n': (1, 2, 0),
    'chair_s': (1, 2, 0), 'waiting_seat': (3, 2, 1), 'signpost': (1, 2, 1),
    'coolant_tank': (3, 4, 2), 'kitchenette': (4, 3, 1),
    'ore_pile': (3, 2, 1), 'hopper': (3, 4, 2), 'ingot_stack': (2, 2, 1), 'slag_bin': (2, 2, 1), 'sorting_machine': (4, 3, 2),
    'hazard_sign': (1, 2, 1), 'breaker_panel': (2, 3, 1), 'storage_shelf': (3, 3, 1), 'barrel_stack': (2, 2, 1), 'pallet': (2, 2, 1),
    'cargo_loader': (3, 3, 2),
})
SHIP_W, SHIP_H = 7, 4                 # the player's ship, in tiles (art/lunar/player_ship.png: 4 frames of 224 x 128)


def chamfer_room(F, x0, y0, x1, y1, ch, k=2):
    """Floor `ch` over the rectangle x0..x1, y0..y1 with its four corners cut off at 45 degrees (k tiles)."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if min(x - x0, x1 - x) + min(y - y0, y1 - y) >= k:
                F[y][x] = ch


def build(g):
    entries = []
    # ================================================================== eng: option E (Zachary, 17 Nov)
    # A rectangular works hall that loops round the geothermal power core, sunk in its own pit; the rooms
    # bulge out of the hall on 45-degree walls. Ore processing fills the west end, fed by conveyor belts from
    # the mine tunnel; cooling and life support bulge out south of the core, piped up into the pit.
    eng = Room(g, 'eng', 'Engineering Level', 120, 78)
    F, O = eng.F, eng.obj
    for y in range(1, 77):
        for x in range(1, 119):
            F[y][x] = '#'
    def poly(pts, ch, only=None):
        n = len(pts)
        for y in range(78):
            for x in range(120):
                px, py, inside = x + .5, y + .5, False
                for i in range(n):
                    (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
                    if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
                        inside = not inside
                if inside and (only is None or F[y][x] in only):
                    F[y][x] = ch
    def fill(x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1): F[y][x] = ch
    # --- the hall loop and the sunken core
    fill(40, 24, 100, 52, '.')
    chamfer_room(F, 48, 30, 92, 46, 'q', 5)                    # the drop round the pit (railed, not walkable)
    chamfer_room(F, 52, 33, 88, 43, 'k', 4)                    # the pit floor
    fill(48, 37, 51, 39, 'j'); fill(89, 37, 92, 39, 'j')       # stairs down, west and east
    # --- ore processing: two rooms and a short hall between them; the mine tunnel carries straight on west
    poly([(6, 33), (6, 18), (16, 8), (34, 8), (39, 13), (39, 33)], 'o')
    fill(6, 34, 39, 38, '.')
    poly([(6, 40), (39, 40), (39, 52), (31, 60), (6, 60)], 'o')
    for x in (13, 14, 15, 25, 26, 27): F[33][x] = F[39][x] = 'o'
    fill(1, 34, 5, 38, 'R')                                    # the mine tunnel runs straight on west from the hall (Zachary, 22 Nov)
    # --- Tikka's engineering bay: the whole north side; her office in the north-east corner, a drone pad
    poly([(48, 23), (48, 12), (54, 6), (90, 6), (96, 12), (96, 23)], 't')
    for x in range(68, 73): F[23][x] = '.'
    chamfer_room(F, 70, 10, 80, 18, 'a', 2)
    for y in range(6, 14): F[y][86] = '#'
    for x in range(86, 96): F[14][x] = '#'
    for y in range(6, 14):
        for x in range(87, 96):
            if F[y][x] == 't': F[y][x] = 'h'
    F[14][90] = F[14][91] = 'h'
    # --- lift (north-east), stores, the corridor to the shuttle bay, cargo staging and a spare workshop
    chamfer_room(F, 98, 15, 104, 22, '.', 1)
    for x in (98, 99, 100): F[23][x] = '.'
    lift = (101, 14)
    poly([(102, 24), (108, 24), (114, 30), (114, 35), (102, 35)], 'f')
    for y in (28, 29, 30): F[y][101] = 'f'
    fill(101, 36, 116, 40, '.')
    eng_door = (117, 38); F[eng_door[1]][eng_door[0]] = '.'
    poly([(102, 42), (115, 42), (115, 52), (107, 60), (102, 60)], 'f')
    for y in (45, 46, 47): F[y][101] = 'f'
    chamfer_room(F, 98, 62, 110, 71, 'f', 3)
    for x in (103, 104, 105): F[60][x] = F[61][x] = 'f'
    # --- south side: crew break room (big), cooling & life support, a spare workshop
    poly([(40, 54), (57, 54), (57, 68), (51, 74), (38, 74), (32, 68), (32, 62)], 'h')
    for x in (46, 47, 48): F[53][x] = '.'
    poly([(58, 54), (83, 54), (83, 64), (77, 70), (64, 70), (58, 64)], 'e')
    for x in (69, 70, 71): F[53][x] = '.'
    chamfer_room(F, 85, 54, 96, 64, 'f', 3)
    for x in (89, 90, 91): F[53][x] = '.'
    # the drop is not walkable
    for y in range(78):
        for x in range(120):
            if F[y][x] == 'q': O[y][x] = 'x'
    eng.t.zones += [['Ore processing', 6, 8, 38, 32], ['Ore sorting', 6, 40, 38, 59], ['Geothermal power core', 48, 30, 92, 46],
                    ["Tikka's engineering bay", 48, 6, 95, 22], ["Tikka's office", 87, 6, 95, 13], ['Lift', 98, 15, 104, 22],
                    ['Stores', 102, 24, 113, 34], ['Cargo staging', 102, 42, 114, 59], ['Spare workshop', 98, 62, 110, 71],
                    ['Crew break room', 32, 54, 56, 73], ['Cooling & life support', 58, 54, 82, 69], ['Spare workshop', 85, 54, 96, 64],
                    ['Engineering works hall', 40, 24, 100, 52], ['Engineering works hall', 6, 34, 39, 38]]
    eng.t.warp('U', [lift], 'main', 115, 169)                   # tools/concourse.py makes this a lift door
    eng.t.warp('R', [(1, y) for y in range(34, 39)], 'mine', 66, 25)   # tools/caves.py ENG_LANDING
    bay_door = (3, 18)
    # keep the walking lanes of the hall and every doorway clear
    eng.keep_clear(40, 24, 100, 27); eng.keep_clear(40, 49, 100, 52); eng.keep_clear(40, 24, 45, 52); eng.keep_clear(95, 24, 100, 52)
    eng.keep_clear(6, 35, 39, 37); eng.keep_clear(1, 34, 9, 38); eng.keep_clear(101, 37, 117, 39)
    for (x0, y0, x1, y1) in ((12, 31, 16, 41), (24, 31, 28, 41), (67, 21, 73, 26), (97, 21, 101, 26), (99, 27, 103, 31), (99, 44, 103, 48),
                             (45, 51, 49, 56), (68, 51, 72, 56), (88, 51, 92, 56), (102, 58, 106, 63), (89, 13, 92, 16), (46, 36, 54, 40), (86, 36, 94, 40)):
        eng.keep_clear(x0, y0, x1, y1)
    P = eng.prop; N = eng.near
    # ore processing: the belt from the mine runs up the west side to the crusher, then on to the furnaces
    N('ore_crusher', 20.5, 18.5, 'Ore crusher', 'look', 'Look')
    for x in (29, 33): P('furnace', x, 9, 'Furnace', 'furnace', 'Smelt what you are holding')
    N('pipe_rack', 36, 16.5, 'Slag chute', None); N('ore_cart', 23, 24.5, 'Ore cart', None); N('ore_cart', 9, 30.5, 'Ore cart', None)
    N('terminal', 18, 27.5, 'Belt control'); N('pump', 9, 21.5, 'Dust extractor', None); N('cargo', 36, 30.5, 'Ingot crates', None)
    N('parts_rack', 20, 46.5, 'Ore bins', None); N('parts_rack', 30, 46.5, 'Ore bins', None); N('ore_cart', 22, 55.5, 'Ore cart', None)
    N('ore_cart', 10, 44.5, 'Ore cart', None); N('console', 33, 52.5, 'Sorting console'); N('cargo', 9, 50.5, 'Rock samples', None)
    # more for the ore rooms: the hopper where the ore chute from the mine comes through the wall, the sorter on the belt, heaps of ore, ingots, slag
    N('hopper', 9.5, 52.5, 'Ore hopper', 'look', 'Look'); N('sorting_machine', 15, 46.5, 'Ore sorter', 'look', 'Look')
    N('ore_pile', 25, 52.5, 'Heap of ore', None); N('ore_pile', 22, 57.5, 'Heap of ore', None); N('slag_bin', 34, 56.5, 'Slag bin', None)
    N('hazard_sign', 18, 42.5, 'Warning: moving belt', None); N('barrel_stack', 36, 42.5, 'Flux barrels', None)
    N('ingot_stack', 30, 25.5, 'Ingots', None); N('ingot_stack', 34, 25.5, 'Ingots', None); N('slag_bin', 37, 20.5, 'Slag bin', None)
    N('ore_pile', 17, 14.5, 'Heap of crushed ore', None); N('hazard_sign', 27, 12.5, 'Warning: hot metal', None)
    N('locker', 21, 10, 'Smelters\' lockers', None); N('locker', 24, 10, 'Smelters\' lockers', None); N('breaker_panel', 9, 27.5, 'Breaker panel')
    N('air_scrubber', 11, 18, 'Fume extractor', None)
    # the power core in its pit: control panels down both long sides, coolant tanks at the ends
    P('geo_core', 68, 36, 'Geothermal power core', 'look', 'Look')
    P('coolant_tank', 55, 36, 'Coolant tank', None); P('coolant_tank', 83, 36, 'Coolant tank', None)
    for x in (58, 63, 76, 81): N('console', x, 34.5, 'Core control panel')
    for x in (59, 66, 74): N('sensor_panel', x, 43.0, 'Core read-outs')
    for x in (50, 58, 66, 74, 82, 90): N('bollard_light', x, 29.0, 'Rail light', None); N('bollard_light', x, 47.6, 'Rail light', None)
    N('signpost', 43, 30.5, 'Direction post', None); N('terminal', 97, 30.5, 'Engineering directory')
    # Tikka's engineering bay
    N('workbench', 52.5, 8.5, "Tikka's workbench", 'repair', 'Inspect tools'); N('workbench', 52.5, 13.5, 'Workbench', None)
    N('wall_screen', 61, 7.5, 'Systems board'); N('sensor_panel', 66, 8, 'Station read-outs'); N('console', 61, 12.5, 'Diagnostics console')
    N('tool_cart', 57, 12, 'Tool cart', None); N('welding_rig', 51, 19, 'Welding rig'); N('parts_rack', 57, 20.5, 'Parts rack', None)
    N('test_rig', 75, 14.5, 'Drone test rig', 'look', 'Look'); N('locker', 83, 9, 'Tool lockers', None)
    N('parts_rack', 84, 20.5, 'Spare parts', None); N('pipe_rack', 92, 19.5, 'Pipe stock', None); N('fuel_tank', 81, 16.5, 'Gas bottles', None)
    N('console', 89.5, 8.5, "Tikka's desk"); N('books', 94, 8.5, "Tikka's manuals", None); N('star_chart', 93.5, 12.5, 'Station blueprints')
    N('plants', 88.5, 12.5, 'Office plant', 'inspect', 'Inspect')
    # lift lobby
    N('plants', 103.5, 17.5, 'Lift planter', 'inspect', 'Inspect')
    # stores
    for fx in (103.5, 106.5): N('storage_shelf', fx, 26.5, 'Stores shelving', None)
    for fx in (104.5, 107.5, 110.5): N('storage_shelf', fx, 34.5, 'Stores shelving', None)
    N('breaker_panel', 110, 29, 'Breaker panel'); N('barrel_stack', 107.5, 30.5, 'Lubricant barrels', None)
    N('terminal', 104, 31.5, 'Stores inventory')
    # cargo staging: the loading pad for Bram's crates; the belt ends here
    for fx in (104.5, 107.5, 110.5): N('storage_shelf', fx, 44.5, 'Cargo racks', None)
    N('pallet', 104, 55.5, 'Pallet of sacks', None); N('pallet', 113, 47.5, 'Pallet of sacks', None); N('barrel_stack', 113, 51.5, 'Fuel barrels', None)
    N('cargo_loader', 109.5, 56.5, 'Cargo loader', 'look', 'Look'); N('cargo', 104, 51.5, 'Cargo crates', None); N('breaker_panel', 114, 44.5, 'Loading panel')
    drop = (109, 50)
    eng.keep_clear(107, 48, 111, 52)
    eng.thing('drop', 'Loading pad', 'Set down the crate', *drop, 22)
    # cooling & life support: three big coolant tanks, pumps, scrubbers
    for x in (62, 68, 74): N('coolant_tank', x + 1.5, 65.5, 'Coolant tank', None)
    for x in (61, 66, 75, 80): N('pump', x, 57.5, 'Coolant pump', 'inspect', 'Inspect')
    N('breaker_panel', 72, 56.5, 'Pump controls');     N('air_scrubber', 80, 63.5, 'Air scrubber'); N('water_tank', 61, 63.5, 'Water reserve', None); N('pipe_rack', 70.5, 69.5, 'Pipe manifold', None)
    # the crew break room: four tables, lockers, a kitchenette
    for tx, ty in ((42, 58), (49, 58), (42, 64), (49, 64)):
        P('table', tx, ty, 'Break table', None)
        P('chair_s', tx + 1, ty - 2, 'Chair [S]', 'seat', 'Sit'); P('chair_n', tx + 1, ty + 2, 'Chair [N]', 'seat', 'Sit')
    for y in (58, 62): N('locker', 35, y + 1.5, 'Crew lockers', None)
    N('kitchenette', 44.5, 72.5, 'Kitchenette', 'inspect', 'Make a cup of tea'); N('drinking_fountain', 53, 70.5, 'Water point', 'inspect', 'Inspect')
    N('bin', 55, 56.5, 'Recycling bin', None); N('plants', 36, 69.5, 'Break room plant', 'inspect', 'Inspect')
    N('bench_n', 51, 72.5, 'Break room bench [N]', 'seat', 'Sit')
    # spare workshops: a few crates and an empty bench, waiting for someone
    for (x0, y0, x1, y1) in ((85, 54, 96, 64), (98, 62, 110, 71)):
        N('cargo', x0 + 3, y0 + 4.5, 'Spare crates', None); N('workbench', x1 - 3, y0 + 4.5, 'Empty workbench', 'inspect', 'Inspect')
    # conveyor belts, coolant pipes and power cables, painted into the floor
    belts = [[(6, 55.5), (14.5, 55.5), (14.5, 23), (19, 18.5)], [(23, 18.5), (27, 18.5), (27, 13), (29, 12)],
             [(31.5, 13), (31.5, 23)]]                                     # furnaces to the ingot stacks; nothing leaves the ore rooms
    pipes = [[(65.5, 63), (65.5, 44)], [(74.5, 63), (74.5, 44)]]
    cables = [[(70.5, 33), (70.5, 24.5), (100.5, 24.5), (100.5, 52.5)], [(48, 38.5), (40.5, 38.5), (40.5, 24.5)], [(40.5, 36), (6.5, 36)]]
    g.setdefault('FLOOR_EXTRAS', {})['eng'] = {'belts': belts, 'pipes': pipes, 'cables': cables, 'core': [70.5, 38],
                                      'pit': [[48, 30, 93, 47, 4.6], [52, 33, 89, 44, 3.6]]}

    # ================================================================== bay: the shuttle bay
    bay = Room(g, 'bay', 'Shuttle Bay', 50, 38)
    B = bay.F
    for y in range(2, 37):
        for x in range(1, 49):
            B[y][x] = '#'
    chamfer_room(B, 4, 6, 46, 34, 'u', 4)
    # big windows along the north wall, either side of the launch doors
    for x in range(4, 47):
        if B[6][x] == 'u' and not 18 <= x <= 29:
            B[5][x] = 'w'
    # Freya's work area (decking), the ship's pad, the tarp fighter's pad
    chamfer_room(B, 5, 8, 12, 16, 'p', 1)
    chamfer_room(B, 17, 12, 30, 20, 'a', 2)
    chamfer_room(B, 35, 9, 45, 16, 'a', 2)
    # launch control booth (south-west) and the Shipwright's Suite (south-east), walled with 45-degree corners
    for (x0, y0, x1, y1) in ((4, 26, 13, 34), (36, 25, 46, 34)):
        for y in range(y0 - 1, y1 + 1):
            for x in range(x0 - 1, x1 + 2):
                if B[y][x] != '~': B[y][x] = '#'
    chamfer_room(B, 5, 27, 12, 33, 'f', 1)
    chamfer_room(B, 37, 26, 46, 33, 'f', 2)
    for x in (8, 9, 10): B[25][x] = B[26][x] = 'u'                      # booth doorway
    for y in (28, 29, 30): B[y][35] = B[y][36] = 'u'                      # suite doorway (blocked by its locked door)
    B[bay_door[1]][bay_door[0]] = 'u'
    bay.keep_clear(4, 17, 14, 19); bay.keep_clear(7, 23, 11, 26)
    BP = bay.prop; BN = bay.near
    ship_x, ship_y = 20, 14                                     # top-left tile of the ship
    for y in range(ship_y + 2, ship_y + SHIP_H):
        for x in range(ship_x, ship_x + SHIP_W):
            bay.obj[y][x] = 'x'
    for x, y in ((18, 13), (29, 13), (18, 19), (29, 19)): BP('mag_clamp', x, y, 'Magnetic clamp', None)
    wreck = ['bay', int((ship_x + SHIP_W / 2) * 16), int((ship_y + SHIP_H) * 16)]
    bay.thing('wreck', 'Your ship', 'Your ship', ship_x + 3, ship_y + 2.5, 60)
    # the tarp-covered fighter: 9 x 5 tiles, its lower three rows solid
    tx, ty = 36, 10
    bay.props.append(['tarp_fighter', tx, ty, 9, 5, 'Covered fighter'])
    for y in range(ty + 2, ty + 5):
        for x in range(tx, tx + 9): bay.obj[y][x] = 'x'
    bay.thing('look', 'Covered fighter', 'Look', tx + 4, ty + 4, 40)
    # launch doors across the middle of the north wall (a picture over the wall)
    bay.props.append(['launch_door', 18, 3, 12, 3, 'Launch doors'])
    bay.thing('look', 'Launch doors', 'Look', 23.5, 6, 40)
    bay.thing('look', 'Hangar windows', 'Look outside', 9, 6, 30); bay.thing('look', 'Hangar windows', 'Look outside', 40, 6, 30)
    # Freya's work area
    BN('workbench', 7.5, 9.5, "Freya's workbench", 'repair', 'Inspect tools'); BN('tool_cart', 11, 12.5, 'Tool cart', None)
    BN('welding_rig', 6, 15.5, 'Welding rig'); BN('parts_rack', 10.5, 15.5, 'Ship parts', None)
    # around the pad and along the south wall
    BN('trolley', 14, 23.5, 'Parts trolley', None); BN('tool_cart', 32.5, 13.5, 'Tool cart', None)
    for fx in (17.5, 22.5, 27.5): BN('parts_rack', fx, 33.5, 'Parts rack', None)
    BN('fuel_tank', 32, 33.5, 'Fuel tank'); BN('fuel_tank', 15, 28.5, 'Fuel tank')
    BN('cargo', 33, 26.5, 'Crates', None)
    # launch control booth
    BN('launch_console', 8.5, 28.5, 'Launch control', 'launch', 'Launch'); BN('waiting_seat', 8.5, 32.5, 'Booth seats', None)
    # the Shipwright's Suite: locked; a few of Freya's father's things inside
    BP('lab_door', 35, 28, "Shipwright's Suite", 'look', 'Look', door=True)
    BN('workbench', 41.5, 27.5, "Old shipwright's bench", None); BN('star_chart', 44, 31.5, 'Hull blueprints', None)
    BN('books', 38.5, 31.5, "Shipwright's logbooks", None)
    bay.t.zones += [['Shuttle bay', 4, 6, 46, 24], ["Freya's work area", 5, 8, 12, 16], ['Launch control', 5, 27, 12, 33],
                    ["Shipwright's Suite", 37, 26, 46, 33]]

    # ================================================================== doors
    warps = {'eng': eng.t.warps, 'bay': bay.t.warps}
    door_pair(entries, warps, 'eng', eng_door, 'W', 'bay', bay_door, 'E', 'Shuttle bay', 'To Engineering')
    g['MAP_PARENT']['bay'] = ['eng', eng_door[0] - 1, eng_door[1]]
    for room in (eng, bay):
        g.setdefault('AREA_PROPS', {})[room.key] = room.props
        g.setdefault('AREA_ROOF_PROPS', {})[room.key] = []
        g.setdefault('AREA_LIGHTS', {})[room.key] = []
        g.setdefault('EXTRA_THINGS', []).extend(room.things)
    g['ENG_ENTRANCES'] = entries
    g['WRECK_SPOT'] = wreck
    return eng.t
