# Freya: heart events and her week (22 Nov 2026)

**Decided with Zachary, 22 Nov:**
- Her father, **Jorvik**, was the station's shipwright. He died testing an earlier version of the FTL stabilizer.
- The Shipwright's Suite has been locked since he died.
- Her 2 is in Engineering.
- She joins your crew after Test Flight (6).
- Her events move off the job: 4 at her home, 6 out past the launch doors, 8 in the Star dome.
- She has weekends off, and her week changes as new places open.

**The arc:**
- 2: she keeps the station running in his shadow.
- 4: she opens his toolbox and finds out why he died.
- 6: she flies his design and learns he was right.
- 8: she says she doesn't have to be him.
- 10: she opens the Suite he left, with both their names over the door.

**What's whose:** lines marked *(Zachary)* are his, unchanged except where long lines are split in two for the dialogue box. Everything else is a draft by Claude, for Zachary to change or approve. Each line starts with a portrait tag the game already reads (`[happy] [sad] [surprised] [love] [angry] [shocked] [bashful]`). Lines stay under about 150 characters. Choices give +30 (Friendship) or +60 (High Friendship), as in the NPC Master.

---

## Her week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where she goes |
|---|---|
| Monday to Friday (unchanged) | Shuttle Bay from 06:00, lunch at the mess, Engineering at 16:30, dinner, Rusk's bar at 19:15, home at 21:30, bed at 22:30 |
| Saturday | A lie-in; her bench at home 08:30; Bram's shop 11:00; lunch; the plaza fountain 14:00; dinner; Rusk's bar 19:15 until 23:00 |
| Sunday | Breakfast at the mess 09:00; the Star dome bench 10:45 (Jorvik watched launches from it); the fountain 13:30; her bench at home 15:30; dinner; home 19:30; bed 22:00 |
| Saturday, once the garden dome is open | The same, but the afternoon is in the dome's meadow instead of at the fountain |
| Sunday, once the garden dome is open | The same morning, then the hot springs from 13:00 until dinner |

Her home is a long walk from everything: about 45 minutes to the mess hall, and 90 from the Star dome to the hot springs.

**Flags this arc sets:** `freya_plans` (4), `freya_parts` (the parts request, Claude), `freya_crew` (6).

---

## ♥2 The Stubborn Heating Pump

**Trigger:** enter Engineering between 16:30 and 17:30 with Freya at 2 hearts. It was 10:00–15:00, but she's only in Engineering at 16:30.

**Setting** *(Zachary)***:** an Engineering alcove. Freya is knee-deep in open floor panels, grease on her freckles, wrestling with a hissing thermal valve.

- **FREYA** *(Zachary)*: "[angry] Come on, you rusty piece of Terran scrap—turn! (Clang!) Ow—my knuckles!"
- *[She spots you and wipes her forehead, leaving another streak of grease.]*
- **FREYA** *(Zachary)*: "[surprised] Oh, hey! Don't mind me—just losing a wrestling match with Sector Three's heating pump."
- **FREYA** *(Zachary)*: "My dad could tune these things by ear in five minutes flat."
- **FREYA** *(Zachary)*: "[sad] Ever since he passed, I feel like I'm just holding the station together with duct tape and stubbornness."
- **CHOICE** *(Zachary)*:
  - **"Let me hold the brace while you torque it."** (+High Friendship)
    - *[You lean on the brace. She hauls on the wrench. The valve gives with a clunk, and warm air sighs through the vents.]*
    - **FREYA:** "[happy] Ha! Two people, one wrench. Dad always said a stuck valve is a two-person job pretending to be a one-person job."
  - **"You're keeping the whole station warm—your dad would be proud."** (+Friendship)
    - **FREYA:** "[bashful] ...Yeah? He'd say I'm holding the wrench wrong."
    - *[She shifts her grip. The valve gives with a clunk, and warm air sighs through the vents.]*
    - **FREYA:** "[surprised] Huh. I was holding the wrench wrong."
- **FREYA:** "[happy] Thanks. Come find me in the bay sometime. I'll show you what real Terran scrap looks like."

---

## ♥4 Dad's Workbench (was "Blueprints in the Attic")

**Trigger:** enter Freya's home (East Home 4) while she's at her bench (Saturday 08:30–11:00, or Sunday afternoon) with Freya at 4 hearts. It doesn't need the Suite, so it needs no backup place.

