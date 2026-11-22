# Echo Landing: ship art, ship UI and ship design (21 Nov 2026)

The instructions from `Echo_Landing_Ship_Art_UI.zip` (Drive), all in one doc. The templates and reference pictures are only in the zip.

This pack covers everything for the space side of the game: ships, crew, weapons, effects, the battle screen and the other ship windows. It also includes templates for **designing** ships, weapons, systems and crew, so Claude can turn your designs straight into game data.

Nothing here is final until you say so. Anything marked **(Claude)** is a suggestion.

## What's in the pack
| File | What it covers |
|---|---|
| `1_SHIP_ART.md` | How to draw a ship: the cell grid, the hull and the cut-away interior, and which ships are needed |
| `2_CREW_ART.md` | Crew in battle (small top-down sprites), the repair drone, and the crew species |
| `3_WEAPONS_AND_EFFECTS.md` | Weapons on the hull, shots, hits, fire, breaches, explosions, space drones, store pictures |
| `4_SHIP_UI.md` | The battle screen, the event window, the store, the ship screen, the jump map, backdrops |
| `5_DESIGN_SHIPS.md` | A fill-in template for designing a ship, with two filled-in examples |
| `6_DESIGN_WEAPONS_SYSTEMS_CREW.md` | Templates and rules for weapons, systems, drones, augments and crew, and how ships work in a fight |
| `7_MORE_LIKE_FTL.md` | Everything that would make the space side play more like FTL: what's built, what's planned, and suggestions |
| `templates/` | Blank grids and sheets at the exact sizes, plus `_guide` versions with labels |
| `reference/` | What the game looks like now, the existing ship art, and the map mock-ups |

## Three decisions to check first (Claude)
1. **One room cell is 24 × 24, the same as one station tile and one character wide.**
   - Ships are drawn at the station's pixel size. **In battle each ship has a window of its own, and the game fits the ship to it** (Zachary, 21 Nov): as big as fits, at a whole number of screen pixels per art pixel so it stays crisp. A small ship is shown bigger; only a ship too big for its window is shrunk.
   - The same picture works in the Shuttle Bay and in battle. The starter fighter is exactly 7 × 4 cells (168 × 96) and shows at 2× in battle.
   - How big each size shows: section 1.1. The battle screen: section 4.3.
2. **Every ship is drawn facing right, nose pointing right.** When a ship is an enemy, the game mirrors it so it faces left.
   - One picture serves as both an enemy and a captured ship you fly.
   - Avoid writing or numbers on hulls, because they would read backwards when mirrored.
3. **The game draws all words and numbers, and fills the bars.** You draw the frames, buttons, icons and bar segments; the game puts text and values in them. That keeps the text crisp and easy to change.

## Order of work (Claude's suggestion)
1. The starter fighter's cut-away interior, and the repair drone (`1_SHIP_ART.md` section 3, `2_CREW_ART.md` section 3).
2. The four story ships: the Rabble Cutter, Ivan's flagship, Ana's corsair and the loyalist gunship. Each needs a hull and an interior.
3. ~~The battle UI kit~~: not needed now; the ship screens use the datapad's parts (section 4).
4. Weapons, shots, hits, fire and explosions (`3_WEAPONS_AND_EFFECTS.md`).
5. Crew sprites: a human crew member and a Rabble pirate first.
6. ~~The event window and the store window~~: built in the datapad style; only store pictures (section 3.5) are wanted.
7. Backdrops for the four zones.
8. Your new ship, weapon and system designs, written with the templates in files 5 and 6.

## Rules for every picture
- **Crisp pixel art:** each pixel fully solid or fully see-through. No soft edges, no anti-aliasing, no blur, no resizing after drawing.
- **Exact sizes,** with no margins or padding unless a template has them.
- **PNG files,** with exactly the names and folders given.
- **Lit from the top left,** matching the station art.
- The station palette and the existing ship are in `reference/`.

## Sending it back
- Zip the pictures in their folders as named (`art/ships/...`, `art/ui/ship/...`).
- Put your design sheets (files 5 and 6, filled in) at the top of the zip.
- Partial sets are fine. Anything the game finds, it uses, and the rest stays drawn in code.

---

## 1. Ship art

### 1.1 The cell grid
- A ship is built on a grid of **cells, each 24 × 24 pixels** (one station tile). Rooms are made of whole cells, and walls run along cell edges.
- **Common room sizes:** 1 × 1, 2 × 1, 1 × 2 and 2 × 2 cells. Long bays like the starter fighter's weapon pod (4 × 1) are fine.
- **One cell holds one crew member** standing still. A 2 × 2 room holds four.
- **How big a ship shows in battle** (21 Nov; on a 1920 × 1080 screen, where the battle page is 768 × 432 at 2 screen pixels per page pixel). The ship has 364 × 194 page pixels in your window and 244 × 150 in the enemy window, after room for its shield bubble:

  | Ship size | In your window | In the enemy window |
  |---|---|---|
  | up to 5 × 3 cells (120 × 72) | 2× | 2× |
  | up to 6 × 4 cells (144 × 96) | 2× | 1.5× |
  | up to 7 × 4 cells (168 × 96), the starter | 2× | 1× |
  | up to 10 × 5 cells (240 × 120) | 1.5× | 1× |
  | up to 10 × 6 cells (240 × 144) | 1× | 1× |
  | up to 15 × 8 cells (360 × 192) | 1× | 0.5× |
  | bigger | 0.5× | 0.5× |

