"""The Survey Level, in three maps (Zachary, 17 Nov):
  top     S.A.R.A.'s core: the main room, where the lift arrives. Doors to the other two, a sealed lab
          door, and a spare room off the lift lobby.
  lounge  the Observation Lounge: a long curved gallery under one window with the gas giant in it.
  museum  Tar'Besh's museum, with the Precursor Sanctum at its far end and his quarters off one side.
Doors between them work like the shop doors on the promenade (right-click to open). Drawn in the
promenade style (scripts/lunar_ground.gd); floors baked by tools/bake_floor.py; placeholder pictures by
tools/make_props.py."""
import math

LIFT, ARRIVE = (20, 37), (20, 36)          # on the core map: the lift tile, and where you arrive

# Sizes of the room props: (width, height, solid rows from the bottom) in tiles.
SIZES = {
    'holo_dais': (3, 3, 2), 'memory_core': (2, 3, 1), 'wall_screen': (4, 2, 1), 'console': (2, 2, 1),
    'tape_archive': (2, 3, 1), 'sensor_panel': (2, 3, 1), 'concierge_desk': (3, 2, 1), 'paris_pictures': (3, 2, 1),
    'case_fossil': (2, 2, 1), 'case_relic': (2, 2, 1), 'case_shard': (2, 2, 1), 'case_wreck': (2, 2, 1),
    'museum_centerpiece': (4, 3, 2), 'curator_desk': (3, 2, 1), 'crystal_pedestal': (2, 3, 1),
    'sanctum_door': (1, 3, 3), 'lab_door': (1, 3, 3), 'star_chart': (2, 3, 1), 'bed': (2, 3, 2),
    'wardrobe': (2, 3, 1), 'telescope': (2, 3, 1), 'bench_n': (3, 2, 1), 'bench_e': (1, 3, 2), 'bench_w': (1, 3, 2),
    'plants': (3, 2, 1), 'books': (2, 2, 1), 'cargo': (2, 2, 1), 'terminal': (1, 2, 1),
}

EXHIBITS = [  # case art, title, what the label says
    ('case_fossil', 'Fossil of a cave crawler', ["A fossil from the moon's own caverns: something with too many legs, a very long time ago."]),
    ('case_relic', "Zaa'sh prayer bell", ["A Zaa'sh temple bell, cast in the shape of a Sky-Weaver's wing.", "Tar'Besh rings it once a year."]),
    ('case_shard', 'Precursor glass shard', ["A splinter of something that grew rather than being made.", "It is warm to the touch, through the glass."]),
    ('case_wreck', 'Hull plate from the first crash', ["Scorched plating from the refugee transport that crash-landed here.", "Every settler signed the back of it."]),
    ('case_relic', 'Terran signal codebook', ["A listening-post codebook, every page stamped TOP SECRET.", "S.A.R.A. says most of it was guesswork."]),
    ('case_fossil', 'Moogli trade weights', ["Brass weights from three different Moogli trading houses. None of them agree."]),
    ('case_shard', 'Star map on bone', ["An ancient star chart scratched on bone. One of the stars on it no longer exists."]),
    ('case_wreck', 'Pirate cutlass', ["Taken from a Chernobog raider.", "The label adds, firmly: not for sale."]),
]


WALKABLE = 'uihsmf.'


