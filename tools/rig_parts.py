"""Cut a resident's side view into rig parts: the body without its near arm, and the arm.

Usage: python3 -I rig_parts.py SRC_ART_DIR OUT_RIG_DIR name ...

Writes OUT_RIG_DIR/npc_<id>_side.png, 48 x 48: the left cell is the body (head, torso, tail,
legs) facing left with the hidden part of the torso painted in, the right cell is the near
arm at rest, in the same registration. Also writes npc_<id>_side.txt with the shoulder pivot
and the hip row. The walk builder (rig_walk.py) turns these into the side walk rows.
"""
import sys, os
import numpy as np
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
FW, FH, LEFT = 24, 48, 2


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], dtype=np.uint8)


def paint(cell, top, left, rows, pal):
    """Paint ascii rows into cell; '.' leaves a pixel alone, ' ' clears it."""
    for j, line in enumerate(rows):
        for i, ch in enumerate(line):
            y, x = top + j, left + i
            if ch == ".":
                continue
            if ch == " ":
                cell[y, x] = 0
            else:
                cell[y, x] = hexc(pal[ch])


RIGS = {}

# Evarra: an olive sleeve from the shoulder down the back of her coat, a lilac hand.
# The arm is lifted out as painted; the coat behind it is filled with its own cream,
# shading to the back edge.
RIGS["evarra"] = dict(
    pivot=(12, 24), hand_top=31, hip=37,
    # her coat ends three rows higher: its bottom band, hem and hem shadow move up to rows 34-36 and
    # her trousers continue up to meet it
    shorten=dict(hem_from=(37, 39), hem_to=34, leg_row=40, leg_rows=(37, 39)),
    # her olive vest stays on the body; only the lilac forearm and hand are lifted out
    arm_rows={31: (11, 15), 32: (11, 15), 33: (11, 16), 34: (11, 16), 35: (11, 16), 36: (11, 14)},
    body_top=31, body_left=10,
    body_patch=[
        ".nnoVD ",     # 31  x10..
        ".nnoVD ",     # 32
        ".nnoVD ",     # 33
        ".nnoVD ",     # 34
        ".nnoVD ",     # 35
        ".nnoV",       # 36
    ],
    # a narrow olive sleeve from the shoulder joins the lifted forearm
    sleeve_top=23, sleeve_left=11,
    sleeve=[
        " DD ",        # 23 shoulder cap
        "DkJD",        # 24
        "DkJD",        # 25
        "DkJD",        # 26
        "DkJD",        # 27
        "DkJD",        # 28
        "DkJD",        # 29
        "DJJD",        # 30 cuff
    ],
    pal={"n": "#f6d7bb", "o": "#eec7c0", "V": "#b89ba5", "D": "#381f2a",
         "k": "#928a71", "J": "#716a5a"},
)

# Jasper: his near arm is painted down the front of his shirt. It is repainted as plain shirt
# and a sleeve with an orange paw is drawn in its place.
RIGS["jasper"] = dict(
    pivot=(10, 25), hand_top=33, hip=37,
    arm_rows={},
    # his own arm runs down the front of the shirt to a paw over the belly: both are
    # repainted as plain shirt, and the drawn arm hangs a little further back
    body_top=29, body_left=6,
    body_patch=[
        "SSSSkkXl",    # 29 x6..
        "SSSSkkXl",    # 30
        "SSSSkkXl",    # 31
        "SSSSkkXl",    # 32
        "SSSSkkXlX",   # 33
        "SSkkkkXlX",   # 34
        "SSkkkkXlX",   # 35
    ],
    arm_top=25, arm_left=8,
    arm=[
        " ddd ",       # 25 shoulder cap
        "dSkld",       # 26
        "dSkld",       # 27
        "dSkld",       # 28
        "dSkld",       # 29
        "dSkld",       # 30
        "dkkld",       # 31 cuff
        "dllld",       # 32
        "dTTMd",       # 33 paw
        "dTTMd",       # 34
        " ddd ",       # 35
    ],
    pal={"S": "#fde1bd", "k": "#e8c4a2", "l": "#a38672", "X": "#cdab8e", "d": "#401a21",
         "T": "#ee7c39", "M": "#ac552f"},
)

# Rusk: his near arm hangs down the middle of his side (white rolled sleeve, orange paw on the
# apron). The shirt and apron behind it are repainted plain, and a sleeve with a rolled cuff
# and a furred forearm is drawn in its place.
RIGS["rusk"] = dict(
    pivot=(12, 23), hand_top=31, hip=40,
    arm_rows={},
    body_top=23, body_left=9,
    body_patch=[
        "TEEESB",      # 23 x9..
        "TEEESB",      # 24
        "TEEESB",      # 25
        "TEEESB",      # 26
        "SBBBBB",      # 27 shirt fold
        "SEEEED",      # 28
        "SDTEEE",      # 29
        "........",    # 30 apron top band kept
        "XaaXMV",      # 31
        "XaaXMV",      # 32
        "XLaXMV",      # 33
        "XaaXMV",      # 34
    ],
    arm_top=22, arm_left=10,
    arm=[
        " YYY ",       # 22 shoulder cap
        "YSSBY",       # 23 sleeve a shade darker than the shirt so it reads against it
        "YSSBY",
        "YSSBY",
        "YSSBY",
        "YSSBY",
        "YBBJY",       # 28 rolled cuff
        "YJJJY",       # 29
        "YefcY",       # 30 forearm fur
        "YefcY",       # 31
        "YefcY",       # 32 paw
        "YggcY",       # 33
        " YYY ",       # 34
    ],
    pal={"T": "#fce7c0", "E": "#f6d3ad", "S": "#ddbd9d", "B": "#a57a62", "D": "#f3c39d",
         "J": "#7d6053", "X": "#5a2c29", "a": "#753d32", "L": "#7d4134", "M": "#61312c",
         "V": "#472425", "Y": "#2a1219", "e": "#e67543", "f": "#dd6d3e", "g": "#cf643b",
         "c": "#c65933"},
)

