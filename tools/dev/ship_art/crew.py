"""Crew inside ships (Claude, 21 Nov 2026). Zachary: "we can use mini people sprites like FTL and player in a space
suit so we dont gotta worry about customization". Small front-facing people, about 14 x 17 pixels, in 24 x 24
frames (one room cell holds one standing crew member), looking like the residents of each species.

Each sheet: art/ships/crew/<id>.png, 24 x 24 frames, 4 across:
  row 1  idle (2 frames), row 2  walk (4 frames)
More rows (repair, fight, knocked out) come when those are built.

Run from the repo root with -I:  python3 -I tools/dev/ship_art/crew.py . [out dir]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image
from ship_kit import hexc

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT_COLOR = "#262535"

# The body below the head: shoulders, uniform, hands, legs, boots. 14 wide.
BODY = [
    "..ouuuuuuuuo..",
    ".ouuuuuuuuuuo.",
    ".ouuuuaauuuuo.",
    ".ouuuuuuuuuuo.",
    ".osUUUUUUUUso.",
    "..oUUUUUUUUo..",
    "..oUUUooUUUo..",
    "..oUUo..oUUo..",
    "..obbo..obbo..",
    "..oooo..oooo..",
]
# Arachnay have four arms: a second pair at the sides.
BODY_FOUR_ARMS = [
    "..ouuuuuuuuo..",
    ".ouuuuuuuuuuo.",
    "osuuuuaauuuuso",
    "o.ouuuuuuuuo.o",
    ".osUUUUUUUUso.",
    "..oUUUUUUUUo..",
    "..oUUUooUUUo..",
    "..oUUo..oUUo..",
    "..obbo..obbo..",
    "..oooo..oooo..",
]
# A short Moogli body.
BODY_SHORT = [
    "..ouuuuuuuuo..",
    ".osuuuaauuuso.",
    ".ouUUUUUUUUuo.",
    "..oUUUooUUUo..",
    "..obbo..obbo..",
    "..oooo..oooo..",
]

HEADS = {
    "human": [
        "....oooooo....",
        "...ohhhhhho...",
        "..ohhhhhhhho..",
        "..ohssssssho..",
        "..osesssseso..",
        "..oSssssssSo..",
        "...oSSSSSSo...",
    ],
    "suit": [
        "....oooooo....",
        "...owwwwwwo...",
        "..owwwwwwwwo..",
        "..owvvvvvvwo..",
        "..owvVvvvvwo..",
        "..owvvvvvvwo..",
        "...owwwwwwo...",
    ],
    "zaash": [
        ".o..o.oo.o..o.",
        ".oh.ohhhho.ho.",
        "..ohhhhhhhho..",
        "..osssssssso..",
        "..osyssssyso..",
        "..osssssssso..",
        "...oSSSSSSo...",
    ],
    "moogli": [
        "..ooo....ooo..",
        ".oweo....oewo.",
        ".osssssssssso.",
        "osssssssssssso",
        "oSSooooooooSSo",
        ".oSSSSSSSSSSo.",
        "..oooooooooo..",
    ],
    "ervani": [
        "..o........o..",
        ".oho......oho.",
        ".ohhoooooohho.",
        "..ohhhhhhhho..",
        "..ohehhhheho..",
        "..ohmmmmmmho..",
        "...ommeemmo...",
    ],
    "vuultam": [
        "...oooooooo...",
        "..ohhhhhhhho..",
        ".ohhhhhhhhhho.",
        ".ohssssssssho.",
        "..osesssseso..",
        "..oSssssssSo..",
        "...oSSSSSSo...",
    ],
    "scyldar": [
        "....oooooo....",
        "...osssssso...",
        "..osssssssso..",
        "..osesssseso..",
        "..osssssssso..",
        "..ottsttstto..",
        "...ot.tt.to...",
    ],
    "arachnay": [
        "....oooooo....",
        "...ohhhhhho...",
        "..ohyhyyhyho..",
        "..osyssssyso..",
        "..osssssssso..",
        "..oSoSSSSoSo..",
        "...oSSSSSSo...",
    ],
}
for k, rows in HEADS.items():
    for r in rows:
        assert len(r) == 14, (k, r, len(r))
for rows in (BODY, BODY_FOUR_ARMS, BODY_SHORT):
    for r in rows:
        assert len(r) == 14, r

# Who: head, body, colours. "u"/"U" is the uniform; hired crew wear mid grey so the game can tint it.
CREW = {
    "player": ("suit", BODY, {"w": "#f4f1ea", "v": "#24324a", "V": "#7fd0f0", "u": "#f4f1ea", "U": "#c8c4bc", "a": "#fb7412", "b": "#7a7480", "s": "#f4f1ea"}),
    "human": ("human", BODY, {"h": "#6a4a32", "s": "#e8b896", "S": "#c89878", "e": "#262535", "u": "#8a8e98", "U": "#6e727c", "a": "#d8d4c8", "b": "#4a4450"}),
    "zaash": ("zaash", BODY, {"h": "#4a7a3a", "s": "#8ab45a", "S": "#6a9442", "y": "#f2c94c", "u": "#8a8e98", "U": "#6e727c", "a": "#d8d4c8", "b": "#4a4450"}),
    "moogli": ("moogli", BODY_SHORT, {"w": "#f4f1ea", "e": "#262535", "s": "#7cc85a", "S": "#5aa842", "u": "#8a8e98", "U": "#6e727c", "a": "#d8d4c8", "b": "#4a4450"}),
    "ervani": ("ervani", BODY, {"h": "#e0763a", "m": "#f6ead8", "e": "#262535", "s": "#e0763a", "u": "#8a8e98", "U": "#6e727c", "a": "#d8d4c8", "b": "#4a4450"}),
    "vuultam": ("vuultam", BODY, {"h": "#f4f0f8", "s": "#c8b0e0", "S": "#a890c8", "e": "#3a2a5a", "u": "#8a8e98", "U": "#6e727c", "a": "#d8d4c8", "b": "#4a4450"}),
    "scyldar": ("scyldar", BODY, {"s": "#4ab4a8", "S": "#2a8a80", "e": "#123a3a", "t": "#2a8a80", "u": "#8a8e98", "U": "#6e727c", "a": "#d8d4c8", "b": "#4a4450"}),
    "arachnay": ("arachnay", BODY_FOUR_ARMS, {"h": "#5a3a8a", "s": "#8a6ac8", "S": "#6a4aa8", "y": "#f2c94c", "u": "#8a8e98", "U": "#6e727c", "a": "#d8d4c8", "b": "#4a4450"}),
    "rabble_pirate": ("human", BODY, {"h": "#b82a20", "s": "#d8a888", "S": "#b88868", "e": "#262535", "u": "#7a4a30", "U": "#5a3420", "a": "#b82a20", "b": "#2e2e38"}),
    "terran_marine": ("suit", BODY, {"w": "#eef0f2", "v": "#1f4a90", "V": "#8ad0ff", "u": "#eef0f2", "U": "#c2c7cf", "a": "#2f6fd0", "b": "#5a606c", "s": "#eef0f2"}),
}


def figure(head, body, pal, lift=(0, 0), bob=0):
    """One 24 x 24 frame. lift: how far each leg is raised (walk frames); bob: the whole figure moves up."""
    rows = head + body
    im = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    px = im.load()
    x0 = 5
    y0 = 24 - len(rows) - 1 - bob
    legs_from = len(rows) - 4          # the last four rows are legs and boots
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            yy = y0 + r
            if r >= legs_from:
                yy -= lift[0] if c < 7 else lift[1]
            col = OUT_COLOR if ch == "o" else pal.get(ch, "#ff00ff")
            if 0 <= yy < 24:
                px[x0 + c, yy] = hexc(col)
    return im


def sheet(cid):
    head_id, body, pal = CREW[cid]
    head = HEADS[head_id]
    out = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    out.alpha_composite(figure(head, body, pal), (0, 0))
    out.alpha_composite(figure(head, body, pal, bob=1), (24, 0))
    for i, (lift, bob) in enumerate((((0, 2), 1), ((0, 0), 0), ((2, 0), 1), ((0, 0), 0))):
        out.alpha_composite(figure(head, body, pal, lift, bob), (i * 24, 24))
    return out


if __name__ == "__main__":
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "art/ships/crew"
    out.mkdir(parents=True, exist_ok=True)
    for cid in CREW:
        sheet(cid).save(out / f"{cid}.png")
    print("ok", len(CREW))
