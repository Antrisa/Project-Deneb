"""Fill pixels of background showing through inside a portrait (fully enclosed by the character) with the
colours around them, nearest first. Notches open to the outside are left alone: they are part of the
outline, and filling them drew black blocks along the edges."""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

def holes_of(op):
    # only background fully enclosed by the character: pockets open by a pixel are notches in the
    # outline, and filling them drew black blocks along the edges
    return ndimage.binary_fill_holes(op) & ~op


def lum(c):
    return 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]


def fill_cell(a, dark_lum=70):
    """Each enclosed pocket takes the colours around it (the most common neighbour, nearest first)."""
    a = a.copy()
    op = a[..., 3] > 0
    dark = op & (lum(a[..., :3].astype(float)) < dark_lum)
    holes = holes_of(op)
    lab, n = ndimage.label(holes)
    todo = np.zeros_like(op)
    for k in range(1, n + 1):
        m = lab == k
        ring = ndimage.binary_dilation(m, np.ones((3, 3), bool)) & op
        todo |= m
    filled = todo.copy()
    count = int(todo.sum())
    have = op.copy()
    while todo.any():
        grow = ndimage.binary_dilation(have, np.ones((3, 3), bool)) & todo
        if not grow.any():
            break
        new = a.copy()
        for y, x in zip(*np.nonzero(grow)):
            ys, xs = slice(max(0, y - 1), y + 2), slice(max(0, x - 1), x + 2)
            nb = a[ys, xs][have[ys, xs]]
            vals, cnt = np.unique(nb.reshape(-1, 4), axis=0, return_counts=True)
            new[y, x] = vals[cnt.argmax()]
        a = new
        have |= grow; todo &= ~grow
    if count and dark.any():
        vals, cnt = np.unique(a[dark][:, :3], axis=0, return_counts=True)
        line = vals[cnt.argmax()]
        op2 = a[..., 3] > 0
        for y, x in zip(*np.nonzero(filled)):
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < a.shape[0] and 0 <= xx < a.shape[1] and not op2[yy, xx]:
                    a[y, x, :3] = line
                    break
    return a, count


if __name__ == "__main__":
    for path in sys.argv[1:]:
        s = np.array(Image.open(path).convert("RGBA"))
        total = 0
        for i in range(s.shape[1] // 128):
            cell, n = fill_cell(s[:, i * 128:(i + 1) * 128])
            s[:, i * 128:(i + 1) * 128] = cell
            total += n
        if total:
            Image.fromarray(s).save(path)
        print(os.path.relpath(path), total)
