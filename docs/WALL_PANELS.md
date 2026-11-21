# Echo Landing: one-tile wall panels (21 Nov 2026)

## What's wrong
The map is already built on single tiles (24 × 24 art pixels, one character wide), and nearly every floor already has one square per tile. See `reference/floor_grid_check.png` and `reference/floor_grid_check2.png`, where the white grid is one tile.

What still reads as "2 × 2" is the **walls**. Each wall panel and roof plate is 48 pixels (two tiles) wide, so next to single-tile floors the walls look twice the scale of everything else. The red lines in `guides/` show the tile size over the current art: today, one panel spans two tiles.

## What to do
Repaint the files below so **each panel or plate is one tile (24 pixels) wide**.

- **Keep every file the same size as now.** The game stretches each wall picture over a fixed two-tile width, so a smaller file would come out stretched. Instead, paint two panels side by side where there is one today.
- **Start from the files in `templates/art/lunar/`.** They are the current art. Keep the colours, the top lip, the dark foot line and the overall style. Only the panel spacing changes.
- **Crisp pixel art:** every pixel fully solid. These files have no transparency.
- **Seamless left to right:** every file repeats along a wall, so its right edge must join its own left edge. The roof files also repeat top to bottom.
- **No map changes are needed.** When the files are in, Claude rebuilds and every map picks them up.

## The files

### Station walls (most of the game)
| File | Size | What it is | Change |
|---|---|---|---|
| `art/lunar/material_2.png` | 48 × 48 | The wall face. It is 2 tiles tall in the game and runs the full height of the file. | Two panels, each 24 wide × 48 tall, side by side. Keep the top cap strip and the dark skirting at the bottom running straight across both. |
| `art/lunar/material_2_a.png` | 48 × 48 | Wall face with a hatch, used now and then for variety | The hatch fits in **one** panel. The other panel is plain, matching `material_2.png`. |
| `art/lunar/material_2_b.png` | 48 × 48 | Wall face with a vent grille | The vent fits in **one** panel; the other panel is plain. |
| `art/lunar/material_1.png` | 48 × 48 | The wall's roof, seen from above: 2 × 2 tiles | Four plates, 24 × 24 each, in a 2 × 2 grid. |
| `art/lunar/material_1_a.png`, `material_1_b.png` | 48 × 48 | Roof variants | Four plates each, with the detail on **one** plate. |

### Engineering and the shuttle bay
| File | Size | Change |
|---|---|---|
| `art/lunar/eng_roof.png`, `eng_roof_a.png`, `eng_roof_b.png` | 48 × 48 each | Four 24 × 24 plates, as for `material_1`. |

`eng_wall.png` is fine as it is: its stripes have no vertical seams.

### The hotel
| File | Size | What it is | Change |
|---|---|---|---|
| `art/lunar/hotel/hotel_enamel_mix.png` | 192 × 48 | The hotel's corridor wall face | Eight panels, 24 wide each (four today). Keep the teal skirting band along the bottom. |
| `art/lunar/hotel/cap_mix.png` | 192 × 48 | The hotel's wall roofs, seen from above | Plates 24 wide (eight across, two rows). |
| `art/lunar/hotel/exposed_steel_mix.png` | 192 × 48 | Bare ribs in the unfinished hotel wings | One rib every 24 pixels. |

### Not needed
- **The cavern walls** (`lush/wall`, `steam/wall` and the roofs) are rough rock with no panel seams, so they're fine.
- **The Agri dome's herb patches** now use your new farm dirt and grass border, so they're done.
- **The Agri pond water** is a seamless animated surface with no seams, so it's fine.

## Sending it
Zip the repainted files with their paths (`art/lunar/...` and `art/lunar/hotel/...`) and give the zip to Claude. Partial sets are fine.