- **Largest sizes, to stay at 1× or more:**
  - Player ships: **15 × 8 cells (360 × 192).** (This replaces 12 × 9: a ship 9 cells tall would be shown at half size.)
  - Enemy ships: **10 × 6 cells (240 × 144).** The Nest and other stations can be bigger; they will be shown at half size, or get a bigger window later.
- A ship's crew, drone and room markings are scaled with it. Small ships are enlarged to 2× at most.
- The picture's size is the grid's size: width = cells across × 24, height = cells down × 24. The hull can include cells with no room in them (noses, fins, engine pods).
- Templates (made before the two windows, so a row or two bigger than the new largest sizes):
  - `templates/ship_grid_player_max_12x9.png`: use at most 8 rows;
  - `templates/ship_grid_enemy_max_10x8.png`: use at most 6 rows;
  - the `_guide_x4` versions, which number every cell

### 1.2 The files for one ship: `art/ships/<ship id>/`
| File | What it is |
|---|---|
| `hull.png` | The ship from outside, rooms covered. Used in the Shuttle Bay, on enemies before your sensors see inside, and on the jump map. |
| `interior.png` | **Same size.** The cut-away: the hull outline and edge plates, then every room's floor, inner walls (2 px on the cell edges), and a console or machine where the room's system sits. Leave door gaps in the walls; the game draws the doors. |
| `gib_1.png` … `gib_5.png` | **Same size.** The pieces the ship breaks into when destroyed, each picture showing only its piece. Three to five pieces. |
| `thruster.png` (optional) | The engine flame: 4 frames of 24 × 24 side by side, pointing left (out of the back). The game places it at the engine points in the design. If missing, a shared flame is used. |

**What the game draws on top:** doors, system icons, damage tint, fire, breaches, low-oxygen tint, crew, weapons on their mounts, shields and targeting.

**Weapon mounts:** the design (file 5) says which cell and which edge each weapon sits on. Draw a small hardpoint there in `hull.png` and `interior.png`; the weapon picture goes on top.

### 1.3 The starter fighter (done, 21 Nov)
Redrawn by Claude after the intro movie and approved by Zachary: plane wings with an orange band, twin engine pods
out behind, a teal canopy, crisp pixel art with shading and depth. Drawn by `tools/dev/ship_art/starter.py`
(`pixkit.py` does the shading), which writes `art/ships/starter/hull.png`, `interior.png` and the Shuttle Bay's
four repair stages in `art/lunar/player_ship.png`.

```
. E W S C C .      E  Engines (feeding the pods)       S  Shields
. E D O C C .      W  Weapons (the gun breech)         O  Oxygen
                   D  Drone bay (the drone's pad)      C  Cockpit, 2 x 2 under the long canopy
```

- A single-seat fighter (Zachary): behind the cockpit are sealed machinery bays the player can't enter; the repair
  drone gets into them through small hatches. Other ships are walkable all through.
- Guns sit near the wing tips; the thrusters glow at the back of the pods.

### 1.4 Ships needed
Sizes are Claude suggestions. Design each one with the template in file 5.

