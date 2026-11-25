"""Short, original foley for the Mother-Drone and rescue radio. Regenerate with
python3 -I tools/dev/mother_sounds.py. Levels are printed into the WAVs so
these cues can share the existing effects path under Lunar Discovery."""
import os
import sys

import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.dirname(__file__))
from madeup_sounds import SR, place, save, t_of


def air(rng, t, low, high):
    band = butter(2, (low, high), btype="bandpass", fs=SR, output="sos")
    signal = sosfilt(band, rng.normal(size=t.size))
    return signal / max(.01, np.sqrt(np.mean(signal**2)))


def breath(t, duration, attack=.18):
    pos = np.clip(t / duration, 0, 1)
    return np.sin(.5*np.pi*np.minimum(pos/attack, 1))**2 * np.cos(.5*np.pi*pos)**2


def resonant_tap(rng, length, body):
    t = t_of(length)
    contact = air(rng, t, 480, 2400)*np.exp(-94*t)
    shell = np.sin(2*np.pi*body*t)*np.exp(-23*t)
    return (.52*contact + shell) * np.minimum(t/.002,1)


def iris():
    rng = np.random.default_rng(741)
    t = t_of(2.55)
    # The shutter eases through its detents. Listen for the second contact and
    # then the last fraction of travel in the aperture animation.
    out = .26*air(rng,t,85,400)*breath(t,1.95,.36)
    for at,pitch,force in ((.12,169,.8),(.32,217,.42),(.6,183,.57),(1.03,145,.35),(1.64,119,.48)):
        place(out, force*resonant_tap(rng,.28,pitch),at)
    sub = np.sin(2*np.pi*(69*t + 3*(1-np.exp(-2*t))))
    out += .56*sub*breath(t,2.55,.23)
    return out


def signal():
    # Two soft articulations through the same hollow resonator, the first
    # opening upwards and the second falling away. No pitched bell attack.
    rng = np.random.default_rng(193)
    t = t_of(.91)
    phase = 2*np.pi*(106*t + 1.7*np.sin(2*np.pi*1.15*t))
    reed = np.sin(phase) + .36*np.sin(phase*2.01+.3) + .12*np.sin(phase*3.04)
    consonant = .35*air(rng,t,465,850) + .09*air(rng,t,1020,1750)
    syllables = breath(t,.39,.34) + .61*breath(t-.35,.53,.23)
    direct = (reed*.8+consonant)*syllables
    out = direct.copy()
    place(out,direct*.12,.072)
    return out


def transfer():
    rng = np.random.default_rng(572)
    t = t_of(1.2)
    stream = .26*air(rng,t,165,665) + .15*air(rng,t,750,1700)
    approach = np.minimum(t/.81,1)**1.8
    out = stream*approach*np.exp(-np.maximum(t-.81,0)*10)
    place(out,.64*resonant_tap(rng,.28,236),.80)
    return out


def extinguish():
    rng = np.random.default_rng(939)
    t = t_of(2.35)
    tphase = 2*np.pi*(53*t+18*(1-np.exp(-1.9*t)))
    out = (.47*np.sin(tphase)+.33*air(rng,t,125,435))*breath(t,2.1,.10)
    place(out,.29*resonant_tap(rng,.28,126),1.33)
    place(out,.17*resonant_tap(rng,.19,108),1.82)
    return out


def receiver():
    rng = np.random.default_rng(212)
    t = t_of(.48)
    out = .12*air(rng,t,520,2050)*breath(t,.37,.055)
    place(out,.5*resonant_tap(rng,.06,520),.014)
    place(out,.28*resonant_tap(rng,.08,420),.31)
    return out


if __name__ == "__main__":
    for name, fn, peak in (("mother_iris",iris,.49),("mother_signal",signal,.26),
                           ("mother_transfer",transfer,.40),("mother_extinguish",extinguish,.36),
                           ("rescue_receiver",receiver,.37)):
        save(name,fn(),peak)
