"""The Survey Level, in four maps (Zachary, 17 Nov):
  top      S.A.R.A.'s core: the main room, where the lift arrives. Doors to the lounge and the museum,
           a sealed lab door, and a spare room off the lift lobby.
  lounge   the Observation Lounge: a long curved gallery under one window with the gas giant in it.
  museum   Tar'Besh's museum: a big hall with 32 display cases (8 filled, 24 waiting for things the
           player finds and donates), the Weaver's Wing in the middle, his quarters off the south side.
  sanctum  the Precursor Sanctum, behind a locked door at the museum's far end: a shrine where the
           crystals are kept like holy relics, with murals, braziers, pews and testing equipment.
Doors between them work like the shop doors on the promenade (right-click to open). Drawn in the
promenade style (scripts/lunar_ground.gd); floors baked by tools/bake_floor.py; placeholder pictures by
tools/make_props.py."""
import math

LIFT, ARRIVE = (23, 45), (23, 44)          # on the core map: the lift tile, and where you arrive

# Sizes of the room props: (width, height, solid rows from the bottom) in tiles.
SIZES = {
    'holo_dais': (3, 3, 2), 'memory_core': (2, 3, 1), 'wall_screen': (4, 2, 1), 'console': (2, 2, 1),
    'tape_archive': (2, 3, 1), 'sensor_panel': (2, 3, 1), 'concierge_desk': (3, 2, 1), 'paris_pictures': (3, 2, 1),
    'case_fossil': (2, 2, 1), 'case_relic': (2, 2, 1), 'case_shard': (2, 2, 1), 'case_wreck': (2, 2, 1),
    'museum_centerpiece': (4, 3, 2), 'curator_desk': (3, 2, 1), 'crystal_pedestal': (2, 3, 1),
    'sanctum_door': (1, 3, 3), 'lab_door': (1, 3, 3), 'star_chart': (2, 3, 1), 'bed': (2, 3, 2),
    'case_empty': (2, 2, 1), 'crystal_pedestal_empty': (2, 3, 1), 'precursor_mural': (3, 3, 1), 'test_rig': (2, 3, 1),
    'spectrometer': (2, 2, 1), 'brazier': (1, 2, 1), 'holy_banner': (1, 3, 1), 'prayer_mat': (2, 1, 0),
    'cafe_table': (2, 2, 1), 'chair_e': (1, 2, 0), 'chair_w': (1, 2, 0), 'flowers': (4, 2, 2),
    'wardrobe': (2, 3, 1), 'telescope': (2, 3, 1), 'bench_n': (2, 2, 1), 'bench_e': (1, 3, 2), 'bench_w': (1, 3, 2),
    'plants': (3, 2, 1), 'books': (2, 2, 1), 'cargo': (2, 2, 1), 'terminal': (1, 2, 1),
}

