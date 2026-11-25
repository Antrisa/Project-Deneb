# Echo Landing: story arcs and heart events (review, 22 Nov 2026)

Every story beat and heart event in one place, with how much of each is written and what needs Zachary's call. Written by Claude for review from:

- Drive: "NPC Master" (19 Nov), "Heart Events: All Romances (merged)" (19 Nov), "Lore Bible V4", "Game Opening & Prologue Script", "Custodian Bundles", "Master NPC Relationship & Heart-Event Bible" and "Character Relationship Map" (both superseded, used only for scenes nobody has rewritten);
- the game on `art24` (`6b80217`): the first and second flights and the arrivals in `scripts/main.gd`.

The full scripts that exist are copied next to this file: [`ROMANCE_SCRIPTS.md`](ROMANCE_SCRIPTS.md) and [`PROLOGUE_SCRIPT.md`](PROLOGUE_SCRIPT.md). The Drive docs stay the source of truth until Zachary says otherwise.

**The courier is Eshu.** The Drive docs renamed him on 19 Nov, and on 23 Nov (Zachary) the game, the repo docs, the Project and the rest of the Drive followed. His file id `tally` stays (art and saves).

**The pirates are the Chernobog** (Zachary, 23 Nov). **Ivan himself is "the Rabble"**, so the Rabble's Reach and the Rabble's Nest keep their names. Ids and files stay `rabble_*`.

**The Sky-Weavers are a sentient nebula** (Zachary, 23 Nov): the main story's ending reveals it, and that should end the Zaa'sh hatred of AI, since their own gods were never ordinary living things either. "Sky-Weavers" is only the Zaa'sh name for them. They have no name we could understand (Zachary, 24 Nov): they are a higher form of life, and the Custodians have to "dumb everything down" for us. "Starborn" stays the human scholars' word. **The main story is now the Custodians: see [`CUSTODIANS.md`](CUSTODIANS.md)** (24 Nov). Tar'Besh, the exiled cleric who first guessed it, is the thread that leads there (section 5.2).

**The Scyldar are an ocean people** (Zachary, 23 Nov), and Zaas names the underground sea **the Merrow Deep**, after Merrow (section 5.3).

**How far each scene is written:**

- **Script:** a full scene: setting, dialogue, choices and what they give.
- **Short:** a setting and one to three lines; no choice, no ending.
- **Outline:** one or two sentences of what happens.
- **(Claude):** a placeholder Claude made up; Zachary hasn't approved it yet.
- **In game:** already playable, with lines written in the code.

Review notes are marked by kind: **Clash** (two sources disagree), **Lock** (breaks the hard-lock rule or can't play when it should), **Gap** (something missing), **Repeat** (the same beat twice), **Idea** (Claude's suggestion, nothing decided).

---

## At a glance

| | Events | Script | Short | Outline |
|---|---|---|---|---|
| Romance arcs (9 × 5) | 45 | 17 | 10 | 18 |
| Jasper & Evarra side arc | 5 (3 since the trim) | 5 | 0 | 0 |
| Platonic arcs (10 × 4) | 40 | 0 | 0 | 40 (five are only a reward, no scene) |
| **All heart events** | **90** | **22** | **10** | **58** |
| Prologue | 4 | 4 | 0 | 0 |
| Main story beats after the prologue | 15 | 5 in game | 0 | 10 |
| Holidays and calendar events | 9 | 0 | 0 | 9 |

*(The table is the review as of 22 Nov. Since then (23 Nov): every pair and family member gets an arc of their own, side arcs are 2–3 scenes, and the two side arcs so far were trimmed to three each.)*

Not written at all yet: the nine friendship endings for the 8-heart confessions, the accept and decline replies to each confession, the wedding cutscene, break-up reactions, birthday lines, and scenes for the five platonic 8-heart rewards that only have a reward.

**The biggest findings:**

