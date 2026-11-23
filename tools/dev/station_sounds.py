"""Softer station sounds (23 Nov 2026; Zachary: "walking i dont like right now, talking to npcs sounds a bit
annoying maybe just a single noise for every text box"). Writes audio/step_soft.wav (a soft footfall) and
audio/talk.wav (one gentle note when a text box opens). Placeholders until real sounds come: a real one dropped in
as audio/<name>.ogg replaces them. Run from the repo root: python3 -I tools/dev/station_sounds.py
"""
import math, os, random, struct, wave

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RATE = 22050


def save(name, samples):
    with wave.open(os.path.join(ROOT, "audio", name + ".wav"), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(RATE)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32000)) for v in samples))


def step():
    # a soft-soled footfall on a station deck: a low thump with a little muffled scuff, no click at the start
    rnd, out, lp, n = random.Random(7), [], 0.0, int(RATE * 0.11)
    for i in range(n):
        t = i / RATE
        k = i / n
        attack = min(1.0, i / (RATE * 0.004))
        thump = math.sin(2 * math.pi * (95 - 40 * k) * t) * math.exp(-28 * t)
        lp += (rnd.uniform(-1, 1) - lp) * 0.08          # heavily smoothed noise: a muffled scuff
        out.append((0.55 * thump + 0.35 * lp * math.exp(-35 * t)) * attack)
    return out


def talk():
    # one soft rounded note with a quieter fifth above it, fading out: a gentle "pip" per text box
    out, n = [], int(RATE * 0.16)
    for i in range(n):
        t = i / RATE
        attack = min(1.0, i / (RATE * 0.008))
        env = attack * math.exp(-16 * t)
        v = 0.38 * math.sin(2 * math.pi * 520 * t) + 0.12 * math.sin(2 * math.pi * 780 * t)
        out.append(v * env)
    return out


if __name__ == "__main__":
    save("step_soft", step())
    save("talk", talk())
    print("audio/step_soft.wav and audio/talk.wav written")
