# Echo Landing: art handoff 2 — items, environment and other details

This is for making pixel art with ChatGPT, or any image tool, for Echo Landing. It is a 2D, top-down 3/4-view station sim in the style of Stardew Valley, made in Godot. Give this whole document to ChatGPT with a few existing pictures from the game as style references. Characters, portraits and animations are in **art handoff 1**. The full item list with recipes is in the sheet "Echo Landing: items, crafting and hotel meals".

Written 18 Nov 2026; **updated the same day for the 24-pixel grid** (branch `art24`). For redrawing the existing environment, use the pack **Echo_Landing_Environment_Art_24px.zip**: it lists all 300 pictures with their new sizes.

---

## 1. Style rules (every picture)

- **Pixel art only.** Hard pixel edges, no anti-aliasing, no blur, no soft shadows.
- **Detail level:** about 1.5× Stardew Valley's: 24 art pixels a tile (Stardew uses 16). **Never copy or trace Stardew Valley art.** Every design is original.
- **Look:**
  - a 1-pixel dark outline, coloured (deep blue-grey), never pure black;
  - light from the top left;
  - 3 to 5 shades per colour;
  - a cosy sci-fi lunar station.
  - **Materials:** white and cream station panels, navy trim, warm wood and brass in homes and the hotel, copper and orange in engineering.
- **View:** top-down 3/4. Furniture and machines are drawn **from the front**, with the top surface visible.
- **Background: transparent PNG.** If the tool can't do transparency, use flat magenta (#FF00FF).
- **Scale:** **24 art pixels = 1 floor tile.** Characters are 24×48. One art pixel is exactly 3 screen pixels at 1080p and 4 at 1440p. Sizes must be exact, as given below.

### Getting exact pixel art out of ChatGPT
1. **Ask for a large picture.** Have it drawn on a flat background at a whole multiple of the target size, with the pixel grid visible, e.g. "each art pixel is an 8×8 block".
2. **Shrink it to the exact size** with nearest-neighbour resampling. ChatGPT can do it with Python: "downscale to exactly 72×48 with nearest-neighbour and remove the magenta background".
3. **Check and fix it** in a pixel editor (Aseprite, Pixelorama or LibreSprite): stray pixels, soft edges, a complete outline.
4. **For sets** (all hotel beds, all ores), make them in one chat, so the palette and outline stay the same.

