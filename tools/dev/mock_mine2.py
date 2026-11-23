"""Mine / North Cave / Caverns mock-ups, round 1 (17 Nov 2026). Zachary picked mine A (later shortened) and north cave A."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_mine_lib import *

MINE_LEG = [(HEAD, "Mine head: lockers, tool crib, Job's desk"), (LOAD, "Loading spot: ore bins + hopper"), (BELT, "Conveyor to Engineering ore processing"),
            (DIG, "Dig floor (rocks regrow overnight)"), (ROCK, "Plain rock (stone)"), (ORE_I, "Iron ore outcrop"), (ORE_C, "Copper ore outcrop"),
            (CRYST, "Crystal samples (Zaas's survey)"), (ANALY, "Ore analyzer"), (SURV, "Survey room (Zaas)"), (GATE, "Cavern gate / lift (Vzz'ket)"),
            (NCAVE, "Passage to the North Cave"), (DOOR, "Way through / warp"), ((250, 110, 150), "Resident's usual spot")]


def mine_frame(m):
    m.rect(0, 0, 86, 50, ROCKBG, None); m.grid(0, 0, 86, 50)


def mine_head(m, x0, y0, x1, y1):
    m.oct(x0, y0, x1, y1, HEAD, 3)
    m.box(x1 - 4, y0 + 3, 2, 6, (120, 130, 150)); m.box(x1 - 4, y1 - 9, 2, 6, (120, 130, 150))   # lockers
    m.box(x0 + 3, y0 + 3, 5, 2, (230, 220, 200))                                                   # Job's desk
    m.box(x0 + 3, y1 - 5, 4, 2, CRATE); m.dot(x0 + 9, y1 - 4, LAMP)
    for i in range(2): m.box(x0 + 9 + i * 3, y0 + 3, 2, 2, ANALY)
    m.label((x0 + x1) / 2, (y0 + y1) / 2, "Mine head", F); m.person(x0 + 5, y0 + 6.5, "Job")


# ============================================================ A: the long gallery
m = Mock(122, 50, "The Mine, option A: one long gallery, dig bays bulging off it",
         "Walk in from Engineering on the east and the gallery runs west to the cavern gate. Iron bay north, copper bay south, both on 45-degree walls. About 84 x 48 tiles.")
mine_frame(m)
m.poly([(28, 20), (28, 12), (34, 6), (48, 6), (54, 12), (54, 20)], DIG)                 # iron bay
m.poly([(36, 30), (36, 38), (42, 44), (58, 44), (62, 40), (62, 30)], DIG)               # copper bay
m.oct(6, 32, 24, 44, SURV, 3)                                                            # survey room
m.rect(13, 28, 17, 32, SURV)
m.rect(38, 1, 42, 6, NCAVE)                                                               # north cave passage
m.rect(8, 18, 66, 32, DIG)                                                                # gallery
m.poly([(8, 18), (8, 32), (4, 28), (4, 22)], DIG)
m.oct(1, 19, 9, 31, GATE, 2)
mine_head(m, 64, 14, 82, 36); m.rect(82, 22, 86, 28, HEAD)
m.poly([(60, 2), (76, 2), (80, 6), (80, 14), (60, 14), (56, 10), (56, 6)], LOAD)         # loading spot, north of the head
m.rect(64, 13, 70, 15, LOAD, None)
m.belt([(74, 7), (86, 7)]); m.box(70, 5, 4, 4, (120, 100, 70)); m.label(68, 11, "Loading\nspot", F)
for i in range(4): m.box(58 + i * 3, 3, 2, 2, CRATE)
m.box(57, 11, 2, 2, ANALY)
SHAPES[:] = [[(28, 20), (28, 12), (34, 6), (48, 6), (54, 12), (54, 20)]]; scatter(m, 29, 7, 53, 19, 30, [(ROCK, 5), (ORE_I, 3), (ORE_C, 1)], 3)
SHAPES[:] = [[(36, 30), (36, 38), (42, 44), (58, 44), (62, 40), (62, 30)]]; scatter(m, 37, 31, 61, 43, 30, [(ROCK, 5), (ORE_C, 3), (ORE_I, 1)], 5)
SHAPES[:] = [[(8, 18), (66, 18), (66, 32), (8, 32)]]; scatter(m, 10, 19, 62, 31, 16, [(ROCK, 6), (ORE_I, 1), (ORE_C, 1)], 7, avoid=[(8, 22.5, 66, 27.5)] + [(x - 1.5, y - 1.5, x + 1.5, y + 1.5) for x in (16, 30, 44, 58) for y in (18.6, 31.4)])
m.d.line([m.P(10, 25), m.P(64, 25)], fill=(216, 200, 170), width=int(2.6 * S)); m.label(36, 25, "Main gallery (kept clear)", F)
for x in (16, 30, 44, 58): m.dot(x, 18.6, LAMP); m.dot(x, 31.4, LAMP)
for x, y in ((9, 36), (20, 36)): m.ore(x, y, CRYST)
m.box(19, 40, 3, 2, ANALY); m.label(15, 38, "Survey\nroom", F); m.person(11, 41, "Zaas")
m.label(5, 25, "Gate", F); m.person(4, 21, "Vzz'ket"); m.person(10, 29, "Ix'ali")
m.label(41, 14, "Iron bay", F); m.label(49, 41, "Copper bay", F)
for x, y in ((40, 1.5), (1.5, 25), (85, 25)): m.door(x, y)
m.text(86.5 - 86 + 88, 2, ""); m.legend(88, 2, MINE_LEG)
m.text(88, 34, "+ Simplest to read: every spot is\n  one step off the gallery.\n+ Clear view from the mine head.\n- Long walk to the gate at the end.\n\nNorth Cave: passage off the iron bay.\nCaverns: through the west gate.")
m.text(0.5, 1, "^ North Cave", (230, 230, 236)); m.text(0.5, 47.5, "< Caverns", WHITE); m.text(76, 47.5, "Engineering >", WHITE)
m.save("mine_A_gallery")

# ============================================================ B: the octagon pit with the cavern lift
m = Mock(122, 50, "The Mine, option B: a big octagonal dig with the cavern lift in the middle",
         "One wide open dig floor. The caverns are reached by a cage lift in its centre (Stardew-style: it also stops every 5 floors once found). About 84 x 48 tiles.")
mine_frame(m)
m.oct(4, 4, 58, 46, DIG, 12)                                                               # the dig
m.rect(28, 0, 34, 4, NCAVE)
mine_head(m, 62, 15, 80, 35); m.rect(56, 22, 62, 28, HEAD); m.rect(80, 22, 86, 28, HEAD)
m.poly([(60, 2), (76, 2), (80, 6), (80, 13), (66, 13), (60, 8)], LOAD)                   # loading spot NE
m.rect(68, 13, 72, 15, LOAD)
m.belt([(76, 6), (86, 6)]); m.box(72, 4, 4, 4, (120, 100, 70)); m.label(68, 9, "Loading", F)
for i in range(3): m.box(61 + i * 3, 3, 2, 2, CRATE)
m.poly([(60, 37), (80, 37), (80, 44), (76, 48), (60, 48), (56, 44), (56, 40)], SURV)    # survey SE
m.rect(68, 35, 72, 37, SURV)
m.ore(60, 45, CRYST); m.ore(63, 46, CRYST); m.box(75, 44, 3, 2, ANALY); m.label(68, 42, "Survey room", F); m.person(64, 39.5, "Zaas")
# centre: lift with a railing ring and a clear cross of paths
m.d.line([m.P(10, 25), m.P(56, 25)], fill=(216, 200, 170), width=int(2.6 * S)); m.d.line([m.P(31, 6), m.P(31, 44)], fill=(216, 200, 170), width=int(2.6 * S))
m.oct(24, 18, 38, 32, (96, 90, 88), 4); m.oct(27, 21, 35, 29, GATE, 2); m.label(31, 25.3, "Cavern\nlift", F, plate=False)
m.person(40, 34, "Vzz'ket"); m.person(16, 33, "Ix'ali")
for x, y in ((24, 18), (38, 18), (24, 32), (38, 32)): m.dot(x, y, LAMP)
SHAPES[:] = [octp(4, 4, 58, 46, 12)]; av = [(4, 22.5, 58, 27.5), (28.5, 4, 33.5, 46), (22, 16, 40, 34)]
scatter(m, 7, 7, 30, 23, 22, [(ROCK, 5), (ORE_I, 3)], 11, av)
scatter(m, 32, 7, 56, 23, 22, [(ROCK, 5), (ORE_I, 2), (ORE_C, 1)], 12, av)
scatter(m, 7, 27, 30, 44, 22, [(ROCK, 5), (ORE_C, 3)], 13, av)
scatter(m, 32, 27, 56, 44, 22, [(ROCK, 5), (ORE_C, 2), (ORE_I, 1)], 14, av)
m.label(16, 9, "iron side", FS); m.label(16, 42, "copper side", FS)
for x, y in ((31, 1), (85, 25)): m.door(x, y)
m.legend(88, 2, MINE_LEG)
m.text(88, 34, "+ One big landmark; the lift is the\n  way down, so no separate gate map.\n+ Room for lots of regrowing rock.\n- Less 'flavour' room for Job's\n  station life; it is mostly dig.\n\nNorth Cave: passage from the top.")
m.text(0.5, 47.5, "", WHITE); m.text(76, 47.5, "Engineering >", WHITE); m.text(34.5, 0.2, "^ North Cave", WHITE)
m.save("mine_B_pit")

# ============================================================ C: a junction hub with four spokes
m = Mock(122, 50, "The Mine, option C: a crossroads junction with rooms on its spokes",
         "A lit octagonal junction (bench, board, water) in the middle; each way off it leads to one place. Smaller digs, more variety. About 84 x 48 tiles.")
mine_frame(m)
m.rect(39, 1, 43, 16, NCAVE)                                                               # N spoke
m.poly([(10, 4), (30, 4), (36, 10), (36, 18), (14, 18), (6, 10)], DIG)                    # NW iron face
m.poly([(8, 32), (36, 32), (36, 40), (30, 46), (10, 46), (6, 42), (6, 34)], DIG)        # SW copper face
m.rect(30, 16, 36, 20, DIG); m.rect(30, 30, 36, 34, DIG)
m.oct(2, 17, 16, 33, GATE, 3); m.rect(16, 23, 34, 27, DIG)                              # W spoke + gate
m.oct(50, 34, 68, 46, SURV, 3); m.poly([(48, 30), (52, 30), (56, 34), (52, 34)], SURV)  # SE survey
m.rect(48, 22, 64, 28, DIG)                                                                # E spoke
mine_head(m, 62, 14, 80, 36); m.rect(80, 22, 86, 28, HEAD)
m.poly([(46, 2), (62, 2), (66, 6), (66, 14), (46, 14)], LOAD); m.rect(62, 10, 66, 16, LOAD)
m.belt([(62, 5), (86, 5)]); m.box(58, 3.5, 3, 3, (120, 100, 70)); m.label(54, 9, "Loading spot", F)
for i in range(3): m.box(47 + i * 3, 3, 2, 2, CRATE)
m.oct(32, 16, 50, 34, JUNC, 5)
m.box(37, 19, 3, 1.5, (130, 110, 90)); m.box(43, 30.5, 4, 1.5, (130, 110, 90)); m.box(45, 18.6, 2, 2, (80, 140, 200))
m.label(41, 24, "Junction", F); m.label(41, 27, "bench, notice board,\nwater, lamps", FS)
for x, y in ((34, 18), (48, 18), (34, 32), (48, 32)): m.dot(x, y, LAMP)
SHAPES[:] = [[(10, 4), (30, 4), (36, 10), (36, 18), (14, 18), (6, 10)]]; scatter(m, 9, 6, 35, 17, 22, [(ROCK, 4), (ORE_I, 3)], 21)
SHAPES[:] = [[(8, 32), (36, 32), (36, 40), (30, 46), (10, 46), (6, 42), (6, 34)]]; scatter(m, 9, 33, 35, 45, 22, [(ROCK, 4), (ORE_C, 3)], 22)
m.label(20, 11, "Iron face", F); m.label(20, 40, "Copper face", F)
m.ore(53, 43, CRYST); m.ore(56, 44, CRYST); m.box(63, 37, 3, 2, ANALY); m.label(59, 40, "Survey room", F); m.person(52, 37, "Zaas")
m.label(9, 25, "Gate", F); m.person(5, 20, "Vzz'ket"); m.person(18, 28.5, "Ix'ali")
for x, y in ((41, 1), (2, 25), (85, 25)): m.door(x, y)
m.legend(88, 2, MINE_LEG)
m.text(88, 34, "+ Most 'place-like': a little rest\n  spot at the heart of the mine.\n+ Short walk to everything.\n- Two smaller digs instead of\n  one big one.\n\nNorth Cave: straight up the N spoke.")
m.text(43.5, 0.2, "^ North Cave", WHITE); m.text(0.5, 47.5, "< Caverns", WHITE); m.text(76, 47.5, "Engineering >", WHITE)
m.save("mine_C_junction")

# ============================================================ North Cave A and B
NC_LEG = [(NCAVE, "Cave floor"), (PILLAR, "Rock pillar (solid)"), (ROCK, "Plain rock (stone)"), (ORE_I, "Iron bed (regrows every 2 days)"),
          (ORE_C, "Copper bed (regrows every 2 days)"), (WATER, "Seep pool"), (FUNG, "Glowing fungus (light)"), (DOOR, "Back to the Mine")]


def bed(m, x, y, c, n=4, seed=1):
    r = random.Random(seed)
    m.oct(x - 2.6, y - 2.1, x + 2.6, y + 2.1, (130, 120, 112), 1.2, (90, 84, 84))
    for i in range(n): m.ore(x - 1.4 + (i % 2) * 2.8 + r.uniform(-.3, .3), y - .9 + (i // 2) * 1.9, c)


m = Mock(96, 40, "North Cave, option A: one big chamber round rock pillars",
         "A single cave, no creatures. Four fixed ore beds (two iron, two copper) that refill every two days, plus loose rock. About 60 x 38 tiles.")
m.rect(0, 0, 62, 40, ROCKBG, None)
m.oct(4, 3, 58, 34, NCAVE, 9); m.rect(28, 34, 34, 40, NCAVE)
m.oct(18, 12, 26, 20, PILLAR, 2); m.oct(36, 10, 44, 18, PILLAR, 2); m.oct(28, 21, 34, 27, PILLAR, 2)
m.oct(44, 6, 54, 14, WATER, 3); m.label(49, 10, "pool", FS)
bed(m, 12, 10, ORE_I, seed=1); bed(m, 50, 24, ORE_I, seed=2); bed(m, 12, 26, ORE_C, seed=3); bed(m, 30, 7, ORE_C, seed=4)
SHAPES[:] = [octp(4, 3, 58, 34, 9)]; scatter(m, 8, 6, 55, 31, 16, [(ROCK, 1)], 31, avoid=[(17, 11, 27, 21), (35, 9, 45, 19), (27, 20, 35, 28), (43, 5, 55, 15), (9, 7, 15, 13), (47, 21, 53, 27), (9, 23, 15, 29), (27, 4, 33, 10), (28, 28, 34, 34)])
for x, y in ((8, 18), (56, 18), (22, 30), (40, 30), (20, 5), (40, 4)): m.dot(x, y, FUNG, .7)
m.door(31, 39)
m.legend(64, 2, NC_LEG)
m.text(64, 21, "+ Quick to sweep: walk one loop,\n  pick up the ore, go home.\n+ Pillars break up the open floor.\n- Little to discover after the\n  first visit.")
m.text(35, 38, "v The Mine", WHITE)
m.save("northcave_A_chamber")

m = Mock(96, 40, "North Cave, option B: three small chambers in a loop",
         "Entry chamber, iron chamber west, copper chamber east, joined at the top by a fungus-lit passage, so you walk a ring and come back out. About 60 x 38 tiles.")
m.rect(0, 0, 62, 40, ROCKBG, None)
m.rect(14, 5, 48, 9, NCAVE)                                                                   # top passage
m.rect(14, 9, 18, 16, NCAVE); m.rect(44, 9, 48, 16, NCAVE)
m.poly([(22, 26), (22, 22), (26, 18), (36, 18), (40, 22), (40, 26)], NCAVE); m.oct(20, 24, 42, 34, NCAVE, 3); m.rect(28, 34, 34, 40, NCAVE)
m.rect(16, 26, 22, 30, NCAVE); m.rect(40, 26, 46, 30, NCAVE)
m.oct(3, 14, 21, 32, NCAVE, 5); m.oct(41, 14, 59, 32, NCAVE, 5)
bed(m, 9, 20, ORE_I, seed=5); bed(m, 13, 27, ORE_I, seed=6); bed(m, 50, 20, ORE_C, seed=7); bed(m, 53, 27, ORE_C, seed=8)
m.oct(27, 21, 35, 26, WATER, 2)
for x in (20, 26, 32, 38, 44): m.dot(x, 6, FUNG, .7)
for x, y in ((24, 31), (38, 31), (6, 30), (56, 16)): m.rock(x, y)
m.label(12, 16.5, "Iron chamber", FS); m.label(50, 16.5, "Copper chamber", FS); m.label(31, 3.4, "Fungus passage", FS, WHITE); m.label(31, 30, "Entry", F)
m.door(31, 39)
m.legend(64, 2, NC_LEG)
m.text(64, 21, "+ Feels like a small trip, not\n  just a room.\n+ Each ore has its own place.\n- A bit more walking for the\n  same four beds.")
m.text(35, 38, "v The Mine", WHITE)
m.save("northcave_B_loop")

# ============================================================ Caverns: how a floor works
LUSH, LUSHF, STEAM, STEAMF, DEEP = (96, 140, 92), (128, 172, 112), (90, 120, 140), (134, 160, 176), (40, 90, 150)


def floor(m, ox, oy, fill, title, rocks, seed, extra=None, water=None, keep=()):
    m.rect(ox, oy, ox + 34, oy + 24, ROCKBG, None)
    m.oct(ox + 2, oy + 3, ox + 32, oy + 22, fill, 5)
    if water: water(m, ox, oy)
    m.oct(ox + 3, oy + 4, ox + 8, oy + 8, (220, 210, 190), 1); m.label(ox + 5.5, oy + 6, "up", FS)
    SHAPES[:] = [octp(ox + 2, oy + 3, ox + 32, oy + 22, 5)]; scatter(m, ox + 4, oy + 5, ox + 31, oy + 21, 26, rocks, seed, avoid=[(ox + 2, oy + 3, ox + 9, oy + 9)] + [(ox + a, oy + b, ox + c, oy + d) for a, b, c, d in keep])
    if extra: extra(m, ox, oy)
    m.label(ox + 17, oy + 1.5, title, F, WHITE)


m = Mock(124, 64, "The Caverns: how a floor works (four sample floors)",
         "Each floor is a small map picked from a set of hand-made layouts, then filled with rock, ore and creatures for its depth. Faceted walls throughout.")
floor(m, 1, 2, (150, 136, 118), "Floors 1-15: rock", [(ROCK, 6), (ORE_I, 2), (ORE_C, 2)], 41, keep=[(13, 9, 21, 16)],
      extra=lambda m, ox, oy: (m.oct(ox + 14, oy + 10, ox + 20, oy + 15, PILLAR, 2), m.dot(ox + 26, oy + 16, (200, 90, 90), .9), m.dot(ox + 12, oy + 18, (200, 90, 90), .9)))
floor(m, 37, 2, LUSHF, "Floors 16-30: green and lush", [(ROCK, 5), (ORE_C, 2), ((210, 210, 220), 2), (CRYST, 1)], 42,
      extra=lambda m, ox, oy: ([m.dot(ox + x, oy + y, (70, 120, 70), 1.1) for x, y in ((14, 9), (22, 14), (10, 17), (27, 8))], m.dot(ox + 19, oy + 19, (200, 90, 90), 1.1)))
floor(m, 1, 30, STEAMF, "Floors 31-45: steamy and watery", [(ROCK, 5), (CRYST, 2), ((120, 220, 230), 2)], 43, keep=[(11, 8, 25, 18)],
      water=lambda m, ox, oy: (m.oct(ox + 12, oy + 9, ox + 24, oy + 17, WATER, 3), [m.dot(ox + x, oy + y, (230, 236, 240), .7, (200, 200, 210)) for x, y in ((14, 8), (22, 8), (26, 15))]),
      extra=lambda m, ox, oy: (m.dot(ox + 28, oy + 18, (200, 90, 90), 1.3),))
# floor 45: the shore of the underground ocean
ox, oy = 37, 30
m.rect(ox, oy, ox + 34, oy + 24, ROCKBG, None)
m.poly([(ox + 2, oy + 6), (ox + 8, oy + 3), (ox + 32, oy + 3), (ox + 32, oy + 22), (ox + 2, oy + 22)], DEEP)
m.poly([(ox + 2, oy + 6), (ox + 8, oy + 3), (ox + 14, oy + 3), (ox + 14, oy + 12), (ox + 20, oy + 18), (ox + 20, oy + 22), (ox + 2, oy + 22)], STEAMF)
m.oct(ox + 3, oy + 4, ox + 8, oy + 8, (220, 210, 190), 1); m.label(ox + 5.5, oy + 6, "up", FS)
m.dot(ox + 24, oy + 11, (150, 40, 60), 3); m.label(ox + 24, oy + 16.5, "the Leviathan", FS, WHITE)
m.label(ox + 26, oy + 6, "underground ocean", FS, WHITE)
m.label(ox + 17, oy + 1.5, "Floor 45: the Leviathan", F, WHITE)
# the way down: three choices
m.text(74, 2, "THE WAY DOWN: pick one", (255, 226, 150))
m.text(74, 4.5, "1. Hidden under a rock (like Stardew).\n   Breaking rock has a small chance to\n   show the shaft; more likely as you\n   clear the floor.\n\n2. A sealed shaft on every floor that\n   opens once you have broken N rocks\n   or killed the creatures.\n   Clear goal, less luck.\n\n3. Shaft always visible but behind\n   rock you have to dig through.\n   Floor is a small puzzle.")
m.text(74, 33, "ON EVERY FLOOR", (255, 226, 150))
m.text(74, 35.5, "- 'up' ladder where you arrive.\n- Lift stop every 5 floors: once\n  reached, the mine's lift goes there.\n- Rocks: plain rock gives stone.\n- Ore and rarer finds deeper down.\n- Creatures (red) bigger and stronger\n  every 15 floors.\n- Floor 45: the Leviathan, then the\n  underground ocean beyond.")
m.legend(104, 33, [(ORE_I, "Iron  "), (ORE_C, "Copper"), (CRYST, "Crystal"), ((120, 220, 230), "Thermal quartz (guess)"), ((200, 90, 90), "Creature"), ((70, 120, 70), "Giant fern / moss"), ((230, 236, 240), "Steam vent")])
m.save("caverns_floor_kit")
