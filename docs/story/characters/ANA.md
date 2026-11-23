# Anastasia "Ana": heart events and her week (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **"No Brig, Just Soup" (her old 2) plays the first time you meet her after her fight.** It's now her 0: the Medbay during her first two days (S.A.R.A.'s morning news sends you there), or the Shuttle Bay if you missed her there.
- **A new 2 in the mess hall:** nobody will talk to her until you decide to sit with her.
- **The lore:** the pirates always "knew" she was weak, because she never once fired on an innocent transport. Ivan covered for her. Once he was gone, her crew turned on her. This settles Decision 2: the game's version of the mutiny stands.
- **The pirates are the Chernobog; Ivan is the Rabble** (Decision 3). The game's text now says Chernobog cutter, Chernobog colours and so on. The Rabble's Reach and the Rabble's Nest are named after Ivan and keep their names.
- **Tally is Eshu** everywhere (Decision 18), so Garrick's line in 4 says Eshu.

**Not answered, so these are Claude's suggestions (change any of them):** her week and days off; at the end of 6 she asks to fly with you as crew; 8 stays in the Observation Lounge; 10 is a narrated orbit, with the flight jacket as the keepsake and the console bolted into your ship.

**The arc:** Ivan's sister unlearns that fear is loyalty.
- 0: pulled out of the wreck, and nobody asking for anything back.
- 2: too soft for the pirates, too pirate for the station.
- 4: fixing a ship instead of patching bullet holes.
- 6: the brother before the king.
- 8: flying solo is just lonely.
- 10: the first chart that points home.

**What's whose:** lines marked *(Zachary)* are his, from "Heart Events: All Romances": all of 0 except the lore lines and Garrick; the setting and every line of 4 but the last exchange; the setting, both of Ana's speeches and the choices in 6; the setting and both of Ana's lines in 8; and the outline of 10 (the star-chart console with both your initials, an orbit over the crater, the flight jacket). The idea of 2 is his and the lines are Claude's. Everything else is a draft by Claude, for Zachary to change or approve. Choices give +30 (Friendship) or +60 (High Friendship).

---

## Her week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where she goes |
|---|---|
| Tuesday, Wednesday, Friday | The Shuttle Bay 07:00, working with Freya; lunch in the mess hall; the bay again 13:30; dinner in the mess hall; home |
| Saturday, Sunday | The same, but she covers the bay alone on Freya's weekends off |
| Monday, Thursday (days off) | Star charts in the Observation Lounge 09:30; lunch; the lounge again 14:00; dinner; Rusk's bar 19:30; home 22:15 |

