"""Cozy interface and everyday sounds (25 Nov), all made from scratch here: sine plucks, filtered noise and
additive "voices". Nothing is sampled from any other game.

Zachary's list (after the Stardew sound-design video): menus, inventory, the furnace, drinking, books and
letters, walking, and talking with residents. Each sound has a few takes that differ a little in pitch and
colour, so repeats never sound the same (main.gd plays a random take of name_1..name_8.ogg).

  click_1..3         menu button: a soft rounded pop
  ui_select_1..3     choosing something in a list: a tiny light tick
  page_tick_1..4     Prev / Next and the mouse wheel: a quick paper flick
  hotbar_1..3        picking a hotbar slot: a small wooden tock
  inv_pick_1..3      lifting an item in the bag: an upward "bwip"
  inv_drop_1..3      putting it down: a downward "bwop" that settles
  datapad_open_1     opening the datapad: two warm notes rising
  talk_1..4          a resident starting a line: a short sung syllable (ba, bo, be, bu), pitched per resident
  drink_1..2         two gulps and a swallow
  letter_open_1..2   unfolding a letter: crinkle and swish
  page_turn_1..3     the journal and books: one page turning over
  furnace_load_1..2  ore tipped in, then the flame catching
  furnace_fire.ogg   a seamless crackling loop played near a lit furnace
  step_base_1..6     the one footstep: a light, gritty tap, like a shoe on a packed path

Output: 44.1 kHz mono Ogg Vorbis in audio/.
Usage: python3 -I tools/cozy_sfx.py [GAME_DIR] [NAME ...]   (default: all)
       python3 -I tools/cozy_sfx.py GAME_DIR --demo OUT.wav  (every sound in a row, for listening)
"""
import os, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
TAU = 2 * np.pi


def secs(s):
    return int(SR * s)


def tt(n):
    return np.arange(n) / SR


def env(n, attack, decay, start=0.0):
    t = tt(n) - start
    a = np.clip(t / max(attack, 1e-5), 0, 1)
    return np.where(t < 0, 0.0, a * np.exp(-np.maximum(0, t - attack) / decay))


def band(x, lo, hi, order=2):
    if lo is None:
        sos = butter(order, hi, "lp", fs=SR, output="sos")
    elif hi is None:
        sos = butter(order, lo, "hp", fs=SR, output="sos")
    else:
        sos = butter(order, [lo, hi], "bp", fs=SR, output="sos")
    return sosfilt(sos, x)


def glide(n, f_from, f_to, over, shape=3.0):
    """Frequency curve sliding from f_from to f_to in `over` seconds (fast at first), then holding."""
    p = np.clip(tt(n) / over, 0, 1)
    k = 1 - (1 - p) ** shape
    return f_from + (f_to - f_from) * k


def osc(freq, phase0=0.0):
    return np.sin(TAU * np.cumsum(freq) / SR + phase0)


def place(dst, src, at):
    i = int(at * SR)
    if i >= len(dst):
        return
    m = min(len(src), len(dst) - i)
    dst[i:i + m] += src[:m]


