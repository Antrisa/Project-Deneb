# Quill: heart events, and his and Maren's weeks (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **Quill and Maren stagger their days off**, two each, so the medbay always has one of them: Quill is off **Mondays and Saturdays**, Maren **Thursdays and Sundays**. Both have lines for their days off and for the days they cover.
- **4** moves to the North Cave past the mine (the script's "upper caverns" are random floors), with Vzz'ket on guard.
- **6** moves to the mine head: Job is the bruised miner.
- **8** is in the library, where he reads every evening.
- **10** is in the little park in the East complex at night, with the plant he names after you (not the Observation Lounge).

**The arc:** Maren's shy apprentice finding his own voice.
- 2: he drops his sample trays and wonders if he's a real medic.
- 4: out in the field, he's brilliant.
- 6: alone with a patient, his hands don't shake, and his name goes on the door.
- 8: the one thing his textbooks can't explain.
- 10: a new species, named after you.

**What's whose:** lines marked *(Zachary)* are his, from "Heart Events: All Romances": all of 2 except the replies to its choice, the setting and line of 4, Maren's and Quill's lines in 6, and both speeches of 8. Everything else is a draft by Claude, for Zachary to change or approve: Vzz'ket and the choice in 4, Job and the treatment in 6, the replies to 8 (accept, decline, friendship ending), and all of 10. Long lines of his are split in two for the dialogue box. Choices give +30 (Friendship) or +60 (High Friendship).

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where he goes |
|---|---|
| Tuesday, Wednesday, Friday (unchanged) | The medbay from 06:00; reading in the promenade's observation bay 15:30; the medbay 16:30; dinner; the library 19:15; home 22:00 |
| Thursday and Sunday (Maren's days off) | The medbay alone from 06:00; dinner; then Maren's evening shift in the medbay 18:15–21:30 |
| Monday and Saturday (days off) | Breakfast 08:00; sketching moss in the North Cave 09:00 (Vzz'ket guards the cavern gate); lunch; the little park in the East complex 14:00 (the garden dome once it's open); dinner; the library 19:15 |

## Maren's week

| Day | Where she goes |
|---|---|
| Monday, Tuesday, Wednesday, Friday, Saturday (unchanged) | The medbay from 06:30; dinner; the medbay again 19:15; home 21:30 |
| Thursday (day off) | Breakfast 08:30; the library with Owen 10:00; a cup of tea in the common room 12:30; the fountain bench 15:00; dinner; home early |
| Sunday (day off, family day) | Breakfast; the library with Owen 10:00; the little park 13:00 (the garden dome once it's open); dinner; home |

**What they say on those days** (`scripts/npc_data.gd`, `DAY_LINES`): Quill on his days off is "going to look at moss. On purpose. For hours."; on Maren's he's in charge ("Please do not get injured. I mean that kindly."). Maren on her days off: "If you're bleeding, go to him. If you're dying, come and find me."; on Quill's she does the inventory herself, and "The bandages are not alphabetical any more." The station calendar lists both.

**Flags this arc sets:** the perks `perk_xeno_salve` (4) and `perk_guardian_medic` (8), `quill_clinic_door` (6), the keepsake `keepsake_stethoscope_compass` (10), and `partner` = Quill if you accept at 8.

## In the game (23 Nov)

All five are playable cutscenes in `scripts/heart_events.gd`. He poses from his new heart-event sheet (`art/npc_quill_event.png`) and his action sheet; Job poses in 6; Maren and Vzz'ket only walk, turn and get emote bubbles. Not run in Godot yet.

- **To test:** in a debug build, **F3** plays the next event in order (Quill's 2 is the twenty-first press).
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **Not in yet:** the Xeno-Salve recipe (Guardian Medic works since 24 Nov: twelve hearts, and Maren charges nothing when you collapse), Quill's name on the clinic door (`quill_clinic_door` is set for when there's a sign), the glowing plant in the park (narrated), and the charm as an item you can hold.
- 2 plays only on Maren's days off, when Quill has the medbay alone (so she isn't standing there while he worries about her tiles).

---

## ♥2 The Spilled Apothecary

**Trigger:** enter the medbay 11:00–15:00 on Maren's day off (Thursday or Sunday), with Quill at 2 hearts. (Script: 11:00–15:00 in "the East Wing Medbay".)

- *[Quill is on his knees by the lab bench, gathering scattered glass vials. His green-blue cheek blotches have flushed bright teal.]*
- **QUILL** *(Zachary)*: "[shocked] Oh, no, no—don't step there! That's luminescent cavern spore extract!"
- **QUILL** *(Zachary)*: "If it stains Maren's clean tiles, I'll be inventorying gauze pads until Year 405!"
- *[You kneel down and help sort the intact vials back into the rack.]* *(Zachary)*
- **QUILL** *(Zachary)*: "Thank you... Maren's treated soldiers and spacers across three sectors, and I still drop my own sample trays."
- **QUILL** *(Zachary)*: "[sad] Sometimes I wonder if I'm cut out to be a real medic."
- **CHOICE:**
  - **"You're researching cures nobody else on the station understands."** *(Zachary)* (+High Friendship)
    - **QUILL:** "[bashful] ...Nobody understands them because I have not finished explaining them. But thank you."
  - **"Even Maren had to start somewhere. Keep at it."** *(Zachary)* (+Friendship)
    - **QUILL:** "[happy] She says she once splinted the wrong leg. I think she was being kind. I hope she was being kind."
- **QUILL:** "[happy] Please do not tell her about the spores."
- **The next morning** *(Claude, 23 Nov)***:** a letter from Quill, "Do not tell Maren" (`quill_spores` in `scripts/mail_data.gd`), with Medpack x2 in the envelope. The text is in [MAIL.md](../MAIL.md).

---

## ♥4 Field Notes in the Dark

**Trigger:** enter the North Cave 09:00–12:30 on his day off (Monday or Saturday) with Quill at 4 hearts, after The Spilled Apothecary.

- *[Glowing blue moss covers the rocks. Quill is sketching it in a leather notebook while Vzz'ket stands guard nearby.]*
- **VZZ'KET:** "The medic has drawn the same rock eleven times. I am guarding a very patient rock."
- **QUILL** *(Zachary)*: "[happy] Look at the cellular regeneration on this cavern lichen!"
- **QUILL** *(Zachary)*: "Mixed with Merrow's hydroponic aloe, it heals burn trauma twice as fast as standard Terran medpacks—"
- **QUILL** *(Zachary)*: "and works safely on Zaa'sh, Arachnay, and humans alike!"
- **CHOICE:**
  - **"Can I help you collect some?"** (+High Friendship)
    - *[You scrape lichen into sample jars while he labels each one in tiny handwriting.]*
    - **QUILL:** "[happy] You have steady hands. That is the highest compliment I know."
  - **"Is it safe down here?"** (+Friendship)
    - **VZZ'KET:** "It is safe because I am here."
    - **QUILL:** "He says that about everywhere. It is very reassuring."
- **QUILL:** "I will call it Xeno-Salve. Doctor Maren will say the name is too plain. She will be right. I will keep it anyway."
- **New recipe: Xeno-Salve (restores full health and cures debuffs)**

---

## ♥6 Doctor's Orders

**Trigger:** enter the mine 13:30–15:30, Tuesday to Friday, with Quill at 6 hearts, after Field Notes in the Dark. (Script: the medbay in the afternoon; moved to the mine head, 23 Nov.)

- *[At the mine head, Job sits on a bench with a bruised, swelling arm. Quill kneels beside him with a jar of green salve.]*
- **JOB:** "[sad] Rock found my arm 'fore I found the rock. Doc's off seein' to a freighter crew, so I got the young'un."
- **QUILL:** "Please hold still. This will be cold, then warm, then you will forget it was there."
- *[He works quickly and calmly: salve, splint, a neat bandage. His hands are perfectly still. He doesn't drop a thing.]*
- **JOB:** "[surprised] Well, I'll be. Can't feel a thing, cher."
- **MAREN** *(Zachary)*: "[happy] Well done, Quill. Steady hands, sharp diagnosis. I think it's high time we put your name on the clinic door beside mine."
- **QUILL** *(Zachary)*: "[happy] I... I didn't even drop a single vial."
- **CHOICE:**
  - **"You were amazing, Quill."** (+High Friendship)
    - **QUILL:** "[bashful] I was terrified. Apparently it does not show. That is useful to know."
  - **"Told you you'd get there."** (+High Friendship)
    - **QUILL:** "[happy] You did. I have written it down. I write down everything that turns out to be true."

---

## ♥8 Heartbeat (confession)

**Trigger:** enter the library 19:15–22:00 on an evening he isn't covering the clinic (not Thursday or Sunday), with Quill at 8 hearts.

- *[Quiet evening light in the library. Quill is sitting beside the potted luminescent ferns with a book he isn't reading.]*
- **QUILL:** "[surprised] Oh! You came. I was... reading. The same page. For about an hour."
- **QUILL** *(Zachary)*: "I've spent years studying biology—how hearts beat, how cells mend, how different species adapt to new worlds."
- **QUILL** *(Zachary)*: "Yet every time you walk into the Medbay, my own pulse forgets every textbook rule I've ever memorized."
- **If you are dating someone else (the friendship ending):**
  - **QUILL:** "[bashful] ...That was a very unscientific way to say you are my dearest friend. I am keeping the sentence anyway."
  - *[He gives you a bookmark: a pressed fern that still glows faintly.]*
- **Otherwise:**
  - *[Blushing deeply, he offers you a bookmark: a pressed fern that still glows faintly.]*
  - **QUILL** *(Zachary)*: "[love] You helped me believe in myself. Would you... let me care for you, not just as your medic, but as someone who loves you?"
  - **CHOICE:**
    - **"Yes, Quill. I'd like that."**
      - *(Quill is now your partner.)*
      - **QUILL:** "[surprised] You... yes? My pulse is doing something extremely irregular."
      - **QUILL:** "[happy] It is fine. It is wonderful."
      - *[Neither of you reads another word. The ferns glow on until the library lights go down.]*
    - **"You mean a lot to me, as a friend."**
      - **QUILL:** "[sad] Of course. Thank you for telling me honestly. Honesty is good medicine."
      - **QUILL:** "[happy] Keep the bookmark. Ferns do not take things back."
- **QUILL:** "[happy] And please stop collapsing in the mine. From now on I am keeping a closer eye on you. Medically."
- **Perk: Guardian Medic (two more hearts of health, and collapsing costs no Scrip)** (24 Nov: health is ten hearts, so "+20" became two hearts)

---

## ♥10 Constellation Study

**Trigger:** walk into the East complex 20:00–24:00 while you're dating Quill, with him at 10 hearts. It plays in the little park.

- *[The little park at night. The ring lights are dimmed, and the dome overhead is full of stars. In a fresh bed of soil, something small is glowing.]*
- **QUILL:** "[happy] You came. Good. Come and look. Carefully. It is shy."
- *[A small plant with silver leaves, each one pricked with tiny points of light, like a map of the sky.]*
- **QUILL:** "I charted it in the North Cave. A new species. Nobody in three sectors has catalogued it, so I get to name it."
- **QUILL:** "[bashful] The convention is Latin. I have decided the convention is wrong."
- *[The little tag beside it, in Quill's tiny handwriting, says your name.]*
- **QUILL:** "[love] It glows brightest when someone it knows is near. I tested that. Many times. It is very reliable."
- **QUILL:** "Look up. If you match its leaves to the stars, they line up. I did not plan that. I am choosing to believe it anyway."
- **QUILL:** "[bashful] And this. I engraved it myself, badly. A stethoscope on one side, a compass on the other."
- **QUILL:** "So you can always find your way back to a heartbeat."
- *[A small brass charm, still warm from his pocket.]*
- **Keepsake: Quill's stethoscope-compass charm**
