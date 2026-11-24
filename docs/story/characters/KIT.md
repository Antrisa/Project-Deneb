# Kit: heart events and his week (24 Nov 2026)

**Decided with Zachary, 24 Nov:** "every character has own arc plus a short family shared arc": an arc each for Garrick, Saffi and Kit, and a two-scene family side arc ([GARRICK_SAFFI_KIT.md](GARRICK_SAFFI_KIT.md)). Claude's first suggestions for the rest, taken: **Garrick was security officer on the refugee transport that crash-landed here**, and a bounty hunter he let dock brought a Chernobog cutter down on it (so he distrusts your trade); **Kit's beacon** leads to a smuggler's cache on the jump map, and **his 8 is a deputy badge** you set down at home; their weeks: the model ship and the seals on Saturdays, Saffi's Monday lunch with Rusk and the market. **Then (Zachary, 24 Nov):** "garriks 8 heart is too powerful, change to self defense class, attacking boarders take extra damage on your ship" (it was Perimeter Defence: the station's guns softening up the first ship you fought on each run); "saffi increase max energy perk" (it was a Sunday potluck: share a dish for friendship with everyone and a well-fed morning).

**The family's story (Claude's drafts):** about forty refugees, Saffi and Kit (in a sling) among them, came down on this moon in a transport with its drive shot out, and S.A.R.A. talked them in. Every settler signed the scorched hull plate now in the museum; Kit's is a handprint. The first night, Saffi made soup for forty in a dented helmet. Most of the forty moved on later; they stayed.

**The arc:** the fastest fox on the station, who wants to be security chief, or a pirate, or a bounty hunter like you.
- 2: a race round the fountain. Run properly and he wins by a whisker; cut through the fountain and you're wet and a cheat.
- 4: a light out in the dark, from the telescope in his room: three long, two short. Saffi knows it: an old smuggler's mark.
- 6: Ix'ali's helmet and a WANTED poster: he's going to be a bounty hunter, like you. Garrick hears it. He swears Kit in as a junior security officer instead.
- 8: Junior Security Officer Kit at the old customs desk, with a rubber stamp. Every officer picks one deputy.

**What's whose:** the title of 4 (the NPC Master's "The Beacon", moved from the Observation Lounge to his own telescope) and his lines about the fountain edge and being security chief or a pirate were already there; the scenes, the cache and the badge are Claude's drafts. Right answers +60, middle +30, wrong −20 (in 2, −10 energy instead: you're soaked).

**Flags:** `kit_race` (2), `kit_beacon` (4), `kit_cache_found` (when you find the cache), `kit_security` (6), `kit_deputy` (8).

## Kit's beacon (his 4)

`ship_runs.gd place_cache`: from his 4 until you've found it, every free flight turns one beacon on the second ring (the first, if that's all that's open), in the Reach if there's one there, into **Kit's beacon** (a new stop kind, `"cache"`, in `ShipData.STOP_KINDS`). Going there (`main.gd _arrive_run`) gives a stronghold's haul without the fight, once, and sets `kit_cache_found`; Kit mentions it in his 6 if you've been.

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What he does |
|---|---|
| Weekdays (unchanged) | Lessons in the library; the fountain at lunch; home; holo-games; dinner; bed at half past eight. Monday afternoons with the Scouts once Artie starts them. |
| **Saturday** | The model ship with his dad at home in the morning, then the fountain. |
| **Saturday, after his 6** (`kit_security`) | The West Terminal's seals with Garrick in the morning, then the fountain. |
| First Saturday of a season | The Scouts' outing, as before (it wins over the two above). |

- **Day lines** for Saturday, before and after his 6 (`npc_data.gd DAY_LINES`).

## In the game (24 Nov)

All four are playable cutscenes (`kit_2` to `kit_8`), with his new heart-event sheet (`art/npc_kit_event.png`) and his action sheet (study, play, toy, holo-game). Not run in Godot yet.

- **Kit's deputy badge** (`deputy_badge`, icon 139, prop `art/lunar/deputy_badge.png`, stand-ins by Claude, `tools/dev/kit_art.py`): set it down at home from the hotbar, like Pip's rocket (`main.gd PLACEABLE`, `"decor"`).
- **Letter:** the morning after 4, "THE BEACON".

---

## ♥2 Fastest on the Station

**Trigger:** The plaza, 12:30–14:30, Monday to Friday. *(Claude)*

- *[Lunchtime on the plaza. Kit is doing laps of the fountain, very fast, with nobody chasing him.]*
- **KIT:** "[happy] You! You're new and you're tall. Race me. Round the fountain. Pip won't race me any more."
- **KIT:** "He says it's because he's busy. [angry] It's because I'm the fastest."
- **KIT:** "Once round, back to here. Three... two... ONE!"
- **CHOICE:**
  - **"Run as fast as you can."** (+High Friendship)
    - **KIT:** "[happy] WON! By a whisker! But you RAN. Properly! Nobody runs properly against me."
  - **"Let him win."** (+Friendship)
    - **KIT:** "[angry] You let me win. I can tell. Dad does it too. ...I still won, though."
  - **"Cut straight across the fountain."**
    - *[You climb over the edge and splash straight through the middle of the fountain. Kit stops dead.]*
    - **KIT:** "[angry] That's CHEATING. You're wet AND a cheater."
    - *(-10 energy)*
- **KIT:** "Same time tomorrow. I'm going to be security chief, and security chiefs have to be fast."
- **KIT:** "[happy] Or a pirate. Pirates have to be fast too. Dad says I can't be both."

