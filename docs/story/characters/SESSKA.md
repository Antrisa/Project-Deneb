# Sesska: heart events and her week (24 Nov 2026)

**Decided with Zachary, 24 Nov:**
- **Everyone gets their own arc**: this one is Sesska's own. She and Tikka also share a two-scene side arc, "Forty Years" ([TIKKA_SESSKA.md](TIKKA_SESSKA.md)).
- **Her week:** **Sundays off** with Tikka. **Wednesday afternoons** she buys fibre from Evarra; **Thursday afternoons**, once the hotel is open, she takes it linens.
- **Her 8's reward:** the NPC Master's **Void-Silk Luxury Linens**, a boost for the hotel. Zachary: "nothing until the hotel is made", so the perk is recorded and does nothing until the hotel takes paying guests.
- **Her 6** unlocks the **Cavern-silk coat** in her shop (it was hidden until something unlocked it).

**The arc:** a weaver who lost her street, and finds a new one.
- 2: she finally mends your crash jacket (her first line promised to), and talks of her shop window on Arach Minor.
- 4: the Landing has no pattern of its own, so she starts one, out on the promenade.
- 6: glow-spider silk in the North Cave: the Landing's own thread.
- 8: she cuts her grandmother's void-silk, forty years in a drawer, and weaves the old street and the new one together.

**What's whose:** the reward is the NPC Master's; the week and the answers above are Zachary's; her first lines (the jacket, the window onto a corridor, forty years married) are the game's; the scenes and every line are drafts by Claude. Right answers give +60 (High Friendship), the middle ones +30. Wrong ones cost −20, and in 2 the letter.

**A small change from my outline:** 4 was going to be her moving her loom into the window so people stop to watch, but her loom is already out on the promenade in the game, so 4 is about the pattern instead.

**Flags this arc sets:** `sesska_jacket` (2), `sesska_landing_pattern` (4), `sesska_cavern_silk` (6: her shop's Cavern-silk coat, `shops.gd` rule `"sesska_silk"`), `sesska_void_silk` and the perk `perk_void_silk_linens` (8).

---

## Her week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What she does |
|---|---|
| Monday, Tuesday, Friday, Saturday (unchanged) | Her loom on the promenade outside the shop from 06:00; dinner; the fabrication shop in the evening; home at 21:30. |
| **Wednesday** | The shop until 14:00; Evarra's greenhouse for fibre (14:00–16:00); the shop again; dinner; the fabrication shop; home. |
| **Thursday** (once the hotel is open) | The shop until 14:00; linens to the hotel (14:00–16:00); the shop again; the evening as usual. |
| **Sunday (off), before Tikka's 8** | Breakfast with Tikka; her loom at home (Tikka has gone "to look at the core"); lunch; waiting for Tikka at the fountain; dinner; home. |
| **Sunday (off), after Tikka's 8** | Breakfast, the fountain, lunch and the Observation Lounge with Tikka (the garden dome once it's open), dinner, home. |

- **Day lines** (`npc_data.gd DAY_LINES`) for Sunday, Wednesday and, once the hotel is open, Thursday. The board calendar lists her Sundays off. Her shop is shut while she's away from her loom.

---

## In the game (24 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`sesska_2` to `sesska_8`), staged like the other arcs: poses from her new heart-event sheet (`art/npc_sesska_event.png`, from `tools/events.py`; her rig side in `art/rig` is her own left-facing walk frame) and her action sheet (weave, chat, rest), emote bubbles and sounds. The glow-spiders in 6 are the code-drawn fireflies (`scripts/scene_fx.gd`) until there's art. Not run in Godot yet.

- **Letter:** the morning after 2, "Offcuts", with a knit cap made from your jacket's offcuts (not if you told her it was only a jacket).
- **To test:** in a debug build, **F3** plays the next event in order.
- **Checked offline:** `python3 tests/check_heart_events.py`, `python3 tests/check_mail.py`.

---

