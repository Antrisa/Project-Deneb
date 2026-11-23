"""Space-battle sound effects (23 Nov 2026), made in code like tools/build.py's sounds: audio/sh_*.wav, 22 kHz mono.
Placeholders in the same chiptune-ish style until real sounds come; replace any file freely (same name).
Run from the repo root:  python3 -I tools/dev/ship_sounds.py
"""
import math, os, random, struct, wave

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AUDIO = os.path.join(ROOT, "audio")
RATE = 22050


def save(name, samples):
    with wave.open(os.path.join(AUDIO, name + ".wav"), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32000)) for v in samples))


def tone(f0, f1, dur, vol=0.5, shape="sine", decay=4.0, vib=0.0):
    out, ph, n = [], 0.0, int(RATE * dur)
    for i in range(n):
        k = i / n
        f = f0 + (f1 - f0) * k
        if vib:
            f *= 1.0 + 0.04 * math.sin(i / RATE * 2 * math.pi * vib)
        ph += 2 * math.pi * f / RATE
        v = math.sin(ph)
        if shape == "square":
            v = 1.0 if v > 0 else -1.0
        elif shape == "saw":
            v = (ph / math.pi) % 2.0 - 1.0
        elif shape == "tri":
            v = 2.0 * abs((ph / math.pi) % 2.0 - 1.0) - 1.0
        env = math.exp(-decay * k) * min(1.0, i / 30.0) * min(1.0, (n - i) / 60.0)
        out.append(v * vol * env)
    return out


def noise(dur, vol=0.5, smooth=0.2, decay=6.0, seed=1, swell=False):
    rnd, out, last, n = random.Random(seed), [], 0.0, int(RATE * dur)
    for i in range(n):
        k = i / n
        last += (rnd.uniform(-1, 1) - last) * smooth
        env = (math.sin(math.pi * k) if swell else math.exp(-decay * k)) * min(1.0, (n - i) / 60.0)
        out.append(last * vol * env)
    return out


def mix(*parts):
    n = max(len(p) for p in parts)
    return [sum(p[i] for p in parts if i < len(p)) for i in range(n)]


def gap(dur):
    return [0.0] * int(RATE * dur)


def main():
    save("sh_laser", mix(tone(1400, 380, 0.16, 0.35, "square", 7.0), noise(0.05, 0.15, 0.6, 20.0, 2)))
    save("sh_missile", mix(noise(0.55, 0.45, 0.08, 2.5, 3), tone(180, 90, 0.5, 0.25, "saw", 3.0)))
    save("sh_beam", mix(tone(220, 240, 0.7, 0.3, "saw", 1.2, vib=30), tone(440, 470, 0.7, 0.12, "sine", 1.2)))
    save("sh_ion", mix(tone(900, 1500, 0.25, 0.25, "tri", 3.0, vib=60), tone(450, 750, 0.25, 0.15, "square", 4.0)))
    save("sh_flak", mix(noise(0.18, 0.6, 0.5, 10.0, 4), tone(160, 70, 0.18, 0.35, "square", 9.0)))
    save("sh_dart", mix(tone(700, 300, 0.2, 0.25, "sine", 5.0), noise(0.2, 0.2, 0.3, 6.0, 5)))
    save("sh_shield", mix(tone(620, 820, 0.28, 0.32, "sine", 5.0, vib=18), tone(1240, 1640, 0.2, 0.12, "tri", 8.0)))
    save("sh_hull", mix(noise(0.32, 0.8, 0.25, 7.0, 6), tone(110, 55, 0.3, 0.5, "square", 6.0)))
    save("sh_hit", mix(noise(0.22, 0.45, 0.35, 9.0, 7), tone(150, 80, 0.2, 0.25, "square", 8.0)))
    save("sh_miss", noise(0.25, 0.18, 0.05, 1.0, 8, swell=True))
    save("sh_explode", mix(noise(1.4, 0.9, 0.06, 2.2, 9), tone(90, 30, 1.2, 0.5, "saw", 2.5), noise(0.25, 0.6, 0.5, 8.0, 10)))
    save("sh_fire", mix(*[gap(0.05 * i) + noise(0.08, 0.25, 0.7, 12.0, 20 + i) for i in range(8)]))
    alarm = tone(880, 880, 0.18, 0.3, "square", 0.5) + gap(0.06) + tone(660, 660, 0.22, 0.3, "square", 0.5)
    save("sh_alarm", alarm)
    save("sh_vent", noise(0.9, 0.5, 0.04, 1.5, 11, swell=True))
    save("sh_fold", mix(tone(120, 900, 0.9, 0.35, "saw", 1.5), noise(0.9, 0.25, 0.1, 1.0, 12, swell=True)))
    save("sh_ready", tone(660, 660, 0.08, 0.3, "square", 2.0) + tone(990, 990, 0.14, 0.3, "square", 3.0))
    save("sh_blaster", mix(tone(1800, 700, 0.09, 0.22, "square", 9.0), noise(0.04, 0.1, 0.6, 20.0, 13)))
    save("sh_pod", mix(noise(0.6, 0.4, 0.1, 2.0, 14), tone(300, 140, 0.5, 0.2, "tri", 2.5)))
    save("sh_door", mix(tone(260, 200, 0.12, 0.2, "square", 6.0), noise(0.12, 0.15, 0.3, 10.0, 15)))
    print("ship sounds written to audio/sh_*.wav")


if __name__ == "__main__":
    main()
