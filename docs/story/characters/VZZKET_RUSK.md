# Vzz'ket & Rusk: the side arc, The Night Watch (23 Nov 2026)

**Their own arcs:** [`VZZKET.md`](VZZKET.md) and [`RUSK.md`](RUSK.md) (Zachary, 23 Nov: "I'm fine with shared side arcs but they need single arcs too"). This is the side arc they share, like Jasper & Evarra's.

**Decided with Zachary, 23 Nov:**
- **Trimmed to three scenes** (Zachary, 23 Nov, for every side arc: "trim to 3"): 2, 4 and 8. The 6 (On the House) is cut; its heart lives on in 8, where Rusk apologises and opens the Friday Open-Mic at the gate, and Vzz'ket tells his true story under the new sign. The 6's script is kept at the end of this doc.
- **The shell in 4** is a crawler brood-mother's, broken open by **the Leviathan** ("sure"): that's what the crawlers are running from, and its heartbeat is what Zaas hears in his 4 (story thread F).
- **"The Nest" is now "The Broken Shell"** (Decision 16): the Rabble's Nest keeps its name.
- **S.A.R.A.'s sensors moved to Vzz'ket's own 8**, where he stops guarding night and day. This side arc's 8 keeps Ix'ali's traps, Rusk's toast and the sign.
- **The Secret Reserve** is Ilsa's wine (Rusk's own arc). In this arc's 8 Rusk opens one of its last bottles; in his own 8 he gives you her vine.

**The arc:** the barman who tells tall tales, and the hunter nobody believes.
- 2: Rusk's bug joke, and the one person at the counter who isn't laughing.
- 4: the shell; Rusk takes back about forty jokes.
- 8: the traps, a bottle from the Secret Reserve, Rusk's apology and the Friday Open-Mic, and Ix'ali on watch; the bar gets its name, THE NIGHT WATCH, and Vzz'ket tells his true story.

**Both need the hearts** (`"who": "Vzz'ket", "with": ["Rusk"]`). Right answers give +60 (High Friendship) to each. Wrong ones: −20 with Vzz'ket, and in 4 a crawler bite as well (−10 energy). Their weeks are in their own docs.

**What's whose:** the outlines are the NPC Master's; the scenes and every line are drafts by Claude.

**Flags this arc sets:** `vzzket_tall_tales` (2), `vzzket_shell` (4), `vzzket_open_mic` (Friday nights at the bar for Vzz'ket, Ix'ali on the gate), `vzzket_sentinels` and the perk `perk_chitin_piercer_traps` (all 8).

---

## In the game (23 Nov)

All three are playable cutscenes in `scripts/heart_events.gd` (`nightwatch_2`, `nightwatch_4`, `nightwatch_8`, after Rusk's own). Not run in Godot yet.

- In 8 the scene moves from the gate to the bar (`go`), where Rusk hangs the sign. The bar's stage (built on 21 Nov) is where Vzz'ket's Fridays are from then on.
- **S.A.R.A.** speaks over the bar speakers in 2.
- **To test:** in a debug build, **F12** plays the next event in order, **Ctrl+F12** all of them in a row (F12 sets the hearts, day and time each one needs).
- **Not in yet:** the traps in play (a flag); the broken shell, the traps and the new sign as art (Art Fix List). The bar's run-down state and its repair are still to be designed; the sign could become part of that.

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

## ♥8 Sentinels of Echo Landing

**Trigger:** the cavern gate, 21:00–23:30, both at 8 hearts. Ix'ali, and Rusk with a bottle. Reward: Chitin-Piercer Traps at the cavern gate.

- *[The cavern gate, near midnight. Ix'ali is fitting long black spikes into iron frames along the barricade.]*
- *[Crawler traps, forged from the shells that came up the stair.]*
- **IX'ALI:** "[happy] Chitin-piercers! Their own shells, made into their own teeth. Vzz'ket's design, my forge."
- **VZZ'KET:** "They will hold a brood until morning. Then I will have words with it."
- **RUSK:** "[happy] Gentlemen! Lady! A toast. One of the last bottles of my Secret Reserve."
- **RUSK:** "I've been saving it for something worth saving it for. This is it."
- **RUSK** *(from the cut 6)*: "[sad] And an apology. I told the bug story wrong for a year. I've seen what they were running from. I'm done laughing at you."
- **RUSK:** "[happy] So: from this Friday the stage at my bar is open, every week. Stories, songs, lies if you must."
- **RUSK:** "[happy] And your drinks are on the house, friend. Forever. ...Within reason."
- **VZZ'KET:** "...I do not tell stories."
- *(The Friday Open-Mic starts: `vzzket_open_mic`.)*
- **RUSK:** "And then, friend: one drink. At my bar. I've something to show you."
- *If S.A.R.A.'s sensors are in (his own 8 has played):*
  - **IX'ALI:** "The machine's box and I have the gate tonight. Go, before I change my mind."
- *If not:*
  - **IX'ALI:** "I have the gate tonight. And on Fridays, it seems. Go, before I change my mind."
- **RUSK:** "You've known him longest, pilot. Who keeps the gate tonight?"
- **CHOICE:**
  - **"Ix'ali does. Vzz'ket's coming for a drink."** (+High Friendship)
    - **VZZ'KET:** "...One drink."
    - **IX'ALI:** "[happy] Two. I am counting."
    - *[Rusk's bar, a little after midnight. Rusk climbs onto a chair by the door with something wrapped in a sack.]*
    - *[He pulls the sack away. Hand-painted, and only slightly crooked: THE NIGHT WATCH.]*
    - **RUSK:** "[happy] Had it in the back for a week. Every bar needs a name, and this one finally earned it."
    - **VZZ'KET:** "...You named your bar after my work."
    - **RUSK:** "[happy] After the folk who keep it. You at your gate, me at mine. Sit down, friend. The stool knows better than to bite you."
    - **RUSK:** "[happy] And the first story on my stage is yours, Friday. Practise on us."
    - **VZZ'KET** *(from the cut 6)*: "...A true one, then. It is short."
    - **VZZ'KET:** "My first night at the gate, a crawler came up the stair carrying its young on its back. I let it pass."
    - **VZZ'KET:** "[sad] Every night since, I have wondered what it was carrying them away from. Now I know. That is the story."
    - **RUSK:** "[happy] ...It'll do, friend. It'll more than do."
    - **VZZ'KET:** "[happy] Sleep well, pilot. ...Tonight, that is what the armourer is for."
    - *(+60 friendship with Rusk)*
  - **"Vzz'ket should stay on watch. Just in case."**
    - **VZZ'KET:** "...Yes. Just in case."
    - *[Rusk pours three small glasses on top of the barricade and leaves the fourth beside Vzz'ket. He doesn't touch it.]*
    - **RUSK:** "[sad] Next time, then. There's always a next time down here. That's rather the trouble."
    - *(-20 friendship with Vzz'ket)*
- *[Perk: Chitin-Piercer Traps at the cavern gate]*

---

## Cut (Zachary, 23 Nov: side arcs are three scenes)

Kept here for the record; its apology, the Open-Mic and Vzz'ket's true story moved into 8, and Rusk's forty years are his own arc's 6 (The Sea Chest). The code is in git history (`nightwatch_6`, before 23 Nov's trim).

### ♥6 On the House (cut)

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
