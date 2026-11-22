# The title screen's easter egg needs to know which pixels of the fighter are its intact wing (the far one).
# This re-creates the pack's fighter render (source/fighter_model.py on fighter_geometry.py in
# Echo_Landing_Title_Screen.zip) with each face tagged wing or body, checks it against fighter.png pixel for
# pixel, and writes the wing's pixels as a mask. It also prints the wing's middle and root for title_scene.gd.
#   python3 tools/dev/title_wing_mask.py title/scene/fighter.png title/scene/fighter_wing.png
import math, sys, numpy as np
from PIL import Image, ImageFilter
PAL = ['ink','dark','shadow','iron','metal','edge','trim','cream','sun','shade','rust','orange','light','gold','glassdark','glasst','glass','aqua','ice']
HEX = {'ink':'2c2336','dark':'38293f','shadow':'564258','iron':'776575','metal':'9c8493','edge':'bd9da6','trim':'d4b5a8','cream':'f1d6af','sun':'ffebc9','shade':'bba4a4','rust':'ae471d','orange':'ed651c','light':'ff902c','gold':'ffc25c','glassdark':'124553','glasst':'175864','glass':'1c7b83','aqua':'58b9b1','ice':'ccebe1'}
colors = np.array([tuple(bytes.fromhex(HEX[k])) for k in PAL], np.uint8)
CRAFT = []
GROUP = ['body']
def face(v, c): CRAFT.append((v, c, GROUP[0]))
def cross_loft(rings, cols, end=None):
    for i in range(len(rings) - 1):
        for j in range(len(rings[i])):
            k = (j + 1) % len(rings[i])
            c = cols(i, j) if callable(cols) else cols[j]
            face([rings[i][j], rings[i + 1][j], rings[i + 1][k], rings[i][k]], c)
    if end: face(rings[0], end); face(rings[-1], end)
def wing(y, c):
    s = (abs(y) - 9) / 40; trail = -1 + 6 * s; lead = 55 - 34 * s
    return (trail + (lead - trail) * c, y, .8 + 1.6 * (1 - abs(2 * c - 1)) + .4 * s)
def lower(v): return (v[0], v[1], v[2] - 2.4)
def buildwing(side, broken):
    cs = [0, .14, .3, .47, .63, .82, 1]
    edge = [33.5, 32, 34, 31.7, 34.4, 33, 35.5] if broken else [49] * 7
    for j, (a, b) in enumerate(zip(cs, cs[1:])):
        for lo, hi in [(9, 19), (19, 27), (27, 31), (31, None)]:
            e0 = edge[j] if hi is None else hi; e1 = edge[j + 1] if hi is None else hi
            k = 'orange' if hi == 31 else ('trim' if j == 0 else 'sun' if j == 5 else 'cream')
            face([wing(side * lo, a), wing(side * lo, b), wing(side * e1, b), wing(side * e0, a)], k)
        p, q = wing(side * edge[j], a), wing(side * edge[j + 1], b)
        face([p, q, lower(q), lower(p)], 'shadow' if broken else 'metal')
    for c in [0, 1]:
        u, v = wing(side * 9, c), wing(side * edge[-1 if c else 0], c)
        face([u, v, lower(v), lower(u)], 'iron' if c == 0 else 'edge')
    if broken:
        for c in [.23, .72]:
            p = np.array(wing(32, c)); q = np.array(wing(36.7, c))
            def end(v): return [(v[0] + i, v[1], v[2] + z - 1.1) for i, z in [(-1.25, -.5), (1.25, -.5), (1.25, .5), (-1.25, .5)]]
            cross_loft([end(p), end(q)], ['shadow', 'iron', 'edge', 'metal'], 'iron')
def ring(x, y, w, z, h): return [(x, y + w * i, z + h * j) for i, j in [(-.75, 1), (.75, 1), (1, .66), (1, -.62), (.72, -1), (-.72, -1), (-1, -.62), (-1, .66)]]
def engine(side):
    y = side * 8.6
    sections = [(-14, 7.4, .1, 6.45), (-8, 7.5, .55, 6.6), (1, 7.7, 1.8, 6.0), (10, 7.0, 2.4, 6.3), (36, 6.4, 2.2, 6.0), (49, 4.4, 2.1, 4.5)]
    rings = [ring(x, y, w, z, h) for x, w, z, h in sections]
    def cols(i, j):
        if i < 2: return ['metal', 'iron', 'shadow', 'dark', 'dark', 'shadow', 'iron', 'edge'][j]
        return ['orange', 'rust', 'metal', 'iron', 'shadow', 'iron', 'edge', 'light'][j] if i < 4 else ['cream', 'trim', 'edge', 'iron', 'dark', 'iron', 'trim', 'sun'][j]
    cross_loft(rings, cols)
    outer = ring(-14.12, y, 7.36, .1, 6.40); inner = ring(-14.14, y, 6.05, .1, 4.74)
    for j in range(8):
        k = (j + 1) % 8
        face([outer[j], outer[k], inner[k], inner[j]], 'metal' if j in [0, 7] else 'iron')
    face(inner, 'dark')
    face([(-14.23, y - 3.4, -1.2), (-14.23, y + 2.4, -1.2), (-14.23, y + 2.4, .0), (-14.23, y - 3.4, .0)], 'rust')
