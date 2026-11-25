"""Set the female player's head back over her neck in the side views (24 Nov).

Seen from the side her head (face and hair layers) sat two pixels ahead of where the male body's sits, on
the same neck and shoulders, so she looked as if she were craning forward. In the side columns (walk:
columns 2 left and 3 right; eating: the same columns of its 48-wide cells) the hair and the face above the
neck move two pixels back; the neck rows of the face layer stay. Masks move with their pictures.
Run once: python3 -I tools/fix_female_head.py
"""
import numpy as np
from PIL import Image

SHIFT = 2


def move(path, cw, ch, cols, neck_row, whole, tail_rows=()):
    a = np.array(Image.open(path).convert("RGBA"))
    orig = a.copy()
    rows = a.shape[0] // ch
    for r in range(rows):
        for c, sign in cols:
            dx = SHIFT * sign
            y0, x0 = r * ch, c * cw
            cell = a[y0:y0 + ch, x0:x0 + cw]
            top = ch if whole else neck_row
            part = cell[:top].copy()
            moved = np.zeros_like(part)
            if dx > 0:
                moved[:, dx:] = part[:, :-dx]
            else:
                moved[:, :dx] = part[:, -dx:]
            cell[:top] = moved
            if r in tail_rows:
                # the low ponytail would run off the cell: its end stays where it was (the tail is two
                # pixels shorter where it meets the hair, not cut off at the tip)
                o = orig[y0:y0 + ch, x0:x0 + cw]
                span = slice(cw - 4, cw) if dx > 0 else slice(0, 4)
                keep = o[:, span, 3] > 0
                cell[:, span][keep] = o[:, span][keep]
    Image.fromarray(a).save(path)


B = "art/player/body2"
for name, whole in (("faces", False), ("hair", True)):
    for suffix in ("", "_mask"):
        move(f"{B}/{name}{suffix}.png", 24, 48, ((2, 1), (3, -1)), 20, whole,
             tail_rows=range(2 * 5, 3 * 5) if name == "hair" else ())      # style 2: low ponytail
E = "player_eating/body_2"
for name, whole in (("faces", False), ("hair", True)):
    for suffix in ("", "_mask"):
        try:
            move(f"{E}/{name}{suffix}.png", 48, 68, ((2, 1), (3, -1)), 38, whole)
        except FileNotFoundError:
            pass
print("ok")