1. **Four big story threads open and never close:** the Terran hardliners who want S.A.R.A. back or destroyed, the Junta and the waking Custodians, Pip's missing parents, and who took Artie in 2036. Section 1.3.
2. **The docs and the game tell Ivan's ending and Ana's mutiny differently** (pirate base raid vs Ivan's flagship; a civilian freighter vs revenge). Section 1.2. (Ana's part settled 23 Nov: the game's version, with her crew always calling her weak for never firing on transports.)
3. **Every 10-heart romance scene and every platonic scene is an outline.** (All nine romance arcs are now written and in the game: Freya, Jasper, Evarra, Job, Quill, Ix'ali, Artie, Stu and Ana; so are the Jasper & Evarra side arc and the platonic arcs of S.A.R.A., Tar'Besh, Zaas, and Vzz'ket & Rusk.)
4. **Five events break the hard-lock rule** (8s must never wait): Jasper & Evarra 8 waits for the hotel; Stu 8 needs the hotel lobby; Evarra 8 and Artie 8 and 10 need the East orchard. Stu's 2 and 6 need the hotel too. Section 7.3. (All settled: the hotel opens after Ivan's fall, before Stu arrives, and the siblings' 8 plays in the mess hall until then.)
5. ~~**Two "first bees" scenes**~~ Settled 22 Nov: the bees are the siblings' 6; Evarra's 6 is a wildflower border.
6. **The code counts hearts three ways:** `main.gd` says 10 points a heart, `ui.gd` says 5, the NPC Master says 100. Section 7.2.
7. **Eleven scenes were in the Observation Lounge**, including three 10-heart milestones and Ana's confession, all at night under the stars. (Eight now: Quill 10 moved to the little park, Ix'ali 10 to the museum and Stu 10 to the terminal airlock; Artie 6 and Ana 8 stay.)

---

## 1. The main story

### 1.1 In the order a player meets it

| # | Beat | Trigger | Status | Notes |
|---|---|---|---|---|
| 1 | **Prologue 1: The Ambush in the Dark.** Ivan the Rabble ambushes your corvette; blind jump. | New game | Script ([PROLOGUE_SCRIPT.md](PROLOGUE_SCRIPT.md)) | Clash: the prologue's ship is "the *Wandering Star*", a rookie bounty hunter's corvette; the game's ship is a fighter. |
| 2 | **Prologue 2: the crash and the Mother-Drone.** You fall through the crust; the dying Precursor Mother-Drone imprints the Lexicon ("Tend the small worlds"). | | Script | |
| 3 | **Prologue 3: Medbay cutscene, then Reception.** Maren and Quill; S.A.R.A. puts you in quarantine in the old barracks (the future hotel). | | Script | Quill notes "a brief electromagnetic spike" in your scans. Nothing picks this up later (Gap). |
| 4 | **Prologue 4: the Reliquary.** Touching the crystal wakes the Chancellor, the Sovereign and the Forgemaster at once. Tar'Besh asks you to keep it secret from the Junta. | | Script | See the note on "awaken" below. |
| 5 | **Quarantine, settling in, repairing the ship in stages.** | Day 1 on | In game | |
| 6 | **First flight:** ice field, the Patient Wren, the Chernobog picket, the Moogli trader, Ivan's flagship. Ivan goes down with his ship; a stasis pod tumbles out of his hold and you tow it home. | Ship repaired | In game | Clash: the docs say Artie is found "at the pirate base" and that Wave 1 comes "after the pirate base raid". |
| 7 | **Wave 1:** Artie wakes in the Medbay (D+1), the first visitor transport brings Stu (D+2), Artie moves into East Home 1 (D+3), Eshu asks for a berth (D+4). D is the day Ivan falls. | Ivan's fall | In game (placeholder lines) | |
| 8 | **Second flight:** Ana drops out of fold to avenge Ivan; at half hull her crew turn her turrets on her own bridge; you beat their gunship and pull her out. Her loyalists: "We always knew you were weak. Never once fired on a transport." | Next flight | In game | Settled 23 Nov (Decision 2). |
| 9 | **Wave 2:** Ana in the Medbay, Garrick at the door; East Home 3 two days later. | Rescue | In game | |
| 10 | **Restoring the first three Custodians** (any order; Sovereign and Chancellor tuned for Spring and Summer, Forgemaster for Summer). | Bundles | Outline (bundles doc) | |
| 11 | **Echoes in the Violet Static.** S.A.R.A. links the nano-fluid to the dead Mother-Drone. | First Custodian | Outline | |
| 12 | **The Secret of Annex 4.** Owen decodes S.A.R.A.'s naval logs: how she defied her self-destruct order. | Museum tape and cipher key donated | Outline | Repeat: S.A.R.A. 2 already tells you this. |
| 13 | **Refugee Night.** A Collective freighter fleeing pirates limps in; the station shelters its passengers overnight. | Two wings restored | Outline | |
| 14 | **The Chitin Exodus.** Vzz'ket and Job see crawlers migrating upward as a Starborn geo-seal cracks. | "Mine Level 5" | Outline | Clash: the caverns are now rock 1–15, lush 16–24, water 25–45. Floors 16–24 fit. |
| 15 | **First Light on the Subterranean Sea.** The Harbinger's crystal explodes on floor 25; floors 25–45 flood; the hot springs open. | Harbinger | Outline | |
| 16 | **The Leviathan** (name is still a placeholder). The sea-monster boss on floor 45. | Floor 45 | In game (fight only) | Renamed 22 Nov: the game called it "the Harbinger", which is the Custodian's name. In the game it guards the stair to the underground lake. |
| 17 | **The Starborn Convergence.** All four crystals reveal the Starborn. | All four Custodians | Outline | |
| 18 | **The Great Museum Gala.** Monument to all seven species; the Archivist's Signet. | All 30 artifacts | Outline | |
| 19 | **The Neutral Zone Summit.** Envoys from all three powers sign a neutrality charter at Echo Landing. | Year 2 and a 5-star hotel | Outline | The only ending beat. |

Also in the docs but not on this list: the yearly Grand Hotel Inspection (section 6), the wedding cutscene (rule 3.5, unwritten) and Ooma's ship, the Nest raid and the pirate strongholds planned for space runs (status doc).

### 1.2 Review notes

- **Clash: how Ivan falls and where Artie comes from.** The game: Ivan dies when his flagship splits, and Artie's pod is in his cargo hold; Wave 1 counts from that day. The docs (NPC Master roster, Custodian Bundles, Lore V4, Stu's script header, Artie 2's trigger): Artie is found "at the pirate base", and Stu comes "after the pirate base raid". The old Relationship Map has a third version: Ivan raids Echo Landing and Garrick and Ix'ali lead the defence. The space-combat plan also has a one-time "Nest raid" on a pirate stronghold, which could be the pirate base. Decision 1.
- ~~**Clash: Ana's mutiny.**~~ Settled 23 Nov (Decision 2): the game's version stands (revenge, then her crew turn on her), and the crew always "knew" she was weak because she never once fired on a transport. Ivan covered for her. Her first scene (the old Ana 2, now her 0) says so, and so do the loyalists in the second flight.
- ~~**Clash: what the pirates are called.**~~ Settled 23 Nov (Decision 3): the pirates are the Chernobog; Ivan is the Rabble. The game's text says Chernobog cutter, Chernobog colours and so on; the Rabble's Reach and the Rabble's Nest are named after Ivan.
- **Clash: "awaken" or "restore".** Prologue scene 4 wakes all three crystals at once and they talk. The bundles doc and the story-event triggers then speak of "awakening" each Custodian ("1st Custodian Awakened"). Suggest: the prologue wakes them, bundles **restore** their wings, and triggers say "first Custodian restored". Decision 19.
- **Clash: the player's ship.** The prologue's *Wandering Star* loses its rear half in the blind jump; the game has a fighter repaired in the Shuttle Bay. If the fighter is what's left of the *Wandering Star*, one line from Freya or Tikka would settle it. Decision 4.
- ~~**Repeat: S.A.R.A.'s secret.**~~ Gone 23 Nov: her new arc doesn't tell it, so The Secret of Annex 4 is the only place it comes out.
- **Gap: there is no act structure.** Beats are gated by bundles and items, not by a shape across the year. Section 1.4 sketches one.

### 1.3 Threads that open and never close

| Thread | Opened by | Closed by |
|---|---|---|
| **A. The Terran hardliners** want Annex 4 back or S.A.R.A.'s self-destruct carried out. Lore V4 adds Empress Asta, whose father's death is tied to synthetic rights. | Nothing now (S.A.R.A.'s "Ghost Signal" was dropped, 23 Nov) | Nothing |
| **B. The Junta and the Custodians.** "If word reaches Zaa'sh space that sentient constructs are active here, the Junta will send warships." | Prologue 4; Tar'Besh 6 (he lies to the Temple about the crystals, 23 Nov) | Nothing yet; the Sky-Weavers' reveal at the end should end the Zaa'sh hatred of AI |
| **C. Pip's parents** ~~are alive in Collective space~~. **Decided 24 Nov (Zachary): they're dead**: their freighter's drive failed between stations, nobody's fault. Pip knows, but not how. | Pip 2, Owen 4 (the Kestrel's recorder), the family's side arc | **Closed:** the family's side arc 6 (Lanterns), where Maren and Owen tell Pip how |
| **D. Who took Artie** in October 2036 ("a silent silver light lifted my truck"), and why was his pod in Ivan's hold? A silent silver light sounds like a Precursor drone. | Artie 2 | Nothing |
| **E. The Precursor Lexicon in your head.** Quill's "electromagnetic spike", the Mother-Drone's "Tend the small worlds". | Prologue 2–3 | Only the Custodians talking to you |
| **F. "Something big stirring below."** The giant carapace, the crawlers fleeing upward, the tides Zaas hears. | Vzz'ket & Rusk's side arc 4, Chitin Exodus, Zaas 4 | The Leviathan on floor 45 (decided 23 Nov: it broke the brood-queen's shell in Vzz'ket & Rusk's side arc 4, and its heartbeat is what Zaas hears in his 4) |
| **G. The Chernobog remnants.** "The Chernobog lieutenants scattered." | Ana 2 | Space runs could pick it up (pirate strongholds) |

**Idea (Claude), nothing decided:** the Neutral Zone Summit is where A and B could land. Each power arrives with a claim (the Empire on S.A.R.A. and Annex 4, the Junta on the Custodians, the Collective on its refugees), and how the residents stand with you decides how it goes: S.A.R.A. 6 and Tar'Besh's secret pay off, Eshu (who keeps a private line to every empire and puts the kettle on for rival envoys) gets everyone to one table, and Ix'ali, Ana and Artie each have a side to speak for. D could close earlier, in Year 1, through the Starborn Convergence (C closed on 24 Nov: Pip's parents are dead).

### 1.4 A possible shape for the year (Idea, Claude)

| When | Story | Arrivals |
|---|---|---|
| Spring, Year 1 | Prologue, quarantine, farming and mining, first Custodian restored, Landing Day, first flight and Ivan | Wave 1 |
| Summer | Ana's ambush; second and third Custodians; Refugee Night; Chivalry & Forge Tourney | Wave 2 |
| Autumn | The Chitin Exodus; down to floor 25; the Harbinger; Founders' Fair | |
| Winter | The sea, the Leviathan, the Starborn Convergence; Terran Yule Tide; Winter Lights | |
| Year 2 | Hotel to five stars, the Gala, Ghost Signal's consequences, the Neutral Zone Summit | |

---

## 2. Rules every heart event follows (NPC Master, section 3)

- Each resident has their own hearts; a shared event says whose hearts it needs. Pair arcs need **both** at the level; family arcs name the one member whose hearts trigger each event.
- Platonic residents cap at 8 hearts; romance candidates at 8, or 10 while you're dating them.
- At 8 hearts a candidate confesses; you accept or stay friends. While dating someone, every other candidate's 8 plays its **friendship ending**: same scene, no confession, same perk. Perks come at 8 either way; 10-heart events give a keepsake.
- **Hard-lock rule:** 8- and 10-heart events never wait for story progress (they use a backup place). 2–6-heart events wait only when the unlock is what they're about. A scene that needs a resident who hasn't arrived plays without them. Zaas 6 waits for the Leviathan (the lake is what it's about); his 8 has a backup like every other 8 (23 Nov).

---

## 3. Romance arcs

### 3.1 Jasper (Ervani, Head Chef)

The Paris dream was really a dream of sharing a table. **Reviewed with Zachary on 22 Nov; all five are written and playable.** Full scenes and his week: [`characters/JASPER.md`](characters/JASPER.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Butter Tin (was Burnt Ration Soufflé) | Ooma's stall, Wednesday 14:30–16:30 or Saturday 07:00–09:00 | He's 400 Scrip short of a tin of real Terran butter; he leaves his savings with Ooma as a deposit for the season. | In game (Claude) |
| 4 | Paris on a Screen | Common room on his break | The cooking-show holo-vid came in the pod with them; even his accent is borrowed from it. Evarra teases him. | In game (Claude) |
| 6 | Taste of Paris | Mess hall 06:00–08:30, Monday, Thursday or Friday; once you've harvested Moon wheat | The first real croissant: Ooma's butter and your wheat. Unlocks the Parisian Bistro Menu. | In game (Claude, from Zachary's outline) |
| 8 | A Table of My Own (confession; was Candlelight in the Mess Hall) | His home on his day off (Tuesday or Saturday), 17:00–20:30 | He sets his own table for the first time; the dream was never the city. Friendship ending: Evarra comes home to a third plate. Perk: Sous-Chef's Blessing. | In game (Claude, from Zachary's outline) |
| 10 | Café Étoile | The fountain, 07:00–11:00 (a morning scene, unlike the siblings' evening banquet there) | Opening morning of his café terrace; you're the first customer. Keepsake: an apron with both your names. | In game (Claude, from Zachary's outline) |

- **Decided:** more variety of place (only 6 in the mess hall); butter is Ooma's tin, not an item; the holo-vid came in the pod; days off staggered with Evarra's (he's off Tuesdays and Saturdays, she's off Wednesdays and Sundays), with lines for those days.
- **Still open:** the café terrace needs drawing on the plaza for after 10 (`cafe_etoile` is set); the bistro menu and his perk need cooking and food buffs in the game.
- **For the side arc:** done 23 Nov: only the siblings' 2 stays in the mess hall; their 8 is in the hotel's dining room (the mess hall until the hotel opens) and their 4 in the West Terminal's star dome.

### 3.2 Evarra (Vuultam, Chief Baker & Gardener)

A gardener without a garden, until there is one. **Reviewed with Zachary on 22 Nov; all five are written and playable.** Full scenes and her week: [`characters/EVARRA.md`](characters/EVARRA.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Window-Box Herb | Her herb bench in the mess hall's greenhouse, 09:30–13:00 on a working day | One pot of lavender is the only thing she grows for herself. (Was "in the dead dome": the game has no dead version of the dome.) | In game (Claude, from Zachary's outline) |
| 4 | First Blossom | The garden dome's meadow on her day off; waits for the dome | Real soil, the first wildflowers; she dances barefoot. | In game (Claude, from Zachary's outline) |
| 6 | A Hem of Wildflowers (was Honey & Brioche) | Your field, Wednesday or Sunday morning | She plants Ooma's wildflower seeds round your field for the bees to come. Unlocks Honey-Lavender Brioche. | In game (Claude) |
| 8 | Wildflower Crown (confession) | The orchard at sunset; **backup** before the dome opens: the promenade flower beds | A crown of every flower she's grown. Perk: Green Thumb. Friendship ending has its own line if you're dating Jasper. | In game (Claude, from Zachary's outline) |
| 10 | The Moonlit Bakery | Your kitchen (your flat by the farm), 20:30–23:30, then the little park | You bake a three-tier honey cake together, then picnic with it. Keepsake: the pressed flowers from her crown, framed. | In game (Claude, from Zachary's outline) |

- **Decided:** the first bees are the siblings' 6, so her 6 doesn't wait on Jasper's hearts (Decision 8); 10 is baking then a picnic; she's off Wednesdays and Sundays, Jasper Tuesdays and Saturdays, with lines for those days; her 8 has a backup place (Decision 11, her part); her keepsake is the pressed-flower frame (Decision 14, her part).
- **Still open:** the wildflower border on your field after 6 needs drawing (`evarra_wildflowers` is set); the brioche and Green Thumb need cooking and crop quality in the game.

### 3.3 Freya (Human, Junior Shipwright)

Stepping out of her late father's shadow. **Reviewed with Zachary on 22 Nov; full scenes in [`characters/FREYA.md`](characters/FREYA.md)** (Claude drafts around his lines). **All five play in the game as cutscenes** (`scripts/heart_events.gd`, `scripts/cutscene.gd`; debug F12, or Ctrl+F12 for all of them in a row; F3 was taken by the repair kit).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Stubborn Heating Pump | Engineering, 16:30–17:30 | A jammed valve; Jorvik could tune them by ear. | Script |
| 4 | Dad's Workbench | Her home (East Home 4), at her bench on a weekend | She opens Jorvik's toolbox: his stabilizer plans and the notes on what went wrong. | Script (Claude) |
| 6 | Test Flight | Shuttle Bay at dusk, then past the launch doors; after 4 | The same wobble starts; his note saves it. She joins your crew. Unlocks the Pioneer Stabilizer. | Script (Claude) |
| 8 | Under the Star Dome (confession) | Star dome bench after 20:00 | Jorvik's bench. Perk: Master Mechanic. Accept, decline and friendship endings written. | Script |
| 10 | Christening the Suite | The Suite, opened for the first time since Jorvik died (or outside its sealed door) | ECHO LANDING SHIPWRIGHTS, JORVIK & FREYA; a pendant from his wrench. | Script (Claude) |

- **Decided (Zachary, 22 Nov):** her father, **Jorvik**, died testing an earlier version of the same stabilizer; the Suite has been locked since. She joins your crew after Test Flight. Her events move off the job. She has weekends off, and her week changes as places open: weekend days are in the game (`SCHEDULE_DAYS_RAW` in `tools/build.py`).
- Still open: how long ago Jorvik died, and whether to add the parts request before 6 (not in the game yet).

### 3.4 Job (Human, Heavy Miner)

A quiet man finding home on a moon he never chose. **Reviewed with Zachary on 22 Nov; all five are written and playable.** Full scenes and his week: [`characters/JOB.md`](characters/JOB.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Gumbo in the Breakroom | Engineering crew break room, 16:00–19:00 on a weekday | His granddaddy's Louisiana spice blend. | In game (Zachary's script, replies to the choice by Claude) |
| 4 | Cave-In on Shaft Four | The mine's iron bay, during his shift | He holds the roof up while you dig out Zaas's crate (a choice now). Unlocks the Reinforced Mining Rig quest (flag only). | In game (Zachary's lines, scene by Claude) |
| 6 | Lanterns by the Cavern Sea | The underground lake's shore once the Leviathan is dead; **backup:** the sealed hatch of the mine's flooded stair | Zaas was right. A choice added. | In game (Zachary's lines, scene by Claude) |
| 8 | Quiet Ground (confession) | Hot springs at dusk once the garden dome is open; **backup:** his porch outside East Home 6 | Perk: Bedrock Strength. Accept, decline and friendship endings written. | In game (Zachary's speeches, replies by Claude) |
| 10 | Bayou Under the Stars | The lake's long dock at night; **backup:** the Shuttle Bay windows, with the half-built skiff | Rowing out in the skiff he built with Tobbin. Keepsake: a carved oar charm. | In game (Claude) |

- **Decided (Zachary, 22 Nov):** weekends off, with lines for those days; 6 gets a backup; 10's backup is the Shuttle Bay windows.
- 8's backup moved from the break room (already his 2) to his porch. 4 plays in the mine because cavern floors are random.
- **Still open:** the skiff needs art. (Zaas 8 is a diving bell now, not a skiff, so the two no longer repeat.)

### 3.5 Quill (Vuultam, Medical Assistant)

Maren's shy apprentice finding his own voice. **Reviewed with Zachary on 23 Nov; all five are written and playable.** Full scenes, and his and Maren's weeks: [`characters/QUILL.md`](characters/QUILL.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Spilled Apothecary | Medbay, 11:00–15:00 on Maren's day off | Spilled spore vials; he doubts he's a real medic. | In game (Zachary's script, replies to the choice by Claude) |
| 4 | Field Notes in the Dark | The North Cave past the mine, on his morning off, Vzz'ket on guard | Cavern lichen plus Merrow's aloe. A choice added. Unlocks Xeno-Salve. | In game (Zachary's line, scene by Claude) |
| 6 | Doctor's Orders | The mine head, weekday afternoons | He treats Job's arm without a tremor; Maren puts his name on the clinic door. | In game (Zachary's lines, scene by Claude) |
| 8 | Heartbeat (confession) | The library in the evening | A pressed glowing-fern bookmark. Perk: Guardian Medic. Accept, decline and friendship endings written. | In game (Zachary's speeches, replies by Claude) |
| 10 | Constellation Study | The little park in the East complex at night | A new glowing species, named after you; a stethoscope-compass charm. | In game (Claude) |

- **Decided (Zachary, 23 Nov):** Quill and Maren stagger two days off each (Quill Monday and Saturday, Maren Thursday and Sunday), with lines to match; 4 in the North Cave; 6 at the mine head; 8 in the library; 10 in the little park (one fewer Observation Lounge scene).
- **Still open:** the clinic-door sign and the glowing plant need art; thread E (the "electromagnetic spike" in your scans) could still come back in one of his scenes.

### 3.6 Ix'ali (Zaa'sh, Armourer)

Junta steel, Earth chivalry: honour means protecting the weak. **Reviewed with Zachary on 23 Nov; all five are written and playable.** Full scenes, and her and Garrick's weeks: [`characters/IXALI.md`](characters/IXALI.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Steel & Chivalry | Armoury forge, while Garrick is out | Earth knights who swore to shield the weak. Replies to the choice added. | In game (Zachary's script, replies by Claude) |
| 4 | The Relic Blade | Museum, Precursor gallery, with Tar'Besh, on her day off; **no item needed** | Folded lunar titanium; one line of why she left the Junta (Claude). | In game (Claude, from Zachary's outline) |
| 6 | Sparring at the Cavern Gate (was Sparring Under the Dome) | The mine's cavern gate in the evening, Vzz'ket and Garrick watching | A duel with blunted blades. Unlocks the Star-Knight Aegis tier. | In game (Zachary's line, scene by Claude) |
| 8 | The Oath (confession) | Armoury forge after hours | She kneels and offers a star pendant, her shield and her heart. Perk: Chivalric Guard. Accept, decline and friendship endings written. | In game (Zachary's oath, replies by Claude) |
| 10 | Forged in Starlight | Museum after hours, the first settlers' gallery | Matching ceremonial pauldrons. Keepsake: a pauldron. | In game (Claude) |

- **Decided (Zachary, 23 Nov):** Ix'ali and Garrick stagger two days off each (Ix'ali Tuesday and Thursday, Garrick Saturday and Sunday), with lines to match; 4 in the museum with no item; 6 at the cavern gate; 10 in the museum (one fewer Observation Lounge scene).
- **Still open:** Decision 12 (is the star pendant an Oath-Crest you could propose with?); her backstory line in 4 is a placeholder; 6 could still set up the Chivalry & Forge Tourney (Summer 29).

### 3.7 Arthur "Artie" Vance (Human, Wave 1)

Woke up centuries late; finds a second chapter teaching the station's kids. **Reviewed with Zachary on 23 Nov; all six (with a new 0) are written and playable.** Full scenes and his week: [`characters/ARTIE.md`](characters/ARTIE.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 0 | Out of Time (new) | Medbay, once he's awake; then the plaza and the Observation Lounge | You show him round; the stars are all in the wrong places. | In game (Claude, from Zachary's direction) |
| 2 | Centuries Late | Library, mornings, while the kids are at lessons | October 2036, the silver light; his old troop, and three kids who've never seen a campfire. | In game (Zachary's script, the Scouts idea by Claude) |
| 4 | The Junior Scouts | The plaza fountain at lunchtime | The first meeting. Starts the Scouts (Monday afternoons, first-Saturday outings). Unlocks Junior Scout Foraging Reports. | In game (Zachary's line, scene by Claude) |
| 6 | Echoes of 2036 | Observation Lounge, Sunday afternoon or early evening | S.A.R.A.'s 2030s sky with crickets. | In game (Zachary's lines, S.A.R.A. and a choice by Claude) |
| 8 | Campfire Under Glass (confession) | The garden dome's woods by the hot springs at night; **backup:** the little park | Perk: Thrifty. Accept, decline and friendship endings written. | In game (Zachary's lines, replies by Claude) |
| 10 | Merit Badge of the Heart | A Scouts campout in the dome's woods; **backup:** the little park | The kids make you an Honorary Scoutmaster. Keepsake: the badge. | In game (Claude) |

- **Decided (Zachary, 23 Nov):** a 0-heart tour; 2 gives him the Scouts idea; campfire scenes in the dome woods with the little park as backup (Decision 11, his part); his week before and after the Scouts; the silver-light origin (his game lines changed to match).
- **Still open:** thread D: who took him, and how did his pod end up in Ivan's hold? (Decision 5, the second half.)

### 3.8 Stowaway Stu (Moogli, Wave 1)

A drifter who can't remember his name learns that staying isn't a trap.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Packed Bags by the Airlock | Hotel lobby on a guest morning (Friday after the transport; Saturday or Sunday from when you wake) | His duffel bag is packed and hidden behind the fern; he doesn't remember his real name. | In game (Zachary's lines, closing beat by Claude) |
| 4 | The Burgundy Suit | Sesska's weaver shop on his day off (Tuesday or Wednesday) | Sesska fits his bellhop uniform. | In game (Zachary's lines, replies by Claude) |
| 6 | A Name on the Door | Outside East Home 2 (his home), Sunday evening | Tobbin's STU nameplate; he has unpacked. | In game (Zachary's lines, Tobbin and a choice by Claude) |
| 8 | After-Hours Lobby Shift (confession) | Hotel lobby after 21:00 on a Friday or Saturday | Cocoa on the lobby sofa. Perk: Five-Star Partner. Accept, decline and friendship endings written. | In game (Zachary's lines, replies by Claude) |
| 10 | Suite for Two | The terminal airlock at night, where his bag used to wait | A candlelit picnic with S.A.R.A.'s and Jasper's help; a freighter leaves without him; a silver bell. Keepsake: the bell. | In game (Claude, from Zachary's outline) |

- **Decided (Zachary, 23 Nov):** the hotel opens after the Ivan fight, so it's open by the time Stu arrives (Decision 10). Guests come Friday to Sunday and stay three days. Monday he cleans the hotel; Tuesday and Wednesday are his days off. "Change what you think is best": the fern for the bag in 2, East Home 2's door for 6, the terminal airlock for 10, and the rest of his week (`docs/story/characters/STU.md`).
- **Still open (optional):** does the game ever give him his real name back? His 8 says "Being Stu is plenty".

### 3.9 Anastasia "Ana" (Human, Wave 2)

Ivan's sister unlearns that fear is loyalty. **Reviewed with Zachary on 23 Nov; all six (with a new 0) are written and playable.** Full scenes and her week: [`characters/ANA.md`](characters/ANA.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 0 | No Brig, Just Soup (was her 2) | The Medbay the first time you visit after her fight; the Shuttle Bay if you missed her there | Saffi's carrot-ginger soup; why did you pull her out? Her crew always called her weak. | In game (Zachary's script, the lore by Claude) |
| 2 | A Seat at the Table (new) | The mess hall at dinner | Nobody will sit with her until you do; then Freya follows. | In game (Claude, from Zachary's idea) |
| 4 | Grease & Second Chances | Shuttle Bay, 14:00–17:00, Tuesday, Wednesday or Friday | Thrusters with Freya; Garrick says she's earning her berth. | In game (Zachary's script, a choice by Claude) |
| 6 | Ghost of the Crown | Rusk's bar after 20:00 | Ivan before he was a monster. She asks to fly with you as crew. | In game (Zachary's script, replies by Claude) |
| 8 | Co-Pilot's Promise (confession) | Observation Lounge, night | She wants to be your navigator. Perk: Wingmate. Accept, decline and friendship endings written. | In game (Zachary's lines, replies by Claude) |
| 10 | True North | Shuttle Bay at sunset: your ship lifts off, orbits the crater (told over a dark screen) and lands | A star-chart console with both your initials. Keepsake: a flight jacket. | In game (Claude, from Zachary's outline) |

- **Decided (Zachary, 23 Nov):** her 2 plays the first time you meet her after her fight (now her 0); a new 2 in the mess hall where nobody will talk to her until you sit with her; the pirates always "knew" she was weak for not firing on transports (Decision 2); the pirates are the Chernobog and Ivan is the Rabble (Decision 3). Her week, the crew ask in 6, keeping 8 in the lounge and 10's shape were Claude's suggestions, not answered: change any of them.
- 6's choices now give +High Friendship (there are no romance points).
- **Animated (Zachary, 23 Nov):** all six now have poses, emote bubbles and sounds like the other arcs; 8 shows a meteor shower in the lounge's window, and in 10 you board your ship and watch it lift off and land (new scene steps `sky`, `hide`/`show` and `ship`).
- **Still open:** the console in 10 could become a real upgrade on your ship (`ana_true_north_console` is set); Wingmate needs hooking into ship battles.
- ~~**Repeat (for later):** 4 has her charting the old ambush corridors for Eshu's skiffs; Eshu 6 "Safe Routes" was the same work.~~ Gone 24 Nov: Eshu has no heart events.

---

## 4. Jasper & Evarra: the sibling side arc

Needs **both** at the level. All five were full scripts ([ROMANCE_SCRIPTS.md](ROMANCE_SCRIPTS.md), Part 1). **Reviewed with Zachary on 23 Nov, then trimmed to three (Zachary: side arcs are 2–3 scenes, "trim to 3"): the pod memory, the bees and the banquet are playable; 2 and 8 are cut** (their scripts are kept at the end of the character doc). Full scenes: [`characters/JASPER_EVARRA.md`](characters/JASPER_EVARRA.md).

| ♥ (both) | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Haute Cuisine on a Ration Budget | Mess hall kitchen, 13:00–14:30 on Monday, Thursday or Friday | Grey béchamel; "little brother?!" | **Cut** (23 Nov) |
| 4 | The Escape Pod Memory | The West Terminal's star dome, 20:30–midnight (was the Observation Lounge) | Two infants in one thermal blanket, about twenty years ago. Honey tarts once the garden dome is restored, ration-flour tarts before. | In game (Zachary's script, a choice and the early version by Claude) |
| 6 | Operation Honeybee | The garden dome, Wednesday 08:00–11:00, once it's restored | The first bees, brought by Ooma's ship. Unlocks Wildflower Honey. | In game (Zachary's script, a choice and the sting by Claude) |
| 8 | The Critic's Practice Run | The hotel's dining room, 21:30–midnight; the mess hall until the hotel opens | Fusion, not imitation. | **Cut** (23 Nov); the soufflé moved to the banquet |
| 8+ | A Table for the Whole Sector | Plaza fountain banquet, 18:00–21:00 in autumn or winter, after the pod memory | The whole station at one table, and Jasper's own soufflé. Rewards: Starlight Soufflé & Lunar Truffle Glaze, the Family Table perk and a framed photo. | In game (Zachary's script; the soufflé line Claude's) |

- **Decided (Zachary, 23 Nov):** 8 in the hotel's dining room, with the mess hall until the hotel opens (Decision 9); 4 in the West Terminal's star dome (Decision 17), in both versions; Ooma brings the hive; the banquet only in autumn or winter; **wrong choices get small consequences** instead of the same reward.
- **Wrong choices:** in 6 (Claude's new choice), telling Jasper to keep the welding helmet on gets you stung (−10 energy) and no friendship. In 4 (Claude's new choice), asking Evarra whether she wants to know where she's from gets nothing and a quiet Evarra.
- **"Every neighbor"** replaces "twenty-eight neighbors"; "the Grand Hotel Inspection comes every spring" replaces "the Spring Hotel Inspection is weeks away" (and before the hotel opens, the critic is booked for opening night).
- **Still open:** honey production, the soufflé's Inspection bonus and Family Table need the cooking and bee systems; art for the apiary box and glass hive, and the framed photo. Freya 8 is also in the West Terminal's star dome (on its bench; the siblings' 4 is at the glass).

---

## 5. Platonic arcs

All 40 were outlines; S.A.R.A.'s, Tar'Besh's, Zaas's, Vzz'ket & Rusk's and Bram's are written and in the game now (23 Nov); Ooma has none (Zachary). Text is from the NPC Master; where the Master has only a word or two, the older bible's outline is used.

### 5.1 S.A.R.A. (AI, Steward & Concierge)

The hostess who never clocks off. **A new set, decided with Zachary on 23 Nov; all four are written and playable.** Full scenes: [`characters/SARA.md`](characters/SARA.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Lost Property | Reception (her West Terminal pad), 18:00–22:00 | She can see every item guests ever left behind and remembers every owner, but she can't open the drawer. You're her hands. | In game (Claude) |
| 4 | Ask the Concierge | Her plaza pad, weekday lunchtime | Rusk, Bram, Garrick and Pip all need her at once; she starts to glitch and asks you who goes first. | In game (Claude) |
| 6 | Walkabout | The Shuttle Bay, then the plaza fountain and the library | Freya and Tikka build her a portable projector; she stands beside you for the first time and turns a page. | In game (Claude) |
| 8 | Night Shift | Her core on the Survey Level, late at night | The station's heartbeats as lights round her dais; keep watch and she rests for the first time (then every Sunday night). Perk: Concierge Fast-Travel & Station Alerts. | In game (Claude) |

- **Decided (Zachary, 23 Nov):** none of the old four (The Croissant Protocol, Turrets & Velvet Curtains, Ghost Signal, Five-Star Heart); this new set instead. Wrong choices: −20 friendship and a glitch (2), nothing and a hurt Pip (4), a walk that ends early (6), no rest night (8).
- **What it drops:** the Paris dream (Jasper's), her self-destruct secret (the museum tape still tells it, so the old Repeat is gone), her argument with Garrick (Garrick's family 6 owns it now), and thread A (nothing opens it now). The brass bell on the hotel desk is just the hotel's.
- **Her rest night** (`sara_rest`, from 8): Sundays from 23:00 her pads stand by. Her day off, out of the story.

### 5.2 Tar'Besh (Zaa'sh, Cleric & Curator)

The heretic who was sent here to die. **Reviewed with Zachary on 23 Nov; all four are written and playable.** Full scenes and his week: [`characters/TARBESH.md`](characters/TARBESH.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Dust on the Relics | The museum before opening (not Monday or Friday morning) | He flinches at S.A.R.A.'s chime but answers her; Vzz'ket can't. "Everything I was taught says she is an empty mirror." | In game (Claude) |
| 4 | Next Assignment (was The Power Surge) | His flat, at his shrine, in the evening | The Temple's letter meant to kill him; S.A.R.A. was the voice that talked his drifting shuttle in. | In game (Claude, from Zachary's backstory) |
| 6 | The Summons (was Tea in the Survey Suite) | S.A.R.A.'s core, evening | The Temple offers his rank back if he recants and reports her for "cleansing"; he refuses, and lies about the crystals. | In game (Claude) |
| 8 | Every Kind of Mind (was Keeper of the Starborn) | The Sanctum after hours | A plaque to the seven peoples, "and one mind of light", and a blank line for whoever made the relics. Perk: Relic Appraisal (+25% Scrip on donations). | In game (Claude) |

- **Decided (Zachary, 23 Nov):** he was a high cleric sent out as a pilgrim to study the Sky-Weavers' relics; for suggesting they might have been sentient, he was as good as cast out, and too well connected to strip, so he was given a "next assignment" in the Neutral Zone and left to the pirates or hunger. He's uneasy with S.A.R.A. at first but quick to accept her; the conflict is the Temple. His week: the museum shuts on Mondays (his day off) and he prays in the Sanctum on Friday mornings.
- **Settled:** why he was exiled (above); thread B is in his arc now (6); 8's new title doesn't give the Convergence away. Wrong choices: nothing (2, 8), −20 friendship (4, 6).
- He only ever says "Sky-Weavers"; the nebula's true name is still open (see the top of this review).

### 5.3 Zaas (Scyldar, Water Reclamation Officer); Merrow appears

The water officer who was right about the ocean, and gave it to the one who kept the water running while he looked. **Reviewed with Zachary on 23 Nov; all four are written and playable.** Full scenes and his week: [`characters/ZAAS.md`](characters/ZAAS.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Clipboard & Diving Helmet | The East Complex reclamation plant, any day but Sunday | A pipe bursts while he tries his diving helmet on over his hat; you help Merrow shut the valve (or help him with the helmet, and everyone's soaked). | In game (Claude) |
| 4 | Sonar Echoes | The sealed hatch of the mine's flooded stair, in the evening | His hydrophone hears tide, and under it a heartbeat (thread F). Merrow brings soup; he misses the sea of home. | In game (Claude) |
| 6 | First Splash | The lake's south beach; waits for the Leviathan | He dives in, hat and all, and names the sea: the Merrow Deep. | In game (Claude) |
| 8 | Captain of the Deep | The end of the lake's west pier; **backup:** a test dive in the plaza fountain, with Nub | A diving bell from his helmet, a porthole and Job's spare drill motor. Merrow dives first; he pins the water officer's badge on her. Reward: Deep-Sea Sonar Lure. | In game (Claude) |

- **Decided (Zachary, 23 Nov):** the Scyldar are an ocean people, so his search is homesickness, not a hobby; the sea is the Merrow Deep. Claude's rework of the places and the bell (it was a research skiff) was accepted. Wrong choices: soaked and nothing gained (2, −10 energy), −20 friendship (4, 6, 8).
- **His week:** Sunday is his day off and his expedition day: the North Cave with his hydrophone, or the lake once it's open.
- **Linked:** 4's heartbeat, the Chitin Exodus and the brood-queen's shell (Vzz'ket & Rusk's side arc) all point at the same thing below (thread F). Job's "I'll dig him a tunnel" pays off in the bell's drill motor.
- **Closed (24 Nov):** Merrow's own story is her arc in section 5.8 (her 8 is her first day off); this arc gives her the badge and the sea's name.

### 5.4 Vzz'ket & Rusk: their own arcs, and a side arc (The Night Watch)

**Reviewed with Zachary on 23 Nov; all eleven are written and playable** (the side arc was trimmed to three: its 6 is cut and folded into its 8). Each has an arc of his own, and they share a side arc like Jasper & Evarra's (Zachary: "I'm fine with shared side arcs but they need single arcs too"). Full scenes: [`characters/VZZKET.md`](characters/VZZKET.md), [`characters/RUSK.md`](characters/RUSK.md), [`characters/VZZKET_RUSK.md`](characters/VZZKET_RUSK.md) (the side arc).

**Vzz'ket** (Zaa'sh, Cavern Hunter): the guard who never leaves his post.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Back to the Wall | The mess hall at dinner | He eats standing, back to the wall, eyes on the door; a hunter sleeps where the prey comes in. | In game (Claude) |
| 4 | A Blessing for the Spear | The Sanctum, Friday morning | Tar'Besh, who blessed his first spear long ago, blesses a new one; they disagree about S.A.R.A. | In game (Claude) |
| 6 | The Night He Left | His campsite by the cavern gate, late | The Hatching Feast; his clutch-brother Tzz'ar held the tunnel alone. The spear and sword he lends you were Tzz'ar's. | In game (Claude; the camp, Zachary) |
| 8 | The Watch Changes | The cavern gate, morning | You've cleared the caverns (or killed the Leviathan); S.A.R.A.'s motion sensors take the night watch and he accepts her help. Rewards: his first spear (a keepsake for your quarters) and the Cavern Monster Radar. | In game (Zachary's outline, scene by Claude) |

**Rusk** (Ervani, Bartender): the barman whose tall tales cover what he won't say.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Lights That Stay On | The bar in the morning | You hold the ladder; his list: a proper counter, lights that stay on, a sign. | In game (Claude) |
| 4 | Uncle Rusk | The fountain, Monday lunch with Saffi and Kit | A tall tale about his tail for Kit; the true one (a fire, a child carried out) for you. | In game (Claude) |
| 6 | The Sea Chest | His room after closing | Ilsa's sign from his first real bar; she grew the grapes and made the Secret Reserve. | In game (Claude) |
| 8 | The First Page | The bar's front step at closing | A new ledger, your story on the first page; seeds of Ilsa's vine. Reward: Nebula grape seeds; Rusk's cask turns five grapes into a bottle of Nebula wine (sells for 350). | In game (Zachary's reward idea, scene by Claude) |

**The side arc** (both at the level):

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Tall Tales at the Bar | Rusk's bar, late, after Vzz'ket's shift | Rusk's bug-migration routine for Job and Freya; Vzz'ket, sharpening his spear: "They are running." | In game (Claude) |
| 4 | The Broken Shell (was The Nest) | The far east end of the North Cave, in the evening | A crawler brood-queen's shell, broken open from outside by the Leviathan; Rusk takes back about forty jokes. | In game (Claude) |
| 6 | On the House | Rusk's bar on a Friday evening | Rusk apologises in front of everyone and opens the stage. | **Cut** (23 Nov): the apology, the Open-Mic and Vzz'ket's true story are in 8 now |
| 8 | Sentinels of Echo Landing | The cavern gate near midnight, then the bar | Ix'ali's chitin-piercer traps, one of the last bottles of the Secret Reserve, Rusk's apology and the Friday Open-Mic, and Ix'ali on watch; Rusk hangs his sign, THE NIGHT WATCH, and Vzz'ket tells his true story. Reward: Chitin-Piercer Traps. | In game (Claude) |

- **Decided (Zachary, 23 Nov):** the Leviathan broke the shell (thread F); "The Nest" is now "The Broken Shell" (Decision 16); Rusk is not Saffi's uncle but a figure in her family's life; Vzz'ket is old-school Zaa'sh and doesn't like S.A.R.A. at first, but respects Tar'Besh; Vzz'ket's 6 is at his campsite (made up properly), his 8 gives his first spear as a keepsake and ends his guarding night and day; Rusk's 8 gives a seed whose grapes you grow, replant or ferment into wine that sells high. Wrong choices: −20 (and a crawler bite in the side arc's 4).
- **Their weeks:** Rusk has Monday mornings off (the bar opens at 18:00). Vzz'ket has no day off until he's earned one: his nights after his own 8 (Sundays off too), and Friday nights at the Open-Mic after the side arc's 8 (Ix'ali holds the gate).
- **Still open:** the bar's run-down state and its repair (Rusk 2's lamp and the side arc's sign could be steps of it); furnishing your quarters (for the spear); a Fermenter at home (the economy plan has one).

### 5.5 Bram (Ooma: no heart events)

**Reviewed with Zachary on 23 Nov; Bram's four are written and playable.** Full scenes: [`characters/BRAM.md`](characters/BRAM.md). **Ooma has no heart events** (Zachary, 23 Nov: "maybe no heart events for oma shes just a wandering trader"): her own arc and the Bram & Ooma side arc (the old outlines' price war, tip-off and guild) were written and then cut the same day; the drafts are in git history.

**Bram** (Moogli, general store): the shopkeeper who never collects.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Night Pod | The cargo bay's yellow loading pad, late, any night | He sends the station's shipping up in his cargo pod to his cousin Pell on the Moogli trade lanes. | In game (Claude) |
| 4 | Quiet Credit | His stall at opening, not Thursdays | You catch him writing off a stranded freighter pilot's tab: "Your tab? I see no tab." | In game (the NPC Master's outline, scene by Claude) |
| 6 | The Long Column | His flat, Thursday night | The family stops shipping until he collects what he's owed, and he never collects. Tell the others, and his 8 remembers. | In game (Claude) |
| 8 | Paid in Full | The mess hall, Sunday lunch | Tobbin, Freya, Job and Jasper pay him back in kind. Reward: his grandfather's Moogli trade beacon. | In game (Zachary's reward, scene by Claude) |

- **Decided (Zachary, 23 Nov): everyone gets their own arc**, and side arcs are 2–3 scenes (the limit for every side arc from now on).
- **Decided (Zachary, 23 Nov): Bram** is the general store owner: seeds, fertiliser, basic goods and crafting recipes. Through his contacts with other Moogli merchants he sells what you put in your shipping crate: it goes up in his cargo pod overnight. He takes **Thursdays off** and works a **half day on Sunday**, with a quiet jab at a certain other general store: "Only a fool closes on a Wednesday. So: Thursday." His 8's reward: a **Moogli trade beacon** (out in space, spend one fuel to call a store to you; `docs/SHIP_ART_UI.md`, section 8). Upstream's shops shut on a keeper's day off (`main.gd _at_workplace`).
- **Ooma's week:** she still spends Saturday evenings on the Merrow Deep's beach once it's open (a schedule, not a scene).
- **Wrong choices:** −20; in Bram's 6, offering to pay his ledger yourself gets nothing (his pride).

### 5.6 Tikka & Sesska

**Reviewed with Zachary on 24 Nov; all ten are written and playable.** Full scenes: [`characters/TIKKA.md`](characters/TIKKA.md), [`characters/SESSKA.md`](characters/SESSKA.md) and their side arc, [`characters/TIKKA_SESSKA.md`](characters/TIKKA_SESSKA.md). Zachary: the shape "looks good"; Tikka's overworking is "slightly linked" to Jorvik "but not the main reason"; Sesska's linens do "nothing until the hotel is made"; the anniversary is at the hotel if it's open, the mess hall if not; "four hands"; forty years married stays.

**Tikka** (Arachnay, chief engineer): the engineer who can't put the station down.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Tuning the Manifold | Engineering's core, late | A flat note only she hears; you turn the valve. Sesska's dinner is a sculpture. | In game (the NPC Master's title, scene by Claude) |
| 4 | The Kettle Queue | The repair bench by the Manufacturing hub, evening | She fixes everyone's things every night. Let Freya take a lamp (her letter), or Freya is hurt. | In game (Claude) |
| 6 | Sunday Shift | The Shuttle Bay, Sunday morning | Freya has been coming in on Sundays because Tikka does. Jorvik is a thread, not the reason. | In game (Claude) |
| 8 | Overclock | Your front door, Sunday morning | A real day off, with a four-minute visit. Reward: Smelter Overclock (furnaces twice as fast). | In game (the NPC Master's reward, scene by Claude) |

**Sesska** (Arachnay, weaver): a weaver who lost her street and finds a new one.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Every Seam Giving Up | Her shop, morning | She mends your crash jacket, as her first line promised. Letter: a cap from the offcuts. | In game (Claude) |
| 4 | A Window onto a Corridor | Her loom on the promenade | The Landing has no pattern of its own, so she starts one, with Pip, Kit and you. | In game (Claude) |
| 6 | Glow-Spider Silk | The North Cave, evening, with Vzz'ket | The Landing's own thread. Her shop sells the Cavern-silk coat from now on. | In game (Claude) |
| 8 | Void-Silk | Their home, late | She cuts her grandmother's last void-silk. Reward: Void-Silk Luxury Linens (for the hotel, no effect until it takes guests). | In game (the NPC Master's reward, scene by Claude) |

**Side arc, "Forty Years"** (both at the hearts):

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 4 | EVA Workwear | Sesska's shop after closing | Tikka's suit tore on the hull; they design workwear together and you settle it. | In game (the NPC Master's outline, scene by Claude) |
| 6 | The Anniversary | Tikka's bench in the morning; the hotel's dining room that evening (the mess hall before the hotel opens) | Tikka forgot; you pull a dinner together in a day. Her coil-wire music box. Letter from both. | In game (the NPC Master's outline, scene by Claude) |

- **Their weeks:** Sundays off together (until her 8 Tikka slips into Engineering on Sunday mornings); Tikka covers launch control on Saturdays; Sesska buys fibre from Evarra on Wednesday afternoons, and takes linens to the hotel on Thursdays once it's open.
- **Still open:** the hotel's income (the linens perk waits for it); art for the glow-spiders, the Landing pattern and the anniversary table (Art Fix List).

### 5.7 Maren, Owen & Pip

**Reviewed with Zachary on 24 Nov; all fourteen are written and playable.** Full scenes: [`characters/MAREN.md`](characters/MAREN.md), [`characters/OWEN.md`](characters/OWEN.md), [`characters/PIP.md`](characters/PIP.md) and the family's side arc, [`characters/MAREN_OWEN_PIP.md`](characters/MAREN_OWEN_PIP.md). Zachary: **Pip's parents are dead** (Decision 7): their freighter's drive failed, "nobodys fault bad things happen somtimes"; Pip knows, "not the details, but he knows"; his 8's reward is "a toy rocketship piece of furniture". Claude's suggestions taken for the rest: an arc each plus a two-scene side arc; Tam and Ines (and the Kestrel) as placeholder names; the Lore Compendium waits for a codex system.

**Maren** (human, the station's doctor): the doctor who came here to stop leaving.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | House Calls | The East Complex after dinner | Her rounds, Job's back first. She didn't really come to retire. | In game (Claude) |
| 4 | A Hot Cup of Tea | The common room, her Thursday off | You keep Pip, Quill and Job away; her first hot tea in thirty years. Tam used to bring her tea. | In game (Claude) |
| 6 | Letting Go | The corridor to the Survey lift, a weekend morning | Pip goes up on his own. His Saturdays change. | In game (the NPC Master's title, scene by Claude) |
| 8 | Med-Stims | The Medbay after hours, with Quill | The old ship's recipe. Reward: Advanced Med-Stims (medpacks heal twice as much). | In game (the NPC Master's reward, scene by Claude) |

**Owen** (human, the librarian): the man who keeps everyone's story.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | One Novel | The library, morning lessons | The Terrans' only novel, and you do the voices. | In game (Claude) |
| 4 | The Freighter Log | The cargo bay by Bram's pod, late | Pell found the Kestrel's recorder. Tam's last log. Nobody's fault. | In game (the NPC Master's title, scene by Claude) |
| 6 | Pip's Book | His study at home, a weekend afternoon | The book he's writing Pip about his parents, and how to end it. | In game (Claude) |
| 8 | The Compendium | The museum after closing, with Tar'Besh | Reward: the Library Lore Compendium (waits for codexes). | In game (the NPC Master's reward, scene by Claude) |

**Pip** (nine): knows where everything is.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Pip in the Archive | The library after closing | Looking for the Kestrel in the register. "Nine is older." | In game (the NPC Master's title, scene by Claude) |
| 4 | Lost and Found | The fountain plaza | His secret crate of everything people drop, given back. Letter: a geode. | In game (Claude) |
| 6 | Except Mine Will Work | Your cockpit in the Shuttle Bay, Saturday | Mum was a pilot. He'll check the drive every single time. | In game (Claude) |
| 8 | Checked Twice | Your front door, a weekend morning | Reward: Pip's toy rocket, a piece of furniture. | In game (Zachary's reward, scene by Claude) |

**Side arc** (all three at the hearts):

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 4 | Sunday Dinner | Their flat, Sunday evening | Owen's stew, Pip's whistle, the photo on the shelf. | In game (Claude) |
| 6 | Lanterns | The West Terminal's star dome, the anniversary | Pip asks how, and they tell him. Three lanterns at the glass. Letter from Pip. | In game (Claude) |

- **Their weeks:** Owen's Saturdays off with Pip (the star dome, the fountain). After Maren's 6, Pip's Saturday afternoons are his own: the launch booth with Tikka.
- **Still open:** codexes for the Compendium; art for the toy rocket (a stand-in now), the lanterns and the photo.

### 5.8 Tobbin, Merrow & Nub

**Reviewed with Zachary on 24 Nov; all fourteen are written and playable.** Full scenes: [`characters/TOBBIN.md`](characters/TOBBIN.md), [`characters/MERROW.md`](characters/MERROW.md), [`characters/NUB.md`](characters/NUB.md) and the family's side arc, [`characters/TOBBIN_MERROW_NUB.md`](characters/TOBBIN_MERROW_NUB.md). Zachary: Tobbin's 4, 6 and 8 **wait for the trees** (the garden dome; an exception, like Zaas's 6 and 8); his 8 is **a real chair and its crafting recipe**; **he sells furniture in his shop**, shut on Sundays; **Merrow has the weekend off after her 8**. Claude's suggestions taken for the rest: an arc each plus a two-scene side arc; Nub's 8 a framed drawing; Hydro-Boost as the NPC Master has it.

**Tobbin** (Moogli, furniture maker): a station that has never had a plank.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Plastic and Steel | His workshop, a working day | A plastic leg snaps; you hold the frame while he pins it. His grandmother's bluebark chairs creaked hello. | In game (the NPC Master's title, scene by Claude) |
| 4 | First Real Wood | The garden dome, Sunday morning; **waits for the dome** | Merrow prunes a limb off the oldest tree. His shop sells planks from now on. | In game (the NPC Master's title, scene by Claude) |
| 6 | A Wooden Starship | Their flat after Nub's bedtime; after the dome | He carves Nub a toy ship from the offcut; you keep Nub from seeing it. | In game (the NPC Master's title, scene by Claude) |
| 8 | A Chair That Stays | His workshop, with Merrow and Nub; after the dome | The first real-wood chair. It's yours; he teaches you the joints. It creaks hello. Reward: the heirloom chair and its recipe. | In game (Zachary's reward, scene by Claude) |

**Merrow** (Moogli, hydroponics; does Zaas's water work): learning to stop.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Filter Day | The plaza fountain at dawn | Every drop on the Landing goes through it. Hair, crayons, a dinosaur. | In game (Claude) |
| 4 | Star-Tomatoes | Behind the reclamation plant's last air scrubber | Her secret tomatoes, on her own water ration, for Nub. | In game (Claude) |
| 6 | Dry Week | The reclamation plant, late | A split membrane; the fountain comes back. "I'm your baby." | In game (Claude) |
| 8 | A Day Off | The Observation Lounge, Saturday | Tobbin took her off the rota. Reward: Hydro-Boost (beds grow 20% faster). Weekends off from now on. | In game (the NPC Master's reward, scene by Claude) |

**Nub** (Moogli, their son): draws everything, so it's remembered.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | I Drew You | The plaza, afternoon | You, the tall one, and a sad ship on fire. | In game (Claude) |
| 4 | The Fountain Edge | The fountain, with Kit and Merrow | His first jump (or, dared, backwards into the water). | In game (Claude) |
| 6 | Junior Curator | The museum, with Tar'Besh | Drawings taped under every label. Junior Curator, Fridays, with pins. | In game (Claude) |
| 8 | Framed | Their flat after dinner | The next drawing, framed in the chair that broke. Reward: Nub's drawing, to set down at home. | In game (Claude) |

**The side arc** (all three need the hearts):

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 4 | Bath Night | Their flat, Wednesday or Saturday evening | Nub hides; he gets in if you tell him about the crash. Twice his size, dry. | In game (Claude) |
| 6 | The First Tree | The garden dome, Sunday morning; **backup:** the tub in their flat | The bluebark seed from Tobbin's grandmother, eleven years in a drawer. Its name is Tree. | In game (Claude) |

- **Closed:** the 8 that ran on Merrow's hearts with Tobbin's story (each has an 8 now), and the wood (the garden dome's pruned limb, not the East orchard).
- **Tobbin's shop:** the hotel's furniture ready-made, and real-wood planks after his 4. **Recipes can be taught** now (`"learn"` and `"teacher"` in `item_data.gd RECIPES`).
- **Their weeks:** Tobbin's Sundays (home bench, the garden or the dome's trees); Merrow's weekends after her 8; Nub's Sunday drawing, and his Fridays at the museum after his 6.
- **Still open:** art for the heirloom chair, the planks and Nub's drawing (stand-ins); Merrow's weekends aren't on the station calendar (its days off are fixed).

### 5.9 Garrick, Saffi & Kit

**Reviewed with Zachary on 24 Nov; all fourteen are written and playable.** Full scenes: [`characters/GARRICK.md`](characters/GARRICK.md), [`characters/SAFFI.md`](characters/SAFFI.md), [`characters/KIT.md`](characters/KIT.md) and the family's side arc, [`characters/GARRICK_SAFFI_KIT.md`](characters/GARRICK_SAFFI_KIT.md). Zachary: "every character has own arc plus a short family shared arc". Claude's first suggestions taken for the rest: Garrick was security officer on the refugee transport that crash-landed here, and a bounty hunter he let dock brought a Chernobog cutter down on it; Kit's beacon leads to a smuggler's cache, and his 8 is a deputy badge. Then Zachary changed the two rewards: Garrick's 8 was "too powerful" (the station's guns softening up your first fight), so it's a self-defence class where boarders take extra damage on your ship; Saffi's 8 is a longer energy bar (it was a Sunday potluck buff).

**Garrick** (human, security chief and quartermaster): checks every seal himself.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Signed For | The armoury, a working day | Everything sharp is signed for, yours too; twelve bounties, and the people near them. | In game (Claude) |
| 4 | The Rounds | The West Terminal's airlocks at night | The transport, the bounty hunter he let dock, and the cutter chasing him. | In game (Claude) |
| 6 | Safety Class (was Self-Defence Class) | The plaza, Saturday morning, with the kids and S.A.R.A. | Hospitality vs security: a "safety class", with mats. | In game (Claude) |
| 8 | Self-Defence Class | The Shuttle Bay after hours, with Freya and Ix'ali | A boarding drill on chalked corridors. Reward: on your own ship, your crew hit boarders half again as hard. | In game (Zachary's reward, scene by Claude) |

**Saffi** (Ervani, community host): a town out of plates.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Welcome Basket | Your front door, morning | Bread, soup, socks, seeds, and everyone's birthdays. | In game (the NPC Master's title, scene by Claude) |
| 4 | Bring a Plate | The market after lunch | A potluck sign-up sheet with one name on it. | In game (Claude) |
| 6 | Every Name | The museum's hull plate from the first crash | Kit's handprint; soup for forty in a dented helmet. | In game (Claude) |
| 8 | The First Potluck | The fountain, Sunday | Half the station, and Jasper not allowed to cook. Reward: Well Fed (your energy bar is 30 longer). | In game (Zachary's reward, scene by Claude) |

**Kit** (Ervani, their son): security chief, or a pirate.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Fastest on the Station | The plaza at lunch | A race round the fountain. | In game (Claude) |
| 4 | The Beacon | His telescope at home, before bed | Three long, two short: a smuggler's mark. A cache goes on your jump map. | In game (the NPC Master's title, moved from the lounge; scene by Claude) |
| 6 | Wanted | The Shuttle Bay after lessons, with Garrick | He wants to be a bounty hunter like you; Garrick makes him a junior security officer. | In game (Claude) |
| 8 | Deputy | The West Terminal's customs hall, a weekend | Every officer picks one deputy. Reward: Kit's deputy badge, to set down at home. | In game (Claude) |

**The side arc** (all three need the hearts):

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 4 | The Model Ship | Their flat, Saturday morning | Your ship in glue; which way does the cockpit go? | In game (Claude) |
| 6 | Brave Together | The mine's cavern gate, after dinner, with Vzz'ket | Kit went to see a crawler so he wouldn't be scared. Brave together counts double. | In game (Claude) |

- **Closed:** S.A.R.A. vs Garrick (his 6 and 8); Garrick's wariness of your pirate-hunter past (his 2, 4, 8 and Kit's 6); the beacon (a smuggler's cache); the 8 that had no scene (each has one).
- **Their weeks:** Kit's Saturdays (the model ship, then the West Terminal's seals with Garrick after his 6); Saffi's Sunday cooking, then the potluck table by the fountain after her 8 (company, not a mechanic); Saffi's Monday lunch with Rusk (already in her day, now a day line).
- **Still open:** art for Kit's badge (a stand-in); the NPC Master still calls Rusk "Saffi's uncle" (he isn't: a figure in their lives, 23 Nov).

### 5.10 Eshu (Arachnay, Courier & bounty pilot; Wave 1)

**No heart events** (Zachary, 24 Nov: "no hearts for eshu he is just behind the courrier desk"), like Ooma. He keeps the Post & Privateer Dispatch desk in the West Terminal (07:30 to dinner), the crew board in the Shuttle Bay's booth, and the capture contracts and bounties (`main.gd`, 23 Nov). The old outline (2 Forty Sacks, 4 The Blockade Letter, 6 Safe Routes, 8 rewards only: Express Export Crates and high-tier bounties) is cut; the contracts already pay bounties.

- **Closed with it:** 4's letter to Pip's parents (they're dead, 24 Nov), and the repeat of his 6 with Ana's 4.

---

## 6. Holidays and calendar events

All outlines; none has a scene yet.

| Day | Event | Notes |
|---|---|---|
| Spring 20 | **Landing Day** (station) | Saffi's potluck, ringing the lobby bell, the fountain photo. If Ivan hasn't fallen yet, the hotel isn't open (it opens after his fall, 23 Nov) and the bell is at Reception. |
| Spring 24 | Grand Hotel Inspection | Needs the hotel open (it opens after Ivan's fall, decided 23 Nov). Ties to Jasper & Evarra 8 and Stu. |
| Summer 22 | Midsummer Star-Gaze | Observation Lounge; a wish with a friend or partner. The one partner beat in the calendar. |
| Summer 29 | **Chivalry & Forge Tourney** (Junta) | Shuttle Bay; Ix'ali 6 can set it up. |
| Autumn 21 | Station Potluck Cook-Off | Judged by Rusk, Maren and Jasper. |
| Autumn 25 | **Founders' Fair** (Collective) | A stall from each Collective people. |
| Winter 21 | Deep-Core Soak | Hot springs and Job's gumbo; before the Harbinger, an aurora watch in the lounge. |
| Winter 26 | **Terran Yule Tide** (Empire) | Lights, gifts, a midwinter feast; toasts by S.A.R.A., Owen and Garrick. |
| Winter 31 | Winter Lights | Everyone under the domes and in the lounge. |

---

## 7. Problems across many events

### 7.1 The confessions are half written

Each of the nine 8-heart scenes ends "Accept confession or stay friends", with no reply to either answer. Rule 3.5 also needs a **friendship ending** for each (same scene, no confession, same perk) for when you're dating someone else. That's 27 short pieces: nine accept replies, nine decline replies, nine friendship endings.

### 7.2 Hearts are counted three ways in the code

`main.gd`: `FRIEND_PER_HEART := 10` (used by the bedroom locks); `ui.gd`: `HEART_POINTS := 5` ("One heart is 5 friendship"); NPC Master: 1 heart = 100 points. Talking gives +1 and a request +2 now. They need to be one number before any event triggers on hearts. Decision 15.

### 7.3 Hard-lock breaks

| Event | Problem | Fix |
|---|---|---|
| Jasper & Evarra 8 (and so 8+) | Waits for the hotel; 8s never wait | Done 23 Nov: the mess hall until the hotel opens (Decision 9) |
| Stu 8 | Hotel lobby; no backup | Done 23 Nov: the hotel opens after Ivan, before Stu arrives, so no backup is needed |
| Stu 2, 6 | Hotel; Stu arrives long before it may open | Done 23 Nov: as above; 6 moved to East Home 2's door |
| Evarra 8 | East orchard; no backup | Done 22 Nov: the promenade flower beds until the garden dome opens |
| Artie 8, 10 | East orchard; no backup | Done 23 Nov: the dome's woods, backup the little park |
| Evarra 6 | Waits on side arc 6, which needs Jasper's hearts | Done 22 Nov: her 6 no longer needs honey |

### 7.4 Places in the scripts that aren't the game's maps

Job 2 and 4 are settled (the Engineering break room; the mine's iron bay); Quill 8 is the library; Stu 6 is settled (East Home 2's door); the Chitin Exodus "Mine Level 5" (floors 16–24); Ix'ali 6 is settled (the cavern gate).

### 7.5 Choices with no outcome, or the wrong kind

~~Jasper & Evarra 8 option B~~ (fixed 23 Nov: the soufflé falls flat, no friendship, the dish waits for the banquet); ~~Ana 6 ("+High Romance")~~ (fixed 23 Nov); the nine confessions (7.1).

### 7.6 What the event engine will have to check

From the triggers above: map and time window; weekday (Wed or Sat); season; hearts (one resident, both of a pair, or "as partners"); flags (Custodian restored, Harbinger woken, hotel open (= Ivan's fall), ship has flown, resident arrived, an earlier event seen); and an automatic cutscene (Jasper & Evarra 8+). "Dusk", "sunset" and "night" need fixed clock windows, and "sunny" needs a meaning.

### 7.7 Eleven scenes in the Observation Lounge

~~Jasper & Evarra 4~~ (moved 23 Nov to the West Terminal's star dome), Artie 6, Ana 8, Quill 10, Ix'ali 10, Stu 10, ~~S.A.R.A. 8~~ (her new 8 is at her core), ~~Tikka & Sesska 6~~ (24 Nov: the hotel's dining room, or the mess hall), Kit 4, Midsummer Star-Gaze, Winter Lights. Quill 10, Ix'ali 10, Stu 10 and Ana 8 are all romantic scenes at night under the stars. Moving two or three would help them feel different (Decision 17): for example Quill 10 in the East Agridome with his named plant, Stu 10 in a hotel suite once it's open. (Moved: Quill 10 to the little park, Ix'ali 10 to the museum, Stu 10 to the terminal airlock. Ana 8 stays: it's a navigator's scene.)

### 7.8 Art the scenes need that doesn't exist yet

Heart-event sheets (already on the status list); props: a training mat, the apiary box and glass hive, the skiff, the "Echo Landing Shipwrights" sign, the framed photo, a camp burner, Stu's nameplate; outfits: Stu's uniform, EVA suits.

---

## 8. Decisions for Zachary

Answer by number; anything left open stays as it is.

1. **Wave 1:** stays on Ivan's fall, as built (24 Nov: Claude's suggestion, not overruled). The docs and scripts change to "Ivan's wreck".
2. **Ana's mutiny:** decided 23 Nov: the game's version, and her crew always "knew" she was weak for never firing on transports.
3. **Rabble or Chernobog:** decided 23 Nov: the pirates are the Chernobog; Ivan is the Rabble.
4. **Your ship:** decided 24 Nov: the fighter is what's left of the *Wandering Star*.
5. **Who took Artie in 2036**, and why was his pod in Ivan's hold?
6. **Where threads A and B end:** at the Neutral Zone Summit, or elsewhere?
7. **Pip's parents:** decided 24 Nov: they're dead. Their freighter's drive failed between stations in the Neutral Zone three years ago, "nobodys fault bad things happen somtimes" (Zachary). Pip knows, but not how; his grandparents tell him in the family's side arc.
8. **The first bees:** decided 22 Nov: side-arc 6. Evarra 6 is now a wildflower border round your field.
9. **Jasper & Evarra 8 waiting for the hotel:** decided 23 Nov: it plays in the hotel's dining room, and in the mess hall until the hotel opens. (Then cut the same day, when side arcs became three scenes.)
10. **Stu before the hotel opens:** decided 23 Nov: the hotel opens after the Ivan fight, before Stu arrives, so he needs no job before it and no backup places. Guests come Friday to Sunday.
11. **Backups for the East orchard:** done. Evarra 8: the promenade flower beds; Artie 8 and 10: the little park (they moved to the garden dome's woods). The engine now has backup places (`"backup"` in `scripts/heart_events.gd`).
12. **Ix'ali's star pendant** at 8: an Oath-Crest you could propose with, or something else?
13. **Freya's father:** decided 22 Nov: **Jorvik**, who died testing an earlier version of the stabilizer. Still open: how long ago.
14. **Keepsakes marked (Claude):** Job's oar charm. (Jasper's apron and Evarra's pressed-flower frame are in the game.)
15. **Hearts:** 100 points a heart, as in the NPC Master? Then the code is changed to match.
16. **"The Nest":** decided 23 Nov: the cavern event is now "The Broken Shell"; the Rabble's Nest keeps its name.
17. **Which Observation Lounge scenes move**, and where to. Moved so far: Quill 10 (the little park), Ix'ali 10 (the museum), Stu 10 (the terminal airlock), Jasper & Evarra 4 (the West Terminal's star dome).
18. **Eshu:** decided 23 Nov: Tally is renamed Eshu in the game and every doc (the file id stays `tally`).
19. **The Custodians:** decided 24 Nov: six of them, a cutscene-only prologue, and an ending still open. See [`CUSTODIANS.md`](CUSTODIANS.md).
20. **Which scenes Claude writes first.** (Done so far: every romance arc, the Jasper & Evarra side arc, S.A.R.A., Tar'Besh, Zaas, and Vzz'ket & Rusk; Bram is done too (Ooma has no heart events), and Tikka & Sesska, Maren, Owen & Pip, Tobbin, Merrow & Nub, and Garrick, Saffi & Kit (24 Nov); Eshu has no heart events (24 Nov), so every arc is written.) Suggested order: the 27 confession pieces (7.1), then Jasper and Evarra, then the 10-heart scenes, then the platonic arcs, in the build order's places (S.A.R.A. 2, Job 2, Freya 2, Quill 2, Ix'ali 2 can play first).
