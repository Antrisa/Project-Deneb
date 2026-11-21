"""The homes off the Community Concourse, rebuilt in the promenade style (Zachary, 20 Nov).

The outside stays as it is: the same six doors on the promenade, the same signs (only "Empty flats" becomes
"Residences C", because it is no longer empty). Inside, each home is its own map and bigger than its door
suggests. Every home has:
  - a room for each person (couples share one), along the top, and in the bigger homes along the bottom
    too, either side of the entrance hall. Bedroom doors lock until you have BEDROOM_HEARTS hearts with the
    owner (scripts/main.gd);
  - one open room in the middle: the kitchen, the dining table and the family area;
  - a washroom.
Who lives where:
  aptB    Residences B           Bram, Freya, Job, Zaas
  aptA    Residences A           Jasper, Evarra
  aptDoc  Family residences      Maren and Owen, Pip, Owen's study, Maren's home clinic
  aptSec  Security residences    Garrick and Saffi, Kit
  aptMoog Moogli residences      Tobbin and Merrow, Nub
  aptEmpty Residences C          Quill, Ix'ali, Tar'Besh, and a little Zaa'sh shrine
Each room is decorated for whoever sleeps in it, and each resident's night stop is beside their own bed
(HOME_SPOTS, used by SCHEDULES_RAW in tools/build.py).
Drawn in the promenade style; floors and walls baked by tools/bake_floor.py."""
import survey
import engineering, spaceport, east     # their prop sizes
from survey import Room, SIZES
from spaceport import fill

WALKABLE = '.shafkoteuj'
SIZES.update({'textiles': (3, 2, 1), 'clothes': (3, 2, 1), 'medical': (2, 3, 1), 'hologame': (2, 2, 1),
              'chess': (2, 2, 1), 'play_piece': (3, 2, 1)})

DECK = ('hotel/warm_deck_mix', None)
KITCHEN = ('hotel/kitchen_ceramic_mix', None)
BATH = ('residential/bath_ceramic_mix', None)
CARPET = 'residential/red_carpet_mix'
NAVY = 'hotel/navy_mix'
SLATE = 'residential/slate_deck_mix'
MINERAL = 'hotel/dining_mineral_mix'


def free_spot(room, fx, fy, taken, doors):
    """The free floor tile nearest (fx, fy) for someone to stand on: not under a prop, not in a doorway."""
    best = None
    for y in range(int(fy) - 4, int(fy) + 5):
        for x in range(int(fx) - 4, int(fx) + 5):
            if room.free(x, y, door=True) and (x, y) not in taken and (x, y) not in doors:
                d = (x + .5 - fx) ** 2 + (y + .5 - fy) ** 2
                if best is None or d < best[0]: best = (d, x, y)
    assert best, ('nowhere to stand', room.key, fx, fy)
    taken.add(best[1:])
    return best[1], best[2]


