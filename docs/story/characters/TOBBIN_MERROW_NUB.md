# Tobbin, Merrow & Nub: the family's side arc (24 Nov 2026)

**Decided with Zachary, 24 Nov:** Tobbin's 4, 6 and 8 **wait for the garden dome's trees** ("wait for trees"), an exception to "8s never wait", like Zaas's 6 and 8 waiting for the Leviathan. His 8 is **a real chair and its crafting recipe**, and **he sells a bunch of furniture in his shop**. **Tobbin's shop is shut on Sundays; Merrow has the weekend off after her 8.** Claude's first suggestions for the rest, taken: **an arc each and a two-scene side arc** ([TOBBIN_MERROW_NUB.md](TOBBIN_MERROW_NUB.md)); **Nub's 8 is a framed drawing** you set down at home; **Hydro-Boost** as the NPC Master has it (hydroponic beds grow 20% faster). This closes the 5.8 gap (the 8 ran on Merrow's hearts but every scene was Tobbin's) and its clash (where the wood comes from: the garden dome's oldest tree, pruned).

**Two scenes** (side arcs are 2–3 scenes). All three need the hearts. Each of them also has an arc of their own ([TOBBIN.md](TOBBIN.md), [MERROW.md](MERROW.md), [NUB.md](NUB.md)), which carry the rewards.

- 4: bath night (Wednesdays and Saturdays). Nub hides; you find him; he'll get in if you tell him about your crash. A Moogli bath is half an hour of splashing and two hours of fur.
- 6: the first tree. Merrow has sprouted the bluebark seed Tobbin's grandmother gave him when they left Moogli Prime, eleven years in a drawer. Planted in the garden dome; until the dome's open, in the tub in their flat (it doesn't wait).

**What's whose:** the scenes and lines are Claude's drafts. Right answers give +60 to the event's resident and some to the other two.

**Flags:** `moogli_bath_night` (4), `moogli_first_tree` (6).

## In the game (24 Nov)

Both are playable cutscenes (`moogli_4` on Tobbin's hearts with Merrow and Nub, `moogli_6` on Merrow's with Tobbin and Nub). The bath's bubbles are the code-drawn ones (`scripts/scene_fx.gd`). Not run in Godot yet.

- **Letter:** the morning after 6, "Tree", from all three.

---

## ♥4 Bath Night

**Trigger:** Their flat, Wednesday or Saturday 19:15–20:30. *(Claude)*

- *[Bath night. Tobbin holds a towel. Merrow holds a sponge. Neither of them is holding Nub, which is the problem.]*
- **MERROW:** "[angry] He was here a minute ago. That child can smell a bath through two doors."
- **TOBBIN:** "{name}! You've got young eyes. Where would you hide, if you were small and against soap?"
- **CHOICE:**
  - **"Behind the sofa."** (+High Friendship)
    - *(+30 friendship with Merrow)*
    - *(+30 friendship with Nub)*
  - **"In his toy chest."** (+Friendship)
    - **MERROW:** "Checked it. Twice. He's learned."
    - *[Then you spot it: one round, guilty ear, poking up behind the sofa.]*
    - *(+15 friendship with Merrow)*
    - *(+15 friendship with Nub)*
  - **"Skip it tonight. He's fine."**
    - **MERROW:** "[angry] One night is how it starts. Then it's a week. Then he smells like the recycler."
    - *[A small, offended voice comes from behind the sofa.]*
    - *(-20 friendship with Merrow)*
- **NUB:** "[angry] No bath! I'm not dirty! I'm only floor-coloured!"
- **NUB:** "...I'll get in if you tell me about the crash. The whole crash. With the fire bit."
- *[So you tell it from the bathroom doorway, fire bits and all, while Nub sits in the tub and Merrow scrubs. It's the best audience it's ever had.]*
- **NUB:** "[happy] And then what? And THEN what?"
- *[Half an hour of splashing later, Nub is clean. Then Tobbin towels him, and his fur dries, and keeps drying, and goes up, and up...]*
- *[...until he is twice his size and perfectly round, like a dandelion with feet.]*
- **TOBBIN:** "[happy] There he is. Our little cloud."
- **MERROW:** "[happy] Every bath night. Every single one. ...Thank you, {name}. Same time next week?"

---

## ♥6 The First Tree

**Trigger:** The garden dome, Sunday 09:00–12:00, after 4; **until the dome is open, their flat** (the tub in the corner). *(Claude)*

- *If the garden dome is open:*
  - *[The garden dome, Sunday morning. Merrow kneels in the grass with a trowel. Tobbin and Nub stand over her, holding hands, very serious.]*
- *If not (their flat):*
  - *[Their flat, Sunday morning. Merrow kneels by the big tub in the corner with a trowel. Tobbin and Nub stand over her, very serious.]*
- **MERROW:** "Come and see, {name}. Quietly. It's shy."
- *[In her cupped hands: a seedling, two leaves high, its stem a soft, dusty blue.]*
- **TOBBIN:** "[love] Bluebark. From my grandmother's tree. She gave me the seed when we left Moogli Prime. Eleven years in a drawer."
- **MERROW:** "Nothing ever had the light for it. Or the soil. Or the time. [happy] Then everything did, all at once."
- **NUB:** "It's a baby tree. It's a baby chair."
- **TOBBIN:** "[happy] ...It is, isn't it?"
- **CHOICE:**
  - **"Can I help plant it?"** (+High Friendship)
    - *[Merrow lets you press the soil down round it. Nub pats it too, very gently, the way you'd pat a head.]*
    - *(+30 friendship with Tobbin)*
    - *(+30 friendship with Nub)*
  - **"How big will it get?"** (+Friendship)
    - **MERROW:** "[happy] Taller than the dome, in a hundred years. We'll worry about that in fifty."
    - *(+15 friendship with Tobbin)*
    - *(+15 friendship with Nub)*
  - **"When can it be made into chairs?"**
    - **TOBBIN:** "[shocked] {name}! Not in front of the tree!"
    - **NUB:** "[sad] Don't make the baby into a chair."
    - *(-20 friendship with Merrow)*
- *If the garden dome is open:*
- *If the garden dome is open:*
  - *[The first tree from Moogli Prime on the whole moon. It's tiny. Nub has already named it. Its name is Tree.]*
- *If not (their flat):*
  - **MERROW:** "In the tub for now. [happy] When the garden dome opens, it goes in the ground. First thing."
  - *[Nub has already named it. Its name is Tree.]*
- *[The next morning: a letter (`moogli_tree`, in [MAIL.md](../MAIL.md))]*
