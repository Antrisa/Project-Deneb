"""Pixel-art helpers for ship mock-ups (21 Nov 2026). Hard edges only: polygons are drawn without anti-aliasing."""
from PIL import Image, ImageDraw

CELL = 24
OUTLINE = (38, 37, 53, 255)

def hexc(s, a=255):
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)

def canvas(cols, rows):
    return Image.new("RGBA", (cols * CELL, rows * CELL), (0, 0, 0, 0))

def poly(im, pts, col):
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=hexc(col) if isinstance(col, str) else col)

def rect(im, x0, y0, x1, y1, col):
    ImageDraw.Draw(im).rectangle((x0, y0, x1, y1), fill=hexc(col) if isinstance(col, str) else col)

def ellipse(im, x0, y0, x1, y1, col):
    ImageDraw.Draw(im).ellipse((x0, y0, x1, y1), fill=hexc(col) if isinstance(col, str) else col)

def line(im, pts, col, w=1):
    ImageDraw.Draw(im).line([tuple(p) for p in pts], fill=hexc(col) if isinstance(col, str) else col, width=w)

def mirror_y(pts, h):
    return [(x, h - 1 - y) for x, y in pts]

def clip_to(im, mask_im):
    """Keep only pixels where mask_im is opaque."""
    a = im.getchannel("A")
    m = mask_im.getchannel("A").point(lambda v: 255 if v > 0 else 0)
    from PIL import ImageChops
    im.putalpha(ImageChops.multiply(a, m))
    return im

def outline(im, col=OUTLINE):
    """A 1-px outline round the opaque shape (outside it)."""
    w, h = im.size
    src = im.load()
    out = im.copy()
    o = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 0:
                        o[x, y] = col
                        break
    return out

def inner_edge(im, col, side="bottom", width=1):
    """Shade the opaque pixels that touch transparency on one side (light from the top left)."""
    w, h = im.size
    src = im.copy().load()
    o = im.load()
    d = {"bottom": (0, 1), "top": (0, -1), "right": (1, 0), "left": (-1, 0)}[side]
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                continue
            for k in range(1, width + 1):
                nx, ny = x + d[0] * k, y + d[1] * k
                if not (0 <= nx < w and 0 <= ny < h) or src[nx, ny][3] == 0:
                    o[x, y] = hexc(col) if isinstance(col, str) else col
                    break

def layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))

def stamp(base, top):
    base.alpha_composite(top)
    return base


def mask_of(size, draw):
    """A mask (L image) from a drawing function given an RGBA layer."""
    m = layer(size)
    draw(m)
    return m.getchannel("A").point(lambda v: 255 if v > 0 else 0)


def paint_shaded(im, m, lite, mid, shade=None, split=None):
    """Fill a mask with a top-lit two-tone (lite above the split line, mid below), shade along the bottom edge."""
    w, h = im.size
    mp = m.load()
    ys = [y for y in range(h) for x in range(w) if mp[x, y]]
    if not ys:
        return
    cy = split if split is not None else (min(ys) + max(ys)) / 2
    px = im.load()
    L, M = hexc(lite), hexc(mid)
    S = hexc(shade) if shade else None
    for y in range(h):
        for x in range(w):
            if mp[x, y]:
                px[x, y] = L if y < cy else M
                if S and (y + 1 >= h or not mp[x, y + 1] or (y + 2 < h and not mp[x, y + 2])):
                    px[x, y] = S


def shape(im, pts, lite, mid, shade=None, split=None):
    m = mask_of(im.size, lambda L: poly(L, pts, (255, 255, 255, 255)))
    paint_shaded(im, m, lite, mid, shade, split)


def oval(im, box, lite, mid, shade=None, split=None):
    m = mask_of(im.size, lambda L: ellipse(L, *box, (255, 255, 255, 255)))
    paint_shaded(im, m, lite, mid, shade, split)
