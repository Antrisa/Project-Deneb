"""Build a resident's front and back walks (rows 1 to 4, columns 0 and 1) from the standing
frames, with the legs and hands moved as separate pieces.

Usage: python3 -I rig_front.py SRC_ART_DIR OUT_ART_DIR name ...

Front (toward the camera) and back walks, per row:
- contact A / B: the body drops one pixel. One leg steps out (it keeps its full length),
  the other trails (its foot one pixel higher, a shade darker). The hand on the side of the
  trailing leg swings forward (its arm one pixel longer), the other hand swings back (one
  pixel shorter).
- passing A / B: one leg is planted, the other lifts its foot two pixels; hands at rest.
The feet stay on row 45 except where lifted. Legs and hands are cut from the standing frame
by the column ranges in CAST; nothing else is redrawn, so the body keeps its painted detail.
Coat or apron shortening (if listed) is applied to the standing frame first.
"""
import sys, os
import numpy as np
from PIL import Image

FW, FH = 24, 48
DARK = 0.8

# Per resident and facing (0 front, 1 back): hip row (first leg row below the hem), the two
# legs' column ranges (viewer's left, viewer's right), the two hands as (x0, x1, y0, y1).
# 'shorten' moves the hem up: rows (a, b) of the columns (c0, c1) go to row t, and the
# trouser row 'leg_row' fills down to the new hip.
RUSK_FIST = {"M": (0x2a, 0x12, 0x19), "h": (0xe7, 0x95, 0x68), "s": (0xe6, 0x75, 0x43),
             "l": (0xc6, 0x59, 0x33)}


def widen_right_leg(c):
    """Rusk's right leg was a pixel narrower than his left: its outline moves out a column."""
    for y in (41, 42):
        c[y, 18] = c[y, 17]
        c[y, 17] = c[y, 16]


def square_left_boot(c):
    """From behind, Rusk's left boot had its heel a pixel past the sole above it."""
    for y in (44, 45):
        c[y, 4] = 0
        c[y, 5] = (0x2a, 0x12, 0x19, 255)


OOMA_FIST = {"M": (0x2a, 0x11, 0x21), "h": (0xd0, 0x86, 0x88), "s": (0xb8, 0x6d, 0x70),
             "l": (0xa9, 0x5a, 0x64)}

TOBBIN_FIST = {"M": (0x36, 0x1f, 0x1d), "h": (0xe9, 0xac, 0x58), "s": (0xc8, 0x8b, 0x42),
               "l": (0xa0, 0x6f, 0x3c)}

MERROW_FIST = {"M": (0x27, 0x0e, 0x16), "h": (0xb5, 0xd6, 0xba), "s": (0x94, 0xbb, 0x9a),
               "l": (0x69, 0x8b, 0x7a)}

NUB_FIST = {"M": (0x26, 0x10, 0x1a), "h": (0xe1, 0xd9, 0x81), "s": (0xce, 0xc7, 0x5f),
            "l": (0xa7, 0x96, 0x40)}

GARRICK_FIST = {"M": (0x28, 0x19, 0x2a), "h": (0xfb, 0xb9, 0x72), "s": (0xec, 0xa2, 0x6a),
                "l": (0xcf, 0x8d, 0x60)}


def square_garrick_boots(c):
    """His left boot was a pixel narrower than his right on its top and bottom rows."""
    for y in (43, 45):
        c[y, 5] = (0x31, 0x1c, 0x2a, 255)


SAFFI_FIST = {"M": (0x2b, 0x0c, 0x11), "h": (0xdf, 0xb8, 0x9a), "s": (0xc9, 0xa1, 0x85),
              "l": (0x97, 0x6f, 0x62)}

def saffi_hips(c):
    """Behind her hands, at her hips, the skirt already flares out; with the hands lifted
    off (as fists or moving arms) that flare is painted in so no notch is left."""
    row = c[35].copy()
    for y, left, right in ((32, 6, 17), (33, 5, 18), (34, 4, 18)):
        for x in range(left, 7):
            c[y, x] = row[max(x, 4) + (1 if x == left else 0)] if x != left else row[4]
        for x in range(17, right + 1):
            c[y, x] = row[18] if x == right else row[17]


# his paws are pale, so they read against his brown shorts
KIT_FIST = {"M": (0x2c, 0x0a, 0x0f), "h": (0xfd, 0xd7, 0xaf), "s": (0xe7, 0xc4, 0xa0),
            "l": (0xbd, 0x8a, 0x62)}

IXALI_FIST = {"M": (0x22, 0x0d, 0x18), "h": (0xeb, 0xc6, 0x59), "s": (0xdd, 0xb7, 0x4e),
              "l": (0xb7, 0x95, 0x43)}

def maren_hands_to_coat(c):
    """Her painted hands at the coat's sides are repainted as coat, so the moving fists
    leave nothing behind."""
    skin = {(0xe0, 0xa6, 0x86), (0xe5, 0xb3, 0x99), (0xf2, 0xd2, 0xb6)}
    for y in range(31, 37):
        for x in list(range(1, 8)) + list(range(16, 23)):
            if c[y, x, 3] and tuple(c[y, x, :3]) in skin:
                c[y, x, :3] = (0xe9, 0xc2, 0xa8)


def maren_winter_hands_to_coat(c):
    """Her painted hands and rust mittens (rows 28-33) are repainted as coat under the moving
    fists; the coat's outer outline is kept."""
    skin = {(0xf3, 0xcc, 0xa2), (0xa7, 0x80, 0x83), (0x94, 0x77, 0x76), (0x8d, 0x6a, 0x73),
            (0x7d, 0x56, 0x57), (0xbd, 0x8a, 0x7f), (0x7f, 0x3b, 0x30), (0x61, 0x37, 0x38),
            (0x9b, 0x54, 0x4a), (0x4f, 0x26, 0x28)}
    for y in range(28, 34):
        xs = np.where(c[y, :, 3] > 0)[0]
        if not len(xs):
            continue
        edge = {int(xs.min()), int(xs.max())}
        for x in list(range(1, 8)) + list(range(16, 23)):
            if c[y, x, 3] and tuple(c[y, x, :3]) in skin:
                # on the silhouette's edge the mitten becomes the coat's dark outline
                c[y, x, :3] = (0x2c, 0x1e, 0x1f) if x in edge else (0x35, 0x4b, 0x4f)


