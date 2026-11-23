# Evarra: heart events and her week (22 Nov 2026)

**Decided with Zachary, 22 Nov:**
- **The first bees are the siblings' 6** (Operation Honeybee). Her own 6 is now a wildflower border round your field, so it no longer waits for honey or for Jasper's hearts.
- **Her 10 is both:** baking a honey cake in your kitchen, then a picnic with it in the little park.
- **Days off are staggered with Jasper's**, so one of them always keeps the mess hall: Evarra is off **Wednesdays and Sundays**, Jasper **Tuesdays and Saturdays**. Both have their own lines on those days.
- Variety of place: only her 2 is at work (the greenhouse bench); 4 and 8 are in the garden dome, 6 at your field, 10 in your kitchen and the little park. Nothing is in the mess hall.
- Keepsake: a frame of the pressed flowers from the crown she makes you at 8 (a slice of cake wouldn't keep).

**The arc:** a gardener without a garden, until there is one.
- 2: one pot of lavender is the only thing she grows for herself.
- 4: the garden dome wakes, and she dances barefoot in real soil.
- 6: she plants wildflowers round your field for the bees to come.
- 8: a crown of every flower she's grown, and what she's grown for you.
- 10: something you made together, eaten on a blanket under the dome.

**What's whose:** Zachary's outlines are 2 (her one lavender plant under a grow-lamp), 4 (real soil and wildflowers; she dances barefoot), 8 (she weaves a blossom crown and confesses at sunset; Green Thumb) and 10 (a night bake and a tiered honey cake). Every line below is a draft by Claude, for Zachary to change or approve. Each line starts with a portrait tag the game already reads (`[happy] [sad] [surprised] [love] [angry] [shocked] [bashful]`). Lines stay under about 150 characters. Choices give +30 (Friendship) or +60 (High Friendship), as in the NPC Master.

**One change from the outline:** her 2 was "in the dead dome". The game draws the garden dome already grown (there's no dead version of it yet), so 2 plays at her herb bench in the mess hall's greenhouse, where she works every morning.

---

## Her week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where she goes |
|---|---|
| Monday, Tuesday, Thursday, Friday, Saturday (unchanged) | The mess hall kitchen from 06:00; her herb bench in the greenhouse 09:30; the kitchen 13:00; the promenade flower beds 14:00; the kitchen; dinner after service 19:15; home 20:30; bed 22:30. On Tuesdays and Saturdays Jasper is off, so the soup is hers. |
| Wednesday (day off) | Her herb bed at home 08:00; Ooma's stall for seeds 10:00 (one of Ooma's days); lunch 12:00; the little park 13:30; the promenade flower beds 16:30; dinner with everyone 18:00; home 19:30 |
| Sunday (day off) | Breakfast at the mess 08:30; the promenade flower beds 10:00; the little park 12:30; her herb bed at home 15:30; dinner 18:00; home 19:30 |
| Wednesday, once the garden dome is open | The same morning, then the dome's meadow from 13:30 until dinner |
| Sunday, once the garden dome is open | Breakfast, then the dome's meadow all day until dinner |

**What she says on those days** (`scripts/npc_data.gd`, `DAY_LINES`; the first time you talk to her that day, a different line each week): on her days off, about soil, sleeping in and Ooma's seed packets; on Jasper's days off, about having the kitchen to herself ("Nobody is singing to the onions."). The station calendar on the board lists who's off each day.

**Flags this arc sets:** `evarra_wildflowers` (6), the perks `perk_honey_lavender_brioche` (6) and `perk_green_thumb` (8), the keepsake `keepsake_pressed_flower_frame` (10), and `partner` = Evarra if you accept at 8. 4 needs `east_dome` (the garden dome open).

## In the game (22 Nov)

All five are playable cutscenes in `scripts/heart_events.gd`, played by `scripts/cutscene.gd`. She poses from her heart-event sheet (`art/npc_evarra_event.png`) and her action sheet. Not run in Godot yet.

- **Two new things in the cutscene engine:**
  - **Backup places** (`"backup"` in an event): her 8 plays in the orchard once the garden dome is open, and at the promenade flower beds until then, so it never waits for the story.
  - **Moving map mid-scene** (`["go", area, x, y, dir]`): her 10 starts in your kitchen and ends in the little park.
- **To test:** in a debug build, **F3** plays the next event in order (Freya's and Jasper's come first, so Evarra's 2 is the eleventh press); **F5** opens the garden dome (4 needs it; with it closed, 8 plays at the flower beds).
- **Checked offline:** `python3 tests/check_heart_events.py` (it checks 8 at both places).
- **Not in yet:** the wildflower border on your field after 6 (`evarra_wildflowers` is set so a map version can switch on), what the brioche and Green Thumb do in play, and the frame as an item you can hold.

---

## ♥2 The Window-Box Herb

**Trigger:** walk into the East complex 09:30–13:00 on one of her working days (not Wednesday or Sunday) with Evarra at 2 hearts.

**Setting:** the mess hall's greenhouse. Evarra is at her herb bench; one pot of lavender sits apart under its own lamp.

- *[The mess hall's greenhouse: rows of basil, thyme and chives for the kitchen.]*
- *[In the corner, one small pot sits apart under its own grow-lamp.]*
- **EVARRA:** "[surprised] Oh! I didn't hear you come in. The fans in here are louder than people."
- **EVARRA:** "Everything in these beds belongs to the kitchen. Jasper's basil. Jasper's thyme. Jasper's very important chives."
- **EVARRA:** "[happy] That pot is mine. Lavender. It doesn't feed anyone. I grow it because it smells like somewhere I've never been."
- *[Her cheek blotches shift to a soft violet, the colour of the flowers.]*
- **EVARRA:** "[sad] A small farm. Flowers, and bees to go with them. I used to think that wasn't much to ask of a galaxy. It is."
- **EVARRA:** "Do you want to smell it? Rub a leaf. Gently."
- **CHOICE:**
  - **"[Rub a leaf]"** (+High Friendship)
    - *[It smells of warm stone and summer evenings, somewhere very far away.]*
    - **EVARRA:** "[happy] There. Now you've been there too."
  - **"Why not grow more of it?"** (+Friendship)
    - **EVARRA:** "Space. Water. Jasper's basil. One pot is what a station can spare."
    - **EVARRA:** "[happy] One pot is enough to remember what I want."
- **EVARRA:** "[happy] If you ever find a garden going spare, you'll tell me first?"
- **The next morning** *(Claude, 23 Nov)***:** a letter from Evarra, "Something that grows" (`evarra_lavender` in `scripts/mail_data.gd`), with Star tomato seeds x3 in the envelope. The text is in [MAIL.md](../MAIL.md).

---

## ♥4 First Blossom

**Trigger:** walk into the East complex once the garden dome is open, on her day off (Sunday 10:00–17:00, or Wednesday 13:30–16:30), with Evarra at 4 hearts, after The Window-Box Herb. It waits for the dome because the dome is what it's about.

**Setting:** the garden dome's meadow. Evarra has kicked off her shoes.

- *[Real soil under the dome lights. Between the young trees the first wildflowers are open. Evarra's shoes lie in the grass.]*
- **EVARRA:** "[surprised] Oh! You saw that. There was a dance happening. I wasn't in charge of it."
- **EVARRA:** "[happy] Feel this. Go on, it's soil. Real soil, not grow-gel. It's cold, and it's alive, and there are worms. Worms!"
- **EVARRA:** "I've been a gardener my whole life without a garden. Pots. Window boxes. One lavender plant under a lamp."
- **EVARRA:** "[bashful] You woke this dome. I don't know how you thank someone for that."
- **CHOICE:**
  - **"Dance with me, then."** (+High Friendship)
    - *[You dance badly, barefoot, among the first flowers on the moon. Neither of you cares.]*
  - **"You look happy here."** (+Friendship)
    - **EVARRA:** "[happy] I am. I didn't know anyone could be this happy about dirt."
- **EVARRA:** "[happy] Next it needs bees. Then it's a real garden. Then you'll never get me out of here."

---

## ♥6 A Hem of Wildflowers (was "Honey & Brioche")

**Trigger:** walk into the West Agridome 08:00–12:00 on her morning off (Wednesday or Sunday) with Evarra at 6 hearts, after The Window-Box Herb. It doesn't wait for the garden dome or for honey.

**Setting:** the edge of your field. Evarra has a pouch of Ooma's seeds.

- **EVARRA:** "[happy] There's the farmer. I've been admiring your rows. They're very straight. Jasper's never would be."
- **EVARRA:** "I bought these from Ooma. Wildflower seeds from six different worlds. She swears only half of them bite."
- **If the garden dome is open:**
  - **EVARRA:** "The garden dome will feed a hive one day, but bees roam. They'll want flowers out here too."
- **Otherwise:**
  - **EVARRA:** "There's nowhere for bees on this moon yet. But when they come, I want flowers waiting for them."
- **EVARRA:** "[bashful] May I plant a border round your field? Just the edges. Bees like a farm with a hem on it."
- **CHOICE:**
  - **"Plant them anywhere you like."** (+High Friendship)
    - **EVARRA:** "[happy] Anywhere! You'll regret that in spring. I won't."
  - **"Just the edges. I need room for wheat."** (+High Friendship)
    - **EVARRA:** "[happy] Spoken like a farmer. The edges it is."
- *[You dig. She sows. By noon there's a thin line of seed all the way round your field, and soil up to both your elbows.]*
- **EVARRA:** "[happy] When the first honey comes, it goes in a brioche. Lavender, honey, and butter if Jasper's ever found any."
- **EVARRA:** "You get the first one. That's the rule now."
- **New recipe: Honey-Lavender Brioche (once there's honey)**

---

## ♥8 Wildflower Crown (confession)

**Trigger:** 17:30–19:30, with Evarra at 8 hearts. Once the garden dome is open: walk into the East complex, and it plays in the orchard. Until then: walk onto the promenade, and it plays at the flower beds where she gardens every afternoon.

**Setting:** sunset. Evarra has been weaving something behind her back.

- **If the garden dome is open:**
  - *[Sunset light through the dome. Blossom drifts down from the orchard trees.]*
- **Otherwise:**
  - *[The promenade lamps are turning gold. The flower beds smell of evening.]*
- **EVARRA:** "[happy] There you are. Don't move. Bow your head a little."
- *[She sets something on your head: a crown, woven from every kind of flower she has ever grown.]*
- **EVARRA:** "[happy] It suits you. I knew it would. I've been practising on Jasper. He looks like a salad."
- **EVARRA:** "When we came out of that pod, all we had was each other. A garden was the one thing I wanted that was only mine."
- **EVARRA:** "Then you came, and things started growing. The dome. The flowers. Me, a little."
- **If you are dating someone else (the friendship ending):**
  - **If you are dating Jasper:**
    - **EVARRA:** "[happy] You're dating my brother, so I'm obliged to like you. Luckily I'd have done it anyway."
  - **Otherwise:**
    - **EVARRA:** "[happy] You're the best friend I've ever had who wasn't my brother. He doesn't count. Keep the crown."
- **Otherwise:**
  - **EVARRA:** "[bashful] I've grown a lot of things. I've never grown this. I like you. More than as a friend, I mean."
  - **EVARRA:** "[love] Would you let me be more than the baker who grows your flowers?"
  - **CHOICE:**
    - **"I'd love that, Evarra."**
      - *(Evarra is now your partner.)*
      - **EVARRA:** "[surprised] You would? Oh. My blotches have gone all pink. Don't look."
      - *[You stay until the lights dim, and the crown slips down over one ear.]*
    - **"You mean a lot to me, as a friend."**
      - **EVARRA:** "[sad] All right. I'm glad I said it. Gardeners plant things that don't come up. That's part of it."
      - **EVARRA:** "[happy] Keep the crown anyway. It was made for you."
- **EVARRA:** "[happy] And come and find me whenever you're planting. I'll teach you how to get the best out of your soil."
- **Perk: Green Thumb (better-quality crops)**

---

## ♥10 The Moonlit Bakery

**Trigger:** come home to your flat 20:30–23:30 while you're dating Evarra, with her at 10 hearts.

**Setting:** your kitchen (your flat by the farm since 23 Nov; it was the hotel's), then a blanket in the little park in the East complex.

- *[Your kitchen smells of honey and warm bread. Every bowl you own is out. Evarra is floury to the elbows.]*
- **EVARRA:** "[happy] S.A.R.A. let me in. She said you wouldn't mind, and that your oven had never been used. Both true, I see."
- **EVARRA:** "Roll this out for me? Not too thin. It's going to be a honey cake. Three tiers, if we're lucky."
- **CHOICE:**
  - **"Like this?"** (+High Friendship)
    - *[You roll it far too thin. She laughs and folds it back up without a word.]*
    - **EVARRA:** "[happy] Perfect. Again."
  - **"I'll do the icing. I'm an artist."** (+High Friendship)
    - **EVARRA:** "[happy] An artist. All right. Pink stars only."
- *[Flour everywhere. The oven ticks and hums. For once your whole flat smells like a bakery.]*
- **EVARRA:** "[happy] Three tiers! A bit lopsided. Jasper will say it leans. Let him."
- **EVARRA:** "[happy] Now we take it somewhere with grass. You carry the basket. I carry the cake. Nobody runs."
- *(The scene moves to the little park in the East complex.)*
- *[A blanket in the little park. Two lanterns. The cake, only slightly squashed from the walk.]*
- **EVARRA:** "[love] I used to dream of a farm with flowers and bees. I nearly have it now. But this is the part I didn't know to dream about."
- **EVARRA:** "You. A blanket. Something we made together, going soft in the lamplight."
- **EVARRA:** "[bashful] And this. I pressed the flowers from the crown. Every one. I couldn't let them go."
- *[A small wooden frame. Inside, flat and bright, are the flowers from your crown.]*
- **Keepsake: the pressed flowers from Evarra's crown**