# Ooma: a wide robe sleeve from the shoulder, a gold cuff and a pink tentacle hand over the
# robe's middle. The hand is painted back to robe and a sleeve is drawn in its place.
RIGS["ooma"] = dict(
    pivot=(12, 25), hand_top=32, hip=42,
    arm_rows={},
    body_top=32, body_left=10,
    body_patch=[
        "RUUWL",       # 32 x10..
        "RUUWL",       # 33
        "RUUWL",       # 34
        "RUUWL",       # 35
        "RUUWL",       # 36
    ],
    arm_top=25, arm_left=10,
    arm=[
        " OOO ",       # 25 shoulder
        "OUWRO",       # 26
        "OUWRO",       # 27
        "OUWRO",       # 28
        "OUWRO",       # 29
        "OUWRO",       # 30
        "OeYeO",       # 31 gold cuff
        "OCJCO",       # 32 tentacle hand
        "OCCJO",       # 33
        " OOO ",       # 34
    ],
    pal={"R": "#4d3150", "U": "#59385d", "W": "#56375b", "L": "#422844", "O": "#2f1b29",
         "e": "#dfb263", "Y": "#d69550", "C": "#b86d70", "J": "#a95a64"},
)

# Tobbin: a big puffed shirt sleeve over his side with a tan hand below it. The overalls
# behind are repainted plain and a sleeve and hand are drawn in its place.
RIGS["tobbin"] = dict(
    pivot=(14, 29), hand_top=35, hip=42,
    arm_rows={},
    body_top=29, body_left=11,
    body_patch=[
        "UUUeUUUQ",    # 29 x11..
        "UUUeUUUQ",    # 30
        "UUUeUUUQ",    # 31
        "UUUeUUUQ",    # 32
        "UUUeUUUQ",    # 33
        "UUUeUUUQ",    # 34
        "UUUeUUUQ",    # 35
        "UUUeUUUQ",    # 36
        "UUUeUUQ",     # 37
        "UUUeUQ",      # 38
    ],
    arm_top=28, arm_left=11,
    arm=[
        " NNNN ",      # 28 shoulder
        "NXXCCN",      # 29 puffed sleeve
        "NXCCSN",      # 30
        "NXCCSN",      # 31
        "NXCSSN",      # 32
        "NCSSRN",      # 33
        " NNNN ",      # 34 cuff
        " NDLN ",      # 35 hand
        " NLKN ",      # 36
        "  NN  ",      # 37
    ],
    pal={"U": "#893f29", "e": "#974c2d", "Q": "#6f3323", "N": "#361f1d", "X": "#fbe1b4",
         "C": "#ebc287", "S": "#a08053", "R": "#785132", "D": "#e9ac58", "L": "#c88b42",
         "K": "#a06f3c"},
)

# Merrow: a short cream sleeve and a long green forearm down the middle of his side. The
# shirt and overalls behind are repainted and the arm is drawn as its own piece.
RIGS["merrow"] = dict(
    pivot=(14, 24), hand_top=34, hip=39,
    arm_rows={},
    body_top=25, body_left=12,
    body_patch=[
        "TRRRUY",      # 25 x12.. shirt
        "TRRRUY",      # 26
        "TRRRUY",      # 27
        "TRRRUY",      # 28
        "TRRRUY",      # 29
        "TRRRUY",      # 30
        "TRRRUY",      # 31
        "PbPWPY",      # 32 overalls
        "PbPWPY",      # 33
        "PbPWPY",      # 34
        "PbPWPY",      # 35
        "PbPWPY",      # 36
        "PbPWPY",      # 37
        "PbPWPY",      # 38
    ],
    arm_top=24, arm_left=12,
    arm=[
        " cccc ",      # 24 shoulder
        "cRRUVc",      # 25 short sleeve
        "cRRUVc",      # 26
        "cRRUVc",      # 27
        "cRRUVc",      # 28
        "cRRUVc",      # 29
        "cVVVVc",      # 30 cuff
        " cEEGc",      # 31 forearm
        " cEEGc",      # 32
        " cEdGc",      # 33
        " cEdGc",      # 34
        " cEGGc",      # 35 hand
        " cEGGc",      # 36
        "  ccc ",      # 37
    ],
    pal={"T": "#c7cea2", "R": "#f6edc7", "U": "#bfbe8e", "Y": "#2f3943", "P": "#304551",
         "b": "#33505f", "W": "#375461", "c": "#342629", "V": "#949a7b", "E": "#94bb9a",
         "G": "#698b7a", "d": "#80a289"},
)

# Nub: a little sleeve and a pale hand at the middle of his side, drawn as its own piece; the
# shirt behind is repainted.
RIGS["nub"] = dict(
    pivot=(12, 33), hand_top=38, hip=42,
    arm_rows={},
    body_top=34, body_left=10,
    body_patch=[
        "LLELJ",       # 34 x10..
        "LLELJ",       # 35
        "LLELJ",       # 36
        "LLELJ",       # 37
        "LLELJ",       # 38
        "LLELJ",       # 39
    ],
    arm_top=33, arm_left=10,
    arm=[
        " NNN ",       # 33 shoulder
        "NPLEN",       # 34
        "NPLEN",       # 35
        "NPLEN",       # 36
        "NEEJN",       # 37 cuff
        "NWFZN",       # 38 hand
        "NFFZN",       # 39
        " NNN ",       # 40
    ],
    pal={"L": "#6d662f", "E": "#665d2e", "J": "#5e572c", "N": "#26101a", "P": "#938d41",
         "W": "#e1d981", "F": "#cec75f", "Z": "#a79640"},
)

