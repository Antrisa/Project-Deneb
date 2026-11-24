"""How Zachary's recordings (Drive folder "Echo Landing Sounds", 24 Nov 2026) were cut into game sounds.
Each source file is first turned into mono 44.1 kHz wav with ffmpeg and named as in the calls below
(e.g. "footstep panel.wav" -> step_panel.wav). Then: python3 -I tools/dev/cut_drive_sounds.py <wav dir> <out dir>
and encode each result to audio/<name>.ogg (ffmpeg -c:a libvorbis -q:a 5). Spans are seconds in the source;
<name>_1, _2 ... are takes the game picks between at random. Loudness is matched to the made-up sound each one
replaced (max 30 ms RMS, in dB)."""
import sys, wave, numpy as np
src, out = sys.argv[1:3]
SR = 44100
def rd(n):
    w = wave.open(f"{src}/{n}.wav"); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x
def loud(x):
    win = int(SR * 0.03); return np.sqrt(np.convolve(x**2, np.ones(win) / win, 'same').max()) + 1e-9
def onset_trim(x):
    hop = int(SR * 0.002); e = np.array([np.sqrt((x[j:j+hop]**2).mean()) for j in range(0, max(1, len(x) - hop), hop)])
    on = int(np.argmax(e > e.max() * 0.06)) * hop
    return x[max(0, on - int(SR * 0.004)):]
def tail_trim(x):
    hop = int(SR * 0.005); e = np.array([np.sqrt((x[j:j+hop]**2).mean()) for j in range(0, max(1, len(x) - hop), hop)])
    keep = np.nonzero(e > e.max() * 10**(-48 / 20))[0]
    end = (keep[-1] + 1) * hop + int(SR * 0.01) if len(keep) else len(x)
    return x[:min(len(x), end)]