MAREN_FIST = {"M": (0x35, 0x14, 0x1c), "h": (0xf2, 0xd2, 0xb6), "s": (0xe0, 0xa6, 0x86),
              "l": (0xc8, 0x96, 0x8a)}

QUILL_FIST = {"M": (0x16, 0x0c, 0x14), "h": (0xa1, 0xbf, 0xae), "s": (0x6a, 0x85, 0x79),
              "l": (0x48, 0x55, 0x50)}


def quill_legs_front(c):
    """His left leg was a pixel narrower than his right: its outline moves out a column."""
    for y in range(38, 43):
        c[y, 6] = c[y, 7]
        c[y, 7] = c[y, 8]


def quill_legs_back(c):
    """From behind it is his right leg that was a pixel narrower."""
    for y in range(38, 43):
        c[y, 17] = c[y, 16]
        c[y, 16] = c[y, 15]


def pip_left_sleeve(c):
    """His left sleeve bulged a pixel out at row 33; as the arm swings the bulge was left
    sticking out on its own, so the sleeve edge is kept straight."""
    c[33, 5] = 0


def pip_back_right_sleeve(c):
    """From behind his right sleeve bulged out at row 33; with the arm hidden the bulge was
    left on its own."""
    c[33, 17] = 0


def bram_vest_edge(c):
    """Under his right hand the vest's edge had no outline of its own (the hand was it); as
    the hand moves away the edge is closed."""
    for y in (37, 38):
        if not c[y, 18, 3]:
            c[y, 18] = (0x2f, 0x14, 0x19, 255)


def freya_feet_front(c):
    """Her right leg and boot were wider than her left and the boot cut off at a slant; the
    right is redrawn as the left mirrored (about the gap between the legs)."""
    c[41:46, 12:19] = c[41:46, 5:12][:, ::-1]


def freya_feet_back(c):
    c[41:46, 13:19] = c[41:46, 6:12][:, ::-1]
    c[41:46, 12] = 0


STU_FIST = {"M": (0x21, 0x10, 0x16), "h": (0xc3, 0xbc, 0x5e), "s": (0xac, 0xb3, 0x4c),
            "l": (0x77, 0x7c, 0x3a)}

ANA_FIST = {"M": (0x2f, 0x16, 0x1e), "h": (0xf9, 0xc5, 0x9b), "s": (0xe1, 0xa3, 0x78),
            "l": (0xaa, 0x7d, 0x67)}

ANA_CHERNOG_FIST = {"M": (0x28, 0x1b, 0x20), "h": (0xf9, 0xc7, 0x8e), "s": (0xd8, 0x9f, 0x64),
                    "l": (0xa6, 0x74, 0x4b)}

SARA_SOLID_FIST = {"M": (0x1d, 0x20, 0x2c), "h": (0xb5, 0xe4, 0xe4), "s": (0x98, 0xe2, 0xe3),
                   "l": (0x6f, 0xbf, 0xc5)}

ARTIE_FIST = {"M": (0x2e, 0x15, 0x1a), "h": (0xf8, 0xbd, 0x83), "s": (0xed, 0xa4, 0x70),
              "l": (0xd5, 0x7b, 0x4f)}

VZZKET_FIST = {"M": (0x1e, 0x0e, 0x16), "h": (0xca, 0xa7, 0x50), "s": (0xb5, 0x97, 0x48),
               "l": (0x87, 0x6a, 0x3d)}

TARBESH_FIST = {"M": (0x2e, 0x18, 0x1d), "h": (0xd8, 0xa8, 0x57), "s": (0xb3, 0x94, 0x4d),
                "l": (0x92, 0x75, 0x3f)}

ZAAS_FIST = {"M": (0x25, 0x1a, 0x24), "h": (0x73, 0xbd, 0xab), "s": (0x5d, 0xa3, 0x95),
             "l": (0x40, 0x6c, 0x6b)}

JOB_FIST = {"M": (0x2f, 0x15, 0x1f), "h": (0xc5, 0x67, 0x34), "s": (0xb6, 0x60, 0x37),
            "l": (0x8e, 0x4c, 0x2f)}

FREYA_FIST = {"M": (0x5e, 0x34, 0x30), "h": (0xf2, 0xc2, 0x9a), "s": (0xd9, 0x92, 0x6e),
              "l": (0xb0, 0x81, 0x58)}

BRAM_FIST = {"M": (0x2f, 0x14, 0x19), "h": (0xb1, 0xb8, 0x52), "s": (0xa6, 0xaa, 0x4d),
             "l": (0x7d, 0x76, 0x49)}

PIP_FIST = {"M": (0x2e, 0x0d, 0x10), "h": (0xf2, 0xc1, 0x94), "s": (0xec, 0xa5, 0x6f),
            "l": (0xda, 0x92, 0x61)}

OWEN_FIST = {"M": (0x2a, 0x0e, 0x15), "h": (0xf4, 0xc2, 0x95), "s": (0xeb, 0xa8, 0x77),
             "l": (0xca, 0x94, 0x6f)}


def owen_jacket_taper(c):
    """Behind his hands the jacket narrows from its widest row (33) to its hem (37); that taper
    is painted in, in the jacket's shadow tone, so a moving or hidden fist leaves no notch."""
    line = (0x2a, 0x0e, 0x15, 255)
    shade = (0xa7, 0x59, 0x28, 255)
    for y, left, right in ((34, 3, 20), (35, 3, 20), (36, 4, 19)):
        for x in range(left, 7):
            if not c[y, x, 3]:
                c[y, x] = shade
        for x in range(17, right + 1):
            if not c[y, x, 3]:
                c[y, x] = shade
        c[y, left] = line
        c[y, right] = line


def owen_right_leg(c):
    """His right leg was a pixel narrower than his left: its outline moves out a column."""
    for y in (41, 42):
        c[y, 18] = c[y, 17]
        c[y, 17] = c[y, 16]


JASPER_FIST = {"M": (0x27, 0x0e, 0x1b), "h": (0xfa, 0x94, 0x49), "s": (0xf5, 0x82, 0x3a),
               "l": (0xd8, 0x6f, 0x38)}

