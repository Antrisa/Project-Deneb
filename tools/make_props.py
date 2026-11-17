"""Placeholder pictures for promenade-style props that have no art yet (art/lunar/<name>.png).
A file that already exists is never touched, so painted art is safe. Sizes are at the double-detail
scale (32 pixels = one tile; the game draws them at half size), standing on their bottom edge.
    python3 tools/make_props.py ."""
import os, sys
from PIL import Image, ImageDraw

OUT = os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", "art", "lunar")
INK = (34, 36, 48, 255)
CREAM, CREAM_D = (226, 214, 190, 255), (184, 170, 146, 255)
STEEL, STEEL_D, STEEL_L = (96, 110, 134, 255), (64, 74, 96, 255), (142, 156, 178, 255)
DARK = (40, 48, 66, 255)
TEAL, TEAL_D = (92, 214, 222, 255), (40, 120, 140, 255)
AMBER, WOOD, WOOD_D = (240, 184, 84, 255), (150, 104, 66, 255), (108, 74, 48, 255)
VIOLET, VIOLET_L = (150, 100, 220, 255), (214, 186, 255, 255)
GLASS = (170, 220, 236, 150)
RED = (214, 82, 72, 255)


def box(d, x0, y0, x1, y1, fill, light=None, shade=None, r=4):
    d.rounded_rectangle((x0, y0, x1, y1), r, fill=fill, outline=INK, width=2)
    if light: d.line((x0 + 3, y0 + 3, x1 - 3, y0 + 3), fill=light, width=2)
    if shade: d.line((x0 + 3, y1 - 3, x1 - 3, y1 - 3), fill=shade, width=2)


def legs(d, xs, y0, y1):
    for x in xs: d.rectangle((x, y0, x + 3, y1), fill=STEEL_D, outline=INK)


