"""Survey Level (area "top"): a half-dome. A long Observation Lounge runs round the top under one curved
window; S.A.R.A.'s core sits in the middle; Tar'Besh's museum fills the west side with the Precursor
Sanctum joined to its far end; a sealed Terran lab on the east; Tar'Besh's quarters, a spare room and the
lift lobby along the bottom. Drawn in the promenade style (scripts/lunar_ground.gd), floor baked by
tools/bake_floor.py. Approved by Zachary as "option C" on 17 Nov.

Coordinates are tiles. The dome's centre is the middle of tile column 43, so a thing is symmetric when it
is centred on column 43 (a cell x mirrors to 86 - x)."""
import math

W, H = 87, 49
OX, OY = 43.5, 40.5              # dome centre (continuous tile coordinates)
CORE = (43.5, 25.0)              # S.A.R.A.'s core, radius 10
SANCT = (13.5, 41.0)             # Sanctum pod, radius 6
LIFT = (43, 43)                  # lift tile; you arrive one tile above it
ARRIVE = (43, 42)

# Sizes of the room props: (width, height, solid rows from the bottom) in tiles.
SIZES = {
    'holo_dais': (3, 3, 2), 'memory_core': (2, 3, 1), 'wall_screen': (4, 2, 1), 'console': (2, 2, 1),
    'tape_archive': (2, 3, 1), 'sensor_panel': (2, 3, 1), 'concierge_desk': (3, 2, 1), 'paris_pictures': (3, 2, 1),
    'case_fossil': (2, 2, 1), 'case_relic': (2, 2, 1), 'case_shard': (2, 2, 1), 'case_wreck': (2, 2, 1),
    'museum_centerpiece': (4, 3, 2), 'curator_desk': (3, 2, 1), 'crystal_pedestal': (2, 3, 1),
    'sealed_door': (3, 2, 2), 'sanctum_door': (1, 3, 3), 'star_chart': (2, 3, 1), 'bed': (2, 3, 2),
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


def r_ang(x, y):
    dx, dy = x + .5 - OX, y + .5 - OY
    return math.hypot(dx, dy), math.degrees(math.atan2(dy, dx)) % 360


def build(g):
    A, Area = g['A'], g['Area']
    t = A['top'] = Area('top', 'Survey Level', W, H, '~')
    F = t.floor
    quarters, spare, lobby = (29, 36, 37, 42), (49, 36, 57, 42), (39, 37, 47, 43)    # x0, y0, x1, y1

    def in_rect(x, y, rc, grow=0):
        return rc[0] - grow <= x <= rc[2] + grow and rc[1] - grow <= y <= rc[3] + grow

    def core_d(x, y):
        return math.hypot(x + .5 - CORE[0], y + .5 - CORE[1])

    for y in range(H):
        for x in range(W):
            r, a = r_ang(x, y)
            if (r <= 35 and y <= 44) or math.hypot(x + .5 - SANCT[0], y + .5 - SANCT[1]) <= 8.2:
                F[y][x] = '#'
            if 27 <= r <= 33 and 190 <= a <= 350 and y <= 40:
                F[y][x] = 'u'                                                   # Observation Lounge
            if core_d(x, y) <= 10:
                F[y][x] = 'i'                                                   # S.A.R.A.'s core
            elif 12 <= r <= 26 and core_d(x, y) > 11.2 and y <= 40:
                if 184 <= a <= 256 and not in_rect(x, y, quarters, 1):
                    F[y][x] = 'h'                                               # museum
                elif 284 <= a <= 350 and not in_rect(x, y, spare, 1):
                    F[y][x] = 'm'                                               # sealed lab
            if math.hypot(x + .5 - SANCT[0], y + .5 - SANCT[1]) <= 6:
                F[y][x] = 's'                                                   # Sanctum
            if in_rect(x, y, quarters) or in_rect(x, y, spare):
                F[y][x] = 'f'
            if in_rect(x, y, lobby):
                F[y][x] = '.'
    # Window: the lounge's outer wall
    for y in range(H - 1):
        for x in range(W):
            if F[y][x] == '#' and F[y + 1][x] == 'u' and r_ang(x, y)[0] > 33:
                F[y][x] = 'w'
    # Doorways
    for x in (42, 43, 44):
        F[14][x] = 'i'                                    # core north, to the lounge
        F[35][x] = F[36][x] = '.'                         # core south, to the lobby
    for y in (40, 41):
        F[y][48] = 'f'                                    # spare room, from the lobby
    for x in (32, 33):
        F[35][x] = 'f'                                    # Tar'Besh's quarters, from the museum

    def radial_door(angle, r0, r1, ch):
        cells = []
        for k in range(int(r0 * 4), int(r1 * 4) + 1):
            rr = k / 4
            for off in (-1, 0, 1):
                a = math.radians(angle)
                px, py = OX + rr * math.cos(a) - off * math.sin(a), OY + rr * math.sin(a) + off * math.cos(a)
                cx_, cy_ = int(math.floor(px)), int(math.floor(py))
                if F[cy_][cx_] in '#':
                    F[cy_][cx_] = ch; cells.append((cx_, cy_))
        return cells
    radial_door(236, 24.5, 28.5, 'h')                    # museum, from the lounge
    lab_cells = radial_door(304, 24.5, 28.5, 'm')         # sealed lab, from the lounge (blocked by its door)
    # The Sanctum has its own wall; one doorway (rows 38-40) opens into the museum's far end.
    for y in range(H):
        for x in range(W):
            d_ = math.hypot(x + .5 - SANCT[0], y + .5 - SANCT[1])
            if 6 < d_ <= 7.6 and F[y][x] == 'h':
                F[y][x] = '#'
    door_col = max(x for x in range(W) if F[39][x] == 's') + 1
    for y in (38, 39, 40):
        for x in range(door_col, door_col + 6):
            if F[y][x] in '#~':
                F[y][x] = 'h'
            else:
                break
    t.zones += [["S.A.R.A.'s core", 33, 14, 54, 35], ['Observation Lounge', 9, 6, 78, 40], ["Tar'Besh's museum", 17, 15, 40, 40],
                ['Precursor Sanctum', 7, 34, 20, 48], ['Sealed lab', 47, 15, 70, 40], ["Tar'Besh's quarters", 29, 36, 37, 42],
                ['Spare room', 49, 36, 57, 42], ['Lift lobby', 39, 37, 47, 43]]
    t.warp('D', [LIFT], 'main', 115, 21)

    # ------------------------------------------------------------------ props
    props, things, obj = [], [], t.obj
    clear = set()
    def clear_line(cells):
        clear.update(cells)
    # keep door approaches and the main walk lines clear
    for y in range(13, 37):
        for x in (42, 43, 44):
            if y < 22 or y > 25: clear.add((x, y))
    for x in range(39, 48): clear.update({(x, 42), (x, 43)} if x in (42, 43, 44) else set())
    for y in (40, 41):
        for x in range(45, 49): clear.add((x, y))
    for y in range(33, 37):
        for x in range(31, 35): clear.add((x, y))
    for y in range(36, 42):
        for x in range(17, 29): clear.add((x, y))

    def dump():
        print('    ' + ''.join(str((x // 10) % 10) for x in range(W))); print('    ' + ''.join(str(x % 10) for x in range(W)))
        for y in range(H):
            print('%3d ' % y + ''.join('X' if obj[y][x] == 'x' else ('+' if (x, y) in clear and F[y][x] != '#' else F[y][x]) for x in range(W)))

    def free(x, y):
        return 0 <= x < W and 0 <= y < H and F[y][x] in 'uihsmf.' and obj[y][x] == ' ' and (x, y) not in clear

    def fits(name, x, y, door=False):
        w, h, solid = SIZES[name]
        ok = (lambda xx, yy: 0 <= xx < W and 0 <= yy < H and F[yy][xx] in 'uihsmf.' and obj[yy][xx] == ' ') if door else free
        return all(ok(xx, yy) for yy in range(y + h - max(solid, 1), y + h) for xx in range(x, x + w))

    def thing(kind, title, hint, x, y, rad=26):
        things.append([kind, title, hint, 'top', [int(x * 16 + 8), int(y * 16 + 8)], rad])

    def prop(name, x, y, title, kind='look', hint='Look', must=True, door=False):
        w, h, solid = SIZES[name]
        if not fits(name, x, y, door):
            if must:
                dump()
            assert not must, ('Survey Level prop does not fit', name, x, y, title)
            return False
        props.append([name, x, y, w, h, title])
        for yy in range(y + h - solid, y + h):
            for xx in range(x, x + w):
                obj[yy][xx] = 'x'
        if kind:
            thing(kind, title, hint, x + (w - 1) / 2, y + h - 1)
        return True

    def near(name, fx, fy, title, kind='look', hint='Look', within=None):
        """Places a prop whose base centre is as close as possible to fx,fy (continuous tiles)."""
        w, h, solid = SIZES[name]
        best = None
        for y in range(int(fy) - 4, int(fy) + 5):
            for x in range(int(fx) - 4, int(fx) + 5):
                if fits(name, x, y) and (within is None or all(within(xx, yy) for xx in (x, x + w - 1) for yy in (y + h - 1,))):
                    d = math.hypot(x + w / 2 - fx, y + h - .5 - fy)
                    if best is None or d < best[0]: best = (d, x, y)
        if not best:
            print('note: no room on the Survey Level for', name, title, round(fx, 1), round(fy, 1)); return False
        return prop(name, best[1], best[2], title, kind, hint)

    # S.A.R.A.'s core (see mock/sara_core_closeup.png)
    prop('holo_dais', 42, 22, 'Hologram dais', 'look', 'Look')
    prop('wall_screen', 38, 16, 'Station map screen'); prop('wall_screen', 45, 16, 'Station map screen')
    prop('concierge_desk', 35, 19, 'Concierge desk'); prop('paris_pictures', 49, 19, 'Pictures of Paris')
    prop('tape_archive', 34, 22, 'Signal tape archive'); prop('sensor_panel', 51, 22, 'Deep-space sensor read-outs')
    prop('memory_core', 34, 26, 'Memory core'); prop('memory_core', 51, 26, 'Memory core')
    prop('memory_core', 37, 29, 'Memory core'); prop('memory_core', 48, 29, 'Memory core')
    prop('console', 40, 28, 'Operator console'); prop('console', 45, 28, 'Operator console')
    DATA_LINES = [(35.0, 28.5), (52.0, 28.5), (38.0, 31.5), (49.0, 31.5), (35.0, 24.5), (52.0, 24.5)]
    # Observation Lounge: telescope in the middle, benches facing the window, star charts and plants between.
    near('telescope', 43.5, 11.5, 'Lunar telescope', 'observe', 'Look through telescope')
    thing('look', 'Panoramic window', 'Look outside', 43, 13, 40)
    for ang in (215, 238, 302, 325):
        a = math.radians(ang); near('bench_n', OX + 29.6 * math.cos(a), OY + 29.6 * math.sin(a), 'Lounge bench [N]', 'seat', 'Sit')
    for ang, side in ((197, 'w'), (343, 'e')):
        a = math.radians(ang); near('bench_' + side, OX + 30 * math.cos(a), OY + 30 * math.sin(a), 'Lounge bench [%s]' % side.upper(), 'seat', 'Sit')
    for ang in (226, 250, 290, 314):
        a = math.radians(ang); near('star_chart', OX + 28.4 * math.cos(a), OY + 28.4 * math.sin(a), 'Star chart')
    for ang in (205, 262, 278, 335):
        a = math.radians(ang); near('plants', OX + 30.6 * math.cos(a), OY + 30.6 * math.sin(a), 'Lounge planter', 'inspect', 'Inspect')
    # Museum: a centrepiece, rows of cases on three arcs, Tar'Besh's desk by the Sanctum.
    museum = lambda x, y: F[y][x] == 'h'
    near('museum_centerpiece', OX + 19 * math.cos(math.radians(222)), OY + 19 * math.sin(math.radians(222)) + 1, "The Weaver's Wing", within=museum)
    n = 0
    for rr, angs in ((15.5, (201, 213, 225)), (22.5, (198, 208, 218, 230, 242))):
        for ang in angs:
            a = math.radians(ang); art_, title, _ = EXHIBITS[n % len(EXHIBITS)]
            if near(art_, OX + rr * math.cos(a), OY + rr * math.sin(a), title, within=museum): n += 1
    near('curator_desk', 24.5, 33.5, "Tar'Besh's desk", within=museum)
    prop('sanctum_door', door_col, 38, 'Sanctum door', 'look', 'Look', door=True)
    # Sanctum: three crystals round the middle.
    for ang in (270, 30, 150):
        a = math.radians(ang); near('crystal_pedestal', SANCT[0] + 2.8 * math.cos(a), SANCT[1] + 2.8 * math.sin(a) + 1, 'Precursor crystal')
    # Sealed lab: its door, then old consoles and crates inside.
    lx, ly = min(c[0] for c in lab_cells), min(c[1] for c in lab_cells)
    for c in lab_cells: clear.discard(c)
    door_x, door_y = sorted(lab_cells, key=lambda c: (c[1], c[0]))[0]
    lab_door = [c for c in lab_cells if r_ang(*c)[0] >= 26.0]
    bx, by = min(c[0] for c in lab_door), max(c[1] for c in lab_door)
    placed = False
    for x0 in range(bx - 2, bx + 2):
        for y0 in range(by - 2, by + 2):
            if not placed and fits('sealed_door', x0, y0, True):
                placed = prop('sealed_door', x0, y0, 'Sealed lab', 'look', 'Look', door=True)
    assert placed, 'sealed lab door'
    labin = lambda x, y: F[y][x] == 'm'
    for fx, fy, nm, tl in ((60, 26, 'console', 'Dusty console'), (55, 21, 'cargo', 'Sealed crates'), (64, 31, 'console', 'Dusty console'), (58, 33, 'cargo', 'Sealed crates')):
        near(nm, fx, fy, tl, None, within=labin)
    # Tar'Besh's quarters and the spare room
    prop('bed', 29, 36, "Tar'Besh's bed", None); prop('wardrobe', 35, 36, "Tar'Besh's wardrobe", None)
    prop('books', 29, 41, "Tar'Besh's books", 'look', 'Look'); prop('plants', 35, 41, 'Prayer garden', 'inspect', 'Inspect')
    prop('cargo', 55, 36, 'Spare crates', None); prop('cargo', 49, 36, 'Spare crates', None)
    # Lift lobby
    prop('plants', 39, 42, 'Lobby planter', 'inspect', 'Inspect'); prop('plants', 45, 42, 'Lobby planter', 'inspect', 'Inspect')

    g.setdefault('AREA_PROPS', {})['top'] = props
    g.setdefault('AREA_ROOF_PROPS', {})['top'] = []
    g.setdefault('AREA_LIGHTS', {})['top'] = []
    g.setdefault('FLOOR_EXTRAS', {})['top'] = {'data_lines': [[[43.5, 23.5], list(p)] for p in DATA_LINES], 'dais': [43.5, 23.5]}
    g.setdefault('EXTRA_THINGS', []).extend(things)
    g.setdefault('EXTRA_LOOKS', {}).update({ex[1]: ex[2] for ex in EXHIBITS})
    return t