# Garrick: a navy uniform sleeve down the middle of his side with the hand over his belt.
# The hand and belt area behind it are repainted as coat, and the arm is drawn on its own.
RIGS["garrick"] = dict(
    pivot=(11, 20), hand_top=33, hip=37,
    arm_rows={},
    body_top=29, body_left=9,
    body_patch=[
        "VRRVOe",      # 29 x9..
        "VRRVOe",      # 30
        "VRRVOe",      # 31
        "VRRVOe",      # 32
        "VRRVOe",      # 33
        "VRRVOe",      # 34
        "VRRVOe",      # 35
    ],
    arm_top=19, arm_left=9,
    arm=[
        " ccc ",       # 19 shoulder
        "cRVOc",       # 20
        "cRVOc",       # 21
        "cRVOc",       # 22
        "cRVOc",       # 23
        "cRVOc",       # 24
        "cRVOc",       # 25
        "cRVOc",       # 26
        "cRVOc",       # 27
        "cRVOc",       # 28
        "cRVOc",       # 29
        "cRVOc",       # 30
        "cRVOc",       # 31
        "cNNNc",       # 32 cuff
        "cBXCc",       # 33 hand
        "cXXCc",       # 34
        " ccc ",       # 35
    ],
    pal={"V": "#3c2f45", "R": "#3f354b", "O": "#3f334a", "e": "#392c3e", "c": "#28192a",
         "N": "#362b41", "B": "#fbb972", "X": "#eca26a", "C": "#cf8d60"},
)

# Saffi: a green puff sleeve and a brown furred forearm with the paw over her dress. The dress
# behind the forearm is repainted, and the arm is drawn as its own piece.
RIGS["saffi"] = dict(
    pivot=(10, 23), hand_top=32, hip=42,
    arm_rows={},
    body_top=31, body_left=8,
    body_patch=[
        "OTSM",        # 31 x8..
        "OTSM",        # 32
        "OTSM",        # 33
        "OTSM",        # 34
        "OTSM",        # 35
    ],
    arm_top=23, arm_left=8,
    arm=[
        " ttt ",       # 23 shoulder
        "tOSMt",       # 24 puff sleeve
        "tOSMt",       # 25
        "tOSMt",       # 26
        "tOSMt",       # 27
        "tTTTt",       # 28 cuff
        "tCWBt",       # 29 forearm fur
        "tCWBt",       # 30
        "tCWBt",       # 31
        "tCWBt",       # 32
        "tDCWt",       # 33 paw
        " ttt ",       # 34
    ],
    pal={"O": "#595c4d", "T": "#4b4b42", "S": "#505347", "M": "#46433d", "t": "#2b0c11",
         "C": "#a77159", "W": "#985b43", "B": "#81544a", "D": "#c9a185"},
)

# Kit: a short yellow sleeve and a little furred arm at the middle of his side; the shirt and
# shorts behind are repainted and the arm is drawn as its own piece.
RIGS["kit"] = dict(
    pivot=(12, 32), hand_top=36, hip=42,
    arm_rows={},
    body_top=34, body_left=11,
    body_patch=[
        "lmmE",        # 34 x11..
        "lmmE",        # 35
        "lmmE",        # 36
        "VBEV",        # 37 shorts
    ],
    arm_top=32, arm_left=10,
    arm=[
        " kkk ",       # 32 shoulder
        "klmmk",       # 33 short sleeve
        "kmmEk",       # 34
        "kGFEk",       # 35 forearm fur
        "kFGEk",       # 36
        "kPFGk",       # 37 paw
        " kkk ",       # 38
    ],
    pal={"l": "#f7b148", "m": "#e99f3e", "E": "#8f5038", "V": "#492324", "B": "#6f3c30",
         "k": "#2c0a0f", "G": "#a25d3d", "F": "#ae6741", "P": "#bd8a62"},
)

# Ix'ali: a tunic sleeve down the middle of her side and a gold hand beside her tail. The
# hand is repainted as tunic and a sleeve and hand are drawn on their own.
RIGS["ixali"] = dict(
    pivot=(11, 22), hand_top=32, hip=40,
    arm_rows={},
    body_top=32, body_left=10,
    body_patch=[
        "RbZS",        # 32 x10..
        "RbZS",        # 33
        "RbZS",        # 34
        "RbZS",        # 35
    ],
    arm_top=22, arm_left=9,
    arm=[
        " PPP ",       # 22 shoulder
        "PRbZP",       # 23
        "PRbZP",       # 24
        "PRbZP",       # 25
        "PRbZP",       # 26
        "PRbZP",       # 27
        "PRbZP",       # 28
        "PRbZP",       # 29
        "PRbZP",       # 30
        "PSSSP",       # 31 cuff
        "PdeCP",       # 32 hand
        "PdeCP",       # 33
        " PPP ",       # 34
    ],
    pal={"R": "#8c4937", "b": "#9a4f39", "Z": "#723b32", "S": "#4c2628", "P": "#2c111b",
         "d": "#ddb74e", "e": "#cdaa49", "C": "#b79543"},
)

