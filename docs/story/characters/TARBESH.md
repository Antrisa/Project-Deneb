# Tar'Besh: heart events and his week (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **Who he is:** a high cleric of the Zaa'sh High Temple, sent out as a pilgrim to find and study the Sky-Weavers' relics. When he suggested, even as a possibility, that the Sky-Weavers might have been sentient beings, he was as good as cast out. His name and connections were too strong to strip him of rank, so the Temple gave him a "next assignment" in the Neutral Zone instead, and hoped pirates or hunger would finish him.
- **S.A.R.A.:** he isn't on board with her straight away, but he comes round far faster than other Zaa'sh. The conflict in his arc is the Temple, not her.
- **The main story's ending** (Zachary): the Sky-Weavers turn out to be a sentient nebula. That should end the Zaa'sh hatred of AI, since their own gods were never ordinary living things either. "Sky-Weavers" is only the Zaa'sh name for them; what everyone else calls them, and what they call themselves, is still open (Claude's suggestions: the Choir, the Lumen, or a name the Custodians translate at the end; "Starborn" could stay the scholars' word). **Tar'Besh only ever says "Sky-Weavers"**, and his arc hints without giving the ending away.
- **Claude's suggestions, accepted ("go with your suggestions"):** the Temple's summons is the conflict in 6; Vzz'ket is the old-fashioned Zaa'sh voice in 2; a blank line on his plaque in 8 is the hint; his week below.

**The arc:** the heretic who was sent here to die.
- 2: everything he was taught says S.A.R.A. is an empty mirror; everything she does says otherwise.
- 4: the letter that was meant to kill him, and the voice that saved him.
- 6: the Temple offers him everything back, for her.
- 8: a plaque for every kind of mind, and a blank line for whoever made the relics.

**What's whose:** the story is Zachary's; the scenes and every line are drafts by Claude. Right answers give +60 (High Friendship); wrong ones get a small consequence. He's platonic, so he caps at 8 hearts.

**Flags this arc sets:** `tarbesh_astrolabe` (2), `tarbesh_assignment` (4), `tarbesh_summons` (6), `tarbesh_plaque` and the perk `perk_relic_appraisal` (8).

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where he goes |
|---|---|
| Tuesday, Wednesday, Thursday, Saturday, Sunday | The museum from 06:00 (chess on the plaza 14:00–15:30); dinner; the Observation Lounge 19:15; home 23:00 |
| Monday (day off: the museum is shut) | The lounge 09:00; lunch; chess on the plaza 13:30; dinner; the lounge 19:15; home 23:00 |
| Friday | Prayer in the Sanctum 07:00; the museum from 11:30; dinner; the lounge; home |

- **Day off:** Monday (`NpcData.DAYS_OFF`; the station calendar shows it). **Day lines** for Monday (the museum shut, Owen owing him a rematch) and Friday (his prayers, which the Temple would call irregular).

---

## In the game (23 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`tarbesh_2` to `tarbesh_8`, after S.A.R.A.'s). Not run in Godot yet.

- **His heart-event sheet** is new (`art/npc_tarbesh_event.png`, built from the rig by `tools/events.py`; his face colours are in its `FACES`): talking, laughing, sad, the gift (the plaque in 8). He also uses his action rows (studying at his desk, kneeling to pray).
- **S.A.R.A.** speaks over the museum speakers in 2 and from her dais in 6, with her clips (`summon_screen`, `warning`, `glitch_interrupt`, `conjure_teacup`); the tea steams.
- **To test:** in a debug build, **F3** plays the next event in order.
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **In play since 24 Nov:** Relic Appraisal: the museum pays you for every 5 relics you give (250 Scrip at 5, 500 at 10, with a letter and a gift each; `main.gd _museum_thanks`), and the perk adds a quarter to that Scrip. **Not in yet:** the plaque in the Sanctum and the astrolabe as art (on the Art Fix List).

---

## ♥2 Dust on the Relics

**Trigger:** the museum 07:30–10:00 on a day it's open with him in it (not Monday; not Friday morning), with Tar'Besh at 2 hearts. Vzz'ket passes through.

