# Echo Landing: NPC sprite remake at 24×48

The playable roster in `art/` now uses Freya’s approved Soft Indie treatment across all 27 scheduled residents. Every regular route includes an animated meal and an occupation. The supplementary clothing sheets and S.A.R.A.’s stationary hologram have matching world sprites. The reference pack and its starter templates below describe the earlier conversion stage.

Echo Landing's residents are being redrawn at **24×48 pixels** (Stardew Valley's are 16×32; we're aiming for about 1.5× its detail). The designs stay the same. This pack has everything ChatGPT, or any image tool, needs to remake each resident's **walk sheet** and **action sheet** at the new size.

| | |
|---|---|
| `NPC_LIST.csv` | All 24 residents: who they are, the exact file names, the sizes, and each one's action rows in order. |
| `<id>/references/` | The current art at the old size: walk sheet (32×64 frames), action sheet (48×64 frames) and portrait. **Match these designs.** |
| `<id>/starters/` | The same sheets shrunk automatically to the new size. These are the original three-row starters. The current walk format appears below. Redraw over it, or use it as a size guide. |
| `TEMPLATE_walk_96x144_at8x.png` | The original three-row guide at 8×. Use the current five-row PNG in `art/` for new walk frames. |
| `TEMPLATE_actions_144xN_at8x.png` | The same for action sheets. |

Portraits (128×128, six moods) are **not** being remade: they belong to the interface and keep their size. Use them as the reference for each face. The player character isn't in this pack (it's built from layers; see Art Handoff 1).

---

## The two sheets

### Walk sheet: `art/npc_<id>.png`, exactly **96 × 240**
- **4 columns × 5 rows**, each frame **24 × 48**.
- **Columns, left to right:** facing **down** (toward the viewer), **up** (back to the viewer), **left**, **right**.
- **Rows, top to bottom:** **standing**, **contact A**, **contact B**, **passing A**, **passing B**. Walking plays rows **1, 3, 2, 4**. On each contact the opposite arm swings forward. During the next passing pose the body rises one pixel over the planted foot and the trailing knee lifts.
- **Height:** adults stand about **40–44 px** tall; children about **30–34 px**. Small species like the Moogli are shorter; tall ones like the Zaa'sh can reach about 46. Leave room for hair, ears and hats.
- **Feet:** on the bottom-centre of every frame, **2 px above the bottom edge** (the blue line in the template). Keep them in the same spot in every frame, so the character doesn't jitter.

### Action sheet: `art/npc_<id>_act.png`, exactly **144 wide × 48 per row**
- **4 frames across**, each **36 × 48**, looping at 3 frames a second. Frames are wider than walk frames so arms and tools fit.
- **One row per action, in the order listed for that resident** in `NPC_LIST.csv`, each facing the way listed. Keep the order, because the game picks rows by number.
- The feet stay at the bottom centre, as in the walk sheet.

---

## Style rules
- **Pixel art only:** hard pixels, no anti-aliasing, no blur, no soft shadows.
- **Detail:** about 1.5× Stardew Valley's. Use Stardew only as a guide to the amount of detail. **Never copy or trace Stardew Valley art.** These are original characters.
- **Proportions:** big heads (about a third of the height), clear silhouettes, readable faces with 2–3 pixel eyes.
- **Outline:** 1 pixel, coloured (deep blue-grey or a dark shade of the character's colour), never pure black.
- **Light:** from the top left.
- **Shading:** 3 to 5 shades per colour.
- **View:** top-down 3/4, like Stardew: seen from the front and slightly above.
- **Consistency:** keep each resident's colours, clothes and features from their references, so they stay recognisable.
- **Background:** transparent PNG. If the tool can't do transparency, use flat magenta (#FF00FF).

---

## Making a sheet with ChatGPT
1. **One resident per chat.** Use the current five-row walk PNG with the resident’s `references/portrait.png`.
2. **Prompt** (fill in from `NPC_LIST.csv`):
   > Pixel art sprite sheet for a cozy sci-fi life sim, about 1.5× Stardew Valley's level of detail, original design (not a copy). Redraw the attached character exactly, same design and colours, at the new size. Layout: 4 columns × 5 rows of 24×48-pixel frames. Columns: facing down, up, left, right. Rows: standing, contact A, contact B, passing A, passing B. Swing opposite arms and legs. Lift the trailing foot in each passing pose. Feet at the bottom centre of each frame, 2 px above the bottom, the same in every frame. Big head, 1-px dark blue-grey outline, light from top-left, 3–5 shades per colour, hard pixels, no anti-aliasing, flat #FF00FF background. Draw each art pixel as an 8×8 block. Character: **[who they are, from the list]**.
3. **Then:**
   > Using Python, downscale to exactly 96×240 with nearest-neighbour, turn #FF00FF transparent, and give me the PNG.
4. **For the action sheet,** paste `references/actions_old_48x64.png` and the action template:
   > Same character, action sheet: 4 frames across of 36×48 pixels, one row per action, in this order: **[action rows from the list]**. Each row is a short loop of that action, facing as listed.

   Downscale it to exactly 144 × (48 × rows).
5. **Check it in a pixel editor** (Aseprite, Pixelorama, LibreSprite):
   - exact size;
   - no soft or stray pixels;
   - the outline is complete;
   - the feet line up across all frames (flip between frames to check);
   - left and right are true mirror poses, unless the design isn't symmetric.

---

## Sending it back
- Name the files exactly `npc_<id>.png` and `npc_<id>_act.png`.
- Zip them in an `art/` folder, with a short `README.txt` saying which residents are included. Partial batches are fine.
- Claude reviews each zip before merging. The game keeps showing the automatic starters for anyone not redrawn yet.

### Suggested order
1. The six romance candidates already in the game: Freya, Jasper, Evarra, Job, Quill, Ix'ali.
2. Then the shopkeepers: Bram, Rusk, Sesska, Tobbin, Ooma, Maren.
3. Then everyone else.
4. S.A.R.A. last: she appears as her animated hologram, which is a separate set of art.