- She always eats at the last table in the mess hall (the scene of her 2).
- **Days off:** Monday and Thursday (`NpcData.DAYS_OFF`); the station calendar shows "Day off: Ana".
- **Her day lines** (the first thing she says when you talk to her; they alternate week by week): Monday and Thursday (her days off: the lounge, and Rusk threatening to charge her rent) and Saturday and Sunday (covering the bay, and Freya's note).
- Her first two days after the rescue are still in the Medbay (`SCHEDULES_ALT`), and she moves into East Home 3 after that.

**Flags this arc sets:** `ana_soup` (0), `ana_seat` (2), `ana_corridors` (4), `ana_compass` (6), the perk `perk_wingmate` (8), `ana_true_north_console` and the keepsake `keepsake_flight_jacket` (10), and `partner` = Ana if you accept at 8.

## In the game (23 Nov)

All six are playable cutscenes in `scripts/heart_events.gd`. She poses from her new heart-event sheet (`art/npc_ana_event.png`) and her action sheet (in a Medbay bed, tuning engines, eating). Saffi and Garrick are in 0; Freya, Job, Stu, Garrick and Jasper in 2; Freya and Garrick in 4. Not run in Godot yet.

- **She only appears once she's arrived** (Wave 2, the day after you pull her out), so her scenes wait for that.
- **0 has two places:** a new story flag, `ana_in_medbay`, is true for her first two days. Until then 0 plays in the Medbay; after that it plays in the Shuttle Bay. The scene marks her as met, so talking to her afterwards isn't a first meeting.
- **The second flight's loyalists** now say: "We always knew you were weak. Never once fired on a transport. Ivan covered for you. Ivan's gone."
- **To test:** in a debug build, **F3** plays the next event in order (Ana's 0 is the forty-second press); it brings Ana in if she hasn't arrived.
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **Not in yet:** Wingmate in ship battles; the console as a real upgrade on your ship; the jacket as an item you can wear.

---

## ♥0 No Brig, Just Soup (was her 2)

**Trigger:** the Medbay 08:00–20:00 during her first two days after the rescue. After that, the Shuttle Bay 07:00–17:00.

- **In the Medbay:**
  - *[The Medbay recovery bay. Ana sits stiffly on the edge of a cot in a torn flight jacket, eyeing the door like a cornered wolf.]* *(Zachary)*
  - *[Garrick stands just inside it, arms folded.]*
- **In the Shuttle Bay:**
  - *[The Shuttle Bay. Ana sits stiffly on a crate by the covered fighter, ribs strapped under a torn flight jacket, eyeing the door like a cornered wolf.]* *(Zachary, moved)*
  - *[Garrick leans on a tool cart nearby, arms folded.]*
- *[Saffi comes in carrying a steaming bowl of vegetable broth and fresh rolls, and sets them gently down beside Ana.]* *(Zachary)*
- **ANA** *(Zachary)*: "[angry] If this is an interrogation tactic, save it. Ivan's dead, the Chernobog lieutenants scattered, and I'm not giving you any old stash codes."
- **SAFFI** *(Zachary)*: "[happy] It's carrot-ginger soup, sweetheart. Maren says your ribs are still bruised from the crash. Eat while it's hot."
- *[Saffi goes back to the door. Ana stares at the bowl in disbelief, then looks up as you step closer.]* *(Zachary)*
- **ANA** *(Zachary)*: "I spent my whole life believing the Chernobog Clan was the only family out here—that we raided to protect our own."
- **ANA** *(Zachary, changed)*: "[angry] Then my own crew turned my guns on my bridge. They said they'd always known I was weak."
- **ANA:** "[sad] I never once fired on a transport. Not in all those years. Ivan covered for me. Without him, I was just the soft one."
- **ANA** *(Zachary)*: "Why did you pull me out of that wreck?"
- **CHOICE:**
  - **"You tried to protect innocent people. That counts."** *(Zachary)* (+Friendship)
  - **"Nobody gets left behind near Echo Landing."** *(Zachary)* (+Friendship)
  - **"I figured you owed me a rematch."** *(Zachary)* (no friendship)
    - *[Ana lets out a surprised, dry laugh.]* *(Zachary)*
- *[She picks up the spoon quietly.]* *(Zachary)*
- **ANA** *(Zachary)*: "Don't expect me to start baking pies tomorrow. Still... thank you."
- **GARRICK:** "[angry] I'll be right over here. Don't mind me."

*(The script's line was "my own second-in-command shot me in the back the second I ordered them not to fire on a civilian freighter". It now fits the game's second flight and the new lore.)*

---

## ♥2 A Seat at the Table (new)

**Trigger:** the mess hall 17:00–19:30 with Ana at 2 hearts, after 0. *(Zachary's idea; the lines are Claude's.)*

- *[The mess hall at dinner, loud and warm. Every table is crowded, everyone talking over everyone else.]*
- *[Every table but one. At the last table, Ana sits alone with her tray, and every seat around her is empty.]*
- **FREYA:** "[happy] Boss! Over here, we saved you a seat."
- *[Stu glances across at Ana, then back down at his plate.]*
- **CHOICE:**
  - **"[Sit with Ana]"** (+High Friendship)
  - **"[Sit with Freya and the others]"** (+Friendship)
    - **GARRICK:** "[angry] Ivan's sister. Eats in ten minutes flat with her back to the wall, like someone's about to take the tray."
    - **JOB:** "Heard Ivan's crew called her soft. Said she never would fire on the transports."
    - **FREYA:** "[sad] She's been in here every night this week. Nobody's sat with her once."
    - **STU:** "[sad] I know that look. That's somebody with a packed bag."
    - *[You look back at the last table. She hasn't touched her food. You pick up your tray.]*
- *(Either way, you sit down across from her.)*
- **ANA:** "[surprised] ...That seat's been empty all week. People walk the long way round so they don't have to pass it."
- **ANA:** "Out there, Ivan's crew always knew I was weak. I'd 'miss' the transports. Every time, for years."
- **ANA:** "[sad] In here I'm too Chernobog to be anything else. Funny, isn't it? Too soft for them, too pirate for you."
- **CHOICE:**
  - **"Then just be Ana."**
    - **ANA:** "...Just Ana. I don't know who that is yet."
  - **"Give them time."**
    - **ANA:** "[sad] Time. Right. I've got plenty of that now, thanks to you."
- *[Across the room, a chair scrapes. Freya brings her tray over.]*
- **FREYA:** "[happy] If the Boss sits here, I sit here. Scoot over, pirate."
- **ANA:** "[surprised] ...Navigator."
- **FREYA:** "[happy] Navigator. Even better. Then you can tell me why the Boss's ship pulls left on a hard burn."
- *[Ana almost smiles. Nobody else comes over. But a few people look, and one or two of them nod.]*

---

## ♥4 Grease & Second Chances

**Trigger:** the Shuttle Bay 14:00–17:00 on a Tuesday, Wednesday or Friday (when she and Freya both work), after 2.

- *[The Shuttle Bay. Ana and Freya are crouched under your ship, recalibrating its thruster manifolds.]* *(Zachary)*
- *[Freya hands Ana a torque wrench. Ana adjusts a fuel injector with practised speed.]* *(Zachary)*
- **FREYA** *(Zachary)*: "[surprised] Whoa—where did you learn to bypass a Terran stabilizer like that? Even Tikka takes twenty minutes on those valves!"
- *[Ana wipes grease from her cheek. A rare, small smile.]* *(Zachary)*
- **ANA** *(Zachary)*: "[happy] When your engines run on stolen parts and hope, you learn to fix them blindfolded."
- **ANA** *(Zachary)*: "Honestly... it feels good fixing a ship instead of patching bullet holes."
- *[Garrick walks into the bay and stops, arms crossed. Ana stiffens and steps back from the tools.]* *(Zachary)*
- **GARRICK** *(Zachary)*: "Relax, Ana. I'm not here to arrest you."
- **GARRICK** *(Zachary, Eshu for Tally)*: "Freya told me you've been charting the old Chernobog ambush corridors so Eshu's mail skiffs can avoid them."
- **GARRICK** *(Zachary)*: "That saved two freighters this week."
- **ANA** *(Zachary)*: "[sad] I can't undo what Ivan did. I'm just trying to balance the ledger."
- **GARRICK** *(Zachary)*: "Keep doing what you're doing. You're earning your berth."
- **FREYA:** "[happy] Told you he'd come round. He just has to glare at you for a month first. It's a Garrick thing."
- **CHOICE:**
  - **"He's right. You're earning it."** (+High Friendship)
    - **ANA:** "[happy] ...Don't make it a speech. But thanks."
  - **"Two freighters is a good week."** (+High Friendship)
    - **ANA:** "[happy] Two this week. I want three next week. Ledgers don't balance themselves."

---

## ♥6 Ghost of the Crown

**Trigger:** Rusk's bar 20:00–midnight, after 4.

- *[A quiet corner of Rusk's bar. Ana sits with a drink she hasn't touched, turning a tarnished brass compass over in her fingers.]* *(Zachary)*
- *[It's the only thing she has left from when she was small.]* *(Zachary)*
- **ANA** *(Zachary)*: "Ivan wasn't always a monster, you know. When our parents died on a frontier mining rig, he stole food so I wouldn't starve."
- **ANA** *(Zachary)*: "Somewhere along the way, he started believing his own ridiculous fairy tales about being a king..."
- **ANA** *(Zachary)*: "[sad] ...and I was too scared of being alone to tell him no."
- **ANA:** "When the crew called me soft, he'd laugh. 'Leave her be. Somebody on this ship should sleep at night.'"
- **ANA** *(Zachary)*: "Look at this place. Rusk pouring drinks for miners, Freya lending me her spare jackets, you checking in on me without asking for a thing."
- **ANA** *(Zachary)*: "[happy] For the first time in my life, I'm not looking over my shoulder."
- **CHOICE:**
  - **"You belong here, Ana—past and all."** *(Zachary)* (+High Friendship)
    - **ANA:** "[happy] Past and all. That's a lot of past. ...Okay."
  - **"You chose who you wanted to be when it mattered."** *(Zachary)* (+High Friendship)
    - **ANA:** "[sad] Every transport I let go. Yeah. I suppose I did."
- **ANA:** "Next time you fly out, take me with you. Eshu can put my name on his crew board."
- **ANA:** "[happy] As crew. Not cargo. I'm a better navigator than I ever was a prisoner."

*(The script's choices gave "+High Romance/Friendship"; there are no romance points, so they give +High Friendship. She can join your crew at 6 hearts on Eshu's board in the Shuttle Bay.)*

---

## ♥8 Co-Pilot's Promise (confession)

**Trigger:** the Observation Lounge 20:00–midnight with Ana at 8 hearts, after 6. Perk, whether or not you accept: Wingmate.

- *[The Observation Lounge at night. Beyond the glass, meteors streak across the Neutral Zone, one after another.]* *(Zachary)*
- **ANA** *(Zachary)*: "I used to think freedom meant flying solo with nobody able to catch you. Turns out, flying solo is just lonely."
- **If you're dating someone else (the friendship ending):**
  - **ANA** *(Zachary)*: "You saved my life twice—once in that wreckage, and once by giving me a reason to stay on Echo Landing."
  - **ANA:** "[happy] So here's the deal. Whoever you fly with, I'm your navigator. Always. That's what friends are for, right?"
- **Otherwise:**
  - *[She turns to you, cheeks faintly flushed, voice steady.]* *(Zachary)*
  - **ANA** *(Zachary)*: "You saved my life twice—once in that wreckage, and once by giving me a reason to stay on Echo Landing."
  - **ANA** *(Zachary)*: "[love] If you still want a navigator by your side... I don't want to go anywhere without you."
  - **CHOICE:**
    - **"I want you by my side, Ana."**
      - *(Ana is now your partner.)*
      - **ANA:** "[surprised] ...Okay. Okay. Plot a course, then. Wherever it goes, I'm navigating."
      - *[A meteor burns all the way across the dome. She doesn't make a wish. She doesn't need one.]*
    - **"You're my best friend, Ana. Nothing less."**
      - **ANA:** "[sad] Best friend. Right. That's... still more than I ever had out there."
      - **ANA:** "[happy] The navigator's chair is still yours whenever you want it. Friends fly together too."
- **ANA:** "[happy] Oh, and I've been tuning your fold drive on the side. Don't tell Freya. You'll feel it on the next jump."
- **Perk: Wingmate (+20% ship evasion and faster FTL travel)** *(Zachary)*

---

## ♥10 True North

**Trigger:** the Shuttle Bay 18:00–20:30 (sunset) while you're dating Ana, with her at 10 hearts.

*(Zachary's outline: Ana surprises you with a custom-calibrated star-chart console etched with both your initials and takes you on a quiet scenic orbit above the moon's glowing crater. Keepsake: the console and a custom flight jacket. The lines are Claude's; the orbit is narrated under a fade, as in Freya's Test Flight.)*

- *[The Shuttle Bay at sunset. The launch doors stand open, and the crater's rim is turning gold.]*
- **ANA:** "[happy] There you are. Get in. Navigator's orders."
- **ANA:** "I made you something. Well. I made us something. It's bolted into the cockpit, so you can't give it back."
- *(The screen fades.)*
- *[Beside the controls, a new star-chart console glows: custom-calibrated, every lane she knows, and both your initials etched into the bezel.]*
- *[The launch doors fall away beneath you. Ana takes you up in a slow, quiet orbit over the moon's glowing crater.]*
- **ANA:** "[love] Every chart I ever drew was a way out. This is the first one that points home."
- *[You land as the last of the light leaves the crater.]*
- **ANA:** "[bashful] And this. A flight jacket, your size. Sesska did the stitching. Mine has both our initials on the collar too. Don't laugh."
- *[A flight jacket, broken in just right.]*
- **Keepsake: Ana's flight jacket** *(Zachary)*

---

## Still open

- **The console** could become a real upgrade on your ship (on the ship screen); for now it's a flag, `ana_true_north_console`.
- **Wingmate** (+20% evasion, faster fold) isn't in ship battles yet.
- **Eshu 6 "Safe Routes"** repeats her corridor charting in 4; it should be the follow-on.
