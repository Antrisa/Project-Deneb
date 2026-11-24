# Perks and keepsakes (24 Nov 2026)

Every perk and keepsake the heart events give, as the datapad's **Perks** tab shows them (Zachary, 24 Nov: "a tab in the inventory for perks, and the icons will be stuff like freyas wrench etc. showing all the perks you have").

- **In the game:** the Inventory page has a sixth filter, **Perks** (`datapad/datapad.gd _perk_grid`), beside All, Tools, Supplies, Materials and Gear. It shows the perks and keepsakes you have as icons; picking one shows who gave it, what it does, and NOT IN THE GAME YET for the ones whose effect isn't built. `scripts/datapad_bridge.gd _perks()` lists them from the story flags (`perk_<id>`, `keepsake_<id>`); the names, givers, effects and icon numbers are in `scripts/perk_data.gd`.
- **Icons:** `art/perks.png`, one 24x24 cell each. Stand-ins by Claude (`tools/dev/perk_icons.py`), drawn from simple shapes: something of the person who gave it. On the Art Fix List.
- **Checked by** `tests/check_heart_events.py`: every perk and keepsake an event gives has an entry and an icon. Not run in Godot yet.

## Perks

| Perk | From | Given by | What it does | In the game? | Icon (stand-in) |
|---|---|---|---|---|---|
| Pioneer Stabilizer (`pioneer_stabilizer`) | Freya | Freya 6, Test Flight | Jorvik's FTL stabilizer, finished at last. Your ship's jumps run steadier. | Not yet | Jorvik's stabilizer (a brass gyroscope) |
| Master Mechanic (`master_mechanic`) | Freya | Freya 8, Under the Star Dome | 20% off ship and tool upgrades. | Not yet | Freya's wrench |
| Parisian Bistro Menu (`parisian_bistro_menu`) | Jasper | Jasper 6, Taste of Paris | Jasper's bistro dishes, on the mess hall's menu. | Not yet | A bistro menu card |
| Sous-Chef's Blessing (`sous_chefs_blessing`) | Jasper | Jasper 8, A Table of My Own | Food buffs last 20% longer. | Not yet | Jasper's whisk |
| Honey-Lavender Brioche (`honey_lavender_brioche`) | Evarra | Evarra 6, A Hem of Wildflowers | A recipe: Evarra's brioche, once there's honey. | Not yet | A sprig of lavender |
| Green Thumb (`green_thumb`) | Evarra | Evarra 8, Wildflower Crown | Better-quality crops. | Not yet | Evarra's trowel |
| Wildflower Honey (`wildflower_honey`) | Jasper & Evarra | Jasper & Evarra 6, Operation Honeybee | The garden dome's bees make honey. | Not yet | A jar of wildflower honey |
| Starlight Souffle (`starlight_souffle`) | Jasper & Evarra | Jasper & Evarra 8, A Table for the Whole Sector | A recipe: Starlight Souffle & Lunar Truffle Glaze, a big boost at the Grand Hotel Inspection. | Not yet | A starlight souffle |
| Family Table (`family_table`) | Jasper & Evarra | Jasper & Evarra 8, A Table for the Whole Sector | Cooked meals restore 25% more health and energy. | Not yet | A place set at the family table |
| Bedrock Strength (`bedrock_strength`) | Job | Job 8, Quiet Ground | Mining uses 20% less energy, and more geodes turn up. | Not yet | Job's work gloves |
| Xeno-Salve (`xeno_salve`) | Quill | Quill 4, Field Notes in the Dark | A recipe: Xeno-Salve restores full health and cures what ails you. | Not yet | A jar of xeno-salve |
| Guardian Medic (`guardian_medic`) | Quill | Quill 8, Heartbeat | +20 max health, and collapsing costs no Scrip. | Not yet | Quill's pressed glowing fern |
| Star-Knight Aegis (`star_knight_aegis`) | Ix'ali | Ix'ali 6, Sparring at the Cavern Gate | Ix'ali can forge the Star-Knight Aegis armour tier. | Not yet | A star-knight shield |
| Chivalric Guard (`chivalric_guard`) | Ix'ali | Ix'ali 8, The Oath | Take 20% less damage. | Not yet | Ix'ali's star pendant |
| Junior Scout Reports (`junior_scout_reports`) | Artie | Artie 4, The Junior Scouts | The Junior Scouts mark rare finds on your map. | Not yet | A scouts' map with marks |
| Thrifty (`thrifty`) | Artie | Artie 8, Campfire Under Glass | Recycling and geodes sometimes give rare items. | Not yet | Artie's tin camp mug |
| Five-Star Partner (`five_star_partner`) | Stu | Stu 8, After-Hours Lobby Shift | +20% hotel income and tips. | Not yet | Stu's bellhop cap |
| Wingmate (`wingmate`) | Ana | Ana 8, Co-Pilot's Promise | +20% ship evasion, and faster FTL travel. | Not yet | Ana's navigator's compass |
| Concierge (`concierge`) | S.A.R.A. | S.A.R.A. 8, Night Shift | S.A.R.A. pings your datapad, and can send you to any of her pads. | Not yet | S.A.R.A.'s little holo-moon |
| Relic Appraisal (`relic_appraisal`) | Tar'Besh | Tar'Besh 8, Every Kind of Mind | +25% Scrip on museum donations. | Not yet | Tar'Besh's appraiser's loupe |
| Deep-Sea Sonar Lure (`deep_sea_sonar_lure`) | Zaas | Zaas 8, Captain of the Deep | A lure for the deep water, for when there's fishing. | Not yet | Zaas's sonar lure |
| Cavern Monster Radar (`monster_radar`) | Vzz'ket | Vzz'ket 8, The Watch Changes | S.A.R.A. warns you what's waiting on the floor below. | Not yet | S.A.R.A.'s motion sensor |
| Chitin-Piercer Traps (`chitin_piercer_traps`) | Vzz'ket & Rusk | Vzz'ket & Rusk 8, Sentinels of Echo Landing | Ix'ali's traps at the cavern gate. | Not yet | A chitin-piercer spike |
| Moogli Trade Beacon (`moogli_trade_beacon`) | Bram | Bram 8, Paid in Full | On a free flight, spend 1 fuel to call the Ollo family trader to where you are. | Yes | The Moogli trade beacon |
| Smelter Overclock (`smelter_overclock`) | Tikka | Tikka 8, Overclock | Every furnace smelts in half the time. | Yes | Tikka's furnace gauge |
| Void-Silk Linens (`void_silk_linens`) | Sesska | Sesska 8, Void-Silk | Luxury linens for the hotel's beds, once it takes paying guests. | Not yet | Folded void-silk |
| Advanced Med-Stims (`advanced_med_stims`) | Maren | Maren 8, Med-Stims | Medpacks heal twice as much. | Yes | Maren's med-stim |
| Lore Compendium (`library_lore_compendium`) | Owen | Owen 8, The Compendium | The codexes you find will fill it in. | Not yet | Owen's compendium |
| Heirloom Chair (`heirloom_chair`) | Tobbin | Tobbin 8, A Chair That Stays | The recipe: 3 real-wood planks and a hide, at a manufacturing hub. | Yes | Tobbin's chisel |
| Hydro-Boost (`hydro_boost`) | Merrow | Merrow 8, A Day Off | Your hydroponic beds grow 20% faster. | Yes | Merrow's grease pencil |
| Self-Defence Class (`self_defence`) | Garrick | Garrick 8, Self-Defence Class | On your own ship, your crew hit boarders half again as hard. | Yes | Garrick's chalk |
| Well Fed (`well_fed`) | Saffi | Saffi 8, The First Potluck | Your energy bar is 30 longer. | Yes | Saffi's soup bowl |

