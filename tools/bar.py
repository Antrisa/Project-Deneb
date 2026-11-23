"""Rusk's bar, rebuilt in the promenade style (Zachary, 21 Nov: layout option E of the mock-ups).

The door on the promenade is unchanged; inside it is bigger:
  - the bar along the north: the counter with stools in front, bottle shelves and taps behind it;
  - a hallway off the bar room at the east end of the counter, open to everyone. Off it: Rusk's room (locked until
    BEDROOM_HEARTS hearts with Rusk), the supply closet (open), and a staff door behind the counter;
  - the open-mic stage at the east end with seats facing it (Friday Open-Mic & Story Night, Rusk's 6-heart event);
  - the games corner and the drinks board in the north-west, pub tables through the room;
  - a washroom in the south-east corner, by the way in.
Rusk works behind the counter and sleeps in his room; Bram, Freya and Job drink at the stools in the evening and
Garrick at a table (BAR_SPOTS via HOME_SPOTS, used by SCHEDULES_RAW in tools/build.py).
The counter, stools and stage pieces are stand-ins until the hotel furniture finals (bar counter, bar stool, piano).
The run-down state the player restores is still to be designed."""
import survey
from survey import SIZES
from spaceport import fill
from residences import Home, free_spot, DECK, KITCHEN, BATH, CARPET, SLATE

SIZES.update({'front_bar_1': (3, 3, 1), 'front_bar_2': (3, 3, 1)})
STAGE = ('home/hearth', None)


class Bar(Home):
    """The bar's map, using the homes' helpers (tools/residences.py): rooms, props, spots, the promenade door."""
    def __init__(self, g):
        W, H, door_x = 41, 34, 20
        self.g, self.key, self.title, self.W, self.H, self.bottom = g, 'bar', "Rusk's bar", W, H, False
        self.r = survey.Room(g, 'bar', "Rusk's bar", W, H)
        self.F = self.r.F
        fill(self.F, 1, 1, W - 2, H - 2, '#')
        self.door = (door_x, H - 3)
        self.floors = {'o': DECK, 'k': KITCHEN, 't': BATH, 'h': STAGE, 'j': (CARPET, ('c8732a', .3)), 's': (SLATE, None)}
        self.zones, self.inner, self.spots, self.taken, self.doors, self.notes = [], [], {}, set(), set(), []
        self.F[H - 3][door_x] = 'o'

    def side_room(self, label, x0, y0, x1, y1, ch, door, owner='', what='room'):
        """A room with a sliding door two tiles tall in a wall running north-south, at door (x, y)."""
        self.carve(x0, y0, x1, y1, ch)
        dx, dy = door
        for yy in (dy, dy + 1):
            self.F[yy][dx] = 'o'
            self.doors.add((dx, yy))
        self.inner.append([self.key, dx, dy, 1, 2, 'E', owner, what])
        self.r.keep_clear(dx - 2, dy, dx + 2, dy + 1)
        if label:
            self.zones.append([label, x0, y0, x1, y1])

    def open_room(self, label, x0, y0, x1, y1, ch):
        self.carve(x0, y0, x1, y1, ch)
        if label:
            self.zones.append([label, x0, y0, x1, y1])


def build(g):
    saved = survey.WALKABLE
    survey.WALKABLE = '.shafkoteuj'
    b = Bar(g)
    b.open_room('Bar room', 3, 10, 37, 30, 'o')
    fill(b.F, 11, 9, 27, 15, '#')                                     # the block behind the counter
    b.side_room('Behind the bar', 12, 10, 26, 15, 'k', (27, 11), '', 'staff door')
    b.open_room('Hallway', 28, 3, 29, 9, 's')
    b.side_room("Rusk's room", 14, 3, 26, 8, 'j', (27, 5), 'Rusk', 'bedroom')
    b.side_room('Supply closet', 31, 3, 37, 8, 's', (30, 5), '', 'supply closet')
    b.open_room('Stage', 31, 11, 37, 20, 'h')
    fill(b.F, 30, 24, 37, 24, '#'); fill(b.F, 30, 25, 30, 30, '#')
    b.rect_room('Washroom', 31, 25, 37, 30, 't', (34, 24), '', 'washroom')
    b.r.keep_clear(28, 9, 29, 13)                                     # the hallway's mouth
    b.r.keep_clear(19, 27, 21, 31)                                    # the way in from the promenade
    b.r.keep_clear(19, 13, 21, 14)                                    # Rusk's place behind the counter
    stools = []
    for x in (13.5, 16.5, 19.5, 22.5, 25.5):
        b.put('market_counter', x, 15.5, 'Bar counter')
        stools.append(b.put('chair_n', x, 17.5, 'Bar stool [N]', 'seat'))
    for x in (13.5, 16.5):
        b.put('storage_shelf', x, 12.5, 'Bottle shelves', 'look')
    b.put('front_bar_1', 24, 12.5, "Rusk's taps", 'look')
    b.put('hologame', 5, 11.5, 'Holo-darts', 'look')
    b.put('chess', 9, 11.5, 'Card table', 'look')
    b.put('scoreboard', 4, 15.5, 'Drinks board', 'look')
    for x in (31.5, 37.5):
        b.put('work_light', x, 11.5, 'Stage light')
    b.put('wall_screen', 34.5, 12.5, 'Open-mic board', 'look')
    for y in (16.5, 19.5):
        b.put('chair_e', 29.5, y, 'Seat [E]', 'seat')
    tables = []
    for (x, y) in ((6.5, 20.5), (11.5, 20.5), (16.5, 21.5), (24.5, 21.5), (6.5, 25.5), (11.5, 25.5), (25.5, 26.5), (6.5, 29.5), (11.5, 29.5)):
        tables.append(b.put('bar_table', x, y, 'Pub table', 'seat'))
    b.put('front_bar_2', 15.5, 29.5, "Rusk's mug sign", 'look')
    b.put('tree_tub', 28.5, 29.5, 'Potted fern')
    b.bed('bed', 15, 5.5, "Rusk's bed", ['Rusk'])
    b.put('wardrobe', 18, 5.5, 'Wardrobe')
    b.put('books', 22, 4.5, "Rusk's tall-tale ledgers", 'look'); b.put('armchair', 22, 7.5, 'Armchair', 'seat')
    b.put('footlocker', 25, 8.5, "Rusk's sea chest", 'look')
    b.put('barrel_stack', 33, 4.5, 'Kegs', 'look'); b.put('barrel_stack', 36, 4.5, 'Kegs', 'look')
    b.put('storage_shelf', 33.5, 7.5, 'Supply shelves', 'look'); b.put('cargo', 36.5, 7.5, 'Crates of glasses', 'look')
    b.put('toilet', 32.5, 26.5, 'Toilet'); b.put('toilet', 36.5, 26.5, 'Toilet')
    b.put('bath_sink', 32.5, 29.5, 'Washbasin'); b.put('bath_sink', 36.5, 29.5, 'Washbasin')
    # Where people stand (HOME_SPOTS): Rusk behind the counter, regulars on the stools facing the bar, Garrick
    # beside the pub table nearest the counter's east end.
    b.spot('Rusk at work', 20.5, 14.5)                               # the tile just behind the middle counter
    for who, k in (('Bram at the bar', 1), ('Freya at the bar', 2), ('Job at the bar', 3)):
        x, y = stools[k]
        b.spot(who, x + 0.5, y + 1.5)                                # on the stool, facing the bar
    tx, ty = tables[3]
    b.spot('Garrick at the bar', tx + 3.5, ty + 1.5)
    b.finish()
    survey.WALKABLE = saved