def write(name, x):
    w = wave.open(f"{out}/{name}.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
def make(name, srcname, a=None, b=None, db=-12.0, fade=0.03, maxlen=None, trim=True, pitch=1.0):
    x = rd(srcname)
    if a is not None: x = x[int(a * SR):int(b * SR) if b else None].copy()
    if trim: x = tail_trim(onset_trim(x))
    if pitch != 1.0:
        idx = np.arange(0, len(x) - 1, pitch); x = np.interp(idx, np.arange(len(x)), x).astype(np.float32)
    if maxlen and len(x) > maxlen * SR: x = x[:int(maxlen * SR)]
    x = x - x.mean()
    fi = int(SR * 0.002); x[:fi] *= np.linspace(0, 1, fi)
    fo = min(len(x) // 2, int(SR * fade)); x[-fo:] *= np.linspace(1, 0, fo) ** 2
    x *= 10**(db / 20) / loud(x)
    pk = np.abs(x).max()
    if pk > 0.95:                       # let sharp clicks go up to 6 dB over the peak, then round the tips off
        x *= max(0.95 / pk, 1.9 / pk if pk > 1.9 else 1.0)
        a = np.abs(x); knee = 0.6
        x = np.where(a > knee, np.sign(x) * (knee + 0.35 * np.tanh((a - knee) / 0.35)), x).astype(np.float32)
    write(name, x); print(f"{name:16s} {len(x)/SR:5.2f}s loud {20*np.log10(loud(x)):6.1f}")
def takes(name, srcname, spans, **k):
    for i, (a, b) in enumerate(spans, 1): make(f"{name}_{i}", srcname, a, b, **k)
def loop(name, srcname, a, b, rms_db, xf=1.5):
    x = rd(srcname)[int(a * SR):int(b * SR)].copy(); x -= x.mean()
    n = int(xf * SR); head = x[:n].copy(); body = x[n:].copy()
    t = np.linspace(0, 1, n); body[-n:] = body[-n:] * np.sqrt(1 - t) + head * np.sqrt(t)   # end flows into the start
    body *= 10**(rms_db / 20) / np.sqrt((body**2).mean())
    pk = np.abs(body).max()
    if pk > 0.9: body *= 0.9 / pk
    write(name, body); print(f"{name:16s} {len(body)/SR:5.2f}s loop rms {20*np.log10(np.sqrt((body**2).mean())):6.1f}")

# footsteps (played at -13 dB, like the Suno steps)
takes("step_deck", "step_panel", [(0.07, 0.32), (0.46, 0.72), (0.87, 1.12)], db=-12, maxlen=0.2, fade=0.06)
takes("step_rock", "step_mine", [(0.10, 0.55), (0.94, 1.28), (1.78, 2.08)], db=-12, maxlen=0.24, fade=0.08)
takes("step_soil", "step_dirt", [(0.72, 0.98), (1.33, 1.58), (1.94, 2.19)], db=-12, maxlen=0.22, fade=0.08)
takes("step_water", "wet_steps", [(0.35, 0.62), (0.90, 1.17), (1.58, 1.85), (2.08, 2.35), (2.81, 3.08)], db=-12, maxlen=0.24, fade=0.08)
takes("step_carpet", "carpet_walk", [(0.88, 1.05), (1.23, 1.40), (1.42, 1.60), (1.91, 2.08), (3.30, 3.48), (3.95, 4.12)], db=-12, maxlen=0.15, fade=0.06)
# doors and travel
make("door_slide", "door_open", 0.50, 1.40, db=-12, fade=0.15)
make("door_locked", "locked_door", db=-11)
takes("ladder", "ladder", [(1.54, 1.90), (3.70, 4.10), (8.56, 8.90)], db=-11, maxlen=0.3, fade=0.08)
make("lift", "lift", db=-14, fade=0.1)
# tools and farming
make("tool_swing", "tool_swing", db=-14, fade=0.05)
make("weapon_swing", "weapon_swing", db=-13, fade=0.05)
make("hoe_dig", "hoe_dig", db=-12)
make("water_pour", "water_pour", 0.08, 1.40, db=-15, fade=0.45)
make("can_refill", "water_fill", 0.05, 1.90, db=-15, fade=0.5)
make("seed_plant", "plant_seed", 0.10, 1.10, db=-15, fade=0.1)
make("harvest", "harvest_pickup", db=-13)
make("item_pickup", "harvest_pickup", db=-15, pitch=1.15)
make("valve_spray", "valve_spray", 0.5, 2.6, db=-18, fade=0.6, trim=False)
make("tool_upgrade", "tool_upgrade", db=-10, fade=0.1)
make("hotbar", "tool_change", db=-17)
# mining and crafting
takes("rock_crack", "rock_crack", [(0.06, 0.31), (0.31, 0.82), (2.16, 2.66)], db=-12, maxlen=0.4, fade=0.12)
make("rock_break", "rock_break", db=-10, fade=0.12)
make("geode_crack", "rare_geode", 0.0, 1.4, db=-12, fade=0.3)
make("ore_find", "rare_geode", 2.95, 4.8, db=-15, fade=0.4)
make("crate_break", "wood_break", db=-11, fade=0.08)
make("crate_hit", "wood_chop", db=-12, fade=0.06)
make("craft", "craft", db=-11)
takes("eat", "eating", [(0.02, 0.42), (0.78, 1.22), (1.96, 2.32), (2.99, 3.24)], db=-15, fade=0.05)
make("chest_open", "chest_open", db=-14, fade=0.08)
# menus, money and people
takes("coin", "coin_pickup", [(0.0, 0.50), (1.43, 2.05), (2.77, 3.70)], db=-12, fade=0.15)
make("click", "inventory", db=-16)
make("quest", "happy", db=-10, fade=0.2)
make("gift", "love_gift", db=-11, fade=0.2)
make("bell_ring", "bell_ding", 0.03, 2.2, db=-14, fade=0.8)
make("mail_waiting", "bell_ding", 6.20, 7.6, db=-16, fade=0.5)
# caverns combat
make("hurt", "player_hit", db=-12)
takes("hit", "slap", [(0.05, 0.40), (0.66, 1.0)], db=-11, fade=0.05)
make("pass_out", "pass_out", db=-11, fade=0.15)
make("medpack", "health_pack", db=-12, fade=0.15)
takes("bug_noise", "bug_noise", [(0.55, 0.95), (3.24, 3.65)], db=-14, fade=0.08)
# space
make("sh_laser", "laser_shot", 0.0, 1.0, db=-14, fade=0.35)
takes("sh_blaster", "blaster_bolt", [(0.0, 0.40), (1.32, 1.75)], db=-18, fade=0.1)
takes("sh_ion", "ion_shot", [(0.0, 0.6), (1.31, 1.95), (2.66, 3.25)], db=-15, fade=0.15)
make("sh_shield", "shield", 0.02, 1.0, db=-15, fade=0.4)
takes("sh_explode", "explosion", [(0.10, 2.70), (4.48, 7.0), (9.69, 12.2)], db=-10, fade=0.8)
make("sh_ready", "computer_bleeps", 9.56, 10.05, db=-16)
make("map_jump", "computer_bleeps", 10.26, 10.58, db=-16)
make("crew_order", "computer_bleeps", 10.82, 11.12, db=-17)
make("toast", "computer_bleeps", 11.44, 11.95, db=-18)
make("datapad_open", "computer_bleeps", 8.25, 8.95, db=-17, fade=0.15)
make("hail", "computer_bleeps", 12.10, 13.30, db=-15, fade=0.2)
make("sara_holo", "computer_bleeps", 5.76, 7.0, db=-17, fade=0.3)
# ambient loops
loop("amb_space", "space_amb", 0.0, 28.0, -27)
loop("amb_caves", "cave_amb", 10.0, 70.0, -30)
