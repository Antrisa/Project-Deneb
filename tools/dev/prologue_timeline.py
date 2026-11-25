"""The prologue's timed part (25 Nov), from its opening until the Mother-Drone dies, built as a timeline against its
music and written into scripts/story_scenes.gd ("prologue", its steps up to S.A.R.A.'s radio call).

Zachary: "the music doesnt sync because you click to continue, so just have it play out"; "the end of battle music
riff should sync to where your ship model jumps"; "dont have the back half of your ship come apart, just the wing
gets shot off". So every line turns over by itself (cutscene step "say_timed"), each given about 1.3 s plus a second
for every 16 letters (or its own time), and the moments that must land on the music wait for it ("score_wait").
Building it checks that every line ends before the next such moment, and stops with a list of the late ones if not.
Song times measured from the files: Space Battle (151.8 bpm, a downbeat at 0.094 s; its full band comes in at 15.2 s,
the drum fill at 60.2-61.4, the finale at 69.675, the last hit at 76.84) and Lunar Discovery (phrase accents about
every 3.73 s; back in full at 173.28, the last chord at 191.21, wound down by 199).
The Mother-Drone has short physical cues for its aperture, voice, transfer and last breath. Lunar Discovery
provides the sustained harmony and the accent when the glyphs fold.
Edit the lines or the times here, then run: python3 tools/dev/prologue_timeline.py"""
import json
import re
import sys

import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "scripts", "story_scenes.gd")
TAG = re.compile(r'^\[(\w+)\] ')


def secs(line):
    text = TAG.sub("", line)
    return round(max(2.4, 1.3 + len(text) / 16.0), 2)


class TL:
    def __init__(self):
        self.steps = []
        self.t = 0.0           # where the scene is (song time while a song runs)
        self.log = []

    def raw(self, *steps, takes=0.0):
        for s in steps:
            self.steps.append(list(s))
        self.t += takes

    def note(self, text):
        self.steps.append(("#", text))

    def at(self, T, label=""):
        if self.t > T + 0.05:
            self.log.append("LATE: %s wanted at %.2f, scene is at %.2f" % (label, T, self.t))
        self.steps.append(["score_wait", T])
        self.t = max(self.t, T)

    def say(self, who, lines, label="", durs=None):
        d = durs or [secs(l) for l in lines]
        self.steps.append(["say_timed", who, lines, label, d])
        self.t += sum(d) + .1

    def start_song(self, song, frm):
        self.steps.append(["score", song, frm])
        self.t = frm


tl = TL()
S, F = tl.raw, tl.say
# The 192-pixel Needle art is registered inside the existing 240 x 165 flight footprint.
HURT = "res://art/prologue/needle_flight_damaged.png"
PLUME = "res://art/prologue/needle_plume.png"
WING = "res://art/prologue/needle_wing.png"
AT = (60, 108)                                  # where she flies, the Needle's top-left
FL1, FL2 = (39, 174), (51, 201)                 # her plumes, on her two nozzles
BOB = [2, 2.6]
CLOSE = "res://art/prologue/mother_close.png"
CLOSE_AT = (122, 80)
CLOSE_WAKE = "res://art/prologue/mother_close_wake.png"
CLOSE_PULSE = "res://art/prologue/mother_close_pulse.png"
CLOSE_DIM = "res://art/prologue/mother_close_dim.png"

# ---------------------------------------------------------------- before the music: who you are
S(["bmove", "rock_a", -114, 279, 65.0, "", "nowait"],
  ["bmove", "rock_b", 64, 40, 142.0, "", "nowait"],
  ["bmoves", [["ship", *AT], ["flame1", *FL1], ["flame2", *FL2]], 2.8, "out"], takes=2.8)
F("", ["The outer Neutral Zone: the asteroid belt, sector seven.",
       "Your little fighter, the Wandering Star, picks her way through the rocks."])
