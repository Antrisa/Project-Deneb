# Perks and keepsakes (24 Nov 2026)

Every perk and keepsake the heart events give, as the datapad's **Perks** tab shows them (Zachary, 24 Nov: "a tab in the inventory for perks, and the icons will be stuff like freyas wrench etc. showing all the perks you have").

- **In the game:** the Inventory page has a sixth filter, **Perks** (`datapad/datapad.gd _perk_grid`), beside All, Tools, Supplies, Materials and Gear. It shows the perks and keepsakes you have as icons; picking one shows who gave it, what it does, and NOT IN THE GAME YET for the ones whose effect isn't built. `scripts/datapad_bridge.gd _perks()` lists them from the story flags (`perk_<id>`, `keepsake_<id>`); the names, givers, effects and icon numbers are in `scripts/perk_data.gd`.
- **Icons:** `art/perks.png`, one 24x24 cell each: the thing the resident hands over or uses in that heart event. Stand-ins by Claude (`tools/dev/perk_icons.py`, redrawn 24 Nov) to the Art Style Guide v2's item-icon rules: master palette only, the `#5b332d` outline all round, filling about 20 of the 24 pixels, drawn straight on (only the oar lies on the diagonal, being long and thin), one main colour and one accent with a 2-px highlight at the top left, chunky shapes and no single-pixel specks. The script checks the palette and the size. On the Art Fix List (row 385) for the artist's pass.
- **Checked by** `tests/check_heart_events.py`: every perk and keepsake an event gives has an entry and an icon. Not run in Godot yet.

## Perks

