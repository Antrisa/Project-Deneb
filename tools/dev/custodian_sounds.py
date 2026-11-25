"""The Custodians' call (25 Nov 2026). Zachary on the bell that played when the crystals spoke: "too loud and harsh
and not mysterious musical". This is a soft swell of glass tones in place of a strike: E, B, F sharp and G rising
one after another into an E minor (add 9) chord, a low E under it, a breath of air over it, and a long, dark echo.
Story scenes play it at a different pitch for each Custodian (cutscene step ["sfx", name, pitch]); played lower it
is also slower, which is the Shepherd's lullaby.

Written as audio/custodian_call.wav. Run from the repo root: python3 -I tools/dev/custodian_sounds.py
"""
import os
import sys

import numpy as np
from scipy.signal import fftconvolve

sys.path.insert(0, os.path.dirname(__file__))
from madeup_sounds import SR, rng, t_of, noise, lowpass, place, save  # noqa: E402

E3, E4, B4, FS5, G5 = 164.81, 329.63, 493.88, 739.99, 783.99


def glass(f, sec, attack=0.45, fall=1.6, beat=0.55, level=1.0):
    """A glass-harmonica voice: a nearly pure tone with a little of its octave and twelfth, two copies a hair apart
    so it beats slowly, swelling in with no strike and fading away."""
    t = t_of(sec)
    v = np.zeros_like(t)
    for d in (-beat, beat):
        ph = 2 * np.pi * (f + d) * t
        v += np.sin(ph) + .16 * np.sin(2 * ph) + .05 * np.sin(3 * ph)
    swell = .5 - .5 * np.cos(np.pi * np.clip(t / attack, 0, 1))
    tremolo = 1 + .06 * np.sin(2 * np.pi * 4.2 * t)
    return v * swell * np.exp(-t / fall) * tremolo * level


def air(sec):
    """Breath over glass: high, soft, filtered noise that swells and falls."""
    t = t_of(sec)
    hiss = noise(sec)
    band = lowpass(hiss, .35) - lowpass(hiss, .08)
    return band * np.sin(np.pi * np.clip(t / sec, 0, 1)) ** 2


def echo(x, length=2.4, fall=0.75, wet=0.65):
    """A long, dark echo: the sound convolved with a fading, darkened noise tail (after a short pre-delay)."""
    t = t_of(length)
    ir = lowpass(rng.uniform(-1, 1, len(t)), .22) * np.exp(-t / fall)
    ir[:int(.025 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    tail = fftconvolve(x, ir)
    out = np.zeros(len(tail))
    out[:len(x)] += x
    return out + wet * tail * (np.abs(x).max() / (np.abs(tail).max() + 1e-9))


def custodian_call():
    sec = 5.0
    out = np.zeros(int(SR * sec))
    place(out, glass(E3, sec, attack=1.1, fall=2.2, beat=.3, level=.35), 0.0)
    for i, (f, lv) in enumerate(((E4, 1.0), (B4, .8), (FS5, .5), (G5, .45))):
        place(out, glass(f, sec - .24 * i, attack=.4, fall=1.5 - .15 * i, level=lv), .24 * i)
    place(out, air(2.6) * .035, .3)
    t = t_of(sec)
    out *= np.clip((sec - t) / 1.2, 0, 1) ** 2         # let the glass die away before the echo takes over (no click)
    return echo(out)


if __name__ == "__main__":
    save("custodian_call", custodian_call(), 0.2)
    print("wrote audio/custodian_call.wav")