CAST = {
    "evarra": {
        # the right leg had an extra outline column (x 13); it is taken out so both legs are
        # four pixels wide with a two-pixel gap
        0: dict(hip=36, legs=((7, 11), (14, 18)), hands=((3, 7, 31, 35), (17, 21, 31, 35)),
                fists=((6, 31), (15, 31)), face=True,
                arms=((5, 8), (16, 20)), arm_rows=(27, 30), neck=22,
                patch=[(16, 43, "G")],  # an olive speck on the right boot
                hand_clear=[(3, 7, 31, 33), (17, 22, 31, 33), (19, 22, 34, 34)],
                clear=[(13, 36, 45)],
                shorten=dict(rows=(36, 38), cols=(5, 19), to=33, leg_row=40)),
        1: dict(hip=36, legs=((5, 11), (12, 19)), hands=((2, 6, 31, 35), (17, 21, 31, 35)),
                fists=((5, 31), (15, 31)), face=False,
                # both boots squared off to five pixels (the painted ones had stray heel and
                # sole pixels sticking out at x5, x11 and x18)
                patch=[(18, 34, "."), (11, 41, "."), (5, 43, ".DGHGB.."), (5, 44, ".BGGGD.."), (5, 45, ".EFFFE.."),
                       (13, 43, "DGHGD.."), (13, 44, "DGGGB.."), (13, 45, "EFFFE..")], arms=((3, 6), (17, 20)), arm_rows=(27, 30), neck=22,
                hand_clear=[(2, 6, 31, 33), (17, 22, 31, 33), (2, 5, 34, 34), (19, 22, 34, 34)],
                shorten=dict(rows=(36, 38), cols=(4, 19), to=33, leg_row=40)),
    },
    "rusk": {
        # apron to row 40, legs from 41; paws become simple fists at the end of the fur forearms
        0: dict(hip=41, legs=((4, 11), (12, 20)), hands=None,
                fists=((3, 32), (17, 32)), face=True, fist_pal=RUSK_FIST,
                arms=((1, 5), (18, 22)), arm_rows=(27, 31), neck=21,
                hand_clear=[(0, 5, 32, 35), (18, 23, 32, 35)],
                fix=[widen_right_leg]),
        1: dict(hip=41, legs=((3, 10), (11, 18)), hands=None,
                fists=((3, 32), (17, 32)), face=False, fist_pal=RUSK_FIST,
                arms=((1, 5), (17, 22)), arm_rows=(27, 31), neck=20,
                hand_clear=[(0, 5, 32, 35), (18, 23, 32, 35)],
                fix=[square_left_boot]),
    },
    "ooma": {
        # a long robe: hem outline on row 41, feet below. The sleeves are wide drapes and stay
        # put; the tentacle hands become simple pink fists over the robe's front edge
        0: dict(hip=42, legs=((6, 11), (13, 18)), hands=None,
                fists=((6, 32), (16, 32)), face=True, fist_pal=OOMA_FIST,
                arms=None, neck=24, clear=[(12, 42, 45)], short_legs=True),
        # from behind the hands are inside the sleeves
        1: dict(hip=42, legs=((4, 11), (12, 19)), hands=None,
                fists=None, face=False, arms=None, neck=22, short_legs=True),
    },
    "tobbin": {
        # overalls to row 41, short legs from 42; puffed sleeves, tan hands become fists
        0: dict(hip=42, legs=((3, 11), (12, 20)), hands=None,
                fists=((4, 36), (16, 36)), face=True, fist_pal=TOBBIN_FIST,
                arms=((0, 5), (18, 23)), arm_rows=(29, 35), neck=28,
                hand_clear=[(1, 5, 36, 38), (19, 22, 36, 38)], short_legs=True),
        1: dict(hip=42, legs=((2, 11), (12, 21)), hands=None,
                fists=((4, 36), (16, 36)), face=False, fist_pal=TOBBIN_FIST,
                arms=((0, 5), (18, 23)), arm_rows=(29, 35), neck=25,
                hand_clear=[(1, 5, 36, 38), (19, 22, 36, 38)], short_legs=True),
    },
    "merrow": {
        # overalls to row 41, legs and shoes from 42; green hands become fists
        0: dict(hip=42, legs=((4, 11), (12, 19)), hands=None,
                fists=((4, 35), (16, 35)), face=True, fist_pal=MERROW_FIST,
                arms=((1, 5), (17, 21)), arm_rows=(29, 34), neck=23,
                hand_clear=[(1, 5, 35, 38), (18, 22, 35, 38), (2, 3, 34, 34), (20, 21, 34, 34)], short_legs=True),
        1: dict(hip=42, legs=((5, 11), (12, 19)), hands=None,
                fists=((4, 35), (16, 35)), face=False, fist_pal=MERROW_FIST,
                arms=((1, 6), (17, 22)), arm_rows=(29, 34), neck=22,
                hand_clear=[(1, 5, 35, 38), (18, 22, 35, 38), (3, 3, 34, 34), (20, 21, 34, 34)], short_legs=True),
    },
    "nub": {
        # a small frog: shirt and shorts to row 41, stubby legs from 42; pale hands become fists
        0: dict(hip=42, legs=((6, 11), (12, 17)), hands=None,
                fists=((4, 38), (16, 38)), face=True, fist_pal=NUB_FIST,
                arms=((3, 6), (17, 20)), arm_rows=(33, 37), neck=32,
                hand_clear=[(3, 6, 38, 40), (17, 20, 38, 40)], short_legs=True),
        1: dict(hip=42, legs=((6, 11), (12, 18)), hands=None,
                fists=((4, 38), (16, 38)), face=False, fist_pal=NUB_FIST,
                arms=((3, 6), (17, 20)), arm_rows=(33, 37), neck=31,
                hand_clear=[(3, 6, 38, 40), (17, 20, 38, 40)], short_legs=True),
    },
    "garrick": {
        # uniform coat to row 40, legs part from 41; hands become fists at the cuffs
        0: dict(hip=41, legs=((4, 11), (12, 19)), hands=None,
                fists=((4, 32), (16, 32)), face=True, fist_pal=GARRICK_FIST,
                arms=((0, 5), (18, 23)), arm_rows=(27, 31), neck=17,
                hand_clear=[(1, 5, 32, 35), (18, 22, 32, 35), (2, 5, 36, 36), (18, 21, 36, 36)],
                fix=[square_garrick_boots]),
        1: dict(hip=42, legs=((4, 11), (12, 19)), hands=None,
                fists=((4, 32), (16, 32)), face=False, fist_pal=GARRICK_FIST,
                arms=((0, 5), (18, 23)), arm_rows=(27, 31), neck=17,
                hand_clear=[(1, 5, 32, 35), (17, 22, 32, 35), (2, 5, 36, 36), (18, 21, 36, 36)],
                short_legs=True),
    },
    "saffi": {
        # dress to row 41, legs from 42; brown paws become fists at the end of the forearms.
        # From behind her tail ends above the legs, so it stays with the body.
        0: dict(hip=42, legs=((5, 10), (11, 17)), hands=None,
                fists=((4, 32), (16, 32)), face=True, fist_pal=SAFFI_FIST,
                arms=((2, 6), (16, 20)), arm_rows=(27, 31), neck=23,
                hand_clear=[(2, 6, 32, 34), (17, 20, 32, 34)], short_legs=True, after_clear=[saffi_hips]),
        1: dict(hip=42, legs=((5, 10), (11, 17)), hands=None,
                fists=((4, 32), (16, 32)), face=False, fist_pal=SAFFI_FIST,
                arms=((2, 6), (16, 20)), arm_rows=(27, 31), neck=22,
                hand_clear=[(2, 6, 32, 34), (17, 20, 32, 34)], short_legs=True, after_clear=[saffi_hips]),
    },
    "stu": {
        # the round bellhop coat; green frog hands below the cuffs become fists and the coat's
        # edge carries on behind them; thin legs from 39
        0: dict(hip=39, legs=((4, 10), (12, 18)), hands=None,
                fists=((3, 33), (16, 33)), face=True, fist_pal=STU_FIST,
                arms=((3, 7), (16, 20)), arm_rows=(27, 32), neck=20,
                hand_clear=[(3, 6, 33, 36), (17, 19, 33, 36)], fill_cleared=True, refill_sleeve=True),
        1: dict(hip=39, legs=((5, 11), (12, 18)), hands=None,
                fists=((4, 33), (16, 33)), face=False, fist_pal=STU_FIST,
                arms=((3, 7), (16, 20)), arm_rows=(27, 32), neck=20,
                hand_clear=[(4, 7, 33, 36), (16, 19, 33, 36)], fill_cleared=True, refill_sleeve=True),
    },
    "ana": {
        # her pilot's jacket to row 30; the hands below its sleeves become fists and the
        # trousers' edge carries up behind them; baggy trousers part from 36
        0: dict(hip=36, legs=((6, 11), (12, 17)), hands=None,
                fists=((4, 31), (16, 31)), face=True, fist_pal=ANA_FIST,
                arms=((4, 7), (16, 19)), arm_rows=(26, 30), neck=21,
                hand_clear=[(4, 7, 31, 33), (16, 19, 31, 33)], fill_cleared=True, refill_sleeve=True),
        1: dict(hip=36, legs=((6, 11), (12, 17)), hands=None,
                fists=((4, 31), (16, 31)), face=False, fist_pal=ANA_FIST,
                arms=((4, 7), (16, 19)), arm_rows=(26, 30), neck=21,
                hand_clear=[(4, 7, 31, 33), (16, 19, 31, 33)], fill_cleared=True, refill_sleeve=True),
    },
    "ana_chernog": {
        # her Chernog clothes: a striped sweater to row 35; the hands below its cuffs become
        # fists and the sweater's edge carries up behind them; legs part from 36. From behind
        # the collar lifts with the head (the row doubled under it is the sweater's, not the
        # dark inside of the collar)
        0: dict(hip=36, legs=((7, 12), (13, 18)), hands=None,
                fists=((5, 32), (16, 32)), face=True, fist_pal=ANA_CHERNOG_FIST,
                arms=((5, 8), (16, 19)), arm_rows=(26, 30), neck=21,
                hand_clear=[(5, 8, 31, 33), (17, 19, 31, 33)], fill_cleared=True, refill_sleeve=True),
        1: dict(hip=37, legs=((6, 11), (12, 17)), hands=None,
                fists=((4, 32), (15, 32)), face=False, fist_pal=ANA_CHERNOG_FIST,
                arms=((4, 7), (15, 19)), arm_rows=(26, 30), neck=22,
                hand_clear=[(4, 7, 31, 33), (15, 18, 31, 33)], fill_cleared=True, refill_sleeve=True),
    },
    "sara_solid": {
        # S.A.R.A.'s solid body: a slim bodysuit under her long hair; the pale hands below the
        # sleeves become fists and the suit's edge carries up behind them; legs part from 34
        0: dict(hip=34, legs=((9, 13), (14, 18)), hands=None,
                fists=((6, 29), (17, 29)), face=True, fist_pal=SARA_SOLID_FIST,
                arms=((6, 9), (17, 20)), arm_rows=(25, 28), neck=19,
                hand_clear=[(6, 8, 28, 31), (18, 20, 28, 31)], fill_cleared=True, refill_sleeve=True),
        1: dict(hip=34, legs=((7, 11), (12, 16)), hands=None,
                fists=((4, 30), (15, 30)), face=False, fist_pal=SARA_SOLID_FIST,
                arms=((4, 7), (15, 18)), arm_rows=(25, 28), neck=19,
                hand_clear=[(4, 6, 29, 32), (16, 18, 29, 32)], fill_cleared=True, refill_sleeve=True),
    },
    "artie": {
        # rolled sleeves, bare forearms; the hands at the ends of the forearms become fists and
        # the trousers' edge carries up behind them; legs from 39
        0: dict(hip=39, legs=((5, 11), (12, 19)), hands=None,
                fists=((4, 31), (17, 31)), face=True, fist_pal=ARTIE_FIST,
                arms=((4, 8), (16, 20)), arm_rows=(26, 30), neck=19,
                hand_clear=[(4, 7, 31, 34), (17, 20, 31, 34)], fill_cleared=True, refill_sleeve=True),
        1: dict(hip=40, legs=((5, 11), (12, 18)), hands=None,
                fists=((4, 31), (17, 31)), face=False, fist_pal=ARTIE_FIST,
                arms=((3, 8), (16, 21)), arm_rows=(26, 30), neck=19,
                hand_clear=[(4, 7, 31, 34), (17, 20, 31, 34)], fill_cleared=True, refill_sleeve=True),
    },
    "vzzket": {
        # armoured: shoulder plates, arms to row 31, gold hands become fists; legs from 40
        0: dict(hip=40, legs=((5, 11), (12, 19)), hands=None,
                fists=((2, 32), (18, 32)), face=True, fist_pal=VZZKET_FIST,
                arms=((1, 6), (17, 22)), arm_rows=(25, 31), neck=18,
                hand_clear=[(2, 5, 32, 35), (19, 22, 32, 35)], fill_cleared=True, refill_sleeve=True),
        1: dict(hip=40, legs=((5, 11), (12, 18)), hands=None,
                fists=((2, 32), (18, 32)), face=False, fist_pal=VZZKET_FIST,
                arms=((1, 6), (17, 22)), arm_rows=(25, 31), neck=18,
                hand_clear=[(2, 5, 32, 35), (18, 21, 32, 35)], fill_cleared=True, refill_sleeve=True),
    },
    "tarbesh": {
        # a long robe with wide sleeves that stay put; the small hands below the gold cuffs
        # become fists and the robe is carried up behind where they were; short legs from 42
        0: dict(hip=42, legs=((5, 11), (12, 18)), hands=None, arms=None,
                fists=((2, 33), (18, 33)), face=True, fist_pal=TARBESH_FIST, neck=20,
                hand_clear=[(2, 6, 33, 35), (18, 21, 33, 35)], fill_cleared=True, short_legs=True),
        1: dict(hip=42, legs=((5, 11), (12, 18)), hands=None, arms=None,
                fists=((2, 33), (18, 33)), face=False, fist_pal=TARBESH_FIST, neck=20,
                hand_clear=[(2, 5, 33, 35), (18, 21, 33, 35)], fill_cleared=True, short_legs=True),
    },
    "zaas": {
        # thin teal arms below the face tentacles; the vest to row 39, short legs from 40
        0: dict(hip=40, legs=((8, 12), (13, 17)), hands=None,
                fists=((4, 35), (17, 35)), face=True, fist_pal=ZAAS_FIST,
                arms=((4, 7), (17, 20)), arm_rows=(31, 34), neck=30,
                hand_clear=[(4, 7, 35, 38), (18, 20, 35, 38)], fill_cleared=True,
                refill_sleeve=True, short_legs=True),
        1: dict(hip=40, legs=((7, 11), (12, 16)), hands=None,
                fists=((4, 35), (16, 35)), face=False, fist_pal=ZAAS_FIST,
                arms=((4, 7), (16, 19)), arm_rows=(31, 34), neck=30,
                hand_clear=[(4, 6, 35, 37), (17, 19, 35, 37)], fill_cleared=True,
                refill_sleeve=True, short_legs=True),
    },
    "job": {
        # chunky short sleeves and bare forearms; the hands at the bottom of the forearms become
        # fists; overalls to row 39, legs from 40
        0: dict(hip=40, legs=((5, 11), (12, 18)), hands=None,
                fists=((2, 33), (18, 33)), face=True, fist_pal=JOB_FIST,
                arms=((0, 5), (18, 23)), arm_rows=(22, 32), neck=19,
                hand_clear=[(1, 5, 33, 37), (18, 22, 33, 37)], fill_cleared=True, refill_sleeve=True),
        1: dict(hip=40, legs=((4, 11), (12, 19)), hands=None,
                fists=((2, 33), (18, 33)), face=False, fist_pal=JOB_FIST,
                arms=((0, 5), (18, 23)), arm_rows=(21, 32), neck=19,
                hand_clear=[(1, 4, 33, 36), (19, 22, 33, 36)], fill_cleared=True, refill_sleeve=True),
    },
    "freya": {
        # bare arms with leather bracers; baggy trousers to row 40, legs from 41
        0: dict(hip=41, legs=((5, 11), (12, 18)), hands=None,
                fists=((5, 30), (17, 30)), face=True, fist_pal=FREYA_FIST,
                arms=((4, 8), (16, 20)), arm_rows=(27, 29), neck=20,
                hand_clear=[(4, 7, 30, 32), (4, 6, 33, 33), (18, 20, 30, 33)],
                fill_cleared=True, refill_sleeve=True, fix=[freya_feet_front]),
        1: dict(hip=41, legs=((6, 11), (12, 18)), hands=None,
                fists=((4, 31), (17, 31)), face=False, fist_pal=FREYA_FIST,
                arms=((4, 8), (16, 20)), arm_rows=(27, 30), neck=20,
                hand_clear=[(4, 7, 31, 33), (18, 20, 31, 33)], fill_cleared=True, refill_sleeve=True,
                fix=[freya_feet_back]),
    },
    "bram": {
        # vest to row 37, trousers to 41, short legs from 42; puffed sleeves, green hands
        # become fists
        0: dict(hip=42, legs=((5, 11), (12, 18)), hands=None,
                fists=((3, 37), (17, 37)), face=True, fist_pal=BRAM_FIST,
                arms=((1, 6), (17, 22)), arm_rows=(32, 36), neck=28,
                hand_clear=[(1, 5, 37, 40), (18, 21, 37, 40)], fix=[bram_vest_edge], short_legs=True, refill_sleeve=True),
        1: dict(hip=42, legs=((5, 11), (12, 18)), hands=None,
                fists=((3, 37), (17, 37)), face=False, fist_pal=BRAM_FIST,
                arms=((1, 6), (17, 22)), arm_rows=(32, 36), neck=28,
                hand_clear=[(2, 5, 37, 40), (18, 21, 37, 40)], fix=[bram_vest_edge], short_legs=True, refill_sleeve=True),
    },
    "pip": {
        # a small boy: tunic to row 37, shorts to 40, short legs from 41
        0: dict(hip=41, legs=((7, 11), (12, 17)), hands=None,
                fists=((5, 35), (15, 35)), face=True, fist_pal=PIP_FIST,
                arms=((5, 7), (16, 18)), arm_rows=(31, 34), neck=29,
                hand_clear=[(5, 7, 35, 37), (16, 18, 35, 37), (6, 6, 38, 38), (18, 18, 38, 38)],
                fix=[pip_left_sleeve], short_legs=True),
        1: dict(hip=41, legs=((7, 11), (12, 16)), hands=None,
                fists=((4, 35), (15, 35)), face=False, fist_pal=PIP_FIST,
                arms=((4, 7), (16, 18)), arm_rows=(31, 34), neck=29,
                # from behind his hands hang to row 38 (39 at his left); the tunic edge (x 7, 15)
                # stays
                hand_clear=[(4, 6, 35, 39), (16, 18, 35, 38)], fix=[pip_back_right_sleeve],
                short_legs=True),
    },
    "kit": {
        # a little fox: shirt and shorts to row 41, tiny legs from 42 (his tail hangs out to
        # the side, above them); paws become fists
        0: dict(hip=42, legs=((7, 11), (12, 18)), hands=None,
                fists=((6, 35), (15, 35)), face=True, fist_pal=KIT_FIST,
                arms=((6, 8), (16, 18)), arm_rows=(31, 34), neck=31,
                hand_clear=[(6, 7, 35, 36), (17, 18, 35, 36)], short_legs=True),
        # from behind his tail reaches down to row 42: the legs start a row lower, under it
        1: dict(hip=43, legs=((6, 11), (12, 17)), hands=None,
                fists=((6, 35), (15, 35)), face=False, fist_pal=KIT_FIST,
                arms=((5, 8), (16, 18)), arm_rows=(31, 34), neck=30,
                # from behind his hands hang a little lower (rows 35-39 on his left, 36-37 on
                # his right, where his tail starts below)
                hand_clear=[(4, 7, 35, 36), (4, 6, 37, 39), (17, 19, 35, 37)], short_legs=True),
    },
    "ixali": {
        # tunic to row 40, legs part from 41; gold hands become fists
        0: dict(hip=41, legs=((5, 12), (13, 21)), hands=None,
                fists=((5, 32), (17, 32)), face=True, fist_pal=IXALI_FIST,
                arms=((2, 6), (18, 22)), arm_rows=(27, 31), neck=21,
                hand_clear=[(3, 7, 32, 35), (19, 22, 32, 35), (5, 5, 36, 36)]),
        1: dict(hip=40, legs=((3, 10), (11, 19)), hands=None,
                fists=((3, 32), (16, 32)), face=False, fist_pal=IXALI_FIST,
                arms=((0, 4), (17, 21)), arm_rows=(27, 31), neck=21,
                hand_clear=[(0, 4, 32, 35), (18, 21, 32, 35), (3, 3, 36, 36), (19, 19, 36, 36)]),
    },
    "maren": {
        # lab coat to row 38, legs from 39. Her long hair falls over her shoulders and down
        # her sleeves, so the sleeves stay put; her hands become fists at the coat's sides.
        0: dict(hip=39, legs=((6, 12), (13, 19)), hands=None,
                fists=((4, 32), (17, 32)), face=True, fist_pal=MAREN_FIST,
                arms=None, neck=20, fix=[maren_hands_to_coat]),
        # from behind her hands show at the coat's sides, below her hair
        1: dict(hip=39, legs=((4, 10), (11, 18)), hands=None,
                fists=((2, 32), (17, 32)), face=False, fist_pal=MAREN_FIST,
                arms=None, neck=20, fix=[maren_hands_to_coat]),
    },
    "maren_weekend": {
        # red top and long trousers: the legs run from row 32 (a seam down the middle), the
        # bare forearms hang beside the top and end in fists
        0: dict(hip=32, legs=((5, 11), (12, 19)), hands=None,
                fists=((5, 30), (15, 30)), face=True, fist_pal=MAREN_FIST,
                arms=((3, 7), (16, 20)), arm_rows=(25, 29), neck=20,
                hand_clear=[(3, 6, 30, 32), (17, 20, 30, 32)]),
        1: dict(hip=32, legs=((5, 11), (12, 18)), hands=None,
                fists=((4, 30), (15, 30)), face=False, fist_pal=MAREN_FIST,
                arms=((2, 6), (17, 20)), arm_rows=(25, 29), neck=20,
                hand_clear=[(3, 5, 30, 32), (18, 20, 30, 32)]),
    },
    "maren_winter": {
        # teal coat to row 38, legs from 39; her hair lies over the coat's shoulders, so the
        # sleeves stay put and only the hands (fists) move
        0: dict(hip=39, legs=((5, 10), (11, 17)), hands=None,
                fists=((4, 28), (17, 28)), face=True, fist_pal=MAREN_FIST,
                arms=None, neck=20, fix=[maren_winter_hands_to_coat]),
        1: dict(hip=39, legs=((5, 10), (11, 17)), hands=None,
                fists=((3, 28), (17, 28)), face=False, fist_pal=MAREN_FIST,
                arms=None, neck=20, fix=[maren_winter_hands_to_coat]),
    },
    "quill": {
        # lab coat to row 37, legs from 38; green hands become fists
        0: dict(hip=38, legs=((5, 11), (12, 18)), hands=None,
                fists=((4, 33), (16, 33)), face=True, fist_pal=QUILL_FIST,
                arms=((2, 7), (16, 20)), arm_rows=(28, 32), neck=20,
                hand_clear=[(2, 6, 33, 35), (17, 20, 32, 35)], fix=[quill_legs_front],
                fill_cleared=True),
        1: dict(hip=38, legs=((5, 12), (12, 19)), hands=None,
                fists=((4, 32), (16, 32)), face=False, fist_pal=QUILL_FIST,
                arms=((3, 7), (16, 20)), arm_rows=(28, 31), neck=20,
                hand_clear=[(3, 7, 32, 35), (17, 20, 32, 35)], fix=[quill_legs_back],
                fill_cleared=True),
    },
    "owen": {
        # jacket to row 37, legs part from row 41 in front (43 behind); hands become fists
        0: dict(hip=41, legs=((4, 11), (12, 20)), hands=None,
                fists=((3, 34), (17, 34)), face=True, fist_pal=OWEN_FIST,
                arms=((1, 6), (17, 22)), arm_rows=(28, 33), neck=21,
                hand_clear=[(2, 5, 34, 36), (18, 21, 34, 36), (19, 19, 44, 44)], fill_cleared=True,
                after_clear=[owen_jacket_taper], fix=[owen_right_leg], short_legs=True,
                refill_sleeve=True),
        1: dict(hip=43, legs=((4, 10), (11, 19)), hands=None,
                fists=((3, 34), (17, 34)), face=False, fist_pal=OWEN_FIST,
                arms=((1, 6), (17, 22)), arm_rows=(28, 33), neck=21,
                hand_clear=[(2, 5, 34, 36), (18, 21, 34, 36)], fill_cleared=True,
                after_clear=[owen_jacket_taper], short_legs=True, refill_sleeve=True),
    },
    "jasper": {
        # chef's coat to row 36 (hem outline 37), legs from 38; paws become simple fists
        0: dict(hip=38, legs=((5, 10), (12, 17)), hands=None,
                fists=((4, 34), (15, 34)), face=True, fist_pal=JASPER_FIST,
                arms=((1, 5), (17, 21)), arm_rows=(28, 33), neck=23,
                hand_clear=[(1, 5, 34, 36), (17, 21, 34, 36)],
                clear=[(11, 38, 38)]),
        # the tail hangs over the legs: it stays with the body, and the legs (hidden behind
        # it) are the front view's trousers and boots
        1: dict(hip=38, legs=((5, 10), (13, 18)), hands=None,
                fists=((4, 34), (15, 34)), face=False, fist_pal=JASPER_FIST,
                arms=((1, 5), (17, 21)), arm_rows=(28, 33), neck=22,
                hand_clear=[(1, 5, 34, 36), (17, 21, 34, 36)],
                keep=[(38, 8, 15), (39, 8, 15), (40, 8, 15), (41, 9, 13), (42, 10, 12)],
                legs_from=dict(facing=0, map=[((5, 10), (5, 10)), ((12, 17), (13, 18))])),
    },
}


