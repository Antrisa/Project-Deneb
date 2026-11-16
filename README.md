# Echo Landing (Project Deneb)

A cozy space-town sim: run a settlement built in an abandoned Terran listening post, get to know its residents, mine, craft, and fight off what comes up from the caves. Built in Godot 4 with GDScript.

## Running it

1. Install Godot 4.6 (standard version, not .NET).
2. In Godot choose **Import**, pick `project.godot` in this folder, and press **F5**.

The first time you open it, Godot imports the art and sounds. That takes a few seconds.

Testing this build? See `TESTING.md` for what to look at and how to report problems.

## Controls

| Action | Keyboard | Mouse |
|---|---|---|
| Move | WASD or arrows | |
| Talk, read, interact | E or Enter | Right click (or left click with nothing usable selected) |
| Use the selected hotbar item | Space or F | Left click |
| Pick a hotbar slot | 1 to 8 | Wheel, or click the slot |
| Menu (pack, crafting, map, friends, journal) | Tab or I | The "Menu" button |
| Journal (your quests) | J | |
| Decline / close | Q or Esc | Right click in conversations; click outside the menu |
| Music on or off | M | |
| Wipe the save and start again | F9 | |
| Character screen (new game, or the locker in your quarters) | Up/Down choose a line, Left/Right change it, R shuffle, Enter start | Click the left or right half of a value; on a colour line, drag the hue, saturation and brightness bars |

The game saves each morning. Sleep in your bunk to end the day; if you are still up at 1:00 am you pass out, lose a few credits and start the next day on half your hearts.

## What is where

| Path | What it is |
|---|---|
| `project.godot`, `main.tscn` | The Godot project and its single scene |
| `scripts/main.gd` | The game: areas, clock, quests, items, combat, saving |
| `scripts/player.gd` | The player: movement, tools, weapons |
| `scripts/resident.gd` | Residents who walk a daily schedule |
| `scripts/enemy.gd` | Cave creatures |
| `scripts/dialogue_box.gd` | Conversations and portraits |
| `scripts/ui.gd` | Hotbar and menu |
| `scripts/nine_frame.gd` | Draws stretchy frames (dialogue box, portrait border) from a 3x3 picture |
| `scripts/area.gd` | Draws a map |
| `scripts/npc_data.gd` | Who the residents are and what they say. **Edit dialogue here.** |
| `scripts/item_data.gd` | Items and crafting recipes |
| `scripts/map_data.gd` | Maps, positions, schedules. **Generated: do not edit by hand.** |
| `tools/build.py` | Generates `map_data.gd`, the placeholder art and the sounds |
| `art/` | All pictures |
| `audio/` | Sound effects and music loops (generated placeholders). `music_<name>.ogg` is used in preference to `.wav`. |

## Changing maps, schedules or generated art

Maps, where things are, resident schedules, ore veins and creatures are all defined in `tools/build.py`. After editing it, run from this folder:

```
python3 tools/build.py .
```

It checks that every room, resident spot and exit can be reached, then rewrites `scripts/map_data.gd`, the generated art and the sounds.

## Art

**Files listed in `art/hand_edited.txt` are never overwritten by the generator.** When you paint over a generated file, add its name to that list.

One exception, for `tiles.png` only: when the game gains a new tile, the generator fills that empty slot with placeholder art, and it keeps its own couch and shop counter (see `KEEP_GENERATED` in `tools/build.py`). It also puts a floor under any floor tile with see-through pixels. This needs Pillow (`pip install pillow`).

