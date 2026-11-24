# Zaas: heart events and his week (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **The Scyldar are an ocean people.** Zaas grew up on Scyldar-home, a world that is mostly sea, and has not heard one since he left. That homesickness is the heart of his arc: he isn't chasing an ocean because he's eccentric, but because he misses one.
- **The sea's name:** Zaas names the underground ocean **the Merrow Deep**, after Merrow ("sure"). He says it in his 6.
- **Claude's rework, accepted ("rework anything you think should be fixed"):**
  - **2** moves to the East Complex reclamation plant (it was the East Agridome). Merrow's burst pipe is the choice.
  - **4** is at the sealed hatch of the mine's flooded stair, in the evening (was "the upper caverns"). The hydrophone hears tide, and under the tide a heartbeat: story thread F, the Leviathan. Merrow brings him the soup he missed.
  - **6** is on the lake's south beach (it waits for the Leviathan, as 6s may). He dives in, hat and all, and names the sea.
  - **8** is a diving bell, not a research skiff, at the end of the lake's west pier. That clears the repeat with Job's skiff (Job 10), and Job's "I'll dig him a tunnel" and Zaas's "a drill made of hope" pay off: the bell's pump is Job's spare drill motor. Merrow dives first, then he pins the water officer's badge on her. 8s never wait, so until the Leviathan is dead it's a test dive in the plaza fountain, with Nub as safety officer.
- **Wrong choices** (Zachary: "minor consequences"): 2, everyone's soaked and nothing is gained (−10 energy, no friendship); 4, 6 and 8, −20 friendship.

**The arc:** the water officer who was right about the ocean, and gave it to the one who kept the water running while he looked.
- 2: he signs the leak reports; she fixes them.
- 4: tide under the rock, and something else.
- 6: the first splash, and the sea's name.
- 8: the badge was always hers; he's Captain of the Deep.