## Keepsakes

10-heart keepsakes. They have no effect: they are things to keep.

| Keepsake | From | Given by | Description | Icon (stand-in) |
|---|---|---|---|---|
| Wrench Pendant (`wrench_pendant`) | Freya | Freya 10, Christening the Suite | A tiny wrench on a chain, made from the wrench Jorvik gave her when she was six. | Freya's wrench pendant |
| Cafe Apron (`jasper_apron`) | Jasper | Jasper 10, Café Étoile | An apron with both your names stitched on the pocket. | Jasper's cafe apron |
| Pressed Flowers (`pressed_flower_frame`) | Evarra | Evarra 10, The Moonlit Bakery | The flowers from her crown, pressed and framed. | Evarra's pressed flowers, framed |
| Oar Charm (`oar_charm`) | Job | Job 10, Bayou Under the Stars | A little carved oar on a cord, worn smooth by his thumbs. | Job's oar charm |
| Stethoscope Compass (`stethoscope_compass`) | Quill | Quill 10, Constellation Study | A brass charm he engraved himself: a stethoscope on one side, a compass on the other. | Quill's stethoscope compass |
| Ceremonial Pauldron (`pauldron`) | Ix'ali | Ix'ali 10, Forged in Starlight | One of a matching pair she forged, lighter than it looks. | Ix'ali's ceremonial pauldron |
| Scoutmaster Badge (`scoutmaster_badge`) | Artie | Artie 10, Merit Badge of the Heart | Honorary Scoutmaster, by vote of the Junior Scouts. | The Honorary Scoutmaster badge |
| Silver Bell (`silver_bell`) | Stu | Stu 10, Suite for Two | A little silver bell like the one on the desk. Ring it and he'll come running. | Stu's silver bell |
| Flight Jacket (`flight_jacket`) | Ana | Ana 10, True North | A flight jacket in your size, Sesska's stitching. Hers has both your initials on the collar. | Ana's flight jacket |
| Family Photo (`family_photo`) | Jasper & Evarra | Jasper & Evarra 8, A Table for the Whole Sector | Jasper, Evarra and you, above the mess hall counter. | The family photo |

## Still to do

7 of the 32 perks work so far. The rest need wiring up, in batches; some wait for systems that aren't in the game yet (honey and bees, fishing, codexes, crop quality).
