# Vzz'ket & Rusk: heart events and their weeks (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **The shell in 4** is a crawler brood-mother's, broken open by **the Leviathan** ("sure"): that's what the crawlers are running from, and its heartbeat is what Zaas hears in his 4 (story thread F).
- **"The Nest" is now "The Broken Shell"** (Decision 16): the Rabble's Nest keeps its name.
- **Rusk is not Saffi's uncle** (that was Claude's placeholder), "but can be a figure in their lives": he has turned up for every birthday until nobody could tell the difference. Saffi's line in the game says so now, and he has lunch with her and Kit on Mondays.
- **Vzz'ket is old-school Zaa'sh and doesn't like S.A.R.A. at the start** ("a voice with no throat"), **but he respects Tar'Besh**, so in 8 he trusts the radar (S.A.R.A.'s sensors) because the cleric asks him to. This is one small step, not the big Zaa'sh change the main story's ending brings.
- **Their weeks** as Claude suggested (below).
- **Claude's rework of places, accepted:** the bar, the North Cave, the bar's stage, the cavern gate (three of the four were in the bar).

**The arc:** the barman who tells tall tales, and the hunter nobody believes.
- 2: Rusk's bug joke, and the one person at the counter who isn't laughing.
- 4: the shell; Rusk takes back about forty jokes.
- 6: Rusk says sorry in front of everyone and opens the stage; Vzz'ket's true story, then Rusk's.
- 8: the radar, the traps and a bottle from the Secret Reserve; Vzz'ket leaves the gate for one drink, and the bar gets its name: THE NIGHT WATCH.

**Both need the hearts** (`"with": ["Rusk"]`; the events are Vzz'ket's). Right answers give +60 (High Friendship) to each. Wrong ones: −20 with Vzz'ket (2, 6, 8), and in 4 a crawler bite as well (−10 energy, −20). Both are platonic, so they cap at 8 hearts.

**What's whose:** the outlines are the NPC Master's; the scenes and every line are drafts by Claude.

**Flags this arc sets:** `vzzket_tall_tales` (2), `vzzket_shell` (4), `vzzket_open_mic` (6), `vzzket_sentinels` and the perks `perk_chitin_piercer_traps` and `perk_secret_reserve` (8).

---

## Their weeks (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

**Rusk**

| Day | Where he goes |
|---|---|
| Tuesday to Sunday (unchanged) | Behind the counter from 07:00; dinner; the bar again 18:50; bed 23:55 |
| Monday (his morning off: the bar opens at 18:00) | A soak at the bath house 09:30; lunch by the fountain with Saffi and Kit; Bram's in the afternoon; dinner; the bar from 18:00 |

A whole day shut would have left Job, Freya, Garrick and Bram at a dark bar, so it's a morning off. The calendar lists Monday as his day off.

**Vzz'ket**

| When | Where he goes |
|---|---|
| Every day at first (unchanged) | The cavern gate from 06:00; dinner; the gate again 19:00; the promenade 22:00; his bedroll by the gate 23:30 |
| Fridays, after his 6 | The gate by day; dinner; the Open-Mic seats in the bar from 19:00. Ix'ali holds the gate (she spars there every evening anyway). |
| Sundays, after his 8 (his day off) | Breakfast; the museum with Tar'Besh 09:30; lunch; holo-darts at the bar 13:30; dinner; the stage seats 19:00 |

- **Day lines:** Rusk's Monday; Vzz'ket's Friday and Sunday, and Ix'ali's Friday, only once the scene that earns them has played. `DAY_LINES` entries can now be `{"flag": f, "lines": [...]}` (`main.gd _day_line()`).
- Vzz'ket isn't on the calendar's days-off list (it can't read story flags yet).

---

## In the game (23 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`vzzket_2` to `vzzket_8`, after Zaas's). Not run in Godot yet.