# Maren (lab coat): a white coat sleeve from the shoulder with her hand at the cuff; the hand
# is repainted as coat and the sleeve is drawn on its own.
RIGS["maren"] = dict(
    pivot=(11, 24), hand_top=35, hip=39,
    arm_rows={},
    body_top=35, body_left=9,
    body_patch=[
        "WeW",         # 35 x9..
        "WeW",         # 36
    ],
    arm_top=24, arm_left=9,
    arm=[
        " MMM ",       # 24 shoulder
        "MeWZM",       # 25 coat sleeve
        "MeWZM",       # 26
        "MeWZM",       # 27
        "MeWZM",       # 28
        "MeWZM",       # 29
        "MeWZM",       # 30
        "MeWZM",       # 31
        "MeWZM",       # 32
        "MeWZM",       # 33
        "MZZZM",       # 34 cuff
        "MDCBM",       # 35 hand
        " MMM ",       # 36
    ],
    pal={"W": "#e9c2a8", "e": "#fdf3d5", "Z": "#c3a7a1", "M": "#44222b", "D": "#e5b399",
         "C": "#e0a686", "B": "#ad796f"},
)

# Maren's weekend clothes: a short red sleeve and a bare forearm; the top behind it is
# repainted and the arm is drawn on its own.
RIGS["maren_weekend"] = dict(
    pivot=(12, 24), hand_top=30, hip=34,
    arm_rows={},
    body_top=26, body_left=10,
    body_patch=[
        "VQPQD",       # 26 x10..
        "VQPQD",       # 27
        "VQPQD",       # 28
        "VQPQD",       # 29
        "VQPQD",       # 30
        "VQPQD",       # 31
        "VQPQD",       # 32
        "VQPQD",       # 33
    ],
    arm_top=24, arm_left=10,
    arm=[
        " OOO ",       # 24 shoulder
        "OVQDO",       # 25 short sleeve
        "OVQDO",       # 26
        "OfeeO",       # 27 forearm
        "OfehO",       # 28
        "OfegO",       # 29
        "OfegO",       # 30 hand
        "OhegO",       # 31
        " OOO ",       # 32
    ],
    pal={"V": "#6c2c37", "Q": "#78313e", "P": "#7e3540", "D": "#57282e", "O": "#4b2023",
         "f": "#f9ca93", "e": "#e9b795", "h": "#dca991", "g": "#c19189"},
)

# Maren's winter coat: a teal coat sleeve with her hand at the cuff.
RIGS["maren_winter"] = dict(
    pivot=(11, 23), hand_top=30, hip=39,
    arm_rows={},
    body_top=30, body_left=9,
    body_patch=[
        "GFDFG",       # 30 x9..
        "GFHFG",       # 31
    ],
    arm_top=23, arm_left=9,
    arm=[
        " DDD ",       # 23 shoulder
        "DGFHD",       # 24 coat sleeve
        "DGFHD",       # 25
        "DGFHD",       # 26
        "DGFHD",       # 27
        "DGFHD",       # 28
        "DXXXD",       # 29 cuff
        "DcMND",       # 30 hand
        " DDD ",       # 31
    ],
    pal={"G": "#35494e", "F": "#35474a", "H": "#304549", "D": "#2d3235", "X": "#31383b",
         "c": "#f3cca2", "M": "#e9c2a8", "N": "#c8968a"},
)

# Quill: a lab-coat sleeve and a green forearm with the hand at the middle of his side; the
# coat behind is repainted and the arm is drawn as its own piece.
RIGS["quill"] = dict(
    pivot=(12, 24), hand_top=33, hip=38,
    arm_rows={},
    body_top=28, body_left=10,
    body_patch=[
        "QRRRK",       # 28 x10..
        "QRRRK",       # 29
        "QRRRK",       # 30
        "QRRRK",       # 31
        "QRRRK",       # 32
        "QRRRK",       # 33
        "QRRRK",       # 34
        "QRRRK",       # 35
        "QRRRK",       # 36
    ],
    arm_top=24, arm_left=10,
    arm=[
        " MMM ",       # 24 shoulder
        "MSRKM",       # 25 coat sleeve
        "MSRKM",       # 26
        "MSRKM",       # 27
        "MSRKM",       # 28
        "MDBAM",       # 29 forearm
        "MDBAM",       # 30
        "MDBAM",       # 31
        "MDBAM",       # 32
        "McDBM",       # 33 hand
        "McDBM",       # 34
        " MMM ",       # 35
    ],
    pal={"Q": "#ffe5c6", "R": "#fadcc0", "K": "#eddec5", "S": "#fff5d9", "M": "#22161e",
         "D": "#6a8579", "B": "#606d66", "A": "#485550", "c": "#a1bfae"},
)

# Owen: an orange jacket sleeve with the hand at the cuff, down his side; the jacket behind the
# hand is repainted and the arm is drawn on its own.
RIGS["owen"] = dict(
    pivot=(14, 24), hand_top=34, hip=38,
    arm_rows={},
    body_top=34, body_left=12,
    body_patch=[
        "TSSOTW",      # 34 x12..
        "TSSOTW",      # 35
    ],
    arm_top=24, arm_left=12,
    arm=[
        " CCC ",       # 24 shoulder
        "CSOTC",       # 25 jacket sleeve
        "CSOTC",       # 26
        "CSOTC",       # 27
        "CSOTC",       # 28
        "CSOTC",       # 29
        "CSOTC",       # 30
        "CSOTC",       # 31
        "CSOTC",       # 32
        "CLLLC",       # 33 cuff
        "CGdFC",       # 34 hand
        "CdFFC",       # 35
        " CCC ",       # 36
    ],
    pal={"T": "#c56d2d", "S": "#e28530", "O": "#d97d2f", "W": "#3c1b1b", "C": "#2a0e15",
         "L": "#623327", "G": "#f4c295", "d": "#eba877", "F": "#ca946f"},
)