| Files | Layout |
|---|---|
| `npc_*.png`, `player.png` | Walk sheet: 4 columns (down, up, left, right) by 3 rows (standing, step A, step B). Any frame size with a 1:2 shape works; the game scales a frame to 16 wide. The NPC sheets are 32x64 per frame. `player.png` is only used if the layered player art below is missing. |
| `player/tops.png`, `bottoms.png`, `faces.png`, `hair.png` and their `_mask.png` | The layered player for the character screen: 4 directions across (down, up, left, right), 10 choices with 3 pose rows each (standing, step A, step B), 32x64 cells; each file is 128x1920. In the mask, red = takes the layer's main colour, green = skin, blue = eyes. `scripts/player_maker.gd` builds the walk sheet from these; the names and colour lists are at the top of that file. Replace the eight files and `player_maker.gd` together. `tools/fix_player_masks.py` can clean masks where grey details were marked as skin; the current art does not need it. |
| `portrait_*.png` | 6 square pictures in a row: neutral, happy, sad, surprised, love, angry. Any size; shown in a 64x64 box. Currently 128x128 each. |
| `tiles.png` | 110 columns, each one cell wide and two cells tall (currently 32x64). The lower half is the tile; the upper half is the top of tall objects. A tile is always drawn 16x16 in the world. Slot names are in `tools/build.py`. |
| `items.png` | 16x16 icons in a row; the order must match `icon` in `scripts/item_data.gd`. |
| `weapon_*.png` | Pointing right, grip at the left end. |
| `enemy_*.png`, `*_ore.png` | Two square frames (creatures 16x16, facing left; ore 32x32). |
| `fx_*.png` | Four square animation frames (currently 32x32), laid over the still tile. |
| `player/body2/` | The second body type (Female; `player/` is Male): the same eight layer files, same layout. The names are in `OPTIONS` in `scripts/player_maker.gd`. |
| `npc_<name>_act.png` | Optional action sheet: what a resident does at each stop of their day. 4 frames across (a loop), 48x64 each, one row per action. The rows for each resident are listed in `ACTION_ROWS` in `scripts/map_data.gd` (set by `ACTIONS` in `tools/build.py`). Without a sheet the game fakes it. |
| `ui_panel.png`, `ui_dialogue.png`, `ui_portrait_frame.png` | 3x3 grids: corners stay sharp, edges and middle stretch. |
| `ui_slot.png` | Three slots side by side: empty, selected, being moved. |
| `ui_tab.png` | Two tabs side by side: not chosen, chosen. |
| `hearts.png` | Two hearts side by side: full, empty. |
| `wreck.png` | Four frames twice as wide as tall (currently 128x64), wrecked to repaired. |

Keep feet at the bottom centre of each walking frame, and keep backgrounds transparent.

To give a line of dialogue an expression, start it with `[happy]`, `[sad]`, `[surprised]`, `[love]` or `[angry]`.

## Credits

- Game code, maps, sounds and placeholder art: generated with Claude.
- NPC walk sheets and portraits: Character Pack v1, supplied by Zachary.
- Tiles, furniture, animated effects, ore and the ship: Environment Pack v1, supplied by Zachary.
- Design, lore and direction: Zachary.

Design notes, decisions and the roadmap live in the "Project Deneb" project on claude.ai.

## How the main level is built

The main level is one circle: the town square is the inner circle, a ring walkway runs round the outside, and six passages join them (`PASSAGES` in `tools/build.py`). The wedges between the passages are the shop buildings, listed in `SHOPS`; each door is where its building meets the square, with its own sign board beside it. Apartments are blocks outside the ring (`building(...)`). The inside of every shop and apartment is its own small map (`interior(...)`).

New tiles are always added at the end of the tile list in `tools/build.py`, so slot numbers in `tiles.png` never change. The sheet is 140 slots wide (4480x64).

## Checking the player art

    godot --headless --path . --script res://tests/player_art_test.gd

Checks every top/bottom and face/top pairing for gaps at the waist and neck, that arms and legs move between steps, and the colour controls.

## He and she in dialogue

The Gender line on the character screen (Male or Female) picks the body and how residents refer to the player. In any resident's line in `scripts/npc_data.gd`, write the "they" form in curly brackets and the game swaps in he or she: `{they} {them} {their} {theirs} {they're} {they've} {are} {were} {have}`, and `{s}` for a verb ending, as in `{they} look{s} tired`. A capital is kept: `{They}`.