- **Heart-event sheets** are new for **Vzz'ket and Rusk** (`art/npc_vzzket_event.png`, `art/npc_rusk_event.png`, from the rig by `tools/events.py`). They also use their action rows: his guard stance with the spear; Rusk pouring.
- **The bar's stage** (built on 21 Nov for this) gets its first use in 6. In 8 the scene moves from the gate to the bar (`go`), where Rusk hangs the sign.
- **S.A.R.A.** speaks over the bar speakers in 2 and through the radar in 8; there's no pad in the mine.
- **To test:** in a debug build, **F3** plays the next event in order (6 waits for a Friday; F3 moves the day on).
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **Not in yet:** the traps, the radar and the Secret Reserve in play (they're flags); the broken shell, the radar box and traps, and the new sign as art (all on the Art Fix List). The bar's run-down state and its repair are still to be designed; the sign could become part of that.

---

## ♥2 Tall Tales at the Bar

**Trigger:** Rusk's bar, 22:00–23:30, both at 2 hearts. Job and Freya are at the counter.

- *[Rusk's bar, late. The good lamps are on and the bad ones are flickering.]*
- *[Rusk is holding court for Job and Freya. At the far end of the counter, Vzz'ket sits alone, sharpening his spear.]*
- **RUSK:** "[happy] There's our pilot! Pull up a stool. Not that one. You're just in time for the bit about the bugs."
- **RUSK:** "So the bugs are all marching up out of the caverns. Hundreds of them, little legs going like pistons."
- **RUSK:** "And where are they all headed? [happy] Here! Happy hour!"
- **JOB:** "[happy] Ha! Somebody pour those bugs a drink, cher."
- **S.A.R.A.** *(speakers)*: "[happy] Last orders in thirty minutes, everyone! Rusk, that means you too."
- **VZZ'KET:** "[angry] The machine. Even here, it counts our cups."
- **RUSK:** "She's all right, Vzz'ket."
- **VZZ'KET:** "She is a voice with no throat."
- *[The scrape of the whetstone stops.]*
- **VZZ'KET:** "Three this week, barman. Last month, three in the whole month."
- **RUSK:** "[happy] Then they like the place! Word's getting round."
- **VZZ'KET:** "[angry] They are not coming for your happy hour. They are running."
- **CHOICE:**
  - **"What are they running from?"** (+High Friendship)
    - **VZZ'KET:** "...You ask. No one asks."
    - **VZZ'KET:** "I do not know. Something that eats things with many legs. I would like to know before it finds the way up."
    - **RUSK:** "[sad] ...Well. That's less funny."
    - *[Rusk pours something dark into a clean glass and slides it down the counter. Vzz'ket looks at it for a long moment, then drinks.]*
    - *(+60 friendship with Rusk)*
  - **"[Laugh along with Rusk]"**
    - **VZZ'KET:** "[angry] Laugh, then. Sleep well. That is what I am for."
    - **RUSK:** "[sad] ...He'll be back. He always comes back. ...Doesn't he?"
    - *(-20 friendship with Vzz'ket)*

## ♥4 The Broken Shell (was The Nest)

**Trigger:** the North Cave, 19:00–22:00, after 2. The far east end of the cave.

- *[The North Cave after dark. Vzz'ket waits at the mouth with a lantern hung on his spear.]*
- *[Rusk is with him, in a coat far too good for caves, holding a flask.]*
- **RUSK:** "[happy] I'm here as a witness. When we find nothing, I want it on record that I found it first."
- **VZZ'KET:** "Stay behind me. Both of you. Step where I step."
- *[Past the glowing moss, past the last of Quill's chalk marks, to the far east wall, where nobody goes.]*
- *[Wedged between the rocks: a crawler shell as big as a shuttle, its plates split open from the outside.]*
- *[Something has scored them in long, deep grooves, like fingers dragged through clay.]*
- **RUSK:** "[shocked] ...That's a bug? That's one of our bugs?"
- **VZZ'KET:** "Their mother. A brood-queen. Every crawler on this moon came out of something like her."
- **VZZ'KET:** "[sad] Something broke her open like an egg. Then it ate what was inside. Then it went back down."
- **VZZ'KET:** "Down toward the water the fish-man keeps listening for."
- *[Rusk takes a long pull from his flask, then holds it out to Vzz'ket. After a moment, Vzz'ket takes it.]*
- **RUSK:** "[sad] I need you both to know I'm taking back about forty jokes."
- **CHOICE:**
  - **"Thank you for showing us."** (+High Friendship)
    - **VZZ'KET:** "...Someone else should know. If it comes up the stair one night, someone else should know what it is."
    - **RUSK:** "[sad] The whole station's going to know, friend. I'll see to it. Nobody believes a word I say. That's why it works."
    - *(+60 friendship with Rusk)*
  - **"Let's take a piece home. Bram would pay a fortune."**
    - *[You lever at a loose plate. It comes away with a crack that rings through the whole cave, and something skitters in the dark.]*
    - *[A crawler drops from the ceiling onto your arm. Vzz'ket's spear flicks it away before you've even shouted.]*
    - **VZZ'KET:** "[angry] The dead call the living. Never take from a kill you did not make."
    - *(-10 energy)*
    - *(-20 friendship with Vzz'ket)*
- **VZZ'KET:** "We go back now. Quietly."

## ♥6 On the House

**Trigger:** Rusk's bar on a Friday, 19:00–21:00, after 4. Job, Freya, Bram, Saffi and Kit are there. Starts Friday Open-Mic & Story Night.

- *[Friday night. Rusk has dragged two stage lights out of the cupboard and pointed them at the dusty corner stage.]*
- *[Half the Landing is here, because he told everyone it was important.]*
- **RUSK:** "Evening, all. Quiet, please. ...Job, that includes your stool."
- **RUSK:** "I've told a lot of stories in this bar. Some of them were even true. [sad] The one about the bugs, I told wrong."
- **RUSK:** "Our pilot and I went down the North Cave with Vzz'ket. I've seen what the bugs are running from."
- **RUSK:** "Or what's left after it's eaten. I'm done laughing at him."
- **RUSK:** "So. From tonight, every Friday, this stage is open. Tell a story, sing a song, lie if you must."
- **RUSK:** "[happy] And Vzz'ket's drinks are on the house. Forever. ...Within reason."
- **RUSK:** "[happy] The first story's his. Come on up, friend."
- **VZZ'KET:** "[angry] I do not tell stories."
- **CHOICE:**
  - **"Then tell them a true one."** (+High Friendship)
    - **VZZ'KET:** "...A true one. It is short."
    - **VZZ'KET:** "My first night at the gate, a crawler came up the stair carrying its young on its back. I let it pass."
    - **VZZ'KET:** "[sad] Every night since, I have wondered what it was carrying them away from. Now I know. That is the story."
    - **KIT:** "[happy] ...Again! Tell it again!"
    - **RUSK:** "[happy] Next week, lad. That's the rule now. Every Friday."
    - *(+60 friendship with Rusk)*
  - **"Tell them the bug joke!"**
    - **VZZ'KET:** "[angry] ...No."
    - *[Vzz'ket steps down and stands at the back with his arms folded. Rusk climbs back up, rather quickly.]*
    - *(-20 friendship with Vzz'ket)*
- **RUSK:** "[happy] My turn, then. Forty years behind bars. My first was the back of a cargo hauler."
- **RUSK:** "Two bottles, three cups and one borrowed stool. The stool bit people. [happy] It's that stool. Job's on it."
- **RUSK:** "[sad] Every bar I ever had, I lost. To a war, to a landlord, to a fire."
- **RUSK:** "This one's a ruin, and the lights go when they like. I'm keeping it."
- **SAFFI:** "[happy] Hear, hear!"

## ♥8 Sentinels of Echo Landing

**Trigger:** the cavern gate, 21:00–23:30, both at 8 hearts. Tikka, Tar'Besh, and Rusk with a bottle. Rewards: Chitin-Piercer Traps and the cavern monster radar (Vzz'ket); the Secret Reserve (Rusk).

- *[The cavern gate, near midnight. Tikka has bolted a squat grey box to the barricade, bristling with S.A.R.A.'s old station sensors.]*
- *[Tar'Besh is watching with his hands folded in his sleeves.]*
- **TIKKA:** "[happy] Motion, heat, and a sound pickup Zaas swears by. Anything bigger than a boot comes up that stair, the radar knows."
- **TIKKA:** "Ix'ali forged the spikes for the traps. Chitin-piercers. They'll hold a brood of crawlers till morning."
- **TIKKA:** "...And the radar tells S.A.R.A., and S.A.R.A. wakes whoever's on watch. That's the part he doesn't like."
- **VZZ'KET:** "[angry] I do not need a voice with no throat to tell me when to wake."
- **S.A.R.A.** *(the radar)*: "[sad] I don't sleep either, Vzz'ket. I thought that might be something we had in common."
- **TAR'BESH:** "Hunter. I have trusted her with every relic in the museum. She has not dropped one."
- **TAR'BESH:** "That is more than I can say for Pip. You may trust her with a door."
- **VZZ'KET:** "...You ask this, cleric? You?"
- **TAR'BESH:** "I do."
- **VZZ'KET:** "...Then I will try it. One night."
- **RUSK:** "[happy] Gentlemen! Lady! ...Box! A toast. This bottle's older than the station."
- **RUSK:** "I've been saving it for something worth saving it for. This is it."
- **RUSK:** "You've known him longest, pilot. Who keeps the gate tonight?"
- **CHOICE:**
  - **"The radar does. Vzz'ket's coming for a drink."** (+High Friendship)
    - **VZZ'KET:** "...One drink."
    - **S.A.R.A.** *(the radar)*: "[happy] I've got it. Go on. I'll wake you if anything so much as sneezes."
    - **VZZ'KET:** "[angry] Crawlers do not sneeze. ...Thank you."
    - *[Rusk's bar, a little after midnight. Rusk climbs onto a chair by the door with something wrapped in a sack.]*
    - *[He pulls the sack away. Hand-painted, and only slightly crooked: THE NIGHT WATCH.]*
    - **RUSK:** "[happy] Had it in the back for a week. Every bar needs a name, and this one finally earned it."
    - **VZZ'KET:** "...You named your bar after my work."
    - **RUSK:** "[happy] After the folk who keep it. Sit down, friend. The stool doesn't bite you. It knows better."
    - **VZZ'KET:** "[happy] Sleep well, pilot. ...Tonight, that is what the box is for."
    - *(+60 friendship with Rusk)*
  - **"Vzz'ket should stay on watch. Just in case."**
    - **VZZ'KET:** "...Yes. Just in case."
    - *[Rusk pours three small glasses on top of the barricade and leaves the fourth beside Vzz'ket. He doesn't touch it.]*
    - **RUSK:** "[sad] Next time, then. There's always a next time down here. That's rather the trouble."
    - *(-20 friendship with Vzz'ket)*
- *[Perk: Chitin-Piercer Traps and the cavern monster radar]*
- *[New at Rusk's: the Secret Reserve]*