def finish(x, peak=0.5, fade=0.01):
    x = np.asarray(x, dtype=np.float64)
    f = min(secs(fade), len(x) // 4)
    if f > 0:
        x[-f:] *= np.linspace(1, 0, f)
    x[:16] *= np.linspace(0, 1, 16)
    m = np.max(np.abs(x))
    return (x / m * peak if m > 0 else x).astype(np.float32)


def grains(n, count, span, width, rng, start=0.0, amp=(0.3, 1.0)):
    """Little noise specks scattered in time: crinkle, grit, crackle."""
    out = np.zeros(n)
    for _ in range(count):
        g = max(8, secs(rng.uniform(*width)))
        at = secs(start + rng.uniform(0, span))
        if at + g >= n:
            continue
        out[at:at + g] += rng.standard_normal(g) * np.hanning(g) * rng.uniform(*amp)
    return out


# ---------------------------------------------------------------- the menus

def click(k, rng):
    n = secs(0.07)
    f = glide(n, 2100, 1350, 0.009) * rng.uniform(0.96, 1.04)
    pop = osc(f) * env(n, 0.0008, 0.014)
    pop += 0.25 * osc(f * 2.02) * env(n, 0.0005, 0.006)
    tick = band(rng.standard_normal(n), 2500, 7000) * env(n, 0.0003, 0.0025) * 0.5
    body = osc(np.full(n, 420 * rng.uniform(0.95, 1.05))) * env(n, 0.001, 0.012) * 0.3
    return finish(pop + tick + body, 0.5)


def ui_select(k, rng):
    n = secs(0.05)
    f = glide(n, 3000, 2300, 0.006) * rng.uniform(0.96, 1.04)
    x = osc(f) * env(n, 0.0005, 0.008)
    x += band(rng.standard_normal(n), 3500, 9000) * env(n, 0.0002, 0.0015) * 0.35
    return finish(x, 0.4)


def page_tick(k, rng):
    n = secs(0.08)
    flick = band(rng.standard_normal(n), rng.uniform(1100, 1400), rng.uniform(3400, 4200)) * env(n, 0.003, 0.012)
    tk = osc(glide(n, 1300, 850, 0.01) * rng.uniform(0.94, 1.06)) * env(n, 0.0006, 0.006) * 0.6
    return finish(flick + tk, 0.42)


def hotbar(k, rng):
    n = secs(0.12)
    f0 = 880 * rng.uniform(0.97, 1.03)
    f = f0 * (1 + 0.08 * np.exp(-tt(n) / 0.004))
    x = osc(f) * env(n, 0.0008, 0.028)
    x += 0.35 * osc(f * 2.76) * env(n, 0.0005, 0.009)      # a woodblock's bright second mode
    x += band(rng.standard_normal(n), 1500, 5000) * env(n, 0.0003, 0.002) * 0.3
    return finish(x, 0.45)


def inv_pick(k, rng):
    n = secs(0.11)
    f = glide(n, 480, 1150, 0.05, 2.0) * rng.uniform(0.95, 1.05)
    x = osc(f) * env(n, 0.003, 0.035)
    x += 0.2 * osc(f * 2) * env(n, 0.002, 0.02)
    x += band(rng.standard_normal(n), 900, 3000) * env(n, 0.002, 0.015) * 0.25    # a little cloth/rustle
    return finish(x, 0.45)


def inv_drop(k, rng):
    n = secs(0.13)
    f = glide(n, 950, 430, 0.045, 2.0) * rng.uniform(0.95, 1.05)
    x = osc(f) * env(n, 0.002, 0.03)
    settle = np.zeros(n)
    place(settle, osc(np.full(secs(0.05), 190.0)) * env(secs(0.05), 0.001, 0.012), 0.032)
    place(settle, band(rng.standard_normal(secs(0.03)), 400, 2200) * env(secs(0.03), 0.0005, 0.006) * 0.5, 0.032)
    return finish(x + settle * 0.8, 0.45)


def datapad_open(k, rng):
    n = secs(0.6)
    x = np.zeros(n)
    for at, f0 in ((0.0, 784.0), (0.075, 1175.0)):              # G5 then D6
        m = secs(0.45)
        note = osc(np.full(m, f0)) + 0.18 * osc(np.full(m, f0 * 2)) + 0.05 * osc(np.full(m, f0 * 3))
        place(x, note * env(m, 0.004, 0.16), at)
    air = band(rng.standard_normal(n), 2000, 6000) * env(n, 0.04, 0.08) * 0.12
    return finish(x + air, 0.4, 0.05)


# ---------------------------------------------------------------- talking

VOWELS = {  # formant (Hz, width, strength) sets: a friendly, slightly rounded voice
    "a": ((760, 140, 1.0), (1250, 180, 0.55), (2600, 260, 0.18)),
    "o": ((520, 110, 1.0), (900, 150, 0.6), (2500, 260, 0.12)),
    "e": ((560, 120, 1.0), (1850, 200, 0.5), (2600, 260, 0.2)),
    "u": ((380, 100, 1.0), (850, 140, 0.45), (2350, 260, 0.1)),
}


def talk(k, rng):
    """A sung syllable from harmonics shaped by vowel formants. The formants slide up from closed lips at the
    start (a soft "b"). dialogue_box.gd plays one per text box at the speaker's own pitch."""
    vowel = "aoeu"[(k - 1) % 4]
    n = secs(0.15)
    t = tt(n)
    p = t / t[-1]
    contour = 1 + 0.07 * np.sin(np.pi * np.clip(p * 1.3, 0, 1)) - 0.03 * p      # up, then gently down
    f0 = 240 * rng.uniform(0.98, 1.02) * contour
    open_lips = 0.55 + 0.45 * np.clip(t / 0.025, 0, 1)
    phase = TAU * np.cumsum(f0) / SR
    x = np.zeros(n)
    for h in range(1, 24):
        fh = h * f0
        if fh.max() > 5500:
            break
        shape = sum(s * np.exp(-((fh - F * open_lips) / w) ** 2) for F, w, s in VOWELS[vowel])
        x += (shape + 0.02) * h ** -0.4 * np.sin(h * phase)
    a = np.clip(t / 0.012, 0, 1) * np.clip((t[-1] - t) / 0.06, 0, 1) ** 1.5
    return finish(x * a, 0.45, 0.005)


# ---------------------------------------------------------------- drinking, letters, books

def gulp(rng):
    n = secs(0.16)
    f = glide(n, 230, 520, 0.035, 1.5) * rng.uniform(0.9, 1.1)          # a bubble's pitch rises as it closes
    bubble = osc(f) * env(n, 0.004, 0.035)
    throat = osc(np.full(n, 115 * rng.uniform(0.9, 1.1))) * env(n, 0.006, 0.045) * 0.7
    slosh = band(rng.standard_normal(n), 250, 1100) * env(n, 0.01, 0.04) * 0.35
    return bubble + throat + slosh


def drink(k, rng):
    n = secs(0.72)
    x = np.zeros(n)
    place(x, gulp(rng), 0.0)
    place(x, gulp(rng) * 0.9, rng.uniform(0.24, 0.28))
    sw = secs(0.08)                                                 # the swallow: a soft closed "gk"
    place(x, band(rng.standard_normal(sw), 500, 1600) * env(sw, 0.002, 0.012) * 0.45, 0.5)
    place(x, osc(glide(sw, 300, 160, 0.03)) * env(sw, 0.003, 0.02) * 0.4, 0.5)
    return finish(x, 0.5, 0.04)


def swish(n, lo0, lo1, width, rng):
    """Noise through a band that sweeps upward: air moving past a sheet of paper."""
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    seg = secs(0.01)
    for i in range(0, n, seg):
        p = i / n
        lo = lo0 + (lo1 - lo0) * p
        blk = band(noise[max(0, i - seg * 4):i + seg], lo, lo * width)[-min(seg, n - i):]
        out[i:i + len(blk)] = blk
    return out


def letter_open(k, rng):
    n = secs(0.55)
    crinkle = band(grains(n, 38, 0.4, (0.0008, 0.003), rng, 0.02), 1800, 6500) * 1.1
    crinkle *= np.clip(tt(n) / 0.05, 0, 1)
    air = swish(n, 1200, 3000, 2.2, rng) * np.sin(np.pi * np.clip(tt(n) / 0.42, 0, 1)) * 0.4
    flap = np.zeros(n)
    f = secs(0.05)
    place(flap, band(rng.standard_normal(f), None, 700) * env(f, 0.002, 0.014) * 1.4, rng.uniform(0.38, 0.43))
    return finish(crinkle + air + flap, 0.42, 0.05)


def page_turn(k, rng):
    n = secs(0.4)
    bell = np.sin(np.pi * np.clip((tt(n) - 0.01) / 0.26, 0, 1)) ** 1.5
    air = swish(n, 800, 2800, 2.5, rng) * bell * 0.7
    crinkle = band(grains(n, 10, 0.22, (0.001, 0.003), rng, 0.02, (0.2, 0.6)), 2500, 8000) * 0.7
    flap = np.zeros(n)
    f = secs(0.05)
    place(flap, band(rng.standard_normal(f), 150, 900) * env(f, 0.002, 0.012) * 1.2, rng.uniform(0.26, 0.29))
    return finish(air + crinkle + flap, 0.42, 0.04)


# ---------------------------------------------------------------- the furnace

def furnace_load(k, rng):
    n = secs(1.0)
    x = np.zeros(n)
    for i in range(int(rng.uniform(6, 9))):                         # ore tipped in: dull stony clacks
        m = secs(0.04)
        f0 = rng.uniform(900, 1600)
        clack = band(rng.standard_normal(m), f0, f0 * 2.5) * env(m, 0.0004, rng.uniform(0.004, 0.009))
        clack += osc(np.full(m, f0 * 0.5)) * env(m, 0.0005, 0.006) * 0.4
        place(x, clack * rng.uniform(0.4, 1.0), 0.02 + i * rng.uniform(0.025, 0.045))
    w = secs(0.8)                                                   # then the flame catches: a soft "fwoomp"
    whoosh = band(rng.standard_normal(w), 120, 1400)
    whoosh = band(whoosh, None, 900) * np.clip(tt(w) / 0.12, 0, 1) ** 2 * np.exp(-np.maximum(0, tt(w) - 0.12) / 0.22)
    rumble = osc(np.full(w, 62.0) + 6 * np.sin(TAU * 3 * tt(w))) * np.clip(tt(w) / 0.1, 0, 1) * np.exp(-tt(w) / 0.35)
    place(x, whoosh * 1.6 + rumble * 0.5, 0.22)
    place(x, fire_crackles(secs(0.6), rng, 14) * 0.6, 0.35)
    return finish(x, 0.5, 0.12)


def fire_crackles(n, rng, per_sec):
    out = np.zeros(n)
    for _ in range(int(per_sec * n / SR)):
        at = rng.integers(0, n)
        if rng.random() < 0.75:                                     # a tiny bright snap
            m = secs(0.012)
            s = band(rng.standard_normal(m), 2000, 7500) * env(m, 0.0002, rng.uniform(0.0008, 0.002))
            a = rng.uniform(0.2, 1.0)
        else:                                                       # a rounder wood-ish pop
            m = secs(0.03)
            s = band(rng.standard_normal(m), 500, 2200) * env(m, 0.0005, rng.uniform(0.004, 0.008))
            a = rng.uniform(0.5, 1.2)
        idx = (at + np.arange(m)) % n                               # wrapped, so a loop never clicks at the seam
        out[idx] += s * a
    return out


def furnace_fire(k, rng):
    """4 s that loop seamlessly: a low breathing roar with snaps and pops on top."""
    n = secs(4.0)
    pad = secs(0.5)
    roar = band(rng.standard_normal(n + pad), 50, 380)
    head, tail = roar[:pad], roar[n:]
    body = roar[:n].copy()
    fade = np.linspace(0, 1, pad)
    body[:pad] = head * fade + tail * (1 - fade)                    # the tail run on into the head
    flutter = np.zeros(n)
    for hz in (0.5, 1.25, 2.0, 3.25):                               # whole cycles in 4 s, so it loops
        flutter += np.sin(TAU * hz * tt(n) + rng.uniform(0, TAU)) * rng.uniform(0.15, 0.3)
    body *= 0.75 + 0.25 * np.tanh(flutter)
    x = body * 2.4 + fire_crackles(n, rng, 9)
    m = np.max(np.abs(x))
    return (x / m * 0.45).astype(np.float32)


# ---------------------------------------------------------------- walking

def step_base(k, rng):
    """Light and gritty rather than a thud: a short pat, a few specks of grit and only a hint of body."""
    n = secs(0.09)
    pat = band(rng.standard_normal(n), rng.uniform(320, 400), rng.uniform(1700, 2100)) * env(n, 0.001, rng.uniform(0.008, 0.011))
    grit = band(grains(n, int(rng.uniform(6, 10)), 0.022, (0.0006, 0.0018), rng, 0.0), 1200, 4500)
    grit *= env(n, 0.0005, 0.018) * 0.8
    body = osc(np.full(n, rng.uniform(190, 230)) * (1 + 0.2 * np.exp(-tt(n) / 0.004))) * env(n, 0.0008, 0.012) * 0.6
    return finish(pat + grit + body, 0.5, 0.02)


SOUNDS = {  # name: (maker, takes)
    "click": (click, 3), "ui_select": (ui_select, 3), "page_tick": (page_tick, 4), "hotbar": (hotbar, 3),
    "inv_pick": (inv_pick, 3), "inv_drop": (inv_drop, 3), "datapad_open": (datapad_open, 1),
    "talk": (talk, 4), "drink": (drink, 2), "letter_open": (letter_open, 2), "page_turn": (page_turn, 3),
    "furnace_load": (furnace_load, 2), "furnace_fire": (furnace_fire, 0), "step_base": (step_base, 6),
}


def render(name, k):
    maker, _ = SOUNDS[name]
    seed = sum(ord(c) for c in name) * 1000 + k                     # fixed: the same file every run
    return maker(max(k, 1), np.random.default_rng(seed))


def save(x, path):
    subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "libvorbis", "-q:a", "6", path], input=x.tobytes(), check=True)


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "."
    rest = sys.argv[2:]
    if rest[:1] == ["--demo"]:
        parts = []
        gap = np.zeros(secs(0.35), np.float32)
        for name, (_, takes) in SOUNDS.items():
            if name == "furnace_fire":
                loop = render(name, 0)
                parts += [np.tile(loop, 2), gap, gap]
                continue
            for k in range(1, takes + 1):
                parts += [render(name, k), gap if name not in ("step_base",) else np.zeros(secs(0.18), np.float32)]
            parts += [gap, gap]
        data = np.concatenate(parts)
        subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        rest[1]], input=data.tobytes(), check=True)
        return
    for name in (rest or list(SOUNDS)):
        _, takes = SOUNDS[name]
        if takes == 0:
            save(render(name, 0), os.path.join(game, "audio", f"{name}.ogg"))
        for k in range(1, takes + 1):
            save(render(name, k), os.path.join(game, "audio", f"{name}_{k}.ogg"))
    print("cozy sounds written")


if __name__ == "__main__":
    main()