EXHIBITS = [  # the exhibit's picture (art/museum/<name>.png, shown inside a plain glass case), title, label
    ('crawler_fossil', 'Fossil of a cave crawler', ["A fossil from the moon's own caverns: something with too many legs, a very long time ago."]),
    ('prayer_bell', "Zaa'sh prayer bell", ["A Zaa'sh temple bell, cast in the shape of a Sky-Weaver's wing.", "Tar'Besh rings it once a year."]),
    ('glass_shard', 'Precursor glass shard', ["A splinter of something that grew rather than being made.", "It is warm to the touch, through the glass."]),
    ('hull_plate', 'Hull plate from the first crash', ["Scorched plating from the refugee transport that crash-landed here.", "Every settler signed the back of it."]),
    ('signal_codebook', 'Terran signal codebook', ["A listening-post codebook, every page stamped TOP SECRET.", "S.A.R.A. says most of it was guesswork."]),
    ('trade_weights', 'Moogli trade weights', ["Brass weights from three different Moogli trading houses. None of them agree."]),
    ('bone_star_map', 'Star map on bone', ["An ancient star chart scratched on bone. One of the stars on it no longer exists."]),
    ('pirate_cutlass', 'Pirate cutlass', ["Taken from a Chernobog raider.", "The label adds, firmly: not for sale."]),
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
        # Nothing stands on the floor tile just above a wall: the wall's roof is drawn over it.
        if not door and any(0 <= y + h < len(self.F) and 0 <= xx < len(self.F[0]) and self.F[y + h][xx] in '#Wzw' for xx in range(x, x + w)):
            return False
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
        if name in SEAT_SETS and kind == 'seat':
            # A table and its chairs are separate pictures, so either can be moved on its own
            # (Zachary, 21 Nov): a chair in each outer column of the table's tiles, each a seat of its own.
            chair_e, chair_w, label = SEAT_SETS[name]
            for cx, d, pic in ((x, 'E', chair_e), (x + w - 1, 'W', chair_w)):
                self.props.append([pic, cx, y, 1, h, '%s [%s]' % (label, d)])
                self.thing('seat', '%s [%s]' % (label, d), 'Sit', cx, y + h - 1)
            return x, y
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


# Tables that come with their own chairs: the picture for the west and east columns, and the seat label.
SEAT_SETS = {'table': ('chair_e', 'chair_w', 'Dining chair'), 'bar_table': ('bar_stool', 'bar_stool', 'Bar stool')}


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
    core = Room(g, 'top', 'Survey Level', 47, 49)
    F = core.F; CX, CY, R = 23.5, 21.5, 16.0
    for y in range(49):
        for x in range(47):
            if disc(CX, CY, x, y) <= R + 2.2 or (17 <= x <= 39 and 38 <= y <= 47):
                F[y][x] = '#'
            if disc(CX, CY, x, y) <= R:
                F[y][x] = 'i'
    for y in range(40, 46):
        for x in range(19, 28): F[y][x] = '.'                     # lift lobby
        for x in range(30, 38): F[y][x] = 'f'                     # spare room
    for y in (38, 39):
        for x in (22, 23, 24): F[y][x] = '.'                      # core to lobby
    for y in (43, 44): F[y][28] = F[y][29] = 'f'                  # lobby to spare room
    north, west = (23, 4), (6, 21)
    # The lounge, museum and sealed lab are buildings of their own beyond these doors: show their bulk
    # as roof running off the edge, not bare moon (Zachary, 17 Nov).
    for (x0, y0, x1, y1) in ((14, 0, 32, 4), (0, 12, 6, 30), (40, 13, 46, 29)):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if F[y][x] not in 'i.f': F[y][x] = '#'
    F[north[1]][north[0]] = 'i'; F[west[1]][west[0]] = 'i'
    for y in (20, 21, 22): F[y][40] = F[y][39] = 'i'              # sealed lab doorway (blocked by its door)
    core.t.warp('D', [LIFT], 'main', 115, 21)
    core.keep_clear(22, 5, 24, 18); core.keep_clear(7, 20, 20, 22); core.keep_clear(22, 22, 24, 44)
    core.keep_clear(19, 43, 29, 44); core.keep_clear(26, 20, 39, 22)
    core.prop('holo_dais', 22, 18, 'Hologram dais')
    pol = lambda r, a: (CX + r * math.cos(math.radians(a)), CY + r * math.sin(math.radians(a)))
    core.near('wall_screen', 17.5, 9.0, 'Station map screen'); core.near('wall_screen', 29.5, 9.0, 'Station map screen')
    core.near('tape_archive', *pol(13.6, 218), 'Signal tape archive'); core.near('sensor_panel', *pol(13.6, 322), 'Deep-space sensor read-outs')
    cores = []
    for ang in (160, 200, 20, 340, 128, 52, 104, 76):
        spot = core.near('memory_core', *pol(13.4, ang), 'Memory core')
        if spot: cores.append(spot)
    core.near('console', 19.5, 27.5, 'Operator console'); core.near('console', 28.5, 27.5, 'Operator console')
    core.near('console', 16.0, 23.5, 'Operator console'); core.near('console', 32.0, 23.5, 'Operator console')
    core.near('concierge_desk', *pol(12.5, 142), 'Concierge desk'); core.near('paris_pictures', *pol(12.5, 38), 'Pictures of Paris')
    core.near('flowers', *pol(14.0, 236), "S.A.R.A.'s flowers", 'inspect', 'Inspect'); core.near('plants', *pol(14.0, 304), 'Core planter', 'inspect', 'Inspect')
    core.prop('lab_door', 40, 20, 'Sealed lab', door=True)
    core.near('cargo', 35, 41.5, 'Spare crates', None); core.near('cargo', 31, 44.5, 'Spare crates', None)
    core.near('plants', 20.5, 41.5, 'Lobby planter', 'inspect', 'Inspect'); core.near('plants', 26.5, 41.5, 'Lobby planter', 'inspect', 'Inspect')
    data_lines = [[[CX, 19.8], [x + 1.0, y + 2.5]] for x, y in cores] + [[[CX, 19.8], [CX, 10.0]]]
    core.t.zones += [["S.A.R.A.'s core", 7, 5, 40, 38], ['Lift lobby', 19, 40, 27, 45], ['Spare room', 30, 40, 37, 45]]

    # ================================================================== lounge: the Observation Lounge
    lounge = Room(g, 'lounge', 'Observation Lounge', 76, 31)
    L = lounge.F; LX, LY = 37.5, 34.0
    for y in range(31):
        for x in range(76):
            r = disc(LX, LY, x, y); a = math.degrees(math.atan2(y + .5 - LY, x + .5 - LX)) % 360
            if r <= 33 and y <= 27:
                L[y][x] = '#'
            if 16 <= r <= 30 and 196 <= a <= 344 and y <= 26:
                L[y][x] = 'u'
    for y in range(30):
        for x in range(76):
            if L[y][x] == '#' and L[y + 1][x] == 'u' and disc(LX, LY, x, y) > 29.5:
                L[y][x] = 'w'
    ldoor = (37, 18)
    L[ldoor[1]][ldoor[0]] = 'u'
    lounge.keep_clear(35, 12, 39, 17)
    lp = lambda r, a: (LX + r * math.cos(math.radians(a)), LY + r * math.sin(math.radians(a)))
    lounge.near('telescope', 37.5, 7.0, 'Lunar telescope', 'observe', 'Look through telescope')
    lounge.thing('look', 'Panoramic window', 'Look outside', 37, 6, 40)
    for ang in (214, 232, 250, 290, 308, 326):
        lounge.near('bench_n', *lp(24.5, ang), 'Lounge bench [N]', 'seat', 'Sit')
    for ang, side in ((200, 'w'), (340, 'e')):
        lounge.near('bench_' + side, *lp(25, ang), 'Lounge bench [%s]' % side.upper(), 'seat', 'Sit')
    for ang in (223, 241, 299, 317):
        lounge.near('star_chart', *lp(20.0, ang), 'Star chart')
    for ang in (207, 259, 281, 333):
        lounge.near('plants', *lp(27.5, ang), 'Lounge planter', 'inspect', 'Inspect')
    # a quiet corner for tea and reading at each end
    for side, ang in ((-1, 214), (1, 326)):
        tx_, ty_ = lp(20.5, ang)
        spot = lounge.near('cafe_table', tx_, ty_, 'Lounge table')
        if spot:
            lounge.near('chair_e', spot[0] - 1, spot[1] + 1.5, 'Lounge chair [E]', 'seat', 'Sit')
            lounge.near('chair_w', spot[0] + 2.5, spot[1] + 1.5, 'Lounge chair [W]', 'seat', 'Sit')
    lounge.near('books', *lp(22.5, 268), 'Lounge bookshelf', 'look', 'Look')
    lounge.t.zones += [['Observation Lounge', 0, 0, 75, 30]]

    # ================================================================== museum: Tar'Besh's museum
    museum = Room(g, 'museum', 'Museum', 66, 50)
    M = museum.F
    X0, Y0, X1, Y1, CH = 4, 4, 60, 38, 6                       # the hall, corners cut off
    MCX, MCY = 32.5, 21.0
    for y in range(50):
        for x in range(66):
            if (X0 - 2 <= x <= X1 + 2 and Y0 - 2 <= y <= Y1 + 2) or (39 <= x <= 52 and 39 <= y <= 48):
                M[y][x] = '#'
            if X0 <= x <= X1 and Y0 <= y <= Y1 and min(x - X0, X1 - x) + min(y - Y0, Y1 - y) >= CH:
                M[y][x] = 'h'
            if M[y][x] == 'h' and disc(MCX, MCY, x, y) <= 7.5:
                M[y][x] = '.'                                     # the atrium round the Weaver's Wing
            if 41 <= x <= 50 and 41 <= y <= 46:
                M[y][x] = 'f'                                     # Tar'Besh's quarters
    for y in (39, 40):
        for x in (45, 46): M[y][x] = 'f'
    mdoor, sdoor = (61, 21), (3, 21)
    M[mdoor[1]][mdoor[0]] = 'h'; M[sdoor[1]][sdoor[0]] = 'h'
    museum.keep_clear(4, 19, 23, 23); museum.keep_clear(42, 19, 60, 23); museum.keep_clear(44, 24, 47, 40)
    museum.prop('museum_centerpiece', 31, 18, "The Weaver's Wing")
    for bx, by, side in ((25, 21, 'e'), (40, 21, 'w')):
        museum.near('bench_' + side, bx, by - 3, 'Museum bench [%s]' % side.upper(), 'seat', 'Sit')
    for px, py in ((27, 15.5), (38, 15.5), (27, 28.5), (38, 28.5)):
        museum.near('plants', px, py, 'Museum planter', 'inspect', 'Inspect')
    # 32 display cases in four galleries; Tar'Besh's eight pieces, then 24 empty ones for donations.
    galleries = [('Natural history', (8, 12, 16, 20), (9, 14)), ('Peoples of the Rim', (44, 48, 52, 56), (9, 14)),
                 ('The first settlers', (8, 12, 16, 20), (30, 35)), ('Precursor gallery', (44, 48, 52, 56), (30, 35))]
    slots, n = [], 0
    for gi, (gname, cols, rows) in enumerate(galleries):
        for ri, base in enumerate(rows):
            for ci, cx_ in enumerate(cols):
                filled = ri == 0 and ci in (1, 2)                  # two of Tar'Besh's pieces in each gallery
                # Every case is the same plain glass case; what is in it is drawn inside by the game
                # (art/museum/<name>.png), so a donation can fill an empty case later (Zachary, 21 Nov).
                if filled:
                    icon_, title, _ = EXHIBITS[n]; n += 1
                else:
                    icon_, title = '', 'Empty display'
                spot = museum.near('case_empty', cx_ + 1, base + .5, title)
                assert spot, ('museum case', gname, cx_, base)
                slots.append([spot[0], spot[1], gname, title if filled else '', icon_])
    for gx, gy in ((23.5, 8.5), (42.5, 8.5), (23.5, 34.5), (42.5, 34.5)):
        museum.near('terminal', gx, gy, 'Audio guide')
    museum.near('flowers', 33.0, 7.5, 'Museum flower bed', 'inspect', 'Inspect'); museum.near('flowers', 33.0, 36.0, 'Museum flower bed', 'inspect', 'Inspect')
    museum.near('curator_desk', 55.5, 26.5, "Tar'Besh's desk"); museum.near('books', 58.0, 26.5, 'Museum catalogue')
    museum.near('holy_banner', 5.0, 18.5, 'Sanctum banner'); museum.near('holy_banner', 5.0, 26.0, 'Sanctum banner')
    museum.prop('bed', 41, 41, 'Day bed', None); museum.prop('wardrobe', 48, 41, 'Curator\'s wardrobe', None)   # he sleeps at home now (Residences C)
    museum.near('books', 42, 46.5, "Tar'Besh's books"); museum.near('plants', 48.5, 46.5, 'Prayer garden', 'inspect', 'Inspect')
    museum.t.zones += [["Tar'Besh's museum", X0, Y0, X1, Y1], ["Curator's rest room", 41, 41, 50, 46]] + \
        [[gname, cols[0] - 1, rows[0] - 3, cols[-1] + 2, rows[1] + 1] for gname, cols, rows in galleries]

    # ================================================================== sanctum: the Precursor Sanctum
    sanctum = Room(g, 'sanctum', 'Precursor Sanctum', 48, 40)
    S_ = sanctum.F; SX, SY, SR = 24.5, 19.5, 15.0
    for y in range(40):
        for x in range(48):
            if disc(SX, SY, x, y) <= SR + 2.2: S_[y][x] = '#'
            if disc(SX, SY, x, y) <= SR: S_[y][x] = 's'
            if disc(SX - 7, SY, x, y) <= 5.5 and S_[y][x] == 's': S_[y][x] = 'i'   # the altar dais
    sdoor_in = (40, 19)
    S_[sdoor_in[1]][sdoor_in[0]] = 's'
    sanctum.keep_clear(26, 18, 39, 20)
    sp = lambda r, a: (SX + r * math.cos(math.radians(a)), SY + r * math.sin(math.radians(a)))
    # The crystals, held up on pedestals round the altar like holy relics: three found, six waiting.
    # The three found crystals stand on the altar dais; six empty cradles wait in an arc behind it.
    crystals = []
    for fx, fy in ((14.0, 20.5), (16.5, 16.5), (16.5, 24.5)):
        spot = sanctum.near('crystal_pedestal', fx, fy, 'Precursor crystal')
        if spot: crystals.append([spot[0], spot[1], 'Precursor crystal'])
    for ang in (152, 166, 180, 194, 208, 222):
        spot = sanctum.near('crystal_pedestal_empty', *sp(12.2, ang), 'Empty crystal cradle')
        if spot: crystals.append([spot[0], spot[1], ''])
    for ang in (250, 290, 110, 70):
        sanctum.near('precursor_mural', *sp(13.2, ang), 'Precursor mural')
    for ang in (236, 138):
        sanctum.near('holy_banner', *sp(13.6, ang), 'Sanctum banner')
    for fx, fy in ((19.5, 14.5), (19.5, 25.5), (21.0, 18.0), (21.0, 22.0)):
        sanctum.near('brazier', fx, fy, 'Violet brazier', 'inspect', 'Inspect')
    for fx, fy in ((23.5, 17.5), (23.5, 20.5), (23.5, 23.5)):
        sanctum.near('prayer_mat', fx, fy, 'Prayer mat', 'inspect', 'Inspect')
    for x_ in (27, 31, 35):
        for y_ in (14.5, 26.5):
            sanctum.near('bench_w', x_, y_, 'Sanctum pew [W]', 'seat', 'Sit')
    sanctum.near('test_rig', *sp(12.5, 300), 'Crystal test rig'); sanctum.near('spectrometer', *sp(12.0, 60), 'Resonance spectrometer')
    sanctum.near('console', *sp(12.0, 40), 'Research console'); sanctum.near('terminal', *sp(13.0, 320), 'Measurement log')
    sanctum.t.zones += [['Precursor Sanctum', 7, 2, 41, 37]]

    # ================================================================== doors between them
    warps = {'top': core.t.warps, 'lounge': lounge.t.warps, 'museum': museum.t.warps, 'sanctum': sanctum.t.warps}
    door_pair(entries, warps, 'top', north, 'S', 'lounge', ldoor, 'N', 'Observation Lounge', "To S.A.R.A.'s core")
    door_pair(entries, warps, 'top', west, 'E', 'museum', mdoor, 'W', "Tar'Besh's museum", "To S.A.R.A.'s core")
    door_pair(entries, warps, 'museum', sdoor, 'E', 'sanctum', sdoor_in, 'W', 'Precursor Sanctum', 'To the museum')
    for e in entries:
        if e[0] == 'museum' and e[3] == 'sanctum': e[8] = True                 # locked until the story opens it
    g['MAP_PARENT']['lounge'] = ['top', north[0], north[1] + 1]
    g['MAP_PARENT']['museum'] = ['top', west[0] + 1, west[1]]
    g['MAP_PARENT']['sanctum'] = ['top', west[0] + 1, west[1]]

    for room in (core, lounge, museum, sanctum):
        g.setdefault('AREA_PROPS', {})[room.key] = room.props
        g.setdefault('AREA_ROOF_PROPS', {})[room.key] = []
        g.setdefault('AREA_LIGHTS', {})[room.key] = []
        g.setdefault('EXTRA_THINGS', []).extend(room.things)
    g.setdefault('FLOOR_EXTRAS', {})['top'] = {'data_lines': data_lines, 'dais': [CX, 19.8]}
    g['SURVEY_ENTRANCES'] = entries
    g['MUSEUM_SLOTS'] = slots                  # [x, y, gallery, what is in it ('' = empty), its picture in art/museum/]
    g['SANCTUM_CRADLES'] = crystals
    return core.t
