# Garrick: heart events and his week (24 Nov 2026)

**Decided with Zachary, 24 Nov:** "every character has own arc plus a short family shared arc": an arc each for Garrick, Saffi and Kit, and a two-scene family side arc ([GARRICK_SAFFI_KIT.md](GARRICK_SAFFI_KIT.md)). Claude's first suggestions for the rest, taken: **Garrick was security officer on the refugee transport that crash-landed here**, and a bounty hunter he let dock brought a Chernobog cutter down on it (so he distrusts your trade); **Kit's beacon** leads to a smuggler's cache on the jump map, and **his 8 is a deputy badge** you set down at home; their weeks: the model ship and the seals on Saturdays, Saffi's Monday lunch with Rusk and the market. **Then (Zachary, 24 Nov):** "garriks 8 heart is too powerful, change to self defense class, attacking boarders take extra damage on your ship" (it was Perimeter Defence: the station's guns softening up the first ship you fought on each run); "saffi increase max energy perk" (it was a Sunday potluck: share a dish for friendship with everyone and a well-fed morning).

**The family's story (Claude's drafts):** about forty refugees, Saffi and Kit (in a sling) among them, came down on this moon in a transport with its drive shot out, and S.A.R.A. talked them in. Every settler signed the scorched hull plate now in the museum; Kit's is a handprint. The first night, Saffi made soup for forty in a dented helmet. Most of the forty moved on later; they stayed.

**The arc:** the security chief who checks every seal himself, and learns to trust a pirate hunter.
- 2: everything sharp gets signed for, yours included. Your log says twelve bounties; he wants to know about the people standing near them.
- 4: his nightly round of the West Terminal's airlocks, and the short version: the transport, the bounty hunter he let dock, and the cutter.
- 6: a safety class for the kids on the plaza; S.A.R.A. doesn't want a parade ground (the NPC Master's tension). You find the middle.
- 8: the self-defence class for grown-ups: a ship's corridors chalked on the hangar floor, Ix'ali as the boarder. You're a resident with a ship, not a hunter.

**What's whose:** his 8's reward is Zachary's (the NPC Master's title for 6, Self-Defence Class, moved to it; 6 is the Safety Class now); his first line ("Pirate hunter. Keep it outside the airlock") was already in the game; the scenes and lines are Claude's drafts. Right answers +60, middle +30, wrong −20.

**Flags:** `garrick_signed` (2), `garrick_rounds` (4), `garrick_class` (6), `garrick_resident` and the perk `perk_self_defence` (8).

## The Self-Defence Class (his 8)

`ship_battle.gd _tick_fights`: with `perk_self_defence` (passed in the fight as `"self_defence"` by `main.gd _my_fight`), your crew deal half again as much damage (`SELF_DEFENCE_X`, 1.5) to boarders fighting them on your own ship. Fights on the enemy's ship, and the boarders' own damage, are unchanged.

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What he does |
|---|---|
| Monday to Friday (unchanged) | The armoury; the plaza at noon; the armoury; dinner; Rusk's bar; home. |
| Saturday and Sunday (unchanged, off) | Home in the morning; the plaza; lunch; the little park or home; dinner; the bar. |
| **Saturday, after Kit's 6** (`kit_security`) | The West Terminal's seals in the morning, with Kit; then as before. |

## In the game (24 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`garrick_2` to `garrick_8`), with his new heart-event sheet (`art/npc_garrick_event.png`, `tools/events.py`) and his action sheet (ledger, patrol). Not run in Godot yet.

- **Letter:** the morning after 4, "Quartermaster's issue", with a medpack.
- **To test:** in a debug build, **F12** plays the next event in order, **Ctrl+F12** all of them in a row.

---

## ♥2 Signed For

**Trigger:** The armoury, 09:00–11:45 or 14:00–17:00, Monday to Friday. *(Claude)*

- *[The armoury. Garrick sits behind the counter with a ledger as big as a door, writing very slowly.]*
- **GARRICK:** "{name}. Good. Saves me a walk. Everything sharp on this station gets signed for. That includes what's on you."
- **GARRICK:** "Laser. Knife. Whatever's in the boot. On the counter."
- *[You set it all on the counter. He writes each one down, then looks at you over the top of the ledger.]*
- **GARRICK:** "Your ship's log says pirate hunter. Bounties on twelve Chernobog."
- **GARRICK:** "[angry] It doesn't say what happened to the people standing near the twelve."
- **CHOICE:**
  - **"Everyone near them walked away. I made sure."** (+High Friendship)
    - **GARRICK:** "...Good answer. Hard to check. But a good answer."
  - **"I don't hunt any more. I farm."** (+Friendship)
    - **GARRICK:** "[happy] Farmer. I'll write that down. In pencil."
  - **"Twelve? It was more than twelve."**
    - **GARRICK:** "[angry] That's not the number I was asking about."
    - *(-20 friendship with Garrick)*
- *[He signs the ledger, turns it round, and taps the line where you sign under him.]*
- **GARRICK:** "There. You're on my books. I know where you are now, and so do you. [happy] Welcome to the Landing. Officially."

---

## ♥4 The Rounds

**Trigger:** The West Terminal, 20:00–21:30, after 2. *(Claude)*

