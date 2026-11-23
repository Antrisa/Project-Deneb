# Preview of the Survey Level lounge view: a numpy copy of scripts/lounge_sky.gdshader (keep the two in
# step). Usage: python3 -I tools/dev/lounge_sky_preview.py OUT.png  (one strip per time and sky event)
import numpy as np, os, sys
from PIL import Image
W, H = 912, 64
PCX, PCY, PR = 455.0, 43.0, 36.0
def fract(x): return x - np.floor(x)
def hash2(x, y, s=0.0):
    x = np.asarray(x, np.float32); y = np.asarray(y, np.float32)
    a = fract(x * np.float32(0.1031) + np.float32(s * 0.1379)); b = fract(y * np.float32(0.1031) + np.float32(s * 0.1379)); c = a.copy()
    d = a * (b + 33.33) + b * (c + 33.33) + c * (a + 33.33)
    a, b, c = a + d, b + d, c + d
    return fract((a + b) * c)
def hash1(n):
    p = fract(np.float32(n) * np.float32(0.1031)); p = p * (p + 33.33); p = p * (p + p); return fract(p)
def vnoise(x, y, s=0.0):
    ix, iy = np.floor(x), np.floor(y); fx, fy = x - ix, y - iy
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy)
    a = hash2(ix, iy, s); b = hash2(ix + 1, iy, s); c = hash2(ix, iy + 1, s); d = hash2(ix + 1, iy + 1, s)
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy
def fbm(x, y, s=0.0):
    return 0.55 * vnoise(x, y, s) + 0.3 * vnoise(x * 2.1, y * 2.1, s + 3.0) + 0.15 * vnoise(x * 4.3, y * 4.3, s + 7.0)
def C(*rgb): return np.array(rgb, float) / 255.0
BG = [C(10, 15, 34), C(13, 21, 44), C(17, 28, 54), C(22, 35, 63), C(26, 40, 69)]
BANDS = [C(30, 49, 139), C(45, 69, 180), C(49, 108, 190), C(89, 138, 209), C(98, 162, 228), C(166, 216, 250), C(235, 239, 221), C(253, 248, 215), C(161, 189, 213), C(102, 190, 234), C(46, 133, 195), C(45, 86, 178)]
def sun_pos(minute, eclipse):
    # 06:00 enters at the left; sets behind the giant at 19:00 (on eclipse days it passes behind at
    # 12:45 and carries on to the right edge by 19:00). After that it stays hidden till morning.
    k = np.clip((minute - 360.0) / (1140.0 - 360.0), 0.0, 1.0)
    x = (24.0 + (888.0 - 24.0) * k) if eclipse else (24.0 + (PCX - 24.0) * k)
    y = 36.0 - 22.0 * np.sin(np.pi * k) if eclipse else 40.0 - 18.0 * np.sin(np.pi * k * 0.9)
    up = (minute >= 360.0) & (minute <= 1170.0)
    return x, y, up
