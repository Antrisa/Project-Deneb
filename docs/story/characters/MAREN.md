# Maren: heart events (24 Nov 2026)

**The family's story (Zachary, 24 Nov):** Pip's parents are dead. Their freighter's drive failed between stations in the Neutral Zone three years ago: "nobodys fault bad things happen somtimes." Pip knows they died, but not how. *(Claude's placeholders: his father is Maren and Owen's son **Tam**, his mother **Ines**, a pilot; the ship was the **Kestrel**; Pip was with his grandparents for that one run; Maren and Owen brought him to the Landing afterwards, for somewhere quiet, which is why the doctor "came here to retire".)* This replaces the old outline, where his parents were alive in Collective space (thread C, Decision 7).

**Decided with Zachary, 24 Nov:** an arc each for Maren, Owen and Pip, and a two-scene family side arc ([MAREN_OWEN_PIP.md](MAREN_OWEN_PIP.md)). Her days off (Thursday and Sunday, staggered with Quill's) were settled on 23 Nov. Her 8's reward is the NPC Master's **Advanced Med-Stims**: medpacks heal twice as much.

**The arc:** the doctor who came here to stop leaving.
- 2: house calls in the East Complex, with you carrying the bag. She didn't really come to retire.
- 4: her Thursday off, and the first hot cup of tea in thirty years. Tam used to bring her tea.
- 6: Pip wants to go up the Survey lift on his own.
- 8: the old ship's med-stim recipe, and why she stays.

**What's whose:** the reward and the old outline of 6 ("Letting Go") are the NPC Master's; the background above is Zachary's; the scenes and every line are drafts by Claude. Right answers +60, middle ones +30, wrong ones −20 (in 6, the wrong one costs Pip's friendship instead, and in 4 it costs the letter).