# A simple fist, 4 wide by 3 tall, at the cuff of each sleeve, overlapping the coat edge by
# a couple of pixels. M outline, h highlight, s skin, l skin shade.
FIST_PAL = {"M": (0x38, 0x1f, 0x2a), "h": (0xee, 0xd8, 0xe3), "s": (0xdb, 0xb1, 0xca),
            "l": (0xbf, 0x8d, 0xc1)}
FIST_FRONT = ["MhsM", "MslM", ".MM."]
FIST_BACK = ["MssM", "MllM", ".MM."]


def fist_piece(x, y, face, pal=None):
    pal = pal or FIST_PAL
    piece = np.zeros((FH, FW, 4), np.uint8)
    for j, line in enumerate(FIST_FRONT if face else FIST_BACK):
        for i, ch in enumerate(line):
            if ch != "." and 0 <= y + j < FH and 0 <= x + i < FW:
                piece[y + j, x + i, :3] = pal[ch]
                piece[y + j, x + i, 3] = 255
    return piece


def arm_piece(cell, cols, rows, change):
    """The lower sleeve between the elbow and the cuff. change -1 drops its second row (the
    cuff rises a pixel), +1 repeats it (the cuff drops a pixel)."""
    x0, x1 = cols
    y0, y1 = rows
    src = list(range(y0, y1 + 1))
    if change < 0:
        src = src[:1] + src[1 - change:]
    elif change > 0:
        src = src[:2] + [src[1]] * change + src[2:]
    piece = np.zeros_like(cell)
    for i, sy in enumerate(src):
        piece[y0 + i, x0:x1 + 1] = cell[sy, x0:x1 + 1]
    return piece


