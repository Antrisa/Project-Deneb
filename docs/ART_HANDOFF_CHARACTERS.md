# Echo Landing: art handoff 1 — characters, portraits and animations

This is for making pixel art with ChatGPT, or any image tool, for Echo Landing. It is a 2D, top-down 3/4-view station sim in the style of Stardew Valley, made in Godot. Give this whole document to ChatGPT, together with two or three existing sprites from the game as style references. Item, environment and effects art is in **art handoff 2**.

Written 18 Nov 2026 from the game files on branch `promenade-v11`.

---

## 1. Style rules (every picture)

- **Pixel art only.** Hard pixel edges, no anti-aliasing, no blur, no gradients that are not dithered or banded, no soft shadows.
- **Detail level:** like Stardew Valley characters, drawn at double detail. Use Stardew only as a guide to the amount of detail. **Never copy or trace Stardew Valley art.** Every design is original.
- **Look:**
  - big heads;
  - clear silhouettes;
  - a 1-pixel dark outline, coloured (deep blue-grey or dark brown), never pure black;
  - light from the top left;
  - 3 to 5 shades per colour.
- **View:** top-down 3/4, like Stardew. Characters are seen from the front and slightly above.
- **Background: transparent PNG.** If the tool can't do transparency, use flat magenta (#FF00FF) with no shading, so it can be keyed out.
- **Exact sizes matter.** The game scales art by exactly one half, and screens show it at 6× (1080p) or 8× (1440p). A picture one pixel off size, or with blurry edges, will look broken.
- **Feet** sit at the bottom centre of each frame, about 2 px above the bottom edge, in the same spot in every frame. That keeps the character from jittering.

