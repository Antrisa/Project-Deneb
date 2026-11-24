# Jasper & Evarra: the sibling side arc (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **Trimmed to three scenes** (Zachary, 23 Nov, for every side arc: "trim to 3"): the pod memory (4), the bees (6) and the banquet. The béchamel (2) and the critic's practice run (8) are cut; their scripts are kept at the end of this doc. The Starlight Soufflé now comes at the banquet.
- *(Before the trim)* **8 moves to the hotel's dining room**, the room the critic will actually eat in. Until the hotel opens (after Ivan's fall) it plays in the mess hall instead, so it never waits. This settles Decision 9.
- **4 moves out of the Observation Lounge** to the West Terminal's little star dome above the landing pads, in two versions: honey tarts once the garden dome is restored, herb tea and ration-flour tarts before.
- **Ooma's ship brings the hive in 6**, not Eshu's mail skiff (Eshu can arrive later than the garden dome).
- **A wrong choice costs a little** instead of giving the same reward: in 4 a quiet Evarra and nothing gained, in 6 a bee sting.
- **The banquet only happens in autumn or winter**, on an evening after the pod memory (4). It doesn't wait for the bees: the honey lines change once they've come.

**The arc:** two foundlings from one escape pod turn scarcity into a feast.
- 4: two infants in one thermal blanket.
- 6: the first bees.
- 10: the whole station at one table, and Jasper's own soufflé.

**What's whose:** lines marked *(Zachary)* are his, from "Heart Events: All Romances" (Part 1, Jasper & Evarra): the setting, every line and the three choices of 2; the setting and every line of 4 (the version before the garden dome is Claude's); the setting and every line of 6; the setting, Jasper's and S.A.R.A.'s lines and both choices of 8; the setting and both speeches of 10. Everything else is Claude's, for Zachary to change or approve: the choice in 4, the choice in 6 and the sting, what happens after each choice in 8, and the small reactions. Choices give +30 (Friendship) or +60 (High Friendship), to one or both of them as the script says.

**How it triggers:** both of them at the hearts (the event's `"with": ["Evarra"]`). Neither can pass 8 hearts unless you're dating them, so the "10" (the banquet) needs both at 8.

**Flags this arc sets:** `siblings_pod_story` (4), `siblings_bees` and the perk `perk_wildflower_honey` (6; `siblings_helmet` if you told Jasper to keep the helmet on), `siblings_feast`, the perks `perk_starlight_souffle` and `perk_family_table`, and the keepsake `keepsake_family_photo` (10).

---

## In the game (23 Nov)

All three are playable cutscenes in `scripts/heart_events.gd` (`siblings_4`, `siblings_6`, `siblings_10`), staged like the romance arcs: poses from both their heart-event sheets and action sheets (cooking, mixing, gardening), emote bubbles for everyone, and sounds. Not run in Godot yet.

- **New engine bits:** an event's `"with"` (others who need the same hearts) and `"seasons"` (only in those seasons), checked in `main.gd _event_ready`; F3 meets both in debug builds (it raises the others' hearts and moves the day into the season). A new scene step, `["energy", -points]`, is the bee sting's cost.
- **Animated (Zachary, 23 Nov):** a new scene step, `["fx", kind, x, y, spread]`, draws bees, fireflies or steam in code (`scripts/scene_fx.gd`) until there's art. Steam rises from the mugs in 4; in 6 the bees buzz in the glass hive, pour out round the flowers (and find Jasper's helmet if you told him to keep it on), then settle on Evarra's hand; fireflies drift over the banquet in 10, with the bees joining them once there are bees. Ana's soup in her 0 steams too.
- **To test:** in a debug build, **F3** plays the next event in order; the side arc comes after Ana's six.
- **Checked offline:** `python3 tests/check_heart_events.py`.
- **Not in yet:** Wildflower Honey production (the bees), the Starlight Soufflé recipe and its Grand Hotel Inspection bonus, (the Family Table perk works since 24 Nov: cooked meals do a quarter more, `main.gd _eat`), and the framed photo above the mess hall counter (art). The apiary box and glass hive in 6 are narrated (art).
- **Shared place:** Freya's 8 is also in the West Terminal's star dome, on its bench; the siblings' 4 is at the glass by the telescope.

---

## ♥4 The Escape Pod Memory

**Trigger:** the West Terminal's star dome 20:30–midnight (after Evarra's shift; Jasper comes up once the mess hall closes), with both at 4 hearts. *(Moved from the Observation Lounge, Zachary 23 Nov.)*

