# The Custodians: the main story (decided 24 Nov 2026)

Zachary's plan, 24 Nov, with his answers to Claude's questions the same evening. It replaces the four-Custodian plan in the Drive doc "Custodian Bundles" (the bundle lists there are kept where the game has the items) and the Reliquary scene in [`PROLOGUE_SCRIPT.md`](PROLOGUE_SCRIPT.md). Lines and names marked (Claude) are drafts.

## The mystery

The Precursors, whom the Zaa'sh call the **Sky-Weavers** and some human scholars the **Starborn**, are a higher form of life we can't really understand. They have no name we could hear or say; the Custodians "dumb everything down" when they speak of them. The Custodians are crystal shards they left behind, vessels of their knowledge and power, made to fix problems. Without their makers they have waited, and they offer to help you.

**Only you can hear them.** When you crash, the dying Mother-Drone beams part of itself into your mind, and from then on you can talk with Precursor artifacts that still have a voice: the Custodians. (Relics stay ordinary: they have a text description, nothing more.)

## The story, in order

1. **Prologue** (cutscenes only). The ambush: Ivan the Rabble catches the *Wandering Star* in the asteroids, you can't win, and you make a blind jump that tears the back of the ship away. The crash: you fall through the crust of an uncharted moon into a cavern where a Precursor Mother-Drone lies half-buried. It beams part of itself into your mind and goes dark. S.A.R.A. calls on the radio and you black out. The Medbay: Maren and Quill; Quill notices a spike in your brain scan. S.A.R.A. puts you in the agri keeper's flat for a few days of quarantine and says Tar'Besh wants to see you at the museum. Then the first morning, as now. The fighter in the Shuttle Bay is what's left of the *Wandering Star*.
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

## Tidelight

A tidally locked world, so everywhere you can go is at sunset: the beach on the sunward edge, a small village in the twilight band, and a forest running into the night side. The name plays on "twilight" and "tidally locked" (Claude).

- **The village:** Collective settlers the storm cut off for years; the storm lifting reunites them. Three or four villagers, a shop and a beach bar, no heart events at first.
- **Getting there:** after the storm ends, a space shuttle runs from the Spaceport, a fast-travel route to Tidelight, and residents visit on their days off (like Ginger Island).
- **Art:** Claude draws everything, to the art style guide.

## The ending (open)

Zachary, 24 Nov: "not entirely sure, but maybe the space storm you see in the intro main menu is a young Starborn using the station and custodians to learn how to control itself."

The green storm cloud with lightning on the title screen. One way it could fit (Claude): the Shepherd's storm was a Starborn dying; the title's storm is one being born, the Mother-Drone's child. The Custodians were left to raise it, and every part of the station they mend with you is it learning to build instead of break. In the vision it shows itself, calm for the first time.

## What's built (24 Nov)

- **The prologue** (`scripts/story_scenes.gd` "prologue"): plays after you make your character on a new game. The space and cavern parts are picture panels (new cutscene steps: `board`, `bsprite`, `bmove`, `bmoves`, `bfade`, `flash`); the cavern, the Mother-Drone and its portrait are drawn by `tools/dev/prologue_art.py`.
- **The museum scene** ("custodians_wake"): the first time you walk into the museum after your first morning. It wakes the three Sanctum Custodians.
- **Giving:** right-click a crystal in the Sanctum. The Custodian speaks; "Give what I have" puts in everything its open bundles still need. A full bundle mends its part overnight, and the first time S.A.R.A. writes to you ("Something odd overnight").
- **The datapad's Relics page** lists every Custodian you've found, each bundle's items (given / needed, and how many you carry) and what it mends.
- **Portraits:** all six crystals (`tools/dev/custodian_art.py`).
- **Rewards that work now:** sprinklers (a recipe on the Crafting page; each waters the four tiles beside it every morning), the storage dome (off S.A.R.A.'s list), fruit-tree saplings (moon-peach, star-apple, sun-fig: 21 days to grow, then fruit every 4), the Shipwright's Suite flag (`suite_restored`, which heart events already read).
- **Rewards that only set their flag so far** (the systems come next): the hotel's second wing (`hotel_wing`), the Spaceport kiosks (`kiosks`), the gates (`gates`), the shipyard (`shipyard`), storm plating (`storm_plating`).
- **Debug:** F3 also gives what the Custodians you've found still need.
