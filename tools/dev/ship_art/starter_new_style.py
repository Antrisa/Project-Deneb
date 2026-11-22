"""The starter fighter in the new cozy style, with its cut-away."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from render import Canvas, glow_dot
from PIL import Image

W, H = 168, 96
def my(pts): return [(x, H - 1 - y) for x, y in pts]
BODY = [(24, 22), (140, 22), (152, 30), (167, 45), (167, 50), (152, 65), (140, 73), (24, 73)]
WING = [(58, 26), (114, 26), (84, 2), (80, 0), (60, 0), (54, 2)]
BAND = [(84, 26), (96, 26), (76, 1), (70, 1)]
FLAP = [(58, 26), (70, 26), (64, 3), (56, 3)]
PODS = ((26, 45), (50, 69))
ROOMS = [(1, 1, 1, 2), (2, 1, 2, 1), (2, 2, 1, 1), (3, 2, 1, 1), (4, 1, 1, 2), (5, 1, 1, 2)]
DOORS = [((1, 1), (2, 1)), ((1, 2), (2, 2)), ((2, 1), (2, 2)), ((3, 1), (3, 2)), ((3, 1), (4, 1)), ((3, 2), (4, 2)), ((4, 1), (5, 1))]

def hull_canvas():
    c = Canvas(W, H, seed=3)
    c.part(polygon=WING, profile="bevel", radius=3, z=1, height=3.5, material="hull", tilt=(0.0, 0.12))
    c.part(polygon=my(WING), profile="bevel", radius=3, z=1, height=3.5, material="hull", tilt=(0.0, -0.12))
    c.part(polygon=BODY, profile="round", radius=5, z=2, height=6, material="hull")
    for (y0, y1) in PODS:
        c.part(rect=(0, y0, 56, y1), profile="tube", z=4, height=11, material="metal")
    c.part(ellipse=(114, 32, 152, 63), profile="round", radius=3, z=7, height=2, material="metal")
    c.part(ellipse=(117, 35, 149, 60), profile="dome", z=7, height=7, material="glass")
    for y in (9, H - 1 - 9):
        c.part(rect=(72, y - 2, 94, y + 2), profile="tube", z=4, height=3, material="metal")
    for pts in (BAND, my(BAND)):
        c.paint(polygon=pts, material="orange", where={"hull"})
    for x in (60, 80):
        c.paint(polygon=[(x, 22), (x + 8, 22), (x + 17, 47), (x + 9, 47)], material="orange", where={"hull"})
        c.paint(polygon=[(x + 9, 48), (x + 17, 48), (x + 8, 73), (x, 73)], material="orange", where={"hull"})
    c.paint(polygon=[(158, 40), (167, 45), (167, 50), (158, 55)], material="orange", where={"hull"})
    for (y0, y1) in PODS:
        c.paint(rect=(16, y0, 21, y1), material="orange", where={"metal"})
    for pts in (FLAP, my(FLAP)):
        c.seam([pts[1], pts[2]], depth=0.8)
    c.seam([(50, 24), (50, 71)]); c.seam([(112, 25), (112, 70)])
    c.groove_rect(28, 30, 44, 42, depth=0.7)          # a hatch on the back
    for (y0, y1) in PODS:
        c.seam([(10, y0 + 1), (10, y1 - 1)]); c.seam([(40, y0 + 1), (40, y1 - 1)])
    c.vents(96, 33, 3, 3, 16, 2)
    c.vents(96, 56, 3, 3, 16, 2)
    c.rivets([(30 + i * 6, 25) for i in range(4)] + [(30 + i * 6, 70) for i in range(4)] + [(118 + i * 6, 26) for i in range(3)] + [(118 + i * 6, 69) for i in range(3)], size=2, rise=0.6)
    for (y0, y1) in PODS:
        c.recess(ellipse=(0, y0 + 3, 6, y1 - 3), depth=3, material="dark")
    return c

def lights(img):
    for (y0, y1) in PODS:
        cy = (y0 + y1) // 2
        for yy in range(cy - 4, cy + 5):
            glow_dot(img, 1, yy, "glow", 0)
        glow_dot(img, 2, cy, "glow", 1)
    glow_dot(img, 62, 2, "glow_green", 0); glow_dot(img, 62, H - 3, "glow_red", 0)
    return img

def interior_canvas():
    c = hull_canvas()
    # the rooms: cut down to deck plates
    for (cx, cy, cw, ch) in ROOMS:
        x0, y0 = cx * 24, cy * 24
        c.flatten(rect=(x0, y0, x0 + cw * 24 - 1, y0 + ch * 24 - 1), z=1.0, material="cream" if cx == 5 else "deck")
    # deck plates: one seam across each cell, and a bolt at the corners
    for (cx, cy, cw, ch) in ROOMS:
        x0, y0 = cx * 24, cy * 24
        for k in range(cw):
            for j in range(ch):
                xx, yy = x0 + k * 24, y0 + j * 24
                c.seam([(xx + 12, yy + 3), (xx + 12, yy + 20)], depth=0.4)
                c.rivets([(xx + 4, yy + 4), (xx + 19, yy + 4), (xx + 4, yy + 19), (xx + 19, yy + 19)], size=1, rise=0.5)
    # walls: raised ridges on room edges, with gaps for the doors
    import numpy as np
    wall = np.zeros((H, W), bool)
    def room_at(cell):
        for i, (cx, cy, cw, ch) in enumerate(ROOMS):
            if cx <= cell[0] < cx + cw and cy <= cell[1] < cy + ch:
                return i
        return -1
    for i, (cx, cy, cw, ch) in enumerate(ROOMS):
        for x in range(cx, cx + cw):
            for y in range(cy, cy + ch):
                x0, y0 = x * 24, y * 24
                if room_at((x + 1, y)) != i: wall[y0:y0 + 24, x0 + 22:x0 + 24] = True
                if room_at((x - 1, y)) != i: wall[y0:y0 + 24, x0:x0 + 2] = True
                if room_at((x, y + 1)) != i: wall[y0 + 22:y0 + 24, x0:x0 + 24] = True
                if room_at((x, y - 1)) != i: wall[y0:y0 + 2, x0:x0 + 24] = True
    for (a, b) in DOORS:
        (c1, r1), (c2, r2) = a, b
        if r1 == r2:
            x = max(c1, c2) * 24; y = r1 * 24 + 7
            wall[y:y + 10, x - 2:x + 2] = False
        else:
            y = max(r1, r2) * 24; x = c1 * 24 + 7
            wall[y - 2:y + 2, x:x + 10] = False
    c.part(shape=wall, profile="flat", z=1.0, height=5, material="cream", edge=True)
    # machines
    def box(x0, y0, x1, y1, mat="metal", h=4):
        c.part(rect=(x0, y0, x1, y1), profile="round", radius=2, z=1, height=h, material=mat, edge=True)
    for yy in (30, 54):
        box(29, yy, 42, yy + 11, "metal", 5); c.paint(rect=(32, yy + 3, 39, yy + 8), material="glow")   # engine cores
    box(53, 29, 90, 35, "metal", 4)                                                                         # gun rack
    c.paint(rect=(57, 31, 62, 33), material="glow_red"); c.paint(rect=(81, 31, 86, 33), material="glow_red")
    c.part(ellipse=(53, 53, 67, 67), profile="round", radius=2, z=1, height=2, material="metal", edge=True)           # drone pad
    c.paint(ellipse=(56, 56, 64, 64), material="yellow")
    c.part(ellipse=(78, 53, 90, 65), profile="dome", z=1, height=5, material="blue", edge=True)                          # oxygen tank
    c.part(ellipse=(100, 34, 115, 61), profile="dome", z=1, height=6, material="teal", edge=True)                        # shield generator
    c.part(rect=(124, 40, 132, 55), profile="round", radius=2, z=1, height=4, material="bronze", edge=True)             # the seat
    box(136, 34, 140, 61, "metal", 5); c.paint(rect=(137, 37, 139, 58), material="glow_teal")               # console
    return c

if __name__ == "__main__":
    hull = lights(hull_canvas().render())
    inside = lights(interior_canvas().render())
    hull.save("starter_new_hull.png"); inside.save("starter_new_interior.png")
    import os
    names = ["fridge", "chair_s", "dining_table", "dresser"]
    props = [Image.open(f"/home/claude/project-deneb/art/lunar/{n}.png").convert("RGBA") for n in names]
    sheet = Image.new("RGBA", (W * 2 + sum(p.width for p in props) + 60, 100), (177, 150, 121, 255))
    sheet.alpha_composite(hull, (4, 2)); sheet.alpha_composite(inside, (W + 12, 2)); x = 2 * W + 20
    for p in props:
        sheet.alpha_composite(p.crop((0, 0, p.width, min(p.height, 96))), (x, 2)); x += p.width + 8
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save("compare2.png")
