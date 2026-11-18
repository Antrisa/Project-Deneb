"""Shrink double-detail pixel art (32 art pixels per tile) to the 24-per-tile grid, as a starting point.

A plain 75% resize blurs pixel art, and nearest-neighbour drops every fourth row and column. This
averages each block, then snaps every pixel back to a colour the original used and makes the alpha
hard again, so the result is clean pixel art at the right size that an artist can tidy up.

    python3 tools/dev/to24.py in.png out.png            # one file
    import to24; to24.shrink(Image) -> Image             # from other tools
"""
import sys
import numpy as np
from PIL import Image

RATIO = 24 / 32


def new_size(w, h, frames=1):
    """The 24-grid size for a picture w x h (frames side by side, each frame scaled on its own)."""
    fw = w // frames
    return max(1, round(fw * RATIO)) * frames, max(1, round(h * RATIO))


def _palette(a):
    """The colours the original really uses (most common first, at most 256)."""
    px = a.reshape(-1, 4)
    px = px[px[:, 3] >= 128][:, :3]
    if len(px) == 0:
        return np.zeros((1, 3), np.int32)
    cols, counts = np.unique(px, axis=0, return_counts=True)
    order = np.argsort(-counts)
    return cols[order][:256].astype(np.int32)


def shrink(img, frames=1):
    img = img.convert("RGBA")
    w, h = img.size
    tw, th = new_size(w, h, frames)
    fw, tfw = w // frames, tw // frames
    out = Image.new("RGBA", (tw, th))
    pal = _palette(np.asarray(img))
    for f in range(frames):
        part = img.crop((f * fw, 0, (f + 1) * fw, h))
        a = np.asarray(part).astype(np.float32)
        # Average colour weighted by alpha, so transparent edges don't darken the outline.
        rgb = a[..., :3] * (a[..., 3:4] / 255.0)
        pre = Image.fromarray(np.concatenate([rgb, a[..., 3:4]], -1).clip(0, 255).astype(np.uint8), "RGBA")
        small = np.asarray(pre.resize((tfw, th), Image.BOX)).astype(np.float32)
        alpha = small[..., 3]
        col = small[..., :3] / np.maximum(alpha[..., None] / 255.0, 1e-3)
        d = ((col[:, :, None, :] - pal[None, None, :, :]) ** 2).sum(-1)
        snapped = pal[d.argmin(-1)]
        res = np.zeros((th, tfw, 4), np.uint8)
        res[..., :3] = snapped
        res[..., 3] = np.where(alpha >= 110, 255, 0)
        out.paste(Image.fromarray(res, "RGBA"), (f * tfw, 0))
    return out


def shrink_tileable(img):
    """For seamless floor and wall textures (64x64 -> 48x48): wrap the edges so it still tiles."""
    img = img.convert("RGBA")
    w, h = img.size
    big = Image.new("RGBA", (w * 3, h * 3))
    for i in range(3):
        for j in range(3):
            big.paste(img, (i * w, j * h))
    s = shrink(big)
    tw, th = new_size(w, h)
    return s.crop((tw, th, tw * 2, th * 2))


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    shrink(Image.open(src)).save(dst)