def head_up(c, neck):
    """Lift the head (rows above 'neck') one pixel; the neck row stretches to fill."""
    out = c.copy()
    out[0:neck - 1] = c[1:neck]
    out[neck - 1] = c[neck]
    return out


PATCH_PAL = {"B": (0x53, 0x31, 0x3f), "D": (0x4b, 0x27, 0x37), "E": (0x34, 0x17, 0x26),
             "F": (0x2d, 0x0e, 0x20), "G": (0x6d, 0x42, 0x50), "H": (0x76, 0x4d, 0x5d)}


def apply_patch(cell, patch):
    for x, y, line in patch:
        for i, ch in enumerate(line):
            if ch == " ":
                continue
            if ch == ".":
                cell[y, x + i] = 0
            else:
                cell[y, x + i, :3] = PATCH_PAL[ch]
                cell[y, x + i, 3] = 255


def darken(c, k=DARK):
    o = c.copy(); m = o[:, :, 3] > 0
    o[m, :3] = np.round(o[m, :3] * k).astype(o.dtype)
    return o


def over(dst, src):
    m = src[:, :, 3] > 0
    dst[m] = src[m]


def shorten(cell, sh):
    out = cell.copy()
    a, b = sh["rows"]
    c0, c1 = sh["cols"]
    band = cell[a:b + 1, c0:c1 + 1].copy()
    t = sh["to"]
    out[t:t + len(band), c0:c1 + 1] = band
    leg = cell[sh["leg_row"], c0:c1 + 1].copy()
    for y in range(t + len(band), sh["leg_row"]):
        out[y, c0:c1 + 1] = leg
    return out