| Ship id | Who | Size (cells) | Notes |
|---|---|---|---|
| `starter` | you | 7 × 4 | Interior only (section 1.3) |
| `rabble_cutter` | Rabble raider | 5 × 4 | Small, patched, spiky. The first fight. |
| `ivan_flagship` | Ivan (boss) | 9 × 6 | Big and ugly. A heavy gun mount for his overcharged cannon. (Was 9 × 7; 6 rows keeps it at 1×.) |
| `ana_corsair` | Ana (boss) | 7 × 5 | Sleek and fast, a navigator's ship: big engines, small guns. |
| `loyalist_gunship` | Ivan's loyalists | 5 × 4 | A Rabble cutter variant with more guns |
| `covered_fighter` | you (Freya's quest) | 9 × 5 | The tarp-covered fighter in the bay (`reference/tarp_fighter_x3.png`). Your first bigger ship, with a crew deck and walkable rooms. |
| `terran_patrol` | Terran patrol | 7 × 5 | Clean white and blue, by the book |
| `zaash_skiff` | Zaa'sh pilgrims / duellists | 6 × 4 | Bone and bronze, ribbed, a shrine mast |
| `collective_freighter` | Collective convoy / distress | 8 × 5 | Patched cargo modules, green-grey, mismatched |
| `moogli_trader` | stores | 6 × 5 | Round, cargo pods, bright colours |
| `ooma_ship` | Ooma (special merchant) | 7 × 5 | Scyldar: sea-creature shapes, teal and coral |
| `pirate_stronghold` | special sector | 8 × 6 | A small asteroid base with turrets. The smaller strongholds after the Nest. |
| `rabble_nest` | the Nest (one-time raid) | 10 × 6, or bigger | The Rabble's main asteroid base, filling the enemy window. Bigger than 10 × 6 shows at half size unless it gets a bigger window. |

### 1.6 Double resolution: every ship at 48 px per cell (21 Nov, drafts)
Zachary: "lets double the pixels", then "lets do all the ships before we add to game". Every ship is now drawn at
**48 art pixels per cell** (twice the detail; rooms are still counted in cells). Mock-ups, not in the game yet.

| Script (`tools/dev/ship_art/`) | Ships |
|---|---|
| `kit2x.py` | Shared helpers: plates, nozzles, turrets, windows, stencils, wear, the lineup sheet |
| `rabble_cutter_2x.py` | Rabble cutter, 6 × 4 (approved) |
| `fleet2x.py` | Terran patrol 7 × 4, Zaa'sh skiff 6 × 4, Vuultam garden ship 7 × 4, Moogli trader 6 × 4, Ervani courier 6 × 4, Scyldar lantern ship (Ooma) 7 × 4, Arachnay weaver 6 × 4, Collective freighter 8 × 5 |
| `story2x.py` | Starter fighter 7 × 4 (same approved shape), Ivan's flagship 9 × 6, Ana's corsair 7 × 5, loyalist gunship 5 × 4, covered fighter 9 × 5 |
| `bases2x.py` | Pirate stronghold 8 × 6, the Rabble Nest 10 × 6, and `piratize2x()`: a Rabble repaint of every culture ship |

Run any of them from the repo root: `python3 -I tools/dev/ship_art/fleet2x.py <out dir>`.

**In the game (21 Nov):** the battle screen takes a per-ship `"art_scale"` (2 for these) and `"art"`/`"interior"`
paths; ships with art are mirrored to face you. The **Rabble cutter** is the first one in: 6 × 4 cells with six rooms
(engines, crew, shields, weapons, oxygen, a 1 × 2 cockpit) and eight doors, cut away by `kit2x.interior()`; its
`ROOMS` and `DOORS` in `rabble_cutter_2x.py` must match `ShipData.ENEMIES["rabble_cutter"]`.
Rooms hold **consoles, not furniture** (Zachary, 21 Nov): one console in each shields, weapons, engines and cockpit
room, where crew stand on station and boost the system (shields recharge faster, weapons arm faster, engines and
the cockpit add evasion). Oxygen and crew rooms are bare deck. A console never sits where a door is: the cockpit's goes on its front wall,
the others on a top wall, else bottom, left or right, in the first cell with a door-free outside wall there; crew stand
in the middle of that cell (`kit2x.console_at()` and `ShipBattle._console_at()` keep in step).

**For the rest:** each ship gets FTL-simple rooms and doors the same way, and the battle screen uses its
`art_scale` (2 for these): the picture is fitted on its art pixels, while rooms, crew and the drone stay in 24-px cell
units. At 1080p a 2x ship shows at 1 screen pixel per art pixel, so it looks the same size as a 1x ship did at 2x.

### 1.5 Style by faction (Claude)
- **Terran:** white hull, orange or blue trim, 45-degree plates, like your fighter.
- **The Rabble:** rust and gunmetal, welded patches, red stripes, spikes and trophies.
- **Zaa'sh:** bone-white and bronze, ribbed like a carapace, small bells and banners.
- **Collective:** green-grey, utilitarian, bolted-together modules that don't quite match.
- **Moogli:** rounded, cheerful colours, lots of cargo racks and hanging goods.
- **Scyldar (Ooma):** smooth, finned, teal and coral, like something from the sea.

---

## 2. Crew art (in battle)

Inside ships, crew are small **top-down** sprites, one per cell, like FTL's. They are separate from the 24 × 48 station sprites.

### 2.1 A crew sheet: `art/ships/crew/<id>.png` (96 × 216)
Frames of **24 × 24**, 4 across, 9 rows. Keep the body inside the middle 18 × 18, so two crew in neighbouring cells don't touch. `templates/crew_sheet_template.png` is the blank; `templates/crew_sheet_guide_x4.png` labels it.

| Row | Animation | Frames |
|---|---|---|
| 1 | walk down | 4 |
| 2 | walk up | 4 |
| 3 | walk right (mirrored for left) | 4 |
| 4 | at a station, facing up (working a console) | 2 |
| 5 | repair, facing up (tools, sparks) | 4 |
| 6 | fight, facing right | 4 |
| 7 | put out a fire, facing up | 4 |
| 8 | knocked out (lying down) | 1 |
| 9 | idle, facing down | 2 |

### 2.2 Who needs a sheet
- **Hired crew, one sheet per species** (Claude). The game tints the uniform, so leave uniforms a plain mid grey.
  - human
  - zaash
  - arachnay (four arms)
  - moogli
  - ervani
  - vuultam
  - scyldar
- **Enemies:**
  - `rabble_pirate`: human, rust and red, bandana or mask;
  - `rabble_zaash`: a Zaa'sh pirate;
  - `terran_marine`: white armour.
- **Residents who can crew** (at 6 hearts):
  - `freya`: work overalls and goggles;
  - `ana`: pilot's jacket with the torn-off insignia.
- **You:** `player`. One neutral sheet in your colours for now. A version layered like the character creator can come later.

### 2.3 The repair drone: `art/ships/crew/repair_drone.png` (96 × 48)
- **Row 1:** moving, 4 frames: a small hovering bot with a little bob.
- **Row 2:** repairing, 4 frames: arms or welder out, with sparks.
- It is your first crew member: you select it and send it bay to bay. Make it readable at a glance and a little cute. Yellow and white matches the current stand-in.
- Templates: `templates/drone_sheet_template.png` and `templates/drone_sheet_guide_x4.png`.

### 2.4 The crew list
The crew list cards on the left of the battle screen show each crew member's **idle frame** (row 9, frame 1). No separate faces are needed.

---

## 3. Weapons and effects

Everything faces or flies **right**. The game mirrors pictures for enemies.

### 3.1 Weapons on the hull: `art/ships/weapons/<weapon id>.png`
- **Small weapons:** 6 frames of **24 × 24** side by side (144 × 24). **Large weapons** (beams, heavy guns): 6 frames of **48 × 24** (288 × 24).
- **The frames:**
  1. idle
  2. charging 1
  3. charging 2
  4. ready (a glow)
  5. firing 1 (muzzle flash)
  6. firing 2 (recoil)
- The barrel points right, and the mount sits at the left middle of the frame.
- Templates: `templates/weapon_small_strip.png` and `templates/weapon_large_strip.png`, with `_guide` versions.
- **Weapons in the game now:**
  - `burst_laser` (yours, small, two shots);
  - `rabble_laser` (small);
  - `heavy_laser` (small, bigger barrel);
  - `ivan_cannon` (large, Ivan's overcharged gun).

### 3.2 Shots: `art/ships/shots/<type>.png`
3 frames of **16 × 8**, flying right (`templates/projectile_strip.png`). One per kind of shot:

| Type | Look (Claude) |
|---|---|
| `laser` | A short bright bolt; colour per faction: yours orange-red, Rabble green |
| `heavy_laser` | A thicker, longer bolt |
| `ion` | A blue crackling orb |
| `missile` | A small missile with a flame trail |
| `flak` | Three small shards (the game scatters them) |
| `cannon` | Ivan's: a big gold slug |

**Beams** are drawn as a repeating segment. `beam_<id>.png` is 8 × 6 with 2 frames, plus `beam_<id>_end.png` (8 × 8, 2 frames) for where it hits.

### 3.3 Effects: `art/ships/fx/<name>.png`
6 frames of **24 × 24** unless noted (`templates/impact_strip.png`).

| Name | What |
|---|---|
| `hit` | A shot hitting the hull: flash, debris |
| `ion_hit` | Blue static crawling over a room |
| `shield_hit` | A ripple on the shield. The game places it on the shield's edge, facing the shot. |
| `fire` | One cell on fire. **4 frames, looping.** |
| `breach` | A hole in the floor, air rushing out. 4 frames, looping. |
| `smoke` | Light smoke for damaged rooms. 4 frames, looping. |
| `sparks` | Repair sparks. 4 frames. |
| `teleport` | Crew beaming in or out (later: boarding) |
| `ship_explosion` | **8 frames of 64 × 64** (`templates/explosion_strip.png`). The game plays several over a dying ship while the gibs drift apart. |

The jump effect (stars stretching into streaks) is drawn by the game.

### 3.4 Drones outside the ship (later): `art/ships/drones/<id>.png`
4 frames of **16 × 16** each.
- `combat_drone`: flies round the enemy and shoots;
- `defence_drone`: shoots down incoming missiles;
- `boarding_drone`: punches into an enemy room.

### 3.5 Store pictures: `art/ships/store/<id>.png`
**48 × 48**, one per thing you can buy: each weapon, drone, augment and system. They're shown in the store and on the ship screen. Draw them like item icons: the object on its own, a little angled, with a dark outline.

---

## 4. Ship UI

**Decided (Zachary, 21 Nov): the ship screens use the Terran field datapad's look**, from the Space UI pack. Its parts (the housing, panel liner, icons and fonts) are the datapad's own, already in `datapad/art`, so **no new UI art is needed** for the ship screens. The pack's ships were not used; ships and interiors will be redrawn.

All four screens (battle, jump map, event window, store) are drawn on one **768 × 432 page**, the same page the datapad uses, fitted to the window with whole-pixel steps (`ui/ship_screen.gd`). **The game draws all text and numbers.** Mock-ups: `datapad_map_x2.png`, `datapad_event_x2.png`, `datapad_store_x2.png` and `battle_two_windows_x2.png` in the Drive folder.

### 4.1 Look
The datapad's case with its TERRAN | FIELD DATAPAD title row; cream panels with an icon and a heading; dark green-grey scope windows (warmer grey for the enemy) with a grid, ticks and corner marks; orange accents.

### 4.2 Optional later: a ship kit, `art/ui/ship/`
Not needed now: the datapad parts cover every screen. These would only replace shapes the game draws itself (power bars, pips, icons).
| File | Size | Notes |
|---|---|---|
| `panel.png` | 24 × 24, **nine-slice** | Every window and box. 8-px corners. See `templates/nine_slice_guide_x8.png`. |
| `panel_dark.png` | 24 × 24, nine-slice | Inset areas inside panels (text boxes, slots) |
| `button.png` | 4 frames of 24 × 24, nine-slice | Normal, hover, pressed, disabled |
| `button_blue.png` | 24 × 24, nine-slice | A choice that needs something you have (an event choice, as in FTL) |
| `tab.png` | 2 frames of 24 × 24, nine-slice | Tab, and tab selected |
| `power_bar.png` | 4 frames of **16 × 5** | One power bar segment: powered (green), unpowered (dark), damaged (red), ion-locked (blue) |
| `hull_pip.png` | 3 frames of **6 × 10** | One hull point: full (green), low (red, when hull is a third or less), empty |
| `shield_pip.png` | 2 frames of **12 × 12** | Shield layer up, and down |
| `charge_bar.png` | 3 frames of 8 × 4, three-slice | Weapon and fold drive charge: left end, middle (repeats), right end |
| `icons_systems_16.png` | 16 × 16 each | **White on clear**; the game tints them green, red, grey or blue. Order in `templates/icons_systems_16_guide.png`. |
| `icons_resources_12.png` | 12 × 12 each, in colour | Hull, fuel, missiles, drone parts, Scrip, crew, shield, evasion, oxygen, power. Order in `templates/icons_resources_12_guide.png`. |
| `icons_map_12.png` | 12 × 12 each | Beacon, distress, store, special, stronghold, the Landing, your ship, visited. Order in `templates/icons_map_12_guide.png`. |
| `cursor_target.png` | 2 frames of 16 × 16 | Aiming a weapon |
| `cursor_move.png` | 16 × 16 | Ordering crew or the drone to a room |
| `door.png` | 4 frames of 24 × 4 | A door, closed to open, lying along a cell edge. The game turns it for vertical walls. |
| `select_ring.png` | 24 × 24 | Drawn round a selected crew member or the drone |

### 4.3 The battle screen
Mock-up: `battle_two_windows_x2.png` (Zachary, 21 Nov: "seperate each ship in the combat screen into like two screen so we can resize the ship"). Page positions, on the 768 × 432 page:
- **Top strip (y 55 to 71):** your hull pips, shields, evasion and oxygen; the fold drive bar; Jump and Auto(fire).
- **Your window (53, 75, 388 × 218):** your ship, fitted to the window (section 1.1), with its shield bubble.
- **The enemy window (447, 75, 268 × 218):** a band along the top with their name, hull, shields, evasion and crew; their ship below it, fitted the same way.
- **Shots** leave one window and come in from the near edge of the other, as in FTL.
- **Bottom panels (y 297 to 380):** Reactor (power bars per system; click to add, right-click to take away), Weapons (a card per slot: name, charge bar, what it's doing), Aboard (you and the drone; later the crew list).
- **Bottom row:** what's happening or what to do next, and Pause / Resume.

### 4.4 Arriving at a stop, and the event window
Built (21 Nov); mock-up `datapad_event_x2.png`. The stop is shown in a scope window at the top, the event in a panel below that grows with the text.
- **Arriving (Zachary, 21 Nov):** your ship jumps to the stop, the backdrop changes, and **a window comes up**, like FTL, instead of dialogue boxes.
- **The window:** a title, the text, then up to four choice buttons, and an outcome strip with resource icons and numbers.
- **Choice states:**
  - normal and hover;
  - **blue**: needs something you have (a crew member, a weapon, the drone);
  - **grey**: needs something you don't have.

### 4.5 The store window
Built (21 Nov); mock-up `datapad_store_x2.png`. Slots are 98 × 112 page pixels, with the 48 × 48 store picture.
- **Tabs:** Weapons, Systems, Crew, Drones & parts, Augments, and a Buy / Sell switch.
- **Item slots:** the 48 × 48 store picture, the name and the price. States: normal, hover, picked, empty.
- **Item details** on the right.
- **Bottom:** resources (fuel, missiles, drone parts), and hull repair (repair 1, repair all).

### 4.6 The ship screen (from the SHIP button)
Layout: `templates/ui_ship_screen_x2.png`.
- **Tabs:**
  - **Upgrades:** each system's bars, with an upgrade button and price; the reactor.
  - **Crew:** names, species, skills, and dismissing someone.
  - **Equipment:** swap weapons and drones in and out of slots; cargo.
- Upgrade bar segments use `power_bar.png` plus one more frame: **bought but not powered** (outlined).

### 4.7 The jump map
Built (21 Nov); mock-up `datapad_map_x2.png`. The map is drawn by the game with the zone colours in the datapad's scope, with the next stop and your ship's stores beside it. No art is needed; 12 × 12 stop icons could replace the dots later.

### 4.8 Backdrops: `art/ships/backdrops/<name>.png` (on hold)
The datapad screens show space in scope windows rather than full-screen backdrops, so these are on hold. If wanted later, they would go in the event window's scene (662 wide, 64 to 330 tall). Keep them dark and low in contrast.
- `home`: the blue gas giant and the moon.
- One per zone, each with 2 versions:
  - `terran_1`, `terran_2`: blue, tidy, distant patrol lights;
  - `zaash_1`, `zaash_2`: amber and bronze;
  - `collective_1`, `collective_2`: green;
  - `reach_1`, `reach_2`: red haze, wreckage.
- Hazards for later:
  - `asteroids`: asteroid field;
  - `nebula`;
  - `star`: close to a star;
  - `ion_storm`.
- **Optional:** planets and moons as separate pictures (`backdrops/props/`), so the game can mix them.

---

## 5. Designing a ship

Copy the template below for each ship. Claude turns it into game data (`scripts/ship_data.gd`) and checks that the layout works: every room reachable, doors on shared edges, weapon mounts on the hull. Rules for each system and weapon are in file 6.

### The template
```
SHIP: <name>
Id: <short id, lowercase, no spaces, e.g. rabble_cutter>
Faction: Terran | Rabble | Zaa'sh | Collective | Moogli | Scyldar | other
Used by: player | enemy | both (an enemy you can capture and fly)
How you get it: shipyard (price) | quest | capture | not flyable
Size: <cells across> x <cells down>        (player max 15 x 8, enemy max 10 x 6; nose pointing right)

Layout: one character per cell. "." = hull with no room. The same letter = one room
(its cells must touch). Use any letters you like and list them under Rooms.
  . . . .
  . . . .

Rooms:
  <letter> = <room name>, system: <shields | engines | weapons | oxygen | medbay | drone control |
             teleporter | cloak | cockpit | sensors | doors | repair drone bay | none>, crew can enter: yes/no
Doors: between cells, e.g. (2,1)-(3,1). Airlocks (doors to space): cell and edge, e.g. (0,2) left.
Weapon mounts: 1 = cell (x,y) top edge, 2 = ...      (one per weapon slot)
Engine flames: cell (x,y) left edge, ...

Hull: <points>                      (starter 12, Rabble Cutter 8, Ivan 14)
Reactor: <bars>                     (starter 6)
Systems, max bars / starting bars:  e.g. Shields 4/2, Engines 3/1, Weapons 4/2, Oxygen 2/1
Subsystems:                         e.g. Cockpit 1, Sensors 1, Doors 1
Weapon slots: <n>    Starting weapons: <ids>
Drone slots: <n>     Starting drones: <ids>
Augment slots: <n>   Starting augments: <ids>
Crew: <how many>, <species>, <who stands where>
Quirk: <one line: what makes this ship different to fly or fight>

As an enemy:
  Behaviour: aggressive | careful | flees when hull is low | offers to surrender when hull is low
  Targets: what its guns go for first (e.g. your shields, your weapons, at random)
  Drops: Scrip, fuel, missiles, parts, items, chance of a weapon

Look: notes for the art (shape, colours, details)
```

### Example 1: the starter fighter (in the game now, on the new grid)
```
SHIP: Your fighter
Id: starter
Faction: Terran
Used by: player
How you get it: you crashed in it; Tikka repairs it
Size: 7 x 4

Layout:
  . W W W W . .
  . L D S S C .
  . L D S S C .
  . E E E E . .

Rooms:
  W = Weapons bay, system: weapons, crew can enter: no (the drone can)
  E = Engine bay, system: engines, crew can enter: no (drone)
  L = Life support, system: oxygen, crew can enter: no (drone)
  D = Drone bay, system: repair drone bay, crew can enter: no (drone's home)
  S = Shields, system: shields, crew can enter: no (drone)
  C = Cockpit, system: cockpit, crew can enter: yes (only you fit)
Doors: none for crew. Drone ducts link D to W, E, L and S. A hatch from C to S.
Weapon mounts: 1 = cell (4,0) right edge, 2 = cell (4,3) right edge
Engine flames: cell (1,0) left edge, cell (1,3) left edge

Hull: 12
Reactor: 6
Systems: Shields 2/2, Engines 2/1, Weapons 2/2, Oxygen 1/1
Subsystems: Cockpit 1, Repair drone bay 1
Weapon slots: 2    Starting weapons: burst_laser
Drone slots: 0
Augment slots: 1
Crew: you (cockpit) and the repair drone
Quirk: sealed bays, so the drone is the only one who can repair; nobody can board you, and you can't board anyone.

Look: the existing white-and-orange fighter. The interior is tight machinery bays, ducts and one seat.
```

### Example 2: a Rabble Cutter (a proposal; the game uses an outline for it now)
```
SHIP: Rabble Cutter
Id: rabble_cutter
Faction: Rabble
Used by: both (capturable)
How you get it: capture contract
Size: 5 x 3

Layout:
  . W W W .
  E S C C P
  E O C C P

Rooms:
  W = Gun deck, system: weapons, crew can enter: yes
  E = Engines, system: engines, yes
  S = Shields, system: shields, yes
  O = Oxygen, system: oxygen, yes
  C = Crew deck, system: none, yes
  P = Cockpit, system: cockpit, yes
Doors: (0,1)-(1,1), (0,2)-(1,2), (1,1)-(2,1), (1,2)-(2,2), (2,0)-(2,1), (3,1)-(4,1). Airlock: (0,2) left.
Weapon mounts: 1 = cell (1,0) top edge, 2 = cell (3,0) top edge
Engine flames: cell (0,1) left edge, cell (0,2) left edge

Hull: 8
Reactor: 6
Systems: Shields 2/2, Engines 1/1, Weapons 2/2, Oxygen 1/1
Subsystems: Cockpit 1, Doors 1
Weapon slots: 2    Starting weapons: rabble_laser, rabble_laser
Crew: 3 rabble_pirate: one in the cockpit, one on the gun deck, one on shields
Quirk: cheap and nasty: two light lasers that fire close together to get past one shield layer.

As an enemy:
  Behaviour: aggressive; flees when hull is low (charges its fold drive)
  Targets: your shields first, then at random
  Drops: 30-50 Scrip, sometimes a hull plate or a missile

Look: rust and gunmetal, a welded-on gun deck, a red stripe, spikes on the bow.
```

---

## 6. Designing weapons, systems, drones, augments and crew, and how a fight works

Numbers in the game now are marked **(now)**; everything else is **(Claude)** until you decide. All of it is first guesses to tune in play.

### 6.1 Weapons

#### Template
```
WEAPON: <name>
Id: <short id>
Type: laser | ion | missile | beam | flak | bomb | special
Size: small (24 x 24 on the hull) | large (48 x 24)
Power: <bars it needs>          Charge time: <seconds>
Shots per volley: <n>           Damage per shot: <hull points>
Ammo: none | 1 missile per volley
Shield: stopped by a layer | pierces 1 layer | ignores shields
Extras (chance per hit): fire <%>, breach <%>, ion <seconds the room's system is locked>,
        crew damage <amount>, stun <seconds>
Price: <Scrip>     Where sold: stores | special merchant | quest | capture
Description: <one line for the store>
```

#### Kinds of weapon (Claude, after FTL)
| Type | How it plays |
|---|---|
| **Laser** | Bursts of shots. Each shot is stopped by a shield layer, so several shots strip shields and the rest get through. |
| **Ion** | Knocks off a shield layer and locks the system for a few seconds, but does no hull damage. **Needed for capture contracts.** |
| **Missile** | Uses a missile, but ignores shields. Good at starting fires and breaches. |
| **Beam** | Charges slowly, then sweeps a line across rooms. A shield layer cuts its damage by one. Strong once shields are down. |
| **Flak** | A cloud of shards. Each can be dodged; lots of hits on shields. |
| **Bomb** | Teleported into a room, ignoring shields. Needs a teleporter or a special weapon. |

#### Weapons in the game now
| Id | Type | Power | Charge (s) | Shots | Damage | Notes |
|---|---|---|---|---|---|---|
| `burst_laser` | laser | 2 | 9 | 2 | 1 | Yours |
| `rabble_laser` | laser | 1 | 11 | 1 | 1 | Rabble |
| `heavy_laser` | laser | 1 | 14 | 1 | 2 | Ivan, Ana |
| `ivan_cannon` | special | 0 | 16 | 1 | 3 | Ivan's second phase; a hit on his weapons room drains it |

### 6.2 Systems
**Main systems** take reactor power, one bar at a time. **Subsystems** don't: they work, or they don't, and their bars come from upgrades.

| System | Kind | What each bar does |
|---|---|---|
| **Shields** | main | Every 2 bars = 1 layer. A layer stops one shot, then recharges in 2.5 s **(now)**. |
| **Engines** | main | +5% evasion per bar **(now)**. The fold drive charges faster. |
| **Weapons** | main | Each weapon needs its own power to charge. |
| **Oxygen** | main | Refills the air in every room. At 0 the air drains. (Now: one air level for the whole ship. Later: each room on its own.) |
| **Medbay** | main | Heals crew standing in it; more bars heal faster. |
| **Drone control** | main | Powers drones; each drone needs its own power. |
| **Teleporter** | main | Sends up to 2 crew to board the enemy and brings them back. Recharges between uses. |
| **Cloak** | main | A few seconds where every shot at you misses. Your weapons pause while it lasts. |
| **Cockpit** | sub | Needs someone in it, or no evasion and no jump. +5% evasion when crewed **(now)**. |
| **Sensors** | sub | 1: see your own crew everywhere. 2: see inside the enemy. 3: see their weapons charging. |
| **Doors** | sub | Open and close doors from the screen (to vent fires, or let air out on boarders). More bars make doors tougher against boarders. |
| **Repair drone bay** | sub | The starter's drone works (when this bay is damaged, the drone works at half speed **(now)**). |
| **S.A.R.A. uplink** | special | No room. +1 shield layer while you're near the Landing (ring 1). Story fights use it **(now)**. |

#### Rooms and hazards (Claude)
- **Damage:** a hit on a room knocks bars off its system (shown red) until someone repairs it **(now)**.
- **Fire:**
  - spreads to neighbouring cells, burns oxygen, hurts crew and damages the system;
  - crew put it out;
  - opening an airlock door lets the air out, and the fire with it.
- **Breach:** a hole that lets the air out of the room until someone patches it.
- **Ion:** locks the room's system for a few seconds (blue).

### 6.3 Drones (Claude)
```
DRONE: <name>      Id: <id>      Power: <bars>      Price: <Scrip>
Kind: combat | defence | anti-boarder | repair | boarding
What it does: <one line>
```
Ideas:
- **combat drone:** a small laser that orbits the enemy;
- **defence drone:** shoots down missiles;
- **anti-boarder drone:** fights boarders inside your ship;
- **hull repair drone:** after a fight, patches a few hull points.

### 6.4 Augments: ship modifications (Claude)
```
AUGMENT: <name>    Id: <id>    Price: <Scrip>    Where: store | quest | special merchant
What it does: <one line>
```
Ideas with residents behind them:

| Augment | What it does | From |
|---|---|---|
| Bram's salvage arm | +15% Scrip from wrecks | Bram |
| Moogli price ledger | 10% off in stores | Moogli traders, Ooma |
| Tikka's coil tune | Weapons charge 10% faster | Tikka's quest |
| Zaa'sh prayer bell | Crew take 15% less damage | Tar'Besh |
| Precursor shard | Shields recharge 20% faster | the caverns |
| Freya's patch kit | Repairs 1 hull after every jump | Freya |
| Collective long-range scanner | See what's at the stops next to you before you jump | a convoy |

### 6.5 Crew

#### Species (Claude, for hired crew)
| Species | Strength | Weakness |
|---|---|---|
| Human | Learns skills twice as fast | none |
| Zaa'sh | +50% damage in fights | Repairs 25% slower |
| Arachnay | Four arms: repairs twice as fast | 20% less health |
| Moogli | +10% Scrip from fights and events | 20% weaker in fights |
| Ervani | Puts out fires twice as fast | none |
| Vuultam | Slowly heals others in the same room | Fights 25% weaker |
| Scyldar | Loses health far slower without air | Slower on foot |

#### Skills (Claude, after FTL)
- **The skills:** piloting, engines, shields, weapons, repair and combat. Each has three levels, and improves with use.
- **What a level gives:** a crew member at a station gives that system a bonus, larger as the skill rises. For example, a gunner at the weapons station makes weapons charge 10% faster, rising to 20%.

#### Health
- Crew have 100 health.
- At 0 they are **knocked out, not killed**. They wake in the Medbay at the station after the run, as decided for this cozy game.

#### Hiring
- At Tally's Post & Privateer Dispatch once he arrives, and sometimes in stores and events.
- Freya and Ana can join at 6 hearts, with an extra bonus at 8.

### 6.6 How a fight works: what the game will do (Claude)
**Enemy crew:**
- Start at their stations (cockpit, weapons, shields, engines) and stay there. A manned station gives its bonus.
- **Damage:** when a room is damaged, the nearest crew member who isn't at a vital station walks there and repairs it. If nobody is free, the shields operator goes, then the gunner.
- **Fire:** the nearest crew put it out. If there's no one free, they vent the room by opening an airlock.
- **Boarders:** crew in the room fight. If they're losing, others come to help. Badly hurt crew walk to the medbay if there is one.
- **Low hull:** each enemy has a behaviour from its design. It may charge its fold drive and flee, or offer to surrender (Scrip, fuel or parts to let it go). Capture contracts want it beaten another way: knock out the crew and keep the ship.

**Your crew:**
- Stay where you put them. They repair the room they're in, fight boarders in it, and put out fire in it.
- A **"Return to stations"** button sends everyone back to their saved stations.
- The repair drone is the first lesson in this.

**Enemy targeting:**
- Each design says what an enemy aims for first, such as your shields or weapons.
- Smarter enemies switch targets to finish off a damaged system.

**Boarding (later):**
- The teleporter sends crew to an enemy room. They fight the crew there, then damage the system.
- Knock out every enemy crew member and the ship is yours: a capture.
- Enemies with teleporters can board you the same way.

---

## 7. Making the space side more like FTL

Tick what you want. **Built** means it's in the game now; **Agreed** means you've asked for it and it's planned; **Suggested** is Claude's idea.

### Built
- [x] Real-time battle that pauses with Space; you give orders while paused
- [x] Reactor power moved between shields, engines, weapons and oxygen
- [x] Shield layers that recharge; evasion from engines and the cockpit
- [x] Aiming weapons at enemy rooms; hits damage the room's system
- [x] The repair drone as a crew member you send bay to bay
- [x] Fold drive charge and jump (not in story fights)
- [x] The jump map with five rings and four zones; the first flight's locked route
- [x] Losing wakes you in the Medbay; Freya repairs the ship
- [x] Ivan's and Ana's story fights; S.A.R.A.'s shield uplink near home

### Agreed (planned)
- [x] **Arriving at a stop:** the jump, the stop in a scope, then the **event window**, instead of dialogue boxes
- [x] **Store window** like FTL's: repairs, fuel, missiles, weapons, crew, drones and augments, to buy and sell
- [ ] Normal runs: random events and distress signals (you're writing them), stores, special sectors
- [ ] The Nest raid, then a smaller pirate stronghold each run; Ooma's ship as the special merchant
- [x] **Enemy crew at their stations**, walking off to repair (fires come later)
- [x] **The datapad look** for every ship screen, and the battle in two windows that fit each ship
- [ ] Bigger ships with crew decks; hired crew at Tally's; Freya and Ana as crew
- [ ] **Boarding** and teleporters; capture contracts
- [ ] Ship art from your redrawn ships and interiors, and more ships, weapons and systems from your designs

### Suggested (Claude)
1. **Ship screen with upgrades.** Spend Scrip on system bars and reactor power between fights. This is FTL's main way of getting stronger, and a good Scrip sink.
2. **Crew skills** that improve with use, and bonuses for manning stations.
3. **Fires, breaches and oxygen per room.** Venting rooms by opening doors and airlocks.
4. **Sensors and doors** subsystems.
5. **More kinds of weapon:** ion, missiles with ammo, beams, flak, bombs.
6. **Drones:** combat, defence (shoots missiles), anti-boarder.
7. **Augments:** small ship modifications with residents behind them (Bram's salvage arm, Tikka's coil tune...).
8. **Surrender offers.** A beaten enemy offers Scrip or fuel to be let go, as in FTL. Capture contracts give a reason to refuse.
9. **Enemies that flee** by charging their fold drive, so you have to finish them quickly.
10. **Hazards at stops,** tied to zones:
    - asteroid fields: random hull hits;
    - near a star: solar flares start fires;
    - nebulae: sensors go dark;
    - ion storms: half your reactor.
11. **Selling** weapons and parts back at stores for half price.
12. **Blue event choices** that only appear with the right crew, weapon or drone (the event template already allows this).
13. **FTL-style keys:**
    - 1–4 for weapons;
    - drone keys;
    - "Return to stations" and "Save stations";
    - Tab to cycle crew;
    - autofire.
14. **Quest markers.** An event can reveal a special sector on the map ("reveal:" in the event template).
15. **Unlockable ships with different layouts,** each with a quirk, like FTL's ship variants. Sources:
    - the Forgemaster's shipyard;
    - captures;
    - Freya's covered fighter.
16. **Combat music and sounds:** weapon fire, shield hits, alarms for fire and breaches, the jump.
17. **A difficulty setting** for ship runs (enemy hull and damage, prices).
