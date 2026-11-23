# Rusk: heart events and his week (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **He has his own arc** as well as the side arc he shares with Vzz'ket: see [`VZZKET_RUSK.md`](VZZKET_RUSK.md) for the side arc.
- **He is not Saffi's uncle**, "but can be a figure in their lives": he has turned up for every birthday until nobody could tell the difference. Kit calls him Uncle Rusk anyway.
- **His 8 gives you a special seed**: you grow it, plant the grapes again for more vines, or ferment them, and the wine sells for a lot.
- **Claude's, accepted:** his late wife Ilsa and her sign in his sea chest; the places and the rest of the arc.

**The vine (in the game):** Rusk gives you 3 **Nebula grape seeds** (Ilsa's vine; the crop already had art). They're ready in 8 watered days and fruit again every 3. **Nebula grapes** plant again like seeds, sell to Bram for 45, or go to **Rusk's cask**: bring him five or more and he ferments them, one bottle of **Nebula wine** for every five, ready in three days. Bram pays 350 a bottle. (`main.gd _rusk_cask_talk()`; it doesn't use up one of the day's chats. The Fermenter in the economy plan could do the same at home later.)

**The arc:** the barman whose tall tales cover what he won't say.
- 2: a proper counter, lights that stay on, and a sign.
- 4: Uncle Rusk tells Kit a tall tale, and tells you the true one.
- 6: Ilsa's sign, and forty years of everyone's stories but his.
- 8: a new ledger with your story on the first page, and Ilsa's vine.

**What's whose:** the decisions above are Zachary's; the scenes and every line are drafts by Claude. Right answers give +60 (High Friendship); wrong ones −20. He's platonic, so he caps at 8 hearts.

**Flags this arc sets:** `rusk_lights` (2), `rusk_tail` (4), `rusk_sea_chest` (6), `rusk_first_page` (8, which opens his cask). 8 also gives 3 `nebula_grape_seeds`.

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where he goes |
|---|---|
| Tuesday to Sunday (unchanged) | Behind the counter from 07:00; dinner; the bar again 18:50; bed 23:55 |
| Monday (his morning off: the bar opens at 18:00) | A soak at the bath house 09:30; lunch by the fountain with Saffi and Kit; Bram's in the afternoon; dinner; the bar from 18:00 |

A whole day shut would have left Job, Freya, Garrick and Bram at a dark bar, so it's a morning off. The calendar lists Monday as his day off, and he has Monday day lines.

---

## In the game (23 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`rusk_2` to `rusk_8`, after Vzz'ket's). Not run in Godot yet.

- **His heart-event sheet** is `art/npc_rusk_event.png`; he also uses his pouring rows.
- **New items:** `nebula_grape_seeds`, `nebula_grape`, `nebula_wine` (stand-in icons 53–55 in `art/items.png`), and the crop `nebula_grape` (`main.gd CROPS`, art `art/farm/crops/nebula_grape.png`).
- **Not in yet:** Ilsa's sign and the cask as art; the bar's repair (2's lamp could become its first step).

---

## ♥2 Lights That Stay On

**Trigger:** the bar, 07:00–10:00, any day but Monday, with Rusk at 2 hearts.

- *[Rusk's bar in the morning, chairs still up on the tables. The lamp over the counter sputters, sparks and goes out.]*
- *[Rusk is halfway up a stepladder with a screwdriver in his teeth.]*
- **RUSK:** "[happy] Ah! Hold the ladder, would you? Not the left leg. The left leg is decorative."
- **RUSK:** "Forty years behind bars, and I've never had all three at once."
- **RUSK:** "A proper counter. Lights that stay on. And a sign. Two out of three, once, on Halden's Rest. The roof fell in."
- **CHOICE:**
  - **"Hand me the pliers. Let's fix it properly."** (+High Friendship)
    - *[You find the frayed wire behind the shade, and Rusk wraps it while you hold the light steady.]*
    - *[The lamp comes on, and stays on. Warm light across the whole counter.]*
    - **RUSK:** "[happy] One out of three! Before breakfast! Pilot, you've ruined me for other helpers."
  - **"Why bother? The whole place is a ruin."**
    - **RUSK:** "[sad] Ruins are where I've always done my best work."
    - *[The lamp sputters and dies again. Rusk climbs down without another word and goes to find a new fuse.]*
    - *(-20 friendship with Rusk)*

## ♥4 Uncle Rusk

**Trigger:** the plaza on a Monday, 11:45–13:30, after 2: his lunch with Saffi and Kit by the fountain.

- *[Monday lunch by the fountain. Rusk, Saffi and Kit share a basket of Jasper's sandwiches on the fountain's edge.]*
- **KIT:** "[happy] Uncle Rusk! Do the one about your tail! The tip of your tail!"
- **RUSK:** "[happy] Ah. The Battle of the Crab Nebula. Pirates on every side, and a space whale the size of a moon."
- **RUSK:** "And me with nothing but a bottle of brandy and a very strong opinion."
- **SAFFI:** "[happy] Last week it was a duel with a Junta admiral."
- **RUSK:** "[happy] It was both. Busy week."
- **SAFFI:** "Come on, Kit. Hands washed before Ooma's stall or there's no stall."
- *[When they've gone, Rusk lowers his voice.]*
- **RUSK:** "Third bar. Halden's Rest. Kitchen fire, two in the morning, and a kid asleep in the back room."
- **RUSK:** "Got him out. Left the tip of my tail in the doorframe."
- **RUSK:** "[sad] Tell it true and they ask about the bar. Then the one before it. Then about her. The whale's simpler."
- **CHOICE:**
  - **"The true one's better than the whale."** (+High Friendship)
    - **RUSK:** "[bashful] ...Don't you tell Kit. He'd be heartbroken it wasn't a whale."
  - **"So it was all a lie?"**
    - **RUSK:** "[sad] All my stories are lies, pilot. That's what makes them safe to tell."
    - *(-20 friendship with Rusk)*

## ♥6 The Sea Chest

**Trigger:** the bar, 23:00–midnight, after 4. His room behind the bar.

- *[Rusk's room behind the bar, after closing. His sea chest stands open.]*
- *[He kneels beside it with something long and flat wrapped in sailcloth.]*
- **RUSK:** "Come in. Mind the ledgers. They bite less than the stool, but only just."
- *[He folds back the sailcloth. A painted wooden sign, its edges scorched: ILSA'S.]*
- **RUSK:** "My first real bar. Hers, really. I poured. She grew nebula grapes over the door and made the wine in the cellar."
- **RUSK:** "[sad] The war took the bar. Time took her. I took the sign, and a few bottles of her wine."
- **RUSK:** "That's the Secret Reserve. There's not much of it left."
- **RUSK:** "Forty years of ledgers on that shelf. Every story anyone ever told me across a bar."
- **RUSK:** "Not one page of mine."
- **CHOICE:**
  - **"Then tell me about her."** (+High Friendship)
    - **RUSK:** "[happy] She laughed at my jokes. Only the bad ones. The good ones she said she'd heard before."
    - **RUSK:** "...There. That's a page."
  - **"Maybe it's time to let it go."**
    - **RUSK:** "[sad] I've let go of everything else, pilot. I'll keep the sign."
    - *(-20 friendship with Rusk)*
- *[He doesn't put the sign back in the chest. He props it against the armchair, where he can see it from the bed.]*

## ♥8 The First Page

**Trigger:** the plaza, 23:00–midnight, with Rusk at 8 hearts: the bar's front step at closing. Reward: Ilsa's vine (3 Nebula grape seeds) and his cask.

- *[Closing time on the promenade. Rusk sits on the bar's front step with two ledgers: one fat and battered, one new.]*
- **RUSK:** "Forty years in this one. Every story anyone ever told me, except mine. Then I told you mine. So it's finished."
- *[He closes the old ledger and opens the new one on his knee. The first page is blank.]*
- **RUSK:** "New bar, new book. And a new book needs a first page. I thought it should be yours. Tell me something true."
- **CHOICE:**
  - **"[Tell him about the crash, and the moon, and staying]"** (+High Friendship)
    - *[You tell him. He writes it down in a slow, square hand, and doesn't add a single whale.]*
    - **RUSK:** "[happy] 'The pilot fell through the roof, and stayed for supper.' ...It's a start."
  - **"Make something up. Make it exciting."**
    - **RUSK:** "[sad] ...I could. I've made up plenty. I was hoping for a true one."
    - *[In the end you tell him about the crash anyway. He writes it down, but he doesn't smile.]*
    - *(-20 friendship with Rusk)*
- **RUSK:** "One more thing. Seeds from Ilsa's vine. I've carried them forty years and never had dirt to put them in."
- **RUSK:** "Then somebody fell through the roof and started digging."
- **RUSK:** "Grow them. Plant the grapes again for more vines, or bring me five and I'll put them in the cask."
- **RUSK:** "Her wine was the Secret Reserve. Let's not let it run out."
- *[Rusk gives you 3 Nebula grape seeds]*
- *[New: bring Rusk five Nebula grapes and he'll make a bottle of Nebula wine]*