def leg_piece(cell, hip, cols, raise_by, dy, short=False):
    """One leg from the hip to the sole, fitted between row hip+dy and row 45-raise_by by
    dropping rows from the middle of the shin; the foot (bottom three rows) keeps its shape.
    A leg too short for that (feet under a long robe) loses its shin first, then the top of
    its foot."""
    x0, x1 = cols
    src_rows = list(range(hip, 46))
    foot = src_rows[-3:]
    shin = src_rows[:-3]
    top, bottom = hip + dy, 45 - raise_by
    n_shin = (bottom - 2) - top
    keep = [shin[min(len(shin) - 1, int(round(i * (len(shin) - 1) / max(1, n_shin - 1))))] for i in range(max(1, n_shin))] if shin else []
    rows = keep + foot
    if top + len(rows) - 1 > (bottom if short else 45):
        # too short to fit (feet under a long robe): the shin goes first, then the foot's top
        avail = bottom - top + 1
        rows = foot[len(foot) - max(1, avail):]
        top = bottom - len(rows) + 1
    piece = np.zeros_like(cell)
    for i, sy in enumerate(rows):
        y = top + i
        if 0 <= y < FH:
            piece[y, x0:x1 + 1] = cell[sy, x0:x1 + 1]
    return piece


def hand_piece(cell, box, change):
    """A hand with change > 0 hangs lower (its top row repeated), change < 0 sits higher
    (its second row dropped)."""
    x0, x1, y0, y1 = box
    rows = list(range(y0, y1 + 1))
    if change > 0:
        rows = [rows[0]] * change + rows
    elif change < 0:
        rows = rows[:1] + rows[1 - change:]
    piece = np.zeros_like(cell)
    for i, sy in enumerate(rows):
        piece[y0 + i, x0:x1 + 1] = cell[sy, x0:x1 + 1]
    return piece