# Pip: a red sleeve down the middle of his side to a small hand at his hip. The arm is
# repainted as tunic and shorts and a sleeve and hand are drawn on their own.
RIGS["pip"] = dict(
    pivot=(12, 30), hand_top=35, hip=40,
    arm_rows={},
    body_top=30, body_left=10,
    body_patch=[
        "IZWVU",       # 30 x10..
        "ZZWVU",       # 31 tunic
        "ZZWVa",       # 32
        "ZZWVa",       # 33
        "ZWWVa",       # 34
        "WWVVa",       # 35
        "NNNNY",       # 36 hem
        "MBBBU",       # 37 shorts
    ],
    arm_top=30, arm_left=10,
    arm=[
        " kkk ",       # 30 shoulder
        "kZWVk",       # 31 sleeve
        "kZWVk",       # 32
        "kZWVk",       # 33
        "kPPPk",       # 34 cuff
        "kdCEk",       # 35 hand
        "kCEBk",       # 36
        " kkk ",       # 37
    ],
    pal={"I": "#79312b", "Z": "#b34d3b", "W": "#a64337", "V": "#9c4235", "U": "#603227",
         "a": "#6d2a26", "N": "#622924", "Y": "#4c2924", "M": "#bf885f", "B": "#b47951",
         "k": "#2e0d10", "P": "#6f3229", "d": "#f2c194", "C": "#eca56f", "E": "#da9261"},
)

# Bram: a puffed cream shirt sleeve and a green frog hand down the middle of his side. The
# vest and trousers behind are repainted and the arm is drawn as its own piece.
RIGS["bram"] = dict(
    pivot=(14, 32), hand_top=37, hip=41,
    arm_rows={},
    body_top=32, body_left=12,
    body_patch=[
        "RQQUUV",      # 32 x12.. vest
        "QQQUUV",      # 33
        "QQQUUV",      # 34
        "UQQUVV",      # 35
        "UQQUVV",      # 36
        "QQUUUU",      # 37 vest hem
        "OOOZOO",      # 38 trousers
        "OZZOOS",      # 39
        "ZOOOZS",      # 40
    ],
    arm_top=32, arm_left=12,
    arm=[
        " NNNN ",      # 32 shoulder
        "NYYYEN",      # 33 puffed sleeve
        "NYDDYN",      # 34
        "NEEEEN",      # 35
        "NYYYYN",      # 36
        "NMMMIN",      # 37 wrist
        "NWaWbN",      # 38 green hand
        "NCFFHN",      # 39
        " NNNN ",      # 40
    ],
    pal={"N": "#2f1419", "Y": "#f8e9bc", "E": "#d9cd83", "D": "#d5bb60", "M": "#5d5733",
         "I": "#564830", "W": "#a6aa4d", "a": "#a1a54b", "b": "#8c9049", "C": "#7d7649",
         "F": "#b1b852", "H": "#6d643e", "Q": "#d0923b", "U": "#b77b2f", "V": "#9a662d",
         "R": "#d5ab48", "O": "#7c4e2b", "Z": "#764027", "S": "#593726"},
)

# Freya: a bare arm with a leather bracer down the middle of her side. The top and the baggy
# trousers behind are repainted and the arm is drawn as its own piece.
RIGS["freya"] = dict(
    pivot=(11, 22), hand_top=31, hip=40,
    arm_rows={},
    body_top=22, body_left=10,
    body_patch=[
        "LIHA",        # 22 x10.. the top
        "LIHA",        # 23
        "LIHA",        # 24
        "LIHA",        # 25
        "LIHA",        # 26
        "AFFB",        # 27 belt
        "EEFA",        # 28 trousers
        "EEFA",        # 29
        "EEFA",        # 30
        "EEEF",        # 31
        "EEEF",        # 32
        "EEFF",        # 33
    ],
    arm_top=21, arm_left=10,
    arm=[
        " AA ",        # 21 shoulder
        "AMMA",        # 22 bare arm
        "AMMA",        # 23
        "AMJA",        # 24
        "AMJA",        # 25
        "AMJA",        # 26
        "AMMA",        # 27
        "AEEA",        # 28 bracer
        "AFFA",        # 29
        "AFFA",        # 30
        "AMMA",        # 31 hand
        "AMJA",        # 32
        " AA ",        # 33
    ],
    pal={"A": "#5e3430", "M": "#f2c29a", "J": "#d9926e", "E": "#86593f", "F": "#6b3a2c",
         "L": "#e8d9bd", "I": "#c9b8a6", "H": "#b08158", "B": "#5a3a22"},
)

