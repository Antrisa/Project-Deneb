"""Sounds for the prologue (24 Nov 2026, Zachary: "needs sound effects"). Made up from tones and filtered noise
like tools/dev/madeup_sounds.py, written as audio/<name>.wav; a real recording dropped in as audio/<name>.ogg
replaces one with no code change. Run from the repo root: python3 -I tools/dev/prologue_sounds.py

  drone_hum      the Mother-Drone waking: a deep crystal chord that swells, beating slowly, with a shimmer on top
  glyph_chime    the star-glyphs: a rising run of glassy bells
  beam_charge    the beam gathering: a rising whine and hiss
  crash_impact   your ship hitting the cavern floor: a deep boom, crunching rock, debris pattering down
  hull_groan     bent metal settling: a slow, low creak
  water_drip     one drop into the puddle, with the cave's echo
  radio_static   a radio waking: crackle, a carrier tone, clicks
  power_down     the drone going dark: a long falling tone that wobbles out
  hull_tear      the back of your ship tearing away in the blind jump
  fire_crackle   small fires on the wreck
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from madeup_sounds import SR, rng, t_of, noise, lowpass, env, tone, place, save  # noqa: E402


def drone_hum():
    sec = 4.5
    t = t_of(sec)
    swell = np.minimum(1, t / 1.2) * np.minimum(1, (sec - t) / 1.0)
    out = np.zeros_like(t)
    for f, a in ((55, 1.0), (82.4, .7), (110, .6), (164.8, .35), (220, .25)):
        out += a * (np.sin(2 * np.pi * f * t) + .6 * np.sin(2 * np.pi * (f + .35) * t))
    shimmer = (np.sin(2 * np.pi * 880 * t) + .5 * np.sin(2 * np.pi * 1318.5 * t)) * (.5 + .5 * np.sin(2 * np.pi * 5.5 * t))
    out += .12 * shimmer * np.minimum(1, t / 2.0)
    return out * swell


def glyph_chime():
    sec = 2.6
    out = np.zeros(int(SR * sec))
    for i, f in enumerate((523.3, 659.3, 784.0, 1046.5, 1318.5, 1568.0)):
        t = t_of(1.4)
        mod = np.sin(2 * np.pi * f * 1.41 * t) * 2.2 * np.exp(-5 * t)
        bell = np.sin(2 * np.pi * f * t + mod) * env(t, .003, 3.2)
        place(out, bell * (.8 - i * .07), i * .16)
    return out


def beam_charge():
    sec = 1.7
    t = t_of(sec)
    f = 180 + 1100 * (t / sec) ** 2
    whine = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / .2)
    hiss = lowpass(noise(sec), np.clip(.02 + .4 * t / sec, 0, .6)) * (t / sec)
    return (whine * .6 + hiss * .9) * np.minimum(1, (sec - t) / .08)


def crash_impact():
    sec = 3.0
    t = t_of(sec)
    boom_f = 70 * np.exp(-t * 1.8) + 32
    boom = np.sin(2 * np.pi * np.cumsum(boom_f) / SR) * np.exp(-t * 2.2)
    crunch = lowpass(noise(sec), .25) * np.exp(-t * 6) * 1.4
    out = boom * 1.2 + crunch
    for at in rng.uniform(.3, 2.4, 30):           # debris pattering down
        place(out, lowpass(noise(.05), .5) * env(t_of(.05), .001, 60) * rng.uniform(.1, .35), at)
    return out


def hull_groan():
    sec = 2.4
    t = t_of(sec)
    f = 62 + 18 * np.sin(2 * np.pi * .4 * t) + 6 * np.sin(2 * np.pi * 3.3 * t)
    saw = ((np.cumsum(f) / SR) % 1) * 2 - 1
    body = lowpass(saw, .05 + .03 * np.sin(2 * np.pi * .7 * t))
    return body * np.minimum(1, t / .4) * np.minimum(1, (sec - t) / .6) * 2.5


def water_drip():
    sec = .9
    t = t_of(sec)
    f = 1500 * np.exp(-t * 18) + 700
    plink = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(t, .001, 22)
    out = plink.copy()
    for d, a in ((.11, .35), (.23, .18), (.37, .08)):     # the cave answering
        place(out, plink * a, d)
    return out


def radio_static():
    sec = 1.8
    t = t_of(sec)
    crackle = lowpass(noise(sec), .7) * (rng.random(len(t)) < .02) * 3
    hiss = lowpass(noise(sec), .35) * .25
    carrier = np.sin(2 * np.pi * 1020 * t) * .18 * ((t > .6) & (t < 1.3))
    return (crackle + hiss + carrier) * np.minimum(1, t / .05)


def power_down():
    sec = 2.6
    t = t_of(sec)
    f = 420 * np.exp(-t * 1.4) + 40 + 6 * np.sin(2 * np.pi * 7 * t) * np.exp(-t)
    tone_ = np.sin(2 * np.pi * np.cumsum(f) / SR) + .4 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return tone_ * np.exp(-t * .9) * np.minimum(1, t / .05)


def hull_tear():
    sec = 2.2
    t = t_of(sec)
    tear = lowpass(noise(sec), np.clip(.5 * np.exp(-t * 1.2), .03, .6)) * np.exp(-t * 1.1) * 1.6
    grind_f = 140 + 80 * np.sin(2 * np.pi * 9 * t)
    grind = (((np.cumsum(grind_f) / SR) % 1) * 2 - 1) * np.exp(-t * 2.4) * .4
    whoosh = lowpass(noise(sec), .08) * np.sin(np.pi * np.clip(t / sec, 0, 1)) * 1.2
    return tear + grind + whoosh


def fire_crackle():
    sec = 2.0
    out = lowpass(noise(sec), .04) * .4
    for at in rng.uniform(0, sec - .05, 40):
        place(out, lowpass(noise(.02), .8) * env(t_of(.02), .0005, 120) * rng.uniform(.2, .7), at)
    return out


SOUNDS = {
    "drone_hum": (drone_hum, .55), "glyph_chime": (glyph_chime, .45), "beam_charge": (beam_charge, .45),
    "crash_impact": (crash_impact, .8), "hull_groan": (hull_groan, .45), "water_drip": (water_drip, .35),
    "radio_static": (radio_static, .4), "power_down": (power_down, .5), "hull_tear": (hull_tear, .7),
    "fire_crackle": (fire_crackle, .35),
}

if __name__ == "__main__":
    for name, (fn, peak) in SOUNDS.items():
        save(name, fn(), peak)
    print(len(SOUNDS), "prologue sounds written to audio/")
