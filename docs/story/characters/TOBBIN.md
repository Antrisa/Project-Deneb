# Tobbin: heart events, his shop and his week (24 Nov 2026)

**Decided with Zachary, 24 Nov:** Tobbin's 4, 6 and 8 **wait for the garden dome's trees** ("wait for trees"), an exception to "8s never wait", like Zaas's 6 and 8 waiting for the Leviathan. His 8 is **a real chair and its crafting recipe**, and **he sells a bunch of furniture in his shop**. **Tobbin's shop is shut on Sundays; Merrow has the weekend off after her 8.** Claude's first suggestions for the rest, taken: **an arc each and a two-scene side arc** ([TOBBIN_MERROW_NUB.md](TOBBIN_MERROW_NUB.md)); **Nub's 8 is a framed drawing** you set down at home; **Hydro-Boost** as the NPC Master has it (hydroponic beds grow 20% faster). This closes the 5.8 gap (the 8 ran on Merrow's hearts but every scene was Tobbin's) and its clash (where the wood comes from: the garden dome's oldest tree, pruned).

**The arc:** a furniture maker on a station that has never had a plank.
- 2: a plastic chair leg snaps in his workshop; you hold the frame while he pins it with steel. His grandmother's bluebark chairs on Moogli Prime creaked hello.
- 4: the garden dome's first pruned limb. Real wood, after eleven years. His shop sells planks from then on.
- 6: a toy starship carved from the offcut for Nub, while you keep Nub from seeing it.
- 8: the first real-wood chair, pegged and wedged the old way. It's yours, he teaches you the joints, and it creaks hello.

**What's whose:** the titles of 2, 4 and 6 and the shape of 8 (the workshop; Heirloom Real-Wood Furniture) are the NPC Master's; the reward, the waiting and the shop are Zachary's; the scenes and every line are drafts by Claude. Right answers +60, middle ones +30, wrong ones −20 (in 2 the wrong one costs 10 energy instead: you sit on the chair).

**Flags:** `tobbin_plastic` (2), `tobbin_first_wood` (4: his shop's planks), `tobbin_starship` (6), `tobbin_heirloom` and the perk `perk_heirloom_chair` (8: the recipe). 4, 6 and 8 need `east_dome`.

## His shop (in the game)

Talk to him at work (outside his workshop door) for **Tobbin's furniture** (`scripts/shop_data.gd STOCK`, `TITLES`; `main.gd SHOP_HELLO`). Shut on Sundays, like every shop on its keeper's day off.

| Item | Price | Notes |
|---|---|---|
| Guest bed | 120 | the hotel's furniture, ready-made, at about 2.5 times what it costs to craft |
| Fine guest bed | 300 | |
| Armchair | 90 | |
| Dresser | 160 | |
| Wardrobe | 230 | |
| Writing desk | 160 | |
| Bedside lamp | 75 | |
| Bookshelf | 180 | |
| Potted plant | 50 | |
| Small fern | 35 | |
| Berry rug | 110 | |
| Real wood plank | 60 | after his 4 (`tobbin_wood` in `shops.gd unlocked`); worth 40 at the crate |

## His 8's reward

- **The heirloom chair** (`heirloom_chair`): furniture you set down at home or in a hotel room (`hotel.gd FURNITURE`: comfort +0.3, decoration +0.3, more than the armchair).
- **The recipe:** 3 real-wood planks and a hide, at a manufacturing hub. Recipes can now be **taught**: a recipe with `"learn"` (a story flag) and `"teacher"` can't be crafted until the flag is set (`main.gd craft`), and the Crafting page shows "Learn from Tobbin" where the station goes (`datapad_bridge.gd _recipes`).

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What he does |
|---|---|
| Monday to Saturday (unchanged) | His workshop door from 07:00; dinner; the common room; home. |
| **Sunday (shop shut)** | His bench at home in the morning; the plaza garden after lunch, sketching; dinner; the common room; home. |
| **Sunday, once the garden dome is open** | The same, but the afternoon is under the dome's trees. |

- **Day lines** for Sunday (`npc_data.gd DAY_LINES`); the station calendar lists his Sundays off.

## In the game (24 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`tobbin_2` to `tobbin_8`), with his new heart-event sheet (`art/npc_tobbin_event.png`, `tools/events.py`) and his action sheet (build, sketch). Not run in Godot yet.

- **Letter:** the morning after 4, "Two planks", with two real-wood planks.
- **Art:** the heirloom chair, the plank icon and the chair's icon are stand-ins by Claude (`tools/dev/moogli_art.py`), on the Art Fix List.
- **To test:** in a debug build, **F12** plays the next event in order, **Ctrl+F12** all of them in a row (and opens the garden dome for the ones that need it).

---

## ♥2 Plastic and Steel

**Trigger:** His workshop, 09:00–17:00, Monday to Saturday. *(The NPC Master's title; the scene is Claude's.)*

- *[Tobbin's workshop smells of hot plastic. Something in his hands goes crack, and a chair leg skitters across the floor.]*
- **TOBBIN:** "[angry] Plastic! It bends when it should hold, and it snaps when it should bend. And steel won't bend at all. It just sulks."
- **TOBBIN:** "Oh! {name}. Mind where you sit. Nothing in here is a chair yet. Some of it never will be."
- **TOBBIN:** "On Moogli Prime my grandmother made chairs from bluebark. You sat in one and it creaked hello."
- **TOBBIN:** "[sad] These creak goodbye."
- **TOBBIN:** "Will you hold the frame? I'll put a steel pin down the leg. Steel inside, plastic outside. Like a Moogli in a spacesuit."
- **CHOICE:**
  - **"Hold it steady."** (+High Friendship)
    - *[You hold the frame while he taps the pin home. The leg holds. The chair stands on four feet, looking a little surprised.]*
    - **TOBBIN:** "[happy] It stands! It's ugly, but it stands. Ugly and standing is how most good things start."
  - **"Have you tried glue?"** (+Friendship)
    - **TOBBIN:** "[happy] Glue! I've tried four glues. I've tried tape. Once, I tried asking nicely. Hold the frame, and we'll try steel."
    - *[The pin goes in. The leg holds. The chair stands, a little crooked, as if it's listening.]*
  - **"Just sit on it and see."**
    - **TOBBIN:** "[shocked] Wait, don't..."
    - *[You sit. The chair doesn't. You meet the floor of Tobbin's workshop, and the floor wins.]*
    - **TOBBIN:** "[sad] ...That's three this week. Are you hurt? Good. Hold the next one for me, please. Don't sit on it."
    - *(-10 energy)*
- **TOBBIN:** "Real wood is alive, even after it's cut. It moves with the air. It forgives you. This station has never had a single plank."
- **TOBBIN:** "[love] If that garden dome ever grows a tree, I'm going to ask it, very politely, for a branch."
- **TOBBIN:** "[happy] Till then, plastic and steel. If you need furniture, I'm outside my door most days. It's honest work, at least."

---

## ♥4 First Real Wood

**Trigger:** The garden dome, Sunday 08:00–13:00, after 2, **once the dome is open**. With Merrow. *(The NPC Master's title; the scene is Claude's: the wood is a pruned limb, not the East orchard's fruit trees.)*

- *[The garden dome, early on a Sunday. Merrow is at the oldest tree with a pruning saw. Tobbin stands beneath it, holding his breath.]*
- **MERROW:** "This limb's been rubbing the glass since before we came. It comes off, or the panel cracks."
- **TOBBIN:** "{name}! Don't talk. Don't breathe. She's cutting a branch off a tree. A real branch. Off a real tree."
- *[A long, pale limb comes down with a soft whump and lies in the grass, leaves and all.]*
- **MERROW:** "[happy] There, love. I asked the tree. It said yes."
- **TOBBIN:** "[love] ...It's warm. Still warm from the lamps. Smell it, {name}. That's what a forest smells like. Eleven years. I'd forgotten."
- **CHOICE:**
  - **"Kneel and smell it."** (+High Friendship)
    - *[Green and sharp and sweet. Under the station's recycled air, it smells like somewhere else.]*
    - **TOBBIN:** "[happy] You see? Somewhere else. That's what wood is. A piece of somewhere else you can hold."
  - **"What will you make first?"** (+Friendship)
    - **TOBBIN:** "A chair. No, a spoon, to practise. No... [happy] I don't know! I've never had to choose before."
  - **"It's just a stick."**
    - **TOBBIN:** "[sad] ...Yes. Just a stick. And a star is just a light."
    - *(-20 friendship with Tobbin)*
- **MERROW:** "One limb a season, Tob. Pruning, not felling. The trees come first."
- **TOBBIN:** "One limb a season. I'll make every splinter count."
- **TOBBIN:** "[happy] And what I can't use, I'll sell. Planks, {name}! Real planks, at my door."
- *[The next morning: a letter (`tobbin_planks`, in [MAIL.md](../MAIL.md))]*

---

## ♥6 A Wooden Starship

**Trigger:** Their flat, 19:30–20:30, after 4 (so once the dome is open). With Nub. *(The NPC Master's title; the scene is Claude's.)*

- *[Their flat, after Nub's bedtime. Tobbin sits at his home bench with a pale block of wood and a very small knife. Shavings curl round his feet.]*
- **TOBBIN:** "Shh. Come and look. Quietly. The first wood had an offcut, and an offcut is a promise."
- *[It's a starship. Fat-bellied, with stubby wings and a little round cockpit. He is carving the hull plates one line at a time.]*
- **TOBBIN:** "My father carved me a boat when I was Nub's size. We had rivers on Moogli Prime. [sad] Nub's never seen a river."
- **TOBBIN:** "[happy] But he's seen ships. He's seen yours. On fire, he says."
- **NUB:** "Daaad? I can't sleep. What's that? Is that a... what is that?"
- *[Tobbin goes very still, the way only a parent hiding a present can.]*
- **CHOICE:**
  - **"Nub! Quick, draw me a picture of your dad!"** (+High Friendship)
    - **NUB:** "[happy] Now? It's NIGHT. ...Okay! Don't move, Dad. You have to stay exactly like that."
    - **TOBBIN:** "[happy] He'll draw for an hour and fall asleep on the paper. You're a genius."
  - **"It's a secret. Off to bed, Nub."** (+Friendship)
    - **NUB:** "[angry] Secrets are only for grown-ups. That's not fair. ...Night."
  - **"It's a toy ship, Nub! For you!"**
    - **NUB:** "[happy] A SHIP? For me? Can I hold it? Can I fly it?"
    - **TOBBIN:** "[sad] ...It was going to be a surprise. It isn't finished, Nub. Bed. You'll have it when it's ready."
    - *(-20 friendship with Tobbin)*
- *[He blows off the dust, turns the ship over and carves on its belly: NUB'S. And under that, smaller: ECHO LANDING.]*
- *[Nub is asleep, a lump under his blanket. Tobbin sets the starship on his toy chest, nose to the window, where it's the first thing he'll see.]*
- **TOBBIN:** "[love] Thank you, {name}. A chair says someone's staying. A toy says someone's growing up here. I never thought we'd have either."

---

## ♥8 A Chair That Stays

**Trigger:** His workshop, 09:00–17:00, Monday to Saturday, after 6 (once the dome is open). With Merrow and Nub. Reward: the heirloom chair and its recipe. *(Zachary's reward; the scene and title are Claude's.)*

- *[Tobbin's workshop, swept clean for once. In the middle stands a chair under a sheet. Merrow and Nub are trying very hard not to peek.]*
- **TOBBIN:** "{name}. Good, you're here. I wanted you here for this. Nub, the sheet."
- *[Nub whips the sheet off. A chair: pale wood, the grain running down the legs like water, the seat worn smooth by hand. Not a pin or bolt in it.]*
- **TOBBIN:** "[happy] Bluebark joints. Pegs and wedges, the way my grandmother did them. The limb from the dome, and every evening since."
- **TOBBIN:** "A chair is a promise that someone is staying."
- **TOBBIN:** "[love] You fell out of the sky onto the worst moon in the sector, and you stayed. So it's yours."
- **CHOICE:**
  - **"Sit in it."** (+High Friendship)
    - *[You sit. The chair takes your weight and gives one small, polite creak.]*
    - **TOBBIN:** "[shocked] ...Did you hear that? It creaked hello."
    - **MERROW:** "[happy] It did, Tob. I heard it."
  - **"I can't take this. It's your first one."** (+Friendship)
    - **TOBBIN:** "[happy] That's exactly why. The first one goes to whoever made me want to make it."
  - **"It'd look great in the hotel lobby."**
    - **TOBBIN:** "[sad] ...The lobby. Yes. Strangers would sit in it. Put it somewhere you live, {name}. Please."
    - *(-20 friendship with Tobbin)*
- *[+ Heirloom chair (set it down at home)]*
- **TOBBIN:** "One more thing. You've watched me cut every joint. Let me show you the rest properly, and then you can make your own."
- *[Learned: the heirloom chair (3 real-wood planks and a hide, at a manufacturing hub)]*
- **NUB:** "[happy] Dad! Make one for me! A tiny one!"
- **TOBBIN:** "[happy] Tiny chairs are the hardest kind. ...Yes. All right. Yes."