tl.note("who you are and why you're out here (Zachary, 25 Nov: \"a little inner monologue at the start to explain you are a pirate hunter paid to hunt pirates by the terran empire since they cannot officially enter neutral space\")")
F("", ["Forty years ago, the Terran Empire, the Zaa'sh Junta and the Free Star Collective ended their war with a treaty.",
       "The space between them became the Neutral Zone: nobody's. No power's warships may cross into it.",
       "So the pirates moved in. Out here, no navy can follow them.",
       "The Empire can't send its fleet. It can send money: bounties, for licensed hunters flying their own ships.",
       "My parents hunted pirates for the Empire. So did theirs. Nobody asked if I wanted anything else.",
       "The biggest name on the board: Ivan the Rabble, warlord of the Chernobog. Eleven years, and nobody's caught him.",
       "Out here, at least, nobody asks where you belong."], "You (thinking)")
pre_music = tl.t

# ---------------------------------------------------------------- Space Battle, from its first note
tl.note("Space Battle plays from its start with the alarm, and the scene plays out in time with it (no clicking): Ivan hails you when the full band comes in (15.2 s), his salvo lands on the drum fill (60.2-61.4 s, the big hit shears your wing off), the drive spools through the finale, and your ship jumps on the song's last hit (76.84 s)")
S(["sfx", "sh_alarm"])
tl.start_song("space_battle", 0.0)
S(["bsprite", "ivan", "res://art/ships/ivan_flagship/hull.png", 700, 10, {"flip": True, "z": 1, "bob": [2, 3.4]}],
  ["sfx", "hull_groan"],
  ["bmove", "ivan", 340, 10, 8.0, "out", "nowait"])
tl.at(0.3, "warning")
F("", ["Warning: four unregistered vessels. Weapons hot."], "Ship computer")
tl.at(4.7, "flagship")
S(["shake", 0.5, 1.0])
F("", ["A lopsided flagship looms out of the dust. Across its bow, in gaudy gold: THE RABBLE'S CROWN."])
F("", ["Speak of the devil."], "You (thinking)")
tl.at(15.2, "Ivan's hail")
S(["sfx", "hail"])
F("Ivan", ["[angry] Halt, trespasser! You drift in the royal hunting grounds of the Chernobog!",
           "[happy] Bow before His Dread Majesty, Ivan the Rabble, rightful heir to the ancient thrones of Old Earth!"], "Ivan the Rabble")
S(["sfx", "radio_static"])
F("", ["Uh, boss... the book says \"Terrible\". Not \"Rabble\"."], "Pirate lieutenant (muffled)")
F("Ivan", ["[angry] The ink was smudged, you illiterate bilge-rat! \"Rabble\" strikes fear into the hearts of peasants!",
           "Surrender your cargo and your ship, little hunter, and I may spare you for the mines!"], "Ivan the Rabble")
F("", ["I'm a licensed bounty hunter, Ivan. Stand down."], "You")
F("Ivan", ["[happy] Bold words for a minnow!"], "Ivan the Rabble")
tl.note("your two volleys, along your heading: they splash off his shield")
for k in range(2):
    S(["bsprite", "b1", "res://art/prologue/bolt_teal.png", 266, 162, {"z": 3}], ["bsprite", "b2", "res://art/prologue/bolt_teal.png", 252, 170, {"z": 3}],
      ["sfx", "sh_laser"],
      ["bmoves", [["ship", AT[0]-5, AT[1]+1], ["flame1", FL1[0]-5, FL1[1]+1], ["flame2", FL2[0]-5, FL2[1]+1]], .12, "out", "nowait"],
      ["bmoves", [["b1", 316, 154], ["b2", 302, 162]], 0.16],
      ["bmoves", [["ship", *AT], ["flame1", *FL1], ["flame2", *FL2]], .26, "out", "nowait"],
      ["bsprite", "b1", ""], ["bsprite", "b2", ""],
      ["bsprite", "shield", "res://art/prologue/shield.png", 297, 36 + 8 * k, {"frames": 6, "fps": 14, "loop": False, "z": 2}],
      ["sfx", "sh_shield"],
      ["wait", 0.3], takes=0.46)