def shift_down(c, dy):
    out = np.zeros_like(c)
    if dy:
        out[dy:] = c[:FH - dy]
    else:
        out[:] = c
    return out


def build(cell, cfg, row, facing, name=None):
    """Stardew-style front and back walk.
    Bob: on the contact frames the whole body drops a pixel; on the passing frames (feet
    together) the head rises a pixel, so the head travels two pixels and the body one.
    Arms, on the contact frames: both fists tuck one pixel in toward the body. Facing the
    camera, the arm swinging forward (toward us) hangs a pixel longer and the one swinging
    back a pixel shorter. Walking away it is the other way round, and the forward hand is
    in front of her, so it is hidden behind the body."""
    hip = cfg["hip"]
    (lx0, lx1), (rx0, rx1) = cfg["legs"]
    dy = 1 if row in (1, 2) else 0
    legs_cell = cfg.get("_legs", cell)
    body = cell.copy()
    body[hip:] = 0
    for (y, x0, x1) in cfg.get("keep", []):      # a tail hanging over the legs stays on the body
        body[y, x0:x1 + 1] = cell[y, x0:x1 + 1]
    out = np.zeros_like(cell)
    left_steps = row in (1, 3)
    if row in (1, 2):
        step_raise, trail_raise = (1, 0) if facing == 1 else (0, 1)
    else:
        step_raise, trail_raise = 0, 2
    short = cfg.get("short_legs", False)
    L = leg_piece(legs_cell, hip, (lx0, lx1), step_raise if left_steps else trail_raise, dy, short)
    R = leg_piece(legs_cell, hip, (rx0, rx1), trail_raise if left_steps else step_raise, dy, short)
    trailing, stepping = (R, L) if left_steps else (L, R)
    over(out, darken(trailing) if row in (1, 2) else trailing)
    over(out, stepping)
    # the arm opposite the stepping leg swings forward
    change = [0, 0]   # cuff and fist, pixels down
    tuck = [0, 0]     # fist, pixels in toward the body
    hidden = [False, False]
    if row in (1, 2):
        fwd = 1 if row == 1 else 0
        back = 1 - fwd
        tuck = [1, 1]
        if cfg["face"]:
            change[fwd], change[back] = 1, -1
        else:
            change[fwd], change[back] = -1, 1
            hidden[fwd] = True
    arms = cfg.get("arms")          # None: long sleeves that stay put (only the hands move)
    y0, y1 = cfg.get("arm_rows", (0, 0))
    sleeves = []
    for side in (0, 1):
        if change[side] and arms:
            x0, x1 = arms[side]
            body[y0:y1 + 1, x0:x1 + 1] = 0
            if change[side] < 0 and cfg.get("refill_sleeve"):
                # the shortened sleeve leaves its last row: the clothes below carry up into it
                body[y1, x0:x1 + 1] = cell[y1 + 1, x0:x1 + 1]
            sleeves.append(arm_piece(cell, arms[side], (y0, y1), change[side]))
    if row in (3, 4):
        body = head_up(body, cfg["neck"])
    over(out, shift_down(body, dy))
    for p in sleeves:
        over(out, shift_down(p, dy))
    for side in (0, 1):
        if hidden[side] or not cfg.get("fists"):
            continue
        fx, fy = cfg["fists"][side]
        fx += tuck[side] if side == 0 else -tuck[side]
        over(out, fist_piece(fx, fy + change[side] + dy, cfg["face"], cfg.get("fist_pal")))
    return out


