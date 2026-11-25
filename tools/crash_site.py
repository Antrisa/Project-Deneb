"""The crash site (24 Nov 2026): the cavern your ship fell into, where the Mother-Drone lies. Only the prologue
comes here (scripts/story_scenes.gd "prologue" goes to it under a fade), so it has no way in or out.

A rough oval cavern in the mine's rock, built and baked like the other caverns: your fighter's front half (the main
menu's fighter, redrawn at three times the size) nose-first in a heap of basalt on the west (art/lunar/crash_wreck.png),
scrap she shed along her gouge, the Mother-Drone half sunk in the floor on the east with crystal grown up round it
(art/lunar/mother_drone.png), clumps of stalagmites, boulders, fallen rock and glowing fungus round the walls. Cool light falls
on the wreck from the hole it made; the fire at its torn end and the drone's glow light the rest (CAVE_LIGHTS).
The two props, and where they stand, are drawn by tools/dev/crash_site_art.py, which also lines up the drone's
animation and the beam with them.
"""
import math
import survey
from survey import Room, SIZES

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dev"))

W, H = 46, 30
SPOT = (21, 13)                       # where the (hidden) player stands, so the camera frames wreck and drone
WRECK_AT, WRECK_SIZE = (5, 10), (11, 7)
DRONE_AT, DRONE_SIZE = (24, 8), (13, 8)
SIZES.update({'crash_wreck': (WRECK_SIZE[0], WRECK_SIZE[1], 3), 'mother_drone': (DRONE_SIZE[0], DRONE_SIZE[1], 4)})
SIZES.setdefault('stalagmite', (1, 2, 1))
SIZES.setdefault('boulder', (2, 2, 1))
SIZES.setdefault('glow_fungus', (1, 1, 1))
SIZES.setdefault('crystal_cluster', (2, 2, 1))
SIZES.setdefault('crystal_column', (1, 3, 1))
SIZES.setdefault('rock_chips', (2, 1, 1))
SIZES.setdefault('wreck_plate', (2, 1, 1))
SIZES.setdefault('wreck_wing', (3, 2, 1))


def build(g):
    survey.WALKABLE = 'ms'
    R = Room(g, 'crash_site', 'The crash site', W, H)
    F = R.F
    for y in range(H):
        for x in range(W):
            F[y][x] = '#'
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            dx, dy = (x + .5 - 23) / 20.5, (y + .5 - 15.5) / 12.5
            k = 1 + .06 * math.sin(math.atan2(dy, dx) * 5 + 1) + .04 * math.sin(math.atan2(dy, dx) * 9)
            if dx * dx + dy * dy <= k * k:
                F[y][x] = 'm'
    R.prop('crash_wreck', WRECK_AT[0], WRECK_AT[1], 'Your ship', None)
    R.prop('mother_drone', DRONE_AT[0], DRONE_AT[1], 'The Mother-Drone', None)
    R.keep_clear(SPOT[0] - 1, SPOT[1] - 1, SPOT[0] + 1, SPOT[1] + 1)
    N = R.near
    # scrap your fighter shed coming in, along the line of the gouge
    for name, x, y, t in (('wreck_plate', 3, 18, 'Hull plating'), ('wreck_wing', 15, 18, 'A wing tip'), ('wreck_plate', 18, 15, 'Hull plating'),
                          ('wreck_plate', 8, 20, 'Hull plating')):
        N(name, x, y, t, None)
    # crystal columns grown up round the drone, and its scattered seeds of crystal
    for x, y in ((38, 13), (39, 14), (24, 18), (25, 19), (33, 19)):
        N('crystal_column', x, y, 'Crystal column', None)
    for x, y in ((23, 19), (37, 15), (40, 10), (28, 6), (34, 20)):
        N('crystal_cluster', x, y, 'Glow crystals', None)
    # stalagmites in clumps against the walls, boulders and rubble where the roof came down
    for x, y in ((4, 7), (5, 8), (9, 5), (10, 6), (15, 4), (31, 4), (33, 5), (39, 7), (42, 12), (42, 14), (41, 21), (40, 22),
                 (33, 25), (32, 26), (24, 26), (15, 25), (14, 26), (6, 22), (3, 16), (2, 13)):
        N('stalagmite', x, y, 'Stalagmite', None)
    for x, y in ((18, 8), (20, 22), (36, 22), (9, 23), (28, 23), (44, 17)):
        N('boulder', x, y, 'Boulder', None)
    for x, y in ((13, 8), (17, 10), (21, 19), (12, 22), (27, 22), (35, 24), (19, 6), (6, 9), (16, 20), (30, 4)):
        N('rock_chips', x, y, 'Fallen rock', None)
    for x, y in ((12, 7), (35, 6), (43, 15), (29, 25), (4, 19), (19, 25), (8, 24), (38, 24)):
        N('glow_fungus', x, y, 'Glowing fungus', None)
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
    # the cave atmosphere the caverns have (bake_floor._cave_atmosphere): cool shadow, a faint violet-grey haze,
    # grit at the foot of the walls, loose stones, and pools of light round the lights below
    bake_floor.CAVE_MOOD['crash_site'] = dict(ao=(.05, .04, .09), mist=(.46, .42, .62), mist_a=.18, dark=.3,
                                             lamp=(1.0, .78, .48), rock="m")
    # the light through the hole on the wreck, the fire at its torn end, the drone's violet, fungus and crystals
    bake_floor.CAVE_LIGHTS['crash_site'] = [(11, 13.5, 'cyan', 5.5), (9, 15, 'warm', 3.4), (31, 12.5, 'violet', 5.5),
                                           (12, 7, 'cyan', 2.4), (35, 6, 'cyan', 2.4), (43, 16, 'cyan', 2.4),
                                           (29, 25, 'cyan', 2.4), (38, 15, 'violet', 3.0), (25, 19, 'violet', 2.6),
                                           (36, 20, 'violet', 2.6), (8, 24, 'cyan', 2.2)]
    return R
