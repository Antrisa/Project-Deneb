"""Redraw a resident's eyes in the house style: each eye two pixels wide and two tall, one
column white (a shaded white over a bright white), the other the dark pupil over the iris,
with a two-pixel brow on the row right above.

Usage: python3 -I fix_eyes.py SRC_PNG OUT_PNG name [--mouth] [--big]
Front (column 0): viewer's left eye  [lid, pupil] / [white, iris],
                  viewer's right eye [pupil, lid] / [iris, white].
Side facing left (column 2): [pupil, lid] / [iris, white]; column 3 is re-mirrored.
Rows of every walk frame are fixed (the head moves down one pixel on the strides).
"""
import sys
import numpy as np
from PIL import Image

def hexc(h):
    h = h.lstrip("#"); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)] + [255], dtype=np.uint8)

EYES = {
    "evarra": dict(
        colours=dict(pupil="#2d1f45", iris="#7d63b8", white="#f6f0ff", lid="#d4c8e2", skin="#d6a2c3", blush="#e98fbf", brow="#6d4250",
                     mouth="#4b2737", iris_lo="#5d4796"),
        # (x, y of the eye's top-left pixel in the standing frame), rows to repaint as skin
        # the eyes sit either side of the face's middle (x 10-11 and 15-16); the old eye's
        # dark edge and the white flecks beside the right eye are painted back to skin
        front=dict(left=(10, 14), right=(15, 14),
                   clear=[(9, 13), (10, 13), (11, 13), (15, 13), (16, 13), (9, 14), (9, 15), (9, 16),
                          (16, 16), (17, 15), (17, 16), (8, 17), (10, 17), (15, 17)],
                   brows=[(10, 13), (11, 13), (15, 13), (16, 13)],
                   mouth=[(12, 18), (13, 18)], mouth_clear=[(11, 18)],
                   blush=[(9, 17), (16, 17)]),
        side=dict(eye=(6, 14), clear=[(6, 13), (7, 13), (9, 16)], blush=[(8, 16)], brows=[(6, 13), (7, 13)],
                  mouth=[(4, 18)]),
    ),
    "jasper": dict(
        colours=dict(pupil="#2a1510", iris="#8a5a2b", iris_lo="#6a4220", white="#fbf3e0", lid="#e4d5bb",
                     skin="#f5823a", blush="#f2998a", brow="#583927", mouth="#4b2737",
                     cream="#fcd3b1"),
        # the eyes keep their columns (white on the outside); the dark lid row above becomes
        # the eye's top row and the brows go on the row above it. The dark flecks at the eye
        # corners are painted back to fur, and the little mouth under the nose to cream.
        front=dict(left=(7, 14), right=(14, 14),
                   clear=[(6, 15), (9, 14), (9, 15), (9, 16), (16, 14)],
                   brows=[(7, 13), (8, 13), (14, 13), (15, 13)],
                   blush=[(6, 17), (16, 17)],
                   always=[(11, 20, "cream"), (12, 20, "cream")]),
        side=dict(eye=(7, 15), clear=[], brows=[(7, 14), (8, 14)], blush=[(8, 17)]),
    ),
    "rusk": dict(
        colours=dict(pupil="#2a1a12", iris="#6b5a2e", iris_lo="#4f4120", white="#f6ecd4", lid="#decdac",
                     skin="#e67543", blush="#f2998a", brow="#563f2f", mouth="#4b2737",
                     cream="#f3c39d"),
        # the dark lid row becomes the eye's top row; the brows sit on the row above; the dark
        # flecks at the inner corners go back to fur; the smile line under the nose to cream
        front=dict(left=(8, 13), right=(14, 13),
                   clear=[(10, 14), (13, 14)],
                   brows=[(8, 12), (9, 12), (14, 12), (15, 12)],
                   blush=[(6, 17), (17, 17)],
                   always=[(10, 19, "cream"), (11, 19, "cream"), (12, 19, "cream"), (13, 19, "cream"),
                           (12, 18, "cream")]),
        side=dict(eye=(7, 14), clear=[], brows=[(7, 13), (8, 13)], blush=[(9, 17)]),
    ),
    "ooma": dict(
        colours=dict(pupil="#130518", iris="#8a6a2a", iris_lo="#5e4518", white="#f0e3a0", lid="#dece86",
                     skin="#b86d70", blush="#dd7f8a", brow="#3f1f2e", mouth="#4b2737"),
        # her yellow eyes keep their columns (yellow outside, dark inside), one row taller, with
        # brows above
        front=dict(left=(10, 14), right=(15, 14), clear=[],
                   brows=[(10, 13), (11, 13), (15, 13), (16, 13)],
                   blush=[(9, 17), (17, 17)]),
        side=dict(eye=(5, 15), clear=[], brows=[(5, 14), (6, 14)], blush=[(7, 17)]),
    ),
    "tobbin": dict(
        colours=dict(pupil="#2e1c1c", iris="#6b4a1f", iris_lo="#4e3416", white="#f6e6c0", lid="#ebc287",
                     skin="#c88b42", blush="#e08a6a", brow="#462820", mouth="#4b2737"),
        # his eyes sit under the goggle bumps, either side of the face's middle
        front=dict(left=(8, 17), right=(14, 17), clear=[],
                   brows=[(8, 16), (9, 16), (14, 16), (15, 16)],
                   blush=[(6, 21), (17, 21)]),
        side=dict(eye=(8, 18), clear=[], brows=[(8, 17), (9, 17)], blush=[(10, 21)]),
    ),
    "merrow": dict(
        colours=dict(pupil="#18070e", iris="#4a4a2e", iris_lo="#33331f", white="#fbf4d6", lid="#f6edc7",
                     skin="#94bb9a", blush="#e7a0a0", brow="#444441", mouth="#4b2737"),
        # his big frog eyes keep their cream outer column; the inner two columns become the
        # house-style eye (white beside pupil, iris, darker iris) with a brow above.
        front=dict(left=(7, 12), right=(14, 12), clear=[],
                   brows=[(7, 11), (8, 11), (14, 11), (15, 11)],
                   blush=[(5, 17), (18, 17)]),
        side=dict(eye=(10, 13), clear=[], brows=[(10, 12), (11, 12)], blush=[(8, 17)]),
    ),
    "nub": dict(
        colours=dict(pupil="#180411", iris="#2b2614", iris_lo="#423b1c", white="#f6f0c0", lid="#e1d981",
                     skin="#cec75f", blush="#e7a08a", brow="#382520", mouth="#4b2737"),
        # his eyes looked off to one side; they are set to look ahead like everyone's, the
        # cream outer bulge kept, a brow above each
        front=dict(left=(8, 23), right=(14, 23), clear=[(16, 24), (16, 25)],
                   brows=[(8, 22), (9, 22), (14, 22), (15, 22)],
                   blush=[(5, 27), (18, 27)]),
        side=dict(eye=(10, 23), clear=[], brows=[(10, 22), (11, 22)], blush=[(9, 27)]),
    ),
    "garrick": dict(
        colours=dict(pupil="#1d0e22", iris="#563f32", iris_lo="#3b2a22", white="#f5d9ae", lid="#e1c7a0",
                     skin="#eca26a", blush="#f08a7a", brow="#563d35", mouth="#4b2737", line="#4a2a2f"),
        # his eyes one row taller under his brows, the mouth painted out; the right eye moves a
        # pixel in (x 14-15) so both sit the same distance from the middle of the face
        front=dict(left=(9, 10), right=(14, 10), clear=[(16, 9), (16, 10), (16, 11), (16, 12)],
                   brows=[(9, 9), (10, 9), (14, 9), (15, 9)],
                   blush=[(8, 13), (16, 13)],
                   always=[(11, 15, "skin"), (12, 15, "skin")]),
        # side: the pupil goes to the front of the eye (it sat behind the white); the chin
        # steps back a pixel so it no longer juts out as far as the nose (an underbite)
        side=dict(eye=(6, 10), clear=[(8, 10), (8, 11)], brows=[(6, 9), (7, 9)], blush=[(9, 12)],
                  always=[(6, 14, "line")], erase=[(5, 14)]),
    ),
    "saffi": dict(
        colours=dict(pupil="#1f2a1a", iris="#5e754e", iris_lo="#4d5f3f", white="#f2dfc2", lid="#decdb2",
                     skin="#976f62", blush="#f09a8a", brow="#7c4b3e", mouth="#4b2737", cream="#f2c6a2"),
        # her green eyes one row taller with brows above; the dark flecks at their outer
        # corners go back to fur, and the little mouth line to cream
        front=dict(left=(8, 15), right=(14, 15), clear=[(7, 16), (16, 16)],
                   brows=[(8, 14), (9, 14), (14, 14), (15, 14)],
                   blush=[(6, 19), (17, 19)],
                   always=[(11, 21, "cream"), (12, 21, "cream")]),
        side=dict(eye=(7, 16), clear=[(6, 16), (6, 17)], brows=[(7, 15), (8, 15)], blush=[(9, 19)]),
    ),
    "kit": dict(
        colours=dict(pupil="#1f2a18", iris="#67744f", iris_lo="#545f40", white="#f6e2bc", lid="#e2cfac",
                     skin="#ae6741", blush="#f09a8a", brow="#623231", mouth="#4b2737", cream="#fdd7af"),
        front=dict(left=(8, 23), right=(15, 23), clear=[(10, 24), (10, 25)],
                   brows=[(8, 22), (9, 22), (15, 22), (16, 22)],
                   blush=[(6, 27), (18, 27)],
                   always=[(11, 28, "cream"), (12, 28, "cream")]),
        side=dict(eye=(9, 25), clear=[], brows=[(9, 24), (10, 24)], blush=[(12, 28)],
                  always=[(11, 26, "cream")]),
    ),
    "ixali": dict(
        colours=dict(pupil="#1f140f", iris="#513c29", iris_lo="#3a2b1e", white="#f3dc9a", lid="#d7b773",
                     skin="#ddb74e", blush="#e98a6a", brow="#5a392c", mouth="#4b2737"),
        # her eyes keep their columns (pale outside), one row taller, brows above; the little
        # mouth painted out
        # the dark flecks beside her left eye (toward the nose) go back to scales
        front=dict(left=(9, 12), right=(16, 12), clear=[(11, 12), (11, 13), (12, 13), (12, 14)],
                   brows=[(9, 11), (10, 11), (16, 11), (17, 11)],
                   blush=[(8, 15), (18, 15)],
                   always=[(12, 17, "skin"), (13, 17, "skin")]),
        side=dict(eye=(6, 13), clear=[], brows=[(6, 12), (7, 12)], blush=[(8, 16)]),
    ),
    "maren": dict(
        colours=dict(pupil="#2a1a14", iris="#564137", iris_lo="#3d2e26", white="#f9ddbb", lid="#e5cbac",
                     skin="#e0a686", blush="#f08a7a", brow="#593e50", mouth="#4b2737"),
        front=dict(left=(9, 13), right=(15, 13), clear=[],
                   brows=[(9, 12), (10, 12), (15, 12), (16, 12)],
                   blush=[(9, 16), (16, 16)],
                   always=[(11, 18, "skin"), (12, 18, "skin")]),
        side=dict(eye=(6, 14), clear=[], brows=[(6, 13), (7, 13)], blush=[(8, 16)]),
    ),
    "quill": dict(
        colours=dict(pupil="#0b0206", iris="#395a50", iris_lo="#2a4038", white="#d9e5c8", lid="#c7d2b8",
                     skin="#9ea999", blush="#e09a9a", brow="#221920", mouth="#4b2737", cheek="#969788"),
        front=dict(left=(8, 13), right=(14, 13), clear=[],
                   brows=[(8, 12), (9, 12), (14, 12), (15, 12)],
                   blush=[(8, 16), (15, 16)],
                   always=[(11, 18, "cheek"), (12, 18, "cheek")]),
        side=dict(eye=(8, 14), clear=[], brows=[(8, 13), (9, 13)], blush=[(10, 16)]),
    ),
    "owen": dict(
        colours=dict(pupil="#2a1a14", iris="#574235", iris_lo="#3d2d24", white="#f8ddba", lid="#e4cbab",
                     skin="#eba877", blush="#f08a7a", brow="#7e4f3e", mouth="#4b2737"),
        # his freckles stay; the eyes one row taller with brows, the mouth painted out
        front=dict(left=(9, 14), right=(14, 14), clear=[],
                   brows=[(9, 13), (10, 13), (14, 13), (15, 13)],
                   blush=[(8, 17), (16, 17)],
                   always=[(10, 19, "skin"), (11, 19, "skin")]),
        side=dict(eye=(6, 14), clear=[], brows=[(6, 13), (7, 13)], blush=[(8, 17)]),
    ),
    "pip": dict(
        colours=dict(pupil="#2a1414", iris="#573826", iris_lo="#3d271b", white="#ffdfb3", lid="#eacda4",
                     skin="#eca56f", blush="#f08a7a", brow="#6d2a26", mouth="#4b2737"),
        # eyes one row taller with brows above, the little mouth painted out
        front=dict(left=(9, 23), right=(14, 23), clear=[],
                   brows=[(9, 22), (10, 22), (14, 22), (15, 22)],
                   blush=[(8, 26), (16, 26)],
                   always=[(11, 27, "skin"), (12, 27, "skin")]),
        side=dict(eye=(8, 23), clear=[], brows=[(8, 22), (9, 22)], blush=[(10, 26)]),
    ),
    "sesska": dict(
        colours=dict(pupil="#1d0e15", iris="#543641", iris_lo="#36212c", white="#e8bfa3", lid="#cfa091",
                     skin="#b88a94", blush="#e0909a", brow="#36212c", mouth="#36212c"),
        # her mouthparts (the pale fangs under the face) are kept
        front=dict(left=(8, 14), right=(16, 14), clear=[(10, 16), (11, 14), (11, 15), (18, 14), (18, 15)],
                   brows=[(8, 13), (9, 13), (16, 13), (17, 13)],
                   blush=[(7, 17), (18, 17)]),
        side=dict(eye=(5, 14), clear=[(4, 14), (4, 15), (7, 14), (5, 16)], brows=[(5, 13), (6, 13)],
                  blush=[(7, 17)]),
    ),
    "bram": dict(
        colours=dict(pupil="#200711", iris="#3d2a1e", iris_lo="#2a1a14", white="#f8e9bc", lid="#d9cd83",
                     skin="#b1b852", dome="#8c9049", blush="#e0907a", brow="#331e1d", mouth="#4b2737"),
        # his eyes looked off to his left; they are set to look ahead, the cream outer edge of
        # each eye bump kept, a brow above; his long frog smile is kept
        front=dict(left=(7, 17), right=(16, 17), clear=[],
                   brows=[(7, 16), (8, 16), (16, 16), (17, 16)],
                   blush=[(7, 22), (17, 22)],
                   always=[(6, 17, "lid"), (6, 18, "white"), (6, 19, "lid"),
                           (18, 17, "lid"), (18, 18, "white"), (18, 19, "lid"),
                           (9, 18, "dome"), (9, 19, "dome"), (15, 18, "dome"),
                           (6, 20, "dome"), (7, 20, "dome"), (8, 20, "dome"),
                           (16, 20, "dome"), (17, 20, "dome"), (18, 20, "dome")]),
        side=dict(eye=(10, 18), clear=[], brows=[(10, 17), (11, 17)], blush=[(11, 22)],
                  always=[(9, 18, "dome"), (10, 20, "dome"), (11, 20, "dome")]),
    ),
    "tikka": dict(
        colours=dict(pupil="#10070d", iris="#542f37", iris_lo="#2f1423", white="#ebbb71", lid="#d2895a",
                     skin="#a65679", blush="#e0809a", brow="#2f1423", mouth="#2f1423"),
        # her gold eyes looked off to one side; they are set to look ahead, the gold kept as
        # the pale of the eye; her head spots and mouthparts are kept
        front=dict(left=(8, 16), right=(14, 16),
                   clear=[(10, 16), (10, 17), (11, 16), (11, 17), (10, 18), (11, 18),
                          (16, 16), (16, 17), (16, 18), (17, 16), (17, 17), (17, 18),
                          (10, 15), (16, 15), (17, 15)],
                   brows=[(8, 15), (9, 15), (14, 15), (15, 15)],
                   blush=[(7, 19), (16, 19)]),
        side=dict(eye=(5, 16), clear=[(4, 18), (5, 18), (6, 18), (4, 16), (4, 14)], brows=[(5, 15), (6, 15)],
                  blush=[(7, 19)]),
    ),
    "freya": dict(
        colours=dict(pupil="#1f3a32", iris="#4f9a3c", iris_lo="#2f6a2a", white="#e6fbff", lid="#e8d9bd",
                     skin="#f2c29a", blush="#ec9a8a", brow="#86593f", mouth="#4b2737"),
        front=dict(left=(10, 13), right=(15, 13), clear=[],
                   brows=[(10, 12), (11, 12), (15, 12), (16, 12)],
                   blush=[(10, 16), (16, 16)],
                   always=[(12, 16, "skin"), (13, 16, "skin")]),
        side=dict(eye=(7, 14), clear=[], brows=[(7, 13), (8, 13)], blush=[(9, 17)]),
    ),
    "job": dict(
        colours=dict(pupil="#1a0b10", iris="#3b2720", iris_lo="#2c111c", white="#f4d3a5", lid="#e0c297",
                     skin="#b66037", blush="#d9766a", brow="#2c111c", mouth="#4b2737"),
        # eyes under the hard-hat brim; the little mouth painted out
        front=dict(left=(8, 13), right=(14, 13), clear=[(10, 13), (10, 14)],
                   brows=[(8, 12), (9, 12), (14, 12), (15, 12)],
                   blush=[(7, 16), (16, 16)],
                   always=[(10, 17, "skin"), (11, 17, "skin")]),
        side=dict(eye=(6, 13), clear=[], brows=[(6, 12), (7, 12)], blush=[(8, 16)]),
    ),
    "zaas": dict(
        colours=dict(pupil="#200b17", iris="#352930", iris_lo="#251a24", white="#e1cc8f", lid="#c9b47a",
                     skin="#50978d", blush="#e0907a", brow="#251a24", mouth="#251a24"),
        # eyes under the hat brim; the little orange beak among the face tentacles is kept
        front=dict(left=(10, 20), right=(16, 20), clear=[],
                   brows=[(10, 19), (11, 19), (16, 19), (17, 19)],
                   blush=[(9, 23), (18, 23)]),
        side=dict(eye=(7, 20), clear=[], brows=[(7, 19), (8, 19)], blush=[(9, 23)]),
    ),
    "tarbesh": dict(
        colours=dict(pupil="#371921", iris="#cc7e43", iris_lo="#a1663f", white="#edd197", lid="#dac08a",
                     skin="#b3944d", blush="#e08a6a", brow="#54392a", mouth="#4b2737"),
        # his orange eyes kept as the iris; the little mouth line on his snout painted out
        front=dict(left=(8, 13), right=(15, 13), clear=[(10, 13), (10, 14)],
                   brows=[(8, 12), (9, 12), (15, 12), (16, 12)],
                   blush=[(7, 16), (17, 16)],
                   always=[(12, 17, "skin"), (13, 17, "skin")]),
        side=dict(eye=(7, 13), clear=[(6, 14)], brows=[(7, 12), (8, 12)], blush=[(9, 16)]),
    ),
    "vzzket": dict(
        colours=dict(pupil="#1f140f", iris="#513c29", iris_lo="#3a2b1e", white="#ebc076", lid="#d8b06c",
                     skin="#b59748", blush="#e98a6a", brow="#523628", mouth="#4b2737"),
        # his eyes keep their columns (pale outside), one row taller, brows above; the little
        # mouth painted out
        front=dict(left=(10, 12), right=(16, 12), clear=[(12, 12)],
                   brows=[(10, 11), (11, 11), (16, 11), (17, 11)],
                   blush=[(9, 15), (18, 15)],
                   always=[(12, 16, "skin"), (13, 16, "skin")]),
        side=dict(eye=(7, 11), clear=[], brows=[(7, 10), (8, 10)], blush=[(9, 15)]),
    ),
    "artie": dict(
        colours=dict(pupil="#2e151a", iris="#624131", iris_lo="#4a2d24", white="#f8dfbb", lid="#e4cdac",
                     skin="#eda470", blush="#ec8a76", brow="#603f34", mouth="#4b2737"),
        front=dict(left=(8, 14), right=(14, 14), clear=[(10, 14), (10, 15)],
                   brows=[(8, 13), (9, 13), (14, 13), (15, 13)],
                   blush=[(7, 17), (16, 17)],
                   always=[(10, 18, "skin"), (11, 18, "skin")]),
        side=dict(eye=(7, 14), clear=[], brows=[(7, 13), (8, 13)], blush=[(9, 17)]),
    ),
    "stu": dict(
        colours=dict(pupil="#070008", iris="#403521", iris_lo="#2b1f1a", white="#fdf4b4", lid="#f6df97",
                     skin="#acb34c", dome="#919647", blush="#e0907a", brow="#2b1f1a", mouth="#4b2737"),
        # like Bram: the cream outer edge of each eye bump kept, the eyes set to look ahead, a
        # brow above; his wide frog smile is kept
        front=dict(left=(8, 12), right=(15, 12), clear=[],
                   brows=[(8, 11), (9, 11), (15, 11), (16, 11)],
                   blush=[(7, 16), (17, 16)],
                   always=[(7, 12, "lid"), (7, 13, "white"), (7, 14, "lid"),
                           (17, 12, "lid"), (17, 13, "white"), (17, 14, "lid"),
                           (10, 12, "dome"), (10, 13, "dome"), (10, 14, "dome")]),
        side=dict(eye=(11, 12), clear=[], brows=[(11, 11), (12, 11)], blush=[(11, 16)]),
    ),
    "tally": dict(
        colours=dict(pupil="#1d1019", iris="#3e2a31", iris_lo="#291b26", white="#f2c26e", lid="#d39c64",
                     skin="#926172", blush="#e0809a", brow="#341d2a", mouth="#291b26"),
        # her gold eyes set to look ahead, the gold kept as the pale of the eye; her mouth
        # tentacles are kept
        front=dict(left=(9, 18), right=(15, 18), clear=[(11, 18), (11, 20), (11, 19)],
                   brows=[(9, 17), (10, 17), (15, 17), (16, 17)],
                   blush=[(8, 21), (16, 21)]),
        side=dict(eye=(7, 18), clear=[(9, 18)], brows=[(7, 17), (8, 17)], blush=[(9, 21)]),
    ),
    "ana": dict(
        colours=dict(pupil="#2f161e", iris="#5f4151", iris_lo="#4a2f3d", white="#f8ddca", lid="#e4cbb9",
                     skin="#e1a378", shade="#aa7d67", blush="#e8857a", brow="#2c1119", mouth="#4b2737"),
        # her half-lidded eyes opened to look ahead (two wide, three tall), a brow above each
        # under her fringe, blush; the little mouth painted out
        # the dark nose-side pixels beside her left eye (and the end of her fringe above it)
        # read as a third eye column: they become skin, so both eyes are two wide
        front=dict(left=(8, 13), right=(14, 13), clear=[(11, 18), (12, 18), (10, 14), (10, 15)],
                   brows=[(8, 12), (9, 12), (14, 12), (15, 12)],
                   blush=[(8, 16), (15, 16)],
                   always=[(10, 12, "shade"), (10, 13, "shade")]),
        side=dict(eye=(7, 14), clear=[], brows=[(7, 13), (8, 13)], blush=[(9, 16)]),
    ),
    "sara_solid": dict(
        colours=dict(pupil="#141521", iris="#2c5d6f", iris_lo="#203746", white="#d8f8f2", lid="#c6e4de",
                     skin="#8dd7da", blush="#d7b3c8", brow="#203746", mouth="#2c5d6f"),
        # her eyes set to look ahead (two wide, three tall), a brow above each, a soft blush,
        # the little mouth painted out
        # the dark pixels beside her left eye on the nose side (x 11, 12) read as a third eye
        # column: they become skin, so both eyes match
        front=dict(left=(9, 12), right=(15, 12), clear=[(13, 16), (14, 16), (11, 12), (11, 13), (12, 12), (12, 13)],
                   brows=[(9, 11), (10, 11), (15, 11), (16, 11)],
                   blush=[(10, 15), (16, 15)]),
        side=dict(eye=(6, 13), clear=[], brows=[(6, 12), (7, 12)], blush=[(8, 15)]),
    ),
}

