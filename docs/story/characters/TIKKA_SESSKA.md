# Tikka & Sesska: "Forty Years", their side arc (24 Nov 2026)

**Decided with Zachary, 24 Nov:**
- **Two scenes** (side arcs are 2–3 scenes): the NPC Master's two shared outlines, **EVA Workwear** (4) and **The Anniversary** (6). Each of them also has an arc of her own ([TIKKA.md](TIKKA.md), [SESSKA.md](SESSKA.md)), which carry the rewards, so the side arc has none.
- **The anniversary dinner** plays in the hotel's dining room if the hotel is open (after the Ivan fight), and in the mess hall after hours if not (Zachary).
- **Forty years married** (the game's line) stays.

**How it triggers:** both of them at the hearts (`"who": "Tikka", "with": ["Sesska"]`).

**What's whose:** the two titles and their outlines ("designing EVA-lined workwear together"; "a surprise the player helps organise") are the NPC Master's; the scenes and every line are drafts by Claude. The right answers give +60 to both of them. Wrong ones cost −20: in 4, siding with Tikka against Sesska's lining costs Sesska, and "tape" costs Tikka; in 6, toasting the core costs Sesska.

**Flags this arc sets:** `forty_workwear` (4), `forty_anniversary` (6).

---

## In the game (24 Nov)

Both are playable cutscenes in `scripts/heart_events.gd` (`forty_4`, `forty_6`), with both their heart-event sheets and action sheets. The anniversary starts at Tikka's bench in the morning and jumps to the evening (`["clock", 540]` under a fade), then goes to the hotel or the mess hall (`["go", ...]` inside an `"if"`). Not run in Godot yet.

- **Letter:** the morning after 6, "Forty years and a day", from both, with two coil wire (Tikka's idea of thanks).
- **To test:** in a debug build, **F3** plays the next event in order; these two come after Sesska's.

---

## ♥4 EVA Workwear

**Trigger:** Sesska's shop after closing, 19:00–21:15, Monday to Saturday. *(Claude)*

- *[Sesska's shop, after closing. Tikka stands on the fitting stool in an EVA suit with a long tear down one leg. She looks like a wronged umbrella.]*
- **TIKKA:** "[angry] A hull bracket. One bracket. It reached out and bit me."
- **SESSKA:** "Brackets don't bite, love. You climbed past it at speed, talking."
- **SESSKA:** "This suit is a disgrace. The lining is older than Freya. I'll line it in bug silk: warm, soft, and it moves when you move."
- **TIKKA:** "[angry] Bug silk snags. I need a tight weave. Three-ply. Snag-proof. Ugly is fine. Ugly is ideal."
- **SESSKA:** "Ugly is not fine. You'll be wearing it. I'll be looking at you wearing it."
- **TIKKA:** "Pilot. You decide."
- **CHOICE:**
  - **"Both. A tight weave outside, bug silk inside."** (+High Friendship)
    - **TIKKA:** "...That is a correct answer. I hate it. It's correct."
    - **SESSKA:** "[happy] Two layers, each doing its own job. Like a marriage."
    - *(+60 friendship with Sesska)*
  - **"Tikka's right. It just has to work."** (+Friendship)
    - **TIKKA:** "[happy] Thank you."
    - **SESSKA:** "[sad] Hm. It will work. It will work beautifully, and nobody will ever know."
    - *(-20 friendship with Sesska)*
  - **"Have you tried tape?"**
    - **TIKKA:** "[angry] Out."
    - **SESSKA:** "[happy] Not out. But don't help."
    - *(-20 friendship with Tikka)*
- *[They work on it together: four hands holding the seam, four hands sewing it, and a running argument about thread tension that nobody wins.]*
- **TIKKA:** "[happy] Look at that. It moves. It doesn't snag. If it holds on the hull, we make them for Freya. And Job. And everyone who goes outside."
- *If she has started the Landing's pattern (her 4):*
  - **SESSKA:** "[happy] With the Landing's pattern on the lining, where only the wearer knows it's there."

---

## ♥6 The Anniversary

**Trigger:** Engineering, Tikka's bench, 08:00–12:00 on a weekday, after 4; the evening is in the hotel's dining room, or the mess hall before the hotel opens. *(Claude)*

- *[Engineering, mid-morning. Tikka is at her bench, building something very small, very fast, with all four hands.]*
- **TIKKA:** "[surprised] Pilot! Good. You. Come here. Don't tell Sesska you saw me."
- **TIKKA:** "Forty years. Tonight. I had it in my diary. My diary was under the core manifold schematics. I found it this morning."
- **TIKKA:** "I have her present. Nearly. A music box: coil wire, wound fine, every note tuned by hand. It plays the song from our wedding. Nearly."
- **TIKKA:** "[sad] What I don't have is a dinner. Or a table. Or a plan. I have a music box and nine hours."
- **CHOICE:**
  - **"Leave the dinner to me. You finish the box."** (+High Friendship)
    - **TIKKA:** "[happy] Load-sharing. You'd make a good engineer, pilot. Go. Go!"
  - **"Just tell her you forgot. She'll understand."**
    - **TIKKA:** "[angry] She'll understand. That is the problem. She always understands."
    - **TIKKA:** "[sad] ...Will you help anyway?"
- *[You spend the day running. Jasper says yes before you finish asking. Evarra sends flowers, and a cake she calls structurally sound.]*
- *If the hotel is open (after the Ivan fight): the hotel's dining room*
  - *[The hotel's dining room, that evening. The guests are out and the lights are low.]*
  - *[One table has a cloth, two candles, and a coil of copper wire tied with a bow.]*
- *If not: the mess hall after hours*
  - *[The mess hall after hours, that evening. The benches are pushed back and the lights are low.]*
  - *[One table has a cloth, two candles, and a coil of copper wire tied with a bow.]*
- **SESSKA:** "[surprised] Tikka? What is all this?"
- **TIKKA:** "[happy] Forty years. Happy anniversary. I absolutely remembered."
- **SESSKA:** "[happy] You found your diary under the schematics this morning."
- **TIKKA:** "[surprised] ...How do you..."
- **SESSKA:** "[happy] Forty years, love."
- **JASPER:** "[happy] Ce soir: a lunar mushroom tart, and a cake Evarra describes as structurally sound. Bon appetit, mesdames."
- *[The music box plays a thin, bright tune. Every note is exactly in tune. Of course it is.]*
- **SESSKA:** "[sad] Our song. ...You tuned every note."
- **TIKKA:** "[happy] Twice. Then a third time. Because I like you."
- **SESSKA:** "Pilot. Rusk sent a bottle, and someone has to make the toast. Tikka will only talk about the box."
- **CHOICE:**
  - **"To forty years, and forty more."** (+High Friendship)
    - **SESSKA:** "[happy] Forty more. I'll hold her to it. I'll hold her to both."
    - *(+60 friendship with Sesska)*
  - **"To the core!"**
    - **TIKKA:** "[happy] To the core!"
    - **SESSKA:** "[angry] Not tonight, the core."
    - *(-20 friendship with Sesska)*
- *[They dance badly, to a music box, with eight hands between them. Nobody else in the room is looking at anything else.]*
- *[The next morning: a letter (`forty_years`, in [MAIL.md](../MAIL.md))]*
