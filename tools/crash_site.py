"""The crash site (24 Nov 2026): the cavern your ship fell into, where the Mother-Drone lies. Only the prologue
comes here (scripts/story_scenes.gd "prologue" goes to it under a fade), so it has no way in or out.

A rough oval cavern in the mine's rock, built and baked like the other caverns: your ship's front half nose-down in
a heap of basalt on the west (art/lunar/crash_wreck.png), the Mother-Drone half sunk in the floor on the east
(art/lunar/mother_drone.png), stalagmites, boulders, glowing fungus and crystals round the walls. Cool light falls
on the wreck from the hole it made; the fire at its torn end and the drone's glow light the rest (CAVE_LIGHTS).
The two props, and where they stand, are drawn by tools/dev/crash_site_art.py, which also lines up the drone's
animation and the beam with them.
"""
import math
import random
import survey
from survey import Room, SIZES

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dev"))

W, H = 46, 30
SPOT = (21, 16)                       # where the (hidden) player stands, so the camera frames wreck and drone
WRECK_AT, WRECK_SIZE = (7, 12), (8, 5)
DRONE_AT, DRONE_SIZE = (25, 8), (10, 6)
SIZES.update({'crash_wreck': (WRECK_SIZE[0], WRECK_SIZE[1], 3), 'mother_drone': (DRONE_SIZE[0], DRONE_SIZE[1], 4)})
SIZES.setdefault('stalagmite', (1, 2, 1))
SIZES.setdefault('boulder', (2, 2, 1))
SIZES.setdefault('glow_fungus', (1, 1, 1))
SIZES.setdefault('crystal_cluster', (2, 2, 1))


def build(g):
    survey.WALKABLE = 'ms'
    R = Room(g, 'crash_site', 'The crash site', W, H)
    F = R.F
    for y in range(H):
        for x in range(W):
            F[y][x] = '#'
    rnd = random.Random(9)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            dx, dy = (x + .5 - 23) / 20.5, (y + .5 - 15.5) / 12.5
            k = 1 + .06 * math.sin(math.atan2(dy, dx) * 5 + 1) + .04 * math.sin(math.atan2(dy, dx) * 9)
            if dx * dx + dy * dy <= k * k:
                F[y][x] = 'm'
    R.keep_clear(SPOT[0] - 1, SPOT[1] - 1, SPOT[0] + 1, SPOT[1] + 1)
    R.prop('crash_wreck', WRECK_AT[0], WRECK_AT[1], 'Your ship', None)
    R.prop('mother_drone', DRONE_AT[0], DRONE_AT[1], 'The Mother-Drone', None)
    N = R.near
    for x, y in ((5, 8), (10, 6), (16, 5), (31, 5), (38, 7), (41, 13), (40, 20), (33, 24), (24, 25), (14, 24), (6, 21), (3, 15)):
        N('stalagmite', x, y, 'Stalagmite', None)
    for x, y in ((18, 9), (20, 21), (37, 18), (8, 20)):
        N('boulder', x, y, 'Boulder', None)
    for x, y in ((12, 7), (35, 6), (42, 16), (28, 24), (4, 18), (19, 25)):
        N('glow_fungus', x, y, 'Glowing fungus', None)
    for x, y in ((37, 22), (27, 5)):
        N('crystal_cluster', x, y, 'Glow crystals', None)
    assert R.free(*SPOT, door=True), 'the camera spot is blocked'
    R.t.zones.append(['The crash site', 1, 1, W - 2, H - 2])
    g.setdefault('AREA_PROPS', {})['crash_site'] = R.props
    g.setdefault('AREA_ROOF_PROPS', {})['crash_site'] = []
    g.setdefault('AREA_LIGHTS', {})['crash_site'] = []
    g['MAP_PARENT']['crash_site'] = ['mine', 5, 26]
    g['CRASH_SITE'] = {'spot': list(SPOT), 'wreck': list(WRECK_AT), 'drone': list(DRONE_AT)}
    import bake_floor
    bake_floor.AREA_FLOORS['crash_site'] = {'m': ('mine_rock', ('3a3850', .25)), 's': ('mine_path', ('5a4030', .3))}
    bake_floor.SECTOR_WALLS['crash_site'] = ('mine_roof', 'mine_wall')
    bake_floor.CAVE_LIGHTS['crash_site'] = [(11, 12.5, 'cyan', 5.0), (8, 15, 'warm', 3.2), (30, 12, 'violet', 4.5),
                                           (12, 7, 'cyan', 2.4), (35, 6, 'cyan', 2.4), (42, 16, 'cyan', 2.4),
                                           (28, 24, 'cyan', 2.4), (37, 22, 'violet', 2.8)]
    return R