| Perk | From | Given by | What it does | In the game? | Icon |
|---|---|---|---|---|---|
| Pioneer Stabilizer (`pioneer_stabilizer`) | Freya | Freya 6, Test Flight | Jorvik's FTL stabilizer, finished at last: an ion storm no longer halves your reactor. | Yes | Jorvik's FTL stabilizer: brass gimbal rings round a glowing core |
| Master Mechanic (`master_mechanic`) | Freya | Freya 8, Under the Star Dome | 20% off ship upgrades. | Yes | Freya's wrench, taped grip |
| Parisian Bistro Menu (`parisian_bistro_menu`) | Jasper | Jasper 6, Taste of Paris | Jasper's bistro dishes, on the mess hall's menu. | Not yet | A bistro chalkboard sign |
| Sous-Chef's Blessing (`sous_chefs_blessing`) | Jasper | Jasper 8, A Table of My Own | Food and drink buffs last 20% longer. | Yes | Jasper's balloon whisk |
| Honey-Lavender Brioche (`honey_lavender_brioche`) | Evarra | Evarra 6, A Hem of Wildflowers | A recipe: Evarra's brioche, once there's honey. | Not yet | A brioche with a sprig of lavender |
| Green Thumb (`green_thumb`) | Evarra | Evarra 8, Wildflower Crown | Better-quality crops. | Not yet | Evarra's wildflower crown |
| Wildflower Honey (`wildflower_honey`) | Jasper & Evarra | Jasper & Evarra 6, Operation Honeybee | The garden dome's bees make honey. | Not yet | A jar of wildflower honey, cloth lid |
| Starlight Souffle (`starlight_souffle`) | Jasper & Evarra | Jasper & Evarra 8, A Table for the Whole Sector | A recipe: Starlight Souffle & Lunar Truffle Glaze, a big boost at the Grand Hotel Inspection. | Not yet | A starlight souffle in its ramekin |
| Family Table (`family_table`) | Jasper & Evarra | Jasper & Evarra 8, A Table for the Whole Sector | Cooked meals restore 25% more health and energy. | Yes | A place set at the family table |
| Bedrock Strength (`bedrock_strength`) | Job | Job 8, Quiet Ground | Mining uses 20% less energy, and more geodes turn up. | Yes | Job's pick |
| Xeno-Salve (`xeno_salve`) | Quill | Quill 4, Field Notes in the Dark | A recipe: Xeno-Salve restores full health and cures what ails you. | Not yet | A jar of glowing xeno-salve |
| Guardian Medic (`guardian_medic`) | Quill | Quill 8, Heartbeat | Two more hearts of health, and collapsing costs no Scrip. | Yes | A heart with a medic's cross |
| Star-Knight Aegis (`star_knight_aegis`) | Ix'ali | Ix'ali 6, Sparring at the Cavern Gate | Ix'ali can forge the Star-Knight Aegis armour tier. | Not yet | A Star-Knight helm, violet crest |
| Chivalric Guard (`chivalric_guard`) | Ix'ali | Ix'ali 8, The Oath | Take 20% less damage. | Yes | Ix'ali's shield, a heart on it |
| Junior Scout Reports (`junior_scout_reports`) | Artie | Artie 4, The Junior Scouts | The Junior Scouts mark rare finds on your map. | Not yet | The scouts' folded map, marked with an X |
| Thrifty (`thrifty`) | Artie | Artie 8, Campfire Under Glass | Geodes sometimes hold rare finds. (Recycling too, once the station has a recycler.) | Yes | Artie's enamel camp mug, steaming |
| Five-Star Partner (`five_star_partner`) | Stu | Stu 8, After-Hours Lobby Shift | +20% hotel income and tips. | Yes | Stu's room key, its bow a five-pointed star |
| Wingmate (`wingmate`) | Ana | Ana 8, Co-Pilot's Promise | +20% ship evasion, and your fold drive charges a fifth faster. | Yes | Ana's pilot wings pin |
| Concierge (`concierge`) | S.A.R.A. | S.A.R.A. 8, Night Shift | S.A.R.A. sends you to any of her pads, and pings you each morning with what's ready. | Yes | One of S.A.R.A.'s holo pads, her light above it |
| Relic Appraisal (`relic_appraisal`) | Tar'Besh | Tar'Besh 8, Every Kind of Mind | +25% on the Scrip the museum pays you for every 5 relics you give. | Yes | Tar'Besh's appraiser's loupe |
| Deep-Sea Sonar Lure (`deep_sea_sonar_lure`) | Zaas | Zaas 8, Captain of the Deep | A lure for the deep water, for when there's fishing. | Not yet | Zaas's sonar lure, a fish with a glowing eye |
| Cavern Monster Radar (`monster_radar`) | Vzz'ket | Vzz'ket 8, The Watch Changes | S.A.R.A. warns you what's waiting on the floor below. | Yes | S.A.R.A.'s motion-sensor scope, a blip on it |
| Chitin-Piercer Traps (`chitin_piercer_traps`) | Vzz'ket & Rusk | Vzz'ket & Rusk 8, Sentinels of Echo Landing | Ix'ali's traps at the cavern gate. | Not yet | Ix'ali's spike trap |
| Moogli Trade Beacon (`moogli_trade_beacon`) | Bram | Bram 8, Paid in Full | On a free flight, spend 1 fuel to call the Ollo family trader to where you are. | Yes | Bram's grandfather's trade beacon, a lantern |
| Smelter Overclock (`smelter_overclock`) | Tikka | Tikka 8, Overclock | Every furnace smelts in half the time. | Yes | Tikka's regulator coil, copper wire wound fine |
| Void-Silk Linens (`void_silk_linens`) | Sesska | Sesska 8, Void-Silk | Luxury linens for the hotel's guest beds: every guest room is more comfortable. | Yes | A void-silk pillowcase, the glowing thread through it |
| Advanced Med-Stims (`advanced_med_stims`) | Maren | Maren 8, Med-Stims | Medpacks heal twice as much. | Yes | Maren's med-stim, a red dose in it |
| Lore Compendium (`library_lore_compendium`) | Owen | Owen 8, The Compendium | The codexes you find will fill it in. | Not yet | Owen's hide-bound ledger with tabs down the side |
| Heirloom Chair (`heirloom_chair`) | Tobbin | Tobbin 8, A Chair That Stays | The recipe: 3 real-wood planks and a hide, at a manufacturing hub. | Yes | Tobbin's chisel |
| Hydro-Boost (`hydro_boost`) | Merrow | Merrow 8, A Day Off | Your hydroponic beds grow 20% faster. | Yes | A seedling under Merrow's grow strip, blue up, red down |
| Self-Defence Class (`self_defence`) | Garrick | Garrick 8, Self-Defence Class | On your own ship, your crew hit boarders half again as hard. | Yes | Garrick's sparring glove |
| Well Fed (`well_fed`) | Saffi | Saffi 8, The First Potluck | Your energy bar is 30 longer. | Yes | Saffi's stew pot, steaming |

## Keepsakes

