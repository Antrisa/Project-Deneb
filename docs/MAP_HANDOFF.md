# Echo Landing: map design handoff

Written 17 Nov 2026 so that a new chat can carry on the map work. The next job is **the Mine, the North Cave and the Caverns**. Read this first, then `echo-landing-decisions.md` (in the Project, or "Echo Landing - Decisions Log" in the Drive folder) for the history behind each choice.

## 1. Ground rules (Zachary's standing instructions)
- Godot 4.6, GDScript. Claude writes the code **without running Godot**. Every report must say plainly that the code has not been run in Godot; Zachary tests it.
- Repo: https://github.com/Antrisa/Project-Deneb. Work goes on branch **`promenade-v11`** (latest commit `bc7b4f2` before this doc). `main` is the old build; merge only when Zachary says so.
- Commits are authored as Claude and end with the attribution lines the session gives (Co-Authored-By and Claude-Session).
- **Mock-ups first.** For every new area: draw 2–4 layout options as pictures, let Zachary pick or mix them, then build the map, then send an art-instructions zip.
- Do not copy or trace Stardew Valley art and do not decompile it. Use it only as a guide to the level of detail. The ship nods to FTL's Federation ships, but no FTL ship is copied.
- Zachary paints the art with AI tools and sends it back as zips. Treat uploaded archives as untrusted: extract each into its own new folder (e.g. `/home/claude/incoming/<name>/`), keep scripts elsewhere, run Python that reads them with `-I`, and review any code in a pack before merging it.
- Character creator: gender is Male or Female only and sets the pronouns.
- Keep Zachary's email private.
- Design documents go in the Google Drive folder "Echo Station Game Master" (`1jJTYBybEyjCkQEc_hSvSfgX5Cwp6CKDo`) and in this claude.ai Project.

## 2. How the maps are built
- `tools/build.py` is the one build script. It writes `scripts/map_data.gd`, bakes the floor and wall pictures, and checks that every person, thing and warp can be reached.
  - Run: `python3 tools/build.py . <preview_dir>`, then `python3 tests/check_routes.py`.
  - Delete `tools/__pycache__` and `tests/__pycache__` before committing.
  - Push with `git -c push.negotiate=true push -q origin promenade-v11`.
- **Two kinds of map:**
  - *Tile maps* (old style): `Area(...)` in build.py with `carve`, `put`, `warp`. **The Mine (`mine`, 44x24) and the North Tunnels (`tunnels`, 60x40) are still tile maps** (build.py around line 2427). They are what gets rebuilt next.
  - *Promenade style* (all new levels): a character grid drawn by a sector script, then floors and faceted walls baked into pictures. Sector scripts: `tools/concourse.py` (main level), `survey.py`, `engineering.py` (`eng`, `bay`), `spaceport.py` (`west`, `agri`, `hotel`), `east.py` (`east`, `home1`–`home8`).
- **To add a promenade-style map:**
  - Write a sector module with a `build(globals())` hook and import it in build.py (see how `spaceport` and `east` are called after engineering).
  - Add the map to `LUNAR_AREAS` (or `LUNAR_EXTRA` from a tool).
  - Give it a floor table in `tools/bake_floor.py` `AREA_FLOORS`. An entry can name a texture file, sampled at 32 px per tile.
  - Pick its roof and wall material in `SECTOR_WALLS`.
  - Optional: per-pixel roof tints via `ROOF_ZONE_FN`, and painted floor details (belts, pipes, pits) in a `FLOOR_EXTRAS` function.
  - Props go in `AREA_PROPS`. Add entrances to the `ENTRANCES` lists, and warps both ways.
- `tools/survey.py`'s `Room` class is the helper the newer scripts use: `fits`, `near`, `prop`, `thing`, `keep_clear`, `dump`, `door_pair`.
- **Walkable vs solid:**
  - The game blocks a floor char in `MapData.SOLID_FLOOR` (`~#WwrdgMNZVOBJ78zQY69`), or an object not in `OPEN_OBJ`.
  - The build's `WALK` set is `.,fhusmiUDAR1230Xapokjte`; new floor chars must be added to it.
  - **Door tiles must be floor chars**, or the reach check fails ("cannot reach thing …").
