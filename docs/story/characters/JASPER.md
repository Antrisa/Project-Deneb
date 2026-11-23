# Jasper: heart events and his week (22 Nov 2026)

**Decided with Zachary, 22 Nov:**
- His events get more variety of place: only 6 is in the mess hall (the dining hall). 2 is at Ooma's stall, 4 in the common room, 8 at his home, 10 by the fountain.
- His old 2 ("Burnt Ration Soufflé") repeated the siblings' 2, so it's replaced by **The Butter Tin**.
- **Butter** comes from Ooma: a rare tin of real Terran butter he saves up a whole season for. There is no Butter item.
- **The holo-vid** of Chef Laurent's cooking show came in the escape pod with Jasper and Evarra (with "a tin of ration cubes", as the siblings' 8+ says). It's his only link to where they came from.
- 10 is a morning scene, so it doesn't repeat the siblings' evening banquet at the same fountain.
- **Days off are staggered with Evarra's**, so one of them always keeps the mess hall: Jasper is off **Tuesdays and Saturdays**, Evarra **Wednesdays and Sundays**. Both have their own lines on those days.

**The arc:** he thinks he's dreaming of Paris, but what he really wants is a table with someone across from him.
- 2: he can't afford the one thing his cooking is missing.
- 4: the Paris he loves came in the pod; even his accent is borrowed.
- 6: the first real croissant, made with your wheat.
- 8: the dream was never the city; it was sitting down with someone.
- 10: his own café, and you as his partner in it.