10-heart keepsakes. They have no effect: they are things to keep.

| Keepsake | From | Given by | Description | Icon |
|---|---|---|---|---|
| Wrench Pendant (`wrench_pendant`) | Freya | Freya 10, Christening the Suite | A tiny wrench on a chain, made from the wrench Jorvik gave her when she was six. | Freya's wrench pendant |
| Cafe Apron (`jasper_apron`) | Jasper | Jasper 10, Café Étoile | An apron with both your names stitched on the pocket. | Jasper's apron, two names stitched on the pocket |
| Pressed Flowers (`pressed_flower_frame`) | Evarra | Evarra 10, The Moonlit Bakery | The flowers from her crown, pressed and framed. | Evarra's pressed flowers, framed |
| Oar Charm (`oar_charm`) | Job | Job 10, Bayou Under the Stars | A little carved oar on a cord, worn smooth by his thumbs. | Job's carved oar charm, its cord wound round the shaft |
| Stethoscope Compass (`stethoscope_compass`) | Quill | Quill 10, Constellation Study | A brass charm he engraved himself: a stethoscope on one side, a compass on the other. | Quill's brass charm, a compass engraved on it |
| Ceremonial Pauldron (`pauldron`) | Ix'ali | Ix'ali 10, Forged in Starlight | One of a matching pair she forged, lighter than it looks. | Ix'ali's ceremonial pauldron |
| Scoutmaster Badge (`scoutmaster_badge`) | Artie | Artie 10, Merit Badge of the Heart | Honorary Scoutmaster, by vote of the Junior Scouts. | The Honorary Scoutmaster badge, a heart on it |
| Silver Bell (`silver_bell`) | Stu | Stu 10, Suite for Two | A little silver bell like the one on the desk. Ring it and he'll come running. | Stu's little silver desk bell |
| Flight Jacket (`flight_jacket`) | Ana | Ana 10, True North | A flight jacket in your size, Sesska's stitching. Hers has both your initials on the collar. | Ana's flight jacket |
| Family Photo (`family_photo`) | Jasper & Evarra | Jasper & Evarra 8, A Table for the Whole Sector | Jasper, Evarra and you, above the mess hall counter. | The family photo: Jasper, Evarra and you |

## Where each working perk is in the code

- Moogli Trade Beacon: `ship_map.gd` (Call trader). Smelter Overclock: `main.gd _furnace_use`. Advanced Med-Stims, Family Table: `main.gd _eat`. Heirloom Chair: `item_data.gd` recipe with `learn`. Hydro-Boost: `main.gd _grow_crops`. Self-Defence Class, Wingmate, Pioneer Stabilizer: `main.gd _my_fight` passes them to `ship_battle.gd` (and the jump map's ion-storm note). Well Fed, Guardian Medic: `main.gd _max_energy`, `_max_hp`, `_collapse`.
- Master Mechanic: `ship_upgrades.gd _discount` (tools are crafted, not bought, so it's ship upgrades only). Sous-Chef's Blessing: `shops.gd start_drink` (drinks are the only buffs so far). Bedrock Strength: `main.gd _mining_energy`, `shops.gd maybe_geode`. Chivalric Guard: `shops.gd damage_taken`. Thrifty: `shops.gd roll_geode`.
- Five-Star Partner, Void-Silk Linens: `hotel.gd base_pay`, `grade` (Five-Star replaced upstream's S.A.R.A. bonus, which counted her hearts on the old 5-a-heart scale). Relic Appraisal: `main.gd _museum_thanks` (the museum pays 250 Scrip at 5 relics, 500 at 10). Concierge: `main.gd concierge_rows`, `sara_send`, `_sara_pings`, `shops.gd` "Concierge". Cavern Monster Radar: `main.gd _radar_ping`, `_cav_mob_kinds`.

## Still to do

21 of the 32 perks work so far. The rest wait for something that isn't in the game yet:

- Thrifty's recycling half: there's no recycler.
- Honey and bees: Wildflower Honey, Honey-Lavender Brioche, Starlight Souffle. Fishing: Deep-Sea Sonar Lure. Codexes: Lore Compendium. Crop quality: Green Thumb.
- New recipes, items or a menu: Parisian Bistro Menu, Xeno-Salve, Star-Knight Aegis. The map: Junior Scout Reports. The cavern gate: Chitin-Piercer Traps.