## ♥2 Every Seam Giving Up

**Trigger:** Her shop, 08:00–12:00, Monday to Saturday. *(Claude)*

- *[Sesska's shop. Bolts of cloth climb every wall, in every colour the moon allows, which is mostly grey, and three colours it doesn't.]*
- **SESSKA:** "[happy] There you are. You, and that jacket. Come here, come here. Off with it."
- **SESSKA:** "Every seam giving up. I said so the day you landed. I've been waiting until I had cloth to spare. This morning, I have cloth to spare."
- *[She takes your jacket in all four hands at once: two to hold it up, and two to read it.]*
- **SESSKA:** "A scorch here, all down the back: you came in too hot. A tear here: you climbed out of something sharp."
- **SESSKA:** "[surprised] And this cuff has been chewed. Something in the mine?"
- **SESSKA:** "[happy] A jacket is a diary that doesn't know it's being read."
- **SESSKA:** "[sad] On Arach Minor my shop had a window onto the street. People walked past with their whole lives on their sleeves, and I mended them."
- **SESSKA:** "So. The scorch. I can weave over it, and the jacket looks new. Or I can mend around it, and it stays yours."
- **CHOICE:**
  - **"Keep the scorch. It's how I got here."** (+High Friendship)
    - **SESSKA:** "[happy] Good answer. The best mends show."
  - **"Make it look new."** (+Friendship)
    - **SESSKA:** "As you like. New is also a story. A shorter one."
  - **"It's only a jacket. Patch it however."**
    - **SESSKA:** "[sad] Only a jacket. Hm. Come back at noon."
    - *(-20 friendship with Sesska)*
- *[A quarter of an hour later the jacket comes back across the counter. The seams hold. They look like they mean it.]*
- *[The next morning: a letter (`sesska_offcuts`, in [MAIL.md](../MAIL.md))]*

---

## ♥4 A Window onto a Corridor

**Trigger:** Her loom on the promenade outside the shop, 13:00–17:00, Monday to Saturday, after 2. With Pip and Kit. *(Claude)*

