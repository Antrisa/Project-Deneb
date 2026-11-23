# Echo Landing: NPC handoff (relationships, events, schedules)

Written 17 Nov 2026 so that a new chat can carry on the resident work: friendship, gifts, heart events, romance, daily life and dialogue. Read this first. The history behind each choice is in `echo-landing-decisions.md` (in the Project) or "Echo Landing - Decisions Log" (in the Drive folder).

## 1. Ground rules
- Godot 4.6, GDScript. Claude writes the code **without running Godot** and always says so; Zachary tests it.
- Repo: https://github.com/Antrisa/Project-Deneb, branch **`promenade-v11`**. Merge into `main` only when Zachary says.
- Commits are authored as Claude and end with the attribution lines the session gives.
- Stardew Valley's *documented designs* may be borrowed: schedules, friendship hearts, gift tastes, heart events, varied dialogue. Its art, text and code may not: no copying, tracing or decompiling. Write all dialogue fresh.
- **Gender is Male or Female only.** It sets he or she. Resident lines use the tokens `{they} {them} {their} {theirs} {they're} {they've} {are} {were} {have} {s}`, which the game swaps for the right pronoun. Zachary rejected a "they" option.
- Zachary's documents are the source of truth for characters. Anything Claude invents is a placeholder and should be marked as one.
- Design documents go in the Drive folder "Echo Station Game Master" (`1jJTYBybEyjCkQEc_hSvSfgX5Cwp6CKDo`) and in this claude.ai Project.
- Keep Zachary's email private.

## 2. Zachary's sources (all in the Drive folder)
- **"Echo Landing - Master NPC Relationship & Heart-Event Bible"** (17 Nov), the main reference. It has:
  - 28 characters: 9 romance candidates with 2–10 heart events (8-heart confession, 10-heart partner milestone), and 19 platonic or family arcs with 2–8 hearts.
  - Seven inter-NPC tensions the player helps settle:
    - S.A.R.A. vs Garrick (hospitality vs security);
    - Merrow vs Zaas (who does the work);
    - Tar'Besh vs S.A.R.A. (the Zaa'sh taboo on AI);
    - Bram vs Ooma (honest ledger vs grey market);
    - Jasper vs Evarra (Paris technique vs ration reality);
    - Maren and Owen vs Pip (overprotective);
    - Vzz'ket vs the sceptics (the cavern threat).
  - A gameplay reward for each arc. Some examples:
    - S.A.R.A.: concierge fast travel.
    - Bram: +10% salvage price.
    - Tobbin family: real-wood furniture.
    - Freya: 20% upgrade discount.
    - Job: +20% mining.
- **"Echo Landing - Heart Events: Job, Quill, Ix'ali & Artie"**: fuller scripts for four arcs.
- **"Echo Landing"**: the lore and cast doc. It was edited by Zachary after Claude's additions of 15 Nov.
- **Lore bible V2** (a docx received 16 Nov). See the differences below.
- **"Echo Landing - Cast Additions"**: Claude's notes from 15 Nov. Names and details marked (Claude) are placeholders.

## 3. Who is in the game now (24) vs the bible (28)
- **In the game:** Sara (S.A.R.A.), Tar'Besh, Bram, Jasper, Evarra, Tikka, Freya, Job, Zaas, Vzz'ket, Maren, Owen, Pip, Quill, Sesska, Rusk, Ooma, Tobbin, Merrow, Nub, Garrick, Saffi, Kit, Ix'ali.
- **In the bible but not the game:** these are unlockable later.
  - Arthur "Artie" Vance (Wave 1): the frozen 2030s human found after the pirate base, who becomes the Junior Scouts leader. He is "the teacher" in older notes.
  - Stowaway Stu (Wave 1): the hotel lobby boy.
  - Eshu (Wave 1): an Arachnay courier.
  - Anastasia "Ana" (Wave 2): a reformed pirate heir, sister of Ivan.
- **Romance candidates (9):** Freya, Jasper, Evarra, Job, Quill, Ix'ali, Artie, Stu, Ana.
- **Differences to reconcile in the game's text** (the bible wins):
  - Zaas is Water Reclamation Officer. The game calls him hydroponics chief.
  - Merrow does the water and hydroponics work.
  - Evarra is baker and gardener in the mess hall, and Jasper's adoptive sister.
  - Jasper is Ervani.
  - Garrick's family is Human/Ervani.
  - Tikka is Chief Engineer.
  - S.A.R.A. is spelled that way and has a hidden Terran Imperial origin.
  - The currency is Station Scrip.
  - Check species and looks against the lore doc. Claude's early guesses for Vuultam and Moogli may be wrong.
