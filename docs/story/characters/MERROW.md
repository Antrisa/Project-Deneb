# Merrow: heart events and her week (24 Nov 2026)

**Decided with Zachary, 24 Nov:** Tobbin's 4, 6 and 8 **wait for the garden dome's trees** ("wait for trees"), an exception to "8s never wait", like Zaas's 6 and 8 waiting for the Leviathan. His 8 is **a real chair and its crafting recipe**, and **he sells a bunch of furniture in his shop**. **Tobbin's shop is shut on Sundays; Merrow has the weekend off after her 8.** Claude's first suggestions for the rest, taken: **an arc each and a two-scene side arc** ([TOBBIN_MERROW_NUB.md](TOBBIN_MERROW_NUB.md)); **Nub's 8 is a framed drawing** you set down at home; **Hydro-Boost** as the NPC Master has it (hydroponic beds grow 20% faster). This closes the 5.8 gap (the 8 ran on Merrow's hearts but every scene was Tobbin's) and its clash (where the wood comes from: the garden dome's oldest tree, pruned).

**The arc:** the one who actually keeps the water running, learning to stop. (Her other story, the sea named after her, is in Zaas's arc: [ZAAS.md](ZAAS.md).)
- 2: filter day at the plaza fountain, at dawn. Every drop on the Landing goes through it; nobody notices until it stops.
- 4: her secret star-tomatoes behind the reclamation plant's last air scrubber, on water saved from her own ration, for Nub, who thinks tomatoes come in tubes.
- 6: a dry week. A recycler membrane split; you patch it with her at night and the fountain comes back. Nub asked her why she's never home.
- 8: her first day off, in the Observation Lounge. She can't sit still, so she shows you how to tune your beds' grow strips. Weekends off from now on.

**What's whose:** the reward (Hydro-Boost) is the NPC Master's; her weekends off are Zachary's; the scenes and lines are Claude's drafts. Right answers +60, middle +30, wrong −20 (in 2 the wrong one is a faceful of fountain, −10 energy).

**Flags:** `merrow_filters` (2), `merrow_tomatoes` (4), `merrow_dry_week` (6), `merrow_weekends` and the perk `perk_hydro_boost` (8).

## Hydro-Boost (her 8)

`main.gd _grow_crops`: with `perk_hydro_boost`, a crop in a hydroponic bed grows an extra day's worth in every five, the first one up front. A 3-day wheat is ready in 2, a 4-day potato in 3, a 6-day star-tomato in 5 and an 8-day grape in 7. Dug tiles are unchanged.

## Her week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What she does |
|---|---|
| Every day, until her 8 (unchanged) | The fountain from 06:30; the mess hall's crop beds in the East Complex; the plaza; her garden hour; dinner; home. |
| **Saturday, after her 8** (`merrow_weekends`) | The lounge glass in the morning; a bench by the fountain at noon (she can't help it); her own grow bed at home; dinner; home. |
| **Sunday, after her 8** | Her grow bed; the plaza garden at noon (or the garden dome, by the bluebark, once it's open); dinner; home. |

- **Day lines** for Saturday and Sunday, before and after her 8 (`npc_data.gd DAY_LINES`, with `"else"`). The station calendar doesn't list her weekends: its days off are fixed, and hers start with her 8.

## In the game (24 Nov)

All four are playable cutscenes (`merrow_2` to `merrow_8`), with her heart-event sheet (made for Zaas's arc) and her action sheet (valve, tend, garden). Not run in Godot yet.

- **Letter:** the morning after 4, "For your beds", with six star-tomato seeds.

---

## ♥2 Filter Day

**Trigger:** The plaza fountain, 06:30–09:30, Monday to Saturday. *(Claude)*

- *[The plaza, before anyone's up. The fountain is off, and Merrow is elbow-deep in it, hauling out a filter the size of a door.]*
- **MERROW:** "Morning. Don't stand there, stand here. Hold this end. It's heavy and it's slimy, and both of those are good signs."
- *[You hold one end while she shakes out the filter. Out come hair, grit, a sock, three crayons and a very small plastic dinosaur.]*
- **MERROW:** "[angry] Nub."
- **MERROW:** "...Every drop on the Landing goes through this fountain. Showers, soup, the lot. A hundred times round, at least."
- **MERROW:** "Don't think about it too hard."
- **CHOICE:**
  - **"That's amazing, actually."** (+High Friendship)
    - **MERROW:** "[happy] Isn't it? Nobody thinks so. Water's only interesting when it stops."
  - **"Can't a drone do this?"** (+Friendship)
    - **MERROW:** "Drones did it for the two years before we came. [angry] That's why it smelled."
  - **"Ugh. Gross."**
    - *[She gives the filter one more shake, and you get a faceful of fountain.]*
    - **MERROW:** "[happy] Sorry. Reflex. It's clean water. Mostly."
    - *(-10 energy)*
- **MERROW:** "Zaas has the title. I have the wrench. [happy] That's all right. A title never cleaned a filter."
- **MERROW:** "I'll keep the dinosaur. He can trade me something for it."
- *[She slides the clean filter home and opens the valve. The fountain coughs once, then sings.]*

---

## ♥4 Star-Tomatoes

**Trigger:** The reclamation plant in the East Complex, 14:00–16:30, Monday to Saturday, after 2. *(Claude)*

- *[The reclamation plant hums. Behind the last air scrubber, where the warm air comes out, someone is humming back.]*
- **MERROW:** "[shocked] Oh! It's you. Only you. Good. Come round, quick, before the chief walks past with his clipboard."
- *[Tucked in the corner: three star-tomato plants in a cut-down drum, under a grow lamp wired to the scrubber's spare socket. Two are blushing.]*
- **MERROW:** "Star-tomatoes. On water I've saved from my own ration, a cup at a time. I wrote the water rules, so I can't break them."
- **MERROW:** "[bashful] So I'm bending them. Very slightly. In a corner."
- **MERROW:** "They're for Nub. [sad] He thinks tomatoes come in tubes. He's never eaten a thing that grew. Not once, his whole life."
- **CHOICE:**
  - **"Your secret's safe with me."** (+High Friendship)
    - **MERROW:** "[happy] Thank you. A secret's lighter with two."
  - **"Can I try one?"** (+Friendship)
    - **MERROW:** "[happy] The first one's Nub's. The second... we'll see how well you keep secrets."
  - **"You should tell Zaas about this."**
    - **MERROW:** "[angry] And he'd put it on a form, and the form in a drawer, and the tomatoes in the soup. No."
    - *(-20 friendship with Merrow)*
- *[She gives each plant a capful of water, exactly the same, like a nurse on her rounds.]*
- **MERROW:** "Grow your own, if you like. Star-tomatoes love a hydroponic bed. [happy] More than a scrubber vent, anyway."
- *[The next morning: a letter (`merrow_seeds`, in [MAIL.md](../MAIL.md))]*

---

## ♥6 Dry Week

**Trigger:** The reclamation plant, 21:00–23:30, after 4. *(Claude)*

- *[The reclamation plant, late. A recycler membrane split three days ago. The fountain's off, showers are two minutes, and Merrow hasn't been home.]*
- **MERROW:** "[sad] Don't. I know how I look. Pass me the patch kit. The grey case. Please."
- **CHOICE:**
  - **"Hand her the grey case."** (+High Friendship)
    - **MERROW:** "Thank you. Now hold the lamp there. No, there. ...There."
  - **"Hand her the red case."** (+Friendship)
    - **MERROW:** "[happy] That's the first-aid kit. Although, at this point... No. The grey one."
  - **"You need to go to bed."**
    - **MERROW:** "[angry] If I go to bed, the Landing goes thirsty. The grey case, {name}."
    - *(-20 friendship with Merrow)*
- *[The patch holds. Overhead, pipes knock and gurgle, and then, very faintly, comes the sound of the plaza fountain starting up.]*
- **MERROW:** "[happy] Listen to that. ...Ha. Ha ha. I'm going to cry now, and it'll be very undignified, and you won't tell anyone."
- **MERROW:** "[sad] Nub asked me this morning why I'm never home. I said, the water. He said, the water's not your baby. I'm your baby."
- **CHOICE:**
  - **"He's right, you know."** (+High Friendship)
    - **MERROW:** "[sad] I know. ...I know. The water will still be here tomorrow. He won't be small for ever."
  - **"You kept the whole station going."** (+Friendship)
    - **MERROW:** "[happy] I did, didn't I? Don't tell him I said so. He'll want a medal too."
  - **"Zaas should have been here."**
    - **MERROW:** "[angry] Zaas was here till midnight last night. Don't you start on my chief. That's my job."
    - *(-20 friendship with Merrow)*
- **MERROW:** "Walk me home? My legs have forgotten the way."

---

## ♥8 A Day Off

**Trigger:** The Observation Lounge, Saturday 10:00–16:00, after 6. Tobbin and Nub bring a picnic. Reward: Hydro-Boost. *(The NPC Master's reward; the scene is Claude's.)*

- *[The Observation Lounge, mid-morning. Merrow stands at the glass with a cup of tea she hasn't drunk.]*
- *[There's no wrench on her belt. She keeps touching the place where it goes.]*
- **MERROW:** "[angry] Tobbin had S.A.R.A. take me off the rota. A whole day. Off. I didn't know you could do that to a person."
- **MERROW:** "I've been to the fountain twice. Just to look. [sad] It's fine. It's running. It doesn't need me. That's the worst part."
- **CHOICE:**
  - **"Tell me about Moogli Prime."** (+High Friendship)
    - **MERROW:** "[happy] Rain. It rained every afternoon at four. The farms on the hills drank it straight from the sky."
    - **MERROW:** "No pumps. No filters. I'd stand in it with my mouth open. ...I haven't thought about that in years."
  - **"Come and see my farm."** (+Friendship)
    - **MERROW:** "That's work, {name}. ...Is it work if it isn't my farm? [happy] Tell me about it, then. Just tell me."
  - **"Shall we check the fountain again?"**
    - **MERROW:** "[angry] Don't. Don't tempt me. I'll go, and I'll stay, and Tobbin will put a lock on the lounge."
    - *(-20 friendship with Merrow)*
- **MERROW:** "Your hydroponic beds. You've left the grow strips on the factory setting, haven't you? Everyone does. The factory never grew a thing."
- **MERROW:** "Blue up, red down, and pulse it at night. They'll think it's spring all the time. Here. I'll write it on your hand."
- *[She writes three numbers on the back of your hand in grease pencil, and smiles for the first time all morning.]*
- *[Hydro-Boost: your hydroponic beds grow 20% faster]*
- **NUB:** "[happy] Mum! We brought a picnic! It's mostly bread!"
- **TOBBIN:** "[happy] Day one of your holiday, my love. How are we doing?"
- **MERROW:** "[happy] Terribly. ...Saturdays, Tob. From now on. And Sundays. The water can learn some patience."