def head_dy(stand, frame):
    best = (10**9, 0)
    for dy in (0, 1, 2):
        s = np.roll(stand, dy, 0)
        d = int((s[4:20] != frame[4:20]).any(2).sum())
        best = min(best, (d, dy))
    return best[1]

def paint(cell, cfg, view, dy, c):
    if view == "front":
        for (x, y) in cfg["clear"]:
            cell[y + dy, x] = c["skin"]
        for (x, y) in cfg.get("blush", []):
            cell[y + dy, x] = c["blush"]
        for (x, y) in cfg.get("brows", []):
            cell[y + dy, x] = c["brow"]
        for (x, y, k) in cfg.get("always", []):
            cell[y + dy, x] = c[k]
        if MOUTH:
            for (x, y) in cfg.get("mouth_clear", []):
                cell[y + dy, x] = c["skin"]
            for (x, y) in cfg.get("mouth", []):
                cell[y + dy, x] = c["mouth"]
        lx, ly = cfg["left"]; rx, ry = cfg["right"]
        cell[ly + dy, lx] = c["lid"]; cell[ly + dy, lx + 1] = c["pupil"]
        cell[ly + 1 + dy, lx] = c["white"]; cell[ly + 1 + dy, lx + 1] = c["iris"]
        cell[ry + dy, rx] = c["pupil"]; cell[ry + dy, rx + 1] = c["lid"]
        cell[ry + 1 + dy, rx] = c["iris"]; cell[ry + 1 + dy, rx + 1] = c["white"]
        if TALL:
            # front eyes two wide and three tall: the white column (shaded white over two bright
            # whites) beside pupil, iris and a darker iris; the side eye keeps its two by two
            for (white_x, iris_x) in ((lx, lx + 1), (rx + 1, rx)):
                cell[ly + dy, white_x] = c["lid"]; cell[ly + dy, iris_x] = c["pupil"]
                cell[ly + 1 + dy, white_x] = c["white"]; cell[ly + 1 + dy, iris_x] = c["iris"]
                cell[ly + 2 + dy, white_x] = c["white"]; cell[ly + 2 + dy, iris_x] = c["iris_lo"]
        if BIG:
            # three wide and three tall: a dark lash row over white + iris, the iris darker
            # at the bottom; the eyes grow outward so the gap between them stays the same
            for (ex, outward) in ((lx - 1, -1), (rx, 1)):
                cols = [ex, ex + 1, ex + 2]
                white = cols[0] if outward < 0 else cols[2]
                iris = [x for x in cols if x != white]
                for x in cols:
                    cell[ly + dy, x] = c["pupil"]
                cell[ly + 1 + dy, white] = c["white"]; cell[ly + 2 + dy, white] = c["white"]
                for x in iris:
                    cell[ly + 1 + dy, x] = c["iris"]; cell[ly + 2 + dy, x] = c["iris_lo"]
                for x in cols:
                    cell[ly - 1 + dy, x] = c["brow"]
    else:
        for (x, y) in cfg["clear"]:
            cell[y + dy, x] = c["skin"]
        for (x, y) in cfg.get("blush", []):
            cell[y + dy, x] = c["blush"]
        for (x, y) in cfg.get("brows", []):
            cell[y + dy, x] = c["brow"]
        for (x, y, k) in cfg.get("always", []):
            cell[y + dy, x] = c[k]
        for (x, y) in cfg.get("erase", []):
            cell[y + dy, x] = 0
        if MOUTH:
            for (x, y) in cfg.get("mouth", []):
                cell[y + dy, x] = c["mouth"]
        ex, ey = cfg["eye"]
        cell[ey + dy, ex] = c["pupil"]; cell[ey + dy, ex + 1] = c["lid"]
        cell[ey + 1 + dy, ex] = c["iris"]; cell[ey + 1 + dy, ex + 1] = c["white"]
        if BIG:
            for x in (ex - 1, ex, ex + 1):
                cell[ey + dy, x] = c["pupil"]; cell[ey - 1 + dy, x] = c["brow"]
            cell[ey + 1 + dy, ex - 1] = c["iris"]; cell[ey + 1 + dy, ex] = c["iris"]; cell[ey + 1 + dy, ex + 1] = c["white"]
            cell[ey + 2 + dy, ex - 1] = c["iris_lo"]; cell[ey + 2 + dy, ex] = c["iris_lo"]; cell[ey + 2 + dy, ex + 1] = c["white"]

src, out, name = sys.argv[1:4]
MOUTH = "--mouth" in sys.argv     # a two-pixel dark mouth (one pixel at the edge of the profile)
BIG = "--big" in sys.argv         # eyes three pixels wide and three tall
TALL = "--tall" in sys.argv       # front eyes two wide and three tall
a = np.array(Image.open(src).convert("RGBA"))
cfg = EYES[name]
c = {k: hexc(v) for k, v in cfg["colours"].items()}
rows = a.shape[0] // 48
for col, view in ((0, "front"), (2, "side")):
    stand = a[0:48, col*24:(col+1)*24].copy()
    for r in range(rows):
        cell = a[r*48:(r+1)*48, col*24:(col+1)*24]
        dy = head_dy(stand, cell)
        paint(cell, cfg[view], view, dy, c)
        if col == 2:
            a[r*48:(r+1)*48, 72:96] = cell[:, ::-1]
Image.fromarray(a).save(out)
print("ok")
