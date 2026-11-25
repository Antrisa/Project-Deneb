"""The public rooms off the Community Concourse, rebuilt in the promenade style (Zachary, 24 Nov: "the mess hall,
but also the community center and some other shops like armoury, Bram's shop, Sesska's shop").

Each room keeps its old floor plan, so everyone's usual spots still work: the old room sits inside the new map
moved ROOM_SHIFT tiles right and down (the new walls are two tiles thick). tools/build.py's moved() applies the
shift to every schedule stop in these rooms, and the heart events set there were shifted the same way.

  common   Common room (the community centre), bigger than the old room: the main hall with the activity corner,
           the reading corner and the fireplace lounge round it, and a chapel and a meeting room behind doors.
  bram     Bram's Sundries: a long counter down the middle, stock shelves, crates and barrels behind it.
  weaver   Sesska's shop: loom and silk on the back wall, the counter across the room, a fitting stool, a clothes
           rack and a chair in front.
  armoury  Ix'ali's armoury: a weapon rack, her forge and arc-anvil and the lockers behind a glass-topped counter,
           crates and a training dummy in front.
  library  Owen's library: bookcases round the walls and the archive in the top corner, the school corner (lesson
           board, three desks) in the middle, reading tables either side, luminescent ferns.
  mess   Mess hall: the kitchen in the north-east behind a serving counter (Jasper cooks facing the room),
         two rows of five mess tables with chairs either side, the menu board, a juice dispenser and the tray
         return by the windows on the north wall (a view of the stars).
Drawn in the promenade style; floors and walls baked by tools/bake_floor.py, wallpapered like the homes."""
import os
import numpy as np
from PIL import Image
import survey
from survey import SIZES
from spaceport import fill
from residences import Home

ROOM_SHIFT = {"mess": (2, 2), "common": (12, 11), "bram": (2, 2), "weaver": (2, 2), "armoury": (2, 2), "library": (2, 2)}
# Spots that don't just move with the old plan but go to a particular new place: (map, old x, old y) -> new x, y.
# The library (25 Nov): the kids at their school desks, Owen at his shelves, the readers at the reading tables.
RESPOT = {("library", 7, 9): (8, 12), ("library", 9, 9): (10, 12), ("library", 11, 10): (12, 12),
          ("library", 8, 8): (16, 9), ("library", 8, 10): (15, 13), ("library", 5, 11): (4, 13),
          ("library", 6, 11): (5, 13), ("library", 12, 12): (14, 13)}
SIZES.update({'serving_counter': (3, 2, 1), 'mess_table': (2, 1, 1), 'menu_board': (2, 3, 1),
              'kitchen_stove': (2, 2, 1), 'kitchen_bot': (1, 2, 1), 'protein_synthesizer': (1, 2, 1),
              'recycler': (2, 2, 1), 'potted_plant': (1, 2, 1), 'chair_s': (1, 2, 0), 'chair_n': (1, 2, 0),
              'fabric_counter': (3, 2, 1), 'arms_counter': (3, 2, 1), 'side_counter': (1, 2, 2), 'weapon_rack': (3, 3, 1),
              'loom': (2, 2, 1), 'altar': (3, 2, 1), 'candle_stand': (1, 2, 1), 'bedside_lamp': (1, 2, 1), 'anvil': (1, 1, 1), 'bench_fitting': (1, 1, 0), 'library_shelf': (3, 3, 1), 'archive_shelf': (3, 3, 1),
              'school_desk': (1, 1, 1), 'reading_table': (3, 1, 1), 'lesson_board': (2, 3, 1), 'lumen_fern': (1, 2, 1), 'crew_board': (2, 3, 1), 'arcade': (2, 3, 1), 'bookshelf_steel': (2, 3, 1)})

DINING = ('hotel/dining_mineral_mix', None)
DECK = ('home/deck', None)
HERRINGBONE = ('hotel/warm_deck_mix', None)
CARPET = ('home/carpet', None)
SLATE = ('home/slate', None)
NAVY = ('home/navy', None)
KITCHEN_TILE = ('hotel/kitchen_ceramic_mix', None)