# Job: a chunky orange shirt sleeve and a bare forearm and hand down the middle of his side.
# The shirt and overalls behind are repainted and the arm is drawn as its own piece.
RIGS["job"] = dict(
    pivot=(15, 22), hand_top=33, hip=40,
    arm_rows={},
    body_top=21, body_left=12,
    body_patch=[
        "OKKKSQR   ",  # 21 x12.. shirt; the old sleeve's edge behind is cleared
        "OKKKKSR   ",  # 22
        "NKKKKSR   ",  # 23
        "NKKKKSGR  ",  # 24
        "NKKKKSGR  ",  # 25
        "NKKKSSGR  ",  # 26
        "NNKKSSGR  ",  # 27
        "MNNSSGGR  ",  # 28
        "MMNNGGR   ",  # 29
        "WWeecWQU  ",  # 30 overalls
        "WeecWWQU  ",  # 31
        "WeecWWQU  ",  # 32
        "WeecWWQU  ",  # 33
        "WeecWWQU  ",  # 34
        "WeecWQU   ",  # 35
        "eWWWQU    ",  # 36
    ],
    arm_top=21, arm_left=12,
    arm=[
        " RRRRR  ",    # 21 shoulder
        "RKOOOKR ",    # 22 sleeve
        "RKOOOKR ",    # 23
        "RSOOKSR ",    # 24
        "RSKKKSR ",    # 25
        "RSKKKSR ",    # 26
        "RNSSSNR ",    # 27
        "RGNNNGR ",    # 28 hem
        " RRRRR  ",    # 29
        " RDCDR  ",    # 30 forearm
        " RDCDR  ",    # 31
        " RDCDR  ",    # 32
        " RDDCR  ",    # 33 hand
        " RDDBR  ",    # 34
        " RCBBR  ",    # 35
        "  RRR   ",    # 36
    ],
    pal={"R": "#2f151f", "K": "#eb7130", "O": "#fc7e31", "S": "#dd662f", "N": "#b6542d",
         "G": "#763526", "M": "#643027", "Q": "#473039", "W": "#533c4b", "e": "#5d4652",
         "c": "#4b3546", "U": "#2e1a25", "D": "#b66037", "C": "#a14f2e", "B": "#864029"},
)

# Zaas: a thin teal arm with a tentacled hand down the middle of the side. The brown vest
# behind is repainted and the arm is drawn as its own piece.
RIGS["zaas"] = dict(
    pivot=(13, 31), hand_top=35, hip=40,
    arm_rows={},
    body_top=31, body_left=11,
    body_patch=[
        "XTVbKR",      # 31 x11.. vest
        "TZVbR.",      # 32
        "TZVbU.",      # 33
        "ZVbSbK",      # 34
        "ZVbSbb",      # 35
        "ZVbSbb",      # 36
        "VbSbbK",      # 37
        "VcSSbR",      # 38
    ],
    arm_top=31, arm_left=11,
    arm=[
        " RRR ",       # 31 shoulder
        "RDCDR",       # 32 teal arm
        "RDCYR",       # 33
        "RBCDR",       # 34
        "RBDDR",       # 35 hand
        "RCDYR",       # 36
        "RBCMR",       # 37
        " RRR ",       # 38
    ],
    pal={"R": "#251a24", "X": "#cc724c", "T": "#ab5941", "V": "#884236", "Z": "#984d3c",
         "b": "#7b4036", "c": "#8b4b3a", "S": "#67352f", "K": "#4d292a", "U": "#33141f",
         "D": "#5da395", "C": "#63ad9e", "Y": "#50978d", "B": "#4c8881", "M": "#36474d"},
)

# Tar'Besh: a wide robe sleeve with a gold cuff and a small hand, down the middle of his side.
# The robe behind the cuff and hand is repainted and the arm is drawn as its own piece.
RIGS["tarbesh"] = dict(
    pivot=(12, 23), hand_top=33, hip=42,
    arm_rows={},
    body_top=30, body_left=9,
    body_patch=[
        "YQQZTZ",      # 30 x9.. robe
        "YQQZTZ",      # 31
        "YQYZTZ",      # 32
        "YQQZTZ",      # 33
        "YQQZTZ",      # 34
        "YQYZTZ",      # 35
    ],
    arm_top=23, arm_left=9,
    arm=[
        " JJJJ ",      # 23 shoulder
        "JYQQZJ",      # 24 robe sleeve
        "JYQQZJ",      # 25
        "JYQQZJ",      # 26
        "JYQYZJ",      # 27
        "JYQQZJ",      # 28
        "JYQQZJ",      # 29
        "JBBGHJ",      # 30 gold cuff
        "JBWWGJ",      # 31
        "JJJJJJ",      # 32
        " JdeJ ",      # 33 hand
        " JfWJ ",      # 34
        " JdeJ ",      # 35
        "  JJ  ",      # 36
    ],
    pal={"J": "#2e181d", "Y": "#6a2b3f", "Q": "#712b41", "Z": "#652a3c", "T": "#62273b",
         "B": "#d2984c", "G": "#cc7e43", "H": "#8f4c3f", "W": "#d8a857", "d": "#a08346",
         "e": "#92753f", "f": "#b3944d"},
)

# Vzz'ket: below the shoulder plate, a leather upper arm, a pale bracer and a gold hand down
# the back half of his side. The tunic behind is repainted (his tail tip is left alone) and
# the arm is drawn as its own piece.
RIGS["vzzket"] = dict(
    pivot=(13, 25), hand_top=32, hip=40,
    arm_rows={},
    body_top=25, body_left=11,
    body_patch=[
        "BCDBKA",      # 25 x11.. tunic
        "BCDBKA",      # 26
        "BCDBKA",      # 27
        "BCDBKA",      # 28
        "BCDBKA",      # 29
        "BCDBKA",      # 30
        "BCDBKA",      # 31
        "BCDBKA",      # 32
        "BCDBK.",      # 33 (tail tip)
        "BCDBK.",      # 34
        "BCDBKA",      # 35
    ],
    arm_top=25, arm_left=11,
    arm=[
        " AAA ",       # 25
        "AKBBA",       # 26 leather
        "AUUaA",       # 27
        "AIHHA",       # 28 bracer
        "AGIGA",       # 29
        "AIGIA",       # 30
        "AEELA",       # 31 wrist
        "AWWVA",       # 32 gold hand
        "AddSA",       # 33
        "AWSMA",       # 34
        " AAA ",       # 35
    ],
    pal={"A": "#1e0e16", "K": "#64222a", "B": "#802931", "U": "#653139", "a": "#69403e",
         "I": "#b2866a", "H": "#c38876", "G": "#9d6d60", "E": "#35181f", "L": "#290e18",
         "W": "#a38642", "V": "#876a3d", "d": "#caa750", "S": "#b59748", "M": "#4b282b",
         "C": "#a83338", "D": "#b54441"},
)

