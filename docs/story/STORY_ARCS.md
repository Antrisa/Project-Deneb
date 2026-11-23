# Echo Landing: story arcs and heart events (review, 22 Nov 2026)

Every story beat and heart event in one place, with how much of each is written and what needs Zachary's call. Written by Claude for review from:

- Drive: "NPC Master" (19 Nov), "Heart Events: All Romances (merged)" (19 Nov), "Lore Bible V4", "Game Opening & Prologue Script", "Custodian Bundles", "Master NPC Relationship & Heart-Event Bible" and "Character Relationship Map" (both superseded, used only for scenes nobody has rewritten);
- the game on `art24` (`6b80217`): the first and second flights and the arrivals in `scripts/main.gd`.

The full scripts that exist are copied next to this file: [`ROMANCE_SCRIPTS.md`](ROMANCE_SCRIPTS.md) and [`PROLOGUE_SCRIPT.md`](PROLOGUE_SCRIPT.md). The Drive docs stay the source of truth until Zachary says otherwise.

**The courier is Eshu** in every Drive doc since 19 Nov (the NPC Master, Lore V4 and the romance scripts). The game still calls him Tally (`npc_data.gd`, the morning news, his schedule), and so does the Project's older copy of the NPC Master. His file id `tally` can stay.

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
| Jasper & Evarra side arc | 5 | 5 | 0 | 0 |
| Platonic arcs (10 × 4) | 40 | 0 | 0 | 40 (five are only a reward, no scene) |
| **All heart events** | **90** | **22** | **10** | **58** |
| Prologue | 4 | 4 | 0 | 0 |
| Main story beats after the prologue | 15 | 5 in game | 0 | 10 |
| Holidays and calendar events | 9 | 0 | 0 | 9 |

Not written at all yet: the nine friendship endings for the 8-heart confessions, the accept and decline replies to each confession, the wedding cutscene, break-up reactions, birthday lines, and scenes for the five platonic 8-heart rewards that only have a reward.

**The biggest findings:**