S(["bsprite", "shield", ""])
F("Ivan", ["[happy] Ha! Was that a sneeze?"], "Ivan the Rabble")
tl.note("his salvo, on the drum fill: the first hits burn along her hull, the big one shears her starboard wing off")
tl.at(59.88, "salvo")
S(["bsprite", "g1", "res://art/prologue/bolt_green.png", 366, 120, {"flip": True, "z": 3}], ["bsprite", "g2", "res://art/prologue/bolt_green.png", 376, 170, {"flip": True, "z": 3}],
  ["bsprite", "g3", "res://art/prologue/bolt_green.png", 366, 210, {"flip": True, "z": 3}], ["bsprite", "g4", "res://art/prologue/bolt_green.png", 380, 250, {"flip": True, "z": 3}],
  ["sfx", "sh_laser"],
  ["bmoves", [["g1", 190, 170], ["g2", 215, 182], ["g3", 160, 192], ["g4", 200, 205]], 0.3, "in"], takes=0.3)
tl.at(60.2, "first hit")
S(["bsprite", "g1", ""], ["bsprite", "g2", ""],
  ["bsprite", "h1", "res://art/ships/fx/hit.png", 174, 148, {"frames": 6, "fps": 12, "loop": False, "z": 4}],
  ["bsprite", "c1", "res://art/prologue/chip.png", 192, 166, {"frames": 4, "fps": 14, "scale": 2, "z": 5}],
  ["bmoves", [["c1", 130, 70]], 1.2, "out", "nowait"],
  ["sfx", "sh_explode"], ["shake", 0.4, 2.0], ["flash", "c94a4a", 0.4])
tl.at(60.4, "second hit")
S(["bsprite", "g3", ""],
  ["bsprite", "h2", "res://art/ships/fx/hit.png", 200, 160, {"frames": 6, "fps": 10, "loop": False, "z": 4}],
  ["bsprite", "c2", "res://art/prologue/chip.png", 218, 178, {"frames": 4, "fps": 11, "scale": 2, "z": 5}],
  ["bmoves", [["c2", 300, 250]], 1.2, "out", "nowait"],
  ["sfx", "sh_explode"], ["shake", 0.4, 2.0])
tl.at(60.6, "third hit")
S(["bsprite", "g4", ""],
  ["bsprite", "h3", "res://art/ships/fx/hit.png", 146, 172, {"frames": 6, "fps": 11, "loop": False, "z": 4}],
  ["bsprite", "fire", "res://art/ships/fx/fire.png", 126, 150, {"frames": 4, "fps": 8, "scale": 2, "z": 3, "bob": BOB}],
  ["bsprite", "smoke", "res://art/ships/fx/smoke.png", 114, 116, {"frames": 4, "fps": 6, "scale": 2, "z": 3, "bob": BOB}],
  ["sfx", "sh_explode"], ["shake", 0.4, 2.0])
tl.at(61.39, "the big hit: the wing")
S(["bsprite", "ship", HURT, *AT, {"z": 2, "bob": BOB}],
  ["bsprite", "wing", WING, AT[0]+73, AT[1]+115, {"frames": 8, "fps": 8, "z": 5, "bob": BOB}],
  ["bmoves", [["wing", 420, 380]], 1.4, "out", "nowait"],
  ["bsprite", "h1", "res://art/ships/fx/hit.png", 141, 214, {"frames": 6, "fps": 12, "loop": False, "z": 4}],
  ["bsprite", "c3", "res://art/prologue/chip.png", 162, 240, {"frames": 4, "fps": 16, "z": 5}],
  ["bmoves", [["c3", 110, 340]], 1.2, "out", "nowait"],
  ["bsprite", "sparks", "res://art/prologue/sparks.png", 145, 223, {"frames": 6, "fps": 12, "z": 4, "bob": BOB}],
  ["bsprite", "flame1", PLUME, *FL1, {"frames": 4, "fps": 20, "alpha": 0.7, "scale": 3, "z": 1, "bob": BOB}],
  ["bsprite", "flame2", PLUME, *FL2, {"frames": 4, "fps": 17, "alpha": 0.55, "scale": 3, "z": 1, "bob": BOB}],
  ["sfx", "sh_explode"], ["sfx", "hull_tear"], ["shake", 1.0, 3.0], ["flash", "c94a4a", 0.7])