**Merrow** (Moogli, hydroponics officer, Tobbin's partner, Nub's mother) is in every scene. Her own 8 should still be about her (see the review of Tobbin's arc), so this arc gives her the badge but not her story.

**What's whose:** the story is Zachary's; the scenes and every line are drafts by Claude. Right answers give +60 (High Friendship). He's platonic, so he caps at 8 hearts.

**Flags this arc sets:** `zaas_helmet` (2), `zaas_heartbeat` (4), `merrow_deep` (6), `zaas_captain` and the perk `perk_deep_sea_sonar_lure` (8).

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where he goes |
|---|---|
| Monday to Saturday | The mine from 07:00 (his ice survey); lunch; the mine again; dinner; stargazing in the Observation Lounge 19:15; home 23:00 |
| Sunday (day off: expedition day) | Breakfast; the North Cave with his hydrophone 09:00 (by the south wall), lunch, the North Cave again 13:30 (the north end); dinner; the lounge; home |
| Sunday, once the Leviathan is dead | Breakfast; the lake's south beach 09:00; a packed lunch on the sand 12:15; the end of the west pier 13:30; dinner; the lounge; home |

- **Day off:** Sunday (`NpcData.DAYS_OFF`; the station calendar shows it). **Day lines** for Sunday: expedition day, listening, and "report any ice".
- On lake Sundays Job is fishing at the old camp on the north shore, so the two of them share the lake.

---

## In the game (23 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`zaas_2` to `zaas_8`, after Tar'Besh's). Not run in Godot yet.

- **Heart-event sheets** are new for **Zaas and Merrow** (`art/npc_zaas_event.png`, `art/npc_merrow_event.png`, built from the rig by `tools/events.py`; their face colours are in its `FACES`). They also use their action rows: his hydrophone (survey), his spyglass (observe); her valve wheel.
- **New effects** (`scripts/scene_fx.gd`): **spray** (the burst pipe in 2, his dive in 6) and **bubbles** (his dive, the bell going down in 8). A scene can now switch an effect off (`["fx", kind, "off"]`), so the spray stops when the valve is shut.
- **The heartbeat** in 4 is two low thuds and a small shake, three times.
- **To test:** in a debug build, **F12** plays the next event in order, **Ctrl+F12** all of them in a row. For his 6 it now kills the Leviathan first (the game keeps that flag itself), so 8 then plays at the lake; the fountain version is checked offline only.
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **Not in yet:** fishing (the Sonar Lure is a flag until there is); the diving helmet, the diving bell and the winch, the hydrophone, the badge, and a splash sound (all on the Art Fix List).

---

## ♥2 Clipboard & Diving Helmet

**Trigger:** the East Complex, 09:00–16:00, any day but Sunday, with Zaas at 2 hearts. Plays in the reclamation plant, by the pipe manifold.

- *[The East Complex reclamation plant. Pumps thump, scrubbers rattle in their rows, and every scrubber has a number chalked on it.]*
- *[Merrow is bent over the pipe manifold with a wrench, a clipboard of leak reports tucked under one arm.]*
- **MERROW:** "Oh, good. Hands. Hold this clipboard. Every line on it is a leak, and every leak is mine."
- **MERROW:** "[angry] My chief signed the top one. Then he went back to his hobby."
- *[Across the room, Zaas sits on an upturned bucket, trying to get a battered brass diving helmet on over his hat. It does not go over his hat.]*
- **ZAAS:** "[happy] Ahoy! Water reclamation officer Zaas, testing the expedition's breathing apparatus."
- **ZAAS:** "A Scyldar diving helmet. Mine, from home. Rated to forty fathoms, which is forty more fathoms than this moon has. So far."
- **MERROW:** "Chief. The manifold."
- **ZAAS:** "The manifold is in excellent hands. Yours. I signed it."
- *[A seam on the manifold splits with a bang. Water sprays across the floor in a hissing fan.]*
- **MERROW:** "[shocked] That's the main line! The valve, I need the valve!"
- **ZAAS:** "[happy] Water! Quick, help me with the helmet! I'll go in after the leak!"
- **CHOICE:**
  - **"Help Merrow shut the valve."** (+High Friendship)
    - *[You put your weight on the wheel beside hers. It turns, grinding, and the spray dies to a drip.]*
    - **MERROW:** "[happy] There. Good hands and better sense. That's rare in this department."
    - **ZAAS:** "[sad] ...You are right, of course. A water officer whose plant is flooding should not be trying on hats."
    - **ZAAS:** "[happy] Merrow, you are a far better water officer than I am. I keep telling you so."
    - **MERROW:** "And I keep telling you the badge is on your chest, chief. Not mine."
  - **"Help Zaas with the helmet first."**
    - *[You wrestle the helmet down over his hat. By the time it seals, the floor is a pond.]*
    - *[Zaas strides off to save the day and walks straight into a scrubber. The glass has fogged solid.]*
    - *[Merrow shuts the valve herself in the end, soaked to the skin. So are you. So is Zaas, inside the helmet, somehow.]*
    - **MERROW:** "[angry] Next time: the valve. Then the hat."
    - *(soaked: -10 energy)*
- **ZAAS:** "[happy] When we find the ocean, the helmet comes with us. And so do you, I think."
- **MERROW:** "Clipboard, please. ...Thank you. Line one: done. Forty to go."

## ♥4 Sonar Echoes

**Trigger:** the mine, 18:00–22:30, after his 2. Plays at the sealed hatch of the flooded stair.

- *[The bottom of the mine, where the old stair goes down into the dark. Its steel hatch is beaded with water.]*
- *[Zaas is kneeling on the hatch with his hydrophone pressed flat to the steel. He hasn't heard you come in.]*
- **ZAAS:** "Shh. Kneel down. Here, take an earpiece."
- *[Static. Then the hiss of moving water: a long, slow swell, in and out, like breathing.]*
- **ZAAS:** "[love] Tide. Real tide, under real rock. There is enough water down there for the gas giant to pull on it."
- **ZAAS:** "That is not a puddle. That is a sea."
- *[Under the tide, slower and much deeper: a double thud. A long pause. Then again.]*
- **ZAAS:** "...That is not the pumps."
- **MERROW:** "Thought I'd find you down here. You missed supper, chief. Again. Soup."
- **ZAAS:** "Merrow! Listen. Tell me that is the pumps."
- *[Merrow sets the soup down and takes the earpiece. For a long moment her face goes very still.]*
- **MERROW:** "...That's not the pumps."
- **ZAAS:** "[sad] On Scyldar-home the sea sang all night. You fell asleep to it as a hatchling. You never once thought it could stop."
- **ZAAS:** "I have not heard a sea since the day I left. I did not know how hungry I was for it until just now."
- **CHOICE:**
  - **"Then let's go and find it."** (+High Friendship)
    - **ZAAS:** "[happy] 'Let's.' Merrow, did you hear that? Let's!"
    - **MERROW:** "[happy] I heard. Eat your soup first, captain."
  - **"It's just the pumps."**
    - **ZAAS:** "[sad] ...Perhaps. Perhaps it is only the pumps."
    - **MERROW:** "[angry] It isn't, and you heard it too. Don't take that off him."
    - *(-20 friendship)*
- *[Under the hatch, faint and slow, the double thud comes again. Zaas writes in his notebook: 'Tide. And something else.']*

## ♥6 First Splash

**Trigger:** the underground lake, 08:00–18:00, after his 4, **once the Leviathan is dead** (6s may wait for the story). Plays on the south beach.

- *[The south shore of the cavern sea. Pale sand runs down into black water so clear you can see crystals glowing on the bottom.]*
- *[Zaas stands at the water's edge with his boots in his hand. Merrow says he hasn't moved in an hour.]*
- **ZAAS:** "[love] I was right. I was right, and I am not even enjoying being right. Is that strange?"
- **MERROW:** "Very strange, chief. Go on, then. It's not getting any wetter."
- *[He runs into the shallows and dives, hat and all.]*
- **MERROW:** "...He can hold his breath for an hour, you know. Scyldar can. He's just never had anywhere to do it."
- *[Zaas comes up in a burst of spray and splashes back up the beach, laughing and crying at once, his hat floating out behind him.]*
- **ZAAS:** "[happy] Warm! It is warm! And salt, a little! Merrow! MERROW!"
- **MERROW:** "[happy] I'm right here, chief. You're dripping on me."
- **ZAAS:** "I told you I had named it already. I named it the night we heard the tide."
- **ZAAS:** "[love] The Merrow Deep. For the officer who kept every drop on this station clean while her chief went looking for ghosts."
- **MERROW:** "[shocked] Zaas. You can't name a sea after me."
- **ZAAS:** "[happy] I can. I found it."
- **CHOICE:**
  - **"It's perfect."** (+High Friendship)
    - **MERROW:** "[bashful] ...Don't you dare put it on a plaque."
    - **ZAAS:** "[happy] Tar'Besh is already making the plaque."
  - **"Shouldn't you name it after yourself?"**
    - **ZAAS:** "[sad] After me? I only listened. She kept us alive long enough to listen."
    - *(-20 friendship)*
- *[Zaas wades back in, fishes his hat out of the Merrow Deep, and puts it back on, dripping.]*
- **The next morning** *(Claude, 23 Nov)***:** a letter from Merrow, "About the plaque" (`merrow_plaque` in `scripts/mail_data.gd`). The text is in [MAIL.md](../MAIL.md).

## ♥8 Captain of the Deep

**Trigger:** the underground lake, 10:00–17:00, at the end of the west pier. **Backup** until the Leviathan is dead: the plaza fountain, same hours, with Nub instead of Job. Reward: the Deep-Sea Sonar Lure.

- *At the lake:*
  - *[The end of the west pier. A squat brass bell hangs from a winch over the water.]*
  - *[It's Zaas's old diving helmet, welded to a porthole and a drum of riveted plate, with a drill motor bolted on top to work the pump.]*
  - **JOB:** "My spare drill motor, cher. Told him I'd dig him a tunnel to the sea someday. Sea came to him first."
  - **ZAAS:** "[happy] And I told you I would build you a drill out of hope, Job. Here it is. It mostly works."
- *Before then (the backup):*
  - *[The plaza fountain, mid-morning. A squat brass bell sits on its rim, guarded very seriously by Nub.]*
  - *[It's Zaas's old diving helmet, welded to a porthole and a drum of riveted plate, with a drill motor bolted on top to work the pump.]*
  - **NUB:** "[happy] I'm the safety officer! If anybody drowns, I blow this whistle. I've been practising."
  - **ZAAS:** "[happy] The sea is shut until the stair is cleared. The fountain is not. A test dive, Officer Nub."
  - **NUB:** "The fountain only comes up to my knees. I've been in it loads."
- **ZAAS:** "One passenger goes down and the same passenger comes back up. That is the whole of the safety report."
- **ZAAS:** "Merrow. I would like you to go first."
- **MERROW:** "Me? Chief, it's your bell. Your sea. You've waited for this your whole life."
- **ZAAS:** "[love] And you kept the whole station alive while I was waiting. Go on."
- **CHOICE:**
  - **"Go on, Merrow. You've earned it."** (+High Friendship)
    - **MERROW:** "[happy] ...All right. All right! Don't let him lower it too fast."
  - **"Stay up top. It's dangerous."**
    - **MERROW:** "[angry] I fix live valves for a living, dear."
    - **ZAAS:** "[sad] She is right, and you are not wrong. But she is more right."
    - *(-20 friendship)*
- *At the lake:*
  - *[The winch clanks. The bell goes down with Merrow's face in the porthole, and a line of bubbles marks the spot.]*
  - *[Long minutes. Zaas counts every one of them out loud. Job pretends not to be counting too.]*
- *Before then (the backup):*
  - *[The winch clanks. The bell goes down into the fountain, all of a foot, with Merrow's face in the porthole.]*
  - **NUB:** "[happy] She's waving! Mum's waving at a coin!"
- *At the lake:*
  - **MERROW:** "[happy] Oh, chief. Oh, Zaas. There are lights down there. Whole fields of them, all the way down."
- *Before then (the backup):*
  - **MERROW:** "[happy] It's a fountain, and it was still wonderful. The whole plaza goes wobbly from underneath."
- *[Zaas unpins the water officer's badge from his own chest and pins it on hers.]*
- **ZAAS:** "Water Officer Merrow. It was always yours. I only held it while I went looking for the sea."
- **MERROW:** "[shocked] Then what are you?"
- **ZAAS:** "[happy] Captain of the Deep. I have already had a hat made."
- **ZAAS:** "And this is for you. It sings to fish the way the hydrophone listens to the sea. For whoever comes fishing in my ocean."
- *[New: the Deep-Sea Sonar Lure (for when there's fishing)]*
