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
