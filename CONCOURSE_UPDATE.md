# Lunar promenade — v11

See V11_UPDATE.md for the current floor, wall and footprint changes. Older entries below are change history.

Open `project.godot` in Godot 4.6. Import into a fresh folder; the archive contains the full project, with project.godot at its root. Existing areas, characters and quests are retained.

This pass replaces the main promenade. Interior rooms and the other districts retain their existing art; this is not a completed whole-game reskin.

## Layout

The central plaza and outer residential walkway are separated by a thick ring of shop rooms. Eight routes connect the rings. Community room (NW), mess hall (NE), manufacturing hub (SW), and medbay (SE) are inset into the outer perimeter. Homes extend into the outer wall, with entrances facing inward. South-side rooms show roofs and inward thresholds, not front-facing storefronts. The fountain stays at map center, with the request board and calendar attached to its south plinth.

## Controls

- Right-click a nearby door, or press E: check its lock, animate the leaves, then enter its separate interior.
- Right-click an elevator: open, board, close, short travel transition, arrive. Walking on a lift tile no longer transports the player automatically.
- Right-click a chair or bench: sit. Movement or E stands up at the original approach position.
- Right-click tables, plants, displays and terminals: inspect.
- Fountain board and calendar remain separate interactions on the same structure.
- F10 toggles a zoomed-out review view. Toggle it off for normal play.
- F11 in a debug/editor run cycles review locations: fountain, garden, games, observation bay, market, mess hall, medbay, manufacturing, upper lift, lower lift. This review shortcut sets 14:35 lighting and resident schedules and can bypass character creation; it is for inspecting the update, not normal progression. It does not reset the save.

## Art and scale

The promenade is built from tiled floor/roof/wall materials, independent portal components, transparent PNG furniture sprites, collision footprints and interaction markers. There is no large JPEG map or facade backdrop. It remains a 2D game with depth cues and sorted sprites, not a 3D engine scene.

Sprites use uniform half-scale, matching the doubled-detail character art. Chairs are about 12 world pixels wide, tables with two chairs 48 pixels wide, ordinary door openings 24 pixels wide, major doors and elevators 32 pixels wide. The existing player/NPC footprint is the scale anchor. Bigger facilities gain floor area rather than stretching their doors or furniture.

Door frames, moving leaves, vestibules, light strips and directional floor symbols are separate drawing components. Water, door status lights and terminal screens animate. Windows contain no baked-in people.

## Editing and access

`tools/concourse.py` defines geometry, entrances, props and interactions. Run `python3 tools/build.py .` from this project to rebuild map data. New art is under `art/lunar`. `scripts/lunar_ground.gd`, `lunar_portal.gd` and `lunar_terminal.gd` assemble the visuals at runtime.

Quest scripts can call `set_door_locked(area, Vector2i(x,y), true)` on the game world. Pass false to unlock. Overrides persist with the existing save mechanism. This update leaves entrances unlocked by default; it does not invent new story requirements. Player lock checks do not change residents' scripted access permissions.

## Validation

Final serialized-map reachability checks cover room entrances, return landings and resident schedule stops. Runtime tests cover 18 promenade portals, denied locked entry, both lift rides, 27 seats, seated directions and stand-up restoration. Manual Godot checks cover overview layout, furniture/character scale, mess hall right-click entry, a seated dining pose, and the upper lift ride.

## Gardens, games and stars

Fine floor grids now vary by area, with broad pedestrian paving and low trim. The upper-left flower pocket and lower-right games nook sit outside the eight through-routes. Bram has a recessed market with a canopy, provisions, seed display and cargo. The west residential loop connects to a projecting observation bay with a lunar viewing window, telescope and seating. Roof utilities use individual vent, pipe and duct sprites.

The fountain now consists of separate rear rim, front rim, column, notice panels and animated water, with a solid elliptical footprint and separate depth anchors. The board and calendar share the south face.

Player activities: water flowers once each day, inspect the telescope/window, read community books, sit, browse supplies, and play three-in-a-row at an unoccupied game table. The chess-themed table uses this small minigame too; full chess is not implemented. Repairs are inspectable scenery, not a new crafting system. Existing Bram quest/trade dialogue is retained.

Resident visits: Evarra gardens at 14:00 and Merrow at 15:30; Owen and Tar’Besh use the game table at 14:00; Kit and Pip use the hologame at 15:30; Zaas visits the telescope at 14:00; Quill reads at 15:30; Saffi browses at 13:00. Bram restocks during his existing work shift. Visiting-day rules still apply. Residents resume their old schedules afterward. Occupied seats and tables respond accordingly. Activity poses reuse each resident’s art with animated tool/hand overlays and seated legs.

Validation for v6 includes map reachability, all portals/lifts/seats, social schedules and pose restoration, fountain collision, the daily watering guard, and table-game win/block logic. Native Godot review covers the new social spaces, draw order and fountain assembly.

## v7 paving refinement

Six native pixel-paving palettes replace the uniform fine grid. Staggered joints, restrained per-paver tones, sparse sage insets, bevels and brass path studs add variation. Eight smooth diagonal/cardinal routes meet a round fountain plaza. Main forecourts and the garden/games pockets use rounded visual borders, with openings at paths. The residential ring uses a cooler sage surface.

This changes the floor rendering only. Walls retain the structural tile footprint; collisions, entrances, props and NPC routes are preserved. Floors are generated once and cached as a floor-only texture. They are not a flattened picture of the buildings or interactive objects.

Review exports are under `review/`: the native transparent floor map, six individual surface samples and labelled preview sheets. These are actual game surfaces, not concept mockups. Recreate them with `godot --headless --script res://tests/paving_test.gd`. The generator lives in `scripts/lunar_paving.gd`; the structural renderer remains in `lunar_ground.gd`.

Validation: floor export dimensions/transparency, serialized-map reachability (6,660 concourse tiles), and social interaction/fountain regression test passed. Floor rendering does not change seating, door or lift logic.

## v8 hexagonal plaza

The warm plaza stone is replaced by continuous hexagonal paving. Each hex receives a coordinate-seeded tone from six warm neutral / sage-grey shades, with occasional recessed service panels, restrained brass or teal inserts and offset scuff marks. The pattern runs across the map in world coordinates, so individual 16-pixel map cells do not restart or repeat a square texture stamp. Main paths and the round fountain apron keep their contrasting pale paving. Other surfaces retain their per-paver variations.

Updated actual floor-only map and six-surface preview are in `review/`. Godot's paving export passed; all five other material samples are byte-identical to v7. This art-only change does not alter collisions, routes, interactions or schedules.

## v9: three subvariants for every floor

Every one of the six floor families now has A (clean), B (recessed inset detail), and C (light wear). All 18 are visible separately in the comparison sheet and exported as individual PNG samples under `review/floor_N_subvariant_N.png`. The six `floor_variant_N.png` files show the mixed result.

Runtime assignment uses a stable coordinate seed per individual paver/hex. Tone variation is independent of subvariant selection. Adjacent tiles can differ without changing the base pattern or restarting a repeated square stamp. No frame-by-frame random changes occur. Paths, curbs, walls, collision and interaction locations remain as in v8.

Godot paving validation passed: all 18 subvariant samples are distinct, each mixed surface differs from its three uniform samples, and map dimensions/transparency remain correct.