# Artie: a maroon shirt sleeve rolled to an orange cuff, a bare forearm and hand, down the
# back half of his side. The shirt and trousers behind are repainted and the arm is drawn as
# its own piece.
RIGS["artie"] = dict(
    pivot=(14, 22), hand_top=31, hip=40,
    arm_rows={},
    body_top=22, body_left=11,
    body_patch=[
        "RRZXW  ",      # 22 x11.. shirt (the old arm's front edge at x 11 too)
        "RRZXXP ",      # 23
        "RRZXXH ",      # 24
        "RRZZXXF",      # 25
        "RRZZXXQ",      # 26
        "RRZZXXH",      # 27
        "RRZZXXH",      # 28
        "RRZZXXW",      # 29
        "ccKcJH ",      # 30 trousers
        "ccKcJW ",      # 31
        "ccKcJa ",      # 32
        "ccKcJW ",      # 33
        "ccKJM  ",      # 34
    ],
    arm_top=22, arm_left=12,
    arm=[
        " FFF ",       # 22 shoulder
        "FRRXF",       # 23 sleeve
        "FRZXF",       # 24
        "FRZXF",       # 25
        "FRZXF",       # 26
        "FVVYF",       # 27 rolled cuff
        "FVYYF",       # 28
        "FEECF",       # 29 forearm
        "FCBEF",       # 30
        "FCBCF",       # 31 hand
        "FBCEF",       # 32
        "FCBEF",       # 33
        " FFF ",       # 34
    ],
    pal={"F": "#2e151a", "R": "#913642", "Z": "#7d2e33", "X": "#672626", "W": "#421a1c",
         "P": "#36191c", "H": "#4d1d1f", "Q": "#290d12", "V": "#bf533a", "Y": "#ad4533",
         "E": "#d57b4f", "C": "#eda470", "B": "#f8bd83", "c": "#78563e", "K": "#71503b",
         "J": "#5f3d30", "a": "#401e20", "M": "#5d2827"},
)

# Stu: the round bellhop coat's sleeve and a green frog hand at the back of his side. The
# coat behind is repainted and the arm is drawn as its own piece.
RIGS["stu"] = dict(
    pivot=(15, 25), hand_top=33, hip=39,
    arm_rows={},
    body_top=26, body_left=13,
    body_patch=[
        "RSSUPV",      # 26 x13.. coat
        "RSSUPV",      # 27
        "RSSUPV",      # 28
        "RSSUPV",      # 29
        "RSSUPV",      # 30
        "RSSUPV",      # 31
        "RSSUPV",      # 32
        "RSUUPV",      # 33
        "RSUUPV",      # 34
        "RSUUPV",      # 35
        "RSUUPV",      # 36
        "OPRPE ",      # 37
    ],
    arm_top=25, arm_left=13,
    arm=[
        " VVVV ",      # 25 shoulder
        "VSSUPV",      # 26 sleeve
        "VSSUPV",      # 27
        "VSSUPV",      # 28
        "VSUUPV",      # 29
        "VSUUPV",      # 30
        "VSSUPV",      # 31
        "VQQQQV",      # 32 cuff
        "VGXXGV",      # 33 wrist
        "VYZabV",      # 34 green hand
        "VdYeZV",      # 35
        " VYFV ",      # 36
        "  VV  ",      # 37
    ],
    pal={"V": "#211016", "S": "#703846", "U": "#572c39", "R": "#61353c", "P": "#3b1d26",
         "Q": "#402328", "O": "#583633", "E": "#1b0a15", "G": "#403521", "X": "#515029",
         "Y": "#a5ab4a", "Z": "#acb34c", "a": "#c3bc5e", "b": "#919647", "d": "#6f6f38",
         "e": "#828442", "F": "#777c3a"},
)

# Ana: her pilot's jacket sleeve with a red cuff and a bare hand down the middle of her side.
# The jacket and trousers behind are repainted and the arm is drawn as its own piece.
RIGS["ana"] = dict(
    pivot=(12, 23), hand_top=32, hip=35,
    arm_rows={},
    body_top=23, body_left=10,
    body_patch=[
        "TZZJO",       # 23 x10.. jacket
        "TZZJN",       # 24
        "TZaJN",       # 25
        "TaaJN",       # 26
        "GTZJR",       # 27
        "GTZJV",       # 28
        "PTZJd",       # 29
        "ccccG",       # 30 waist
        "ddaGO",       # 31 trousers
        "ddaGA",       # 32
        "ddaGf",       # 33
    ],
    arm_top=22, arm_left=10,
    arm=[
        " KKK ",       # 22 shoulder
        "KaZJK",       # 23 sleeve
        "KaZJK",       # 24
        "KaZJK",       # 25
        "KaZJK",       # 26
        "KaZJK",       # 27
        "KaZJK",       # 28
        "KaZJK",       # 29
        "KaZJK",       # 30
        "KIIrK",       # 31 red cuff
        "KCBDK",       # 32 hand
        "KBCDK",       # 33
        " KKK ",       # 34
    ],
    pal={"K": "#2f161e", "T": "#402731", "Z": "#422a34", "a": "#452d39", "J": "#372029",
         "O": "#35161c", "N": "#351a22", "R": "#2b151d", "G": "#361e26", "V": "#3a222b",
         "P": "#331c23", "d": "#472f3c", "c": "#30181f", "A": "#562b35", "f": "#2c1119",
         "I": "#953a43", "r": "#6e2a33", "C": "#f9c59b", "B": "#e1a378", "D": "#aa7d67"},
)