class PublicRoom(Home):
    """A public room's map: the old room (w x h, walls included) moved by ROOM_SHIFT into thicker walls."""
    def __init__(self, g, key, title, old_w, old_h, old_door_x, floors, size=None):
        dx, dy = ROOM_SHIFT[key]
        W, H = size or (old_w + 2 * dx, old_h + 2 * dy)
        door_x = old_door_x + dx
        self.g, self.key, self.title, self.W, self.H, self.bottom = g, key, title, W, H, False
        self.r = survey.Room(g, key, title, W, H)
        self.F = self.r.F
        fill(self.F, 1, 1, W - 2, H - 2, '#')
        self.door = (door_x, H - 3)
        self.floors = floors
        self.zones, self.inner, self.spots, self.taken, self.doors, self.notes = [], [], {}, set(), set(), []
        self.F[H - 3][door_x] = 'o'
        self.r.keep_clear(door_x - 1, H - 6, door_x + 1, H - 3)
        self.dx, self.dy = dx, dy

    def area(self, label, x0, y0, x1, y1, ch):
        self.carve(x0, y0, x1, y1, ch)
        if label:
            self.zones.append([label, x0, y0, x1, y1])

    def side_door(self, label, x, y, what, owner=''):
        """A sliding door two tiles tall in a wall running north-south, at (x, y) and (x, y + 1)."""
        for yy in (y, y + 1):
            self.F[yy][x] = 'o'
            self.doors.add((x, yy))
        self.inner.append([self.key, x, y, 1, 2, 'E', owner, what])
        self.r.keep_clear(x - 2, y, x + 2, y + 1)

    def p(self, name, x, y, title, kind=None, hint='Look'):
        return self.r.prop(name, x, y, title, kind, hint)


