# Echo Landing v11 — smaller paving and curved structural footprints

Import project.godot from the extracted full project in Godot 4.6.

## Changes
- Promenade floor patterns are approximately one-third of v10's linear size. Floors now bake at one world pixel per image pixel to preserve small seams rather than skipping them during downsampling.
- Garden green panels replaced with generated warm-grey natural limestone paving, with stone variation and three subtle tone variants. Other floor families retain three subvariants.
- Removed rectangular building collision stamps from the circular structural bands. The four major corner facilities, shops and homes now use the existing annular wall footprint, with recessed door links.
- South-facing facade modules follow actual wall boundary cells instead of bridging public floor with a flat rectangular facade. North-facing doors keep their inward thresholds.
- Convex roof tile corners are rounded inward, without adding visual material to the walkway. Navigation still uses the game's tile grid; this is not continuous curved collision geometry.
- Wall variations: pale warm/cool panel tones, vents, access panels and restrained service lights.
- Ceiling/roof variations: three blue-grey tones, ventilation grilles, access hatches and seam details. Existing larger roof machinery remains independent sprites and is placed only on solid cells.

## Checks
- Generator and serialized-map reachability passed for doorways, return landings and resident stops.
- New regression checks verify the entire residential ring between radii 40 and 49 is free of solid floor stamps, plus all eight radial connectors.
- Door/lift/25-seat and social interaction regression checks passed after footprint changes.
- Native paving export passed: six families, 18 distinct subvariants, 3696 x 3056 floor image, transparent structural regions.
- In-game review covered garden stone/paving scale, the manufacturing corner, the zoomed-out ring layout and the curved mess-hall frontage.

The higher-resolution paving is baked once and cached in memory; first loading may take longer. Walls retain grid-based structure with rounded visual corners. Interior maps outside the promenade retain their previous materials.

## New art
Asset: art/lunar/garden_stone.png (96 x 96, nearest-neighbor downsample for game use).
Generated with the built-in image tool; source preserved in the conversation. Prompt:
"Use case: stylized-concept. Asset type: tileable game floor texture for Echo Landing, a cozy lunar base pixel RPG with Stardew-like readability. Create a square, perfectly overhead flat texture of small warm-grey natural limestone paving stones, irregular rounded rectangles in a close staggered bond. Subtle taupe and cool grey variations, fine darker recessed grout, modest upper-left pixel bevel highlights and lower-right contact shading. Hand-painted pixel art with restrained detail and clean clusters, no photorealism. The entire canvas is filled with pavement; no border, no labels, no scenery, no plants, no furniture, no perspective, no green panels. About eight stones across, each small, organically uneven edges, three quiet variations: clean, gently chipped, faint mineral flecks. All edges suitable for repeating as a ground material. Keep contrast quiet beneath characters."

Wall/roof variations are implemented in scripts/lunar_ground.gd using the existing metal material art, independently drawn details and stable coordinate seeds. They do not need a new flattened scenery image.
