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
3. **Every 10-heart romance scene and every platonic scene is an outline**, and Jasper's and Evarra's own arcs have no dialogue at all.
4. **Five events break the hard-lock rule** (8s must never wait): Jasper & Evarra 8 waits for the hotel; Stu 8 needs the hotel lobby; Evarra 8 and Artie 8 and 10 need the East orchard. Stu's 2 and 6 need the hotel too. Section 7.3.
5. **Two "first bees" scenes** (Evarra 6 and side-arc 6), and Evarra's own 6 can't play until Jasper is at 6 hearts as well.
6. **The code counts hearts three ways:** `main.gd` says 10 points a heart, `ui.gd` says 5, the NPC Master says 100. Section 7.2.
7. **Eleven scenes are in the Observation Lounge**, including three 10-heart milestones and Ana's confession, all at night under the stars.

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
| 16 | **The Leviathan of the Deep** (name is a placeholder). Boss on floor 45. | Floor 45 | Outline | |
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

The Paris dream was really a dream of sharing a table.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Burnt Ration Soufflé | Mess hall, after 20:00 | Alone after dinner, his ration-powder soufflé collapses; you bring herbs; he fears the dream is silly. | Outline (Claude) |
| 4 | Paris on a Screen | Mess hall, evening | Shows his holo-vid collection; has never tasted real butter. | Outline (Claude) |
| 6 | Taste of Paris | Mess hall, morning; waits for West Agridome wheat | First real croissant. Unlocks the Parisian Bistro Menu. | Outline |
| 8 | Candlelight in the Mess Hall (confession) | Mess hall after hours | A private dinner for two; the dream of Paris was a dream of sharing a table with you. Perk: Sous-Chef's Blessing. | Outline |
| 10 | Café Étoile | Terrace by the plaza fountain | Opens an outdoor bistro terrace. Keepsake (Claude): a monogrammed apron. | Outline |

- **Gap:** no dialogue for any of the five.
- **Repeat:** his 2 is the side arc's 2 again (ration paste that won't turn French, herbs to the rescue). His own 2 needs different ground.
- **Gap:** there is no butter in the game (`item_data.gd` has no butter, milk or cream), yet 4 sets up "never tasted real butter" and 6 is a croissant. It needs a source (an import from Ooma or the Moogli trader, a station substitute) or a different dish.
- 6 "waits for West Agridome wheat": the farm already grows moon wheat, so this can simply be "you have harvested Moon-Wheat once".
- 10's terrace by the fountain exists now, so it needs no backup.

### 3.2 Evarra (Vuultam, Chief Baker & Gardener)

A gardener without a garden, until there is one.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Window-Box Herb | East Agridome, morning | Her one lavender plant under a grow-lamp in the dead dome. | Outline |
| 4 | First Blossom | East Agridome; waits for the Sovereign | Real soil and wildflowers; she dances barefoot. | Outline |
| 6 | Honey & Brioche | Mess hall kitchen; waits for her first honey (after side arc 6) | They bake with the first honey. Unlocks Honey-Lavender Brioche. | Outline (Claude) |
| 8 | Wildflower Crown (confession) | East orchard at sunset | She weaves a blossom crown and confesses. Perk: Green Thumb. | Outline |
| 10 | The Moonlit Bakery | Mess hall, night | A tiered honey cake. Keepsake: a kept slice (Claude: a pressed-flower frame?). | Outline |

- **Gap:** no dialogue for any of the five.
- **Lock / Repeat:** 6 waits for side arc 6 (Operation Honeybee), which needs Jasper at 6 too, so her own event hangs on his hearts. And two scenes are about the first bees: side-arc 6 brings the hive, and the older bible had Evarra 6 bring it. Decision 8.
- **Lock:** 8 is in the East orchard, which only exists after the Sovereign, and 8s must not wait. Needs a backup (her window-box in the East Agridome would echo her 2).
- **Gap:** a slice of cake doesn't keep. Decision 14.
- **Repeat:** her single herb box is already the opening image of side-arc 2. Fine as continuity, but her 2 needs something of its own.

### 3.3 Freya (Human, Junior Shipwright)

Stepping out of her late father's shadow.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Stubborn Heating Pump | Engineering, 10:00–15:00 | A jammed valve; her father could tune them by ear. | Script |
| 4 | Blueprints in the Attic | Shipwright's Suite; backup: her father's locker in the bay | His unfinished FTL stabilizer plans. | Short |
| 6 | Test Flight | Shuttle Bay at dusk; waits for your ship to fly | EVA test of the stabilizer. Unlocks the Pioneer Stabilizer. | Short |
| 8 | Stargazing on the Hull (confession) | Shuttle Bay catwalk after 20:00 | She counts the minutes until you dock. Perk: Master Mechanic. | Script |
| 10 | Christening the Suite | Shipwright's Suite; backup: her work area in the bay | The "Echo Landing Shipwrights" sign, with Tikka, Sesska and Ana (if arrived). Keepsake: wrench pendant. | Outline |