def window_strip(width_px, seed=4, centre=None):
    """The view through the mess hall's north windows: deep space, stars, the edge of the gas giant."""
    rng = np.random.default_rng(seed)
    H = 48
    yy, xx = np.mgrid[0:H, 0:width_px]
    sky = np.zeros((H, width_px, 3))
    top, bot = np.array([18, 16, 44]), np.array([52, 36, 86])
    t = (yy / (H - 1))[..., None]
    sky[:] = top * (1 - t) + bot * t
    # the gas giant's limb low in the window, banded warm
    cx, cy, r = (width_px * 0.42 if centre is None else centre), 150.0, 128.0    # the planet: centred on the windows
    d = np.hypot(xx - cx, yy - cy)
    planet = d < r
    band = (((yy + (xx - cx) * 0.12) // 5) % 3).astype(int)
    pcol = np.array([[236, 170, 110], [210, 128, 92], [248, 206, 140]], float)[band]
    rim = np.clip((r - d) / 10, 0, 1)[..., None]
    sky = np.where(planet[..., None], pcol * (0.55 + 0.45 * rim), sky)
    sky = np.where(((d >= r) & (d < r + 2))[..., None], np.array([255, 220, 180]) * 0.8, sky)
    for _ in range(width_px // 6):
        x, y = rng.integers(0, width_px), rng.integers(1, H - 4)
        if not planet[y, x]:
            sky[y, x] = (255, 250, 230) if rng.random() < 0.3 else (190, 196, 240)
    # window frames: a mullion every three tiles, a sill along the bottom
    for x in range(0, width_px, 72):
        sky[:, x:x + 3] = (120, 96, 110); sky[:, x + 3] = (70, 52, 70)
    sky[:3] = (150, 120, 120); sky[3] = (90, 66, 80)
    sky[-4:] = (196, 160, 130); sky[-4] = (236, 206, 170); sky[-1] = (110, 76, 72)
    return Image.fromarray(sky.astype(np.uint8), "RGB")


def build_mess(g):
    """The mess hall (old room 31 x 20, door at x 14)."""
    m = PublicRoom(g, 'mess', 'Mess hall', 31, 20, 14, {'o': DINING, 'k': KITCHEN_TILE})
    r = m.r
    m.area('Dining hall', 3, 3, 31, 20, 'o')
    m.area('Kitchen', 20, 3, 31, 6, 'k')
    for x in range(11, 18):                                         # the windows in the north wall
        m.F[2][x] = 'w'
    r.keep_clear(19, 3, 19, 8)                                      # the way into the kitchen, round the counter
    r.keep_clear(20, 5, 31, 6)                                      # the cooks' aisle behind the counter
    # kitchen: everything stands against the back wall, the counter across its front
    m.p('kitchenette', 20, 2, 'Sinks and prep counter', 'look')
    m.p('kitchen_stove', 24, 3, 'Range and ovens', 'look')
    m.p('fridge', 26, 2, 'Cold store', 'look')
    m.p('storage_shelf', 28, 2, 'Pantry shelves', 'look')
    m.p('kitchen_bot', 31, 3, 'Kitchen bot', 'look')
    for x in (20, 23, 26, 29):
        m.p('serving_counter', x, 6, 'Serving counter', 'look')
    # dining: two rows of five tables, two chairs either side of each (the old stools' places)
    for ty in (10, 15):
        for tx in (6, 11, 16, 21, 26):
            m.p('mess_table', tx, ty, 'Mess table')
            for x in (tx, tx + 1):
                m.p('chair_s', x, ty - 2, 'Dining chair [S]', 'seat', 'Sit')
                m.p('chair_n', x, ty, 'Dining chair [N]', 'seat', 'Sit')
    # along the north wall, west of the windows: the menu, drinks and the tray return
    m.p('tree_tub', 3, 3, 'Potted fern tree')
    m.p('menu_board', 5, 2, "Today's menu", 'look')
    m.p('protein_synthesizer', 7, 3, 'Juice dispenser', 'look')
    m.p('recycler', 8, 3, 'Tray return', 'look')
    m.p('potted_plant', 18, 3, 'Potted plant')
    # the corners by the door, and a bin by the kitchen
    m.p('tree_tub', 3, 18, 'Potted fern tree')
    m.p('tree_tub', 31, 18, 'Potted fern tree')
    m.p('bin', 31, 9, 'Recycling bin')
    m.p('planter_long', 5, 18, 'Herb planter')
    m.p('planter_long', 24, 18, 'Herb planter')
    m.p('drinking_fountain', 3, 8, 'Water point', 'look')
    m.finish()
    art = os.path.join(g['OUT'], 'art', 'lunar')
    window_strip(m.W * 24).save(os.path.join(art, 'window_mess.png'))


def build_common(g):
    """The common room, the community centre (Zachary, 24 Nov: "bigger with more rooms and props, a reading
    corner, an activity corner, a fireplace area, a worship area"). The old room is the main hall in the middle
    (moved ROOM_SHIFT['common'] tiles in); round it:
      north  the activity corner (arcades, games tables, a craft table, the kids' play frame), open to the hall
      west   the reading corner (shelves, reading chairs and lamps), open to the hall; behind a door below it,
             the chapel (an altar, candles, prayer mats, two rows of chairs), for anyone of any faith: Tar'Besh leads
             a service there on Sunday mornings (tools/build.py SCHEDULE_DAYS_RAW)
      east   the fireplace lounge, open to the hall; behind a door below it, the meeting room
    """
    m = PublicRoom(g, 'common', 'Common room', 25, 18, 12, {'o': HERRINGBONE, 'a': SLATE, 'j': NAVY, 'h': CARPET,
                                                            't': DINING, 'k': DECK}, size=(49, 31))
    r = m.r
    m.area('Main hall', 13, 12, 35, 27, 'o')
    m.area('', 18, 16, 26, 21, 'h')                                  # a big rug in the middle, where people gather
    m.area('Activity corner', 13, 3, 35, 10, 'a')
    m.area('Reading corner', 3, 3, 11, 17, 'j')
    m.area('Fireplace lounge', 37, 3, 45, 17, 'h')
    m.area('Chapel', 3, 19, 11, 27, 't')
    m.area('Meeting room', 37, 19, 45, 27, 'k')
    # inside walls (everything not carved above is wall): the activity corner's wide opening between half walls,
    # and the openings from the hall into the reading corner and the fireplace lounge
    m.carve(19, 11, 29, 11, 'o')
    m.carve(12, 13, 12, 16, 'o'); m.carve(36, 13, 36, 16, 'o')
    m.side_door('', 12, 23, 'chapel'); m.side_door('', 36, 23, 'meeting room')
    for x in list(range(5, 10)) + list(range(20, 29)):
        m.F[2][x] = 'w'
    r.keep_clear(19, 9, 29, 12); r.keep_clear(9, 13, 13, 16); r.keep_clear(35, 13, 38, 16)
    # activity corner
    m.p('arcade', 13, 2, 'Arcade cabinet', 'look')
    m.p('arcade', 15, 2, 'Arcade cabinet', 'look')
    m.p('scoreboard', 17, 2, 'Activities board', 'look')
    m.p('play_piece', 30, 3, "Kids' play frame", 'look')
    m.p('chess', 21, 6, 'Chess table', 'look')
    m.p('hologame', 25, 6, 'Holo-game table', 'look')
    m.p('table', 14, 7, 'Craft table', 'seat', 'Sit')
    m.p('workbench', 32, 7, 'Craft bench', 'look')
    # reading corner
    m.p('books', 3, 3, 'Lending shelf', 'look')
    m.p('bookshelf_steel', 10, 2, 'Board games and puzzles', 'look')
    m.p('books', 3, 8, 'Lending shelf', 'look')
    m.p('armchair', 6, 6, 'Reading chair', 'seat', 'Sit')
    m.p('bedside_lamp', 8, 6, 'Reading lamp')
    m.p('armchair', 9, 6, 'Reading chair', 'seat', 'Sit')
    m.p('cafe_table', 7, 10, 'Side table')
    m.p('sofa', 4, 13, 'Reading sofa', 'seat', 'Sit')
    m.p('potted_plant', 3, 15, 'Potted plant')
    # main hall: the tea corner and the notice board under the half walls, tables to the east, planters by the door
    m.p('kitchenette', 13, 10, 'Tea and coffee corner', 'look')
    m.p('crew_board', 31, 10, 'Community notice board', 'look')
    for (x, y) in ((29, 15), (29, 21), (14, 15), (14, 21)):
        m.p('table', x, y, 'Table', 'seat', 'Sit')
    m.p('tree_tub', 13, 25, 'Potted tree')
    m.p('tree_tub', 35, 25, 'Potted tree')
    m.p('planter_long', 15, 25, 'Flower planter')
    m.p('planter_long', 28, 25, 'Flower planter')
    # fireplace lounge
    m.p('fireplace', 40, 2, 'Fireplace', 'look')
    m.p('books', 37, 3, 'Bookshelf', 'look')
    m.p('plants', 43, 3, 'Planter')
    m.p('armchair', 37, 8, 'Fireside armchair', 'seat', 'Sit')
    m.p('cafe_table', 40, 9, 'Coffee table')
    m.p('armchair', 43, 8, 'Fireside armchair', 'seat', 'Sit')
    m.p('sofa', 39, 12, 'Sofa', 'seat', 'Sit')
    m.p('potted_plant', 45, 12, 'Potted plant')
    m.p('tree_tub', 45, 15, 'Potted tree')
    # chapel: the altar against the north wall between two candle stands, pews facing it, prayer mats
    m.p('candle_stand', 4, 19, 'Candle stand')
    m.p('altar', 6, 19, 'Altar', 'look')
    m.p('candle_stand', 10, 19, 'Candle stand')
    m.p('prayer_mat', 4, 21, 'Prayer mat')
    m.p('prayer_mat', 8, 21, 'Prayer mat')
    # two rows of chairs facing the altar (chairs, not pews, so the congregation can sit in them: Sunday service)
    for y in (23, 25):
        for x in (4, 5, 7, 8):
            m.p('chair_n', x, y - 1, 'Chapel chair [N]', 'seat', 'Sit')
    # meeting room
    m.p('wall_screen', 40, 19, 'Meeting screen', 'look')
    for (x, y) in ((39, 22), (43, 22), (39, 25), (43, 25)):
        m.p('table', x, y, 'Meeting table', 'seat', 'Sit')
    m.p('potted_plant', 45, 19, 'Potted plant')
    m.finish()
    window_strip(m.W * 24, 7, 24 * 24).save(os.path.join(g['OUT'], 'art', 'lunar', 'window_common.png'))


def build_bram(g):
    """Bram's Sundries (old room 12 x 10, door at x 4): a long counter down the middle of the shop, shelves
    of stock behind it on the east side, customers on the west."""
    m = PublicRoom(g, 'bram', "Bram's Sundries", 12, 10, 4, {'o': DECK})
    r = m.r
    m.area("Bram's Sundries", 3, 3, 12, 10, 'o')
    r.keep_clear(9, 3, 9, 3); r.keep_clear(9, 10, 10, 10)          # round either end of the counter
    for y in (4, 6, 8):
        m.p('side_counter', 9, y, "Bram's counter", 'look')
    m.p('storage_shelf', 10, 2, 'Stock shelves', 'look')
    m.p('cargo', 11, 6, 'Crates of stock', 'look')
    m.p('barrel_stack', 11, 8, 'Barrels', 'look')
    m.p('potted_plant', 3, 3, 'Potted plant')
    m.p('kiosk', 4, 2, 'Sundries display', 'look')
    m.p('cargo', 3, 8, 'Crates')
    m.finish()


def build_weaver(g):
    """Sesska's shop (old room 11 x 10, door at x 5): her loom and bolts of silk along the back wall, the
    counter across the room, a rack of finished clothes and a chair for customers in front."""
    m = PublicRoom(g, 'weaver', "Weaver's shop", 11, 10, 5, {'o': DECK, 'j': CARPET})
    r = m.r
    m.area("Weaver's shop", 3, 3, 11, 10, 'o')
    m.area('', 3, 8, 11, 10, 'j')
    m.p('textiles', 3, 3, 'Bolts of bug silk', 'look')
    m.p('loom', 6, 3, '')
    m.p('textiles', 9, 3, 'Bolts of bug silk', 'look')
    for x in (4, 7):
        m.p('fabric_counter', x, 6, "Sesska's counter", 'look')
    m.p('armchair', 3, 8, 'Armchair', 'seat', 'Sit')
    m.p('bench_fitting', 5, 9, 'Fitting stool', 'look')               # where Stu and Tikka get fitted (heart events)
    m.p('clothes', 9, 8, 'Rack of finished clothes', 'look')
    m.finish()


def build_armoury(g):
    """The armoury (old room 11 x 10, door at x 5): weapon racks and lockers behind the counter, crates and
    a training dummy on the customers' side."""
    m = PublicRoom(g, 'armoury', 'Armoury', 11, 10, 5, {'o': SLATE})
    r = m.r
    m.area('Armoury', 3, 3, 11, 10, 'o')
    # set back into the wall a tile, so Ix'ali's heart events have the aisle behind the counter (two rows)
    m.p('weapon_rack', 3, 1, 'Weapon racks', 'look')
    m.p('furnace', 6, 1, 'Forge', 'look')                            # Ix'ali's forge and arc-anvil (her heart events)
    m.p('anvil', 8, 3, 'Arc-anvil', 'look')
    m.p('locker', 10, 1, 'Lockers', 'look')
    for x in (4, 7):
        m.p('arms_counter', x, 5, 'Armoury counter', 'look')
    m.p('cargo', 3, 8, 'Ammunition crates', 'look')
    m.p('punching_bag', 11, 8, 'Training dummy', 'look')
    m.finish()


def build_library(g):
    """Owen's library (old room 17 x 15, door at x 8): bookcases along the north wall with the archive in the top
    corner (Pip's 2), bookcases down both sides, the school corner in the middle (the lesson board, three desks
    with chairs: Pip, Kit and Nub's lessons, Owen's 2), reading tables either side of the door's walk (Jasper and
    Maren; Artie and Quill, by the luminescent ferns: Quill's 8)."""
    m = PublicRoom(g, 'library', 'Library', 17, 15, 8, {'o': HERRINGBONE, 'j': NAVY})
    r = m.r
    m.area('Library', 3, 3, 17, 15, 'o')
    m.area('', 8, 10, 12, 13, 'j')                                  # a rug under the school desks
    for x in (3, 6, 9, 12):
        m.p('library_shelf', x, 1, 'Library shelves', 'look')
    m.p('archive_shelf', 15, 1, 'The archive', 'look')
    m.p('library_shelf', 3, 6, 'Library shelves', 'look')
    m.p('library_shelf', 15, 6, 'Library shelves', 'look')
    m.p('lesson_board', 9, 6, 'Lesson board', 'look')
    for x in (8, 10, 12):
        m.p('school_desk', x, 11, 'School desk', 'look')
        m.p('chair_n', x, 11, 'School chair [N]', 'seat', 'Sit')
    m.p('reading_table', 3, 12, 'Reading table', 'look')
    m.p('reading_table', 14, 12, 'Reading table', 'look')
    for x in (3, 4, 5, 14, 15, 16):
        m.p('chair_n', x, 12, 'Reading chair [N]', 'seat', 'Sit')
    m.p('bedside_lamp', 6, 11, 'Reading lamp')
    m.p('lumen_fern', 17, 9, 'Luminescent ferns', 'look')
    m.p('lumen_fern', 17, 12, 'Luminescent ferns', 'look')              # beside Quill's reading chair (his 8)
    m.p('potted_plant', 3, 9, 'Potted plant')
    m.finish()


def build(g):
    saved = survey.WALKABLE
    survey.WALKABLE = '.shafkoteuj'
    build_mess(g)
    build_common(g)
    build_bram(g)
    build_weaver(g)
    build_armoury(g)
    build_library(g)
    survey.WALKABLE = saved