- *[The promenade outside Sesska's shop. Her big loom stands out in the corridor by her shop window, and she's weaving in the middle of everybody's way.]*
- **SESSKA:** "[happy] Pilot. You're in my light. Stay, stay. The light out here is terrible anyway."
- **SESSKA:** "A window onto a corridor. I've decided: if the street won't come to the window, the loom goes out to the street."
- **SESSKA:** "And now that I'm out here, a problem. Every Arachnay town has its own pattern. Arach Minor's is the river and its seven bridges."
- **SESSKA:** "[sad] This station has stood longer than I've lived on it, and it has no pattern of its own. Everybody here wears somewhere else."
- **PIP:** "Is it a flag? Are you making a flag?"
- **SESSKA:** "Better. A flag is only for waving. This, you can wear."
- **KIT:** "Put a bug on it! A really big one!"
- **SESSKA:** "[happy] Vzz'ket would approve. Everybody else would sit somewhere else at dinner."
- **SESSKA:** "Pilot. What does the Landing look like, to you? One thing. I'll weave it in."
- **CHOICE:**
  - **"The ring of the station, with the moon underneath."** (+High Friendship)
    - **SESSKA:** "[happy] Ring and moon. Plain, and true. That's the warp, then: everything else hangs on it."
  - **"Everyone at dinner. All kinds of people at one table."** (+High Friendship)
    - **SESSKA:** "...Every kind of thread in one weave. That will be very hard to do. [happy] Good."
  - **"Something from Arach Minor. You must miss it."**
    - **SESSKA:** "[sad] I miss it every day. That's why this one has to be new."
- *[By the time the corridor lights dim, a hand's width of new cloth hangs from the loom: grey and gold, with one thread of blue.]*
- *[People stop to look. Some of them stay to argue about it.]*
- **PIP:** "[happy] It's us!"

---

## ♥6 Glow-Spider Silk

**Trigger:** The North Cave, 19:00–22:00, after 4. With Vzz'ket. Her shop sells the Cavern-silk coat from now on. *(Claude)*

- *[The North Cave, after dark. Tiny blue lights hang from the roof like a second sky. They aren't stars. They have legs.]*
- **VZZ'KET:** "Slowly, pilot. The pale ones bite."
- **SESSKA:** "[happy] Glow-spiders. Look at them. Distant cousins. Very distant. They never write."
- **SESSKA:** "Every night they spin, and every morning the mine bugs walk straight through it. A whole night of silk, and it glows, and it's wasted."
- **VZZ'KET:** "The hunter in me says: burn the nest."
- **SESSKA:** "The weaver in me says: touch my spiders, and I'll knit you a sock with no foot in it."
- **VZZ'KET:** "...The hunter withdraws."
- *[One of the lights drops on a thread, right in front of your face, and hangs there, considering you.]*
- **CHOICE:**
  - **"Hold still and let it look."** (+High Friendship)
    - **SESSKA:** "[happy] Good. It's only curious. So are you."
  - **"Ask it, very politely, for some silk."** (+Friendship)
    - **SESSKA:** "[happy] That's exactly how I'd do it. Manners cost nothing, even with a spider."
  - **"Squash it!"**
    - **SESSKA:** "[angry] Don't you dare!"
    - *[The spider leaves, offended. So, very nearly, does Sesska.]*
    - *(-20 friendship with Sesska)*
- **SESSKA:** "Enough for one coat, tonight. I'll come back every week, and Vzz'ket will glare at the dark for me."
- **SESSKA:** "[happy] The Landing's own thread, for the Landing's own pattern. Come by the shop. I'll have something to show you."
- *[Sesska's shop now sells the Cavern-silk coat]*

---

## ♥8 Void-Silk

**Trigger:** Their home in the East Complex, 21:45–23:30, after 6. Tikka is asleep at her bench. Reward: Void-Silk Luxury Linens (for the hotel, once it takes paying guests). *(Claude)*

- *[Tikka and Sesska's home, late. Tikka has fallen asleep at her bench with a drone in her lap. Through the far doorway, a loom is still going.]*
- **SESSKA:** "[happy] Shh. She'll wake if you say 'coil'."
- **SESSKA:** "You came at the right moment. I'm about to do something foolish, and I'd like a witness."
- *[From under the bolts of bug silk she draws a long, flat parcel, in paper gone soft with age.]*
- **SESSKA:** "Void-silk. Spun in the dark between stations, the old way, by my mother's mother. The last bolt of it that ever left Arach Minor."
- **SESSKA:** "I brought it here forty years ago, and I've been saving it for something worth cutting it for."
- **SESSKA:** "[sad] Forty years in a drawer. That isn't saving. That's only a drawer."
- *[She weaves until the small hours: her grandmother's void-silk, the North Cave's glowing thread, and the Landing's new pattern running through both.]*
- **SESSKA:** "[happy] Old street, new street. Linens. For the hotel, when it has guests worth spoiling: they'll sleep like stones and pay like princes."
- **SESSKA:** "And the first pillowcase is yours. You'll sleep like a stone too. A happy stone."
- **CHOICE:**
  - **"Your grandmother would be proud."** (+High Friendship)
    - **SESSKA:** "[sad] She'd say the hem is crooked. [happy] ...And then she'd be proud."
  - **"Are you sure? It was the last of it."** (+Friendship)
    - **SESSKA:** "Kept things are only kept. Used things are loved."
  - **"What would void-silk sell for?"**
    - **SESSKA:** "[angry] You can sleep on it, pilot. That's what it's for."
    - *(-20 friendship with Sesska)*
- *[Perk: Void-Silk Luxury Linens (for the hotel's beds, once it takes paying guests)]*
- **TIKKA:** "[surprised] ...Coil?"
- **SESSKA:** "[happy] No, love. Bed."