- *[The West Terminal's little star dome. Starlight falls on Evarra by the glass, turning a small, tarnished metal locket over in her hands.]* *(Zachary, moved)*
- *[She looks up with a gentle smile and makes room for you at the glass.]* *(Zachary, changed: she patted the bench)*
- **EVARRA** *(Zachary)*: "Do you ever look out at the Neutral Zone and wonder where you were meant to land?"
- **EVARRA** *(Zachary)*: "People always do a double-take when Jasper and I call each other brother and sister."
- **EVARRA** *(Zachary)*: "An Ervani and a Vuultam—anyone with a biology chart can tell we aren't blood."
- **EVARRA** *(Zachary)*: "S.A.R.A. told us how we got here. A drifting lifepod during a border skirmish, about twenty years ago."
- **EVARRA** *(Zachary)*: "Two infants wrapped in the same thermal blanket, holding onto each other's hands."
- **EVARRA** *(Zachary)*: "[sad] No registry, no homeworld coordinates. Just each other."
- **CHOICE:**
  - **"Then you found the most important thing first."** (+High Friendship with Evarra)
    - **EVARRA:** "[happy] ...Yes. I suppose we did. Don't tell him I said so. He'll be unbearable."
  - **"Don't you ever want to know where you're from?"** (the wrong one: nothing, and she goes quiet)
    - **EVARRA:** "[sad] ...Sometimes. In the middle of the night."
    - **EVARRA:** "I used to ask S.A.R.A. every year. She never had anything new. So I stopped asking."
- *[Footsteps come up the ramp from the terminal.]*
- **Once the garden dome is restored:**
  - *[Jasper arrives carrying two steaming mugs of herbal tea and a tiny plate of honey-glazed tarts from the garden dome's first harvest.]* *(Zachary)*
  - **JASPER** *(Zachary)*: "I knew I'd find you star-gazing. Look—Merrow let me harvest the first Nectar-Blossoms from the garden dome. Taste this."
  - **EVARRA** *(Zachary)*: "[happy] Jasper... it tastes like real sunlight. Like a meadow I've only ever seen in dreams."
- **Before that:**
  - *[Jasper arrives carrying two steaming mugs of herb tea and a plate of ration-flour tarts, still warm from the oven.]*
  - **JASPER:** "I knew I'd find you star-gazing. Ration flour, a pinch of your lavender, and one drop of Ooma's syrup. Taste this."
  - **EVARRA:** "[happy] Jasper... it's lovely. One day it'll taste like real sunlight. Like a meadow I've only ever seen in dreams."
- **JASPER** *(Zachary; softly, dropping the accent)*: "Wherever that pod came from, Evarra, we landed in the exact right place."
- **JASPER** *(Zachary)*: "[happy] Now come on—if we don't plant those wildflower seeds before morning, you'll never get your bees."
- *(Jasper gets +Friendship for the tea either way.)*

---

## ♥6 Operation Honeybee

**Trigger:** the garden dome 08:00–11:00 on a Wednesday (Evarra's day off, and the day Ooma's ship comes in), once the dome is restored, with both at 6 hearts, after 4. Gameplay unlock: Wildflower Honey. *(The Honey-Lavender Brioche is Evarra's own 6.)*

- *[The garden dome in full bloom. Beside the wildflowers stands a new wooden apiary box Tobbin built, and a glass-walled travelling hive.]* *(Zachary)*
- *[Ooma brought the hive in on her ship this morning. Jasper, Merrow and the station kids watch nervously from a few paces back.]* *(Zachary, changed: Ooma for Eshu)*
- *[Jasper is wearing an oversized welding helmet from Tikka's shop.]* *(Zachary)*
- **JASPER** *(Zachary)*: "[surprised] Are you certain these Earth honeybees recognize the Landing Accord, Evarra? They look remarkably armed!"
- **CHOICE:**
  - **"Take the helmet off, Jasper. You're scaring them."** (+Friendship with both)
    - **EVARRA** *(Zachary, adapted)*: "[happy] Thank you. Listen to our neighbor, Jasper. Bees only sting when they're frightened. Watch."
    - *[Jasper sheepishly lifts the helmet off. His ears pop back up.]*
  - **"Keep it on. They do look armed."** (the wrong one)
    - **EVARRA:** "[sad] Bees only sting when they're frightened. And a talking welding helmet is very frightening. ...Watch."
- *[Evarra unlatches the hive gate. A soft golden hum fills the dome as dozens of fuzzy, lunar-adapted honeybees drift out.]* *(Zachary)*
- **If you told him to keep the helmet on:**
  - *[One bee bounces off Jasper's helmet with a loud tink, spins round, and stings you on the hand.]* (−10 energy)
  - **JASPER:** "[sad] ...I will take the helmet off now."
- *[They circle the Nectar-Blossoms, then settle, one by one, on Evarra's outstretched hand.]* *(Zachary)*
- **PIP** *(Zachary)*: "Whoa... they're tiny starships!"
- *[Evarra turns to you, eyes bright with tears.]* *(Zachary)*
- **EVARRA** *(Zachary)*: "[happy] All my life I dreamed of a garden with flowers and bees. Thank you for helping wake this dome back up."
- **EVARRA** *(Zachary)*: "[happy] Today, Echo Landing finally feels alive."
- **Unlocked: Wildflower Honey** *(Zachary)*

---

## ♥10 A Table for the Whole Sector

**Trigger:** the plaza fountain 18:00–21:00 in autumn or winter, after the pod memory (4), with both at 8 hearts. Everyone who has arrived on the station is there. Rewards: the Starlight Soufflé recipe, the Family Table perk and a framed photo above the mess hall counter.

- *[A starlit banquet around the fountain. Every resident shares one long table laden with fresh bread, pastries, roasted roots and sparkling cider.]* *(Zachary)*
- *[Jasper rings a little silver bell. Evarra brings out a towering honey-and-berry cake decorated with edible star-flowers.]* *(Zachary)*
- **JASPER** *(Zachary)*: "[happy] When Evarra and I arrived on this station, we had nothing but a tin of ration cubes and a flickering holo-vid."
- **JASPER** *(Zachary, "every neighbor" for "twenty-eight neighbors")*: "[happy] Tonight, we feed travelers from three empires and call every neighbor family!"
- **JASPER:** "[happy] And tonight's soufflé comes from no holo. Our honey, the caverns' truffles, and a little nerve. Paris never tasted anything like it." *(Claude: the critic's run, which unlocked it, is cut)*
- **Recipe: Starlight Soufflé & Lunar Truffle Glaze** *(Zachary's reward from the cut 8: a big boost at the Grand Hotel Inspection, Spring 24)*
- **EVARRA** *(Zachary)*: "[happy] You gave me my garden, and you gave my brother his kitchen."
- **EVARRA** *(Zachary)*: "[love] No matter where we came from before that escape pod, this is our home forever."
- *[The whole station cheers around the fountain as fireflies and honeybees drift beneath the dome.]* *(Zachary; no bees before 6)*
- **Perk: Family Table (cooked meals restore 25% more health and energy)** *(Zachary)*
- **A framed photo of Jasper, Evarra and you now hangs above the mess hall counter** *(Zachary)*

---

## Still open

- **Wildflower Honey production**, the soufflé recipe and its Grand Hotel Inspection bonus, and the Family Table perk need the cooking and bee systems in the game; for now they're flags.
- **Art** (on the Art Fix List, 23 Nov): the apiary box and glass hive (6), the banquet table (10), the framed photo above the mess hall counter (10), and sprites for the bees and fireflies that are drawn in code for now.
- **The Grand Hotel Inspection** (Spring 24) itself isn't in the calendar yet.

---

## Cut (Zachary, 23 Nov: side arcs are three scenes)

Kept here for the record. They're Zachary's scripts ("Heart Events: All Romances", Part 1), so they could come back as something else: the béchamel as a day line, say, or the critic's run as part of the Grand Hotel Inspection. The code for both is in git history (`siblings_2`, `siblings_8`, before 23 Nov's trim).

### ♥2 Haute Cuisine on a Ration Budget (cut)

**Trigger:** the mess hall 13:00–14:30 on a Monday, Thursday or Friday (both work; Jasper goes on his break at 14:30), with both at 2 hearts.

- *[The mess hall kitchen. Smoke curls from a simmering pot while a holo-projector plays a crackling old video of a Parisian bistro.]* *(Zachary)*
- *[Jasper is furiously whisking a grey paste in a steel bowl, his fox ears flat. Evarra snips leaves from one potted herb onto ration biscuits.]* *(Zachary)*
- **JASPER** *(Zachary)*: "[angry] Non, non, non! Look at the viscosity, Evarra! In the old Earth holos, Chef Laurent's béchamel flows like liquid silk!"
- **JASPER** *(Zachary)*: "[sad] Mine looks like Tikka's hull sealant!"
- **EVARRA** *(Zachary)*: "[happy] That might be because Chef Laurent had butter, cream and flour, Jasper—and we have dehydrated soy-paste and reclaimed water."
- **JASPER** *(Zachary)*: "[happy] Ah, mon ami! Tell me honestly—does this smell like a candlelit terrace overlooking the Seine, or like boiled cardboard?"
- **CHOICE** *(Zachary)*:
  - **"It smells... ambitious. Maybe add some of Evarra's herbs?"** (+Friendship with both)
    - *[Evarra sprinkles a pinch of her herbs into the bowl. Jasper sniffs it, and one ear lifts.]*
  - **"Honestly, it looks a little like hull sealant."** (+Friendship with Evarra only)
    - *[Jasper laughs ruefully and sets the whisk down. His ears stay flat.]* *(Zachary's "laughs ruefully")*
  - **"It's the passion behind the dish that counts."** (+Friendship with Jasper only)
    - **JASPER:** "[happy] Passion! You hear that, Evarra? Passion!"
- **EVARRA** *(Zachary)*: "[happy] See? Even our newest neighbor agrees. You don't need Earth butter to make people feel at home, little brother."
- **JASPER** *(Zachary)*: "[surprised] Little brother?! Evarra, we were found in the same escape pod—we have no idea who hatched or was born first!"
- **JASPER** *(Zachary)*: "Besides, one day I will serve a true Parisian feast right here on Echo Landing. You'll see!"

### ♥8 The Critic's Practice Run (cut)

**Trigger:** the hotel's dining room 21:30–midnight, after the last service, with both at 8 hearts. Until the hotel opens (after Ivan's fall), the mess hall instead. Gameplay unlock: Jasper's signature dish, *Starlight Soufflé & Lunar Truffle Glaze*: a big boost at the Grand Hotel Inspection (Spring 24).

- *[The hotel's dining room after the last service, transformed: white linens from Sesska, warm lanterns from Tobbin, polished glassware.]* *(Zachary, moved; "the mess hall" before the hotel opens)*
- *(Jasper paces frantically up and down in front of the counter: shown, not narrated.)* *(Zachary)*
- *[Rusk sits at a corner table as a test judge, with S.A.R.A.'s little holo-emitter glowing beside his plate.]* *(Zachary)*
- **Once the hotel is open:**
  - **JASPER** *(Zachary, changed for the season)*: "[shocked] The Grand Hotel Inspection comes every spring! If Vaelen writes that we serve 'frontier gruel', S.A.R.A.'s five-star dream is ruined!"
- **Before that:**
  - **JASPER:** "[shocked] S.A.R.A. wants a critic here the night the hotel opens! If Vaelen writes that we serve 'frontier gruel', her dream is ruined!"
- **JASPER** *(Zachary)*: "Everything must be authentic Parisian perfection!"
- **S.A.R.A.** *(Zachary)*: "[happy] Calm your whiskers, Jasper. True Parisian hospitality is not rigid imitation."
- **S.A.R.A.** *(Zachary)*: "It is celebrating the finest ingredients of the region you inhabit."
- **CHOICE** *(Zachary)*:
  - **"Blend French technique with our lunar crops and honey."** (+High Friendship with both; the dish now)
    - *[Jasper pauses, looking from Evarra's honey jars to the fresh cavern truffles on the counter.]* *(Zachary)*
    - **JASPER** *(Zachary)*: "[surprised] You're right... Why pretend we're on Earth when we have flavors no Parisian chef has ever dreamed of?"
    - **JASPER** *(Zachary)*: "[happy] Evarra—pass me the cavern truffles and the wildflower honey!" *(before the bees: "Ooma's star-blossom honey")*
    - *[A soufflé rises, golden and shining, glazed with truffle and honey. Rusk takes one bite and puts his fork down very slowly.]*
    - **S.A.R.A.:** "[happy] Five stars. I am not programmed to say that lightly."
    - **Recipe: Starlight Soufflé & Lunar Truffle Glaze** *(Zachary)*
  - **"Stick to the holo-recipe. You've practiced it a hundred times."** (the wrong one: no friendship, and no dish yet)
    - *[Jasper follows the holo-recipe to the gram. The soufflé rises... wobbles... and sighs flat in its dish.]*
    - **S.A.R.A.:** "Technically flawless. Joyless. Vaelen will call it 'competent'."
    - **JASPER:** "[sad] Competent. The worst word in any language."
    - **EVARRA:** "[sad] We'll try again, little brother. With our own honey next time."
    - *(He works the dish out on his own and serves it at the banquet; the recipe unlocks there.)*
