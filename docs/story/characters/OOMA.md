# Ooma: heart events and her week (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **Everyone gets their own arc**, and side arcs are 2–3 scenes. Ooma's arc is her own; what she shares with Bram is the side arc in [`BRAM_OOMA.md`](BRAM_OOMA.md).
- **Keep her mysterious** (Zachary: "she may be a spy or blackmarket trader or whatever, but she seems to like the station and giving you good product"). Nothing in the arc says what she is. Each scene shows one more side of her (she knows things she shouldn't, her ship flies under many names, her crate has a false bottom) and one more good thing she has quietly done, and leaves it there.

**The arc:** the trader nobody can place.
- 2: the first pick. She knows more about you than you told her.
- 4: three names. S.A.R.A. has been keeping a list of the names her ship flies under.
- 6: the inspection. Garrick wants her crate opened; vouch for her and she shows you almost all of it.
- 8: low tide. One true thing: in three hundred ports, this is the only one where people wave when her ship comes down.

**What's whose:** Zachary's direction above; the scenes and every line are drafts by Claude. Right answers give +60 (High Friendship); wrong ones −20.

**Flags this arc sets:** `ooma_first_pick` (2), `ooma_three_names` (4), `ooma_inspection` (6), `ooma_low_tide` and the perk `perk_ooma_old_friend` (8).

---

## Her week

- She's on the station on **Wednesdays and Saturdays** only (`tools/build.py VISITOR_DAYS`), and out on her ship in space the rest of the week (ring 2, selling rare weapons). Her scenes are on her days.
- **Once the Merrow Deep is open** (the Leviathan is dead), she spends **Saturday evenings** on its south beach with her feet in the water, then goes back to her stall for the night (`SCHEDULE_DAYS_RAW`), with a Saturday day line to match.

---

## In the game (23 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`ooma_2` to `ooma_8`), with poses from her new heart-event sheet (`art/npc_ooma_event.png`) and her action sheet (beckon, eat), emotes and sounds; in 4, S.A.R.A. acts from her Reception pad. Not run in Godot yet.

- **Her 8's reward: an old friend's price.** From then on everything at her ship in space costs 20% less: weapons, augments, systems, goods, fuel, missiles, parts and repairs (`main.gd _ooma_stock`).
- **Letter:** the morning after 2, from "O.", with a void sapphire: "This was not on the table."
- **Her kiosk:** the scenes put her behind her kiosk on the plaza (`Ooma's kiosk`, 132, 90). Her usual day still stands her at (120, 108), by the games tables, where upstream's concourse placed her. Moving her usual spot to behind the kiosk would match the scenes (`tools/concourse.py`, `outdoor`).
- **To test:** **F3** plays the next event in order; it moves the day to a Wednesday or Saturday.

---

## ♥2 The First Pick

**Trigger:** her kiosk on the plaza, Saturday 06:00–09:00. *(Claude)*

- *[Saturday, early. Ooma is setting out her stock: things in jars, things in boxes, and one thing in a cage under a cloth.]*
- **OOMA:** "Ahh. Good morning, pilot. You are early. Early people get the first pick."
- **OOMA:** "Tell me what you need, and I will tell you what you want. They are rarely the same thing."
- **OOMA:** "You came down on this moon with a cracked hull and a name nobody here had heard of. [happy] I have heard it now. I hear most things."
- **CHOICE:**
  - **"Then what do I want?"** (+High Friendship)
    - **OOMA:** "[happy] Oh, very good. Most people ask how I know their name. You ask the useful question."
    - *[She looks at you for a long moment, the way Bram looks at a crate of ore. Then she lifts the cloth an inch, and drops it again.]*
    - **OOMA:** "Not yet. You are not ready for it, and it is not ready for you. Come back when you need something you do not know about."
  - **"I'll give you half for whatever's under the cloth."**
    - **OOMA:** "I do not haggle. I simply wait until you agree."
    - **OOMA:** "...And you have not agreed. [happy] Next week, perhaps."
    - *(-20 friendship with Ooma)*
- *[From somewhere under the cloth comes one soft, polite chirp.]*
- *[The next morning: a letter (`ooma_sapphire`, in [MAIL.md](../MAIL.md))]*

---

## ♥4 Three Names

**Trigger:** the West Terminal's customs desk as she signs out, Wednesday 20:00–22:30, after 2; S.A.R.A. on her Reception pad. *(Claude)*

- *[The West Terminal at night. Through the far window, Ooma's ship waits on the landing pad with its lights turned low.]*
- *[Ooma is at the customs desk, signing herself out, as she does every Wednesday.]*
- **S.A.R.A.:** "[happy] Departure logged, Ooma. Your transponder says the Gilded Eel tonight."
- **OOMA:** "A pretty name."
- **S.A.R.A.:** "Last month it said the Patient Tide. In the spring, the Seventh Daughter. I keep a list. It is a long list."
- **OOMA:** "[happy] Pilot. Come and help me. The station's mind is counting my ships."
- **S.A.R.A.:** "I am counting your ship. Singular. It is the names that are plural."
- **OOMA:** "A ship is like a coat, dear. You wear a different one to a different party."
- **S.A.R.A.:** "Most coats don't have Terran customs seals on the inside of the hatch."
- **OOMA:** "Well? You have heard the charges."
- **CHOICE:**
  - **"Her business is her own. She's always been good to us."** (+High Friendship)
    - **OOMA:** "[happy] ...Hm. A good customer and a good character witness. You are wasted on farming."
    - **S.A.R.A.:** "Noted. And for the record, Ooma: the antibiotics last winter. Maren never found out who brought them. I did."
    - **OOMA:** "I do not know what you mean."
    - *[She very clearly does.]*
  - **"Come on, Ooma. Who are you really?"**
    - **OOMA:** "[sad] Truth is a luxury good, pilot. I do not stock it."
    - *(-20 friendship with Ooma)*
- **OOMA:** "Goodnight, both of you."
- **S.A.R.A.:** "She says 'goodnight'. In all these years she has never once said 'goodbye'. I've checked."

---

## ♥6 The Inspection

**Trigger:** the armoury, Wednesday 14:00–16:30 (Garrick's working day), after 4. Garrick and Ix'ali are there. *(Claude)*

- *[The armoury. A battered sea-green crate sits on the floor between Garrick and Ooma, its lock shaped like a curled shell.]*
- **GARRICK:** "Terran bulletin this morning. A Scyldar trader of your description, running medicine and worse past their blockade."
- **OOMA:** "So many Scyldar traders. I expect we all look alike to you."
- **GARRICK:** "[angry] Open the crate, Ooma."
- **OOMA:** "I do not open my crates for bulletins. I open them for friends."
- **GARRICK:** "Pilot. You've been at her stall more than anyone on this station. Your call."
- **CHOICE:**
  - **"I'll vouch for her. Whatever's in there, it's never hurt us."** (+High Friendship)
    - **GARRICK:** "...Fine. On your word. If it bites somebody, it's your word that bit them."
    - **IX'ALI:** "[happy] He likes you both. He would sooner swallow his badge than say so."
    - *[Ooma kneels and opens the crate for you alone. Seed packets. Sealed medicine vials. A child's carved wooden fish.]*
    - *[A stack of letters tied with green string, none of them hers. Then she lifts the bottom of the crate an inch.]*
    - *[Under it is something dark that catches the light once. She lets you see that much, and closes it again.]*
    - **OOMA:** "[happy] Some things are not for sale. Even to you. ...Especially to you."
  - **"Just open it, Ooma. Then it's over."**
    - *[Ooma opens the crate. Seed packets. Medicine vials. A carved wooden fish. Garrick grunts, satisfied, and goes back to his ledger.]*
    - **OOMA:** "[sad] You could have trusted me. Many do not. I had hoped you were not many."
    - *(-20 friendship with Ooma)*

---

## ♥8 Low Tide

**Trigger:** Saturday 19:00–22:30, ankle-deep in the Merrow Deep (its south beach) once the Leviathan is dead; **backup** until then, her feet in the plaza fountain. Reward: an old friend's price at her ship. *(Claude)*

- *If the Leviathan is dead:*
  - *[The Merrow Deep at night. Ooma stands ankle-deep in the black water with her robe hitched up, her face tentacles drifting in the sea breeze.]*
- *If not:*
  - *[The plaza fountain after closing. Ooma sits on its rim with her robe hitched up and her feet in the water, the kiosk shut behind her.]*
- *If the Leviathan is dead:*
  - **OOMA:** "Pilot. Come in. Salt water is good for the feet. Zaas would say it is good for everything, and he would be nearly right."
- *If not:*
  - **OOMA:** "Pilot. Sit. Fresh water, and far too clean. Merrow's work. It will do, until there is a sea."
- **OOMA:** "Do you know how many ports I have sold in? I stopped counting at three hundred. In every one, people ask what I really am."
- **OOMA:** "Trader. Smuggler. Spy, Garrick thinks. [happy] Garrick is never entirely wrong about anyone. That is why he is good at his job."
- **OOMA:** "Here is one true thing. It is free, so do not get used to it."
- **OOMA:** "In three hundred ports, this is the only one where people wave when my ship comes down."
- **CHOICE:**
  - **"Then keep coming down."** (+High Friendship)
    - **OOMA:** "[happy] Twice a week. The tides decide. ...I think the tides like it here."
  - **"You still haven't told me who you are."**
    - **OOMA:** "No. And still you came. [sad] Let us leave it there, pilot."
    - *(-20 friendship with Ooma)*
- **OOMA:** "One more thing. When you find my ship out past the lamp-posts, you pay what Bram pays. An old friend's price."
- *[Perk: Old Friend's Price (20% off everything at Ooma's ship)]*
- **OOMA:** "And pilot. If anyone ever comes asking about me, anyone in a uniform, you have never heard of me."

---

## Still open

- **What she is.** Deliberately unanswered (Zachary). If the main story ever needs her to be something (a Terran informant, a Collective courier, a smuggler with a conscience), 4's ship names, 6's Terran bulletin and the false bottom are the threads to pull.
- **What's under the false bottom in 6, and what chirps under the cloth in 2.** Nothing says yet.
- **Her station stall** isn't one of upstream's shops yet (`scripts/shop_data.gd`; the shop proposal has her rotating 3–4 items each visit). Her catalogue (the side arc's 8) works through talking to her.
- **Art** (on the Art Fix List): her sea-green crate with the shell-shaped lock (6), and her ship on the West Terminal's landing pad through the window (4).
