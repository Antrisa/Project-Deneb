"""Animate the iris and the two visible faults on the painted Mother-Drone insert.

Pixel positions refer to art/prologue/mother_close.png (640 x 360). The three
strips share the same tight crop, placed at (122, 80) on the picture board.
Run python3 -I tools/dev/mother_close.py from the project root.
"""
from pathlib import Path
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parents[2] / "art/prologue"
LEFT, TOP, WIDTH, HEIGHT = 122, 80, 394, 165
yy, xx = np.indices((HEIGHT, WIDTH), dtype=float)
u = (xx + LEFT + .5 - 164.6) / 36.8
v = (yy + TOP + .5 - 198.3) / 37.8
radius = np.hypot(u, v)
azimuth = np.arctan2(v, u)
# The paths follow fractures in the painted shell. Each child starts where the
# light from the optic can reach it. The long upper branch ends at the crystal.
FAULTS = [
    (0, [(213,178),(239,174),(260,172),(278,170),(295,168),(314,166),(326,164),(337,159),
         (346,155),(355,152),(367,150),(382,140),(396,136),(418,138),(439,141),(454,144),(470,149),
         (478,148),(485,143),(491,136),(504,131)]),
    (113, [(326,164),(333,158),(339,153),(339,144),(344,138),(351,136),(357,132),(361,123),
           (363,117),(360,113),(358,105),(352,99),(351,92),(346,87)]),
    (133, [(347,155),(356,150),(366,148),(377,149),(385,154),(396,155),(405,156),(416,162),
           (427,169),(444,176)]),
]


def fault_distance():
    distance = np.full((HEIGHT, WIDTH), np.inf)
    for travelled, points in FAULTS:
        for a,b in zip(points, points[1:]):
            length = np.hypot(b[0]-a[0], b[1]-a[1])
            for f in np.linspace(0, 1, int(length*2)+2):
                x = round(a[0]+(b[0]-a[0])*f)-LEFT
                y = round(a[1]+(b[1]-a[1])*f)-TOP
                distance[y,x] = min(distance[y,x],travelled+f*length)
            travelled += length
    return distance


DIST = fault_distance()
FAR = DIST[np.isfinite(DIST)].max()


def frame(aperture, charge, wave=0.0):
    out = np.zeros((HEIGHT, WIDTH, 4),np.uint8)
    def paint(where, rgb):
        out[where] = (*bytes.fromhex(rgb),255)
    if aperture > 0:
        # Six overlapping curved shutter leaves reveal a recessed hexagonal pupil.
        eye = radius <= 1
        phase = (azimuth + 1.05*(1-radius)**2 - .57*aperture) / (np.pi/3)
        sector = np.floor(phase).astype(int)
        seam = phase-np.floor(phase)
        paint(eye, '44344f')
        paint(eye & ((sector % 6 == 0) | (sector % 6 == 5)), '543d5e')
        paint(eye & (v>.23) & (sector%2==0), '372b46')
        paint(eye & (seam<.045) & (radius>.14), '30253d')
        # The rim occludes the light as the opening moves, including during shutdown.
        hexagon = radius * np.cos((azimuth + .16 + np.pi/6) % (np.pi/3)-np.pi/6)
        opening = aperture*.77
        paint(eye & (hexagon < opening+.026), '261d35')
        paint(eye & (hexagon < opening), '584276')
        glass = np.hypot(u-.055, v-.065)
        paint((hexagon<opening) & (glass<opening*.89), '6a76a7')
        paint((hexagon<opening) & (glass<opening*.66+wave*.025), '73a7bf')
        paint((hexagon<opening) & (glass<opening*.38+wave*.03), 'ace1da')
        glint = ((u+.13)**2/.075**2 + (v+.23)**2/.047**2 < 1)
        paint((hexagon<opening) & glint, 'fff0cc')
    if charge > 0:
        lit = DIST <= charge*FAR
        paint(lit, 'af775f')
        paint(lit & (np.cos(np.minimum(DIST, FAR)*.036-wave*1.4)>.05), 'e4b778')
        paint(lit & (DIST>(charge*FAR-19)) & (charge<.99), 'f6db9d')
        paint(lit & (DIST<16) & (charge>.2), 'edd09e')
    return Image.fromarray(out)


def write_strip(name,frames):
    strip = Image.new("RGBA",(WIDTH*len(frames),HEIGHT))
    for idx,img in enumerate(frames):
        strip.paste(img,(WIDTH*idx,0))
    strip.save(OUT/(name+".png"), optimize=True)


if __name__ == "__main__":
    assert Image.open(OUT/"mother_close.png").size == (640,360)
    wake = [(0,0),(.025,0),(.115,0),(.33,.035),(.58,.12),
            (.77,.31),(.92,.55),(.98,.77),(1,.94),(1,1)]
    write_strip("mother_close_wake", [frame(a,c) for a,c in wake])
    breath = (0,.23,.58,.9,1,.75,.42,.15)
    write_strip("mother_close_pulse", [frame(1-.025*b,1,b) for b in breath])
    # For one beat the exhausted lens catches again, then the shutter settles.
    dim = [(1,1),(.96,.78),(.8,.57),(.62,.35),(.48,.15),
           (.29,.05),(.37,.035),(.19,0),(.06,0),(0,0)]
    write_strip("mother_close_dim", [frame(a,c) for a,c in dim])