def keel():
    sections = [(-13.2, 1.1, 1, 4.7), (4, 2, 3, 4.9), (32, 4.1, 4.4, 4.1), (52, 8.8, 3.3, 4.6), (66, 8.9, 2, 4.2), (84, 5.8, 1.0, 3.0), (110, 1, 0, .8)]
    cross_loft([ring(x, 0, w, z, h) for x, w, z, h in sections], ['cream', 'trim', 'metal', 'shadow', 'iron', 'iron', 'edge', 'sun'], 'trim')
def grille():
    base = [(11, -4.8, 9.95), (11, 4.8, 9.95), (33, 4.8, 10.35), (33, -4.8, 10.35)]
    cross_loft([[(x, y, z - 1.1) for x, y, z in base], base], ['iron', 'trim', 'edge', 'sun'])
    face(base, 'dark')
    for x in [17, 23.5, 29]:
        z = 9.96 + (x - 11) * .0182
        face([(x, -4.4, z + .1), (x, 4.4, z + .1), (x + 2, 4.4, z + .18), (x + 2, -4.4, z + .18)], 'iron')
def pod(side, cy, x, wingpod):
    z = 3.7 if wingpod else 6.1
    sections = [(x, 3.05, z + .2, 2.15), (x + 5, 3.3, z + .55, 2.8), (x + 14, 2.5, z + .65, 2.15), (x + 20, .9, z, 1.0)]
    rr = [ring(a, side * cy, w, h, d) for a, w, h, d in sections]
    cross_loft(rr, ['cream', 'trim', 'metal', 'shadow', 'iron', 'iron', 'trim', 'sun'])
    face(rr[0], 'edge'); face(ring(x - .08, side * cy, 2.4, z + .2, 1.45), 'dark')
def roofshape(sections, col, rear, front):
    rings = [[(x, y, z) for y, z in [(-w, b), (-w * .67, t), (w * .67, t), (w, b)]] for x, w, b, t in sections]
    for i in range(len(rings) - 1):
        for j in range(3):
            face([rings[i][j], rings[i + 1][j], rings[i + 1][j + 1], rings[i][j + 1]], col(i, j))
    face(rings[0], rear); face(rings[-1], front)
def cockpit():
    roofshape([(47, 7.5, 7.8, 9.3), (51, 9.5, 7.7, 11), (71, 8.8, 5.5, 8.8), (82, 4.7, 4.3, 5.7)], lambda i, j: ['sun', 'edge', 'metal'][j], 'iron', 'edge')
    window = [(49, 6.2, 9.55, 10.75), (56, 8, 10.1, 17), (66, 7.7, 9.7, 17), (75, 6.0, 7.4, 12.4), (80, 3.9, 5.8, 6.7)]
    def glass(i, j): return [['aqua', 'glass', 'glassdark'], ['aqua', 'glass', 'glassdark'], ['glass', 'glasst', 'glassdark'], ['glasst', 'glass', 'glassdark']][i][j]
    roofshape(window, glass, 'glasst', 'glasst')
    face([(56.3, -4.7, 17.12), (64.6, -4.6, 17.12), (63.8, -2.9, 17.12), (57.6, -2.9, 17.12)], 'ice')
    a, b = window[2], window[3]
    stripe = [a, tuple(v + .115 * (w - v) for v, w in zip(a, b))]
    roofshape([(x, w + .06, z + .10, h + .10) for x, w, z, h in stripe], lambda i, j: 'metal' if j != 2 else 'iron', 'glass', 'glasst')
def mesh(broken):
    CRAFT.clear()
    GROUP[0] = 'wing'; buildwing(-1, False)
    GROUP[0] = 'body'; buildwing(1, broken); keel()
    for side in [-1, 1]:
        engine(side)
        GROUP[0] = 'wing' if side == -1 else 'body'; pod(side, 21.4, 11, True)
        GROUP[0] = 'body'; pod(side, 10.6, 54, False)
    grille()
    start = len(CRAFT); cockpit()
    for i in range(start, len(CRAFT)):
        poly, paint, g = CRAFT[i]
        CRAFT[i] = ([(62 + (x - 62) * 1.20, y * 1.07, 7.5 + (z - 7.5) * .88) for x, y, z in poly], paint, g)
    return list(CRAFT)
