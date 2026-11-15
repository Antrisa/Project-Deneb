# Echo Landing: notes for testers

Thanks for trying this. It is an early build: one town, 24 residents, a mine and some caves. A lot of it has never been run before today, so expect rough edges and please report them.

## Getting it running

1. Install **Godot 4.6** (standard version, not .NET) from godotengine.org.
2. Download this project (on GitHub: **Code > Download ZIP**, then unzip it).
3. Open Godot, choose **Import**, pick `project.godot` in the unzipped folder, then press **F5**.

Controls are in `README.md`. **F9** wipes your save and starts a new game.

## If it will not start

If the game stops with a red error in Godot, that is the most useful thing you can send. Copy the red text from the **Debugger > Errors** tab or the **Output** panel at the bottom of the Godot window. It names a file and a line number.

## What is new and has not been played yet

Please look at these in particular.

- **Character screen** at the start of a new game: gender, hair, face, clothes, colours. Do all the lines fit? Do the colour bars drag properly? You can reopen it at the locker in your quarters.
- **Your character walking** in all four directions, both genders, especially hair from the side.
- **The 14 new residents.** Find each one and talk to them. Do their walking pictures and portraits look right, and do they face the right way?
  - Medbay (east wing): Maren and Quill. Library: Owen. Pip, Nub and Kit play by the fountain after noon.
  - Weaver's shop (east wing): Sesska. Armoury (east wing, south side): Garrick and Ix'ali.
  - Rusk's bar (south-west of the square). Furniture workshop (west wing): Tobbin. Merrow works at the fountain.
  - Ooma's market stall is only there on **Wednesdays and Saturdays** (days 3 and 6).
- **Residents doing things.** When the new residents stop walking they should play an action: checking a chart, wiping a glass, sweeping. Do they stand in the right spot, with feet on the floor? Does anyone jump sideways or float?
- **Dinner at 18:00** in the mess hall: 23 people should be seated. Does anyone get stuck on the way or sit on someone else?
- **The bar in the evening** (from about 19:15): Bram, Freya, Job and Garrick should be there.
- **Medpacks:** buy one from Maren (40 credits) and use it from the hotbar.
- **Collapsing:** run out of hearts in the tunnels. You should wake up in the medbay.
- **Friends page** (Tab, fourth page): 24 residents in three columns. Is anything cut off?
- **"He" and "she":** Evarra and Job each have a line that talks about you. It should match the gender you picked.

## Known gaps (no need to report)

- The ten original residents have no action animations yet; they bob in place.
- Rusk, Ooma, Tobbin, Sesska and Ix'ali do not sell anything yet.
- Some furniture is placeholder art: couch, counters, stove, sink, fridge, stools, tables.
- The cave creatures, weapons and slash effect are in an older, blockier style.
- Walls are one tile high, and the map is due a redesign (a ring of apartments around the square, shop interiors as their own rooms).
- Sound effects and music are simple generated placeholders.

## Reporting

For each problem, say **where you were**, **what day and time it was** (top of the screen), **what you did**, and **what happened**. A screenshot helps.