# Ana in her Chernog clothes: a striped sweater sleeve (red at the shoulder, an orange cuff)
# and a bare hand down the middle of her side. The sweater behind is repainted (its red
# stripe and orange belt carried across) and the arm is drawn as its own piece.
RIGS["ana_chernog"] = dict(
    pivot=(11, 23), hand_top=31, hip=35,
    arm_rows={},
    body_top=23, body_left=9,
    body_patch=[
        "fhhgV",       # 23 x9.. sweater
        "jkkkj",       # 24 red stripe
        "ddddd",       # 25
        "fhhgg",       # 26
        "fhhgV",       # 27
        "fhhgc",       # 28
        "TSSSt",       # 29 belt
        "pfhmm",       # 30
        "mfhgc",       # 31
        "mfhgZ",       # 32
        "ifhgr",       # 33
    ],
    arm_top=22, arm_left=9,
    arm=[
        " ccc ",       # 22 shoulder
        "chfgc",       # 23 sleeve
        "ckkjc",       # 24 red stripe
        "cddjc",       # 25
        "chfgc",       # 26
        "chfgc",       # 27
        "chfgc",       # 28
        "chfgc",       # 29
        "cttTc",       # 30 orange cuff
        "cuuNc",       # 31 hand
        "cOuSc",       # 32
        " ccc ",       # 33
    ],
    pal={"c": "#281b20", "h": "#412b34", "f": "#3c2a34", "g": "#39252d", "V": "#331e22",
         "j": "#864133", "k": "#a43e3a", "d": "#6e302f", "T": "#5d3b2f", "S": "#915838",
         "t": "#72412d", "p": "#382125", "m": "#40262a", "Z": "#29171e", "i": "#3c262d",
         "r": "#301b20", "u": "#f9c78e", "O": "#d89f64", "N": "#a6744b"},
)

# S.A.R.A.'s solid body: a slim bodysuit arm and a pale hand down the middle of her side,
# below the hair that hangs down her back. The suit behind is repainted (its light belt
# carried across) and the arm is drawn as its own piece.
RIGS["sara_solid"] = dict(
    pivot=(11, 21), hand_top=31, hip=34,
    arm_rows={},
    body_top=26, body_left=9,
    body_patch=[
        "LhaCA",       # 26 x9.. suit
        "LhaCA",       # 27
        "LhaCA",       # 28
        "HGGQA",       # 29 belt
        "LhaCA",       # 30
        "LhaCA",       # 31
        "LhaCA",       # 32
        "IhaCC",       # 33
    ],
    arm_top=21, arm_left=10,
    arm=[
        " AA ",        # 21 shoulder
        "ALhA",        # 22 sleeve
        "ALhA",        # 23
        "ALhA",        # 24
        "ALhA",        # 25
        "ALhA",        # 26
        "ALhA",        # 27
        "ALhA",        # 28
        "ALhA",        # 29
        "AQQA",        # 30 cuff
        "AGPA",        # 31 hand
        "AdGA",        # 32
        " AA ",        # 33
    ],
    pal={"A": "#1d202c", "L": "#375c6a", "h": "#314d5b", "a": "#2f5463", "C": "#28323e",
         "H": "#6fbfc5", "G": "#98e2e3", "Q": "#48717c", "I": "#4996a3", "P": "#8ecfd2",
         "d": "#b5e4e4"},
)

os.makedirs(OUT, exist_ok=True)
for name in sys.argv[3:]:
    r = RIGS[name]
    a = np.array(Image.open(os.path.join(SRC, f"npc_{name}.png")).convert("RGBA"))
    stand = a[0:FH, LEFT * FW:(LEFT + 1) * FW].copy()
    body = stand.copy()
    arm = np.zeros_like(stand)
    for y, (x0, x1) in r["arm_rows"].items():
        for x in range(x0, x1 + 1):
            if stand[y, x, 3]:
                arm[y, x] = stand[y, x]
                body[y, x] = 0
    paint(body, r["body_top"], r["body_left"], r["body_patch"], r["pal"])
    if "shorten" in r:
        sh = r["shorten"]
        a0, a1 = sh["hem_from"]
        band = body[a0:a1 + 1].copy()
        legrow = body[sh["leg_row"]].copy()
        body[sh["hem_to"]:sh["hem_to"] + len(band)] = band
        for y in range(sh["leg_rows"][0], sh["leg_rows"][1] + 1):
            body[y] = legrow
        # the lifted hand's lowest rows sat on the removed hem
        arm[sh["hem_to"] + len(band):, :] = 0
    if "sleeve" in r:
        paint(arm, r["sleeve_top"], r["sleeve_left"], [line.replace(" ", ".") for line in r["sleeve"]], r["pal"])
    if "arm" in r:
        blank = np.zeros_like(stand)
        paint(blank, r["arm_top"], r["arm_left"], [line.replace(" ", ".") for line in r["arm"]], r["pal"])
        arm = blank
    sheet = np.zeros((FH, FW * 2, 4), dtype=np.uint8)
    sheet[:, :FW] = body
    sheet[:, FW:] = arm
    Image.fromarray(sheet).save(os.path.join(OUT, f"npc_{name}_side.png"))
    with open(os.path.join(OUT, f"npc_{name}_side.txt"), "w") as f:
        f.write(f"pivot {r['pivot'][0]} {r['pivot'][1]}\nhand_top {r['hand_top']}\nhip {r['hip']}\n")
        if r.get("leg_extend"):
            f.write(f"leg_extend {r['leg_extend']}\n")
    print(name, "ok")