tl.at(61.6, "damage report")
F("", ["Starboard wing gone. Shields offline. Hull integrity at eighteen percent."], "Ship computer", [5.5])
S(["bsprite", "h1", ""], ["bsprite", "h2", ""], ["bsprite", "h3", ""], ["bsprite", "c1", ""], ["bsprite", "c2", ""],
  ["bsprite", "c3", ""], ["bsprite", "wing", ""], ["sfx", "sh_alarm"])
F("", ["No time. No course."], "You (thinking)", [2.1])
tl.at(69.675, "the lever, as the finale comes in")
S(["sfx", "beam_charge"],
  ["bsprite", "streaks", "res://art/prologue/jump_streaks.png", 0, 0, {"alpha": 0.0, "z": 8}],
  ["bfade", "streaks", 0.35, 7.0, "nowait"],
  ["bsprite", "flame1", PLUME, *FL1, {"frames": 4, "fps": 24, "scale": 3, "z": 1, "bob": BOB}],
  ["bsprite", "flame2", PLUME, *FL2, {"frames": 4, "fps": 22, "scale": 3, "z": 1, "bob": BOB}],
  ["shake", 7.2, 1.0])
F("", ["You slam the FTL lever."])
F("", ["Fold drive at ninety percent. Warning. Warning."], "Ship computer", [3.9])
tl.at(76.84, "the jump, on the last hit")
tl.note("the blind jump: what's left of her streaks away along her heading, and she's gone")
S(["sfx", "sh_fold"],
  ["bsprite", "flame1", ""], ["bsprite", "flame2", ""], ["bsprite", "fire", ""], ["bsprite", "smoke", ""], ["bsprite", "sparks", ""],
  ["bfade", "streaks", 1.0, 0.15, "nowait"],
  ["shake", 0.8, 4.0],
  ["bmove", "ship", 800, -14, .35, "in", "nowait"],
  ["wait", .22], ["flash", "fff3d6", .48], ["wait", .13], takes=0.35)
F("", ["Space folds around you, and the asteroid belt is gone."])
S(["score_end"], ["music", "silence"], ["fade", 1.0, 0.8], ["board", ""], takes=0.8)
song1_end = tl.t

# ---------------------------------------------------------------- the moon and the crash, in silence
tl.t = 0.0
tl.note("a moon nobody charted, with a few lights on its rim (the main menu's own picture)")
S(["board", "res://art/prologue/approach.png"],
  ["bsprite", "fall", "res://art/prologue/streak.png", -160, 116, {"frames": 4, "fps": 14, "z": 2}],
  ["fade", 0.0, 0.8], takes=0.8)
F("", ["Deep inside the Neutral Zone, a moon nobody bothered to chart.",
       "A few lights glimmer on its rim. Somebody lives down there."])
S(["sfx", "sh_fire"],
  ["bmove", "fall", 225, 298, 1.8, "in"],
  ["bsprite", "fall", ""],
  ["bsprite", "boom", "res://art/prologue/impact.png", 245, 236, {"frames": 10, "fps": 10, "loop": False, "z": 2}],
  ["sfx", "sh_explode"],
  ["shake", 0.6, 2.0],
  ["wait", 1.2],
  ["fade", 1.0, 0.8],
  ["board", ""],
  ["ambient", "none"],
  ["sfx", "crash_impact"],
  ["shake", 1.2, 3.0], takes=3.8)
