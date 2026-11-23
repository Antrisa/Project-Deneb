# Echo Landing: art handoff 1 — characters, portraits and animations

This is for making pixel art with ChatGPT, or any image tool, for Echo Landing. It is a 2D, top-down 3/4-view station sim in the style of Stardew Valley, made in Godot. Give this whole document to ChatGPT, together with two or three existing sprites from the game as style references. Item, environment and effects art is in **art handoff 2**.

Written 18 Nov 2026; **updated the same day for the 24-pixel grid** (24×48 characters, branch `art24`).

---

## 1. Style rules (every picture)

- **Pixel art only.** Hard pixel edges, no anti-aliasing, no blur, no gradients that are not dithered or banded, no soft shadows.
- **Detail level:** about 1.5× Stardew Valley's: characters are **24×48** (Stardew's are 16×32). Use Stardew only as a guide to the amount of detail. **Never copy or trace Stardew Valley art.** Every design is original.
- **Look:**
  - big heads;
  - clear silhouettes;
  - a 1-pixel dark outline, coloured (deep blue-grey or dark brown), never pure black;
  - light from the top left;
  - 3 to 5 shades per colour.
- **View:** top-down 3/4, like Stardew. Characters are seen from the front and slightly above.
- **Background: transparent PNG.** If the tool can't do transparency, use flat magenta (#FF00FF) with no shading, so it can be keyed out.
- **Exact sizes matter.** One art pixel is exactly 3 screen pixels at 1080p and 4 at 1440p. A picture one pixel off size, or with blurry edges, will look broken.
- **Feet** sit at the bottom centre of each frame, about 2 px above the bottom edge, in the same spot in every frame. That keeps the character from jittering.