### Getting exact pixel art out of ChatGPT
Image tools draw large, soft pictures. To turn one into a game sprite:
1. **Ask for a large picture.** Have it drawn on a flat background (transparent, or #FF00FF), at a whole multiple of the target size, with the pixel grid clearly visible. "Each art pixel is an 8×8 block" works well.
2. **Shrink it to the exact size** using nearest-neighbour resampling. ChatGPT can do this with Python. Ask: "downscale to exactly 128×192 with nearest-neighbour, remove the magenta background, and give me the PNG."
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

### Walk sheet: `art/npc_<id>.png`, **128 × 192**
- 4 columns × 3 rows. Each frame is **32 × 64**.
- **Columns**, left to right: facing **down** (toward the viewer), **up** (back to the viewer), **left**, **right**.
- **Rows**, top to bottom: **standing**, **step A** (left foot forward), **step B** (right foot forward). The game plays step A, standing, step B, standing.
- The character fills most of the frame height. Adults are about 52–58 px tall, children about 40–46 px, with headroom for hair and ears.

### Action sheet: `art/npc_<id>_act.png`, **192 wide**, **64 × number of rows** tall
- 4 frames across, each **48 × 64**. They play in a loop at 3 frames a second.
- One row per action, in the order listed for that character. Each action faces one way (down, up, left or right).
- The frames are wider than walk frames so arms and tools fit. Feet stay at the bottom centre.

### Portrait: `art/portrait_<id>.png`, **768 × 128**
- 6 frames of **128 × 128**, left to right: **neutral, happy, sad, surprised, love, angry**.
- Head and shoulders, turned slightly toward the viewer. Same framing in all 6 frames: only the face and a little of the posture change.
- Transparent background. The dialogue box supplies the panel.

---

## 3. What already exists (keep matching it)

All 24 current residents have a walk sheet, an action sheet and a portrait, painted by Zachary:
- Bram, Evarra, Freya, Garrick, Ix'ali, Jasper, Job, Kit, Maren, Merrow, Nub, Ooma
- Owen, Pip, Quill, Rusk, Saffi, Sesska, Tar'Besh, Tikka, Tobbin, Vzz'ket, Zaas
- S.A.R.A. She also has a separate hologram animation module in `sara/`.

The rows on their current action sheets, kept in this order:

| Resident | Action rows, top to bottom |
|---|---|
| Bram | counter (left), eat (down), drink (up), rest (down) |
| Evarra | mix (down), herbs (up), rest (down) |
| Freya | weld (up), hammer (up), eat (down), drink (up), rest (down) |
| Garrick | ledger (up), patrol (down), eat (up), drink (left), rest (down) |
| Ix'ali | polish (down), eat (down), spar (left), rest (down) |
| Jasper | cook (down), relax (down), rest (down) |
| Job | mine (up), eat (down), drink (up), rest (down) |
| Kit | study (up), play (down), toy (down), eat (up), rest (down) |
| Maren | treat (down), eat (down), rest (down) |
| Merrow | valve (down), tend (up), valve (left), eat (up), rest (down) |
| Nub | draw (up), play (down), eat (up), rest (down) |
| Ooma | beckon (up) |
| Owen | shelve (up), eat (down), bench (down), rest (down) |
| Pip | study (up), play (down), wave (up), eat (down), rest (down) |
| Quill | sort (down), eat (down), read (up), rest (down) |
| Rusk | wipe (down), eat (down), pour (down) |
| Saffi | sweep (down), browse (down), watch (left), eat (up), rest (down) |
| Sesska | weave (down), eat (down), chat (left), rest (left) |
| Tar'Besh | study (up), eat (down), ponder (up), rest (down) |
| Tikka | console (up), eat (down), tinker (down), rest (right) |
| Tobbin | build (down), eat (up), sketch (down), rest (down) |
| Vzz'ket | guard (right), eat (down), walk-stop (down) |
| Zaas | survey (up), eat (down), stargaze (up), rest (down) |

When you add rows to an existing sheet, add them **at the bottom** so the existing row numbers don't change.

---

## 4. Needed next

### 4a. Four new residents (from the NPC Relationship Bible; they arrive later in the story)
Each needs a walk sheet, an action sheet and a portrait, using the file ids below. The looks are suggestions; Zachary has the final say.

| id | Who | Look (suggested) | Action rows |
|---|---|---|---|
| `artie` | Arthur "Artie" Vance, human man, a 2036 Minnesota scout frozen for 400 years | Late 20s to 30s, outdoorsy, a faded 2030s flannel or scout shirt under a station jacket, neckerchief, slightly lost expression | teach knots (down), read (up), campfire sit (down), eat (down), rest (down) |
| `stu` | Stowaway Stu, human man, the hotel lobby boy | Young and wiry. A plain drifter jacket at first; later the burgundy-and-gold bellhop uniform (make the uniform a second walk sheet, `npc_stu_uniform.png`) | carry luggage (down), ring bell (down), sweep (down), eat (down), rest (down) |
| `tally` | Tally, Arachnay man, courier | Arachnay like Tikka and Sesska, with four arms and a courier satchel and cap | sort mail with four arms (down), carry crate (down), eat (down), rest (down) |
| `ana` | Anastasia "Ana", human woman, reformed pirate heir | Pilot's jacket with a torn-off pirate insignia, practical, guarded posture, a scar or bandage at first | tune thrusters (up), chart at console (up), eat (down), drink (left), rest (down) |

### 4b. Heart-event poses (event sheet per character)
Heart events are short scenes, and they need poses the daily action sheets don't have. Give each character one more file: **`art/npc_<id>_event.png`**, in the same format as the action sheet (192 wide, rows 48 × 64, 4 frames).
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

### 4c. Player animations (layered: ask Claude before starting)
The player is built from layers so the character creator works:
- **Layers:** bottoms, tops, faces and hair. Each is 128 × 1920: 4 directions × 10 style choices × 3 walk poses.
- **Body types:** two, `art/player/` (Male) and `art/player/body2/` (Female).
- **Masks:** each layer has a mask where **red** = the layer's colour, **green** = skin and **blue** = eyes.

New player actions are needed for:
- timed mining (laser swing, 4 frames per direction);
- watering;
- fishing (cast, wait, reel);
- the two weapon attacks;
- getting hurt;
- collapsing;
- sitting;
- sleeping;
- eating or drinking;
- holding a found item up overhead.

Every one of these must exist on every layer, for every style choice and both bodies, so it is a lot of work. **Ask Claude to set up the pose-sheet format and code first.** It may be simpler to draw action poses as a single full-body sheet per body type, with only the hair and clothes colours tinted.

### 4d. Creatures (caverns)
- **Format:** `art/enemy_<id>.png`, **2 frames side by side**, each **32 × 32**. The 2 frames are a simple idle or move loop.
- **Existing:** bug, lizard, spore crawler, vent crab. Check the mine chat's latest list for what is already done.
- **Needed:**
  - Creatures for each cavern band, getting bigger every 15 floors:
    - floors 1–15, rock: stone beetle, cave bat;
    - floors 16–30, lush: vine creeper, glow moth, fungus brute;
    - floors 31–45, steamy and watery: steam eel, magma slug, armoured crab.
  - **The Harbinger of Destruction** (boss, floor 45). Its current file is a tiny placeholder. A boss needs a much bigger sprite, and the game currently shows every creature 16 px wide, so **ask Claude to add boss sizing first**. Suggested: 4 frames of 128 × 128.

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