F("", ["Stone and metal, screaming. Then nothing at all."])
tl.note("the crash site: the game's own cavern, your fighter (the Needle without her wing, burning at the stump and the engines) nose-first in the rubble under the hole she punched through the roof, the Mother-Drone asleep across the cavern with crystal grown up round it")
S(["go", "crash_site", 21, 13, "d"],
  ["hide", "player"],
  ["ambient", "amb_caves"],
  ["wsprite", "shaft", "res://art/prologue/light_shaft.png", 7.5, 1.0, {"add": True, "alpha": 0.7, "z": -2}],
  ["wsprite", "motes", "res://art/prologue/motes.png", 7.5, 1.0, {"frames": 8, "fps": 3, "add": True, "z": -1}],
  ["wsprite", "grit", "res://art/prologue/grit.png", 11.0, 1.3, {"frames": 12, "fps": 7}],
  ["wsprite", "fire", "res://art/ships/fx/fire.png", 9.7, 15.5, {"frames": 4, "fps": 8}],
  ["wsprite", "fire2", "res://art/ships/fx/fire.png", 7.0, 13.8, {"frames": 4, "fps": 7}],
  ["wsprite", "smoke", "res://art/ships/fx/smoke.png", 6.9, 12.8, {"frames": 4, "fps": 5, "alpha": 0.8, "bob": [2, 3.0]}],
  ["wsprite", "sparks", "res://art/prologue/sparks.png", 9.4, 15.2, {"frames": 6, "fps": 10}],
  ["wsprite", "blink", "res://art/prologue/blink.png", 11.6, 12.9, {"frames": 2, "fps": 2}],
  ["wait", 0.8],
  ["sfx", "water_drip"],
  ["fade", 0.0, 2.0],
  ["sfx", "fire_crackle"], takes=2.8)
F("", ["Red emergency lights flicker across your tilted cockpit. Grit trickles down through the hole you punched in the roof.",
       "Somewhere in the dark, water drips."])
S(["sfx", "hull_groan"])
silent = tl.t

# ---------------------------------------------------------------- Lunar Discovery, from the drone's first sighting
tl.note("Lunar Discovery from a phrase start (62.95 s) as you see the drone; it wakes on an accent (104.06), the beam reaches you on another (145.4), the glyphs fold into the mark as the song comes back in full (173.28), and the drone dies on the last chord (191.21), its light going out with the slow wind-down")
tl.start_song("lunar_discovery", 62.95)
tl.at(63.1, "the drone sighted")
F("", ["Across the cavern, half sunk in the basalt, lies something enormous:",
       "seamless, silver, shaped like a sleeping seed, with violet crystal grown up through the cracks in its shell."])
S(["board", CLOSE])
F("", ["Spacers tell stories about things like this. Silver lights that hum like struck glass and never show on a scanner.",
       "Terran scholars call the Starborn a myth: a people from before everyone, who left nothing but ruins nobody can date.",
       "Nobody grows a ship. But nothing on that shell was built. No seam, no rivet, no weld."], "You (thinking)")
S(["board", ""], ["sfx", "hull_groan"])
F("", ["What's left of your ship settles with a groan."], "", [3.3])
tl.at(104.06, "the drone wakes")
S(["sfx", "mother_iris"], ["board", CLOSE],
  ["bsprite", "close_light", CLOSE_WAKE, *CLOSE_AT, {"frames": 10, "fps": 5, "loop": False}],
  ["wsprite", "dglow", "res://art/prologue/drone_glow.png", 22, 6, {"add": True, "alpha": 0.0, "z": -3}],
  ["wsprite", "drone", "res://art/prologue/mother_drone_wake.png", 24, 8, {"frames": 8, "fps": 5, "loop": False}],
  ["wfade", "dglow", 0.6, 1.6, "nowait"])
F("", ["A deep hum rises through what's left of your hull, like a struck crystal. Gold light runs through its veins,",
       "and the crystals catch it."])
tl.at(115.26, "it speaks")
S(["bsprite", "close_light", CLOSE_PULSE, *CLOSE_AT, {"frames": 8, "fps": 3}],
  ["wsprite", "drone", "res://art/prologue/mother_drone_pulse.png", 24, 8, {"frames": 6, "fps": 3}])
F("MotherDrone", ["...Signal... faint... Core reserves at 0.04 percent...", "...An organic mind. Close."], "???")
tl.at(123.04, "its story")
F("MotherDrone", ["...You fell through the roof of the world... and did not break. Good.",
                  "...Long before your sun had a name, we were sown here. Seeds... left to wake when the small worlds needed tending.",
                  "...The makers went on. Not gone. Further. Larger. Your words for them are... storms. And stars."], "???")