### Getting exact pixel art out of ChatGPT
Image tools draw large, soft pictures. To turn one into a game sprite:
1. **Ask for a large picture.** Have it drawn on a flat background (transparent, or #FF00FF), at a whole multiple of the target size, with the pixel grid clearly visible. "Each art pixel is an 8×8 block" works well.
2. **Shrink it to the exact size** using nearest-neighbour resampling. ChatGPT can do this with Python. Ask: "downscale to exactly 96×240 with nearest-neighbour, remove the magenta background, and give me the PNG."
3. **Check and fix it** in a pixel editor (Aseprite, Pixelorama or LibreSprite):
   - stray coloured pixels;
   - soft edges;
   - the outline is complete;
   - the feet line up in every frame.
4. **Keep each character consistent.** Paste their existing walk sheet and portrait into the chat and say "match this character exactly".

Prompt template:
> Pixel art sprite sheet for a cozy sci-fi life sim (Stardew Valley level of detail, original design, not a copy). Top-down 3/4 view, big head, 1-px dark blue-grey outline, light from top-left, hard pixels, no anti-aliasing, flat #FF00FF background. Layout: [layout from below]. Character: [description]. Match the attached reference sprites in proportions, outline and palette.

---

## 2. Sheet formats (what the game expects)

### Walk sheet: `art/npc_<id>.png`, **96 × 240**
- 4 columns × 5 rows. Each frame is **24 × 48**.
- **Columns**, left to right: facing **down** (toward the viewer), **up** (back to the viewer), **left**, **right**.
- **Rows**, top to bottom: **standing**, **contact A**, **contact B**, **passing A**, **passing B**. Walking plays rows **1, 3, 2, 4**. On each contact the opposite arm swings forward. During the next passing pose the body rises one pixel over the planted foot and the trailing knee lifts.
- The character fills most of the frame height. Adults are about 40–44 px tall, children about 30–34 px, with headroom for hair and ears.

### Action sheet: `art/npc_<id>_act.png`, **144 wide**, **48 × number of rows** tall
- 4 frames across, each **36 × 48**. They play in a loop at 3 frames a second.
- One row per action, in the order listed for that character. Each action faces one way (down, up, left or right).
- The frames are wider than walk frames so arms and tools fit. Feet stay at the bottom centre.

### Portrait: `art/portrait_<id>.png`, **768 × 128** (unchanged: portraits belong to the interface)
- 6 frames of **128 × 128**, left to right: **neutral, happy, sad, surprised, love, angry**.
- Head and shoulders, turned slightly toward the viewer. Same framing in all 6 frames: only the face and a little of the posture change.
- Transparent background. The dialogue box supplies the panel.

---

## 3. What already exists (keep matching it)

All 27 scheduled residents have four-direction, four-phase walks and individual activity sheets. All 27 use Freya’s approved Soft Indie style for their walking, meals and work. Freya’s own work clothes match her walking sprite. The dialogue portraits are the identity reference for each resident. The Moogli and children have shorter silhouettes, the Arachnay walk on offset limbs, and S.A.R.A. projects from her dais. The original cast includes the following characters.
- Bram, Evarra, Freya, Garrick, Ix'ali, Jasper, Job, Kit, Maren, Merrow, Nub, Ooma
- Owen, Pip, Quill, Rusk, Saffi, Sesska, Tar'Besh, Tikka, Tobbin, Vzz'ket, Zaas
- S.A.R.A. She also has a separate hologram animation module in `sara/`.

The rows on their current action sheets, kept in this order:

| Resident | Action rows, top to bottom |
|---|---|
| Bram | counter (left), eat (down), drink (up), rest (down), restock (left) |
| Evarra | mix (down), herbs (up), rest (down), eat (down), garden (up) |
| Freya | weld (up), hammer (up), eat (down), drink (up), rest (down) |
| Garrick | ledger (up), patrol (down), eat (up), drink (left), rest (down) |
| Ix'ali | polish (down), eat (down), spar (left), rest (down) |
| Jasper | cook (down), relax (down), rest (down), eat (down) |
| Job | mine (up), eat (down), drink (up), rest (down) |
| Kit | study (up), play (down), toy (down), eat (up), rest (down), hologame (down) |
| Maren | treat (down), eat (down), rest (down), kneel (down), first aid (down) |
| Merrow | valve (down), tend (up), valve (left), eat (up), rest (down), garden (up) |
| Nub | draw (up), play (down), eat (up), rest (down) |
| Ooma | beckon (up), eat (down) |
| Owen | shelve (up), eat (down), bench (down), rest (down), chess (right) |
| Pip | study (up), play (down), wave (up), eat (down), rest (down), hologame (up) |
| Quill | sort (down), eat (down), read (up), rest (down), read (left) |
| Rusk | wipe (down), eat (down), pour (down), rest (down) |
| Saffi | sweep (down), browse (down), watch (left), eat (up), rest (down), browse (up) |
| Sesska | weave (down), eat (down), chat (left), rest (left) |
| Tar'Besh | study (up), eat (down), ponder (up), rest (down), chess (left) |
| Tikka | console (up), eat (down), tinker (down), rest (right) |
| Tobbin | build (down), eat (up), sketch (down), rest (down) |
| Vzz'ket | guard (right), eat (down), walk-stop (down) |
| Zaas | survey (up), eat (down), stargaze (up), rest (down), observe (left) |

Jasper and Evarra take staggered suppers after service. Ooma takes a meal break on visiting days. The concourse garden, chess, hologame, reading, observation, browsing and restocking stops use painted poses for the attending resident. Maren’s weekend and winter clothing, Ana’s alternate uniform, Tally’s event poses and S.A.R.A.’s solid appearance follow the same cast artwork.

When you add rows to an existing sheet, add them **at the bottom** so the existing row numbers don't change.

---

## 4. Later arrivals and event poses

### 4a. Later arrivals

The four arrival characters use the same walk and activity formats as the original residents. Their existing route, arrival conditions and overnight stays select these rows through `MapData.SCHEDULES` and `MapData.SCHEDULES_ALT`. Each activity name includes its facing.

| Resident | Activity rows in sheet order |
|---|---|
| Artie | Tie knots (down), read (up), sit at a campfire (down), eat (down), rest (down), eat (up), recover (up) |
| Stu | Carry luggage (down), ring a bell (down), sweep (down), eat (down), rest (down), eat (up) |
| Tally | Sort mail (down), carry a crate (down), eat (down), rest (down), sort mail (up), eat (up) |
| Ana | Tune thrusters (up), chart a route (up), eat (down), drink (left), rest (down), eat (up), recover (up) |

### 4b. Heart-event poses (event sheet per character)
Heart events are short scenes, and they need poses the daily action sheets don't have. Give each character one more file: **`art/npc_<id>_event.png`**, in the same format as the action sheet (144 wide, rows of 4 frames of 36 × 48).
- **Shared rows, every character, in this order:**
  1. talk with hands (down)
  2. laugh (down)
  3. sad or teary (down)
  4. surprised jump (down)
  5. hold out a gift (right)
  6. sit on a bench (down)
  7. wave (down)
- **Extra rows after those, per character** (from the bible's events):

| id | Extra event rows |
|---|---|
| `freya` | spacesuit walk (down), sit on catwalk looking up (up) |
| `jasper` | present a plate (right), despair over a pan (down) |
| `evarra` | barefoot dance in grass (down), weave a flower crown (down) |
| `job` | brace a beam overhead (up), row a skiff (right) |
| `quill` | gather spilled vials, kneeling (down), offer a pressed fern (right) |
| `ixali` | kneel with a shield (left), duel stance with practice blade (left) |
| `sara` | No sheet. Her events use her existing hologram clips; ask Claude which ones are missing. |
| `zaas` | wear brass diving helmet (down), joyful cry (down) |
| `tarbesh` | carry a tea tray (right), bow (left) |
| `rusk` | raise a mug (down) |
| `pip`, `kit`, `nub` | run (right), point excitedly (up) |

Start with the six romance candidates who are already in the game (Freya, Jasper, Evarra, Job, Quill and Ix'ali), then S.A.R.A.'s and Tar'Besh's arcs.

> Code note: the event sheets aren't wired into the game yet. The NPC chat builds the heart-event system that plays them. Painting them first is fine; the format above is what that system will expect.

### 4c. Player model and animations

The two player starter looks use the silhouettes and colours of the original player turnaround. The first has chestnut hair, an open slate flight jacket with a copper sleeve patch, plum-grey trousers and broad brown boots. The second has a low plum ponytail, a terracotta tunic with cream edging, teal-grey trousers and brown boots. Each walking cell is 24 × 48 art pixels. Keep the level, two-pixel brows touching the row of the eyes, a flat two-pixel resting mouth, and the planted sole on row 45.

The eight reference cells in `docs/player_turnaround_24x48.png` show the front, back, right side and extended right step for each body. They supply the native hair, face, clothes and boot shapes. In a passing pose the planted shoe uses the flat standing sole. Starting a new character and switching bodies shows the corresponding starter outfit until the player customizes it. Changing bodies at the locker keeps the player's wardrobe and dyes. Selecting **Starter look** (Home on the keyboard) applies the pictured outfit and colours for the current body.

- The four walk layers in `art/player/` and `art/player/body2/` are bottoms, faces, tops and hair. Each 96 × 2400 atlas has ten styles, with five rows per style in the walk-sheet order. The ten face slots share the player face for compatibility with saved appearances.
- Walking turns the jacket at the shoulders above the planted hips. The near elbow flexes as the opposite boot reaches, and the trailing hand clears the belt in each passing pose.
- `action_tops.png` and its mask measure 960 × 960. Ten outfits run across, each with four 24-pixel direction columns. Their 20 rows are carry idle, carry contact A, carry contact B, carry passing A, carry passing B, grip, lift, strike, pour, scythe windup, sweep, follow-through, ground reach, overhead pickup, brace, recoil, recover, gather the can, raise the handle and hold the can forward. The assembled player action sheet is 96 × 960.
- `scripts/player_poses.gd` defines the native head and hand positions. Higher hands cross the fringe when facing the camera. In a watering profile, the near arm is drawn across the handle and the far arm passes behind the can. The tool's pivot follows its hand throughout the turn, including mining recoil. Harvesting ripe moon wheat plays the scythe sweep. Potatoes and tomatoes use the ground reach and overhead pickup.
- Watering gathers the can at chest height, lifts the handle in front of the player, tips the spout toward the plot and lowers the can. The face and hair stay registered to the standing pose in all four directions. A compact bend at the elbow keeps the wrist on the handle. The six droplets leave the visible spout during the pour.
- In `art/player/watering_arm_mask.png`, each outfit uses four direction columns. The first four rows are the first body’s gather, raise, ready and pour poses. The next four are the second body’s poses. The arm stencil selects the sleeve and hand to draw in front of the can from the player’s dyed outfit. The startup player uses `art/player_watering_arms.png` until the custom appearance loads.
- Red masks select the layer colour, green selects skin and blue selects eyes. A blue value of 64 on a red or green mask preserves the painted hue shifts when tinting. Pure masks use the earlier luminance rule. Unmasked stitching, boot leather and eye whites keep their painted colours.
- Eating uses the same body and wardrobe in `player_eating/`. Each 48 × 68 cell includes the reach above the head. The arm atlas has ten outfit-specific sleeves. The final pose returns to the standing art at offset (12, 17).
- Seated poses draw from the selected model. Combat and hit effects use the active appearance. Dedicated poses for fishing, sleeping and collapsing remain possible future additions.

### 4d. Creatures (caverns)
- **Format:** `art/enemy_<id>.png`, **2 frames side by side**, each **24 × 24** for normal creatures. The 2 frames are a simple idle or move loop.
- **Existing:** bug, lizard, spore crawler, vent crab. Check the mine chat's latest list for what is already done.
- **Needed:**
  - Creatures for each cavern band, getting bigger every 15 floors:
    - floors 1–15, rock: stone beetle, cave bat;
    - floors 16–30, lush: vine creeper, glow moth, fungus brute;
    - floors 31–45, steamy and watery: steam eel, magma slug, armoured crab.
  - **The Harbinger of Destruction** (boss, floor 45). Its current file is a tiny placeholder. A boss needs a much bigger sprite, and the game currently shows every creature one tile wide, so **ask Claude to add boss sizing first**. Suggested: 4 frames of 96 × 96.

---

## 5. Delivering the art
- Put the files in a zip, using the exact file names above, inside an `art/` folder.
- Add a short `README.txt` listing what's new or changed.
- Claude reviews the zip before merging and adds every file to `art/hand_edited.txt`, so the game's placeholder generator never overwrites them.
- Before zipping, check each one:
  - exact size;
  - transparent background;
  - no soft edges;
  - feet in the same place in every frame;
  - the same outline colour as the existing art.
