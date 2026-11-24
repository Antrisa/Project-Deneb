# Bram: heart events and his week (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **Everyone gets their own arc**, and side arcs are 2–3 scenes. Bram's arc is his own. A side arc with Ooma, the Merchant Guild of Two, was written and then cut the same day, with Ooma's own arc (Zachary: "maybe no heart events for oma shes just a wandering trader"); the drafts are in git history.
- **Who he is:** the general store owner. He sells seeds, fertiliser, basic goods and crafting recipes. Through his contacts with other Moogli merchants he sells what you put in your shipping crate: it goes up in his cargo pod overnight.
- **His week:** **Thursdays off**, with a quiet jab at a certain other general store ("Only a fool closes on a Wednesday. So: Thursday."), and a **half day on Sunday**.
- **His 8's reward:** a **Moogli trade beacon**. In the space segment you spend one fuel to call a store to you.

**The arc:** the shopkeeper who never collects.
- 2: the night pod, and his cousin Pell on the comm. Your shipping goes to the Moogli trade lanes.
- 4: you catch him writing off a stranded pilot's tab (the NPC Master's "Quiet Credit").
- 6: the family stops shipping until he collects what he's owed, and he never collects.
- 8: the station pays him back in kind, and he gives you his grandfather's trade beacon.

**What's whose:** the identity, week and reward are Zachary's; 4 is the NPC Master's outline; the scenes and every line are drafts by Claude. Right answers give +60 (High Friendship). Wrong ones: −20. In 6, offering to pay it yourself gets nothing (his pride).

**Flags this arc sets:** `bram_night_pod` (2), `bram_quiet_credit` (4), `bram_long_column` and, for the right answer, `bram_told` (6), `bram_paid_in_full` and the perk `perk_moogli_trade_beacon` (8).

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What he does |
|---|---|
| Monday to Wednesday, Friday, Saturday | His stall under the canopy from 07:00; dinner; the bar from 19:15; home at 22:00. |
| **Thursday (off)** | A late breakfast in the mess hall, the common room, lunch on the plaza watching who needs what, the afternoon at Tobbin's bench, dinner, the bar. His counter shows a sign: CLOSED THURSDAYS, and underneath, "Only a fool closes on a Wednesday." |
| **Sunday (half day)** | The stall until noon; lunch in the mess hall; a long soak at the bath house; dinner; the bar. His counter: CLOSED SUNDAY AFTERNOONS. |

- **Day lines** for Thursday and Sunday (`npc_data.gd DAY_LINES`), one a week in turn, and two everyday lines about his stock and the cargo pod. The board calendar lists his Thursdays off.
- **The shipping crate** says it goes up in his cargo pod to the Moogli traders.

---

## In the game (23 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`bram_2` to `bram_8`), staged like the other arcs: poses from his new heart-event sheet (`art/npc_bram_event.png`, from `tools/events.py`) and his action sheet (counter, restock, eat, drink), emote bubbles and sounds. Not run in Godot yet.

