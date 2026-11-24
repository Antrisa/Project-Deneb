# Nub: heart events and his week (24 Nov 2026)

**Decided with Zachary, 24 Nov:** Tobbin's 4, 6 and 8 **wait for the garden dome's trees** ("wait for trees"), an exception to "8s never wait", like Zaas's 6 and 8 waiting for the Leviathan. His 8 is **a real chair and its crafting recipe**, and **he sells a bunch of furniture in his shop**. **Tobbin's shop is shut on Sundays; Merrow has the weekend off after her 8.** Claude's first suggestions for the rest, taken: **an arc each and a two-scene side arc** ([TOBBIN_MERROW_NUB.md](TOBBIN_MERROW_NUB.md)); **Nub's 8 is a framed drawing** you set down at home; **Hydro-Boost** as the NPC Master has it (hydroponic beds grow 20% faster). This closes the 5.8 gap (the 8 ran on Merrow's hearts but every scene was Tobbin's) and its clash (where the wood comes from: the garden dome's oldest tree, pruned).

**The arc:** a small Moogli who draws everything, so it's remembered.
- 2: his drawing of you, the tall one with the sad ship. The ship's sad because it fell.
- 4: the fountain's edge. Kit jumps off it again and again; Nub can't, yet.
- 6: he has taped a drawing under every label on the museum's south cases. Tar'Besh makes him Junior Curator (Fridays, with pins).
- 8: the next drawing, framed: the whole Landing under the dome, a tree that isn't there yet, and your ship smiling. Tobbin made the frame from the plastic chair that broke.

**What's whose:** the reward's shape (a framed drawing) was Claude's suggestion, taken; the scenes and lines are Claude's drafts. Right answers +60, middle +30, wrong −20.

**Flags:** `nub_drew_you` (2), `nub_jumped` (4), `nub_junior_curator` (6), `nub_framed` (8).

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What he does |
|---|---|
| Weekdays (unchanged) | Lessons in the library; the plaza; dinner; home by half past eight. Monday afternoons and seasonal outings with the Scouts, once Artie starts them. |
| **Friday, after his 6** (`nub_junior_curator`) | Lessons, then the museum all afternoon, drawing for Tar'Besh. |
| **Sunday** | Drawing at his desk at home in the morning; the fountain in the afternoon; dinner; home. |

- **Day lines** for Sunday, and Friday once he's Junior Curator (`npc_data.gd DAY_LINES`).

## In the game (24 Nov)

All four are playable cutscenes (`nub_2` to `nub_8`), with his new heart-event sheet (`art/npc_nub_event.png`) and his action sheet (draw, play). Not run in Godot yet.

- **Nub's drawing** (`nub_drawing`, icon 138, prop `art/lunar/nub_drawing.png`, stand-ins by Claude): set it down at home from the hotbar, like Pip's toy rocket (`main.gd PLACEABLE`, `"decor"`).
- **Letter:** the morning after 6, "JUNIOR CURATOR", with a bug shell (chitin) "for your museum".

---

## ♥2 I Drew You

**Trigger:** The plaza, 12:30–17:00. *(Claude; his line "I drew you" was already in his repeat lines.)*

- *[Nub is lying on his tummy on the plaza floor, drawing with great concentration and the tip of his tongue out.]*
- **NUB:** "[happy] It's you! I'm drawing you! Don't look! ...Okay, look."
- *[A stick person with very long arms stands by a ship. The ship has a sad face and orange scribble coming out of it. Everyone is smiling but the ship.]*
- **NUB:** "That's you. You're the tall one. That's your ship. It's on fire, because Pip said."
- **CHOICE:**
  - **"It's wonderful, Nub."** (+High Friendship)
    - **NUB:** "[happy] I know! Dad says I'm the best drawer on the whole moon."
  - **"Why is the ship sad?"** (+Friendship)
    - **NUB:** "Because it fell down. Falling's sad. [happy] Then you fixed it, so it's happy. That's the next drawing. I haven't done it yet."
  - **"I don't look like that."**
    - **NUB:** "[sad] You do in the drawing."
    - *(-20 friendship with Nub)*
- **NUB:** "You can have it. Every drawing's for somebody, and this one's yours. [happy] Don't fold it. Folding is bad for drawings."
- *[Nub's drawing goes up on your wall at home]*

---

## ♥4 The Fountain Edge

**Trigger:** The plaza fountain, 15:00–17:00, Monday to Saturday, after 2. With Kit and Merrow. *(Claude; Kit's line "I'm teaching" was already his.)*

- *[Kit is jumping off the fountain's edge, again and again, landing like a cat. Nub stands on the edge with his toes curled over it.]*
- **KIT:** "[happy] Your go, Nub! It's easy! You just go!"
- **NUB:** "[sad] It's very high. It's higher when you're on it. ...Will you do something?"
- **CHOICE:**
  - **"Jump with him."** (+High Friendship)
    - *[You step up beside him. One... two...]*
    - *[...three. You land together. Nub lands on his bottom, but he lands.]*
    - **NUB:** "[happy] I JUMPED! Kit! KIT! I jumped off the fountain edge! A real jump!"
    - **KIT:** "[happy] That was a real jump."
    - **MERROW:** "[happy] I saw that! I see everything from over there. Even the bits I'm not meant to."
  - **"Hold out your hand."** (+Friendship)
    - *[You hold out a hand. He takes it, squeezes very hard, and jumps.]*
    - **NUB:** "[happy] I did it! I mostly did it. You did the hand bit."
    - **MERROW:** "[happy] That's my boy. Both feet off the ground. That counts."
  - **"Bet you can't!"**
    - **NUB:** "[angry] I CAN!"
    - *[He jumps. Backwards. Into the fountain.]*
    - **MERROW:** "[angry] Nub! That's twice this week! Out. Out, and drip on someone else."
    - *(-20 friendship with Nub)*
- **KIT:** "[happy] Tomorrow I'm teaching him the twisty one."

---

## ♥6 Junior Curator

**Trigger:** The museum, 13:00–16:30, Monday to Saturday, after 4. With Tar'Besh. *(Claude)*

- *[The museum, quiet as ever. Under every label on the south cases, someone has taped a drawing. Nub is taping up another one, very carefully.]*
- **NUB:** "[happy] Shh! It's a museum. I'm doing labels. The real labels are only words. Words don't show you anything."
- *[Under 'Star map on bone' is a bone with stars on. Under 'Pirate cutlass' is a sword with a frowning face. Its label says BAD SWORD.]*
- **TAR'BESH:** "Young Nub. There is tape on my display cases."
- **NUB:** "[sad] ...It's good tape. It comes off."
- **TAR'BESH:** "{name}. You are a sensible person, now and then. What would you have me do?"
- **CHOICE:**
  - **"His drawings are better than the labels."** (+High Friendship)
    - **TAR'BESH:** "[happy] ...They are, rather. 'BAD SWORD.' I wrote four hundred words on that cutlass. He has said it in two."
  - **"Nub, next time, ask first."** (+Friendship)
    - **NUB:** "[sad] Okay. ...Can I ask now?"
    - **TAR'BESH:** "[happy] You may."
  - **"Take them down, Nub."**
    - **NUB:** "[sad] Okay."
    - **TAR'BESH:** "Hm. Wait. Leave them a moment, Nub. I have not finished looking."
    - *(-20 friendship with Nub)*
- **TAR'BESH:** "A museum is a way of remembering. A child remembering is the best kind there is. [happy] They stay. In frames. With proper credit."
- **TAR'BESH:** "Junior Curator Nub: one drawing a week, on Fridays, approved by the senior curator. Tape is forbidden. I will supply pins."
- **NUB:** "[happy] JUNIOR CURATOR! I have to tell Mum! I have to tell DAD!"
- **TAR'BESH:** "[happy] My first hire. The Temple would be appalled. I find I do not mind."
- *[The next morning: a letter (`nub_curator`, in [MAIL.md](../MAIL.md))]*

---

## ♥8 Framed

**Trigger:** Their flat, 18:45–20:15, after 6. With Tobbin and Merrow. Reward: Nub's drawing. *(Claude)*

- *[Their flat. Nub stands in the middle of the room holding something flat and square behind his back, vibrating slightly.]*
- **NUB:** "[happy] Close your eyes! ...Are they closed? They're not closed. Okay. Open them."
- *[A drawing in a frame. The whole Landing under the dome: Mum at the fountain, Dad with a chair, Pip, Kit, a tree that isn't there yet.]*
- *[And you, the tall one, beside a ship that's smiling now.]*
- **NUB:** "It's the next drawing. The ship's happy because you fixed it. [happy] Dad made the frame. Out of the chair that broke."
- **TOBBIN:** "[happy] Every bad chair is a good frame, waiting."
- **CHOICE:**
  - **"I'll hang it where I see it every day."** (+High Friendship)
    - **NUB:** "[happy] By your bed! So it's the first thing! Like Dad's ship!"
  - **"Is that tree in the dome?"** (+Friendship)
    - **NUB:** "Not yet. Mum says one day. [happy] I drew it now so it knows where to go."
  - **"You could sell these, Nub."**
    - **NUB:** "[sad] ...You don't sell presents."
    - **MERROW:** "[angry] He's right, {name}."
    - *(-20 friendship with Nub)*
- *[+ Nub's drawing (set it down at home)]*
- **MERROW:** "He did eleven of these this week. That one's the best. He made us promise not to look. [happy] We looked."