**Setting:** her bench. On it sits a dented, scorched toolbox with dusty latches. Freya is sitting in front of it, not working.

- **FREYA:** "[surprised] Oh! Hey. Door was open? Sorry, I'm not really working."
- **FREYA:** "[sad] This was my dad's. Jorvik. He was the station's shipwright, before me. Before the Suite got locked up."
- **FREYA:** "[sad] He was testing a new FTL stabilizer. Two minutes past the launch doors, it shook itself apart. We never got him back."
- **FREYA:** "Tikka sealed the Suite after. I brought his toolbox home. I've never opened it."
- *[She runs a thumb along a latch.]*
- **FREYA:** "[bashful] Would you stay while I do?"
- *[The latches snap. Inside, wrapped in an oilcloth: a roll of blueprints, every margin crowded with his handwriting.]*
- **FREYA:** "[shocked] These are the stabilizer plans. His last version. Look at the notes: 'Mount's too stiff. It has to give. Next one floats.'"
- **FREYA:** "And here, underlined twice: 'If it sings, don't fight it. Ease off. Let it find its note.'"
- **FREYA:** "[sad] He knew what was wrong. He was going to fix it after one more run. He always said that. 'One more run, then I'll fix it.'"
- **CHOICE:**
  - **"Then let's fix it. Together."** (+High Friendship)
    - **FREYA:** "[surprised] Just like that?"
    - **FREYA:** "[happy] ...Yeah. Just like that. Okay."
  - **"You don't have to finish his work, you know."** (+High Friendship)
    - **FREYA:** "[sad] I know. Nobody's ever actually said that to me."
    - **FREYA:** "[happy] That's kind of why I want to. Because now it's my choice."
- **FREYA:** "[happy] I'll need titanium for a floating mount, and a couple of good cells. Bring me what you can, and I'll do the rest."

**Sets:** `freya_plans`.

**Parts request (Claude):** bring Freya 3 Titanium Ingots and 2 Lithium Cells (both are on her loves list). That sets `freya_parts`. Test Flight waits for it, which the hard-lock rule allows because the stabilizer is what 6 is about.

---

## ♥6 Test Flight

**Trigger:** enter the Shuttle Bay at dusk (18:00–20:00) with Freya at 6 hearts, once your ship has flown and `freya_parts` is set.

**Setting:** your ship on the clamps, a new housing bolted under the drive. Freya is in a flight suit with her helmet under her arm. Tikka is in launch control.

- **FREYA:** "[happy] Stabilizer's in. Floating mount, just like his note said. Short burn past the launch doors, three minutes at full, then home."
- **FREYA:** "[bashful] I'm riding along, in the duct behind your seat. Don't argue. I already measured it."
- **TIKKA (comms):** "Launch control here. Same booth. Same chair."
- **TIKKA (comms):** "[sad] I was in this chair for his last run, Freya. I'd like a better memory of it."
- **FREYA:** "Then let's give you one."
- *[The launch doors open on the dark. The drive lights. For a minute the hum is clean.]*
- **SENSORS:** "Drive harmonic rising. Six tenths. Seven tenths."
- *[The cockpit starts to shake. Loose bolts rattle in the duct.]*
- **FREYA:** "[shocked] That's it. That's the sound."
- **TIKKA (comms):** "[shocked] Freya? Freya, talk to me."
- **FREYA:** "'If it sings, don't fight it.' Ease off. Two-thirds. Let it find its note."
- **CHOICE:**
  - **[Ease off to two-thirds]** (+High Friendship)
  - **[Hold full power]** (no friendship)
    - *[The shaking gets worse. Something cracks in the duct.]*
    - **FREYA:** "[angry] Ease off! Please!"
    - *[You pull back to two-thirds.]*
- *[The shaking fades. The hum drops, steadies, and settles into one clean sapphire note.]*
- **FREYA** *(Zachary)*: "[happy] Did you hear that purr?! Not a single harmonic wobble! Dad's design works—and it's flying on your ship!"
- **TIKKA (comms):** "[happy] He'd have whooped so loud they'd hear it in the mine."
- *[Fade. The bay, later. Freya sits on a docking clamp with her helmet in her lap.]*
- **FREYA:** "I spent years in that booth listening to ships leave. I don't want to listen anymore."
- **FREYA:** "[bashful] Take me with you? On your runs. I can fix anything you break. Mostly."
- **CHOICE** (both take her on):
  - **"Welcome aboard."**
  - **"Best mechanic in the Neutral Zone? Obviously."**
