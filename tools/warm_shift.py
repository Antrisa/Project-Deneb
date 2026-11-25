"""Warm "C" colour shift for baked floors and walls (Zachary, 23 Nov 2026: props got the warm C style, walls and
floors to match). Light tones lean warm (toward yellow), dark tones lean purple, a little more saturation.
numpy only. build.py runs every floor_/walls_ image through warm() as it saves them. STRENGTH 0 turns it off."""
import numpy as np

STRENGTH = 1.0
SAT = 1.18


def _rgb_to_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1); mn = rgb.min(-1); d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-9
    rc = np.where(m, (mx - r) / np.where(m, d, 1), 0); gc = np.where(m, (mx - g) / np.where(m, d, 1), 0)
    bc = np.where(m, (mx - b) / np.where(m, d, 1), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
    h = np.where(m, (h / 6.0) % 1.0, 0.0)
    s = np.where(mx > 1e-9, d / np.where(mx > 1e-9, mx, 1), 0.0)
    return h, s, mx


def _hsv_to_rgb(h, s, v):
    i = np.floor(h * 6.0).astype(int) % 6
    f = h * 6.0 - np.floor(h * 6.0)
    p = v * (1 - s); q = v * (1 - s * f); t = v * (1 - s * (1 - f))
    r = np.choose(i, [v, q, p, p, t, v]); g = np.choose(i, [t, v, v, q, p, p]); b = np.choose(i, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1)


def warm_array(a, strength=None):
    k = STRENGTH if strength is None else strength
    if k <= 0:
        return a
    rgb = a[..., :3].astype(float) / 255.0
    h, s, v = _rgb_to_hsv(rgb)
    l = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    target = np.where(l > 0.5, 0.13, 0.75)
    pull = np.abs(l - 0.5) * 0.5 * (0.5 + s) * k
    dh = ((target - h + 0.5) % 1.0) - 0.5
    h2 = (h + dh * pull) % 1.0
    s2 = np.clip(s * (1 + (SAT - 1) * k) + np.where(s > 0.05, 0.05, 0.02) * k, 0, 1)
    out = a.copy()
    out[..., :3] = (_hsv_to_rgb(h2, s2, v) * 255 + 0.5).astype(np.uint8)
    return out


def warm(img):
    """A PIL image in, the same mode out."""
    from PIL import Image
    mode = img.mode
    a = np.asarray(img.convert("RGBA"))
    return Image.fromarray(warm_array(a), "RGBA").convert(mode)


def runtime_copies(root):
    """Warm copies of the pictures the game draws itself at runtime (not baked): the eight floor materials that
    lunar_ground.gd uses for the concourse roof, walls and moon surface. The originals stay as they are, because
    bake_floor reads them too and warms its own output. Written to art/lunar/warm/."""
    import os
    from PIL import Image
    src = os.path.join(root, "art", "lunar")
    dst = os.path.join(src, "warm")
    os.makedirs(dst, exist_ok=True)
    n = 0
    for i in range(8):
        f = os.path.join(src, "material_%d.png" % i)
        if os.path.exists(f):
            warm(Image.open(f)).save(os.path.join(dst, "material_%d.png" % i)); n += 1
    return n