- *[The West Terminal after hours. Garrick goes from airlock to airlock with a lamp, checking every seal by hand. Every night, Saffi says.]*
- **GARRICK:** "Evening. Walk with me or go home. Don't stand there being a silhouette."
- **GARRICK:** "Outer seal. Holding. ...You want to know why I don't like your trade. Fine. You've earned the short version."
- **GARRICK:** "I was security officer on the transport that brought us here. Refugees. Saffi, Kit in a sling, forty others."
- **GARRICK:** "A bounty hunter asked to dock. Said he was being chased. I let him in. [angry] What was chasing him was a Chernobog cutter."
- **GARRICK:** "[sad] They shot our drive out to get at him. We came down on this moon with half a hull, and S.A.R.A. talked us in."
- **GARRICK:** "He patched his ship from our wreck and left in the night. I've signed every airlock on this station shut myself ever since."
- **CHOICE:**
  - **"You couldn't have known what was chasing him."** (+High Friendship)
    - **GARRICK:** "[sad] That's what Saffi says. I check the seals anyway. ...Thank you."
  - **"I'd never have asked you to dock."** (+Friendship)
    - **GARRICK:** "No? ...Maybe not. You've got farm dirt under your nails now, anyway."
  - **"Sounds like he did what he had to."**
    - **GARRICK:** "[angry] He did what he wanted. Forty people paid for it."
    - *(-20 friendship with Garrick)*
- *[He checks the seal a second time. Then a third.]*
- **GARRICK:** "Same time tomorrow, if you're up. The lamp's heavier than it looks."
- *[The next morning: a letter (`garrick_issue`, in [MAIL.md](../MAIL.md))]*

---

## ♥6 Safety Class

**Trigger:** The plaza by the fountain, Saturday 10:00–12:30, after 4. With Kit, Pip, Nub and S.A.R.A. at her plaza pad. *(Claude; the NPC Master's self-defence class, for the kids.)*

- *[Saturday on the plaza. Garrick has laid out three foam mats by the fountain. Kit, Pip and Nub sit on them, as still as they can manage.]*
- **GARRICK:** "Lesson one. Feet apart. If somebody grabs you, you don't fight. You get loud, and you get gone."
- **KIT:** "[happy] And then you punch them!"
- **GARRICK:** "And then you get gone, Kit."
- **S.A.R.A.:** "Chief Garrick. I asked you not to turn my plaza into a parade ground. Guests will arrive to find children practising escapes."
- **GARRICK:** "[angry] Guests arrived on my last ship, too. One of them brought a war with him. I'd like these three to know where the doors are."
- *[S.A.R.A.'s light flickers. Garrick folds his arms. Both of them look at you.]*
- **CHOICE:**
  - **"Call it a safety class. Doors, shouting, hiding. No punching."** (+High Friendship)
    - **S.A.R.A.:** "[happy] A safety class. On a Saturday. With mats. ...I could put that in the hotel brochure."
    - **GARRICK:** "Safety class. Fine. Same lesson, better name."
  - **"Hold it in the armoury instead."** (+Friendship)
    - **GARRICK:** "The kids won't come to the armoury. That's rather the point of a plaza."
    - **S.A.R.A.:** "...Then here. But softly, Chief."
  - **"Let them punch. Kids should learn to fight."**
    - **GARRICK:** "[angry] No. That's exactly what I'm not teaching."
    - *(-20 friendship with Garrick)*
- **GARRICK:** "Right. Lesson two. Where's the nearest door? Point. ...Nub, that's a planter."
- **NUB:** "[happy] It's a door for plants."
- **GARRICK:** "[happy] ...Close enough."

---

## ♥8 Self-Defence Class

**Trigger:** The Shuttle Bay, 18:30–21:00, Monday to Friday, after 6. With Freya and Ix'ali. Reward: on your own ship, your crew hit boarders half again as hard. *(Zachary's reward; the scene is Claude's.)*

- *[The Shuttle Bay after hours. Garrick has chalked a ship's corridors on the hangar floor. Freya sits on a crate. Ix'ali holds two blunted blades.]*
- **GARRICK:** "{name}. Good. The kids got the safety class. You get the other one."
- **GARRICK:** "You fly with a crew now. Sooner or later somebody cuts through your hull and comes aboard. I've been on the wrong end of that."
- **GARRICK:** "On your own deck, you know every corner and they don't. Hold the doors. Fight in pairs. Never chase them back out."
- **IX'ALI:** "[happy] I am the boarder. I have been told not to enjoy this. I will enjoy it a little."
- **CHOICE:**
  - **"Hold the door with Freya: two on one."** (+High Friendship)
    - *[You and Freya take the chalk doorway together. Ix'ali comes in fast and finds two blades waiting for her.]*
    - **IX'ALI:** "[happy] Good. Very good. I am defeated. Honourably."
    - **GARRICK:** "That's the drill."
  - **"Charge her before she's through."** (+Friendship)
    - *[You meet her in the chalk corridor. It's close. Garrick calls it a draw.]*
    - **GARRICK:** "Brave. Wrong, but brave. On your own deck, make them come to you."
  - **"Chase her back to her ship."**
    - *[You drive Ix'ali back out of the chalk lines, across the hangar, and straight into a stack of fuel drums.]*
    - **GARRICK:** "[angry] And now you're on their ship. Alone. With their friends. That's how people die."
    - *(-20 friendship with Garrick)*
- **GARRICK:** "[happy] You'll do. Freya, you too. Anyone who flies with you gets the same drill."
- **FREYA:** "[happy] Dad hated boarders. He'd have loved this."
- *[Self-Defence Class: on your own ship, your crew hit boarders half again as hard]*
- **GARRICK:** "I had you down as a hunter. [happy] You're a resident with a ship. I've crossed the other word out in the ledger."