- **Decided (Zachary, 22 Nov):** her father, **Jorvik**, died testing an earlier version of the same stabilizer. She joins your crew after Test Flight (6). Event 4 is renamed (no attic). Her 2 happens in Engineering.
- **Gap:** 4 and 6 have one line each and no choice.
- **Idea:** the status doc has Freya joining your crew at 6 hearts; no scene marks it. "Test Flight" is the natural moment for her to ask to fly with you.
- **Clash:** the script's 2 says "Engineering / Shuttle Bay"; the Master says Engineering. 4's title says "Attic", but there's no attic.

### 3.4 Job (Human, Heavy Miner)

A quiet man finding home on a moon he never chose.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | Gumbo in the Breakroom | Engineering break room, 16:00–19:00 | His granddaddy's Louisiana spice blend. | Script |
| 4 | Cave-In on Shaft Four | Cavern floor 4 | He braces a beam while you pull Zaas's gear free. Unlocks the Reinforced Mining Rig quest with Tikka. | Short |
| 6 | Lanterns by the Cavern Sea | Sea of Echoes shore; waits for the Harbinger | Zaas was right; the wildest dreams are under your boots. | Short |
| 8 | Quiet Ground (confession) | Hot springs at dusk; backup: Engineering break room | Perk: Bedrock Strength. | Script |
| 10 | Bayou Under the Stars | Sea of Echoes dock at night; backup (Claude): the Shuttle Bay windows | Rows you across the lake in a skiff he built with Tobbin. Keepsake (Claude): a carved oar charm. | Outline |

- **Clash:** the script's triggers still name old places: 2 "the Mines entrance breakroom", 4 "Mine Level 3" (the title says "Shaft Four"; the Master says cavern floor 4).
- **Gap:** 4 and 6 have no choice.
- 6 waits for the Harbinger (late Autumn), so it will often play after his 8. The rule allows it.
- **Repeat:** his skiff (10) and Zaas's research skiff (Zaas 8) are two boats on the same sea. They could be one: Job builds it with Tobbin, Zaas christens it.

### 3.5 Quill (Vuultam, Medical Assistant)

Maren's shy apprentice finding his own voice.

| ♥ | Event | When and where | What happens | Status |
|---|---|---|---|---|
| 2 | The Spilled Apothecary | Medbay, 11:00–15:00 | Spilled spore vials; he doubts he's a real medic. | Script |
| 4 | Field Notes in the Dark | Upper caverns (Vzz'ket on guard) | Cavern lichen plus Merrow's aloe. Unlocks Xeno-Salve. | Short |
| 6 | Doctor's Orders | Medbay, afternoon | Treats a miner alone; Maren puts his name on the clinic door. | Short |
| 8 | Heartbeat (confession) | Library or medbay, evening | A pressed glowing-fern bookmark. Perk: Guardian Medic. | Script |
| 10 | Constellation Study | Observation Lounge, night | Names a new plant after you. Keepsake: stethoscope-compass charm. | Outline |

- **Clash:** 8 is at "the Library / Medbay garden bench"; there's no medbay garden. The library suits his evening reading.
- **Gap:** 4 and 6 have no choice.
- **Idea:** in the prologue Quill notices "a brief electromagnetic spike" in your scans. His 4 or 6 could come back to it (he's been reading your scans; the Lexicon shows up again), tying a romance to the main story (thread E).

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
| Evarra 8 | East orchard; no backup | East Agridome (Decision 11) |
| Artie 8, 10 | East orchard; no backup | Plaza fountain (Decision 11) |
| Evarra 6 | Waits on side arc 6, which needs Jasper's hearts | Decision 8 |

### 7.4 Places in the scripts that aren't the game's maps

Job 2 "Mines entrance breakroom" (Engineering break room); Job 4 "Mine Level 3" (cavern floor 4); Quill 8 "Library / Medbay garden bench" (pick one); Stu 6 "West Wing Residential Corridor" (East Home 2?); Artie 10 "Library / Concourse" (East orchard); the Chitin Exodus "Mine Level 5" (floors 16–24); Ix'ali 6 "Shuttle Bay training mat" (no mat prop yet).

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
8. **The first bees:** Evarra 6 or side-arc 6? Whichever doesn't get them needs a new beat.
9. **Jasper & Evarra 8 waiting for the hotel:** allow it as an exception, or write a version without the hotel?
10. **Stu before the hotel opens:** his job, and backup places for 2, 6 and 8.
11. **Backups for the East orchard** (Evarra 8, Artie 8 and 10).
12. **Ix'ali's star pendant** at 8: an Oath-Crest you could propose with, or something else?
13. **Freya's father:** decided 22 Nov: **Jorvik**, who died testing an earlier version of the stabilizer. Still open: how long ago.
14. **Keepsakes marked (Claude):** Jasper's apron, Evarra's cake slice or pressed-flower frame, Job's oar charm.
15. **Hearts:** 100 points a heart, as in the NPC Master? Then the code is changed to match.
16. **"The Nest":** rename the cavern event or the pirate stronghold.
17. **Which Observation Lounge scenes move**, and where to.
18. **Eshu:** rename Tally in the game's text (lines, morning news, schedule name; the file id stays `tally`).
19. **"Awaken" or "restore"** for completing a Custodian's bundles.
20. **Which scenes Claude writes first.** Suggested order: the 27 confession pieces (7.1), then Jasper and Evarra, then the 10-heart scenes, then the platonic arcs, in the build order's places (S.A.R.A. 2, Job 2, Freya 2, Quill 2, Ix'ali 2 can play first).