def holo_dais(d, w, h):
    d.ellipse((4, h - 44, w - 4, h - 4), fill=STEEL_D, outline=INK, width=2)
    d.ellipse((12, h - 40, w - 12, h - 14), fill=STEEL, outline=INK, width=2)
    d.ellipse((24, h - 35, w - 24, h - 19), fill=TEAL_D, outline=TEAL, width=2)
    d.ellipse((38, h - 30, w - 38, h - 24), fill=TEAL)
    for i, a in enumerate((60, 110)):
        d.polygon([(w // 2 - 3, h - 27), (w // 2 + 3, h - 27), (w // 2 + 10 + i * 4, h - a), (w // 2 - 10 - i * 4, h - a)], fill=(120, 230, 236, 70))


def memory_core(d, w, h):
    box(d, 6, 4, w - 6, h - 2, STEEL, STEEL_L, STEEL_D)
    for y in range(14, h - 14, 10):
        d.rectangle((14, y, w - 14, y + 5), fill=DARK)
        for x in range(18, w - 16, 7): d.rectangle((x, y + 1, x + 2, y + 3), fill=TEAL if (x + y) % 3 else AMBER)
    d.rectangle((w // 2 - 6, h - 12, w // 2 + 6, h - 8), fill=TEAL)


def wall_screen(d, w, h):
    legs(d, (20, w - 24), h - 20, h - 2)
    box(d, 4, 4, w - 4, h - 18, DARK, STEEL_L)
    d.rectangle((12, 12, w - 12, h - 26), fill=(20, 52, 72, 255))
    d.ellipse((w // 2 - 22, 16, w // 2 + 22, h - 30), outline=TEAL, width=2)
    for i in range(8): d.line((w // 2, (h - 14) // 2, w // 2 + (i - 4) * 9, 14 if i % 2 else h - 28), fill=TEAL_D, width=1)
    d.ellipse((w // 2 - 4, (h - 18) // 2 - 4, w // 2 + 4, (h - 18) // 2 + 4), fill=AMBER)


def console(d, w, h):
    box(d, 4, h - 34, w - 4, h - 2, STEEL, STEEL_L, STEEL_D)
    d.polygon([(8, h - 34), (w - 8, h - 34), (w - 14, h - 58), (14, h - 58)], fill=DARK, outline=INK)
    d.polygon([(14, h - 37), (w - 14, h - 37), (w - 18, h - 54), (18, h - 54)], fill=TEAL_D)
    for x in range(12, w - 12, 8): d.rectangle((x, h - 26, x + 4, h - 23), fill=AMBER if x % 16 else TEAL)


def tape_archive(d, w, h):
    box(d, 4, 4, w - 4, h - 2, WOOD, (180, 136, 94, 255), WOOD_D)
    for y in range(12, h - 12, 22):
        d.rectangle((10, y, w - 10, y + 16), fill=WOOD_D)
        for x in (14, 34):
            d.ellipse((x, y + 1, x + 14, y + 15), fill=(60, 60, 70, 255), outline=INK)
            d.ellipse((x + 5, y + 6, x + 9, y + 10), fill=CREAM)


def sensor_panel(d, w, h):
    box(d, 4, 4, w - 4, h - 2, STEEL, STEEL_L, STEEL_D)
    for i, y in enumerate((14, 44)):
        d.ellipse((12, y, w - 12, y + 24), fill=CREAM, outline=INK, width=2)
        d.line((w // 2, y + 12, w // 2 + (10 if i else -8), y + 4), fill=RED, width=2)
    for x in range(12, w - 12, 8): d.rectangle((x, h - 22, x + 4, h - 12), fill=TEAL if x % 16 else AMBER)


def concierge_desk(d, w, h):
    box(d, 4, h - 40, w - 4, h - 2, WOOD, (186, 140, 96, 255), WOOD_D)
    d.rectangle((10, h - 32, w - 10, h - 28), fill=AMBER)
    d.ellipse((w - 34, h - 52, w - 18, h - 40), fill=AMBER, outline=INK)               # bell
    d.rectangle((w - 27, h - 56, w - 25, h - 52), fill=AMBER)
    d.rectangle((14, h - 58, 24, h - 40), fill=(200, 220, 236, 255), outline=INK)       # vase
    for i, c in enumerate(((236, 120, 160, 255), (250, 210, 90, 255), (236, 120, 160, 255))):
        d.ellipse((8 + i * 8, h - 70 + (i % 2) * 4, 18 + i * 8, h - 60 + (i % 2) * 4), fill=c, outline=INK)


def paris_pictures(d, w, h):
    legs(d, (14, w - 18), h - 24, h - 2)
    box(d, 4, 4, w - 4, h - 22, WOOD_D)
    for i, x in enumerate((10, 50)):
        d.rectangle((x, 12, x + 34, h - 30), fill=(250, 232, 200, 255), outline=AMBER, width=2)
        cx = x + 17
        if i == 0:   # a lattice tower at sunset
            d.polygon([(cx, 16), (cx - 10, h - 34), (cx + 10, h - 34)], outline=(80, 70, 90, 255), fill=(244, 170, 120, 255))
            d.line((cx - 6, h - 46, cx + 6, h - 46), fill=(80, 70, 90, 255))
        else:        # a cafe awning
            for k in range(4): d.rectangle((x + 4 + k * 7, 20, x + 9 + k * 7, 30), fill=RED if k % 2 else CREAM)
            d.rectangle((x + 4, 30, x + 30, h - 34), fill=(190, 160, 120, 255))


def case(content):
    def draw(d, w, h):
        box(d, 4, h - 26, w - 4, h - 2, CREAM, (246, 238, 220, 255), CREAM_D)
        d.rectangle((8, 10, w - 8, h - 26), fill=(200, 230, 240, 110), outline=INK, width=2)
        d.line((12, 14, 20, 14), fill=(255, 255, 255, 200), width=2)
        content(d, w, h)
        d.rectangle((w // 2 - 10, h - 18, w // 2 + 10, h - 12), fill=AMBER)
    return draw


def fossil(d, w, h):
    for i in range(5): d.ellipse((14 + i * 7, 30 + (i % 2) * 3, 22 + i * 7, 38 + (i % 2) * 3), fill=(210, 196, 166, 255), outline=INK)
    for i in range(4): d.line((18 + i * 8, 38, 14 + i * 9, 46), fill=INK, width=2)


def relic(d, w, h):
    d.polygon([(w // 2, 20), (w // 2 + 12, 44), (w // 2 - 12, 44)], fill=AMBER, outline=INK)
    d.ellipse((w // 2 - 3, 42, w // 2 + 3, 48), fill=AMBER, outline=INK)


def shard(d, w, h):
    d.polygon([(w // 2 - 4, 18), (w // 2 + 8, 30), (w // 2 + 2, 46), (w // 2 - 10, 36)], fill=VIOLET, outline=INK)
    d.line((w // 2 - 4, 22, w // 2, 40), fill=VIOLET_L, width=2)


def wreck(d, w, h):
    d.polygon([(14, 26), (w - 16, 20), (w - 12, 44), (18, 46)], fill=STEEL, outline=INK)
    for x in (22, 34, 44): d.ellipse((x, 30, x + 4, 34), fill=STEEL_D)
    d.line((18, 40, w - 18, 26), fill=(60, 40, 40, 255), width=3)


def centerpiece(d, w, h):
    box(d, 8, h - 36, w - 8, h - 2, CREAM, (246, 238, 220, 255), CREAM_D)                # plinth
    box(d, 20, 8, w - 20, h - 34, (170, 150, 120, 255), (200, 180, 150, 255), r=10)        # stone mural
    d.polygon([(w // 2, 20), (w // 2 + 30, 50), (w // 2, 70), (w // 2 - 30, 50)], outline=VIOLET, width=3)   # a Sky-Weaver's wing
    for k in range(4): d.arc((w // 2 - 40 + k * 4, 26 + k * 4, w // 2 + 40 - k * 4, 86 - k * 4), 200, 340, fill=(110, 90, 70, 255), width=2)
    d.ellipse((w // 2 - 6, 44, w // 2 + 6, 56), fill=TEAL, outline=INK)


def curator_desk(d, w, h):
    box(d, 4, h - 38, w - 4, h - 2, WOOD, (186, 140, 96, 255), WOOD_D)
    for i in range(3): d.rectangle((12 + i * 10, h - 50, 20 + i * 10, h - 38), fill=((170, 80, 70, 255), (80, 110, 160, 255), (210, 180, 90, 255))[i], outline=INK)
    d.ellipse((w - 34, h - 48, w - 16, h - 40), fill=CREAM, outline=INK)                   # magnifier
    d.line((w - 20, h - 42, w - 12, h - 52), fill=AMBER, width=3)


def crystal_pedestal(d, w, h):
    box(d, 10, h - 40, w - 10, h - 2, STEEL, STEEL_L, STEEL_D)
    d.rectangle((6, h - 44, w - 6, h - 36), fill=STEEL_L, outline=INK)
    d.polygon([(w // 2, 8), (w // 2 + 14, 34), (w // 2 + 8, h - 48), (w // 2 - 8, h - 48), (w // 2 - 14, 34)], fill=VIOLET, outline=INK)
    d.polygon([(w // 2, 14), (w // 2 + 6, 34), (w // 2, h - 54)], fill=VIOLET_L)


def sealed_door(d, w, h):
    box(d, 2, 2, w - 2, h - 2, STEEL_D, STEEL, DARK, r=6)
    d.rectangle((14, 14, w - 14, h - 8), fill=STEEL, outline=INK, width=2)
    for k in range(5): d.polygon([(14 + k * 16, h - 22), (22 + k * 16, h - 22), (14 + k * 16 + 12, h - 14), (6 + k * 16 + 12, h - 14)], fill=AMBER)
    d.line((w // 2, 14, w // 2, h - 24), fill=INK, width=2)
    d.ellipse((w // 2 - 6, 4, w // 2 + 6, 12), fill=RED, outline=INK)


def sanctum_door(d, w, h):
    box(d, 2, 2, w - 2, h - 2, (80, 60, 120, 255), VIOLET, (50, 36, 80, 255), r=6)
    for y in range(16, h - 12, 18): d.polygon([(w // 2, y), (w // 2 + 7, y + 8), (w // 2, y + 16), (w // 2 - 7, y + 8)], outline=VIOLET_L, width=2)
    d.ellipse((w // 2 - 4, 4, w // 2 + 4, 12), fill=RED, outline=INK)


def lab_door(d, w, h):
    box(d, 2, 2, w - 2, h - 2, STEEL_D, STEEL, DARK, r=6)
    for k in range(5): d.polygon([(4, 20 + k * 16), (w - 4, 12 + k * 16), (w - 4, 18 + k * 16), (4, 26 + k * 16)], fill=AMBER)
    d.ellipse((w // 2 - 4, 4, w // 2 + 4, 12), fill=RED, outline=INK)


def case_empty(d, w, h):
    box(d, 4, h - 26, w - 4, h - 2, CREAM, (246, 238, 220, 255), CREAM_D)
    d.rectangle((8, 10, w - 8, h - 26), fill=(200, 230, 240, 110), outline=INK, width=2)
    d.line((12, 14, 20, 14), fill=(255, 255, 255, 200), width=2)
    d.rectangle((w // 2 - 8, h - 34, w // 2 + 8, h - 28), fill=STEEL_L, outline=INK)     # an empty stand
    d.rectangle((w // 2 - 10, h - 18, w // 2 + 10, h - 12), fill=CREAM_D)                # blank label


def crystal_pedestal_empty(d, w, h):
    box(d, 10, h - 40, w - 10, h - 2, STEEL, STEEL_L, STEEL_D)
    d.rectangle((6, h - 44, w - 6, h - 36), fill=STEEL_L, outline=INK)
    d.polygon([(w // 2 - 12, h - 44), (w // 2 - 6, h - 58), (w // 2 + 6, h - 58), (w // 2 + 12, h - 44)], outline=VIOLET, fill=(60, 44, 90, 255))
    d.ellipse((w // 2 - 4, h - 54, w // 2 + 4, h - 48), fill=(120, 90, 180, 255))


def precursor_mural(d, w, h):
    box(d, 4, 4, w - 4, h - 2, (150, 136, 160, 255), (184, 170, 196, 255), (110, 96, 124, 255), r=8)
    d.ellipse((w // 2 - 22, 16, w // 2 + 22, 60), outline=VIOLET, width=3)                # a world
    for k in range(3): d.arc((w // 2 - 40 + k * 6, 8 + k * 4, w // 2 + 40 - k * 6, 72 - k * 4), 200, 340, fill=VIOLET_L, width=2)
    for i in range(5): d.polygon([(14 + i * 16, h - 26), (20 + i * 16, h - 34), (26 + i * 16, h - 26), (20 + i * 16, h - 18)], outline=(80, 64, 100, 255), width=2)


def test_rig(d, w, h):
    box(d, 6, h - 30, w - 6, h - 2, STEEL, STEEL_L, STEEL_D)
    d.rectangle((w // 2 - 3, 20, w // 2 + 3, h - 30), fill=STEEL_D, outline=INK)
    d.line((w // 2, 22, w - 12, 12), fill=STEEL_D, width=5)
    d.ellipse((w - 18, 6, w - 6, 18), fill=TEAL, outline=INK)
    d.ellipse((12, h - 46, 28, h - 30), fill=(60, 44, 90, 255), outline=VIOLET, width=2)  # sample cradle
    for x in range(12, w - 12, 8): d.rectangle((x, h - 20, x + 4, h - 16), fill=AMBER if x % 16 else TEAL)


def spectrometer(d, w, h):
    box(d, 4, h - 40, w - 4, h - 2, STEEL, STEEL_L, STEEL_D)
    d.rectangle((10, h - 34, w - 10, h - 18), fill=DARK)
    for i, x in enumerate(range(12, w - 12, 4)): d.line((x, h - 20, x, h - 22 - (i * 7) % 11), fill=VIOLET_L)
    d.ellipse((w - 18, h - 52, w - 6, h - 40), fill=VIOLET, outline=INK)


def brazier(d, w, h):
    d.polygon([(6, h - 30), (w - 6, h - 30), (w - 10, h - 20), (10, h - 20)], fill=(150, 120, 80, 255), outline=INK)
    d.rectangle((w // 2 - 3, h - 20, w // 2 + 3, h - 6), fill=WOOD_D, outline=INK)
    d.rectangle((8, h - 6, w - 8, h - 2), fill=WOOD_D, outline=INK)
    d.polygon([(8, h - 30), (w // 2, 4), (w - 8, h - 30)], fill=VIOLET)
    d.polygon([(12, h - 30), (w // 2, 18), (w - 12, h - 30)], fill=VIOLET_L)


def holy_banner(d, w, h):
    d.rectangle((w // 2 - 2, 4, w // 2 + 2, h - 2), fill=WOOD_D, outline=INK)
    d.rectangle((4, 4, w - 4, 8), fill=AMBER, outline=INK)
    d.polygon([(4, 8), (w - 4, 8), (w - 4, h - 40), (w // 2, h - 30), (4, h - 40)], fill=(90, 56, 140, 255), outline=INK)
    d.polygon([(w // 2, 24), (w // 2 + 7, 36), (w // 2, 48), (w // 2 - 7, 36)], outline=AMBER, width=2)


def prayer_mat(d, w, h):
    d.rounded_rectangle((2, 4, w - 2, h - 4), 4, fill=(110, 70, 150, 255), outline=INK, width=2)
    d.rectangle((8, 10, w - 8, h - 10), outline=AMBER, width=2)


ORANGE_T, ORANGE_TD = (232, 120, 40, 255), (184, 82, 30, 255)
WHITE_T = (238, 236, 228, 255)


def geo_core(d, w, h):
    d.ellipse((6, h - 70, w - 6, h - 4), fill=STEEL_D, outline=INK, width=2)
    box(d, 30, 24, w - 30, h - 34, STEEL, STEEL_L, STEEL_D, r=12)
    d.ellipse((44, 6, w - 44, 46), fill=STEEL_L, outline=INK, width=2)
    d.ellipse((58, 14, w - 58, 38), fill=(250, 140, 50, 255), outline=INK, width=2)
    d.ellipse((68, 20, w - 68, 32), fill=(255, 214, 120, 255))
    for k in range(5): d.rectangle((40, 54 + k * 12, w - 40, 58 + k * 12), fill=ORANGE_T if k % 2 else STEEL_D)
    for x in (16, w - 30): d.rectangle((x, h - 52, x + 14, h - 20), fill=STEEL_D, outline=INK)


def furnace(d, w, h):
    box(d, 4, 14, w - 4, h - 2, (110, 96, 92, 255), (150, 130, 120, 255), (80, 70, 68, 255))
    d.rectangle((w // 2 - 6, 2, w // 2 + 6, 16), fill=STEEL_D, outline=INK)
    d.rounded_rectangle((14, h - 50, w - 14, h - 18), 6, fill=(60, 30, 20, 255), outline=INK, width=2)
    d.rounded_rectangle((20, h - 44, w - 20, h - 24), 4, fill=(250, 130, 40, 255))
    d.rectangle((24, h - 38, w - 24, h - 30), fill=(255, 214, 120, 255))


def ore_crusher(d, w, h):
    box(d, 6, 34, w - 6, h - 2, STEEL, STEEL_L, STEEL_D)
    d.polygon([(10, 34), (w - 10, 34), (w - 24, 6), (24, 6)], fill=STEEL_D, outline=INK)
    d.rectangle((30, 10, w - 30, 30), fill=(70, 60, 56, 255))
    for k in range(4): d.polygon([(14 + k * 18, h - 30), (22 + k * 18, h - 30), (30 + k * 18, h - 18), (22 + k * 18, h - 18)], fill=AMBER)


def ore_cart(d, w, h):
    d.polygon([(4, 14), (w - 4, 14), (w - 10, h - 14), (10, h - 14)], fill=STEEL, outline=INK)
    for x, y in ((14, 8), (26, 6), (38, 9), (22, 12)): d.ellipse((x, y, x + 12, y + 10), fill=(120, 100, 90, 255), outline=INK)
    for x in (10, w - 22): d.ellipse((x, h - 16, x + 12, h - 4), fill=DARK, outline=INK)


def pump(d, w, h):
    box(d, 8, h - 46, w - 8, h - 2, STEEL, STEEL_L, STEEL_D)
    d.rectangle((w // 2 - 8, 6, w // 2 + 8, h - 44), fill=(190, 130, 70, 255), outline=INK)
    d.ellipse((w // 2 - 14, h - 40, w // 2 + 14, h - 14), fill=STEEL_L, outline=INK, width=2)
    d.line((w // 2, h - 27, w // 2 + 9, h - 33), fill=RED, width=2)


def pipe_rack(d, w, h):
    legs(d, (8, w - 12), 20, h - 2)
    for k, c in enumerate(((190, 130, 70, 255), STEEL_L, (120, 160, 120, 255))):
        d.rectangle((2, 10 + k * 12, w - 2, 18 + k * 12), fill=c, outline=INK)


def locker(d, w, h):
    box(d, 4, 4, w - 4, h - 2, (80, 110, 140, 255), (120, 150, 180, 255), (60, 84, 110, 255))
    d.line((w // 2, 8, w // 2, h - 6), fill=INK, width=2)
    for x in (w // 4, 3 * w // 4):
        for y in range(16, 40, 6): d.line((x - 8, y, x + 8, y), fill=(50, 70, 92, 255))
        d.rectangle((x - 2, h // 2, x + 2, h // 2 + 6), fill=AMBER)


def tool_cart(d, w, h):
    box(d, 6, 14, w - 6, h - 12, (200, 70, 60, 255), (236, 110, 96, 255), (150, 50, 44, 255))
    for y in (24, 34): d.line((10, y, w - 10, y), fill=INK)
    for x in (12, 26, 40): d.rectangle((x, 6, x + 4, 14), fill=STEEL_L, outline=INK)
    for x in (10, w - 18): d.ellipse((x, h - 12, x + 8, h - 4), fill=DARK)


def welding_rig(d, w, h):
    box(d, 6, h - 40, w - 6, h - 6, STEEL, STEEL_L, STEEL_D)
    for x, c in ((12, (90, 140, 200, 255)), (34, (200, 80, 70, 255))): d.rounded_rectangle((x, 10, x + 16, h - 40), 6, fill=c, outline=INK)
    for k in range(4): d.polygon([(8 + k * 12, h - 20), (14 + k * 12, h - 20), (20 + k * 12, h - 12), (14 + k * 12, h - 12)], fill=AMBER)
    d.ellipse((10, h - 8, 20, h - 2), fill=DARK); d.ellipse((w - 20, h - 8, w - 10, h - 2), fill=DARK)


def fuel_tank(d, w, h):
    d.rounded_rectangle((8, 8, w - 8, h - 8), 14, fill=WHITE_T, outline=INK, width=2)
    d.rectangle((8, h // 2 - 6, w - 8, h // 2 + 6), fill=ORANGE_T)
    d.line((16, 14, 16, h - 16), fill=(255, 255, 255, 255), width=2)
    d.rectangle((14, h - 10, w - 14, h - 2), fill=STEEL_D, outline=INK)


def parts_rack(d, w, h):
    box(d, 4, 4, w - 4, h - 2, STEEL_D, STEEL, DARK)
    for y in (16, 46, 76):
        d.rectangle((8, y, w - 8, y + 24), fill=(60, 66, 80, 255))
        for x in range(12, w - 16, 14):
            c = (WHITE_T, ORANGE_T, STEEL_L, AMBER)[(x + y) % 4]
            d.rectangle((x, y + 8, x + 10, y + 22), fill=c, outline=INK)


def launch_console(d, w, h):
    box(d, 4, h - 34, w - 4, h - 2, WHITE_T, (255, 255, 255, 255), (190, 190, 186, 255))
    d.polygon([(8, h - 34), (w - 8, h - 34), (w - 16, h - 64), (16, h - 64)], fill=DARK, outline=INK)
    d.polygon([(18, h - 38), (w - 18, h - 38), (w - 22, h - 58), (22, h - 58)], fill=TEAL_D)
    d.rectangle((w // 2 - 10, h - 28, w // 2 + 10, h - 18), fill=RED, outline=INK)
    d.rectangle((10, h - 12, w - 10, h - 8), fill=ORANGE_T)


def air_scrubber(d, w, h):
    box(d, 4, 4, w - 4, h - 2, STEEL, STEEL_L, STEEL_D)
    d.ellipse((12, 14, w - 12, 50), fill=DARK, outline=INK, width=2)
    d.line((w // 2, 18, w // 2, 46), fill=STEEL_L, width=3); d.line((16, 32, w - 16, 32), fill=STEEL_L, width=3)
    for y in range(58, h - 12, 8): d.line((12, y, w - 12, y), fill=STEEL_D)


def mag_clamp(d, w, h):
    d.rectangle((4, 4, w - 4, h - 4), fill=STEEL_D, outline=INK, width=2)
    d.rectangle((10, 10, w - 10, h - 10), fill=ORANGE_T)


def launch_door(d, w, h):
    d.rectangle((0, 0, w - 1, h - 1), fill=STEEL_D, outline=INK, width=3)
    d.rectangle((8, 12, w - 9, h - 10), fill=STEEL, outline=INK, width=2)
    d.line((w // 2, 12, w // 2, h - 10), fill=INK, width=3)
    for k in range(0, w, 24):
        d.polygon([(k, h - 10), (k + 12, h - 10), (k + 24, h), (k + 12, h)], fill=AMBER)
    for x in range(20, w - 20, 40): d.rectangle((x, 24, x + 20, 30), fill=STEEL_L)
    for x in (16, w - 24): d.ellipse((x, 2, x + 8, 10), fill=RED, outline=INK)


def coolant_tank(d, w, h):
    d.ellipse((6, h - 24, w - 6, h - 4), fill=STEEL_D, outline=INK, width=2)
    d.rounded_rectangle((12, 10, w - 12, h - 14), 18, fill=(110, 170, 220, 255), outline=INK, width=2)
    d.rectangle((12, 40, w - 12, 48), fill=STEEL_D); d.rectangle((12, 80, w - 12, 88), fill=STEEL_D)
    d.line((22, 18, 22, h - 22), fill=(200, 230, 250, 255), width=3)
    d.ellipse((w // 2 - 8, 56, w // 2 + 8, 72), fill=STEEL_L, outline=INK); d.line((w // 2, 64, w // 2 + 5, 60), fill=RED, width=2)
    d.rectangle((w // 2 - 6, 0, w // 2 + 6, 12), fill=STEEL, outline=INK)


def kitchenette(d, w, h):
    box(d, 2, 30, w - 2, h - 2, (236, 232, 222, 255), (255, 255, 255, 255), (196, 190, 180, 255))
    d.rectangle((2, 30, w - 2, 38), fill=(150, 120, 90, 255), outline=INK)
    d.rectangle((14, 6, 50, 28), fill=(200, 210, 220, 255), outline=INK)
    d.rectangle((66, 32, 92, 37), fill=STEEL_L, outline=INK)
    d.ellipse((96, 18, 112, 34), fill=RED, outline=INK)
    for x in (20, 60, 100): d.rectangle((x, 48, x + 2, 56), fill=INK)
    d.line((32, 38, 32, h - 4), fill=INK)


ROCK, ROCK_D, ROCK_L = (124, 108, 96, 255), (88, 76, 70, 255), (160, 146, 130, 255)
HAZ = (226, 180, 48, 255)


def ore_pile(d, w, h):
    d.polygon([(4, h - 4), (20, h - 30), (44, h - 44), (70, h - 36), (w - 4, h - 4)], fill=ROCK, outline=INK)
    for x, y in ((18, h - 14), (34, h - 26), (50, h - 18), (66, h - 12), (42, h - 36), (28, h - 8)):
        d.ellipse((x, y, x + 12, y + 9), fill=ROCK_L if (x + y) % 3 else ROCK_D, outline=INK)
    d.ellipse((56, h - 26, 62, h - 21), fill=(200, 150, 90, 255))


def hopper(d, w, h):
    legs(d, (10, w - 14), h - 40, h - 2)
    d.polygon([(4, 6), (w - 4, 6), (w - 26, h - 44), (26, h - 44)], fill=STEEL, outline=INK)
    d.rectangle((30, h - 44, w - 30, h - 30), fill=STEEL_D, outline=INK)
    d.rectangle((4, 2, w - 4, 10), fill=STEEL_L, outline=INK)
    for k in range(5): d.polygon([(10 + k * 16, 14), (18 + k * 16, 14), (12 + k * 16, 22), (4 + k * 16, 22)], fill=HAZ)
    for x, y in ((24, 0), (40, -2), (56, 0)): d.ellipse((x, y, x + 12, y + 8), fill=ROCK, outline=INK)


def ingot_stack(d, w, h):
    d.rectangle((2, h - 8, w - 2, h - 2), fill=WOOD_D, outline=INK)
    for row in range(4):
        for k in range(3 - row % 2):
            x = 6 + k * 18 + (row % 2) * 9; y = h - 18 - row * 9
            d.polygon([(x, y + 8), (x + 16, y + 8), (x + 13, y), (x + 3, y)], fill=(196, 170, 120, 255) if row % 2 else (170, 176, 186, 255), outline=INK)


def slag_bin(d, w, h):
    d.polygon([(4, 14), (w - 4, 14), (w - 10, h - 4), (10, h - 4)], fill=(70, 66, 64, 255), outline=INK)
    d.rectangle((4, 10, w - 4, 16), fill=STEEL_D, outline=INK)
    for x, y in ((12, 4), (26, 2), (40, 5)): d.ellipse((x, y, x + 12, y + 10), fill=(60, 40, 36, 255), outline=INK)
    d.ellipse((24, 6, 32, 11), fill=(250, 130, 40, 255))
    d.rectangle((14, 28, w - 14, 36), fill=HAZ)


def sorting_machine(d, w, h):
    box(d, 6, 24, w - 6, h - 2, STEEL, STEEL_L, STEEL_D)
    d.rectangle((0, h - 34, w, h - 20), fill=(64, 66, 74, 255), outline=INK)
    for x in range(4, w, 8): d.line((x, h - 33, x, h - 21), fill=(118, 122, 132, 255))
    for k, c in enumerate(((150, 120, 90, 255), (190, 170, 120, 255), (120, 160, 170, 255))):
        x = 16 + k * 34; d.polygon([(x, 6), (x + 22, 6), (x + 18, 26), (x + 4, 26)], fill=c, outline=INK)
    d.rectangle((w // 2 - 14, 40, w // 2 + 14, 54), fill=DARK, outline=INK); d.rectangle((w // 2 - 10, 43, w // 2 + 10, 51), fill=TEAL_D)
    for x in (12, w - 20): d.ellipse((x, 36, x + 8, 44), fill=AMBER, outline=INK)


def hazard_sign(d, w, h):
    d.rectangle((w // 2 - 2, 28, w // 2 + 2, h - 2), fill=STEEL_D, outline=INK)
    d.polygon([(w // 2, 2), (w - 2, 30), (2, 30)], fill=HAZ, outline=INK)
    d.rectangle((w // 2 - 1, 11, w // 2 + 1, 21), fill=INK); d.rectangle((w // 2 - 1, 24, w // 2 + 1, 26), fill=INK)
    d.rectangle((6, h - 6, w - 6, h - 2), fill=STEEL_D, outline=INK)


def breaker_panel(d, w, h):
    box(d, 6, 4, w - 6, h - 2, (110, 116, 126, 255), STEEL_L, STEEL_D)
    d.rectangle((12, 12, w - 12, 50), fill=DARK, outline=INK)
    for row in range(3):
        for k in range(4):
            x, y = 16 + k * 9, 16 + row * 11
            d.rectangle((x, y, x + 5, y + 8), fill=(200, 200, 200, 255), outline=INK); d.rectangle((x + 1, y + (1 if (k + row) % 3 else 5), x + 4, y + (3 if (k + row) % 3 else 7)), fill=INK)
    for k, c in enumerate((RED, (90, 200, 110, 255), AMBER)): d.ellipse((16 + k * 12, 58, 24 + k * 12, 66), fill=c, outline=INK)
    d.rectangle((12, h - 14, w - 12, h - 8), fill=HAZ)
    d.rectangle((w // 2 - 3, 0, w // 2 + 3, 6), fill=(60, 60, 66, 255))


def storage_shelf(d, w, h):
    for x in (4, w - 8): d.rectangle((x, 4, x + 4, h - 2), fill=(70, 110, 160, 255), outline=INK)
    for y in (30, 62, 94): d.rectangle((4, y, w - 4, y + 4), fill=(214, 140, 50, 255), outline=INK)
    import random; r = random.Random(w * h)
    for y in (6, 38, 70):
        x = 10
        while x < w - 22:
            bw = r.choice((14, 18, 22)); bh = r.choice((16, 20, 24))
            c = r.choice(((176, 140, 96, 255), (150, 160, 170, 255), (120, 150, 110, 255), (196, 170, 120, 255)))
            d.rectangle((x, y + 24 - bh, x + bw, y + 24), fill=c, outline=INK); x += bw + 3


def barrel_stack(d, w, h):
    for k, (x, y) in enumerate(((4, h - 40), (w - 32, h - 40), (18, h - 66))):
        c = ((60, 120, 180, 255), (200, 80, 60, 255), (60, 120, 180, 255))[k]
        d.rounded_rectangle((x, y, x + 28, y + 38), 6, fill=c, outline=INK, width=2)
        for yy in (y + 10, y + 26): d.line((x + 2, yy, x + 26, yy), fill=INK)
        d.ellipse((x + 4, y + 2, x + 24, y + 8), fill=STEEL_L, outline=INK)


def pallet(d, w, h):
    d.rectangle((2, h - 10, w - 2, h - 2), fill=WOOD, outline=INK)
    for x in (6, w // 2 - 3, w - 12): d.rectangle((x, h - 10, x + 6, h - 2), fill=WOOD_D)
    for k, (x, y) in enumerate(((4, h - 30), (32, h - 30), (18, h - 48))):
        d.rounded_rectangle((x, y, x + 28, y + 20), 7, fill=(214, 200, 168, 255), outline=INK, width=2)
        d.line((x + 6, y + 10, x + 22, y + 10), fill=(150, 130, 100, 255))


def cargo_loader(d, w, h):
    box(d, 10, 34, w - 10, h - 12, HAZ, (250, 214, 110, 255), (180, 140, 30, 255))
    d.rectangle((16, 14, 52, 36), fill=GLASS, outline=INK, width=2); d.rectangle((14, 10, 54, 16), fill=DARK, outline=INK)
    d.rectangle((w - 22, 6, w - 16, h - 14), fill=STEEL_D, outline=INK)
    d.rectangle((w - 16, h - 22, w - 2, h - 16), fill=STEEL, outline=INK)
    for x in (16, w - 40): d.ellipse((x, h - 22, x + 20, h - 2), fill=DARK, outline=INK); d.ellipse((x + 6, h - 16, x + 14, h - 8), fill=STEEL_L)


def customs_desk(d, w, h):
    box(d, 2, 22, w - 2, h - 2, CREAM, (246, 238, 220, 255), CREAM_D)
    d.rectangle((2, 22, w - 2, 30), fill=(60, 104, 112, 255), outline=INK)
    d.rectangle((60, 4, 86, 22), fill=DARK, outline=INK); d.rectangle((63, 7, 83, 19), fill=TEAL_D)
    d.rectangle((14, 12, 30, 22), fill=STEEL_L, outline=INK); d.line((22, 12, 22, 4), fill=INK, width=2)
    d.rectangle((40, h - 20, 56, h - 10), fill=AMBER, outline=INK)


def stanchion(d, w, h):
    d.ellipse((6, h - 8, w - 6, h - 2), fill=STEEL_D, outline=INK)
    d.rectangle((w // 2 - 2, 8, w // 2 + 2, h - 6), fill=(200, 170, 90, 255), outline=INK)
    d.ellipse((w // 2 - 5, 2, w // 2 + 5, 12), fill=(220, 190, 110, 255), outline=INK)
    d.rectangle((w // 2 + 3, 9, w - 1, 13), fill=RED)


def departures_board(d, w, h):
    legs(d, (16, w - 20), 50, h - 2)
    box(d, 2, 2, w - 2, 54, DARK, STEEL, INK)
    for k in range(5):
        y = 10 + k * 8
        d.rectangle((8, y, 60, y + 5), fill=(220, 200, 120, 255)); d.rectangle((66, y, w - 8, y + 5), fill=RED if k % 2 else (200, 80, 60, 255))


def beacon_mast(d, w, h):
    d.ellipse((6, h - 26, w - 6, h - 4), fill=STEEL_D, outline=INK, width=2)
    d.rectangle((w // 2 - 6, 20, w // 2 + 6, h - 14), fill=STEEL, outline=INK)
    for y in range(30, h - 20, 16): d.line((w // 2 - 6, y, w // 2 + 6, y + 10), fill=STEEL_L, width=2)
    d.ellipse((w // 2 - 14, 2, w // 2 + 14, 26), fill=(250, 200, 80, 255), outline=INK, width=2)
    d.ellipse((w // 2 - 6, 8, w // 2 + 6, 20), fill=(255, 240, 180, 255))
    d.rectangle((14, h - 30, w - 14, h - 24), fill=(60, 104, 112, 255), outline=INK)


def planter_dead(d, w, h):
    box(d, 2, 16, w - 2, h - 2, (150, 136, 116, 255), (180, 166, 146, 255), (110, 100, 86, 255))
    d.rectangle((6, 16, w - 6, 24), fill=(90, 74, 60, 255))
    for x in (16, 34, 52, 70):
        d.line((x, 18, x - 4, 4), fill=(120, 100, 70, 255), width=2); d.line((x - 2, 10, x + 4, 6), fill=(120, 100, 70, 255), width=2)


def rubble(d, w, h):
    for x, y, r in ((8, h - 12, 9), (24, h - 16, 11), (42, h - 12, 8), (54, h - 8, 5)):
        d.polygon([(x - r, y + r // 2), (x - r // 2, y - r // 2), (x + r // 2, y - r // 2), (x + r, y + r // 2)], fill=(150, 140, 130, 255), outline=INK)
    d.line((16, h - 22, 30, h - 4), fill=STEEL_D, width=3)


def glass_shards(d, w, h):
    for x, y in ((8, 10), (24, 16), (40, 8), (50, 18), (16, 22)):
        d.polygon([(x, y), (x + 8, y - 4), (x + 10, y + 4), (x + 3, y + 6)], fill=(180, 230, 244, 255), outline=(90, 130, 150, 255))


def shipping_bin(d, w, h):
    box(d, 4, 18, w - 4, h - 2, WOOD, (186, 140, 100, 255), WOOD_D)
    d.polygon([(4, 18), (w - 4, 18), (w - 10, 4), (10, 4)], fill=(186, 140, 100, 255), outline=INK)
    for y in (30, 44): d.line((6, y, w - 6, y), fill=WOOD_D, width=2)
    d.rectangle((w // 2 - 8, 34, w // 2 + 8, 42), fill=AMBER, outline=INK)


def steam_vent(d, w, h):
    d.ellipse((2, h - 12, w - 2, h - 2), fill=(110, 110, 110, 255), outline=INK)
    d.ellipse((8, h - 10, w - 8, h - 5), fill=(60, 60, 60, 255))
    for k, (x, y) in enumerate(((10, h - 22), (16, h - 30), (8, h - 36))):
        d.ellipse((x, y, x + 12, y + 10), fill=(236, 244, 248, 255))


def bunk_bed(d, w, h):
    for x in (4, w - 8): d.rectangle((x, 4, x + 4, h - 2), fill=STEEL_D, outline=INK)
    for y in (24, 64):
        d.rectangle((4, y, w - 4, y + 16), fill=(150, 160, 150, 255), outline=INK)
        d.rectangle((8, y - 4, 24, y + 4), fill=(226, 222, 210, 255), outline=INK)
    d.line((8, 80, w - 8, 72), fill=(110, 110, 100, 255), width=3)


def armchair(d, w, h):
    box(d, 6, 8, w - 6, h - 20, (150, 70, 60, 255), (190, 100, 90, 255), (110, 50, 44, 255), r=8)
    box(d, 2, 28, 14, h - 6, (150, 70, 60, 255)); box(d, w - 14, 28, w - 2, h - 6, (150, 70, 60, 255))
    box(d, 12, 36, w - 12, h - 8, (176, 90, 80, 255))
    for x in (8, w - 12): d.rectangle((x, h - 6, x + 4, h - 2), fill=WOOD_D)


def footlocker(d, w, h):
    box(d, 2, 6, w - 2, h - 2, (80, 100, 70, 255), (110, 130, 100, 255), (60, 76, 52, 255))
    d.line((4, 14, w - 4, 14), fill=INK); d.rectangle((w // 2 - 4, 12, w // 2 + 4, 20), fill=STEEL_L, outline=INK)


def gym_rack(d, w, h):
    legs(d, (6, w - 10), 20, h - 2)
    d.rectangle((2, 20, w - 2, 26), fill=STEEL, outline=INK); d.rectangle((2, 44, w - 2, 50), fill=STEEL, outline=INK)
    for x in (12, 32, 52, 72):
        d.ellipse((x, 8, x + 12, 22), fill=DARK, outline=INK); d.ellipse((x, 32, x + 12, 46), fill=DARK, outline=INK)


def front_desk(d, w, h):
    box(d, 2, 20, w - 2, h - 2, (150, 104, 66, 255), (186, 140, 100, 255), (108, 74, 48, 255))
    d.rectangle((2, 18, w - 2, 26), fill=(226, 214, 190, 255), outline=INK)
    for x in range(14, w - 10, 24): d.rectangle((x, 32, x + 14, h - 10), outline=(108, 74, 48, 255))
    d.ellipse((w // 2 - 7, 8, w // 2 + 7, 20), fill=(220, 180, 80, 255), outline=INK)
    d.rectangle((20, 8, 40, 18), fill=DARK, outline=INK); d.rectangle((23, 10, 37, 16), fill=TEAL_D)
    d.rectangle((w - 44, 12, w - 24, 18), fill=(240, 236, 220, 255), outline=INK)


def front_desk_side(d, w, h):
    box(d, 2, 20, w - 2, h - 2, (150, 104, 66, 255), (186, 140, 100, 255), (108, 74, 48, 255))
    d.rectangle((2, 18, w - 2, 26), fill=(226, 214, 190, 255), outline=INK)
    d.rectangle((16, 32, w - 16, h - 10), outline=(108, 74, 48, 255))
    d.rectangle((w // 2 - 10, 8, w // 2 + 10, 18), fill=(120, 170, 100, 255), outline=INK)


def key_board(d, w, h):
    legs(d, (10, w - 14), 50, h - 2)
    box(d, 4, 4, w - 4, 54, WOOD, (186, 140, 100, 255), WOOD_D)
    for r in range(3):
        for c in range(4):
            x, y = 12 + c * 12, 12 + r * 14
            d.ellipse((x, y, x + 4, y + 4), fill=AMBER); d.line((x + 2, y + 4, x + 2, y + 10), fill=(220, 190, 110, 255))


def luggage_cart(d, w, h):
    d.rectangle((6, h - 16, w - 6, h - 10), fill=(220, 180, 80, 255), outline=INK)
    for x in (8, w - 12): d.rectangle((x, 8, x + 4, h - 12), fill=(220, 180, 80, 255), outline=INK)
    d.arc((8, 0, w - 8, 20), 180, 360, fill=(220, 180, 80, 255), width=4)
    d.rectangle((14, 30, 40, h - 16), fill=(150, 70, 60, 255), outline=INK); d.rectangle((30, 40, 52, h - 16), fill=(60, 104, 112, 255), outline=INK)
    for x in (8, w - 16): d.ellipse((x, h - 10, x + 8, h - 2), fill=DARK)


def sofa(d, w, h):
    box(d, 6, 8, w - 6, h - 22, (60, 104, 112, 255), (90, 140, 150, 255), (40, 76, 84, 255), r=8)
    box(d, 2, 26, 14, h - 6, (60, 104, 112, 255)); box(d, w - 14, 26, w - 2, h - 6, (60, 104, 112, 255))
    box(d, 12, 32, w - 12, h - 8, (80, 126, 134, 255))
    d.line((w // 2, 34, w // 2, h - 10), fill=(40, 76, 84, 255))


def fireplace(d, w, h):
    box(d, 2, 10, w - 2, h - 2, (170, 150, 130, 255), (200, 184, 166, 255), (120, 104, 90, 255))
    d.rectangle((0, 6, w, 14), fill=(150, 104, 66, 255), outline=INK)
    d.rounded_rectangle((20, 40, w - 20, h - 8), 10, fill=(40, 30, 30, 255), outline=INK, width=2)
    d.polygon([(32, h - 10), (40, h - 34), (48, h - 18), (56, h - 40), (64, h - 10)], fill=(250, 140, 50, 255))
    d.polygon([(40, h - 10), (48, h - 26), (56, h - 10)], fill=(255, 220, 120, 255))


def fridge(d, w, h):
    box(d, 4, 4, w - 4, h - 2, (226, 230, 232, 255), (255, 255, 255, 255), (180, 186, 190, 255))
    d.line((6, 40, w - 6, 40), fill=INK, width=2)
    for y in (16, 52): d.rectangle((w - 14, y, w - 10, y + 20), fill=STEEL_D)
    d.rectangle((12, 10, 26, 16), fill=TEAL_D)


def fruit_tree(d, w, h):
    d.rectangle((w // 2 - 4, h - 34, w // 2 + 4, h - 4), fill=WOOD_D, outline=INK)
    d.ellipse((w // 2 - 14, h - 10, w // 2 + 14, h - 2), fill=(110, 84, 62, 255))
    d.ellipse((4, 4, w - 4, h - 30), fill=(90, 150, 70, 255), outline=INK, width=2)
    for x, y in ((18, 20), (36, 14), (42, 34), (22, 40), (30, 28)): d.ellipse((x, y, x + 7, y + 7), fill=(230, 120, 60, 255), outline=INK)


def park_tree(d, w, h):
    d.rectangle((w // 2 - 4, h - 34, w // 2 + 4, h - 4), fill=WOOD_D, outline=INK)
    d.ellipse((2, 2, w - 2, h - 28), fill=(80, 136, 70, 255), outline=INK, width=2)
    d.ellipse((12, 10, w - 22, h - 50), fill=(110, 170, 90, 255))


def treadmill(d, w, h):
    d.rectangle((4, h - 22, w - 4, h - 6), fill=DARK, outline=INK); d.rectangle((8, h - 20, w - 8, h - 10), fill=(60, 64, 72, 255))
    for x in (6, w - 10): d.rectangle((x, 10, x + 4, h - 20), fill=STEEL, outline=INK)
    d.rectangle((6, 6, w - 6, 18), fill=STEEL_D, outline=INK); d.rectangle((w // 2 - 8, 8, w // 2 + 8, 15), fill=TEAL_D)


def weight_bench(d, w, h):
    d.rectangle((10, h - 26, w - 30, h - 16), fill=(60, 62, 70, 255), outline=INK)
    legs(d, (14, w - 36), h - 16, h - 2)
    for x in (w - 26, w - 12): d.rectangle((x, 8, x + 4, h - 4), fill=STEEL, outline=INK)
    d.rectangle((w - 34, 14, w - 2, 18), fill=STEEL_L, outline=INK)
    for x in (w - 34, w - 6): d.ellipse((x - 4, 6, x + 4, 26), fill=DARK, outline=INK)


def punching_bag(d, w, h):
    d.line((w // 2, 0, w // 2, 10), fill=STEEL_D, width=2)
    d.rounded_rectangle((4, 10, w - 4, h - 14), 8, fill=(150, 50, 44, 255), outline=INK, width=2)
    d.rectangle((4, 24, w - 4, 28), fill=(220, 200, 120, 255))
    d.ellipse((6, h - 8, w - 6, h - 2), fill=(70, 70, 70, 255))


def court_hoop(d, w, h):
    d.rectangle((w // 2 - 3, 30, w // 2 + 3, h - 6), fill=STEEL, outline=INK)
    d.ellipse((6, h - 10, w - 6, h - 2), fill=STEEL_D, outline=INK)
    d.rectangle((4, 4, w - 4, 28), fill=(240, 240, 236, 255), outline=INK); d.rectangle((w // 2 - 8, 12, w // 2 + 8, 24), outline=RED, width=2)
    d.ellipse((w // 2 - 9, 26, w // 2 + 9, 34), outline=(240, 130, 50, 255), width=3)


def washer(d, w, h):
    box(d, 4, 4, w - 4, h - 2, (236, 238, 240, 255), (255, 255, 255, 255), (190, 196, 200, 255))
    d.rectangle((6, 6, w - 6, 16), fill=(200, 206, 212, 255), outline=INK)
    d.ellipse((14, 22, w - 14, h - 10), fill=(120, 190, 220, 255), outline=INK, width=3)
    d.ellipse((22, 30, w - 22, h - 18), fill=(170, 220, 240, 255))
    for x in (w - 20, w - 12): d.ellipse((x, 9, x + 5, 14), fill=TEAL_D)


def laundry_basket(d, w, h):
    d.polygon([(2, 14), (w - 2, 14), (w - 6, h - 2), (6, h - 2)], fill=(200, 170, 120, 255), outline=INK)
    for y in (20, 28): d.line((4, y, w - 4, y), fill=(160, 130, 90, 255))
    d.ellipse((6, 4, 18, 16), fill=(120, 170, 210, 255), outline=INK); d.ellipse((14, 2, 26, 14), fill=(230, 180, 190, 255), outline=INK)


def star_chart(d, w, h):
    legs(d, (16, w - 20), h - 20, h - 2)
    box(d, 4, 4, w - 4, h - 18, DARK, STEEL_L)
    d.rectangle((10, 10, w - 10, h - 24), fill=(16, 26, 54, 255))
    import random
    rnd = random.Random(w * h)
    pts = [(rnd.randint(14, w - 14), rnd.randint(14, h - 28)) for _ in range(9)]
    for a, b in zip(pts, pts[1:5]): d.line(a + b, fill=TEAL_D, width=1)
    for p in pts: d.rectangle((p[0] - 1, p[1] - 1, p[0] + 1, p[1] + 1), fill=(240, 236, 200, 255))


def bed(d, w, h):
    box(d, 4, 10, w - 4, h - 2, WOOD, (186, 140, 96, 255), WOOD_D)
    d.rectangle((8, 16, w - 8, h - 10), fill=(120, 80, 150, 255), outline=INK)            # purple and gold, like his robes
    d.rectangle((8, 16, w - 8, 34), fill=CREAM, outline=INK)
    d.line((8, 48, w - 8, 48), fill=AMBER, width=3)


def wardrobe(d, w, h):
    box(d, 4, 4, w - 4, h - 2, WOOD, (186, 140, 96, 255), WOOD_D)
    d.line((w // 2, 10, w // 2, h - 8), fill=INK, width=2)
    for x in (w // 2 - 7, w // 2 + 4): d.rectangle((x, h // 2 - 4, x + 3, h // 2 + 4), fill=AMBER)


PROPS = {
    'holo_dais': (96, 96, holo_dais), 'memory_core': (64, 112, memory_core), 'wall_screen': (128, 80, wall_screen),
    'console': (64, 64, console), 'tape_archive': (64, 104, tape_archive), 'sensor_panel': (64, 104, sensor_panel),
    'concierge_desk': (96, 72, concierge_desk), 'paris_pictures': (96, 80, paris_pictures),
    'case_fossil': (64, 72, case(fossil)), 'case_relic': (64, 72, case(relic)), 'case_shard': (64, 72, case(shard)),
    'case_wreck': (64, 72, case(wreck)), 'museum_centerpiece': (128, 128, centerpiece), 'curator_desk': (96, 72, curator_desk),
    'crystal_pedestal': (64, 112, crystal_pedestal), 'sanctum_door': (32, 112, sanctum_door), 'lab_door': (32, 112, lab_door),
    'star_chart': (64, 104, star_chart),
    'geo_core': (160, 144, geo_core), 'furnace': (64, 104, furnace), 'ore_crusher': (96, 104, ore_crusher), 'ore_cart': (64, 56, ore_cart),
    'pump': (64, 96, pump), 'pipe_rack': (96, 64, pipe_rack), 'locker': (64, 104, locker), 'tool_cart': (64, 64, tool_cart),
    'welding_rig': (64, 96, welding_rig), 'fuel_tank': (64, 112, fuel_tank), 'parts_rack': (96, 104, parts_rack),
    'launch_console': (96, 72, launch_console), 'air_scrubber': (64, 104, air_scrubber), 'mag_clamp': (32, 32, mag_clamp),
    'launch_door': (384, 112, launch_door), 'coolant_tank': (96, 128, coolant_tank), 'kitchenette': (128, 96, kitchenette),
    'ore_pile': (96, 56, ore_pile), 'hopper': (96, 128, hopper), 'ingot_stack': (64, 56, ingot_stack), 'slag_bin': (64, 64, slag_bin),
    'sorting_machine': (128, 104, sorting_machine), 'hazard_sign': (32, 72, hazard_sign), 'breaker_panel': (64, 104, breaker_panel),
    'storage_shelf': (96, 112, storage_shelf), 'barrel_stack': (64, 72, barrel_stack), 'pallet': (64, 56, pallet), 'cargo_loader': (96, 96, cargo_loader),
    'customs_desk': (96, 64, customs_desk), 'stanchion': (32, 40, stanchion), 'departures_board': (128, 88, departures_board),
    'beacon_mast': (96, 144, beacon_mast), 'planter_dead': (96, 56, planter_dead), 'rubble': (64, 32, rubble), 'glass_shards': (64, 28, glass_shards),
    'shipping_bin': (64, 64, shipping_bin), 'steam_vent': (32, 48, steam_vent), 'bunk_bed': (64, 104, bunk_bed), 'armchair': (64, 72, armchair),
    'footlocker': (64, 36, footlocker), 'gym_rack': (96, 72, gym_rack),
    'front_desk': (160, 72, front_desk), 'front_desk_l': (96, 72, front_desk_side), 'front_desk_r': (96, 72, front_desk_side),
    'key_board': (64, 80, key_board), 'luggage_cart': (64, 72, luggage_cart), 'sofa': (96, 64, sofa), 'fireplace': (96, 104, fireplace),
    'fridge': (64, 104, fridge),
    'fruit_tree': (64, 104, fruit_tree), 'park_tree': (64, 112, park_tree), 'treadmill': (64, 72, treadmill), 'weight_bench': (96, 64, weight_bench),
    'punching_bag': (32, 80, punching_bag), 'court_hoop': (64, 104, court_hoop), 'washer': (64, 72, washer), 'laundry_basket': (32, 36, laundry_basket), 'case_empty': (64, 72, case_empty),
    'crystal_pedestal_empty': (64, 112, crystal_pedestal_empty), 'precursor_mural': (96, 112, precursor_mural),
    'test_rig': (64, 96, test_rig), 'spectrometer': (64, 72, spectrometer), 'brazier': (32, 64, brazier),
    'holy_banner': (32, 112, holy_banner), 'prayer_mat': (64, 32, prayer_mat), 'bed': (64, 96, bed), 'wardrobe': (64, 112, wardrobe),
}

if __name__ == "__main__":
    for name, (w, h, draw) in PROPS.items():
        path = os.path.join(OUT, name + ".png")
        if os.path.exists(path):
            continue
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw(ImageDraw.Draw(im), w, h)
        # hard edges only: anything half see-through becomes either solid or gone
        px = im.load()
        for yy in range(h):
            for xx in range(w):
                r, g, b, a = px[xx, yy]
                px[xx, yy] = (r, g, b, 255 if a >= 100 else 0) if a not in (0, 255) and a < 150 and (r, g, b) == (170, 220, 236) else (r, g, b, 0 if a < 100 else 255)
        im.save(path)
        print("placeholder:", path)
