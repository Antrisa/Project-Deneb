# Owen: heart events and his week (24 Nov 2026)

**The family's story (Zachary, 24 Nov):** Pip's parents are dead. Their freighter's drive failed between stations in the Neutral Zone three years ago: "nobodys fault bad things happen somtimes." Pip knows they died, but not how. *(Claude's placeholders: his father is Maren and Owen's son **Tam**, his mother **Ines**, a pilot; the ship was the **Kestrel**; Pip was with his grandparents for that one run; Maren and Owen brought him to the Landing afterwards, for somewhere quiet, which is why the doctor "came here to retire".)* This replaces the old outline, where his parents were alive in Collective space (thread C, Decision 7).

**Decided with Zachary, 24 Nov:** an arc each, and a family side arc ([MAREN_OWEN_PIP.md](MAREN_OWEN_PIP.md)). His 8's reward is the NPC Master's **Library Lore Compendium**; there's no codex system yet, so it does nothing until there is (Claude's suggestion, taken).

**The arc:** the librarian who keeps everyone's story.
- 2: the Terrans' only novel, read aloud at lessons. Tam read it nine times at nine.
- 4: the Kestrel's flight recorder, found on the trade lanes by Bram's cousin Pell. Tam's last log. Nobody's fault.
- 6: the book he's writing Pip about his mum and dad, and how to end it.
- 8: the Compendium, with Tar'Besh in the museum.

**What's whose:** the reward and the title of 4 ("The Freighter Log") are the NPC Master's; the background is Zachary's; the scenes and lines are Claude's drafts. Right answers +60, middle +30, wrong −20.

**Flags:** `owen_novel` (2), `owen_kestrel_log` (4), `owen_book` (6), `owen_compendium` and the perk `perk_library_lore_compendium` (8).

## His week (in the game: `tools/build.py`, `SCHEDULE_DAYS_RAW`)

| Day | What he does |
|---|---|
| Monday to Friday (unchanged) | The library from 07:00 (lessons in the morning); chess on the plaza at 14:00; the library; dinner; the fountain; home. |
| **Saturday (off)** | No lessons. Breakfast with Pip; the West Terminal's star dome to watch the ships come in; the fountain in the afternoon; dinner; home. |
| Sunday | As before: Maren's family day (the library, the little park). |

- **Day lines** for Saturday (`npc_data.gd DAY_LINES`); the board calendar lists his Saturdays off.

## In the game (24 Nov)

All four are playable cutscenes (`owen_2` to `owen_8`), with his new heart-event sheet (`art/npc_owen_event.png`) and his action sheet. Not run in Godot yet.

- **Letter:** the morning after 4, "Good company".
- **The Compendium** is only a perk flag for now: the codex system will use it.

---

## ♥2 One Novel

**Trigger:** The library during lessons, 08:00–11:00, Monday to Friday. With Pip, Kit and Nub. *(Claude)*

- *[The library, during lessons. Owen holds up a battered paperback the way other people hold up a lantern.]*
- **OWEN:** "Today: the novel. The only novel the Terrans left, among four hundred technical manuals."
- **OWEN:** "I've read it nine times. It is not good. That's what makes it such a good lesson."
- **OWEN:** "[happy] Ah. A guest reader. Every story needs voices, and mine all sound like a librarian."
- **PIP:** "[happy] Do Captain Valor! Do Captain Valor!"
- **CHOICE:**
  - **"Read Captain Valor, in your deepest voice."** (+High Friendship)
    - *["Stand fast, crew," you rumble. "The nebula is merely weather!" Pip falls off his chair laughing.]*
    - **OWEN:** "[happy] Better than the author deserved."
  - **"Read the villain, with a terrible cackle."** (+High Friendship)
    - *["At last, Valor, your little ship is MINE!" Nub hides under the table, thrilled.]*
    - **OWEN:** "[happy] Oh, very good. Very bad. Very good."
  - **"Skip to the end. Everyone knows how these go."**
    - **OWEN:** "[angry] We never skip to the end. The end is only any good because of everything before it."
    - *(-20 friendship with Owen)*
- **OWEN:** "Today's lesson: a bad book still has somebody's whole heart in it. That's why we keep them."
- **OWEN:** "Pip's father read this one too. Nine times, the summer he was nine. [happy] He thought Captain Valor was real."
- **PIP:** "[happy] Grandad does Dad's voice for Captain Valor. It's the same voice."

---

## ♥4 The Freighter Log

**Trigger:** Engineering's cargo bay by Bram's pod, 21:45–23:30, after 2. With Bram. *(The NPC Master's title; the scene is Claude's.)*

