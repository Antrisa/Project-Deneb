"""Made-up stand-in sounds (24 Nov 2026; Zachary: "please make up the rest and we can replace later ... get
creative making sounds"). Each one is built from tones and filtered noise and written as audio/<name>.wav.
A real sound dropped in as audio/<name>.ogg replaces it with no code change.
Run from the repo root: python3 -I tools/dev/madeup_sounds.py
"""
import os, wave
import numpy as np
from scipy.signal import lfilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SR = 44100
rng = np.random.default_rng(24)


def t_of(sec):
    return np.arange(int(SR * sec)) / SR


def noise(sec):
    return rng.uniform(-1, 1, int(SR * sec))


def lowpass(x, a):
    # one-pole smoothing; a near 0 = darker
    if np.ndim(a) == 0:
        return lfilter([a], [1, a - 1], x)
    y = np.empty_like(x); v = 0.0              # a sweeping filter, sample by sample
    for i, s in enumerate(x):
        v += (s - v) * a[i]; y[i] = v
    return y


def env(t, attack=0.004, decay=8.0):
    return np.minimum(1.0, t / attack) * np.exp(-decay * t)


def tone(f, sec, decay=6.0, attack=0.006, harm=(1.0, 0.0, 0.0)):
    t = t_of(sec)
    ph = 2 * np.pi * (np.cumsum(np.broadcast_to(f, t.shape)) / SR if np.ndim(f) else f * t)
    v = sum(h * np.sin(ph * (k + 1)) for k, h in enumerate(harm))
    return v * env(t, attack, decay)


def place(dst, x, at):
    i = int(at * SR); dst[i:i + len(x)] += x[:len(dst) - i]
    return dst


def save(name, x, peak=0.6):
    x = x - np.mean(x)
    x = x / (np.abs(x).max() + 1e-9) * peak
    fo = min(len(x) // 3, int(SR * 0.02)); x[-fo:] *= np.linspace(1, 0, fo)
    with wave.open(os.path.join(ROOT, "audio", name + ".wav"), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def clunk(sec=0.25, f=110, bright=0.25):
    t = t_of(sec)
    body = np.sin(2 * np.pi * (f + 40 * np.exp(-30 * t)) * t) * np.exp(-22 * t)
    rattle = lowpass(noise(sec), bright) * np.exp(-40 * t)
    return body + 0.8 * rattle


def chime(f, sec=0.8, decay=5.0):
    # bell-like: a few inharmonic partials
    t = t_of(sec)
    return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-decay * d * t)
               for r, a, d in ((1, 1, 1), (2.76, 0.4, 1.6), (5.4, 0.2, 2.4), (8.9, 0.08, 3)))


def arp(freqs, gap, sec=0.5, decay=7.0, harm=(1, 0.3, 0.1)):
    out = np.zeros(int(SR * (gap * len(freqs) + sec)))
    for k, f in enumerate(freqs):
        place(out, tone(f, sec, decay, harm=harm), k * gap)
    return out


def launch():
    # engines spool up from a low rumble into a rising roar, then a whoosh as the bay falls away
    sec = 2.4; t = t_of(sec)
    rumble = lowpass(noise(sec), 0.02) * np.minimum(1, t / 0.6) * 3
    whoosh = lowpass(noise(sec), 0.05 + 0.25 * (t / sec) ** 2) * np.sin(np.pi * np.minimum(1, t / sec)) ** 2
    hum = np.sin(2 * np.pi * np.cumsum(55 + 70 * (t / sec) ** 2) / SR) * 0.4 * np.minimum(1, t / 0.8)
    out = rumble + whoosh * 1.5 + hum
    return out * np.minimum(1, (sec - t) / 0.5)


def ship_crate():
    out = np.zeros(int(SR * 0.6))
    place(out, clunk(0.2, 220, 0.4) * 0.5, 0.0)     # lid opens
    place(out, clunk(0.25, 90, 0.15), 0.18)          # the item lands
    place(out, clunk(0.2, 180, 0.35) * 0.7, 0.36)    # lid shuts
    return out


def chest_close():
    return clunk(0.3, 150, 0.3)


def furnace_load():
    out = np.zeros(int(SR * 0.9)); t = t_of(0.7)
    place(out, clunk(0.25, 120, 0.2), 0.0)
    fire = lowpass(noise(0.7), 0.12) * np.sin(np.pi * t / 0.7) * 0.9      # the flame catches
    return place(out, fire, 0.12)


def machine_done():
    out = np.zeros(int(SR * 0.6))
    place(out, tone(320, 0.08, 40, harm=(1, 0.5)) * 0.6, 0.0)              # pop
    place(out, chime(1046, 0.5, 6) * 0.5, 0.06)
    return out


def cook():
    sec = 1.0; t = t_of(sec)
    hiss = (noise(sec) - lowpass(noise(sec), 0.3)) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
    pops = np.zeros(len(t))
    for at in rng.uniform(0.05, 0.85, 9):
        place(pops, tone(rng.uniform(900, 1600), 0.03, 120) * 0.7, at)
    return (hiss * 0.5 + pops) * np.minimum(1, t / 0.08) * np.minimum(1, (sec - t) / 0.3)


