"""Cozy footsteps (25 Nov): short, soft, quick taps made from filtered noise and a little body tone.

Zachary found the footsteps not quick or cozy enough. The carpet takes were low thumps (almost all their
sound under 100 Hz), the farm-path ones dry clicks, the deck ones long. These are built to sit between: a
fast attack, a body that dies away in about 60 ms, and a soft top so they patter rather than thud.

  step_deck_1..6    metal deck plates: a light tap with a faint ring
  step_carpet_1..6  homes, the hotel, the lounge: a muffled pat
  step_soft_1..6    the farm's paths: a pat with a little grassy rustle
  step_soil_1..6    dug soil: a soft crunch
  step_base_1..6    (25 Nov, second pass) the one footstep now used on every floor: a warm, dull tock

The cave (rock) and bath house (water) recordings stay as they were. Every take differs a little in pitch,
length and colour so a walk never repeats. Output: 44.1 kHz mono Ogg Vorbis in audio/.
Usage: python3 -I tools/cozy_steps.py [GAME_DIR] [KIND ...]   (default: base, the one footstep used everywhere)
"""
import os, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt

GAME = sys.argv[1] if len(sys.argv) > 1 else "."
SR = 44100
TAKES = 6


def env(n, attack, decay):
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1)
    return a * np.exp(-np.maximum(0, t - attack) / decay)


def band(x, lo, hi):
    if lo is None:
        sos = butter(2, hi, "lp", fs=SR, output="sos")
    elif hi is None:
        sos = butter(2, lo, "hp", fs=SR, output="sos")
    else:
        sos = butter(2, [lo, hi], "bp", fs=SR, output="sos")
    return sosfilt(sos, x)


def tone(n, f, decay, rng):
    t = np.arange(n) / SR
    f = f * (1 + 0.15 * np.exp(-t / 0.01))          # a little pitch drop at the start: a "tock", not a beep
    return np.sin(2 * np.pi * np.cumsum(f) / SR + rng.uniform(0, 6.28)) * np.exp(-t / decay)


def make(kind, k):
    rng = np.random.default_rng({"deck": 11, "carpet": 23, "soft": 37, "soil": 51, "base": 67}[kind] * 100 + k)
    v = lambda a, b: rng.uniform(a, b)
    n = int(SR * 0.16)
    noise = rng.standard_normal(n)
    if kind == "deck":
        body = tone(n, v(150, 185), v(0.025, 0.035), rng) * 0.55
        tap = band(noise, v(900, 1200), v(3800, 4800)) * env(n, 0.0012, v(0.018, 0.026)) * 0.9
        ring = sum(np.sin(2 * np.pi * f * np.arange(n) / SR) * np.exp(-np.arange(n) / SR / 0.05)
                   for f in (v(1750, 1900), v(2650, 2800))) * 0.035
        x = body + tap + ring
    elif kind == "carpet":
        body = tone(n, v(115, 140), v(0.03, 0.04), rng) * 0.6
        pat = band(noise, v(250, 350), v(1300, 1700)) * env(n, 0.003, v(0.03, 0.04)) * 0.8
        x = body + pat
    elif kind == "soft":
        body = tone(n, v(125, 150), v(0.025, 0.035), rng) * 0.45
        pat = band(noise, v(400, 550), v(2000, 2600)) * env(n, 0.002, v(0.025, 0.032)) * 0.7
        rustle = band(noise, v(3000, 3800), v(7500, 9000)) * env(n, 0.008, v(0.035, 0.05)) * 0.35
        x = body + pat + rustle
    elif kind == "base":
        # the one footstep everywhere (Zachary, 25 Nov: "too metallic, we just need a base walking sound, like
        # walking in Stardew"): a warm, dull tock with no ring and no hiss
        body = tone(n, v(120, 145), v(0.022, 0.03), rng) * 0.7
        pat = band(noise, v(220, 300), v(1100, 1400)) * env(n, 0.0015, v(0.018, 0.024)) * 0.75
        x = body + pat
    else:  # soil
        body = tone(n, v(105, 130), v(0.03, 0.04), rng) * 0.45
        grains = np.zeros(n)
        for _ in range(int(v(9, 14))):
            at = int(v(0.0, 0.05) * SR)
            g = int(0.004 * SR)
            grains[at:at + g] += rng.standard_normal(g) * np.hanning(g) * v(0.4, 1.0)
        crunch = band(grains, v(1200, 1600), v(5000, 6500)) * env(n, 0.002, 0.045) * 1.2
        x = body + crunch
    x = x * env(n, 0.0008, 1.0)
    x[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))       # no click at the end
    x = x / np.max(np.abs(x)) * 0.5                                   # about -6 dBFS peak, as the old takes
    return x.astype(np.float32)


def save(x, path):
    subprocess.run(["ffmpeg", "-v", "quiet", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "libvorbis", "-q:a", "6", path], input=x.tobytes(), check=True)


for kind in (sys.argv[2:] or ["base"]):
    for k in range(1, TAKES + 1):
        save(make(kind, k), os.path.join(GAME, "audio", f"step_{kind}_{k}.ogg"))
print("cozy steps written")
