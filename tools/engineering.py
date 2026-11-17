"""Engineering (area "eng") and the shuttle bay (area "bay"), approved by Zachary on 17 Nov.

eng  a long rectangular works floor between the mine ramp (west) and the shuttle bay doors (east), rooms
     along both sides: ore processing, the geothermal power core, the lift, Tikka's engineering bay and two
     spare workshops on the north; life support, stores, the crew break room, two spare workshops and cargo
     staging on the south. Every room has 45-degree plates in its corners.
bay  the shuttle bay, its own map: a hangar cut into the crater wall, with big windows along the north wall
     either side of the launch doors, your ship on its pad, a bigger fighter under a tarp, Freya's work area,
     the launch control booth and the (locked) Shipwright's Suite.
Drawn in the promenade style; walls faceted by tools/bake_floor.py."""
import math
import survey
from survey import Room, SIZES, door_pair

survey.WALKABLE = 'uihsmf.apR'
SIZES.update({
    'geo_core': (5, 4, 3), 'furnace': (2, 3, 1), 'ore_crusher': (3, 3, 2), 'ore_cart': (2, 2, 1), 'pump': (2, 3, 1),
    'pipe_rack': (3, 2, 1), 'locker': (2, 3, 1), 'tool_cart': (2, 2, 1), 'welding_rig': (2, 3, 1), 'fuel_tank': (2, 3, 1),
    'parts_rack': (3, 3, 1), 'launch_console': (3, 2, 1), 'air_scrubber': (2, 3, 1), 'mag_clamp': (1, 1, 0),
    'workbench': (3, 2, 1), 'table': (3, 2, 1), 'trolley': (2, 2, 1), 'water_tank': (2, 2, 1), 'bollard_light': (1, 1, 1),
    'bin': (1, 1, 1), 'drinking_fountain': (1, 2, 1), 'lamp_post': (1, 2, 1), 'bench_s': (3, 2, 1), 'chair_n': (1, 2, 0),
    'chair_s': (1, 2, 0), 'waiting_seat': (3, 2, 1), 'signpost': (1, 2, 1),
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
    # ================================================================== eng: the works floor
    eng = Room(g, 'eng', 'Engineering Level', 100, 46)
    F = eng.F
    for y in range(3, 44):
        for x in range(1, 98):
            F[y][x] = '#'
    chamfer_room(F, 6, 20, 93, 27, '.', 2)                     # the works floor
    for y in range(22, 26):
        for x in range(2, 7): F[y][x] = '.'                   # ramp down to the mine
    north = [('ore', 'Ore processing', 7, 21), ('core', 'Geothermal power core', 24, 37), ('lift', 'Lift', 40, 46),
             ('tikka', "Tikka's engineering bay", 49, 62), ('spareA', 'Spare workshop', 65, 74), ('spareB', 'Spare workshop', 77, 92)]
    south = [('life', 'Life support', 7, 24), ('stores', 'Stores', 27, 36), ('break', 'Crew break room', 39, 50),
             ('spareC', 'Spare workshop', 53, 62), ('spareD', 'Spare workshop', 65, 74), ('cargo', 'Cargo staging', 77, 92)]
    rooms = {}
    for key, title, x0, x1 in north:
        y0 = 12 if key == 'lift' else 6
        chamfer_room(F, x0, y0, x1, 18, '.' if key == 'lift' else 'f', 1 if key == 'lift' else 2)
        mid = (x0 + x1) // 2
        for x in (mid - 1, mid, mid + 1): F[19][x] = '.'
        rooms[key] = (title, x0, y0, x1, 18)
    for key, title, x0, x1 in south:
        chamfer_room(F, x0, 29, x1, 40, 'f', 2)
        mid = (x0 + x1) // 2
        for x in (mid - 1, mid, mid + 1): F[28][x] = '.'
        rooms[key] = (title, x0, 29, x1, 40)
    eng.t.zones += [[t, x0, y0, x1, y1] for (t, x0, y0, x1, y1) in rooms.values()] + [['Engineering works floor', 6, 20, 93, 27]]
    lift = (43, 11)
    eng.t.warp('U', [lift], 'main', 115, 169)                   # tools/concourse.py makes this a lift door
    eng.t.warp('R', [(2, 22), (2, 23), (2, 24), (2, 25)], 'mine', 38, 4)
    eng_door, bay_door = (94, 23), (3, 18)
    F[eng_door[1]][eng_door[0]] = '.'
    # keep the middle of the works floor, every doorway and the lift clear
    eng.keep_clear(3, 22, 93, 25); eng.keep_clear(42, 12, 44, 21)
    for _, _, x0, x1 in north + south:
        mid = (x0 + x1) // 2; eng.keep_clear(mid - 1, 17, mid + 1, 21); eng.keep_clear(mid - 1, 26, mid + 1, 30)
    P = eng.prop; N = eng.near
    # ore processing: two furnaces, a crusher, ore carts
    for x in (9, 13):
        P('furnace', x, 6, 'Furnace', 'furnace', 'Smelt what you are holding')
    N('ore_crusher', 18.5, 9.5, 'Ore crusher'); N('ore_cart', 10, 13, 'Ore cart', None); N('ore_cart', 18, 15, 'Ore cart', None)
    N('pipe_rack', 9.5, 17.5, 'Slag chute', None)
    # the geothermal power core
    P('geo_core', 28, 9, 'Power core', 'look', 'Look')
    N('console', 26, 16.5, 'Core monitor'); N('console', 34, 16.5, 'Core monitor'); N('pump', 25.5, 8, 'Heat exchanger', None); N('pump', 36, 8, 'Heat exchanger', None)
    # lift lobby
    N('terminal', 41, 13.5, 'Engineering directory'); N('plants', 45, 17.5, 'Lift planter', 'inspect', 'Inspect')
    # Tikka's engineering bay
    N('workbench', 52, 8.5, 'Tikka\'s workbench', 'repair', 'Inspect tools'); N('tool_cart', 57, 8.5, 'Tool cart', None)
    N('welding_rig', 60.5, 9, 'Welding rig'); N('parts_rack', 51.5, 15.5, 'Parts rack'); N('console', 59, 15.5, 'Diagnostics console')
    N('wall_screen', 55.5, 7.5, 'Systems board')
    # spare workshops: a few crates and an empty bench, waiting for someone
    for key in ('spareA', 'spareB', 'spareC', 'spareD'):
        _, x0, y0, x1, y1 = rooms[key]
        N('cargo', x0 + 3, y0 + 3.5, 'Spare crates', None); N('workbench', x1 - 3, y0 + 3.5, 'Empty workbench', 'inspect', 'Inspect')
    # life support: pumps, scrubbers, water
    for fx, fy in ((10, 32.5), (14, 32.5), (18, 32.5)): N('pump', fx, fy, 'Heating pump', 'inspect', 'Inspect')
    N('air_scrubber', 22, 32.5, 'Air scrubber'); N('water_tank', 10, 38.5, 'Water reserve', None); N('water_tank', 21, 38.5, 'Water reserve', None)
    N('pipe_rack', 15.5, 38.5, 'Pipe manifold', None)
    # stores
    for fx, fy in ((29.5, 32.5), (34.5, 32.5)): N('parts_rack', fx, fy, 'Stores shelving', None)
    N('cargo', 29, 38.5, 'Stored crates', None); N('cargo', 34, 38.5, 'Stored crates', None)
    # crew break room
    N('locker', 41, 32.5, 'Crew lockers', None); N('locker', 48, 32.5, 'Crew lockers', None)
    N('table', 43.5, 36.5, 'Break table'); N('drinking_fountain', 49, 38.5, 'Water point', 'inspect', 'Inspect'); N('bin', 40, 39.5, 'Recycling bin', None)
    N('bench_n', 44.5, 39.5, 'Break room bench [N]', 'seat', 'Sit')
    # cargo staging: the loading pad for Bram's crates
    N('cargo', 80, 32.5, 'Cargo crates', None); N('cargo', 89, 32.5, 'Cargo crates', None); N('trolley', 85, 38.5, 'Cargo trolley', None)
    drop = (84, 34)
    eng.thing('drop', 'Loading pad', 'Set down the crate', *drop, 22)
    # along the works floor: lights, carts and a direction post
    for x in range(10, 92, 8):
        N('bollard_light', x, 21.0, 'Floor light', None)
        N('bollard_light', x + 4, 26.6, 'Floor light', None)
    N('signpost', 47.5, 21.5, 'Direction post', None); N('ore_cart', 20, 26.5, 'Ore cart', None)

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
    BN('launch_console', 8.5, 28.5, 'Launch control', 'look', 'Look'); BN('waiting_seat', 8.5, 32.5, 'Booth seats', None)
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