def recipe_new():
    return arp([784, 988, 1175, 1568], 0.07, 0.5, 6, harm=(1, 0.2, 0.05))


def repair_done():
    out = arp([523, 659, 784], 0.11, 0.4, 7, harm=(1, 0.35, 0.1))
    return place(np.concatenate([out, np.zeros(int(SR * 0.9))]), tone(1046, 0.9, 3.5, harm=(1, 0.35, 0.1)) * 1.1, 0.36)


def museum_place():
    out = np.zeros(int(SR * 1.0))
    place(out, chime(1319, 0.8, 4), 0.0)
    return place(out, chime(1760, 0.8, 4) * 0.7, 0.12)


def letter_open():
    sec = 0.45; t = t_of(sec)
    crinkle = (noise(sec) - lowpass(noise(sec), 0.2)) * (rng.uniform(0, 1, len(t)) > 0.6)
    return lowpass(crinkle, 0.5) * np.sin(np.pi * t / sec) ** 0.5


def trash():
    out = np.zeros(int(SR * 0.5))
    place(out, letter_open()[:int(SR * 0.25)], 0.0)
    return place(out, clunk(0.25, 140, 0.35) * 0.8, 0.2)


def sleep():
    return arp([659, 523, 440, 330], 0.16, 1.0, 2.8, harm=(1, 0.15))


def enemy_die():
    sec = 0.5; t = t_of(sec)
    squish = lowpass(noise(sec), 0.15) * np.exp(-14 * t)
    drop = np.sin(2 * np.pi * np.cumsum(300 * np.exp(-5 * t) + 60) / SR) * np.exp(-6 * t) * 0.6
    return squish + drop


def crew_down():
    sec = 0.6; t = t_of(sec)
    thud = clunk(0.3, 70, 0.08)
    groan = np.sin(2 * np.pi * np.cumsum(180 - 80 * t / sec) / SR) * np.exp(-5 * t) * 0.3
    out = np.zeros(len(t)); place(out, thud, 0.0)
    return out + groan


def drink():
    out = np.zeros(int(SR * 0.6))
    for k, at in enumerate((0.0, 0.18, 0.36)):
        t = t_of(0.12)
        place(out, np.sin(2 * np.pi * np.cumsum(220 + 500 * t) / SR) * np.exp(-25 * t), at)   # a glug
    return out


def win_sting():
    return arp([523, 659, 784, 1046], 0.12, 0.9, 3.0, harm=(1, 0.4, 0.15))


def lose_sting():
    return arp([494, 440, 392, 311], 0.18, 1.0, 2.5, harm=(1, 0.3, 0.1))


def loop_of(x, xf=1.0):
    n = int(SR * xf); head = x[:n].copy(); body = x[n:].copy(); a = np.linspace(0, 1, n)
    body[-n:] = body[-n:] * np.sqrt(1 - a) + head * np.sqrt(a)
    return body


def amb_station():
    # a big ship-station hum: air handlers, a low mains hum and a far-off clank now and then
    sec = 22; t = t_of(sec)
    air = lowpass(noise(sec), 0.03) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t))
    hum = 0.25 * np.sin(2 * np.pi * 60 * t) + 0.1 * np.sin(2 * np.pi * 120 * t)
    out = air * 2.5 + hum
    for at in (4.1, 11.7, 17.3):
        place(out, clunk(0.4, 60, 0.05) * 0.25, at)
    return loop_of(out)


def amb_agri():
    # greenhouse fans and dripping irrigation
    sec = 20; t = t_of(sec)
    fan = lowpass(noise(sec), 0.06) * (0.8 + 0.2 * np.sin(2 * np.pi * 3.1 * t))
    out = fan * 1.5
    for at in rng.uniform(0.3, sec - 1.3, 26):
        place(out, tone(rng.uniform(1400, 2400), 0.06, 70, harm=(1, 0.2)) * 0.18, at)
    return loop_of(out)


SOUNDS = {
    "launch": (launch, 0.8), "ship_crate": (ship_crate, 0.6), "chest_close": (chest_close, 0.5),
    "furnace_load": (furnace_load, 0.6), "machine_done": (machine_done, 0.5), "cook": (cook, 0.45),
    "recipe_new": (recipe_new, 0.45), "repair_done": (repair_done, 0.5), "museum_place": (museum_place, 0.4),
    "letter_open": (letter_open, 0.35), "trash": (trash, 0.5), "sleep": (sleep, 0.4), "enemy_die": (enemy_die, 0.6),
    "crew_down": (crew_down, 0.6), "drink": (drink, 0.45), "win_sting": (win_sting, 0.5),
    "lose_sting": (lose_sting, 0.45), "amb_station": (amb_station, 0.12), "amb_agri": (amb_agri, 0.15),
}

if __name__ == "__main__":
    for name, (fn, peak) in SOUNDS.items():
        save(name, fn(), peak)
    print(len(SOUNDS), "made-up sounds written to audio/")
