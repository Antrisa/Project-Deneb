import sys
from PIL import Image, ImageDraw
src, rows_txt, out = sys.argv[1:4]
a = Image.open(src).convert("RGBA")
labels = open(rows_txt).read().split()
labels = [" ".join(labels[i:i + 2]) for i in range(0, len(labels), 2)]
acts = list(dict.fromkeys(l.split()[0] for l in labels))
S = 5; BG = (150, 170, 150, 255); CW, FH = 36, 48
W, H = 4 * (CW * S + 8), len(acts) * (FH * S + 22)
frames = []
for f in range(4):
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    for i, act in enumerate(acts):
        for j, dr in enumerate("dulr"):
            if f"{act} {dr}" not in labels:
                continue
            r = labels.index(f"{act} {dr}")
            cell = a.crop((f * CW, r * FH, (f + 1) * CW, (r + 1) * FH)).resize((CW * S, FH * S), Image.NEAREST)
            x, y = j * (CW * S + 8), i * (FH * S + 22)
            im.alpha_composite(cell, (x, y + 18))
            d.text((x + 4, y + 3), f"{act} {dr}", fill=(0, 0, 0, 255))
    frames.append(im.convert("RGB"))
frames[0].save(out, save_all=True, append_images=frames[1:], duration=220, loop=0)