class Home:
    """One home's map. Top rooms: y 3..10, their doors in the wall at y 11. The open room: y 12..21 (with
    bottom rooms) or 12..23. Bottom rooms: y 23..30, doors in the wall at y 22, either side of the entrance
    hall. The front door is in the bottom wall at door_x."""
    def __init__(self, g, key, title, W, bottom, door_x, floors):
        H = 34 if bottom else 27
        self.g, self.key, self.title, self.W, self.H, self.bottom = g, key, title, W, H, bottom
        self.r = Room(g, key, title, W, H)
        self.F = self.r.F
        fill(self.F, 1, 1, W - 2, H - 2, '#')
        self.y1 = 21 if bottom else 23
        self.door = (door_x, H - 3)
        self.floors = dict(floors, o=DECK, k=KITCHEN, t=BATH)
        self.zones, self.inner, self.spots, self.taken, self.doors = [], [], {}, set(), set()
        self.notes = []
        self.carve(3, 12, W - 4, self.y1, 'o')
        if bottom:
            self.carve(door_x - 2, 22, door_x + 2, 30, 'o')
            self.zones.append(['Entrance hall', door_x - 2, 22, door_x + 2, 30])
        self.F[H - 3][door_x] = 'o'
        self.r.keep_clear(door_x - 1, (20 if bottom else self.y1 - 2), door_x + 1, H - 3)

    def carve(self, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.F[y][x] = ch

    def room(self, label, x0, x1, row, ch, door_x, owner='', what='bedroom'):
        """A room along the top or bottom, with a sliding door into the open room."""
        y0, y1, wall = (3, 10, 11) if row == 'top' else (23, 30, 22)
        self.carve(x0, y0, x1, y1, ch)
        self.F[wall][door_x] = 'o'
        self.doors.add((door_x, wall))
        self.inner.append([self.key, door_x, wall, 1, 1, 'S', owner, what])
        self.r.keep_clear(door_x, wall - 2, door_x, wall + 2)
        self.zones.append([label, x0, y0, x1, y1])

    def open_plan(self, kitchen_x1, kitchen_y1, dining, family):
        """Names the parts of the open room: the kitchen in the top-left corner (floored in tile), the dining
        table and the family area."""
        self.carve(3, 12, kitchen_x1, kitchen_y1, 'k')
        self.zones.append(['Kitchen', 3, 12, kitchen_x1, kitchen_y1])
        self.zones.append(['Dining area'] + list(dining))
        self.zones.append(['Family area'] + list(family))

    def put(self, name, fx, fy, title, kind=None, hint='Look'):
        if kind in ('inspect',): hint = 'Inspect'
        if kind == 'seat': hint = 'Sit'
        at = self.r.near(name, fx, fy, title, kind, hint)
        if at is None: self.notes.append((name, title))
        return at

    def bed(self, name, fx, fy, title, sleepers):
        """A bed, and a place beside it for each sleeper's night stop."""
        at = self.put(name, fx, fy, title, 'look')
        assert at, ('no room for a bed', self.key, title)
        w, h, _ = SIZES[name]
        x, y = at
        sides = [(x + w + .5, y + h - .5), (x + w / 2, y + h + .5), (x - .5, y + h - .5)]
        for who, (sx, sy) in zip(sleepers, sides):
            self.spots[who] = (self.key,) + free_spot(self.r, sx, sy, self.taken, self.doors)
        return at

    def spot(self, label, fx, fy):
        """A daytime stop at home (HOME_SPOTS[label]): Saffi sweeping, Kit playing in his room."""
        self.spots[label] = (self.key,) + free_spot(self.r, fx, fy, self.taken, self.doors)

    def finish(self):
        g, r = self.g, self.r
        r.t.zones += self.zones
        # the way out: concourse.rebuild points it at the promenade door; the promenade door lands you here
        r.t.warps.append([self.door[0], self.door[1], 'main', 0, 0])
        bx, by, ch, _, _ = g['DOORS'][self.key]
        old = g['m']
        old.warps = [w for w in old.warps if w[2] != self.key]
        old.warp(ch, [(bx, by)], self.key, self.door[0], self.door[1] - 1)
        g.setdefault('INNER_DOORS', []).extend(self.inner)
        import bake_floor
        bake_floor.AREA_FLOORS[self.key] = self.floors
        g.setdefault('AREA_PROPS', {})[self.key] = r.props
        g.setdefault('AREA_ROOF_PROPS', {})[self.key] = []
        g.setdefault('AREA_LIGHTS', {})[self.key] = []
        g.setdefault('EXTRA_THINGS', []).extend(r.things)
        g.setdefault('LUNAR_EXTRA', {})[self.title] = self.key
        g.setdefault('HOME_SPOTS', {}).update(self.spots)
        self.check()
        for name, title in self.notes:
            print('note: no room in %s for %s (%s)' % (self.key, name, title))

    def check(self):
        """Everyone can get from the front door to every room, bed-side spot and seat."""
        r = self.r
        start = (self.door[0], self.door[1] - 1)
        seen, todo = {start}, [start]
        while todo:
            x, y = todo.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if (nx, ny) not in seen and r.F[ny][nx] in WALKABLE and r.obj[ny][nx] == ' ':
                    seen.add((nx, ny)); todo.append((nx, ny))
        for (_, x, y) in self.spots.values():
            assert (x, y) in seen, ('night stop cut off', self.key, x, y)
        for d in self.doors:
            assert d in seen, ('door cut off', self.key, d)


def build(g):
    saved = survey.WALKABLE
    survey.WALKABLE = WALKABLE

    # ============================================================ Residences B: Bram, Freya, Job, Zaas
    hm = Home(g, 'aptB', 'Residences B', 33, True, 16, {
        'h': (CARPET, ('7a6a3a', .25)), 'j': (NAVY, None), 's': (SLATE, None), 'a': (NAVY, ('2a8a90', .35))})
    hm.room("Bram's room", 3, 11, 'top', 'h', 9, 'Bram')
    hm.room("Freya's room", 13, 21, 'top', 'j', 19, 'Freya')
    hm.room('Washroom', 23, 29, 'top', 't', 26, '', 'washroom')
    hm.room("Job's room", 3, 12, 'bottom', 's', 8, 'Job')
    hm.room("Zaas's room", 20, 29, 'bottom', 'a', 24, 'Zaas')
    hm.open_plan(14, 16, (3, 17, 14, 21), (16, 12, 29, 21))
    hm.bed('bed', 4, 5.5, "Bram's bed", ['Bram'])
    hm.put('wardrobe', 7, 4.5, 'Wardrobe'); hm.put('books', 11, 4.5, "Bram's ledgers", 'look')
    hm.put('footlocker', 4, 8.5, "Bram's strongbox", 'look'); hm.put('cargo', 7, 8.5, 'Salvage crate', 'look')
    hm.bed('bed', 14, 5.5, "Freya's bed", ['Freya'])
    hm.put('workbench', 17.5, 4.5, "Freya's bench", 'look'); hm.put('tool_cart', 21, 4.5, 'Tool cart')
    hm.put('wardrobe', 14, 8.5, 'Wardrobe'); hm.put('star_chart', 17, 8.5, 'Ship schematics', 'look')
    hm.bed('bed', 4, 25.5, "Job's bed", ['Job'])
    hm.put('wardrobe', 12, 25.5, 'Wardrobe'); hm.put('gym_rack', 5.5, 29.5, "Job's weights", 'look')
    hm.put('cargo', 11, 29.5, 'Box of geodes', 'look')
    hm.bed('bed', 29, 25.5, "Zaas's bed", ['Zaas'])
    hm.put('telescope', 21, 25.5, "Zaas's telescope", 'look'); hm.put('star_chart', 27, 25.5, "Zaas's ocean charts", 'look')
    hm.put('water_tank', 21, 29.5, 'Fish tank', 'look'); hm.put('wardrobe', 28.5, 29.5, 'Wardrobe')
    hm.put('shower', 24, 5.5, 'Shower'); hm.put('toilet', 27.5, 4.5, 'Toilet'); hm.put('bath_sink', 29.5, 4.5, 'Washbasin')
    hm.put('laundry_basket', 29.5, 8.5, 'Laundry basket')
    hm.put('kitchenette', 5, 14.5, 'Kitchenette', 'inspect'); hm.put('fridge', 8, 14.5, 'Fridge')
    hm.put('kitchenette', 12, 14.5, 'Stove'); hm.put('table', 11.5, 18.5, 'Dining table', 'seat')
    hm.put('fireplace', 22.5, 14.5, 'Electric hearth', 'inspect'); hm.put('sofa', 22.5, 17.5, 'Sofa', 'seat')
    hm.put('cafe_table', 22, 19.5, 'Coffee table'); hm.put('armchair', 26, 18.5, 'Armchair', 'seat')
    hm.put('books', 29, 13.5, 'Bookshelf'); hm.put('tree_tub', 29.5, 20.5, 'Potted tree')
    hm.put('tree_tub', 14.5, 29.5, 'Potted tree'); hm.put('tree_tub', 18.5, 29.5, 'Potted tree')
    hm.finish()

    # ============================================================ Residences A: Jasper, Evarra
    hm = Home(g, 'aptA', 'Residences A', 33, False, 16, {
        'h': (CARPET, None), 'j': (SLATE, ('5a8a4a', .35))})
    hm.room("Jasper's room", 3, 11, 'top', 'h', 9, 'Jasper')
    hm.room("Evarra's room", 13, 21, 'top', 'j', 19, 'Evarra')
    hm.room('Washroom', 23, 29, 'top', 't', 26, '', 'washroom')
    hm.open_plan(15, 17, (3, 18, 15, 23), (17, 12, 29, 23))
    hm.bed('bed', 4, 5.5, "Jasper's bed", ['Jasper'])
    hm.put('wardrobe', 7, 4.5, 'Wardrobe'); hm.put('paris_pictures', 10.5, 4.5, "Jasper's pictures of Paris", 'look')
    hm.put('books', 4, 8.5, "Jasper's cookbooks", 'look'); hm.put('armchair', 7, 8.5, 'Armchair', 'seat')
    hm.bed('bed', 14, 5.5, "Evarra's bed", ['Evarra'])
    hm.put('flowers', 18, 4.5, "Evarra's flower box", 'look'); hm.put('fern', 21.5, 3.5, 'Fern')
    hm.put('wardrobe', 14, 8.5, 'Wardrobe'); hm.put('plants', 17.5, 8.5, 'Drying herbs', 'look')
    hm.put('shower', 24, 5.5, 'Shower'); hm.put('toilet', 27.5, 4.5, 'Toilet'); hm.put('bath_sink', 29.5, 4.5, 'Washbasin')
    hm.put('kitchenette', 5, 14.5, "Jasper's range", 'look'); hm.put('fridge', 8, 14.5, 'Fridge')
    hm.put('kitchenette', 12, 14.5, 'Kitchenette', 'inspect'); hm.put('seed_rack', 15, 13.5, 'Spice rack', 'look')
    hm.put('table', 5.5, 17.5, 'Breakfast table', 'seat')
    hm.put('table', 11.5, 20.5, 'Dining table', 'seat')
    hm.put('wall_screen', 23, 13.5, 'Family screen', 'look'); hm.put('cafe_table', 23, 16.5, 'Coffee table')
    hm.put('sofa', 23.5, 19.5, 'Sofa', 'seat'); hm.put('armchair', 27.5, 17.5, 'Armchair', 'seat')
    hm.put('books', 29, 13.5, 'Bookshelf'); hm.put('planter_long', 28, 22.5, "Evarra's herb bed", 'look')
    hm.put('tree_tub', 20.5, 22.5, 'Potted tree')
    hm.finish()

    # ============================================================ Family residences: Maren and Owen, Pip
    hm = Home(g, 'aptDoc', 'Family residences', 35, True, 17, {
        'h': (CARPET, None), 'j': (NAVY, ('d0a040', .25)), 's': (SLATE, ('8a6a4a', .2)), 'f': (MINERAL, None)})
    hm.room("Maren and Owen's room", 3, 13, 'top', 'h', 11, 'Maren|Owen')
    hm.room("Pip's room", 15, 23, 'top', 'j', 21, 'Pip')
    hm.room('Washroom', 25, 31, 'top', 't', 28, '', 'washroom')
    hm.room("Owen's study", 3, 13, 'bottom', 's', 9, 'Owen', 'study')
    hm.room("Maren's home clinic", 21, 31, 'bottom', 'f', 25, '', 'clinic')
    hm.open_plan(10, 16, (3, 17, 12, 21), (14, 12, 31, 21))
    hm.bed('bed_double', 4.5, 5.5, "Maren and Owen's bed", ['Maren', 'Owen'])
    hm.put('wardrobe', 8, 4.5, 'Wardrobe'); hm.put('wardrobe', 10, 4.5, "Maren's wardrobe")
    hm.put('books', 13, 4.5, "Owen's bedside books", 'look'); hm.put('armchair', 4, 8.5, 'Armchair', 'seat')
    hm.put('plants', 8, 8.5, 'Plant')
    hm.bed('bed', 16, 5.5, "Pip's bed", ['Pip'])
    hm.put('star_chart', 19, 5.5, "Pip's map of the station", 'look'); hm.put('books', 23, 4.5, "Pip's schoolbooks", 'look')
    hm.put('footlocker', 16, 8.5, "Pip's toy chest", 'look'); hm.put('play_piece', 19.5, 8.5, "Pip's play set", 'look')
    hm.put('curator_desk', 5.5, 24.5, "Owen's desk", 'look'); hm.put('books', 13, 24.5, "Owen's codex collection", 'look')
    hm.put('case_relic', 13, 28.5, 'Codex under glass', 'look'); hm.put('armchair', 5, 28.5, 'Reading chair', 'seat')
    hm.put('books', 8, 29.5, 'Library overflow', 'look'); hm.put('tree_tub', 3.5, 29.5, 'Potted tree')
    hm.put('bed', 22, 25.5, 'Spare cot', 'look'); hm.put('terminal', 27.5, 24.5, "Maren's medical terminal", 'look')
    hm.put('medical', 31, 25.5, "Maren's medicine cabinet", 'look'); hm.put('armchair', 29, 29.5, 'Armchair', 'seat')
    hm.put('plants', 23, 29.5, 'Plant')
    hm.put('shower', 26, 5.5, 'Shower'); hm.put('toilet', 29.5, 4.5, 'Toilet'); hm.put('bath_sink', 31.5, 4.5, 'Washbasin')
    hm.put('laundry_basket', 31.5, 8.5, 'Laundry basket')
    hm.put('kitchenette', 5, 14.5, 'Kitchenette', 'inspect'); hm.put('fridge', 8, 14.5, 'Fridge')
    hm.put('table', 7.5, 18.5, 'Family table', 'seat')
    hm.put('hologame', 16, 13.5, "Pip's holo-game", 'look')
    hm.put('fireplace', 24.5, 14.5, 'Electric hearth', 'inspect'); hm.put('cafe_table', 24, 16.5, 'Coffee table')
    hm.put('sofa', 24.5, 18.5, 'Sofa', 'seat'); hm.put('armchair', 28.5, 17.5, 'Armchair', 'seat')
    hm.put('armchair', 20, 17.5, 'Armchair', 'seat'); hm.put('books', 31, 13.5, 'Family bookshelf', 'look')
    hm.put('tree_tub', 13.5, 20.5, 'Potted tree')
    hm.finish()

    # ============================================================ Security residences: Garrick and Saffi, Kit
    hm = Home(g, 'aptSec', 'Security residences', 35, False, 17, {
        'h': (CARPET, ('6a2a2a', .2)), 'j': (NAVY, ('c87a3a', .3))})
    hm.room("Garrick and Saffi's room", 3, 13, 'top', 'h', 11, 'Garrick|Saffi')
    hm.room("Kit's room", 15, 23, 'top', 'j', 21, 'Kit')
    hm.room('Washroom', 25, 31, 'top', 't', 28, '', 'washroom')
    hm.open_plan(10, 16, (3, 17, 14, 23), (16, 12, 31, 23))
    hm.bed('bed_double', 4.5, 5.5, "Garrick and Saffi's bed", ['Garrick', 'Saffi'])
    hm.put('locker', 8, 5.5, "Garrick's uniform locker", 'look'); hm.put('wardrobe', 10, 5.5, 'Wardrobe')
    hm.put('plants', 12.5, 4.5, "Saffi's plants", 'look'); hm.put('armchair', 4, 8.5, 'Armchair', 'seat')
    hm.bed('bed', 16, 5.5, "Kit's bed", ['Kit'])
    hm.put('telescope', 19, 5.5, "Kit's telescope", 'look'); hm.put('star_chart', 23, 5.5, "Kit's sky chart", 'look')
    hm.put('footlocker', 16, 8.5, "Kit's toy chest", 'look'); hm.put('play_piece', 19.5, 8.5, "Kit's toys", 'look')
    hm.put('shower', 26, 5.5, 'Shower'); hm.put('toilet', 29.5, 4.5, 'Toilet'); hm.put('bath_sink', 31.5, 4.5, 'Washbasin')
    hm.put('kitchenette', 5, 14.5, 'Kitchenette', 'inspect'); hm.put('fridge', 8, 14.5, 'Fridge')
    for fx in (7.5, 11.5):
        hm.put('table', fx, 19.5, "Saffi's potluck table", 'seat')
    hm.put('hologame', 15, 13.5, "Kit's holo-game", 'look')
    hm.put('wall_screen', 24, 13.5, 'Family screen', 'look'); hm.put('cafe_table', 24, 16.5, 'Coffee table')
    hm.put('sofa', 24.5, 19.5, 'Sofa', 'seat'); hm.put('armchair', 28.5, 17.5, 'Armchair', 'seat')
    hm.put('books', 31, 13.5, 'Bookshelf'); hm.put('punching_bag', 30.5, 22.5, "Garrick's training bag", 'look')
    hm.put('tree_tub', 20.5, 22.5, 'Potted tree')
    hm.spot('Saffi sweeping', 19.5, 17.5); hm.spot('Kit playing', 19.5, 6.5)
    hm.finish()

    # ============================================================ Moogli residences: Tobbin and Merrow, Nub
    hm = Home(g, 'aptMoog', 'Moogli residences', 35, False, 17, {
        'h': (CARPET, ('4a7a3a', .3)), 'j': (SLATE, ('d0b040', .25))})
    hm.room("Tobbin and Merrow's room", 3, 13, 'top', 'h', 11, 'Tobbin|Merrow')
    hm.room("Nub's room", 15, 23, 'top', 'j', 21, 'Nub')
    hm.room('Washroom', 25, 31, 'top', 't', 28, '', 'washroom')
    hm.open_plan(10, 16, (3, 17, 14, 23), (16, 12, 31, 23))
    hm.bed('bed_double', 4.5, 5.5, "Tobbin and Merrow's bed", ['Tobbin', 'Merrow'])
    hm.put('wardrobe', 8, 5.5, "Tobbin's wardrobe", 'look'); hm.put('star_chart', 10.5, 5.5, "Tobbin's furniture blueprints", 'look')
    hm.put('plants', 12.5, 4.5, "Merrow's seedlings", 'look'); hm.put('armchair', 4, 8.5, 'Armchair', 'seat')
    hm.bed('bed', 16, 5.5, "Nub's bed", ['Nub'])
    hm.put('curator_desk', 19.5, 4.5, "Nub's drawing desk", 'look'); hm.put('star_chart', 23, 5.5, "Nub's drawings", 'look')
    hm.put('footlocker', 16, 8.5, "Nub's toy chest", 'look'); hm.put('play_piece', 19.5, 8.5, "Nub's toys", 'look')
    hm.put('shower', 26, 5.5, 'Shower'); hm.put('toilet', 29.5, 4.5, 'Toilet'); hm.put('bath_sink', 31.5, 4.5, 'Washbasin')
    hm.put('kitchenette', 5, 14.5, 'Kitchenette', 'inspect'); hm.put('fridge', 8, 14.5, 'Fridge')
    hm.put('table', 9.5, 19.5, 'Handmade table', 'seat')
    hm.put('hydroponics', 23.5, 13.5, "Merrow's grow bed", 'look'); hm.put('water_tank', 26, 13.5, "Merrow's water filter", 'look')
    hm.put('cafe_table', 24, 16.5, 'Coffee table'); hm.put('sofa', 24.5, 19.5, 'Sofa', 'seat')
    hm.put('armchair', 28.5, 17.5, 'Armchair', 'seat'); hm.put('books', 31, 13.5, 'Bookshelf')
    hm.put('workbench', 30, 22.5, "Tobbin's home bench", 'look'); hm.put('tree_tub', 20.5, 22.5, 'Potted tree')
    hm.finish()

    # ============================================================ Residences C: Quill, Ix'ali, Tar'Besh
    hm = Home(g, 'aptEmpty', 'Residences C', 33, True, 16, {
        'j': (SLATE, ('3a8a8a', .3)), 'h': (CARPET, ('5a3a7a', .3)), 'a': (NAVY, ('6f5a9a', .3)), 's': (MINERAL, ('6f5a9a', .32))})
    hm.room("Quill's room", 3, 11, 'top', 'j', 9, 'Quill')
    hm.room("Ix'ali's room", 13, 21, 'top', 'h', 19, "Ix'ali")
    hm.room('Washroom', 23, 29, 'top', 't', 26, '', 'washroom')
    hm.room("Tar'Besh's room", 3, 12, 'bottom', 'a', 8, "Tar'Besh")
    hm.room('Shrine', 20, 29, 'bottom', 's', 24, '', 'shrine')
    hm.open_plan(12, 16, (3, 17, 14, 21), (16, 12, 29, 21))
    hm.bed('bed', 4, 5.5, "Quill's bed", ['Quill'])
    hm.put('wardrobe', 7, 4.5, 'Wardrobe'); hm.put('books', 10, 4.5, "Quill's medical journals", 'look')
    hm.put('curator_desk', 5, 8.5, "Quill's desk", 'look'); hm.put('fern', 8.5, 8.5, 'Pressed ferns', 'look')
    hm.bed('bed', 14, 5.5, "Ix'ali's bed", ["Ix'ali"])
    hm.put('case_wreck', 17, 4.5, "Ix'ali's human weapons", 'look'); hm.put('punching_bag', 21.5, 4.5, 'Practice dummy', 'look')
    hm.put('wardrobe', 14, 8.5, 'Wardrobe'); hm.put('gym_rack', 18, 8.5, 'Practice blades', 'look')
    hm.bed('bed', 4, 25.5, "Tar'Besh's bed", ["Tar'Besh"])
    hm.put('books', 6, 24.5, "Tar'Besh's books", 'look'); hm.put('wardrobe', 12, 25.5, 'Wardrobe')
    hm.put('plants', 5, 29.5, "Tar'Besh's prayer garden", 'look'); hm.put('curator_desk', 10.5, 29.5, "Tar'Besh's writing desk", 'look')
    for fx in (21.5, 28.5): hm.put('holy_banner', fx, 25.5, 'Sky-Weaver banner', 'look')
    for fx in (23, 26.5): hm.put('prayer_mat', fx, 27.5, 'Prayer mat', 'inspect')
    for fx in (22, 27.5): hm.put('brazier', fx, 29.5, 'Violet brazier', 'inspect')
    hm.put('shower', 24, 5.5, 'Shower'); hm.put('toilet', 27.5, 4.5, 'Toilet'); hm.put('bath_sink', 29.5, 4.5, 'Washbasin')
    hm.put('kitchenette', 5, 14.5, 'Kitchenette', 'inspect'); hm.put('fridge', 8, 14.5, 'Fridge')
    hm.put('table', 12.5, 18.5, 'Dining table', 'seat')
    hm.put('books', 22, 13.5, 'Shared bookshelf', 'look'); hm.put('cafe_table', 22, 15.5, 'Coffee table')
    hm.put('sofa', 22.5, 18.5, 'Sofa', 'seat'); hm.put('armchair', 26.5, 17.5, 'Armchair', 'seat')
    hm.put('chess', 28.5, 20.5, 'Chess set', 'look'); hm.put('tree_tub', 3.5, 20.5, 'Potted tree')
    hm.finish()

    survey.WALKABLE = saved
