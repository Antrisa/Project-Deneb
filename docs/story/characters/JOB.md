# Job: heart events and his week (22 Nov 2026)

**Decided with Zachary, 22 Nov:**
- **Weekends off** (a miner doesn't need cover like the cooks): Saturday and Sunday. He has his own lines on those days.
- **6 gets a backup place:** it plays by the underground lake once the Leviathan is dead and the old stair opens; until then, at the sealed hatch of the mine's flooded stair, where you can hear the sea below.
- **10's backup** is his script's: the Shuttle Bay windows at night, where he shows you the skiff he's building with Tobbin.
- 8's backup before the hot springs open is his porch outside East Home 6, because his script's backup (the break room) is already his 2.
- 4 plays in the mine's iron bay: the caverns are random floors, so a cutscene can't be set on "floor 4".

**The arc:** a quiet man carrying the station's weight on a worn-out drill, and the homeland he's never seen.
- 2: his granddaddy's gumbo smells like a home he's never been to.
- 4: the roof comes down, and he admits how much he hates letting folks down.
- 6: Zaas was right; there's a sea under the moon.
- 8: he doesn't need Earth to know where he belongs.
- 10: a skiff on the underground sea: home is who's in the boat with you.

**What's whose:** lines marked *(Zachary)* below are his, from "Heart Events: All Romances": all of 2 except the replies to its choice, the setting and both lines of 4, both lines of 6, and the two speeches of 8. Everything else is a draft by Claude, for Zachary to change or approve: the cave-in action and Zaas in 4, the choices in 4 and 6 (his script has none), the replies to 8 (accept, decline, friendship ending), and all of 10. Long lines of his are split in two for the dialogue box. Each line starts with a portrait tag the game already reads. Choices give +30 (Friendship) or +60 (High Friendship).

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | Where he goes |
|---|---|
| Monday to Friday | The mine from 06:30; lunch at the mess; the mine 13:30; a thermos break in the Engineering break room 15:45; dinner; Rusk's bar 19:15; home 22:00; bed 22:45 |
| Saturday (day off) | A late breakfast at the mess 09:00; Bram's shop 10:30; lunch 12:30; his porch outside East Home 6 14:00; dinner; the bar 19:15 |
| Sunday (day off) | Breakfast 09:00; his porch 10:30; gumbo at home from 14:00 (he skips the mess-hall dinner); the bar 19:15 |
| Saturday, once the garden dome is open | The afternoon is at the hot springs instead of the porch |
| Sunday, once the Leviathan is dead | Fishing at the underground lake's old fishing camp 10:00–16:00, then gumbo at home |

**What he says on those days** (`scripts/npc_data.gd`, `DAY_LINES`): Saturday is boots off and doing nothing on the porch; Sunday is a pot of gumbo "by noon". The station calendar lists his days off.

**Flags this arc sets:** `job_rig_quest` (4: the Reinforced Mining Rig quest with Tikka, not built yet), the perk `perk_bedrock_strength` (8), the keepsake `keepsake_oar_charm` (10), and `partner` = Job if you accept at 8.

## In the game (22 Nov)

All five are playable cutscenes in `scripts/heart_events.gd`. He poses from his new heart-event sheet (`art/npc_job_event.png`) and his action sheet. Not run in Godot yet.

- **To test:** in a debug build, **F4** plays the next event in order (Job's 2 is the sixteenth press). **F5** opens the garden dome (8 at the hot springs). The lake versions of 6 and 10 need the Leviathan dead.
- **Checked offline:** `python3 tests/check_heart_events.py` (6, 8 and 10 at both their places).
- **Not in yet:** the Reinforced Mining Rig quest itself, what Bedrock Strength does in play, the skiff (art, and rowing it: the crossing happens under a fade), and the oar charm as an item you can hold.
- **Still open:** Zaas's 8 christens a research skiff on the same sea; the review suggested making it the same boat (Job builds it with Tobbin, Zaas christens it).

---

## ♥2 Gumbo in the Breakroom

**Trigger** *(Zachary, place renamed)***:** enter the Engineering crew break room between 16:00 and 19:00 on a weekday, with Job at 2 hearts. (The script's "Mines entrance breakroom" is this room, by the mine lift.)

**Setting** *(Zachary)***:** a small metal table near the mine lift. Job is carefully stirring a thermos of spiced stew while polishing a dented plasma pickaxe.

- *[A small metal table near the mine lift. Job is stirring a thermos of spiced stew, a dented plasma pickaxe across his knees.]*
- **JOB** *(Zachary)*: "[happy] Well now, look who came down from the bright lights. Pull up a crate, sha—you look like you been swinging a pick all afternoon."
- *[He pours a mug of rich, smoky stew and slides it across the table.]* *(Zachary)*
- **JOB** *(Zachary)*: "My granddaddy passed down that spice blend from old Louisiana—or so the family logbooks say."
- **JOB** *(Zachary)*: "Never set foot on Earth myself, never seen a bayou or heard a cicada, yet somehow the smell of cayenne and smoked root still feels like home."
- **CHOICE:**
  - **"Home is wherever you bring your people and your recipes."** *(Zachary)* (+High Friendship)
    - **JOB:** "[happy] ...Huh. Mama used to say near the same thing."
  - **"This is the best thing I've tasted since landing here."** *(Zachary)* (+Friendship)
- **JOB** *(Zachary)*: "[happy] Careful saying things like that, or Jasper's gonna try to steal my thermos."

---

## ♥4 Cave-In on Shaft Four

**Trigger:** enter the mine during his shift (07:00–15:45 on a weekday) with Job at 4 hearts, after Gumbo in the Breakroom.

**Setting** *(Zachary)***:** a narrow iron-vein tunnel. Loose shale rumbles down, pinning Zaas's diving-bell crate and cracking Job's old drill rig.

- *[A crack like a gunshot. Loose shale pours from the roof of the iron vein.]*
- **JOB:** "[shocked] Ceilin's comin' down! Get clear, cher!"
- *[Job throws his shoulder under a steel support beam and holds the roof up by main force.]*
- *[Zaas's diving-bell crate is half buried. Job's old drill rig lies cracked beside it.]*
- **ZAAS:** "[shocked] My hydrophones! Seven years of listening are in that crate!"
- **JOB:** "[angry] Get his crate, cher! I got the roof!"
- **CHOICE:**
  - **"[Dig out the crate]"** (+High Friendship)
    - *[You haul rock until the crate slides free. Zaas drags it clear and hugs it.]*
  - **"[Help Job hold the beam]"** (+Friendship)
    - *[You put your shoulder beside his. The beam steadies, and Zaas digs out his own crate, muttering.]*
- *[Job kicks a wedge under the beam. The rumbling stops. Dust settles.]*
- **JOB** *(Zachary)*: "[sad] Appreciate the quick hands. Truth is, this old Terran drill's held together by prayer and copper wire."
- **JOB** *(Zachary)*: "Everybody counts on my ore quotas to patch the hull, and I hate letting folks down."
- **JOB:** "Tikka's been on at me to let her rebuild the rig. Reckon it's time I knocked on her door."

---

## ♥6 Lanterns by the Cavern Sea

**Trigger:** 19:00–22:30 with Job at 6 hearts, after the cave-in. Once the Leviathan is dead: go down to the underground lake, and it plays on the shore by the old fishing camp. Until then: go into the mine, and it plays at the sealed hatch of the flooded stair.

- **If the Leviathan is dead (the lake is open):**
  - *[Lantern light on black water. Job sits on a smooth basalt boulder, watching the ripples glow.]*
  - **JOB** *(Zachary)*: "All those years Zaas was hollering about underground oceans, I thought the poor fella had breathed too much rock dust."
  - **JOB** *(Zachary)*: "Turns out... sometimes the wildest dreams are right underneath your boots."
- **Otherwise:**
  - *[The old stair is sealed with a steel hatch. Water seeps up round its edges, cold, in slow pulses.]*
  - **JOB:** "Hear that? Under the hatch. That ain't the pumps, cher. That's tide."
  - **JOB** *(Zachary)*: "All those years Zaas was hollering about underground oceans, I thought the poor fella had breathed too much rock dust."
  - **JOB** *(Zachary)*: "Turns out... sometimes the wildest dreams are right underneath your boots."
- **JOB** *(Zachary)*: "Reminded me of the old stories about the Gulf coast back on Earth. Funny how a dry moon can surprise you when someone takes the time to dig deep."
- **CHOICE:**
  - **"[Sit with him a while]"** (+High Friendship)
    - *[You sit. Neither of you says much. The water does the talking.]*
    - **JOB:** "[happy] Ain't many folks can sit quiet. You're one of 'em."
  - **"Tell me the Gulf coast stories."** (+High Friendship)
    - **JOB:** "[happy] Mama told 'em. Pelicans. Shrimp boats. Water so warm you could fall asleep in it."
    - **JOB:** "I never could tell which parts she made up. Didn't matter much."
- **JOB:** "[happy] Bring a lantern next time. It's better with two."

---

## ♥8 Quiet Ground (confession)

**Trigger:** walk into the East complex 17:30–19:30 with Job at 8 hearts. Once the garden dome is open it plays at the hot springs; until then on his porch.

- **If the garden dome is open:**
  - *[Steaming mineral pools, lit by warm lanterns. Job sits by the water with his boots off.]*
- **Otherwise:**
  - *[Job's porch at the end of the day. A lantern hangs by his door, and the street is quiet.]*
- **JOB:** "[happy] Evenin', cher. Sit a spell."
- **JOB** *(Zachary)*: "I'm a simple man, sha. Give me honest work, good company, and a quiet place to sit at the end of a shift."
- **JOB** *(Zachary)*: "Since your ship fell through the moon's roof into that old drone's cave, every single one of those things got brighter."
- **If you are dating someone else (the friendship ending):**
  - **JOB:** "[happy] You're the best company I've had, cher. Whoever you're sweet on, they're lucky. You tell 'em I said so."
- **Otherwise:**
  - *[He reaches out a calloused hand.]*
  - **JOB** *(Zachary)*: "[love] I don't need to travel to Earth to find where I belong. Right here with you is all the home I'll ever want. What do you say?"
  - **CHOICE:**
    - **"Yes, Job. Right here."**
      - *(Job is now your partner.)*
      - **JOB:** "[surprised] Well now. Well now."
      - **JOB:** "[happy] Mama'd have liked you, cher. She'd have fed you till you couldn't stand."
      - *[You sit with him until the lanterns burn low.]*
    - **"You mean a lot to me, as a friend."**
      - **JOB:** "[sad] That's all right, sha. Had to say it, or I'd be carryin' it around."
      - **JOB:** "[happy] This spot's still yours whenever you want it. That don't change."
- **JOB:** "[happy] And you're workin' too hard down in that mine. I'll show you how to swing a pick so it don't swing you."
- **Perk: Bedrock Strength (mining uses 20% less energy, and more geodes drop)**

---

## ♥10 Bayou Under the Stars

**Trigger:** 20:00–24:00 while you're dating Job, with him at 10 hearts. Once the Leviathan is dead: go down to the underground lake (the long dock). Until then: the Shuttle Bay, at the windows.

- **If the Leviathan is dead (the lake is open):**
  - *[At the end of the long dock a little wooden skiff rocks on the black water, a lantern on its bow.]*
  - **JOB:** "[happy] Built her with Tobbin. Took us all winter. She don't leak much."
  - **JOB:** "Climb in, cher. Mind the middle seat. That's where the gumbo goes."
  - *[He rows you out across the glowing lake. Crystals hang from the dark above, like stars that came down for a closer look.]*
  - *[Somewhere in the middle he stops rowing, and you just drift.]*
- **Otherwise:**
  - *[The Shuttle Bay at night. Past the windows the crater is silver with starlight. Behind you, on trestles, sits a half-built wooden skiff.]*
  - **JOB:** "[bashful] Tobbin and me, we been buildin' her nights. For when that old stair opens up."
  - **JOB:** "Ain't no bayou on this moon. But there's a sea under it, and I mean to row you across it."
  - *[You sit on the trestles with him and watch the stars wheel past the windows, the way he says folks sat out on the bayou at night.]*
- **JOB:** "[love] Mama used to say a home ain't the land. It's who's in the boat with you."
- **JOB:** "[bashful] Whittled you somethin'. Out of the offcuts from the oar."
- *[A little carved oar on a cord, worn smooth by his thumbs.]*
- **Keepsake: Job's carved oar charm**