if __name__ == "__main__":
    SRC, OUT = sys.argv[1], sys.argv[2]
    os.makedirs(OUT, exist_ok=True)
    for name in sys.argv[3:]:
        a = np.array(Image.open(os.path.join(SRC, f"npc_{name}.png")).convert("RGBA"))
        done = {}
        bare = np.zeros((FH, 2 * FW, 4), np.uint8)   # standing front and back without the fists
        for facing, cfg in CAST[name].items():
            stand = a[0:FH, facing * FW:(facing + 1) * FW].copy()
            if "shorten" in cfg:
                stand = shorten(stand, cfg["shorten"])
                a[0:FH, facing * FW:(facing + 1) * FW] = stand
            for (x, y0, y1) in cfg.get("clear", []):
                stand[y0:y1 + 1, x] = 0
            apply_patch(stand, cfg.get("patch", []))
            for f in cfg.get("fix", []):
                f(stand)
            for (x0, x1, y0, y1) in cfg.get("hand_clear", []):
                stand[y0:y1 + 1, x0:x1 + 1] = 0
            for f in cfg.get("after_clear", []):
                f(stand)
            if cfg.get("fill_cleared"):
                # what was behind the hands (the coat's sides) is carried up from the row
                # below each cleared box, so a moving fist uncovers coat, not a gap
                for (x0, x1, y0, y1) in cfg.get("hand_clear", []):
                    below = stand[y1 + 1].copy()
                    for y in range(y0, y1 + 1):
                        for x in range(x0, x1 + 1):
                            if below[x, 3] and not stand[y, x, 3]:
                                stand[y, x] = below[x]
            if "legs_from" in cfg:
                # the legs here are hidden behind a tail; they are taken from another view
                # (the same trousers and boots) so they can move without dragging tail pixels
                lf = cfg["legs_from"]
                other = done[lf["facing"]]
                legs = np.zeros_like(stand)
                for (sx0, sx1), (dx0, dx1) in lf["map"]:
                    legs[cfg["hip"]:, dx0:dx1 + 1] = other[cfg["hip"]:, sx0:sx1 + 1]
                body = stand.copy()
                body[cfg["hip"]:] = 0
                for (y, x0, x1) in cfg.get("keep", []):
                    body[y, x0:x1 + 1] = stand[y, x0:x1 + 1]
                stand = legs.copy()
                over(stand, body)
                cfg["_legs"] = legs
            done[facing] = stand.copy()
            bare[:, facing * FW:(facing + 1) * FW] = stand
            shown = stand.copy()
            if cfg.get("fists"):
                for (fx, fy) in cfg["fists"]:
                    over(shown, fist_piece(fx, fy, cfg["face"], cfg.get("fist_pal")))
            a[0:FH, facing * FW:(facing + 1) * FW] = shown
            for row in (1, 2, 3, 4):
                a[row * FH:(row + 1) * FH, facing * FW:(facing + 1) * FW] = build(stand, cfg, row, facing, name)
        Image.fromarray(a).save(os.path.join(OUT, f"npc_{name}.png"))
        Image.fromarray(bare).save(os.path.join(OUT, f"npc_{name}_bare.png"))
        print(name, "ok")
