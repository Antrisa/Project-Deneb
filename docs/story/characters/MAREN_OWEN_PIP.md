# Maren, Owen & Pip: the family's side arc (24 Nov 2026)

**The family's story (Zachary, 24 Nov):** Pip's parents are dead. Their freighter's drive failed between stations in the Neutral Zone three years ago: "nobodys fault bad things happen somtimes." Pip knows they died, but not how. *(Claude's placeholders: his father is Maren and Owen's son **Tam**, his mother **Ines**, a pilot; the ship was the **Kestrel**; Pip was with his grandparents for that one run; Maren and Owen brought him to the Landing afterwards, for somewhere quiet, which is why the doctor "came here to retire".)* This replaces the old outline, where his parents were alive in Collective space (thread C, Decision 7).

**Two scenes** (side arcs are 2–3 scenes). All three need the hearts (`"who": "Maren", "with": ["Owen", "Pip"]`). Each of them also has an arc of their own ([MAREN.md](MAREN.md), [OWEN.md](OWEN.md), [PIP.md](PIP.md)), which carry the rewards.

- 4: Sunday dinner at their flat, and the photo on the shelf.
- 6: the anniversary, in the West Terminal's star dome. Pip asks how, and they tell him: a little part in the drive failed; nobody's fault; bad things happen sometimes. Three lanterns at the glass.

**What's whose:** the background is Zachary's ("nobodys fault bad things happen somtimes" is his, in Maren's words); the scenes and lines are Claude's drafts. Right answers give +60 to Maren (and to Owen and Pip where the scene says).

**Flags:** `family_dinner` (4), `family_lanterns` (6).

## In the game (24 Nov)

Both are playable cutscenes (`family_4`, `family_6`). The lanterns are the code-drawn fireflies (`scripts/scene_fx.gd`) until there's art. Not run in Godot yet.

- **Letter:** the morning after 6, "Green stars", from Pip.

---

## ♥4 Sunday Dinner

**Trigger:** Their flat, Sunday 19:15–20:45. *(Claude)*

- *[Maren and Owen's flat, Sunday dinner. Owen has cooked, which Maren says is brave of him. There's a place set for you.]*
- **PIP:** "[happy] You sit there. That's the guest chair. It wobbles. That's how you know it's for guests."
- **OWEN:** "[happy] Stew. Of a sort. The sort is mostly hope."
- **PIP:** "Dad could whistle with two fingers. Really loud. I can do it with one finger."
- *[Pip demonstrates. It is mostly air.]*
- **MAREN:** "[happy] He could. Loudly. On ships with very thin walls. The captain made a rule about it."
- **OWEN:** "The Tam Rule. It's still in the regulations of a freighter somewhere."
- **PIP:** "Do you want to see them? Mum and Dad? There's a picture on the shelf. Mum's the one laughing. Dad's the one making her."
- **CHOICE:**
  - **"I'd love to see them."** (+High Friendship)
    - *[A small photo in a big frame: a woman in a flight jacket, laughing, and a man with Pip's ears pulling a face behind her.]*
    - **PIP:** "[happy] That's them. That's on the Kestrel. Grandad says the green behind them is a nebula."
    - *(+60 friendship with Owen)*
    - *(+60 friendship with Pip)*
  - **"Maybe after dinner."**
    - **PIP:** "[sad] Oh. ...Okay. After dinner."
    - *[After dinner, Pip has forgotten. You don't think Maren has.]*

---

## ♥6 Lanterns

**Trigger:** The West Terminal's star dome, 19:30–21:30, after 4. *(Claude)*

- *[The West Terminal's little star dome, on a quiet evening. Three years ago today. Maren, Owen and Pip each hold a paper lantern with a light inside.]*
- **OWEN:** "[sad] Thank you for coming. Pip asked for you. So did we."
- **PIP:** "Gran. Grandad. ...Nine is older. Will you tell me how?"
- **MAREN:** "[sad] ...Yes. It's time. Your mum and dad's ship had a drive, like every ship. One day, between stations, a little part in it failed."
- **MAREN:** "It wasn't anybody's fault. Not theirs. Not the ship's. Not yours. Never yours. Bad things happen sometimes."
- **OWEN:** "[sad] Their last message said they'd be home for your birthday, and that the stars there were green. I've kept it for you. Whenever you want it."
- **PIP:** "[sad] ...Green stars."
- **CHOICE:**
  - **"Kneel down beside him."** (+High Friendship)
    - *[You kneel beside him. He leans into your shoulder, the way you'd lean on a wall you trust.]*
    - *(+60 friendship with Pip)*
  - **"It's all right to be sad, Pip."** (+High Friendship)
    - **PIP:** "[sad] I know. Gran says sad is just love with nowhere to go."
    - *(+60 friendship with Pip)*
  - **"Hey, look, a shooting star!"**
    - **PIP:** "[sad] ...I don't want a star right now."
    - *(-20 friendship with Pip)*
- *[Three lanterns lift towards the glass and hang there under the stars, glowing, as if the stars had come a little closer.]*
- **PIP:** "[happy] Bye, Mum. Bye, Dad. I'm going to check the drive. Every time."
- *[The next morning: a letter (`pip_lanterns`, in [MAIL.md](../MAIL.md))]*
