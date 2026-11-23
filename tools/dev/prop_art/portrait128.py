"""Portraits in Jasper's style at full 128 x 128 (Zachary, 23 Nov: "you can do 128"). Keeps each face's drawing and
changes how it is coloured and outlined: a small set of flat colours shared by all expressions (no soft gradients),
isolated specks cleaned, the C warm/purple colour lean, and Jasper's thick dark outer outline. Framing: the
character fills the picture and sits on the bottom edge, like Jasper."""
import sys
import numpy as np
from PIL import Image

SIZE = 128
OUTLINE = np.array([40, 24, 32])


def frames_of(path):
    im = Image.open(path).convert("RGBA")
    n = im.width // SIZE
    return [im.crop((i * SIZE, 0, (i + 1) * SIZE, SIZE)) for i in range(n)]


def refit(frames, fill_w=116, fill_h=126):
    boxes = [f.getbbox() for f in frames if f.getbbox()]
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
    bw, bh = box[2] - box[0], box[3] - box[1]
    s = min(fill_w / bw, fill_h / bh)
    if 0.97 < s < 1.06:          # already framed like Jasper: leave the pixels alone
        return frames
    out = []
    for f in frames:
        sub = f.crop(box)
        w, h = round(bw * s), round(bh * s)
        sm = sub.resize((w, h), Image.LANCZOS)
        c = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        c.alpha_composite(sm, ((SIZE - w) // 2, SIZE - h))
        out.append(c)
    return out


def palette(frames, k, iters=30, seed=5):
    """k colours for the whole character (all expressions together), by k-means on its own pixels, so every colour
    is a true average of a region (median-cut and max-coverage drifted dark purples toward brown)."""
    px = np.concatenate([np.array(f)[..., :3][np.array(f)[..., 3] > 127] for f in frames]).astype(float)
    rng = np.random.default_rng(seed)
    sample = px[rng.choice(len(px), min(len(px), 12000), replace=False)]
    c = sample[rng.choice(len(sample), k, replace=False)]
    for _ in range(iters):
        lab = ((sample[:, None, :] - c[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            m = lab == j
            if m.any(): c[j] = sample[m].mean(0)
    return np.round(c).astype(int)


def warm(rgb):
    sys.path.insert(0, "/home/claude/project-deneb/tools")
    import warm_shift
    a = np.zeros((1, len(rgb), 4), np.uint8); a[0, :, :3] = rgb; a[0, :, 3] = 255
    return warm_shift.warm_array(a, 0.35)[0, :, :3].astype(int)


def smooth(f):
    """Take the soft painting's noise out before choosing colours: a 3x3 median on colour, alpha untouched."""
    from PIL import ImageFilter
    a = np.array(f)
    rgb = Image.fromarray(a[..., :3]).filter(ImageFilter.MedianFilter(3))
    b = np.array(rgb).astype(int); o = a[..., :3].astype(int)
    # keep the drawing's features: dark lines (eyes, brows, mouths) and marks that stand out (blush, catch-lights)
    lum_o = (0.299 * o[..., 0] + 0.587 * o[..., 1] + 0.114 * o[..., 2]) / 255.0
    distinct = np.sqrt(((o - b) ** 2).sum(-1)) > 55
    keep = (lum_o < 0.32) | distinct
    out = a.copy(); m = (a[..., 3] > 127) & ~keep
    out[m, :3] = b[m]
    return Image.fromarray(out, "RGBA")


def remake(path, out_path, k=32, outline=2, passes=2):
    frames = [smooth(f) for f in refit(frames_of(path))]
    feats = []
    for f in frames:
        o = np.array(f)[..., :3].astype(int)
        feats.append((0.299 * o[..., 0] + 0.587 * o[..., 1] + 0.114 * o[..., 2]) / 255.0 < 0.32)
    pal = palette(frames, k)
    wpal = warm(pal)
    res = []
    for fi, f in enumerate(frames):
        a = np.array(f).astype(int)
        sol = a[..., 3] > 127
        d = ((a[..., :3][..., None, :] - pal[None, None]) ** 2).sum(-1)
        idx = d.argmin(-1)
        # clean specks: a pixel unlike all 8 neighbours takes the most common of them
        cl = idx.copy()
        for _ in range(passes):
            src = cl.copy()
            for y in range(1, SIZE - 1):
                for x in range(1, SIZE - 1):
                    if not sol[y, x] or feats[fi][y, x]: continue
                    nb = np.delete(src[y - 1:y + 2, x - 1:x + 2].ravel(), 4)
                    if (nb == src[y, x]).sum() <= 1:
                        v, c = np.unique(nb, return_counts=True)
                        if c.max() >= 4: cl[y, x] = v[c.argmax()]
        out = np.zeros((SIZE, SIZE, 4), np.uint8)
        out[..., :3] = wpal[cl]; out[..., 3] = np.where(sol, 255, 0)
        # thick outer outline, like Jasper's
        m = sol.copy()
        for _ in range(outline):
            grow = m.copy()
            grow[1:] |= m[:-1]; grow[:-1] |= m[1:]; grow[:, 1:] |= m[:, :-1]; grow[:, :-1] |= m[:, 1:]
            ring = grow & ~m
            out[ring, :3] = OUTLINE; out[ring, 3] = 255
            m = grow
        # the existing edge pixels darken to the outline too, so the line reads as one bold stroke
        edge = sol & ~(np.roll(sol, 1, 0) & np.roll(sol, -1, 0) & np.roll(sol, 1, 1) & np.roll(sol, -1, 1))
        dark = edge & ((out[..., :3].astype(int).sum(-1)) < 260)
        out[dark, :3] = OUTLINE
        res.append(out)
    Image.fromarray(np.concatenate(res, 1), "RGBA").save(out_path)


if __name__ == "__main__":
    remake(sys.argv[1], sys.argv[2])
