# The Custodians: the main story (decided 24 Nov 2026)

Zachary's plan, 24 Nov, with his answers to Claude's questions the same evening. It replaces the four-Custodian plan in the Drive doc "Custodian Bundles" (the bundle lists there are kept where the game has the items) and the Reliquary scene in [`PROLOGUE_SCRIPT.md`](PROLOGUE_SCRIPT.md). Lines and names marked (Claude) are drafts.

## The mystery

The Precursors, whom the Zaa'sh call the **Sky-Weavers** and some human scholars the **Starborn**, are a higher form of life we can't really understand. They have no name we could hear or say; the Custodians "dumb everything down" when they speak of them. The Custodians are crystal shards they left behind, vessels of their knowledge and power, made to fix problems. Without their makers they have waited, and they offer to help you.

**Only you can hear them.** When you crash, the dying Mother-Drone beams part of itself into your mind, and from then on you can talk with Precursor artifacts that still have a voice: the Custodians. (Relics stay ordinary: they have a text description, nothing more.)

## The story, in order

1. **Prologue** (cutscenes only). The ambush: Ivan the Rabble catches the *Wandering Star* in the asteroids, you can't win; his salvo shears her starboard wing off, and you make a blind jump. The crash: you fall through the crust of an uncharted moon into a cavern where a Precursor Mother-Drone lies half-buried. It beams part of itself into your mind and goes dark. S.A.R.A. calls on the radio and you black out. The Medbay: Maren and Quill; Quill notices a spike in your brain scan. S.A.R.A. puts you in the agri keeper's flat for a few days of quarantine and says Tar'Besh wants to see you at the museum. Then the first morning, as now. The fighter in the Shuttle Bay is what's left of the *Wandering Star*.
2. **The museum** (the first time you walk in). Tar'Besh explains a little of the Sky-Weavers' lore and shows you what he has found. He is called away (the children knock something over). The three crystals in the Sanctum call to you: they are Custodians, they explain what they are, and they offer to fix the station if you bring what they need. Tar'Besh comes back and sees them glowing. He can't hear them, so he becomes your partner: you translate, he writes it down. S.A.R.A. notices her station mending itself overnight.
3. **The three Custodians of the Sanctum**: their bundles fix parts of the station.
4. **The Harbinger**, a crystal on cavern floor 25. He needs volatile materials, and his blast opens the underground sea.
5. **The Shepherd of Storms** (Claude), in a sector of Collective space under a severe storm. The storm is a dying Starborn; the Shepherd was left to tend it. Your materials let it lay the Starborn to rest, and the storm ends. That opens **Tidelight**.
6. **The Warden** on Tidelight, the sixth Custodian (name to come).
7. Each Custodian found outside the Sanctum is carried there once its bundles are done.
8. **The vision.** With all six together in the Sanctum, they share a vision with you, Tar'Besh and S.A.R.A. (the first time those two hear them): more about the Starborn, and how life can come in many forms.

## The six Custodians and what they fix

Each has three bundles on the datapad's Reliquary tab; each finished bundle fixes one named part of the station overnight. The Drive doc's items the game doesn't have yet are swapped for ones it does.

| Custodian | Where | Bundles fix |
| :- | :- | :- |
| **Sovereign of Hydro-Flora** (serene, poetic) | Sanctum | the Agri Complex's storage dome (moved off S.A.R.A.'s repair list); sprinklers; fruit trees for the agri dome |
| **Chancellor of Hearths** (warm, fussy) | Sanctum | the hotel's second wing (four more suites); the Spaceport's empty kiosks (new shops); the sealed gates |
| **Forgemaster of Keels** (gruff, naval) | Sanctum | the Shipwright's Suite; the shipyard; storm plating for your ship |
| **Harbinger** (polite, sorry about his title) | cavern floor 25 | his blast opens the sea: the East Complex garden dome comes back to life, the Underground Lake opens, and the way down to the Leviathan on floor 45 |
| **Shepherd of Storms** (Claude) | the storm sector, Collective space | the storm ends; Tidelight appears on the jump map |
| **The Warden** (name to come) | Tidelight | to come |