**What's whose:** Zachary's outlines are the start of 6 (first real croissant, the bistro menu), 8 (a private dinner; the dream of Paris was a dream of sharing a table; Sous-Chef's Blessing) and 10 (Café Étoile, an outdoor terrace by the fountain). Chef Laurent and the pod's holo-vid come from his side-arc scripts. Every line below is a draft by Claude, for Zachary to change or approve. Each line starts with a portrait tag the game already reads (`[happy] [sad] [surprised] [love] [angry] [shocked] [bashful]`). Lines stay under about 150 characters. Choices give +30 (Friendship) or +60 (High Friendship), as in the NPC Master.

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where he goes |
|---|---|
| Monday, Thursday, Friday, Sunday (unchanged) | The mess hall kitchen from 06:00; his break in the common room 14:30–16:30; back to the kitchen; dinner 18:40; cooks until 21:30; home; bed at 22:30. On Sundays Evarra is off, so he's the baker too. |
| Wednesday | The same, but his break is at Ooma's stall (she's on the station Wednesdays and Saturdays). Evarra is off. |
| Tuesday (day off) | Breakfast at the mess as a customer 08:30; picking herbs beside Evarra in the greenhouse 10:00; the library 12:30 (Owen's old Earth cookbooks); the common room 14:30, out of habit; cooking at his own stove at home 17:00; dinner at home with Evarra 20:30 |
| Saturday (day off) | Ooma's stall 07:00 (market day); the library 09:00; lunch at the mess as a customer 12:00; the bench by the fountain 13:30, sketching his café; cooking at home 17:00; dinner with Evarra 20:30 |
| Tuesday or Saturday, once the garden dome is open | The same, but the library (Tuesday) or the fountain bench (Saturday) gives way to the dome, by the stream |

**What he says on those days** (`scripts/npc_data.gd`, `DAY_LINES`; the first time you talk to him that day, a different line each week): on his days off, about not cooking, Ooma's stall and his sketches; on Evarra's days off, about being the baker too ("Pray for the bread."). The station calendar on the board lists who's off each day.

**Flags this arc sets:** `jasper_butter_deposit` (2), `cafe_etoile` (10), the perks `perk_parisian_bistro_menu` (6) and `perk_sous_chefs_blessing` (8), the keepsake `keepsake_jasper_apron` (10), and `partner` = Jasper if you accept at 8. 6 needs `moon_wheat_harvested`, which is set the first time you harvest Moon wheat (older saves count Moon wheat you're carrying).

## In the game (22 Nov)

All five are playable cutscenes in `scripts/heart_events.gd`, played by `scripts/cutscene.gd`, like Freya's. Jasper and Evarra now have heart-event sheets (`art/npc_jasper_event.png`, `art/npc_evarra_event.png`: talk, laugh, sad, jump, gift, bench, wave). Ooma, Rusk and Pip only walk, turn and get emote bubbles. Not run in Godot yet.

- **To test:** in a debug build, **F4** plays the next event in order (Freya's five come first, so Jasper's 2 is the sixth press; it sets the hearts, day, time and place each needs); **Shift+F4** forgets the ones you've seen.
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **Not in yet:** what the Parisian Bistro Menu and Sous-Chef's Blessing do in play (there's no cooking or food buffs yet, so they're recorded as perks); the café terrace on the map after 10 (it needs tables, an awning and a sign drawn for the plaza; `cafe_etoile` is set so a map version can switch on); the apron as an item you can hold.

---

## ♥2 The Butter Tin (was "Burnt Ration Soufflé")

**Trigger:** walk onto the promenade on a Wednesday 14:30–16:30 or a Saturday 07:00–09:00 (Ooma's days, when Jasper is at her stall) with Jasper at 2 hearts.

**Setting:** Ooma's stall by the fountain plaza. Jasper is holding a small, frosted tin as if it might bite.

- **JASPER:** "[angry] Nine hundred Scrip? Madame, that is not a price. That is a hostage situation."
- **OOMA:** "It is real Terran butter, little chef. Cold-sealed. It crossed four borders to sit on my table."
- **OOMA:** "I do not haggle. I simply wait until you agree."
- *[Jasper turns out his apron pocket: a few coins, a button and a folded recipe card.]*
- **JASPER:** "[sad] Five hundred and twelve. And the button, which is a very nice button."
- **JASPER:** "[surprised] Mon ami! You arrive at the perfect moment. Tell her. Tell her a chef deserves butter!"
- **CHOICE:**
  - **"Save up. I'll grow you the wheat for the pastry."** (+High Friendship)
    - **JASPER:** "[surprised] Wheat... from your own field? Then the butter would have something to live up to."
  - **"Can't you cook without it?"** (+Friendship)
    - **JASPER:** "[sad] You sound like Evarra. Of course I can. I have cooked without it all my life. That is the problem."
  - **"Butter is overrated."** (no friendship)
    - **JASPER:** "[shocked] ...I will pretend I did not hear that, for the sake of our friendship."
- **OOMA:** "[happy] Leave me what you have, little chef. I will keep the tin cold until the season turns."
- **OOMA:** "If the rest comes by then, it is yours. If not, I know a collector who will weep for it."
- **JASPER:** "[happy] Madame, you are a poet!"
- *[He pours every coin onto her table. The button too. Ooma keeps the button.]*
- **JASPER:** "[happy] One season. Then, mon ami, you will taste a croissant the way it was meant to be."

---

## ♥4 Paris on a Screen

**Trigger:** enter the common room 14:30–16:30 on any day but Wednesday and Saturday (his break; on Tuesdays, his day off, he goes anyway) with Jasper at 4 hearts, after The Butter Tin.

**Setting:** the common room, empty but for Jasper and a cracked holo-projector. Evarra comes in near the end.

- *[The common room is empty except for Jasper. A cracked little holo-projector flickers in his hands.]*
- *[On its screen, a chef in a tall white hat folds butter into dough and talks about Paris.]*
- **JASPER:** "[surprised] Ah! You caught me. Every day at half past two, I visit Paris. It is a short trip."
- **JASPER:** "This is Chef Laurent. Episode four: the soufflé. I have watched it perhaps three thousand times."
- **JASPER:** "[sad] It was in the pod with us. A ration tin, a thermal blanket, Evarra, me, and this."
- **JASPER:** "S.A.R.A. says it was still playing when the pod docked. We grew up on it. We learned to talk from Chef Laurent."
- *[His accent slips away. His voice goes quiet and plain.]*
- **JASPER:** "[sad] I am not French. I have never been to Earth. I have never even tasted butter. The accent is his. I borrowed it."
- **JASPER:** "Sometimes I think whoever put us in that pod wanted us to see Paris. So I keep watching. In case it is a message."
- **JASPER:** "[bashful] Is that foolish?"
- **CHOICE:**
  - **"Maybe they wanted you to have something beautiful."** (+High Friendship)
    - **JASPER:** "[bashful] ...Something beautiful. Yes. I like that better than a message."
  - **"Do you want to find out who sent the pod?"** (+Friendship)
    - **JASPER:** "[sad] Once, very much. Now I am not sure. The answer might be smaller than the question."
  - **"The accent suits you. Keep it."** (+High Friendship)
    - **JASPER:** "[happy] Ha! Then I keep it. It took me years to roll the R."
- **EVARRA:** "[happy] Is he making you watch the soufflé episode again? He cries at the end. Every time."
- **JASPER:** "[angry] I do not cry. The onions in that episode are very strong."
- **JASPER:** "[happy] Come back sometime. Episode five is the croissant. It is a tragedy, and a triumph."

---

## ♥6 Taste of Paris

**Trigger:** enter the mess hall 06:00–08:30 on a Monday, Thursday or Friday (when both siblings are working) with Jasper at 6 hearts, once you've harvested Moon wheat, after Paris on a Screen.

**Setting:** the mess hall before breakfast. Jasper is at the oven; Evarra is mixing at her counter.

- *[The tables are still dark. The kitchen smells like nothing on this moon has ever smelled.]*
- **JASPER:** "[surprised] You! You are early. No, you are exactly on time. Sit, sit! Do not look at the oven."
- **JASPER:** "Ooma came through. One tin of Terran butter, cold-sealed, paid in full. Every coin of it."
- **JASPER:** "[happy] And the flour is Moon wheat from your field. I milled it by hand, all night."
- *[He sets down a plate. On it sits one croissant: golden, flaky and noticeably lopsided.]*
- **JASPER:** "[bashful] It leans. Chef Laurent's never leaned. Taste it anyway? Together. On three."
- **CHOICE:**
  - **"Un, deux, trois!"** (+High Friendship)
    - **JASPER:** "[surprised] You learned the French!"
  - **"You first. You've waited longer."** (+High Friendship)
    - **JASPER:** "[bashful] ...Twenty years, give or take. Very well."
- *[It shatters into a hundred flakes. Inside it is soft and warm, and it tastes of butter, which is to say like nothing else at all.]*
- **JASPER:** "[sad] Oh. Oh, non. I am not crying. There is flour in my eye."
- **JASPER:** "[happy] It is real. It is a real croissant, on the moon!"
- **EVARRA:** "[surprised] Is that butter? Jasper, did you spend a whole season's pay on one tin of butter?"
- **JASPER:** "[happy] Half a tin. The other half is for the menu."
- **JASPER:** "[happy] Croissants on Saturdays. Onion soup. Crêpes with Evarra's herbs. A real bistro menu!"
- **JASPER:** "Starting very soon. When I have more butter."
- **New: Jasper's Parisian Bistro Menu**

---

## ♥8 A Table of My Own (confession; was "Candlelight in the Mess Hall")

**Trigger:** enter Residences A (his and Evarra's home) 17:00–20:30 on his day off (Tuesday or Saturday) with Jasper at 8 hearts. Evarra is working at the mess hall. It needs no story progress.

**Setting:** his home. Something is on his stove; the dining table is set for two with a candle.

- *[Something sizzles on Jasper's stove. The dining table has a cloth, two plates and a single candle.]*
- **JASPER:** "[happy] Ah! Right on time. Well, you did not know you were invited. But you were. Evarra has the mess hall tonight."
- **JASPER:** "[bashful] Sit. Please. Tonight I am not the chef of anything. I am only a person who made dinner."
- *[Star tomato soup. Crater potatoes roasted crisp. The last of the butter, on bread made from your wheat.]*
- **JASPER:** "[sad] For years I have set tables for everyone. A hundred plates a day. I never once set a table of my own."
- **JASPER:** "I always thought my dream was Paris. The bridges, the cafés, the tower of iron lace."
- **JASPER:** "But do you know which part of the holo-vid I watch the most? Not the cooking. The end, when he sits down and eats with someone."
- **If you are dating someone else (the friendship ending):**
  - **JASPER:** "[happy] That part is what I wanted all along. You helped me see it, my friend."
  - **EVARRA:** "[surprised] Candlelight? In our kitchen? Jasper, is there a third plate?"
  - **JASPER:** "[happy] There is always a third plate. A table needs more than two chairs. That is the whole secret, I think."
- **Otherwise:**
  - **JASPER:** "[bashful] And when you sit across from me, I do not miss Paris at all. Not even a little."
  - **JASPER:** "[love] I would like this to be our table. Not as friends. Will you stay for dessert, and for a great many dinners after?"
  - **CHOICE:**
    - **"I'd love to share your table, Jasper."**
      - *(Jasper is now your partner.)*
      - **JASPER:** "[surprised] Truly? Ha! Then dessert! Wait here. Do not move!"
      - *[Dessert is a little burnt. Neither of you minds. The candle burns down to nothing before you leave.]*
    - **"You mean a lot to me, as a friend."**
      - **JASPER:** "[sad] Ah. Of course. Then you will always have a seat here, as my friend. That is not a small thing."
      - **JASPER:** "[happy] Now eat. I did not cook all afternoon for you to look sad at my soup."
- **JASPER:** "[happy] And from now on, bring me what you cook. I will teach you how to make a good meal stay with you."
- **Perk: Sous-Chef's Blessing (food buffs last 20% longer)**

---

## ♥10 Café Étoile

**Trigger:** walk onto the promenade 07:00–11:00 while you're dating Jasper, with him at 10 hearts, after A Table of My Own.

**Setting:** opening morning. Two little tables with striped cloths by the fountain. Evarra, Rusk and Pip turn up partway through.

- *[Two little tables with striped cloths stand by the fountain. A chalkboard sign reads: CAFÉ ÉTOILE. OPEN SOON.]*
- **JASPER:** "[happy] Bonjour! Welcome to Café Étoile! You are our first customer. Also our only customer. Also the reason it exists."
- **JASPER:** "[bashful] Tobbin built the tables. Sesska hemmed the cloths. S.A.R.A. gave me the plaza mornings. I only had to ask."
- **JASPER:** "[happy] Étoile means star. A café under the stars, every morning. Paris never had that."
- *[He brings two coffees and two croissants. Both of them stand up straight this time.]*
- **JASPER:** "[love] I used to think I would have to cross the galaxy to find my table. It was here all along. It was you."
- **EVARRA:** "[happy] Is this where the line starts? Rusk has been telling everyone since six."
- **RUSK:** "[happy] Best news I've poured in years. A café, on our moon!"
- **PIP:** "Do croissants come with jam? Grandma says I can have one if it comes with jam."
- **JASPER:** "[happy] Everyone sits! There are only two tables, so everyone sits very close!"
- **JASPER:** "[love] Wait. First, this. A café needs two names on the door, and the cook needs a partner in the kitchen."
- *[A new apron, folded neatly. Two names are stitched on the pocket: his, and yours.]*
- **Keepsake: an apron with both your names**