class Room:
    """One map being laid out: floor, props (pictures with solid tiles) and things to look at."""
    def __init__(self, g, key, title, w, h):
        self.A = g['A']; self.key = key
        self.t = g['A'][key] = g['Area'](key, title, w, h, '~')
        self.F, self.obj, self.W, self.H = self.t.floor, self.t.obj, w, h
        self.props, self.things, self.clear = [], [], set()

    def free(self, x, y, door=False):
        return 0 <= x < self.W and 0 <= y < self.H and self.F[y][x] in WALKABLE and self.obj[y][x] == ' ' and (door or (x, y) not in self.clear)

    def fits(self, name, x, y, door=False):
        w, h, solid = SIZES[name]
        return all(self.free(xx, yy, door) for yy in range(y + h - max(solid, 1), y + h) for xx in range(x, x + w))

    def thing(self, kind, title, hint, x, y, rad=26):
        self.things.append([kind, title, hint, self.key, [int(x * 16 + 8), int(y * 16 + 8)], rad])

    def prop(self, name, x, y, title, kind='look', hint='Look', door=False):
        w, h, solid = SIZES[name]
        if not self.fits(name, x, y, door):
            self.dump()
            raise AssertionError(('prop does not fit', self.key, name, x, y, title))
        self.props.append([name, x, y, w, h, title])
        for yy in range(y + h - solid, y + h):
            for xx in range(x, x + w):
                self.obj[yy][xx] = 'x'
        if kind:
            self.thing(kind, title, hint, x + (w - 1) / 2, y + h - 1)
        return x, y

    def near(self, name, fx, fy, title, kind='look', hint='Look'):
        """Puts a prop whose base centre is as close as it can get to fx,fy (continuous tiles)."""
        w, h, solid = SIZES[name]
        best = None
        for y in range(int(fy) - 5, int(fy) + 6):
            for x in range(int(fx) - 5, int(fx) + 6):
                if self.fits(name, x, y):
                    d = math.hypot(x + w / 2 - fx, y + h - .5 - fy)
                    if best is None or d < best[0]: best = (d, x, y)
        if not best:
            print('note: no room in %s for %s (%s)' % (self.key, name, title)); return None
        return self.prop(name, best[1], best[2], title, kind, hint)

    def keep_clear(self, x0, y0, x1, y1):
        self.clear.update((x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1))

    def dump(self):
        print('    ' + ''.join(str((x // 10) % 10) for x in range(self.W))); print('    ' + ''.join(str(x % 10) for x in range(self.W)))
        for y in range(self.H):
            print('%3d ' % y + ''.join('X' if self.obj[y][x] == 'x' else ('+' if (x, y) in self.clear and self.F[y][x] != '#' else self.F[y][x]) for x in range(self.W)))


def disc(cx, cy, x, y):
    return math.hypot(x + .5 - cx, y + .5 - cy)


def door_pair(entries, warps, a, at, facing_a, b, bt, facing_b, title_a, title_b):
    """Two linked doors: at in map a and bt in map b. facing is the side you stand on to use it
    (S: you stand south of it). You arrive one tile in front of the other door."""
    step = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}
    ax, ay = at[0] + step[facing_a][0], at[1] + step[facing_a][1]
    bx, by = bt[0] + step[facing_b][0], bt[1] + step[facing_b][1]
    entries.append([a, at[0], at[1], b, bx, by, facing_a, title_a, False])
    entries.append([b, bt[0], bt[1], a, ax, ay, facing_b, title_b, False])
    warps[a].append([at[0], at[1], b, bx, by]); warps[b].append([bt[0], bt[1], a, ax, ay])


def build(g):
    entries = []
    # ================================================================== top: S.A.R.A.'s core
    core = Room(g, 'top', 'Survey Level', 41, 41)
    F = core.F; CX, CY, R = 20.5, 18.5, 13.4
    for y in range(41):
        for x in range(41):
            if disc(CX, CY, x, y) <= R + 2.2 or (15 <= x <= 33 and 31 <= y <= 39):
                F[y][x] = '#'
            if disc(CX, CY, x, y) <= R:
                F[y][x] = 'i'
    for y in range(33, 38):
        for x in range(17, 24): F[y][x] = '.'                     # lift lobby
        for x in range(26, 32): F[y][x] = 'f'                     # spare room
    for x in (19, 20, 21): F[32][x] = '.'                         # core to lobby
    for y in (35, 36): F[y][24] = 'f'                             # lobby to spare room
    north, west, east = (20, 4), (6, 18), (34, 18)
    F[north[1]][north[0]] = 'i'; F[west[1]][west[0]] = 'i'
    for y in (17, 18, 19): F[y][34] = F[y][33] = 'i'              # sealed lab doorway (blocked by its door)
    core.t.warp('D', [LIFT], 'main', 115, 21)
    core.keep_clear(19, 5, 21, 14); core.keep_clear(7, 17, 16, 19); core.keep_clear(19, 21, 21, 36)
    core.keep_clear(17, 35, 25, 36); core.keep_clear(25, 17, 32, 19)
    core.prop('holo_dais', 19, 16, 'Hologram dais')
    core.prop('wall_screen', 14, 7, 'Station map screen'); core.prop('wall_screen', 23, 7, 'Station map screen')
    core.prop('tape_archive', 9, 10, 'Signal tape archive'); core.prop('sensor_panel', 30, 10, 'Deep-space sensor read-outs')
    for x, y in ((8, 14), (31, 14), (8, 21), (31, 21), (11, 25), (28, 25), (15, 28), (24, 28)):
        core.prop('memory_core', x, y, 'Memory core')
    core.prop('console', 15, 22, 'Operator console'); core.prop('console', 24, 22, 'Operator console')
    core.prop('concierge_desk', 12, 24, 'Concierge desk'); core.prop('paris_pictures', 26, 24, 'Pictures of Paris')
    core.prop('lab_door', 34, 17, 'Sealed lab', door=True)
    core.prop('cargo', 29, 33, 'Spare crates', None); core.prop('cargo', 26, 36, 'Spare crates', None)
    data_lines = [[[CX, 16.5], [x + 1.0, y + 2.5]] for x, y in ((8, 14), (31, 14), (8, 21), (31, 21), (11, 25), (28, 25), (15, 28), (24, 28))]
    data_lines += [[[CX, 16.5], [10.0, 12.5]], [[CX, 16.5], [31.0, 12.5]], [[CX, 16.5], [CX, 8.5]]]
    core.t.zones += [["S.A.R.A.'s core", 6, 4, 34, 32], ['Lift lobby', 17, 33, 23, 37], ['Spare room', 25, 33, 31, 37]]

    # ================================================================== lounge: the Observation Lounge
    lounge = Room(g, 'lounge', 'Observation Lounge', 64, 26)
    L = lounge.F; LX, LY = 31.5, 30.0
    for y in range(26):
        for x in range(64):
            r = disc(LX, LY, x, y); a = math.degrees(math.atan2(y + .5 - LY, x + .5 - LX)) % 360
            if r <= 29 and y <= 23:
                L[y][x] = '#'
            if 15 <= r <= 26.5 and 196 <= a <= 344 and y <= 22:
                L[y][x] = 'u'
    for y in range(25):
        for x in range(64):
            if L[y][x] == '#' and L[y + 1][x] == 'u' and disc(LX, LY, x, y) > 26:
                L[y][x] = 'w'
    ldoor = (31, 15)
    L[ldoor[1]][ldoor[0]] = 'u'
    lounge.keep_clear(29, 10, 33, 14)
    lounge.near('telescope', 31.5, 6.6, 'Lunar telescope', 'observe', 'Look through telescope')
    lounge.thing('look', 'Panoramic window', 'Look outside', 31, 6, 40)
    for ang in (218, 241, 299, 322):
        a = math.radians(ang); lounge.near('bench_n', LX + 21 * math.cos(a), LY + 21 * math.sin(a), 'Lounge bench [N]', 'seat', 'Sit')
    for ang, side in ((201, 'w'), (339, 'e')):
        a = math.radians(ang); lounge.near('bench_' + side, LX + 21.5 * math.cos(a), LY + 21.5 * math.sin(a), 'Lounge bench [%s]' % side.upper(), 'seat', 'Sit')
    for ang in (229, 252, 288, 311):
        a = math.radians(ang); lounge.near('star_chart', LX + 18.6 * math.cos(a), LY + 18.6 * math.sin(a), 'Star chart')
    for ang in (209, 262, 278, 331):
        a = math.radians(ang); lounge.near('plants', LX + 23.5 * math.cos(a), LY + 23.5 * math.sin(a), 'Lounge planter', 'inspect', 'Inspect')
    lounge.t.zones += [['Observation Lounge', 0, 0, 63, 25]]

    # ================================================================== museum: Tar'Besh's museum and the Sanctum
    museum = Room(g, 'museum', 'Museum', 52, 34)
    M = museum.F
    SX, SY = 7.5, 15.5
    for y in range(34):
        for x in range(52):
            hall = 15 <= x <= 45 and 4 <= y <= 25 and (x - 15) + (y - 4) >= 4 and (45 - x) + (y - 4) >= 4 and (x - 15) + (25 - y) >= 4 and (45 - x) + (25 - y) >= 4
            if (14 <= x <= 47 and 2 <= y <= 27) or disc(SX, SY, x, y) <= 8.2 or (29 <= x <= 39 and 26 <= y <= 32):
                M[y][x] = '#'
            if hall: M[y][x] = 'h'
            if disc(SX, SY, x, y) <= 6: M[y][x] = 's'
            if 30 <= x <= 38 and 28 <= y <= 31: M[y][x] = 'f'                     # Tar'Besh's quarters
    for y in (14, 15, 16):
        for x in range(13, 15): M[y][x] = 'h'                                     # Sanctum doorway
    for x in (33, 34): M[26][x] = M[27][x] = 'f'                                  # quarters doorway
    mdoor = (46, 15)
    M[mdoor[1]][mdoor[0]] = 'h'
    museum.keep_clear(40, 14, 45, 16); museum.keep_clear(13, 14, 18, 16); museum.keep_clear(32, 22, 35, 27)
    museum.prop('sanctum_door', 13, 14, 'Sanctum door', door=True)
    museum.prop('museum_centerpiece', 28, 12, "The Weaver's Wing")
    n = 0
    for x, y in ((19, 6), (24, 6), (34, 6), (39, 6), (19, 21), (24, 21), (38, 21), (43, 11)):
        art_, title, _ = EXHIBITS[n % len(EXHIBITS)]
        if museum.near(art_, x + 1, y + 1.5, title): n += 1
    museum.near('curator_desk', 18.5, 11.5, "Tar'Besh's desk")
    museum.near('books', 42, 22, 'Museum catalogue', 'look', 'Look')
    for ang in (270, 30, 150):
        a = math.radians(ang); museum.near('crystal_pedestal', SX + 2.8 * math.cos(a), SY + 2.8 * math.sin(a) + 1, 'Precursor crystal')
    museum.prop('bed', 30, 28, "Tar'Besh's bed", None); museum.prop('wardrobe', 37, 28, "Tar'Besh's wardrobe", None)
    museum.prop('books', 30, 30, "Tar'Besh's books"); museum.prop('plants', 36, 30, 'Prayer garden', 'inspect', 'Inspect')
    museum.t.zones += [["Tar'Besh's museum", 15, 4, 45, 25], ['Precursor Sanctum', 1, 9, 13, 22], ["Tar'Besh's quarters", 30, 28, 38, 31]]

    # ================================================================== doors between them
    warps = {'top': core.t.warps, 'lounge': lounge.t.warps, 'museum': museum.t.warps}
    door_pair(entries, warps, 'top', north, 'S', 'lounge', ldoor, 'N', 'Observation Lounge', "To S.A.R.A.'s core")
    door_pair(entries, warps, 'top', west, 'E', 'museum', mdoor, 'W', "Tar'Besh's museum", "To S.A.R.A.'s core")
    g['MAP_PARENT']['lounge'] = ['top', north[0], north[1] + 1]
    g['MAP_PARENT']['museum'] = ['top', west[0] + 1, west[1]]

    for room in (core, lounge, museum):
        g.setdefault('AREA_PROPS', {})[room.key] = room.props
        g.setdefault('AREA_ROOF_PROPS', {})[room.key] = []
        g.setdefault('AREA_LIGHTS', {})[room.key] = []
        g.setdefault('EXTRA_THINGS', []).extend(room.things)
    g.setdefault('FLOOR_EXTRAS', {})['top'] = {'data_lines': data_lines, 'dais': [CX, 16.5]}
    g['SURVEY_ENTRANCES'] = entries
    return core.t
