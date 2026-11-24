"""Fill pixels of background showing through inside a portrait (enclosed by the character, or by the
character plus a one-pixel gap) with the colours around them, nearest first."""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

def holes_of(op):
    h = ndimage.binary_fill_holes(op) & ~op
    pad = np.pad(op, 2)
    clo = ndimage.binary_closing(pad, np.ones((3, 3), bool))[2:-2, 2:-2]
    h2 = ndimage.binary_fill_holes(clo) & ~op
    # keep the near-enclosed pockets only where they are more than a notch in the outline
    lab, n = ndimage.label(h2 & ~h)
    for k in range(1, n + 1):
        m = lab == k
        if m.sum() >= 3:
            h |= m
    return h

def fill_cell(a):
    a = a.copy()
    op = a[..., 3] > 0
    todo = holes_of(op)
    n = int(todo.sum())
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
    return a, n

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
