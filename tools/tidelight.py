"""Tidelight (Zachary, 24 Nov): the world the Great Storm hid, open once the Shepherd of Storms lays the storm to rest
(docs/story/CUSTODIANS.md). Tidally locked, so wherever you can go it is sunset: scripts/main.gd _light_color keeps
the map in a low golden light, always.

West to east, from the sunward edge to the night side:
    the sea      warm water to the map's west edge, with a dock out into it
    the beach    sand, a few boulders, fishing spots off the dock
    the village  sunset grass: a landing pad for the shuttle at the north, the settlers' prefab homes (walled blocks
                 drawn with the East Complex's materials), the old Collective distress beacon on its mast, a market
                 stall, a beach bar, lamps and a campfire
    the forest   dark forest floor running into the night: trees, glowing fungus and crystals, and in a clearing at
                 the far east the Warden of Tidelight's crystal
Cliffs close the north and south. You arrive on the landing pad (TIDELIGHT_LANDING) by shuttle or your own ship
(main.gd); there is no warp to it. Forage spots are things of kind "forage" (main.gd picks them, and they grow
back the next day).
"""
import math
import random
import survey
from survey import Room, SIZES

SIZES.setdefault('tarp_fighter', (9, 5, 3))
SIZES.setdefault('beacon_mast', (3, 4, 2))
SIZES.setdefault('market_counter', (3, 2, 1))
SIZES.setdefault('bar_table', (3, 2, 1))
SIZES.setdefault('bar_stool', (1, 2, 0))
W, H = 86, 50
LANDING = (38, 11)                    # where you arrive (the foot of the landing pad)
WARDEN = (77, 24)                     # the Warden's crystal (a pedestal in the clearing)
WALK = 'jeukpf'                       # beach (sand), grass, path, forest, dock, pad


def fill(F, x0, y0, x1, y1, ch, only=None):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if only is None or F[y][x] in only:
                F[y][x] = ch


def band_x(y, base, amp, phase, wobble=.21):
    """An x that wanders with y: the edges between sea, sand, grass and forest."""
    return int(round(base + amp * math.sin(y * wobble + phase) + amp * .5 * math.sin(y * wobble * 2.3 + phase * 1.7)))