Prompt template:
> Pixel art game asset for a cozy sci-fi lunar station life sim (about 1.5× Stardew Valley's level of detail, original design). Top-down 3/4 view, seen from the front with the top visible, 1-px dark blue-grey outline, light from top-left, hard pixels, no anti-aliasing, flat #FF00FF background. Exact size: [W×H] art pixels ([w×h] floor tiles at 24 px per tile). Object: [description]. Match the attached reference assets.

---

## 2. Formats (what the game expects)

| Kind | File | Size | Notes |
|---|---|---|---|
| Item icon | `art/items/<item_id>.png` | **24 × 24** | One per item, centred, with a little margin. Claude packs them into the game's icon strip. |
| Ore or rock node in the world | `art/<item_id>.png` | **48 × 24** | 2 frames of 24 × 24: **whole**, then **cracked** (half mined). The base sits at the bottom of the frame. |
| Furniture, machine, prop | `art/lunar/<name>.png` | width = **tiles wide × 24**; height = whatever it needs | Bottom edge = where it stands. Tall pieces (wardrobes, lamps) can be 2–3 tiles tall. A piece seen from behind (facing up) is `<name>_n.png`. |
| Animated prop | `art/lunar/anim/<name>.png` | **(still width × frames) × still height** | A horizontal strip of frames, each exactly the size of the still. It loops at 8 frames a second. Also deliver the still. |
| Floor texture | `art/lunar/<name>.png` | **48 × 48** | Covers 2 × 2 tiles and must **tile seamlessly**. Keep it low contrast so props stand out. |
| Wall roof / wall face | `art/lunar/<sector>_roof.png`, `<sector>_wall.png` | **48 × 48** each, seamless | The roof is the top surface of walls, seen from above. The wall is the front face, shown 2 tiles tall below each roof edge. |
| Window strip | `art/lunar/window_<name>.png` | **width × 48** | For long windows in walls (like the Shuttle Bay's crater view). |

---

## 3. Item icons needed (24 × 24 each)

Today the game has 23 icons, made by the game's generator rather than painted. The new crafting list needs these. Ids are the names in lower case with underscores, e.g. `steel_bar`, `moon_opal`.

**Resources (36):**
- Stone, copper ore, iron ore, carbon (graphite), silica sand, quartz
- Aluminium ore (anorthite), titanium ore, gold ore, rare earths, lithium salts, thermal quartz
- Sulphur, basalt core, cobalt-60, ice, helium-3, geode
- Moon opal, crater garnet, void sapphire, fossil / relic, Precursor crystal shard, bioluminescent spores
- Glow-moss, cave mushroom, cavern silk, chitin plate, lizard hide, scrap
- Logs, resin, lunar cotton, bio-plankton, honey, milk powder

**Components (25):**
- Copper bar, iron bar, steel bar, aluminium bar, titanium bar, gold bar
- Glass pane, refined silicon, brick, wood plank, flour
- Copper wire, magnet, motor, circuit board, hull plate, precision lens, lithium cell, high-density core, seal kit
- Cotton cloth, reinforced silk, dyed cloth, leather, Precursor alloy

**Tools and gear, four tiers each:**
- Mining laser, hoe, watering can, cutter, fishing rod
- Sword, spear, blaster pistol
- Body armour, helmet, boots
- Chest, sprinkler

The same shape at each tier, with a different material, so the tier reads at a glance:

| Tier | Material and colours |
|---|---|
| **basic** | worn grey metal with orange tape |
| **steel** | blue-grey steel with rivets |
| **titanium** | bright silver-white with teal light strips |
| **Precursor** | dark crystal-violet with a soft inner glow |

Ids: `<tool>_basic`, `<tool>_steel`, `<tool>_titanium`, `<tool>_precursor`.

**Consumables (12):**
- Glow-flare, small charge, cluster charge, demolition charge
- Rope ladder, return beacon, ore scanner, ammo cell
- Field rations, stamina tonic, healing tonic, fertiliser

**Food (19):**
- **Ice creams:** vanilla, star-apple, honey frost, frost-berry sorbet. Make these special: a cone or cup, frosty, "very important".
- Moon-wheat bread, crater-potato mash, star-tomato soup, synth-steak and mash, plankton noodles
- Cave mushroom risotto, glow-moss salad, moon-peach tart, sun-fig preserves on toast
- Grilled cave-trout, crayfish boil, lantern-eel sushi, king crab feast
- Mess hall stew, station breakfast

Also an icon for every furniture piece and machine below, so they can sit in the inventory: a small 24 × 24 version.

---

## 4. In-world objects needed

### 4a. Mine and caverns: ore and rock nodes (48 × 24, whole + cracked)
- **One node per mineable resource:** stone, copper, iron, carbon, silica, quartz, aluminium, titanium, gold, rare earths, lithium, thermal quartz, sulphur, basalt core, cobalt-60, ice, geode, gem node (opal, garnet, sapphire), Precursor crystal.
- **Plain rock in three looks, one per cavern band:**
  - floors 1–15: grey moon rock;
  - floors 16–30: mossy green, with glow-moss;
  - floors 31–45: wet blue-black, steaming.
- **Cavern floors** (48 × 48 seamless, one per band) and **cavern walls** (roof + wall, per band).
- **Cavern details:**
  - the ladder or hole down to the next floor (24 × 24);
  - glowing fungus clusters and crystal clusters;
  - steam vents (animated);
  - shallow water edges (floors 31–45);
  - the underground ocean shore (floor 45).

Check with the mine chat for anything already done.

### 4b. Crafting machines (front view)
Suggested footprints, in tiles wide × deep:

| Machine | Size |
|---|---|
| Workbench | 2 × 1 |
| Arc Smelter | 2 × 2, animated: glow |
| Manufacturing Hub | 3 × 2 |
| Loom | 2 × 1 |
| Hotel carpentry bench | 3 × 1 |
| Kitchen stove | 2 × 1 |
| Kitchen bot | 1 × 1, animated |
| Fermenter | 1 × 1 |
| Preserver | 1 × 1 |
| **Ice cream maker** | 1 × 1, animated: churning |
| Dehydrator | 1 × 1 |
| Recycler | 2 × 1 |
| Bee hive | 1 × 1 |
| Mushroom log | 2 × 1 |
| Plankton vat | 1 × 1, animated |
| Seed maker | 1 × 1 |
| Geode cracker | 1 × 1 |
| Protein synthesizer | 1 × 1 |
| Fish hatchery | 2 × 1 |
| Abyssal trap pot | 1 × 1 |

### 4c. Hotel furniture (the hotel-decorating game; front view, plus `_n` back views for seats)
Suggested footprints, in tiles wide × deep:

| Furniture | Size |
|---|---|
| Single bed | 1 × 2 |
| Double bed, luxury double bed | 2 × 2 |
| Bunk bed | 1 × 2 |
| Wardrobe, mirrored wardrobe | 2 × 1, tall |
| Bedside table, bedside lamp | 1 × 1 |
| Writing desk | 2 × 1 |
| Desk chair | 1 × 1 |
| Armchair, velvet armchair | 1 × 1 |
| Rugs (plain, patterned, moon-opal) | 3 × 2, flat |
| Curtains, velvet curtains | 2 wide, wall-mounted |
| Viewport window frame | 2 wide, wall-mounted |
| Wall painting (crater), holo-art frame | 1 wide, wall-mounted |
| Potted fern | 1 × 1 |
| Glow-moss terrarium | 1 × 1 |
| Bookshelf | 2 × 1, tall |
| Minibar | 1 × 1 |
| Toilet, washbasin | 1 × 1 |
| Shower | 1 × 1, tall |
| Bathtub | 2 × 1 |
| Hot-spring tub | 2 × 2 |
| Towel rail | 1 × 1 |
| Front desk bell | small, sits on a counter |
| Lobby sofa | 3 × 1 |
| Fountain kit | 2 × 2, animated |
| Dining table (4) | 2 × 2 |
| Dining chair | 1 × 1, all 4 facings |
| Banquet table (8) | 4 × 2 |
| Buffet counter | 3 × 1 |
| Chandelier | 2 × 2, ceiling, drawn high |
| Bar counter | 3 × 1 |
| Bar stool | 1 × 1 |
| Fireplace | 2 × 1, animated |
| Piano | 2 × 1 |
| Games table | 2 × 2 |
| Aquarium (wall) | 2 wide, animated |
| Telescope | 1 × 1 |
| Ice cream counter | 2 × 1 |
| Planter box | 2 × 1 |
| Wall lamp | wall-mounted |
| Room sign / number plate | wall-mounted |
| Vending machine | 1 × 1, tall |

- **Floors you can build** (48 × 48 seamless): brick path, parquet, marble.
- **Wallpaper:** 48 × 48 seamless wall face, 3 or 4 styles.

### 4d. Farming, fishing, hot springs (not designed yet: art can wait)
- Crops: 4–5 growth stages each, 24 × 48 per stage, as a strip.
- Fishing: bobber, splash and fish icons.
- Hot springs: a dry state and a filled state.
- Beehive honey states.

The farming design comes first. Ask the economy chat for the crop list.

---

## 5. Other details

- **Effects** (strips, 8 fps):
  - mining sparks and dust, 4 frames, 24 × 24;
  - rock breaking apart, 6 frames;
  - ore pickup sparkle;
  - water splash;
  - heal sparkle;
  - level-up / "new recipe" burst.
- **Emote bubbles over heads** (24 × 24): heart, music note, "!", "?", sweat drop, anger mark, zZz, lightbulb.
- **UI:**
  - **Energy bar frame:** vertical, about 24 × 96, with a separate fill strip.
  - **Hearts for the friendship page:** full, half and empty heart, 14 × 12 each, with a locked-bedroom padlock icon.
  - Star-rating stars for the hotel: full and empty.
  - The scrip currency coin icon.
  - Clock and calendar frames.
- **Door art:** the new doors between rooms (scripts/inner_door.gd) are drawn by code for now.
  - A front-view sliding door: frame 24 wide × 36 tall, plus a leaf.
  - A side-view door for walls running north–south: 12 × 36.
  - A locked light (red) and an unlocked light (green).
- **North-facing doors:** a doorway with a canopy seen from above, for buildings you enter from their north side (medbay, fab). 36 × 36.

---

## 6. Delivering the art
- Zip the files with the exact folder and file names above. Include a `README.txt` listing what's new.
- Claude reviews the zip, wires it in, and adds each file to `art/hand_edited.txt`, so placeholders never overwrite it.
- Before zipping, check each one:
  - exact size;
  - transparent background;
  - no soft edges;
  - floors and walls tile seamlessly;
  - animation frames line up.