S(["board", ""])
tl.at(144.60, "the lens sends a pilot ray")
S(["sfx", "mother_transfer"],
  ["wsprite", "beam", "res://art/prologue/crash_beam_reach.png", 11, 9, {"frames": 6, "fps": 7.5, "loop": False, "alpha": .85}])
tl.at(145.4, "the beam reaches you")
S(["wsprite", "beam", "res://art/prologue/crash_beam.png", 11, 9, {"frames": 4, "fps": 4, "alpha": .67}],
  ["board", "clear"],
  ["bsprite", "glyphs", "res://art/prologue/glyphs.png", 0, 0, {"frames": 12, "fps": 9, "alpha": 0.0}],
  ["bfade", "glyphs", 1.0, 0.8, "nowait"])
F("", ["The light pours into you. Star-glyphs wheel through your sight: strange, musical, and warm."])
F("MotherDrone", ["...Too late for me. Not for you.",
                  "...A little of me goes with you. The others are waiting. You will hear them, and they will hear you..."], "???")
F("MotherDrone", ["...They are Custodians. Broken tools, waiting for hands."], "???")
tl.at(172.45, "the glyphs fold")
S(["bsprite", "glyphs", "res://art/prologue/glyph_fold.png", 0, 0, {"frames": 8, "fps": 10, "loop": False}])
tl.at(173.28, "the mark, as the song comes back in")
S(["bsprite", "glyphs", ""],
  ["bsprite", "mark", "res://art/prologue/glyph_mark.png", 608, 12, {"alpha": 0.0, "z": 3}],
  ["bfade", "mark", 1.0, 0.4, "nowait"])
F("MotherDrone", ["...Three sleep close, behind glass. Others in the stone, in the storm, on a world that never sees its night..."], "???")
S(["board", CLOSE], ["bsprite", "close_light", CLOSE_PULSE, *CLOSE_AT, {"frames": 8, "fps": 2.5}],
  ["bfade", "mark", 0.0, 1.6, "nowait"])
F("MotherDrone", ["...Remember... the song...", "...Tend the small... worlds..."], "???")
tl.at(191.21, "it dies on the last chord")
S(["sfx", "mother_extinguish"],
  ["bsprite", "close_light", CLOSE_DIM, *CLOSE_AT, {"frames": 10, "fps": 4.5, "loop": False}],
  ["wfade", "beam", 0.0, 1.2, "nowait"],
  ["wfade", "dglow", 0.0, 7.5, "nowait"],
  ["wfade", "drone", 0.0, 7.8, "nowait"])
F("", ["The hum sinks, and stops. The golden veins fade back to dark silver."])
S(["board", ""], ["score_end"], ["music", "silence"])
S(["fade", 0.7, 1.2], ["sfx", "rescue_receiver"])

if tl.log:
    print("\n".join(tl.log))
    sys.exit(1)
print("before the music %.1f s; Space Battle part ends at %.1f; crash in silence %.1f s; Lunar part ends at %.1f"
      % (pre_music, song1_end, silent, tl.t))


def gd(v):
    return json.dumps(v, ensure_ascii=False).replace(": ", ": ")


out = []
for s in tl.steps:
    if s[0] == "#":
        words, line = s[1].split(), "\t\t\t#"
        for wd in words:
            if len(line) + len(wd) + 1 > 118:
                out.append(line)
                line = "\t\t\t#"
            line += " " + wd
        out.append(line)
    else:
        out.append("\t\t\t" + gd(s) + ",")
text = "\n".join(out) + "\n"

src = open(P).read()
a = src.index('\t\t"steps": [\n', src.index('"prologue": {')) + len('\t\t"steps": [\n')
b = src.index('\t\t\t["say", "Sara", ["Unidentified vessel', a)
src = src[:a] + text + src[b:]
open(P, "w").write(src)
print("wrote", len(tl.steps), "steps")
