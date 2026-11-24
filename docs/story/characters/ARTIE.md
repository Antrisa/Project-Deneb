# Artie: heart events and his week (23 Nov 2026)

**Decided with Zachary, 23 Nov:**
- **He starts out sad and out of place, and finds his place.** A new **0-heart scene** when he first wakes: you show him round the station, and he gets sad.
- **2** (talking about his history in the library) **gives him the idea for the Scouts**, which he starts at **4**.
- **The campfire scenes (8 and 10)** are in the garden dome's woods by the hot springs, with the **little park** in the East complex as the backup until the dome is open.
- **His week:** before the Scouts, mostly the library, wandering round the plaza, or the Observation Lounge. After the Scouts, he helps out in the library; **Monday afternoons** are Scouts; **the first Saturday of every month** is a Scouts outing (a season is the station's month).
- **Where he came from:** your script's version: in October 2036 a silent silver light lifted his truck off a Minnesota highway. His game lines said "a cold-sleep trial by a lake", so his first-meeting line now matches the script.

**The arc:** woke up centuries late; finds a second chapter teaching the station's kids.
- 0: everything's strange, and even the stars are in the wrong places.
- 2: his old life, and three kids who've never seen a campfire.
- 4: the Junior Scouts: why he woke up.
- 6: the same stars from a different porch.
- 8: done looking backward.
- 10: a troop, a home, and you.

**What's whose:** lines marked *(Zachary)* are his, from "Heart Events: All Romances": the setting and line of 2 and its choices, the setting and line of 4, the setting and line of 6, and both lines of 8 (split three ways). Everything else is a draft by Claude, for Zachary to change or approve: all of 0, the troop story and the Scouts idea in 2, the kids and the plan in 4, S.A.R.A. and the choice in 6, the replies to 8 (accept, decline, friendship ending), and all of 10. Choices give +30 (Friendship) or +60 (High Friendship).

---

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| | Day | Where he goes |
|---|---|---|
| Before the Scouts | Monday, Wednesday, Friday | The library 08:00; wandering round the plaza 11:00–13:00; lunch; the Observation Lounge 14:00; dinner; home |
| | Tuesday, Thursday, Saturday, Sunday | The lounge 09:00; the plaza at noon; lunch; the library 14:30; dinner; home |
| After the Scouts (his 4) | Tuesday to Friday | Helping Owen in the library, mornings and afternoons |
| | Monday | The library in the morning; **Scouts at the fountain 14:30** with Pip, Kit and Nub |
| | Saturday | The plaza, the lounge, the library |
| | Sunday | A late breakfast, the plaza, the lounge in the afternoon |
| | First Saturday of each season | **Scouts outing** all day: the little park, or the garden dome's woods once it's open, with the kids |

The kids' weeks change too: on Mondays Pip, Kit and Nub come to the fountain at 15:00 instead of their usual afternoon, and they join the first-Saturday outing. "First Saturday" is new in the schedules: `"dates": [1, ..., 7]` (days of the season) with `"days": [5]`.

**Flags this arc sets:** `artie_troop_story` (2), `artie_scouts` (4: changes his week and the kids'), the perks `perk_junior_scout_reports` (4) and `perk_thrifty` (8), the keepsake `keepsake_scoutmaster_badge` (10), and `partner` = Artie if you accept at 8.

## In the game (23 Nov)

All six are playable cutscenes in `scripts/heart_events.gd`. He poses from his new heart-event sheet (`art/npc_artie_event.png`) and his action sheet (recovering in bed, reading, tying knots, at the campfire). The tour in 0 moves between three maps (Medbay, plaza, lounge) under fades. S.A.R.A. speaks in 6. Not run in Godot yet.

- **He only appears once he's arrived** (Wave 1, the day after Ivan falls), so his scenes wait for that. 0 plays the first time you go into the Medbay after he wakes; S.A.R.A.'s morning news sends you there.
- **New step `met`:** the tour introduces him, so talking to him afterwards isn't a first meeting.
- **To test:** in a debug build, **F3** plays the next event in order (Artie's 0 is the thirty-first press); it now brings Wave 1 in if it hasn't arrived. **F5** opens the garden dome (8 and 10 in the woods).
- **Checked offline:** `python3 tests/check_heart_events.py` (8 and 10 at both places).
- **In play since 24 Nov:** Thrifty, for geodes (Job's bench sometimes finds one of the rare ones, `shops.gd roll_geode`); the recycling half waits for a recycler. **Not in yet:** the Junior Scout Foraging Reports in play, tents and the burner as props (narrated), the badge as an item you can hold.

---

## ♥0 Out of Time (new)

**Trigger:** go into the Medbay 08:00–20:00 once Artie is awake.

- *[Artie sits on the edge of a medbay bed in borrowed clothes, turning his hands over as if they belong to someone else.]*
- **MAREN:** "[happy] Good, you're here. He's awake, he's restless, and he's asked me what year it is four times."
- **MAREN:** "Take him for a walk. Slowly. And bring him back in one piece."
- **ARTIE:** "[surprised] You're the one who towed me in? Arthur Vance. Artie. Thank you. I think."
- **ARTIE:** "[sad] Maren says it's been centuries. Nobody's sure how many. I keep waiting for someone to tell me it's a joke."
- **CHOICE:**
  - **"Come on. I'll show you around."** (+Friendship)
  - **"It's a lot. One step at a time."** (+Friendship)
- **ARTIE:** "[happy] ...Okay. A walk. I can do a walk."
- *(The scene moves to the plaza.)*
- *[The plaza: a fountain under a painted sky, and people of half a dozen species going about their day.]*
- **ARTIE:** "[surprised] Okay. Okay. Somebody just waved at me with four arms. I waved back with two. I think I did it wrong."
- **ARTIE:** "And that's a fox. In an apron. Running a kitchen. Sure. Why not."
- **ARTIE:** "[sad] Back home I knew everybody on my street. Here I don't even know what half of you are. No offence."
- *(The scene moves to the Observation Lounge.)*
- *[The Observation Lounge. Beyond the glass, a sky thick with stars.]*
- **ARTIE:** "[happy] Now this I know. Stars. Okay. The Big Dipper should be right about..."
- **ARTIE:** "[sad] ...It isn't there. None of them are. They're all in the wrong places."
- *[He's quiet for a long time.]*
- **ARTIE:** "[sad] Everybody I ever knew is a few hundred years gone. And I'm on a moon I can't pronounce, looking for a sky that isn't here."
- **CHOICE:**
  - **"You're not alone here, Artie."** (+Friendship)
    - **ARTIE:** "[sad] ...Yeah. I'm starting to see that. Thanks."
  - **"[Stand with him a while]"** (+Friendship)
    - *[You stand beside him and say nothing. It seems to help.]*
- **ARTIE:** "Thanks for the tour. I think I'll sit here a while. Maybe the stars'll make sense if I stare long enough."

---

## ♥2 Centuries Late

**Trigger:** enter the library 08:00–11:00 with Artie at 2 hearts, after Out of Time. (Pip, Kit and Nub are at their lessons there.)

- *[Owen's library. Artie sits surrounded by glowing holo-scrolls covering centuries of Earth history, looking overwhelmed.]* *(Zachary)*
- *[He rubs his temples and offers a wry, tired smile.]* *(Zachary)*
- **ARTIE** *(Zachary)*: "Last thing I remember, it was October 2036, I was driving home from a troop campout in Minnesota,"
- **ARTIE** *(Zachary)*: "and a silent silver light lifted my truck right off the highway."
- **ARTIE** *(Zachary)*: "Now Owen tells me my hometown is a historical footnote and my neighbors are seven-foot lizard clerics and fox chefs."
- **CHOICE:**
  - **"Take it one day at a time—you don't have to catch up overnight."** *(Zachary)* (+High Friendship)
    - **ARTIE:** "[happy] One day at a time. My old Scoutmaster used to say that. Huh."
  - **"Honestly, the fox chef makes incredible food."** *(Zachary)* (+Friendship)
    - **ARTIE:** "[happy] Ha! Okay. Yeah. He does. That's one thing this century got right."
- **ARTIE:** "A troop campout. Twelve kids, one canoe that leaked, and me, the guy who taught them to tie knots and find north."
- *[Across the library, Pip, Kit and Nub are hunched over their lessons: glowing screens, and not a window in sight.]*
- **ARTIE:** "Those three have never seen a campfire. Never slept under the sky. Pip asked me yesterday what a canoe is."
- **ARTIE:** "[sad] Back home I'd have had them out the door in five minutes. Here I wouldn't even know where to start."
- **CHOICE:**
  - **"Start where you always did."** (+High Friendship)
    - **ARTIE:** "...Huh. With a knot. You always start with a knot."
  - **"Teach them anyway."** (+High Friendship)
    - **ARTIE:** "...Huh. You make it sound easy."
- **ARTIE:** "[happy] Thanks for listening. It feels good to talk about home with someone who doesn't need it explained."

---

## ♥4 The Junior Scouts

**Trigger:** walk onto the promenade 12:30–15:00 with Artie at 4 hearts, after Centuries Late.

- *[Pip, Nub and Kit sit cross-legged around Artie at the fountain as he teaches them square knots, emergency beacon signals and lunar orienteering.]* *(Zachary)*
- **ARTIE:** "[happy] Right over left, left over right. That's a square knot. It holds a tent, a splint or a friendship bracelet."
- **PIP:** "Mine's a lump."
- **KIT:** "Mine's a better lump."
- **NUB:** "[happy] Nub's is a knot! Nub's is a REAL knot!"
- **ARTIE:** "[happy] Hey! Come see. Remember what we talked about in the library? I couldn't stop thinking about it."
- **ARTIE** *(Zachary)*: "Turns out knot-tying and looking out for your buddy don't go out of style in a few hundred years."
- **ARTIE** *(Zachary)*: "Seeing Pip laugh again... I think I finally figured out why I woke up."
- **ARTIE:** "So: the Echo Landing Junior Scouts. Mondays after lessons. And an outing on the first Saturday of every season."
- **ARTIE:** "That's what you folks call a month, right? Close enough."
- **CHOICE:**
  - **"Can I join?"** (+High Friendship)
    - **ARTIE:** "[happy] Honorary member. You'll have to learn the knot."
  - **"They're lucky to have you."** (+High Friendship)
    - **ARTIE:** "[bashful] I think I'm the lucky one."
- **New: Junior Scout Foraging Reports (the kids mark rare finds on your map)**
- **The next morning** *(Claude, 23 Nov)***:** a letter from The Junior Scouts, "From the Junior Scouts" (`scouts_knots` in `scripts/mail_data.gd`), with Quartz x1 in the envelope. The text is in [MAIL.md](../MAIL.md).

---

## ♥6 Echoes of 2036

**Trigger:** enter the Observation Lounge on a Sunday afternoon (13:00–17:00) or any day 18:00–19:10, with Artie at 6 hearts, after The Junior Scouts.

- *[S.A.R.A. has dimmed the lounge and filled the glass with a reconstructed 2030s night sky: Earth's constellations.]* *(Zachary)*
- *[Crickets chirp softly through the speakers.]* *(Zachary)*
- **S.A.R.A.:** "[happy] From the old Terran archives, Mister Vance. Minnesota, an October night, 2036. As near as I can manage."
- *[Artie doesn't answer for a while. His eyes are glistening.]*
- **ARTIE** *(Zachary)*: "[sad] That's Orion right there... same stars, just seen from a different porch."
- **ARTIE** *(Zachary)*: "I used to grieve everything I lost in 2036. Now I realize I didn't lose my life—I just got a second chapter."
- **CHOICE:**
  - **"Tell me about your porch."** (+High Friendship)
    - **ARTIE:** "[happy] A screen door that slammed. A swing that squeaked. My dog, Biscuit, asleep on my feet. I can hear it right now."
  - **"[Listen to the crickets]"** (+High Friendship)
    - *[You listen. Somewhere, centuries away, it's a warm October night.]*
- **ARTIE:** "[happy] Thank you, S.A.R.A."
- **S.A.R.A.:** "You're welcome, Mister Vance. I'll keep the file. Any night you like."

---

## ♥8 Campfire Under Glass (confession)

**Trigger:** walk into the East complex 19:30–23:00 with Artie at 8 hearts. Once the garden dome is open it plays in the woods by the hot springs; until then in the little park.

- **If the garden dome is open:**
  - *[Deep in the garden dome's woods, not far from the steam of the hot springs, is a small lantern-lit clearing.]*
  - *[Artie is roasting marshmallows over a safe thermal burner.]*
- **Otherwise:**
  - *[A lantern-lit corner of the little park. Artie is roasting marshmallows over a safe thermal burner.]*
- **ARTIE:** "[happy] There you are. Marshmallow? I synthesised them myself. They're... mostly marshmallows."
- **ARTIE** *(Zachary)*: "When you pulled me out of that cryo-pod, I felt like a ghost haunting a museum."
- **ARTIE** *(Zachary)*: "You didn't treat me like a relic—you treated me like a neighbor..."
- **If you are dating someone else (the friendship ending):**
  - **ARTIE:** "[happy] ...and then like a friend. The first real one I've made in a few hundred years. That's a record I'm proud of."
  - **ARTIE:** "I'm done looking backward at 2036. My future's right here, and I'm glad you're in it."
- **Otherwise:**
  - **ARTIE** *(Zachary)*: "...and then like the person I want to wake up next to every morning."
  - **ARTIE** *(Zachary)*: "[love] I'm done looking backward at 2036. My future is right here—if you want to share it with me."
  - **CHOICE:**
    - **"I want to share it with you, Artie."**
      - *(Artie is now your partner.)*
      - **ARTIE:** "[surprised] Yeah? Okay. Wow. Okay."
      - **ARTIE:** "[happy] A few hundred years late, and I finally got the timing right."
      - *[The burner hisses. The marshmallows burn. Neither of you notices.]*
    - **"You mean a lot to me, as a friend."**
      - **ARTIE:** "[sad] Okay. That's okay. I'm glad I said it. Old habit from 2036: say the thing, then make s'mores."
      - **ARTIE:** "[happy] Here. Have a marshmallow anyway."
- **ARTIE:** "[happy] And here's a scout trick for you: never throw anything away. Everything's useful to somebody."
- **Perk: Thrifty (recycling and geodes sometimes give rare items)**

---

## ♥10 Merit Badge of the Heart

**Trigger:** walk into the East complex 17:30–20:30 while you're dating Artie, with him at 10 hearts. The woods by the hot springs, or the little park until the dome is open.

- **If the garden dome is open:**
  - *[A Scouts campout in the garden dome's woods: three small tents, a thermal burner, and the hot springs steaming somewhere through the trees.]*
- **Otherwise:**
  - *[A Scouts campout in the little park: three small tents, a thermal burner, and the ring lights dimmed for the night.]*
- **PIP:** "[happy] They're here! They're here! Places, everybody!"
- **KIT:** "I'm doing the speech."
- **NUB:** "Nub is doing the speech."
- **KIT:** "We're BOTH doing the speech."
- **ARTIE:** "[happy] Don't look at me. I've been sworn to secrecy. Scout's honour."
- **PIP:** "By the power of the Echo Landing Junior Scouts..."
- **KIT:** "...and Mrs Sesska, who did the sewing..."
- **NUB:** "[happy] ...you are an Honorary Scoutmaster!"
- *[Pip holds up a round cloth badge, a little crooked, stitched with a campfire and a crescent moon.]*
- **ARTIE:** "[love] I woke up out of time, with nothing. Now I've got a troop, a home, and you. That's a merit badge I never thought I'd earn."
- **ARTIE:** "[bashful] The kids made the badge. I wrote a speech too. Mine was worse."
- **Keepsake: the Honorary Scoutmaster badge**
