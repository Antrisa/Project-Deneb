"""The six Custodians' portraits for the talk box (24 Nov 2026): a Precursor crystal shard each, in its own colour,
with a light inside it and small shards floating round it. 128 x 128, one picture (the talk box shows it for every
mood). Drawn in code to the art style guide: master palette only, #5b332d outline, flat facets lit from the top left,
no single-pixel specks. Writes art/portrait_<id>.png. Run: python3 tools/dev/custodian_art.py [--preview]
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from prologue_art import C, Canvas, OUT, poly, edge, disc, sh, check, despeckle  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
S = 128

# id -> facet ramp (dark, mid, light, highlight), the core's light, the halo, the shape (width, height, lean)
CUSTODIANS = {
    "chancellor": dict(ramp=[("brass", 1), ("brass", 2), ("brass", 3), ("brass", 4)], core=("cream", 4),
                       halo=[("wood", 0), ("wood", 1)], size=(44, 92, 4)),        # amber-gold, warm and fussy
    "sovereign": dict(ramp=[("teal", 1), ("teal", 2), ("leaf", 3), ("leaf", 4)], core=("cream", 4),
                      halo=[("leaf", 0), ("teal", 0)], size=(38, 100, -3)),       # emerald-teal, serene
    "forgemaster": dict(ramp=[("glow", 1), ("glow", 2), ("rock", 3), ("rock", 4)], core=("glow", 4),
                        halo=[("glow", 0), ("rock", 0)], size=(54, 84, 0)),       # cobalt-silver, gruff and broad
    "harbinger": dict(ramp=[("berry", 1), ("copper", 2), ("copper", 3), ("copper", 4)], core=("brass", 4),
                      halo=[("berry", 0), ("copper", 0)], size=(46, 96, 6)),      # ember-red, sorry about his title
    "shepherd": dict(ramp=[("violet", 1), ("violet", 2), ("glow", 3), ("glow", 4)], core=("cream", 4),
                     halo=[("violet", 0), ("glow", 0)], size=(36, 104, -5)),      # storm violet
    "warden": dict(ramp=[("berry", 2), ("copper", 3), ("brass", 3), ("brass", 4)], core=("cream", 4),
                   halo=[("violet", 1), ("berry", 0)], size=(42, 94, 2)),        # sunset rose-gold, Tidelight
}


def crystal(cx, top, w, h, lean):
    """A hexagonal shard standing up: a pointed top, straight sides, a short point below. Returns the outline
    polygon and the three facet polygons (left, middle, right)."""
    hw = w / 2
    tip = (cx + lean, top)
    shoulder = top + h * .26
    base = top + h * .86
    foot = (cx - lean * .3, top + h)
    l, r = cx - hw, cx + hw
    ml, mr = cx - hw * .34, cx + hw * .34
    outline = [tip, (r, shoulder), (r, base), foot, (l, base), (l, shoulder)]
    left = [tip, (ml + lean * .2, shoulder + 4), (ml, base + 5), foot, (l, base), (l, shoulder)]
    mid = [tip, (mr + lean * .2, shoulder + 4), (mr, base + 5), foot, (ml, base + 5), (ml + lean * .2, shoulder + 4)]
    right = [tip, (r, shoulder), (r, base), foot, (mr, base + 5), (mr + lean * .2, shoulder + 4)]
    return outline, left, mid, right


def portrait(spec):
    cv = Canvas(S, S, fill=C("violet", 0))
    # a halo in two bands behind the crystal
    yy, xx = np.mgrid[0:S, 0:S]
    d = ((xx - 64) / 58.0) ** 2 + ((yy - 66) / 62.0) ** 2
    cv.paint(d <= 1.0, C(*spec["halo"][0]))
    cv.paint(d <= .55, C(*spec["halo"][1]))
    w, h, lean = spec["size"]
    out, left, mid, right = crystal(64, 64 - h / 2 - 4, w, h, lean)
    body = poly(out, S, S)
    ramp = [C(*r) for r in spec["ramp"]]
    cv.paint(poly(right, S, S) & body, ramp[0])
    cv.paint(poly(mid, S, S) & body, ramp[1])
    cv.paint(poly(left, S, S) & body, ramp[2])
    # the light inside: a bright band down the middle facet, brightest in its heart
    core = poly([(64 + lean * .6, 64 - h * .25), (64 + 5, 64), (64 - lean * .1, 64 + h * .26), (64 - 5, 64)], S, S) & body
    cv.paint(core, ramp[3])
    cv.paint(disc(64, 64, 5, S, S) & body, C(*spec["core"]))
    # a highlight along the lit edge
    hl = body & ~sh(body, 3, 3) & poly(left, S, S)
    cv.paint(hl, ramp[3])
    cv.paint(edge(body), OUT)
    # small shards floating round it
    for (x, y, s) in ((28, 40, 7), (98, 34, 6), (100, 92, 8), (26, 96, 5)):
        o, l2, m2, r2 = crystal(x, y - s * 1.2, s * 1.1, s * 2.4, 0)
        b = poly(o, S, S)
        cv.paint(b, ramp[1])
        cv.paint(poly(l2, S, S) & b, ramp[2])
        cv.paint(edge(b), OUT)
    despeckle(cv, np.ones((S, S), bool), passes=2)
    return cv


def main():
    for cid, spec in CUSTODIANS.items():
        cv = portrait(spec)
        check(cv, cid)
        cv.save(os.path.join(ROOT, "art", "portrait_%s.png" % cid))
    if "--preview" in sys.argv:
        sheet = Image.new("RGBA", (S * 2 * 6, S * 2))
        for i, cid in enumerate(CUSTODIANS):
            im = Image.open(os.path.join(ROOT, "art", "portrait_%s.png" % cid)).resize((S * 2, S * 2), Image.NEAREST)
            sheet.paste(im, (i * S * 2, 0))
        sheet.save("/tmp/look/custodians.png")
    print("wrote", ", ".join("portrait_%s" % c for c in CUSTODIANS))


if __name__ == "__main__":
    main()