- **Pell**, his cousin, is only ever a voice on the comm, so he needs no art. So is the freighter pilot in 4.
- **The beacon** (his 8): on a free flight, once you're at a stop, the jump map's Ship panel shows **Call trader: 1 fuel**. The Ollo family trader (the Moogli trader's stock) comes alongside and stays at that stop for the rest of the run (`ship_map.gd can_beacon`, `main.gd _call_trader`; `docs/SHIP_ART_UI.md`).
- **Letter:** the morning after 4, "You heard nothing", with five packets of crater potato seeds ("This is not generosity. This is stock control.").
- **To test:** in a debug build, **F3** plays the next event in order (it sets the hearts, day and time).
- **Checked offline:** `python3 tests/check_heart_events.py`, `python3 tests/check_mail.py`.

---

## ♥2 The Night Pod

**Trigger:** the cargo bay in Engineering, by the yellow loading pad, 21:45–23:30, any night (the pod never takes a day off). *(Claude)*

- *[The cargo bay, late. A squat silver pod sits on the yellow loading pad with its hatch open.]*
- *[Bram is feeding it crates, one at a time, reading each label aloud like a prayer.]*
- **BRAM:** "Potatoes, agri porch. Copper, Tikka's. Bug shells, Job's. Lizard hides, yours. [happy] Nobody else ties a hide that neatly."
- **BRAM:** "[surprised] Oh! A customer, at this hour? The shop is shut. The pod is not. The pod never shuts."
- **BRAM:** "Every crate on the station goes up in this, every night. My cousins on the trade lanes buy it by sunrise."
- **PELL** *(comm)*: "Bram! Is that pod coming, or are you reading it bedtime stories again?"
- **BRAM:** "[happy] Coming, cousin! And I have a new seller on the manifest. Say hello, Pell."
- **PELL** *(comm)*: "Hello, new seller. Your hides are very neat. Bram, the moon wheat is underweight again."
- **BRAM:** "[angry] The moon wheat is perfect. The scales on your ship are Collective. Everybody knows Collective scales are optimistic."
- **CHOICE:**
  - **"That's where my shipping goes? You keep the station trading."** (+High Friendship)
    - **BRAM:** "[happy] I keep the station eating, mostly. Trading is only how. I buy, I sell, I introduce people who should meet."
    - **BRAM:** "Tonight I introduced you to Pell. You will regret it. Everyone does. Then they cannot do without him."
  - **"So you take a cut of everything I ship?"**
    - **BRAM:** "[angry] A cut? A Moogli takes a cut of the air he breathes. I take less than my cousins would. Much less."
    - **BRAM:** "...Less than is wise, Pell says. Pell is not here."
    - *(-20 friendship with Bram)*
- *[Bram thumps the hatch shut, pats it twice, and steps back behind the yellow line.]*
- *[With a cough and a roar the pod lifts off the pad, climbs through the bay doors and is gone into the dark.]*
- **BRAM:** "[happy] Every night I watch it go, and every night I think: there goes the station's dinner money. Sleep well, new seller."

---

## ♥4 Quiet Credit

**Trigger:** his stall, 07:00–09:00, any day but Thursday, after 2. *(The NPC Master's outline; the scene is Claude's.)*

- *[Opening time. Bram is behind his counter with the comm pressed to his ear, talking low, his ledger open in front of him.]*
- **FREIGHTER PILOT** *(comm)*: "I can pay on the next run, I swear it. The coupling cost more than the whole cargo, and the cargo was soup."
- **BRAM:** "Your tab? I see no tab. My ledger is very old, captain. Pages fall out. Safe travels."
- *[He tears a page out of the ledger, folds it twice and tucks it into his apron. Then he sees you.]*
- **BRAM:** "[surprised] How long have you been standing there?"
- **BRAM:** "...A Collective freighter. Her coupling blew two jumps out. The part was four hundred Scrip. She had sixty."
- **BRAM:** "If she does not fly, she does not trade. If she does not trade, she does not come back. This is arithmetic. Not charity."
- **CHOICE:**
  - **"Your secret's safe with me."** (+High Friendship)
    - **BRAM:** "[happy] Good. A soft Moogli is bad for business. ...Good for business, actually. Just not this year."
  - **"Everyone should know how generous you are!"**
    - **BRAM:** "[shocked] Then everyone will want credit! Please. Not a word. I have a reputation for being greedy and I worked hard for it."
    - *(-20 friendship with Bram)*
- **BRAM:** "Now. Are you buying, or are you only standing there being right?"
- *[The next morning: a letter (`bram_seeds`, in [MAIL.md](../MAIL.md))]*

---

## ♥6 The Long Column

**Trigger:** his flat, Thursday (his day off) 22:00–23:30, after 4. *(Claude)*

- *[Bram's flat. The dining table has vanished under ledgers. Bram stands over them with a pencil behind each ear.]*
- **BRAM:** "[sad] Ah. Come in. Mind the stock. Mind the other stock."
- **PELL** *(comm)*: "Last word, cousin. The family sends no more seed and no more stock until the long column is paid. Mother's orders."
- **BRAM:** "Mother has never been to a moon."
- **PELL** *(comm)*: "Mother has never needed to. Collect, Bram. Or come home."
- *[He turns the biggest ledger round so you can read it. One column runs down three pages: OWED TO BRAM.]*
- **BRAM:** "Freya, a till part. Tobbin, glue. Two years of glue. Job, a pick-head. Jasper owes me forty lunches. I ate them. They still count."
- **BRAM:** "[sad] I never collect. Out here, if you collect, people go without. If people go without, they leave. Then who do I sell to?"
- **BRAM:** "Next week my shelves are empty. No seed for your field. No fertiliser. Nothing."
- **CHOICE:**
  - **"Let me tell the others. They'd want to know."** (+High Friendship)
    - **BRAM:** "...Tell them? A Moogli does not ask. [sad] But you are not a Moogli. You could tell them, and I would not stop you."
    - **BRAM:** "[happy] I would pretend to be very surprised."
  - **"I'll pay it off for you."**
    - **BRAM:** "[angry] You? Pay my ledger? I would sooner eat the ledger."
    - **BRAM:** "...Thank you. No."
  - **"Then make them pay. It's your money."**
    - **BRAM:** "[sad] It is their bread. ...Go home, friend. I have sums to do."
    - *(-20 friendship with Bram)*

---

## ♥8 Paid in Full

**Trigger:** the mess hall at Sunday lunch, 12:15–13:30 (his half day). Tobbin, Freya, Job and Jasper are there. Nothing waits for the story, so there's no backup. Reward: the Moogli trade beacon *(Zachary)*.

- *[Sunday lunch, and the mess hall is full. Bram eats alone at his usual table, his ledger open beside the soup, doing sums with his spoon.]*
- **BRAM:** "Friend. Sit. The soup is free, Jasper owes me. Everything else, I am counting."
- *[Tobbin unrolls a drawing across Bram's ledger: shelves, measured to the inch.]*
- **TOBBIN:** "[happy] Two years of glue. I'm paying it back in shelves. Plastic. ...For now."
- **FREYA:** "[happy] Your till sticks on the seven. Not since this morning. We're square, Bram."
- **JOB:** "[happy] One pick-head, cher, plus interest. Ain't cracked this geode yet. Could be anything."
- **JASPER:** "[happy] Forty lunches, mon ami. This is the first. The other thirty-nine come with dessert."
- *If you told the others (his 6):*
  - **BRAM:** "...You told them."
- *If not:*
  - **BRAM:** "Somebody told them. S.A.R.A. says it was not her. [happy] S.A.R.A. is a terrible liar."
- **PELL** *(comm)*: "Cousin? The family ledger just balanced itself. In shelves, apparently, and a geode. Mother wants to know what a geode is."
- **BRAM:** "[happy] Tell Mother it is not for sale."
- **PELL** *(comm)*: "...The pod goes up full tonight. Mother says you have friends. She says it like a complaint."
- **BRAM:** "Everybody paying me back. How does a Moogli say thank you without it costing anything?"
- **CHOICE:**
  - **"You looked after them. Now they're looking after you."** (+High Friendship)
    - **BRAM:** "[bashful] ...That is not how it works. [happy] It seems to be how it works."
  - **"About time they paid up."**
    - **BRAM:** "[sad] They never owed me. That was the point. ...Here. Take it anyway."
    - *(-20 friendship with Bram)*
- **BRAM:** "This was my grandfather's. A Moogli trade beacon, tuned to the Ollo frequency."
- **BRAM:** "Light it out past the lamp-posts and one of my cousins comes running. It costs a fuel cell. Cheap, not free. Nothing is free."
- **BRAM:** "[happy] Except today's lunch. Everybody! Nobody pays today. Just this once. Do not get used to it."
- *[Perk: Moogli Trade Beacon (on a free flight, spend 1 fuel to call the Ollo family trader)]*

---

## Still open

- **His shop** is upstream's (23 Nov: `scripts/shop_data.gd`, `scripts/shops.gd`). It now shuts on his days off: `main.gd _at_workplace` counts his stall (`restock`) as work, and someone who usually works but has no work stop today is off, so on Thursdays and Sunday afternoons talking to him is a chat, not the shop. Fertiliser isn't in his stock yet.
- **Art** (on the Art Fix List): the cargo pod on the yellow loading pad and its launch, the CLOSED THURSDAYS sign on his counter, the ledgers on his dining table in 6.