1. **Four big story threads open and never close:** the Terran hardliners who want S.A.R.A. back or destroyed, the Junta and the waking Custodians, Pip's missing parents, and who took Artie in 2036. Section 1.3.
2. **The docs and the game tell Ivan's ending and Ana's mutiny differently** (pirate base raid vs Ivan's flagship; a civilian freighter vs revenge). Section 1.2.
3. **Every 10-heart romance scene and every platonic scene is an outline.** (Freya's, Jasper's, Evarra's, Job's and Quill's arcs are now written and in the game.)
4. **Five events break the hard-lock rule** (8s must never wait): Jasper & Evarra 8 waits for the hotel; Stu 8 needs the hotel lobby; Evarra 8 and Artie 8 and 10 need the East orchard. Stu's 2 and 6 need the hotel too. Section 7.3.
5. ~~**Two "first bees" scenes**~~ Settled 22 Nov: the bees are the siblings' 6; Evarra's 6 is a wildflower border.
6. **The code counts hearts three ways:** `main.gd` says 10 points a heart, `ui.gd` says 5, the NPC Master says 100. Section 7.2.
7. **Eleven scenes were in the Observation Lounge**, including three 10-heart milestones and Ana's confession, all at night under the stars. (Ten now: Quill 10 moved to the little park.)

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
| 6 | **First flight:** ice field, the Patient Wren, the Rabble picket, the Moogli trader, Ivan's flagship. Ivan goes down with his ship; a stasis pod tumbles out of his hold and you tow it home. | Ship repaired | In game | Clash: the docs say Artie is found "at the pirate base" and that Wave 1 comes "after the pirate base raid". |
| 7 | **Wave 1:** Artie wakes in the Medbay (D+1), the first visitor transport brings Stu (D+2), Artie moves into East Home 1 (D+3), Eshu asks for a berth (D+4). D is the day Ivan falls. | Ivan's fall | In game (placeholder lines) | |
| 8 | **Second flight:** Ana drops out of fold to avenge Ivan; at half hull her crew turn her turrets on her own bridge; you beat their gunship and pull her out. | Next flight | In game | Clash with Ana 2 (section 3.9). |
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
- **Clash: Ana's mutiny.** In the game she comes for revenge, and her crew turn on her ("You weren't there when he needed you"). In Ana 2 she says her second-in-command shot her "the second I ordered them not to fire on a civilian freighter", and the player can answer "You tried to protect innocent people." Decision 2.
- **Clash: what the pirates are called.** The scripts say the Chernobog Clan; the game says the Rabble (Rabble cutter, Rabble colours). Both can stand (the Chernobog Clan, nicknamed the Rabble after Ivan), but scenes should agree. Decision 3.
- **Clash: "awaken" or "restore".** Prologue scene 4 wakes all three crystals at once and they talk. The bundles doc and the story-event triggers then speak of "awakening" each Custodian ("1st Custodian Awakened"). Suggest: the prologue wakes them, bundles **restore** their wings, and triggers say "first Custodian restored". Decision 19.
- **Clash: the player's ship.** The prologue's *Wandering Star* loses its rear half in the blind jump; the game has a fighter repaired in the Shuttle Bay. If the fighter is what's left of the *Wandering Star*, one line from Freya or Tikka would settle it. Decision 4.
- **Repeat: S.A.R.A.'s secret.** S.A.R.A. 2 has her tell you she let her self-destruct timer run out; The Secret of Annex 4 then reveals the same thing as a discovery. Suggest she jokes around it at 2 and the tape gives the full truth.
- **Gap: there is no act structure.** Beats are gated by bundles and items, not by a shape across the year. Section 1.4 sketches one.

### 1.3 Threads that open and never close

| Thread | Opened by | Closed by |
|---|---|---|
| **A. The Terran hardliners** want Annex 4 back or S.A.R.A.'s self-destruct carried out. Lore V4 adds Empress Asta, whose father's death is tied to synthetic rights. | S.A.R.A. 6 "Ghost Signal" | Nothing |
| **B. The Junta and the Custodians.** "If word reaches Zaa'sh space that sentient constructs are active here, the Junta will send warships." | Prologue 4; Tar'Besh | Nothing (Tar'Besh's own arc never mentions it) |
| **C. Pip's parents** are alive in Collective space. | Maren/Owen/Pip 4, Eshu 4 (Pip's letter) | Nothing |
| **D. Who took Artie** in October 2036 ("a silent silver light lifted my truck"), and why was his pod in Ivan's hold? A silent silver light sounds like a Precursor drone. | Artie 2 | Nothing |
| **E. The Precursor Lexicon in your head.** Quill's "electromagnetic spike", the Mother-Drone's "Tend the small worlds". | Prologue 2–3 | Only the Custodians talking to you |
| **F. "Something big stirring below."** The giant carapace, the crawlers fleeing upward, the tides Zaas hears. | Vzz'ket & Rusk 4, Chitin Exodus, Zaas 4 | Implied by the floor-45 boss, never said |
| **G. The Chernobog remnants.** "The Chernobog lieutenants scattered." | Ana 2 | Space runs could pick it up (pirate strongholds) |

**Idea (Claude), nothing decided:** the Neutral Zone Summit is where A and B could land. Each power arrives with a claim (the Empire on S.A.R.A. and Annex 4, the Junta on the Custodians, the Collective on its refugees), and how the residents stand with you decides how it goes: S.A.R.A. 6 and Tar'Besh's secret pay off, Eshu (who keeps a private line to every empire and puts the kettle on for rival envoys) gets everyone to one table, and Ix'ali, Ana and Artie each have a side to speak for. C and D could close earlier, in Year 1: Pip's parents through Eshu's network, and Artie's abductors through the Starborn Convergence.

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
- **Hard-lock rule:** 8- and 10-heart events never wait for story progress (they use a backup place). 2–6-heart events wait only when the unlock is what they're about. A scene that needs a resident who hasn't arrived plays without them. Exception: Zaas 6 and 8 wait for the Harbinger.

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
- **For the side arc:** the siblings' 2 and 8 are also in the mess hall; spread them out when we get to it.

### 3.2 Evarra (Vuultam, Chief Baker & Gardener)

A gardener without a garden, until there is one. **Reviewed with Zachary on 22 Nov; all five are written and playable.** Full scenes and her week: [`characters/EVARRA.md`](characters/EVARRA.md).

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Window-Box Herb | Her herb bench in the mess hall's greenhouse, 09:30–13:00 on a working day | One pot of lavender is the only thing she grows for herself. (Was "in the dead dome": the game has no dead version of the dome.) | In game (Claude, from Zachary's outline) |
| 4 | First Blossom | The garden dome's meadow on her day off; waits for the dome | Real soil, the first wildflowers; she dances barefoot. | In game (Claude, from Zachary's outline) |
| 6 | A Hem of Wildflowers (was Honey & Brioche) | Your field, Wednesday or Sunday morning | She plants Ooma's wildflower seeds round your field for the bees to come. Unlocks Honey-Lavender Brioche. | In game (Claude) |
| 8 | Wildflower Crown (confession) | The orchard at sunset; **backup** before the dome opens: the promenade flower beds | A crown of every flower she's grown. Perk: Green Thumb. Friendship ending has its own line if you're dating Jasper. | In game (Claude, from Zachary's outline) |
| 10 | The Moonlit Bakery | Your kitchen in the hotel, 20:30–23:30, then the little park | You bake a three-tier honey cake together, then picnic with it. Keepsake: the pressed flowers from her crown, framed. | In game (Claude, from Zachary's outline) |

- **Decided:** the first bees are the siblings' 6, so her 6 doesn't wait on Jasper's hearts (Decision 8); 10 is baking then a picnic; she's off Wednesdays and Sundays, Jasper Tuesdays and Saturdays, with lines for those days; her 8 has a backup place (Decision 11, her part); her keepsake is the pressed-flower frame (Decision 14, her part).
- **Still open:** the wildflower border on your field after 6 needs drawing (`evarra_wildflowers` is set); the brioche and Green Thumb need cooking and crop quality in the game.

### 3.3 Freya (Human, Junior Shipwright)

Stepping out of her late father's shadow. **Reviewed with Zachary on 22 Nov; full scenes in [`characters/FREYA.md`](characters/FREYA.md)** (Claude drafts around his lines). **All five play in the game as cutscenes** (`scripts/heart_events.gd`, `scripts/cutscene.gd`; debug F3).

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
- **Still open:** the skiff needs art; his skiff and Zaas's research skiff (Zaas 8) could be the same boat.

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

Junta steel, Earth chivalry: honour means protecting the weak.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Steel & Chivalry | Armoury | Earth knights who swore to shield the weak. | Script |
| 4 | The Relic Blade | Armoury, when you bring a Zaa'sh or Terran metal artifact | With Tar'Besh: folded lunar titanium. | Outline |
| 6 | Sparring Under the Dome | Shuttle Bay mat (Garrick watching) | A blunted-blade duel. Unlocks the Star-Knight Aegis tier. | Short |
| 8 | The Oath (confession) | Armoury forge after hours | She kneels and offers a star pendant, her shield and her heart. Perk: Chivalric Guard. | Script |
| 10 | Forged in Starlight | Observation Lounge, night | Matching ceremonial pauldrons. Keepsake: a pauldron. | Outline |

- **Gap:** 2 ends on the choice, with no reply to either option.
- **Gap:** 4 needs writing, and its trigger needs the engine to know what you're holding. Which items count as "a Zaa'sh or Terran metal artifact"?
- **Clash:** the Master says her star pendant is an Oath-Crest, the marriage token. If she gives it to you at 8, you could propose with it before her 10. Decision 12.
- **Gap:** "I am no longer a soldier of the Junta": did she serve and leave? One line of backstory would carry the arc. There's no training mat in the Shuttle Bay map yet.
- **Idea:** 6 could set up the Chivalry & Forge Tourney (Summer 29), also in the Shuttle Bay.

### 3.7 Arthur "Artie" Vance (Human, Wave 1)

Woke up centuries late; finds a second chapter teaching the station's kids.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Centuries Late | Library | October 2036, Minnesota, "a silent silver light lifted my truck". | Script |
| 4 | The Junior Scouts | Plaza fountain | Knots and orienteering with Pip, Nub and Kit. Unlocks Junior Scout Foraging Reports. | Short |
| 6 | Echoes of 2036 | Observation Lounge | S.A.R.A. projects a 2030s sky with crickets. | Short |
| 8 | Campfire Under Glass (confession) | East orchard at night | Marshmallows beside Evarra's wildflowers. Perk: Thrifty. | Script |
| 10 | Merit Badge of the Heart | Campout in the East orchard | The kids give you an Honorary Scoutmaster badge Sesska sewed. Keepsake: the badge. | Outline |

- **Clash:** 2's trigger says "after rescuing Artie from the pirate base" (Decision 1). 10's trigger in the script says "Library / Concourse", but the scene is a campout in the East orchard (the Master agrees with the orchard).
- **Lock:** 8 and 10 are in the East orchard, which needs the Sovereign. Both need a backup; the plaza fountain, where the Scouts meet, would fit. Decision 11.
- **Gap:** 4 and 6 have one line each.
- **Gap:** thread D. Who took him, and how did he get into Ivan's hold? Decision 5.

### 3.8 Stowaway Stu (Moogli, Wave 1)

A drifter who can't remember his name learns that staying isn't a trap.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Packed Bags by the Airlock | Hotel lobby, morning | His duffel bag is packed; he doesn't remember his real name. | Script |
| 4 | The Burgundy Suit | Weaver's shop | Sesska fits his bellhop uniform. | Script |
| 6 | A Name on the Door | Hotel staff room | Tobbin's STU nameplate; he has unpacked. | Short |
| 8 | After-Hours Lobby Shift (confession) | Hotel lobby after 21:00 | Cocoa on the lobby sofa. Perk: Five-Star Partner. | Script |
| 10 | Suite for Two | Observation Lounge, night | A candlelit picnic; a silver hotel bell. Keepsake: the bell. | Outline |

- **Lock (the biggest in the cast):** Stu arrives right after Ivan, but 2, 6 and 8 happen in the hotel, which only opens with the Chancellor. 8 must not wait, and nothing says what Stu does before the hotel exists (in the game he waits at the terminal, then lives in East Home 2). **Idea:** he carries bags at the terminal and Reception for S.A.R.A. until the hotel opens; backups: Reception for 2 and 8, East Home 2's door for 6. Decision 10.
- **Clash:** in 2 the bag is "hidden behind the potted fern", then S.A.R.A. says it's "sitting by the terminal airlock".
- **Clash:** 6 is "the West Wing Residential Corridor" in the script and "the hotel staff room" in the Master; in the game he lives in East Home 2. The nameplate could go on that door.
- **Gap:** 6 has no choice. Does the game ever give him his name back? (Optional.)

### 3.9 Anastasia "Ana" (Human, Wave 2)

Ivan's sister unlearns that fear is loyalty.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | No Brig, Just Soup | Medbay | Saffi's carrot-ginger soup; why did you pull her out? | Script |
| 4 | Grease & Second Chances | Shuttle Bay, 14:00–17:00 | Thrusters with Freya; Garrick says she's earning her berth. | Script |
| 6 | Ghost of the Crown | Rusk's bar after 20:00 | Ivan before he was a monster. | Script |
| 8 | Co-Pilot's Promise (confession) | Observation Lounge, night | She wants to be your navigator. Perk: Wingmate. | Script |
| 10 | True North | Board the ship at sunset | A star-chart console with both your initials; an orbit over the crater. Keepsake: the console and a flight jacket. | Outline |

- **Clash:** 2's story of her mutiny doesn't match the game's second flight (section 1.2). Decision 2.
- **Gap:** 6's choices give "+High Romance/Friendship"; there are no romance points (hearts are friendship only), so "+High Friendship".
- **Idea:** the status doc has Ana joining your crew at 6 hearts, but her 6 is at the bar. Her 4 (in the bay, with Freya) is the better place for the offer, or 6 ends with it.
- **Repeat:** 4 has her charting the old ambush corridors for Eshu's skiffs; Eshu 6 "Safe Routes" is the same work. Make Eshu 6 the follow-on.

---

## 4. Jasper & Evarra: the sibling side arc

Needs **both** at the level. All five are full scripts ([ROMANCE_SCRIPTS.md](ROMANCE_SCRIPTS.md), Part 1).

| ♥ (both) | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Haute Cuisine on a Ration Budget | Mess hall, 13:00–16:00 | Grey béchamel; "little brother?!" | Script |
| 4 | The Escape Pod Memory | Observation Lounge after 19:00 | Two infants in one thermal blanket, about twenty years ago. | Script |
| 6 | Operation Honeybee | East Agridome, a sunny morning; waits for its restoration | The first bees. Unlocks Wildflower Honey. | Script |
| 8 | The Critic's Practice Run | Mess hall, evening; waits for the hotel | Fusion, not imitation. Unlocks Starlight Soufflé & Lunar Truffle Glaze. | Script |
| 8+ | A Table for the Whole Sector | Plaza fountain banquet, evening; after the Critic's run | The whole station at one table. Reward: Family Table perk and a framed photo. | Script |

- **Gap (4):** only the honey-tart version is written. The trigger says that before the East Agridome is restored Jasper brings herb tea and ration-flour tarts, so "Merrow let me harvest the first Nectar-Blossoms" and "it tastes like real sunlight" need a second version.
- **Clash (6):** the hive comes "by Eshu's mail skiff", but the East Agridome can be restored in Spring, before Eshu arrives. Another carrier is needed (Ooma's ship on a Wednesday or Saturday, or Bram ordering it). "A sunny morning" needs defining inside a dome on a moon (daytime, not Winter?). And Decision 8 (two first-bees scenes).
- **Lock (8):** it waits for the hotel, but 8s never wait. Either the side arc is an exception like Zaas, or 8 gets a version without the hotel (practising for the Landing Day potluck?). Decision 9.
- **Gap (8):** "The Spring Hotel Inspection is weeks away" is only true in late Winter or early Spring; make it season-aware. Option B ("stick strictly to the recipe") has no outcome: Jasper's "You're right..." answers option A.
- **Clash (8+):** "call twenty-eight neighbors family" is right only once Ana has arrived; "every neighbor" always is. The framed photo needs art.

---

## 5. Platonic arcs

All 40 are outlines. Text is from the NPC Master; where the Master has only a word or two, the older bible's outline is used.

### 5.1 S.A.R.A. (AI, Steward & Concierge)

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Croissant Protocol | Reception at night | Paris hotel brochures; she let her self-destruct timer run out rather than detonate with guests aboard. | Outline |
| 4 | Turrets & Velvet Curtains | Plaza, with Garrick | Compromise: a hidden defence grid and a brass reception bell. | Outline |
| 6 | Ghost Signal | S.A.R.A.'s core, evening | A Terran patrol has found Annex 4's signature; hardliners want the station back or her self-destruct carried out; the old directive is still live in her core. Keep it between you. Clips: `warning`, `glitches`. | Outline (Claude) |
| 8 | Five-Star Heart | Observation Lounge | A ribbon-cutting (with the hotel) or honorary co-proprietor (without). Reward: Concierge Fast-Travel & Station Alerts. | Outline |

- **Repeat:** 2 and The Secret of Annex 4 (section 1.2).
- **Gap:** 6 opens thread A, and nothing closes it.
- The brass bell from 4 turns up in Stu 2 and on Landing Day. Is it at Reception or in the hotel lobby?
- Two secrets kept from two empires (hers in 6, the Custodians in the prologue). Good material for the Summit.

### 5.2 Tar'Besh (Zaa'sh, Cleric & Curator)

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Dust on the Relics | Museum | He stiffens at S.A.R.A.'s chime; you catalogue a Sky-Weaver astrolabe. | Outline |
| 4 | The Power Surge | Plaza fountain (Pip and Nub) | S.A.R.A. shields the children with her own emitters. | Outline |
| 6 | Tea in the Survey Suite | S.A.R.A.'s core | Zaa'sh spiced tea; he apologises. | Outline |
| 8 | Keeper of the Starborn | Museum | A plaque to all seven species. Reward: Starborn Relic Appraisal, +25% Scrip on donations. | Outline |

- **Gap:** Lore V4 calls him exiled. Exiled for what?
- **Gap:** he keeps the Custodian secret (thread B), and his arc never mentions it.
- "Starborn" in 8's title gives away the Convergence if 8 plays first. "Keeper of the Sky-Weavers" until then?

### 5.3 Zaas (Scyldar, Water Reclamation Officer); Merrow appears

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Clipboard & Diving Helmet | East Agridome | Merrow fixes leaks while Zaas fits a diving helmet to an ice drill; you help Merrow. | Outline |
| 4 | Sonar Echoes | Upper caverns | His hydrophone hears real tides below. | Outline |
| 6 | First Splash | Sea of Echoes; waits for the Harbinger | Joyful tears; he hands Merrow the water officer badge. | Outline |
| 8 | Captain of the Deep | Sea of Echoes; waits for the Harbinger | They christen a research skiff. Reward: Deep-Sea Sonar Lure. | Outline |

- 6 and 8 wait for the Harbinger by design, so Zaas can sit at 4 for most of Year 1.
- **Idea:** 4's tides, the Chitin Exodus and Vzz'ket's carapace all point at the same thing below. Saying so links three arcs to the floor-45 boss (thread F).
- **Repeat:** the skiff (section 3.4).

### 5.4 Vzz'ket & Rusk (both)

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Tall Tales at the Bar | Rusk's bar at night | Rusk laughs off the crawler migration; Vzz'ket sharpens his spear. | Outline |
| 4 | The Nest | Caverns, lush floors | A carapace far bigger than any crawler. | Outline |
| 6 | On the House | Rusk's bar | Rusk apologises; Friday Open-Mic & Story Night starts. | Outline |
| 8 | Sentinels of Echo Landing | Rusk's bar | Chitin-Piercer Traps and monster radar; Secret Reserve drinks. | Outline |

- **Clash:** "the Nest" is also the pirate stronghold in the space-combat plan ("the Nest raid"). Rename one. Decision 16.
- Rusk gets no scene of his own. His forty years behind the bar and being Saffi's uncle (both Claude placeholders) go unused.

### 5.5 Bram & Ooma (both, except 4)

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Price War on Aisle One | Bram's, Wed or Sat | Ooma sold "a genuine pre-war toaster" for half his scrap rate. | Outline |
| 4 | Quiet Credit | Bram's (Bram's hearts only) | He writes off a stranded pilot's repair tab. | Outline |
| 6 | The Tip-Off | Bram's, Wed or Sat | Ooma trades him the coordinates of an unclaimed wreck for a hot meal from Jasper. | Outline |
| 8 | Merchant Guild of Two | Bram's, Wed or Sat | +10% salvage price; the VIP Contraband Catalog and exotic seeds. | Outline |

- **Idea:** 6's coordinates could reveal a special salvage stop on the jump map (space events already have `reveal: <special sector>`).
- **Gap:** Ooma herself (who she is, where she goes) never comes up; her ship is planned as the special merchant in space runs.

### 5.6 Tikka & Sesska (both)

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Tuning the Manifold | Engineering power core | Tuning the geothermal manifold. | Outline |
| 4 | EVA Workwear | Weaver's shop | Designing EVA-lined workwear together. | Outline |
| 6 | The Anniversary | Observation Lounge | A surprise you help organise. | Outline |
| 8 | (no title) | Engineering | Rewards only: Smelter Overclock; Void-Silk Luxury Linens. | Gap |

- **Gap:** 8 has no scene. Nothing is at stake in 2 or 4 (a cosy arc can still have a worry: Tikka overworking the core, say).
- "Forty years married" is a Claude placeholder. Tikka mentors Freya, but they share no scene until Freya 10.

### 5.7 Maren, Owen & Pip

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Pip in the Archive (Pip's hearts) | Library | Pip sneaks into the restricted archive. | Outline |
| 4 | The Freighter Log (Owen's) | Library | Clues that Pip's parents are alive in Collective space. | Outline |
| 6 | Letting Go (Maren's) | Plaza | Pip joins Artie's Junior Scouts; backup before Artie: Freya lets him help in the bay. | Outline |
| 8 | (no title) (Maren's) | Medbay | Rewards only: Advanced Med-Stims; Library Lore Compendium. | Gap |

- **Gap:** thread C has the most pull and no ending. How did Pip's parents go missing? Do they write back, come home, or stay lost? Decision 7.
- **Gap:** 8 has no scene.

### 5.8 Tobbin, Merrow & Nub

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Plastic and Steel (Tobbin's hearts) | Furniture workshop | He fights plastic-and-steel furniture. | Outline |
| 4 | First Real Wood (Tobbin's) | East orchard; waits for the first wood | The first real-wood harvest. | Outline |
| 6 | A Wooden Starship (Tobbin's) | Their home | He carves Nub a toy ship. | Outline |
| 8 | (no title) (Merrow's) | Furniture workshop | Rewards only: Heirloom Real-Wood Furniture; Hydro-Boost. | Gap |

- **Gap:** 8 runs on Merrow's hearts, but every scene before it is Tobbin's, and Merrow's own story plays in Zaas's arc. Her 8 should be about her.
- **Clash:** where the wood comes from. The Sovereign gives Lunar Birch saplings to your West Agridome; the East orchard is fruit trees. You bringing him your first Lunar Birch Log might be the better trigger.

### 5.9 Garrick, Saffi & Kit

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Welcome Basket (Saffi's hearts) | Their home | Saffi's potluck basket. | Outline |
| 4 | The Beacon (Kit's) | Observation Lounge | Kit spots a smuggler's beacon. | Outline |
| 6 | Self-Defence Class (Garrick's) | Plaza | Self-defence without militarising the plaza. | Outline |
| 8 | (no title) (Garrick's) | Armoury | Rewards only: Potluck Buffs; Perimeter Defence. | Gap |

- **Repeat:** 6 settles S.A.R.A. vs Garrick a second time (S.A.R.A. 4 already did). Pick one to own it, and give the other a different beat.
- **Gap:** Garrick is "wary of the player's pirate-hunter background" (cast doc); no scene uses it. **Gap:** 4's smuggler beacon goes nowhere (a space-run stop? Ooma?). 8 has no scene.

### 5.10 Eshu (Arachnay, Courier & bounty pilot; Wave 1)

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Forty Sacks | Reception | Sorting mail with four arms at once. | Outline |
| 4 | The Blockade Letter | Reception | He runs a pirate blockade to deliver Pip's letter. | Outline |
| 6 | Safe Routes | Shuttle Bay, with Ana; backup: with Garrick | Safe trade routes with Ana. | Outline |
| 8 | (no title) | Reception | Rewards only: Express Export Crates; high-tier bounties. | Gap |

- **Clash:** the game still calls him Tally (decision 18). His shop room and home are still undecided; 2 and 8 should move to the Post & Privateer Dispatch once it has a room.
- **Idea:** make 4's letter the next step in Pip's thread (a letter to his parents, or from them).
- **Repeat:** 6 and Ana 4 (section 3.9).

---

## 6. Holidays and calendar events

All outlines; none has a scene yet.

| Day | Event | Notes |
|---|---|---|
| Spring 20 | **Landing Day** (station) | Saffi's potluck, ringing the lobby bell, the fountain photo. In Year 1 the hotel isn't open: the bell is at Reception. |
| Spring 24 | Grand Hotel Inspection | Needs the hotel open, so realistically Year 2 first. Ties to Jasper & Evarra 8 and Stu. |
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
| Jasper & Evarra 8 (and so 8+) | Waits for the hotel; 8s never wait | Exception, or a no-hotel version (Decision 9) |
| Stu 8 | Hotel lobby; no backup | Reception (Decision 10) |
| Stu 2, 6 | Hotel; Stu arrives long before it may open | Reception; East Home 2 (Decision 10) |
| Evarra 8 | East orchard; no backup | Done 22 Nov: the promenade flower beds until the garden dome opens |
| Artie 8, 10 | East orchard; no backup | Plaza fountain (Decision 11) |
| Evarra 6 | Waits on side arc 6, which needs Jasper's hearts | Done 22 Nov: her 6 no longer needs honey |

### 7.4 Places in the scripts that aren't the game's maps

Job 2 and 4 are settled (the Engineering break room; the mine's iron bay); Quill 8 is the library; Stu 6 "West Wing Residential Corridor" (East Home 2?); Artie 10 "Library / Concourse" (East orchard); the Chitin Exodus "Mine Level 5" (floors 16–24); Ix'ali 6 "Shuttle Bay training mat" (no mat prop yet).

### 7.5 Choices with no outcome, or the wrong kind

Jasper & Evarra 8 option B; Ix'ali 2 (no reply after the choice); Ana 6 ("+High Romance"); the nine confessions (7.1).

### 7.6 What the event engine will have to check

From the triggers above: map and time window; weekday (Wed or Sat); season; hearts (one resident, both of a pair, or "as partners"); flags (Custodian restored, Harbinger woken, hotel open, ship has flown, resident arrived, an earlier event seen); the item in your hand (Ix'ali 4); and an automatic cutscene (Jasper & Evarra 8+). "Dusk", "sunset" and "night" need fixed clock windows, and "sunny" needs a meaning.

### 7.7 Eleven scenes in the Observation Lounge

Jasper & Evarra 4, Artie 6, Ana 8, Quill 10, Ix'ali 10, Stu 10, S.A.R.A. 8, Tikka & Sesska 6, Kit 4, Midsummer Star-Gaze, Winter Lights. Quill 10, Ix'ali 10, Stu 10 and Ana 8 are all romantic scenes at night under the stars. Moving two or three would help them feel different (Decision 17): for example Quill 10 in the East Agridome with his named plant, Stu 10 in a hotel suite once it's open.

### 7.8 Art the scenes need that doesn't exist yet

Heart-event sheets (already on the status list); props: a training mat, the apiary box and glass hive, the skiff, the "Echo Landing Shipwrights" sign, the framed photo, a camp burner, Stu's nameplate; outfits: Stu's uniform, EVA suits.

---

## 8. Decisions for Zachary

Answer by number; anything left open stays as it is.

1. **Wave 1:** keep it on Ivan's fall (as built), or move it to a pirate-base raid (as the docs say)? If Ivan's fall, the docs and scripts change to "Ivan's wreck".
2. **Ana's mutiny:** add a civilian ship she refuses to fire on to the second flight, or rewrite Ana 2 to match revenge followed by mutiny?
3. **Rabble or Chernobog** for the pirates (or the Chernobog Clan, nicknamed the Rabble)?
4. **Your ship:** is the game's fighter what's left of the *Wandering Star*?
5. **Who took Artie in 2036**, and why was his pod in Ivan's hold?
6. **Where threads A and B end:** at the Neutral Zone Summit, or elsewhere?
7. **Pip's parents:** found, a letter only, or left open?
8. **The first bees:** decided 22 Nov: side-arc 6. Evarra 6 is now a wildflower border round your field.
9. **Jasper & Evarra 8 waiting for the hotel:** allow it as an exception, or write a version without the hotel?
10. **Stu before the hotel opens:** his job, and backup places for 2, 6 and 8.
11. **Backups for the East orchard** (Artie 8 and 10). Evarra 8's is done: the promenade flower beds. The engine now has backup places (`"backup"` in `scripts/heart_events.gd`).
12. **Ix'ali's star pendant** at 8: an Oath-Crest you could propose with, or something else?
13. **Freya's father:** decided 22 Nov: **Jorvik**, who died testing an earlier version of the stabilizer. Still open: how long ago.
14. **Keepsakes marked (Claude):** Job's oar charm. (Jasper's apron and Evarra's pressed-flower frame are in the game.)
15. **Hearts:** 100 points a heart, as in the NPC Master? Then the code is changed to match.
16. **"The Nest":** rename the cavern event or the pirate stronghold.
17. **Which Observation Lounge scenes move**, and where to.
18. **Eshu:** rename Tally in the game's text (lines, morning news, schedule name; the file id stays `tally`).
19. **"Awaken" or "restore"** for completing a Custodian's bundles.
20. **Which scenes Claude writes first.** Suggested order: the 27 confession pieces (7.1), then Jasper and Evarra, then the 10-heart scenes, then the platonic arcs, in the build order's places (S.A.R.A. 2, Job 2, Freya 2, Quill 2, Ix'ali 2 can play first).
