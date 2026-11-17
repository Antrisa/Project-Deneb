# Echo Landing v10 — paving depth and social courts

Full project for Godot 4.6. Import project.godot from an extracted folder.

- Steel-blue hex plaza with painted surface texture, recessed joints and bevel shading.
- Six floor families retain three deterministic subvariations each; patterns stay aligned across tiles.
- Raised-looking curb runs use cap highlights, shaded sides, joints and contact shadows. They are low, walkable trim, with open approaches.
- Library reading/flower terrace and south-east games court replace oval floor patches. Diagonal and cardinal circulation routes remain open.
- Directional benches and chairs face their activity. Chess seats face one another; the observation bench faces the window. Removed four scattered seating clusters.
- NPC social destinations follow the revised garden and game-table positions. North/south seated NPC overlays use two bent legs.

The scenery remains layered 2D art with depth cues; this is not a conversion to a 3D engine. Doors, lifts, seating and fountain collision retain their existing independent behavior.

Validation: generator reachability check; native paving export and 18 distinct sample assertions; 18 animated portals, locks, two lifts and 25 seats; fountain collision, social schedules, watering and table-game behavior. In-game visual inspection covered the garden curb and occupied chess court. The spectator bench was subsequently moved clear of the curb.

New art: paving_painted.png is derived from a generated six-material atlas (steel-blue beveled hex, ivory ceramic, sage composite, copper-taupe decking, olive garden ceramic, blue-grey recreation slabs). Directional bench/chair sprites are derived from a generated transparent four-direction sheet: amber cushions, blue-grey metal frames, small warm lights, matching cozy lunar pixel-RPG furniture. Runtime materials sample the atlas and apply native pattern boundaries so joints remain continuous. New assets are protected in art/hand_edited.txt.

F11 in a debug build cycles review landmarks. These previews are for reviewing the updated project; test with a copy of your save.