def project(points):
    x, y, z = np.asarray(points, float).T
    a = math.radians(74); elev = math.radians(38); yaw = math.radians(32)
    across = y * math.cos(yaw) + x * math.sin(yaw)
    length = (x * math.cos(yaw) - y * math.sin(yaw)) * math.sin(elev) + z * math.cos(elev)
    return np.column_stack((length * math.cos(a) + across * math.sin(a), -length * math.sin(a) + across * math.cos(a), -(x * math.cos(yaw) - y * math.sin(yaw)) * math.cos(elev) + z * math.sin(elev)))
verts = np.vstack([np.array(p, float) for p, c, g in mesh(False)])
view = project(verts)[:, :2]; lo, hi = view.min(0), view.max(0)
def transform(poly, w, h):
    co = project(poly); fit = min((w - 6) / (hi[0] - lo[0]), (h - 5) / (hi[1] - lo[1]))
    co[:, :2] = (co[:, :2] - (lo + hi) * .5) * fit + np.array([w / 2, h / 2]); return co
W, H = 72, 49
depth = np.full((H, W), -np.inf); index = np.zeros((H, W), int); owner = np.zeros((H, W), int)
for poly, c, g in mesh(True):
    tri = transform(poly, W, H)
    for k in range(1, len(tri) - 1):
        a, b, e = tri[[0, k, k + 1]]
        x0, y0 = np.maximum([0, 0], np.floor(np.min([a[:2], b[:2], e[:2]], axis=0)).astype(int))
        x1, y1 = np.minimum([W - 1, H - 1], np.ceil(np.max([a[:2], b[:2], e[:2]], axis=0)).astype(int))
        if x1 < x0 or y1 < y0: continue
        y, x = np.mgrid[y0:y1 + 1, x0:x1 + 1]; x = x + .5; y = y + .5
        ax, ay = a[:2]; bx, by = b[:2]; ex, ey = e[:2]
        det = (by - ey) * (ax - ex) + (ex - bx) * (ay - ey)
        if abs(det) < 1e-6: continue
        u = ((by - ey) * (x - ex) + (ex - bx) * (y - ey)) / det; v = ((ey - ay) * (x - ex) + (ax - ex) * (y - ey)) / det; w = 1 - u - v
        z = u * a[2] + v * b[2] + w * e[2]
        region = depth[y0:y1 + 1, x0:x1 + 1]
        hit = (u >= -.00001) & (v >= -.00001) & (w >= -.00001) & (z >= region)
        region[hit] = z[hit]; index[y0:y1 + 1, x0:x1 + 1][hit] = PAL.index(c); owner[y0:y1 + 1, x0:x1 + 1][hit] = 1 if g == 'wing' else 2
mask = np.isfinite(depth)
alpha = np.asarray(Image.fromarray(np.uint8(mask) * 255).filter(ImageFilter.MaxFilter(3)))
mine = np.dstack([colors[index], alpha])
orig = np.asarray(Image.open(sys.argv[1]).convert('RGBA'))
same = (mine == orig).all(-1)
print('re-created sprite matches fighter.png on', same.sum(), 'of', same.size, 'pixels; differing opaque pixels:', int((~same & (orig[..., 3] > 0)).sum()))
# outline pixels (alpha from the dilation only) go with the wing when they touch only wing pixels
wing = owner == 1; body = owner == 2
near_wing = np.asarray(Image.fromarray(np.uint8(wing) * 255).filter(ImageFilter.MaxFilter(3))) > 0
near_body = np.asarray(Image.fromarray(np.uint8(body) * 255).filter(ImageFilter.MaxFilter(3))) > 0
outline = (alpha > 0) & ~mask
wing_full = wing | (outline & near_wing & ~near_body)
print('wing pixels', int(wing.sum()), '+ outline', int((wing_full & ~wing).sum()), '; body pixels', int(body.sum()))
# the root: wing pixels touching body pixels
root = wing & near_body
ys, xs = np.nonzero(root)
print('root pixels', len(xs), 'centre', round(xs.mean() + .5, 2), round(ys.mean() + .5, 2), 'x range', xs.min(), xs.max(), 'y range', ys.min(), ys.max())
ys, xs = np.nonzero(wing_full)
print('wing centre', round(xs.mean() + .5, 2), round(ys.mean() + .5, 2))
m = np.zeros((H, W, 4), np.uint8); m[..., :3] = 255; m[..., 3] = np.uint8(wing_full) * 255
Image.fromarray(m).save(sys.argv[2])
