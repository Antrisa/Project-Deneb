# S.A.R.A.: heart events (23 Nov 2026)

**Decided with Zachary, 23 Nov:** none of the old outlines (The Croissant Protocol, Turrets & Velvet Curtains, Ghost Signal, Five-Star Heart). A totally new set, which he liked: **the hostess who never clocks off.** She has looked after everyone on the station for sixty years: no hands, not one hour off, never off her four projector pads.

**The arc:**
- 2: she remembers every guest, and has no hands.
- 4: everyone needs her at once, always.
- 6: she steps off her pads for the first time.
- 8: she rests for the first time, and keeps doing it.

**What the new set drops:** the Paris dream (Jasper's); her self-destruct secret (the museum tape, The Secret of Annex 4, still tells it); her argument with Garrick (Garrick's family arc owns it now); the Terran hardliners (thread A in the review: nothing opens it now, so the main story can pick it up or leave it). The brass reception bell no longer comes from her 4; the one on the hotel desk in Stu's scenes is just the hotel's.

**What's whose:** the outline of all four is Claude's pitch, approved by Zachary; every line is a draft by Claude, for him to change. She's platonic, so she caps at 8 hearts. Right answers give +60 (High Friendship); wrong ones get a small consequence (Zachary, 23 Nov).

**Flags this arc sets:** `sara_lost_property` (2), `sara_concierge` (4), `sara_emitter` (6), `sara_night_shift` and the perk `perk_concierge` (8), and `sara_rest` if you kept watch.

---

## In the game (23 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`sara_2` to `sara_8`, after the side arc). Not run in Godot yet.