- **FREYA:** "[happy] Then I'm crew. I'll get my kit. And a cushion for that duct."

**Unlocks:** the Pioneer Stabilizer (lower fuel cost on runs), and Freya joins your crew (`freya_crew`). Until you have a ship with a second seat, she rides in the duct, the way Ana came home.

---

## ♥8 Under the Star Dome (confession; was "Stargazing on the Hull")

**Trigger:** enter the Star dome after 20:00 with Freya at 8 hearts. Perk either way: **Master Mechanic** (20% off ship and tool upgrades).

**Setting:** the Star dome at night. Freya sits on the bench under the telescope, her boots up on the rail.

- **FREYA:** "[happy] Found me. I come here Sunday mornings. Dad used to watch the launches from this bench."
- **FREYA** *(Zachary)*: "For years I thought restoring this docking bay meant trying to become my dad."
- **FREYA** *(Zachary)*: "Working alongside you made me realize I don't have to be a copy of him—I get to build my own future here."
- **FREYA** *(Zachary's line, changed now that she flies with you)*: "[bashful] And honestly? When we're out there together, I forget to be scared. When you fly without me, I count the minutes till you dock."
- **FREYA** *(Zachary)*: "[love] I like you—more than just as my favorite test pilot."
- **CHOICE:**
  - **Accept**
    - **FREYA:** "[surprised] Wait. Really? You're not just being nice?"
    - **FREYA:** "[love] Okay. Okay! Um. I don't know what you do now. Sit with me a while?"
    - *[You sit with her on the bench and watch the stars wheel past the glass until the lamps dim.]*
  - **Stay friends**
    - **FREYA:** "[sad] Yeah. Okay. I had to say it, or I'd be asking 'what if' forever."
    - **FREYA:** "[happy] You're still my favorite test pilot. That doesn't change."
- **FREYA:** "[happy] Oh, and from now on, anything you want upgraded, you bring it to me. Family rate."

**Friendship ending** (you're dating someone else): the same setting and the first three lines. Then, instead of the confession and the choice:
- **FREYA:** "[happy] You're the best friend I've made on this station. Thought you should know."
- **FREYA:** "[happy] Oh, and from now on, anything you want upgraded, you bring it to me. Family rate."

---

## ♥10 Christening the Suite (partners)

**Trigger:** enter the Shuttle Bay with Freya at 10 hearts while you're dating her. If the Forgemaster has restored the Shipwright's Suite, the scene goes inside. If not, it stays outside the Suite's sealed door.

**Setting:** Tikka, Sesska and Ana (if she has arrived) wait by the Suite's door. A canvas sheet hangs over something above it.

- **TIKKA:** "[happy] There she is. And her favorite test pilot."
- **TIKKA:** "[sad] This door's been shut since Jorvik's last run. I kept the code. Never had the heart to use it."
- **TIKKA:** "[happy] It's yours, Freya. Should've been yours a long time ago."
- *If the Suite is restored: [The door slides open on clean benches, new lights and his old hull blueprints, framed.]*
- *If not: [The door grinds open on dust and dark.]*
  - **FREYA:** "[happy] Okay. It needs work. We'll fix the rest together."
- **SESSKA:** "[happy] Pull the sheet, dear. All four of my arms are tired of holding it up."
- *[The sheet falls: a brass sign reading ECHO LANDING SHIPWRIGHTS. Under it, smaller: JORVIK & FREYA.]*
- **ANA** (if she has arrived): "[happy] Fancy. Do I get a desk?"
  - **FREYA:** "[happy] You get a stool. Earn the desk."
- **FREYA:** "[love] I made you something. From Dad's old wrench. The one he gave me when I was six."
- *[A tiny wrench on a chain, polished bright.]*
- **FREYA:** "[love] He built ships so people could come home. I think I finally get it. You're what I come home to."

**Keepsake:** the wrench pendant.

---

## Still open

- How long ago Jorvik died. The scenes avoid a number.
- Whether the parts request before 6 stays.
- Lines for Freya when you come home badly damaged (not an event). They'd play when she repairs your hull after a loss.
- An event sheet for her (the status doc already lists event sheets as art still to draw).