- **Events take place in rooms that now exist on `promenade-v11`:**
  - Reception and Star dome (`west`); Observation Lounge, S.A.R.A.'s core and Museum (Survey Level).
  - Shuttle Bay, with the Shipwright's Suite and catwalk (`bay`).
  - Engineering and its break room (`eng`).
  - Hot springs (`agri`); the hotel lobby (`hotel`).
  - The mess hall greenhouse (`east`); Rusk's bar, medbay and armoury (main level).
  - The caverns and the underground ocean (not built yet; see `docs/MAP_HANDOFF.md`).
  - The bible's "Hydroponics" is the East Complex greenhouse. "Mine Level 4" becomes a caverns floor.

## 4. How the code works now
- `scripts/npc_data.gd`:
  - `PEOPLE` holds each resident's `id` (art files `art/npc_<id>.png`, `art/portrait_<id>.png`), voice `pitch`, `first` lines (first meeting) and rotating `repeat` lines.
  - A line can start with `[happy] [sad] [surprised] [love] [angry]` to change the portrait. Keep lines under about 150 characters.
  - `LOOKS` holds descriptions for things you inspect.
- `tools/build.py`:
  - `PEOPLE` gives each resident a start spot.
  - `SCHEDULES_RAW` gives their day: a time, a map, x and y, a radius, which way they face, and an activity (`work`, `eat`, `idle`).
  - Schedules cross maps, so residents leave early enough to arrive on time.
  - Everyone eats dinner in the mess hall at 18:00; only Job, Freya and Zaas eat lunch.
  - Ooma appears only on Wednesdays and Saturdays.
- `scripts/resident.gd` and `scripts/resident_activity.gd` handle walking and activity poses. Hand-made activity frames can go in `art/npc_<id>_act.png`.
- `scripts/main.gd`:
  - `persons[who]` holds `met`, `talked_today`, `friendship` and `next`.
  - Talking once a day gives +1 friendship. Jasper also hands over a ration pack.
  - A finished bulletin-board request gives +2.
  - Friendship is a plain number shown in a toast, and saved each morning.
  - `_talk()` is where any new relationship logic hooks in.
- S.A.R.A. uses Zachary's hologram module (`sara/`, 33 clips). Talking plays greeting, explain, talk_both, nod, head_tilt or laugh. Unused clips that could serve events include paris_daydream, conjure_teacup, warning, glitches, rotate_moon and unfold_map.
- `scripts/station_calendar.gd` shows days and weekdays only: no seasons, birthdays or festivals.
- The friendship page exists in the menu. It shows the number, not hearts.
- **Not built:** hearts, gifts and gift tastes, birthdays, heart-event cutscenes, romance (dating, confession, partner), inter-NPC tension quests, event rewards, the Wave 1 and 2 arrivals.

## 5. Suggested build order (not yet confirmed by Zachary)
1. **Hearts:** turn the friendship number into hearts. Use a points-per-heart scale, a cap of 8 hearts for platonic residents and 10 for romance candidates, and slow decay if ignored (optional). Show hearts on the friendship page.
2. **Gifts:**
   - each resident gets loves, likes, dislikes and hates (Zachary to fill in, Claude to draft);
   - one gift a day and two a week;
   - birthdays count extra;
   - this needs the item list from `docs/ECONOMY_HANDOFF.md`.
3. **Calendar:**
   - birthdays first;
   - then decide on seasons or festivals: an open roadmap question, since the moon has no seasons (supply-ship days, Terran holidays, station anniversaries?).
4. **Heart-event system:**
   - Data-driven events. Each has a trigger: map, time window, hearts needed, flags and weekday.
   - Each has a script of simple steps: move, face, say, emote, wait, fade, play S.A.R.A. clip, give item, set flag.
   - Events play once and are saved.
   - Start with the ones the bible ties to places that exist now, e.g. S.A.R.A.'s "Croissant Protocol" at Reception at night, Job's breakroom gumbo, Freya's heating pump in Engineering.
5. **Romance:** an item to start dating at 8 hearts (the bible's confession), and a partner milestone at 10. Rewards are applied as perks.
6. **Tension quests:** the seven pairings, each resolved by a chain of events and requests.
7. **Arrivals:** Wave 1 (Artie, Stu, Eshu) after the pirate base and the space fight, then Wave 2 (Ana).
8. **More dialogue:** lines that vary by hearts, weekday, weather and events, and by what the player has done.

## 6. Open questions for Zachary
- Is the bible final, or still changing? Does the Heart Events doc replace the bible's entries for Job, Quill, Ix'ali and Artie?
- Can the player romance S.A.R.A.? The bible says no. Can the player marry and move a partner in, and where would they live: the hotel suite or an East Complex home?
- Birthdays for all 28.
- Do children (Pip, Nub, Kit) have gift tastes and events of their own, or only family arcs?
- Should the 8 empty homes in the East Complex go to the Wave 1 and 2 arrivals?