def build(g):
    survey.WALKABLE = WALK
    T = Room(g, 'tidelight', 'Tidelight', W, H)
    F = T.F
    fill(F, 0, 0, W - 1, H - 1, '#')
    rnd = random.Random(42)
    top = [3 + int(1.5 * math.sin(x * .3) + rnd.random()) for x in range(W)]           # the cliffs, north and south
    bottom = [H - 4 - int(1.5 * math.sin(x * .27 + 1) + rnd.random()) for x in range(W)]
    for x in range(1, W - 1):
        for y in range(top[x], bottom[x] + 1):
            sea = band_x(y, 12, 1.5, 0.4)
            sand = band_x(y, 25, 1.6, 2.0)
            woods = band_x(y, 57, 2.2, 4.1, .17)
            F[y][x] = 'Y' if x <= sea else 'j' if x <= sand else 'e' if x < woods else 'k'
    for y in range(1, H - 1):                       # the sea runs right out to the west edge
        for x in range(1, 4):
            if F[y][x] == '#' and y > 1 and y < H - 2:
                F[y][x] = 'Y'
    # the dock, out into the sea
    fill(F, 5, 24, 15, 25, 'p')
    # the landing pad, and paths from it to the beach, the beacon and the forest
    fill(F, 33, 4, 43, 10, 'f')
    fill(F, 37, 11, 39, 31, 'u', 'ej')
    fill(F, 16, 30, 57, 32, 'u', 'ej')
    fill(F, 56, 23, 70, 24, 'u', 'ek')
    # the settlers' homes: prefab blocks with roofs (bake_floor HOUSE_FRONTS), doors on their south faces
    homes = [(27, 13, 32, 18), (44, 13, 49, 18), (27, 35, 32, 40), (44, 35, 49, 40)]
    for x0, y0, x1, y1 in homes:
        fill(F, x0, y0, x1, y1, '#')
    T.keep_clear(LANDING[0] - 2, LANDING[1] - 1, LANDING[0] + 2, LANDING[1] + 2)
    T.keep_clear(36, 11, 40, 33)
    T.keep_clear(15, 29, 58, 33)
    T.keep_clear(4, 23, 16, 26)
    T.keep_clear(55, 22, 71, 25)
    for x0, y0, x1, y1 in homes:
        T.keep_clear(x0 - 1, y1 + 1, x1 + 1, y1 + 2)
    P, N = T.prop, T.near
    # the pad: the shuttle (a covered ship for now) and the way home
    N('tarp_fighter', 38, 9, 'The shuttle', 'shuttle', 'Fly home')
    # the village
    N('beacon_mast', 52, 27, 'The old Collective beacon', 'look', 'Look')
    N('market_counter', 30, 27, "Settlers' market", 'look', 'Look')
    N('market_counter', 22, 28, 'Beach bar', 'look', 'Look')
    N('brazier', 41, 25, 'Campfire', 'look', 'Look')
    N('bench_s', 41, 22, 'Log bench [S]', 'seat', 'Sit')
    for lx, ly in ((34, 12), (42, 12), (34, 29), (42, 29), (24, 31), (55, 31)):
        N('lamp_post', lx, ly, 'Lamp', None)
    for x0, y0, x1, y1 in homes:
        T.thing('look', "A settler's home", 'Look', (x0 + x1) / 2, y1 + 1, 30)
        N('flowers', x0 + 1, y1 + 2.5, 'Window box', None)
    N('barrel_stack', 50, 20, 'Rain barrels', None)
    N('cargo', 33, 21, 'Supply crates', 'look', 'Look')
    # the beach
    for bx, by in ((18, 10), (20, 41), (16, 17)):
        N('boulder', bx, by, 'Boulder', None)
    T.thing('look', 'Fishing spot: the dock', 'Look', 6, 24.5, 36)
    T.thing('look', 'The endless sunset', 'Look', 14, 14, 50)
    # the forest: trees thick at the edges, thinner along the path, a clearing for the Warden
    for tx, ty in ((60, 8), (64, 12), (68, 7), (72, 11), (62, 18), (66, 30), (70, 34), (61, 38), (75, 40), (80, 33),
                   (83, 15), (58, 43), (66, 44), (73, 8), (79, 9), (82, 41), (62, 28), (70, 16), (81, 28)):
        N('park_tree', tx, ty, 'Dusk tree', None)
    for fx, fy in ((59, 13), (67, 20), (64, 35), (74, 36), (78, 18), (71, 29), (83, 22)):
        N('glow_fungus', fx, fy, 'Glowing fungus', None)
    for fx, fy in ((74, 20), (80, 27)):
        N('crystal_cluster', fx, fy, 'Glow crystals', 'inspect', 'Inspect')
    T.prop('crystal_pedestal', WARDEN[0], WARDEN[1], 'Precursor crystal', 'look', 'Look')
    T.keep_clear(WARDEN[0] - 2, WARDEN[1] + 3, WARDEN[0] + 3, WARDEN[1] + 4)       # room to stand in front of it
    # forage that grows back each day (main.gd "forage" things): sun-lilies on the sand, plankton at the tideline,
    # ember asters in the village, resin, hardwood and glow-moss in the forest
    forage = [('sun_lily', 19, 12), ('sun_lily', 22, 22), ('sun_lily', 18, 38), ('bio_plankton', 15, 9), ('bio_plankton', 15, 36),
              ('ember_aster', 35, 34), ('ember_aster', 47, 23), ('resin', 63, 22), ('hardwood', 69, 38), ('hardwood', 76, 13),
              ('glow_moss', 72, 26), ('glow_moss', 60, 34)]
    for item, fx, fy in forage:
        assert F[fy][fx] in WALK, ('forage on a wall', item, fx, fy)
        T.thing('forage', item, 'Pick', fx, fy, 22)
    T.t.zones += [['The landing pad', 33, 4, 43, 10], ['The beach', 13, 1, 26, H - 2], ['The village', 26, 1, 56, H - 2],
                  ['The dusk forest', 56, 1, W - 2, H - 2], ['The sea', 1, 1, 13, H - 2], ['Tidelight', 1, 1, W - 2, H - 2]]
    assert T.free(*LANDING, door=True), 'landing blocked'
    g.setdefault('AREA_PROPS', {})['tidelight'] = T.props
    g.setdefault('AREA_ROOF_PROPS', {})['tidelight'] = []
    g.setdefault('AREA_LIGHTS', {})['tidelight'] = []
    g.setdefault('EXTRA_THINGS', []).extend(T.things)
    g.setdefault('LUNAR_EXTRA', {})['Tidelight'] = 'tidelight'
    g['MAP_PARENT']['tidelight'] = ['west', 22, 26]          # on the station map: Gate 2, where the shuttle leaves
    g['TIDELIGHT_LANDING'] = list(LANDING)
    g['TIDELIGHT_WARDEN'] = list(WARDEN)
    import bake_floor
    bake_floor.AREA_FLOORS['tidelight'] = {
        'j': ('tidelight/sand', None), 'e': ('tidelight/grass', None), 'k': ('tidelight/forest', None),
        'u': ('east/stones', ('ffb070', .18)), 'p': ('east/dock', ('ff9a5a', .2)), 'f': ('eng_floor_concrete', ('ffb070', .2)),
        'Y': ('lake/water', ('b0607a', .2)),
    }
    bake_floor.SECTOR_WALLS['tidelight'] = ('lake/roof', 'lake/wall')
    bake_floor.HOUSE_FRONTS['tidelight'] = [
        {"roof": (x0, y0, x1, y1), "cuts": (1, 1, 0, 0), "front": (x0, y0, x1, y1 + 1), "roof_art": 'hotel/cap_mix', "wall_art": 'east/wall'}
        for x0, y0, x1, y1 in homes]
    return T
