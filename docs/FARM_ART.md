# Echo Landing: farm art (21 Nov 2026)

Farming now works one tile at a time, like Stardew: dig a tile, plant it, water it, harvest it. **One tile is 24 × 24 art pixels, the same width as a character** (the player and residents are 24 × 48). The old soil art was drawn in 48-pixel squares, two tiles wide, which is why it looked too big next to the player.

Until this art arrives, the game cuts the old 48-pixel soil art into tiles and draws stand-in crops. As soon as the files below are in the game folder, it uses them instead. No code changes are needed.

See `reference/field_in_game_now_x3.png` for how the field looks now, and `reference/player_24x48_for_scale.png` for the size of a person against a tile.

## Rules for every file
- **Crisp pixel art:** each pixel fully solid or fully see-through. No soft edges, no anti-aliasing, no blur, no resizing after drawing.
- **Exact sizes:** each tile 24 × 24, each crop picture 24 × 48. Don't add margins or padding.
- **PNG files, with exactly the names and folders below.**
- **Front-facing, top-down view**, lit from the top left, matching the station art.
- **Match the existing soil colours:** see `reference/existing_soil_art.png`. The main colours:
  - dry dirt: `#875d40`, `#785238`;
  - dug furrows: `#85573b`, `#68452f`, `#96684a`;
  - watered: `#5b3f30`, `#473429`, `#6c4b38`.

## 1. Dug soil: `art/farm/tilled.png` (96 × 96)
16 tiles of 24 × 24 in a 4 × 4 grid. The game picks a tile by which of its four neighbours are also dug, so any shape of field joins up. `templates/tilled_template.png` is the layout to paint over. `templates/tilled_guide_x4.png` labels every tile.

- **Number of a tile:** add 1 if the tile to the **north** is dug, 2 if **east**, 4 if **south**, 8 if **west**.
- **Where it goes:** tile number *i* is at column *i* % 4 and row *i* ÷ 4, counting from 0 at the top left. Tile 0 is a single dug square on its own; tile 15 is dug on all sides (the middle of a field).
- **Sides with no dug neighbour:** draw the edge of the dug ground there, such as a raised lip of loose earth with a little shadow inside it.
- **Sides with a dug neighbour:** no edge. The furrows must carry straight on into the next tile.
- **Furrows:** run them east–west, at the same heights in every tile, so a row of tiles reads as one long bed. The middle tile (15) must repeat seamlessly in all directions.
- **Variety (optional):** two or three versions of tile 15 make big fields less repetitive. Add them to the right of the sheet, making it 120 or 144 wide, and tell Claude.

## 2. Watered soil: `art/farm/tilled_wet.png` (96 × 96)
The same 16 tiles in the same places, darker and wet. The edges must sit exactly where they sit in `tilled.png`, so a tile can switch between dry and wet without moving. `templates/tilled_wet_guide_x4.png` is the guide.

## 3. Undug field: `art/farm/field.png` (72 × 24)
Plain field dirt that hasn't been dug, in three 24 × 24 versions side by side. Each must repeat seamlessly and fit next to the other two. The game mixes them across the field. `templates/field_template.png` is the size.

## 4. Crops: `art/farm/crops/<crop>.png`
One picture per growth stage, side by side, each 24 wide × 48 tall. The plant stands on the **bottom 24 pixels**, which is its tile. It may grow up into the top 24 pixels; tall crops like wheat should. Keep the base of the plant centred on the bottom tile. The last picture is the ripe crop. The `templates/crop_*` files have the right number of pictures for each crop, and the `_guide_x4` versions label them.

These three crops are placeholders until the economy chat settles the real crop list:

| File | Pictures | Notes |
|---|---|---|
| `crater_potato.png` | 5 (120 × 48): seeds, 3 growing, ripe | A low leafy bush; purple-skinned potatoes peeking out of the soil when ripe. |
| `moon_wheat.png` | 4 (96 × 48): seeds, 2 growing, ripe | Pale wheat; when ripe, tall golden stalks reaching well into the top half. |
| `star_tomato.png` | 5 (120 × 48): seeds, 3 growing, ripe | A staked bush with red five-pointed tomatoes when ripe. It fruits again after picking, so the ripe picture minus the fruit is the stage before it. |

**Seeds stage:** a few seeds or a small mound on the dug soil. Don't draw the soil itself, which is already there, and leave everything else see-through.

## 5. Icons, 24 × 24 each (in `art/items/`)
Same style as the other item icons.
- **Tools:** `hoe_basic.png`, `watering_can_basic.png`. These are the basic tier: worn grey metal with orange tape. Steel, titanium and Precursor versions come later.
- **Seed packets:** `crater_potato_seeds.png`, `moon_wheat_seeds.png`, `star_tomato_seeds.png`.
- **Crops:** `crater_potato.png`, `moon_wheat.png`, `star_tomato.png`.

## 6. Nice to have
- **Tool animations for the player:** hoeing and watering, 4 frames each, for each facing, in the same layered format as the eating animation, so they match the player's look.
- **Water splash:** about 4 frames of 24 × 24.
- **Grass border round the field:** the field is still framed with the old 48-pixel grass border. A 24-pixel version would follow the same 16-tile rule as `tilled.png`.

## Sending it
Zip everything with the folders as listed: `art/farm/tilled.png`, `art/farm/tilled_wet.png`, `art/farm/field.png`, `art/farm/crops/<crop>.png` and `art/items/<id>.png`. Then give the zip to Claude to install. Partial sets are fine: any file the game finds, it uses.