Notes:

- **Bees:** Evarra's bees already arrive in the Jasper & Evarra side arc (decided 22 Nov), so the Sovereign's third bundle gives fruit trees instead of the apiary.
- **S.A.R.A.'s paid repairs:** the hot springs and fish ponds stay with her, after the Leviathan.
- **The Leviathan:** it lives in the sea the Harbinger opens. Before the blast the caverns end at floor 44.

## Tidelight (to rework later)

Zachary, 24 Nov: maybe call it **Everlight Falls**; add a cool waterfall and a stream running through the village; and the future map should be **woodland themed**. "We can work on the planet later." The map below is the first pass.

A tidally locked world, so everywhere you can go is at sunset: the beach on the sunward edge, a small village in the twilight band, and a forest running into the night side. The name plays on "twilight" and "tidally locked" (Claude).

- **The village:** Collective settlers the storm cut off for years; the storm lifting reunites them. Three or four villagers, a shop and a beach bar, no heart events at first.
- **Getting there:** after the storm ends, a space shuttle runs from the Spaceport, a fast-travel route to Tidelight, and residents visit on their days off (like Ginger Island).
- **Art:** Claude draws everything, to the art style guide.

## The ending (open)

Zachary, 24 Nov: "not entirely sure, but maybe the space storm you see in the intro main menu is a young Starborn using the station and custodians to learn how to control itself."

The green storm cloud with lightning on the title screen. One way it could fit (Claude): the Shepherd's storm was a Starborn dying; the title's storm is one being born, the Mother-Drone's child. The Custodians were left to raise it, and every part of the station they mend with you is it learning to build instead of break. In the vision it shows itself, calm for the first time.

## What's built (24 Nov)