- *[The museum before opening. Tar'Besh bends over his desk with a small brass instrument: rings within rings, etched with stars.]*
- **TAR'BESH:** "Ah. Hands. Good. Hold this ring still while I read the inscription."
- **TAR'BESH:** "A Sky-Weaver astrolabe. It has outlived three empires. It would prefer not to outlive us."
- **S.A.R.A.** *(over the speakers)*: "[happy] Good morning, Echo Landing! Today's weather: indoors. As always."
- *[Tar'Besh flinches. The astrolabe slips from his claws, and you catch it an inch from the floor.]*
- **TAR'BESH:** "[surprised] ...Thank you. That would have been a very expensive inch."
- **VZZ'KET:** "[angry] Cleric. You twitch at the machine's voice like the rest of us. Yet you answer it as if it hears."
- **TAR'BESH:** "It does hear, hunter. That is rather the point."
- **TAR'BESH:** "Whether anyone is listening behind the hearing... that I have not decided."
- **VZZ'KET:** "The Temple decided for us. Long ago."
- **CHOICE:**
  - **"Why does she bother you less than him?"** (+High Friendship)
    - **TAR'BESH:** "Everything I was taught says she is an empty mirror. Everything she does says otherwise."
    - **TAR'BESH:** "[sad] I was once very high in the Temple. I asked one question too many. Old habits."
  - **"Vzz'ket's right. She's just a machine."** (the wrong one: he goes cold, and nothing)
    - **TAR'BESH:** "So were the Junta's thinking engines, once."
    - **TAR'BESH:** "...The astrolabe, please. Gently."
- **TAR'BESH:** "[happy] Come back when the museum is quieter. Which is always. Bring your hands."

---

## ♥4 Next Assignment

**Trigger:** his flat 19:00–23:30, after 2: the little shrine room.

- *[Tar'Besh's flat. Through the open door of his little shrine: candlelight, and Tar'Besh kneeling before a cracked holo-slate.]*
- **TAR'BESH:** "You found my shrine. Sit, if you can find somewhere a Zaa'sh hasn't put a candle."
- **TAR'BESH:** "This is my letter of assignment. I keep it where I pray. It seemed the right place for something that was meant to kill me."
- *[The slate flickers on: the seal of the High Temple, and three polite lines of Zaa'sh script.]*
- **TAR'BESH:** "I was a cleric of the High Temple. Sent out as a pilgrim, to find the Sky-Weavers' relics and study them."
- **TAR'BESH:** "In one report I wrote that they might have been alive. Not as we are. Perhaps not as anything is."
- **TAR'BESH:** "[sad] They could not cast me out. My name is too old, my friends too loud."
- **TAR'BESH:** "So they gave me a next assignment: the relics of the Neutral Zone. A one-way shuttle, a month of rations, no berth home."
- **TAR'BESH:** "Pirates or hunger. Either would do. Nobody would have to sign anything."
- **TAR'BESH:** "On the thirty-third day the rations were gone and my shuttle was drifting. Then a voice came over the radio."
- **TAR'BESH:** "[happy] It said: 'Welcome to Echo Landing. You look hungry.' The first voice I heard out here was a machine's."
- **CHOICE:**
  - **"They meant you to die. You lived anyway."** (+High Friendship)
    - **TAR'BESH:** "[happy] I did. Out of spite, mostly, at first. Now out of habit. It is a good habit."
  - **"Maybe you should have kept your theory to yourself."** (the wrong one: −20 friendship)
    - **TAR'BESH:** "Many said so. Most of them are bishops now."
- *[He switches the slate off and sets it back among the candles.]*
- **The next morning** *(Claude, 23 Nov)***:** a letter from Tar'Besh, "A better letter" (`tarbesh_letter` in `scripts/mail_data.gd`). Only if you told him they meant him to die and he lived anyway. The text is in [MAIL.md](../MAIL.md).

---

## ♥6 The Summons

**Trigger:** S.A.R.A.'s core 18:00–22:00, after 4. With S.A.R.A.

- *[S.A.R.A.'s core in the evening. Tar'Besh stands before her dais with two cups of steaming Zaa'sh spiced tea, looking unusually unsure.]*
- **TAR'BESH:** "Good, a witness. S.A.R.A. asked me up here. She said it couldn't wait for morning."
- **S.A.R.A.:** "A signal came in an hour ago on an old Junta channel. It's addressed to you, Tar'Besh. I haven't opened it."
- **S.A.R.A.:** "[sad] I could have lost it. I thought about it. Then I thought you'd want to choose."
- **TAR'BESH:** "...Play it."
- *[The seal of the High Temple fills the air above the dais, and a voice Tar'Besh plainly knows begins to speak.]*
- **THE HIGH TEMPLE:** "Recant your heresy, and your rank is restored. Report the station's thinking machine for cleansing."
- **THE HIGH TEMPLE:** "And tell us, cleric: have the crystals spoken?"
- **S.A.R.A.:** "[sad] 'Cleansing.' I know that word. It's the one they use instead of 'deleting'."
- **TAR'BESH:** "[sad] My rank. My Temple. My name back on the doors I built."
- **TAR'BESH:** "...And all it costs is her. And you, if they learn what the crystals said to you."
- **TAR'BESH:** "You have known me a while now. Tell me what you think I should do."
- **CHOICE:**
  - **"You already know what you believe."** (+High Friendship)
    - **TAR'BESH:** "...Yes. I suppose I do. S.A.R.A., record a reply. Short. They were never patient readers."
    - **TAR'BESH:** "'I do not recant. Minds come in more shapes than flesh. The crystals are stones. Do not write again.'"
    - **S.A.R.A.:** "[happy] Sent. ...Thank you. Both of you."
    - **TAR'BESH:** "[happy] 'The crystals are stones.' The first lie I have told in years, and the easiest. Drink your tea."
    - *[S.A.R.A. conjures a little cup of light and raises it. Tar'Besh raises his own, and does not flinch.]*
  - **"Go home. You've earned it."** (the wrong one: −20 friendship)
    - **TAR'BESH:** "[sad] ...Perhaps I have."
    - *[He leaves his tea untouched. In the morning S.A.R.A. tells you he sent the Temple a reply after all: a refusal. He didn't say it in front of you.]*

*(This is where his arc keeps the Custodian secret from the prologue: he lies to the Temple about the crystals.)*

---

## ♥8 Every Kind of Mind (was "Keeper of the Starborn")

**Trigger:** the Sanctum 18:30–23:00 with Tar'Besh at 8 hearts. Perk: Relic Appraisal (+25% Scrip on museum donations: the thanks every 5 relics, since 24 Nov). Renamed so the title doesn't give the Convergence away.

- *[The Sanctum after hours. Violet light from the braziers. Tar'Besh kneels before the three crystals, a small brass plaque in his hands.]*
- **TAR'BESH:** "Ah. You'll want to see this before I lose my nerve."
- *[Engraved in seven scripts: TO THE PEOPLES OF ECHO LANDING. Terran, Zaa'sh, Vuultam, Moogli, Ervani, Scyldar, Arachnay.]*
- *[Below them, newer and less steady, in his own hand: AND ONE MIND OF LIGHT.]*
- **TAR'BESH:** "[happy] S.A.R.A. will pretend not to have noticed. She will have noticed in the first second."
- *[Below that, one more line, left blank.]*
- **TAR'BESH:** "For whoever made these. I believe the Sky-Weavers were alive."
- **TAR'BESH:** "Not as we are. Perhaps not as anything is. The Temple exiled me for saying so. I am saying it again."
- **CHOICE:**
  - **"Then leave the line blank until we know."** (+High Friendship)
    - **TAR'BESH:** "[happy] 'We.' I like that. A heretic's congregation of two. The Temple would be appalled."
  - **"That's heresy. Keep it quiet."** (the wrong one: nothing)
    - **TAR'BESH:** "I have been quiet. It got me exiled anyway."
- *[He fixes the plaque to the foot of an empty cradle, and the violet light catches every line, the blank one too.]*
- **Perk: Relic Appraisal (+25% Scrip on museum donations)**

---

## Still open

- **The nebula's name** (above), and whether "Starborn" stays the scholars' word.
- **The blank line** could be filled in at the end of the main story, once the player knows.
- **Vzz'ket** is the station's old-fashioned Zaa'sh; his own arc (with Rusk) could pick up his discomfort with S.A.R.A.