- *[The cargo bay, late. Bram's pod sits on the yellow pad with its hatch open. Owen waits beside it, very still, holding his hat.]*
- **BRAM:** "[sad] Pell found it in a salvage lot on the lanes, two systems out. He knew the name. Everybody on the lanes knows the name."
- *[A flight recorder, scorched black at one corner. On the side, in stencil: KESTREL.]*
- **BRAM:** "There is no charge. I see no charge. My ledger is very old."
- **OWEN:** "[sad] Our son's ship. Tam, and his wife Ines. Three years ago her drive failed between stations. Pip was with us, for that one run."
- **OWEN:** "I asked the traders to look for it. I never thought they would. Will you stay while I listen? I can't do it with Maren. Not yet."
- *[Static. Then a young man's voice, tired and cheerful.]*
- **TAM** *(recording)*: "Kestrel, log. Drive's running hot again. Ines says it's nothing. Ines always says it's nothing."
- **TAM** *(recording)*: "We'll put in at the next station and have it looked at. Tell Pip we'll be home for his birthday. Tell him the stars here are green."
- *[The recording ends in a crackle. Owen listens to the quiet after it for a long time.]*
- **OWEN:** "[sad] A coupling. That's all it was. Nobody's fault. Bad things happen sometimes."
- **OWEN:** "Pip knows they're gone. He doesn't know how. He's never asked, and I've never offered."
- **CHOICE:**
  - **"One day he'll want to hear his dad's voice. Keep it for him."** (+High Friendship)
    - **OWEN:** "...His voice. Yes. Not the ending. The green stars."
    - **OWEN:** "[happy] I'll keep it for when he asks. He will. He's his father's son."
  - **"Some things are better not knowing."** (+Friendship)
    - **OWEN:** "[sad] Perhaps. I've spent three years not knowing. It wasn't better. It was only quieter."
  - **"Send it off in the pod. Let it go."**
    - **OWEN:** "[angry] It's the last of his voice. I'll let go of a great many things. Not this."
    - *(-20 friendship with Owen)*
- **BRAM:** "[sad] ...I will wait to close the hatch. Take your time. The pod can be late. My cousins will survive."
- *[The next morning: a letter (`owen_recorder`, in [MAIL.md](../MAIL.md))]*

---

## ♥6 Pip's Book

**Trigger:** His study at home, Saturday or Sunday 14:00–17:00, after 4. *(Claude)*

- *[Owen's study, at the weekend. He sits at his desk under a slope of paper, writing by hand, which he says is the only honest way.]*
- **OWEN:** "[happy] Come in, mind the drafts. Both kinds."
- **OWEN:** "I'm writing Pip a book. About his mum and dad. Everything we remember, before we forget the small things."
- **OWEN:** "Chapter one: Tam at nine, and the toaster. Chapter two: Ines, who could land a freighter on a coin, and once did, to win the coin."
- **OWEN:** "The last chapter's the hard one. I've written it six times. Every time, it ends with the drive."
- **OWEN:** "How would you end it?"
- **CHOICE:**
  - **"End it with Pip. They're the beginning of his story."** (+High Friendship)
    - **OWEN:** "...Not their last day. His first. [happy] Yes. That's the book. I'd been writing the wrong one."
  - **"End it with the green stars."** (+High Friendship)
    - **OWEN:** "[happy] 'Tell him the stars here are green.' Yes. Let the last word be Tam's."
  - **"Leave the sad part out. He's only nine."**
    - **OWEN:** "[sad] He's nine, and he already has the sad part. What he hasn't got is everything around it."
    - *(-20 friendship with Owen)*
- **OWEN:** "Thank you. I'll have it bound. Tobbin says he can do covers. Tobbin says he can do anything, given glue."

---

## ♥8 The Compendium

**Trigger:** The museum after closing, 19:30–21:30, after 6. With Tar'Besh. Reward: the Library Lore Compendium. *(Claude)*

- *[The museum after closing. Owen and Tar'Besh have one great book open across Tar'Besh's desk, and are arguing over it with tremendous politeness.]*
- **TAR'BESH:** "Ah. A witness. Owen insists the Precursor glass is a window. I insist it is a mirror. We have agreed to let you be wrong for both of us."
- **OWEN:** "[happy] We've been making you something. Well. The bones of something."
- *[A thick ledger, bound in hide, with tabs down the side. Nearly all its pages are blank.]*
- **OWEN:** "The Library Lore Compendium. Every codex you find out there, every scrap with writing on it, has a page waiting in here."
- **OWEN:** "The Terrans left me four hundred manuals and one novel. You're going to bring me the rest."
- *[Perk: Library Lore Compendium (the codexes you find will fill it in)]*
- **TAR'BESH:** "[happy] He has put my name on the spine. Under his, in smaller letters. I have chosen to be gracious."
- **CHOICE:**
  - **"I'll fill every page."** (+High Friendship)
    - **OWEN:** "[happy] Good. Then one day Pip can read it, and know how we all got here."
  - **"So is it a window or a mirror?"** (+Friendship)
    - **OWEN:** "[happy] A window, obviously."
    - **TAR'BESH:** "A mirror, obviously."
  - **"Couldn't I just read the manuals?"**
    - **OWEN:** "[sad] You could. Nobody ever has. That's rather the problem."
    - *(-20 friendship with Owen)*