- **The prologue** (`scripts/story_scenes.gd` "prologue"): plays after you make your character on a new game.
  - **Space** is picture panels (cutscene steps `board`, `bsprite`, `bmove`, `bmoves`, `bfade`, `flash`). It opens with your inner monologue (25 Nov, Zachary: "a little inner monologue at the start to explain you are a pirate hunter paid ... by the Terran empire since they cannot officially enter neutral space"): forty years ago the war between the Empire, the Junta and the Collective ended in a treaty that made the space between them the Neutral Zone, where no power's warships may go; the pirates moved in, so the Empire pays licensed hunters in their own ships; your family has hunted pirates for generations; Ivan the Rabble is the biggest name on the board (Claude's draft).
    - **The Wandering Star** is the artist's own pixel art, the Needle (25 Nov: "original pngs of the player fighter"): `art/ships/needle/needle_intact.png` and `needle_damaged.png`, 80 x 55, used exactly as drawn. She is only ever shown at a whole size (3x in space, 2x in the storm scenes, 3x into the crash-site wreck) with no smoothing, so her pixels stay crisp. Ivan's first hits burn along her hull; the big one swaps her to the damaged picture and the lost wing tumbles away (`needle_wing.png`, cut from the difference between the two pictures). She stays in one piece otherwise (25 Nov: "dont have the back half of your ship come apart, just the wing gets shot off"): the jump takes her whole. Her engine plumes (`needle_plume.png`) sit on her two nozzles and trail behind her, in the menu's plume colours. The 3D model that drew her before (`tools/dev/fighter_model.py`) is gone.
    - Ivan's flagship glides in on the right; near asteroids drift past. You fire first and your bolts splash off his shield; his salvo burns along her hull and shears her wing off. Then the moon, put together from the main menu's own art; she burns in with a smoke trail and strikes the slope in a flash, a fireball and a dust plume (`tools/dev/prologue_art.py`).
  - **It plays out by itself** (25 Nov: "the music doesnt sync because you click to continue, so just have it play out"): from the start until the Mother-Drone dies, every line turns over by itself (cutscene step `say_timed`; clicks do nothing while one is up), timed to the music. The choice of reply to Ivan is gone (it needed a click); you say "I'm a licensed bounty hunter, Ivan. Stand down." S.A.R.A.'s radio call and the Medbay after it are clicked through as usual. Lines get about 1.3 s plus a second for every 16 letters.
  - **Music** (Zachary's two songs; `music_director.gd` scene scores, cutscene steps `score`, `score_wait`, `score_end`):
    - Your opening thoughts play in silence. **Space Battle** starts from its first note with the alarm: Ivan hails you as the full band comes in (15.2 s); his salvo lands on the drum fill (60.2, 60.4, 60.6 s; the big hit at 61.4 s shears your wing off); you slam the FTL lever as the finale comes in (69.7 s) and the drive spools through it; and your ship jumps on the song's last hit (76.84 s, "the end of battle music riff should sync to where your ship model jumps"). The moon and the crash are silent.
    - **Lunar Discovery** comes in as you see the drone across the cavern (63 s, a phrase start): it wakes on an accent (104.1 s), speaks on another (115.3 s), its beam reaches you on another (145.4 s), the glyphs fold into the mark as the song comes back in full (173.3 s), and it dies on the last chord (191.2 s), its light going out with the slow wind-down.
    - Song times measured from the files (Space Battle's beat grid: 151.8 bpm, a downbeat at 0.094 s). The timeline is built by `tools/dev/prologue_timeline.py`: edit a line or a cue time there and run it; it rewrites the scene and stops if any line would run past the moment after it.
  - **The crash** plays in the game itself, on a cavern map built and baked like the others, with the caverns' haze, grit and pools of light (`tools/crash_site.py`, area `crash_site`). She lies nose-first in a heap of rock: the damaged Needle drawn 3x into a 13 x 8 prop, the torn edge of her wing glowing, wires hanging out of the stump, the canopy cracked, a gouge and scrap behind her. The Mother-Drone (13 x 8 tiles): raised ribs, a channel of engraved glyphs, an aperture lens, violet crystal grown out of the cracks in its shell and a crown of it where the tail broke open, crystal columns round it (`tools/dev/crash_site_art.py`). Light falls through the hole you made, with dust and grit; fire, smoke, sparks and the red emergency light play on the wreck; when the drone wakes its veins light, its lens blades turn, its crystals catch the light, and its beam reaches your canopy; the star-glyphs wheel over the screen and fold into the mark.
    - **Lore** (Claude's drafts): your thoughts on the spacers' stories (silver lights that hum like struck glass) and the Terran scholars who call the Starborn a myth; the drone: "Long before your sun had a name, we were sown here. Seeds... left to wake when the small worlds needed tending", the makers "not gone. Further. Larger. Your words for them are... storms. And stars", and where the Custodians sleep: three behind glass among the old things your kind keeps (the museum), others in the stone, in the storm, and on a world that never sees its night.
  - **Sound:** no music between the songs; the ship's drone in space and the cave's drips at the crash (cutscene steps `music`, `ambient`), and eight effects (`tools/dev/prologue_sounds.py`). Nothing made up plays over Lunar Discovery's moments: the drone's hum and the bell run on the glyphs are gone (25 Nov, Zachary didn't like them clashing with the song).
- **The museum scene** ("custodians_wake"): the first time you walk into the museum after your first morning. It wakes the three Sanctum Custodians.
- **Giving:** right-click a crystal in the Sanctum. The Custodian speaks; "Give what I have" puts in everything its open bundles still need. A full bundle mends its part overnight, and the first time S.A.R.A. writes to you ("Something odd overnight").
- **The datapad's Relics page** lists every Custodian you've found, each bundle's items (given / needed, and how many you carry) and what it mends.
- **The Custodians' call** (25 Nov; Zachary on the bell that played when they spoke: "too loud and harsh and not mysterious musical"): `audio/custodian_call.wav`, a soft swell of glass tones rising into an E minor (add 9) chord over a low E, with a long, dark echo; no strike, and quieter than the bell (`tools/dev/custodian_sounds.py`). Each Custodian's scenes play it at its own pitch, a musical step apart (cutscene step `["sfx", name, pitch]`): the three in the museum and the vision as made, the Harbinger three semitones down, the Shepherd a tone down, the Warden a tone up, and the lullaby that ends the storm a fourth down, so slower and lower. The bell still plays in three heart events that aren't the Custodians (Tar'Besh's prayer, Tikka's music box, the lanterns), now softened: its clang filtered off above 3 kHz, its strike eased in over 25 ms, and about 4.5 dB quieter (`tools/dev/cut_drive_sounds.py`).
- **Portraits:** all six crystals (`tools/dev/custodian_art.py`).
- **Rewards that work now:** sprinklers (a recipe on the Crafting page; each waters the four tiles beside it every morning), the storage dome (off S.A.R.A.'s list), fruit-tree saplings (moon-peach, star-apple, sun-fig: 21 days to grow, then fruit every 4), the Shipwright's Suite flag (`suite_restored`, which heart events already read).
- **Rewards that only set their flag so far** (the systems come next): the hotel's second wing (`hotel_wing`), the Spaceport kiosks (`kiosks`), the gates (`gates`), the shipyard (`shipyard`), storm plating (`storm_plating`).
- **The Harbinger:** a crystal in the wall of cavern floor 25, near the ladder, whatever layout the floor gets. The first time, it speaks ("harbinger_found", a scene that plays where you stand). Its last bundle sets off the blast at once ("harbinger_blast"); overnight the sea opens (`blast`), the East Complex's garden dome gets its water (`east_dome`, which residents' days and heart events already read), the Underground Lake's stair unseals, and Tar'Besh writes that an ember-coloured crystal has turned up in an empty Sanctum cradle. You talk to it there from then on. Until the blast, floor 44 has no shaft down: the Leviathan's shore (45) is sealed. Saves that already reached 45 keep it.
- **The Great Storm:** a stop on the outermost ring of every free flight, in Collective space (`ShipRuns.place_storm`). Without the Forgemaster's storm plating it throws you back (-3 hull). With it, the first visit plays "shepherd_found" (picture panels over the storm): the storm is a dying Starborn and the Shepherd was left to tend her. You give the Shepherd's bundles at the stop. The last one plays "storm_ends" at once: the lullaby, the dying Starborn's one line, and the storm going out. Overnight the stop becomes **Tidelight** (for now it only logs the old Collective beacon; landing comes with the planet), S.A.R.A. writes about the world and the beacon, and the Shepherd's crystal turns up in a Sanctum cradle, tinted violet.
- **Tidelight** (`tools/tidelight.py`, 86 x 50): the sea on the west, a beach with a dock, the village (a landing pad, four prefab homes, the old Collective beacon on its mast, a market stall, a beach bar, lamps, a campfire), and the dusk forest running east into the night. Always sunset (`main.gd _light_color`). Floors drawn by `tools/dev/tidelight_art.py`. Twelve forage spots (sun-lilies, glow plankton, ember asters, dusk resin, duskwood, night moss) grow back every day.
- **Getting there:** land from the Tidelight stop on the jump map (it ends the day's flight), or, once the Chancellor has opened the gates, board the shuttle at the Spaceport's Gate 2. The shuttle on Tidelight's landing pad flies you home. The first visit plays "tidelight_arrival".
- **The Warden:** in the forest clearing at the far east. Coming near it plays "warden_found". Its bundles want Tidelight's forage, and its last one the Sovereign's star-apples. When it's done, Tar'Besh writes that the sixth cradle is full.
- **The vision** ("the_vision"): once all six are complete and home, the next time you walk into the Sanctum. Tar'Besh and S.A.R.A. hear the Custodians for the first time; the six show you what the Starborn are, and that the green storm on the title screen is a young one, the Mother-Drone's child, learning from them to build instead of break. This is Claude's draft of Zachary's idea; the ending is still open.
- **Debug:** F3 also gives what the Custodians you've found still need.

## Still to do

- **Tidelight's settlers:** the village is there but nobody is out yet ("keeping out of sight, for now"). Next: three or four villagers, the market and the beach bar as shops, and residents visiting on their days off, like Ginger Island.
- **A shuttle pilot** at Gate 2 (Eshu, if he's arrived), and the shuttle's own art (it's the covered fighter for now).
- **The rewards that only set a flag:** the hotel's second wing, the kiosks, the shipyard, the Tidelight market and beacon.
- **The ending,** once Zachary decides.
