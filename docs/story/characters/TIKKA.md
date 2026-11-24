# Tikka: heart events and her week (24 Nov 2026)

**Decided with Zachary, 24 Nov:**
- **Everyone gets their own arc**: this one is Tikka's own. She and Sesska also share a two-scene side arc, "Forty Years" ([TIKKA_SESSKA.md](TIKKA_SESSKA.md)).
- **Why she overworks:** she has listened to the station for forty years, and quiet sounds wrong to her. Jorvik is "slightly linked but not the main reason" (Zachary): he came in on Sundays too, and after him there was only her.
- **Her week:** **Sundays off** with Sesska. Until her 8 she slips into Engineering on Sunday mornings "to look at the core". **Saturdays** she covers launch control in the Shuttle Bay while Freya's off.
- **Her 8's reward:** the NPC Master's **Smelter Overclock**: every furnace smelts in half the time.
- **Four hands:** her first line now says "Four hands, no waiting" (it said "Eight hands", but the Arachnay have four arms; Sesska's "eight hands" are the two of them together). Forty years married stays.

**The arc:** the engineer who can't put the station down.
- 2: the core at night: a flat note only she can hear, and a dinner going cold at home.
- 4: the repair bench: she does everyone's repairs every evening, and won't let Freya take one.
- 6: Sunday in the Shuttle Bay: Freya has learned the habit from her.
- 8: a real day off, with one four-minute visit on the way.

**What's whose:** the title of 2 ("Tuning the Manifold") and the reward are the NPC Master's; the week and the answers above are Zachary's; the scenes and every line are drafts by Claude. Right answers give +60 (High Friendship). Wrong ones cost a little: in 2 a late night (−15 energy), in 4 Freya's feelings (−20 with Freya, nothing for Tikka, who'd agree with you), in 6 −20, and in 8 Sesska's patience (−20 with Sesska).

**Flags this arc sets:** `tikka_manifold` (2), `tikka_freya_helps` (4, the right answer), `tikka_day_off` (6, the right answer), `tikka_sundays_off` and the perk `perk_smelter_overclock` (8).

---

## Her week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What she does |
|---|---|
| Monday to Friday (unchanged) | Engineering from 06:00; dinner; the public repair bench by the Manufacturing hub from 19:15; home at 21:30. |
| **Saturday** (Freya's off) | Launch control in the Shuttle Bay from 07:00 (the lower console, so the launch console stays free for you); dinner; the repair bench; home. |
| **Sunday (off), before her 8** | Breakfast with Sesska; Engineering's core room "just to look" (10:30, not working, so her shop is shut); lunch; the fountain with Sesska; dinner; home early. |
| **Sunday (off), after her 8** | Breakfast, the fountain, lunch, the Observation Lounge with Sesska (the garden dome once it's open), dinner, home. |

- **Day lines** (`npc_data.gd DAY_LINES`): Saturday's launch duty, and Sunday's, which change at her 8 (a day line can now have `"else"` lines for before its flag, `main.gd _day_line`). The board calendar lists her Sundays off.
- A new pseudo-area for weekly spots, `"promenade"` (main level, today's coordinates), puts her Saturday evenings at the repair bench outside the old square.

---

## In the game (24 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`tikka_2` to `tikka_8`), staged like the other arcs: poses from her new heart-event sheet (`art/npc_tikka_event.png`, from `tools/events.py`; her rig side in `art/rig` is her own left-facing walk frame, all eight limbs kept) and her action sheet (console, tinker, rest), emote bubbles and sounds (the valve, the comm, the welder). Not run in Godot yet.

- **Smelter Overclock** (her 8): `main.gd _furnace_use` halves the cooking time with `perk_smelter_overclock`, and the toast shows the shorter time.
- **Letter:** the morning after 4, if you let Freya take Owen's lamp: "She let me", from Freya.
- **To test:** in a debug build, **F3** plays the next event in order (it sets the hearts, day and time).
- **Checked offline:** `python3 tests/check_heart_events.py`, `python3 tests/check_mail.py`.

---

## ♥2 Tuning the Manifold

**Trigger:** Engineering's geothermal core, 21:45–23:30, any night (she should be home by now). *(Claude)*

- *[Engineering, late. The geothermal core hums in its cage of light. Tikka is alone at a control panel, humming back at it.]*
- **TIKKA:** "Mmm-mm. Mm-mmm. No. Mmmm..."
- **TIKKA:** "[surprised] Pilot! It's late. Why are you here? ...Why am I here? Don't answer that."
- **TIKKA:** "Listen. Under the hum. Hear it? One flat note. A valve on the manifold is a hair out, and the whole station is singing a quarter-tone flat."
- **TIKKA:** "S.A.R.A. says the readings are fine. The readings are fine. The note is not."
- **TIKKA:** "My ears are busy. Go to the coolant tank by the west wall. Third wheel from the top. When I say turn, turn. Slowly."
- **TIKKA:** "Turn."
- **TIKKA:** "[angry] Too far! Back. Half of that. Half of half."
- *[The hum smooths out, like a held breath let go. You never heard the flat note. Now that it's gone, you can hear that it was there.]*
- **TIKKA:** "[happy] There. Forty years I've listened to this station. When it's right, I can't hear it at all. That's the best sound there is."
- **TIKKA:** "When it's wrong, I hear it from my bed. Sesska says I married the core first. I didn't. I met it a week before I met her."
- **SESSKA** *(comm)*: "Tikka. It is late. Your dinner has become a sculpture."
- **TIKKA:** "[sad] Coming, love. ...One more valve. Then home."
- **CHOICE:**
  - **"Go home, Tikka. The valve will still be here tomorrow."** (+High Friendship)
    - **TIKKA:** "[surprised] It will. It's a valve. They're very patient."
    - **TIKKA:** "[happy] Coming, love. Tell the sculpture I'm sorry."
  - **"One more valve, then. I'll help."**
    - **TIKKA:** "[happy] Good! Third wheel again. No, the other third wheel."
    - *[One more valve becomes four. By the time Tikka lets go of the manifold, your arms ache.]*
    - **TIKKA:** "[sad] ...Sesska will be very polite to me tomorrow. That is the worst thing she does."
    - *(-15 energy)*

---

## ♥4 The Kettle Queue

**Trigger:** The public repair bench by the Manufacturing hub, 19:30–21:15, Monday to Saturday, after 2. With Saffi, Owen, Pip and Freya. *(Claude)*

- *[The public repair bench by the Manufacturing hub, after dinner. A queue has formed: a kettle, a reading lamp, and a small, sad drone.]*
- **TIKKA:** "Next. Saffi. Kettle. The element's gone again. Two minutes."
- **SAFFI:** "[happy] You did this kettle in spring, Tikka."
- **TIKKA:** "And I'll do it in autumn. Kettles are seasonal."
- **TIKKA:** "Pilot. If you're in the queue, you're behind Pip. Pip's drone is a disaster."
- **PIP:** "[angry] It's not a disaster, it's a prototype!"
- **SAFFI:** "She's here every night after a full shift. Nobody asks her to. Nobody has to."
- **SAFFI:** "[sad] Nobody ever offers to help, either. She wouldn't let them."
- **FREYA:** "[happy] Tikka! I can take one. Owen's lamp? It's only a switch."
- **TIKKA:** "...It's a switch, a wire and a socket, Freya. Three things to go wrong."
- **FREYA:** "[sad] I know what a lamp is."
- **CHOICE:**
  - **"Let her. You taught her, didn't you?"** (+High Friendship)
    - **TIKKA:** "...I did. Mostly by telling her not to hit things."
    - **TIKKA:** "[happy] Fine. Owen's lamp. No hitting."
    - **FREYA:** "[happy] Done! Owen, try it."
    - **OWEN:** "[happy] Brighter than before. I can read the footnotes. I didn't know there were footnotes."
    - **TIKKA:** "Brighter. Hm. I'll check it tomorrow."
    - **FREYA:** "[angry] Tikka!"
    - **TIKKA:** "[happy] ...I won't check it tomorrow."
    - *[With two of them at it, the queue is gone before nine. Even Pip's drone flies, briefly, and lands in the planter. Pip is delighted.]*
  - **"You're faster, Tikka. Just do it yourself."**
    - **TIKKA:** "[happy] I am faster."
    - **FREYA:** "[sad] ...Right. Course you are. Night, Tikka."
    - *[Tikka watches her go, then picks up Owen's lamp. The queue is gone by midnight. Tikka isn't.]*
    - *(-20 friendship with Freya)*

---

## ♥6 Sunday Shift

**Trigger:** The Shuttle Bay, 08:00–12:00 on a Sunday (her day off), after 4. With Freya. *(Claude)*

- *[The Shuttle Bay on a Sunday morning. It should be empty. It isn't: someone is hammering at Freya's bench.]*
- **TIKKA:** "[surprised] Freya. It's Sunday. What are you doing here?"
- **FREYA:** "[surprised] What are you doing here?"
- **TIKKA:** "...Checking the fuel lines."
- **FREYA:** "On a Sunday."
- **TIKKA:** "They're fuel lines on Sundays too."
- **FREYA:** "[happy] You come in every Sunday. Everybody knows. I figured that's just what engineers do. So I've been coming in too."
- **FREYA:** "Third Sunday running! I didn't tell you. I wanted it to be a surprise."
- *[Freya yawns, enormously, behind a hand black with grease.]*
- **TIKKA:** "[sad] ...A surprise. Yes."
- **FREYA:** "[happy] Coffee! I'll get coffee. Don't touch my bench, either of you."
- **TIKKA:** "Jorvik came in on Sundays too. I used to tell him off for it. Then he was gone, and it was only me, and I came in on Sundays."
- **TIKKA:** "It isn't for him. Don't think that. It's the station. When it's busy, I can hear it's fine. When it's quiet, I hear everything that might go wrong."
- **TIKKA:** "[sad] I've been teaching that girl since she could hold a spanner. And the thing she learned best is this."
- **CHOICE:**
  - **"Then teach her the other thing. Take today off, both of you."** (+High Friendship)
    - **TIKKA:** "...The other thing. I don't know the other thing."
    - **TIKKA:** "[happy] Sesska knows it. She's been trying to teach me for forty years. I'm a slow student."
    - **TIKKA:** "Freya. Go home. Rest. That's an order from your chief engineer."
    - **TIKKA:** "...I'm going home too. Probably. Look: I'm going."
    - **FREYA:** "[surprised] You're going home? On purpose? [happy] I'm telling Sesska."
  - **"She's young. She'll manage."**
    - **TIKKA:** "[sad] That's what they said about me."
    - *[Freya comes back with two coffees. Tikka takes hers to the fuel lines, and doesn't come back.]*
    - *(-20 friendship with Tikka)*

---

## ♥8 Overclock

**Trigger:** Your front door in the Agri complex, 07:00–11:00 on a Sunday, after 6. With Sesska. Reward: Smelter Overclock. *(Claude)*

- *[Your front door, Sunday morning. Tikka is waiting on the porch with a toolbag. A little way off, Sesska is waiting with a picnic basket and a look.]*
- **TIKKA:** "[happy] Pilot! Good morning. This is a visit. I'm visiting."
- **SESSKA:** "It is a visit with a toolbag."
- **TIKKA:** "Visits can have toolbags."
- **TIKKA:** "Freya has the core today. S.A.R.A. is watching Freya, and Sesska is watching me. Everybody is watched. It's very restful."
- **TIKKA:** "But on Thursday I had a thought, and you can't un-have a thought. Furnaces. Everybody's furnaces run cool. Twice as long as they need to."
- **TIKKA:** "Regulators. Coil wire, wound fine. One for every furnace on this moon. I did Engineering's last night."
- **TIKKA:** "Yours take four minutes. Four hands, four minutes."
- *[She's back in four minutes exactly, wiping her hands on a rag.]*
- *[Perk: Smelter Overclock (every furnace smelts in half the time)]*
- **SESSKA:** "Four minutes. I timed it. Tikka. Picnic."
- **CHOICE:**
  - **"Go on. Have your day off."** (+High Friendship)
    - **TIKKA:** "[happy] Going. Look. This is me, going."
    - **SESSKA:** "[happy] Forty years, and she's learning the other thing. I'm going to frame this morning."
  - **"While you're here, could you look at my hoe?"**
    - **TIKKA:** "[happy] I could!"
    - **SESSKA:** "[angry] She could not. Pilot."
    - **TIKKA:** "[sad] ...I could not. Sorry. It's Sunday."
    - *(-20 friendship with Sesska)*
