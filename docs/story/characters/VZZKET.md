# Vzz'ket: heart events and his week (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **He has his own arc** as well as the side arc he shares with Rusk ("they need single arcs too"): see [`VZZKET_RUSK.md`](VZZKET_RUSK.md) for the side arc.
- **He's old-school Zaa'sh and doesn't like S.A.R.A. at the start** ("a voice with no throat"), **but he respects Tar'Besh.**
- **6 is at his campsite by the cavern gate.** The camp is made up properly now: his bedroll, the camp stove, kit chest and ration crates, plus his hunting banner and a spear rack (stand-ins until there's art).
- **8:** his first spear is a keepsake you can put in your quarters (a placeable item). At the end of 8 he stops guarding night and day. You've cleared most of what comes up from the caverns, or, once the Leviathan is dead, killed the thing the crawlers ran from. S.A.R.A. puts motion sensors down the stair to wake him if anything does come, and he trusts her enough now to accept her help.
- **Claude's, accepted:** 2 in the mess hall; 4 in the Sanctum, where Tar'Besh blesses a new spearhead (he blessed Vzz'ket's first spear on his pilgrimage, which is why the hunter respects the exile); 6's story.
- **Changed from the proposal:** the one who held the tunnel is his **clutch-brother, Tzz'ar**, not a mentor, because the game already says the spear and sword he lends you were his clutch-brother's.

**The arc:** the guard who never leaves his post.
- 2: a hunter eats with his back to the wall, and sleeps where the prey comes in.
- 4: the exile who blessed his first spear, and the voice with no throat.
- 6: the night he left his post, and the clutch-brother who held it alone.
- 8: the watch changes: S.A.R.A. keeps it, and his first spear watches over your house.

**What's whose:** the outlines and the decisions above are Zachary's; the scenes and every line are drafts by Claude. Right answers give +60 (High Friendship); wrong ones −20. He's platonic, so he caps at 8 hearts.

**Flags this arc sets:** `vzzket_wall` (2), `vzzket_blessing` (4), `vzzket_clutch_brother` (6), `vzzket_sensors` and the perk `perk_monster_radar` (8). 8 also gives the item `vzzket_first_spear`.

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| When | Where he goes |
|---|---|
| Every day at first (unchanged) | The cavern gate from 06:00; dinner; the gate again 19:00; the promenade 22:00; his bedroll by the gate 23:30 |
| After his 8, Monday to Saturday | The gate by day; dinner; the gate 19:00 (sparring with Ix'ali); a drink at the bar 21:00; his bedroll 23:00 |
| After his 8, Sunday (his day off) | Breakfast; the museum with Tar'Besh 09:30; lunch; holo-darts at the bar 13:30; dinner; the stage seats 19:00 |
| Fridays, after the side arc's 8 | The gate by day; dinner; the Open-Mic seats in the bar from 19:00 (Ix'ali holds the gate) |

- **Day lines** for Friday (after the side arc's 8) and Sunday (after his 8) only appear once he's earned them.
- He isn't on the calendar's days-off list (it can't read story flags yet).

---

## In the game (23 Nov)

All four are playable cutscenes in `scripts/heart_events.gd` (`vzzket_2` to `vzzket_8`, after Zaas's). Not run in Godot yet.

- **His heart-event sheet** is `art/npc_vzzket_event.png`; he also uses his guard rows.
- **The camp** (`tools/caves.py`): the hunting banner south of the gate and the spear rack north of it are new; there was no room for a seat by the stove, so he sits on a ration crate.
- **New scene step** `["give", item, count, toast]` puts items in your pack (his spear; Rusk's seeds).
- **His first spear** (`vzzket_first_spear`) is an item now; it can't be placed until your quarters can be furnished.
- **In play since 24 Nov:** the monster radar: on each cavern floor S.A.R.A. names the creatures on the floor below, and they are the ones you meet (`main.gd _radar_ping`). **Not in yet:** the sensor box and the camp's own art (Art Fix List).

---

## ♥2 Back to the Wall

**Trigger:** the mess hall, 17:15–18:45, with Vzz'ket at 2 hearts. Kit bursts in if you sit in the middle of the room.

- *[Dinner in the mess hall. Every table is full of talk, except the corner by the west wall.]*
- *[Vzz'ket eats his stew there standing up, his back to the wall and his eyes on the door.]*
- **VZZ'KET:** "Pilot. You are standing in my view of the door."
- **CHOICE:**
  - **"[Stand beside him, back to the wall]"** (+High Friendship)
    - *[You lean on the wall beside him and look at the room the way he does. Every way in. Every way out.]*
    - **VZZ'KET:** "...Good. You learn faster than the armourer."
  - **"[Take the empty seat in the middle of the room]"**
    - **KIT:** "[happy] VZZ'KET! Mum says you have to eat SITTING DOWN like a PERSON."
    - **VZZ'KET:** "[angry] Middle of the room. Back to the door. You would have been the first one taken."
    - *(-20 friendship with Vzz'ket)*
- **VZZ'KET:** "A hunter eats with a wall behind him and the door in his eye. And he sleeps where the prey comes in."
- *[You ask about the bedroll by the cavern gate.]*
- **VZZ'KET:** "The gate is the door. So I sleep by the door."
- **VZZ'KET:** "[sad] ...One night, I did not. Eat your stew, pilot."

## ♥4 A Blessing for the Spear

**Trigger:** the Sanctum on a Friday, 07:00–11:00 (Tar'Besh's Friday prayers), after 2.

- *[The Sanctum on a Friday morning. Tar'Besh is at his prayers before the crystals.]*
- *[Vzz'ket kneels in front of him, a new spearhead laid across his palms.]*
- **TAR'BESH:** "By the sky that made the hunter and the hunted: may this point fly true, and may it rarely need to."
- **TAR'BESH:** "[happy] The last spear I blessed for you was no longer than my arm. And you were no taller than that brazier."
- **VZZ'KET:** "The cleric came to our lodge on his pilgrimage, when I was a hatchling. He blessed my first spear."
- **S.A.R.A.** *(speakers)*: "[happy] Good morning! I've turned the Sanctum's heating back on, Tar'Besh, like you asked."
- **VZZ'KET:** "[angry] The voice with no throat. Even here."
- **TAR'BESH:** "She keeps the braziers lit when I forget. The crystals have not complained."
- **VZZ'KET:** "The Temple says—"
- **TAR'BESH:** "The Temple exiled me, hunter. And still you come to me for blessings."
- **VZZ'KET:** "The Temple did not bless my first spear. You did."
- **VZZ'KET:** "You. You trust the voice?"
- **CHOICE:**
  - **"I do. You don't have to. Not yet."** (+High Friendship)
    - **VZZ'KET:** "...'Not yet.' You sound like him."
    - **TAR'BESH:** "[happy] There are worse things to sound like. Go on, hunter. Your gate is waiting."
  - **"Only a fool wouldn't."**
    - **VZZ'KET:** "[angry] Then I am a fool. I have been called worse, by better."
    - *(-20 friendship with Vzz'ket)*

## ♥6 The Night He Left

**Trigger:** the mine, 22:30–midnight, after 4. His campsite by the cavern gate.

- *[Vzz'ket's camp by the cavern gate, late. The fire in the camp stove has burned down to violet coals.]*
- *[He sits on an upturned ration crate beside it, turning a whetstone over in his claws, not using it.]*
- **VZZ'KET:** "Sit. The gate is quiet. I can talk and listen at once."
- **VZZ'KET:** "On Kesh'ra our lodge held the hive-tunnels under the colony. Two hunters on the gate each night."
- **VZZ'KET:** "Me, and my clutch-brother, Tzz'ar."
- **VZZ'KET:** "On the night of the Hatching Feast, I left. One cup. One song. Back before the moon turned."
- **VZZ'KET:** "The tunnels had been quiet for a year. I was young."
- **VZZ'KET:** "[sad] When I came back, the gate was shut from the inside. Tzz'ar held it alone until the lodge came."
- **VZZ'KET:** "The colony slept through it. Nobody else was hurt."
- **VZZ'KET:** "[sad] They gave me his spear and his sword. You have carried both of them. That is why I said, bring them back clean."
- **VZZ'KET:** "So I do not leave the gate. Not for one cup. Not for one song."
- **CHOICE:**
  - **"[Sit with him by the fire]"** (+High Friendship)
    - *[You sit. For a long time neither of you says anything, and the coals tick, and nothing comes up the stair.]*
    - **VZZ'KET:** "He held it. That is the whole story. ...Thank you for listening to it."
  - **"You can't guard it forever."**
    - **VZZ'KET:** "[angry] Watch me."
    - *(-20 friendship with Vzz'ket)*

## ♥8 The Watch Changes

**Trigger:** the mine, 06:00–09:00, with Vzz'ket at 8 hearts. Tikka fits S.A.R.A.'s sensor box above the barricade. Rewards: his first spear (a keepsake for your quarters) and the Cavern Monster Radar.

- *[Morning at the cavern gate. Tikka is up on a crate, bolting a small grey box to the rock above the barricade.]*
- *[It has S.A.R.A.'s station seal on it. Vzz'ket watches it the way he watches the stair.]*
- *If the Leviathan is dead:*
  - **VZZ'KET:** "You killed the thing that broke the brood-queen. The thing the crawlers were running from."
  - **VZZ'KET:** "Since then the stair has been quiet. Truly quiet. I listened for a month to be sure."
- *If not:*
  - **VZZ'KET:** "You have cleared more of the caverns than our lodge did in a season."
  - **VZZ'KET:** "Three a week became one. One became none. I listened for a month to be sure."
- **TIKKA:** "[happy] Motion sensors, all the way down the stair. Anything bigger than a boot comes up, S.A.R.A. knows."
- **S.A.R.A.** *(the sensors)*: "[happy] And I'll wake you, Vzz'ket. Day or night. I don't sleep either, you know."
- **VZZ'KET:** "A year ago I would have pulled that box off the wall."
- **VZZ'KET:** "The cleric says a mind is a mind, whatever it is made of. ...Tzz'ar talked too much as well. He would have liked you, machine."
- **S.A.R.A.** *(the sensors)*: "[happy] I'll take that."
- **CHOICE:**
  - **"Let her keep watch tonight. Get some sleep."** (+High Friendship)
    - **VZZ'KET:** "...Yes. Tonight, I will sleep the whole night. I do not remember the last time."
  - **"Are you sure you can trust her?"**
    - **VZZ'KET:** "...No. But I will try. You are the one who taught me to try, pilot. Do not stop now."
    - *(-20 friendship with Vzz'ket)*
- *[He kneels at his kit chest and brings out something long, wrapped in faded lodge cloth.]*
- **VZZ'KET:** "My first spear. The one the cleric blessed. Hang it where you sleep."
- **VZZ'KET:** "On Kesh'ra, a hunter's first spear watches over the house. Yours has no hunter in it yet. It has one now."
- *[Vzz'ket gives you his first spear (for your quarters)]*
- **S.A.R.A.** *(the sensors)*: "[happy] Sleep well, Vzz'ket. That's what I'm for."
- **VZZ'KET:** "[happy] ...Those are my words, machine. Keep them. They suit you."
- *[Perk: Cavern Monster Radar (S.A.R.A. warns you what's waiting below)]*
- **The next morning** *(Claude, 23 Nov)***:** a letter from Vzz'ket, "The box chirped" (`vzzket_sleep` in `scripts/mail_data.gd`). The text is in [MAIL.md](../MAIL.md).