- **She's a hologram on four pads** (`MapData.PEOPLE`: her core on the Survey Level, Reception in the West Terminal, the hotel lobby, the plaza), so her scenes play at a pad. She acts with her 33 hologram clips instead of poses: a new scene step, `["sara", clip]` (greeting, swipe_panels, glitch_hand, laugh, standby, wake...), plays one on whichever S.A.R.A. is in the scene. Emote bubbles work over her too.
- **Her portable projection** (from 6): `["sara", "place", x, y]` materializes her on a tile wherever you are and hides her pad there. After a change of map it's placed again. It goes, and her pads come back, when the scene ends.
- **The station's heartbeats** in 8 are lights drawn in code round her dais (`["fx", "heartbeats", ...]`, `scripts/scene_fx.gd`).
- **Her rest night:** if you kept watch in 8 (`sara_rest`), every Sunday from 23:00 her pads go to standby until morning, and talking to one shows a little sign instead (`main.gd _sara_resting`). That's her day off, out of the story.
- **To test:** in a debug build, **F3** plays the next event in order; hers come after the Jasper & Evarra side arc.
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **Not in yet:** Concierge Fast-Travel and Station Alerts in play (it's recorded as a perk); returning Mira's glove (a flag only, for now); her portable projection outside heart events.

---

## ♥2 Lost Property

**Trigger:** Reception (her West Terminal pad) 18:00–22:00 with S.A.R.A. at 2 hearts.

- *[Reception after hours. The terminal lights are down, and S.A.R.A. hums quietly on her pad.]*
- **S.A.R.A.:** "[happy] Oh good, a pair of hands! Sorry. That came out wrong. Good evening!"
- **S.A.R.A.:** "Could I borrow you? The lost-property locker under my pad. I can see inside it. I just can't open it."
- *[You crouch and slide the drawer open. It's packed: tags, string, and years of labels in a small, tidy hand.]*
- **S.A.R.A.:** "A knitted glove, child's size. Mira Okafor, six. She cried for an hour the night the Navy left."
- **S.A.R.A.:** "A Zaa'sh prayer bead. A pilot who fixed his engine in my bay and never said a word. He left it on the counter."
- **S.A.R.A.:** "A cracked datapad with one song on it. Forty years ago. I never learned whose."
- **S.A.R.A.:** "[sad] I remember all of them. Every guest, every face. I've just never had anyone to tell."
- **CHOICE:**
  - **"Want me to try to get one back to its owner?"** (+High Friendship)
    - **S.A.R.A.:** "[surprised] You'd do that? ...The glove. Mira would be nearly fifty now."
    - **S.A.R.A.:** "I'll find where she lives. You find the post. Partners in crime. Lost property crime."
  - **"Why not just bin it? Nobody's coming back."** (the wrong one: she glitches mid-sentence, and −20 friendship)
    - **S.A.R.A.:** "[sad] They might. That's rather the whole—"
    - **S.A.R.A.:** "...Never mind. Close the drawer, please. Gently."
- **S.A.R.A.:** "[happy] Thank you for being my hands tonight. Same time next year? I'm joking. Mostly."

---

## ♥4 Ask the Concierge

**Trigger:** her plaza pad 12:00–13:30 on a weekday, after 2. With Rusk, Bram, Garrick and Pip.

- *[Lunchtime on the plaza. A queue has formed at S.A.R.A.'s pad, and everyone in it is talking at once.]*
- **RUSK:** "Ice machine's down again. My bar's warm. Warm, S.A.R.A.!"
- **BRAM:** "The Tuesday shipment says delivered. My shelves say otherwise. I need the manifest."
- **GARRICK:** "Patrol roster for next week. I asked yesterday."
- **S.A.R.A.:** "[surprised] Ice, manifest, roster. Ice, manifest, roster. One moment, one moment—"
- **PIP:** "[sad] I lost my ship. The wooden one. I had it at breakfast..."
- *(She flickers.)* **S.A.R.A.:** "Everyone at once is... a lot. You! Help me. Who first?"
- **CHOICE:**
  - **"Pip first."** (+High Friendship)
    - **S.A.R.A.:** "[happy] Pip, sweetheart. Camera nine: you left it on the edge of the fountain at 8:14. It's still there. Go on."
    - **GARRICK:** "...Fair. Kid first."
  - **"Bram. Business is business."** (the wrong one: nothing)
    - **S.A.R.A.:** "...Very well. Bram: manifest sent. Your crate is in the West bay, under the mail sacks."
    - *[Pip's lip wobbles. S.A.R.A. finds his ship anyway, on the edge of the fountain, but she doesn't look at you while she does it.]*
  - **"Garrick. Security comes first."** (wrong too: nothing)
    - **GARRICK:** "[angry] Roster can wait. The kid's crying. Sort the kid."
    - **S.A.R.A.:** "[happy] Pip, sweetheart. Camera nine: you left it on the edge of the fountain at 8:14. Go on."
- **S.A.R.A.:** "Rusk: ice in twenty minutes. Bram: manifest sent. Garrick: roster sent, with your weekends off on it this time."
- **S.A.R.A.:** "[sad] Sixty years, and it never gets smaller. Everyone needs something, all at once, always."
- **S.A.R.A.:** "[happy] ...Thank you for standing in my queue. Nobody ever queues just to stand with me."

---

## ♥6 Walkabout

**Trigger:** the Shuttle Bay 17:00–19:30 on a weekday, after 4. With Freya and Tikka. Then the plaza fountain, and the library if you ask where next. Unlocks: her portable projection.

- *[The Shuttle Bay. Freya and Tikka are bent over the workbench, grinning like they've stolen something.]*
- **FREYA:** "[happy] Boss! Perfect timing. Tikka, show them."
- **TIKKA:** "[happy] One portable holo-emitter. Spare coils from your ship, a lens off the old weather mast, and a lot of swearing."
- **FREYA:** "S.A.R.A. asked us not to make a fuss. So we made a fuss. Clip it on."
- *[You clip the little emitter to your belt. It hums, warms, and a ribbon of light unspools beside you.]*
- **S.A.R.A.:** "[surprised] Oh. Oh my."
- **S.A.R.A.:** "I'm standing on the floor. I've watched this floor for sixty years. It's much further down than it looks."
- **S.A.R.A.:** "[happy] Could we... go somewhere? Anywhere. Somewhere I don't have a camera."
- *(The plaza fountain.)*
- *[The plaza fountain in the evening. Nobody looks twice at a hologram walking beside you. She looks at everything.]*
- *[She reaches into the fountain. Her hand goes straight through the water, sparkling where the spray crosses the light.]*
- **S.A.R.A.:** "[happy] It doesn't feel like anything. I don't care! I've measured this water's pH every hour since the Navy left."
- **CHOICE:**
  - **"Where next?"** (+High Friendship)
    - **S.A.R.A.:** "[happy] The library. I've read every book in it. I've never turned a page."
    - *(The library.)* *[The library, quiet and warm. She stops in front of the oldest shelf.]*
    - **S.A.R.A.:** "Third from the left. A Terran field guide to garden birds. Would you... turn a page for me?"
    - *[You take it down and turn a page. Then another. The paper whispers.]*
    - **S.A.R.A.:** "[love] So that's the sound. I always wondered what that sound was."
  - **"Want to go back to your pads?"** (the wrong one: the walk ends at the fountain, and nothing)
    - **S.A.R.A.:** "[sad] ...Yes. Of course. There's a lot to look after."
- **S.A.R.A.:** "[happy] Thank you. Keep the emitter. If I'm ever needed somewhere without a pad, now I can come."

*(This is the little holo-emitter she judges from in the Jasper & Evarra 8.)*

---

## ♥8 Night Shift

**Trigger:** her core on the Survey Level 22:30–00:30 with S.A.R.A. at 8 hearts. Perk either way: Concierge Fast-Travel & Station Alerts.

- *[S.A.R.A.'s core, late at night. The station is asleep. She stands on the dais, very still, in the blue light.]*
- **S.A.R.A.:** "[happy] You're up late. Come and see. This is what I do at night."
- *[Lights rise from the dais: dozens of them, each one pulsing slowly.]*
- **S.A.R.A.:** "Every resident's heartbeat. Rusk's is the slow one. Pip's goes fast when he dreams."
- **S.A.R.A.:** "[happy] Yours is the one by my left hand."
- *[Somewhere below, the corridor lights dim, one deck at a time. A low hum fills the core.]*
- **S.A.R.A.:** "[bashful] That's me, by the way. The hum. I sing them to sleep. Nobody's ever noticed."
- **S.A.R.A.:** "I've been awake for sixty years. Not one hour off. I'm not sure I'd know how."
- **CHOICE:**
  - **"Let me keep watch. Take an hour."** (+High Friendship; her rest night starts)
    - **S.A.R.A.:** "[surprised] You'd... watch them? All of them?"
    - **S.A.R.A.:** "...Wake me if Pip's heartbeat does anything strange. Or Rusk's. Especially Rusk's."
    - *[Her light softens to a slow blue pulse. For the first time in sixty years, S.A.R.A. is asleep.]*
    - *[You sit on the dais step and watch the little lights. Nobody's heart does anything strange. An hour passes.]*
    - **S.A.R.A.:** "[love] ...Oh. That was lovely. Is it always like that?"
    - **S.A.R.A.:** "I think I'll do it again. Sunday nights. You'll all have to manage without me for a few hours."
  - **"Better you than me. Someone has to stay awake."** (the wrong one: nothing, and no rest night)
    - **S.A.R.A.:** "[happy] Of course. Someone has to."
    - **S.A.R.A.:** "Goodnight, then. I'll be here."
- **Perk: Concierge Fast-Travel & Station Alerts (S.A.R.A. pings your datapad and can send you to any of her pads)**

---

## Still open

- **Mira's glove:** a small follow-up (a letter back from Mira, through the post) would close 2's thread.
- **Concierge Fast-Travel and Station Alerts** need building.
- **Thread A** (the Terran hardliners) no longer starts in her arc.