---

## ♥4 The Beacon

**Trigger:** His room at home, 19:15–20:15 (before bed), after 2. With Saffi. *(The NPC Master's title, moved from the Observation Lounge; the scene is Claude's.)*

- *[Kit's room. He's up on his toes at his telescope, one eye screwed shut, counting under his breath.]*
- **KIT:** "[shocked] Don't move! It's blinking again. Look. Look! Out past the third bright star, down a bit."
- *[You look. Something tiny out in the dark blinks: three long, two short. Then nothing. Then again. Three long, two short.]*
- **KIT:** "It's not on my chart. Stars don't blink like that. [happy] It's a code! It's a pirate code!"
- **CHOICE:**
  - **"Let's write it down properly."** (+High Friendship)
    - **KIT:** "[happy] Like a real log! When, where, what it did!"
    - *[Kit writes it on his sky chart in enormous letters: 19:40. THREE LONG TWO SHORT. NOT A STAR.]*
  - **"Go and tell your mum."** (+Friendship)
    - **KIT:** "[angry] She'll just say it's bedtime."
  - **"It's just a star, Kit."**
    - **KIT:** "[sad] Stars don't blink in a code. ...You didn't even look properly."
    - *(-20 friendship with Kit)*
- **SAFFI:** "Bed in ten minutes, Captain. What's all this?"
- **KIT:** "[happy] A beacon, Mum! Three long, two short!"
- **SAFFI:** "...Three long, two short is an old smuggler's mark. Garrick will want to know."
- **SAFFI:** "[happy] And I suspect {name} will want to go and look."
- **KIT:** "Bring me something back! Not treasure. Well. Treasure if there's treasure."
- *[Kit's beacon goes on your jump map: a beacon on the second ring]*
- *[The next morning: a letter (`kit_coordinates`, in [MAIL.md](../MAIL.md))]*

---

## ♥6 Wanted

**Trigger:** The Shuttle Bay, 15:00–17:00, Monday to Friday, after 4. With Garrick. *(Claude)*

- *[The Shuttle Bay. A small fox in an enormous flight helmet stands on a crate by your ship, holding up a hand-drawn poster.]*
- **KIT:** "[happy] WANTED: the Chernobog. Reward: lots. I'm going to be a bounty hunter. Like you. I've got the helmet already."
- *If you've found the smuggler's cache:*
  - **KIT:** "And you found my beacon! Mum said it was a whole cargo pod! [happy] I found that. I'm basically a hunter already."
- *[The helmet comes down to his shoulders. It's Ix'ali's, borrowed without asking.]*
- **GARRICK:** "[angry] KIT. Off the crate. That's Ix'ali's helmet, and that is not a toy."
- **KIT:** "[sad] I'm practising. For being a hunter. Like {name}."
- *[Garrick goes very still. He looks at you, and doesn't say anything at all.]*
- **CHOICE:**
  - **"Hunting is mostly being scared, Kit. Your dad keeps people safe."** (+High Friendship)
    - **KIT:** "...Safe is better than scared?"
    - *(+30 friendship with Garrick)*
  - **"Ask your dad what he thinks."** (+Friendship)
    - **GARRICK:** "[sad] I think I'd like you to want to keep people safe. Not to chase them."
    - **KIT:** "...Can I do both?"
  - **"One day I'll take you hunting, Kit."**
    - **GARRICK:** "[angry] Not on a hunt, you won't. {name}. A word, later."
    - *(-20 friendship with Garrick)*
- **GARRICK:** "Give me the helmet. ...We'll get you one that fits. A security one. Saturdays, you can help me check the seals."
- **KIT:** "[happy] A REAL one? Security chief, then! And a hunter on Sundays."
- **GARRICK:** "[happy] We'll discuss Sundays."

---

## ♥8 Deputy

**Trigger:** The West Terminal's customs hall, Saturday or Sunday 10:00–12:00, after 6. Reward: Kit's deputy badge. *(Claude)*

- *[The customs hall, empty on a weekend. Behind the old customs desk, standing on two crates, is Kit, in a security cap that actually fits.]*
- **KIT:** "Halt! Papers, please. ...It's you. You still have to show papers. Dad says no exceptions."
- *[You hand over a seed receipt. Kit studies it, frowning, and stamps it twice. The stamp says APPROVED, backwards.]*
- **KIT:** "[happy] Junior Security Officer Kit. Dad swore me in. Saturdays I check the seals with him. Every one. Even the boring ones."
- **KIT:** "And a junior officer gets to pick one deputy. [bashful] I picked you. If you want."
- **CHOICE:**
  - **"I'd be honoured, Officer."** (+High Friendship)
    - **KIT:** "[happy] YES. I knew it. I told Pip you'd say that."
  - **"Shouldn't you pick Pip?"** (+Friendship)
    - **KIT:** "[angry] Pip would want to be in charge. ...You can share it with Pip. Sometimes."
  - **"Deputies are for kids, Kit."**
    - **KIT:** "[sad] ...It's not for kids. It's real."
    - *(-20 friendship with Kit)*
- *[+ Kit's deputy badge (set it down at home)]*
- *[A tin star, painted gold, with DEPUTY stamped across it a little crooked. Garrick's stamp, Kit's hammering.]*
- **KIT:** "It's real. Dad says it's real enough, and that's the same thing. [happy] Now you have to come when I call. Deputy."