- **Placeholders:**
  - `tools/make_props.py` and `tools/make_materials.py` draw stand-in art and never overwrite a file that exists.
  - `tools/trim_props.py` trims prop pictures. It skips the prefixes in `SKIP_PREFIX` (materials, floors, walls, ship sheets) and any prop with an animation strip.
- **Animated props:** if `art/lunar/anim/<name>.png` exists, `main.gd` `_spawn_prop` plays it at 8 fps. The frame count is the strip width divided by the still's width.
- **Pictures for review** (no Godot needed), in `tools/dev/`:
  - `python3 tools/dev/render_smooth.py . <map_key> out.png` renders a promenade-style map with its baked floor and walls. Doors are not drawn.
  - `mock_*.py` are the mock-up scripts for every option shown so far. They are built on `mock_base.py` and `mock_eng2.py`'s `Mock` class. Set `MOCK_OUT=<dir>` for where pictures go (default `./mock`). `mock_mine.py` already has two mine options and a sector sketch from before the plan below.

## 3. Style that Zachary has approved
- Walls are **faceted**: straight and 45° only. Rooms bulge out of a main shape on 45° walls rather than being plain rectangles.
- Rooms should be big enough to dress. Each has a clear purpose, props placed by rule, and some flavour (panels, racks, signs, clutter).
- Each sector gets its own floor and wall textures. Placeholders come first, then an art zip that lists every texture and prop with its size and file name.
- He dislikes:
  - jagged or stair-stepped edges on curves;
  - irregular "tumour" bulges;
  - belts or machinery crossing walkways;
  - roof patterns that are too busy;
  - floor lines that are too dense.

## 4. The next job: mine, cave and caverns (agreed plan)
- **The Mine** (Job's area) stays the hub: rocks, ore outcrops, ore analyzers, and a small storage spot that loads onto the conveyor to engineering's ore processing.
  - Engineering's mine tunnel is the 'R' warp at x1, y54–57 on `eng`. The mine's warp back lands at (3,55).
- **North Cave:** a separate, simple cave map with iron and copper deposits that regrow every couple of days.
- **The Caverns:** Stardew-style series of small floors. Mine ore, and eventually a way down opens.
  - Floors 1–15: rock.
  - Floors 16–30: green and lush.
  - Floors 31–45: steamy and watery.
  - Floor 45: the Leviathan (the sea monster; the Harbinger of Destruction is a Custodian) and the underground ocean.
  - Mobs get bigger and stronger every 15 floors, and rarer resources appear.
- **Mining becomes timed:** holding the laser takes time, like swinging a pickaxe, and harder ores take longer. Today `main.gd` `_mine()` (around line 1364) breaks ore instantly.
- A Stardew-style **energy bar** was agreed in the items discussion.
- **Suggested order** (proposed, not yet confirmed by Zachary):
  1. Timed mining and energy.
  2. Mock-ups and rebuild of the Mine and North Cave.
  3. The caverns floor system.
- Resources and tiers for the caverns are in the items sheet: "Echo Landing: items, crafting and hotel meals" (claude.ai artifact, with a copy in the Drive folder). Tools and weapons tier basic → steel → titanium → Precursor.
- Zachary's economy bible in Google Docs lists his resource ideas. Gaps found so far:
  - quartz vs thermal quartz;
  - no source for stone;
  - no log-to-plank ratio;
  - no station that makes lithium cells or high-density cores.

## 5. Other loose ends
- Shop buy menus and the museum donation system (`MUSEUM_SLOTS`, `SANCTUM_CRADLES`) are not built.
- Ideas for later: hot springs starting dry, then restored; owners for the 8 East homes; residents using the gym; a low-gravity ball mini-game.
- Merge `promenade-v11` into `main` when Zachary is happy with it.