def render(minute, t, event):
    px, py = np.meshgrid(np.arange(W, dtype=float), np.arange(H, dtype=float))
    row = np.clip(py, 3, 59)
    band = np.select([row < 12, row < 27, row < 42, row < 57], [0, 1, 2, 3], 4).astype(int)
    col = np.stack([BG[b] for b in band.ravel()]).reshape(H, W, 3)
    night = 1.0 - np.clip((np.abs(minute - 750.0) - 390.0) / 90.0, 0.0, 1.0)  # 1 by day, 0 at night
    night = 1.0 - night
    # stars: fixed, a few twinkle
    h = hash2(px, py, 1.0)
    star = h > 0.985 - 0.006 * night
    tw = 0.75 + 0.25 * np.sin(t * (1.0 + 3.0 * hash2(px, py, 2.0)) + 6.28 * hash2(px, py, 3.0))
    bright = np.where(hash2(px, py, 4.0) > 0.85, 1.0, 0.55) * np.where(hash2(px, py, 5.0) > 0.6, tw, 1.0)
    scol = np.where((hash2(px, py, 6.0) > 0.7)[..., None], C(190, 215, 255), C(235, 240, 255))
    col = np.where(star[..., None], col * (1 - bright[..., None] * 0.8) + scol * bright[..., None] * 0.8, col)
    # violet gas cloud
    if event == "gas_cloud":
        g = fbm(px / 40.0 + t * 0.01, py / 18.0, 11.0) * np.clip((px - 520.0) / 200.0, 0, 1) * np.clip((880.0 - px) / 80.0, 0, 1)
        g = np.floor(np.clip(g - 0.35, 0, 1) * 8.0) / 8.0 * 1.6
        col = col * (1 - g[..., None] * 0.6) + C(120, 70, 170) * g[..., None] * 0.6
    if event == "storm":
        s = fbm(px / 50.0 - t * 0.03, py / 20.0 + t * 0.01, 21.0)
        s = np.floor(np.clip(s - 0.3, 0, 1) * 6.0) / 6.0
        col = col * (1 - s[..., None] * 0.55) + C(40, 160, 150) * s[..., None] * 0.55
        flash = float(hash1(np.floor(t * 3.0) * 12.9898) > 0.8)
        lx = 100.0 + 700.0 * hash1(np.floor(t * 3.0) * 78.233)
        bolt = (np.abs(px - lx - 6.0 * np.sin(py * 0.7 + np.floor(t * 3.0))) < 0.8) & (py > 6) & (py < 40)
        col = np.where((bolt & (flash > 0))[..., None], C(220, 250, 255), col)
        col = col + flash * 0.05 * s[..., None]
    # comet, fixed, tail shimmering, pointing away from the sun
    if event == "comet":
        hx, hy = 690.0, 22.0
        dx, dy = px - hx, py - hy
        along = dx; across = dy - dx * 0.12
        tail = (along > 0) & (along < 70) & (np.abs(across) < 1.0 + along * 0.06)
        fade = np.clip(1.0 - along / 70.0, 0, 1) * (0.7 + 0.3 * np.sin(along * 0.5 - t * 2.0))
        col = np.where(tail[..., None], col + C(150, 190, 220) * (fade * 0.6)[..., None], col)
        head = dx * dx + dy * dy < 3.0
        col = np.where(head[..., None], C(240, 250, 255), col)
    # the sun, behind the giant
    sx, sy, up = sun_pos(minute, event == "eclipse")
    if up:
        d = np.sqrt((px - sx) ** 2 + (py - sy) ** 2)
        glow = np.clip(1.0 - d / 18.0, 0, 1)
        glow = np.floor(glow * 4.0) / 4.0
        col = col + C(255, 130, 50) * (glow * 0.6)[..., None]
        col = np.where((d < 7.5)[..., None], C(255, 190, 90), col)
        col = np.where((d < 5.0)[..., None], C(255, 236, 190), col)
    # the giant: bands drift, the turquoise storm turns, lit from the sun's side
    dxp, dyp = (px - PCX) / PR, (py - PCY) / PR
    rr = dxp * dxp + dyp * dyp
    inside = rr < 1.0
    z = np.sqrt(np.clip(1.0 - rr, 0, 1))
    lon = np.arctan2(dxp, z) + t * 0.02
    lat = dyp
    turb = fbm(lon * 3.0, lat * 9.0, 31.0) - 0.5
    b = lat * 5.0 + turb * 1.6 + 0.4 * np.sin(lon * 2.0 + lat * 7.0)
    idx = np.floor(fract(b * 0.5) * len(BANDS)).astype(int) % len(BANDS)
    pcol = np.stack([BANDS[i] for i in idx.ravel()]).reshape(H, W, 3)
    # storm spot
    slon = fract((lon - 0.6) / 6.2832 + 0.5) - 0.5
    sd = (slon * 6.2832 / 0.35) ** 2 + ((lat - 0.32) / 0.12) ** 2
    pcol = np.where((sd < 1.0)[..., None], np.where((sd < 0.45)[..., None], C(102, 190, 234), C(46, 133, 195)), pcol)
    if up:
        L = np.array([sx - PCX, sy - PCY, 0.0]); L[2] = 70.0 * np.cos(np.pi * np.clip((minute - 360) / 780, 0, 1))
        if event == "eclipse": L[2] = 70.0 * np.cos(np.pi * np.clip((minute - 360) / 780 * 2.0, 0, 2))
        L = L / np.linalg.norm(L)
        lit = dxp * L[0] + dyp * L[1] + z * L[2]
    else:
        lit = np.full_like(dxp, -1.0)
    shade = np.clip(lit * 1.4 + 0.3, 0.0, 1.0)
    shade = np.floor(shade * 5.0) / 5.0 * 0.82 + 0.18
    if up:
        sdx, sdy = sx - PCX, sy - PCY
        sl = np.sqrt(sdx * sdx + sdy * sdy)
        near = np.clip(1.0 - (sl - PR) / 60.0, 0, 1)
        face = np.clip((dxp * sdx + dyp * sdy) / sl, 0, 1)
        rim = np.clip(1.0 - z * 3.0, 0, 1) * face * near
        rim = np.floor(rim * 3.0) / 3.0
    else:
        rim = np.zeros_like(z)
    pcol = pcol * shade[..., None] + C(10, 20, 50) * ((1 - shade) * 0.6)[..., None] + C(255, 190, 110) * (rim * 0.9)[..., None]
    if event == "aurora" and night > 0.2:
        a = np.clip(1.0 - np.abs(lat + 0.62 + 0.05 * np.sin(lon * 9.0 + t * 0.8)) / 0.08, 0, 1)
        pcol = pcol + C(90, 255, 160) * (a * 0.7 * night)[..., None]
    if event == "transit":
        k = np.clip((minute - 600.0) / 360.0, 0, 1)
        mx, my = PCX - 40.0 + 80.0 * k, 22.0
        md = (px - mx) ** 2 + (py - my) ** 2
        sh = (px - mx - 3.0) ** 2 + (py - my - 4.0) ** 2 < 9.0
        pcol = np.where((sh & inside)[..., None], pcol * 0.35, pcol)
    col = np.where(inside[..., None], pcol, col)
    if event == "transit":
        col = np.where((md < 9.0)[..., None], C(60, 58, 70), col)
        col = np.where(((md < 9.0) & (px - mx < -1) & (py - my < -1))[..., None], C(120, 115, 125), col)
    # shooting stars
    period = 1.6 if event == "meteors" else (7.0 if night > 0.5 else 14.0)
    for layer in range(2 if event == "meteors" else 1):
        slot = np.floor(t / period + layer * 0.5)
        ph = fract(t / period + layer * 0.5)
        go = hash1(slot * 91.7 + layer * 13.0) < (0.9 if event == "meteors" else 0.6)
        if go and ph < 0.3:
            x0 = 40.0 + 820.0 * hash1(slot * 12.3 + layer)
            y0 = 4.0 + 16.0 * hash1(slot * 45.1 + layer)
            dirx = -1.0 if hash1(slot * 7.7 + 3.0) < 0.5 else 1.0
            prog = ph / 0.3 * 40.0
            hx, hy = x0 + dirx * prog, y0 + prog * 0.45
            ax, ay = px - hx, py - hy
            along = -(ax * dirx + ay * 0.45) / np.sqrt(1.2025)
            across = np.abs(ax * 0.45 - ay * dirx) / np.sqrt(1.2025)
            trail = (along >= 0) & (along < 12.0) & (across < 0.7)
            f = np.clip(1.0 - along / 12.0, 0, 1) * np.clip(1.0 - (ph / 0.3 - 0.7) / 0.3, 0, 1)
            col = np.where(trail[..., None], col + C(220, 235, 255) * f[..., None], col)
    # the frame on top
    return np.clip(col, 0, 1)
if __name__ == "__main__":
    frame = np.array(Image.open(os.path.join(os.path.dirname(__file__), '..', '..', 'art', 'lunar', 'lounge_sky', 'frame.png')).convert('RGBA')).astype(float) / 255
    shots = [(420, 3, 'clear'), (780, 3, 'clear'), (1080, 3, 'clear'), (1150, 3.1, 'clear'), (1300, 4, 'aurora'),
             (765, 3, 'eclipse'), (720, 5, 'transit'), (800, 2, 'gas_cloud'), (900, 2.2, 'meteors'), (1300, 1.4, 'storm'), (900, 3, 'comet')]
    rows = []
    for m, t, ev in shots:
        c = render(m, t, ev)
        c = c * (1 - frame[..., 3:4]) + frame[..., :3] * frame[..., 3:4]
        rows.append((c * 255).astype(np.uint8))
    out = np.concatenate([np.concatenate([r, np.zeros((4, W, 3), np.uint8)]) for r in rows])
    Image.fromarray(out).save(sys.argv[1])