**Flags:** `maren_house_calls` (2), `maren_hot_tea` (4), `maren_lets_go` (6: Pip's Saturday afternoons are his own from now on), `maren_home` and the perk `perk_advanced_med_stims` (8).

## In the game (24 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`maren_2` to `maren_8`), with her new heart-event sheet (`art/npc_maren_event.png`, `tools/events.py`) and her action sheet (treat, eat). Not run in Godot yet.

- **Advanced Med-Stims:** `main.gd _eat` doubles a medpack's healing with `perk_advanced_med_stims`.
- **Letter:** the morning after 4, "Hot tea" (not if you told her it was only tea).
- **To test:** in a debug build, **F12** plays the next event in order, **Ctrl+F12** all of them in a row.

---

## ♥2 House Calls

**Trigger:** The East Complex, 19:30–21:15, not on her days off. With Job on his porch. *(Claude)*

- *[The East Complex, after dinner. Maren walks fast for someone carrying two bags. She has handed you the heavier one.]*
- **MAREN:** "House calls. The clinic shuts at seven. The patients don't. First, Job's back."
- **JOB:** "[happy] Evening, Doc."
- **MAREN:** "Sit up straight."
- **JOB:** "I am sitting up straight."
- **MAREN:** "Sit up straighter."
- *[She runs two fingers down his spine as if she's reading it.]*
- **MAREN:** "You lifted something you shouldn't have."
- **JOB:** "[sad] ...A beam. Only a little beam."
- **MAREN:** "Of course it was. A stim tonight, a hot soak tomorrow, and no mining for a day."
- **MAREN:** "[angry] No mining, Job. I can hear you thinking about it."
- **MAREN:** "Thirty years a ship's surgeon. I've stitched people up in nine systems: in corridors, in cargo holds, once in a lift."
- **MAREN:** "I came here to retire. [happy] Everyone laughs when I say that. You're allowed to."
- **CHOICE:**
  - **"You didn't really come here to retire, did you?"** (+High Friendship)
    - **MAREN:** "[sad] ...No. We came for Pip. After his mum and dad, we wanted somewhere quiet. Somewhere nothing happens."
    - **MAREN:** "[happy] Then you fell out of the sky."
  - **"Retirement suits you."** (+Friendship)
    - **MAREN:** "[happy] Liar. I look exhausted. But thank you."
  - **"Let Quill do the house calls."**
    - **MAREN:** "[angry] Quill has the clinic. The house calls are mine. People tell you things on their own doorstep."
    - *(-20 friendship with Maren)*
- **MAREN:** "Next: Tobbin's wrist. Then Nub has a splinter he's very proud of. Keep up."

---

## ♥4 A Hot Cup of Tea

**Trigger:** The common room, Thursday (her day off) 12:30–15:00, after 2. With Pip, Quill and Job, briefly. *(Claude)*

- *[The common room, on Maren's Thursday off. A kettle is just coming to the boil, and Maren is watching it like a patient.]*
- **MAREN:** "[happy] Shh. Don't move. It's nearly there."
- **MAREN:** "Thirty years, and I've never once finished a cup of tea while it was hot. Today I am going to."
- *[She pours. Steam curls off the cup. Somewhere outside, running feet.]*
- **PIP:** "Gran! Gran, guess what Kit..."
- *[You get to Pip first, turn him round by the shoulders, and point him at the fountain.]*
- **QUILL:** "Maren, the bandage order..."
- **QUILL:** "[surprised] Ah. Tea. Understood. Retreating."
- *[Job takes one look at your face, holds up both hands, and backs out again.]*
- **MAREN:** "[happy] Hot. ...It's hot."
- **MAREN:** "Our Tam used to bring me tea on the ship, every morning between patients. By the time I got to it, it was always cold."
- **MAREN:** "[sad] He made terrible tea. On time, every day."
- **CHOICE:**
  - **"Tell me about him."** (+High Friendship)
    - **MAREN:** "[happy] He took a toaster apart at nine and put it back with two parts left over. It worked better. Pip has his ears, and his hands."
    - **MAREN:** "[sad] ...Thank you for asking. People don't. They think it hurts. It hurts more when nobody says his name."
  - **"Drink your tea. I'll keep watch."** (+Friendship)
    - **MAREN:** "[happy] Yes, doctor."
  - **"It's only tea."**
    - **MAREN:** "[sad] ...Yes. Only tea."
    - *(-20 friendship with Maren)*
- *[The next morning: a letter (`maren_tea`, in [MAIL.md](../MAIL.md))]*

---

## ♥6 Letting Go

**Trigger:** The corridor to the Survey lift, Saturday or Sunday 10:00–12:00, after 4. With Pip. *(The NPC Master's title; the scene is Claude's: Artie's 4 already puts Pip in the Scouts.)*

- *[The corridor to the Survey lift. Pip stands at the lift doors with his hand on the button. Maren stands behind him with her hand on Pip.]*
- **PIP:** "[happy] I'm going up to the Survey Level. By myself. S.A.R.A. says she'll meet me at the top. Gran's deciding."
- **MAREN:** "Gran is deciding."
- **MAREN:** "His father went up his first lift alone at nine, too. Then his first ship at twenty. Then..."
- **MAREN:** "[sad] You keep a child safe by keeping him close. And then one day, keeping him close is the thing that hurts him."
- **CHOICE:**
  - **"Let him go. S.A.R.A. watches every floor."** (+High Friendship)
    - **MAREN:** "...Every floor. Yes. She does."
    - **MAREN:** "Go on, then. Straight up, straight to S.A.R.A., and back by lunch."
    - **PIP:** "[happy] Straight up, straight to S.A.R.A., back by lunch!"
    - *[The lift doors close. Maren lets out a breath she seems to have been holding for three years.]*
    - **MAREN:** "[happy] Well. He's going to be insufferable now."
  - **"Go up with him, just this once."**
    - **PIP:** "[angry] Gran! That's not by myself!"
    - **MAREN:** "[sad] ...Next time. I'll be ready next Saturday."
    - *[She is. The Saturday after, Pip goes up on his own, and tells everyone about it for a week.]*
    - *(-20 friendship with Pip)*

---

## ♥8 Med-Stims

**Trigger:** The Medbay after hours, 19:30–21:15, not on her days off, after 6. With Quill. Reward: Advanced Med-Stims. *(Claude)*

- *[The Medbay after hours. Maren has laid out vials, a burner and a very old textbook. Quill is taking notes about the notes.]*
- **MAREN:** "Good, you're here. Stand there. Don't touch the blue one."
- **MAREN:** "Med-stims. The old ship's recipe: twice the kick of a medpack, half the shakes. I've never taught it to anyone. Nobody stayed long enough."
- **QUILL:** "[surprised] You're adding the spores now? The journal says after."
- **MAREN:** "The journal was written by a man who'd never been shot at. Now."
- **MAREN:** "[happy] There. Every medpack you carry, I'll top up the old way."
- *[Perk: Advanced Med-Stims (medpacks heal twice as much)]*
- **MAREN:** "I told you I came here to retire. I didn't. I came here to stop leaving."
- **MAREN:** "Thirty years of ports. You patch someone up, they fly off, and you never learn how it ends."
- **MAREN:** "[sad] Here, I'll learn how it ends. I'm not sure I'm brave enough for that. I'm doing it anyway."
- **CHOICE:**
  - **"Welcome home, Maren."** (+High Friendship)
    - **MAREN:** "[happy] ...Home. Don't tell Owen I said it first. He's been waiting three years to say it."
  - **"Pip's lucky to have you."** (+Friendship)
    - **MAREN:** "[happy] Pip's lucky to have a whole station. I'm the part that makes him wear a coat."
  - **"So you're never retiring?"**
    - **MAREN:** "[angry] I'll retire when people stop falling out of the sky. Present company included."
    - *(-20 friendship with Maren)*
- **QUILL:** "[happy] I've written that down. 'Home.' Underlined twice."
